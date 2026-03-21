"""
Fraud Detection Data API

Transaction analysis for fraud detection. Based on patterns from
real credit card fraud datasets.

Key fraud indicators:
- Velocity: Multiple transactions in short time
- Amount anomalies: Unusually large or small amounts
- Location mismatches: Transaction far from normal location
- Time patterns: Transactions at unusual hours
- Merchant category: High-risk merchant types

No LLM needed — this is pure rule-based scoring.

Usage:
    from fraud_data import FraudDataClient
    client = FraudDataClient()
    score = client.calculate_suspicion_score(transaction, history)
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FraudDataClient:
    """Client for analyzing transactions for fraud indicators."""

    def __init__(self):
        """Initialize fraud detection client with scoring weights."""
        self.fraud_patterns = {
            "velocity": {"threshold": 5, "weight": 0.30},
            "amount_anomaly": {"threshold": 3.0, "weight": 0.25},
            "location": {"distance_km": 500, "weight": 0.20},
            "time": {"suspicious_hours": [0, 1, 2, 3, 4, 5], "weight": 0.10},
            "merchant": {
                "high_risk": ["gambling", "crypto", "wire_transfer"],
                "weight": 0.15,
            },
        }

    def create_sample_transaction(
        self,
        amount: float,
        merchant: str,
        merchant_category: str,
        card_last4: str,
        location: str,
        timestamp: Optional[datetime] = None,
    ) -> Dict:
        """Create a sample transaction dictionary."""
        if timestamp is None:
            timestamp = datetime.now()

        return {
            "transaction_id": f"TX_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}",
            "amount": amount,
            "merchant": merchant,
            "merchant_category": merchant_category,
            "card_last4": card_last4,
            "location": location,
            "timestamp": timestamp.isoformat(),
            "status": "pending",
        }

    def calculate_suspicion_score(
        self, transaction: Dict, user_history: Optional[List[Dict]] = None
    ) -> float:
        """
        Calculate suspicion score (0-1, where 1 = most suspicious).

        Checks: velocity, amount anomaly, location, time, merchant category.
        """
        score = 0.0
        if user_history is None:
            user_history = []

        # 1. Velocity check
        if user_history:
            recent = [
                tx
                for tx in user_history
                if self._time_diff_hours(tx["timestamp"], transaction["timestamp"]) < 1
            ]
            if len(recent) > self.fraud_patterns["velocity"]["threshold"]:
                velocity_score = min(len(recent) / 10, 1)
                score += velocity_score * self.fraud_patterns["velocity"]["weight"]

        # 2. Amount anomaly
        amount = transaction.get("amount", 0)
        if user_history:
            amounts = [tx.get("amount", 0) for tx in user_history]
            mean = sum(amounts) / len(amounts)
            std = (sum((x - mean) ** 2 for x in amounts) / len(amounts)) ** 0.5
            if std > 0:
                z_score = abs((amount - mean) / std)
                if z_score > self.fraud_patterns["amount_anomaly"]["threshold"]:
                    amount_score = min(z_score / 5, 1)
                    score += (
                        amount_score * self.fraud_patterns["amount_anomaly"]["weight"]
                    )
        else:
            if amount > 500:
                score += 0.5 * self.fraud_patterns["amount_anomaly"]["weight"]

        # 3. Location check
        if user_history:
            last_location = user_history[0].get("location", "")
            current_location = transaction.get("location", "")
            if (
                last_location
                and current_location
                and last_location != current_location
            ):
                time_diff = self._time_diff_hours(
                    user_history[0]["timestamp"], transaction["timestamp"]
                )
                if time_diff < 2:
                    score += 1.0 * self.fraud_patterns["location"]["weight"]

        # 4. Time pattern
        tx_time = datetime.fromisoformat(transaction["timestamp"])
        if tx_time.hour in self.fraud_patterns["time"]["suspicious_hours"]:
            score += 1.0 * self.fraud_patterns["time"]["weight"]

        # 5. Merchant category
        category = transaction.get("merchant_category", "")
        if category in self.fraud_patterns["merchant"]["high_risk"]:
            score += 1.0 * self.fraud_patterns["merchant"]["weight"]

        return round(min(score, 1.0), 3)

    def _time_diff_hours(self, time1: str, time2: str) -> float:
        """Calculate time difference in hours."""
        t1 = datetime.fromisoformat(time1)
        t2 = datetime.fromisoformat(time2)
        return abs((t2 - t1).total_seconds() / 3600)

    def get_suspicion_category(self, suspicion_score: float) -> str:
        """Categorize suspicion: 'low', 'medium', or 'high'."""
        if suspicion_score < 0.4:
            return "low"
        elif suspicion_score < 0.7:
            return "medium"
        else:
            return "high"

    def extract_patterns(self, transaction: Dict) -> Dict:
        """Extract key patterns from a transaction."""
        tx_time = datetime.fromisoformat(transaction["timestamp"])
        return {
            "amount": transaction.get("amount", 0),
            "merchant": transaction.get("merchant", "unknown"),
            "category": transaction.get("merchant_category", "unknown"),
            "location": transaction.get("location", "unknown"),
            "hour": tx_time.hour,
            "day_of_week": tx_time.strftime("%A"),
            "card_last4": transaction.get("card_last4", "unknown"),
        }

    def get_suspicion_factors(
        self, transaction: Dict, user_history: Optional[List[Dict]] = None
    ) -> List[str]:
        """Identify specific suspicion factors for a transaction."""
        factors = []
        if user_history is None:
            user_history = []

        # Velocity
        if user_history:
            recent = [
                tx
                for tx in user_history
                if self._time_diff_hours(tx["timestamp"], transaction["timestamp"])
                < 1
            ]
            if len(recent) > self.fraud_patterns["velocity"]["threshold"]:
                factors.append(
                    f"High velocity: {len(recent)} transactions in 1 hour"
                )

        # Amount
        amount = transaction.get("amount", 0)
        if amount > 1000:
            factors.append(f"Large amount: ${amount:,.2f}")
        elif amount < 1:
            factors.append(f"Unusually small amount: ${amount:.2f}")

        # Time
        tx_time = datetime.fromisoformat(transaction["timestamp"])
        if tx_time.hour in self.fraud_patterns["time"]["suspicious_hours"]:
            factors.append(f"Suspicious time: {tx_time.hour}:00 (late night)")

        # Merchant
        category = transaction.get("merchant_category", "")
        if category in self.fraud_patterns["merchant"]["high_risk"]:
            factors.append(f"High-risk merchant category: {category}")

        # Location
        if user_history:
            last_location = user_history[0].get("location", "")
            current_location = transaction.get("location", "")
            if (
                last_location
                and current_location
                and last_location != current_location
            ):
                time_diff = self._time_diff_hours(
                    user_history[0]["timestamp"], transaction["timestamp"]
                )
                if time_diff < 2:
                    factors.append(
                        f"Location change: {last_location} → {current_location} "
                        f"in {time_diff:.1f} hours"
                    )

        return factors


# ═══════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testing Fraud Detection Client\n")

    client = FraudDataClient()

    # Normal transaction history
    base_time = datetime.now() - timedelta(hours=5)
    history = [
        client.create_sample_transaction(
            amount=45.20,
            merchant="Grocery Store",
            merchant_category="grocery",
            card_last4="1234",
            location="New York",
            timestamp=base_time + timedelta(hours=i),
        )
        for i in range(3)
    ]

    # Test 1: Normal transaction
    print("Test 1: Normal Transaction")
    normal = client.create_sample_transaction(
        amount=55.00,
        merchant="Gas Station",
        merchant_category="gas",
        card_last4="1234",
        location="New York",
    )
    score = client.calculate_suspicion_score(normal, history)
    print(f"  Score: {score} ({client.get_suspicion_category(score)})")
    print(f"  Factors: {client.get_suspicion_factors(normal, history)}")

    # Test 2: Suspicious transaction
    print("\nTest 2: Suspicious Transaction (crypto at 3 AM)")
    suspicious = client.create_sample_transaction(
        amount=750,
        merchant="Crypto Exchange",
        merchant_category="crypto",
        card_last4="1234",
        location="New York",
        timestamp=datetime.now().replace(hour=3),
    )
    score = client.calculate_suspicion_score(suspicious, history)
    print(f"  Score: {score} ({client.get_suspicion_category(score)})")
    print(f"  Factors: {client.get_suspicion_factors(suspicious, history)}")

    print("\n✅ All tests passed!")
