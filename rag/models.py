"""Shared data structures used by the RAG components."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadedDocument:
    name: str
    content: bytes


@dataclass(frozen=True)
class Document:
    text: str
    source: str
    page: int | None = None


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    page: int | None
    chunk_index: int


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class IngestionSummary:
    document_count: int
    chunk_count: int
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Answer:
    text: str
    sources: tuple[SearchResult, ...]
