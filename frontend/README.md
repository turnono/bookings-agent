# Bookings Agent Frontend

This is the Angular frontend for the Bookings Agent project. It provides a chat interface to interact with your ADK agent backend.

---

## Features

- Modern Angular (standalone components)
- Chat UI for interacting with the agent
- Displays all agent/user/system messages and events
- Integrates with backend via `/run` endpoint
- Automatically creates a session on chat start
- Uses Angular proxy to bypass CORS in development

---

## Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Proxy Configuration (Development)

The Angular dev server is configured to proxy `/run` requests to the backend, avoiding CORS issues.

- See `proxy.conf.json`:
  ```json
  {
    "/run": {
      "target": "http://localhost:8000",
      "secure": false
    }
  }
  ```
- The `start` script in `package.json` uses this proxy:
  ```json
  "start": "ng serve --proxy-config proxy.conf.json"
  ```

### 3. Running the Frontend

```bash
npm start
```

This will start the Angular app at [http://localhost:4200](http://localhost:4200).

### 4. Backend Requirements

- The backend (ADK agent server) must be running at `http://localhost:8000`.
- The `/run` endpoint must be available.

### 5. Session Creation

- The frontend automatically creates a session for the user and session ID when the chat loads.
- If the session already exists, it proceeds without error.
- You can customize the user/session IDs in `src/app/agent.service.ts`.

---

## File Overview

- `src/app/agent.service.ts`: Handles API calls and session creation.
- `src/app/chat/chat.component.ts`: Chat UI and logic.
- `proxy.conf.json`: Proxy config for development.
- `package.json`: Scripts and dependencies.

---

## Customization

- **User/Session IDs:**
  - Change `userId` and `sessionId` in `agent.service.ts` for per-user sessions.
- **Backend URL:**
  - For production, update the API URLs and proxy config as needed.

---

## Troubleshooting

- **CORS errors:**
  - Ensure you use `/run` (not a full URL) in the service, and the proxy is active.
- **404 Not Found:**
  - Make sure the backend is running and a session exists (the frontend now creates it automatically).

---

## License

MIT

## Development Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Testing

Run the smoke test to verify basic functionality:

```bash
npm run smoke-test
```

## Recent Fixes

### Fixed 422 Validation Error (May 2025)

- **Issue**: Backend rejected requests with 422 errors when `user_id` was null
- **Root Cause**: The API requires `user_id` to be a non-null string, but the frontend was sending null
- **Fix**: Modified `AgentService.sendMessage()` to never send a null user_id by:
  - Using the Firebase UID when available
  - Falling back to "anonymous-user" when no UID is available
- **Verification**: Confirmed via the smoke test that the fix resolves the 422 error

### Fixed 404 Session Not Found Error (May 2025)

- **Issue**: Backend returned 404 errors because the session didn't exist
- **Root Cause**: Messages were being sent before the session was created in the backend
- **Fix**: Enhanced session management in several ways:
  - Added `ensureSessionExists()` method to create sessions before sending messages
  - Updated all message sending methods to ensure a session exists first
  - Made chat initialization create a session automatically
  - Added proper error handling for session creation failures
- **Verification**: Confirmed the backend now returns 200 OK responses instead of 404 errors

## Future Enhancements

Once backend session issues are resolved (currently returning 404), the booking flow tests will automatically extend to verify:

- Email input
- Date selection
- Time slot selection
- Booking confirmation
