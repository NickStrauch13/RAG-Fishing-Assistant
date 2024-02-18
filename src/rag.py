import pymysql
from openai import OpenAI
from embeddings_utils import get_related_text_for_rag


def rag(input_text: str,
        openai_client: OpenAI,
        db_cursor: pymysql.Connection.cursor,
        embedding_list: list,
        num_chunks: int = 5,
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
            0. If the prompted task is not related to fishing, say that you cannot assist with that type of request, then skip all other steps.
            1. Recursively break-down the post into smaller questions/directives
            2. For each atomic question/directive:
            2a. Select the most relevant information from the context, if available
            3. Generate a draft response using the selected information. If you do not know the answer, say that you do not know!
            4. Remove duplicate content from the draft response
            5. Generate your final response after adjusting it to increase accuracy and relevance
            6. Add an overview at the end, detailing a step-by-step guide to completing the task in the optimal way.
            7. Now only show your final response!
            '''
    context = "\nCONTEXT: \n" + "\n".join(related_text)
    system_prompt = prefix + context
    # Generate the response
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
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