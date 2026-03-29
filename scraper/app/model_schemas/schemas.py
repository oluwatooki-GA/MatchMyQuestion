from pydantic import BaseModel, HttpUrl


class YearInfo(BaseModel):
    year: int
    page_nums: int


class ExamInfo(BaseModel):
    years: list[YearInfo] | None
    subject: str
    url: str | HttpUrl
