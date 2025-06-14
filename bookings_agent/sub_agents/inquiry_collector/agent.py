from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.inquiry_collector.prompts import INQUIRY_COLLECTOR_PROMPT
from bookings_agent.models import DEFAULT_MODEL
from google.adk.tools import FunctionTool
from bookings_agent.tools.save_user_enquiry import save_user_inquiry
from bookings_agent.tools.interact_with_firestore import interact_with_firestore

inquiry_collector_agent = LlmAgent(
    name="inquiry_collector",
    model=DEFAULT_MODEL,
    description="Collects free incoming inquiries and saves them to Firestore.",
    instruction=INQUIRY_COLLECTOR_PROMPT,
    tools=[
        FunctionTool(save_user_inquiry),
        FunctionTool(interact_with_firestore)
    ],
    output_key="inquiry_collector_output"
) 