"""
Fraud Detection System — LangGraph Conditional Routing

Demonstrates multi-path conditional routing in LangGraph.
Transactions are scored and routed to different paths based on risk:

    Low suspicion  → Quick approve
    High suspicion → Quick block
    Medium suspicion → Investigate (with optional LLM analysis)

Supports two modes:
    --no-llm    Rule-based only (no API key needed)
    (default)   Uses Claude for medium-risk investigation

Usage:
    python main.py              # With LLM (needs ANTHROPIC_API_KEY)
    python main.py --no-llm     # Without LLM (runs offline)
"""

import os
import sys
from typing import TypedDict, Literal, List, Dict, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END

from fraud_data import FraudDataClient


# ═══════════════════════════════════════════════
# Step 1: Define State
# ═══════════════════════════════════════════════

class FraudState(TypedDict):
    """State that flows through the fraud detection graph."""
    # Input
    transaction_id: str
    transaction: Dict
    user_history: List[Dict]

    # Analysis
    patterns: Dict
    suspicion_score: float
    suspicion_category: str
    suspicion_factors: List[str]

    # Investigation
    investigation_results: List[str]
    investigation_depth: int
    max_depth: int

    # Decision
    action: str       # "approve", "block", "flag"
    confidence: str   # "high", "medium", "low"
    explanation: str
    recommended_actions: List[str]

    # Config
    use_llm: bool


# ═══════════════════════════════════════════════
# Step 2: Initialize tools
# ═══════════════════════════════════════════════

fraud_client = FraudDataClient()


# ═══════════════════════════════════════════════
# Step 3: Define Nodes
# ═══════════════════════════════════════════════

def fetch_transaction(state: FraudState) -> FraudState:
    """Node 1: Load and validate the transaction."""
    print(f"\n📥 Processing transaction {state['transaction_id']}...")
    tx = state["transaction"]
    print(f"  Amount: ${tx.get('amount', 0):,.2f}")
    print(f"  Merchant: {tx.get('merchant', 'unknown')} ({tx.get('merchant_category', '')})")
    print(f"  Location: {tx.get('location', 'unknown')}")
    return state


def extract_patterns(state: FraudState) -> FraudState:
    """Node 2: Extract patterns and calculate suspicion score."""
    print("\n📊 Analyzing transaction patterns...")
    tx = state["transaction"]
    history = state["user_history"]

    state["patterns"] = fraud_client.extract_patterns(tx)
    state["suspicion_score"] = fraud_client.calculate_suspicion_score(tx, history)
    state["suspicion_category"] = fraud_client.get_suspicion_category(state["suspicion_score"])
    state["suspicion_factors"] = fraud_client.get_suspicion_factors(tx, history)

    print(f"  Suspicion Score: {state['suspicion_score']:.3f} ({state['suspicion_category']})")
    if state["suspicion_factors"]:
        for factor in state["suspicion_factors"]:
            print(f"  ⚠ {factor}")
    else:
        print("  ✓ No suspicious factors detected")

    return state


def quick_approve(state: FraudState) -> FraudState:
    """Node 3a: Instant approval for low-risk transactions."""
    print("\n✅ QUICK APPROVE")
    state["action"] = "approve"
    state["confidence"] = "high"
    state["explanation"] = (
        f"Low suspicion score ({state['suspicion_score']:.3f}). "
        f"Transaction matches normal spending patterns."
    )
    state["recommended_actions"] = []
    print(f"  Approved: ${state['transaction']['amount']:,.2f}")
    return state


def quick_block(state: FraudState) -> FraudState:
    """Node 3b: Instant block for high-risk transactions."""
    print("\n🚫 QUICK BLOCK")
    state["action"] = "block"
    state["confidence"] = "high"
    factors_text = "; ".join(state["suspicion_factors"][:3])
    state["explanation"] = (
        f"High suspicion score ({state['suspicion_score']:.3f}). "
        f"Indicators: {factors_text}."
    )
    state["recommended_actions"] = [
        "Contact cardholder to verify",
        "Review account for other suspicious activity",
        "Consider temporary card freeze",
    ]
    print(f"  Blocked: ${state['transaction']['amount']:,.2f}")
    return state


