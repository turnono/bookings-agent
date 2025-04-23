import os

import uvicorn
from fastapi import FastAPI, Request
from google.adk.cli.fast_api import get_fast_api_app
from simulation_guide.firestore_memory_service import FirestoreSessionService
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Firestore session/memory service instance
firestore_service = FirestoreSessionService()

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app: FastAPI = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# --- Firestore Memory API Models ---
class StoreMemoryRequest(BaseModel):
    user_id: str
    session_id: str
    agent_name: str
    content: Any
    embedding_vector: Optional[List[float]] = None

class GetMemoriesRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_name: Optional[str] = None
    limit: int = 20

class StoreEventRequest(BaseModel):
    user_id: str
    session_id: str
    event: Dict[str, Any]

class GetEventsRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = 50

# --- Firestore Memory Endpoints ---
@app.post("/memory/store")
def store_memory(req: StoreMemoryRequest):
    doc_id = firestore_service.store_memory(
        user_id=req.user_id,
        session_id=req.session_id,
        agent_name=req.agent_name,
        content=req.content,
        embedding_vector=req.embedding_vector,
    )
    return {"status": "success", "doc_id": doc_id}

@app.post("/memory/get")
def get_memories(req: GetMemoriesRequest):
    memories = firestore_service.get_memories(
        user_id=req.user_id,
        session_id=req.session_id,
        agent_name=req.agent_name,
        limit=req.limit,
    )
    return {"status": "success", "memories": memories}

@app.post("/event/store")
def store_event(req: StoreEventRequest):
    doc_id = firestore_service.store_event_log(
        user_id=req.user_id,
        session_id=req.session_id,
        event=req.event,
    )
    return {"status": "success", "doc_id": doc_id}

@app.post("/event/get")
def get_events(req: GetEventsRequest):
    events = firestore_service.get_event_logs(
        user_id=req.user_id,
        session_id=req.session_id,
        limit=req.limit,
    )
    return {"status": "success", "events": events}

# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))