from src.embeddings_utils import embed_text_openai 


def test_text_embedding():
    """
    Test the text embedding function.
    """
    # Define the input text
    text = "This is a test."
    # Embed the text
    embedding = embed_text_openai(text)
    # Check the type of the output
    assert type(embedding) == list
    # Check the length of the output
    assert len(embedding) == 1536
