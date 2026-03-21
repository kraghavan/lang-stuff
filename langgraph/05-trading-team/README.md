# 💼 Algorithmic Trading Team

A **multi-agent system** where specialist agents have **competing objectives**, can **veto** decisions, and **negotiate alternatives** to reach consensus. All code is **complete and ready to run**.

## 🎯 What It Does

Given a query like *"Should we buy NVDA?"*, a team of agents collaborates:

1. **Portfolio Manager** (supervisor) coordinates the team
2. **Market Agent** proposes a trade based on signals
3. **Risk Agent** checks portfolio limits — can **VETO** if risk too high
4. **Compliance Agent** checks regulations — can **VETO** if non-compliant
5. If vetoed → Market Agent proposes an **alternative** from a different sector
6. Loop until consensus or max rounds reached

This mirrors how **actual hedge fund trading desks** operate.

## 🌟 Why This Is the Capstone Example

This is the **most complex LangGraph pattern** — combining everything from examples 01-04:

| Pattern | Where You Learned It | How It's Used Here |
|---------|---------------------|-------------------|
| State management | Example 01 | `TradingState` with 15+ fields |
| Conditional routing | Example 02 | PM routes to different agents |
| Tool/LLM integration | Example 03 | Market Agent uses Claude for rationale |
| Loop + negotiation | Example 04 | Block → alternative → re-check loop |
| **Multi-agent** | **NEW** | 4 agents with different objectives |

**New concepts:**
- Agents that **disagree** (Market wants to buy, Risk says no)
- **Veto power** (Risk and Compliance can block)
- **Negotiation loops** (try alternatives until consensus)
- **Hub-and-spoke** supervisor pattern

## 📁 Files

```
05-trading-team/
├── README.md              # This file
├── main.py                # Graph, supervisor, routing, entry point
├── agents.py              # Market, Risk, Compliance agent nodes
├── portfolio_data.py      # Portfolio loading, risk calculations
├── market_data.py         # Simulated market signals (17 tickers)
├── data/
│   └── sample_portfolio.csv  # Starting portfolio (tech-heavy)
└── test_trading.py        # 8 tests covering all scenarios
```

## 🚀 Quick Start

```bash
cd langgraph/05-trading-team
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY="your-key-here"

python main.py                          # Default: "Should we buy NVDA?"
python main.py "Should we buy UNH?"     # Healthcare — should approve
python main.py "Find me a good trade"   # Agent picks best opportunity
```

## 🏗️ Architecture

```
START → Portfolio Manager → [route_next_agent]
              ↑                    │
              │         ┌──────────┼──────────┐
              │         ↓          ↓          ↓
              │    Market Agent  Risk Agent  Compliance
              │    (proposes)   (approves/   (approves/
              │                 blocks)      blocks)
              │         │          │          │
              └─────────┴──────────┴──────────┘
                    (all loop back to PM)

              PM → finalize → END
```

### Three Scenarios

**Happy Path** — All approve:
```
PM → Market("BUY UNH") → PM → Risk(✅) → PM → Compliance(✅) → PM → Execute
```

**Conflict** — Risk blocks, alternative works:
```
PM → Market("BUY NVDA") → PM → Risk(🚫 tech overweight)
→ PM → Market("BUY UNH" alternative) → PM → Risk(✅) → PM → Compliance(✅) → Execute
```

**Deadlock** — Multiple blocks, give up:
```
PM → Market("NVDA") → Risk(🚫) → Market("AMD") → Risk(🚫) → Market("QCOM") → Risk(🚫)
→ PM: Max rounds reached → PASS (no trade)
```

---

## 📖 Code Walkthrough

### `portfolio_data.py` — Risk Calculations (Rule-Based)

Hard limits that the Risk and Compliance agents enforce:

| Limit | Value | Checked By |
|-------|-------|-----------|
| Max sector allocation | 40% | Risk Agent |
| Max position size (risk) | 15% | Risk Agent |
| Max position size (compliance) | 10% | Compliance Agent |
| Max portfolio volatility | 25% | Risk Agent |
| Max correlated positions | 3 per sector | Risk Agent |
| Restricted list | META, COIN | Compliance Agent |
| Blackout list | TSLA | Compliance Agent |

