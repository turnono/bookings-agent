import os
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from datetime import datetime

# FirestoreSessionService: persistent session/memory service for ADK agents
# class FirestoreSessionService:
#     def __init__(self, collection_name: str = "agent_memory"):
#         self.collection_name = collection_name
#         self.client = firestore.Client()
#         self.collection = self.client.collection(self.collection_name)

#     def store_memory(self, user_id: str, session_id: str, agent_name: str, content: Any, embedding_vector: Optional[List[float]] = None) -> str:
#         doc = {
#             "user_id": user_id,
#             "session_id": session_id,
#             "agent_name": agent_name,
#             "content": content,
#             "timestamp": firestore.SERVER_TIMESTAMP,
#         }
#         if embedding_vector is not None:
#             doc["embedding_vector"] = embedding_vector
#         ref = self.collection.document()
#         ref.set(doc)
#         return ref.id

#     def get_memories(self, user_id: Optional[str] = None, session_id: Optional[str] = None, agent_name: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
#         query = self.collection
#         if user_id:
#             query = query.where("user_id", "==", user_id)
#         if session_id:
#             query = query.where("session_id", "==", session_id)
#         if agent_name:
#             query = query.where("agent_name", "==", agent_name)
#         query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
#         return [doc.to_dict() for doc in query.stream()]

#     def store_event_log(self, user_id: str, session_id: str, event: Dict[str, Any]) -> str:
#         # Store an event log as a memory document with a type field
#         doc = {
#             "user_id": user_id,
#             "session_id": session_id,
#             "agent_name": event.get("agent_name", "event_log"),
#             "content": event,
#             "timestamp": firestore.SERVER_TIMESTAMP,
#             "type": "event_log",
#         }
#         ref = self.collection.document()
#         ref.set(doc)
#         return ref.id

#     def get_event_logs(self, user_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
#         query = self.collection.where("type", "==", "event_log")
#         if user_id:
#             query = query.where("user_id", "==", user_id)
#         if session_id:
#             query = query.where("session_id", "==", session_id)
#         query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
#         return [doc.to_dict() for doc in query.stream()]

