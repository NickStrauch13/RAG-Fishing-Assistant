from aws_utils import connect_to_database, query_db
from embeddings_utils import embed_all_db_rows


def create_embeddings(output_embeddings_file: str = "../data/embeddings.json"):
    """
    Creates embeddings for all the paragraphs in the database and saves them to a json file.

    Args:
        - output_embeddings_file (str): The name of the output file.
    """
    # Connect to DB
    conn, cursor = connect_to_database()
    # Query the DB
    query = "SELECT * FROM raw_paragraphs"
    records = query_db(cursor, query)
    print("Got data!")
    # Embed the paragraphs and save the embeddings to a json file
    embed_all_db_rows(records, output_embeddings_file)
    print("Embeddings created and saved!")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_embeddings("../data/embeddings_768.json")
