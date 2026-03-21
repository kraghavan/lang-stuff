"""
Portfolio Models — Pydantic Output Schemas

Defines the structured output models that Claude will return.
These models enforce that every LLM response has exactly the
right fields, types, and constraints.

Key Pydantic Concepts:
- BaseModel: Base class for all models
- Field(): Adds descriptions, validators, and defaults
- Literal[]: Constrains to specific allowed values
- ge/le: Greater-than-or-equal / less-than-or-equal validators

Usage:
    from portfolio_models import HoldingAnalysis, PortfolioSummary

    # Claude returns these as typed objects:
    analysis = chain.invoke(data)  # → HoldingAnalysis(...)
    print(analysis.risk_level)     # → "LOW"
    print(analysis.star_rating)    # → 4
"""

from pydantic import BaseModel, Field
from typing import Literal


class HoldingAnalysis(BaseModel):
    """
    Structured analysis of a single portfolio holding.

    Claude returns instances of this model, ensuring every response
    has exactly these fields with correct types and constraints.

    Example:
        HoldingAnalysis(
            ticker="AAPL",
            company_name="Apple Inc.",
            outlook="STABLE",
            risk_level="LOW",
            star_rating=4,
            summary="Strong ecosystem moat with industry-leading margins...",
            recommendation="HOLD",
            key_strengths=["Services revenue growth", "Massive cash position"],
            key_risks=["China market softness"]
        )
    """
    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL)")

    company_name: str = Field(description="Full company name")

    outlook: Literal["POSITIVE", "STABLE", "MIXED", "NEGATIVE"] = Field(
        description="Forward-looking business outlook based on fundamentals and trends"
    )

    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Current risk assessment. LOW=stable blue-chip, MEDIUM=some concerns, HIGH=significant risks"
    )

    star_rating: int = Field(
        ge=1, le=5,
        description="Overall quality rating: 1=poor, 2=below average, 3=average, 4=good, 5=excellent"
    )

    summary: str = Field(
        description="2-3 sentence concise analysis of the holding's current position and prospects"
    )

    recommendation: Literal["BUY", "HOLD", "SELL", "TRIM"] = Field(
        description="Recommended action. BUY=increase position, HOLD=maintain, TRIM=reduce, SELL=exit"
    )

    key_strengths: list[str] = Field(
        description="Top 2-3 strengths or competitive advantages"
    )

    key_risks: list[str] = Field(
        description="Top 1-2 risks or concerns to monitor"
    )


class PortfolioSummary(BaseModel):
    """
    Aggregated portfolio-level summary and recommendations.

    Generated after all individual holdings are analyzed.
    Provides portfolio-wide insights and action items.

    Example:
        PortfolioSummary(
            total_holdings=5,
            overall_risk="MEDIUM",
            sector_concentration="Heavily concentrated in Technology (80%)",
            top_recommendation="Diversify into Healthcare and Consumer Staples",
            action_items=["Trim NVDA position after 95% gain", ...]
        )
    """
    total_holdings: int = Field(description="Number of holdings in the portfolio")

    overall_risk: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Portfolio-wide risk level considering diversification and individual risks"
    )

    sector_concentration: str = Field(
        description="Assessment of sector diversification (e.g., 'Heavy tech concentration')"
    )

    top_recommendation: str = Field(
        description="Single most important recommendation for improving the portfolio"
    )

    action_items: list[str] = Field(
        description="3-5 specific, actionable items for portfolio improvement"
    )


# ═══════════════════════════════════════════════
# Test the models
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    import json

    print("💼 Testing Portfolio Models")
    print("=" * 40)

    # Print the JSON schema (this is what Claude sees)
    print("\n📋 HoldingAnalysis Schema:")
    schema = HoldingAnalysis.model_json_schema()
    print(json.dumps(schema, indent=2))

    print("\n📋 PortfolioSummary Schema:")
    schema = PortfolioSummary.model_json_schema()
    print(json.dumps(schema, indent=2))

    # Test creating an instance
    print("\n🧪 Test Instance:")
    test = HoldingAnalysis(
        ticker="AAPL",
        company_name="Apple Inc.",
        outlook="STABLE",
        risk_level="LOW",
        star_rating=4,
        summary="Strong ecosystem with industry-leading margins.",
        recommendation="HOLD",
        key_strengths=["Services growth", "Cash position"],
        key_risks=["China market"]
    )
    print(f"  ✓ Created: {test.ticker} — {test.outlook} ({test.risk_level} risk, {'⭐' * test.star_rating})")
    print(f"  ✓ JSON: {test.model_dump_json()[:100]}...")
