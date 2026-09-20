"""
PDF Table Detection
===================

Phase 3.1.2

Responsibilities:
    - Detect possible tables in a PDF
    - Identify table bounding boxes
    - Return table locations
    - Create TableMetadata objects

This module DOES NOT extract table contents.

Extraction will be implemented in Phase 3.1.3.
"""

from pathlib import Path
from uuid import uuid4

import pdfplumber

from app.models.table import (
    BoundingBox,
    TableMetadata,
)


# ============================================================
# TABLE DETECTION
# ============================================================


def detect_tables(
    pdf_path: Path,
    document_id: str,
) -> list[TableMetadata]:
    """
    Detect tables throughout a PDF.

    Args:
        pdf_path:
            Path to the PDF file.

        document_id:
            ID of the document being processed.

    Returns:
        List of TableMetadata objects.
    """

    detected_tables: list[
        TableMetadata
    ] = []

    with pdfplumber.open(
        pdf_path
    ) as pdf:

        for page_number, page in enumerate(
            pdf.pages,
            start=1,
        ):

            page_tables = detect_tables_on_page(
                page=page,
                document_id=document_id,
                page_number=page_number,
                source_filename=pdf_path.name,
            )

            detected_tables.extend(
                page_tables
            )

    return detected_tables


# ============================================================
# PAGE TABLE DETECTION
# ============================================================


def detect_tables_on_page(
    page,
    document_id: str,
    page_number: int,
    source_filename: str | None = None,
) -> list[TableMetadata]:
    """
    Detect tables on a single PDF page.

    Returns:
        List of detected table metadata.
    """

    tables: list[
        TableMetadata
    ] = []

    try:

        table_objects = (
            page.find_tables()
        )

    except Exception as exc:

        print(
            f"Warning: table detection "
            f"failed on page "
            f"{page_number}: {exc}"
        )

        return tables

    for table_object in table_objects:

        bbox = table_object.bbox

        table_id = generate_table_id()

        metadata = TableMetadata(

            document_id=document_id,

            table_id=table_id,

            page_number=page_number,

            bbox=BoundingBox(
                x0=float(bbox[0]),
                y0=float(bbox[1]),
                x1=float(bbox[2]),
                y1=float(bbox[3]),
            ),

            extraction_method=(
                "pdfplumber"
            ),

            source_filename=(
                source_filename
            ),
        )

        tables.append(
            metadata
        )

    return tables


# ============================================================
# TABLE ID
# ============================================================


def generate_table_id() -> str:
    """
    Generate a unique table ID.

    Example:
        TABLE-A91F72C83B41
    """

    return (
        f"TABLE-"
        f"{uuid4().hex[:12].upper()}"
    )