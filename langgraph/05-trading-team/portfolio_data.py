"""
Portfolio Data — Loading, Risk Calculations, and Constraint Checking

Handles portfolio loading from CSV, sector calculations, and all
rule-based risk/compliance checks. No LLM needed.

Usage:
    from portfolio_data import load_portfolio, calculate_sector_breakdown, check_risk_limits
"""

import csv
import os
from typing import Dict, List, Tuple

from market_data import get_price, get_sector, get_correlation


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ═══════════════════════════════════════════════
# Risk limits (configurable)
# ═══════════════════════════════════════════════
MAX_SECTOR_PCT = 0.40          # Max 40% in any one sector
MAX_POSITION_PCT = 0.15        # Max 15% in any one holding (risk)
MAX_COMPLIANCE_POSITION_PCT = 0.10  # Max 10% in any one holding (compliance)
MAX_PORTFOLIO_VOLATILITY = 0.25     # Max 25% portfolio volatility
MAX_CORRELATED_POSITIONS = 3        # Max 3 highly correlated positions

# Restricted tickers (compliance — e.g., company insiders, sanctioned)
RESTRICTED_LIST = ["META", "COIN"]

# Blackout tickers (earnings blackout period)
BLACKOUT_LIST = ["TSLA"]

# Simulated volatility by sector
SECTOR_VOLATILITY = {
    "Technology": 0.28,
    "Financials": 0.22,
    "Healthcare": 0.20,
    "Consumer Staples": 0.12,
    "Energy": 0.25,
}


def load_portfolio(filepath: str = None) -> Dict[str, Dict]:
    """
    Load portfolio from CSV.

    Returns:
        {"AAPL": {"shares": 100, "cost_basis": 150.0, "sector": "Technology"}, ...}
    """
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "sample_portfolio.csv")

    portfolio = {}
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row["ticker"].strip().upper()
            portfolio[ticker] = {
                "shares": int(row["shares"]),
                "cost_basis": float(row["cost_basis"]),
                "sector": row["sector"].strip(),
            }
    return portfolio


def calculate_portfolio_value(portfolio: Dict[str, Dict]) -> float:
    """Calculate total portfolio market value."""
    total = 0.0
    for ticker, holding in portfolio.items():
        price = get_price(ticker)
        total += price * holding["shares"]
    return total


def calculate_sector_breakdown(portfolio: Dict[str, Dict]) -> Dict[str, float]:
    """
    Calculate sector allocation as percentages.

    Returns:
        {"Technology": 0.81, "Financials": 0.16, "Healthcare": 0.03}
    """
    total_value = calculate_portfolio_value(portfolio)
    if total_value == 0:
        return {}

    sectors: Dict[str, float] = {}
    for ticker, holding in portfolio.items():
        sector = holding["sector"]
        value = get_price(ticker) * holding["shares"]
        sectors[sector] = sectors.get(sector, 0) + value

    return {sector: round(value / total_value, 4) for sector, value in sectors.items()}


def calculate_position_weights(portfolio: Dict[str, Dict]) -> Dict[str, float]:
    """Calculate each position's weight in the portfolio."""
    total_value = calculate_portfolio_value(portfolio)
    if total_value == 0:
        return {}

    weights = {}
    for ticker, holding in portfolio.items():
        value = get_price(ticker) * holding["shares"]
        weights[ticker] = round(value / total_value, 4)
    return weights


def estimate_portfolio_volatility(portfolio: Dict[str, Dict]) -> float:
    """Estimate portfolio volatility based on sector weights and correlations."""
    sectors = calculate_sector_breakdown(portfolio)
    # Simplified: weighted average of sector volatilities adjusted by correlation
    vol_sq = 0.0
    sector_list = list(sectors.items())
    for i, (s1, w1) in enumerate(sector_list):
        v1 = SECTOR_VOLATILITY.get(s1, 0.20)
        for j, (s2, w2) in enumerate(sector_list):
            v2 = SECTOR_VOLATILITY.get(s2, 0.20)
            corr = get_correlation(s1, s2)
            vol_sq += w1 * w2 * v1 * v2 * corr
    return round(vol_sq ** 0.5, 4)


