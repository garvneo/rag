"""Embed questions and retrieve the closest indexed chunks."""

from rag.interfaces import Embedder, VectorStore
from rag.models import SearchResult


class SimilarityRetriever:
    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self.embedder = embedder
        self.store = store

    def retrieve(self, question: str, limit: int = 4) -> list[SearchResult]:
        vectors = self.embedder.embed([question])
        if not vectors:
            return []
        return self.store.search(vectors[0], limit)
