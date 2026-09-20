"""
Table Cleaning & Normalization
==============================

Phase 3.1.4
Phase 3.1.4.1 — Intelligent Header & Title Detection
Phase 3.1.4.2 — Multi-line Cell Reconstruction
Phase 3.1.4.3 — Intelligent Data Type & Semantic Normalization

Responsibilities
----------------

Phase 3.1.4
    - Clean cell whitespace
    - Normalize line breaks
    - Normalize Unicode whitespace
    - Detect empty cells
    - Normalize row lengths
    - Detect duplicate rows
    - Detect basic data types
    - Detect numeric values
    - Preserve raw extracted values

Phase 3.1.4.2
    - Reconstruct multi-line cell content
    - Preserve raw_text
    - Store reconstructed text in normalized_text

Phase 3.1.4.3
    - Detect semantic data types
    - Normalize numbers
    - Normalize percentages
    - Normalize dates
    - Normalize currencies
    - Normalize status values
    - Detect engineering identifiers
    - Preserve original extracted values

Important
---------

This module:

    DOES NOT perform PDF extraction.
    DOES NOT perform OCR.
    DOES NOT perform spelling correction.

raw_text is always preserved.

Pipeline
--------

    Extracted Table
          |
          v
    Synchronize rows -> cells
          |
          v
    Basic cell cleaning
          |
          v
    Multi-line reconstruction
          |
          v
    Semantic normalization
          |
          v
    Synchronize cells -> rows
          |
          v
    Header cleaning
          |
          v
    Statistics
          |
          v
    Cleaned / Normalized Table
"""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from datetime import datetime

from app.models.table import (
    Table,
    TableCell,
)

from app.extraction.multiline_cell_reconstructor import (
    reconstruct_multiline_cells,
)

from app.extraction.table_value_normalizer import (
    normalize_table_values,
)


# ============================================================
# PUBLIC API
# ============================================================


def clean_table(
    table: Table,
) -> Table:
    """
    Complete Phase 3.1.4 table cleaning pipeline.

    The original Table object is never modified.

    Pipeline:

        1. Deep-copy source table
        2. Synchronize rows -> cells
        3. Clean individual cells
        4. Reconstruct multi-line cells
        5. Perform semantic normalization
        6. Synchronize cells -> rows
        7. Normalize row lengths
        8. Clean headers
        9. Calculate statistics
        10. Mark table as cleaned
        11. Return cleaned table
    """

    # ========================================================
    # 1. SAFE COPY
    # ========================================================

    cleaned_table = deepcopy(
        table
    )

    # ========================================================
    # 2. CRITICAL SYNCHRONIZATION
    # ========================================================
    #
    # The PDF extractor may populate:
    #
    #     table.rows
    #
    # while TableCell objects contain empty values.
    #
    # We therefore make Table.rows the source for populating
    # missing TableCell values before any cell-level processing.
    #
    # Existing non-empty raw_text values are preserved.
    #
    # ========================================================

    cleaned_table = synchronize_cells_from_rows(
        cleaned_table
    )

    # ========================================================
    # 3. BASIC CELL CLEANING
    # ========================================================

    for cell in cleaned_table.cells:

        clean_cell(
            cell
        )

    # ========================================================
    # 4. MULTI-LINE CELL RECONSTRUCTION
    # ========================================================
    #
    # Example:
    #
    #     "Air Handlig\nunit"
    #
    # becomes:
    #
    #     "Air Handlig unit"
    #
    # while:
    #
    #     raw_text
    #
    # remains:
    #
    #     "Air Handlig\nunit"
    #
    # ========================================================

    cleaned_table = reconstruct_multiline_cells(
        cleaned_table
    )

    # ========================================================
    # 5. INTELLIGENT SEMANTIC NORMALIZATION
    # ========================================================
    #
    # Examples:
    #
    #     "1,250,000"
    #          ->
    #     1250000
    #
    #     "26-05-2025"
    #          ->
    #     "2025-05-26"
    #
    #     "Done"
    #          ->
    #     "DONE"
    #
    #     "AHU-B50"
    #          ->
    #     identifier
    #
    # raw_text is never modified.
    #
    # ========================================================

    cleaned_table = normalize_table_values(
        cleaned_table
    )

    # ========================================================
    # 6. SYNCHRONIZE CELLS -> ROWS
    # ========================================================
    #
    # After reconstruction and semantic normalization,
    # rebuild the row matrix from the cell representation.
    #
    # Human-readable rows use:
    #
    #     normalized_text
    #
    # rather than:
    #
    #     normalized_value
    #
    # This prevents values such as dates/numbers from
    # unexpectedly replacing the table display representation.
    #
    # ========================================================

    cleaned_table = synchronize_rows_from_cells(
        cleaned_table
    )

    # ========================================================
    # 7. NORMALIZE ROW LENGTHS
    # ========================================================

    cleaned_table.rows = normalize_rows(
        cleaned_table.rows,
        cleaned_table.column_count,
    )

    # ========================================================
    # 8. CLEAN HEADERS
    # ========================================================

    cleaned_table.headers = clean_headers(
        cleaned_table.headers
    )

    # ========================================================
    # 9. STATISTICS
    # ========================================================

    cleaned_table.empty_cell_count = sum(
        1
        for cell in cleaned_table.cells
        if not get_cell_value(cell)
    )

    cleaned_table.duplicate_row_count = (
        count_duplicate_rows(
            cleaned_table.rows
        )
    )

    # ========================================================
    # 10. CLEANING STATUS
    # ========================================================

    cleaned_table.cleaning_applied = True

    # ========================================================
    # 11. NORMALIZATION VERSION
    # ========================================================

    if hasattr(
        cleaned_table,
        "normalization_version",
    ):

        cleaned_table.normalization_version = (
            "3.1.4.3"
        )

    # ========================================================
    # RETURN
    # ========================================================

    return cleaned_table


