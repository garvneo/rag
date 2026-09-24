"""Load supported runtime uploads into page-aware text documents."""

from collections.abc import Sequence
from io import BytesIO

from pypdf import PdfReader

from rag.models import Document, UploadedDocument


class BasicDocumentLoader:
    """Supports text, Markdown, and text-based PDF files."""

    SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}

    def load(
        self, uploads: Sequence[UploadedDocument]
    ) -> tuple[list[Document], list[str]]:
        documents: list[Document] = []
        warnings: list[str] = []

        for upload in uploads:
            suffix = "." + upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
            if suffix not in self.SUPPORTED_SUFFIXES:
                warnings.append(f"{upload.name}: unsupported file type (PDF, TXT, and MD are supported).")
                continue
            if not upload.content:
                warnings.append(f"{upload.name}: file is empty.")
                continue

            try:
                if suffix == ".pdf":
                    reader = PdfReader(BytesIO(upload.content))
                    if reader.is_encrypted:
                        raise ValueError("encrypted PDFs are not supported")
                    found_text = False
                    for page_number, page in enumerate(reader.pages, start=1):
                        text = (page.extract_text() or "").strip()
                        if text:
                            documents.append(Document(text=text, source=upload.name, page=page_number))
                            found_text = True
                    if not found_text:
                        warnings.append(f"{upload.name}: no extractable text found (scanned PDFs need OCR).")
                else:
                    text = upload.content.decode("utf-8", errors="replace").strip()
                    if text:
                        documents.append(Document(text=text, source=upload.name))
                    else:
                        warnings.append(f"{upload.name}: no text found.")
            except Exception as exc:
                warnings.append(f"{upload.name}: could not read file ({exc}).")

        return documents, warnings
