"""
Table Structure Analyzer
========================

Phase 3.1.7
------------

Table Structure Analysis

Pipeline position:

    PDF
      ↓
    Detection
      ↓
    Extraction
      ↓
    Cleaning
      ↓
    Quality
      ↓
    Validation
      ↓
    Structure Analysis
      ↓
    Structured Table

Responsibilities
----------------

    1. Detect title rows
    2. Detect header rows
    3. Detect data rows
    4. Detect empty rows
    5. Determine data boundaries
    6. Analyze row consistency
    7. Analyze column consistency
    8. Detect structural indicators
    9. Classify table structure
    10. Calculate structure confidence

Important
---------

This module does NOT:

    - perform PDF extraction
    - perform OCR
    - modify raw_text
    - perform semantic value normalization
    - perform spelling correction
    - remove rows
    - remove columns

The analyzer works on the existing Table model.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from app.models.table import Table


# ============================================================
# CONSTANTS
# ============================================================

STRUCTURE_ANALYSIS_VERSION = "3.1.7"

DEFAULT_HEADER_MIN_NON_EMPTY_RATIO = 0.30

DEFAULT_DATA_MIN_NON_EMPTY_RATIO = 0.20

DEFAULT_TITLE_MAX_NON_EMPTY_CELLS = 2


# ============================================================
# PUBLIC API
# ============================================================


def analyze_table_structure(
    table: Table,
) -> Table:
    """
    Analyze the logical structure of a table.

    The original Table is NOT modified.

    Returns:
        A deep-copied Table with structure information.
    """

    analyzed_table = deepcopy(
        table
    )

    rows = get_rows(
        analyzed_table
    )

    if not rows:

        reset_structure_fields(
            analyzed_table
        )

        analyzed_table.structure_analyzed = True

        analyzed_table.structure_type = (
            "EMPTY"
        )

        analyzed_table.structure_confidence = 1.0

        analyzed_table.structure_analysis_version = (
            STRUCTURE_ANALYSIS_VERSION
        )

        return analyzed_table

    # --------------------------------------------------------
    # Ensure dimensions are available
    # --------------------------------------------------------

    if analyzed_table.row_count <= 0:

        analyzed_table.row_count = len(
            rows
        )

    if analyzed_table.column_count <= 0:

        analyzed_table.column_count = max(
            (
                len(row)
                for row in rows
            ),
            default=0,
        )

    # --------------------------------------------------------
    # Empty rows
    # --------------------------------------------------------

    empty_rows = detect_empty_rows(
        rows
    )

    analyzed_table.empty_row_indices = (
        empty_rows
    )

    analyzed_table.has_empty_rows = bool(
        empty_rows
    )

    # --------------------------------------------------------
    # Row / column consistency
    # --------------------------------------------------------

    analyzed_table.row_consistency_score = (
        calculate_row_consistency(
            rows,
            analyzed_table.column_count,
        )
    )

    analyzed_table.column_consistency_score = (
        calculate_column_consistency(
            rows,
            analyzed_table.column_count,
        )
    )

    # --------------------------------------------------------
    # Title detection
    # --------------------------------------------------------

    title_rows, title_confidence = (
        detect_title_rows_with_confidence(
            rows,
            empty_rows,
        )
    )

    analyzed_table.title_row_indices = (
        title_rows
    )

    analyzed_table.title_confidence = (
        title_confidence
    )

    analyzed_table.has_title = bool(
        title_rows
    )

    # --------------------------------------------------------
    # Header detection
    # --------------------------------------------------------

    header_rows, header_confidence = (
        detect_header_rows_with_confidence(
            rows,
            title_rows,
            empty_rows,
            analyzed_table.column_count,
        )
    )

    analyzed_table.header_row_indices = (
        header_rows
    )

    analyzed_table.header_confidence = (
        header_confidence
    )

    analyzed_table.has_header = bool(
        header_rows
    )

    # --------------------------------------------------------
    # Data rows
    # --------------------------------------------------------

    data_rows, data_start, data_end, data_confidence = (
        detect_data_rows_with_boundaries(
            rows,
            header_rows,
            title_rows,
            empty_rows,
        )
    )

    analyzed_table.data_row_indices = (
        data_rows
    )

    analyzed_table.data_start_row_index = (
        data_start
    )

    analyzed_table.data_end_row_index = (
        data_end
    )

    analyzed_table.data_boundary_confidence = (
        data_confidence
    )

    analyzed_table.has_data_rows = bool(
        data_rows
    )

    # --------------------------------------------------------
    # Synchronize existing model fields
    # --------------------------------------------------------

    if header_rows:

        analyzed_table.header_row_index = (
            header_rows[0]
        )

        analyzed_table.headers = build_headers(
            rows,
            header_rows,
            analyzed_table.column_count,
        )

    if title_rows:

        analyzed_table.title_row_index = (
            title_rows[0]
        )

        analyzed_table.title = build_title(
            rows,
            title_rows,
        )

    # --------------------------------------------------------
    # Data rows
    # --------------------------------------------------------

    analyzed_table.data_rows = [
        rows[index]
        for index in data_rows
        if 0 <= index < len(rows)
    ]

    # --------------------------------------------------------
    # Multi-level header detection
    # --------------------------------------------------------

    analyzed_table.has_multi_level_header = (
        len(header_rows) > 1
    )

    # --------------------------------------------------------
    # Merged-cell indicator
    # --------------------------------------------------------

    analyzed_table.has_merged_cells = (
        detect_possible_merged_cells(
            rows,
            analyzed_table.column_count,
        )
    )

    # --------------------------------------------------------
    # Structure classification
    # --------------------------------------------------------

    analyzed_table.structure_type = (
        classify_structure(
            rows=rows,
            title_rows=title_rows,
            header_rows=header_rows,
            data_rows=data_rows,
            empty_rows=empty_rows,
        )
    )

    # --------------------------------------------------------
    # Structure issues
    # --------------------------------------------------------

    issues, warnings = (
        collect_structure_diagnostics(
            analyzed_table
        )
    )

    analyzed_table.structure_issues = (
        issues
    )

    analyzed_table.structure_warnings = (
        warnings
    )

    # --------------------------------------------------------
    # Overall confidence
    # --------------------------------------------------------

    analyzed_table.structure_confidence = (
        calculate_structure_confidence(
            analyzed_table
        )
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    analyzed_table.structure_analyzed = True

    analyzed_table.structure_analysis_version = (
        STRUCTURE_ANALYSIS_VERSION
    )

    return analyzed_table


# Backward-compatible alias.


def analyze_structure(
    table: Table,
) -> Table:
    """
    Alias for analyze_table_structure().
    """

    return analyze_table_structure(
        table
    )


# ============================================================
# ROW ACCESS
# ============================================================


def get_rows(
    table: Table,
) -> list[list[str]]:
    """
    Return the best available row matrix.

    Priority:

        table.rows
        ↓
        cells
    """

    if table.rows:

        return [
            list(row)
            for row in table.rows
        ]

    if not table.cells:

        return []

    max_row = max(
        (
            cell.row_index
            for cell in table.cells
        ),
        default=-1,
    )

    max_column = max(
        (
            cell.column_index
            for cell in table.cells
        ),
        default=-1,
    )

    if max_row < 0:

        return []

    rows = [
        ["" for _ in range(max_column + 1)]
        for _ in range(max_row + 1)
    ]

    for cell in table.cells:

        value = (
            cell.normalized_text
            if cell.normalized_text is not None
            else cell.text
        )

        if value is None:

            value = cell.raw_text or ""

        rows[
            cell.row_index
        ][
            cell.column_index
        ] = str(value)

    return rows


# ============================================================
# EMPTY ROW DETECTION
# ============================================================


def detect_empty_rows(
    rows: list[list[str]],
) -> list[int]:
    """
    Detect completely empty rows.
    """

    result = []

    for index, row in enumerate(rows):

        if is_empty_row(row):

            result.append(index)

    return result


def is_empty_row(
    row: Iterable[str],
) -> bool:
    """
    Return True when every cell is empty.
    """

    for value in row:

        if normalize_cell(
            value
        ):

            return False

    return True


# ============================================================
# TITLE DETECTION
# ============================================================


def detect_title_rows(
    rows: list[list[str]],
    empty_rows: list[int] | None = None,
) -> list[int]:
    """
    Detect likely title rows.

    This is intentionally conservative.

    A title row normally:

        - appears before the header
        - contains very few non-empty cells
        - contains textual content
        - does not look like a normal data row
    """

    title_rows, _ = (
        detect_title_rows_with_confidence(
            rows,
            empty_rows
            if empty_rows is not None
            else detect_empty_rows(rows),
        )
    )

    return title_rows


def detect_title_rows_with_confidence(
    rows: list[list[str]],
    empty_rows: list[int],
) -> tuple[list[int], float]:
    """
    Detect title rows and confidence.
    """

    if not rows:

        return [], 0.0

    candidates = []

    # Only inspect the first few rows.
    inspection_limit = min(
        len(rows),
        4,
    )

    for index in range(
        inspection_limit
    ):

        if index in empty_rows:

            continue

        row = rows[index]

        non_empty = [
            normalize_cell(value)
            for value in row
            if normalize_cell(value)
        ]

        if not non_empty:

            continue

        non_empty_count = len(
            non_empty
        )

        # A title generally occupies only one
        # or a small number of cells.
        if (
            non_empty_count
            <= DEFAULT_TITLE_MAX_NON_EMPTY_CELLS
        ):

            text_count = sum(
                1
                for value in non_empty
                if not looks_numeric(value)
            )

            if text_count == non_empty_count:

                candidates.append(
                    index
                )

    if not candidates:

        return [], 0.0

    # Avoid treating an actual one-column header
    # as a title if there is no subsequent header.
    candidate = candidates[0]

    if candidate == len(rows) - 1:

        return [], 0.0

    confidence = 0.90

    if len(
        [
            value
            for value in rows[candidate]
            if normalize_cell(value)
        ]
    ) == 1:

        confidence = 0.95

    return [candidate], confidence


# ============================================================
# HEADER DETECTION
# ============================================================


def detect_header_rows(
    rows: list[list[str]],
    title_rows: list[int] | None = None,
    empty_rows: list[int] | None = None,
    column_count: int | None = None,
) -> list[int]:
    """
    Detect likely header rows.
    """

    result, _ = (
        detect_header_rows_with_confidence(
            rows,
            title_rows
            if title_rows is not None
            else [],
            empty_rows
            if empty_rows is not None
            else detect_empty_rows(rows),
            column_count
            if column_count is not None
            else max(
                (
                    len(row)
                    for row in rows
                ),
                default=0,
            ),
        )
    )

    return result


def detect_header_rows_with_confidence(
    rows: list[list[str]],
    title_rows: list[int],
    empty_rows: list[int],
    column_count: int,
) -> tuple[list[int], float]:
    """
    Detect header rows using structural heuristics.

    Strong signals:

        - follows title
        - mostly textual
        - reasonable number of populated columns
        - next rows look more like data
    """

    if not rows:

        return [], 0.0

    candidates = []

    start = 0

    if title_rows:

        start = max(
            title_rows
        ) + 1

    # Skip empty rows immediately after title.
    while (
        start < len(rows)
        and start in empty_rows
    ):

        start += 1

    # --------------------------------------------------------
    # Existing headers are a strong signal
    # --------------------------------------------------------

    if rows and hasattr(
        rows,
        "__len__",
    ):

        pass

    # --------------------------------------------------------
    # Search candidate rows
    # --------------------------------------------------------

    for index in range(
        start,
        min(
            len(rows),
            start + 4,
        ),
    ):

        if index in empty_rows:

            continue

        row = rows[index]

        non_empty = [
            normalize_cell(value)
            for value in row
            if normalize_cell(value)
        ]

        if not non_empty:

            continue

        non_empty_ratio = (
            len(non_empty)
            / max(
                column_count,
                1,
            )
        )

        text_ratio = (
            sum(
                1
                for value in non_empty
                if not looks_numeric(value)
            )
            / len(non_empty)
        )

        # Header usually has substantial textual
        # coverage.
        if (
            non_empty_ratio
            >= DEFAULT_HEADER_MIN_NON_EMPTY_RATIO
            and text_ratio >= 0.50
        ):

            score = (
                0.55 * non_empty_ratio
                + 0.45 * text_ratio
            )

            candidates.append(
                (
                    index,
                    score,
                )
            )

    if not candidates:

        return [], 0.0

    # --------------------------------------------------------
    # Prefer the earliest strong candidate
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            item[0],
            -item[1],
        )
    )

    best_index, best_score = (
        candidates[0]
    )

    # --------------------------------------------------------
    # Multi-level header detection
    # --------------------------------------------------------

    header_indices = [
        best_index
    ]

    next_index = (
        best_index + 1
    )

    if (
        next_index < len(rows)
        and next_index not in empty_rows
    ):

        next_row = rows[next_index]

        next_non_empty = [
            normalize_cell(value)
            for value in next_row
            if normalize_cell(value)
        ]

        if next_non_empty:

            next_text_ratio = (
                sum(
                    1
                    for value in next_non_empty
                    if not looks_numeric(value)
                )
                / len(next_non_empty)
            )

            # If both rows are strongly textual,
            # consider the second row part of a
            # multi-level header only when it has
            # similar structural density.
            next_density = (
                len(next_non_empty)
                / max(
                    column_count,
                    1,
                )
            )

            current_density = (
                len(
                    [
                        value
                        for value in rows[best_index]
                        if normalize_cell(value)
                    ]
                )
                / max(
                    column_count,
                    1,
                )
            )

            if (
                next_text_ratio >= 0.75
                and next_density >= 0.50
                and abs(
                    next_density
                    - current_density
                )
                <= 0.35
            ):

                # Only classify as multi-level if
                # the row does not look like ordinary
                # data.
                if not row_looks_like_data(
                    next_row
                ):

                    header_indices.append(
                        next_index
                    )

    confidence = min(
        1.0,
        max(
            0.0,
            best_score,
        ),
    )

    return (
        header_indices,
        confidence,
    )


# ============================================================
# DATA ROW DETECTION
# ============================================================


def detect_data_rows(
    rows: list[list[str]],
    header_rows: list[int],
    title_rows: list[int] | None = None,
    empty_rows: list[int] | None = None,
) -> list[int]:
    """
    Detect logical data rows.
    """

    result, _, _, _ = (
        detect_data_rows_with_boundaries(
            rows,
            header_rows,
            title_rows
            if title_rows is not None
            else [],
            empty_rows
            if empty_rows is not None
            else detect_empty_rows(rows),
        )
    )

    return result


def detect_data_rows_with_boundaries(
    rows: list[list[str]],
    header_rows: list[int],
    title_rows: list[int],
    empty_rows: list[int],
) -> tuple[
    list[int],
    int | None,
    int | None,
    float,
]:
    """
    Detect data rows and boundaries.
    """

    if not rows:

        return [], None, None, 0.0

    # --------------------------------------------------------
    # Determine starting point
    # --------------------------------------------------------

    if header_rows:

        start = max(
            header_rows
        ) + 1

    elif title_rows:

        start = max(
            title_rows
        ) + 1

    else:

        start = 0

    # --------------------------------------------------------
    # Collect non-empty rows
    # --------------------------------------------------------

    data_indices = []

    for index in range(
        start,
        len(rows),
    ):

        if index in empty_rows:

            continue

        row = rows[index]

        if is_empty_row(row):

            continue

        # A row after the header is normally data
        # unless it strongly resembles another header.
        if row_looks_like_data(
            row
        ):

            data_indices.append(
                index
            )

        else:

            # If there is no data yet and this is
            # textual, it may still be data.
            if not data_indices:

                non_empty = [
                    normalize_cell(value)
                    for value in row
                    if normalize_cell(value)
                ]

                if non_empty:

                    data_indices.append(
                        index
                    )

    if not data_indices:

        return [], None, None, 0.0

    data_start = min(
        data_indices
    )

    data_end = max(
        data_indices
    )

    # --------------------------------------------------------
    # Boundary confidence
    # --------------------------------------------------------

    confidence = 1.0

    if not header_rows:

        confidence -= 0.25

    if data_start is None:

        confidence -= 0.25

    confidence = max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )

    return (
        data_indices,
        data_start,
        data_end,
        confidence,
    )


# ============================================================
# DATA ROW HEURISTICS
# ============================================================


def row_looks_like_data(
    row: list[str],
) -> bool:
    """
    Determine whether a row resembles a data row.

    A row is considered data-like when it contains:

        - numeric values
        - identifiers
        - dates
        - mixed semantic content
    """

    values = [
        normalize_cell(value)
        for value in row
        if normalize_cell(value)
    ]

    if not values:

        return False

    if len(values) == 1:

        return False

    numeric_count = sum(
        1
        for value in values
        if looks_numeric(value)
    )

    date_count = sum(
        1
        for value in values
        if looks_date(value)
    )

    identifier_count = sum(
        1
        for value in values
        if looks_identifier(value)
    )

    semantic_signals = (
        numeric_count
        + date_count
        + identifier_count
    )

    # One strong semantic signal is sufficient for
    # a normal extracted data row.
    if semantic_signals >= 1:

        return True

    # Otherwise, sufficiently populated mixed text
    # can still represent a data row.
    return len(values) >= 2


# ============================================================
# HEADER BUILDING
# ============================================================


def build_headers(
    rows: list[list[str]],
    header_rows: list[int],
    column_count: int,
) -> list[str]:
    """
    Build headers from detected header rows.

    For a single header row, values are copied directly.

    For multi-level headers, values are joined using
    ' | '.
    """

    if not header_rows:

        return []

    result = []

    for column in range(
        column_count
    ):

        parts = []

        for row_index in header_rows:

            if (
                0 <= row_index < len(rows)
                and column < len(rows[row_index])
            ):

                value = normalize_cell(
                    rows[row_index][column]
                )

                if value:

                    parts.append(
                        value
                    )

        if parts:

            result.append(
                " | ".join(parts)
            )

        else:

            result.append("")

    return result


# ============================================================
# TITLE BUILDING
# ============================================================


def build_title(
    rows: list[list[str]],
    title_rows: list[int],
) -> str | None:
    """
    Build logical title text.
    """

    if not title_rows:

        return None

    parts = []

    for index in title_rows:

        if (
            0 <= index < len(rows)
        ):

            for value in rows[index]:

                value = normalize_cell(
                    value
                )

                if value:

                    parts.append(
                        value
                    )

    if not parts:

        return None

    return " ".join(parts)


# ============================================================
# CONSISTENCY
# ============================================================


def calculate_row_consistency(
    rows: list[list[str]],
    expected_columns: int,
) -> float:
    """
    Calculate row-length consistency.

    Score:

        1.0 = all rows match expected length
        0.0 = no rows match
    """

    if not rows:

        return 1.0

    if expected_columns <= 0:

        return 1.0

    matching = sum(
        1
        for row in rows
        if len(row)
        == expected_columns
    )

    return (
        matching
        / len(rows)
    )


def calculate_column_consistency(
    rows: list[list[str]],
    expected_columns: int,
) -> float:
    """
    Calculate column occupancy consistency.

    Measures how consistently each expected column
    exists across the rows.
    """

    if not rows:

        return 1.0

    if expected_columns <= 0:

        return 1.0

    scores = []

    for column in range(
        expected_columns
    ):

        present = sum(
            1
            for row in rows
            if column < len(row)
        )

        scores.append(
            present / len(rows)
        )

    if not scores:

        return 1.0

    return sum(
        scores
    ) / len(scores)


# ============================================================
# MERGED CELL INDICATOR
# ============================================================


def detect_possible_merged_cells(
    rows: list[list[str]],
    column_count: int,
) -> bool:
    """
    Detect a basic indication of merged cells.

    This is heuristic only.

    A row with a very low occupancy compared with the
    table width may indicate a title or merged region.

    It does NOT claim exact PDF merge geometry.
    """

    if not rows:

        return False

    if column_count <= 1:

        return False

    for row in rows:

        occupied = sum(
            1
            for value in row
            if normalize_cell(value)
        )

        if occupied == 1 and column_count >= 3:

            return True

    return False


# ============================================================
# STRUCTURE CLASSIFICATION
# ============================================================


def classify_structure(
    rows: list[list[str]],
    title_rows: list[int],
    header_rows: list[int],
    data_rows: list[int],
    empty_rows: list[int],
) -> str:
    """
    Classify table structure.
    """

    if not rows:

        return "EMPTY"

    if (
        title_rows
        and header_rows
        and data_rows
    ):

        if len(header_rows) > 1:

            return "TITLE_MULTI_LEVEL_HEADER_DATA"

        return "TITLE_HEADER_DATA"

    if (
        header_rows
        and data_rows
    ):

        if len(header_rows) > 1:

            return "MULTI_LEVEL_HEADER_DATA"

        return "HEADER_DATA"

    if data_rows:

        return "DATA_ONLY"

    if header_rows:

        return "HEADER_ONLY"

    if title_rows:

        return "TITLE_ONLY"

    return "UNSTRUCTURED"


# ============================================================
# DIAGNOSTICS
# ============================================================


def collect_structure_diagnostics(
    table: Table,
) -> tuple[list[str], list[str]]:
    """
    Collect structure issues and warnings.
    """

    issues = []

    warnings = []

    if not table.has_header:

        warnings.append(
            "NO_HEADER_DETECTED"
        )

    if not table.has_data_rows:

        warnings.append(
            "NO_DATA_ROWS_DETECTED"
        )

    if (
        table.row_consistency_score
        < 0.90
    ):

        warnings.append(
            "INCONSISTENT_ROW_LENGTH"
        )

    if (
        table.column_consistency_score
        < 0.90
    ):

        warnings.append(
            "INCONSISTENT_COLUMN_OCCUPANCY"
        )

    if table.has_multi_level_header:

        warnings.append(
            "MULTI_LEVEL_HEADER_DETECTED"
        )

    if table.has_merged_cells:

        warnings.append(
            "POSSIBLE_MERGED_CELLS"
        )

    if (
        table.has_data_rows
        and table.data_start_row_index is None
    ):

        issues.append(
            "DATA_START_BOUNDARY_MISSING"
        )

    if (
        table.has_data_rows
        and table.data_end_row_index is None
    ):

        issues.append(
            "DATA_END_BOUNDARY_MISSING"
        )

    return (
        issues,
        warnings,
    )


# ============================================================
# STRUCTURE CONFIDENCE
# ============================================================


def calculate_structure_confidence(
    table: Table,
) -> float:
    """
    Calculate overall structure confidence.

    Components:

        Header confidence       25%
        Data boundary           25%
        Row consistency         15%
        Column consistency      15%
        Structural completeness 20%
    """

    header_score = (
        table.header_confidence
        if table.has_header
        else 0.0
    )

    data_score = (
        table.data_boundary_confidence
        if table.has_data_rows
        else 0.0
    )

    completeness = 0.0

    if table.has_header:

        completeness += 0.50

    if table.has_data_rows:

        completeness += 0.50

    score = (
        header_score * 0.25
        + data_score * 0.25
        + table.row_consistency_score * 0.15
        + table.column_consistency_score * 0.15
        + completeness * 0.20
    )

    # Penalize structural errors.
    if table.structure_issues:

        score -= (
            0.10
            * len(
                table.structure_issues
            )
        )

    # Mild warning penalty.
    if table.structure_warnings:

        score -= (
            0.02
            * len(
                table.structure_warnings
            )
        )

    return max(
        0.0,
        min(
            1.0,
            score,
        ),
    )


# ============================================================
# UTILITY FUNCTIONS
# ============================================================


def normalize_cell(
    value: object,
) -> str:
    """
    Convert a cell value into normalized comparison text.
    """

    if value is None:

        return ""

    return str(
        value
    ).strip()


def looks_numeric(
    value: str,
) -> bool:
    """
    Detect basic numeric values.
    """

    if not value:

        return False

    normalized = (
        value
        .replace(",", "")
        .replace(" ", "")
        .replace("%", "")
    )

    try:

        float(
            normalized
        )

        return True

    except ValueError:

        return False


def looks_date(
    value: str,
) -> bool:
    """
    Detect common date representations.
    """

    if not value:

        return False

    patterns = (
        r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$",
        r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$",
        r"^\d{1,2}\.\d{1,2}\.\d{2,4}$",
    )

    return any(
        _fullmatch(
            pattern,
            value,
        )
        for pattern in patterns
    )


def looks_identifier(
    value: str,
) -> bool:
    """
    Detect common engineering identifiers.
    """

    if not value:

        return False

    if " " in value:

        return False

    return bool(
        _fullmatch(
            r"[A-Za-z]{2,10}"
            r"(?:[-_][A-Za-z0-9]+)+",
            value,
        )
    )


def _fullmatch(
    pattern: str,
    value: str,
) -> bool:
    """
    Small regex helper kept private.
    """

    import re

    return (
        re.fullmatch(
            pattern,
            value,
        )
        is not None
    )


# ============================================================
# RESET
# ============================================================


def reset_structure_fields(
    table: Table,
) -> None:
    """
    Reset Phase 3.1.7 fields.
    """

    table.structure_analyzed = False

    table.structure_type = None

    table.structure_confidence = None

    table.title_row_indices = []

    table.header_row_indices = []

    table.data_row_indices = []

    table.empty_row_indices = []

    table.data_start_row_index = None

    table.data_end_row_index = None

    table.row_consistency_score = 1.0

    table.column_consistency_score = 1.0

    table.header_confidence = 0.0

    table.title_confidence = 0.0

    table.data_boundary_confidence = 0.0

    table.has_title = False

    table.has_header = False

    table.has_data_rows = False

    table.has_empty_rows = False

    table.has_merged_cells = False

    table.has_multi_level_header = False

    table.structure_issues = []

    table.structure_warnings = []

    table.structure_analysis_version = None


# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "analyze_table_structure",
    "analyze_structure",
    "detect_title_rows",
    "detect_header_rows",
    "detect_data_rows",
    "detect_empty_rows",
    "calculate_row_consistency",
    "calculate_column_consistency",
    "calculate_structure_confidence",
    "classify_structure",
]