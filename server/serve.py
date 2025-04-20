from fastapi import FastAPI, Request, WebSocket, Query, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vertexai import agent_engines
import uvicorn
import threading
import os
import traceback
import uuid
import time
import json

# Determine base directory for locating static assets
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

app = FastAPI()

# Allow CORS for local frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the agent once
print("Loading agent...")
agent = agent_engines.get("projects/819021695798/locations/us-central1/reasoningEngines/9199033247462326272")
print("Agent loaded successfully")

# In-memory session store: {user_id: {session_id: str, state: dict}}
session_store = {}
session_lock = threading.Lock()

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.get("/")
def serve_frontend():
    # Serve the front-end HTML from the simulation_guide/static directory
    frontend_path = os.path.join(
        BASE_DIR,
        "simulation_guide",
        "static",
        "frontend.html"
    )
    return FileResponse(frontend_path, media_type="text/html")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    print(f"Received user_id: {user_id}, message: {message}")

    def get_or_create_session():
        with session_lock:
            user_session = session_store.get(user_id)
            if not user_session:
                print(f"Creating new session for user {user_id}")
                session = agent.create_session(user_id=user_id)
                session_id = session["id"]
                session_store[user_id] = {
                    "session_id": session_id,
                    "state": {},
                    "events": [],
                    "current_agent": "simulation_guide"  # Track current agent
                }
                print(f"Created session with ID: {session_id}")
                return session_id, session_store[user_id]
            else:
                print(f"Using existing session for user {user_id}: {user_session['session_id']}")
            return user_session["session_id"], user_session
    
    session_id, user_session = get_or_create_session()
    tried_new_session = False
    
    # Get current agent - default to simulation_guide if not set
    current_agent = user_session.get("current_agent", "simulation_guide")
    
    # Generate unique IDs for this interaction
    request_id = str(uuid.uuid4())
    invocation_id = f"e-{uuid.uuid4()}"
    
    # Create user event
    user_event = {
        "content": {
            "parts": [
                {
                    "text": message
                }
            ],
            "role": "user"
        },
        "invocation_id": invocation_id,
        "author": "user",
        "actions": {
            "state_delta": {},
            "artifact_delta": {},
            "requested_auth_configs": {}
        },
        "id": f"user-{uuid.uuid4().hex[:8]}",
        "timestamp": time.time()
    }
    
    # Add user event to events list
    user_session["events"].append(user_event)
    
    full_response = ""
    model_event = None
    transfer_to = None
    
    while True:
        try:
            print(f"Sending query to agent: user_id={user_id}, session_id={session_id}, message={message}")
            event_count = 0
            start_time = time.time()
            
            for event in agent.stream_query(user_id=user_id, session_id=session_id, message=message):
                event_count += 1
                print(f'AGENT EVENT #{event_count}:', event)
                
                # Check for function calls and transfer requests
                if isinstance(event, dict):
                    # Process function calls (especially transfers)
                    if "content" in event and "parts" in event["content"]:
                        parts = event["content"].get("parts") or []
                        for part in parts:
                            if "function_call" in part:
                                function_call = part["function_call"]
                                if function_call["name"] == "transfer_to_agent" and "args" in function_call:
                                    if "agent_name" in function_call["args"]:
                                        transfer_to = function_call["args"]["agent_name"]
                                        print(f"Transfer request detected: {transfer_to}")
                            
                            if "text" in part:
                                text = part["text"]
                                full_response += text
                                print(f"Agent says (part {event_count}):", text)
                    
                    # Also check for direct transfer actions
                    if "actions" in event and "transfer_to_agent" in event["actions"]:
                        transfer_to = event["actions"]["transfer_to_agent"]
                        print(f"Transfer action detected: {transfer_to}")
                
                elif isinstance(event, str):
                    full_response += event
                    print(f"Agent says (string event {event_count}):", event)
            
            end_time = time.time()
            print(f"Query complete. Received {event_count} events in {end_time - start_time:.2f} seconds")
            print(f"Full response: {full_response}")
            
            # If no response was received, provide a fallback
            if not full_response.strip():
                full_response = "I'm here to help you navigate the simulation. I can assist with questions about the environment, agents, and tools available to you. How can I help you today?"
                print(f"Using fallback response: {full_response}")
            
            # Create model response event
            model_event = {
                "content": {
                    "parts": [
                        {
                            "text": full_response
                        }
                    ],
                    "role": "model"
                },
                "partial": False,
                "invocation_id": invocation_id,
                "author": current_agent,
                "actions": {
                    "state_delta": {
                        f"{current_agent}_output": full_response
                    },
                    "artifact_delta": {},
                    "requested_auth_configs": {}
                },
                "id": f"model-{uuid.uuid4().hex[:8]}",
                "timestamp": time.time()
            }
            
            # If transfer was detected, add it to actions
            if transfer_to:
                model_event["actions"]["transfer_to_agent"] = transfer_to
                # Update the current agent in the session
                user_session["current_agent"] = transfer_to
            
            # Update session state with the latest response
            user_session["state"][f"{current_agent}_output"] = full_response
            user_session["events"].append(model_event)
            
            break  # Success, exit loop
        except Exception as e:
            print(f"Agent query failed for session_id={session_id}, user_id={user_id}, message={message}")
            print(f"Error type: {type(e).__name__}, Error message: {str(e)}")
            traceback.print_exc()
            # If we haven't retried with a new session, try once
            if not tried_new_session:
                print(f"Session error: {e}, creating new session and retrying.")
                with session_lock:
                    session = agent.create_session(user_id=user_id)
                    session_id = session["id"]
                    session_store[user_id]["session_id"] = session_id
                tried_new_session = True
                continue
            # If already retried, return user-friendly error
            return JSONResponse({
                "error": "Sorry, the agent encountered an internal error and could not process your request. Please try again or rephrase your message."
            }, status_code=500)
    
    # Construct final response in ADK format
    response = {
        "id": request_id,
        "app_name": "simulation_guide",
        "user_id": user_id,
        "state": user_session["state"],
        "events": [user_event, model_event],
        "last_update_time": time.time()
    }
    
    # Include transfer info in the response if needed
    if transfer_to:
        response["transfer_to_agent"] = transfer_to
    
    print(f"Returning response with state size: {len(json.dumps(user_session['state']))}")
    return response

@app.websocket("/run_live")
async def websocket_endpoint(
    websocket: WebSocket,
    app_name: str = Query(...),
    user_id: str = Query(...),
    session_id: str = Query(...)
):
    await websocket.accept()
    # Send a message explaining that WebSockets are not supported
    await websocket.send_json({
        "error": "WebSocket streaming is not supported in this implementation. Please use the /api/chat endpoint instead.",
        "code": "websocket_not_supported"
    })
    await websocket.close(1000)

def main():
    """Run the FastAPI server using Uvicorn."""
    # Use PORT env var if set (e.g., Cloud Run) otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()