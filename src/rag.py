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
            1. Recursively break-down the post into smaller questions/directives
            2. For each atomic question/directive:
            2a. Select the most relevant information from the context, if available
            3. Generate a draft response using the selected information. If you do not know the answer, say that you do not know!
            4. Remove duplicate content from the draft response
            5. Generate your final response after adjusting it to increase accuracy and relevance
            6. Now only show your final response!
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
    return response.choices[0].message['content']



