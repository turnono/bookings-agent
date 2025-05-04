# End-to-End Tests Documentation

This directory contains the end-to-end (E2E) tests for the Booking Agent application. These tests
verify core functionality by simulating user interactions with the application.

## Key Features

- Automatic startup of both frontend and backend servers
- Health checks before test execution
- Resilient UI testing that doesn't depend on backend responses
- Screenshot capture at key points for debugging

## Test Implementation

The main smoke test performs these steps:

1. Verifies backend health (but continues even if failing)
2. Loads the chat interface
3. Verifies UI components are visible and interactive
4. Sends a test message
5. Verifies the message appears in the UI
6. Checks for agent responses (optional)

## Running Tests

### Basic Usage

```bash
# From the frontend directory
npm run e2e
```

This will:

1. Start both frontend and backend servers
2. Run the tests
3. Generate reports and screenshots

### Debug Mode

For troubleshooting, use the debug mode which shows the browser:

```bash
npm run e2e:debug
```

### Interactive UI Mode

For detailed investigation with the Playwright UI:

```bash
npm run e2e:ui
```

## Test Structure

Our implementation follows these Playwright best practices:

1. **Resilient selectors**: Using accessible selectors like `aria-label` attributes
2. **Explicit waits**: Clear timeouts for expected conditions
3. **Progressive enhancement**: Core UI tests pass even if backend is unavailable
4. **Health checks**: Proactive diagnosis of server issues
5. **Visual evidence**: Strategic screenshots at critical points

## Troubleshooting

If tests are failing, check:

1. **Server connectivity**: Are both servers running on the correct ports?
2. **Environment variables**: Is the backend configured with `ENV=development` and `DEPLOYED_CLOUD_SERVICE_URL`?
3. **Frontend build**: Is the Angular app compiled with the right configuration?
4. **UI changes**: Have selectors or component structure changed?

## CI Integration

Tests run automatically in GitHub Actions with:

- Explicit health checks before test execution
- Retry mechanisms for improved reliability
- Artifact collection for diagnostics
