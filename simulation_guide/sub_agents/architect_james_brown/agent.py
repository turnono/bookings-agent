"""Defines the Tech Architect Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from simulation_guide.models import DEFAULT_MODEL
from .prompts import TECH_ARCHITECT_INSTRUCTION
from .tools import identify_capability_gap, propose_agent_spec, select_toolset, risk_assessment

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
        FunctionTool(risk_assessment)
    ],
    output_key="architect_james_brown_output"  # Store output in session state with this key
)

# You might want a way to easily get this agent instance later
def get_architect_james_brown_agent() -> LlmAgent:
    """Returns an instance of the Architect James Brown Agent."""
    return architect_james_brown_agent

# Explicitly define root_agent for ADK discovery
root_agent = architect_james_brown_agent 