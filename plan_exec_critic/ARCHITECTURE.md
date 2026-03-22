# Planner-Executor-Critic Loop Architecture

## Overview

This system implements a **Planner-Executor-Critic (PEC) loop** pattern for intelligent Jira ticket analysis. The loop provides iterative refinement and quality control, ensuring high-quality outputs through automated feedback and retry mechanisms.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JIRA TICKET INPUT                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  TICKET AGENT  │  ← Fetch ticket data from Jira
         └────────┬───────┘
                  │
    ┌─────────────▼─────────────────────────────────┐
    │         ITERATION LOOP (max 3 times)          │
    │                                                │
    │  ┌──────────────────────────────────────┐    │
    │  │   1️⃣  PLANNER AGENT                  │    │
    │  │   Creates execution plan              │    │
    │  │   - analyze_ticket                    │    │
    │  │   - generate_solution                 │    │
    │  │   - generate_tests                    │    │
    │  │   - generate_report                   │    │
    │  └──────────┬───────────────────────────┘    │
    │             │                                  │
    │             ▼                                  │
    │  ┌──────────────────────────────────────┐    │
    │  │   2️⃣  EXECUTOR AGENT                 │    │
    │  │   Runs each plan step:                │    │
    │  │   ┌─────────────────────────────┐    │    │
    │  │   │ Analysis Agent              │    │    │
    │  │   │ Solution Agent              │    │    │
    │  │   │ Test Agent                  │    │    │
    │  │   │ Report Agent                │    │    │
    │  │   └─────────────────────────────┘    │    │
    │  └──────────┬───────────────────────────┘    │
    │             │                                  │
    │             ▼                                  │
    │  ┌──────────────────────────────────────┐    │
    │  │   3️⃣  CRITIC AGENT                   │    │
    │  │   Evaluates quality:                  │    │
    │  │   - Score (0.0 - 1.0)                │    │
    │  │   - Feedback                          │    │
    │  │   - Retry decision                    │    │
    │  └──────────┬───────────────────────────┘    │
    │             │                                  │
    │             ├─── Score < 0.6? ──┐            │
    │             │                    │            │
    │             NO                  YES           │
    │             │                    │            │
    │             ▼                    └─── RETRY   │
    └─────────────┼──────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  FINAL REPORT  │
         └────────────────┘
```

## Components

### 1. **Ticket Agent** (`agents/ticket_agent.py`)
- Fetches ticket data from Jira API
- Extracts essential fields (summary, description, status, etc.)
- Error handling for API failures

### 2. **Planner Agent** (`agents/planner_agent.py`)
- **Purpose**: Creates a strategic execution plan
- **Input**: Ticket ID and basic ticket data
- **Output**: List of action steps
- **Actions**:
  - `analyze_ticket` - Analyze requirements and impact
  - `generate_solution` - Create technical solution
  - `generate_tests` - Generate test strategy
  - `generate_report` - Compile final report

### 3. **Executor Agent** (`agents/executor_agent.py`)
- **Purpose**: Executes the planned steps sequentially
- **Input**: Plan (list of actions), ticket ID, ticket data
- **Output**: Context object with all results
- **Process**:
  1. Iterates through each step in the plan
  2. Calls appropriate specialized agent
  3. Builds up context with cumulative results
  4. Handles dependencies (e.g., solution needs analysis)

### 4. **Critic Agent** (`agents/critic_agent.py`)
- **Purpose**: Quality control and retry decisions
- **Input**: Execution context with all results
- **Output**: Review object with:
  - `score` (0.0-1.0) - Quality rating
  - `feedback` - Specific comments
  - `retry` (boolean) - Whether to retry
- **Evaluation Criteria**:
  - Completeness of analysis
  - Clarity of solution steps
  - Test coverage adequacy
  - Overall coherence

### 5. **Specialized Agents**
- **Analysis Agent**: Analyzes ticket requirements and impact
- **Solution Agent**: Generates technical approach and implementation steps
- **Test Agent**: Creates test scenarios and edge cases
- **Report Agent**: Compiles final formatted report

## The Loop Flow

### Iteration Process

```python
for iteration in range(max_iterations):
    # 1. PLAN
    plan = planner_agent(issue_id, ticket)
    
    # 2. EXECUTE
    context = executor_agent(plan, issue_id, ticket)
    
    # 3. CRITIQUE
    review = critic_agent(context)
    
    # 4. DECIDE
    if review['score'] >= 0.6 and not review['retry']:
        break  # Quality approved
    else:
        continue  # Retry with improvements
