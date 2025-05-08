# Contributing to Bookings Agent

We love your input! We want to make contributing to Bookings Agent as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Local Development Setup

1. Clone your fork
2. Create necessary config files:
   - Copy `.env.example` to `.env` and fill in your values
   - Create `service-account.json` with your Google Cloud credentials
   - Update Firebase config in frontend environment files
3. Install dependencies:

   ```bash
   # Backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

## Testing

Before submitting a PR, please ensure:

1. All existing tests pass
2. New tests are added for new features
3. Run the e2e tests as described in the README

## Any Questions?

Feel free to create an issue to discuss any questions or concerns.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
