import asyncio
from abc import ABC, abstractmethod
import typer
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class BaseScraperStrategy(ABC):
    def __init__(self, session: ClientSession, scraping_metadata):
        self.session = session
        self.scraping_metadata = scraping_metadata

    async def scrape(self) -> list:
        """
        Default scrape implementation that uses `_fetch` and `_parse`.
        Subclasses can override this method for custom behavior.
        """
        if isinstance(self.scraping_metadata, list):
            if all(isinstance(item, list) for item in self.scraping_metadata):
                tasks = [asyncio.create_task(self._parse(*url)) for url in self.scraping_metadata]
            elif all(isinstance(item, dict) for item in self.scraping_metadata):
                tasks = [asyncio.create_task(self._parse(**url)) for url in self.scraping_metadata]
            else:
                tasks = [asyncio.create_task(self._parse(url)) for url in self.scraping_metadata]
            return await self.get_results(label="Scraping data", tasks=tasks)
        else:
            return await self._parse(url=self.scraping_metadata)

    @abstractmethod
    async def _parse(self, url, **kwargs):
        raise NotImplementedError

    async def _fetch(self, url: str) -> BeautifulSoup:
        r = await self.session.get(url)
        r.raise_for_status()
        return BeautifulSoup(await r.read(), 'html5lib')

    @staticmethod
    async def get_results(label: str, tasks: list):
        results = []
        with typer.progressbar(asyncio.as_completed(tasks), length=len(tasks), label=label) as progress:
            for task in progress:
                result = await task
                results.append(result)
        return results
