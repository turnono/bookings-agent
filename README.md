# Bookings Agent

Bookings Agent is an intelligent, modular system for managing appointment bookings, user screening, and calendar protection—designed for seamless integration with social media and modern web interfaces.

## Project Objective

The goal of this project is to automate and streamline the process of booking appointments, especially for users coming from social media platforms. It ensures only relevant, serious inquiries are allowed through, protects the owner's private time, and provides a professional, guided experience from first contact to confirmed booking.

## What's Available

### Backend (Python, FastAPI, Google ADK)

- **Root Booking Guide Agent**: Orchestrates the booking flow, screens users, manages session progression, and handles calendar logic.
- **Sub-Agents**:
  - **Booking Validator**: Screens users for topic relevance and seriousness before showing available slots.
  - **Inquiry Collector**: Collects general inquiries and saves them to Firestore, without promising a reply.
- **Firestore Integration**: Stores user preferences, booking details, validation results, and inquiries in namespaced collections.
- **Calendar Management**: Integrates with Google Calendar to show only available slots, prevent double bookings, and respect blocked/private times.
- **Deployment**: Designed for Google Cloud Run deployment, with local development supported via Firestore emulator and Makefile scripts.

### Frontend (Angular 19)

- **Modern Chat UI**: Provides a real-time chat interface for users to interact with the agent, view messages, and complete bookings.
- **Session Management**: Automatically creates and manages user sessions, supporting anonymous sign-in via Firebase.
- **Integration**: Communicates with the backend via a `/run` endpoint, with proxy configuration for local development.
- **Material Design**: Uses Angular Material for a polished, responsive user experience.

## System Architecture

- **Backend**: Python, FastAPI, Google ADK, Firestore, Google Calendar, Paystack integration.
- **Frontend**: Angular 19, Angular Material, Firebase Auth, RxJS.

## Key Features

- User screening and topic validation before showing available slots
- Private time and double booking protection
- Smart appointment suggestions and reminders
- Inquiry collection for general requests

## Data Storage

- **Firestore Collections**:
  - `booking_memories`: Owner preferences, blocked times, recurring patterns
  - `booking_bookings`: Appointment details, status, user info
  - `booking_validations`: Validation and screening results
  - `inquiries`: General user inquiries

## Development & Deployment

- **Local Development**: Use the Firestore emulator and Makefile for running backend and frontend locally.
- **Cloud Deployment**: Deploy to Google Cloud Run using the provided Makefile.
- **Frontend**: Run with `npm start` in the `frontend/` directory.
- **Backend**: Run with `python main.py` (ensure Firestore credentials are set).

## Summary

Bookings Agent is a robust, extensible platform for managing appointment bookings with intelligent screening, calendar protection, and a modern chat-based frontend. It is suitable for professionals and businesses seeking to automate and secure their booking workflows, especially when handling high volumes of social media inquiries.

## Features

- Interactive chat interface for booking appointments
- Schedule selection with calendar integration
- Email validation and notifications
- Persistent storage of bookings in Firestore

## Installation

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

## Running the Application

### Backend

```bash
# Start the backend server
python -m uvicorn bookings_agent.main:app --reload
```

### Frontend

```bash
# Start the frontend development server
cd frontend
npm start
```

Visit http://localhost:4200 in your browser to use the application.

## Running End-to-End Tests

The application includes Playwright-based smoke tests to verify core functionality. These tests require both the frontend and backend to be running correctly.

### Setup for Testing

1. Make sure you have installed all dependencies for both frontend and backend:

```bash
# For backend
pip install -r requirements.txt

# For frontend
cd frontend
npm install
```

2. Install Playwright browsers:

```bash
cd frontend
npx playwright install --with-deps
```

### Running Tests Locally

To run the tests properly, you need to:

1. Start the backend server with the correct environment variables:

```bash
# In one terminal (from the project root)
ENV=development DEPLOYED_CLOUD_SERVICE_URL=http://localhost:4200 python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Start the frontend server:

```bash
# In another terminal
cd frontend
npm start
```

3. Run the tests:

```bash
# In a third terminal
cd frontend
npx playwright test
```

For a more visual experience, you can run the tests with the browser visible:

```bash
cd frontend
npx playwright test --headed
```

### Test Output and Debugging

The tests will:

1. Load the initial chat interface
2. Send a greeting message
3. Wait for and verify the agent's response
4. Take screenshots at key points for debugging

Screenshots are saved in the frontend directory with names like:

- `01-initial-load.png`
- `02-greeting-sent.png`
- `03-agent-responded.png`

### Troubleshooting Tests

If tests are failing, try the following:

1. Check that the backend environment variables are properly set:

   - `ENV=development`
   - `DEPLOYED_CLOUD_SERVICE_URL=http://localhost:4200`

2. Ensure both servers are running successfully before starting the tests

3. Check the screenshots to see what might be going wrong

4. Increase timeouts in `e2e/booking-flow.spec.ts` if the agent is taking longer to respond

5. Try running with the UI for better debugging:

```bash
cd frontend
npx playwright test --headed
```

6. View the detailed HTML test report:

```bash
cd frontend
npx playwright show-report
```

### CI Integration

Tests are automatically run on GitHub Actions when code is pushed to the main branch. The workflow:

1. Sets up both frontend and backend environments
2. Starts both servers with correct environment variables
3. Runs the smoke tests
4. Uploads screenshots and test reports as artifacts

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
CALENDAR_ID=your-calendar-id@group.calendar.google.com
```
