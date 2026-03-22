def report_agent(issue_id, ticket, analysis, solution, tests):
    return f"""
🎫 Ticket: {issue_id}

📄 Raw Ticket:
{ticket}

🧠 Analysis:
{analysis}

🛠️ Solution:
{solution}

🧪 Test Strategy:
{tests}
"""
