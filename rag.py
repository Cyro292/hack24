# %%  
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.response.notebook_utils import display_response
from mongo_client import get_mongo_client
import openai
import pickle
import pprint

from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

llm = OpenAI()
embed_model=OpenAIEmbedding(model="text-embedding-3-small",dimensions=512)
Settings.llm = llm
Settings.embed_model=embed_model


# %%    
# Configure the MongoDB client
mongo_client = get_mongo_client()
DB_NAME="natel"
COLLECTION_NAME="sg_records"
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# %%
# To ensure we are working with a fresh collection 
# delete any existing records in the collection
collection.delete_many({})


# %%
# Ingest (or reload/update) data + the embeddings into MongoDB
with open('logs/checkpoint_900.pkl', 'rb') as f:
    nodes = pickle.load(f)

vector_store = MongoDBAtlasVectorSearch(mongo_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, index_name="vector_index", dimension=512)
vector_store.add(nodes)

# Create an Llama index
index = VectorStoreIndex.from_vector_store(vector_store)

# %%


#Query the index
query_engine = index.as_query_engine(similarity_top_k=10)
query = "Was ist ein inhaltsverzeichnis?"
response = query_engine.query(query)
display_response(response)
pprint.pprint(response.source_nodes)


# def vector_search(user_query, collection):
#     """
#     Perform a vector search in the MongoDB collection based on the user query.

#     Args:
#     user_query (str): The user's query string.
#     collection (MongoCollection): The MongoDB collection to search.

#     Returns:
#     list: A list of matching documents.
#     """

#     # Generate embedding for the user query
#     query_embedding = get_embedding(user_query)

#     if query_embedding is None:
#         return "Invalid query or embedding generation failed."

#     # Define the vector search pipeline
#     pipeline = [
#         {
#             "$vectorSearch": {
#                 "index": "vector_index",
#                 "queryVector": query_embedding,
#                 "path": "plot_embedding_optimised",
#                 "numCandidates": 150,  # Number of candidate matches to consider
#                 "limit": 5  # Return top 5 matches
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,  # Exclude the _id field
#                 "plot_embedding_opitimzed": 0,  # Exclude the plot_embedding_opitimzed field
#                 "plot": 1,  # Include the plot field
#                 "title": 1,  # Include the title field
#                 "genres": 1, # Include the genres field
#                 "score": {
#                     "$meta": "vectorSearchScore"  # Include the search score
#                 }
#             }
#         }
#     ]

#     # Execute the search
#     results = collection.aggregate(pipeline)
#     return list(results)







# %%