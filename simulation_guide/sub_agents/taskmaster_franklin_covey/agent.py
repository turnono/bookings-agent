"""Defines the TaskMaster Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TASK_MASTER_INSTRUCTION
from .tools import break_down_tasks, prioritize_tasks, set_deadline, summarize_progress
from simulation_guide.tools import interact_with_firestore

# Helper to always use the correct agent name
def taskmaster_interact_with_firestore(user_id: str, session_id: str, memory_type: str, content: dict) -> None:
    return interact_with_firestore(user_id, session_id, memory_type, content, agent_name="taskmaster_franklin_covey")

# Define the core instruction for the TaskMaster Agent.
taskmaster_franklin_covey_agent = LlmAgent(
    name="taskmaster_franklin_covey",
    description="Assists with breaking down, prioritizing, and tracking tasks using structured productivity frameworks.",
    instruction=TASK_MASTER_INSTRUCTION,
    model=DEFAULT_MODEL,  # Using Gemini Flash for faster task management responses
    tools=[
        FunctionTool(break_down_tasks),
        FunctionTool(prioritize_tasks),
        FunctionTool(set_deadline),
        FunctionTool(summarize_progress),
        FunctionTool(taskmaster_interact_with_firestore)
    ],
    output_key="taskmaster_franklin_covey_output"  # Store output in session state with this key
)

# Function to access this agent
def get_taskmaster_franklin_covey_agent() -> LlmAgent:
    """Returns an instance of the TaskMaster Agent."""
    return taskmaster_franklin_covey_agent    

# Set as the system entrypoint agent for this package
root_agent = taskmaster_franklin_covey_agent 