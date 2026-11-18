from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SearchItem(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    years: Optional[list[str]] = Field(default=None, max_length=50)


class SearchRequest(BaseModel):
    q: str = Field(min_length=1, max_length=1000)
    search_items: Optional[list[SearchItem]] = Field(default=None, max_length=100)

    @field_validator("q")
    @classmethod
    def q_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("q must not be blank")
        return value


class SearchResultItem(BaseModel):
    question: str
    options: Optional[list] = None
    correct_answer: Optional[str] = None
    correct_answer_letter: Optional[str] = None
    explanation_html: Optional[str] = None
    subject: str
    exam_type: str
    year: str
    image_url: Optional[str] = None


class SearchResult(BaseModel):
    result: list[SearchResultItem] | None
