"""
retriever.py
────────────
Loads the FAISS index from disk and provides semantic search.
Returns top-k most relevant chunks for a given query.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict

import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL   = "text-embedding-ada-002"
INDEX_FILE    = Path("faiss_index/index.faiss")
METADATA_FILE = Path("faiss_index/metadata.pkl")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Retriever:
    """
    Wraps a FAISS index and exposes a simple .search(query, k) interface.

    Usage:
        retriever = Retriever()
        results = retriever.search("What APR do I get with a 720 credit score?", k=3)
    """

    def __init__(self):
        if not INDEX_FILE.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {INDEX_FILE}. "
                "Run `python ingest.py` first."
            )

        print("Loading FAISS index...", end=" ")
        self.index    = faiss.read_index(str(INDEX_FILE))
        self.metadata = pickle.load(open(METADATA_FILE, "rb"))
        print(f"OK ({self.index.ntotal} vectors)")

    def _embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string, normalize for cosine similarity."""
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=[query]
        )
        vec = np.array([response.data[0].embedding], dtype="float32")
        faiss.normalize_L2(vec)
        return vec

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Semantic search over the indexed chunks.

        Returns list of dicts sorted by relevance:
            {chunk_id, source_name, text, score, rank}
        """
        vec = self._embed_query(query)
        scores, indices = self.index.search(vec, k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue
            chunk = self.metadata[idx].copy()
            chunk["score"] = float(score)
            chunk["rank"]  = rank + 1
            results.append(chunk)

        return results

    def format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved chunks into a single context block for the LLM prompt.
        Each chunk is labeled with its source file and relevance rank.
        """
        parts = []
        for r in results:
            parts.append(
                f"[Source: {r['source_name']} | Relevance rank: {r['rank']}]\n"
                f"{r['text']}"
            )
        return "\n\n---\n\n".join(parts)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    r = Retriever()

    test_queries = [
        "What APR can I get with a 750 credit score on a new car?",
        "How much down payment do I need?",
        "What happens if I miss a payment?",
        "Can I refinance my car loan?",
        "What fees are charged at closing?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        results = r.search(q, k=3)
        for res in results:
            print(f"  [{res['rank']}] {res['source_name']}  "
                  f"score={res['score']:.4f}")
            print(f"      {res['text'][:120].strip()}...")
