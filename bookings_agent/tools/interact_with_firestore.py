from bookings_agent.firestore_service import FirestoreService, sanitize_sentinel
from typing import Optional, Dict, Any, List, Union
from google.cloud.firestore_v1.transforms import Sentinel
import datetime
from google.adk.tools import ToolContext
import json
import os
import uuid
import firebase_admin
from google.cloud.firestore import Client, DocumentReference
from firebase_admin import firestore, initialize_app
from absl import logging

from bookings_agent.firestore_service import get_firestore_client

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Constants for collection names
MEMORIES_COLLECTION = "booking_memories"  # Updated namespace for bookings
BOOKINGS_COLLECTION = "booking_bookings"  # New collection for bookings
VALIDATIONS_COLLECTION = "booking_validations"  # New collection for validations

def sanitize_firestore_data(data: Any) -> Any:
    """
    Recursively sanitize data to ensure it's compatible with Firestore.
    
    Args:
        data: The data to sanitize
        
    Returns:
        The sanitized data
    """
    if isinstance(data, dict):
        return {k: sanitize_firestore_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_firestore_data(item) for item in data]
    elif isinstance(data, (int, float, bool, str, type(None))):
        return data
    else:
        # Convert unsupported types to strings
        return str(data)

def interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Interact with Firestore to store or retrieve data.
    
    Operations:
    - "memorize": Store a memory
    - "get_memory": Get a specific memory by ID
    - "list_memories": List memories with optional filters
    - "update_memory": Update an existing memory
    - "delete_memory": Delete a memory
    - "save_booking": Create or update a booking
    - "get_booking": Get a booking by ID
    - "list_bookings": List bookings with optional filters
    - "update_booking": Update a booking
    - "delete_booking": Delete a booking
    - "save_validation": Create or update a validation record
    - "get_validation": Get a validation record by ID
    - "list_validations": List validation records with optional filters
    - "update_validation": Update a validation record
    - "delete_validation": Delete a validation record
    
    Args:
        operation: The operation to perform
        args: The arguments for the operation
        
    Returns:
        The result of the operation
    """
    client = get_firestore_client()
    
    # Clean up the args to ensure they're compatible with Firestore
    clean_args = sanitize_firestore_data(args)
    
    if operation == "memorize":
        # Store a memory
        memory_id = clean_args.get("id", str(uuid.uuid4()))
        memory_type = clean_args.get("type", "fact")
        content = clean_args.get("content", {})
        tags = clean_args.get("tags", [])
        
        memory_data = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "tags": tags,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        client.collection(MEMORIES_COLLECTION).document(memory_id).set(memory_data)
        return {"success": True, "id": memory_id, "message": "Memory stored successfully"}
    
    elif operation == "get_memory":
        # Get a specific memory by ID
        memory_id = clean_args.get("id")
        if not memory_id:
            return {"success": False, "message": "Memory ID is required"}
        
        doc = client.collection(MEMORIES_COLLECTION).document(memory_id).get()
        if doc.exists:
            return {"success": True, "memory": doc.to_dict()}
        else:
            return {"success": False, "message": "Memory not found"}
    
    elif operation == "list_memories":
        # List memories with optional filters
        filters = clean_args.get("filters", {})
        
        # Start with the memories collection
        query = client.collection(MEMORIES_COLLECTION)
        
        # Apply filters if any
        for field, value in filters.items():
            if isinstance(value, list):
                # For array fields like tags, use array_contains_any
                query = query.where(field, "array_contains_any", value)
            else:
                # For other fields, use equality
                query = query.where(field, "==", value)
        
        # Execute the query
        docs = query.stream()
        memories = [doc.to_dict() for doc in docs]
        
        return {"success": True, "memories": memories}
    
    elif operation == "update_memory":
        # Update an existing memory
        memory_id = clean_args.get("id")
        if not memory_id:
            return {"success": False, "message": "Memory ID is required"}
        
        updates = clean_args.get("updates", {})
        if not updates:
            return {"success": False, "message": "No updates provided"}
        
        # Add the updated_at timestamp
        updates["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # Update the memory
        client.collection(MEMORIES_COLLECTION).document(memory_id).update(updates)
        
        return {"success": True, "message": "Memory updated successfully"}
    
    elif operation == "delete_memory":
        # Delete a memory
        memory_id = clean_args.get("id")
        if not memory_id:
            return {"success": False, "message": "Memory ID is required"}
        
        client.collection(MEMORIES_COLLECTION).document(memory_id).delete()
        
        return {"success": True, "message": "Memory deleted successfully"}
    
    elif operation == "save_booking":
        # Save a booking
        booking_id = clean_args.get("id", str(uuid.uuid4()))
        description = clean_args.get("description", "")
        date = clean_args.get("date", "")
        time = clean_args.get("time", "")
        duration = clean_args.get("duration", 0)
        resource_id = clean_args.get("resource_id", "")
        user_id = clean_args.get("user_id", "")
        session_id = clean_args.get("session_id", "")
        status = clean_args.get("status", "pending")
        tags = clean_args.get("tags", [])
        
        booking_data = {
            "id": booking_id,
            "description": description,
            "date": date,
            "time": time,
            "duration": duration,
            "resource_id": resource_id,
            "user_id": user_id,
            "session_id": session_id,
            "status": status,
            "tags": tags,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        client.collection(BOOKINGS_COLLECTION).document(booking_id).set(booking_data)
        return {"success": True, "id": booking_id, "message": "Booking saved successfully"}
    
    elif operation == "get_booking":
        # Get a specific booking by ID
        booking_id = clean_args.get("id")
        if not booking_id:
            return {"success": False, "message": "Booking ID is required"}
        
        doc = client.collection(BOOKINGS_COLLECTION).document(booking_id).get()
        if doc.exists:
            return {"success": True, "booking": doc.to_dict()}
        else:
            return {"success": False, "message": "Booking not found"}
    
    elif operation == "list_bookings":
        # List bookings with optional filters
        filters = clean_args.get("filters", {})
        
        # Start with the bookings collection
        query = client.collection(BOOKINGS_COLLECTION)
        
        # Apply filters if any
        for field, value in filters.items():
            if isinstance(value, list):
                # For array fields like tags, use array_contains_any
                query = query.where(field, "array_contains_any", value)
            else:
                # For other fields, use equality
                query = query.where(field, "==", value)
        
        # Execute the query
        docs = query.stream()
        bookings = [doc.to_dict() for doc in docs]
        
        return {"success": True, "bookings": bookings}
    
    elif operation == "update_booking":
        # Update an existing booking
        booking_id = clean_args.get("booking_id")
        if not booking_id:
            return {"success": False, "message": "Booking ID is required"}
        
        updates = clean_args.get("updates", {})
        if not updates:
            return {"success": False, "message": "No updates provided"}
        
        # Add the updated_at timestamp
        updates["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # Update the booking
        client.collection(BOOKINGS_COLLECTION).document(booking_id).update(updates)
        
        return {"success": True, "message": "Booking updated successfully"}
    
    elif operation == "delete_booking":
        # Delete a booking
        booking_id = clean_args.get("id")
        if not booking_id:
            return {"success": False, "message": "Booking ID is required"}
        
        client.collection(BOOKINGS_COLLECTION).document(booking_id).delete()
        
        return {"success": True, "message": "Booking deleted successfully"}
    
    elif operation == "save_validation":
        # Save a validation record
        validation_id = clean_args.get("id", str(uuid.uuid4()))
        booking_id = clean_args.get("booking_id", "")
        status = clean_args.get("status", "")
        message = clean_args.get("message", "")
        user_id = clean_args.get("user_id", "")
        session_id = clean_args.get("session_id", "")
        tags = clean_args.get("tags", [])
        
        validation_data = {
            "id": validation_id,
            "booking_id": booking_id,
            "status": status,
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "tags": tags,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        client.collection(VALIDATIONS_COLLECTION).document(validation_id).set(validation_data)
        return {"success": True, "id": validation_id, "message": "Validation saved successfully"}
    
    elif operation == "get_validation":
        # Get a specific validation by ID
        validation_id = clean_args.get("id")
        if not validation_id:
            return {"success": False, "message": "Validation ID is required"}
        
        doc = client.collection(VALIDATIONS_COLLECTION).document(validation_id).get()
        if doc.exists:
            return {"success": True, "validation": doc.to_dict()}
        else:
            return {"success": False, "message": "Validation not found"}
    
    elif operation == "list_validations":
        # List validations with optional filters
        filters = clean_args.get("filters", {})
        
        # Start with the validations collection
        query = client.collection(VALIDATIONS_COLLECTION)
        
        # Apply filters if any
        for field, value in filters.items():
            if isinstance(value, list):
                # For array fields like tags, use array_contains_any
                query = query.where(field, "array_contains_any", value)
            else:
                # For other fields, use equality
                query = query.where(field, "==", value)
        
        # Execute the query
        docs = query.stream()
        validations = [doc.to_dict() for doc in docs]
        
        return {"success": True, "validations": validations}
    
    elif operation == "update_validation":
        # Update an existing validation
        validation_id = clean_args.get("validation_id")
        if not validation_id:
            return {"success": False, "message": "Validation ID is required"}
        
        updates = clean_args.get("updates", {})
        if not updates:
            return {"success": False, "message": "No updates provided"}
        
        # Add the updated_at timestamp
        updates["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # Update the validation
        client.collection(VALIDATIONS_COLLECTION).document(validation_id).update(updates)
        
        return {"success": True, "message": "Validation updated successfully"}
    
    elif operation == "delete_validation":
        # Delete a validation
        validation_id = clean_args.get("id")
        if not validation_id:
            return {"success": False, "message": "Validation ID is required"}
        
        client.collection(VALIDATIONS_COLLECTION).document(validation_id).delete()
        
        return {"success": True, "message": "Validation deleted successfully"}
    
    else:
        return {"success": False, "message": f"Unknown operation: {operation}"}
    
    