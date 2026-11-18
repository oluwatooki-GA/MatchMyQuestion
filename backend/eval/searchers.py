"""Anything with `.search(query, subject) -> list[(payload, score)]` can be evaluated.

Add new systems here (hybrid, reranked, another embedding model) and compare their
reports against the baseline with `run_eval --compare`.
"""
from typing import Protocol


class Searcher(Protocol):
    name: str

    def search(self, query: str, subject: str | None, limit: int) -> list[tuple[dict, float]]: ...


class ProductionSearcher:
    """Exactly what the API does today, minus the score threshold (applied later, in the report)."""

    name = "production"

    def __init__(self, collection: str | None = None):
        from app.config.settings import settings
        from app.services.neural_search_service import NeuralSearcherService

        self.service = NeuralSearcherService(collection or settings.QDRANT_COLLECTION_NAME)
        self.name = f"production:{settings.EMBEDDING_MODEL}"

    def search(self, query: str, subject: str | None, limit: int) -> list[tuple[dict, float]]:
        from app.schemas.search_schema import SearchItem, SearchRequest

        request = SearchRequest(q=query, search_items=[SearchItem(subject=subject)] if subject else None)
        return self.service.search_with_scores(query, request, limit=limit, score_threshold=0.0)

    def close(self):
        self.service.close()


def get_searcher(name: str, collection: str | None = None) -> Searcher:
    if name == "production":
        return ProductionSearcher(collection)
    raise ValueError(f"Unknown searcher {name!r}. Add it to eval/searchers.py.")
