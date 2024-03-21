import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

from mongo_client import get_mongo_client

from dotenv import load_dotenv

from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.core.schema import MetadataMode
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.node_parser import SentenceSplitter

from generate_embeddings import generate_embeddings

load_dotenv()  # Loda the .env file (API keys, URI's etc.)


# Loading the llm and embedding models
llm = OpenAI()
embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=1536)
Settings.llm = llm
Settings.embed_model = embed_model


aggregated_data = pd.read_csv('aggregated_data.csv')

# Convert the DataFrame to a JSON representation
data_json = aggregated_data.to_json(orient='records')
# Load the JSON data into a Python list of dictionaries
data_list = json.loads(data_json)


llama_documents = []

for document in data_list:
    meta_data = {
        "fileurl": None,
        "headings": None
    }

    # We're just storing the filepath as metadata
    # Storing headings, bold text, etc. would make the context vector too large (LlamaIndex throws an error)
    meta_data["filepath"] = json.dumps(document["filepath"])
    meta_data["headings"] = json.dumps(document["headings"])

    cleaned_string = re.sub(r'[^a-zA-Z0-9 .,;\'"-]',
                            '', document['paragraphs'])
    cleaned_string = cleaned_string.translate(str.maketrans('', '', "\"',"))

    # Create a Document object with the text and excluded metadata for llm and embedding models
    llama_document = Document(
        text=cleaned_string,
        metadata=meta_data,
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
    )

    llama_documents.append(llama_document)


parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
nodes = parser.get_nodes_from_documents(llama_documents, show_progress=True)


def get_text_embedding(node, index, total, progress_dict, embed_model):
    try:
        content = node.get_content(metadata_mode="all")
        embedding = embed_model.get_text_embedding(content)
        progress_dict[index] = True  # Mark as completed
        completed = sum(progress_dict.values())
        print(
            f'Generated embedding for node {index + 1}/{total}, completed {completed}/{total}')
        return embedding
    except Exception as exc:
        print(f'Node {index + 1} generated an exception: {exc}')
        return None


def set_node_embedding(nodes, embed_model):
    total = len(nodes)
    progress_dict = {i: False for i in range(total)}  # Track completion
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_text_embedding, node, i, total,
                                   progress_dict, embed_model) for i, node in enumerate(nodes)]
        for future, node in zip(as_completed(futures), nodes):
            embedding = future.result()
            if embedding is not None:
                node.embedding = embedding


set_node_embedding(nodes, embed_model)

mongo_client = get_mongo_client()

DB_NAME = "natel"
COLLECTION_NAME = "sg_records"

db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]


# Make sure the colleciton is empty
collection.delete_many({})


# Ingest (or reload/update) data into MongoDB
vector_store = MongoDBAtlasVectorSearch(
    mongo_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, index_name="vector_index")
vector_store.add(nodes)
