"""Defines the TaskMaster Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TASK_MASTER_INSTRUCTION
from .tools import break_down_tasks, prioritize_tasks, set_deadline, summarize_progress
from simulation_guide.tools import store_memory

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
        store_memory
    ],
    output_key="taskmaster_franklin_covey_output"  # Store output in session state with this key
)

# Function to access this agent
def get_taskmaster_franklin_covey_agent() -> LlmAgent:
    """Returns an instance of the TaskMaster Agent."""
    return taskmaster_franklin_covey_agent    

# Set as the system entrypoint agent for this package
root_agent = taskmaster_franklin_covey_agent 