from app.services.base_scraper import BaseScraperStrategy


class SubjectScraperStrategy(BaseScraperStrategy):

    async def _parse(self, url, **kwargs):
        """Extract subjects from the soup."""
        soup = await self._fetch(url=url)
        results = soup.select('div h5 a')
        subjects = [(i.get_text().strip(), i.get('href')) for i in results]
        return subjects
