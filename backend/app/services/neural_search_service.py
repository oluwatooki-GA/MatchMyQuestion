import ast
from typing import Any

from fastembed import TextEmbedding
from loguru import logger
from qdrant_client import QdrantClient, models

from app.config.settings import settings
from app.schemas.search_schema import SearchRequest


class NeuralSearcherService:
    """Embeds the query with a small ONNX model (fastembed) and searches Qdrant.

    fastembed runs the same all-MiniLM-L6-v2 weights as sentence-transformers,
    but on onnxruntime instead of PyTorch, so it needs a fraction of the RAM.
    Vectors are compatible with a collection built with sentence-transformers.
    """

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.model = TextEmbedding(
            model_name=settings.EMBEDDING_MODEL,
            cache_dir=settings.EMBEDDING_CACHE_DIR,
            threads=settings.EMBEDDING_THREADS,
        )
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
            timeout=settings.QDRANT_TIMEOUT,
        )

    @staticmethod
    def _get_match(val: list[str]):
        if len(val) > 1:
            return models.MatchAny(any=val)
        return models.MatchValue(value=val[0])

    @staticmethod
    def _parse_options(options: Any) -> list | None:
        if not options:
            return None
        if isinstance(options, list):
            return options
        try:
            parsed = ast.literal_eval(options)
        except (ValueError, SyntaxError):
            logger.warning(f"Could not parse options payload: {options!r}")
            return None
        return parsed if isinstance(parsed, list) else None

    @classmethod
    def format_payload(cls, payload: dict) -> dict:
        payload = {k: (None if v == "N/A" else v) for k, v in payload.items()}
        payload["options"] = cls._parse_options(payload.get("options"))
        correct_answer = payload.get("correct_answer")
        payload["correct_answer_letter"] = correct_answer.strip()[-1] if correct_answer and correct_answer.strip() else None
        for key in ("year", "subject", "exam_type"):
            if payload.get(key) is not None:
                payload[key] = str(payload[key])
        return payload

    def embed(self, text: str) -> list[float]:
        return next(iter(self.model.embed([text]))).tolist()

    def build_filter(self, search_request: SearchRequest) -> models.Filter | None:
        filters = []
        for search_item in search_request.search_items or []:
            conditions = [models.FieldCondition(key="subject", match=models.MatchValue(value=search_item.subject))]
            if search_item.years:
                conditions.append(models.FieldCondition(key="year", match=self._get_match(search_item.years)))
            filters.append(models.Filter(must=conditions))
        return models.Filter(should=filters) if filters else None

    def search(self, text: str, search_request: SearchRequest) -> list[dict]:
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=self.embed(text),
            score_threshold=settings.SEARCH_SCORE_THRESHOLD,
            query_filter=self.build_filter(search_request),
            limit=settings.SEARCH_LIMIT,
        ).points

        return [self.format_payload(hit.payload or {}) for hit in search_result]

    def close(self):
        self.qdrant_client.close()
