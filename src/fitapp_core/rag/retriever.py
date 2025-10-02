# #v1
# from typing import List, Dict

# def retrieve_snippets(inputs: Dict) -> List[Dict]:
#     # TODO: integrate LangChain retriever later; return [{"id": "...", "text": "..."}]
#     return []






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

# Optional central config
try:
    from config_paths import INDEX_DIR, PROC_DIR
except Exception:
    DATA_DIR = Path("./data")
    INDEX_DIR = DATA_DIR / "index" / "v1"
    PROC_DIR = DATA_DIR / "processed"

_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class RAGStore:
    def __init__(self, index_dir: Path = INDEX_DIR, processed_dir: Path = PROC_DIR):
        self._disabled = False
        self._use_faiss = False
        self._embedder = None

        data_dir = Path("./data").resolve()
        print(f"[RAG] Data dir: {data_dir}", file=sys.stderr)

        # Load metadata (prefer meta.parquet; fallback to chunks.jsonl)
        meta_path = index_dir / "meta.parquet"
        chunks_path = processed_dir / "chunks.jsonl"
        self.meta = None
        try:
            if meta_path.exists():
                self.meta = pd.read_parquet(meta_path)
            elif chunks_path.exists():
                chunks = pd.read_json(chunks_path, lines=True)
                self.meta = chunks[["id", "text"]].copy()
            else:
                self._disabled = True
                print("[RAG] disabled (no meta/chunks found)", file=sys.stderr)
        except Exception as e:
            self._disabled = True
            print(f"[RAG] disabled (meta load error: {e})", file=sys.stderr)

        # Backend selection
        if not self._disabled:
            faiss_path = index_dir / "faiss.index"
            emb_path = index_dir / "embeddings.npy"

            if faiss is not None and faiss_path.exists():
                try:
                    self.index = faiss.read_index(str(faiss_path))
                    self._use_faiss = True
                    print("[RAG] Using FAISS backend", file=sys.stderr)
                except Exception as e:
                    print(f"[RAG] FAISS load failed: {e}", file=sys.stderr)

            if not self._use_faiss:
                if emb_path.exists():
                    try:
                        emb = np.load(emb_path)
                        norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
                        self.emb = (emb / norms).astype(np.float32)
                        print("[RAG] Using NumPy backend", file=sys.stderr)
                    except Exception as e:
                        self._disabled = True
                        print(f"[RAG] disabled (embeddings load error: {e})", file=sys.stderr)
                else:
                    self._disabled = True
                    print("[RAG] disabled (no backend/index)", file=sys.stderr)

        # If still no meta, disable
        if self.meta is None or getattr(self.meta, "empty", True):
            self._disabled = True
            print("[RAG] disabled (empty metadata)", file=sys.stderr)

    def _embedder_model(self):
        from sentence_transformers import SentenceTransformer  # lazy import
        if self._embedder is None:
            self._embedder = SentenceTransformer(_EMBED_MODEL_NAME)
        return self._embedder

    def _encode(self, texts: List[str]) -> np.ndarray:
        model = self._embedder_model()
        vecs = model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)

    def _search_numpy(self, qv: np.ndarray, k: int):
        # qv shape (1, d), emb shape (N, d) normalized -> cosine via dot
        sims = (self.emb @ qv.T).ravel()
        n = sims.size
        if k >= n:
            order = np.argsort(-sims)
        else:
            topk = np.argpartition(-sims, k)[:k]
            order = topk[np.argsort(-sims[topk])]
        return sims[order], order

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
        if self._disabled:
            print("[RAG] query skipped (disabled)", file=sys.stderr)
            return []

        # Encode query; if embedding model missing, fail soft
        try:
            qv = self._encode([q])  # (1, d)
        except Exception as e:
            print(f"[RAG] embedder unavailable ({e}); skipping retrieval", file=sys.stderr)
            return []

        # Search
        over_k = max(top_k * 3, top_k)
        if self._use_faiss:
            sims, idx = self.index.search(qv, over_k)
            sims = sims[0]
            idx = idx[0]
            pre_count = len(idx)
        else:
            sims, idx = self._search_numpy(qv, over_k)
            pre_count = len(idx)

        # Collect with tag filtering
        out: List[Dict] = []
        for rank, i in enumerate(idx.tolist() if hasattr(idx, "tolist") else idx):
            if i < 0:
                continue
            row = self.meta.iloc[i].to_dict()
            tags = row.get("tags", [])
            if domains and not any(f"domain:{d}" in tags for d in domains):
                continue
            if evidence and f"evidence:{evidence}" not in tags:
                continue
            out.append(
                {
                    "id": row.get("id"),
                    "doc_id": row.get("doc_id"),
                    "text": row.get("text", ""),
                    "tags": tags,
                    "score": float(sims[rank]) if rank < len(sims) else None,
                }
            )
            if len(out) >= top_k:
                break

        # Logs
        print(f"[RAG] Query: {q[:120]}... | top_k={top_k}", file=sys.stderr)
        print(f"[RAG] Hits (pre-filter): {pre_count}", file=sys.stderr)
        print(f"[RAG] Hits (post-filter): {len(out)}", file=sys.stderr)
        return out


def retrieve_snippets(inputs: Dict) -> List[Dict]:
    try:
        store = RAGStore()
        return store.query(
            inputs,
            top_k=inputs.get("top_k", 6),
            domains=inputs.get("domains"),
            evidence=inputs.get("evidence"),
        )
    except Exception as e:
        # Fail-soft: no retrieval rather than crash generation/tests
        print(f"[RAG] retrieval error: {e}", file=sys.stderr)
        return []
