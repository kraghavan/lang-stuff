"""
Trace Trading Team — Add LangSmith Observability to Example 05

Traces the multi-agent negotiation: which agents blocked,
what alternatives were tried, and cost per agent.

Usage:
    export LANGCHAIN_TRACING_V2=true
    python add_tracing.py                         # Default query
    python add_tracing.py "Should we buy MSFT?"   # Custom query
    python add_tracing.py --all                   # 3 scenarios

Requires:
    - LANGCHAIN_API_KEY
    - ANTHROPIC_API_KEY
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "05-trading-team"))

from main import analyze_trade


@traceable(
    name="Trading Team Analysis",
    metadata={"example": "05-trading-team", "type": "multi-agent"},
    tags=["trading", "multi-agent", "negotiation"],
)
def trade_with_tracing(query: str, cash: float = 20000):
    """Run the trading team with enhanced tracing."""
    print(f"\n  Tracing: {'✅ enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else '❌ disabled'}")
    result = analyze_trade(query, cash=cash)
    print(f"\n  📊 View trace at: https://smith.langchain.com")
    return result


def run_all_scenarios():
    """Run multiple scenarios to compare traces."""
    scenarios = [
        ("Should we buy UNH?", 20000),     # Happy path — healthcare, should approve
        ("Should we buy NVDA?", 20000),     # Block → alternative (tech overweight)
        ("Should we buy TSLA?", 20000),     # Compliance block (blackout period)
    ]

    print("═" * 55)
    print("  Trading Team — Traced Scenarios")
    print("═" * 55)

    for i, (query, cash) in enumerate(scenarios, 1):
        print(f"\n{'─' * 55}")
        print(f"  Scenario {i}/{len(scenarios)}: {query}")
        trade_with_tracing(query, cash)

    print(f"\n✅ {len(scenarios)} traces created. Compare at: https://smith.langchain.com")


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not set — traces won't be captured\n")

    if "--all" in sys.argv:
        run_all_scenarios()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        trade_with_tracing(" ".join(sys.argv[1:]))
    else:
        trade_with_tracing("Should we buy NVDA?")
