# 📄 Learning Guide: SEC Filing Q&A (RAG)

A walkthrough of your first Retrieval-Augmented Generation pipeline. All code is **complete and ready to run** — this guide explains the RAG pattern and gives you challenges to experiment with.

## Prerequisites

- Completed Examples [01](../01-stock-summary) and [02](../02-financial-news-analyzer)
- `ANTHROPIC_API_KEY` environment variable set
- Understanding of LCEL and chain composition

## How to Use This Guide

1. **Run it first** — `python simple_version.py`, then ask "What was Apple's total revenue?"
2. **Read each section** — understand the indexing and querying phases
3. **Try different questions** — see how retrieval quality affects answers
4. **Run the challenges** — modify chunk size, top-K, and the prompt

---

## Why RAG Matters

Claude is smart but doesn't know the contents of a specific SEC filing. RAG solves this:

```
Without RAG:
  Q: "What was Apple's revenue in fiscal 2024?"
  A: "Based on my training data..." ← May be outdated or wrong

With RAG:
  Q: "What was Apple's revenue in fiscal 2024?"
  → [Retrieves relevant paragraphs from the actual filing]
  A: "According to the 10-K filing, revenue was $391.0B..." ← Grounded in source
```

RAG is the **most important pattern** in production LLM applications. Master this and you can build document Q&A, customer support bots, internal knowledge bases, and more.

---

## Phase 1: Indexing (`filing_loader.py`)

The indexing phase happens once when the app starts. Open `filing_loader.py`.

### Step 1: `load_filing()` — Document Loading

Uses LangChain's `TextLoader` to read the sample 10-K file into a `Document` object.

```python
loader = TextLoader("data/sample_10k.txt", encoding="utf-8")
documents = loader.load()
# Returns: [Document(page_content="...", metadata={"source": "data/sample_10k.txt"})]
```

A `Document` has two parts:
- `page_content` — the actual text
- `metadata` — info about where it came from

**Test it:**
```bash
python -c "from filing_loader import load_filing; docs = load_filing(); print(f'{len(docs[0].page_content):,} chars')"
```

**Challenge:** Open `data/sample_10k.txt` and skim it. What sections does it contain? (Items 1, 1A, 6, 7, 8)

---

### Step 2: `split_into_chunks()` — Text Splitting

Breaks the long document into smaller, overlapping pieces using `RecursiveCharacterTextSplitter`.

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # Max chars per chunk
    chunk_overlap=200,     # Overlap between adjacent chunks
    separators=["\n\n", "\n", ". ", " ", ""]  # Split at natural boundaries
)
```

**Why chunk?**
- The filing is too long to send entirely to Claude
- We only need the relevant sections for each question
- Smaller chunks = more precise similarity matching

**Why overlap?**
- A relevant sentence might straddle two chunk boundaries
- With 200-char overlap, nothing gets lost at the edges

**Splitting priority:** Paragraphs first (`\n\n`), then lines, then sentences, then words, then characters (last resort).

**Test it:**
```bash
python filing_loader.py
# Shows chunk statistics: count, avg/min/max length, previews
```

**Challenge:** Try changing `chunk_size` to 500 and 2000. How does the number of chunks change? Which produces better Q&A results?

---

## Phase 2: Embedding & Storage (`simple_version.py`)

Open `simple_version.py`. This phase converts text chunks into searchable vectors.

### Step 3: `create_vector_store()` — Embeddings + FAISS

**Concept: Embeddings**

Embeddings convert text into vectors (lists of ~384 numbers) where **similar meanings are close together**:

```
"Apple's revenue was $391 billion"  → [0.12, -0.34, 0.56, ...]
"What was Apple's total sales?"     → [0.13, -0.33, 0.55, ...]  ← Very close!
"Risk factors include competition"  → [0.78, 0.23, -0.11, ...]  ← Far away
```

We use `HuggingFaceEmbeddings` which runs **locally** (no API key needed, ~80MB download on first run).

**Concept: Vector Store (FAISS)**

FAISS (Facebook AI Similarity Search) stores all chunk vectors and enables fast nearest-neighbor search.

```python
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embeddings)
```

**What happens under the hood:**
1. Each chunk's text is converted to a 384-dimensional vector
2. All vectors are indexed in FAISS for fast similarity search
3. When you query, your question is also embedded and compared to all stored vectors

---

### Step 4: `create_retriever()` — Standardized Search Interface

The retriever wraps FAISS's similarity search into LangChain's standard interface:

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
# Usage: docs = retriever.invoke("What was the revenue?")
# Returns: Top 4 most similar Document chunks
```

**Challenge:** Try different `k` values (2, 4, 8). More chunks = more context but also more noise.

---

## Phase 3: RAG Chain (`simple_version.py`)

