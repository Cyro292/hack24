import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')


# generate embeddings
def generate_embeddings(text, embedding_model):
    """Generate vector embeddings for each web page (text) in the dataset"""
    
    # Check for valid input
    if not text or not isinstance(text, str):
        return None

    try:
        # Call OpenAI API to get the embedding
        embedding = openai.embeddings.create(input=text, model=embedding_model).data[0].embedding
        return embedding
    
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None

