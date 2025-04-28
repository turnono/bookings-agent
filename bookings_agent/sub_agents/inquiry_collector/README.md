# Inquiry Collector Agent

## Purpose

Collects free incoming requests and inquiries, gathers user details, and saves them to Firestore under the `inquiries` collection. Never promises a reply.

## Behavior

- Greets users warmly and checks if they want Abdullah to contact them.
- Collects name, email, type of inquiry, and message.
- Saves all details to Firestore (`inquiries` collection).
- Sends a polite thank-you message.
- Never promises a reply or offers paid services.

## Integration Notes

- Exposed as `inquiry_collector_agent` in the package.
- Uses the `INQUIRY_COLLECTOR_PROMPT` for LLM instructions.
- Firestore integration should use a method to save to the `inquiries` collection (see `firestore_service.py`).
