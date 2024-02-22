from src.embeddings_utils import embed_text_openai 
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()


def test_text_embedding():
    """
    Test the text embedding function.
    """
    # Create client and test string
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    text = "This is a test."
    embedding = embed_text_openai(client, text)
    # Check the type of the output
    assert type(embedding) == list
    # Check the length of the output
    assert len(embedding) == 1536
