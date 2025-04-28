from bookings_agent.tools.google_calendar import create_event
from bookings_agent.tools.interact_with_firestore import interact_with_firestore

def handle_payment_confirmed(booking_id: str, user_id: str) -> str:
    """
    When payment is confirmed, create the calendar event, update the booking, and return a confirmation message.
    """
    # 1. Fetch booking details
    booking_resp = interact_with_firestore("get_booking", {"user_id": user_id, "booking_id": booking_id})
    booking = booking_resp.get("data")
    if not booking:
        return "Sorry, we could not find your booking to confirm the event. Please contact support."

    slot = booking.get("selected_slot", {})
    summary = booking.get("discussion_summary", "Consultation")
    email = booking.get("email")
    # 2. Create calendar event if not already created
    if slot.get("start") and slot.get("end") and email:
        event = create_event(
            summary=summary,
            start_time=slot["start"],
            end_time=slot["end"],
            attendees=[email]
        )
        # 3. Update booking with event link
        interact_with_firestore("update_booking", {
            "user_id": user_id,
            "booking_id": booking_id,
            "updates": {"calendar_event_link": event["htmlLink"]}
        })
        # 4. Return confirmation message
        return f"Your payment is confirmed and your booking is scheduled!\n\nEvent: {summary}\nTime: {slot['start']} to {slot['end']}\nCalendar link: {event['htmlLink']}"
    else:
        return "Your payment is confirmed, but we could not create the calendar event due to missing information. Please contact support." 