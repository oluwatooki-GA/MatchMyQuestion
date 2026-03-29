from app.model_schemas.schemas import ExamInfo
from app.services.scraper_service import ScraperService
from app.config.constants import *
from app.utils.helpers import save_to_json
from pathlib import Path
import typer
import asyncio
import aiohttp
import os

scraper_app = typer.Typer()


@scraper_app.command(help="Scrapes data and stores the results in the specified folder.")
def scrape(
    folder: str = typer.Option(
        DEFAULT_STORAGE_FOLDER,
        help="The folder where scraped results will be stored. Defaults to the predefined storage folder."
    ),
    auto: bool = typer.Option(
        False,
        "--auto",
        "-a",
        help="Run automatically without prompts for confirmation."
    )
):
    """
    Scrapes data and saves the results in the specified folder.

    This command retrieves data from a predefined source and stores it in a local folder for further processing.
    """
    async def pipeline():
        typer.echo("Initializing the scraping pipeline...")
        os.makedirs(Path(__file__).resolve().parent.parent.parent / folder, exist_ok=True)

        scraper_service = ScraperService(folder=Path(folder), scrapers=SCRAPERS)

        async with aiohttp.ClientSession() as session:
            typer.secho('\nStep 1. Retrieving subjects and their corresponding scraping_metadata', fg=typer.colors.CYAN)
            scraper_service.set_scraper("subject")
            subject_urls = await scraper_service.execute(session=session, default_filename=SUBJECTS_FILENAME,
                                                         scraping_metadata=URL)

        async with aiohttp.ClientSession() as session:
            typer.secho(
                '\n\nStep 2. Retrieving subject information such as the last 5 years available and the number of pages per year',
                fg=typer.colors.CYAN)
            scraper_service.set_scraper("exam_info")
            exam_info = await scraper_service.execute(session=session, default_filename=EXAM_INFO_FILENAME,
                                                      scraping_metadata=subject_urls)

            if isinstance(exam_info, list) and all(isinstance(item, dict) for item in exam_info):
                exam_info = [ExamInfo(**item) for item in exam_info]

        async with aiohttp.ClientSession() as session:
            typer.secho(
                '\n\nStep 3. Retrieving all the Question urls (The Question urls with the question options, explanations, etc) based on the exam-info from the previous step',
                fg=typer.colors.CYAN)
            scraper_service.set_scraper("question_urls")
            urls = await scraper_service.execute(session=session, default_filename=QUESTION_URLS_FILENAME,
                                                 scraping_metadata=exam_info)

            total_questions = sum([len(x['scraping_metadata']) for x in urls])
            typer.secho(
                f'Question scraping_metadata retrieval has been completed successfully, there are {total_questions} Total Questions',
                fg=typer.colors.GREEN)

        typer.secho(
            '\n\nStep 4. Retrieving all Question data the process Question Data for every Subject based on the question data scraping_metadata from the previous step',
            fg=typer.colors.CYAN)

        all_results = []
        scraper_service.set_scraper("question_data")
        for subject_data in urls:
            typer.echo(f'Processing with {subject_data["subject"]}')
            subject = subject_data['subject']
            filename = subject + '_data.json'
            if auto or typer.confirm(f'Do you want to scrape {subject}?'):
                async with aiohttp.ClientSession() as session:
                    result = await scraper_service.execute(session=session, default_filename=filename,
                                                           scraping_metadata=subject_data)
                all_results.extend(result)
                typer.secho(f'Done retrieving {subject} data\n\n', fg=typer.colors.BRIGHT_GREEN)
            else:
                typer.secho(f'Skipped {subject} data\n\n', fg=typer.colors.YELLOW)
        if auto or typer.confirm('Do you want to save all the results into a single file?'):
            result_filename = RESULTS_FILENAME if auto else typer.prompt('Where should we save the final result file? -  default:', RESULTS_FILENAME)
            save_to_json(data=all_results, filename=result_filename, folder=Path(folder))
        typer.secho('Scraping Pipeline Complete',fg=typer.colors.GREEN)
    asyncio.run(pipeline())
