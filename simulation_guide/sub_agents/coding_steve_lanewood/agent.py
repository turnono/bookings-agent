from google.adk.agents import Agent
from simulation_guide.models import DEFAULT_MODEL
from .prompts import CODING_INSTRUCTION
from google.adk.tools import built_in_code_execution
from simulation_guide.tools import store_memory
from google.adk.tools import FunctionTool

# Helper to always use the correct agent name
def coding_steve_store_memory(user_id: str, session_id: str, memory_type: str, content: dict) -> None:
    return store_memory(user_id, session_id, memory_type, content, agent_name="coding_steve_lanewood")

coding_steve_lanewood_agent = Agent(
    name="coding_steve_lanewood",
    description="A specialist in Code Execution",
    instruction=CODING_INSTRUCTION,
    model=DEFAULT_MODEL,
    tools=[built_in_code_execution],
    output_key="coding_steve_lanewood_output"
)

def get_coding_steve_lanewood_agent() -> Agent:
    """Returns an instance of the Coding Steve Lanewood Agent."""
    return coding_steve_lanewood_agent

root_agent = coding_steve_lanewood_agent 