from tools.jira_tools import get_jira_issue

def ticket_agent(issue_id):
    return get_jira_issue(issue_id)
