"""
Document parser: converts uploaded files into plain text.

Supported formats (Phase 1):
  - PDF   → PyMuPDF (fast, no external process)
  - TXT   → direct read
  - MD    → direct read (treated as plain text)

Phase 2 will add image/OCR support via pytesseract.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def parse_document(file_path: str | Path) -> str:
    """
    Extract raw text from a document file.

    Args:
        file_path: Absolute or relative path to the uploaded file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file extension is not supported.
        RuntimeError: If parsing fails.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {SUPPORTED_EXTENSIONS}"
        )

    logger.info("Parsing document: %s (type=%s)", path.name, ext)

    if ext == ".pdf":
        return _parse_pdf(path)
    else:
        return _parse_text(path)


def _parse_pdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise RuntimeError("PyMuPDF is not installed. Run: uv add PyMuPDF") from e

    text_parts: list[str] = []
    with fitz.open(str(path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(page_text)
            else:
                logger.debug("Page %d appears to have no selectable text (may need OCR)", page_num)

    full_text = "\n".join(text_parts)
    if not full_text.strip():
        raise RuntimeError(
            f"No text could be extracted from '{path.name}'. "
            "The PDF may be scanned — OCR support is coming in Phase 2."
        )

    return full_text


def _parse_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