# ============================================================
# ROW -> CELL SYNCHRONIZATION
# ============================================================


def synchronize_cells_from_rows(
    table: Table,
) -> Table:
    """
    Synchronize Table.rows into Table.cells.

    This fixes the situation where extraction produces:

        table.rows
            populated

        table.cells
            empty

    Existing non-empty raw_text values are preserved.

    Empty cells are created where necessary.

    Returns:
        The same Table object.
    """

    if not table.rows:
        return table

    # --------------------------------------------------------
    # Determine dimensions from rows
    # --------------------------------------------------------

    row_count = len(
        table.rows
    )

    column_count = max(
        (
            len(row)
            for row in table.rows
        ),
        default=0,
    )

    if column_count <= 0:
        return table

    # --------------------------------------------------------
    # Existing cells
    # --------------------------------------------------------

    existing_cells = {
        (
            cell.row_index,
            cell.column_index,
        ): cell
        for cell in table.cells
    }

    synchronized_cells = []

    # --------------------------------------------------------
    # Build cells from rows
    # --------------------------------------------------------

    for row_index, row in enumerate(
        table.rows
    ):

        for column_index in range(
            column_count
        ):

            value = ""

            if column_index < len(row):

                raw_value = row[
                    column_index
                ]

                if raw_value is not None:

                    value = str(
                        raw_value
                    )

            cell = existing_cells.get(
                (
                    row_index,
                    column_index,
                )
            )

            # ------------------------------------------------
            # Existing cell
            # ------------------------------------------------

            if cell is not None:

                # Preserve valid extracted raw_text.
                if not cell.raw_text and value:

                    cell.raw_text = value

                # Populate text only when currently empty.
                if not cell.text and value:

                    cell.text = value

            # ------------------------------------------------
            # Missing cell
            # ------------------------------------------------

            else:

                cell = TableCell(
                    row_index=row_index,
                    column_index=column_index,
                    raw_text=value,
                    text=value,
                )

            synchronized_cells.append(
                cell
            )

    table.cells = synchronized_cells

    return table


# ============================================================
# CELL -> ROW SYNCHRONIZATION
# ============================================================


