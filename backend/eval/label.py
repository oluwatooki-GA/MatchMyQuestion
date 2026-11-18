"""Hand-label real queries: run a search, mark which results are correct, save to manual.jsonl.

    python -m eval.label                               # type queries interactively
    python -m eval.label --queries student_queries.txt # label a list (one query per line)

Labelled queries are worth far more than synthetic ones: use real student phrasing,
half-remembered questions, typos, maths notation. 50-100 is enough to start.
Search with --limit 20 so the right question is usually somewhere in the list; if it
isn't, paste its url manually.
"""
import argparse
import sys
from pathlib import Path

from eval.dataset import EvalQuery, load_dataset, save_dataset


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        sys.exit(0)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--queries", help="text file, one query per line")
    p.add_argument("--subject", help="restrict searches to this subject")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("-o", "--out", default="eval/data/manual.jsonl")
    args = p.parse_args(argv)

    from eval.searchers import get_searcher

    out = Path(args.out)
    existing = load_dataset(out) if out.exists() else []
    next_id = len(existing) + 1
    done = {q.query for q in existing}
    pending = [l.strip() for l in Path(args.queries).read_text().splitlines() if l.strip()] if args.queries else None
    searcher = get_searcher("production")

    print("For each query: enter result numbers that are correct (e.g. '1,4'), a url, "
          "'s' to skip, or 'q' to quit.\n")
    try:
        while True:
            if pending is not None:
                if not pending:
                    break
                query = pending.pop(0)
                if query in done:
                    continue
                print(f"\nQuery: {query}")
            else:
                query = ask("\nQuery (blank to quit): ")
                if not query:
                    break
            subject = args.subject or ask("Subject filter (blank = all): ") or None

            hits = searcher.search(query, subject, args.limit)
            for i, (payload, score) in enumerate(hits, 1):
                print(f"  {i:2d}. [{score:.2f}] {payload.get('subject')} {payload.get('year')}: "
                      f"{(payload.get('question') or '')[:100]}")
            if not hits:
                print("  (no results)")

            answer = ask("Correct: ")
            if answer.lower() == "q":
                break
            if answer.lower() in ("s", ""):
                continue
            relevant = []
            for part in answer.replace(" ", "").split(","):
                if part.startswith("http"):
                    relevant.append(part)
                elif part.isdigit() and 1 <= int(part) <= len(hits):
                    relevant.append(hits[int(part) - 1][0]["url"])
            if not relevant:
                print("  nothing recorded")
                continue
            tags = [t for t in ask("Tags, comma-separated (e.g. typo,math,paraphrase; optional): ").split(",") if t]
            target = next((pl.get("question") for pl, _ in hits if pl.get("url") == relevant[0]), None)
            save_dataset([EvalQuery(id=f"man-{next_id:04d}", query=query, relevant=relevant,
                                    subject=subject, tags=["manual"] + tags, target_question=target)],
                         out, append=True)
            print(f"  saved man-{next_id:04d}")
            next_id += 1
            done.add(query)
    finally:
        searcher.close()


if __name__ == "__main__":
    main()
