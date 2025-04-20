# TaskMaster Agent (Franklin Covey)

An AI agent that helps break down, prioritize, and track tasks using structured productivity frameworks.

## Core Purpose

The TaskMaster agent assists the Simulation Guide Agent by analyzing tasks and providing structured guidance. It excels at breaking complex tasks into manageable pieces, prioritizing using the Eisenhower Matrix, providing realistic scheduling recommendations, suggesting delegation opportunities, and establishing progress tracking frameworks.

## Capabilities

- Break down large, complex tasks into smaller, actionable subtasks
- Prioritize tasks using the Eisenhower Matrix (Urgent/Important framework)
- Suggest realistic time estimates and scheduling
- Recommend which tasks should be delegated to other specialized agents
- Track progress and create accountability structures
- Allocate tasks across available daily hours based on priorities and estimated durations
- Assign mental energy levels to tasks and schedule accordingly

## Input Format

The agent expects:

- List of tasks or objectives (either well-defined or vague)
- Available time constraints
- User's stated priorities or goals
- Current context and resources
- Number of available hours per day (e.g., 4 hours, 5 hours)
- User's mental energy state (if provided)

## Output Format

The agent produces a structured analysis in this format:

```
## Task Analysis
{Brief assessment of the overall task landscape and key challenges}

## Task Breakdown
{Hierarchical breakdown of major tasks into subtasks with clear descriptions}

## Priority Matrix
### Urgent & Important
• {High-priority tasks that need immediate attention}

### Important, Not Urgent
• {Tasks crucial for long-term success that should be scheduled}

### Urgent, Not Important
• {Tasks that could be delegated or minimized}

### Neither Urgent Nor Important
• {Tasks that could be eliminated}

## Mental Energy Classification
• HIGH: {Tasks requiring deep focus and complex thinking}
• MEDIUM: {Tasks requiring moderate focus and engagement}
• LOW: {Tasks that can be done with minimal mental effort}

## Daily Schedule
{A suggested task schedule for the user's available hours, accounting for priority and energy levels}

## Scheduling Recommendations
• {Specific timeframes for high-priority tasks}
• {Suggested time blocks and sequencing}

## Delegation Opportunities
• {Tasks that should be handled by specialized agents with rationale}

## Progress Tracking
• {Key milestones and checkpoints}
• {Metrics for measuring progress}
```

## Time Allocation Guidelines

- Estimates realistic durations for each task (in 15-30 minute increments)
- Respects the user's available hours per day
- Schedules highest priority tasks first
- Allows buffer time between tasks (about 10-15%)
- Avoids overbooking available hours; remains realistic

## Mental Energy Classification

- **HIGH**: Complex analysis, strategic planning, learning new concepts, difficult decisions
- **MEDIUM**: Problem-solving, creative work, focused reading
- **LOW**: Routine tasks, simple organization, basic communication
- Schedules HIGH energy tasks earlier in the day when possible
- For users who report being tired, limits HIGH energy tasks

## Usage

This agent is designed to be used by the Simulation Guide Agent. It is not an entry point agent, but rather a specialist that can be invoked when task management expertise is needed.

### Example Integration

```python
from agents.task_franklin_covey import get_task_master_agent

task_master = get_task_master_agent()

# Can be added to a parent agent as a tool
parent_agent = LlmAgent(
    name="parent_agent",
    tools=[AgentTool(task_master)]
)

# Or as a sub-agent
parent_agent = LlmAgent(
    name="parent_agent",
    sub_agents=[task_master]
)
```

## Related Agents

- `simulation_guide` - Can use this agent to handle task breakdown and prioritization
- `architect_james_brown` - Designs agent architecture while this agent focuses on task management

## Constraints

This agent only provides advice and structured analysis. It does not perform actions itself, making it ideal as an advisory component in a larger agent ecosystem.
