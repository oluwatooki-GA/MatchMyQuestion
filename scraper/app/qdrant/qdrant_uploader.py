from typing import Protocol, List, Dict

import typer
from sentence_transformers import SentenceTransformer
import numpy as np
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
import pandas as pd


class EntriesProvider(Protocol):
    def get_entries(self) -> List[Dict]:
        """
        Protocol for any class providing database entries as a list of dictionaries.
        """
        ...


class QdrantUploader:
    def __init__(self, qdrant_url: str, api_key: str, collection_name: str, payload_indexes: str | list,
                 entries_provider: EntriesProvider | None, input_data: list | None):

        if not api_key:
            self.client = QdrantClient(qdrant_url)
        else:
            self.client = QdrantClient(url=qdrant_url, api_key=api_key)

        if entries_provider and input_data:
            typer.secho('You cannot use both the database entries and a custom file', fg=typer.colors.RED)
        self.collection_name = collection_name
        self.payload_indexes = payload_indexes
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        input_func = lambda: input_data
        self.get_entries = input_func if input_data else entries_provider.get_entries

    def load_data(self) -> tuple[pd.DataFrame, list[dict]]:
        """Load and prepare data from a JSON file."""
        data = self.get_entries()
        df = pd.DataFrame(data)
        return df, data

    @staticmethod
    def format_row(row):
        item = row.question
        if row.explanation_text != "N/A":
            item += ' ---- '
            item += row.explanation_text
        return item

    def encode_questions(self, dfx: pd.DataFrame) -> np.ndarray:
        """Encode questions using the SentenceTransformer model."""
        # vectors = self.model.encode(questions, show_progress_bar=True)
        vectors = self.model.encode(
            [self.format_row(row) for row in dfx.itertuples()],
            show_progress_bar=True,
        )
        return vectors

    def _create_collection(self, vector_size: int):
        """Create a Qdrant collection if it does not already exist."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        always_ram=True,
                    ),
                ),
            )
            typer.echo(f"Created collection: {self.collection_name}")

    def _create_payload_indexes(self, field_names: list[str],valid_field_names=list[str]):
        created_field_names = []
        for field_name in field_names:
            if field_name in valid_field_names:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                created_field_names.append(field_name)
            else:
                typer.secho(f'Could not create payload index for `{field_name}` because the field does not exist')
        typer.echo(f'Created payload indexes for: {created_field_names}')

    def _upload_vectors(self, vectors: np.ndarray, payload: list[dict], batch_size: int = 256):
        """Upload vectors and associated payloads to Qdrant."""
        self.client.upload_collection(
            collection_name=self.collection_name,
            vectors=vectors,
            payload=payload,
            ids=None,  # Vector ids will be assigned automatically
            # batch_size=batch_size,
        )
        typer.echo('Uploaded Vectors')

    def process_and_upload(self):
        """Complete pipeline:delete the collection, load data, encode, save vectors, and upload to Qdrant."""
        # Load and process data
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        df, payload = self.load_data()

        # Encode and save vectors
        vectors = self.encode_questions(df)

        self._create_collection(vector_size=vectors.shape[1])
        self._upload_vectors(vectors=vectors, payload=payload)
        self._create_payload_indexes(field_names=self.payload_indexes,valid_field_names=df.columns.tolist())
