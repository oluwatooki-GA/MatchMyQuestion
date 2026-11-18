# Search evaluation

Measures how often search finds the right question, so changes like hybrid search, reranking or a
new embedding model can be judged by numbers instead of by feel.

Run everything from `backend/`, with the same env as the API (`.env.dev` or `QDRANT_*` variables).

## 1. Build a synthetic test set (once)

```bash
python -m eval.build_dataset --from-qdrant -n 300
```

This takes 300 questions (balanced across subjects) and creates up to 5 queries from each, imitating how
students search. The source question is the correct answer, so no manual labelling is needed:

| tag | example | imitates |
|---|---|---|
| `keywords` | `organelle production energy cell` | remembering key words |
| `typo` | `organlle prodution energy cell` | misspellings |
| `shuffled` | `energy cell organelle production` | different word order |
| `truncated` | `Which organelle is responsible for the` | remembering only the start |
| `answer` | `organelle responsible Mitochondrion` | searching by the answer |

Questions repeated across years count as correct for each other. Queries about diagrams or passages are
also tagged `image_ref`, since text search can't fully answer them.

Commit `eval/data/synthetic.jsonl`: every comparison needs the **same** set.

## 2. Add real queries (the most valuable part)

```bash
python -m eval.label                                  # interactive
python -m eval.label --queries student_queries.txt    # label a list, one per line
```

Type a query, then enter the numbers of the correct results. These are saved to `eval/data/manual.jsonl`.
Synthetic queries reuse the question's own words, so they make keyword matching look better than it is.
50-100 real queries with typos, paraphrases and maths will tell you much more.

## 3. Run

```bash
python -m eval.run_eval                     # filter by the target's subject, like the UI does
python -m eval.run_eval --filter none       # search across all subjects (harder)
python -m eval.run_eval --tags typo,manual  # a subset
```

You get overall metrics, a breakdown by query type, the worst subjects, a **score threshold sweep**,
and sample failures. Reports are saved in `eval/reports/`.

- **hit@k:** share of queries where a correct question is in the top k (the main number).
- **mrr@10:** rewards the correct question being near the top (1.0 = always first).
- **empty_rate:** share of queries returning nothing after the score cutoff.
- **Threshold sweep:** searches run with no cutoff, then the cutoff is applied when scoring, so one run
  shows how `SEARCH_SCORE_THRESHOLD` trades lost answers against empty results. If raising it costs a lot
  of hit@10, it is too high.

## 4. Compare two systems

```bash
python -m eval.run_eval -o eval/reports/baseline.json
# ...change something (model, hybrid, reranker)...
python -m eval.run_eval -o eval/reports/hybrid.json
python -m eval.run_eval --compare eval/reports/baseline.json eval/reports/hybrid.json
```

The comparison warns if the two reports used different datasets and tells you how large a difference is
likely just noise for your dataset size.

To evaluate a new search approach, add a class with
`search(query, subject, limit) -> [(payload, score), ...]` to `eval/searchers.py` and run it with
`--searcher <name>`.
