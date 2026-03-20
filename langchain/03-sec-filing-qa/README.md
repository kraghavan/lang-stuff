# 📄 SEC Filing Q&A

A Retrieval-Augmented Generation (RAG) application that lets you ask natural language questions about SEC financial filings and get accurate, source-cited answers.

## 🎯 What It Does

Turns dense SEC filings into a conversational Q&A system:

1. **Load** — Reads a 10-K or 10-Q filing (text format, included as sample data)
2. **Chunk** — Splits the long document into manageable pieces
3. **Embed** — Converts each chunk into a vector representation
4. **Store** — Saves vectors in an in-memory vector store
5. **Query** — Finds the most relevant chunks for your question
6. **Answer** — Claude generates an answer grounded in the retrieved context

## 🌟 Why LangChain?

RAG is LangChain's **killer feature** — the pattern it's most known for:

- ✅ **Document loading** — Built-in loaders for many file types
- ✅ **Text splitting** — Smart chunking that preserves context
- ✅ **Embeddings** — Convert text to vectors for similarity search
- ✅ **Vector stores** — In-memory and persistent vector databases
- ✅ **Retrieval chains** — Combine retrieval + generation in one chain

**Why NOT LangGraph?**
- ❌ No loops needed — retrieve once, answer once
- ❌ No conditional branching — same flow for every question
- ❌ No multi-agent coordination — single retriever + single generator

**When WOULD you use LangGraph for RAG?**
- If you need iterative retrieval ("that wasn't enough, search again with different terms")
- If you need to route queries to different document stores
- If you need human-in-the-loop verification of answers

## 📁 Files in This Example

```
03-sec-filing-qa/
├── README.md                # This file
├── LEARNING_GUIDE.md        # Step-by-step TODO tutorial
├── requirements.txt         # Python dependencies
├── simple_version.py        # Main RAG implementation (has TODOs)
├── filing_loader.py         # Document loading and chunking
├── data/
│   └── sample_10k.txt       # Sample 10-K filing (Apple, excerpted)
└── examples/
    └── EXAMPLE_OUTPUTS.md   # Sample Q&A outputs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd langchain/03-sec-filing-qa
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run It

```bash
python simple_version.py
```

### Example Session

```
📄 SEC Filing Q&A System
========================================

Loading Apple Inc. 10-K filing...
✓ Loaded 45 pages of filing text
✓ Split into 128 chunks (avg ~500 tokens each)
✓ Created embeddings and vector store

Ready! Ask questions about the filing (type 'quit' to exit).

You: What was Apple's total revenue last year?

🔍 Searching filing for relevant sections...
✓ Found 4 relevant chunks

🤖 Generating answer...

Answer:
  According to the 10-K filing, Apple's total net revenue
  for fiscal year 2024 was $391.0 billion, compared to
  $383.3 billion in the prior year, representing a 2%
  year-over-year increase.

  Sources:
  • Item 6: Selected Financial Data (p. 23)
  • Item 7: Revenue discussion (p. 28)

────────────────────────────────────────

You: What are the main risk factors?

🔍 Searching filing for relevant sections...
✓ Found 4 relevant chunks

🤖 Generating answer...

Answer:
  The 10-K filing identifies several key risk factors:

  1. **Macroeconomic conditions** — Global economic
     uncertainty could reduce consumer spending
  2. **Supply chain** — Reliance on single-source
     components and concentration in specific regions
  3. **Competition** — Intense competition in all
     product categories
  4. **Regulatory** — Increasing regulation globally,
     particularly in the EU (Digital Markets Act)
  5. **Foreign exchange** — Significant international
     revenue exposed to currency fluctuations

  Sources:
  • Item 1A: Risk Factors (pp. 8-18)

────────────────────────────────────────

You: quit
Goodbye!
```

## 🏗️ Architecture

### RAG Pipeline

```
                    ┌─────────────────────────────────────────────────┐
                    │            INDEXING (one-time setup)             │
                    │                                                 │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
                    │  │  Load    │→ │  Split   │→ │  Embed +     │ │
                    │  │  Filing  │  │  Chunks  │  │  Store       │ │
                    │  └──────────┘  └──────────┘  └──────────────┘ │
                    │  TextLoader    RecursiveText   HuggingFace     │
                    │                Splitter        Embeddings +    │
                    │                                FAISS           │
                    └─────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────┐
                    │           QUERYING (per question)               │
                    │                                                 │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
                    │  │ Question │→ │ Retrieve │→ │  Generate    │ │
                    │  │          │  │ Top-K    │  │  Answer      │ │
                    │  └──────────┘  └──────────┘  └──────────────┘ │
                    │  User input    FAISS          Claude +         │
                    │                similarity     Retrieved        │
                    │                search         context          │
                    └─────────────────────────────────────────────────┘
