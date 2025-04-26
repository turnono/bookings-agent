import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import agent_tool, FunctionTool
from dotenv import load_dotenv

from simulation_guide.prompt import SIMULATION_GUIDE_INSTRUCTION
from simulation_guide.tools import count_characters, current_time, interact_with_firestore
from simulation_guide.tools.interact_with_firestore import sanitize_firestore_data
from simulation_guide.firestore_service import sanitize_sentinel
from simulation_guide.models import DEFAULT_MODEL
from simulation_guide.sub_agents.architect_james_brown.agent import architect_james_brown_agent
from simulation_guide.sub_agents.taskmaster_franklin_covey.agent import taskmaster_franklin_covey_agent
from simulation_guide.sub_agents.search_thomas_eel.agent import search_thomas_eel_agent
from simulation_guide.sub_agents.coding_steve_lanewood.agent import coding_steve_lanewood_agent

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

# Wrapper for interact_with_firestore specific to the simulation_guide agent
def simulation_guide_interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Execute Firestore operations on behalf of the simulation guide agent.
    
    This tool can create, read, update, and delete tasks and memories in Firestore.
    Each operation is automatically associated with the current user and session.
    
    Args:
        operation: The operation to perform. Valid operations include:
            - 'save_task': Create or update a task
            - 'get_task': Get a task by ID
            - 'update_task': Update a task by ID
            - 'delete_task': Delete a task by ID
            - 'list_tasks': List tasks with optional filtering
            - 'memorize': Create a new memory
            - 'get_memory': Get a memory by ID
            - 'update_memory': Update a memory by ID
            - 'delete_memory': Delete a memory by ID
            - 'list_memories': List memories with optional filtering
        args: The arguments for the operation. For example:
            - For 'save_task': {'description': 'Task description', 'status': 'pending'}
            - For 'get_task': {'task_id': 'task123'}
            - For 'list_tasks': {'filters': {'status': 'pending'}}
        
    Returns:
        Dict with operation results:
        - success (bool): Whether the operation succeeded
        - data: The operation result data (if applicable)
        - error: Error information (if operation failed)
    """
    # Sanitize args before processing to ensure no Sentinel objects
    clean_args = sanitize_sentinel(args)
    
    # Skip adding default user_id and session_id - tool_context will handle this automatically
    # Instead, just ensure agent tagging is applied for memory operations
    
    # Ensure agent is tagged properly if memorizing
    if operation == "memorize" and "tags" in clean_args:
        if not any(tag.startswith("agent:") for tag in clean_args["tags"]):
            clean_args["tags"].append("agent:simulation_guide")
    elif operation == "memorize" and "tags" not in clean_args:
        clean_args["tags"] = ["agent:simulation_guide"]
    
    # Call the interact_with_firestore function
    # The ToolContext will be automatically injected by ADK
    response = interact_with_firestore(operation, clean_args)
    
    return response

root_agent = LlmAgent(
    name="simulation_guide",
    model=DEFAULT_MODEL,
    description="Primary guide through the simulation. Coordinates agent activity based on user needs. Has memory capabilities to retain important information.",
    instruction=SIMULATION_GUIDE_INSTRUCTION,
    tools=[agent_tool.AgentTool(search_thomas_eel_agent),
           agent_tool.AgentTool(coding_steve_lanewood_agent),
           count_characters,
           FunctionTool(simulation_guide_interact_with_firestore),
           current_time,
           ],
    sub_agents=[
        architect_james_brown_agent,
        taskmaster_franklin_covey_agent,
    ],
    output_key="simulation_guide_output"
)
