from app.commands.scraper_commands import scraper_app, scrape
from app.commands.qdrant_commands import qdrant_app, upload_to_qdrant
from app.config.constants import DEFAULT_STORAGE_FOLDER, RESULTS_FILENAME
import typer
from pathlib import Path

app = typer.Typer(help="""
📚 Question CLI Application

A tool to scrape questions and upload them to Qdrant for semantic search.

 Features:

1. Scraping:
   - Extract question-answer pairs from myschool.ng

2. Qdrant Uploading:
   - Upload embeddings of question-answer pairs to Qdrant

3. Local Data Management:
   - Save question-answer pairs to JSON files for backup

 Usage:

- Use the `--help` option with any command to get specific details, e.g., `python app.py <command> --help`.

 Example Commands:
- `scrape` - Scrape question-answer pairs to JSON files
- `upload` - Upload JSON data to Qdrant
- `run-all` - Run the complete pipeline: scrape and upload

""")


@app.command(help="Run the complete pipeline: scrape and upload to Qdrant.")
def run_all(
    folder: str = typer.Option(
        DEFAULT_STORAGE_FOLDER,
        "--folder",
        "-f",
        help="The folder where scraped results will be stored."
    ),
    environment: str = typer.Option(
        'dev',
        "--environment",
        "-e",
        help="Environment: 'dev' or 'prod'. Default is 'dev'."
    ),
    payload_indexes: list[str] = typer.Option(
        ["subject", "year"],
        "--payload-indexes",
        "-p",
        help="Payload indexes for Qdrant collection."
    ),
    collection_name: str = typer.Option(
        "questions",
        "--collection-name",
        "-c",
        help="Qdrant collection name."
    )
):
    """
    Run the complete pipeline: scrape data and upload to Qdrant.
    """
    typer.secho(f"🚀 Starting complete pipeline in {environment} environment...\n", fg=typer.colors.CYAN)

    # Step 1: Scrape data
    typer.secho("Step 1/2: Scraping data...", fg=typer.colors.CYAN)
    scrape(folder=folder, auto=True)

    # Step 2: Upload to Qdrant
    typer.secho("\nStep 2/2: Uploading to Qdrant...", fg=typer.colors.CYAN)
    upload_to_qdrant(
        input_file=str(RESULTS_FILENAME),
        folder=folder,
        collection_name=collection_name,
        payload_indexes=payload_indexes,
        environment=environment
    )

    typer.secho("\n✅ Complete pipeline finished successfully!", fg=typer.colors.GREEN)


if __name__ == '__main__':
    app.add_typer(scraper_app)
    app.add_typer(qdrant_app)
    app()
