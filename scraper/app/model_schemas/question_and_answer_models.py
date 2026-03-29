from sqlmodel import SQLModel, Field
from uuid import uuid4
from pydantic import UUID4
from typing import Optional


class Questions_And_Answers(SQLModel, table=True):
    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    question: str
    options: str | None = None
    correct_answer: Optional[str] = None
    explanation_html: Optional[str] = None
    explanation_text: Optional[str] = None
    subject: str
    exam_type: str
    year: str
    url: str
    image_url: Optional[str] = None  # Optional image URL
