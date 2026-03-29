from app.config.constants import DEFAULT_STORAGE_FOLDER
from app.services.database_service import DatabaseService
from app.config.settings import Settings
from app.utils.helpers import read_json
from pathlib import Path
import typer

db_app = typer.Typer()


@db_app.command(help="Sets up the database by creating tables for the specified environment.")
def setup_db(
        environment: str = typer.Option(
            'dev',
            "--environment",
            "-e",
            help="Specify the environment for database setup: 'dev' for development or 'prod' for production. Default is 'dev'."
        )
):
    """
    Sets up the database by first deleting then creating necessary tables based on the specified environment.

    The `environment` option allows you to choose between a development or production environment.
    The default environment is 'dev'.
    """
    settings = Settings.load_environment(environment)
    db = DatabaseService(settings)
    db.create_tables()
    typer.secho("Database tables created successfully.", fg=typer.colors.GREEN)


@db_app.command(name='db-save', help="Saves results from the input file to the database.")
def save_results_to_db(
        input_file: str,
        folder: str = typer.Option(
            DEFAULT_STORAGE_FOLDER,
            help="The folder where input data is stored. Defaults to the predefined storage folder."
        ),
        environment: str = "dev"
):
    """
    Saves the results from the specified input file into the database.

    This command reads data from a JSON file located in the specified folder and stores it in the database.
    You can specify the environment for the database connection (default is 'dev').
    """
    settings = Settings.load_environment(environment)
    db = DatabaseService(settings)
    results = read_json(Path(input_file), Path(folder))
    db.create_entries(results)
    typer.secho("Results saved to the database successfully.", fg=typer.colors.GREEN)
