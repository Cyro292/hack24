#%%
import os
import pandas as pd

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

# Loda the .env file (API keys, URI's etc.)
load_dotenv() 

# Loading the llm and embedding models
llm = OpenAI()
embed_model=OpenAIEmbedding(model="text-embedding-3-small",dimensions=1536)
Settings.llm = llm
Settings.embed_model=embed_model

# Load the aggregated data
aggregated_data = pd.read_csv('aggregated_data.csv')
# Convert the DataFrame to a JSON representation
data_json = aggregated_data.to_json(orient='records')
# Load the JSON data into a Python list of dictionaries
data_list = json.loads(data_json)
# data_list


import ast

def aggregate_headings_paragraphs(data):
    headings = ast.literal_eval(data['headings'])
    paragraphs = ast.literal_eval(data['paragraphs'])
    blockquotes = ast.literal_eval(data['blockquotes'])
    strong_bold = ast.literal_eval(data['strong_bold'])
    
    content = []
    current_heading = None
    current_paragraphs = []
    for text in paragraphs:
        if text in headings:
            if current_heading is not None and current_paragraphs:
                content.append({ 'heading': current_heading, 'paragraphs': "\n\n ".join(current_paragraphs) })
            current_heading = text
            current_paragraphs = []
        elif text.strip():  # Check if paragraph is not empty
            current_paragraphs.append(text)
    if current_heading is not None and current_paragraphs:
        content.append({ 'heading': current_heading, 'paragraphs': "\n\n ".join(current_paragraphs) })
    
    # Remove empty blockquotes and bold texts
    blockquotes = [quote for quote in blockquotes if quote.strip()]
    strong_bold = [bold for bold in strong_bold if bold.strip()]
    
    return {
        'filepath': data['filepath'],
        'content': content,
        'blockquotes': blockquotes,
        'strong_bold': strong_bold
    }

# Usage
content = []
for data in data_list:
    new_data = aggregate_headings_paragraphs(data)
    content.append(new_data)
    
content



#%%

### Generate a list of llama documents (one for each web page) ###
llama_documents = []

for document in data_list:
    meta_data = {
        "filepath": document["filepath"],
        "strong_bold": document["strong_bold"],
        "blockquotes": document["blockquotes"],
    }

    # Storing the filepath, strong_bold and blockquotes as strings
    meta_data["filepath"] = json.dumps(document["filepath"])
    meta_data["strong_bold"] = json.dumps(document["strong_bold"])
    meta_data["blockquotes"] = json.dumps(document["blockquotes"])
    
    
    document["content"] = json.dumps(document["content"])
    
    # Create a Document object with the text content and metadata 
    llama_document = Document(
        text=''.join(document["content"]),
        metadata=meta_data,
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
    
    # add the generated Document object to the llama_documents list
    llama_documents.append(llama_document)


# parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
# nodes = parser.get_nodes_from_documents(llama_documents, show_progress=True)


# # This will take a while because here, all the OpenAI API-requests are made
# # Louis: I ran this for 30+ min. (on Google-Colab) and it only computed 5000 embeddings
# # You can find the embeddings for the 5000 first nodes in the `embeddings.json` file
# # You can use this file to save time
# # Maybe we can run the requests concurrently?
# for i, node in enumerate(nodes):
#     node_embedding = embed_model.get_text_embedding(
#         node.get_content(metadata_mode="all")
#     )
#     node.embedding = node_embedding
#     print(f'Generated embedding for node {i}/{len(nodes)}')

        
# mongo_client = get_mongo_client()

# DB_NAME="natel"
# COLLECTION_NAME="sg_records"

# db = mongo_client[DB_NAME]
# collection = db[COLLECTION_NAME]


# # Ingest (or reload/update) data into MongoDB
# vector_store = MongoDBAtlasVectorSearch(mongo_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, index_name="vector_index")
# vector_store.add(nodes)

# %%
