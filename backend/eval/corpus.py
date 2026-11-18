"""Load the question corpus from the scraper's JSON output or straight from Qdrant."""
import json
from pathlib import Path


def from_json(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list of question records")
    return data


def from_qdrant(collection: str | None = None, batch: int = 1000) -> list[dict]:
    from qdrant_client import QdrantClient

    from app.config.settings import settings

    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None, timeout=60)
    records, offset = [], None
    while True:
        points, offset = client.scroll(
            collection_name=collection or settings.QDRANT_COLLECTION_NAME,
            limit=batch, offset=offset, with_payload=True, with_vectors=False,
        )
        records.extend(p.payload for p in points)
        if offset is None:
            break
    client.close()
    return records
