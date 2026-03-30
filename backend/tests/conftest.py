import pytest
from fastapi.testclient import TestClient
from app.config.settings import settings
from app.main import app
from app.services.neural_search_service import NeuralSearcherService


def get_subject_year_info() -> dict:
    return {"Accounts - Principles of Accounts": ["2023", "2022", "2020", "2021", "2019"],
            "Agricultural Science": ["2019", "2022", "2020", "2021", "2023"],
            "Animal Husbandry": ["2021", "2020", "2019", "2023", "2022"],
            "Biology": ["2021", "2022", "2019", "2020", "2023"],
            "Catering Craft Practice": ["2022", "2018", "2020", "2019", "2021"],
            "Chemistry": ["2019", "2022", "2023", "2021", "2020"],
            "Christian Religious Knowledge (CRK)": ["2019", "2022", "2020", "2021", "2023"],
            "Civic Education": ["2023", "2022", "2020", "2021", "2019"],
            "Commerce": ["2020", "2023", "2019", "2021", "2022"],
            "Computer Studies": ["2022", "2021", "2020", "2019", "2023"],
            "Data Processing": ["2022", "2019", "2023", "2021", "2020"],
            "Economics": ["2023", "2019", "2022", "2021", "2020"],
            "English Language": ["2021", "2020", "2023", "2019", "2022"], "Fine Arts": ["2018"],
            "French": ["2011", "2010"],
            "Further Mathematics": ["2020", "2019", "2022", "2021", "2023"],
            "Geography": ["2023", "2020", "2019", "2022", "2021"],
            "Government": ["2022", "2019", "2020", "2021", "2023"], "History": ["2023", "2022", "2020", "2021", "2019"],
            "Insurance": ["2017", "2014", "2016", "2018", "2015"],
            "Islamic Religious Knowledge (IRK)": ["2020", "2019", "2021", "2022", "2023"],
            "Literature in English": ["2021", "2022", "2023", "2020", "2019"],
            "Marketing": ["2020", "2021", "2023", "2019", "2022"],
            "Mathematics": ["2020", "2021", "2019", "2022", "2023"], "Music": ["2018"],
            "Office Practice": ["2020", "2019", "2021"],
            "Physical Education": ["2023", "2022"], "Physics": ["2023", "2022", "2021", "2019", "2020"]}


class MockRedis:
    def __init__(self):
        self.store = {}

    def get(self, name: str):
        return self.store.get(name)

    def set(self, name: str, value: str,ex:int):
        self.store[name] = value

    def close(self):
        self.store.clear()


@pytest.fixture()
def mock_redis():

    return MockRedis


@pytest.fixture()
def mock_get_subject_year_info():
    return get_subject_year_info


@pytest.fixture()
def client(mock_redis,mock_get_subject_year_info):

    app.state.subject_years = mock_get_subject_year_info()
    app.state.redis = mock_redis()
    app.state.neural_search_service = NeuralSearcherService(settings.QDRANT_COLLECTION_NAME)

    client = TestClient(app,base_url="http://testserver/api/v1")

    yield client

    app.state.redis.close()
