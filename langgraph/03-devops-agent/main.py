"""
DevOps Troubleshooting Agent — ReAct Pattern with Tool Calling

A "deep agent" that autonomously investigates infrastructure issues by
choosing which tools to use, observing results, and deciding next steps.

This is the ReAct (Reason + Act) pattern:
    Think → Choose tool → Execute → Observe → Think → ... → Done

Key Concepts:
    - Tool calling: Agent has 5 tools and decides which to use
    - ReAct loop: Iterative reason → act → observe cycle
    - Agentic behavior: Agent picks its own path (not hardcoded)
    - create_react_agent: LangGraph's built-in ReAct implementation

Usage:
    python main.py
    python main.py "The payments endpoint is returning errors"

Requires:
    - ANTHROPIC_API_KEY environment variable
"""

import os
import sys
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from tools import devops_tools

load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

SYSTEM_PROMPT = """You are a senior DevOps engineer troubleshooting a production issue.

You have access to these tools:
- check_logs: View recent logs for any service
- check_metrics: Check CPU, memory, disk, and connection metrics
- query_database: Investigate database performance (slow queries, missing indexes, table stats)
- test_endpoint: Test API endpoints for availability and response time
- run_remediation: Execute fixes (create indexes, vacuum tables, restart/scale services)

INVESTIGATION APPROACH:
1. Start by checking logs for the most likely affected service
2. Check metrics if logs suggest resource issues
3. Query the database if logs show slow queries
4. Test endpoints to confirm the issue
5. Run remediation ONLY after identifying root cause

Be systematic. Check one thing at a time. State your reasoning before each tool call.
After finding the root cause, suggest a fix and optionally run remediation.

Available services: api-gateway, user-service, payment-service, auth-service
Available endpoints: https://api.example.com/health, /api/v2/users, /api/v2/users/123, /api/v2/payments
"""


# ═══════════════════════════════════════════════
# Build the Agent
#
# create_react_agent is LangGraph's built-in ReAct implementation.
# It creates a graph with:
#   - An "agent" node (LLM decides what to do)
#   - A "tools" node (executes the chosen tool)
#   - A conditional edge (loop back or finish)
#
# The graph looks like:
#   START → agent → [should_continue?]
#                       ├─ tool_call → tools → agent (LOOP)
#                       └─ no_tool_call → END
# ═══════════════════════════════════════════════

def create_devops_agent():
    """Create the DevOps troubleshooting agent."""
    llm = ChatAnthropic(model=MODEL, temperature=0, max_tokens=1024)

    # create_react_agent builds the full ReAct graph:
    # - Binds tools to the LLM
    # - Creates the agent node (LLM reasoning)
    # - Creates the tools node (tool execution)
    # - Adds the loop (agent → tools → agent → ... → END)
    agent = create_react_agent(
        model=llm,
        tools=devops_tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent


# ═══════════════════════════════════════════════
# Run Investigation
# ═══════════════════════════════════════════════

def investigate(issue: str):
    """
    Run the DevOps agent to investigate an issue.

    Args:
        issue: Description of the problem (e.g., "The API is slow")
    """
    print("═" * 55)
    print("  DEVOPS TROUBLESHOOTING AGENT")
    print("═" * 55)
    print(f"\n  Issue: {issue}\n")
    print("─" * 55)

    agent = create_devops_agent()

    # The agent takes a messages list as input
    result = agent.invoke({
        "messages": [("human", issue)]
    })

    # Print the agent's investigation trail
    print("\n" + "═" * 55)
    print("  INVESTIGATION COMPLETE")
    print("═" * 55)

    # Extract the final message (agent's conclusion)
    messages = result["messages"]

    # Count tool calls made
    tool_calls = [m for m in messages if hasattr(m, "tool_calls") and m.tool_calls]
    tool_results = [m for m in messages if m.type == "tool"]

    print(f"\n  Tools used: {len(tool_results)}")
    for msg in tool_results:
        print(f"    → {msg.name}")

    # Print the final response
    final_msg = messages[-1]
    if hasattr(final_msg, "content") and final_msg.content:
        print(f"\n  Conclusion:\n")
        # Handle content that might be a list of blocks
        content = final_msg.content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    print(f"  {block['text']}")
                elif isinstance(block, str):
                    print(f"  {block}")
        else:
            for line in str(content).split("\n"):
                print(f"  {line}")

    print("\n" + "═" * 55)

    return result


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Get issue from command line or use default
    if len(sys.argv) > 1:
        issue = " ".join(sys.argv[1:])
    else:
        issue = "The /api/v2/users endpoint is timing out. Users are reporting that the app is very slow. Please investigate and fix the issue."

    investigate(issue)
