import pytest
from qdrant_client import models

from app.schemas.search_schema import SearchItem, SearchRequest, SearchResult
from app.services.neural_search_service import NeuralSearcherService
from app.services.search_service import SearchService
from tests.conftest import FakeNeuralSearch, MockRedis


def test_search_returns_formatted_results(client):
    response = client.post("/search", json={"q": "lungs", "search_items": [{"subject": "Biology", "years": ["2022"]}]})
    assert response.status_code == 200
    result = SearchResult(**response.json()).result
    assert result[0].options == ["A. Digestion", "B. Gas exchange", "C. Excretion", "D. Support"]
    assert result[0].correct_answer_letter == "B"
    assert result[0].image_url is None


def test_search_no_results(client, fake_search):
    fake_search.payloads = []
    response = client.post("/search", json={"q": "nothing matches"})
    assert response.status_code == 200
    assert response.json() == {"result": None}


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"q": ""},
        {"q": "   "},
        {"q": "x" * 1001},
        {"q": "lungs", "search_items": [{"subject": ["Biology"], "years": "2022"}]},
    ],
)
def test_search_invalid_requests(client, body):
    assert client.post("/search", json=body).status_code == 422


def test_cache_is_used_for_equivalent_queries(client, fake_search):
    body1 = {"q": "Lungs  function", "search_items": [{"subject": "Biology", "years": ["2022", "2021"]}]}
    body2 = {"q": "lungs function", "search_items": [{"subject": "Biology", "years": ["2021", "2022"]}]}
    assert client.post("/search", json=body1).status_code == 200
    assert client.post("/search", json=body2).status_code == 200
    assert len(fake_search.calls) == 1


def test_search_works_without_redis(fake_search):
    service = SearchService(redis_client=None, neural_search_service=fake_search)
    assert service.search(SearchRequest(q="lungs")).result


def test_redis_failure_does_not_break_search(fake_search):
    from redis import RedisError

    class BrokenRedis(MockRedis):
        def get(self, name):
            raise RedisError("down")

        def set(self, name, value, ex):
            raise RedisError("down")

    service = SearchService(redis_client=BrokenRedis(), neural_search_service=fake_search)
    assert service.search(SearchRequest(q="lungs")).result


@pytest.mark.parametrize(
    "options, expected",
    [("['A. x', 'B. y']", ["A. x", "B. y"]), (["A. x"], ["A. x"]), ("N/A", None), ("not a list(", None), (None, None)],
)
def test_format_payload_options(options, expected):
    payload = NeuralSearcherService.format_payload({"question": "q", "options": options, "correct_answer": None})
    assert payload["options"] == expected
    assert payload["correct_answer_letter"] is None


def test_build_filter():
    service = NeuralSearcherService.__new__(NeuralSearcherService)
    assert service.build_filter(SearchRequest(q="x")) is None
    f = service.build_filter(SearchRequest(q="x", search_items=[
        SearchItem(subject="Biology", years=["2022"]),
        SearchItem(subject="Physics", years=["2021", "2022"]),
        SearchItem(subject="Chemistry"),
    ]))
    assert len(f.should) == 3
    assert isinstance(f.should[0].must[1].match, models.MatchValue)
    assert isinstance(f.should[1].must[1].match, models.MatchAny)
    assert len(f.should[2].must) == 1


def test_rate_limit_uses_forwarded_ip(client):
    for _ in range(5):
        assert client.post("/search", json={"q": "a"}, headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.post("/search", json={"q": "a"}, headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 429
    assert client.post("/search", json={"q": "a"}, headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200
