# RAG Generator

A small Streamlit application that builds a retrieval-augmented question-answering experience from documents uploaded at runtime. Upload a document set, build its knowledge base, then ask questions and inspect the source excerpts used for each answer.

## Requirements

- Python 3.9 or newer
- An OpenAI API key with access to the configured chat and embedding models

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `.env`, then run:

```bash
streamlit run app.py
```

The app accepts PDF, TXT, and Markdown (`.md`) files. Text-based PDFs are supported; scanned PDFs require OCR and are reported as having no extractable text. Uploading and building another document set replaces the current session's knowledge base and clears its chat history.

## How it works

The app delegates RAG responsibilities to separate components under `rag/`:

- `loaders.py` extracts text and source metadata from uploads.
- `chunking.py` creates overlapping text chunks.
- `embeddings.py` provides OpenAI text embeddings through the `Embedder` interface.
- `vector_store.py` stores vectors in memory and performs cosine-similarity search through the `VectorStore` interface.
- `retrieval.py` embeds a question and asks the vector store for its closest chunks.
- `generation.py` builds a context-grounded answer with numbered source citations.
- `service.py` orchestrates ingestion and question answering. `app.py` handles the user interface and calls this service.

The small contracts in `interfaces.py` make the embedding provider and vector store replaceable without changing the user flow. Model names can also be changed with `OPENAI_CHAT_MODEL` and `OPENAI_EMBEDDING_MODEL`.

## Scaling this up

For a production multi-user system, the main changes would be:

- Replace `InMemoryVectorStore` with a persistent vector database so indexes survive restarts and can grow beyond one process's memory.
- Move parsing, chunking, and embedding into background ingestion jobs. Track job state and report completion or failures to the user.
- Assign each index a dataset or tenant identifier and enforce that filter during every retrieval. Keep uploaded source files and index metadata in durable storage.
- Add authentication and authorization, then scope document upload, replacement, and retrieval to the authenticated user or tenant.
- Add operational controls such as upload limits, retry handling, observability, and retention policies.

The current implementation intentionally keeps indexes in per-session memory and does not include accounts, persistence, OCR, or background jobs.

## Assessment transcript

`AI_AGENT_TRANSCRIPT.md` contains the conversation and implementation record for this submission.
