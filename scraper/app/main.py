from app.commands.scraper_commands import scraper_app, scrape
from app.commands.database_commands import db_app, setup_db, save_results_to_db
from app.commands.qdrant_commands import qdrant_app, upload_to_qdrant
from app.config.constants import DEFAULT_STORAGE_FOLDER, RESULTS_FILENAME
import typer
from pathlib import Path

app = typer.Typer(help="""
📚 Question CLI Application

A comprehensive tool to manage, query, and upload question-answer pairs with embeddings to Qdrant, or local files. The CLI supports various operations including database setup, data scraping, Qdrant uploading, and more.

 Features:

1. Database Setup & Management:
   - Create and manage database tables for questions.
   - Save question-answer pairs to the database from a variety of sources.

2. Scraping:
   - Extract and manage question-answer pairs from structured or semi-structured sources.

3. Qdrant Uploading:
   - Upload embeddings of question-answer pairs to a Qdrant instance for efficient querying.

4. Local Data Management:
   - Save question-answer pairs to files for offline use.

 Usage:

- Use the `--help` option with any command to get specific details, e.g., `python app.py <command> --help`.

 Example Commands:
- `setup-db` - Initialize the database for storing question-answer pairs.
- `scrape` - Scrape question-answer pairs from specified sources.
- `qdrant-upload` - Upload questions with embeddings to Qdrant.
- `query` - Query questions and find similar matches based on embeddings.

Tip: Refer to the README for detailed examples and advanced configurations.

""")


@app.command(help="Run the complete pipeline: setup-db, scrape, db-save, and qdrant-upload.")
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
        help="Environment to use: 'dev' or 'prod'. Default is 'dev'."
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
    Run the complete pipeline: setup database, scrape data, save to database, and upload to Qdrant.
    """
    typer.secho("🚀 Starting complete pipeline...\n", fg=typer.colors.CYAN)

    # Step 1: Setup database
    typer.secho("Step 1/4: Setting up database...", fg=typer.colors.CYAN)
    setup_db(environment=environment)

    # Step 2: Scrape data
    typer.secho("\nStep 2/4: Scraping data...", fg=typer.colors.CYAN)
    scrape(folder=folder, auto=True)

    # Step 3: Save to database
    typer.secho("\nStep 3/4: Saving to database...", fg=typer.colors.CYAN)
    input_file = str(RESULTS_FILENAME)
    save_results_to_db(
        input_file=input_file,
        folder=folder,
        environment=environment
    )

    # Step 4: Upload to Qdrant
    typer.secho("\nStep 4/4: Uploading to Qdrant...", fg=typer.colors.CYAN)
    upload_to_qdrant(
        collection_name=collection_name,
        payload_indexes=payload_indexes,
        input_file=None,
        folder=folder,
        environment=environment
    )

    typer.secho("\n✅ Complete pipeline finished successfully!", fg=typer.colors.GREEN)


if __name__ == '__main__':
    app.add_typer(scraper_app)
    app.add_typer(db_app)
    app.add_typer(qdrant_app)
    app()
