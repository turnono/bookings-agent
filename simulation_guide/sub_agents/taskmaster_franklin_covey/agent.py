"""Defines the TaskMaster Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
# from guide_zero_simulation.tools.memory import memorize, memorize_list, forget, get_memory, list_memories
# from guide_zero_simulation.tools.state_aware_tools import get_agent_responses, get_conversation_summary, store_user_preference
# from .tools.agent_response_tracker import track_agent_response
# from guide_zero_simulation.tools.safety_guardrails import input_safety_guardrail, tool_usage_guardrail
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TASK_MASTER_INSTRUCTION

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

# # Combine all tools
# all_tools = memory_tools + state_tools

# Define the core instruction for the TaskMaster Agent.
taskmaster_franklin_covey_agent = LlmAgent(
    name="taskmaster_franklin_covey",
    description="Assists with breaking down, prioritizing, and tracking tasks using structured productivity frameworks.",
    instruction=TASK_MASTER_INSTRUCTION,
    model=DEFAULT_MODEL,  # Using Gemini Flash for faster task management responses
    # tools=all_tools,  # Add all tools
    # after_agent_callback=track_agent_response,  # Track agent responses
    # before_model_callback=input_safety_guardrail,  # Add input safety guardrail
    # before_tool_callback=tool_usage_guardrail,  # Add tool usage guardrail
    output_key="taskmaster_franklin_covey_output"  # Store output in session state with this key
)

# Function to access this agent
def get_taskmaster_franklin_covey_agent() -> LlmAgent:
    """Returns an instance of the TaskMaster Agent."""
    return taskmaster_franklin_covey_agent    

# Set as the system entrypoint agent for this package
root_agent = taskmaster_franklin_covey_agent 