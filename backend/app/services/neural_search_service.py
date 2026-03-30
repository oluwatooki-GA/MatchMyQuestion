import json
from typing import Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from app.config.settings import settings
from app.schemas.search_schema import SearchRequest, SearchItem
import ast


class NeuralSearcherService:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY)

    @staticmethod
    def _get_match(val):
        if len(val) > 1:
            return models.MatchAny(any=val)
        else:
            return models.MatchValue(value=val[0])

    @staticmethod
    def format_payload(payload: dict):
        for key, value in payload.items():
            if value == "N/A":
                payload[key] = None

        if payload['options']:
            payload['options'] = ast.literal_eval(payload['options'])
            # payload['options'] = list(map(lambda x:x[:2] + x[2:].title(), payload['options']))
            # payload['options_letters'] = [x[0] for x in payload['options']]
        else:
            payload['options_letters'] = None
        if payload['correct_answer']:
            payload['correct_answer_letter'] = payload['correct_answer'][-1]
        else:
            payload['correct_answer_letter'] = None

        return payload

    def search(self, text: str, search_request: SearchRequest) -> list[dict] | None:

        filters = []
        if search_request.search_items:
            for search_item in search_request.search_items:
                search_item: SearchItem
                subject_filter = models.FieldCondition(key='subject', match=models.MatchValue(value=search_item.subject)) if search_item.subject else None
                year_filter = models.FieldCondition(key='year', match=self._get_match(search_item.years)) if search_item.years else None
                filter_item = models.Filter(must=[query for query in (subject_filter,year_filter) if query])
                filters.append(filter_item)
        query_filter = models.Filter(should=filters)

        vector = self.model.encode(text).tolist()

        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=vector,
            score_threshold=0.35,
            query_filter=query_filter if filters else None,
            limit=50,
        ).points

        payloads = [self.format_payload(hit.payload) for hit in search_result]
        return payloads

    def close(self):
        self.qdrant_client.close()
