# 💼 Learning Guide: Portfolio Report Generator

A walkthrough of structured output and batch processing in LangChain. All code is **complete and ready to run** — this guide explains how Pydantic models and `chain.batch()` work, and gives you challenges to try.

## Prerequisites

- Completed Examples 01-03 (or understand LCEL, chain composition, and RAG)
- `ANTHROPIC_API_KEY` environment variable set
- Familiarity with Python classes (Pydantic is straightforward)

## How to Use This Guide

1. **Run it first** — `python simple_version.py` (analyzes the sample portfolio)
2. **Read each section** — focus on `with_structured_output()` and `chain.batch()`
3. **Inspect the Pydantic models** — `python portfolio_models.py`
4. **Try the challenges** — modify the portfolio, models, and report format

---

## Why Structured Output Matters

In previous examples, Claude returned raw text. That works for display, but what if you need to:
- Sort holdings by risk level?
- Calculate aggregate portfolio statistics?
- Export analysis to a database or API?
- Programmatically filter for "SELL" recommendations?

You need **structured data**, not prose:

```python
# Previous examples: raw text — hard to process programmatically
result = chain.invoke(...)  # → "Apple is a stable company with low risk..."

# This example: Pydantic objects — typed, validated, easy to process
result = chain.invoke(...)  # → HoldingAnalysis(ticker="AAPL", risk_level="LOW", star_rating=4)
print(result.risk_level)    # → "LOW"  (typed access)
sorted_by_risk = sorted(results, key=lambda r: r.star_rating)  # (easy sorting)
```

---

## Phase 1: Pydantic Models (`portfolio_models.py`)

Open `portfolio_models.py` and follow along.

### Step 1: `HoldingAnalysis` — The Output Schema

This Pydantic model defines **exactly** what Claude must return for each holding:

```python
class HoldingAnalysis(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    outlook: Literal["POSITIVE", "STABLE", "MIXED", "NEGATIVE"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    star_rating: int = Field(ge=1, le=5)
    summary: str = Field(description="2-3 sentence analysis")
    recommendation: Literal["BUY", "HOLD", "SELL", "TRIM"]
    key_strengths: list[str]
    key_risks: list[str]
```

**Key Pydantic features used:**

| Feature | What It Does | Example |
|---------|-------------|---------|
| `Literal[...]` | Claude must pick from these exact values | `"LOW"`, `"MEDIUM"`, `"HIGH"` |
| `Field(ge=1, le=5)` | Validates numeric range | Star rating must be 1-5 |
| `Field(description=...)` | Claude reads this to know what to generate | "2-3 sentence analysis" |
| `list[str]` | A list of strings | `["Services growth", "Cash position"]` |

**Test it:**
```bash
python portfolio_models.py
# Prints the JSON schema Claude will see, plus a test instance
```

**Challenge:** Add a new field `sector: str = Field(description="Company's business sector")` and re-run. Does Claude populate it correctly?

---

### Step 2: `PortfolioSummary` — Portfolio-Level Model

A second model for aggregated portfolio insights. This one is used for the overall assessment, not per-holding analysis.

---

## Phase 2: Data & Analysis (`simple_version.py`)

Open `simple_version.py` and follow along.

### Step 3: `load_portfolio()` — CSV Loading

Reads the sample portfolio from `data/sample_portfolio.csv`:

```csv
ticker,shares,cost_basis
AAPL,100,150.00
MSFT,50,280.00
TSLA,30,200.00
NVDA,25,450.00
JPM,40,140.00
```

**Challenge:** Edit `sample_portfolio.csv` to add `AMZN,20,120.00` and re-run. The new holding will be analyzed automatically.

---

### Step 4: `enrich_holdings()` — Add Financial Data

Adds financial data from the built-in `SAMPLE_FINANCIAL_DATA` dictionary. In a real app, you'd call the SEC EDGAR API here (see Example 01).

---

### Step 5: `create_analysis_chain()` — The Key Concept

**Concept: `with_structured_output()`**

This is the **most important new thing** in this example:

```python
llm = ChatAnthropic(model=MODEL, temperature=0)

# Instead of:
#   chain = prompt | llm | StrOutputParser()     → returns string
# We use:
#   chain = prompt | llm.with_structured_output(HoldingAnalysis)  → returns Pydantic object
```

**What happens under the hood:**
1. LangChain converts `HoldingAnalysis` to a JSON Schema
2. The schema is sent to Claude as a "tool" definition
3. Claude generates a response that exactly matches the schema
4. LangChain parses Claude's response into a Pydantic object
5. You get a typed Python object — no string parsing needed!

**The result:**
```python
result = chain.invoke({"ticker": "AAPL", ...})

# result is a HoldingAnalysis object:
result.ticker        # → "AAPL"
result.risk_level    # → "LOW"
result.star_rating   # → 4
result.key_strengths # → ["Services growth", "Cash position"]

# Convert to dict or JSON easily:
result.model_dump()       # → {"ticker": "AAPL", "risk_level": "LOW", ...}
result.model_dump_json()  # → '{"ticker": "AAPL", ...}'
```

