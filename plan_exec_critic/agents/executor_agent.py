from agents.analysis_agent import analysis_agent
from agents.solution_agent import solution_agent
from agents.test_agent import test_agent
from agents.report_agent import report_agent

def executor_agent(plan, issue_id, ticket_data):
    """
    Executes the plan steps and builds up context.
    Returns a dictionary with all execution results.
    """
    context = {
        "issue_id": issue_id,
        "ticket": ticket_data,
        "analysis": None,
        "solution": None,
        "tests": None,
        "report": None
    }

    for step in plan:
        print(f"  ⚙️  Executing: {step}")
        
        if step == "analyze_ticket":
            context["analysis"] = analysis_agent(ticket_data)
            
        elif step == "generate_solution":
            if context["analysis"]:
                context["solution"] = solution_agent(context["analysis"])
            else:
                print("    ⚠️  Skipping solution generation - no analysis available")
                
        elif step == "generate_tests":
            if context["solution"]:
                context["tests"] = test_agent(context["solution"])
            else:
                print("    ⚠️  Skipping test generation - no solution available")
                
        elif step == "generate_report":
            context["report"] = report_agent(
                issue_id,
                ticket_data,
                context["analysis"],
                context["solution"],
                context["tests"]
            )
        else:
            print(f"    ⚠️  Unknown step: {step}")

    return context
