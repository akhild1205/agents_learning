import ollama
import json
import os
from dotenv import load_dotenv

load_dotenv()

def critic_agent(context):
    """
    Reviews the execution results and determines if they meet quality standards.
    Returns a dictionary with score, feedback, and retry decision.
    """
    
    # Extract and truncate previews before f-string to avoid slice notation issues
    analysis_preview = str(context.get('analysis'))[:300] + "..." if context.get('analysis') else ''
    solution_preview = str(context.get('solution'))[:300] + "..." if context.get('solution') else ''
    tests_preview = str(context.get('tests'))[:300] + "..." if context.get('tests') else ''
    
    # Build a summary of what was produced
    summary = f"""
Ticket: {context.get('issue_id')}
Ticket Summary: {context.get('ticket', {}).get('summary', 'N/A')}

Analysis Present: {'Yes' if context.get('analysis') else 'No'}
{analysis_preview}

Solution Present: {'Yes' if context.get('solution') else 'No'}
{solution_preview}

Tests Present: {'Yes' if context.get('tests') else 'No'}
{tests_preview}

Report Present: {'Yes' if context.get('report') else 'No'}
"""

    prompt = f"""
You are a quality critic agent reviewing the output of a Jira ticket analysis pipeline.

Review this execution result:
{summary}

Evaluate the quality and completeness:
1. Is the analysis comprehensive and actionable?
2. Does the solution provide clear implementation steps?
3. Are test scenarios well-defined?
4. Is all required information present?

Quality Criteria:
- Score 0.0-0.4: Poor quality, definitely retry
- Score 0.5-0.6: Below average, consider retry
- Score 0.7-0.8: Good quality, acceptable
- Score 0.9-1.0: Excellent quality

Return ONLY a JSON object:
{{
  "score": 0.8,
  "feedback": "Brief feedback about what's good or needs improvement",
  "retry": false
}}

Set "retry" to true ONLY if critical information is missing or quality is very poor (score < 0.6).
"""

    try:
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response["message"]["content"])
        
        # Validate the result structure
        if "score" not in result or "retry" not in result:
            raise ValueError("Invalid critic response structure")
            
        return {
            "score": float(result.get("score", 0.7)),
            "feedback": result.get("feedback", "No feedback provided"),
            "retry": bool(result.get("retry", False))
        }
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"    ⚠️  Critic parsing error: {e}, assuming acceptable quality")
        # Default to accepting the result if we can't parse the critic's response
        return {
            "score": 0.7,
            "feedback": "Unable to parse critic response, accepting result",
            "retry": False
        }
