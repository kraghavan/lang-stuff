"""
SEC Filing Q&A — RAG (Retrieval-Augmented Generation)

Ask natural language questions about SEC filings and get accurate,
source-grounded answers using the RAG pattern.

Architecture:
    Filing → Chunk → Embed → Store (indexing)
    Question → Retrieve → Prompt + Context → Claude → Answer (querying)

Key Concepts:
    - Document loading and chunking
    - Embeddings (HuggingFace, local)
    - Vector store (FAISS, in-memory)
    - Retrieval chain (retrieve + generate)

Usage:
    python simple_version.py

Requires:
    - ANTHROPIC_API_KEY environment variable
    - data/sample_10k.txt (included)
    - sentence-transformers package (for embeddings)
"""

import os
import sys
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Local imports
from filing_loader import load_and_chunk

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
MAX_TOKENS = 1024
TOP_K = 4  # Number of chunks to retrieve per question
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, free (runs locally, ~80MB)


# ═══════════════════════════════════════════════
# Create Embeddings and Vector Store
#
# Embeddings convert text into vectors (lists of numbers)
# where similar meanings are close together:
#
#   "Apple's revenue was $391 billion"  → [0.12, -0.34, 0.56, ...]
#   "What was Apple's total sales?"     → [0.13, -0.33, 0.55, ...]  ← Close!
#   "Risk factors include competition"  → [0.78, 0.23, -0.11, ...]  ← Far away
#
# FAISS (Facebook AI Similarity Search) stores these vectors
# and enables fast nearest-neighbor search.
# ═══════════════════════════════════════════════

def create_vector_store(chunks: list):
    """
    Create a FAISS vector store from document chunks.

    Args:
        chunks: List of Document chunks from filing_loader

    Returns:
        FAISS vector store
    """
    print("📊 Creating embeddings (first run downloads the model ~80MB)...")

    # HuggingFace embeddings run locally — no API key needed
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # Create vector store: embeds all chunks and indexes them
    vector_store = FAISS.from_documents(chunks, embeddings)
    print(f"✓ Created vector store with {len(chunks)} vectors")

    return vector_store


# ═══════════════════════════════════════════════
# Create the Retriever
#
# A retriever wraps the vector store's similarity search
# into a standardized interface compatible with LCEL chains.
#
# Usage:
#   docs = retriever.invoke("What was the revenue?")
#   → Returns top-K documents most similar to the query
# ═══════════════════════════════════════════════

def create_retriever(vector_store, top_k: int = TOP_K):
    """
    Create a retriever from the vector store.

    Args:
        vector_store: FAISS vector store
        top_k: Number of chunks to retrieve per query

    Returns:
        Retriever compatible with LCEL chains
    """
    retriever = vector_store.as_retriever(
        search_kwargs={"k": top_k}
    )
    return retriever


# ═══════════════════════════════════════════════
# RAG Prompt
#
# This prompt is CRITICAL — it instructs Claude to:
# 1. Answer ONLY from the provided context
# 2. Admit when the context doesn't contain the answer
# 3. Cite specific data points
#
# Without these rules, Claude might hallucinate answers
# from its training data instead of the actual filing.
# ═══════════════════════════════════════════════

def create_rag_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for RAG-based Q&A.

    Returns:
        ChatPromptTemplate with {context} and {question} placeholders
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a financial analyst answering questions about SEC filings. "
         "\n\nIMPORTANT RULES:"
         "\n- Answer ONLY based on the provided context from the filing"
         "\n- If the context doesn't contain the answer, say 'I don't have that information in the filing'"
         "\n- Cite specific sections, data points, or figures from the context"
         "\n- Be precise with numbers — do not round or estimate"
         "\n- Keep answers concise but complete"),
        ("human", """Context from the SEC filing:
{context}

Question: {question}

Answer based only on the context above:""")
    ])
    return prompt


# ═══════════════════════════════════════════════
# RAG Chain
#
# The RAG chain combines retrieval with generation using LCEL:
#
#   question → retriever (finds relevant chunks)
#            → format into context string
#            → inject into prompt alongside question
#            → Claude generates grounded answer
#            → parser extracts text
#
# The {"context": ..., "question": ...} syntax creates a
# RunnableParallel: the retriever and passthrough run
# simultaneously, then results are merged into a dict.
# ═══════════════════════════════════════════════

def format_docs(docs: list) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(retriever):
    """
    Build the complete RAG chain using LCEL.

    Args:
        retriever: Document retriever from create_retriever()

    Returns:
        LCEL chain: str (question) → str (answer)
    """
    prompt = create_rag_prompt()
    llm = ChatAnthropic(model=MODEL, temperature=0, max_tokens=MAX_TOKENS)
    parser = StrOutputParser()

    # The RAG chain:
    # 1. {"context": ...} runs the retriever on the input, then formats docs
    # 2. {"question": ...} passes the input through unchanged
    # 3. Both are merged into a dict → fed to the prompt → llm → parser
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | parser
    )

    return rag_chain


# ═══════════════════════════════════════════════
# Interactive Q&A Loop
# ═══════════════════════════════════════════════

def run_qa_session(rag_chain):
    """
    Run an interactive Q&A session with the filing.

    Args:
        rag_chain: The RAG chain from create_rag_chain()
    """
    print("\nReady! Ask questions about the filing (type 'quit' to exit).\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\n🔍 Searching filing for relevant sections...")
        try:
            answer = rag_chain.invoke(question)
            print(f"\nAnswer:\n  {answer}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

        print("─" * 40 + "\n")


# ═══════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════

def main():
    """Set up the RAG pipeline and start Q&A session."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n📄 SEC Filing Q&A System")
    print("=" * 40)

    # Step 1: Load and chunk the filing
    print("\n📂 Loading filing...")
    chunks = load_and_chunk()
    if not chunks:
        print("✗ Failed to load filing. Check that data/sample_10k.txt exists.")
        sys.exit(1)

    # Step 2: Create vector store
    print("\n📊 Building vector store...")
    vector_store = create_vector_store(chunks)

    # Step 3: Create retriever and RAG chain
    retriever = create_retriever(vector_store)
    rag_chain = create_rag_chain(retriever)

    # Step 4: Start interactive session
    run_qa_session(rag_chain)


if __name__ == "__main__":
    main()
