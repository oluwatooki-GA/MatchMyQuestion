import typer
from sqlmodel import SQLModel, create_engine, Session, select
from app.model_schemas.question_and_answer_models import Questions_And_Answers


class DatabaseService:
    def __init__(self, settings):
        """
        Initialize the DatabaseService with settings for the database connection.

        Args:
            settings: An object containing database configuration (username, password, host, port, database name).
        """
        self.database_url = (
            f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}"
            f"@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
        )
        self.engine = create_engine(self.database_url)

    def create_tables(self):
        """
        Drop and recreate all tables in the database based on the SQLModel metadata.
        """
        SQLModel.metadata.drop_all(self.engine)
        SQLModel.metadata.create_all(self.engine)

    def create_entries(self, questions_data):
        """
        Insert multiple entries into the database, replacing `None` values with 'N/A', except for the 'id' field.

        Args:
            questions_data: A list of dictionaries representing questions and answers data to be inserted.
        """

        def replace_none_with_na(data):
            return {key: ('N/A' if value is None and key != 'id' else value) for key, value in data.items()}
        # questions_data = [x.model_dump() for x in questions_data]
        with Session(self.engine) as session:
            for data in questions_data:
                if data:
                    cleaned_data = replace_none_with_na(data)
                    question_entry = Questions_And_Answers(**cleaned_data)
                    session.add(question_entry)
            session.commit()
            typer.echo("Entries successfully added to the database.")

    def read_database(self):
        """
        Read all entries from the database and return them.

        Returns:
            A list of Questions_And_Answers objects from the database.
        """
        with Session(self.engine) as session:
            return session.exec(select(Questions_And_Answers)).all()

    def get_entries(self) -> list[dict]:
        """
        Retrieve entries from the database as a list of dictionaries, excluding 'url' and 'id' fields.

        Returns:
            A list of dictionaries representing the data in the database.
        """
        with Session(self.engine) as session:
            query_result = session.exec(select(Questions_And_Answers)).all()
            return [item.model_dump(exclude={'url', 'id'}) for item in query_result]
