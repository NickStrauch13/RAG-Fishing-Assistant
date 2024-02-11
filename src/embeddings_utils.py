from sentence_transformers import SentenceTransformer
from typing import Tuple
import json
import numpy as np


def prepare_db_row_for_embedding(row: tuple) -> Tuple[str, int]:
    """
    Prepares a database row for embedding by concatenating the text fields.

    Args:
    - row (tuple): A tuple containing the fields of a database row.

    Returns:
    - str: The concatenated string of the fields.
    - int: The id of the row.
    """
    body, location, month, year, id = row
    return f"{body} Location: {location}, Month: {month}, Year: {year}", id


def embed_text(text: str, model_name: str = "all-mpnet-base-v2") -> list:
    """
    Embeds the input text using a pre-trained model.

    Args:
    - text (str): The input text to embed.
    - model_name (str): The name of the pre-trained model to use.

    Returns:
    - list: A list of vectors, one for each paragraph in the input text.
    """
    # Load a pre-trained model
    model = SentenceTransformer(model_name)
    # Generate embeddings
    embeddings = model.encode(text)
    return embeddings


def embed_all_db_rows(rows: list, output_file: str) -> None:
    """
    Embeds a list of database rows. 
    Saves the embeddings to a json file, with id as the key and the embeddings as the value.

    Args:
    - rows (list): A list of database rows. Each list element should be the row tuple.
    - output_file (str): The name of the output file.
    """
    # Prepare the rows for embedding
    prepared_rows = [(prepare_db_row_for_embedding(row)[0],prepare_db_row_for_embedding(row)[1]) for row in rows]
    # Embed the rows
    embeddings = {}
    total_rows = len(prepared_rows)
    c = 0
    for text, id in prepared_rows:
        c += 1
        embeddings[id] = embed_text(text).tolist()
        print(f"Embedding {c} of {total_rows}")
    # Save the embeddings to a json file
    with open(output_file, "w") as f:
        json.dump(embeddings, f)


def cosine_similarity(vec1, vec2):
    """
    Computes the cosine similarity between two vectors.

    Args:
    - vec1 (np.ndarray): The first vector.
    - vec2 (np.ndarray): The second vector.

    Returns:
    - float: The cosine similarity between the two vectors.
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    similarity = dot_product / (norm1 * norm2)
    return similarity


def find_most_similar_chunks(input_text_embeddings, chunk_embeddings, top_n=5):
    """
    Finds the most similar paragraphs to the input text.

    Args:
    - input_text_embeddings (np.ndarray): Embeddings of the input text.
    - chunk_embeddings (list of np.ndarray): Embeddings of paragraphs to compare against.
    - top_n (int): Number of most similar paragraphs to return.

    Returns:
    - list of tuples: A list of tuples containing the index of the paragraph and its similarity score.
    """
    # Calculate cosine similarity between input text embeddings and paragraph embeddings
    similarities = [cosine_similarity(input_text_embeddings, emb) for emb in chunk_embeddings]
    # Get indices of top_n most similar paragraphs
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    # Create a list of tuples containing paragraph index and similarity score
    most_similar_paragraphs = [(idx, similarities[idx]) for idx in top_indices]
    return most_similar_paragraphs


def load_embeddings(file: str) -> dict:
    """
    Loads embeddings from a json file.

    Args:
    - file (str): The name of the file to load.

    Returns:
    - dict: A dictionary of embeddings.
    """
    with open(file, "r") as f:
        embeddings = json.load(f)
    return embeddings




if __name__ == "__main__":
    # load the embeddings
    embedding_dict = load_embeddings("../data/embeddings.json")

    # Put embedding_dict into a list of its values
    embedding_list = [embedding_dict[str(i)] for i in range(1, len(embedding_dict)+1)]

    # Embed the input text
    input_text = "red drum"
    input_text_embedding = embed_text(input_text)

    # Find the most similar paragraphs
    most_similar = find_most_similar_chunks(input_text_embedding, embedding_list)
    print("Found most similar chunks!")

    # Print the most similar paragraphs
    from aws_utils import connect_to_database, query_db
    conn, cursor = connect_to_database()
    for idx, sim in most_similar:
        query = f"SELECT paragraph, month, year FROM raw_paragraphs WHERE id={idx}"
        records = query_db(cursor, query)
        print(f"Similarity: {sim}")
        print(f"{records[0][0]} {records[0][1]},{records[0][2]}")
        print("-------------------------------------------------")




