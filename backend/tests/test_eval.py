import json
import random
import zlib

import numpy as np
import pytest
from qdrant_client import QdrantClient, models

from eval import run_eval
from eval.dataset import EvalQuery, load_dataset, save_dataset
from eval.metrics import QueryResult, summarize, threshold_sweep
from eval.synth import add_typos, build_synthetic, correct_option_text

CORPUS = [
    ("Biology", "2021", "Which organelle is responsible for the production of energy in the cell?",
     ["A. Ribosome", "B. Mitochondrion", "C. Nucleus", "D. Golgi body"], "B"),
    ("Biology", "2022", "Which organelle is responsible for the production of energy in the cell?",
     ["A. Ribosome", "B. Mitochondrion", "C. Nucleus", "D. Golgi body"], "B"),
    ("Biology", "2020", "The process by which green plants manufacture food using sunlight is called",
     ["A. Respiration", "B. Transpiration", "C. Photosynthesis", "D. Osmosis"], "C"),
    ("Biology", "2019", "Movement of water molecules across a semi permeable membrane is known as",
     ["A. Diffusion", "B. Osmosis", "C. Plasmolysis", "D. Imbibition"], "B"),
    ("Chemistry", "2021", "What is the oxidation number of sulphur in sulphuric acid H2SO4 compound?",
     ["A. +2", "B. +4", "C. +6", "D. -2"], "C"),
    ("Chemistry", "2020", "Which gas is produced when zinc granules react with dilute hydrochloric acid solution?",
     ["A. Oxygen", "B. Hydrogen", "C. Chlorine", "D. Nitrogen"], "B"),
    ("Physics", "2022", "Calculate the kinetic energy of a moving body of mass 4 kg travelling with velocity 5 m/s",
     ["A. 10 J", "B. 20 J", "C. 50 J", "D. 100 J"], "C"),
    ("Physics", "2023", "The refractive index of glass relative to air when light travels between media equals",
     ["A. 1.0", "B. 1.5", "C. 2.0", "D. 0.5"], "B"),
    ("Literature in English", "2021", "In Chinua Achebe's Things Fall Apart novel, the protagonist Okonkwo is exiled because he",
     ["A. stole yams", "B. killed a clansman accidentally", "C. beat his wife", "D. insulted elders"], "B"),
]


def records():
    return [{"question": q, "options": str(o), "correct_answer": f"Correct Answer: Option {a}",
             "explanation_text": "N/A", "explanation_html": "N/A", "subject": s, "exam_type": "WAEC",
             "year": y, "image_url": "N/A", "url": f"https://example.test/q/{i}"}
            for i, (s, y, q, o, a) in enumerate(CORPUS)]


def trigram_embed(text: str, dim: int = 512) -> list[float]:
    """Stand-in for the real model: hashed character trigrams. Typo-tolerant, deterministic."""
    v = np.zeros(dim)
    t = f"  {text.lower()}  "
    for i in range(len(t) - 2):
        v[zlib.crc32(t[i:i + 3].encode()) % dim] += 1
    return (v / (np.linalg.norm(v) or 1)).tolist()


@pytest.fixture()
def searcher():
    from app.services.neural_search_service import NeuralSearcherService
    from eval.searchers import ProductionSearcher

    client = QdrantClient(":memory:")
    client.create_collection("q", vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE))
    client.upload_points("q", [models.PointStruct(id=i, vector=trigram_embed(r["question"]), payload=r)
                               for i, r in enumerate(records())])
    service = NeuralSearcherService.__new__(NeuralSearcherService)
    service.collection_name, service.qdrant_client, service.embed = "q", client, trigram_embed
    s = ProductionSearcher.__new__(ProductionSearcher)
    s.service, s.name = service, "production:test"
    s.close = lambda: None  # shared across runs within a test
    return s