---

### Step 6: `analyze_all_holdings()` — Batch Processing

**Concept: `chain.batch()`**

Instead of analyzing holdings one at a time, batch them:

```python
# Slow: sequential (5 API calls, one after another)
for h in holdings:
    result = chain.invoke(h)

# Fast: batch with concurrency (up to 3 at a time)
results = chain.batch(holdings, config={"max_concurrency": 3})
```

`chain.batch()` returns a list of `HoldingAnalysis` objects — one per input.

**Challenge:** Time the difference between sequential and batch:
```python
import time

# Sequential
start = time.time()
for h in inputs:
    chain.invoke(h)
print(f"Sequential: {time.time() - start:.1f}s")

# Batch
start = time.time()
chain.batch(inputs, config={"max_concurrency": 3})
print(f"Batch: {time.time() - start:.1f}s")
```

---

### Step 7: `generate_report()` — Structured Data → Report

**Why structured output shines here:**

Because each analysis is a Pydantic object, the report generation is pure Python — no string parsing:

```python
# Filter high-risk holdings
high_risk = [a for a in analyses if a.risk_level == "HIGH"]

# Sort by star rating
best_to_worst = sorted(analyses, key=lambda a: a.star_rating, reverse=True)

# Count recommendations
from collections import Counter
rec_counts = Counter(a.recommendation for a in analyses)

# Calculate average rating
avg = sum(a.star_rating for a in analyses) / len(analyses)
```

**Challenge:** Modify the report to sort holdings by star rating (best first) instead of portfolio order.

---

## Deep Dive: Structured Output

### How `with_structured_output()` Works

```
1. You define: HoldingAnalysis(BaseModel) with typed fields
2. LangChain converts to JSON Schema
3. Schema sent to Claude as a tool definition
4. Claude fills in the tool call with matching data
5. LangChain parses tool call → Pydantic object
6. You get: HoldingAnalysis(ticker="AAPL", risk_level="LOW", ...)
```

### Structured Output vs String Parsing

```python
# BAD: Ask for JSON in prompt, hope it's valid, parse manually
result = chain.invoke(...)   # "```json\n{\"ticker\": \"AAPL\"...}\n```"
data = json.loads(...)       # Fragile! What if Claude adds markdown?

# GOOD: Guaranteed schema, typed objects, no parsing
result = structured_chain.invoke(...)  # HoldingAnalysis(ticker="AAPL", ...)
print(result.ticker)                   # Type-safe, validated, clean
```

### When to Use Structured Output

| Use Case | String Output | Structured Output |
|----------|:---:|:---:|
| Display to user | ✅ | ❌ (overkill) |
| Store in database | ❌ | ✅ |
| Feed into next processing step | ❌ | ✅ |
| Aggregate across multiple calls | ❌ | ✅ |
| Sort/filter results | ❌ | ✅ |

---

## Bonus Challenges

1. **Add a field:** Add `estimated_fair_value: str` to `HoldingAnalysis` — does Claude provide reasonable estimates?
2. **Portfolio summary chain:** Create a second chain using `PortfolioSummary` that takes all individual analyses and produces a portfolio-level assessment
3. **Different portfolios:** Create `aggressive_portfolio.csv` and `conservative_portfolio.csv` — compare the reports
4. **Export to JSON:** Add a `--json` flag that outputs all analyses as JSON instead of formatted text
5. **Real data:** Replace `SAMPLE_FINANCIAL_DATA` with calls to `stock_data.py` from Example 01
6. **Sector analysis:** Group holdings by sector (from the analysis) and add a sector breakdown to the report

---

## Completion Checklist

- [ ] Ran `python simple_version.py` and saw the portfolio report
- [ ] Ran `python portfolio_models.py` and saw the JSON schema
- [ ] Understand what `with_structured_output(HoldingAnalysis)` does
- [ ] Understand why `chain.batch()` is faster than a loop
- [ ] Can access typed fields on the result (`result.risk_level`, `result.star_rating`)
- [ ] Understand the difference between string output and structured output
- [ ] Tried at least one bonus challenge

## What's Next?

Congratulations — you've completed all LangChain examples! You now understand:

1. **LCEL basics** (prompts, LLMs, parsers) ← Example 01
2. **Chain composition** (sequential pipelines, RunnablePassthrough) ← Example 02
3. **RAG** (embeddings, vectors, retrieval-augmented generation) ← Example 03
4. **Structured output + batch processing** (Pydantic, chain.batch()) ← Example 04

**Ready for [LangGraph](../../langgraph/)?** LangGraph adds loops, conditional branching, shared state, and multi-agent coordination on top of everything you've learned here.

---

**Concepts Learned:**
- ✅ Pydantic BaseModel for output schemas
- ✅ Field() with descriptions, validators, Literal types
- ✅ `llm.with_structured_output(Model)` — typed LLM responses
- ✅ `chain.batch()` — concurrent processing
- ✅ Programmatic analysis of LLM results (sort, filter, aggregate)
- ✅ Report generation from structured data
