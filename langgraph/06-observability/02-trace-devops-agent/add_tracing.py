"""
Trace DevOps Agent — Add LangSmith Observability to Example 03

LangGraph auto-traces when LANGCHAIN_TRACING_V2=true.
This script runs the DevOps Agent with tracing enabled and
shows you how to add custom metadata.

The magic: you don't need to change any code in the agent!
Just set the env var and run it. LangSmith captures everything.

For custom trace names/metadata, use the @traceable decorator.

Usage:
    export LANGCHAIN_TRACING_V2=true
    python add_tracing.py

Requires:
    - LANGCHAIN_API_KEY
    - ANTHROPIC_API_KEY
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

# Add the devops agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "03-devops-agent"))

from main import create_devops_agent


@traceable(
    name="DevOps Investigation",
    metadata={"example": "03-devops-agent", "type": "tool-calling"},
    tags=["devops", "react", "tool-calling"],
)
def investigate_with_tracing(issue: str):
    """
    Run the DevOps agent with enhanced LangSmith tracing.

    The @traceable decorator adds:
    - Custom trace name (shows in LangSmith UI)
    - Metadata (filterable in LangSmith)
    - Tags (searchable in LangSmith)
    """
    print(f"\n🔍 Investigating: {issue}")
    print(f"   Tracing: {'✅ enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else '❌ disabled'}")
    print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'default')}\n")

    agent = create_devops_agent()

    result = agent.invoke({
        "messages": [("human", issue)]
    })

    # Summary
    messages = result["messages"]
    tool_results = [m for m in messages if m.type == "tool"]

    print(f"\n{'═' * 55}")
    print(f"  Investigation Complete")
    print(f"  Tools used: {len(tool_results)}")
    for msg in tool_results:
        print(f"    → {msg.name}")

    final = messages[-1]
    if hasattr(final, "content") and final.content:
        content = final.content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    print(f"\n  Conclusion: {block['text'][:200]}...")
                    break
        else:
            print(f"\n  Conclusion: {str(content)[:200]}...")

    print(f"\n  📊 View trace at: https://smith.langchain.com")
    print(f"{'═' * 55}")

    return result


def run_debug_scenarios():
    """Run multiple scenarios to generate interesting traces."""
    scenarios = [
        "The /api/v2/users endpoint is timing out. Users report the app is slow.",
        "Memory usage on the database server is at 92%. Should we be worried?",
        "The payment service health check is failing intermittently.",
    ]

    print("═" * 55)
    print("  DevOps Agent — Traced Scenarios")
    print("═" * 55)

    for i, issue in enumerate(scenarios, 1):
        print(f"\n{'─' * 55}")
        print(f"  Scenario {i}/{len(scenarios)}")
        investigate_with_tracing(issue)

    print(f"\n✅ {len(scenarios)} traces created. View at: https://smith.langchain.com")


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not set — traces won't be captured")
        print("   Run 01-setup/test_connection.py first\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_debug_scenarios()
    else:
        investigate_with_tracing(
            "The /api/v2/users endpoint is timing out. Users report the app is very slow."
        )
