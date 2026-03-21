"""
Trading Team Agents — Market, Risk, and Compliance Specialists

Each agent is a node function that reads/writes to shared TradingState.

- Market Agent: Proposes trades, suggests alternatives when blocked
- Risk Agent: Rule-based risk checks (sector, position, correlation, volatility)
- Compliance Agent: Rule-based compliance checks (limits, restricted list, blackout)

Usage:
    from agents import market_analysis_agent, risk_management_agent, compliance_agent
"""

import os
from typing import TYPE_CHECKING

from market_data import get_market_data, find_alternative, extract_ticker_from_query, get_price, get_sector
from portfolio_data import (
    calculate_portfolio_value, calculate_shares_to_buy,
    check_sector_limits, check_position_limits, check_correlation, check_volatility,
    check_compliance_position_limit, check_restricted_list, check_blackout_period,
)

if TYPE_CHECKING:
    from main import TradingState


# ═══════════════════════════════════════════════
# Market Analysis Agent (LLM-powered)
#
# First call: Analyzes the user's query and proposes a trade.
# Retry call: Previous suggestion was blocked — proposes an
#             alternative from a different sector.
# ═══════════════════════════════════════════════

def market_analysis_agent(state: "TradingState") -> "TradingState":
    """
    Analyze market conditions and propose trades.

    On first call (negotiation_round == 0): analyze user query.
    On retry (negotiation_round > 0): propose alternative from different sector.
    """
    round_num = state["negotiation_round"]

    if round_num == 0:
        # First suggestion — analyze user query
        ticker = extract_ticker_from_query(state["user_query"])

        if not ticker:
            # No ticker in query — find best opportunity
            from market_data import MARKET_UNIVERSE
            # Pick highest conviction BUY
            buys = [(t, d) for t, d in MARKET_UNIVERSE.items() if d["signal"] == "BUY"]
            buys.sort(key=lambda x: {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x[1]["conviction"], 0), reverse=True)
            if buys:
                ticker = buys[0][0]
            else:
                state["market_analysis"] = {"ticker": None, "signal": "HOLD", "conviction": "LOW", "rationale": "No strong BUY signals found"}
                return state

        data = get_market_data(ticker)
        if not data:
            state["market_analysis"] = {"ticker": ticker, "signal": "HOLD", "conviction": "LOW", "rationale": f"No market data available for {ticker}"}
            return state

        # Calculate suggested shares
        price = data["price"]
        portfolio_value = calculate_portfolio_value(state["portfolio"])
        shares = calculate_shares_to_buy(state["cash_available"], price, portfolio_value)

        # Use LLM for analysis rationale if available
        rationale = _generate_rationale(ticker, data, state)

        state["market_analysis"] = {
            "ticker": ticker,
            "signal": data["signal"],
            "conviction": data["conviction"],
            "price": price,
            "suggested_shares": shares,
            "suggested_value": round(price * shares, 2),
            "sector": data["sector"],
            "rationale": rationale,
        }

        print(f"\n  🔍 Market Agent: {data['signal']} {ticker}")
        print(f"     Conviction: {data['conviction']}")
        print(f"     Shares: {shares} @ ${price:.2f} = ${price * shares:,.2f}")
        print(f"     Sector: {data['sector']}")

    else:
        # Alternative suggestion — previous was blocked
        blocked = state.get("alternative_suggestions", [])
        # Collect sectors to avoid from risk assessment
        blocked_sectors = []
        if state.get("risk_assessment") and not state["risk_assessment"].get("approved", True):
            failed = state["risk_assessment"].get("failed", [])
            if "sector_concentration" in failed:
                # Get the sector that was over-limit
                sector_info = state["risk_assessment"].get("checks", {}).get("sector_concentration", {})
                blocked_sector = sector_info.get("sector", "")
                if blocked_sector:
                    blocked_sectors.append(blocked_sector)

        # Also exclude sectors of all previously blocked tickers
        for t in blocked:
            s = get_sector(t)
            if s and s not in blocked_sectors:
                blocked_sectors.append(s)

        # Find alternative
        existing_tickers = list(state["portfolio"].keys()) + blocked
        alt = find_alternative(
            exclude_tickers=existing_tickers,
            exclude_sectors=blocked_sectors,
        )

        if not alt:
            state["market_analysis"] = {
                "ticker": None,
                "signal": "HOLD",
                "conviction": "LOW",
                "rationale": "No suitable alternatives found outside blocked sectors",
            }
            print(f"\n  🔍 Market Agent: No alternatives found")
            return state

        ticker = alt["ticker"]
        price = alt["price"]
        portfolio_value = calculate_portfolio_value(state["portfolio"])
        shares = calculate_shares_to_buy(state["cash_available"], price, portfolio_value)

        state["market_analysis"] = {
            "ticker": ticker,
            "signal": alt["signal"],
            "conviction": alt["conviction"],
            "price": price,
            "suggested_shares": shares,
            "suggested_value": round(price * shares, 2),
            "sector": alt["sector"],
            "rationale": f"Alternative: {ticker} ({alt['sector']}) for diversification",
        }
        state["alternative_suggestions"].append(ticker)

        print(f"\n  🔍 Market Agent (Alternative #{round_num}): {alt['signal']} {ticker}")
        print(f"     Sector: {alt['sector']} (diversification)")
        print(f"     Shares: {shares} @ ${price:.2f} = ${price * shares:,.2f}")

    return state


