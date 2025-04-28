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

    # BOOKINGS
    def _infer_topic_tags_from_text(self, text: str) -> list:
        """
        Infer topic tags from the provided text using the new taxonomy.
        """
        text = text.lower()
        tags = []
        if any(word in text for word in ["web", "website", "frontend", "backend", "angular", "firebase"]):
            tags.append("web-development")
        if "ai" in text or "agent" in text:
            tags.append("ai-agents")
        if "quran" in text or "arabic" in text:
            tags.append("quranic-arabic")
        if "islamic" in text or "imam" in text or "religious" in text:
            tags.append("islamic-studies")
        if "education" in text or "school" in text or "curriculum" in text:
            tags.append("education")
        if "family" in text:
            tags.append("family-life")
        if "fitness" in text or "swim" in text or "exercise" in text:
            tags.append("fitness")
        if "social" in text or "tiktok" in text or "instagram" in text:
            tags.append("social-media")
        if "tech" in text or "trend" in text or "industry" in text:
            tags.append("tech-trends")
        if "startup" in text or "business" in text or "solopreneur" in text:
            tags.append("startup-growth")
        if "personal" in text or "growth" in text or "resilience" in text:
            tags.append("personal-development")
        if "leader" in text or "leadership" in text:
            tags.append("leadership")
        if not tags:
            tags.append("general")
        return tags

    def create_booking(self, user_id: str, booking_data: Dict[str, Any]) -> str:
        """
        Create a booking under users/{user_id}/bookings/{booking_id}.
        Fields:
            - id: string (auto-generated if not provided)
            - user_id: string
            - status: string (pending, confirmed, canceled, expired)
            - created_at: timestamp
            - updated_at: timestamp
            - selected_slot: object {start, end}
            - payment_status: string (pending, completed, failed, etc.)
            - discussion_summary: string (short summary of user's topic)
            - topic_tags: array of strings (from taxonomy)
            - agent_notes: string (optional)
            - source: string (optional)
        Only lightweight discussion_summary and topic_tags are stored for privacy.
        Note: For efficient queries on payment_status (e.g., all pending bookings), ensure a Firestore index exists on payment_status in users/{user_id}/bookings.
        """
        bookings_collection = self.client.collection("users").document(user_id).collection("bookings")
        booking_data_copy = booking_data.copy()
        booking_id = booking_data_copy.get("id")
        if not booking_id:
            booking_id = bookings_collection.document().id
            booking_data_copy["id"] = booking_id
        # Required fields
        required_fields = ["selected_slot", "discussion_summary"]
        for field in required_fields:
            if field not in booking_data_copy:
                raise ValueError(f"Missing required booking field: {field}")
        # topic_tags: auto-generate if not present
        if "topic_tags" not in booking_data_copy:
            summary_text = booking_data_copy.get("discussion_summary", "")
            inferred_tags = self._infer_topic_tags_from_text(summary_text)
            booking_data_copy["topic_tags"] = list(set([t.lower() for t in inferred_tags]))
            booking_data_copy["topic_tags_raw"] = inferred_tags
        else:
            # Always store normalized and raw
            raw_tags = booking_data_copy["topic_tags"]
            booking_data_copy["topic_tags_raw"] = raw_tags
            booking_data_copy["topic_tags"] = list(set([t.lower() for t in raw_tags]))
        # payment_status
        if "payment_status" not in booking_data_copy:
            booking_data_copy["payment_status"] = "pending"
        # status
        if "status" not in booking_data_copy:
            booking_data_copy["status"] = "pending"
        # user_id
        booking_data_copy["user_id"] = user_id
        # created_at/updated_at
        now = SERVER_TIMESTAMP
        if "created_at" not in booking_data_copy:
            booking_data_copy["created_at"] = now
        booking_data_copy["updated_at"] = now
        # Only keep allowed fields
        allowed_fields = {"id", "user_id", "status", "created_at", "updated_at", "selected_slot", "payment_status", "discussion_summary", "topic_tags", "topic_tags_raw", "agent_notes", "source"}
        booking_data_copy = {k: v for k, v in booking_data_copy.items() if k in allowed_fields}
        bookings_collection.document(booking_id).set(booking_data_copy, merge=True)
        return booking_id

    def update_booking(self, user_id: str, booking_id: str, updates: Dict[str, Any]) -> None:
        """
        Update fields of a booking under users/{user_id}/bookings/{booking_id}.
        Allows updating any of the new booking fields.
        """
        bookings_collection = self.client.collection("users").document(user_id).collection("bookings")
        updates_copy = updates.copy()
        updates_copy["updated_at"] = SERVER_TIMESTAMP
        # In update_booking, always normalize topic_tags if present
        if "topic_tags" in updates_copy:
            raw_tags = updates_copy["topic_tags"]
            updates_copy["topic_tags_raw"] = raw_tags
            updates_copy["topic_tags"] = list(set([t.lower() for t in raw_tags]))
        allowed_fields = {"status", "selected_slot", "payment_status", "discussion_summary", "topic_tags", "topic_tags_raw", "agent_notes", "source", "updated_at"}
        updates_copy = {k: v for k, v in updates_copy.items() if k in allowed_fields}
        bookings_collection.document(booking_id).update(updates_copy)

    def get_booking(self, user_id: str, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a booking document.
        """
        bookings_collection = self.client.collection("users").document(user_id).collection("bookings")
        doc = bookings_collection.document(booking_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return sanitize_sentinel(data)
        return None

    def list_bookings(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List bookings for a user, optionally filtered.
        """
        bookings_collection = self.client.collection("users").document(user_id).collection("bookings")
        query = bookings_collection
        if filters:
            if "status" in filters:
                query = query.where("status", "==", filters["status"])
            if "start_time" in filters:
                query = query.where("start_time", ">=", filters["start_time"])
            if "end_time" in filters:
                query = query.where("end_time", "<=", filters["end_time"])
            limit = filters.get("limit", 20)
        else:
            limit = 20
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(sanitize_sentinel(data))
        return results

    def save_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """
        Create or update an inquiry with the provided data in the 'inquiries' collection.
        Args:
            inquiry_data: Dictionary containing inquiry information
        Returns:
            inquiry_id: The ID of the created/updated inquiry
        """
        inquiries_collection = self.client.collection("inquiries")
        inquiry_data_copy = inquiry_data.copy()
        inquiry_id = inquiry_data_copy.get("id")
        if not inquiry_id:
            inquiry_id = inquiries_collection.document().id
            inquiry_data_copy["id"] = inquiry_id
        if "created_at" not in inquiry_data_copy:
            inquiry_data_copy["created_at"] = SERVER_TIMESTAMP
        inquiry_data_copy["updated_at"] = SERVER_TIMESTAMP
        inquiries_collection.document(inquiry_id).set(inquiry_data_copy, merge=True)
        return inquiry_id