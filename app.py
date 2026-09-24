"""Streamlit UI; RAG work is delegated to the service and its components."""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag.chunking import CharacterChunker
from rag.embeddings import OpenAIEmbedder
from rag.generation import OpenAIAnswerGenerator
from rag.loaders import BasicDocumentLoader
from rag.models import SearchResult, UploadedDocument
from rag.retrieval import SimilarityRetriever
from rag.service import RAGService
from rag.vector_store import InMemoryVectorStore


def create_service(client: OpenAI) -> RAGService:
    embedder = OpenAIEmbedder(client, model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    store = InMemoryVectorStore()
    return RAGService(
        loader=BasicDocumentLoader(),
        chunker=CharacterChunker(),
        embedder=embedder,
        store=store,
        retriever=SimilarityRetriever(embedder, store),
        answer_generator=OpenAIAnswerGenerator(
            client, model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini")
        ),
    )


def render_sources(sources: tuple[SearchResult, ...]) -> None:
    if not sources:
        return
    with st.expander("Sources"):
        for index, result in enumerate(sources, start=1):
            page = f", page {result.chunk.page}" if result.chunk.page is not None else ""
            st.markdown(f"**[{index}] {result.chunk.source}{page}**")
            st.caption(result.chunk.text)


load_dotenv()
st.set_page_config(page_title="RAG Generator", page_icon="📚")
st.title("RAG Generator")
st.write("Upload documents to build a knowledge base, then ask questions grounded in their content.")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.info("Set OPENAI_API_KEY in your environment or local .env file to get started.")
    st.stop()

if "rag_service" not in st.session_state:
    st.session_state.rag_service = create_service(OpenAI(api_key=api_key))
if "messages" not in st.session_state:
    st.session_state.messages = []
if "index_summary" not in st.session_state:
    st.session_state.index_summary = None

uploads = st.file_uploader(
    "Choose PDF, TXT, or Markdown files",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
    help="Building a new knowledge base replaces the current one for this session.",
)

if st.button("Build / replace knowledge base", type="primary", disabled=not uploads):
    runtime_uploads = [UploadedDocument(name=file.name, content=file.getvalue()) for file in uploads]
    try:
        with st.spinner("Reading documents and creating embeddings…"):
            summary = st.session_state.rag_service.ingest(runtime_uploads)
        st.session_state.index_summary = summary
        st.session_state.messages = []
        st.success(
            f"Knowledge base ready: {summary.document_count} document(s), "
            f"{summary.chunk_count} chunk(s). Previous chat cleared."
        )
        for warning in summary.warnings:
            st.warning(warning)
    except Exception as exc:
        st.error(f"Could not build the knowledge base: {exc}")

if st.session_state.index_summary:
    summary = st.session_state.index_summary
    st.caption(f"Current knowledge base: {summary.document_count} document(s), {summary.chunk_count} chunk(s).")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        if message["role"] == "assistant":
            render_sources(message["sources"])

question = st.chat_input("Ask a question about your documents")
if question:
    st.session_state.messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the documents…"):
                answer = st.session_state.rag_service.ask(question)
            st.markdown(answer.text)
            render_sources(answer.sources)
            st.session_state.messages.append(
                {"role": "assistant", "text": answer.text, "sources": answer.sources}
            )
        except Exception as exc:
            error_text = f"I couldn't answer that question: {exc}"
            st.error(error_text)
            st.session_state.messages.append(
                {"role": "assistant", "text": error_text, "sources": ()}
            )