def calculate_shares_to_buy(cash: float, price: float, portfolio_value: float, max_pct: float = MAX_COMPLIANCE_POSITION_PCT) -> int:
    """
    Calculate how many shares to buy within compliance position limit.

    The compliance check uses: new_value / (portfolio_market_value + new_value) <= max_pct
    Solving for new_value: new_value <= max_pct * portfolio_market_value / (1 - max_pct)

    Here portfolio_value should be the MARKET value of existing holdings only (not including cash).
    """
    if price <= 0:
        return 0
    # Max value to stay within compliance limit
    max_value = max_pct * portfolio_value / (1 - max_pct)
    max_from_limit = int(max_value / price)
    max_from_cash = int(cash / price)
    return max(0, min(max_from_limit, max_from_cash))


# ═══════════════════════════════════════════════
# Risk checks (used by Risk Agent)
# ═══════════════════════════════════════════════

def check_sector_limits(portfolio: Dict, new_ticker: str, new_shares: int) -> Dict:
    """Check if adding a position would exceed sector limits."""
    sector = get_sector(new_ticker)
    new_value = get_price(new_ticker) * new_shares
    total_value = calculate_portfolio_value(portfolio) + new_value

    # Calculate sector exposure after trade
    sectors = {}
    for t, h in portfolio.items():
        s = h["sector"]
        sectors[s] = sectors.get(s, 0) + get_price(t) * h["shares"]
    sectors[sector] = sectors.get(sector, 0) + new_value

    sector_pct = sectors[sector] / total_value if total_value > 0 else 0

    return {
        "passed": sector_pct <= MAX_SECTOR_PCT,
        "sector": sector,
        "current_pct": round(sector_pct, 4),
        "limit": MAX_SECTOR_PCT,
        "detail": f"{sector}: {sector_pct:.1%} (limit: {MAX_SECTOR_PCT:.0%})",
    }


def check_position_limits(portfolio: Dict, new_ticker: str, new_shares: int) -> Dict:
    """Check if position size would exceed risk limits."""
    new_value = get_price(new_ticker) * new_shares
    total_value = calculate_portfolio_value(portfolio) + new_value
    existing = portfolio.get(new_ticker, {})
    existing_value = get_price(new_ticker) * existing.get("shares", 0)
    position_value = existing_value + new_value
    position_pct = position_value / total_value if total_value > 0 else 0

    return {
        "passed": position_pct <= MAX_POSITION_PCT,
        "ticker": new_ticker,
        "position_pct": round(position_pct, 4),
        "limit": MAX_POSITION_PCT,
        "detail": f"{new_ticker}: {position_pct:.1%} (limit: {MAX_POSITION_PCT:.0%})",
    }


def check_correlation(portfolio: Dict, new_ticker: str) -> Dict:
    """Check if adding a position creates too many correlated holdings."""
    new_sector = get_sector(new_ticker)
    same_sector = [t for t, h in portfolio.items() if h["sector"] == new_sector]
    count_after = len(same_sector) + 1  # +1 for the new ticker

    return {
        "passed": count_after <= MAX_CORRELATED_POSITIONS,
        "same_sector_count": count_after,
        "limit": MAX_CORRELATED_POSITIONS,
        "detail": f"{count_after} positions in {new_sector} (limit: {MAX_CORRELATED_POSITIONS})",
    }


def check_volatility(portfolio: Dict, new_ticker: str, new_shares: int) -> Dict:
    """Check if adding a position would push portfolio volatility too high."""
    # Simulate adding the position
    simulated = dict(portfolio)
    existing = simulated.get(new_ticker, {"shares": 0, "cost_basis": get_price(new_ticker), "sector": get_sector(new_ticker)})
    simulated[new_ticker] = {
        "shares": existing["shares"] + new_shares,
        "cost_basis": existing.get("cost_basis", get_price(new_ticker)),
        "sector": existing.get("sector", get_sector(new_ticker)),
    }

    vol = estimate_portfolio_volatility(simulated)

    return {
        "passed": vol <= MAX_PORTFOLIO_VOLATILITY,
        "estimated_volatility": vol,
        "limit": MAX_PORTFOLIO_VOLATILITY,
        "detail": f"Portfolio volatility: {vol:.1%} (limit: {MAX_PORTFOLIO_VOLATILITY:.0%})",
    }


