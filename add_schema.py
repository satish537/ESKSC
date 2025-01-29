import os, json
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Change URI if needed
db = client['mydatabase']  # Replace with your database name

# Load environment variables from .env file
load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Function to read schema from JSON file
def load_schema_from_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            schema = json.load(file)
        return schema
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        return None

# Function to create or update the collection with schema validation
def create_or_update_collection_with_schema_from_file(file_path: str, collection_name: str):
    schema = load_schema_from_file(file_path)
    
    if not schema:
        print("Schema loading failed. Exiting.")
        return

    try:
        if collection_name not in db.list_collection_names():
            db.create_collection(
                collection_name,
                validator={"$jsonSchema": schema}
            )
            print(f"Collection '{collection_name}' created with JSON schema validator.")
        else:
            db.command({
                "collMod": collection_name,
                "validator": {"$jsonSchema": schema},
                "validationLevel": "strict"
            })
            print(f"Collection '{collection_name}' updated with new JSON schema validator.")
    except OperationFailure as e:
        print("Error creating or updating collection:", e)
    except PyMongoError as e:
        print("General PyMongoError:", e)



# Usage
create_or_update_collection_with_schema_from_file("schema.json", COLLECTION_NAME)
