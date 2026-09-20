"""
Multi-line Cell Reconstruction
==============================

Phase 3.1.4.2

Purpose
-------

Reconstruct logical text values that have been split across
multiple lines during PDF table extraction.

Example:

    Raw:
        "Air Handling\\nUnit"

    Normalized:
        "Air Handling Unit"

Important
---------

This module does NOT destroy the original extracted value.

The original value remains available through:

    TableCell.raw_text

The reconstructed value is stored in:

    TableCell.normalized_text

The function returns a NEW Table object.
"""

from __future__ import annotations

import re
from copy import deepcopy

from app.models.table import Table


# ============================================================
# PUBLIC API
# ============================================================


def reconstruct_multiline_cells(
    table: Table,
) -> Table:
    """
    Reconstruct multi-line cell values.

    The original Table is not modified.

    Returns
    -------
    Table
        Deep-copied table containing reconstructed values.
    """

    result = deepcopy(table)

    # --------------------------------------------------------
    # Process every cell
    # --------------------------------------------------------

    for cell in result.cells:

        # Preserve original extracted value.
        source_text = (
            cell.raw_text
            or cell.text
            or ""
        )

        # Empty cell
        if not source_text:
            cell.normalized_text = ""
            cell.is_multiline = False
            continue

        # Detect whether original value contained
        # multiple physical lines.
        cell.is_multiline = has_multiple_lines(
            source_text
        )

        # Reconstruct logical value.
        reconstructed = reconstruct_cell_text(
            source_text
        )

        # Store reconstructed value.
        cell.normalized_text = reconstructed

    # --------------------------------------------------------
    # Count multiline cells
    # --------------------------------------------------------

    result.multiline_cells_detected = sum(
        1
        for cell in result.cells
        if cell.is_multiline
    )

    # --------------------------------------------------------
    # Rebuild row matrix
    # --------------------------------------------------------

    result.rows = rebuild_rows_from_cells(
        result
    )

    # --------------------------------------------------------
    # Rebuild data rows
    # --------------------------------------------------------

    if result.header_row_index is not None:

        result.data_rows = (
            extract_data_rows_from_cells(
                result
            )
        )

    else:

        result.data_rows = []

    return result


# ============================================================
# MULTI-LINE DETECTION
# ============================================================


def has_multiple_lines(
    text: str,
) -> bool:
    """
    Determine whether a cell contains multiple
    physical text lines.
    """

    if not text:
        return False

    return (
        "\n" in text
        or "\r" in text
    )


# ============================================================
# CELL RECONSTRUCTION
# ============================================================


def reconstruct_cell_text(
    text: str,
) -> str:
    """
    Convert a multi-line logical value into one
    normalized text value.

    Example
    -------

        Air Handling
        Unit

    becomes:

        Air Handling Unit
    """

    if not text:
        return ""

    # --------------------------------------------------------
    # Normalize newline variants
    # --------------------------------------------------------

    normalized = (
        str(text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # --------------------------------------------------------
    # Split into logical lines
    # --------------------------------------------------------

    lines = [
        line.strip()
        for line in normalized.split("\n")
        if line.strip()
    ]

    if not lines:
        return ""

    # --------------------------------------------------------
    # Single line
    # --------------------------------------------------------

    if len(lines) == 1:

        return normalize_spaces(
            lines[0]
        )

    # --------------------------------------------------------
    # Multiple lines
    # --------------------------------------------------------

    return normalize_spaces(
        " ".join(lines)
    )


# ============================================================
# SPACE NORMALIZATION
# ============================================================


def normalize_spaces(
    text: str,
) -> str:
    """
    Collapse repeated whitespace.

    Example:

        "Air    Handling   Unit"

    becomes:

        "Air Handling Unit"
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


# ============================================================
# TABLE ROW REBUILDING
# ============================================================


def rebuild_rows_from_cells(
    table: Table,
) -> list[list[str]]:
    """
    Rebuild table.rows from TableCell objects.

    Priority:

        normalized_text
            ↓
        text
            ↓
        raw_text
            ↓
        empty string
    """

    if not table.cells:

        return table.rows

    # --------------------------------------------------------
    # Determine dimensions
    # --------------------------------------------------------

    row_count = table.row_count

    column_count = table.column_count

    # --------------------------------------------------------
    # Fallback row count
    # --------------------------------------------------------

    if row_count <= 0:

        row_count = (
            max(
                cell.row_index
                for cell in table.cells
            )
            + 1
        )

    # --------------------------------------------------------
    # Fallback column count
    # --------------------------------------------------------

    if column_count <= 0:

        column_count = (
            max(
                cell.column_index
                for cell in table.cells
            )
            + 1
        )

    # --------------------------------------------------------
    # Create empty matrix
    # --------------------------------------------------------

    rows = [
        ["" for _ in range(column_count)]
        for _ in range(row_count)
    ]

    # --------------------------------------------------------
    # Populate matrix
    # --------------------------------------------------------

    for cell in table.cells:

        row_index = cell.row_index
        column_index = cell.column_index

        # Protect against invalid coordinates.
        if row_index < 0:
            continue

        if column_index < 0:
            continue

        if row_index >= row_count:
            continue

        if column_index >= column_count:
            continue

        # ----------------------------------------------------
        # Select best available value
        # ----------------------------------------------------

        if cell.normalized_text is not None:

            value = cell.normalized_text

        elif cell.text:

            value = cell.text

        elif cell.raw_text:

            value = cell.raw_text

        else:

            value = ""

        rows[
            row_index
        ][
            column_index
        ] = value

    return rows


# ============================================================
# DATA ROW REBUILDING
# ============================================================


def extract_data_rows_from_cells(
    table: Table,
) -> list[list[str]]:
    """
    Extract data rows after the detected header.

    Example:

        header_row_index = 1

        Row 0 → title
        Row 1 → header
        Row 2 → data
        Row 3 → data
        Row 4 → data

    Result:

        Row 2
        Row 3
        Row 4
    """

    if table.header_row_index is None:

        return []

    start_index = (
        table.header_row_index + 1
    )

    if start_index >= len(table.rows):

        return []

    return table.rows[
        start_index:
    ]