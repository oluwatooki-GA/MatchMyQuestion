"""Run the eval set against a searcher and report retrieval quality.

    python -m eval.run_eval                                  # baseline, default datasets
    python -m eval.run_eval --filter none                    # search all subjects
    python -m eval.run_eval --compare eval/reports/A.json eval/reports/B.json

Searches run once with no score threshold; the threshold is applied when scoring,
so one run also shows what any other threshold would do (see the sweep table).
"""
import argparse
import hashlib
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from eval.dataset import load_dataset
from eval.metrics import QueryResult, summarize, threshold_sweep

DEFAULT_DATASETS = ["eval/data/synthetic.jsonl", "eval/data/manual.jsonl"]
SWEEP = [0.0, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
HEADLINE = ["n", "hit@1", "hit@5", "hit@10", "mrr@10", "ndcg@10", "empty_rate"]


def fmt(v):
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def print_table(rows: list[dict], cols: list[str], first: str):
    widths = {c: max(len(c), *(len(fmt(r.get(c, ""))) for r in rows)) for c in [first] + cols}
    print("  ".join(c.ljust(widths[c]) for c in [first] + cols))
    for r in rows:
        print("  ".join(fmt(r.get(c, "")).ljust(widths[c]) for c in [first] + cols))


def run(queries, searcher, filter_mode: str, limit: int) -> list[QueryResult]:
    results = []
    for i, q in enumerate(queries, 1):
        subject = q.subject if filter_mode == "subject" else None
        t0 = time.perf_counter()
        hits = searcher.search(q.query, subject, limit)
        latency = (time.perf_counter() - t0) * 1000
        results.append(QueryResult(
            query_id=q.id, tags=q.tags, subject=q.subject,
            ranked_urls=[p.get("url") for p, _ in hits], scores=[s for _, s in hits],
            relevant=set(q.relevant), latency_ms=latency,
        ))
        if i % 50 == 0 or i == len(queries):
            print(f"  {i}/{len(queries)} queries", file=sys.stderr)
    return results


def build_report(queries, results, threshold, meta) -> dict:
    by_tag, by_subject = defaultdict(list), defaultdict(list)
    for r in results:
        for t in r.tags:
            by_tag[t].append(r)
        by_subject[r.subject or "?"].append(r)

    qmap = {q.id: q for q in queries}
    failures = []
    for r in results:
        rank = r.first_relevant_rank(threshold)
        if rank is None or rank > 10:
            q = qmap[r.query_id]
            failures.append({
                "id": q.id, "query": q.query, "tags": q.tags, "expected": q.target_question,
                "relevant_rank_ignoring_threshold": r.first_relevant_rank(0.0),
                "top_score": r.scores[0] if r.scores else None,
            })

    return {
        "meta": meta,
        "overall": summarize(results, threshold),
        "by_tag": {t: summarize(rs, threshold) for t, rs in sorted(by_tag.items())},
        "by_subject": {s: summarize(rs, threshold) for s, rs in sorted(by_subject.items())},
        "threshold_sweep": threshold_sweep(results, SWEEP),
        "failures": failures,
    }


def print_report(rep: dict, show_failures: int):
    m = rep["meta"]
    print(f"\n== {m['searcher']} | filter={m['filter']} | threshold={m['threshold']} | {m['n_queries']} queries ==\n")
    print_table([{"set": "overall", **rep["overall"]}], HEADLINE + ["latency_p50_ms", "latency_p95_ms"], "set")
    print("\nBy query type:")
    print_table([{"tag": t, **s} for t, s in rep["by_tag"].items()], HEADLINE, "tag")
    print("\nWorst subjects (hit@10):")
    worst = sorted(rep["by_subject"].items(), key=lambda kv: kv[1]["hit@10"])[:8]
    print_table([{"subject": s, **v} for s, v in worst], ["n", "hit@10", "mrr@10"], "subject")
    print("\nScore threshold sweep (the API currently uses the value in SEARCH_SCORE_THRESHOLD):")
    print_table(rep["threshold_sweep"], ["hit@10", "empty_rate", "avg_returned"], "threshold")
    if show_failures and rep["failures"]:
        print(f"\nSample failures ({min(show_failures, len(rep['failures']))} of {len(rep['failures'])}):")
        for f in rep["failures"][:show_failures]:
            where = f["relevant_rank_ignoring_threshold"]
            why = "not in top 50" if where is None else f"rank {where} (or cut by threshold)"
            print(f"  [{','.join(f['tags'][1:]) or f['tags'][0]}] {f['query']!r}\n"
                  f"      expected: {f['expected'][:110]!r}\n      -> {why}")


def compare(path_a: str, path_b: str):
    a, b = (json.loads(Path(p).read_text()) for p in (path_a, path_b))
    print(f"A = {a['meta']['searcher']} ({path_a})\nB = {b['meta']['searcher']} ({path_b})\n")
    if a["meta"].get("dataset_fingerprint") != b["meta"].get("dataset_fingerprint"):
        print("WARNING: reports were run on different datasets; deltas are not comparable.\n")
    rows = []
    for key in ["overall"] + [f"tag:{t}" for t in a["by_tag"]]:
        sa = a["overall"] if key == "overall" else a["by_tag"].get(key[4:])
        sb = b["overall"] if key == "overall" else b["by_tag"].get(key[4:])
        if not sa or not sb:
            continue
        row = {"set": key}
        for m in ["hit@1", "hit@10", "mrr@10", "empty_rate"]:
            row[m] = f"{sa[m]:.3f} -> {sb[m]:.3f} ({sb[m] - sa[m]:+.3f})"
        rows.append(row)
    print_table(rows, ["hit@1", "hit@10", "mrr@10", "empty_rate"], "set")
    n = a["overall"]["n"]
    if n:
        # Rough 95% margin for a difference in proportions near 0.5; tells you if a delta is noise.
        print(f"\n(With n={n}, differences under ~{1.96 * (0.5 / n) ** 0.5 * 100:.0f} points in hit@k are likely noise.)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", nargs="+", help=f"JSONL files (default: those of {DEFAULT_DATASETS} that exist)")
    p.add_argument("--searcher", default="production")
    p.add_argument("--collection")
    p.add_argument("--filter", choices=["subject", "none"], default="subject",
                   help="subject: filter by the target's subject, like the UI does (default)")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--threshold", type=float, help="score cutoff for metrics (default: SEARCH_SCORE_THRESHOLD)")
    p.add_argument("--tags", help="only run queries with any of these comma-separated tags")
    p.add_argument("--show-failures", type=int, default=10)
    p.add_argument("-o", "--out", help="report path (default: eval/reports/<timestamp>.json)")
    p.add_argument("--compare", nargs=2, metavar=("A.json", "B.json"))
    args = p.parse_args(argv)

    if args.compare:
        return compare(*args.compare)

    paths = args.dataset or [d for d in DEFAULT_DATASETS if Path(d).exists()]
    if not paths:
        sys.exit("No dataset found. Run `python -m eval.build_dataset` or `python -m eval.label` first.")
    queries = load_dataset(*paths)
    if args.tags:
        wanted = set(args.tags.split(","))
        queries = [q for q in queries if wanted & set(q.tags)]
    if not queries:
        sys.exit("Dataset is empty after filtering.")

    from eval.searchers import get_searcher
    from app.config.settings import settings

    threshold = settings.SEARCH_SCORE_THRESHOLD if args.threshold is None else args.threshold
    searcher = get_searcher(args.searcher, args.collection)
    print(f"Running {len(queries)} queries from {', '.join(paths)} ...", file=sys.stderr)
    try:
        results = run(queries, searcher, args.filter, args.limit)
    finally:
        getattr(searcher, "close", lambda: None)()

    meta = {
        "searcher": searcher.name, "filter": args.filter, "threshold": threshold, "limit": args.limit,
        "datasets": paths, "n_queries": len(queries),
        "dataset_fingerprint": hashlib.sha256("\n".join(sorted(q.id + "\t" + q.query for q in queries)).encode()).hexdigest()[:16],
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    report = build_report(queries, results, threshold, meta)
    print_report(report, args.show_failures)

    out = Path(args.out or f"eval/reports/{datetime.now():%Y%m%d-%H%M%S}-{args.searcher}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to {out}")


if __name__ == "__main__":
    main()