def test_correct_option_text():
    r = records()[0]
    assert correct_option_text(r) == "Mitochondrion"
    assert correct_option_text({**r, "correct_answer": "N/A"}) is None
    assert correct_option_text({**r, "options": "garbage("}) is None


def test_add_typos_changes_long_words_only():
    out = add_typos(["photosynthesis", "is", "osmosis"], random.Random(1), rate=1.0)
    assert out[1] == "is" and out[0] != "photosynthesis" and out[2] != "osmosis"


def test_build_synthetic_marks_repeats_relevant_and_is_deterministic():
    a = build_synthetic(records(), n=20, seed=7)
    b = build_synthetic(records(), n=20, seed=7)
    assert [q.query for q in a] == [q.query for q in b]
    assert {t for q in a for t in q.tags} >= {"keywords", "typo", "truncated", "answer", "synthetic"}
    organelle = [q for q in a if q.target_question.startswith("Which organelle")]
    assert organelle and all(q.relevant == ["https://example.test/q/0", "https://example.test/q/1"] for q in organelle)
    assert len({q.id for q in a}) == len(a)
    assert len({(q.target_question, *q.tags) for q in a}) == len(a)  # repeat not used as a second source


def test_dataset_roundtrip_and_validation(tmp_path):
    p = tmp_path / "d.jsonl"
    save_dataset([EvalQuery(id="x", query="q", relevant=["u"], tags=["manual"])], p)
    assert load_dataset(p)[0].relevant == ["u"]
    p.write_text(p.read_text() + p.read_text())
    with pytest.raises(ValueError, match="duplicate"):
        load_dataset(p)
    p.write_text(json.dumps({"id": "y", "query": "q", "relevant": []}) + "\n")
    with pytest.raises(ValueError, match="no relevant"):
        load_dataset(p)


def test_metrics_and_threshold():
    r1 = QueryResult("a", [], None, ["x", "rel"], [0.9, 0.5], {"rel"}, 10)    # rank 2
    r2 = QueryResult("b", [], None, ["rel"], [0.3], {"rel"}, 20)              # rank 1, low score
    r3 = QueryResult("c", [], None, ["x"], [0.8], {"rel"}, 30)                # miss
    s = summarize([r1, r2, r3], threshold=0.0)
    assert s["hit@1"] == pytest.approx(1 / 3) and s["hit@5"] == pytest.approx(2 / 3)
    assert s["mrr@10"] == pytest.approx((0.5 + 1) / 3)
    s35 = summarize([r1, r2, r3], threshold=0.35)
    assert s35["hit@5"] == pytest.approx(1 / 3) and s35["empty_rate"] == pytest.approx(1 / 3)
    sweep = threshold_sweep([r1, r2, r3], [0.0, 0.35])
    assert sweep[0]["hit@10"] > sweep[1]["hit@10"]


def test_end_to_end_run_and_compare(searcher, tmp_path, monkeypatch, capsys):
    data = tmp_path / "syn.jsonl"
    save_dataset(build_synthetic(records(), n=20, seed=3), data)
    monkeypatch.setattr("eval.searchers.get_searcher", lambda name, collection=None: searcher)

    out_a, out_b = tmp_path / "a.json", tmp_path / "b.json"
    run_eval.main(["--dataset", str(data), "-o", str(out_a), "--threshold", "0"])
    run_eval.main(["--dataset", str(data), "-o", str(out_b), "--threshold", "0", "--filter", "none"])
    rep = json.loads(out_a.read_text())
    assert rep["overall"]["n"] == len(load_dataset(data))
    assert rep["overall"]["hit@10"] > 0.8          # tiny corpus: nearly everything is findable
    assert {"keywords", "typo", "answer"} <= set(rep["by_tag"])
    assert json.loads(out_b.read_text())["meta"]["dataset_fingerprint"] == rep["meta"]["dataset_fingerprint"]

    run_eval.main(["--compare", str(out_a), str(out_b)])
    out = capsys.readouterr().out
    assert "hit@10" in out and "WARNING" not in out
