from flask import Blueprint, render_template, request, g, render_template_string, jsonify
from openai import OpenAI
import os
from src.rag import rag 
from src.aws_utils import connect_to_database
from src.embeddings_utils import load_embeddings


main = Blueprint('main', __name__)

def get_db_cursor():
    if 'db' not in g:
        _, db_cursor = connect_to_database()
        g.db_cursor = db_cursor
    return g.db_cursor

def get_openai_client():
    if 'openai_client' not in g:
        g.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return g.openai_client

def get_embedding_list():
    if 'embedding_list' not in g:
        g.embedding_list = load_embeddings("data/embeddings_1536.json")
    return g.embedding_list


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the request is AJAX
        if request.is_json:
            data = request.get_json()
            query = data.get('query')
            # Your processing logic here
            cursor = get_db_cursor()
            openai_client = get_openai_client()
            embedding_list = get_embedding_list()
            
            # Assuming your rag function returns a string or a data structure that can be JSON serialized
            rag_output = rag(query, openai_client, cursor, embedding_list)
            
            # Return JSON response
            return jsonify({'rag_output': rag_output})
        else:
            # Handle non-AJAX POST request if necessary
            pass

    # GET request or non-AJAX POST, render template normally
    return render_template('index.html')

