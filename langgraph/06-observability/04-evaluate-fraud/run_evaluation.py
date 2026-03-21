"""
Fraud Detection Evaluation — Test Accuracy on a Dataset

Runs the fraud detection system (Example 02) on 20 test transactions
and measures accuracy, false positives, and false negatives.

Works with or without LangSmith:
- Without: prints results to terminal
- With LANGCHAIN_TRACING_V2=true: also sends traces to LangSmith

Usage:
    python run_evaluation.py

No special API key needed — uses rule-based mode (--no-llm).
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "02-fraud-detection"))

from fraud_data import FraudDataClient
from main import create_fraud_analyzer, FraudState


client = FraudDataClient()

# ═══════════════════════════════════════════════
# Test Dataset
# ═══════════════════════════════════════════════

def create_test_dataset():
    """
    Create 20 test transactions with expected outcomes.

    10 legitimate (should approve) + 10 fraudulent (should block/flag).
    """
    now = datetime.now()
    base_history = [
        client.create_sample_transaction(
            amount=45, merchant="Grocery", merchant_category="grocery",
            card_last4="1234", location="New York",
            timestamp=now - timedelta(hours=h),
        )
        for h in range(1, 4)
    ]

    dataset = []

    # 10 Legitimate transactions (expected: approve)
    legit_cases = [
        {"amount": 55, "merchant": "Gas Station", "category": "gas", "location": "New York", "hour": 14, "label": "Normal gas purchase"},
        {"amount": 32, "merchant": "Coffee Shop", "category": "food", "location": "New York", "hour": 9, "label": "Morning coffee"},
        {"amount": 120, "merchant": "Restaurant", "category": "food", "location": "New York", "hour": 19, "label": "Dinner"},
        {"amount": 85, "merchant": "Pharmacy", "category": "health", "location": "New York", "hour": 11, "label": "Pharmacy visit"},
        {"amount": 200, "merchant": "Department Store", "category": "retail", "location": "New York", "hour": 15, "label": "Shopping"},
        {"amount": 15, "merchant": "Parking", "category": "transport", "location": "New York", "hour": 10, "label": "Parking fee"},
        {"amount": 45, "merchant": "Bookstore", "category": "retail", "location": "New York", "hour": 13, "label": "Book purchase"},
        {"amount": 90, "merchant": "Gym", "category": "health", "location": "New York", "hour": 7, "label": "Gym membership"},
        {"amount": 65, "merchant": "Grocery Store", "category": "grocery", "location": "New York", "hour": 17, "label": "Groceries"},
        {"amount": 25, "merchant": "Subway", "category": "transport", "location": "New York", "hour": 8, "label": "Transit"},
    ]

    for case in legit_cases:
        tx = client.create_sample_transaction(
            amount=case["amount"], merchant=case["merchant"],
            merchant_category=case["category"], card_last4="1234",
            location=case["location"],
            timestamp=now.replace(hour=case["hour"]),
        )
        dataset.append({
            "transaction": tx,
            "history": base_history,
            "expected_action": "approve",
            "label": case["label"],
        })

    # 10 Fraudulent transactions (expected: block or flag)
    fraud_cases = [
        {"amount": 5000, "merchant": "Crypto Exchange", "category": "crypto", "location": "New York", "hour": 3, "label": "Crypto at 3 AM"},
        {"amount": 3000, "merchant": "Online Casino", "category": "gambling", "location": "New York", "hour": 2, "label": "Gambling at 2 AM"},
        {"amount": 1500, "merchant": "Wire Transfer", "category": "wire_transfer", "location": "New York", "hour": 4, "label": "Wire at 4 AM"},
        {"amount": 800, "merchant": "Electronics", "category": "retail", "location": "London", "hour": 1, "label": "Different country at 1 AM"},
        {"amount": 2000, "merchant": "Crypto", "category": "crypto", "location": "Tokyo", "hour": 5, "label": "Crypto from Tokyo at 5 AM"},
        {"amount": 999, "merchant": "Gift Cards", "category": "retail", "location": "Chicago", "hour": 3, "label": "Gift cards different city 3 AM"},
        {"amount": 4500, "merchant": "Gambling Site", "category": "gambling", "location": "Las Vegas", "hour": 1, "label": "Gambling from Vegas at 1 AM"},
        {"amount": 750, "merchant": "ATM Withdrawal", "category": "crypto", "location": "Miami", "hour": 4, "label": "Crypto from Miami at 4 AM"},
        {"amount": 1200, "merchant": "Wire Service", "category": "wire_transfer", "location": "New York", "hour": 2, "label": "Wire transfer at 2 AM"},
        {"amount": 3500, "merchant": "Crypto Exchange", "category": "crypto", "location": "New York", "hour": 3, "label": "Large crypto at 3 AM"},
    ]

    # Fraud transactions get the same New York history — so location
    # changes (London, Tokyo, etc.) trigger the location mismatch check
    for case in fraud_cases:
        tx = client.create_sample_transaction(
            amount=case["amount"], merchant=case["merchant"],
            merchant_category=case["category"], card_last4="1234",
            location=case["location"],
            timestamp=now.replace(hour=case["hour"]),
        )
        # Use recent history so location + velocity checks can fire
        recent_history = [
            client.create_sample_transaction(
                amount=50, merchant="Grocery", merchant_category="grocery",
                card_last4="1234", location="New York",
                timestamp=now.replace(hour=case["hour"]) - timedelta(minutes=30),
            )
        ] + base_history
        dataset.append({
            "transaction": tx,
            "history": recent_history,
            "expected_action": "block",
            "label": case["label"],
        })

    return dataset


# ═══════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════

def run_evaluation():
    """Run fraud detection on all test transactions and measure accuracy."""
    print("═" * 60)
    print("  FRAUD DETECTION EVALUATION")
    print("═" * 60)

    dataset = create_test_dataset()
    print(f"\n  Test set: {len(dataset)} transactions")
    print(f"    Legitimate: {sum(1 for d in dataset if d['expected_action'] == 'approve')}")
    print(f"    Fraudulent: {sum(1 for d in dataset if d['expected_action'] == 'block')}")
    print()

    workflow = create_fraud_analyzer()
    app = workflow.compile()

    results = []
    correct = 0
    false_positives = []
    false_negatives = []

    for i, case in enumerate(dataset, 1):
        tx = case["transaction"]

        state: FraudState = {
            "transaction_id": tx["transaction_id"],
            "transaction": tx,
            "user_history": case["history"],
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
        actual = result["action"]
        expected = case["expected_action"]

        # "flag" counts as "block" for evaluation (both are non-approve)
        actual_binary = "approve" if actual == "approve" else "block"

        is_correct = actual_binary == expected
        if is_correct:
            correct += 1
        elif expected == "approve" and actual_binary == "block":
            false_positives.append({**case, "actual": actual, "score": result["suspicion_score"]})
        elif expected == "block" and actual_binary == "approve":
            false_negatives.append({**case, "actual": actual, "score": result["suspicion_score"]})

        icon = "✓" if is_correct else "✗"
        sys.stdout.write(f"\r  Processing: {i}/{len(dataset)} {icon}")
        sys.stdout.flush()

    # Results
    accuracy = correct / len(dataset) * 100

    print(f"\n\n{'═' * 60}")
    print(f"  RESULTS")
    print(f"{'═' * 60}")
    print(f"\n  Accuracy: {correct}/{len(dataset)} ({accuracy:.0f}%)")
    print(f"  Correct:  {correct}")
    print(f"  Wrong:    {len(dataset) - correct}")

    if false_positives:
        print(f"\n  False Positives ({len(false_positives)}) — legit blocked:")
        for fp in false_positives:
            print(f"    ✗ ${fp['transaction']['amount']:,.0f} {fp['label']} — {fp['actual'].upper()} (score: {fp['score']:.3f})")

    if false_negatives:
        print(f"\n  False Negatives ({len(false_negatives)}) — fraud approved:")
        for fn in false_negatives:
            print(f"    ✗ ${fn['transaction']['amount']:,.0f} {fn['label']} — {fn['actual'].upper()} (score: {fn['score']:.3f})")

    if not false_positives and not false_negatives:
        print(f"\n  🎉 Perfect score!")

    # Recommendations
    if false_positives or false_negatives:
        print(f"\n  Recommendations:")
        if false_positives:
            print(f"    → Reduce sensitivity for normal merchant categories during business hours")
        if false_negatives:
            print(f"    → Increase weight for high-risk merchant categories (crypto, gambling)")

    print(f"\n{'═' * 60}")

    return {
        "accuracy": accuracy,
        "total": len(dataset),
        "correct": correct,
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
    }


if __name__ == "__main__":
    run_evaluation()
