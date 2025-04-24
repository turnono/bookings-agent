from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import SEARCH_INSTRUCTION
from google.adk.tools import google_search
from simulation_guide.tools import store_memory

search_thomas_eel_agent = Agent(
    name="search_thomas_eel",
    description="A specialist in Search",
    instruction=SEARCH_INSTRUCTION,
    model=DEFAULT_MODEL,
    tools=[google_search, store_memory],
    output_key="search_thomas_eel_output"
    )

def get_search_thomas_eel_agent() -> Agent:
    """Returns an instance of the Search Thomas Eel Agent."""
    return search_thomas_eel_agent

root_agent = search_thomas_eel_agent 