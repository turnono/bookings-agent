import os

import uvicorn
from fastapi import FastAPI, Request, Response, status, Query
from google.adk.cli.fast_api import get_fast_api_app
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from bookings_agent.sub_agents.payment_agent.paystack_api import PaystackAPI
from bookings_agent.tools.interact_with_firestore import interact_with_firestore

IS_DEV_MODE = os.getenv("ENV").lower() == "development"
DEPLOYED_CLOUD_SERVICE_URL = os.getenv("DEPLOYED_CLOUD_SERVICE_URL")

print(f"DEPLOYED_CLOUD_SERVICE_URL: {DEPLOYED_CLOUD_SERVICE_URL}")

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["https://tjr-scheduler.web.app", DEPLOYED_CLOUD_SERVICE_URL]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = False

app: FastAPI = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

@app.post("/webhooks/paystack")
async def paystack_webhook(request: Request):
    signature = request.headers.get("x-paystack-signature")
    body = await request.body()
    try:
        if not signature or not PaystackAPI.verify_webhook_signature(body, signature):
            return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid signature")
        event = await request.json()
        data = event.get("data", {})
        status_ = data.get("status")
        metadata = data.get("metadata", {})
        booking_id = metadata.get("bookingId")
        user_id = metadata.get("userId")
        reference = data.get("reference")
        if status_ == "success":
            # Update booking as confirmed in Firestore
            if booking_id and user_id:
                interact_with_firestore("update_booking", {"user_id": user_id, "booking_id": booking_id, "updates": {"payment_status": "completed", "status": "confirmed", "transaction_id": reference}})
            return {"payment_confirmed": True, "bookingId": booking_id, "transactionId": reference}
        else:
            if booking_id and user_id:
                interact_with_firestore("update_booking", {"user_id": user_id, "booking_id": booking_id, "updates": {"payment_status": "failed", "status": "pending"}})
            return {"payment_rejected": True, "bookingId": booking_id, "reason": status_ or "failed"}
    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Webhook error: {str(e)}")

@app.get("/payment/complete")
async def payment_complete(request: Request):
    # Optionally, you can extract query params like reference, status, etc.
    # reference = request.query_params.get("reference")
    return Response(
        content="""
        <html>
        <head><title>Payment Complete</title></head>
        <body>
            <h2>Thank you! Your payment was successful and your booking is confirmed.</h2>
            <p>You may now close this window.</p>
        </body>
        </html>
        """,
        media_type="text/html"
    )

@app.get("/api/payment-status")
async def payment_status(reference: str = Query(...)):
    """
    Verify payment with Paystack and confirm booking if successful.
    """
    # 1. Verify with Paystack
    paystack_resp = PaystackAPI.verify_transaction(reference)
    status_ = paystack_resp.get("data", {}).get("status")
    metadata = paystack_resp.get("data", {}).get("metadata", {})
    booking_id = metadata.get("bookingId")
    user_id = metadata.get("userId")

    # 2. Find booking by booking_id and user_id
    booking = None
    if booking_id and user_id:
        booking_resp = interact_with_firestore("get_booking", {"user_id": user_id, "booking_id": booking_id})
        booking = booking_resp.get("data")

    # 3. If payment is successful and booking not yet confirmed, update it
    if status_ == "success" and booking and booking.get("payment_status") != "completed":
        interact_with_firestore("update_booking", {
            "user_id": user_id,
            "booking_id": booking_id,
            "updates": {"payment_status": "completed", "status": "confirmed", "transaction_id": reference}
        })

    # 4. Return status for UI/agent
    return {
        "payment_status": status_,
        "booking": booking,
        "booking_confirmed": status_ == "success"
    }

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))