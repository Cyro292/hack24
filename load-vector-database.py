#%%
#!pip install datasets pandas openai pymongo 
import os
import pandas as pd

import json
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.core.schema import MetadataMode

from generate_embeddings import generate_embeddings

load_dotenv() # Loda the .env file (API keys, URI's etc.)


# Loading the llm and embedding models
llm = OpenAI()
embed_model=OpenAIEmbedding(model="text-embedding-3-small",dimensions=1536)
Settings.llm = llm
Settings.embed_model=embed_model


aggregated_data = pd.read_csv('aggregated_data.csv')
aggregated_data = aggregated_data.dropna(subset=['lists'])


# Convert the DataFrame to a JSON representation
data_json = aggregated_data.to_json(orient='records')
# Load the JSON data into a Python list of dictionaries
data_list = json.loads(data_json)


# Convert all the lists to a string

    
    
    #
    # item['lists'] = json.dumps(item['lists'])


#




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




 #%%