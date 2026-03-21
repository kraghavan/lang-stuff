"""
Algorithmic Trading Team — Multi-Agent System with Conflict Resolution

A multi-agent system where specialist agents (Market, Risk, Compliance)
can DISAGREE, VETO, and NEGOTIATE to reach consensus on trades.

Architecture:
    Portfolio Manager (supervisor) coordinates:
    → Market Agent (proposes trades / alternatives)
    → Risk Agent (approves/blocks based on portfolio risk)
    → Compliance Agent (approves/blocks based on regulations)

    If blocked → Market Agent proposes alternative → re-check
    Max 3 negotiation rounds before giving up.

Usage:
    python main.py                          # Default: "Should we buy NVDA?"
    python main.py "Should we buy MSFT?"    # Custom query
    python main.py "Find me a good trade"   # Agent finds best opportunity

Requires:
    - ANTHROPIC_API_KEY environment variable (for Market Agent rationale)
    - Works without API key too (uses rule-based rationale)
"""

import os
import sys
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from agents import market_analysis_agent, risk_management_agent, compliance_agent
from portfolio_data import (
    load_portfolio, format_portfolio_summary,
    calculate_portfolio_value, calculate_sector_breakdown,
    estimate_portfolio_volatility,
)
from market_data import get_price, get_sector

load_dotenv()


# ═══════════════════════════════════════════════
# Step 1: Define State
# ═══════════════════════════════════════════════

class TradingState(TypedDict):
    """Shared state across all agents."""
    # Input
    user_query: str
    portfolio: Dict[str, Dict]
    cash_available: float

    # Market Agent outputs
    market_analysis: Optional[Dict]
    alternative_suggestions: List[str]

    # Risk Agent outputs
    risk_assessment: Optional[Dict]

    # Compliance Agent outputs
    compliance_check: Optional[Dict]

    # Portfolio Manager (supervisor) state
    next_agent: str
    trade_decision: Optional[str]   # "EXECUTE", "BLOCKED", "PASS"
    negotiation_round: int
    max_negotiation_rounds: int

    # Final output
    final_report: str
    trade_executed: Optional[Dict]


# ═══════════════════════════════════════════════
# Step 2: Supervisor (Portfolio Manager)
#
# Coordinates the team. Decision logic:
#   1. No analysis yet → send to Market Agent
#   2. Market done → send to Risk Agent
#   3. Risk approved → send to Compliance Agent
#   4. Risk blocked → ask Market for alternative (or give up)
#   5. Compliance approved → finalize (execute)
#   6. Compliance blocked → ask Market for alternative (or give up)
# ═══════════════════════════════════════════════

def portfolio_manager(state: TradingState) -> TradingState:
    """Supervisor: coordinates agents and decides next step."""
    has_market = state["market_analysis"] is not None
    has_risk = state["risk_assessment"] is not None
    has_compliance = state["compliance_check"] is not None

    if not has_market:
        state["next_agent"] = "market"
        print("\n  📋 PM: Requesting market analysis...")

    elif not has_risk:
        ticker = state["market_analysis"].get("ticker")
        if not ticker:
            # Market couldn't find anything
            state["next_agent"] = "finalize"
            state["trade_decision"] = "PASS"
            print("\n  📋 PM: No viable trade found. PASS.")
        else:
            state["next_agent"] = "risk"
            print(f"\n  📋 PM: Checking risk for {ticker}...")

    elif not state["risk_assessment"].get("approved", False):
        # Risk blocked
        if state["negotiation_round"] >= state["max_negotiation_rounds"]:
            state["next_agent"] = "finalize"
            state["trade_decision"] = "PASS"
            print(f"\n  📋 PM: Max negotiation rounds ({state['max_negotiation_rounds']}) reached. PASS.")
        else:
            state["negotiation_round"] += 1
            state["risk_assessment"] = None
            state["compliance_check"] = None
            state["next_agent"] = "market"
            blocked_reason = state["risk_assessment"] if state["risk_assessment"] else "unknown"
            print(f"\n  📋 PM: Risk blocked. Requesting alternative (round {state['negotiation_round']})...")

    elif not has_compliance:
        state["next_agent"] = "compliance"
        ticker = state["market_analysis"].get("ticker", "?")
        print(f"\n  📋 PM: Risk approved. Checking compliance for {ticker}...")

    elif not state["compliance_check"].get("approved", False):
        # Compliance blocked
        if state["negotiation_round"] >= state["max_negotiation_rounds"]:
            state["next_agent"] = "finalize"
            state["trade_decision"] = "PASS"
            print(f"\n  📋 PM: Compliance blocked. Max rounds reached. PASS.")
        else:
            state["negotiation_round"] += 1
            state["risk_assessment"] = None
            state["compliance_check"] = None
            state["next_agent"] = "market"
            print(f"\n  📋 PM: Compliance blocked. Requesting alternative (round {state['negotiation_round']})...")

    else:
        # All approved!
        state["next_agent"] = "finalize"
        state["trade_decision"] = "EXECUTE"
        ticker = state["market_analysis"].get("ticker", "?")
        print(f"\n  📋 PM: All agents approved {ticker}. EXECUTE TRADE.")

    return state


