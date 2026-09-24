"""Small component contracts to keep implementations replaceable."""

from collections.abc import Sequence
from typing import Protocol

from rag.models import Chunk, Document, SearchResult, UploadedDocument


class DocumentLoader(Protocol):
    def load(
        self, uploads: Sequence[UploadedDocument]
    ) -> tuple[list[Document], list[str]]: ...


class Chunker(Protocol):
    def split(self, documents: Sequence[Document]) -> list[Chunk]: ...


class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    def replace(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> None: ...

    def search(self, vector: Sequence[float], limit: int) -> list[SearchResult]: ...


class Retriever(Protocol):
    def retrieve(self, question: str, limit: int = 4) -> list[SearchResult]: ...


class AnswerGenerator(Protocol):
    def generate(self, question: str, sources: Sequence[SearchResult]) -> str: ...