```

### How RAG Works (Step by Step)

```
Phase 1: INDEXING (happens once when app starts)
═══════════════════════════════════════════════

SEC Filing (long text document)
    │
    ▼
┌───────────────────────────────────────────┐
│ Text Splitter                             │
│ Breaks into chunks of ~500 tokens         │
│ with ~50 token overlap                    │
│                                           │
│ "Apple's total revenue..." → Chunk 1      │
│ "Risk factors include..." → Chunk 2       │
│ "The company operates..."  → Chunk 3      │
│ ... (128 chunks total)                    │
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│ Embedding Model                           │
│ Converts each chunk to a vector           │
│ (list of ~384 numbers)                    │
│                                           │
│ Chunk 1 → [0.12, -0.34, 0.56, ...]      │
│ Chunk 2 → [0.78, 0.23, -0.11, ...]      │
│ Chunk 3 → [0.45, -0.67, 0.89, ...]      │
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│ Vector Store (FAISS)                      │
│ Stores all chunks + their vectors         │
│ Enables fast similarity search            │
└───────────────────────────────────────────┘


Phase 2: QUERYING (happens per question)
═══════════════════════════════════════════════

User: "What was Apple's revenue?"
    │
    ▼
┌───────────────────────────────────────────┐
│ Embed the Question                        │
│ Same model as indexing                    │
│ "What was Apple's revenue?" → [0.11, ...] │
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│ Similarity Search                         │
│ Find top-4 chunks closest to question     │
│                                           │
│ Match 1: "Total net revenue was $391.0B"  │ ← Most similar
│ Match 2: "Revenue by segment: iPhone..."  │
│ Match 3: "Revenue grew 2% year-over..."  │
│ Match 4: "Services revenue reached..."    │
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│ Prompt + Claude                           │
│                                           │
│ System: "Answer based ONLY on context"    │
│ Context: [4 retrieved chunks]             │
│ Question: "What was Apple's revenue?"     │
│                                           │
│ → "Apple's total net revenue for fiscal   │
│    year 2024 was $391.0 billion..."       │
└───────────────────────────────────────────┘
```

### LCEL Implementation

```python
from langchain_core.runnables import RunnablePassthrough

# The retriever fetches relevant chunks
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# Format retrieved documents into a single string
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# The RAG chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Ask a question
answer = rag_chain.invoke("What was Apple's revenue?")
```

## 📊 Data: Sample SEC Filing

This example includes a **sample 10-K filing excerpt** (`data/sample_10k.txt`) so you don't need to download anything.

### What's in the Sample File?

An excerpted Apple 10-K annual filing containing:
- **Item 1**: Business description
- **Item 1A**: Risk factors
- **Item 6**: Selected financial data
- **Item 7**: Management's discussion and analysis (MD&A)
- **Item 8**: Financial statements (condensed)

### Why a Sample File?

- **No API calls needed** for the RAG part (fast iteration)
- **Consistent** results for everyone
- **Focused** content that demonstrates RAG well
- **Extendable** — swap in any 10-K text file

### Using Real Filings

Once the example works, you can replace the sample with real filings:
```python
# Download from SEC EDGAR
# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AAPL&type=10-K
# Save the filing text to data/your_filing.txt
```

## 🛠️ Key LangChain Concepts You'll Learn

### 1. Document Loaders

Load documents from various sources:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("data/sample_10k.txt")
documents = loader.load()
# Returns: [Document(page_content="...", metadata={"source": "..."})]
```

**Other loaders**: `PyPDFLoader`, `CSVLoader`, `WebBaseLoader`, `UnstructuredHTMLLoader`

### 2. Text Splitters

Break long documents into chunks with overlap:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Max characters per chunk
    chunk_overlap=200,    # Overlap between adjacent chunks
    separators=["\n\n", "\n", ". ", " "]  # Split at natural boundaries
)

chunks = splitter.split_documents(documents)
# Returns: [Document(page_content="chunk 1..."), Document(page_content="chunk 2..."), ...]
```

**Why overlap?** A relevant sentence might straddle two chunks. Overlap ensures context isn't lost at boundaries.

### 3. Embeddings

Convert text to numerical vectors for similarity search:

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Small, fast, free (runs locally)
)

# Convert text to vector
vector = embeddings.embed_query("What was Apple's revenue?")
# Returns: [0.12, -0.34, 0.56, ...] (384 dimensions)
```

