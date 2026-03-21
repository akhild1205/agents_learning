from core.coordinator import run_pipeline
from utils.extractor import extract_issue_id

if __name__ == "__main__":
    while True:
        user_input = input("\n🔗 Enter Jira URL or ID (or 'exit'): ")

        if user_input.lower() == "exit":
            break

        issue_id = extract_issue_id(user_input)

        if not issue_id:
            print("❌ Invalid issue ID")
            continue

        result = run_pipeline(issue_id)

        print("\n✅ FINAL OUTPUT:\n")
        print(result)
