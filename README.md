# Simulation Guide Agent

A Python-based intelligent agent built with Google's Agent Development Kit (ADK) that serves as a guide to help users navigate "the simulation." The agent uses Google Vertex AI for its language model capabilities and provides specialized sub-agents for different tasks.

## Project Overview

This project implements a multi-agent system with the following components:

- **Root Agent**: Coordinates the overall interaction and manages sub-agents
- **Sub-Agents**:
  - **Architect (James Brown)**: Helps with planning and organization
  - **Taskmaster (Franklin Covey)**: Assists with task management
  - **Search (Thomas Eel)**: Handles search-related operations
  - **Coding (Steve Lanewood)**: Provides coding assistance

The system uses Firestore for data persistence, storing tasks and memories that help the agent maintain context across conversations.

## Prerequisites

- Python 3.11+
- Poetry (Python package manager)
- Google Cloud account with Vertex AI API enabled
- Google Cloud CLI (`gcloud`) installed and authenticated
  - Follow the [official installation guide](https://cloud.google.com/sdk/docs/install) to install gcloud
  - After installation, run `gcloud init` and `gcloud auth login`
- Firebase project (for Firestore database)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/turnono/simulation-guide-agent.git
cd simulation-guide-agent
```

2. Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install project dependencies:

```bash
poetry install
```

4. Activate the virtual environment:

```bash
poetry shell
# Or alternatively:
# source $(poetry env info --path)/bin/activate
```

## Configuration

1. Create a `.env` file in the project root with the following variables:

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-location  # e.g., us-central1
GOOGLE_CLOUD_STAGING_BUCKET=gs://your-bucket-name
```

2. Set up Google Cloud authentication:

```bash
gcloud auth login
gcloud config set project your-project-id
```

3. Enable required APIs:

```bash
gcloud services enable aiplatform.googleapis.com
```

4. Set up Firebase:
   - Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/)
   - Set up Firestore in your project
   - Download your Firebase service account key and save it as `sim-guide-agent-service-account.json` in the project root

## Usage

### Local Testing

The project includes deployment scripts to run the agent locally or deploy it to Google Cloud.

#### Local Deployment

Use the local deployment script to test the agent on your development machine:

```bash
# Run the local deployment script
python -m deployment.local
```

Or use the Poetry script shortcut:

```bash
poetry run python -m deployment.local
```

This will:

- Initialize Vertex AI with your project settings
- Create a local app instance
- Create a test session
- List available sessions
- Send a test query to verify functionality

### Remote Deployment

Use the remote deployment script to deploy the agent to Google Cloud:

```bash
# Deploy the agent to Google Cloud
python -m deployment.remote --create
```

After deployment, interact with the agent using:

```bash
# Create a session
python -m deployment.remote --create_session --resource_id=your-resource-id

# List sessions
python -m deployment.remote --list_sessions --resource_id=your-resource-id

# Send a message
python -m deployment.remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Your question here"

# Clean up (delete deployment)
python -m deployment.remote --delete --resource_id=your-resource-id
```

## Project Structure

```
.
├── simulation_guide/       # Core agent implementation
│   ├── agent.py            # Main agent definition
│   ├── prompt.py           # Agent prompts and instructions
│   ├── models.py           # Data models
│   ├── firestore_service.py # Firestore integration
│   ├── tools/              # Agent tools implementations
│   └── sub_agents/         # Sub-agent implementations
├── deployment/             # Deployment scripts
│   ├── local.py            # Local testing deployment
│   ├── remote.py           # Google Cloud deployment
│   └── cleanup.py          # Resource cleanup utilities
├── main.py                 # FastAPI server implementation
├── .env                    # Environment variables
├── pyproject.toml          # Python project configuration
├── poetry.lock             # Poetry dependencies lock file
├── requirements.txt        # Basic requirements
├── firebase.json           # Firebase configuration
├── sim-guide-agent-service-account.json # Firebase service account
└── Dockerfile              # Container configuration for deployment
```

## Development

### Adding New Features

To add new features to the agent:

1. **Add new tools**:

   - Create new tool functions in the `simulation_guide/tools/` directory
   - Register them with the agent in `simulation_guide/agent.py`

2. **Add new sub-agents**:

   - Create a new agent module in `simulation_guide/sub_agents/`
   - Add the sub-agent to the root agent in `simulation_guide/agent.py`

3. **Modify prompts**:

   - Update agent instructions in `simulation_guide/prompt.py`

4. **Test your changes**:
   - Run the local deployment script to verify functionality
   - Use the remote deployment for full-scale testing

### Customizing the Agent

The agent's behavior is primarily controlled by its prompt instructions and tools. To customize:

1. Modify the `SIMULATION_GUIDE_INSTRUCTION` in `prompt.py`
2. Add or remove tools from the `root_agent` configuration in `agent.py`
3. Adjust the sub-agent configuration to fit your use case

## Troubleshooting

1. **Authentication Issues**:

   - Ensure you're logged in with `gcloud auth login`
   - Verify your project ID and location in `.env`
   - Check that the Vertex AI API is enabled

2. **Deployment Failures**:

   - Check the staging bucket exists and is accessible
   - Verify all required environment variables are set
   - Ensure you have the necessary permissions in your Google Cloud project

3. **Firestore Connection Issues**:

   - Verify your service account key file is correctly set up
   - Check Firestore permissions in your Firebase project

4. **Model Access Issues**:
   - Ensure the models specified in `models.py` are available in your Vertex AI project
   - Request model access if needed through Google Cloud Console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
