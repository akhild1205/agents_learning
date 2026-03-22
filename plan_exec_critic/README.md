# Jira Ticket Analysis with Planner-Executor-Critic Loop

An AI-powered multi-agent system that uses a **Planner-Executor-Critic (PEC) loop** pattern with local Ollama LLM to intelligently fetch, analyze, and generate solutions for Jira tickets.

## 🎯 Architecture

This system implements an iterative refinement process:

1. **Planner Agent** - Creates an execution plan based on ticket analysis
2. **Executor Agent** - Runs specialized agents (Analysis, Solution, Test, Report)  
3. **Critic Agent** - Reviews output quality and decides if retry is needed

The loop runs up to 3 iterations, automatically improving output quality until it meets acceptance criteria.

📘 **[Read Full Architecture Documentation](ARCHITECTURE.md)**

## Features

- ✅ **Planner-Executor-Critic Loop**: Iterative refinement with quality control
- ✅ **LLM-Powered Analysis**: Uses Ollama for intelligent ticket analysis
- ✅ **Dynamic Planning**: Adapts execution plan to ticket complexity
- ✅ **Automatic Quality Control**: Critic agent validates outputs
- ✅ **Self-Correction**: Automatically retries on low-quality results

## Setup

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create .env File

Copy the example file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Jira detail
```

Start Ollama and pull a model:

```bash
ollama serve  # Start Ollama server
ollama pull llama3.2  # Pull the default model
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

You need to configure three environment variables:

```bash
export JIRA_URL='https://yourcompany.atlassian.net'
export JIRA_EMAIL='your.email@example.com'
export JIRA_API_TOKEN='your_api_token_here'
```

###Paste it into your `.env` file

## Usage

### Interactive Mode (Recommended)

The agent runs in an interactive chat mode where you can:
- Analyze tickets by entering their key (e.g., `PROJ-123`)
- Search tickets with JQL (e.g., `search: status = "In Progress"`)
- Ask natural language questions

```bash
python main.py
```

**Example interaction:**
Programmatic Usage

```python
from main import JiraAgent
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the agent
agent = JiraAgent(
    jira_url=os.getenv('JIRA_URL'),
    email=os.getenv('JIRA_EMAIL'),
    api_token=os.getenv('JIRA_API_TOKEN'),
    ollama_model='llama3.2'
)

# Analyze a specific ticket with LLM
analysis = agent.analyze_ticket_with_llm('PROJ-123')
print(analysis)

# Ask a specific question about a ticket
analysis = agent.analyze_ticket_with_llm('PROJ-123', "What are the risks?")
print(analysis)

# Search and analyze multiple tickets
summary = agent.search_and_analyze(
    'project = PROJ AND status = "In Progress"',
    analysis_query="Which ticket should I prioritize?"
)
print(summary)

# Chat with the agent
response = agent.chat("Show me all critical bugs")
print(response)
, ollama_model='llama3.2')`
Initialize the Jira agent with authentication credentials and Ollama model.

### LLM-Powered Methods

#### `analyze_ticket_with_llm(ticket_key, question=None)`
Fetch a ticket and analyze it using the LLM. Optionally ask a specific question.

#### `search_and_analyze(jql, analysis_query=None, max_results=10)`
Search for tickets using JQL and get an LLM-powered analysis summary.

#### `chat(user_input)`
Interactive chat interface - interprets natural language queries.

#### `ask_llm(prompt, context="")`
Direct access to the LLM with optional context.

### Ollama Connection Error
- Make sure Ollama is running: `ollama serve`
- Check if the model is pulled: `ollama list`
- Pull the model if needed: `ollama pull llama3.2`

### Traditional Methods

#### `fetch_ticket(ticket_key)`
Fetch complete details of a specific ticket. Returns raw JSON response.

#### `get_ticket_summary(ticket_key)`
Get a formatted summary with key fields extracted. Returns a dictionary.

### Slow LLM Responses
- Try a smaller/faster model: `OLLAMA_MODEL=llama3.2:1b`
- Available models: run `ollama list` to see options
- Pull faster models: `ollama pull phi` or `ollama pull mistral`

## Advanced Usage

### Using Different Ollama Models

```bash
# In your .env file
OLLAMA_MODEL=mistral      # Faster, good for quick analysis
OLLAMA_MODEL=llama3.2     # Balanced (default)
OLLAMA_MODEL=llama3.1:70b  # Most capable, slower
```

### Custom Analysis Queries

```python
# Analyze technical risks
agent.analyze_ticket_with_llm('PROJ-123', 'What are the technical risks and dependencies?')

# Get time estimates
agent.search_and_analyze(
    'sprint = "Sprint 23"',
    'Estimate total hours needed and identify blockers'
)

# Priority recommendations
agent.search_and_analyze(
    'assignee = currentUser()',
    'Which tickets should I work on first and why?'
)
```

#### `display_ticket_details(ticket_key)`
Fetch and display ticket details in a readable format.

#
```bash
python main.py
```

### Use Programmatically

```python
from main import JiraAgent

# Initialize the agent
agent = JiraAgent(
    jira_url='https://yourcompany.atlassian.net',
    email='your.email@example.com',
    api_token='your_api_token'
)

# Fetch a specific ticket
ticket = agent.fetch_ticket('PROJ-123')
print(ticket)

# Display formatted ticket details
agent.display_ticket_details('PROJ-123')

# Search tickets using JQL
tickets = agent.search_tickets('project = PROJ AND status = "In Progress"')
for ticket in tickets:
    print(ticket['key'], ticket['fields']['summary'])
```

## JQL Query Examples

- Find all open tickets: `status = Open`
- Find tickets assigned to you: `assignee = currentUser()`
- Find high priority bugs: `type = Bug AND priority = High`
- Find tickets in a project: `project = MYPROJECT`
- Complex query: `project = PROJ AND status IN ("In Progress", "To Do") AND assignee = currentUser()`

## API Methods

### `JiraAgent(jira_url, email, api_token)`
Initialize the Jira agent with authentication credentials.

### `fetch_ticket(ticket_key)`
Fetch complete details of a specific ticket. Returns raw JSON response.

### `get_ticket_summary(ticket_key)`
Get a formatted summary with key fields extracted. Returns a dictionary.

### `display_ticket_details(ticket_key)`
Fetch and display ticket details in a readable format.

### `search_tickets(jql, max_results=50)`
Search for tickets using JQL. Returns a list of ticket objects.

## Troubleshooting

### Authentication Error
- Verify your API token is correct
- Ensure your email matches your Jira account
- Check that the Jira URL is correct (including https://)

### 404 Not Found
- Verify the ticket key exists
- Check you have permission to view the ticket
- Ensure the project key is correct

### Rate Limiting
Jira API has rate limits. If you're making many requests, consider adding delays between calls.

## Security Notes

- Never commit your API token to version control
- Use environment variables or a secure secrets manager
- Rotate your API tokens regularly
- Limit token permissions to only what's needed
