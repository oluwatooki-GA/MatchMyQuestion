"""Eval dataset format: one JSON object per line (JSONL).

    {"id": "syn-000123-keywords",
     "query": "function lungs gas exchange",
     "relevant": ["https://myschool.ng/classroom/biology/12345", ...],  # question `url`s
     "subject": "Biology",            # optional; used when evaluating with --filter subject
     "tags": ["synthetic", "keywords"],
     "target_question": "What is the function of the lungs?"}  # for readable failure reports

A result counts as relevant if its payload `url` is in `relevant`. Repeated questions
(same text, different year) are all listed as relevant, since showing any of them is correct.
"""
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class EvalQuery:
    id: str
    query: str
    relevant: list[str]
    subject: str | None = None
    tags: list[str] = field(default_factory=list)
    target_question: str | None = None


def load_dataset(*paths: str | Path) -> list[EvalQuery]:
    queries, seen = [], set()
    for path in paths:
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("//"):
                continue
            try:
                q = EvalQuery(**json.loads(line))
            except (json.JSONDecodeError, TypeError) as exc:
                raise ValueError(f"{path}:{n}: invalid eval record: {exc}") from exc
            if not q.relevant:
                raise ValueError(f"{path}:{n}: query {q.id!r} has no relevant urls")
            if q.id in seen:
                raise ValueError(f"{path}:{n}: duplicate query id {q.id!r}")
            seen.add(q.id)
            queries.append(q)
    return queries


def save_dataset(queries: list[EvalQuery], path: str | Path, append: bool = False) -> None:
    with open(path, "a" if append else "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps(asdict(q), ensure_ascii=False) + "\n")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (text or "").lower())).strip()
