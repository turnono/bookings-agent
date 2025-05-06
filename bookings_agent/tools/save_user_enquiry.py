from google.adk.tools import ToolContext
from typing import Dict, Any, Optional
from bookings_agent.firestore_service import FirestoreService

firestore_service = FirestoreService()

def save_user_inquiry(inquiry_details: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Saves user inquiry data to Firestore.

    The 'inquiry_details' dictionary should contain the following keys:
    - 'message' (str, required): The user's inquiry message.
    - 'email' (str, optional): The user's email address.
    - 'category' (str, optional): Category of the inquiry (default: "General question").

    This tool will store the provided inquiry data in the 'inquiries' collection in Firestore.
    It will return a JSON object indicating the success of the operation and the ID of the created inquiry.
    """
    # Extract session information from tool_context if available
    user_id = None
    session_id = None
    
    if tool_context:
        try:
            # Access session information through the internal session service
            if hasattr(tool_context, "_invocation_context") and hasattr(tool_context._invocation_context, "session_service"):
                session_service = tool_context._invocation_context.session_service
                
                # The session service contains a 'sessions' dictionary with app_name as key
                if hasattr(session_service, "__dict__") and "sessions" in session_service.__dict__:
                    sessions_dict = session_service.__dict__["sessions"]
                    
                    # Get the bookings_agent sessions
                    if "bookings_agent" in sessions_dict:
                        bookings_sessions = sessions_dict["bookings_agent"]
                        
                        # The first key is the user_id
                        if bookings_sessions:
                            user_id = list(bookings_sessions.keys())[0]
                            user_sessions = bookings_sessions[user_id]
                            
                            # The first key in user_sessions is the session_id
                            if user_sessions:
                                session_id = list(user_sessions.keys())[0]
            
            print(f"Extracted from session service - user_id: {user_id}, session_id: {session_id}")
        except Exception as e:
            print(f"Error extracting session info: {e}")
            
            # Fall back to other methods if the new approach fails
            # Try to get from session object directly
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
    
    # Prepare inquiry data for Firestore
    inquiry_data = {
        'inquiry_text': inquiry_details.get('message', ''),
        'email': inquiry_details.get('email', ''),
        'category': inquiry_details.get('category', 'General question'),
        'conversation_context': inquiry_details.get('conversation_context', ''),
        'status': 'new',
    }
    
    # Add session info if available
    if user_id:
        inquiry_data['user_id'] = user_id
    if session_id:
        inquiry_data['session_id'] = session_id
        
    # Save to Firestore
    result = firestore_service.save_inquiry(inquiry_data)
    return {"success": result.get("success", False), "data": result.get("data"), "error": result.get("error")}