**Why HuggingFace?** It's free and runs locally. No API key needed. For production, consider OpenAI or Cohere embeddings.

### 4. Vector Stores

Store and search document vectors:

```python
from langchain_community.vectorstores import FAISS

# Create vector store from documents
vector_store = FAISS.from_documents(chunks, embeddings)

# Search for similar chunks
results = vector_store.similarity_search("revenue", k=4)
# Returns: Top 4 chunks most similar to "revenue"
```

**FAISS** (Facebook AI Similarity Search) — fast, in-memory, no setup needed. For production, consider Pinecone, Weaviate, or ChromaDB.

### 5. Retrieval Chain

Combine retrieval with generation:

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

The `{"context": ..., "question": ...}` syntax creates a `RunnableParallel` that runs the retriever and passes the question through simultaneously.

## 🧪 Testing

### Good Questions to Try

| Question | What It Tests |
|----------|---------------|
| "What was Apple's total revenue?" | Simple fact retrieval |
| "What are the main risk factors?" | Multi-point retrieval |
| "How did iPhone sales perform?" | Segment-specific data |
| "What is Apple's debt situation?" | Financial statement data |
| "Who is Apple's CEO?" | Business description |
| "What is the meaning of life?" | Out-of-scope handling |

### Testing Incrementally

```bash
# Step 1: Test document loading
python -c "from filing_loader import load_and_chunk; chunks = load_and_chunk(); print(f'{len(chunks)} chunks')"

# Step 2: Test the full Q&A system
python simple_version.py
# Ask: "What was Apple's revenue?"

# Step 3: Test out-of-scope questions
# Ask: "What is Bitcoin's price?"
# Should say "I don't have that information in the filing"
```

## 🔧 Configuration

```python
# Chunking parameters
CHUNK_SIZE = 1000        # Characters per chunk (larger = more context, fewer chunks)
CHUNK_OVERLAP = 200      # Overlap between chunks (larger = more redundancy, better recall)

# Retrieval parameters
TOP_K = 4                # Number of chunks to retrieve per query

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free, local, ~80MB download

# LLM
MODEL = "claude-sonnet-4-5-20250929"
TEMPERATURE = 0          # Factual answers only
```

### Tuning Tips

| Parameter | Too Small | Too Large |
|-----------|-----------|-----------|
| `CHUNK_SIZE` | Loses context, fragmented answers | Retrieves too much noise |
| `CHUNK_OVERLAP` | Misses boundary content | Wastes storage, slower |
| `TOP_K` | Might miss relevant info | Includes irrelevant context |

## 💡 Learning Outcomes

After completing this example, you'll understand:

- ✅ The **RAG pattern** — when and why to use retrieval-augmented generation
- ✅ **Document loaders** — loading text files into LangChain Documents
- ✅ **Text splitters** — chunking strategies and why overlap matters
- ✅ **Embeddings** — converting text to vectors for similarity search
- ✅ **Vector stores** — storing and querying document vectors with FAISS
- ✅ **Retrieval chains** — combining retrieval + generation with LCEL
- ✅ **Grounded answers** — making LLMs answer from source documents only

## 🔗 Comparison: Progressive Complexity

| Feature | 01-Stock Summary | 02-News Analyzer | 03-Filing Q&A |
|---------|-----------------|------------------|---------------|
| Chain steps | 1 | 3 (sequential) | 2 (retrieve + generate) |
| Data source | SEC API (live) | Sample headlines | Local document |
| Key concept | LCEL basics | RunnablePassthrough | RAG pipeline |
| New concepts | — | Chain composition | Embeddings, vectors, retrieval |

## 🚧 Future Enhancements

- [ ] Support PDF filing uploads (PyPDFLoader)
- [ ] Persistent vector store (save to disk, reload later)
- [ ] Chat history (follow-up questions with context)
- [ ] Multi-document Q&A (compare two filings)
- [ ] Source highlighting (show exact paragraphs used)
- [ ] Streaming answers (token by token)
- [ ] Citation with page numbers

## 📚 Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Text Splitters Guide](https://python.langchain.com/docs/how_to/#text-splitters)
- [Vector Store Integrations](https://python.langchain.com/docs/integrations/vectorstores/)
- [FAISS Documentation](https://faiss.ai/)
- [HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

---

**Next up: [Portfolio Report Generator](../04-portfolio-report-generator) — learn structured output and batch processing →**
