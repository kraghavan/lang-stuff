# Example Outputs — SEC Filing Q&A

These are examples of what the completed RAG Q&A system produces.

---

## Example 1: Simple Fact Retrieval

```
You: What was Apple's total revenue in fiscal 2024?

🔍 Searching filing for relevant sections...

Answer:
  According to the 10-K filing, Apple's total net revenue for
  fiscal year 2024 was $391.0 billion ($391,035 million), an
  increase of 2% compared to fiscal 2023's $383.3 billion.

  The revenue breakdown was:
  - Products: $295.0 billion (-1% YoY)
  - Services: $96.0 billion (+13% YoY)

  Sources: Item 7 (MD&A) and Item 8 (Financial Statements)

────────────────────────────────────────
```

## Example 2: Multi-Point Retrieval

```
You: What are Apple's main risk factors?

🔍 Searching filing for relevant sections...

Answer:
  The 10-K filing identifies several key risk factors in Item 1A:

  1. **Macroeconomic conditions** — Global economic uncertainty
     could cause consumers to defer purchases

  2. **Supply chain concentration** — Manufacturing is primarily
     outsourced to partners in China, India, Japan, South Korea,
     Taiwan, and Vietnam

  3. **Component availability** — Subject to natural disasters,
     geopolitical tensions, and trade restrictions

  4. **Competition** — Substantial competition in all business
     areas from Samsung, Huawei, Google, Microsoft, and others

  5. **Regulatory risk** — EU's Digital Markets Act requires
     allowing alternative app stores and payment systems on iOS

  6. **Foreign exchange** — International operations exposed to
     currency fluctuations

  7. **Litigation** — Various legal proceedings and government
     investigations ongoing

  Sources: Item 1A (Risk Factors)

────────────────────────────────────────
```

## Example 3: Specific Financial Data

```
You: What was the gross margin percentage and how did it change?

🔍 Searching filing for relevant sections...

Answer:
  Apple's gross margin for fiscal 2024 was $180.7 billion,
  representing a gross margin percentage of 46.2%, up from
  44.1% in fiscal 2023.

  By segment:
  - Products gross margin: 36.9% (up from 36.5%)
  - Services gross margin: 74.0% (up from 70.8%)

  The improvement was driven by cost savings and a favorable
  mix shift toward the higher-margin Services business.

  Sources: Item 7 (Gross Margin discussion)

────────────────────────────────────────
```

## Example 4: Segment Performance

```
You: How did Apple perform in China?

🔍 Searching filing for relevant sections...

Answer:
  Greater China segment revenue was $67.0 billion in fiscal
  2024, a decrease of 3% compared to the prior year. This
  was one of only two segments to decline (Japan also fell 2%).

  For context, Apple's other segments grew:
  - Americas: +3%
  - Europe: +7%
  - Rest of Asia Pacific: +4%

  Sources: Item 7 (Segment Performance)

────────────────────────────────────────
```

## Example 5: Out-of-Scope Question

```
You: What is the current stock price of Apple?

🔍 Searching filing for relevant sections...

Answer:
  I don't have that information in the filing. The 10-K filing
  contains historical financial data but does not include
  current stock prices. For real-time stock prices, please
  check a financial data provider like Yahoo Finance.

────────────────────────────────────────
```

## Example 6: Capital Return

```
You: How much did Apple return to shareholders?

🔍 Searching filing for relevant sections...

Answer:
  During fiscal 2024, Apple returned over $110 billion to
  shareholders:

  - Share repurchases: $94.9 billion
  - Dividends and dividend equivalents: $15.2 billion

  The Company generated $118.3 billion in cash from operations
  during the year. Cash, cash equivalents, and marketable
  securities totaled $140.6 billion as of September 28, 2024.

  Sources: Item 7 (Liquidity and Capital Resources)

────────────────────────────────────────
```

---

## What to Notice

1. **Grounded answers** — Every answer cites specific data from the filing
2. **Precise numbers** — The system doesn't approximate; it uses exact figures
3. **Source attribution** — Answers reference specific filing sections
4. **Honest uncertainty** — Out-of-scope questions get a clear "I don't know"
5. **Context-aware** — The retriever finds relevant chunks even with different phrasing
