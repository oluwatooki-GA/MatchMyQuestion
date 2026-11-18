import math
from dataclasses import dataclass


@dataclass
class QueryResult:
    query_id: str
    tags: list[str]
    subject: str | None
    ranked_urls: list[str]       # results in rank order, with no score threshold applied
    scores: list[float]
    relevant: set[str]
    latency_ms: float

    def first_relevant_rank(self, threshold: float = 0.0) -> int | None:
        """1-based rank of the first relevant hit that survives `threshold`, else None."""
        for rank, (url, score) in enumerate(zip(self.ranked_urls, self.scores), 1):
            if score < threshold:
                return None  # scores are sorted descending; nothing below survives
            if url in self.relevant:
                return rank
        return None

    def returned_count(self, threshold: float) -> int:
        return sum(1 for s in self.scores if s >= threshold)


def dcg(rels: list[int]) -> float:
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(rels))


def ndcg_at_k(r: QueryResult, k: int, threshold: float) -> float:
    rels = [int(u in r.relevant) for u, s in zip(r.ranked_urls[:k], r.scores[:k]) if s >= threshold]
    ideal = dcg([1] * min(len(r.relevant), k))
    return dcg(rels) / ideal if ideal else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = (len(s) - 1) * p / 100
    lo, hi = math.floor(idx), math.ceil(idx)
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)


def summarize(results: list[QueryResult], threshold: float, ks=(1, 3, 5, 10)) -> dict:
    n = len(results)
    if n == 0:
        return {"n": 0}
    ranks = [r.first_relevant_rank(threshold) for r in results]
    out = {"n": n}
    for k in ks:
        out[f"hit@{k}"] = sum(1 for x in ranks if x is not None and x <= k) / n
    out["mrr@10"] = sum(1 / x for x in ranks if x is not None and x <= 10) / n
    out["ndcg@10"] = sum(ndcg_at_k(r, 10, threshold) for r in results) / n
    out["empty_rate"] = sum(1 for r in results if r.returned_count(threshold) == 0) / n
    out["latency_p50_ms"] = percentile([r.latency_ms for r in results], 50)
    out["latency_p95_ms"] = percentile([r.latency_ms for r in results], 95)
    return out


def threshold_sweep(results: list[QueryResult], thresholds: list[float]) -> list[dict]:
    """How a score cutoff trades away correct answers vs. how often it returns nothing."""
    rows = []
    for t in thresholds:
        s = summarize(results, t)
        rows.append({"threshold": t, "hit@10": s["hit@10"], "empty_rate": s["empty_rate"],
                     "avg_returned": sum(min(r.returned_count(t), 50) for r in results) / max(len(results), 1)})
    return rows
