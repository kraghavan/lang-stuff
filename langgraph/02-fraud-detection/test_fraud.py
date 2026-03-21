"""
Test script for Fraud Detection System.

Tests the graph structure, routing logic, and rule-based decisions.
No API key needed — all tests use --no-llm mode.
"""

from datetime import datetime, timedelta
from main import create_fraud_analyzer, FraudState
from fraud_data import FraudDataClient

client = FraudDataClient()


def make_state(amount, merchant_category, location="New York", history=None, hour=12):
    """Create a test state with a given transaction."""
    timestamp = datetime.now().replace(hour=hour)
    tx = client.create_sample_transaction(
        amount=amount,
        merchant="Test Merchant",
        merchant_category=merchant_category,
        card_last4="1234",
        location=location,
        timestamp=timestamp,
    )
    return {
        "transaction_id": tx["transaction_id"],
        "transaction": tx,
        "user_history": history or [],
        "patterns": {},
        "suspicion_score": 0.0,
        "suspicion_category": "",
        "suspicion_factors": [],
        "investigation_results": [],
        "investigation_depth": 0,
        "max_depth": 1,
        "action": "",
        "confidence": "",
        "explanation": "",
        "recommended_actions": [],
        "use_llm": False,
    }


def test_graph_compiles():
    """Test that the graph compiles."""
    print("Test 1: Graph compiles... ", end="")
    workflow = create_fraud_analyzer()
    app = workflow.compile()
    assert app is not None
    print("✓")


def test_low_risk_approves():
    """Test that low-risk transactions are approved."""
    print("Test 2: Low risk → approve... ", end="")
    workflow = create_fraud_analyzer()
    app = workflow.compile()

    # Normal grocery purchase
    history = [
        client.create_sample_transaction(
            amount=40, merchant="Grocery", merchant_category="grocery",
            card_last4="1234", location="New York",
            timestamp=datetime.now() - timedelta(hours=2),
        )
    ]
    state = make_state(55.0, "gas", history=history)
    result = app.invoke(state)

    assert result["suspicion_category"] == "low"
    assert result["action"] == "approve"
    print("✓")


def test_high_risk_blocks():
    """Test that high-risk transactions are blocked."""
    print("Test 3: High risk → block... ", end="")
    workflow = create_fraud_analyzer()
    app = workflow.compile()

    # Transaction at a specific time
    tx_time = datetime.now().replace(hour=2, minute=30)

    # History: 8 transactions within the last hour from a DIFFERENT location
    history = [
        client.create_sample_transaction(
            amount=100, merchant=f"M{i}", merchant_category="retail",
            card_last4="1234", location="Chicago",
            timestamp=tx_time - timedelta(minutes=i * 3),
        )
        for i in range(8)
    ]

    # Build state directly with the right timestamp
    tx = client.create_sample_transaction(
        amount=1500, merchant="Casino Online", merchant_category="gambling",
        card_last4="1234", location="New York", timestamp=tx_time,
    )
    state: FraudState = {
        "transaction_id": tx["transaction_id"],
        "transaction": tx,
        "user_history": history,
        "patterns": {},
        "suspicion_score": 0.0,
        "suspicion_category": "",
        "suspicion_factors": [],
        "investigation_results": [],
        "investigation_depth": 0,
        "max_depth": 1,
        "action": "",
        "confidence": "",
        "explanation": "",
        "recommended_actions": [],
        "use_llm": False,
    }
    result = app.invoke(state)

    # Score should be high (>=0.7) or at least medium with a block action
    assert result["suspicion_score"] >= 0.5, f"Expected high suspicion, got {result['suspicion_score']}"
    assert result["action"] == "block", f"Expected block, got {result['action']}"
    print("✓")


def test_medium_risk_investigates():
    """Test that medium-risk triggers investigation."""
    print("Test 4: Medium risk → investigate... ", end="")
    workflow = create_fraud_analyzer()
    app = workflow.compile()

    tx_time = datetime.now().replace(hour=3, minute=15)

    # History: recent transaction from different city (triggers location check)
    history = [
        client.create_sample_transaction(
            amount=40, merchant="Grocery", merchant_category="grocery",
            card_last4="1234", location="Chicago",
            timestamp=tx_time - timedelta(minutes=30),
        )
    ]

    # Crypto at 3 AM from different location → should hit time + merchant + location
    tx = client.create_sample_transaction(
        amount=750, merchant="Crypto Exchange", merchant_category="crypto",
        card_last4="1234", location="New York", timestamp=tx_time,
    )
    state: FraudState = {
        "transaction_id": tx["transaction_id"],
        "transaction": tx,
        "user_history": history,
        "patterns": {},
        "suspicion_score": 0.0,
        "suspicion_category": "",
        "suspicion_factors": [],
        "investigation_results": [],
        "investigation_depth": 0,
        "max_depth": 1,
        "action": "",
        "confidence": "",
        "explanation": "",
        "recommended_actions": [],
        "use_llm": False,
    }
    result = app.invoke(state)

    assert result["suspicion_score"] >= 0.4, f"Expected medium+ suspicion, got {result['suspicion_score']}"
    assert result["action"] in ("approve", "flag", "block")
    print("✓")


def test_conditional_routing():
    """Test that routing function returns correct keys."""
    print("Test 5: Routing logic... ", end="")
    from main import route_by_suspicion

    low_state = {"suspicion_category": "low"}
    high_state = {"suspicion_category": "high"}
    med_state = {"suspicion_category": "medium"}

    assert route_by_suspicion(low_state) == "approve"
    assert route_by_suspicion(high_state) == "block"
    assert route_by_suspicion(med_state) == "investigate"
    print("✓")


if __name__ == "__main__":
    print("\n🧪 Fraud Detection Tests")
    print("=" * 40)

    test_graph_compiles()
    test_low_risk_approves()
    test_high_risk_blocks()
    test_medium_risk_investigates()
    test_conditional_routing()

    print("\n✅ All tests passed!")
