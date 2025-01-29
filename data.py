import json
from bson import ObjectId, json_util
from pymongo import MongoClient, errors
from jsonschema import validate, ValidationError

# Connect to MongoDB (local server or MongoDB Atlas)
client = MongoClient('mongodb://localhost:27017/')  # Change URI for MongoDB Atlas if needed
db = client['mydatabase']  # Replace with your database name

class SchemaValidator:
    def __init__(self, db, schema_file="schema.json"):
        """Load schema from a JSON file instead of hardcoding it."""
        self.db = db
        self.json_schema = self.load_schema(schema_file)

    def load_schema(self, file_path):
        """Read the schema from a JSON file."""
        try:
            with open(file_path, 'r') as file:
                schema = json.load(file)
            return schema
        except FileNotFoundError:
            print(f"Error: Schema file '{file_path}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{file_path}'.")
            return None

    def validate_document(self, document):
        """Validate the document against the schema."""
        if not self.json_schema:
            return {"status": "error", "message": "Schema not loaded."}

        try:
            validate(instance=document, schema=self.json_schema)
            return True  # Valid document
        except ValidationError as e:
            return {"status": "error", "message": f"Validation failed: {e.message}"}

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Function to add data to a collection
def add_data_to_collection(collection_name: str, data_obj: dict, schema_file="schema.json"):
    try:
        schema_obj = SchemaValidator(db, schema_file)
        
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
        return {"status": "error", "message": f"Schema validation failed: {str(ve)}"}
    except errors.PyMongoError as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}

# Function to retrieve data based on field and return only that field's value
def retrieve_data_from_collection(collection_name: str, field: str):
    try:
        collection = db[collection_name]
        results = list(collection.find({ "field": field }))
        
        if not results:
            raise ValueError(f"No documents found for the field: {field}")
        
        return json.loads(json.dumps(results, default=json_util.default))

    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "error", "message": str(e)}

# Function to retrieve all data from a collection
def retrieve_all_data(collection_name: str):
    try:
        collection = db[collection_name]
        results = list(collection.find())
        return json.loads(json.dumps(results, cls=JSONEncoder))
    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}

