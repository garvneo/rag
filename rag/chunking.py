"""Character-based overlapping chunking for extracted documents."""

from collections.abc import Sequence

from rag.models import Chunk, Document


class CharacterChunker:
    def __init__(self, chunk_size: int = 800, overlap: int = 120) -> None:
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, documents: Sequence[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for document in documents:
            text = document.text.strip()
            start = 0
            chunk_index = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                part = text[start:end].strip()
                if part:
                    chunks.append(
                        Chunk(
                            text=part,
                            source=document.source,
                            page=document.page,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1
                if end == len(text):
                    break
                start = end - self.overlap
        return chunks
