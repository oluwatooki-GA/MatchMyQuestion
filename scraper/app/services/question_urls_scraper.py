import asyncio
import itertools

from app.model_schemas.schemas import ExamInfo
from app.services.base_scraper import BaseScraperStrategy


class QuestionUrlsScraperStrategy(BaseScraperStrategy):
    async def scrape(self):
        tasks = []
        for item in self.scraping_metadata:
            item: ExamInfo
            subject = item.subject
            for year in item.years:
                for page in range(1, year.page_nums + 1):
                    tasks.append(asyncio.create_task(self._parse(url=item.url, page=page, year=year.year, subject=subject)))

        question_urls = await self.get_results(label="Scraping Question scraping_metadata",tasks=tasks)
        question_urls = list(itertools.chain.from_iterable(question_urls))
        question_urls.sort(key=lambda x: x['subject'])
        question_urls_grouped_by_subject = itertools.groupby(question_urls, key=lambda x: x['subject'])
        grouped_data = [{'subject': subject, 'scraping_metadata': list(group)} for subject, group in
                        question_urls_grouped_by_subject]
        return grouped_data

    async def _parse(self, url, **kwargs) -> list:
        subject = kwargs.get('subject')
        year = kwargs.get('year')
        page = kwargs.get('page')
        soup = await self._fetch(url=url + f"?exam_year={year}&page={page}")
        question_urls = soup.select('div.media-body a.btn-outline-danger')
        result = [{'url': url.get('href'), 'subject': subject} for url in question_urls]
        return result
