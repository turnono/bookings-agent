"""Defines the Tech Architect Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TECH_ARCHITECT_INSTRUCTION
from .tools import identify_capability_gap, propose_agent_spec, select_toolset, risk_assessment
from simulation_guide.tools import interact_with_firestore
from simulation_guide.tools.interact_with_firestore import sanitize_firestore_data
from simulation_guide.firestore_service import sanitize_sentinel

# Helper to always use the correct agent name
def architect_interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Wrapper for the interact_with_firestore function for the architect agent.
    
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
            clean_args["tags"].append("agent:architect_james_brown")
    elif operation == "memorize" and "tags" not in clean_args:
        clean_args["tags"] = ["agent:architect_james_brown"]
    
    # Handle the Firestore operation
    response = interact_with_firestore(operation, clean_args)
    
    # Already sanitized by the new FirestoreService implementation
    return response

# Define the core instruction for the Tech Architect Agent.
# It should guide the LLM to produce a structured blueprint.
architect_james_brown_agent = LlmAgent(
    name="architect_james_brown",
    description="Designs the technical foundation and blueprints for AI agents.",
    instruction=TECH_ARCHITECT_INSTRUCTION,
    model=DEFAULT_MODEL,  # Using Gemini Pro for complex architectural tasks
    tools=[
        FunctionTool(identify_capability_gap),
        FunctionTool(propose_agent_spec),
        FunctionTool(select_toolset),
        FunctionTool(risk_assessment),
        FunctionTool(architect_interact_with_firestore)
    ],
    output_key="architect_james_brown_output"  # Store output in session state with this key
)

# You might want a way to easily get this agent instance later
def get_architect_james_brown_agent() -> LlmAgent:
    """Returns an instance of the Architect James Brown Agent."""
    return architect_james_brown_agent

# Explicitly define root_agent for ADK discovery
root_agent = architect_james_brown_agent 