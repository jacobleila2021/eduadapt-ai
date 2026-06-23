"""
Extract plain text from teacher-uploaded lesson files (PDF and DOCX).
"""

from io import BytesIO

from docx import Document
from pypdf import PdfReader

# Strip bytes that break Word export and other XML pipelines.
import re

_BAD_TEXT_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufeff]")


def _clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    return _BAD_TEXT_CHARS.sub("", text).replace("\x00", "")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Read every page of a PDF and return combined plain text.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Extracted text with page breaks marked for readability.
    """
    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"--- Page {index} ---\n{page_text.strip()}")

    return _clean_extracted_text("\n\n".join(pages))


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Read paragraphs from a Word document and return plain text.

    Args:
        file_bytes: Raw bytes of the uploaded DOCX file.

    Returns:
        Paragraphs joined with blank lines between them.
    """
    document = Document(BytesIO(file_bytes))
    paragraphs = [para.text.strip() for para in document.paragraphs if para.text.strip()]
    return _clean_extracted_text("\n\n".join(paragraphs))


def extract_lesson_text(filename: str, file_bytes: bytes) -> str:
    """
    Route extraction to the correct parser based on file extension.

    Args:
        filename: Original upload filename (used for extension check).
        file_bytes: Raw file content.

    Returns:
        Extracted lesson text.

    Raises:
        ValueError: If the file type is not PDF or DOCX.
    """
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)

    raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")
