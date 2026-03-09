from __future__ import annotations

import fitz  # PyMuPDF


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF document represented by bytes."""
    text_chunks: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_chunks.append(page.get_text("text"))
    return "\n".join(text_chunks).strip()
