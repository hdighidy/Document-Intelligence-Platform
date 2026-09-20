
"""
Document Ingestion Service
==========================

Phase 1 + Phase 2.2

Responsibilities:
    1. Validate uploaded PDF
    2. Generate unique Document ID
    3. Calculate SHA-256 hash
    4. Store original PDF
    5. Extract PDF metadata
    6. Extract text blocks
    7. Analyze document structure
    8. Save processed text
    9. Register document
    10. Save document metadata

This service is the main orchestration layer.

It does NOT:
    - Perform OCR
    - Extract tables
    - Extract images
    - Generate embeddings
    - Perform RAG
"""

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import uuid

from app.config import settings

from app.extraction.structure_analyzer import (
    analyze_document_structure,
)

from app.extraction.table_pipeline import (
    extract_document_tables,
)

from app.extraction.text_extractor import (
    extract_text_from_pdf,
)

from app.ingestion.metadata import (
    extract_pdf_metadata,
)

from app.ingestion.validator import (
    validate_pdf,
)

from app.models.document import (
    DocumentMetadata,
    ProcessingStatus,
)

from app.storage.document_storage import (
    save_extracted_tables,
    save_extracted_text,
)

from app.storage.registry import (
    get_document_by_sha256,
    register_document,
)


# ============================================================
# DOCUMENT ID
# ============================================================


def generate_document_id() -> str:
    """
    Generate a unique Document ID.

    Example:
        DOC-A91F72C83B41
    """
    prefix = "INV-" 

    return (
        f"{prefix}{uuid.uuid4().hex[:12].upper()}"
    )


# ============================================================
# SHA-256
# ============================================================


def calculate_sha256(
    file_path: Path,
) -> str:
    """
    Calculate SHA-256 hash of a file.

    Used for:
        - File integrity
        - Duplicate detection
        - Document traceability
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb",
    ) as file:

        while chunk := file.read(
            1024 * 1024
        ):

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ============================================================
# SAVE DOCUMENT METADATA
# ============================================================


def save_document_metadata(
    document: DocumentMetadata,
) -> None:
    """
    Save document metadata as JSON.
    """

    settings.metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_file = (
        settings.metadata_dir
        / f"{document.document_id}.json"
    )

    metadata_file.write_text(
        json.dumps(
            document.model_dump(
                mode="json"
            ),
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# MAIN INGESTION FUNCTION
# ============================================================


def ingest_pdf(
    source_file: Path,
    original_filename: str,
) -> DocumentMetadata:
    """
    Complete PDF ingestion pipeline.

    Pipeline:

        PDF
         ↓
        Validate
         ↓
        Generate Document ID
         ↓
        SHA-256
         ↓
        Store Original PDF
         ↓
        Extract Metadata
         ↓
        Extract Text
         ↓
        Analyze Structure
         ↓
        Save pages.json
         ↓
        Register Document
         ↓
        Save Metadata
    """

    # ========================================================
    # 1. Validate PDF
    # ========================================================

    validate_pdf(
        source_file,
        max_size_mb=settings.max_file_size_mb,
    )

    # ========================================================
    # 2. Generate Document ID
    # ========================================================

    document_id = (
        generate_document_id()
    )

    # ========================================================
    # 3. Calculate SHA-256
    # ========================================================

    sha256 = (
        calculate_sha256(
            source_file
        )
    )

    # ========================================================
    # 3.5 Deduplication Check
    # ========================================================
    #
    # If a document with identical content (same SHA-256) has
    # already been ingested, return the existing record instead
    # of creating a duplicate copy. This makes upload idempotent
    # for repeated uploads of the same file, and avoids
    # duplicate content later ending up in retrieval/indexing.

    existing_document = (
        get_document_by_sha256(sha256)
    )

    if existing_document is not None:
        return existing_document

    # ========================================================
    # 4. Create Document Storage Directory
    # ========================================================

    document_dir = (
        settings.raw_dir
        / document_id
    )

    document_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 5. Save Original PDF
    # ========================================================

    destination = (
        document_dir
        / "original.pdf"
    )

    shutil.copy2(
        source_file,
        destination,
    )

    # ========================================================
    # 6. Extract PDF Metadata
    # ========================================================

    pdf_metadata = (
        extract_pdf_metadata(
            destination
        )
    )

    # ========================================================
    # 7. Extract Text
    # ========================================================

    pages = (
        extract_text_from_pdf(
            destination
        )
    )

    # ========================================================
    # 8. Analyze Document Structure
    # ========================================================

    pages = (
        analyze_document_structure(
            pages
        )
    )

    # ========================================================
    # 9. Save Extracted Text + Structure
    # ========================================================

    save_extracted_text(
        document_id=document_id,
        pages=pages,
    )

    # ========================================================
    # 9.5 Extract Tables
    # ========================================================
    #
    # Table extraction is treated as best-effort enrichment,
    # not a hard requirement for ingestion to succeed. A bug or
    # an unusual layout in the table pipeline should not prevent
    # the document's text content from being ingested and usable.

    try:
        tables = extract_document_tables(
            pdf_path=destination,
            document_id=document_id,
        )

    except Exception as exc:
        print(
            f"Warning: table extraction failed for "
            f"{document_id}: {exc}"
        )
        tables = []

    if tables:
        save_extracted_tables(
            document_id=document_id,
            tables=tables,
        )

    final_status = (
        ProcessingStatus.TABLES_EXTRACTED
        if tables
        else ProcessingStatus.TEXT_EXTRACTED
    )

    # ========================================================
    # 10. Create Document Metadata
    # ========================================================

    document_metadata = DocumentMetadata(

        document_id=document_id,

        original_filename=original_filename,

        stored_filename="original.pdf",

        file_path=str(
            destination
        ),

        file_size_bytes=(
            destination.stat().st_size
        ),

        sha256=sha256,

        uploaded_at=(
            datetime.now(
                timezone.utc
            )
        ),

        status=(
            final_status
        ),

        pdf=pdf_metadata,

        table_count=len(tables),
    )

    # ========================================================
    # 11. Register Document
    # ========================================================

    register_document(
        document_metadata
    )

    # ========================================================
    # 12. Save Document Metadata
    # ========================================================

    save_document_metadata(
        document_metadata
    )

    # ========================================================
    # 13. Return Result
    # ========================================================

    return document_metadata