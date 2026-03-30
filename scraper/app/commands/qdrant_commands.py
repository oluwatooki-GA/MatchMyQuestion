from pathlib import Path

from app.config.constants import DEFAULT_STORAGE_FOLDER
from app.qdrant.qdrant_uploader import QdrantUploader
from app.config.settings import Settings
import typer

from app.utils.helpers import read_json

qdrant_app = typer.Typer()


@qdrant_app.command(name='upload', help="Upload JSON data to a Qdrant collection.")
def upload_to_qdrant(
    input_file: str = typer.Option(...,
        help="Path to a JSON file containing the input data."),
    folder: str = typer.Option(DEFAULT_STORAGE_FOLDER, help="Folder the input file is located in."),
    collection_name: str = typer.Option(...,
        help="The name of the Qdrant collection to which data will be uploaded."),
    payload_indexes: list[str] = typer.Option(...,
        help="List of field names to create as payload indexes in the collection."),
    environment: str = typer.Option(
        'dev',
        "--environment",
        "-e",
        help="Environment: 'dev' or 'prod'. Default is 'dev'."
    ),
):
    """
    Upload data from a JSON file to a Qdrant collection.

    This command processes data from a JSON file,
    encodes it into vectors using a SentenceTransformer model, and uploads it to
    the specified Qdrant collection. Additionally, it sets up payload indexes for
    efficient retrieval.

    Example:
        qdrant-upload --input-file final_result.json --collection-name questions --payload-indexes subject year -e prod
    """
    settings = Settings.load(environment)
    input_data = read_json(Path(input_file), Path(folder))

    QdrantUploader(
        api_key=settings.QDRANT_API_KEY,
        qdrant_url=settings.QDRANT_URL,
        collection_name=collection_name,
        entries_provider=None,
        input_data=input_data,
        payload_indexes=payload_indexes
    ).process_and_upload()
    typer.secho("Data uploaded to Qdrant", fg=typer.colors.GREEN)
