import os
from google.adk.agents import Agent, LlmAgent

from simulation_guide.prompt import SIMULATION_GUIDE_INSTRUCTION
from simulation_guide.tools import count_characters
from simulation_guide.models import DEFAULT_MODEL
from simulation_guide.sub_agents.architect_james_brown.agent import architect_james_brown_agent
from simulation_guide.sub_agents.taskmaster_franklin_covey.agent import taskmaster_franklin_covey_agent
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

root_agent = LlmAgent(
    name="simulation_guide",
    model=DEFAULT_MODEL,
    description="Primary guide through the simulation. Coordinates agent activity based on user needs. Has memory capabilities to retain important information.",
    instruction=SIMULATION_GUIDE_INSTRUCTION,
    tools=[count_characters],
    sub_agents=[
        architect_james_brown_agent,
        taskmaster_franklin_covey_agent
    ],
    output_key="simulation_guide_output"
)