def synchronize_rows_from_cells(
    table: Table,
) -> Table:
    """
    Rebuild Table.rows from TableCell values.

    Display priority:

        normalized_text
            ↓
        text
            ↓
        raw_text
            ↓
        ""

    IMPORTANT:

        normalized_value is intentionally NOT used for
        the display row matrix.

    Example:

        normalized_text:
            "Air Handlig unit"

        normalized_value:
            "Air Handlig unit"

        row value:
            "Air Handlig unit"

    Numeric example:

        text:
            "1,250,000"

        normalized_value:
            1250000

        row value:
            "1,250,000"

    This keeps the human-readable table representation
    separate from machine-readable semantic values.
    """

    if not table.cells:
        return table

    # --------------------------------------------------------
    # Determine dimensions
    # --------------------------------------------------------

    row_count = max(
        (
            cell.row_index
            for cell in table.cells
        ),
        default=-1,
    ) + 1

    column_count = max(
        (
            cell.column_index
            for cell in table.cells
        ),
        default=-1,
    ) + 1

    if row_count <= 0:
        return table

    if column_count <= 0:
        return table

    # --------------------------------------------------------
    # Create matrix
    # --------------------------------------------------------

    rows = [
        ["" for _ in range(column_count)]
        for _ in range(row_count)
    ]

    # --------------------------------------------------------
    # Populate matrix
    # --------------------------------------------------------

    for cell in table.cells:

        value = get_cell_display_value(
            cell
        )

        # Safety check
        if cell.row_index < 0:
            continue

        if cell.column_index < 0:
            continue

        if cell.row_index >= row_count:
            continue

        if cell.column_index >= column_count:
            continue

        rows[
            cell.row_index
        ][
            cell.column_index
        ] = value

    table.rows = rows

    return table


# ============================================================
# CELL DISPLAY VALUE
# ============================================================


def get_cell_display_value(
    cell: TableCell,
) -> str:
    """
    Return the best human-readable representation
    of a TableCell.

    Priority:

        normalized_text
        text
        raw_text
        ""

    normalized_value is deliberately excluded because
    it is intended for machine-readable semantic use.
    """

    normalized_text = getattr(
        cell,
        "normalized_text",
        None,
    )

    if normalized_text is not None:

        value = str(
            normalized_text
        ).strip()

        if value:
            return value

    text = getattr(
        cell,
        "text",
        None,
    )

    if text is not None:

        value = str(
            text
        ).strip()

        if value:
            return value

    raw_text = getattr(
        cell,
        "raw_text",
        None,
    )

    if raw_text is not None:

        value = str(
            raw_text
        ).strip()

        if value:
            return value

    return ""


# ============================================================
# CELL VALUE HELPER
# ============================================================


def get_cell_value(
    cell: TableCell,
) -> str:
    """
    Return the best available value for statistics.

    Priority:

        normalized_text
        text
        raw_text
        ""

    This is intentionally based on textual content.
    """

    return get_cell_display_value(
        cell
    )


# ============================================================
# BASIC CELL CLEANING
# ============================================================


def clean_cell(
    cell: TableCell,
) -> None:
    """
    Clean one TableCell in-place.

    Operations:

        - Preserve raw_text
        - Unicode normalization
        - Normalize line breaks
        - Normalize tabs
        - Normalize whitespace
        - Remove surrounding whitespace
        - Detect basic data type
    """

    # --------------------------------------------------------
    # Preserve original extracted value
    # --------------------------------------------------------

    if cell.raw_text is None:

        cell.raw_text = (
            cell.text
            if cell.text is not None
            else ""
        )

    # --------------------------------------------------------
    # Empty cell
    # --------------------------------------------------------

    if not cell.raw_text:

        cell.text = ""

        cell.data_type = "empty"

        cell.numeric_value = None

        return

    # --------------------------------------------------------
    # Convert to string
    # --------------------------------------------------------

    value = str(
        cell.raw_text
    )

    # --------------------------------------------------------
    # Unicode normalization
    # --------------------------------------------------------

    value = unicodedata.normalize(
        "NFKC",
        value,
    )

    # --------------------------------------------------------
    # Normalize line breaks / tabs
    # --------------------------------------------------------

    value = re.sub(
        r"[\r\n\t]+",
        " ",
        value,
    )

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    # --------------------------------------------------------
    # Strip
    # --------------------------------------------------------

    value = value.strip()

    # --------------------------------------------------------
    # Store cleaned text
    # --------------------------------------------------------

    cell.text = value

    # --------------------------------------------------------
    # Basic type detection
    # --------------------------------------------------------

    data_type, numeric_value = detect_data_type(
        value
    )

    cell.data_type = data_type

    cell.numeric_value = numeric_value


