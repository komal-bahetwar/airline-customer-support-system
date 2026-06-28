import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core_logic import handle_user_query

# Define the request and response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

app = FastAPI(title="Airline Support API")

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        result = handle_user_query(request.query)
        return QueryResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Airline Support System API is active"}
