import ollama
import os
from dotenv import load_dotenv

load_dotenv()

def solution_agent(analysis):
    prompt = f"""
You are a senior engineer.

Based on this analysis:
{analysis}

Provide:
- Technical approach
- Implementation steps
- Risks
"""

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]