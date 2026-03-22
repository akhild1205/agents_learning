import re

def extract_issue_id(text):
    match = re.search(r"[A-Z]+-\d+", text)
    return match.group(0) if match else None
