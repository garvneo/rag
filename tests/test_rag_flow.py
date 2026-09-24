"""Fast, offline checks of document ingestion, retrieval, and replacement."""

import hashlib
import re
import unittest

from rag.chunking import CharacterChunker
from rag.loaders import BasicDocumentLoader
from rag.models import SearchResult, UploadedDocument
from rag.retrieval import SimilarityRetriever
from rag.service import RAGService
from rag.vector_store import InMemoryVectorStore


class LocalTestEmbedder:
    """Small deterministic token vectors; no network calls or model dependency."""

    def embed(self, texts):
        vectors = []
        for text in texts:
            vector = [0.0] * 128
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                slot = int.from_bytes(hashlib.blake2b(token.encode(), digest_size=2).digest(), "big") % 128
                vector[slot] += 1.0
            vectors.append(vector)
        return vectors


class ContextOnlyTestGenerator:
    """Return a fixed fact only when it appears in retrieved context."""

    def generate(self, question, sources):
        context = " ".join(source.chunk.text for source in sources).lower()
        question = question.lower()
        if "observatory" in question and "observatory" in context and "orbit-47" in context:
            return "The observatory access code is ORBIT-47. [1]"
        if "garden" in question and "garden shed" in context and "maple-12" in context:
            return "The garden shed key is MAPLE-12. [1]"
        if "code" in question and "orbit-47" in context:
            return "The code is ORBIT-47. [1]"
        return "I cannot answer from the current documents."


class RAGFlowTest(unittest.TestCase):
    def setUp(self):
        self.embedder = LocalTestEmbedder()
        self.store = InMemoryVectorStore()
        self.service = RAGService(
            loader=BasicDocumentLoader(),
            chunker=CharacterChunker(chunk_size=800, overlap=120),
            embedder=self.embedder,
            store=self.store,
            retriever=SimilarityRetriever(self.embedder, self.store),
            answer_generator=ContextOnlyTestGenerator(),
        )

    def upload(self, name, text):
        return UploadedDocument(name=name, content=text.encode("utf-8"))

    def test_answer_sources_abstention_and_replacement(self):
        first = self.service.ingest(
            [self.upload("observatory.txt", "The observatory access code is ORBIT-47.")]
        )
        self.assertEqual(first.document_count, 1)
        self.assertGreater(first.chunk_count, 0)

        supported = self.service.ask("What is the observatory access code?")
        self.assertIn("ORBIT-47", supported.text)
        self.assertEqual(supported.sources[0].chunk.source, "observatory.txt")
        self.assertIn("observatory", supported.sources[0].chunk.text)

        unsupported = self.service.ask("What is the capital of France?")
        self.assertEqual(unsupported.text, "I cannot answer from the current documents.")

        second = self.service.ingest(
            [self.upload("garden.txt", "The garden shed key is MAPLE-12.")]
        )
        self.assertEqual(second.document_count, 1)
        self.assertEqual(second.chunk_count, 1)

        old_question = self.service.ask("What is the observatory access code?")
        self.assertNotIn("ORBIT-47", old_question.text)
        self.assertTrue(all(source.chunk.source == "garden.txt" for source in old_question.sources))
        self.assertEqual(old_question.text, "I cannot answer from the current documents.")

        new_question = self.service.ask("What is the garden shed key?")
        self.assertIn("MAPLE-12", new_question.text)
        self.assertTrue(all(source.chunk.source == "garden.txt" for source in new_question.sources))

    def test_unreadable_replacement_preserves_existing_index(self):
        self.service.ingest([self.upload("observatory.txt", "The code is ORBIT-47.")])
        with self.assertRaisesRegex(ValueError, "current knowledge base was kept"):
            self.service.ingest([UploadedDocument(name="empty.txt", content=b"")])
        answer = self.service.ask("What is the code?")
        self.assertIn("ORBIT-47", answer.text)


if __name__ == "__main__":
    unittest.main()