def _generate_rationale(ticker: str, data: dict, state: "TradingState") -> str:
    """Generate analysis rationale using LLM if available, else rule-based."""
    try:
        from langchain_anthropic import ChatAnthropic

        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("No API key")

        llm = ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            temperature=0, max_tokens=200,
        )
        prompt = (
            f"In 2 sentences, explain why {ticker} is a {data['signal']} at ${data['price']:.2f}. "
            f"RSI is {data['rsi']}, momentum is {data['momentum']}. Be concise and data-driven."
        )
        response = llm.invoke(prompt)
        return response.content if isinstance(response.content, str) else str(response.content)
    except Exception:
        # Fallback to rule-based rationale
        reasons = []
        if data["rsi"] < 30:
            reasons.append("oversold (RSI < 30)")
        elif data["rsi"] > 70:
            reasons.append("overbought (RSI > 70)")
        if data["momentum"] in ("bullish", "strong_bullish"):
            reasons.append("positive momentum")
        elif data["momentum"] == "oversold":
            reasons.append("oversold with reversal potential")
        if not reasons:
            reasons.append(f"moderate signals (RSI: {data['rsi']})")
        return f"{ticker} shows {data['signal']} signal: {', '.join(reasons)}."


# ═══════════════════════════════════════════════
# Risk Management Agent (Rule-based)
#
# Pure deterministic checks — no LLM.
# Can VETO (block) trades that exceed risk limits.
# ═══════════════════════════════════════════════

def risk_management_agent(state: "TradingState") -> "TradingState":
    """
    Evaluate portfolio risk and approve/block the proposed trade.

    Checks: sector concentration, position size, correlation, volatility.
    """
    analysis = state["market_analysis"]
    ticker = analysis.get("ticker")

    if not ticker:
        state["risk_assessment"] = {"approved": False, "failed": ["no_ticker"], "checks": {}, "comment": "No ticker proposed"}
        print(f"\n  ⚠️  Risk Agent: No ticker to evaluate")
        return state

    shares = analysis.get("suggested_shares", 0)
    portfolio = state["portfolio"]

    # Run all risk checks
    checks = {
        "sector_concentration": check_sector_limits(portfolio, ticker, shares),
        "position_size": check_position_limits(portfolio, ticker, shares),
        "correlation": check_correlation(portfolio, ticker),
        "volatility": check_volatility(portfolio, ticker, shares),
    }

    failed = [name for name, check in checks.items() if not check["passed"]]
    all_passed = len(failed) == 0

    state["risk_assessment"] = {
        "approved": all_passed,
        "checks": checks,
        "failed": failed,
        "comment": "All risk metrics within limits" if all_passed else f"Blocked: {', '.join(failed)}",
    }

    if all_passed:
        print(f"\n  ✅ Risk Agent: APPROVED")
        for name, check in checks.items():
            print(f"     ✓ {check['detail']}")
    else:
        print(f"\n  🚫 Risk Agent: BLOCKED")
        for name, check in checks.items():
            icon = "✓" if check["passed"] else "✗"
            print(f"     {icon} {check['detail']}")

    return state


# ═══════════════════════════════════════════════
# Compliance Agent (Rule-based)
#
# Pure deterministic checks — no LLM.
# Can VETO (block) trades that violate regulations.
# ═══════════════════════════════════════════════

def compliance_agent(state: "TradingState") -> "TradingState":
    """
    Ensure regulatory compliance for the proposed trade.

    Checks: position size limits, restricted list, blackout periods.
    """
    analysis = state["market_analysis"]
    ticker = analysis.get("ticker")

    if not ticker:
        state["compliance_check"] = {"approved": False, "failed": ["no_ticker"], "checks": {}, "comment": "No ticker to check"}
        print(f"\n  ⚠️  Compliance Agent: No ticker to evaluate")
        return state

    shares = analysis.get("suggested_shares", 0)
    portfolio = state["portfolio"]

    checks = {
        "position_size_limit": check_compliance_position_limit(portfolio, ticker, shares),
        "restricted_list": check_restricted_list(ticker),
        "blackout_period": check_blackout_period(ticker),
    }

    failed = [name for name, check in checks.items() if not check["passed"]]
    all_passed = len(failed) == 0

    state["compliance_check"] = {
        "approved": all_passed,
        "checks": checks,
        "failed": failed,
        "comment": "Trade complies with all regulations" if all_passed else f"Violation: {', '.join(failed)}",
    }

    if all_passed:
        print(f"\n  ✅ Compliance Agent: APPROVED")
        for name, check in checks.items():
            print(f"     ✓ {check['detail']}")
    else:
        print(f"\n  🚫 Compliance Agent: BLOCKED")
        for name, check in checks.items():
            icon = "✓" if check["passed"] else "✗"
            print(f"     {icon} {check['detail']}")

    return state