class FirestoreService:
    def __init__(self):
        self.client = firestore.Client()
        self.users_collection = self.client.collection("users")
        self.agent_memory_collection = self.client.collection("agent_memory")
        self.artifacts_collection = self.client.collection("artifacts")
        self.sessions_collection = self.client.collection("sessions")
        self.tasks_collection = self.client.collection("tasks")
        self.knowledge_base_collection = self.client.collection("knowledge_base")

    # USERS
    def create_or_update_user(self, user_id: str, display_name: str, user_type: str, role: str, email: str = None, preferences: dict = None):
        """Create or update a user (human or agent) profile."""
        doc_ref = self.users_collection.document(user_id)
        data = {
            "display_name": display_name,
            "user_type": user_type,  # 'human' or 'agent'
            "role": role,             # 'user', 'superuser', 'admin', 'agent'
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        if email:
            data["email"] = email
        if preferences:
            data["preferences"] = preferences
        doc_ref.set(data, merge=True)

    def get_user(self, user_id: str):
        doc = self.users_collection.document(user_id).get()
        return doc.to_dict() if doc.exists else None

    def get_all_users(self, limit: int = 100):
        return [doc.to_dict() for doc in self.users_collection.limit(limit).stream()]

    # SESSIONS
    # we will use the session data from the web ui
    def create_session(self, user_id: str, session_id: str, session_data: dict):
        """Create a new session for a user."""
        sessions = self.sessions_collection
        sessions.document(session_id).set(session_data, merge=True)

    def update_session(self, user_id: str, session_id: str, session_data: dict):
        sessions = self.sessions_collection
        # update the session with the current contents
        sessions.document(session_id).update(session_data)

    def get_sessions(self, user_id: str, limit: int = 10):
        sessions = self.sessions_collection
        return [doc.to_dict() for doc in sessions.order_by("started_at", direction=firestore.Query.DESCENDING).limit(limit).stream()]

    def delete_session(self, user_id: str, session_id: str):
        sessions = self.sessions_collection
        sessions.document(session_id).delete()

    # TASKS
    def create_task(self, user_id: str, session_id: str, task_id: str, description: str, status: str = "pending", priority: str = "medium", due_date = None):
        """Create a new task under a user's session."""
        tasks = self.tasks_collection
        data = {
            "description": description,
            "status": status,
            "priority": priority,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        if due_date:
            data["due_date"] = due_date
        tasks.document(task_id).set(data, merge=True)

    def get_tasks(self, user_id: str, session_id: str, limit: int = 20):
        tasks = self.tasks_collection
        return [doc.to_dict() for doc in tasks.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()]

    # AGENT MEMORY (logs, facts, preferences, events)
    def store_agent_memory(self, user_id: str, session_id: str, agent_name: str, content: dict, memory_type: str = "fact"):
        """Store a memory, log, or event for a user or agent."""
        doc = {
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "content": content,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "type": memory_type,
        }
        ref = self.agent_memory_collection.document()
        ref.set(doc)
        return ref.id

    def get_agent_memory(self, user_id: str, session_id: str = None, agent_name: str = None, memory_type: str = None, limit: int = 20):
        query = self.agent_memory_collection.where("user_id", "==", user_id)
        if session_id:
            query = query.where("session_id", "==", session_id)
        if agent_name:
            query = query.where("agent_name", "==", agent_name)
        if memory_type:
            query = query.where("type", "==", memory_type)
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        return [doc.to_dict() for doc in query.stream()]

    # ARTIFACTS (metadata for files in Firebase Storage)
    def store_artifact(self, user_id: str, session_id: str, storage_path: str, artifact_type: str, description: str = None):
        """Store metadata for an artifact (file) in Firebase Storage."""
        doc = {
            "user_id": user_id,
            "session_id": session_id,
            "storage_path": storage_path,
            "type": artifact_type,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        if description:
            doc["description"] = description
        ref = self.artifacts_collection.document()
        ref.set(doc)
        return ref.id

    def get_artifacts(self, user_id: str = None, session_id: str = None, artifact_type: str = None, limit: int = 20):
        query = self.artifacts_collection
        if user_id:
            query = query.where("user_id", "==", user_id)
        if session_id:
            query = query.where("session_id", "==", session_id)
        if artifact_type:
            query = query.where("type", "==", artifact_type)
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        return [doc.to_dict() for doc in query.stream()]

    # KNOWLEDGE BASE
    def add_knowledge_item(self, content: str, embedding: list, user_id: str = None, agent_id: str = None, session_id: str = None, metadata: dict = None):
        """Add a knowledge item with optional embedding and metadata."""
        doc = {
            "content": content,
            "embedding": embedding,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        if user_id:
            doc["user_id"] = user_id
        if agent_id:
            doc["agent_id"] = agent_id
        if session_id:
            doc["session_id"] = session_id
        if metadata:
            doc["metadata"] = metadata
        ref = self.knowledge_base_collection.document()
        ref.set(doc)
        return ref.id

    def get_knowledge_items(self, user_id: str = None, agent_id: str = None, session_id: str = None, tags: list = None, limit: int = 20):
        query = self.knowledge_base_collection
        if user_id:
            query = query.where("user_id", "==", user_id)
        if agent_id:
            query = query.where("agent_id", "==", agent_id)
        if session_id:
            query = query.where("session_id", "==", session_id)
        if tags:
            query = query.where("metadata.tags", "array_contains_any", tags)
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        return [doc.to_dict() for doc in query.stream()]

        # This file provides Firestore-backed persistent memory services for the Simulation Guide agent system.
        # It defines service classes and methods to store and retrieve user memories, session data, artifacts, and knowledge base items.
        # These services are used by agent tools (such as store_memory and set_user_pref) to enable long-term, context-aware memory and event logging
        # for users and sessions across all sub-agents in the simulation environment.


