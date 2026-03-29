from pathlib import Path

from app.config.constants import DEFAULT_STORAGE_FOLDER
from app.qdrant.qdrant_uploader import QdrantUploader
from app.services.database_service import DatabaseService
from app.config.settings import Settings
import typer

from app.utils.helpers import read_json

qdrant_app = typer.Typer()


@qdrant_app.command(name='qdrant-upload', help="Upload data to a Qdrant collection.")
def upload_to_qdrant(
        collection_name: str = typer.Option(...,
                                            help="The name of the Qdrant collection to which data will be uploaded."),
        payload_indexes: list[str] = typer.Option(...,
                                                  help="List of field names to create as payload indexes in the collection."),
        input_file: str = typer.Option(None,
                                       help="Path to a JSON file containing the input data. If not provided, data is fetched from the database."),
        folder: str = typer.Option(DEFAULT_STORAGE_FOLDER, help="Folder the input file is located at. If there is no input_file this is ignored"),
        environment: str = typer.Option(
            'dev',
            "--environment",
            "-e",
            help="Specify the environment in which to run: 'dev' (default) or 'prod'."
        ),
):
    """
    Upload data to a Qdrant collection.

    This command processes data (either from a database or a specified input file),
    encodes it into vectors using a SentenceTransformer model, and uploads it to
    the specified Qdrant collection. Additionally, it sets up payload indexes for
    efficient retrieval.

    Example:
        qdrant-upload --collection-name my_collection --payload-indexes field1 field2 -e prod
    """
    settings = Settings.load_environment(environment)
    typer.echo(f'Running In {environment} environment')
    db = DatabaseService(settings)

    QdrantUploader(
        api_key=settings.QDRANT_API_KEY,
        qdrant_url=settings.QDRANT_URL,
        collection_name=collection_name,
        entries_provider=db if not input_file else None,
        input_data=read_json(Path(input_file),Path(folder)) if input_file else None,
        payload_indexes=payload_indexes
    ).process_and_upload()
    typer.secho("Data uploaded to Qdrant", fg=typer.colors.GREEN)
