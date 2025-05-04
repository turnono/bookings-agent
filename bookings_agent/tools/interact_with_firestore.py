from bookings_agent.firestore_service import FirestoreService, sanitize_sentinel
from typing import Optional, Dict, Any, List, Union
from google.cloud.firestore_v1.transforms import Sentinel
import datetime
from google.adk.tools import ToolContext

def sanitize_firestore_data(data: Any) -> Any:
    """
    Sanitize Firestore data to make it serializable.
    Handles special Firestore types like SERVER_TIMESTAMP.
    
    Args:
        data: The data to sanitize
        
    Returns:
        Serializable data
    """
    # We now use the centralized sanitize_sentinel function from firestore_service
    return sanitize_sentinel(data)

def interact_with_firestore(
    operation: str,
    args: Dict[str, Any],
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Safely execute Firestore operations on ?? as requested.
    Use only the specific Firestore service functions.
    Modify only what is necessary, nothing more.
    
    Args:
        operation (str): The Firestore operation to perform (e.g., 'save_task', 'memorize')
        args (Dict): Arguments required for the specific operation
        tool_context (ToolContext, optional): The ADK tool context, containing session information
        
    Returns:
        Dict: Response containing success status and any requested data
    """
    service = FirestoreService()
    
    # Initialize response
    response = {
        "success": False,
        "data": None,
        "error": None
    }
    
    try:
        # Sanitize any Sentinel objects in the input arguments
        args = sanitize_firestore_data(args)
        
        # Create a copy to avoid modifying the original args
        args_copy = args.copy()
        
        # Extract session information from tool_context if available
        user_id = None
        session_id = None
        
        if tool_context:
            # First try to get from session object directly
            if hasattr(tool_context, "session") and tool_context.session:
                user_id = getattr(tool_context.session, "user_id", None)
                session_id = getattr(tool_context.session, "id", None)
            
            # Then try from state
            if not user_id and hasattr(tool_context, "state"):
                user_id = tool_context.state.get("user_id")
            
            if not session_id and hasattr(tool_context, "state"):
                session_id = tool_context.state.get("session_id")
            
            # Fallback to direct attributes
            if not user_id and hasattr(tool_context, "user_id"):
                user_id = tool_context.user_id
            
            if not session_id and hasattr(tool_context, "session_id"):
                session_id = tool_context.session_id
                
            # For creation operations, ensure user_id and session_id are set
            if operation in ["save_task", "memorize"]:
                if user_id and "user_id" not in args_copy:
                    args_copy["user_id"] = user_id
                if session_id and "session_id" not in args_copy:
                    args_copy["session_id"] = session_id
                    
            # For filtering operations, add user_id and session_id to filters
            if operation in ["list_tasks", "list_memories"]:
                if "filters" not in args_copy:
                    args_copy["filters"] = {}
                    
                if user_id and "user_id" not in args_copy.get("filters", {}):
                    args_copy.setdefault("filters", {})["user_id"] = user_id
                if session_id and "session_id" not in args_copy.get("filters", {}):
                    args_copy.setdefault("filters", {})["session_id"] = session_id
            
            # Debug: log session information for troubleshooting
            print(f"Using session info - user_id: {user_id}, session_id: {session_id}")
        
        # Task operations
        if operation == "save_task":
            # Set defaults for required fields
            if "status" not in args_copy:
                args_copy["status"] = "pending"
            if "created_at" not in args_copy:
                args_copy["created_at"] = datetime.datetime.now().isoformat()
                
            task_id = service.save_task(args_copy)
            response["success"] = True
            response["data"] = {"task_id": task_id}
            
            # Store the last created task ID in session state if context available
            if tool_context and hasattr(tool_context, "state"):
                tool_context.state["last_task_id"] = task_id
                
        elif operation == "get_task":
            task = service.get_task(args_copy.get("task_id"))
            response["success"] = True
            response["data"] = task  # Already sanitized by the service
            
        elif operation == "update_task":
            service.update_task(args_copy.get("task_id"), args_copy.get("updates", {}))
            response["success"] = True
            
        elif operation == "delete_task":
            service.delete_task(args_copy.get("task_id"))
            response["success"] = True
            
        elif operation == "list_tasks":
            tasks = service.list_tasks(args_copy.get("filters"))
            response["success"] = True
            response["data"] = tasks  # Already sanitized by the service
            
        # Memory operations
        elif operation == "memorize":
            if "created_at" not in args_copy:
                args_copy["created_at"] = datetime.datetime.now().isoformat()
                
            memory_id = service.memorize(args_copy)
            response["success"] = True
            response["data"] = {"memory_id": memory_id}
            
            # Store the last created memory ID in session state if context available
            if tool_context and hasattr(tool_context, "state"):
                tool_context.state["last_memory_id"] = memory_id
                
        elif operation == "get_memory":
            memory = service.get_memory(args_copy.get("memory_id"))
            response["success"] = True
            response["data"] = memory  # Already sanitized by the service
            
        elif operation == "update_memory":
            service.update_memory(args_copy.get("memory_id"), args_copy.get("updates", {}))
            response["success"] = True
            
        elif operation == "delete_memory":
            service.delete_memory(args_copy.get("memory_id"))
            response["success"] = True
            
        elif operation == "list_memories":
            memories = service.list_memories(args_copy.get("filters"))
            response["success"] = True
            response["data"] = memories  # Already sanitized by the service
  
  
        # Session operations
        elif operation == "save_session":
            # Get user_id from args or context
            user_id = args_copy.get("user_id") or user_id
            if not user_id:
                raise ValueError("user_id is required for save_session")
            
            # Get session_id from args or context
            session_id = args_copy.get("session_id") or session_id or args_copy.get("id")
            if session_id:
                args_copy["id"] = session_id
                
            # Add timestamps if not present
            if "created_at" not in args_copy:
                args_copy["created_at"] = datetime.datetime.now().isoformat()
                
            # Save the session data
            session_id = service.save_session(user_id, args_copy)
            response["success"] = True
            response["data"] = {"session_id": session_id}
            
            # Store the session ID in the tool context for future reference
            if tool_context and hasattr(tool_context, "state"):
                tool_context.state["session_id"] = session_id
                
        elif operation == "get_session":
            # Get user_id from args or context
            user_id = args_copy.get("user_id") or user_id
            # Get session_id from args or context
            session_id = args_copy.get("session_id") or session_id
            
            if not user_id or not session_id:
                raise ValueError("user_id and session_id are required for get_session")
                
            session = service.get_session(user_id, session_id)
            response["success"] = True
            response["data"] = session
            
        elif operation == "update_session":
            # Get user_id from args or context
            user_id = args_copy.get("user_id") or user_id
            # Get session_id from args or context
            session_id = args_copy.get("session_id") or session_id
            updates = args_copy.get("updates", {})
            
            if not user_id or not session_id:
                raise ValueError("user_id and session_id are required for update_session")
                
            service.update_session(user_id, session_id, updates)
            response["success"] = True

        else:
            # Safety fallback for unsupported operations
            response["error"] = {
                "code": "unsupported_operation",
                "message": f"The operation '{operation}' is not supported by the interact_with_firestore tool."
            }
            
    except Exception as e:
        response["error"] = {
            "code": "execution_error",
            "message": str(e) if hasattr(e, 'message') else 'A Firestore error occurred. Please try again or contact support.'
        }
        # Commented out to avoid leaking stack traces
        # print(f"Error in interact_with_firestore: {str(e)}")
    
    return response
    
    