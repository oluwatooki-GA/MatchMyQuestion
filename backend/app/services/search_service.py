import json
from app.schemas.search_schema import SearchRequest, SearchResult, SearchResultItem


class SearchService:
    def __init__(self, redis_client, neural_search_service):
        self.redis_client = redis_client
        self.neural_search_service = neural_search_service

    def search(self, search_request: SearchRequest) -> SearchResult:
        cache_key = json.dumps(search_request.model_dump())
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            cached_data = json.loads(cached_result)
            return SearchResult(**cached_data)

        items = self.neural_search_service.search(
            search_request.q,
            search_request=search_request
        )

        if not items:
            result = SearchResult(result=None)
        else:
            # Convert dict items to SearchResultItem
            search_items = [SearchResultItem(**item) for item in items]
            result = SearchResult(result=search_items)

        self.redis_client.set(name=cache_key, value=json.dumps(result.model_dump()), ex=1800)
        return result
