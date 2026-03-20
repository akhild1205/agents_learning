"""
Jira Ticket Fetcher Agent with Ollama Integration
Fetches and displays Jira ticket details using the Jira REST API
Uses local Ollama LLM for intelligent query processing
"""

import os
import re
import logging
import textwrap
import requests
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv
import ollama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class JiraAgent:
    """LLM-powered agent to fetch and process Jira ticket details"""
    
    def __init__(self, jira_url: str, email: str, api_token: str, ollama_model: str = "llama3.2", timeout: int = 15):
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.ollama_model = ollama_model
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self) -> bool:
        """Test the Jira connection and authentication"""
        try:
            url = f"{self.jira_url}/rest/api/3/myself"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info(f"Connected to Jira as: {user_data.get('displayName')} ({user_data.get('emailAddress')})")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error during connection test: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection failed: {str(e)}")
        return False
    
    def fetch_ticket(self, ticket_key: str) -> Optional[Dict[str, Any]]:
        """Fetch details of a specific Jira ticket"""
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{ticket_key.upper()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Ticket {ticket_key} not found.")
            elif response.status_code == 401:
                logger.error("Authentication error - check your API token.")
            elif response.status_code == 403:
                logger.error(f"Permission denied for ticket {ticket_key}.")
            else:
                logger.error(f"Unexpected error fetching ticket: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching ticket: {str(e)}")
        
        return None
    
    def get_ticket_summary(self, ticket_key: str) -> Optional[Dict[str, Any]]:
        """Get a formatted summary of a Jira ticket"""
        ticket = self.fetch_ticket(ticket_key)
        if not ticket:
            return None
        
        fields = ticket.get('fields', {})
        
        return {
            'key': ticket.get('key'),
            'summary': fields.get('summary', 'No summary provided'),
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'None'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'reporter': fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown',
            'created': fields.get('created'),
            'updated': fields.get('updated'),
            'description': fields.get('description', 'No description provided'),
            'project': fields.get('project', {}).get('name', 'Unknown'),
        }
    
    def search_tickets(self, jql: str, max_results: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Search for tickets using JQL (Jira Query Language)"""
        try:
            url = f"{self.jira_url}/rest/api/3/search"
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': 'summary,status,priority,assignee'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json().get('issues', [])
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching tickets via JQL: {str(e)}")
            return None
    
    def ask_llm(self, prompt: str, context: str = "") -> str:
        """Query Ollama LLM with a prompt and optional context"""
        full_prompt = f"{context}\n\nUser query: {prompt}" if context else prompt
        
        try:
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful Jira assistant. Analyze ticket data and provide clear, concise answers.'
                    },
                    {
                        'role': 'user',
                        'content': full_prompt
                    }
                ]
            )
            return response.get('message', {}).get('content', "Error: No content returned from LLM.")
            
        except Exception as e:
            logger.error(f"Failed to communicate with Ollama: {str(e)}")
            return "Error querying LLM. Please ensure the Ollama service is running locally and the model is pulled."
    
    def analyze_ticket_with_llm(self, ticket_key: str, question: Optional[str] = None) -> str:
        """Fetch a ticket and analyze it using the LLM"""
        summary = self.get_ticket_summary(ticket_key)
        
        if not summary:
            return f"Could not retrieve ticket {ticket_key}."
        
        context = textwrap.dedent(f"""
            Ticket: {summary['key']}
            Summary: {summary['summary']}
            Status: {summary['status']}
            Type: {summary['issue_type']}
            Priority: {summary['priority']}
            Project: {summary['project']}
            Assignee: {summary['assignee']}
            Reporter: {summary['reporter']}
        """).strip()
        
        prompt = f"Based on this Jira ticket, {question}" if question else "Provide a brief analysis of this ticket, highlighting key points and potential concerns."
        return self.ask_llm(prompt, context)
    
    def search_and_analyze(self, jql: str, analysis_query: Optional[str] = None, max_results: int = 10) -> str:
        """Search for tickets and analyze them using the LLM"""
        tickets = self.search_tickets(jql, max_results)
        
        if not tickets:
            return "No tickets found matching that query or an error occurred."
        
        context_lines = [f"Found {len(tickets)} tickets:"]
        for i, ticket in enumerate(tickets, 1):
            fields = ticket.get('fields', {})
            context_lines.append(
                f"{i}. [{ticket.get('key')}] {fields.get('summary', 'No summary')}\n"
                f"   Status: {fields.get('status', {}).get('name', 'Unknown')} | "
                f"Priority: {fields.get('priority', {}).get('name', 'Unknown')} | "
                f"Assignee: {fields.get('assignee', {}).get('displayName', 'Unassigned')}"
            )
        
        context = "\n".join(context_lines)
        prompt = analysis_query or "Summarize these tickets, identify patterns, and suggest priorities."
        return self.ask_llm(prompt, context)
    
    @staticmethod
    def extract_ticket_key(text: str) -> Optional[str]:
        """Extract Jira ticket key from text (handles URLs and plain keys)"""
        pattern = r'\b([A-Z][A-Z0-9]+-\d+)\b'
        match = re.search(pattern, text.upper())
        return match.group(1) if match else None

def main():
    load_dotenv()
    
    JIRA_URL = os.environ.get('JIRA_URL')
    JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')
    
    if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
        print(textwrap.dedent("""
            --- SETUP REQUIRED ---
            Please create a .env file with the following variables:
            
            JIRA_URL=https://yourcompany.atlassian.net
            JIRA_EMAIL=your.email@example.com
            JIRA_API_TOKEN=your_api_token
            OLLAMA_MODEL=llama3.2  # optional
            
            To generate an API token:
            1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
            2. Click 'Create API token'
            ----------------------
        """))
        return
    
    print(f"\nInitializing Jira Agent with Ollama ({OLLAMA_MODEL})...")
    agent = JiraAgent(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OLLAMA_MODEL)
    
    print("Testing Jira connection...")
    if not agent.test_connection():
        print("Connection test failed. Check your credentials in .env and your network connection.")
        return
    
    print(textwrap.dedent("""
        --- JIRA AGENT WITH OLLAMA - INTERACTIVE MODE ---
        Commands:
          - Type a ticket key (e.g., PROJ-123) to analyze it.
          - Type 'search: <JQL>' to search and summarize tickets.
          - Ask general questions.
          - Type 'quit' to exit.
        -------------------------------------------------
    """))
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye!")
                break
            
            if user_input.lower().startswith('search:'):
                jql = user_input[7:].strip()
                print("\nSearching and analyzing tickets...\n")
                response = agent.search_and_analyze(jql)
                print(f"Agent:\n{response}\n")
                
            else:
                ticket_key = agent.extract_ticket_key(user_input)
                if ticket_key:
                    print(f"\nAnalyzing ticket {ticket_key}...\n")
                    response = agent.analyze_ticket_with_llm(ticket_key)
                    print(f"Agent:\n{response}\n")
                else:
                    print("\nAgent: ", end="")
                    system_prompt = "You are a Jira assistant. Guide the user to provide a ticket ID (like PROJ-123) or a JQL query starting with 'search: '."
                    print(agent.ask_llm(user_input, system_prompt) + "\n")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in chat loop: {str(e)}")

if __name__ == "__main__":
    main()
