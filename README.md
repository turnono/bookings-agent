# Booking Agent

A specialized agent system for guiding social media users through the appointment booking process, with intelligent screening and calendar protection.

## Purpose

The Booking Agent system serves as an intelligent intermediary between social media inquiries and your calendar:

1. **Social Media Gateway**: Efficiently handles appointment booking requests from users coming from social media platforms.

2. **User Screening**: Filters users by checking topic relevance and seriousness before showing available times.

3. **Smart Calendar Management**:

   - Only shows available time slots based on owner preferences
   - Protects private time (no bookings during blocked times)
   - Prevents double bookings or calendar conflicts

4. **Seamless Experience**: Maintains a professional, smooth experience from first message to confirmed booking.

## System Architecture

The Booking Agent consists of two specialized agents:

1. **Booking Guide Agent (Root)**: Primary agent that screens users, presents available time slots, and handles the booking process.

2. **Booking Validator Agent (Sub-agent)**: Specialized agent for validating appointment requests, checking calendar availability, and ensuring they don't conflict with private time.

## Key Features

- Thorough user screening before showing available slots
- Topic relevance verification to ensure alignment with expertise
- Private time protection to maintain personal boundaries
- Double booking prevention
- Smart appointment suggestions based on conversation context
- Appointment confirmation and reminders

## Tools

The root agent (Booking Guide) has access to these function tools:

- **MemoryTool (Firestore)**: Store and retrieve user preferences, booking history, and blocked times
- **ValidationTool**: Screen appointment requests for relevance and seriousness
- **CalendarTool**: Check availability while respecting private time
- **BookingConfirmationTool**: Send appointment confirmations to users

## Firestore Collections

All Firestore collections are namespaced for the booking system:

- **booking_memories**: For storing owner preferences, blocked times, and recurring patterns
- **booking_bookings**: For tracking appointment details, status, and user information
- **booking_validations**: For storing validation records and screening results

## Project Structure

```
bookings_agent/
├── __init__.py
├── agent.py                      # Root agent definition
├── prompt.py                     # Root agent prompt
├── models.py                     # Model definitions
├── firestore_service.py          # Firestore service
├── tools/
│   ├── __init__.py
│   ├── current_time.py           # Time utility
│   └── interact_with_firestore.py # Firestore interaction
└── sub_agents/
    ├── __init__.py
    └── booking_validator/        # Booking Validator sub-agent
        ├── __init__.py
        ├── agent.py              # Validator agent definition
        └── prompts.py            # Validator agent prompt
```

## Booking Process Flow

1. **Initial Screening**: When a user requests an appointment, the agent asks qualifying questions to assess relevance and seriousness.

2. **Topic Validation**: The agent verifies that the appointment topic falls within the owner's expertise.

3. **Calendar Check**: If the user passes screening, the agent shows available time slots that respect private time.

4. **Appointment Details**: The agent collects necessary details for the appointment.

5. **Confirmation**: The appointment is confirmed and added to the calendar, with confirmation sent to the user.

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Firestore credentials

   - Obtain a Google Cloud service account key with Firestore access (JSON file).
   - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account file before running the app:

     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
     ```

   - This is required for Firestore access unless you are using the Firestore emulator.

4. Configure your calendar preferences and blocked times
5. Run the main application: `python main.py`
