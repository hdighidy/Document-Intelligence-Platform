"""
Table Quality & Confidence Scoring
==================================

Phase 3.1.5

Responsibilities:

    - Evaluate table structure
    - Evaluate header quality
    - Evaluate cell completeness
    - Evaluate semantic normalization
    - Evaluate row consistency
    - Calculate overall confidence
    - Identify quality issues

Important:

    This module does NOT modify the extracted values.

    This module only evaluates quality.
"""

from __future__ import annotations

from app.models.table import (
    Table,
    TableQualityScore,
)


# ============================================================
# PUBLIC API
# ============================================================


def score_table_quality(
    table: Table,
) -> Table:
    """
    Calculate quality and confidence scores for a table.

    The Table object is updated with a
    TableQualityScore.

    Returns:
        The same Table object with quality_score populated.
    """

    structure_score = (
        calculate_structure_score(
            table
        )
    )

    header_score = (
        calculate_header_score(
            table
        )
    )

    cell_quality_score = (
        calculate_cell_quality_score(
            table
        )
    )

    normalization_score = (
        calculate_normalization_score(
            table
        )
    )

    consistency_score = (
        calculate_consistency_score(
            table
        )
    )

    overall_score = calculate_overall_score(
        structure_score=structure_score,
        header_score=header_score,
        cell_quality_score=cell_quality_score,
        normalization_score=normalization_score,
        consistency_score=consistency_score,
    )

    confidence_level = (
        determine_confidence_level(
            overall_score
        )
    )

    issues = identify_quality_issues(
        table
    )

    total_cells = len(
        table.cells
    )

    populated_cells = sum(
        1
        for cell in table.cells
        if get_cell_text(cell)
    )

    empty_cells = (
        total_cells
        - populated_cells
    )

    normalized_cells = sum(
        1
        for cell in table.cells
        if getattr(
            cell,
            "normalized_value",
            None,
        ) is not None
    )

    table.quality_result = (
        TableQualityScore(
            structure_score=structure_score,
            header_score=header_score,
            cell_quality_score=cell_quality_score,
            normalization_score=normalization_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            confidence_level=confidence_level,
            total_cells=total_cells,
            populated_cells=populated_cells,
            empty_cells=empty_cells,
            normalized_cells=normalized_cells,
            issues=issues,
        )
    )

    # quality_score is declared as a 0.0-1.0 scalar (unlike the
    # 0-100 scale used throughout TableQualityScore), so it must
    # be normalized before assignment.
    table.quality_score = overall_score / 100.0

    return table


# ============================================================
# STRUCTURE SCORE
# ============================================================


def calculate_structure_score(
    table: Table,
) -> float:
    """
    Evaluate basic table structure.
    """

    score = 0.0

    # --------------------------------------------------------
    # Rows
    # --------------------------------------------------------

    if table.rows:

        score += 40.0

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    if table.column_count > 0:

        score += 30.0

    # --------------------------------------------------------
    # Cells
    # --------------------------------------------------------

    if table.cells:

        score += 30.0

    return score


# ============================================================
# HEADER SCORE
# ============================================================


def calculate_header_score(
    table: Table,
) -> float:
    """
    Evaluate header quality.
    """

    headers = getattr(
        table,
        "headers",
        [],
    )

    if not headers:

        return 0.0

    if table.column_count <= 0:

        return 0.0

    non_empty_headers = sum(
        1
        for header in headers
        if str(header).strip()
    )

    ratio = (
        non_empty_headers
        / table.column_count
    )

    return round(
        min(
            ratio,
            1.0,
        )
        * 100.0,
        2,
    )


# ============================================================
# CELL QUALITY SCORE
# ============================================================


def calculate_cell_quality_score(
    table: Table,
) -> float:
    """
    Calculate populated-cell percentage.
    """

    total_cells = len(
        table.cells
    )

    if total_cells == 0:

        return 0.0

    populated_cells = sum(
        1
        for cell in table.cells
        if get_cell_text(cell)
    )

    return round(
        (
            populated_cells
            / total_cells
        )
        * 100.0,
        2,
    )


# ============================================================
# NORMALIZATION SCORE
# ============================================================


