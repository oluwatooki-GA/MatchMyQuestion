import asyncio
import json
import os
import traceback
from functools import wraps
from aiohttp import ClientConnectorError
from pathlib import Path
import typer

BASE_JSON_PATH = Path(__file__).resolve().parent.parent.parent


def save_to_json(data, filename: Path, folder: Path) -> None:
    processed_data = []
    if isinstance(data, list):
        for item in data:
            if hasattr(item, 'model_dump'):
                new_item = item.model_dump()
                if 'id' in new_item.keys():
                    new_item['id'] = str(new_item['id'])
            else:
                new_item = item
            processed_data.append(new_item)
    elif hasattr(data, 'model_dump'):
        processed_data = data.model_dump()

    json_file_path = BASE_JSON_PATH / folder / filename
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
    typer.echo(f"Saved data to {json_file_path}")


def read_json(filename: Path, folder: Path):
    """Reads the content of a JSON file and returns it."""
    json_file_path = BASE_JSON_PATH / folder / filename
    try:
        typer.secho(f"Loading data from {filename}...", fg=typer.colors.GREEN)
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        typer.secho(f"Data successfully loaded from {filename}", fg=typer.colors.GREEN)
        return data
    except FileNotFoundError:
        typer.echo(f"Error: {filename} not found.")
        return None
    except json.JSONDecodeError:
        typer.echo(f"Error: Failed to decode JSON in {filename}.")
        return None


def file_exists(filename: Path, folder: Path) -> bool:
    return os.path.exists(BASE_JSON_PATH / folder / filename)


def retry_on_error(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except ClientConnectorError as e:
                    if attempt < retries:
                        typer.echo(f"Connection error encountered. {e} Retrying {attempt}/{retries}...")
                        await asyncio.sleep(delay)
                    else:
                        typer.echo(f"Connection error after {retries} retries. Skipping.")
                        raise e
                except Exception as e:
                    # Get the exception details and traceback
                    exc_type, exc_value, exc_traceback = e.__class__, e, e.__traceback__
                    traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)

                    # Extracting the last traceback entry
                    tb_last = traceback.extract_tb(exc_traceback)[-1]
                    filename = tb_last.filename
                    lineno = tb_last.lineno
                    func_name = tb_last.name

                    kwargs_copy = kwargs.copy()
                    kwargs_copy.pop('session', None)

                    typer.echo(
                        f"An error occurred in function '{func_name}' at {filename}:{lineno} "
                        f". kwargs = {kwargs_copy}"
                    )
                    raise e

        return wrapper

    return decorator
