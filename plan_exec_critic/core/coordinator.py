from agents.ticket_agent import ticket_agent
from agents.planner_agent import planner_agent
from agents.executor_agent import executor_agent
from agents.critic_agent import critic_agent


def run_pipeline(issue_id: str, max_iterations: int = 3) -> dict:
    """
    Run the planner-executor-critic loop for ticket analysis.
    
    This implements an iterative refinement process:
    1. PLANNER: Creates an execution plan based on the ticket
    2. EXECUTOR: Executes the plan steps (analyze, solve, test, report)
    3. CRITIC: Reviews output quality and decides if retry is needed
    
    Args:
        issue_id: The Jira ticket ID
        max_iterations: Maximum number of retry iterations (default: 3)
    
    Returns:
        The final report or context from the last successful iteration
    """

    try:
        print(f"🎫 Fetching ticket: {issue_id}")
        ticket_data = ticket_agent(issue_id)
        
        # Check if ticket fetch failed
        if isinstance(ticket_data, str) and ticket_data.startswith("Error"):
            print(f"❌ {ticket_data}")
            return {"error": ticket_data}
        
        if not ticket_data:
            raise ValueError("Ticket data is empty or invalid")
        
        context = None
        
        # PLANNER-EXECUTOR-CRITIC LOOP
        for iteration in range(max_iterations):
            print(f"\n{'='*60}")
            print(f"🔁 Iteration {iteration + 1}/{max_iterations}")
            print(f"{'='*60}")
            
            # PLANNER: Create execution plan
            print("\n🧠 PLANNER: Creating execution plan...")
            plan = planner_agent(issue_id, ticket_data)
            print(f"  📋 Plan: {' → '.join(plan)}")
            
            # EXECUTOR: Execute the plan
            print("\n⚙️  EXECUTOR: Running plan steps...")
            context = executor_agent(plan, issue_id, ticket_data)
            
            # CRITIC: Review the results
            print("\n🔍 CRITIC: Evaluating output quality...")
            review = critic_agent(context)
            
            print(f"  📊 Quality Score: {review['score']:.2f}/1.0")
            print(f"  💬 Feedback: {review['feedback']}")
            
            if not review.get("retry", False):
                print("\n✅ Quality approved! Pipeline complete.")
                break
            else:
                if iteration < max_iterations - 1:
                    print("\n🔄 Quality below threshold, initiating retry...")
                else:
                    print("\n⚠️  Max iterations reached, proceeding with current result")
        
        print(f"\n{'='*60}")
        print("✅ Pipeline completed successfully")
        print(f"{'='*60}\n")
        
        # Return the final report if available, otherwise the full context
        return context.get("report") if context and context.get("report") else context
        
    except Exception as error:
        print(f"\n❌ Pipeline failed for ticket {issue_id}")
        print(f"Error: {str(error)}")
        raise
    