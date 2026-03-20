# 📰 Learning Guide: Financial News Analyzer

A walkthrough of a multi-step LangChain pipeline. All code is **complete and ready to run** — this guide explains how the sequential chain composition works and gives you challenges to try.

## Prerequisites

- Completed [01-Stock Summary](../01-stock-summary) (or understand basic LCEL)
- `ANTHROPIC_API_KEY` environment variable set
- Understanding of `prompt | llm | parser` pattern

## How to Use This Guide

1. **Run the code first** — `python simple_version.py`, enter `NVDA`
2. **Read each section below** — focus on the new concept: `RunnablePassthrough.assign()`
3. **Try the challenges** to deepen understanding
4. **Compare outputs** across different tickers (NVDA vs TSLA vs AAPL)

---

## Phase 1: Data Layer (`news_data.py`)

Open `news_data.py` and follow along.

### Step 1: The News Database

Instead of calling a paid news API, we use curated sample headlines. Each ticker has 5 headlines with different sentiment signals:

| Ticker | Expected Sentiment | Why |
|--------|-------------------|-----|
| NVDA | BULLISH | Record revenue, AI demand, new products |
| TSLA | MIXED | Record deliveries but margin compression |
| AAPL | SLIGHTLY BULLISH | Steady services growth, no drama |
| MSFT | BULLISH | Cloud + AI leadership |
| JPM | NEUTRAL | Record profit but rate headwinds coming |

**Challenge:** Add headlines for a new ticker (e.g., `AMZN` or `META`). Include a mix of positive and negative news.

### Step 2: `format_headlines()`

Converts the headline list into a numbered, prompt-ready string:
```
1. [Reuters, 2025-02-21] NVIDIA Reports Record Q4 Revenue of $22.1B
2. [Bloomberg, 2025-02-20] AI Chip Demand Surges...
```

**Why include source and date?** It gives Claude context about credibility and timeliness.

**Test it:**
```bash
python news_data.py
# Prints headlines for NVDA, AAPL, TSLA
```

---

## Phase 2: The 3-Step Pipeline (`simple_version.py`)

Open `simple_version.py` and follow along. This is where the new concepts live.

### Step 3: Summarize Chain

**What it does:** Takes raw headlines → produces a thematic summary

```python
summarize_chain = summarize_prompt | llm | StrOutputParser()
```

This works exactly like Example 01 — single prompt, single LLM call. Nothing new yet.

**Key detail:** The input variable is `{headlines}` — the formatted headline string.

---

### Step 4: Sentiment Chain

**What it does:** Takes the summary from Step 3 → rates sentiment

```python
sentiment_chain = sentiment_prompt | llm | StrOutputParser()
```

**Key difference:** The input variable is `{summary}`, NOT `{headlines}`. This chain receives the **output** of the summarize chain, not the original input.

**How does it get the summary?** That's where `RunnablePassthrough.assign()` comes in — see Step 6.

---

### Step 5: Brief Chain

**What it does:** Takes ALL accumulated data → produces investment brief

This chain receives 4 variables: `{ticker}`, `{company_name}`, `{summary}`, `{sentiment}`. Two come from the original input, two from previous steps.

---

### Step 6: `create_analysis_pipeline()` — The Key Concept

**Concept: RunnablePassthrough.assign()**

This is the **most important thing** in this example. It's how you pass data between chain steps.

```python
pipeline = (
    RunnablePassthrough.assign(summary=summarize)       # Step 1
    | RunnablePassthrough.assign(sentiment=sentiment)    # Step 2
    | brief                                              # Step 3
)
```

**How data flows through the pipeline:**

```
INPUT:   {"ticker": "NVDA", "company_name": "NVIDIA Corp", "headlines": "1. Reuters..."}

STEP 1:  RunnablePassthrough.assign(summary=summarize)
         → Runs summarize chain on the input
         → ADDS "summary" to the dict, keeps everything else
         → {"ticker": "NVDA", "company_name": "...", "headlines": "...", "summary": "Key themes: AI..."}

STEP 2:  RunnablePassthrough.assign(sentiment=sentiment)
         → Runs sentiment chain (uses "summary" from step 1)
         → ADDS "sentiment" to the dict
         → {"ticker": "NVDA", ..., "summary": "...", "sentiment": "BULLISH (85%)..."}

STEP 3:  brief
         → Runs brief chain with ALL accumulated fields
         → Returns final string (not a dict)
         → "NVIDIA's dominance in AI accelerators..."
```

