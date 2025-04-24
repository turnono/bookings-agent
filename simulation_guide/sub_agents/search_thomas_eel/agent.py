from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import SEARCH_INSTRUCTION
from google.adk.tools import google_search
from simulation_guide.tools import store_memory

# Helper to always use the correct agent name
def search_thomas_store_memory(user_id: str, session_id: str, memory_type: str, content: dict) -> None:
    return store_memory(user_id, session_id, memory_type, content, agent_name="search_thomas_eel")

search_thomas_eel_agent = Agent(
    name="search_thomas_eel",
    description="A specialist in Search",
    instruction=SEARCH_INSTRUCTION,
    model=DEFAULT_MODEL,
    tools=[google_search],
    output_key="search_thomas_eel_output"
    )

def get_search_thomas_eel_agent() -> Agent:
    """Returns an instance of the Search Thomas Eel Agent."""
    return search_thomas_eel_agent

root_agent = search_thomas_eel_agent 