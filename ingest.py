"""
ingest.py
─────────
Offline pipeline: reads PDF/TXT/CSV documents → chunks text →
generates OpenAI embeddings → saves FAISS index to disk.

Run once (or whenever documents change):
    python ingest.py
"""

import os
import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
CHUNK_SIZE       = 400    # approximate words per chunk (~500 tokens)
CHUNK_OVERLAP    = 40     # words overlap between chunks
EMBED_MODEL      = "text-embedding-ada-002"
EMBED_DIM        = 1536   # ada-002 output dimension
DATA_DIR         = Path("data")
INDEX_DIR        = Path("faiss_index")
INDEX_FILE       = INDEX_DIR / "index.faiss"
METADATA_FILE    = INDEX_DIR / "metadata.pkl"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── Text loading ──────────────────────────────────────────────────────────────

def load_pdf(path: Path) -> str:
    """Extract text from a PDF using PyMuPDF with pdfplumber fallback for tables."""
    try:
        import fitz  # PyMuPDF
        import pdfplumber

        chunks = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        rows = ["\t".join(cell or "" for cell in row) for row in table]
                        chunks.append("\n".join(rows))
                else:
                    doc = fitz.open(str(path))
                    chunks.append(doc[i].get_text())
        return "\n\n".join(chunks)

    except Exception as e:
        print(f"  PDF parse error for {path.name}: {e}")
        return ""


def load_txt(path: Path) -> str:
    """Load plain text file (used for demo .txt stand-ins)."""
    return path.read_text(encoding="utf-8", errors="ignore")


def load_csv(path: Path) -> str:
    """
    Convert CSV to a human-readable string.
    Each row becomes 'Column: Value | Column: Value ...' so the LLM
    can reason over individual rows naturally.
    """
    try:
        df = pd.read_csv(path)
        rows = []
        for _, row in df.iterrows():
            parts = [f"{col}: {val}" for col, val in row.items()]
            rows.append(" | ".join(parts))
        header = f"[Table: {path.stem}]\n"
        return header + "\n".join(rows)
    except Exception as e:
        print(f"  CSV parse error for {path.name}: {e}")
        return ""


def load_documents(data_dir: Path) -> List[Dict]:
    """
    Walk data_dir recursively and load all supported file types.
    Returns list of dicts: {source, content}
    """
    docs = []
    patterns = [("**/*.pdf", load_pdf),
                ("**/*.txt", load_txt),
                ("**/*.csv", load_csv)]

    for glob_pattern, loader in patterns:
        for path in sorted(data_dir.glob(glob_pattern)):
            print(f"  Loading: {path.relative_to(data_dir)}")
            content = loader(path)
            if content.strip():
                docs.append({"source": str(path), "content": content})
            else:
                print(f"    ↳ Warning: empty content, skipping")

    return docs


# ── Chunking ──────────────────────────────────────────────────────────────────

def split_into_chunks(text: str, source: str) -> List[Dict]:
    """
    Splits text into overlapping word-bounded chunks (~400 words each).
    Avoids tiktoken network dependency while preserving semantic coherence.
    Returns list of {chunk_id, source, text, word_count}
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk_text = " ".join(words[start:end])

        chunk_id = hashlib.md5(f"{source}:{start}".encode()).hexdigest()[:12]
        chunks.append({
            "chunk_id":    chunk_id,
            "source":      source,
            "source_name": Path(source).name,
            "text":        chunk_text,
            "word_count":  end - start,
            "start_word":  start,
        })

        if end == len(words):
            break
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ── Embedding ─────────────────────────────────────────────────────────────────

def embed_batch(texts: List[str], batch_size: int = 100) -> np.ndarray:
    """
    Embed a list of strings using OpenAI ada-002.
    Processes in batches to respect API limits.
    Returns numpy array of shape (N, EMBED_DIM).
    """
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        print(f"  Embedding batch {i // batch_size + 1} "
              f"({len(batch)} chunks)...")

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return np.array(all_embeddings, dtype="float32")


# ── FAISS index ───────────────────────────────────────────────────────────────

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS flat inner-product index (equivalent to cosine similarity
    when vectors are L2-normalised).
    """
    # Normalize vectors so inner product == cosine similarity
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(embeddings)
    return index


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_ingest():
    print("\n═══════════════════════════════════════")
    print("  Automotive Finance RAG — Ingestion")
    print("═══════════════════════════════════════\n")

    INDEX_DIR.mkdir(exist_ok=True)

    # 1. Load documents
    print("Step 1 / 4  Loading documents...")
    documents = load_documents(DATA_DIR)
    if not documents:
        print("  ERROR: No documents found in data/. Run generate_sample_data.py first.")
        return
    print(f"  Loaded {len(documents)} document(s)\n")

    # 2. Chunk
    print("Step 2 / 4  Chunking text...")
    all_chunks = []
    for doc in documents:
        chunks = split_into_chunks(doc["content"], doc["source"])
        all_chunks.extend(chunks)
        print(f"  {Path(doc['source']).name} → {len(chunks)} chunks")
    print(f"  Total chunks: {len(all_chunks)}\n")

    # 3. Embed
    print("Step 3 / 4  Generating embeddings...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_batch(texts)
    print(f"  Embeddings shape: {embeddings.shape}\n")

    # 4. Build and save FAISS index
    print("Step 4 / 4  Building FAISS index...")
    index = build_faiss_index(embeddings)
    faiss.write_index(index, str(INDEX_FILE))

    # Save metadata (parallel list to FAISS vectors)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"  Index saved → {INDEX_FILE}")
    print(f"  Metadata saved → {METADATA_FILE}")
    print(f"\n✓ Ingestion complete — {len(all_chunks)} chunks indexed.\n")


if __name__ == "__main__":
    run_ingest()
