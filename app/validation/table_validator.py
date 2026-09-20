"""
Table Validation Engine
=======================

Phase 3.1.6.2

Responsibilities
----------------

Validate a cleaned and normalized Table against
structural, completeness, semantic and confidence rules.

This module does NOT:

    - detect tables
    - extract tables
    - clean tables
    - normalize values
    - modify the source Table

The validator returns a TableValidationResult.

Pipeline:

    Cleaned Table
        ↓
    Structural Validation
        ↓
    Header Validation
        ↓
    Row Validation
        ↓
    Cell Validation
        ↓
    Semantic Validation
        ↓
    Confidence Validation
        ↓
    Final Validation Result
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.models.table import (
    Table,
    TableCell,
    TableValidationResult,
    TableValidationStatus,
    ValidationCheck,
    ValidationIssue,
    ValidationSeverity,
)


# ============================================================
# VERSION
# ============================================================

VALIDATOR_VERSION = "3.1.6.2"


# ============================================================
# PUBLIC API
# ============================================================


def validate_table(
    table: Table,
) -> TableValidationResult:
    """
    Validate a complete Table.

    The original Table is NOT modified.

    Returns
    -------
    TableValidationResult
        Complete validation result.
    """

    checks: list[ValidationCheck] = []
    issues: list[ValidationIssue] = []

    # --------------------------------------------------------
    # 1. STRUCTURE
    # --------------------------------------------------------

    check, check_issues = validate_structure(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 2. HEADERS
    # --------------------------------------------------------

    check, check_issues = validate_headers(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 3. ROW LENGTHS
    # --------------------------------------------------------

    check, check_issues = validate_row_lengths(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 4. EMPTY CELLS
    # --------------------------------------------------------

    check, check_issues = validate_empty_cells(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 5. DUPLICATE ROWS
    # --------------------------------------------------------

    check, check_issues = validate_duplicate_rows(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 6. CELL TYPES
    # --------------------------------------------------------

    check, check_issues = validate_cell_types(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 7. DATES
    # --------------------------------------------------------

    check, check_issues = validate_dates(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 8. NUMERIC VALUES
    # --------------------------------------------------------

    check, check_issues = validate_numeric_values(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 9. SEMANTIC VALUES
    # --------------------------------------------------------

    check, check_issues = validate_semantic_values(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # 10. CONFIDENCE
    # --------------------------------------------------------

    check, check_issues = validate_confidence(table)

    checks.append(check)
    issues.extend(check_issues)

    # --------------------------------------------------------
    # CALCULATE RESULT
    # --------------------------------------------------------

    total_checks = len(checks)

    passed_checks = sum(
        1
        for check in checks
        if check.passed
    )

    failed_checks = (
        total_checks
        - passed_checks
    )

    error_count = sum(
        1
        for issue in issues
        if issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
    )

    warning_count = sum(
        1
        for issue in issues
        if issue.severity
        == ValidationSeverity.WARNING
    )

    score = calculate_validation_score(
        checks
    )

    status = determine_validation_status(
        issues=issues,
        score=score,
    )

    return TableValidationResult(
        status=status,
        score=score,
        checks=checks,
        issues=issues,
        validated_at=datetime.utcnow(),
        validator_version=VALIDATOR_VERSION,
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        error_count=error_count,
        warning_count=warning_count,
    )


# ============================================================
# STRUCTURE VALIDATION
# ============================================================


def validate_structure(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate basic table structure.
    """

    issues: list[ValidationIssue] = []

    if table.row_count < 0:

        issues.append(
            ValidationIssue(
                code="INVALID_ROW_COUNT",
                message="Row count cannot be negative.",
                severity=ValidationSeverity.ERROR,
                field="row_count",
                actual=table.row_count,
                expected=">= 0",
            )
        )

    if table.column_count < 0:

        issues.append(
            ValidationIssue(
                code="INVALID_COLUMN_COUNT",
                message="Column count cannot be negative.",
                severity=ValidationSeverity.ERROR,
                field="column_count",
                actual=table.column_count,
                expected=">= 0",
            )
        )

    if (
        table.row_count > 0
        and not table.rows
    ):

        issues.append(
            ValidationIssue(
                code="MISSING_ROWS",
                message="Table declares rows but row matrix is empty.",
                severity=ValidationSeverity.ERROR,
                field="rows",
            )
        )

    if (
        table.column_count > 0
        and table.rows
    ):

        for index, row in enumerate(table.rows):

            if len(row) == 0:

                issues.append(
                    ValidationIssue(
                        code="EMPTY_ROW",
                        message="Table contains an empty row.",
                        severity=ValidationSeverity.WARNING,
                        row_index=index,
                    )
                )

    passed = not any(
        issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
        for issue in issues
    )

    score = 1.0 if passed else 0.0

    return (
        ValidationCheck(
            name="structure",
            passed=passed,
            score=score,
            message=(
                "Table structure is valid."
                if passed
                else "Table structure contains errors."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# HEADER VALIDATION
# ============================================================


def validate_headers(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate table headers.
    """

    issues: list[ValidationIssue] = []

    if not table.headers:

        issues.append(
            ValidationIssue(
                code="MISSING_HEADER",
                message="Table has no detected headers.",
                severity=ValidationSeverity.WARNING,
                field="headers",
            )
        )

    else:

        non_empty_headers = sum(
            1
            for header in table.headers
            if str(header).strip()
        )

        if non_empty_headers == 0:

            issues.append(
                ValidationIssue(
                    code="EMPTY_HEADER",
                    message="All detected headers are empty.",
                    severity=ValidationSeverity.ERROR,
                    field="headers",
                )
            )

        if (
            table.column_count > 0
            and len(table.headers)
            != table.column_count
        ):

            issues.append(
                ValidationIssue(
                    code="HEADER_COLUMN_MISMATCH",
                    message="Header count does not match column count.",
                    severity=ValidationSeverity.WARNING,
                    field="headers",
                    actual=len(table.headers),
                    expected=table.column_count,
                )
            )

    passed = not any(
        issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
        for issue in issues
    )

    score = (
        1.0
        if passed
        else 0.0
    )

    return (
        ValidationCheck(
            name="headers",
            passed=passed,
            score=score,
            message=(
                "Headers are valid."
                if passed
                else "Header validation failed."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# ROW LENGTH VALIDATION
# ============================================================


def validate_row_lengths(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Ensure all rows have the expected number
    of columns.
    """

    issues: list[ValidationIssue] = []

    expected = table.column_count

    if expected <= 0:

        return (
            ValidationCheck(
                name="row_lengths",
                passed=True,
                score=1.0,
                message="Column count is not defined.",
                issues_count=0,
            ),
            issues,
        )

    for row_index, row in enumerate(table.rows):

        if len(row) != expected:

            issues.append(
                ValidationIssue(
                    code="INCONSISTENT_ROW_LENGTH",
                    message=(
                        "Row length does not match "
                        "the expected column count."
                    ),
                    severity=ValidationSeverity.ERROR,
                    row_index=row_index,
                    expected=expected,
                    actual=len(row),
                )
            )

    passed = len(issues) == 0

    return (
        ValidationCheck(
            name="row_lengths",
            passed=passed,
            score=1.0 if passed else 0.0,
            message=(
                "All rows have consistent lengths."
                if passed
                else "One or more rows have inconsistent lengths."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# EMPTY CELL VALIDATION
# ============================================================


def validate_empty_cells(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate empty-cell ratio.

    Empty cells are not automatically invalid.

    A warning is raised when the table contains
    a significant number of empty cells.
    """

    issues: list[ValidationIssue] = []

    total_cells = len(table.cells)

    if total_cells == 0:

        return (
            ValidationCheck(
                name="empty_cells",
                passed=False,
                score=0.0,
                message="No cells are available.",
                issues_count=1,
            ),
            [
                ValidationIssue(
                    code="NO_CELLS",
                    message="Table contains no extracted cells.",
                    severity=ValidationSeverity.ERROR,
                )
            ],
        )

    empty_cells = sum(
        1
        for cell in table.cells
        if not get_cell_value(cell)
    )

    ratio = (
        empty_cells
        / total_cells
    )

    # --------------------------------------------------------
    # Thresholds
    # --------------------------------------------------------

    if ratio >= 0.50:

        issues.append(
            ValidationIssue(
                code="HIGH_EMPTY_CELL_RATIO",
                message=(
                    f"Empty cell ratio is {ratio:.1%}."
                ),
                severity=ValidationSeverity.ERROR,
                field="empty_cell_ratio",
                actual=ratio,
                expected="< 50%",
            )
        )

    elif ratio >= 0.25:

        issues.append(
            ValidationIssue(
                code="HIGH_EMPTY_CELL_RATIO",
                message=(
                    f"Empty cell ratio is {ratio:.1%}."
                ),
                severity=ValidationSeverity.WARNING,
                field="empty_cell_ratio",
                actual=ratio,
                expected="< 25%",
            )
        )

    passed = not any(
        issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
        for issue in issues
    )

    score = max(
        0.0,
        1.0 - ratio,
    )

    return (
        ValidationCheck(
            name="empty_cells",
            passed=passed,
            score=score,
            message=(
                "Empty-cell ratio is acceptable."
                if passed
                else "Empty-cell ratio is too high."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# DUPLICATE ROW VALIDATION
# ============================================================


def validate_duplicate_rows(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Detect duplicate data rows.
    """

    issues: list[ValidationIssue] = []

    seen: dict[
        tuple[str, ...],
        int,
    ] = {}

    start_index = (
        table.header_row_index + 1
        if table.header_row_index is not None
        else 0
    )

    for row_index in range(
        start_index,
        len(table.rows),
    ):

        row = table.rows[row_index]

        key = tuple(
            str(value).strip().lower()
            for value in row
        )

        if not any(key):

            continue

        if key in seen:

            issues.append(
                ValidationIssue(
                    code="DUPLICATE_ROW",
                    message=(
                        "Duplicate data row detected."
                    ),
                    severity=ValidationSeverity.WARNING,
                    row_index=row_index,
                    expected=f"unique row",
                    actual=(
                        f"duplicate of row "
                        f"{seen[key]}"
                    ),
                )
            )

        else:

            seen[key] = row_index

    passed = len(issues) == 0

    return (
        ValidationCheck(
            name="duplicate_rows",
            passed=passed,
            score=(
                1.0
                if passed
                else 0.8
            ),
            message=(
                "No duplicate rows detected."
                if passed
                else "Duplicate rows were detected."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# CELL TYPE VALIDATION
# ============================================================


def validate_cell_types(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate TableCell data classifications.
    """

    issues: list[ValidationIssue] = []

    valid_types = {
        "empty",
        "string",
        "integer",
        "float",
        "number",
        "percentage",
        "date",
    }

    for cell in table.cells:

        if cell.data_type not in valid_types:

            issues.append(
                ValidationIssue(
                    code="INVALID_DATA_TYPE",
                    message=(
                        f"Unsupported data type: "
                        f"{cell.data_type}"
                    ),
                    severity=ValidationSeverity.ERROR,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="data_type",
                    actual=cell.data_type,
                    expected=sorted(valid_types),
                )
            )

    passed = len(issues) == 0

    return (
        ValidationCheck(
            name="cell_types",
            passed=passed,
            score=1.0 if passed else 0.0,
            message=(
                "Cell data types are valid."
                if passed
                else "Invalid cell data types detected."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# DATE VALIDATION
# ============================================================


def validate_dates(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate cells classified as dates.
    """

    issues: list[ValidationIssue] = []

    for cell in table.cells:

        if cell.semantic_type != "date":

            continue

        value = cell.normalized_value

        if not isinstance(
            value,
            str,
        ):

            issues.append(
                ValidationIssue(
                    code="INVALID_DATE",
                    message="Date cell has no valid normalized date.",
                    severity=ValidationSeverity.ERROR,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="normalized_value",
                    actual=value,
                    expected="YYYY-MM-DD",
                )
            )

            continue

        try:

            datetime.strptime(
                value,
                "%Y-%m-%d",
            )

        except ValueError:

            issues.append(
                ValidationIssue(
                    code="INVALID_DATE",
                    message=(
                        "Normalized date is not "
                        "in valid ISO format."
                    ),
                    severity=ValidationSeverity.ERROR,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="normalized_value",
                    actual=value,
                    expected="YYYY-MM-DD",
                )
            )

    passed = len(issues) == 0

    return (
        ValidationCheck(
            name="dates",
            passed=passed,
            score=1.0 if passed else 0.0,
            message=(
                "Date values are valid."
                if passed
                else "Invalid date values detected."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================


def validate_numeric_values(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate numeric and percentage cells.
    """

    issues: list[ValidationIssue] = []

    numeric_types = {
        "integer",
        "float",
        "number",
        "percentage",
    }

    for cell in table.cells:

        if cell.data_type not in numeric_types:

            continue

        if cell.normalized_value is None:

            issues.append(
                ValidationIssue(
                    code="INVALID_NUMERIC_VALUE",
                    message=(
                        "Numeric cell has no normalized value."
                    ),
                    severity=ValidationSeverity.ERROR,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="normalized_value",
                )
            )

    passed = len(issues) == 0

    return (
        ValidationCheck(
            name="numeric_values",
            passed=passed,
            score=1.0 if passed else 0.0,
            message=(
                "Numeric values are valid."
                if passed
                else "Invalid numeric values detected."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# SEMANTIC VALIDATION
# ============================================================


def validate_semantic_values(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate semantic classifications.
    """

    issues: list[ValidationIssue] = []

    valid_semantic_prefixes = {
        "empty",
        "text",
        "number",
        "date",
        "percentage",
        "status",
        "identifier",
        "currency:",
    }

    for cell in table.cells:

        semantic = cell.semantic_type

        if semantic is None:

            if get_cell_value(cell):

                issues.append(
                    ValidationIssue(
                        code="MISSING_SEMANTIC_TYPE",
                        message=(
                            "Non-empty cell has no semantic type."
                        ),
                        severity=ValidationSeverity.WARNING,
                        row_index=cell.row_index,
                        column_index=cell.column_index,
                        cell_id=cell.cell_id,
                        field="semantic_type",
                    )
                )

            continue

        if not any(
            semantic == prefix
            or semantic.startswith(prefix)
            for prefix in valid_semantic_prefixes
        ):

            issues.append(
                ValidationIssue(
                    code="UNKNOWN_SEMANTIC_TYPE",
                    message=(
                        f"Unknown semantic type: "
                        f"{semantic}"
                    ),
                    severity=ValidationSeverity.WARNING,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="semantic_type",
                    actual=semantic,
                )
            )

    passed = not any(
        issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
        for issue in issues
    )

    return (
        ValidationCheck(
            name="semantic_values",
            passed=passed,
            score=(
                1.0
                if passed
                else 0.5
            ),
            message=(
                "Semantic classifications are valid."
                if passed
                else "Semantic validation found errors."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# CONFIDENCE VALIDATION
# ============================================================


def validate_confidence(
    table: Table,
) -> tuple[
    ValidationCheck,
    list[ValidationIssue],
]:
    """
    Validate extraction confidence values.
    """

    issues: list[ValidationIssue] = []

    for cell in table.cells:

        confidence = cell.confidence

        if confidence < 0.0 or confidence > 1.0:

            issues.append(
                ValidationIssue(
                    code="INVALID_CONFIDENCE",
                    message=(
                        "Cell confidence must be "
                        "between 0 and 1."
                    ),
                    severity=ValidationSeverity.ERROR,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="confidence",
                    actual=confidence,
                    expected="0.0 - 1.0",
                )
            )

        elif confidence < 0.50:

            issues.append(
                ValidationIssue(
                    code="LOW_CONFIDENCE",
                    message=(
                        f"Cell confidence is "
                        f"{confidence:.2f}."
                    ),
                    severity=ValidationSeverity.WARNING,
                    row_index=cell.row_index,
                    column_index=cell.column_index,
                    cell_id=cell.cell_id,
                    field="confidence",
                    actual=confidence,
                    expected=">= 0.50",
                )
            )

    passed = not any(
        issue.severity
        in {
            ValidationSeverity.ERROR,
            ValidationSeverity.CRITICAL,
        }
        for issue in issues
    )

    confidence_values = [
        cell.confidence
        for cell in table.cells
    ]

    score = (
        sum(confidence_values)
        / len(confidence_values)
        if confidence_values
        else 0.0
    )

    return (
        ValidationCheck(
            name="confidence",
            passed=passed,
            score=score,
            message=(
                "Confidence values are valid."
                if passed
                else "Invalid confidence values detected."
            ),
            issues_count=len(issues),
        ),
        issues,
    )


# ============================================================
# HELPERS
# ============================================================


def get_cell_value(
    cell: TableCell,
) -> str:
    """
    Get the best available cell representation.

    Priority:

        normalized_text
        text
        raw_text
    """

    if cell.normalized_text is not None:

        return str(
            cell.normalized_text
        ).strip()

    if cell.text:

        return str(
            cell.text
        ).strip()

    if cell.raw_text:

        return str(
            cell.raw_text
        ).strip()

    return ""


# ============================================================
# SCORE
# ============================================================


def calculate_validation_score(
    checks: list[ValidationCheck],
) -> float:
    """
    Calculate weighted validation score.

    Failed checks reduce the overall score.
    """

    if not checks:

        return 0.0

    total = sum(
        check.score
        for check in checks
    )

    return round(
        total / len(checks),
        4,
    )


# ============================================================
# STATUS
# ============================================================


def determine_validation_status(
    issues: list[ValidationIssue],
    score: float,
) -> TableValidationStatus:
    """
    Determine final validation status.
    """

    has_critical = any(
        issue.severity
        == ValidationSeverity.CRITICAL
        for issue in issues
    )

    has_error = any(
        issue.severity
        == ValidationSeverity.ERROR
        for issue in issues
    )

    has_warning = any(
        issue.severity
        == ValidationSeverity.WARNING
        for issue in issues
    )

    if has_critical:

        return TableValidationStatus.INVALID

    if has_error:

        return TableValidationStatus.INVALID

    if score < 0.70:

        return TableValidationStatus.INVALID

    if has_warning:

        return TableValidationStatus.WARNING

    return TableValidationStatus.VALID


# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "VALIDATOR_VERSION",
    "validate_table",
    "validate_structure",
    "validate_headers",
    "validate_row_lengths",
    "validate_empty_cells",
    "validate_duplicate_rows",
    "validate_cell_types",
    "validate_dates",
    "validate_numeric_values",
    "validate_semantic_values",
    "validate_confidence",
]