import os

os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_COLLECTION_NAME", "questions")

import pytest
from fastapi.testclient import TestClient

from app.main import app, limiter


class MockRedis:
    def __init__(self):
        self.store = {}

    def get(self, name: str):
        return self.store.get(name)

    def set(self, name: str, value: str, ex: int):
        self.store[name] = value

    def close(self):
        self.store.clear()


SAMPLE_PAYLOAD = {
    "question": "What is the function of the lungs?",
    "options": "['A. Digestion', 'B. Gas exchange', 'C. Excretion', 'D. Support']",
    "correct_answer": "Correct Answer: Option B",
    "explanation_html": "<p>The lungs exchange gases.</p>",
    "explanation_text": "The lungs exchange gases.",
    "subject": "Biology",
    "exam_type": "WAEC",
    "year": "2022",
    "image_url": "N/A",
}


class FakeNeuralSearch:
    def __init__(self, payloads=None):
        self.payloads = [SAMPLE_PAYLOAD] if payloads is None else payloads
        self.calls = []

    def search(self, text, search_request):
        from app.services.neural_search_service import NeuralSearcherService
        self.calls.append((text, search_request))
        return [NeuralSearcherService.format_payload(p) for p in self.payloads]

    def close(self):
        pass


@pytest.fixture()
def fake_search():
    return FakeNeuralSearch()


@pytest.fixture()
def client(fake_search):
    limiter.reset()
    app.state.redis = MockRedis()
    app.state.neural_search_service = fake_search
    # No `with` block: the lifespan (real model + Qdrant) is not started.
    yield TestClient(app, base_url="http://testserver/api/v1")
    app.state.redis.close()