def calculate_normalization_score(
    table: Table,
) -> float:
    """
    Calculate the percentage of populated cells
    that received semantic normalization.
    """

    populated_cells = [
        cell
        for cell in table.cells
        if get_cell_text(cell)
    ]

    if not populated_cells:

        return 0.0

    normalized_cells = sum(
        1
        for cell in populated_cells
        if getattr(
            cell,
            "normalized_value",
            None,
        ) is not None
    )

    return round(
        (
            normalized_cells
            / len(populated_cells)
        )
        * 100.0,
        2,
    )


# ============================================================
# CONSISTENCY SCORE
# ============================================================


def calculate_consistency_score(
    table: Table,
) -> float:
    """
    Evaluate row/column consistency.
    """

    if not table.rows:

        return 0.0

    expected_columns = (
        table.column_count
    )

    if expected_columns <= 0:

        return 0.0

    valid_rows = sum(
        1
        for row in table.rows
        if len(row)
        == expected_columns
    )

    return round(
        (
            valid_rows
            / len(table.rows)
        )
        * 100.0,
        2,
    )


# ============================================================
# OVERALL SCORE
# ============================================================


def calculate_overall_score(
    structure_score: float,
    header_score: float,
    cell_quality_score: float,
    normalization_score: float,
    consistency_score: float,
) -> float:
    """
    Calculate weighted overall score.

    Weights:

        Structure       25%
        Header          15%
        Cell Quality    20%
        Normalization   20%
        Consistency     20%
    """

    score = (
        structure_score * 0.25
        + header_score * 0.15
        + cell_quality_score * 0.20
        + normalization_score * 0.20
        + consistency_score * 0.20
    )

    return round(
        min(
            max(
                score,
                0.0,
            ),
            100.0,
        ),
        2,
    )


# ============================================================
# CONFIDENCE LEVEL
# ============================================================


def determine_confidence_level(
    score: float,
) -> str:
    """
    Convert numerical score into confidence level.
    """

    if score >= 90.0:

        return "HIGH"

    if score >= 75.0:

        return "MEDIUM"

    if score >= 60.0:

        return "LOW"

    return "REVIEW_REQUIRED"


# ============================================================
# QUALITY ISSUES
# ============================================================


def identify_quality_issues(
    table: Table,
) -> list[str]:
    """
    Identify potential table-quality issues.
    """

    issues = []

    # --------------------------------------------------------
    # No rows
    # --------------------------------------------------------

    if not table.rows:

        issues.append(
            "No table rows detected."
        )

    # --------------------------------------------------------
    # No columns
    # --------------------------------------------------------

    if table.column_count <= 0:

        issues.append(
            "No table columns detected."
        )

    # --------------------------------------------------------
    # No headers
    # --------------------------------------------------------

    headers = getattr(
        table,
        "headers",
        [],
    )

    if not headers:

        issues.append(
            "No headers detected."
        )

    # --------------------------------------------------------
    # Empty cells
    # --------------------------------------------------------

    total_cells = len(
        table.cells
    )

    if total_cells:

        empty_cells = sum(
            1
            for cell in table.cells
            if not get_cell_text(cell)
        )

        empty_ratio = (
            empty_cells
            / total_cells
        )

        if empty_ratio > 0.30:

            issues.append(
                "More than 30% of cells are empty."
            )

    # --------------------------------------------------------
    # Inconsistent rows
    # --------------------------------------------------------

    expected_columns = (
        table.column_count
    )

    inconsistent_rows = sum(
        1
        for row in table.rows
        if len(row)
        != expected_columns
    )

    if inconsistent_rows:

        issues.append(
            f"{inconsistent_rows} rows "
            "have inconsistent column counts."
        )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_count = getattr(
        table,
        "duplicate_row_count",
        0,
    )

    if duplicate_count:

        issues.append(
            f"{duplicate_count} duplicate "
            "rows detected."
        )

    return issues


# ============================================================
# HELPERS
# ============================================================


def get_cell_text(
    cell,
) -> str:
    """
    Get the best available textual representation.
    """

    normalized_text = getattr(
        cell,
        "normalized_text",
        None,
    )

    if normalized_text:

        return str(
            normalized_text
        ).strip()

    text = getattr(
        cell,
        "text",
        None,
    )

    if text:

        return str(
            text
        ).strip()

    raw_text = getattr(
        cell,
        "raw_text",
        None,
    )

    if raw_text:

        return str(
            raw_text
        ).strip()

    return ""