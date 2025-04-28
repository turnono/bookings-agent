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
