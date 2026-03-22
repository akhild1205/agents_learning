import ollama
import json
import os
from dotenv import load_dotenv

load_dotenv()

def planner_agent(issue_id, ticket_data):
    """
    Creates an execution plan based on the ticket data.
    Returns a list of steps to be executed.
    """
    # Extract and truncate description before f-string to avoid slice notation issues
    description = ticket_data.get('description', 'N/A')
    truncated_desc = description[:500] if description else 'N/A'
    
    prompt = f"""
You are a planning agent for a Jira ticket analysis system.

Ticket ID: {issue_id}
Ticket Summary: {ticket_data.get('summary', 'N/A')}
Ticket Description: {truncated_desc}...

Create a step-by-step plan to analyze and provide solutions for this ticket.
Available actions:
- analyze_ticket: Analyze the ticket requirements and impact
- generate_solution: Create technical solution and implementation steps
- generate_tests: Create test strategy and scenarios
- generate_report: Compile final report

Return ONLY a JSON object with this structure:
{{"plan": ["action1", "action2", "action3", "action4"]}}

Example:
{{"plan": ["analyze_ticket", "generate_solution", "generate_tests", "generate_report"]}}
"""

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response["message"]["content"])
        return result.get("plan", ["analyze_ticket", "generate_solution", "generate_tests", "generate_report"])
    except json.JSONDecodeError:
        # Fallback to default plan if JSON parsing fails
        print("⚠️  Failed to parse plan, using default")
        return ["analyze_ticket", "generate_solution", "generate_tests", "generate_report"]
