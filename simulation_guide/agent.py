import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import agent_tool, FunctionTool
from dotenv import load_dotenv

from simulation_guide.prompt import SIMULATION_GUIDE_INSTRUCTION
from simulation_guide.tools import count_characters, current_time, interact_with_firestore
from simulation_guide.models import DEFAULT_MODEL
from simulation_guide.sub_agents.architect_james_brown.agent import architect_james_brown_agent
from simulation_guide.sub_agents.taskmaster_franklin_covey.agent import taskmaster_franklin_covey_agent
from simulation_guide.sub_agents.search_thomas_eel.agent import search_thomas_eel_agent
from simulation_guide.sub_agents.coding_steve_lanewood.agent import coding_steve_lanewood_agent

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

root_agent = LlmAgent(
    name="simulation_guide",
    model=DEFAULT_MODEL,
    description="Primary guide through the simulation. Coordinates agent activity based on user needs. Has memory capabilities to retain important information.",
    instruction=SIMULATION_GUIDE_INSTRUCTION,
    tools=[agent_tool.AgentTool(search_thomas_eel_agent),
           agent_tool.AgentTool(coding_steve_lanewood_agent),
           count_characters,
           FunctionTool(interact_with_firestore),
           current_time,
           ],
    sub_agents=[
        architect_james_brown_agent,
        taskmaster_franklin_covey_agent,
    ],
    output_key="simulation_guide_output"
)
