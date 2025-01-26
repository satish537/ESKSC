from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

# Connect to MongoDB (local server or MongoDB Atlas)
client = MongoClient('mongodb://localhost:27017/')  # Change URI for MongoDB Atlas if needed
db = client['mydatabase']  # Replace with your database name

# Define the JSON schema for the collection
json_schema = {
    "bsonType": "object",
    "additionalProperties": True,
    "required": ["field", "datatype", "origin", "sample"],
    "properties": {
        "field": {
            "bsonType": "string"
        },
        "datatype": {
            "bsonType": "string"
        },
        "origin": {
            "bsonType": "string"
        },
        "sample": {
            "bsonType": "string"
        },
        "notes": {
            "bsonType": "string"
        }
    }
}

# Create or modify the collection with schema validation
def create_or_update_collection_with_schema(collection_name: str = "collect"):
    try:
        # Check if the collection already exists
        if collection_name not in db.list_collection_names():
            db.create_collection(
                collection_name,  # Collection name
                validator={
                    "$jsonSchema": json_schema  # Attach JSON schema validator
                }
            )
            print(f"Collection '{collection_name}' created with JSON schema validator.")
        else:
            # Update the schema validator for the existing collection
            db.command({
                "collMod": collection_name,
                "validator": {
                    "$jsonSchema": json_schema
                },
                "validationLevel": "strict"  # Enforce strict validation
            })
            print(f"Collection '{collection_name}' updated with new JSON schema validator.")
    except OperationFailure as e:
        print("Error creating or updating collection:", e)
    except PyMongoError as e:
        print("General PyMongoError:", e)



# Usage
# create_or_update_collection_with_schema("collect2")