"""Application-level orchestration for ingestion and question answering."""

from collections.abc import Sequence

from rag.interfaces import AnswerGenerator, Chunker, DocumentLoader, Embedder, Retriever, VectorStore
from rag.models import Answer, IngestionSummary, SearchResult, UploadedDocument


class RAGService:
    def __init__(
        self,
        loader: DocumentLoader,
        chunker: Chunker,
        embedder: Embedder,
        store: VectorStore,
        retriever: Retriever,
        answer_generator: AnswerGenerator,
    ) -> None:
        self.loader = loader
        self.chunker = chunker
        self.embedder = embedder
        self.store = store
        self.retriever = retriever
        self.answer_generator = answer_generator
        self._has_index = False

    def ingest(self, uploads: Sequence[UploadedDocument]) -> IngestionSummary:
        documents, warnings = self.loader.load(uploads)
        chunks = self.chunker.split(documents)
        if not chunks:
            details = " " + " ".join(warnings) if warnings else ""
            raise ValueError(
                "No readable text was found; the current knowledge base was kept." + details
            )

        vectors = self.embedder.embed([chunk.text for chunk in chunks])
        if len(vectors) != len(chunks):
            raise ValueError("The embedding provider returned an unexpected number of vectors.")
        self.store.replace(chunks, vectors)
        self._has_index = True
        return IngestionSummary(document_count=len({doc.source for doc in documents}), chunk_count=len(chunks), warnings=tuple(warnings))

    def ask(self, question: str, limit: int = 4) -> Answer:
        if not self._has_index:
            return Answer(text="Upload and build a knowledge base before asking a question.", sources=())
        sources = self.retriever.retrieve(question, limit=limit)
        if not sources:
            return Answer(text="Upload and build a knowledge base before asking a question.", sources=())
        text = self.answer_generator.generate(question, sources)
        return Answer(text=text, sources=tuple(sources))