**The key insight:** `assign()` keeps all existing data and adds new fields. Without it, you'd lose the original ticker/company_name after step 1.

**Challenge:** Add a `print()` after each step to see the intermediate data:
```python
# In create_analysis_pipeline(), try adding debug steps:
from langchain_core.runnables import RunnableLambda

def debug_print(data):
    print(f"DEBUG: Keys = {list(data.keys())}")
    return data

pipeline = (
    RunnablePassthrough.assign(summary=summarize)
    | RunnableLambda(debug_print)   # See what's in the dict after step 1
    | RunnablePassthrough.assign(sentiment=sentiment)
    | RunnableLambda(debug_print)   # See what's in the dict after step 2
    | brief
)
```

---

### Step 7: `analyze_news()` — Putting It Together

This function:
1. Loads news for the ticker
2. Formats headlines into a prompt-ready string
3. Creates the pipeline and invokes it
4. Returns the final brief

**Test it:**
```bash
python simple_version.py  # Enter: NVDA → should be bullish
python simple_version.py  # Enter: TSLA → should be mixed
```

---

## Deep Dive: RunnablePassthrough

### The Problem It Solves

Without `RunnablePassthrough`, data gets lost between steps:

```python
# BROKEN: After summarize runs, the ticker is gone!
chain = summarize | sentiment | brief
# ❌ brief_chain can't access {ticker} — it was consumed by summarize

# WORKING: Data accumulates at each step
chain = (
    RunnablePassthrough.assign(summary=summarize)  # Keeps ticker + adds summary
    | RunnablePassthrough.assign(sentiment=sentiment)  # Keeps everything + adds sentiment
    | brief  # Has access to ticker, summary, and sentiment
)
```

### Visual Comparison

```
WITHOUT assign():          WITH assign():
{ticker, headlines}        {ticker, headlines}
      │                          │
      ▼                          ▼
  [summarize]              assign(summary=summarize)
      │                          │
      ▼                          ▼
"summary text"             {ticker, headlines, summary}  ← everything kept!
      │                          │
      ▼                          ▼
  [sentiment]              assign(sentiment=sentiment)
      │                          │
      ▼                          ▼
"BULLISH..."               {ticker, headlines, summary, sentiment}
      │                          │
  ❌ Lost ticker!                ▼
                            [brief]  ← has ALL the data it needs
```

---

## Bonus Challenges

1. **Add a 4th step:** Create a "risk assessment" chain between sentiment and brief
2. **Use RunnableParallel:** Run summarize and sentiment simultaneously (they don't depend on each other if you feed both headlines)
3. **Add streaming:** Use `pipeline.stream()` to watch the final brief generate token by token
4. **Test different models:** Try `claude-haiku-4-5-20251001` (faster, cheaper) vs `claude-sonnet-4-5-20250929` — compare quality
5. **Add your own ticker:** Create headlines for a company you follow and add them to `NEWS_DATABASE`

---

## Completion Checklist

- [ ] Ran `python simple_version.py` with NVDA successfully
- [ ] Ran with TSLA and observed different sentiment
- [ ] Understand what `RunnablePassthrough.assign()` does
- [ ] Understand how data accumulates through the pipeline
- [ ] Can explain why `assign()` is needed (vs plain chaining)
- [ ] Tried at least one bonus challenge

## What's Next?

**[03 - SEC Filing Q&A](../03-sec-filing-qa)** — Learn Retrieval-Augmented Generation (RAG), the most important pattern in real-world LLM applications.

---

**Concepts Learned:**
- ✅ Multiple PromptTemplates for different tasks
- ✅ RunnablePassthrough.assign() for data accumulation
- ✅ Sequential chain composition
- ✅ Multi-step LCEL pipelines
- ✅ Debugging chains step by step
