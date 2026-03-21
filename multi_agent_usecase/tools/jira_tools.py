import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_URL")  # Note: variable is JIRA_URL in .env file

def get_jira_issue(issue_id):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_id}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"}
    )
    
    if response.status_code != 200:
        return f"Error fetching ticket: {response.status_code} - {response.text}"
    
    data = response.json()
    fields = data.get("fields", {})
    
    # Extract only relevant fields for analysis
    return {
        "key": data.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
        "reporter": fields.get("reporter", {}).get("displayName"),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "labels": fields.get("labels", []),
        "components": [c.get("name") for c in fields.get("components", [])]
    }
