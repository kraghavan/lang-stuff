"""
Filing Loader — Document Loading and Chunking for RAG

Loads SEC filing text files and splits them into chunks suitable
for embedding and retrieval. This is the "indexing" phase of RAG.

Key Concepts:
- Document Loaders: Read files into LangChain Document objects
- Text Splitters: Break long docs into smaller, overlapping chunks
- Chunk Size: How big each piece is (~1000 chars is a good default)
- Chunk Overlap: How much adjacent chunks share (~200 chars prevents lost context)

Usage:
    from filing_loader import load_and_chunk
    chunks = load_and_chunk("data/sample_10k.txt")
"""

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
DEFAULT_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_10k.txt")
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


# ═══════════════════════════════════════════════
# Load the Filing Document
#
# TextLoader reads a text file and creates a LangChain Document object.
# Each Document has:
#   - page_content: The text string
#   - metadata: {"source": "data/sample_10k.txt"}
# ═══════════════════════════════════════════════

def load_filing(file_path: str = DEFAULT_FILE_PATH) -> list:
    """
    Load a SEC filing text file into LangChain Documents.

    Args:
        file_path: Path to the filing text file

    Returns:
        List of Document objects (typically one per file)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Filing not found: {file_path}\n"
            f"Make sure data/sample_10k.txt exists in the 03-sec-filing-qa directory."
        )

    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"✓ Loaded {len(documents)} document(s) ({total_chars:,} chars)")
    return documents


# ═══════════════════════════════════════════════
# Split into Chunks
#
# RecursiveCharacterTextSplitter breaks long documents into
# smaller, overlapping chunks. It tries to split at natural
# boundaries in this priority order:
#   1. "\n\n" — paragraph boundaries (best)
#   2. "\n"   — line breaks
#   3. ". "   — sentence boundaries
#   4. " "    — word boundaries
#   5. ""     — character level (last resort)
#
# Why overlap? A relevant sentence might straddle two chunk
# boundaries. Overlap ensures no information is lost at edges.
# ═══════════════════════════════════════════════

def split_into_chunks(
    documents: list,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> list:
    """
    Split documents into smaller, overlapping chunks.

    Args:
        documents: List of Document objects from load_filing()
        chunk_size: Maximum characters per chunk (default: 1000)
        chunk_overlap: Characters shared between adjacent chunks (default: 200)

    Returns:
        List of smaller Document chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    avg_len = sum(len(c.page_content) for c in chunks) // max(len(chunks), 1)
    print(f"✓ Split into {len(chunks)} chunks (avg {avg_len} chars each)")
    return chunks


# ═══════════════════════════════════════════════
# Convenience Function
# ═══════════════════════════════════════════════

def load_and_chunk(
    file_path: str = DEFAULT_FILE_PATH,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> list:
    """
    Load a filing and split it into chunks. One-stop convenience function.

    Args:
        file_path: Path to the filing text file
        chunk_size: Max characters per chunk
        chunk_overlap: Overlap between adjacent chunks

    Returns:
        List of Document chunks ready for embedding
    """
    documents = load_filing(file_path)
    chunks = split_into_chunks(documents, chunk_size, chunk_overlap)
    return chunks


# ═══════════════════════════════════════════════
# Test the module directly
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("📄 Testing Filing Loader")
    print("=" * 40)

    chunks = load_and_chunk()

    if chunks:
        print(f"\n📊 Chunk Statistics:")
        lengths = [len(c.page_content) for c in chunks]
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Avg length:   {sum(lengths) // len(lengths)} chars")
        print(f"  Min length:   {min(lengths)} chars")
        print(f"  Max length:   {max(lengths)} chars")

        print(f"\n📝 First chunk preview:")
        print(f"  {chunks[0].page_content[:200]}...")

        print(f"\n📝 Last chunk preview:")
        print(f"  {chunks[-1].page_content[:200]}...")
    else:
        print("✗ No chunks created. Check that data/sample_10k.txt exists.")
