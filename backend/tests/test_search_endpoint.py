import pytest
from app.schemas.search_schema import SearchResult


@pytest.mark.parametrize(
    "search_data, expected_status_code",
    [
        ({"q": "Photosynthesis"}, 200),
        ({"q": "Einstein's Theory"}, 200),
        ({"q": "Python Programming"}, 200),
    ]
)
def test_search_valid_text(client, search_data, expected_status_code):
    response = client.post("/search", json=search_data)

    assert response.status_code == expected_status_code

    result = response.json()
    assert "result" in result
    assert len(result["result"]) > 0
    SearchResult.model_validate(result)


@pytest.mark.parametrize(
    "search_data, expected_status_code",
    [
        (
                {
                    "q": "electrical conduction via gases",
                    "search_items": [
                        {
                            "subject": "Physics",
                            "years": ["2022", "2023"]
                        }
                    ]
                },

                200
        ),
        (
                {
                    "q": "What does the heart do?",
                    "search_items": [
                        {
                            "subject": "Biology",
                            "years": ["2022", "2023"]
                        },
                        {
                            "subject": "Chemistry",
                            "years": ["2021"]
                        }
                    ]
                },
                200
        ),
    ]
)
def test_search_valid_filtered(client, search_data, expected_status_code):
    """Test searching with text, subject, and years."""
    response = client.post("/search", json=search_data)
    assert response.status_code == 200

    # Extract the result and validate
    result = response.json()
    assert "result" in result
    assert len(result["result"]) > 0

    SearchResult.model_validate(result)


@pytest.mark.parametrize(
    "search_data, expected_status_code",
    [
        (
                {"q": "ssssssssssssssssssssssssssssssss"},
                404
        )
    ]
)
def test_search_no_results(client, search_data, expected_status_code):
    """Test searching for a text with no matching results."""

    response = client.post("/search", json=search_data)

    assert response.status_code == expected_status_code
    result = response.json()
    assert "detail" in result


@pytest.mark.parametrize(
    "search_data, expected_status_code",
    [
        (
                {"q": "What is the Lungs Function",
                 "search_items": [
                     {
                         "subject": ["Biology"],
                         "years": "2022"
                     }
                 ]
                 },
                422,
        )
    ]
)
def test_search_invalid_subject_or_year(client, search_data, expected_status_code):
    """Test searching with invalid subject or years."""
    response = client.post("/search", json=search_data)
    assert response.status_code == expected_status_code
