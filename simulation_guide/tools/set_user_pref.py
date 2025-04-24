from simulation_guide.firestore_memory_service import FirestoreSessionService
from typing import Optional

def set_user_pref(
    user_id: str,
    session_id: str,
    key: str,
    value: str,
    agent_name: Optional[str] = "simulation_guide"
) -> None:
    """
    Set a user preference in persistent state (Firestore/ADK).
    Args:
        user_id (str): User ID
        session_id (str): Session ID
        key (str): Preference key
        value (str): Preference value
        agent_name (str, optional): The agent's name.
    """
    service = FirestoreSessionService()
    pref_content = {"preference_key": key, "preference_value": value, "type": "user_preference"}
    service.store_memory(user_id, session_id, agent_name, pref_content)