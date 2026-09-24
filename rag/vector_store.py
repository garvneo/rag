"""Simple in-memory cosine-similarity vector store."""

from collections.abc import Sequence

import numpy as np

from rag.models import Chunk, SearchResult


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors = np.empty((0, 0), dtype=np.float32)

    def replace(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Each chunk must have exactly one embedding.")
        if not chunks:
            self._chunks = []
            self._vectors = np.empty((0, 0), dtype=np.float32)
            return

        matrix = np.asarray(vectors, dtype=np.float32)
        if matrix.ndim != 2 or matrix.shape[0] != len(chunks):
            raise ValueError("Embeddings must be a two-dimensional matrix matching the chunks.")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        matrix = matrix / np.maximum(norms, 1e-12)
        self._chunks = list(chunks)
        self._vectors = matrix

    def search(self, vector: Sequence[float], limit: int) -> list[SearchResult]:
        if not self._chunks or limit <= 0:
            return []
        query = np.asarray(vector, dtype=np.float32)
        if query.ndim != 1 or query.shape[0] != self._vectors.shape[1]:
            raise ValueError("Query embedding does not match the indexed embedding dimensions.")
        query = query / max(float(np.linalg.norm(query)), 1e-12)
        scores = self._vectors @ query
        indexes = np.argsort(scores)[::-1][:limit]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(scores[i])) for i in indexes]
