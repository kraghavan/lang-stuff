# 📰 Financial News Analyzer

A multi-step LangChain pipeline that summarizes news, analyzes sentiment, and generates an investment brief — using sequential chain composition. All code is **complete and ready to run**.

## 🎯 What It Does

1. **Fetch** — Gets recent news headlines for a company (sample dataset)
2. **Summarize** — Condenses headlines into key themes (LLM call #1)
3. **Sentiment** — Rates market sentiment: bullish/bearish/neutral (LLM call #2)
4. **Brief** — Generates a professional investment brief (LLM call #3)

## 🌟 Why LangChain (not LangGraph)?

- ✅ **Sequential processing** — Each step feeds into the next
- ✅ **Multiple prompts** — Different prompts for different tasks
- ✅ **Chain composition** — `RunnablePassthrough.assign()` accumulates data
- ❌ No conditional branching — every ticker goes through the same pipeline

## 📁 Files

```
02-financial-news-analyzer/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── simple_version.py      # Main 3-step pipeline
├── news_data.py           # Sample news dataset
└── examples/
    └── EXAMPLE_OUTPUTS.md # Sample outputs for reference
```

## 🚀 Quick Start

```bash
cd langchain/02-financial-news-analyzer
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python simple_version.py
# Enter: NVDA
```

### Example Output

```
📰 Financial News Analyzer
========================================
Enter a stock ticker (e.g., AAPL, TSLA, NVDA): NVDA

📥 Loading news for NVDA...
✓ Found 5 recent headlines

🔗 Running analysis pipeline...
  Step 1/3: Summarizing headlines...
  ✓ All steps complete

════════════════════════════════════════════════════════
           NVDA — INVESTMENT BRIEF
════════════════════════════════════════════════════════
📰 News Summary:
  NVIDIA dominates the AI chip market with record data
  center revenue and expanding cloud provider partnerships.

📊 Sentiment: BULLISH (85% confidence)
  • Strong earnings beat, data center revenue +154% YoY
  • Concerns: elevated valuation, export restrictions

💼 Action: HOLD existing, ADD on pullbacks below $120.
════════════════════════════════════════════════════════
```

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  News Data   │ ──► │  Summarize   │ ──► │  Sentiment   │ ──► │  Investment  │
│  (headlines) │     │  Chain       │     │  Chain       │     │  Brief Chain │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
  news_data.py        Prompt + LLM         Prompt + LLM         Prompt + LLM
```

### Data Flow with `RunnablePassthrough.assign()`

```
INPUT:   {"ticker": "NVDA", "company_name": "NVIDIA", "headlines": "1. Reuters..."}
            │
STEP 1:  assign(summary=summarize_chain)
            │  → adds "summary" to dict, keeps everything else
            ▼
         {"ticker": "NVDA", ..., "headlines": "...", "summary": "AI demand surging..."}
            │
STEP 2:  assign(sentiment=sentiment_chain)
            │  → adds "sentiment", keeps everything
            ▼
         {"ticker": "NVDA", ..., "summary": "...", "sentiment": "BULLISH (85%)..."}
            │
STEP 3:  brief_chain
            │  → consumes all fields, returns final string
            ▼
OUTPUT:  "NVIDIA's dominance in AI accelerators positions it as..."
```

---

## 📖 Code Walkthrough

### `news_data.py` — Sample Headlines

Curated headlines for NVDA, TSLA, AAPL, MSFT, and JPM — each with different sentiment profiles:

| Ticker | Expected Sentiment | Why |
|--------|-------------------|-----|
| NVDA | BULLISH | Record revenue, AI demand |
| TSLA | MIXED | Deliveries up, margins down |
| AAPL | SLIGHTLY BULLISH | Steady services growth |

`format_headlines()` converts them to a numbered list with source and date for Claude.

```bash
python news_data.py  # See all available headlines
```

### `simple_version.py` — The 3-Step Pipeline

**`create_summarize_chain()`** — Headlines → thematic summary. Input: `{headlines}`.

**`create_sentiment_chain()`** — Summary → sentiment rating. Input: `{summary}`. Note: this receives the *output* of the previous chain, not the original headlines.

**`create_brief_chain()`** — All data → investment brief. Input: `{ticker}`, `{company_name}`, `{summary}`, `{sentiment}`. Uses data from the original input AND both previous steps.

**`create_analysis_pipeline()`** — The key function. Composes all 3 chains:

```python
pipeline = (
    RunnablePassthrough.assign(summary=summarize)       # Step 1: + summary
    | RunnablePassthrough.assign(sentiment=sentiment)    # Step 2: + sentiment
    | brief                                              # Step 3: → final string
)
```

---

## 🛠️ Key LangChain Concept: `RunnablePassthrough.assign()`

This is the **most important new concept** in this example. It runs a chain and **adds** the result to the existing data — without losing any previous fields.

**Without `assign()` (broken):**
```python
chain = summarize | sentiment | brief
# ❌ After summarize, the ticker is lost!
```

**With `assign()` (correct):**
```python
chain = (
    RunnablePassthrough.assign(summary=summarize)   # Keeps everything + adds summary
    | RunnablePassthrough.assign(sentiment=sentiment) # Keeps everything + adds sentiment
    | brief                                           # Has ALL fields available
)
```

---

## 🧪 Testing

```bash
python news_data.py                    # Test data loading
echo "NVDA" | python simple_version.py  # Bullish result
echo "TSLA" | python simple_version.py  # Mixed result
echo "AAPL" | python simple_version.py  # Stable result
```

---

## 🎯 Challenges

1. **Add a 4th step** — Insert a "risk assessment" chain between sentiment and brief
2. **Add a new ticker** — Create headlines for AMZN or META in `news_data.py`
3. **Debug the pipeline** — Add `RunnableLambda(lambda d: print(d.keys()) or d)` between steps to see the data accumulate
4. **Try different models** — Compare `claude-haiku-4-5-20251001` (fast) vs `claude-sonnet-4-5-20250929` (better)
5. **Use `RunnableParallel`** — Run summarize and sentiment simultaneously (they could be independent if both take headlines)

---

## ✅ Completion Checklist

- [ ] Ran with NVDA (bullish) and TSLA (mixed) — compared outputs
- [ ] Understand `RunnablePassthrough.assign()` — how data accumulates
- [ ] Understand why `assign()` is needed vs plain chaining
- [ ] Tried at least one challenge

## 📚 Resources

- [LCEL Chaining Guide](https://python.langchain.com/docs/how_to/sequence/)
- [RunnablePassthrough](https://python.langchain.com/docs/how_to/passthrough/)
- [RunnableParallel](https://python.langchain.com/docs/how_to/parallel/)

---

**Next: [03 — SEC Filing Q&A](../03-sec-filing-qa) — learn RAG (Retrieval-Augmented Generation) →**
