from simulation_guide.firestore_service import FirestoreService
from typing import Optional, Dict, Any

def interact_with_firestore(
    user_id: str,
    session_id: str,
    memory_type: str,
    content: dict,
    agent_name: Optional[str] = "simulation_guide"
) -> None:
    """
    Store any kind of memory in persistent state (Firestore/ADK).
    Args:
        user_id (str): User ID
        session_id (str): Session ID
        memory_type (str): e.g. 'fact', 'user_preference', etc.
        content (dict): The memory content.
        agent_name (str, optional): The agent's name.
    """
    service = FirestoreService()
    service.store_agent_memory(user_id, session_id, agent_name, content, memory_type=memory_type)
    return 