import ollama
import os
from dotenv import load_dotenv

load_dotenv()

def analysis_agent(ticket_data):
    prompt = f"Analyze this Jira ticket:\n{ticket_data}"

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
