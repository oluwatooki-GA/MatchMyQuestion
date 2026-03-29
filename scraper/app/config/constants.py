from pathlib import Path

from app.services.exam_info_scraper import ExamInfoScraperStrategy
from app.services.question_scraper import QuestionScraperStrategy
from app.services.question_urls_scraper import QuestionUrlsScraperStrategy
from app.services.subject_scraper import SubjectScraperStrategy

URL = "https://myschool.ng/classroom"

SUBJECTS_FILENAME = Path("subjects.json")
EXAM_INFO_FILENAME = Path("exam_info.json")
QUESTION_URLS_FILENAME = Path("question_urls.json")
RESULTS_FILENAME = Path("final_result.json")
DEFAULT_STORAGE_FOLDER = 'results0'

SCRAPERS = {
    "subject": SubjectScraperStrategy,
    "exam_info": ExamInfoScraperStrategy,
    "question_urls": QuestionUrlsScraperStrategy,
    "question_data": QuestionScraperStrategy,
}