### Step 5: `create_rag_prompt()` — The Grounding Prompt

This prompt is **critical** — it prevents Claude from making things up:

```python
("system", "Answer ONLY based on the provided context... "
           "If the context doesn't contain the answer, say "
           "'I don't have that information in the filing'")
```

**Why these rules matter:**
- Without "only answer from context" → Claude uses training data (possibly outdated)
- Without "say I don't know" → Claude hallucinates an answer
- Without "cite sections" → Users can't verify the answer

**Challenge:** Remove the "ONLY" constraint from the prompt and ask "What is Bitcoin's price?" Compare the response with and without the constraint.

---

### Step 6: `create_rag_chain()` — The Core Pattern

This is the heart of RAG:

```python
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | parser
)
```

**How it works:**

The `{...}` creates a `RunnableParallel` — two things happen simultaneously:

```
Input: "What was Apple's revenue?"
       │
       ├──► retriever.invoke("What was Apple's revenue?")
       │    → [Doc1, Doc2, Doc3, Doc4]         (4 relevant chunks)
       │    → format_docs                       (join into one string)
       │    → assigned to "context"
       │
       └──► RunnablePassthrough()
            → "What was Apple's revenue?"
            → assigned to "question"

Result: {"context": "relevant chunks...", "question": "What was...?"}
        → prompt formats into messages
        → Claude generates grounded answer
        → parser extracts text
```

**Key insight:** The retriever and passthrough run **in parallel**, then their results merge into a dict that feeds the prompt.

---

### Step 7: `run_qa_session()` — Interactive Q&A

A simple loop: ask questions, get answers, repeat. Type `quit` to exit.

**Good questions to try:**

| Question | Tests |
|----------|-------|
| "What was Apple's total revenue?" | Simple fact retrieval |
| "What are the main risk factors?" | Multi-point retrieval (Item 1A) |
| "How did iPhone sales perform?" | Specific segment data |
| "What was the gross margin percentage?" | Numerical precision |
| "How much did Apple return to shareholders?" | Capital allocation data |
| "What is Bitcoin's price?" | Out-of-scope handling (should say "I don't know") |

---

## Deep Dive: RAG Concepts

### Why Not Just Send the Whole Filing?

| Approach | Pros | Cons |
|----------|------|------|
| Send entire filing | Simple | Too long, expensive, slow |
| Send random excerpts | Cheap | Misses relevant parts |
| **RAG (retrieve relevant)** | **Fast, cheap, accurate** | **Requires setup** |

### Chunk Size Trade-offs

```
Small (200 chars):  Precise retrieval, but may lack context
Large (2000 chars): More context, but retrieves noise too
Sweet spot (800-1200): Good balance ← we use 1000
```

### The Embedding Magic

Embeddings understand **meaning**, not just words:
- "revenue" and "total sales" are close in vector space
- "revenue" and "risk factors" are far apart
- This is why you can ask questions using different words than the document uses

---

## Bonus Challenges

1. **Change chunk size:** Edit `filing_loader.py` to use 500 or 2000. How does Q&A quality change?
2. **Change top-K:** Retrieve 2 vs 8 chunks. When does more context help vs hurt?
3. **Add source citations:** Modify `format_docs()` to include chunk numbers, so Claude can cite "Chunk 3"
4. **Try a different filing:** Replace `sample_10k.txt` with any company's 10-K text (download from SEC EDGAR)
5. **Add chat history:** Modify the prompt to include previous Q&A pairs for follow-up questions
6. **Measure retrieval:** Print the retrieved chunks before sending to Claude — are they actually relevant?

---

## Completion Checklist

- [ ] Ran `python simple_version.py` and asked 3+ questions
- [ ] Verified a factual answer against the raw `sample_10k.txt` file
- [ ] Asked an out-of-scope question and got "I don't have that information"
- [ ] Understand the two phases: indexing (chunk → embed → store) and querying (retrieve → generate)
- [ ] Understand what `RunnablePassthrough()` does in the RAG chain
- [ ] Can explain why the grounding prompt is critical
- [ ] Tried at least one bonus challenge

## What's Next?

**[04 - Portfolio Report Generator](../04-portfolio-report-generator)** — Learn structured output (Pydantic models) and batch processing, the most production-relevant LangChain features.

---

**Concepts Learned:**
- ✅ Document Loaders (TextLoader)
- ✅ Text Splitters (RecursiveCharacterTextSplitter)
- ✅ Embeddings (HuggingFaceEmbeddings)
- ✅ Vector Stores (FAISS)
- ✅ Retrievers (vector_store.as_retriever())
- ✅ RAG Chain (retriever | format_docs + RunnablePassthrough)
- ✅ Grounded Q&A (answer from context only)