# ============================================================
# HEADER CLEANING
# ============================================================


def clean_headers(
    headers: list[str],
) -> list[str]:
    """
    Clean table headers.

    Operations:

        - Unicode normalization
        - Line-break normalization
        - Whitespace normalization
        - Strip surrounding whitespace
    """

    if not headers:
        return []

    cleaned = []

    for header in headers:

        if header is None:

            value = ""

        else:

            value = unicodedata.normalize(
                "NFKC",
                str(header),
            )

        value = re.sub(
            r"[\r\n\t]+",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip()

        cleaned.append(
            value
        )

    return cleaned


# ============================================================
# ROW NORMALIZATION
# ============================================================


def normalize_rows(
    rows: list[list[str]],
    expected_columns: int,
) -> list[list[str]]:
    """
    Normalize row lengths.

    Short rows are padded.

    Long rows are preserved and are NOT silently truncated.
    """

    if not rows:
        return []

    normalized = []

    for row in rows:

        if row is None:
            row = []

        cleaned_row = []

        for value in row:

            if value is None:

                value = ""

            else:

                value = unicodedata.normalize(
                    "NFKC",
                    str(value),
                )

            value = re.sub(
                r"[\r\n\t]+",
                " ",
                value,
            )

            value = re.sub(
                r"\s+",
                " ",
                value,
            )

            cleaned_row.append(
                value.strip()
            )

        # ----------------------------------------------------
        # Pad short rows
        # ----------------------------------------------------

        if len(cleaned_row) < expected_columns:

            cleaned_row.extend(
                [
                    ""
                    for _ in range(
                        expected_columns
                        - len(cleaned_row)
                    )
                ]
            )

        normalized.append(
            cleaned_row
        )

    return normalized


# ============================================================
# BASIC DATA TYPE DETECTION
# ============================================================


def detect_data_type(
    value: str,
) -> tuple[str, float | None]:
    """
    Detect basic data type.

    Returns:

        ("empty", None)
        ("integer", number)
        ("float", number)
        ("percentage", number)
        ("string", None)
    """

    if not value:

        return (
            "empty",
            None,
        )

    normalized = value.strip()

    # --------------------------------------------------------
    # Percentage
    # --------------------------------------------------------

    percentage_match = re.fullmatch(
        r"[-+]?\d+(?:\.\d+)?\s*%",
        normalized,
    )

    if percentage_match:

        numeric = float(
            normalized
            .replace(
                "%",
                "",
            )
            .strip()
        )

        return (
            "percentage",
            numeric,
        )

    # --------------------------------------------------------
    # Remove numeric separators
    # --------------------------------------------------------

    numeric_candidate = (
        normalized
        .replace(
            ",",
            "",
        )
        .replace(
            " ",
            "",
        )
    )

    # --------------------------------------------------------
    # Integer
    # --------------------------------------------------------

    if re.fullmatch(
        r"[-+]?\d+",
        numeric_candidate,
    ):

        return (
            "integer",
            float(
                numeric_candidate
            ),
        )

    # --------------------------------------------------------
    # Float
    # --------------------------------------------------------

    if re.fullmatch(
        r"[-+]?(?:\d+\.\d*|\.\d+)",
        numeric_candidate,
    ):

        return (
            "float",
            float(
                numeric_candidate
            ),
        )

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    return (
        "string",
        None,
    )


# ============================================================
# DUPLICATE ROW DETECTION
# ============================================================


def count_duplicate_rows(
    rows: list[list[str]],
) -> int:
    """
    Count duplicate rows.

    The first occurrence is not counted as a duplicate.
    """

    if not rows:
        return 0

    seen = set()

    duplicates = 0

    for row in rows:

        key = tuple(
            str(cell or "")
            .strip()
            .lower()
            for cell in row
        )

        if key in seen:

            duplicates += 1

        else:

            seen.add(
                key
            )

    return duplicates