def investigate_transaction(state: FraudState) -> FraudState:
    """Node 3c: Deep investigation for medium-risk transactions."""
    print("\n🔍 INVESTIGATING...")
    state["investigation_depth"] += 1

    patterns = state["patterns"]
    factors = state["suspicion_factors"]

    if state["use_llm"]:
        # LLM-powered investigation
        try:
            from langchain_anthropic import ChatAnthropic

            llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
                temperature=0,
                max_tokens=512,
            )
            prompt = (
                f"Analyze this transaction for fraud. Be concise (3 sentences max).\n\n"
                f"Amount: ${patterns['amount']:,.2f} at {patterns['merchant']} ({patterns['category']})\n"
                f"Location: {patterns['location']}, Time: {patterns['hour']}:00\n"
                f"Flags: {', '.join(factors) if factors else 'None major'}\n"
                f"Suspicion score: {state['suspicion_score']:.3f}\n\n"
                f"Recommend: approve, block, or flag for manual review."
            )

            print(f"  🤖 Running Claude analysis...")
            response = llm.invoke(prompt)
            analysis = response.content

            state["investigation_results"].append(analysis)
            state["explanation"] = analysis

            # Parse decision
            analysis_lower = analysis.lower()
            if "block" in analysis_lower:
                state["action"] = "block"
                state["confidence"] = "medium"
                state["recommended_actions"] = ["Contact cardholder"]
            elif "flag" in analysis_lower or "review" in analysis_lower:
                state["action"] = "flag"
                state["confidence"] = "medium"
                state["recommended_actions"] = ["Manual fraud analyst review"]
            else:
                state["action"] = "approve"
                state["confidence"] = "medium"
                state["recommended_actions"] = []

            print(f"  ✓ LLM decision: {state['action']}")

        except Exception as e:
            print(f"  ✗ LLM error: {e}")
            _rule_based_decision(state)
    else:
        # Rule-based investigation (no LLM)
        _rule_based_decision(state)

    return state


def _rule_based_decision(state: FraudState):
    """Fallback rule-based decision for medium-risk transactions."""
    score = state["suspicion_score"]
    factors = state["suspicion_factors"]

    if score > 0.55 or len(factors) >= 3:
        state["action"] = "block"
        state["confidence"] = "medium"
        state["explanation"] = (
            f"Suspicion score {score:.3f} with {len(factors)} risk factors. "
            f"Blocked as precaution."
        )
        state["recommended_actions"] = ["Contact cardholder to verify"]
    elif score > 0.45:
        state["action"] = "flag"
        state["confidence"] = "medium"
        state["explanation"] = (
            f"Suspicion score {score:.3f} is borderline. "
            f"Flagged for manual review."
        )
        state["recommended_actions"] = ["Manual fraud analyst review"]
    else:
        state["action"] = "approve"
        state["confidence"] = "medium"
        state["explanation"] = (
            f"Suspicion score {score:.3f} is on the lower end of medium. "
            f"Approved with monitoring."
        )
        state["recommended_actions"] = ["Monitor next 24h of activity"]

    print(f"  ✓ Rule-based decision: {state['action']}")


def finalize_decision(state: FraudState) -> FraudState:
    """Node 4: Finalize and log the decision."""
    print(f"\n📝 Final: {state['action'].upper()} (confidence: {state['confidence']})")
    if state["recommended_actions"]:
        for rec in state["recommended_actions"]:
            print(f"  → {rec}")
    return state


# ═══════════════════════════════════════════════
# Step 4: Routing Logic
#
# This is the KEY CONCEPT — conditional edges.
# The routing function returns a string that maps
# to the next node via the edge dictionary.
# ═══════════════════════════════════════════════

def route_by_suspicion(state: FraudState) -> Literal["approve", "block", "investigate"]:
    """
    Route based on suspicion level.

    Returns the KEY of the edge to follow:
    - "approve" → quick_approve node
    - "block"   → quick_block node
    - "investigate" → investigate node
    """
    category = state["suspicion_category"]
    if category == "low":
        print("  → Routing: LOW risk → quick approve")
        return "approve"
    elif category == "high":
        print("  → Routing: HIGH risk → quick block")
        return "block"
    else:
        print("  → Routing: MEDIUM risk → investigate")
        return "investigate"


def should_continue_investigating(state: FraudState) -> Literal["investigate", "finalize"]:
    """Decide whether to loop back for more investigation."""
    if state["investigation_depth"] >= state["max_depth"]:
        return "finalize"
    return "finalize"  # For now, always finalize after first pass


# ═══════════════════════════════════════════════
# Step 5: Build the Graph
#
# This graph has CONDITIONAL EDGES — the path
# depends on the suspicion score.
#
#   extract_patterns → [route_by_suspicion]
#                          ├─ low  → quick_approve → finalize
#                          ├─ high → quick_block   → finalize
#                          └─ mid  → investigate   → finalize
# ═══════════════════════════════════════════════

