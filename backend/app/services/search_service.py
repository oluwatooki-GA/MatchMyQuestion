import hashlib
import json

from loguru import logger
from redis import RedisError

from app.schemas.search_schema import SearchRequest, SearchResult, SearchResultItem

CACHE_TTL_SECONDS = 1800


class SearchService:
    def __init__(self, redis_client, neural_search_service):
        self.redis_client = redis_client
        self.neural_search_service = neural_search_service

    @staticmethod
    def cache_key(search_request: SearchRequest) -> str:
        """Order- and whitespace-insensitive key so equivalent searches share a cache entry."""
        items = sorted(
            (item.subject.strip(), sorted(set(item.years or [])))
            for item in (search_request.search_items or [])
        )
        normalized = {"q": " ".join(search_request.q.lower().split()), "items": items}
        digest = hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()
        return f"search:v1:{digest}"

    def _cache_get(self, key: str) -> SearchResult | None:
        if not self.redis_client:
            return None
        try:
            cached = self.redis_client.get(key)
        except RedisError as exc:
            logger.warning(f"Redis read failed, skipping cache: {exc}")
            return None
        return SearchResult(**json.loads(cached)) if cached else None

    def _cache_set(self, key: str, result: SearchResult) -> None:
        if not self.redis_client:
            return
        try:
            self.redis_client.set(name=key, value=result.model_dump_json(), ex=CACHE_TTL_SECONDS)
        except RedisError as exc:
            logger.warning(f"Redis write failed, result not cached: {exc}")

    def search(self, search_request: SearchRequest) -> SearchResult:
        key = self.cache_key(search_request)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        items = self.neural_search_service.search(search_request.q, search_request=search_request)
        result = SearchResult(result=[SearchResultItem(**item) for item in items] or None)

        self._cache_set(key, result)
        return result
