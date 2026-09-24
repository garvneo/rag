# Implementation Plan

- [x] Accept documents at runtime — Streamlit upload supports PDF, TXT, and Markdown.
- [x] Build a RAG index over uploaded documents — loading, chunking, embeddings, and vector storage are separate components.
- [x] Answer questions from document content and show sources — retrieval feeds grounded generation; answers include source labels and excerpts.
- [x] Replace the current document set without code changes — successful re-indexing replaces stored chunks and clears chat history.

## Verification

- [x] `.venv/bin/python -m unittest discover -s tests -v` — both offline end-to-end checks pass.
- [x] Supported question returns the expected document fact and source metadata.
- [x] Unsupported question abstains; replacing documents answers from the new set and no longer returns the old fact.
- [x] Unreadable replacement keeps the previous index.
- [x] Streamlit startup smoke check shows the API-key setup prompt with no runtime exception.
- [ ] Live OpenAI generation and actual browser upload/chat interaction (no API key configured; test doubles were used for the core RAG flow).
