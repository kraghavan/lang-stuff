# 📄 SEC Filing Q&A

A RAG (Retrieval-Augmented Generation) app that lets you ask natural language questions about SEC filings and get accurate, source-cited answers. All code is **complete and ready to run**.

## 🎯 What It Does

1. **Load** — Reads a 10-K filing (sample Apple filing included)
2. **Chunk** — Splits the document into ~1000-char pieces with overlap
3. **Embed** — Converts each chunk into a vector (HuggingFace, runs locally)
4. **Store** — Indexes vectors in FAISS for fast similarity search
5. **Query** — Finds the most relevant chunks for your question
6. **Answer** — Claude generates an answer grounded in the retrieved context

## 🌟 Why LangChain (not LangGraph)?

- ✅ **RAG is LangChain's killer feature** — built-in loaders, splitters, embeddings, vector stores
- ✅ **Single-pass** — retrieve once, answer once
- ❌ No iterative retrieval or conditional branching needed

## 📁 Files

```
03-sec-filing-qa/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── simple_version.py      # Main RAG implementation
├── filing_loader.py       # Document loading and chunking
├── data/
│   └── sample_10k.txt     # Apple 10-K filing (excerpted)
└── examples/
    └── EXAMPLE_OUTPUTS.md # Sample Q&A outputs
```

## 🚀 Quick Start

```bash
cd langchain/03-sec-filing-qa
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python simple_version.py
# Ask: "What was Apple's total revenue?"
# Ask: "What are the main risk factors?"
# Type: quit
```

### Example Session

```
📄 SEC Filing Q&A System
========================================
📂 Loading filing...
✓ Loaded 1 document(s) (14,295 chars)
✓ Split into 18 chunks (avg 858 chars each)

📊 Building vector store...
✓ Created vector store with 18 vectors

Ready! Ask questions about the filing (type 'quit' to exit).

You: What was Apple's total revenue in fiscal 2024?

🔍 Searching filing for relevant sections...

Answer:
  According to the 10-K filing, Apple's total net revenue for
  fiscal year 2024 was $391.0 billion ($391,035 million):
  - Products: $295.0 billion (-1% YoY)
  - Services: $96.0 billion (+13% YoY)
  Sources: Item 7 (MD&A) and Item 8 (Financial Statements)
```

## 🏗️ Architecture

```
INDEXING (one-time):
Filing text → Chunk (RecursiveTextSplitter) → Embed (HuggingFace) → Store (FAISS)

QUERYING (per question):
Question → Embed → Similarity Search → Top-K chunks → Prompt + Claude → Answer
```

### LCEL Implementation

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
answer = rag_chain.invoke("What was Apple's revenue?")
```

The `{"context": ..., "question": ...}` creates a `RunnableParallel`: the retriever and passthrough run simultaneously, then results merge into a dict for the prompt.

---

## 📖 Code Walkthrough

### `filing_loader.py` — Indexing Phase

**`load_filing()`** — Uses `TextLoader` to read `data/sample_10k.txt` into a LangChain `Document` (has `.page_content` and `.metadata`).

**`split_into_chunks()`** — Uses `RecursiveCharacterTextSplitter` with `chunk_size=1000` and `chunk_overlap=200`. Splits at natural boundaries: paragraphs → lines → sentences → words.

- **Why chunk?** Filing is too long to send entirely to Claude. We only need relevant sections.
- **Why overlap?** Prevents losing context at chunk boundaries.

```bash
python filing_loader.py  # See chunk statistics
```

### `simple_version.py` — RAG Pipeline

**`create_vector_store(chunks)`** — Embeds all chunks using `HuggingFaceEmbeddings` (runs locally, ~80MB model, no API key) and stores in FAISS for fast similarity search.

**`create_retriever(vector_store)`** — Wraps FAISS into LangChain's retriever interface: `retriever.invoke("revenue")` → top-4 matching chunks.

**`create_rag_prompt()`** — The critical grounding prompt. Tells Claude to:
- Answer **ONLY** from the provided context
- Say "I don't have that information" when unsure
- Cite specific data points

Without these rules, Claude might hallucinate answers from training data.

**`create_rag_chain(retriever)`** — Composes the full RAG chain. The `RunnableParallel` runs retrieval and question passthrough simultaneously, then feeds both into the prompt.

---

## 🛠️ Key LangChain Concepts

### Embeddings
Convert text to vectors where similar meanings are close together:
```
"Apple's revenue was $391 billion"  → [0.12, -0.34, ...]
"What was Apple's total sales?"     → [0.13, -0.33, ...]  ← Close!
"Risk factors include competition"  → [0.78, 0.23, ...]   ← Far away
```

### Vector Store (FAISS)
Stores all chunk vectors and enables fast nearest-neighbor search. When you query, your question is embedded with the same model and compared to all stored vectors.

### The RAG Chain Pattern
```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | parser
)
```
`RunnablePassthrough()` passes the question through unchanged while the retriever fetches relevant chunks.

---

## 🧪 Testing

| Question | Tests |
|----------|-------|
| "What was Apple's total revenue?" | Simple fact retrieval |
| "What are the main risk factors?" | Multi-point retrieval |
| "How did iPhone sales perform?" | Segment data |
| "How much did Apple return to shareholders?" | Capital allocation |
| "What is Bitcoin's price?" | Out-of-scope (should say "I don't know") |

```bash
python filing_loader.py  # Test chunking
printf "What was Apple's revenue?\nquit\n" | python simple_version.py  # Test RAG
```

---

## 🎯 Challenges

1. **Change chunk size** — Try 500 vs 2000 in `filing_loader.py`. How does Q&A quality change?
2. **Change top-K** — Retrieve 2 vs 8 chunks. When does more context help vs hurt?
3. **Remove the grounding constraint** — Delete "ONLY" from the prompt and ask "What is Bitcoin?" — see what happens
4. **Print retrieved chunks** — Add a print before the LLM call to see what was retrieved
5. **Swap the filing** — Replace `sample_10k.txt` with any company's 10-K text

---

## ✅ Completion Checklist

- [ ] Asked 3+ questions and got grounded answers
- [ ] Verified an answer against the raw `sample_10k.txt`
- [ ] Asked an out-of-scope question and got "I don't have that information"
- [ ] Understand indexing (chunk → embed → store) vs querying (retrieve → generate)
- [ ] Tried at least one challenge

## 📚 Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Text Splitters Guide](https://python.langchain.com/docs/how_to/#text-splitters)
- [Vector Store Integrations](https://python.langchain.com/docs/integrations/vectorstores/)
- [FAISS](https://faiss.ai/)

---

**Next: [04 — Portfolio Report Generator](../04-portfolio-report-generator) — structured output and batch processing →**
