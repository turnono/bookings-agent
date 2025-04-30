from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.payment_agent.prompts import PAYMENT_AGENT_PROMPT
from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.sub_agents.payment_agent.paystack_api import PaystackAPI
import os

payment_agent = LlmAgent(
    name="payment_agent",
    model=DEFAULT_MODEL,
    description="Handles Paystack checkout and webhook verification for consultation bookings.",
    instruction=PAYMENT_AGENT_PROMPT,
    output_key="payment_agent_output"
)

def create_paystack_checkout(amount: int, email: str, booking_id: str, user_id: str) -> str:
    """
    Initialize a Paystack payment session and return the checkout URL.
    Args:
        amount (int): Amount in kobo (NGN * 100)
        email (str): Customer's email address
        booking_id (str): Booking identifier for metadata
        user_id (str): User identifier for metadata
    Returns:
        str: Paystack checkout URL for user payment
    """
    metadata = {"bookingId": booking_id, "userId": user_id}
    # Use PAYSTACK_CALLBACK_URL if set, otherwise use localhost:4200/payment-complete
    
    IS_DEV_MODE = os.getenv("ENV").lower() == "development"
    print(f"IS_DEV_MODE: {IS_DEV_MODE}")
    if IS_DEV_MODE:
        callback_url = "http://localhost:4200/payment-complete"
    else:
        callback_url = os.getenv(
            "PAYSTACK_CALLBACK_URL",
            "https://tjr-scheduler.web.app/payment-complete"
        )
    resp = PaystackAPI.initialize_transaction(amount, email, metadata, callback_url=callback_url)
    return resp["data"]["authorization_url"] 