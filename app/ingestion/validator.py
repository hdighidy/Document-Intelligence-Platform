from pathlib import Path

import fitz


class PDFValidationError(Exception):
    pass


def validate_pdf(file_path: Path, max_size_mb: int = 50) -> None:

    if not file_path.exists():
        raise PDFValidationError("File does not exist.")

    if file_path.suffix.lower() != ".pdf":
        raise PDFValidationError("Only PDF files are allowed.")

    max_size_bytes = max_size_mb * 1024 * 1024

    if file_path.stat().st_size > max_size_bytes:
        raise PDFValidationError(
            f"PDF exceeds maximum allowed size of {max_size_mb} MB."
        )

    try:
        document = fitz.open(file_path)

        if document.page_count == 0:
            raise PDFValidationError("PDF contains no pages.")

        document.close()

    except Exception as exc:
        raise PDFValidationError(
            f"Invalid or corrupted PDF: {exc}"
        ) from exc