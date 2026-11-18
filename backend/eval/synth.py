"""Generate labelled queries automatically from the question corpus.

Each generator imitates a way students actually search: remembering only key words,
only the start of a question, misspelling, or searching by the answer. The source
question's url is the ground truth, so no manual labelling is needed.

Synthetic queries are a floor, not a substitute for real ones: they overlap lexically
with the source text, so they flatter keyword search. Mix in hand-labelled queries
(see label.py) before trusting small differences between systems.
"""
import ast
import random
import re
from collections import defaultdict

from eval.dataset import EvalQuery, normalize_text

STOPWORDS = set("""
a an the of to in on at for from by with and or but if then than as is are was were be been being
which what who whom whose when where why how this that these those it its into about above below
following following: one two each any all some most more less not no do does did can could would
should will shall may might must has have had i you he she we they them his her their our your my
me us so such there here also only very following.
""".split())

IMAGE_HINTS = re.compile(r"\b(diagram|figure|fig\.?|graph|table|passage|above|below|shown|illustrat)", re.I)


def content_words(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-^²³√+]*", text or "")
    return [w for w in words if w.lower() not in STOPWORDS and len(w) > 1]


def add_typos(words: list[str], rng: random.Random, rate: float = 0.5) -> list[str]:
    out = []
    for w in words:
        if len(w) >= 5 and rng.random() < rate:
            i = rng.randrange(1, len(w) - 1)
            op = rng.choice(["swap", "drop", "double"])
            if op == "swap":
                w = w[:i] + w[i + 1] + w[i] + w[i + 2:]
            elif op == "drop":
                w = w[:i] + w[i + 1:]
            else:
                w = w[:i] + w[i] + w[i:]
        out.append(w)
    return out


def correct_option_text(record: dict) -> str | None:
    answer, options = record.get("correct_answer"), record.get("options")
    if not answer or answer == "N/A" or not options or options == "N/A":
        return None
    if isinstance(options, str):
        try:
            options = ast.literal_eval(options)
        except (ValueError, SyntaxError):
            return None
    letter = answer.strip()[-1].upper()
    for opt in options:
        m = re.match(r"^\s*([A-E])[.)]\s*(.+)", str(opt))
        if m and m.group(1).upper() == letter:
            return m.group(2).strip()
    return None


def _keyword_query(words: list[str], rng: random.Random) -> list[str]:
    k = min(len(words), rng.randint(3, 6))
    idx = sorted(rng.sample(range(len(words)), k))
    return [words[i] for i in idx]


def generate(record: dict, rng: random.Random) -> dict[str, str]:
    """Return {tag: query} for one question. Skips generators that don't apply."""
    question = record["question"]
    words = content_words(question)
    all_words = question.split()
    out: dict[str, str] = {}

    kw = _keyword_query(words, rng)
    out["keywords"] = " ".join(kw)
    out["typo"] = " ".join(add_typos(kw, rng))

    shuffled = kw[:]
    rng.shuffle(shuffled)
    if shuffled != kw:
        out["shuffled"] = " ".join(shuffled)

    if len(all_words) >= 10:
        cut = max(5, int(len(all_words) * rng.uniform(0.4, 0.6)))
        out["truncated"] = " ".join(all_words[:cut])

    answer = correct_option_text(record)
    if answer and normalize_text(answer) not in {"true", "false", "none of the above", "all of the above"}:
        out["answer"] = " ".join(words[: rng.randint(2, 3)] + [answer])

    return out


def build_synthetic(
    corpus: list[dict],
    n: int,
    seed: int = 42,
    kinds: set[str] | None = None,
    min_words: int = 4,
) -> list[EvalQuery]:
    rng = random.Random(seed)

    # Repeated questions (same text, other years) are all correct answers.
    by_text: dict[str, list[str]] = defaultdict(list)
    for r in corpus:
        if r.get("url"):
            by_text[normalize_text(r.get("question", ""))].append(r["url"])

    # One source per distinct question text, so repeats across years don't become duplicate queries.
    eligible, seen_text = [], set()
    for r in corpus:
        key = normalize_text(r.get("question", ""))
        if r.get("url") and key and key not in seen_text and len(content_words(r["question"])) >= min_words:
            seen_text.add(key)
            eligible.append(r)
    # Stratify by subject so big subjects don't dominate the dataset.
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for r in eligible:
        by_subject[r.get("subject") or "?"].append(r)
    for rs in by_subject.values():
        rng.shuffle(rs)
    picked, subjects = [], sorted(by_subject)
    while len(picked) < n and any(by_subject.values()):
        for s in subjects:
            if by_subject[s] and len(picked) < n:
                picked.append(by_subject[s].pop())

    queries = []
    for i, r in enumerate(picked):
        base_tags = ["synthetic"] + (["image_ref"] if IMAGE_HINTS.search(r["question"]) or
                                     (r.get("image_url") not in (None, "", "N/A")) else [])
        for kind, text in generate(r, rng).items():
            if kinds and kind not in kinds:
                continue
            queries.append(EvalQuery(
                id=f"syn-{i:05d}-{kind}",
                query=text,
                relevant=sorted(set(by_text[normalize_text(r["question"])])),
                subject=r.get("subject"),
                tags=base_tags + [kind],
                target_question=r["question"],
            ))
    return queries
