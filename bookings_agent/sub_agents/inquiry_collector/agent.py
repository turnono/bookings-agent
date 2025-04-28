from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.inquiry_collector.prompts import INQUIRY_COLLECTOR_PROMPT
from bookings_agent.models import DEFAULT_MODEL

inquiry_collector_agent = LlmAgent(
    name="inquiry_collector",
    model=DEFAULT_MODEL,
    description="Collects free incoming inquiries and saves them to Firestore.",
    instruction=INQUIRY_COLLECTOR_PROMPT,
    output_key="inquiry_collector_output"
) 