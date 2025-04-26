"""Defines the TaskMaster Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TASK_MASTER_INSTRUCTION
from .tools import break_down_tasks, prioritize_tasks, set_deadline, summarize_progress
from simulation_guide.tools import interact_with_firestore
from simulation_guide.tools.interact_with_firestore import sanitize_firestore_data
from simulation_guide.firestore_service import sanitize_sentinel

# Helper to always use the correct agent name
def taskmaster_interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Wrapper for the interact_with_firestore function for the taskmaster agent.
    
    Args:
        operation: The operation to perform (e.g., 'save_task', 'memorize')
        args: The arguments for the operation
        
    Returns:
        The response from the interact_with_firestore function
    """
    # Sanitize args before processing to ensure no Sentinel objects
    clean_args = sanitize_sentinel(args)
    
    # Ensure agent is tagged properly if memorizing
    if operation == "memorize" and "tags" in clean_args:
        if not any(tag.startswith("agent:") for tag in clean_args["tags"]):
            clean_args["tags"].append("agent:taskmaster_franklin_covey")
    elif operation == "memorize" and "tags" not in clean_args:
        clean_args["tags"] = ["agent:taskmaster_franklin_covey"]
    
    # Handle the Firestore operation
    response = interact_with_firestore(operation, clean_args)
    
    # Already sanitized by the new FirestoreService implementation
    return response

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