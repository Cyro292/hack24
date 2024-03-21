from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from mongo_client import get_mongo_client

mongo_client = get_mongo_client()

DB_NAME="sg"
COLLECTION_NAME="sg_records"

db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(mongo_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, index_name="vector_index")

# Create a vector search index 
index = VectorStoreIndex.from_vector_store(vector_store)

query_engine = index.as_query_engine(similarity_top_k=3)

# need the real query here
query = "Recommend a romantic movie suitable for the christmas season and justify your selecton"

response = query_engine.query(query)
print(response.source_nodes)