# ═══════════════════════════════════════════════
# Step 3: Finalize (Execute or Report)
# ═══════════════════════════════════════════════

def finalize_decision(state: TradingState) -> TradingState:
    """Execute trade if approved, or generate pass report."""
    decision = state["trade_decision"]
    analysis = state["market_analysis"] or {}

    if decision == "EXECUTE":
        ticker = analysis.get("ticker", "?")
        shares = analysis.get("suggested_shares", 0)
        price = analysis.get("price", 0)
        value = round(price * shares, 2)

        state["trade_executed"] = {
            "ticker": ticker,
            "action": "BUY",
            "shares": shares,
            "price": price,
            "total_value": value,
        }

        # Generate final report with LLM if available
        state["final_report"] = _generate_final_report(state)

        print(f"\n  ✅ TRADE EXECUTED: BUY {shares} shares of {ticker} @ ${price:.2f} = ${value:,.2f}")

    else:
        state["trade_executed"] = None
        alts = state.get("alternative_suggestions", [])
        alt_text = f" Alternatives tried: {', '.join(alts)}." if alts else ""
        state["final_report"] = (
            f"No trade executed.{alt_text} "
            f"Reason: {'All alternatives blocked by risk/compliance.' if alts else 'No suitable opportunities within risk constraints.'} "
            f"Portfolio unchanged."
        )
        print(f"\n  ❌ NO TRADE: {state['final_report'][:100]}")

    return state


def _generate_final_report(state: TradingState) -> str:
    """Generate final report — LLM if available, else template."""
    trade = state["trade_executed"]
    analysis = state["market_analysis"] or {}
    alts = state.get("alternative_suggestions", [])

    try:
        from langchain_anthropic import ChatAnthropic

        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("No key")

        llm = ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            temperature=0, max_tokens=300,
        )

        alt_text = f"Original suggestions were blocked. Alternatives tried: {', '.join(alts)}. " if alts else ""
        prompt = (
            f"Write a 3-sentence trade execution summary for a portfolio manager.\n\n"
            f"Trade: BUY {trade['shares']} shares of {trade['ticker']} at ${trade['price']:.2f} (${trade['total_value']:,.2f})\n"
            f"Sector: {analysis.get('sector', 'N/A')}\n"
            f"Conviction: {analysis.get('conviction', 'N/A')}\n"
            f"{alt_text}"
            f"Risk and compliance checks passed. Be concise and professional."
        )
        response = llm.invoke(prompt)
        return response.content if isinstance(response.content, str) else str(response.content)

    except Exception:
        # Template fallback
        alt_text = f" Original suggestions blocked; {trade['ticker']} selected as alternative." if alts else ""
        return (
            f"Executed BUY {trade['shares']} shares of {trade['ticker']} at ${trade['price']:.2f} "
            f"(${trade['total_value']:,.2f}).{alt_text} "
            f"All risk and compliance checks passed."
        )


