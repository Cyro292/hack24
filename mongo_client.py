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