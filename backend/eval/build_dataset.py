"""Build a synthetic eval set from the question corpus.

    python -m eval.build_dataset --from-qdrant -n 300
    python -m eval.build_dataset --from-json ../scraper/results0/final_result.json -n 300
"""
import argparse
from collections import Counter

from eval import corpus
from eval.dataset import save_dataset
from eval.synth import build_synthetic


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-json", help="scraper output file (list of question records)")
    src.add_argument("--from-qdrant", action="store_true", help="scroll the collection in QDRANT_URL")
    p.add_argument("--collection", help="override QDRANT_COLLECTION_NAME")
    p.add_argument("-n", type=int, default=300, help="number of source questions (each yields up to 5 queries)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--kinds", help="comma-separated subset of: keywords,typo,shuffled,truncated,answer")
    p.add_argument("-o", "--out", default="eval/data/synthetic.jsonl")
    args = p.parse_args(argv)

    records = corpus.from_json(args.from_json) if args.from_json else corpus.from_qdrant(args.collection)
    print(f"Loaded {len(records)} questions")
    kinds = set(args.kinds.split(",")) if args.kinds else None
    queries = build_synthetic(records, n=args.n, seed=args.seed, kinds=kinds)
    save_dataset(queries, args.out)

    kinds_count = Counter(t for q in queries for t in q.tags if t not in ("synthetic", "image_ref"))
    print(f"Wrote {len(queries)} queries from {len({q.target_question for q in queries})} questions "
          f"across {len({q.subject for q in queries})} subjects -> {args.out}")
    print("  " + ", ".join(f"{k}: {v}" for k, v in sorted(kinds_count.items())))


if __name__ == "__main__":
    main()
