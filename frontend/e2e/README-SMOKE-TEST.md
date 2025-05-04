# Booking Agent Enhanced Smoke Test

This enhanced smoke test provides a resilient way to verify the booking agent UI functionality while capturing detailed diagnostic information about any failures, particularly focusing on backend 422 errors.

## What's Tested

The test verifies that:

1. The Angular application loads successfully
2. The chat interface is visible and interactive
3. Users can enter and send messages
4. The UI properly displays user messages
5. Agent responses are detected (if backend is working)
6. The full booking flow is attempted (if backend is working)
   - Email input
   - Date selection
   - Time slot selection
   - Booking confirmation

## Key Features

- **Backend Resilience**: The test will not fail if the backend is unavailable
- **Flexible Selectors**: Uses multiple fallback selectors to adapt to UI changes
- **Detailed Logging**: Provides comprehensive diagnostic information
- **422 Error Debugging**: Special handling to capture and diagnose 422 errors
- **Network Traffic Analysis**: Records all API requests and responses
- **Visual Evidence**: Takes screenshots at each key step
- **Progressive Testing**: Attempts the full booking flow only if agent responds

## Running the Test

```bash
# Basic execution
npm run smoke-test

# With visual browser (for debugging)
npx playwright test e2e/booking-flow.spec.ts --headed

# With debug mode for step-by-step analysis
npm run e2e:debug -- e2e/booking-flow.spec.ts
```

## Diagnostic Output

The test generates extensive diagnostic information:

1. **Screenshots**: Captures the UI state at each critical step
2. **Network Logs**: Records all API requests and responses in `debug-logs/`
3. **Console Errors**: Captures browser console errors
4. **422 Error Details**: Special handling for 422 errors with detailed information

### Diagnosing 422 Errors

When a 422 error occurs, the test:

1. Captures the complete request and response
2. Records the error details and status text
3. Identifies the matching request for the error
4. Logs the parsed JSON payload that caused the error
5. Saves all information to `debug-logs/422-error-details.json`

## CI/CD Integration

The test is integrated with GitHub Actions and will automatically:

1. Verify the UI on each push to the main branch
2. Generate comprehensive reports and screenshots
3. Continue testing even if backend services have issues
4. Upload detailed debug logs as separate artifacts

## Troubleshooting

If the test fails:

1. Check the screenshots in the `frontend/` directory
2. Examine the `debug-logs/` directory for detailed network logs
3. Look for 422 error details in `debug-logs/422-error-details.json`
4. Check the console output for specific error messages
5. Review the backend logs for server-side issues

## Extending the Test

The test is designed to be easily extended:

1. Add more selectors to the selector arrays if UI elements change
2. Enhance the full booking flow section as new features are added
3. Add additional screenshots at critical points
4. Extend the network logging for new API endpoints

## Resilient Design Philosophy

This test follows a resilient design philosophy:

1. **Progressive Enhancement**: Tests basic functionality first, then attempts more advanced flows
2. **Graceful Degradation**: Continues testing what's possible even when parts fail
3. **Multiple Detection Strategies**: Uses various selectors to find UI elements
4. **Comprehensive Logging**: Captures detailed information to diagnose issues
5. **Failure Isolation**: Ensures failures in one area don't prevent testing others
