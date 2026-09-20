"""
PDF Table Extraction
====================

Phase 3.1.3

Responsibilities:
    - Open the PDF
    - Use the tables detected by Phase 3.1.2
    - Extract table cells
    - Preserve row / column positions
    - Build Table and TableCell objects
    - Identify basic headers
    - Preserve table bounding boxes

Important:
    This module does NOT independently detect tables.

    Detection is handled by:
        app.extraction.table_detector

    Extraction operates on the detected table
    locations supplied by the detector.
"""

from pathlib import Path

import pdfplumber

from app.models.table import (
    BoundingBox,
    Table,
    TableCell,
    TableMetadata,
)


# ============================================================
# PUBLIC API
# ============================================================


def extract_tables(
    pdf_path: Path,
    detected_tables: list[TableMetadata],
) -> list[Table]:
    """
    Extract the contents of previously detected tables.

    Args:
        pdf_path:
            Path to the source PDF.

        detected_tables:
            Tables returned by table_detector.py.

    Returns:
        List of fully populated Table objects.
    """

    if not detected_tables:
        return []

    extracted_tables: list[Table] = []

    with pdfplumber.open(
        pdf_path
    ) as pdf:

        for metadata in detected_tables:

            table = extract_single_table(
                pdf=pdf,
                metadata=metadata,
            )

            if table is not None:

                extracted_tables.append(
                    table
                )

    return extracted_tables


# ============================================================
# SINGLE TABLE
# ============================================================


def extract_single_table(
    pdf,
    metadata: TableMetadata,
) -> Table | None:
    """
    Extract one previously detected table.

    The table is located using:

        metadata.page_number
        metadata.bbox
    """

    page_index = (
        metadata.page_number - 1
    )

    if page_index < 0:

        return None

    if page_index >= len(pdf.pages):

        return None

    page = pdf.pages[
        page_index
    ]

    # --------------------------------------------------------
    # Find the exact detected table
    # --------------------------------------------------------

    detected_table = (
        find_matching_table(
            page=page,
            metadata=metadata,
        )
    )

    if detected_table is None:

        return None

    # --------------------------------------------------------
    # Extract raw table data
    # --------------------------------------------------------

    raw_table = (
        detected_table.extract()
    )

    if not raw_table:

        return None

    # --------------------------------------------------------
    # Clean table rows
    # --------------------------------------------------------

    cleaned_rows = (
        clean_rows(
            raw_table
        )
    )

    if not cleaned_rows:

        return None

    # --------------------------------------------------------
    # Determine dimensions
    # --------------------------------------------------------

    row_count = len(
        cleaned_rows
    )

    column_count = max(
        (
            len(row)
            for row in cleaned_rows
        ),
        default=0,
    )

    # --------------------------------------------------------
    # Determine headers
    # --------------------------------------------------------

    headers = extract_headers(
        cleaned_rows
    )

    # --------------------------------------------------------
    # Build cells
    # --------------------------------------------------------

    cells = build_cells(
        page=page,
        detected_table=detected_table,
        rows=cleaned_rows,
        headers=headers,
    )

    # --------------------------------------------------------
    # Build Table
    # --------------------------------------------------------

    table = Table(

        table_id=metadata.table_id,

        document_id=metadata.document_id,

        page_number=metadata.page_number,

        metadata=metadata,

        cells=cells,

        row_count=row_count,

        column_count=column_count,

        headers=headers,

        rows=cleaned_rows,

        extraction_method=(
            metadata.extraction_method
        ),

    )

    return table


# ============================================================
# MATCH DETECTED TABLE
# ============================================================


