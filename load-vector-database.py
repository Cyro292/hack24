#!pip install datasets pandas openai pymongo 
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from generate_embeddings import generate_embeddings

# Loda the .env file (API keys, URI's etc.)
load_dotenv()


# Establish MongoDB connection
def get_mongo_client(mongo_uri):
    """Establishing the connection to the MongoDB database."""
    
    # Create a new client and connect to the server
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    
    except Exception as e:
        print(e)
        return None
        

# Check if 'mongo_client' already exists in the global scope
if 'mongo_client' not in globals():
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    print("MongoDB connection established.")
else:
    print("MongoDB connection already established.")



# Ingest (or reload/update) data into MongoDB



# Create a vector search index 



EMBEDDING_MODEL = "text-embedding-3-small"

# Query the vector search index
def vector_search(user_query, collection):
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.

    Returns:
    list: A list of matching documents.
    """

    # Generate embedding for the user query
    query_embedding = generate_embeddings(user_query, EMBEDDING_MODEL)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "plot_embedding_optimised",
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": 5  # Return top 5 matches
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "plot_embedding_opitimzed": 0,  # Exclude the plot_embedding_opitimzed field
                "plot": 1,  # Include the plot field
                "title": 1,  # Include the title field
                "genres": 1, # Include the genres field
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }
    ]

    # Execute the search
    results = collection.aggregate(pipeline)
    return list(results)