def create_fraud_analyzer() -> StateGraph:
    """Build the fraud detection graph."""
    workflow = StateGraph(FraudState)

    # Add nodes
    workflow.add_node("fetch_transaction", fetch_transaction)
    workflow.add_node("extract_patterns", extract_patterns)
    workflow.add_node("quick_approve", quick_approve)
    workflow.add_node("quick_block", quick_block)
    workflow.add_node("investigate", investigate_transaction)
    workflow.add_node("finalize", finalize_decision)

    # Entry point
    workflow.set_entry_point("fetch_transaction")

    # Linear edge: fetch → extract
    workflow.add_edge("fetch_transaction", "extract_patterns")

    # CONDITIONAL EDGES: route based on suspicion
    workflow.add_conditional_edges(
        "extract_patterns",
        route_by_suspicion,
        {
            "approve": "quick_approve",
            "block": "quick_block",
            "investigate": "investigate",
        },
    )

    # After investigation, could loop or finalize
    workflow.add_conditional_edges(
        "investigate",
        should_continue_investigating,
        {"investigate": "investigate", "finalize": "finalize"},
    )

    # Quick paths → finalize
    workflow.add_edge("quick_approve", "finalize")
    workflow.add_edge("quick_block", "finalize")

    # End
    workflow.add_edge("finalize", END)

    return workflow


# ═══════════════════════════════════════════════
# Step 6: Main Function
# ═══════════════════════════════════════════════

def analyze_transaction(
    amount: float,
    merchant: str,
    merchant_category: str,
    location: str,
    card_last4: str = "1234",
    user_history: Optional[List[Dict]] = None,
    timestamp: Optional[datetime] = None,
    use_llm: bool = True,
    max_depth: int = 1,
):
    """Analyze a transaction for fraud."""
    print("═" * 55)
    print("  FRAUD DETECTION SYSTEM")
    print("═" * 55)

    tx = fraud_client.create_sample_transaction(
        amount=amount,
        merchant=merchant,
        merchant_category=merchant_category,
        card_last4=card_last4,
        location=location,
        timestamp=timestamp,
    )

    workflow = create_fraud_analyzer()
    app = workflow.compile()

    initial_state: FraudState = {
        "transaction_id": tx["transaction_id"],
        "transaction": tx,
        "user_history": user_history or [],
        "patterns": {},
        "suspicion_score": 0.0,
        "suspicion_category": "",
        "suspicion_factors": [],
        "investigation_results": [],
        "investigation_depth": 0,
        "max_depth": max_depth,
        "action": "",
        "confidence": "",
        "explanation": "",
        "recommended_actions": [],
        "use_llm": use_llm,
    }

    final_state = app.invoke(initial_state)

    # Print summary
    print("\n" + "═" * 55)
    print("  DECISION SUMMARY")
    print("═" * 55)
    print(f"  Transaction: ${amount:,.2f} at {merchant}")
    print(f"  Suspicion:   {final_state['suspicion_score']:.3f} ({final_state['suspicion_category']})")
    print(f"  Action:      {final_state['action'].upper()}")
    print(f"  Confidence:  {final_state['confidence']}")
    print(f"  Explanation: {final_state['explanation'][:120]}")
    print("═" * 55)

    return final_state


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    use_llm = "--no-llm" not in sys.argv

    if use_llm and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set. Running in --no-llm mode.")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("  Or run with: python main.py --no-llm\n")
        use_llm = False

    mode = "LLM-assisted" if use_llm else "rule-based only"
    print(f"🔒 Fraud Detection System ({mode})\n")

    # Create normal history
    base_time = datetime.now() - timedelta(hours=5)
    normal_history = [
        fraud_client.create_sample_transaction(
            amount=45.20,
            merchant="Grocery Store",
            merchant_category="grocery",
            card_last4="1234",
            location="New York",
            timestamp=base_time + timedelta(hours=i),
        )
        for i in range(3)
    ]

    # Test 1: Normal transaction (→ approve)
    print("\n" + "=" * 55)
    print("TEST 1: NORMAL TRANSACTION")
    analyze_transaction(
        amount=55.00,
        merchant="Gas Station",
        merchant_category="gas",
        location="New York",
        user_history=normal_history,
        use_llm=use_llm,
    )

    # Test 2: Obvious fraud (→ block)
    print("\n\nTEST 2: HIGH-VELOCITY FRAUD")
    fraud_history = normal_history + [
        fraud_client.create_sample_transaction(
            amount=100,
            merchant=f"Store {i}",
            merchant_category="retail",
            card_last4="1234",
            location="New York",
            timestamp=datetime.now() - timedelta(minutes=i * 5),
        )
        for i in range(8)
    ]
    analyze_transaction(
        amount=1500,
        merchant="Online Electronics",
        merchant_category="retail",
        location="New York",
        user_history=fraud_history,
        use_llm=use_llm,
    )

    # Test 3: Suspicious (→ investigate)
    print("\n\nTEST 3: SUSPICIOUS TRANSACTION")
    analyze_transaction(
        amount=750,
        merchant="Crypto Exchange",
        merchant_category="crypto",
        location="New York",
        user_history=normal_history,
        timestamp=datetime.now().replace(hour=3),
        use_llm=use_llm,
    )
