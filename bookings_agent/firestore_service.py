import os
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from datetime import datetime
from google.cloud.firestore_v1.transforms import Sentinel
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

def sanitize_sentinel(data: Any) -> Any:
    """
    Convert Firestore Sentinel objects (like SERVER_TIMESTAMP) to serializable formats.
    
    Args:
        data: The data that might contain Sentinel objects
        
    Returns:
        Serializable data with Sentinels replaced
    """
    if isinstance(data, Sentinel):
        return "<SERVER_TIMESTAMP>"
    elif isinstance(data, dict):
        return {k: sanitize_sentinel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_sentinel(item) for item in data]
    else:
        return data

class FirestoreService:
    def __init__(self):
        self.client = firestore.Client()
        self.memories_collection = self.client.collection("memories")
        self.tasks_collection = self.client.collection("tasks")

    # TASKS
    def save_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create or update a task with the provided data.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            task_id: The ID of the created/updated task
        """
        # Create a copy of the data to avoid modifying the original
        task_data_copy = task_data.copy()
        
        task_id = task_data_copy.get("id")
        if not task_id:
            task_id = self.tasks_collection.document().id
            task_data_copy["id"] = task_id
            
        if "created_at" not in task_data_copy:
            task_data_copy["created_at"] = SERVER_TIMESTAMP
        # Always update updated_at
        task_data_copy["updated_at"] = SERVER_TIMESTAMP
        
        # Set without using SERVER_TIMESTAMP
        self.tasks_collection.document(task_id).set(task_data_copy, merge=True)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Task document or None if not found
        """
        doc = self.tasks_collection.document(task_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            # Sanitize any Sentinel objects before returning
            return sanitize_sentinel(data)
        return None
        
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """
        Update specific fields of a task.
        
        Args:
            task_id: The ID of the task to update
            updates: Dictionary of fields to update
        """
        # Create a copy of updates to avoid modifying the original
        updates_copy = updates.copy()
        
        # Use current datetime instead of SERVER_TIMESTAMP
        updates_copy["updated_at"] = SERVER_TIMESTAMP
        
        self.tasks_collection.document(task_id).update(updates_copy)
        
    def delete_task(self, task_id: str) -> None:
        """
        Delete a task by ID.
        
        Args:
            task_id: The ID of the task to delete
        """
        self.tasks_collection.document(task_id).delete()
        
    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get a list of tasks with optional filtering.
        
        Args:
            filters: Dictionary of filters to apply
                - user_id: Filter by user ID
                - session_id: Filter by session ID
                - status: Filter by status
                - limit: Maximum number of tasks to return (default: 20)
            
        Returns:
            List of task documents
        """
        query = self.tasks_collection
        
        if filters:
            if "user_id" in filters:
                query = query.where("user_id", "==", filters["user_id"])
            if "session_id" in filters:
                query = query.where("session_id", "==", filters["session_id"])
            if "status" in filters:
                query = query.where("status", "==", filters["status"])
                
            limit = filters.get("limit", 20)
        else:
            limit = 20
            
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        # Include document IDs in the results
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            # Sanitize any Sentinel objects
            results.append(sanitize_sentinel(data))
            
        return results

    # MEMORY MANAGEMENT
    def memorize(self, memory_data: Dict[str, Any]) -> str:
        """
        Store a memory with the provided data.
        
        Args:
            memory_data: Dictionary containing memory information
                - type: Memory type (e.g., "fact", "preference", "event")
                - content: The actual memory content
                - tags: Optional list of tags for filtering
            
        Returns:
            The ID of the created memory document
        """
        # Create a copy of the data to avoid modifying the original
        memory_data_copy = memory_data.copy()
        
        memory_id = memory_data_copy.get("id")
        if not memory_id:
            memory_id = self.memories_collection.document().id
            memory_data_copy["id"] = memory_id
            
        if "created_at" not in memory_data_copy:
            memory_data_copy["created_at"] = SERVER_TIMESTAMP
        memory_data_copy["updated_at"] = SERVER_TIMESTAMP
        
        self.memories_collection.document(memory_id).set(memory_data_copy, merge=True)
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by its ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory document or None if not found
        """
        doc = self.memories_collection.document(memory_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            # Sanitize any Sentinel objects
            return sanitize_sentinel(data)
        return None
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing memory.
        
        Args:
            memory_id: The ID of the memory to update
            updates: Dictionary of fields to update
        """
        # Create a copy of updates to avoid modifying the original
        updates_copy = updates.copy()
        
        # Use current datetime instead of SERVER_TIMESTAMP
        updates_copy["updated_at"] = SERVER_TIMESTAMP
        
        self.memories_collection.document(memory_id).update(updates_copy)
    
    def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory by its ID.
        
        Args:
            memory_id: The ID of the memory to delete
        """
        self.memories_collection.document(memory_id).delete()
        
    def list_memories(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve memories with optional filtering.
        
        Args:
            filters: Dictionary of filters to apply
                - type: Filter by memory type
                - tags: Filter by one or more tags
                - limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory documents
        """
        query = self.memories_collection
        
        if filters:
            if "type" in filters:
                query = query.where("type", "==", filters["type"])
                
            if "tags" in filters and isinstance(filters["tags"], list) and len(filters["tags"]) == 1:
                query = query.where("tags", "array_contains", filters["tags"][0])
                
            limit = filters.get("limit", 20)
        else:
            limit = 20
            
        query = query.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        # Include document IDs in the results
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            # Sanitize any Sentinel objects
            results.append(sanitize_sentinel(data))
            
        # If filtering by multiple tags, we need to do it after the query
        if filters and "tags" in filters and isinstance(filters["tags"], list) and len(filters["tags"]) > 1:
            results = [doc for doc in results if all(tag in doc.get("tags", []) for tag in filters["tags"])]
            
        return results

    # SESSIONS
    def save_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """
        Create or update a session record under users/{user_id}/sessions/{session_id}.
        
        Fields:
            - email: string
            - intent: string
            - topic: string
            - screening_answer: string
            - booking_slot: timestamp
            - created_at: timestamp
            - updated_at: timestamp
        
        Args:
            user_id: The user ID
            session_data: Dictionary containing session information
            
        Returns:
            session_id: The ID of the created/updated session
        """
        sessions_collection = self.client.collection("users").document(user_id).collection("sessions")
        session_data_copy = session_data.copy()
        
        session_id = session_data_copy.get("id") or session_data_copy.get("session_id")
        if not session_id:
            session_id = sessions_collection.document().id
            session_data_copy["id"] = session_id
        
        # Add user_id reference
        session_data_copy["user_id"] = user_id
        
        # Add timestamps
        if "created_at" not in session_data_copy:
            session_data_copy["created_at"] = SERVER_TIMESTAMP
        session_data_copy["updated_at"] = SERVER_TIMESTAMP
        
        # Store the session data
        sessions_collection.document(session_id).set(session_data_copy, merge=True)
        return session_id
    
    def get_session(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session document.
        """
        sessions_collection = self.client.collection("users").document(user_id).collection("sessions")
        doc = sessions_collection.document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return sanitize_sentinel(data)
        return None