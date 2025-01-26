import os
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status
from data import add_data_to_collection, retrieve_all_data, retrieve_data_from_collection

app = FastAPI()

# Load environment variables from .env file
load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


class AddDataPayload(BaseModel):
    dataObj: dict

@app.post("/add-data")
def add_data(param: AddDataPayload):
    response = add_data_to_collection(COLLECTION_NAME, param.dataObj)
    if response.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response
        )
    return JSONResponse(content=response, status_code=status.HTTP_200_OK)




class RetrieveDataPayload(BaseModel):
    field: str

@app.post("/retrieve-data")
def retrieve_data(param: RetrieveDataPayload):
    response = retrieve_data_from_collection(COLLECTION_NAME, param.field)
    if "status" in response and response["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response
        )
    return JSONResponse(content=response, status_code=status.HTTP_200_OK)




@app.get("/retrieve-all-data")
def retrieve_all_data_endpoint():
    try:
        # Await the retrieve_all_data function
        response = retrieve_all_data(COLLECTION_NAME)
        if isinstance(response, dict) and "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        return JSONResponse(content=http_exc.detail, status_code=http_exc.status_code)

    except Exception as e:
        return JSONResponse(
            content={"error": f"Internal server error: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

