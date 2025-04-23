from simulation_guide.firestore_memory_service import FirestoreSessionService
import os

def set_user_pref(key: str, value: str) -> None:
    """Set a user preference in persistent state (Firestore). Args: key (str), value (str)."""
    user_id = os.environ.get("SIM_GUIDE_USER_ID", "default_user")
    session_id = os.environ.get("SIM_GUIDE_SESSION_ID", "default_session")
    agent_name = os.environ.get("SIM_GUIDE_AGENT_NAME", "simulation_guide")
    service = FirestoreSessionService()
    pref_content = {"preference_key": key, "preference_value": value, "type": "user_preference"}
    service.store_memory(user_id, session_id, agent_name, pref_content)