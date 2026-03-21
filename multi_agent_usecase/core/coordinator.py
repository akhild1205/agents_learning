from agents.ticket_agent import ticket_agent
from agents.analysis_agent import analysis_agent
from agents.solution_agent import solution_agent
from agents.test_agent import test_agent
from agents.report_agent import report_agent


def run_pipeline(issue_id: str) -> dict:
    """
    End-to-end pipeline to process a ticket and generate a report.

    Steps:
    1. Fetch ticket details
    2. Analyze the issue
    3. Generate solution
    4. Create test strategy
    5. Build final report
    """

    try:
        print(f"Starting pipeline for ticket: {issue_id}")

        # Step 1: Fetch Ticket
        print("Fetching ticket details...")
        ticket_data = ticket_agent(issue_id)
        if not ticket_data:
            raise ValueError("Ticket data is empty or invalid")

        # Step 2: Analysis
        print("Running analysis...")
        analysis_result = analysis_agent(ticket_data)

        # Step 3: Solution Generation
        print("Generating solution...")
        solution_result = solution_agent(analysis_result)

        # Step 4: Test Strategy
        print("Creating test strategy...")
        test_plan = test_agent(solution_result)

        # Step 5: Final Report
        print("Compiling report...")
        final_report = report_agent(
            issue_id=issue_id,
            ticket=ticket_data,
            analysis=analysis_result,
            solution=solution_result,
            tests=test_plan
        )

        print("Pipeline completed successfully")
        return final_report

    except Exception as error:
        print(f"Pipeline failed for ticket {issue_id}")
        print(f"Error: {str(error)}")
        raise
    