# ═══════════════════════════════════════════════
# Compliance checks (used by Compliance Agent)
# ═══════════════════════════════════════════════

def check_compliance_position_limit(portfolio: Dict, new_ticker: str, new_shares: int) -> Dict:
    """Compliance position limit (stricter than risk: 10% vs 15%)."""
    new_value = get_price(new_ticker) * new_shares
    total_value = calculate_portfolio_value(portfolio) + new_value
    existing = portfolio.get(new_ticker, {})
    existing_value = get_price(new_ticker) * existing.get("shares", 0)
    position_value = existing_value + new_value
    position_pct = position_value / total_value if total_value > 0 else 0

    return {
        "passed": position_pct <= MAX_COMPLIANCE_POSITION_PCT,
        "position_pct": round(position_pct, 4),
        "limit": MAX_COMPLIANCE_POSITION_PCT,
        "detail": f"{new_ticker}: {position_pct:.1%} (compliance limit: {MAX_COMPLIANCE_POSITION_PCT:.0%})",
    }


def check_restricted_list(ticker: str) -> Dict:
    """Check if ticker is on the restricted trading list."""
    restricted = ticker.upper() in RESTRICTED_LIST
    return {
        "passed": not restricted,
        "detail": f"{ticker} {'IS' if restricted else 'is not'} on restricted list",
    }


def check_blackout_period(ticker: str) -> Dict:
    """Check if ticker is in earnings blackout period."""
    in_blackout = ticker.upper() in BLACKOUT_LIST
    return {
        "passed": not in_blackout,
        "detail": f"{ticker} {'IS' if in_blackout else 'is not'} in blackout period",
    }


def format_portfolio_summary(portfolio: Dict, cash: float) -> str:
    """Format portfolio into a readable summary."""
    total_value = calculate_portfolio_value(portfolio)
    sectors = calculate_sector_breakdown(portfolio)
    lines = ["Current Portfolio:"]

    for ticker, holding in portfolio.items():
        price = get_price(ticker)
        value = price * holding["shares"]
        pct = value / total_value * 100 if total_value > 0 else 0
        lines.append(f"  {ticker:5s} {holding['shares']:>4d} shares @ ${price:>8.2f} = ${value:>10,.2f} ({pct:4.1f}%)")

    lines.append(f"\n  Total Value: ${total_value:,.2f}")
    lines.append(f"  Cash Available: ${cash:,.2f}")
    lines.append(f"\n  Sector Breakdown:")
    for sector, pct in sorted(sectors.items(), key=lambda x: -x[1]):
        warning = " ⚠️" if pct > MAX_SECTOR_PCT else ""
        lines.append(f"    {sector:20s} {pct:6.1%}{warning}")

    vol = estimate_portfolio_volatility(portfolio)
    lines.append(f"\n  Estimated Volatility: {vol:.1%}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("💼 Portfolio Data Test\n")
    portfolio = load_portfolio()
    print(format_portfolio_summary(portfolio, 20000))

    print("\n--- Risk checks (adding NVDA, 11 shares) ---")
    print(f"  Sector: {check_sector_limits(portfolio, 'NVDA', 11)}")
    print(f"  Position: {check_position_limits(portfolio, 'NVDA', 11)}")
    print(f"  Correlation: {check_correlation(portfolio, 'NVDA')}")
    print(f"  Volatility: {check_volatility(portfolio, 'NVDA', 11)}")

    print("\n--- Compliance checks (NVDA) ---")
    print(f"  Position limit: {check_compliance_position_limit(portfolio, 'NVDA', 11)}")
    print(f"  Restricted: {check_restricted_list('NVDA')}")
    print(f"  Blackout: {check_blackout_period('NVDA')}")