def find_matching_table(
    page,
    metadata: TableMetadata,
):
    """
    Find the same table detected during
    Phase 3.1.2.

    Matching is performed using the
    table bounding box.
    """

    if metadata.bbox is None:

        return None

    target = metadata.bbox

    tables = page.find_tables()

    if not tables:

        return None

    best_match = None

    best_distance = float(
        "inf"
    )

    for table in tables:

        bbox = table.bbox

        distance = (

            abs(
                bbox[0]
                - target.x0
            )

            +

            abs(
                bbox[1]
                - target.y0
            )

            +

            abs(
                bbox[2]
                - target.x1
            )

            +

            abs(
                bbox[3]
                - target.y1
            )

        )

        if distance < best_distance:

            best_distance = (
                distance
            )

            best_match = table

    return best_match


# ============================================================
# CLEAN ROWS
# ============================================================


def clean_rows(
    rows: list,
) -> list[list[str]]:
    """
    Normalize extracted table rows.

    Converts:
        None -> ""

    and:
        non-string values -> str
    """

    cleaned: list[
        list[str]
    ] = []

    for row in rows:

        if row is None:

            continue

        cleaned_row = []

        for cell in row:

            if cell is None:

                cleaned_row.append("")

            else:

                value = str(
                    cell
                ).strip()

                cleaned_row.append(
                    value
                )

        # Skip completely empty rows

        if any(
            value != ""
            for value in cleaned_row
        ):

            cleaned.append(
                cleaned_row
            )

    return cleaned


# ============================================================
# HEADER DETECTION
# ============================================================


def extract_headers(
    rows: list[list[str]],
) -> list[str]:
    """
    Basic header detection.

    Current strategy:
        First non-empty row = header.

    More advanced header detection
    will be introduced later.
    """

    if not rows:

        return []

    first_row = rows[0]

    if not any(
        cell.strip()
        for cell in first_row
    ):

        return []

    return [
        cell.strip()
        for cell in first_row
    ]


# ============================================================
# BUILD CELLS
# ============================================================


def build_cells(
    page,
    detected_table,
    rows: list[list[str]],
    headers: list[str],
) -> list[TableCell]:
    """
    Build TableCell objects.

    We preserve the row / column coordinates
    and attempt to preserve cell bounding boxes.
    """

    cells: list[
        TableCell
    ] = []

    # --------------------------------------------------------
    # Extract table cell bounding boxes
    # --------------------------------------------------------

    bbox_matrix = (
        get_cell_bboxes(
            detected_table
        )
    )

    for row_index, row in enumerate(
        rows
    ):

        for column_index, text in enumerate(
            row
        ):

            cell_bbox = None

            if (
                row_index
                < len(bbox_matrix)
            ):

                row_bboxes = (
                    bbox_matrix[
                        row_index
                    ]
                )

                if (
                    column_index
                    < len(row_bboxes)
                ):

                    raw_bbox = (
                        row_bboxes[
                            column_index
                        ]
                    )

                    if raw_bbox:

                        cell_bbox = (
                            BoundingBox(
                                x0=float(
                                    raw_bbox[0]
                                ),
                                y0=float(
                                    raw_bbox[1]
                                ),
                                x1=float(
                                    raw_bbox[2]
                                ),
                                y1=float(
                                    raw_bbox[3]
                                ),
                            )
                        )

            is_header = (
                row_index == 0
                and bool(headers)
            )

            cells.append(
                TableCell(

                    row_index=row_index,

                    column_index=column_index,

                    text=text,

                    bbox=cell_bbox,

                    is_header=is_header,

                )
            )

    return cells


# ============================================================
# CELL BOUNDING BOXES
# ============================================================


def get_cell_bboxes(
    detected_table,
) -> list[list]:
    """
    Retrieve cell bounding boxes from
    pdfplumber's detected table.

    pdfplumber normally exposes:

        table.cells

    as a flat list of cell bounding boxes.

    We convert them into row/column
    structure using table.rows.
    """

    if not getattr(
        detected_table,
        "cells",
        None,
    ):

        return []

    rows = getattr(
        detected_table,
        "rows",
        None,
    )

    if not rows:

        return []

    matrix = []

    for row in rows:

        row_bboxes = []

        for cell in row.cells:

            row_bboxes.append(
                cell
            )

        matrix.append(
            row_bboxes
        )

    return matrix