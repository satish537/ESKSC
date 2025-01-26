import json
from bson import ObjectId, json_util
from pymongo import MongoClient, errors
from jsonschema import validate, ValidationError

# Connect to MongoDB (local server or MongoDB Atlas)
client = MongoClient('mongodb://localhost:27017/')  # Change URI for MongoDB Atlas if needed
db = client['mydatabase']  # Replace with your database name


class SchemaValidator:
    def __init__(self, db):
        # Define the JSON schema for validation
        self.json_schema = {
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
        
        self.db = db

    def validate_document(self, document):
        """Validate the document against the schema."""
        try:
            # Use jsonschema.validate to check if the document matches the schema
            validate(instance=document, schema=self.json_schema)
            return True  # Valid document
        except ValidationError as e:
            return {"status": "error", "message": f"Validation failed: {e.message}"}
        
    def add_default_values(self, document):
        """Add default values for missing required fields."""
        # Set default values for missing fields
        default_values = {
            "field": "default_field",
            "datatype": "default_datatype",
            "origin": "default_origin",
            "sample": "default_sample",
            "notes": "default_notes"
        }
        
        # Add default values if not provided
        for key, value in default_values.items():
            if key not in document:
                document[key] = value
        return document




# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Function to add data to a collection
def add_data_to_collection(collection_name: str, data_obj: dict):
    try:
        schema_obj = SchemaValidator(db)
        
        # Validate the document
        validation_result = schema_obj.validate_document(data_obj)
        
        if validation_result is True:  # If valid
            collection = db[collection_name]
            result = collection.insert_one(data_obj)
            return {"status": "success", "inserted_id": str(result.inserted_id)}
        else:
            # If validation fails, raise an exception with a meaningful message
            raise ValueError(validation_result["message"])
    
    except ValueError as ve:
        # Handle schema validation errors
        return {"status": "error", "message": f"Schema validation failed: {str(ve)}"}
    except errors.PyMongoError as e:
        # Handle MongoDB-specific errors
        return {"status": "error", "message": f"Database error: {str(e)}"}




# Function to retrieve data based on field and return only that field's value
def retrieve_data_from_collection(collection_name: str, field: str):
    try:
        collection = db[collection_name]

        # Retrieve only the specified field from documents
        results = list(collection.find({ "field": field }))
        print("Retrieved results:", results)

        # If no results are found, raise an error
        if not results:
            raise ValueError(f"No documents found for the field: {field}")
        
        # Return as list of JSON-serializable objects
        return json.loads(json.dumps(results, default=json_util.default))

    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except KeyError as e:
        return {"status": "error", "message": str(e)}



# Function to retrieve all data from a collection
def retrieve_all_data(collection_name: str):
    try:
        collection = db[collection_name]
        results = list(collection.find())
        return json.loads(json.dumps(results, cls=JSONEncoder))  # Return as list of JSON-serializable objects
    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}


