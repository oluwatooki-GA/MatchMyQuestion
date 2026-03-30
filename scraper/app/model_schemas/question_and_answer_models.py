from pydantic import BaseModel, Field
from typing import Optional


class Questions_And_Answers(BaseModel):
    question: str
    options: str | None = None
    correct_answer: Optional[str] = None
    explanation_html: Optional[str] = None
    explanation_text: Optional[str] = None
    subject: str
    exam_type: str
    year: str
    url: str
    image_url: Optional[str] = None