```

### Quality Thresholds

| Score Range | Quality Level | Action |
|-------------|--------------|---------|
| 0.0 - 0.4   | Poor         | Retry   |
| 0.5 - 0.6   | Below Avg    | Retry   |
| 0.7 - 0.8   | Good         | Accept  |
| 0.9 - 1.0   | Excellent    | Accept  |

## Benefits of PEC Loop

### 1. **Self-Correction**
- Automatically retries on low-quality outputs
- No manual intervention needed
- Learns from previous iteration failures

### 2. **Quality Assurance**
- Every output is reviewed by critic agent
- Ensures minimum quality standards
- Provides feedback for improvement

### 3. **Adaptability**
- Planner can adjust strategy based on ticket complexity
- Executor handles dependencies dynamically
- Critic provides specific improvement guidance

### 4. **Transparency**
- Clear step-by-step progress tracking
- Quality scores and feedback visible
- Iteration count shows refinement process

## Configuration

### Environment Variables

```bash
# Jira Configuration
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@example.com
JIRA_API_TOKEN=your_api_token_here

# Ollama Configuration
OLLAMA_MODEL=llama3.2
```

### Tuning Parameters

In `core/coordinator.py`:

```python
run_pipeline(issue_id, max_iterations=3)
```

- **max_iterations**: Maximum retry attempts (default: 3)
- Higher values = more refinement, longer execution time
- Lower values = faster execution, potential quality trade-off

## Usage Example

```bash
python main.py
```

```
🔗 Enter Jira URL or ID (or 'exit'): ENG-12345

🎫 Fetching ticket: ENG-12345

============================================================
🔁 Iteration 1/3
============================================================

🧠 PLANNER: Creating execution plan...
  📋 Plan: analyze_ticket → generate_solution → generate_tests → generate_report

⚙️  EXECUTOR: Running plan steps...
  ⚙️  Executing: analyze_ticket
  ⚙️  Executing: generate_solution
  ⚙️  Executing: generate_tests
  ⚙️  Executing: generate_report

🔍 CRITIC: Evaluating output quality...
  📊 Quality Score: 0.85/1.0
  💬 Feedback: Comprehensive analysis with clear implementation steps

✅ Quality approved! Pipeline complete.

============================================================
✅ Pipeline completed successfully
============================================================
```

## Advanced Features

### Graceful Fallbacks
- JSON parsing errors → default plan
- Missing dependencies → skip with warning
- Critic parsing errors → accept result

### Error Handling
- Jira API failures caught and reported
- Invalid ticket data validation
- Exception handling with clear error messages

### Optimization
- Minimal ticket data extraction (no bloat)
- Configurable LLM model via environment
- Fast iteration with streaming output

## Comparison: Before vs After

| Aspect | Original Pipeline | PEC Loop Pipeline |
|--------|------------------|-------------------|
| Quality Control | None | Automated critic review |
| Adaptability | Fixed sequence | Dynamic planning |
| Error Recovery | Manual | Automatic retry |
| Transparency | Basic logging | Detailed iteration tracking |
| Execution | One-shot | Iterative refinement |
| Feedback | None | Specific improvement guidance |

## Future Enhancements

- [ ] Persistent memory of critic feedback across tickets
- [ ] Learning from successful vs failed iterations
- [ ] Adaptive max_iterations based on ticket complexity
- [ ] Multi-model ensemble for critic evaluation
- [ ] Parallel execution of independent plan steps
- [ ] Human-in-the-loop override for critic decisions
