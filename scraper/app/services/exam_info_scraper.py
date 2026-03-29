import asyncio
from app.model_schemas.schemas import ExamInfo, YearInfo
from app.services.base_scraper import BaseScraperStrategy


class ExamInfoScraperStrategy(BaseScraperStrategy):
    async def scrape(self):
        tasks = [asyncio.create_task(self._parse(url=url,subject=subject)) for subject,url in self.scraping_metadata]
        results = await self.get_results(label="Scraping Exam Info", tasks=tasks)
        return results

    async def _parse(self,url,**kwargs):
        subject = kwargs.get('subject')
        soup = await self._fetch(url=url)
        exam_years = soup.select('select[name=exam_year] option', limit=6)
        exam_years = [x.get('value') for x in exam_years if x.get('value')]

        if not exam_years:
            return ExamInfo(years=[], subject=subject, url=url)

        years_pages = []
        for year in exam_years:
            year_soup = await self._fetch(url=url + f"?exam_type=&exam_year={year}&type=&topic=")
            pagination_urls = year_soup.select('ul.pagination.flex-wrap li')
            pages = pagination_urls[-2].get_text() if pagination_urls else 1
            years_pages.append(YearInfo(year=int(year), page_nums=int(pages)))
        return ExamInfo(years=years_pages, subject=subject, url=url)
