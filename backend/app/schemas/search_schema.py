from typing import Optional, List
from pydantic import BaseModel


class SearchItem(BaseModel):
    subject: str
    years: Optional[list[str]] = None


class SearchRequest(BaseModel):
    q: str
    search_items: Optional[list[SearchItem]] = None


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
