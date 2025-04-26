import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import agent_tool, FunctionTool
from dotenv import load_dotenv
from google.adk.agents.extra_agents import ToolkitAgent
from google.adk.agents.toolkit_tool import ToolkitTool

from bookings_agent.prompt import BOOKINGS_AGENT_INSTRUCTION
from bookings_agent.tools import count_characters, current_time, interact_with_firestore
from bookings_agent.tools.interact_with_firestore import sanitize_firestore_data
from bookings_agent.firestore_service import sanitize_sentinel
from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.sub_agents.architect_james_brown.agent import architect_james_brown_agent
from bookings_agent.sub_agents.taskmaster_franklin_covey.agent import taskmaster_franklin_covey_agent
from bookings_agent.sub_agents.search_thomas_eel.agent import search_thomas_eel_agent
from bookings_agent.sub_agents.coding_steve_lanewood.agent import coding_steve_lanewood_agent

from absl import logging
import uuid

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

# Wrapper for interact_with_firestore specific to the bookings_agent agent
def bookings_agent_interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Wrapper for the interact_with_firestore tool that automatically adds the
    simulation guide agent tag to memories and tasks.
    
    Args:
        operation: The Firestore operation to perform
        args: The arguments for the operation
    
    Returns:
        The result of the Firestore operation
    """
    # Clean the args to ensure they're safe for Firestore
    clean_args = sanitize_firestore_data(args)
    
    # For memorize and save_task operations, ensure the agent is tagged
    if operation in ["memorize", "save_task"]:
        # Add a tag for this agent
        if "tags" in clean_args and isinstance(clean_args["tags"], list):
            clean_args["tags"].append("agent:bookings_agent")
        else:
            clean_args["tags"] = ["agent:bookings_agent"]
    
    # Call the base interact_with_firestore tool
    result = interact_with_firestore(operation, clean_args)
    
    # Clean the result for return
    return sanitize_sentinel(result)

root_agent = LlmAgent(
    name="bookings_agent",
    model=DEFAULT_MODEL,
    description="Primary guide through the simulation. Coordinates agent activity based on user needs. Has memory capabilities to retain important information.",
    instruction=BOOKINGS_AGENT_INSTRUCTION,
    tools=[
        FunctionTool(count_characters),
        FunctionTool(current_time),
        FunctionTool(bookings_agent_interact_with_firestore),
        ToolkitTool(agent=architect_james_brown_agent),
        ToolkitTool(agent=taskmaster_franklin_covey_agent),
        ToolkitTool(agent=search_thomas_eel_agent),
        ToolkitTool(agent=coding_steve_lanewood_agent),
    ],
    output_key="bookings_agent_output"
)
