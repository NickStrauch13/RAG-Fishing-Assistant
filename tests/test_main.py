from src.embeddings_utils import embed_text_openai
from src.aws_utils import connect_to_database, query_db
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# TODO: Setup ENV Vars in Github Actions for non-local testing

# def test_text_embedding():
#     """
#     Test the text embedding function.
#     """
#     # Create client and test string
#     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     text = "This is a test."
#     embedding = embed_text_openai(client, text)
#     # Check the type of the output
#     assert type(embedding) == list
#     # Check the length of the output
#     assert len(embedding) == 1536

# def test_connect_to_database():
#     conn, cursor = connect_to_database()
#     assert conn is not None
#     assert cursor is not None
#     cursor.close()
#     conn.close()


# def test_query_db():
#     conn, cursor = connect_to_database()
#     query = "SELECT * FROM raw_paragraphs LIMIT 10"
#     records = query_db(cursor, query)
#     assert records is not None
#     assert type(records) == tuple
#     assert len(records) == 10
#     cursor.close()
#     conn.close()


def test_null():
    """
    Stand-in test to make sure the test suite runs.
    """
    assert True