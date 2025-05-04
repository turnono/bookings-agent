import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';

/**
 * Read environment variables from .env file.
 */
// require('dotenv').config();

/**
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',
  /* Maximum time one test can run for. */
  timeout: 120 * 1000, // Increased to allow for server startup
  expect: {
    /**
     * Maximum time expect() should wait for the condition to be met.
     */
    timeout: 20000,
  },
  /* Run tests in files in parallel */
  fullyParallel: false, // Turn off parallel execution to avoid server conflicts
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env['CI'],
  /* Retry on CI only */
  retries: process.env['CI'] ? 2 : 1, // Add 1 retry for local tests too
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html'],
    ['list'], // Add list reporter for better console output
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:4200',
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on', // Capture traces for all test runs
    /* Capture screenshots on failure */
    screenshot: {
      mode: 'on',
      fullPage: true,
    },
    /* Set a reasonable timeout for all actions */
    actionTimeout: 15000,
    /* Record video for debugging */
    video: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 }, // Ensure consistent viewport size
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: [
    {
      command: 'npm run start',
      url: 'http://localhost:4200',
      reuseExistingServer: !process.env['CI'],
      timeout: 120 * 1000, // Extra time for Angular to compile
      stdout: 'pipe', // Pipe server output to test logs
      stderr: 'pipe',
      env: {
        NODE_ENV: 'development',
      },
    },
    {
      command:
        process.platform === 'win32'
          ? 'cd .. && set ENV=development && set DEPLOYED_CLOUD_SERVICE_URL=http://localhost:4200 && python -m uvicorn main:app --host 0.0.0.0 --port 8000'
          : 'cd .. && ENV=development DEPLOYED_CLOUD_SERVICE_URL=http://localhost:4200 python -m uvicorn main:app --host 0.0.0.0 --port 8000',
      url: 'http://localhost:8000/healthz',
      reuseExistingServer: !process.env['CI'],
      timeout: 60 * 1000,
      stdout: 'pipe', // Pipe server output to test logs
      stderr: 'pipe',
    },
  ],
});
