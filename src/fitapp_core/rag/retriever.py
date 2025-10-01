# #v1
# from typing import List, Dict

# def retrieve_snippets(inputs: Dict) -> List[Dict]:
#     # TODO: integrate LangChain retriever later; return [{"id": "...", "text": "..."}]
#     return []

# file: retriever.py
from __future__ import annotations
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
import pandas as pd
import sys

try:
    import faiss  # type: ignore
except ImportError:
    faiss = None

try:
    from config_paths import INDEX_DIR, PROC_DIR
except Exception:
    # Fallback if config_paths.py isn't used
    DATA_DIR = Path("./data")
    INDEX_DIR = DATA_DIR / "index" / "v1"
    PROC_DIR = DATA_DIR / "processed"

_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class RAGStore:
    def __init__(self, index_dir: Path = INDEX_DIR, processed_dir: Path = PROC_DIR):
        data_dir = Path("./data").resolve()
        print(f"[RAG] Data dir: {data_dir}", file=sys.stderr)
        print(f"[RAG] Using {'FAISS' if faiss else 'NumPy'} backend", file=sys.stderr)
        if faiss is None:
            raise RuntimeError("faiss-cpu is required at runtime for retrieval.")
        self.index = faiss.read_index(str(index_dir / "faiss.index"))
        self.meta = pd.read_parquet(index_dir / "meta.parquet")
        if "text" not in self.meta.columns or self.meta["text"].isna().all():
            chunks = pd.read_json(processed_dir / "chunks.jsonl", lines=True)
            self.meta = self.meta.merge(chunks[["id", "text"]], on="id", how="left")
        self._embedder = None

    def _embedder_model(self):
        from sentence_transformers import SentenceTransformer
        if self._embedder is None:
            self._embedder = SentenceTransformer(_EMBED_MODEL_NAME)
        return self._embedder

    def _encode(self, texts: List[str]) -> np.ndarray:
        model = self._embedder_model()
        vecs = model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)

    def query(
        self,
        inputs: Dict,
        top_k: int = 6,
        domains: Optional[List[str]] = None,
        evidence: Optional[str] = None,
    ) -> List[Dict]:
        q = inputs.get("query") or ""
        if not q.strip():
            return []
        qv = self._encode([q])
        sims, idx = self.index.search(qv, top_k * 3)  # over-retrieve, then filter
        out: List[Dict] = []
        for rank, i in enumerate(idx[0].tolist()):
            row = self.meta.iloc[i].to_dict()
            tags = row.get("tags", [])
            if domains and not any(f"domain:{d}" in tags for d in domains):
                continue
            if evidence and f"evidence:{evidence}" not in tags:
                continue
            out.append({
                "id": row["id"],
                "doc_id": row.get("doc_id"),
                "text": row.get("text", ""),
                "tags": tags,
                "score": float(sims[0, rank]),
            })
            if len(out) >= top_k:
                break
        print(f"[RAG] Query: {q[:120]}... | top_k={top_k}", file=sys.stderr)
        print(f"[RAG] Hits (pre-filter): {len(idx.tolist() if hasattr(idx,'tolist') else idx)}", file=sys.stderr)
        print(f"[RAG] Hits (post-filter): {len(out)}", file=sys.stderr)
        return out    
        return out

def retrieve_snippets(inputs: Dict) -> List[Dict]:
    store = RAGStore()
    return store.query(
        inputs,
        top_k=inputs.get("top_k", 6),
        domains=inputs.get("domains"),
        evidence=inputs.get("evidence"),
    )
