from simulation_guide.firestore_memory_service import FirestoreUserService
import os

def store_memory(memory_type: str, content: dict) -> None:
    """Store any kind of memory in persistent state (Firestore). Args: memory_type (str), content (dict)."""
    user_id = os.environ.get("SIM_GUIDE_USER_ID", "default_user")
    session_id = os.environ.get("SIM_GUIDE_SESSION_ID", "default_session")
    agent_name = os.environ.get("SIM_GUIDE_AGENT_NAME", "simulation_guide")
    service = FirestoreUserService()
    service.store_agent_memory(user_id, session_id, agent_name, content, memory_type=memory_type) 