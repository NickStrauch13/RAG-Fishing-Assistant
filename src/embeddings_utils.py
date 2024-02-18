from sentence_transformers import SentenceTransformer
from typing import Tuple
import json
import numpy as np
import pymysql
from aws_utils import query_db
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()


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
    - list: The embedding of the input text.
    """
    # Load a pre-trained model
    model = SentenceTransformer(model_name)
    # Generate embeddings
    embeddings = model.encode(text)
    return embeddings.tolist()


def embed_text_openai(client: OpenAI, text: str, model_name: str = "text-embedding-3-small") -> list:
    """
    Embeds the input text using a pre-trained model.

    Args:
    - client (OpenAI): The OpenAI client.
    - text (str): The input text to embed.
    - model_name (str): The name of the pre-trained model to use.

    Returns:
    - dict: A dictionary with the embedding at ['data'][0]['embedding']
    """
    response = client.embeddings.create(
        input=text,
        model=model_name  
    )
    return response.data[0].embedding


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
    # Create openai client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Embed the rows
    embeddings = {}
    total_rows = len(prepared_rows)
    c = 0
    for text, id in prepared_rows:
        c += 1
        #embeddings[id] = embed_text(text)
        embeddings[id] = embed_text_openai(client, text)
        print(f"Embedding {c} of {total_rows}")
    # Save the embeddings to a json file
    with open(output_file, "w") as f:
        json.dump(embeddings, f)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
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


def find_most_similar_chunks(input_text_embedding: np.ndarray, chunk_embeddings: list, top_n: int = 5) -> list:
    """
    Finds the most similar paragraphs to the input text using matrix operations.

    Args:
    - input_text_embedding (np.ndarray): Embedding of the input text.
    - chunk_embeddings (list of np.ndarray): Embeddings of paragraphs to compare against.
    - top_n (int): Number of most similar paragraphs to return.

    Returns:
    - list of tuples: A list of tuples containing the index of the paragraph and its similarity score.
    """
    input_text_embedding = np.array(input_text_embedding).reshape(1, -1)
    chunk_embeddings_matrix = np.array(chunk_embeddings)

    # Normalize the embeddings to unit length
    input_text_embedding /= np.linalg.norm(input_text_embedding, axis=1, keepdims=True)
    chunk_embeddings_matrix /= np.linalg.norm(chunk_embeddings_matrix, axis=1, keepdims=True)

    # Compute cosine similarities using dot product
    similarities = np.dot(input_text_embedding, chunk_embeddings_matrix.T).flatten()

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


def get_related_text_for_rag(input_text: str, 
                             embedding_list: list, 
                             openai_client: OpenAI, 
                             db_cursor: pymysql.Connection.cursor,
                             top_n: int = 5) -> list:
    """
    Gets the most similar paragraphs to the input text.

    Args:
    - input_text (str): The input text.
    - embedding_list (list): A list of embeddings to compare against. Index of the list corresponds to the paragraph index.
    - openai_client (OpenAI): The OpenAI client.
    - top_n (int): Number of most similar chunks to return.

    Returns:
    - related_text (list): A list of tuples containing the formatted text chunks and its similarity score.
    """
    # Embed the input text
    input_text_embedding = embed_text_openai(openai_client, input_text)
    # Find the most similar paragraphs
    most_similar = find_most_similar_chunks(input_text_embedding, embedding_list, top_n=top_n)
    # Get the text from the DB
    related_text = []
    for idx, sim in most_similar:
        # Shift the index by 1 to match the database (db is 1-indexed  :/)
        shifted_idx = idx + 1
        query = f"SELECT paragraph, month, year, city FROM raw_paragraphs WHERE id={shifted_idx}"
        records = query_db(db_cursor, query)
        formatted_text = f"{records[0][0]} Location: {records[0][3]}, Month: {records[0][1]}, Year: {records[0][2]}"
        related_text.append((formatted_text, sim))
    return related_text



if __name__ == "__main__":
    import time
    from aws_utils import connect_to_database

    # Create connections
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    conn, cursor = connect_to_database()

    # load the embeddings
    embedding_dict = load_embeddings("../data/embeddings_1536.json")
    embedding_list = [embedding_dict[str(i)] for i in range(1, len(embedding_dict)+1)]

    start = time.time()
    # Find and print the most similar paragraphs
    input_text = "Where is the best place to target pompano?"
    related_text = get_related_text_for_rag(input_text, embedding_list, client, cursor, top_n=5)
    for text, sim in related_text:
        print(f"{text}\nSimilarity: {sim}")
        print("-"*50)

    time_taken = time.time() - start
    print(f"Time taken: {time_taken} seconds")
    
    




