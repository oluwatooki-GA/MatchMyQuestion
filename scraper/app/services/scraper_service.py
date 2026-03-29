from pathlib import Path
from typing import Any, Type
import typer
from aiohttp import ClientSession
from app.services.base_scraper import BaseScraperStrategy
from app.utils.helpers import file_exists, read_json, save_to_json, retry_on_error


class ScraperService:
    def __init__(self, folder: Path, scrapers: dict[str, Type[BaseScraperStrategy]]):
        self.folder = folder
        self.scrapers = scrapers
        self.current_scraper: Type[BaseScraperStrategy] | None = None

    def set_scraper(self, scraper_name: str):
        if scraper_name not in self.scrapers:
            raise ValueError(f"Scraper '{scraper_name}' not found in scrapers.")
        self.current_scraper = self.scrapers[scraper_name]

    @retry_on_error()
    async def execute(self, *, session: ClientSession, default_filename: Path, scraping_metadata) -> Any:
        if not self.current_scraper:
            raise ValueError("Scraper strategy is not set")

        filename = typer.prompt(
            f'Enter the file name to load or save the '
            f'{str(default_filename).removesuffix(".json")} data. - Default:',
            default=default_filename
        )

        if file_exists(folder=self.folder, filename=filename):
            typer.secho(f"The file already exists: {filename}", fg=typer.colors.YELLOW)
            if typer.confirm("Would you like to re-scrape the data?"):
                scraper = self.current_scraper(session=session, scraping_metadata=scraping_metadata)
                result = await scraper.scrape()
                save_to_json(data=result, filename=filename, folder=self.folder)
                return result
            else:
                data = read_json(filename=filename, folder=self.folder)
                return data
        else:
            scraper = self.current_scraper(session=session, scraping_metadata=scraping_metadata)
            result = await scraper.scrape()
            save_to_json(data=result, filename=filename, folder=self.folder)
            return result