# ═══════════════════════════════════════════════
# Step 4: Routing
# ═══════════════════════════════════════════════

def route_next_agent(state: TradingState) -> str:
    """Route to the next agent based on supervisor decision."""
    return state["next_agent"]


# ═══════════════════════════════════════════════
# Step 5: Build the Graph
#
# Hub-and-spoke pattern:
#   PM → Market/Risk/Compliance → PM → ... → Finalize → END
#
# All specialist agents return to PM, who decides next step.
# ═══════════════════════════════════════════════

def create_trading_team():
    """Build the multi-agent trading team graph."""
    workflow = StateGraph(TradingState)

    # Add nodes
    workflow.add_node("portfolio_manager", portfolio_manager)
    workflow.add_node("market_agent", market_analysis_agent)
    workflow.add_node("risk_agent", risk_management_agent)
    workflow.add_node("compliance_agent", compliance_agent)
    workflow.add_node("finalize", finalize_decision)

    # Entry point: always start with PM
    workflow.set_entry_point("portfolio_manager")

    # PM routes to the next agent
    workflow.add_conditional_edges(
        "portfolio_manager",
        route_next_agent,
        {
            "market": "market_agent",
            "risk": "risk_agent",
            "compliance": "compliance_agent",
            "finalize": "finalize",
        },
    )

    # All specialist agents loop back to PM
    workflow.add_edge("market_agent", "portfolio_manager")
    workflow.add_edge("risk_agent", "portfolio_manager")
    workflow.add_edge("compliance_agent", "portfolio_manager")

    # Finalize → END
    workflow.add_edge("finalize", END)

    return workflow


# ═══════════════════════════════════════════════
# Step 6: Run
# ═══════════════════════════════════════════════

def analyze_trade(query: str, cash: float = 20000, portfolio_path: str = None):
    """
    Run the trading team on a query.

    Args:
        query: e.g., "Should we buy NVDA?" or "Find me a good trade"
        cash: Available cash for trading
        portfolio_path: Path to portfolio CSV (default: sample)
    """
    print("═" * 58)
    print("  💼 ALGORITHMIC TRADING TEAM")
    print("═" * 58)
    print(f"\n  Query: \"{query}\"\n")

    portfolio = load_portfolio(portfolio_path)
    print(format_portfolio_summary(portfolio, cash))
    print("\n" + "─" * 58)

    # Build and run graph
    workflow = create_trading_team()
    app = workflow.compile()

    initial_state: TradingState = {
        "user_query": query,
        "portfolio": portfolio,
        "cash_available": cash,
        "market_analysis": None,
        "alternative_suggestions": [],
        "risk_assessment": None,
        "compliance_check": None,
        "next_agent": "",
        "trade_decision": None,
        "negotiation_round": 0,
        "max_negotiation_rounds": 3,
        "final_report": "",
        "trade_executed": None,
    }

    result = app.invoke(initial_state)

    # Print final report
    print("\n" + "═" * 58)
    print("  📊 FINAL REPORT")
    print("═" * 58)
    print(f"\n  Decision: {result['trade_decision']}")

    if result["trade_executed"]:
        t = result["trade_executed"]
        print(f"  Trade: BUY {t['shares']} shares of {t['ticker']} @ ${t['price']:.2f}")
        print(f"  Total: ${t['total_value']:,.2f}")

    print(f"\n  {result['final_report']}")

    if result["alternative_suggestions"]:
        print(f"\n  Alternatives tried: {', '.join(result['alternative_suggestions'])}")

    print(f"  Negotiation rounds: {result['negotiation_round']}")
    print("═" * 58)

    return result


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Should we buy NVDA?"

    analyze_trade(query)