These are **pure math** — no LLM involved. Hard limits shouldn't be decided by an LLM.

### `market_data.py` — Simulated Market Universe

17 tickers across 5 sectors, each with price, RSI, momentum, and conviction:

```
Technology:       AAPL, MSFT, NVDA, AMD, QCOM, GOOGL
Financials:       JPM, GS, BAC
Healthcare:       JNJ, UNH, PFE
Consumer Staples: WMT, PG, KO
Energy:           XOM, CVX
```

`find_alternative()` picks the best BUY signal from a non-blocked sector.

### `agents.py` — The Three Specialists

**Market Agent** — Uses Claude (optional) for trade rationale. On retry, proposes from a different sector.

**Risk Agent** — Pure rule-based. Runs 4 checks (sector, position, correlation, volatility). Can VETO.

**Compliance Agent** — Pure rule-based. Runs 3 checks (position limit, restricted list, blackout). Can VETO.

### `main.py` — Portfolio Manager + Graph

The **supervisor pattern**: PM reads state, decides which agent to call next, routes via conditional edges. All agents loop back to PM.

```python
workflow.add_conditional_edges(
    "portfolio_manager",
    route_next_agent,
    {"market": "market_agent", "risk": "risk_agent",
     "compliance": "compliance_agent", "finalize": "finalize"}
)
workflow.add_edge("market_agent", "portfolio_manager")   # Always back to PM
workflow.add_edge("risk_agent", "portfolio_manager")
workflow.add_edge("compliance_agent", "portfolio_manager")
```

### Key: The Negotiation Loop

When Risk blocks, PM increments `negotiation_round`, clears previous assessments, and routes back to Market Agent. Market Agent sees the round > 0 and proposes from a different sector.

```python
# In portfolio_manager:
if not risk_approved:
    state["negotiation_round"] += 1
    state["risk_assessment"] = None      # Clear for re-check
    state["compliance_check"] = None
    state["next_agent"] = "market"       # Ask for alternative
```

---

## 🧪 Testing

```bash
python market_data.py       # See all 17 tickers
python portfolio_data.py    # See portfolio + risk checks
python test_trading.py      # 8 tests covering all scenarios
python main.py              # Full run with Claude
```

### Test Scenarios

| Test | Query | Expected |
|------|-------|----------|
| Happy path | "Buy UNH" | ✅ Execute (healthcare, no conflicts) |
| Risk block | "Buy NVDA" | 🔄 Block → alternative → execute |
| Give up | Concentrated portfolio | ❌ PASS after max rounds |

## 🎯 Challenges

1. **Add a news agent** — Analyze recent headlines before proposing trades
2. **Real prices** — Replace `market_data.py` with Yahoo Finance API calls
3. **Portfolio visualization** — Print a sector pie chart before/after trade
4. **Tax optimization** — Add a tax agent that checks for wash sales
5. **HITL approval** — Add an `interrupt()` before trade execution (combine with Example 04)
6. **Backtesting** — Run the team on historical data and track performance

## ✅ Completion Checklist

- [ ] Ran `python test_trading.py` — all 8 tests pass
- [ ] Ran `python main.py` with NVDA query — saw block → alternative flow
- [ ] Ran `python main.py "Should we buy UNH?"` — saw happy path
- [ ] Understand the supervisor (hub-and-spoke) pattern
- [ ] Understand how agents can VETO and trigger alternatives
- [ ] Understand the negotiation loop (round tracking, state clearing)
- [ ] Understand why risk/compliance are rule-based (not LLM)

## 📚 Resources

- [LangGraph Multi-Agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [Agent Supervisor Pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangGraph Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)

---

**Congratulations! You've completed all 5 LangGraph examples.** You now understand production-grade patterns: state management, conditional routing, tool calling (deep agents), human-in-the-loop, and multi-agent coordination.
