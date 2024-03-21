import pprint
from llama_index.core.response.notebook_utils import display_response
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

llm = OpenAI()
embed_model=OpenAIEmbedding(model="text-embedding-3-small",dimensions=512)
Settings.llm = llm
Settings.embed_model=embed_model

from llama_index.core import VectorStoreIndex, StorageContext
from dotenv import load_dotenv

import os
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    """Establish connection to the MongoDB."""

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not set in environment variables")

    try:
        client = MongoClient(mongo_uri)
        print("Connection to MongoDB successful")
        return client
    except ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None


def query_vector_store(
    query,
    db_name="natel",
    collection_name="sg_records",
    index_name="vector_index",
    similarity_top_k=3,
):
    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    collection = db[collection_name]

    vector_store = MongoDBAtlasVectorSearch(
        mongo_client,
        db_name=db_name,
        collection_name=collection_name,
        index_name=index_name,
        dimension=512,  # Add this line
    )
    index = VectorStoreIndex.from_vector_store(vector_store)

    query_engine = index.as_query_engine(similarity_top_k=similarity_top_k)
    response = query_engine.query(query)
    display_response(response)
    pprint.pprint(response.source_nodes)


# Usage
if __name__ == "__main__":
    query = (
        "Wir suchen engagierte, dynamische und kompetente Mitarbeiterinnen und Mitarbeiter"
    )
    query_vector_store(query)
