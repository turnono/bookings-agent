"""Defines the Tech Architect Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
# from guide_zero_simulation.tools.memory import memorize, memorize_list, forget, get_memory, list_memories
# from guide_zero_simulation.tools.state_aware_tools import get_agent_responses, get_conversation_summary, store_user_preference
# from guide_zero_simulation.tools.agent_response_tracker import track_agent_response
# from guide_zero_simulation.tools.safety_guardrails import input_safety_guardrail, tool_usage_guardrail
from simulation_guide.models import gemini_pro, gemini_flash, DEFAULT_MODEL
from .prompts import TECH_ARCHITECT_INSTRUCTION

# Define memory tools
# memory_tools = [
#     FunctionTool(memorize),
#     FunctionTool(memorize_list),
#     FunctionTool(forget),
#     FunctionTool(get_memory),
#     FunctionTool(list_memories)
# ]

# # Define state-aware tools
# state_tools = [
#     FunctionTool(get_agent_responses),
#     FunctionTool(get_conversation_summary),
#     FunctionTool(store_user_preference)
# ]

# Combine all tools
# all_tools = memory_tools + state_tools

# Define the core instruction for the Tech Architect Agent.
# It should guide the LLM to produce a structured blueprint.
architect_james_brown_agent = LlmAgent(
    name="architect_james_brown",
    description="Designs the technical foundation and blueprints for AI agents.",
    instruction=TECH_ARCHITECT_INSTRUCTION,
    model=gemini_pro,  # Using Gemini Pro for complex architectural tasks
    # tools=all_tools,  # Add all tools
    # after_agent_callback=track_agent_response,  # Track agent responses
    # before_model_callback=input_safety_guardrail,  # Add input safety guardrail
    # before_tool_callback=tool_usage_guardrail,  # Add tool usage guardrail
    output_key="architect_james_brown_output"  # Store output in session state with this key
)

# You might want a way to easily get this agent instance later
def get_architect_james_brown_agent() -> LlmAgent:
    """Returns an instance of the Architect James Brown Agent."""
    return architect_james_brown_agent

# Explicitly define root_agent for ADK discovery
root_agent = architect_james_brown_agent 