import ollama
import os
from dotenv import load_dotenv

load_dotenv()

def test_agent(solution):
    prompt = f"""
You are a QA expert.

Based on this solution:
{solution}

Provide:
- Test scenarios
- Edge cases
- Automation ideas
"""

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
