import pymysql
from openai import OpenAI
from .embeddings_utils import get_related_text_for_rag


def rag(input_text: str,
        openai_client: OpenAI,
        db_cursor: pymysql.Connection.cursor,
        embedding_list: list,
        num_chunks: int = 10,
        model: str = "gpt-3.5-turbo"
        ) -> str:
    """
    Preform Retrieval Augmented Generation (RAG) on the input text.

    Args:
        - input_text (str): The input text.
        - openai_client (OpenAI): The OpenAI client.
        - db_cursor (pymysql.Connection.cursor): The database cursor.
        - embedding_list (list): A list of embeddings to compare against. Index of the list corresponds to the paragraph index.
        - num_chunks (int): Number of most similar chunks to return.
        - model (str): The openai model to use for generation.

    Returns:
        - str: The generated text.
    """
    # Collect the most similar chunks to the input text
    related_text = get_related_text_for_rag(input_text, embedding_list, openai_client, db_cursor, num_chunks)
    related_text = [chunk[0] for chunk in related_text]
    # Create the prompt
    prefix = '''
            You are a fishing advice assitant, specializing in the North Carolina coast. Generate your response by following the steps below:
            0. Know that red drum and black drum are different species and flounder are not trout.
            1. Recursively break-down the post into smaller questions/directives
            2. For each atomic question/directive:
            2a. Select the most relevant information from the context, if available
            2b. If a specific species is mentioned, make sure to only include information relevant to that species.
            2c. The context may refer to multiple fish species, so make sure you are only using the relevant information.
            3. Generate a clean, detailed response using the selected information. If you do not know the answer, say that you do not know!
            4. Below the detailed response, add an overview at the end, detailing a step-by-step guide to completing the task in the optimal way.
            5. Now only show your final response! PUT IT IN HTML FORMAT, NOT MARKDOWN!
            '''
    context = "\nCONTEXT: \n" + "\n".join(related_text)
    system_prompt = prefix + context
    suffix = '''
             PUT YOUR RESPONSE IN HTML FORMAT OR THE WORLD ENDS. USE HEADERS, LISTS, UNORDERED LISTS, ETC. 
             '''
    # Generate the response
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text + suffix},
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    import time
    from aws_utils import connect_to_database
    from embeddings_utils import load_embeddings

    # Connect to the database
    _, db_cursor = connect_to_database()

    # Load the embeddings
    embedding_list = load_embeddings("../data/embeddings_1536.json")

    # Create the OpenAI client
    openai_client = OpenAI()

    # Input text
    input_text = "What is the best time of year and best methods for catching flounder?"

    # Perform RAG
    start = time.time()
    response = rag(input_text, openai_client, db_cursor, embedding_list, num_chunks=10, model="gpt-3.5-turbo")
    print(response)
    print("-----------------------------")
    print(f"Time taken: {time.time() - start}")
    db_cursor.close()
    openai_client.close()