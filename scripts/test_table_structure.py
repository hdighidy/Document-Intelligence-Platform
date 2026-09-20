"""
Phase 3.1.7 — Table Structure Analysis Test
============================================

End-to-end test for:

    1. Table detection
    2. Table extraction
    3. Table cleaning
    4. Table structure analysis
    5. Structure result verification
    6. Automated validation checks

IMPORTANT
---------
The structure analyzer returns a NEW analyzed Table object.

Therefore this test intentionally does:

    analyzed_table = analyze_table_structure(table)

and NEVER assumes that the original table was mutated.

Expected pipeline:

    PDF
      ↓
    Detection
      ↓
    Extraction
      ↓
    Cleaning
      ↓
    Structure Analysis
      ↓
    Verified analyzed tables
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from app.models.table import Table

from app.extraction.table_detector import detect_tables
from app.extraction.table_extractor import extract_tables
from app.extraction.table_cleaner import clean_table
from app.extraction.table_structure.structure_analyzer import (
    analyze_table_structure,
)


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)


# ============================================================
# DISPLAY HELPERS
# ============================================================


def line(char: str = "=", length: int = 70) -> None:
    print(char * length)


def section(title: str) -> None:
    print()
    line("=")
    print(title)
    line("=")


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    if value is None:
        return default

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_list(
    value: Any,
) -> list:
    """
    Safely convert a value to list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


# ============================================================
# STRUCTURE SUMMARY
# ============================================================


def print_structure_summary(
    table: Table,
    index: int,
) -> None:
    """
    Print the complete Phase 3.1.7 structure result.
    """

    print()
    print(
        f"TABLE #{index}"
    )
    line("-")

    print()
    print("STRUCTURE RESULTS")
    line("-")

    print(
        f"Table ID                : "
        f"{getattr(table, 'table_id', '')}"
    )

    print(
        f"Rows                    : "
        f"{getattr(table, 'row_count', 0)}"
    )

    print(
        f"Columns                 : "
        f"{getattr(table, 'column_count', 0)}"
    )

    print(
        f"Structure analyzed      : "
        f"{getattr(table, 'structure_analyzed', False)}"
    )

    print(
        f"Structure type          : "
        f"{getattr(table, 'structure_type', None)}"
    )

    structure_confidence = getattr(
        table,
        "structure_confidence",
        None,
    )

    if structure_confidence is None:
        print(
            "Structure confidence    : None"
        )
    else:
        print(
            f"Structure confidence    : "
            f"{safe_float(structure_confidence):.4f}"
        )

    print()

    title_rows = safe_list(
        getattr(
            table,
            "title_row_indices",
            [],
        )
    )

    header_rows = safe_list(
        getattr(
            table,
            "header_row_indices",
            [],
        )
    )

    data_rows = safe_list(
        getattr(
            table,
            "data_row_indices",
            [],
        )
    )

    empty_rows = safe_list(
        getattr(
            table,
            "empty_row_indices",
            [],
        )
    )

    print(
        f"Title rows              : "
        f"{title_rows}"
    )

    print(
        f"Header rows             : "
        f"{header_rows}"
    )

    print(
        f"Data rows               : "
        f"{data_rows}"
    )

    print(
        f"Empty rows              : "
        f"{empty_rows}"
    )

    print()

    print(
        f"Data start row          : "
        f"{getattr(table, 'data_start_row_index', None)}"
    )

    print(
        f"Data end row            : "
        f"{getattr(table, 'data_end_row_index', None)}"
    )

    print()

    print(
        f"Has title               : "
        f"{getattr(table, 'has_title', False)}"
    )

    print(
        f"Has header              : "
        f"{getattr(table, 'has_header', False)}"
    )

    print(
        f"Has data rows           : "
        f"{getattr(table, 'has_data_rows', False)}"
    )

    print(
        f"Has empty rows          : "
        f"{getattr(table, 'has_empty_rows', False)}"
    )

    print(
        f"Possible merged cells   : "
        f"{getattr(table, 'has_merged_cells', False)}"
    )

    print(
        f"Multi-level header      : "
        f"{getattr(table, 'has_multi_level_header', False)}"
    )

    print()

    print(
        "Title confidence        : "
        f"{_format_optional_float(table, 'title_confidence')}"
    )

    print(
        "Header confidence       : "
        f"{_format_optional_float(table, 'header_confidence')}"
    )

    print(
        "Data boundary confidence: "
        f"{_format_optional_float(table, 'data_boundary_confidence')}"
    )

    print()

    print(
        "Row consistency         : "
        f"{_format_optional_float(table, 'row_consistency_score')}"
    )

    print(
        "Column consistency      : "
        f"{_format_optional_float(table, 'column_consistency_score')}"
    )


def _format_optional_float(
    table: Table,
    field_name: str,
) -> str:
    """
    Safely format optional float fields.
    """

    value = getattr(
        table,
        field_name,
        None,
    )

    if value is None:
        return "None"

    return f"{safe_float(value):.4f}"


# ============================================================
# LOGICAL STRUCTURE
# ============================================================


def print_logical_structure(
    table: Table,
) -> None:
    """
    Print logical row classification.
    """

    print()
    print("LOGICAL STRUCTURE")
    line("-")

    rows = getattr(
        table,
        "rows",
        [],
    )

    title_rows = set(
        safe_list(
            getattr(
                table,
                "title_row_indices",
                [],
            )
        )
    )

    header_rows = set(
        safe_list(
            getattr(
                table,
                "header_row_indices",
                [],
            )
        )
    )

    data_rows = set(
        safe_list(
            getattr(
                table,
                "data_row_indices",
                [],
            )
        )
    )

    empty_rows = set(
        safe_list(
            getattr(
                table,
                "empty_row_indices",
                [],
            )
        )
    )

    for index, row in enumerate(rows):

        if index in title_rows:
            role = "TITLE"

        elif index in header_rows:
            role = "HEADER"

        elif index in data_rows:
            role = "DATA"

        elif index in empty_rows:
            role = "EMPTY"

        else:
            role = "OTHER"

        print(
            f"[{index:02d}] "
            f"{role:<7} "
            f"{row}"
        )


# ============================================================
# DIAGNOSTICS
# ============================================================


def print_diagnostics(
    table: Table,
) -> None:
    """
    Print structure diagnostics.
    """

    print()
    print("STRUCTURE DIAGNOSTICS")
    line("-")

    issues = safe_list(
        getattr(
            table,
            "structure_issues",
            [],
        )
    )

    warnings = safe_list(
        getattr(
            table,
            "structure_warnings",
            [],
        )
    )

    if not issues:
        print("Issues   : None")

    else:
        print("Issues   :")

        for issue in issues:
            print(
                f"  - {issue}"
            )

    if not warnings:
        print("Warnings : None")

    else:
        print("Warnings :")

        for warning in warnings:
            print(
                f"  - {warning}"
            )


# ============================================================
# HEADERS
# ============================================================


def print_headers(
    table: Table,
) -> None:

    print()
    print("HEADERS")
    line("-")

    headers = getattr(
        table,
        "headers",
        [],
    )

    print(headers)


# ============================================================
# TITLE
# ============================================================


def print_title(
    table: Table,
) -> None:

    print()
    print("TITLE")
    line("-")

    print(
        getattr(
            table,
            "title",
            None,
        )
    )


# ============================================================
# DATA ROWS
# ============================================================


def print_data_rows(
    table: Table,
) -> None:

    print()
    print("DATA ROWS")
    line("-")

    data_rows = getattr(
        table,
        "data_rows",
        [],
    )

    for row in data_rows:
        print(row)


# ============================================================
# AUTOMATED CHECKS
# ============================================================


def run_structure_checks(
    tables: list[Table],
) -> tuple[int, int]:
    """
    Run automated Phase 3.1.7 checks.

    Returns:

        passed_checks,
        failed_checks
    """

    print()
    line("=")
    print("AUTOMATED STRUCTURE CHECKS")
    line("=")

    passed = 0
    failed = 0

    def check(
        name: str,
        condition: bool,
    ) -> None:

        nonlocal passed
        nonlocal failed

        if condition:

            print(
                f"PASS  {name}"
            )

            passed += 1

        else:

            print(
                f"FAIL  {name}"
            )

            failed += 1

    for table in tables:

        # ----------------------------------------------------
        # 1
        # ----------------------------------------------------

        check(
            "structure_analyzed",
            bool(
                getattr(
                    table,
                    "structure_analyzed",
                    False,
                )
            ),
        )

        # ----------------------------------------------------
        # 2
        # ----------------------------------------------------

        structure_type = getattr(
            table,
            "structure_type",
            None,
        )

        check(
            "structure_type_detected",
            structure_type is not None
            and str(structure_type).strip() != "",
        )

        # ----------------------------------------------------
        # 3
        # ----------------------------------------------------

        header_rows = safe_list(
            getattr(
                table,
                "header_row_indices",
                [],
            )
        )

        check(
            "header_detected",
            bool(header_rows)
            or bool(
                getattr(
                    table,
                    "has_header",
                    False,
                )
            ),
        )

        # ----------------------------------------------------
        # 4
        # ----------------------------------------------------

        data_rows = safe_list(
            getattr(
                table,
                "data_row_indices",
                [],
            )
        )

        check(
            "data_rows_detected",
            bool(data_rows)
            or bool(
                getattr(
                    table,
                    "has_data_rows",
                    False,
                )
            ),
        )

        # ----------------------------------------------------
        # 5
        # ----------------------------------------------------

        data_start = getattr(
            table,
            "data_start_row_index",
            None,
        )

        check(
            "data_start_detected",
            data_start is not None,
        )

        # ----------------------------------------------------
        # 6
        # ----------------------------------------------------

        data_end = getattr(
            table,
            "data_end_row_index",
            None,
        )

        check(
            "data_end_detected",
            data_end is not None,
        )

        # ----------------------------------------------------
        # 7
        # ----------------------------------------------------

        row_consistency = getattr(
            table,
            "row_consistency_score",
            None,
        )

        check(
            "row_consistency_valid",
            row_consistency is not None
            and 0.0
            <= safe_float(row_consistency)
            <= 1.0,
        )

        # ----------------------------------------------------
        # 8
        # ----------------------------------------------------

        column_consistency = getattr(
            table,
            "column_consistency_score",
            None,
        )

        check(
            "column_consistency_valid",
            column_consistency is not None
            and 0.0
            <= safe_float(column_consistency)
            <= 1.0,
        )

        # ----------------------------------------------------
        # 9
        # ----------------------------------------------------

        structure_confidence = getattr(
            table,
            "structure_confidence",
            None,
        )

        check(
            "structure_confidence_valid",
            structure_confidence is not None
            and 0.0
            <= safe_float(structure_confidence)
            <= 1.0,
        )

    print()

    line("-")

    print(
        f"Checks passed: {passed}"
    )

    print(
        f"Checks failed: {failed}"
    )

    return passed, failed


# ============================================================
# TABLE PIPELINE
# ============================================================


def run_pipeline(
    pdf_path: Path,
) -> list[Table]:

    section(
        "PHASE 3.1.7 — TABLE STRUCTURE ANALYSIS"
    )

    print()

    print(
        f"PDF: {pdf_path}"
    )

    # ========================================================
    # STEP 1 — DETECTION
    # ========================================================

    print()
    print("Step 1 — Detecting tables...")

    document_id = f"TEST-{pdf_path.stem.upper()}"

    detected_tables = detect_tables(
        pdf_path,
        document_id,
    )

    print(
        f"Detected tables: {len(detected_tables)}"
    )

    # ========================================================
    # STEP 2 — EXTRACTION
    # ========================================================

    print()
    print(
        "Step 2 — Extracting tables..."
    )

    extracted_tables = extract_tables(
        pdf_path,
        detected_tables,
    )

    print(
        f"Extracted tables: "
        f"{len(extracted_tables)}"
    )

    # ========================================================
    # STEP 3 — CLEANING
    # ========================================================

    print()
    print(
        "Step 3 — Cleaning tables..."
    )

    cleaned_tables: list[Table] = []

    for table in extracted_tables:

        cleaned = clean_table(
            table
        )

        cleaned_tables.append(
            cleaned
        )

    print(
        f"Cleaned tables: "
        f"{len(cleaned_tables)}"
    )

    # ========================================================
    # STEP 4 — STRUCTURE ANALYSIS
    # ========================================================

    print()
    print(
        "Step 4 — Analyzing structure..."
    )

    analyzed_tables: list[Table] = []

    for table in cleaned_tables:

        # IMPORTANT:
        #
        # analyze_table_structure()
        # returns the analyzed Table.
        #
        # We MUST capture the return value.

        analyzed_table = (
            analyze_table_structure(
                table
            )
        )

        analyzed_tables.append(
            analyzed_table
        )

        # Immediate verification

        print(
            f"  {analyzed_table.table_id}: "
            f"analyzed="
            f"{getattr(analyzed_table, 'structure_analyzed', False)}, "
            f"type="
            f"{getattr(analyzed_table, 'structure_type', None)}, "
            f"headers="
            f"{getattr(analyzed_table, 'header_row_indices', [])}, "
            f"data="
            f"{getattr(analyzed_table, 'data_row_indices', [])}"
        )

    print()
    print(
        f"Analyzed tables: "
        f"{len(analyzed_tables)}"
    )

    return analyzed_tables


# ============================================================
# MAIN
# ============================================================


def main() -> int:

    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not PDF_PATH.exists():

        print()
        print(
            "ERROR: Test PDF was not found."
        )

        print(
            f"Expected: {PDF_PATH}"
        )

        return 1

    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    try:

        analyzed_tables = run_pipeline(
            PDF_PATH
        )

    except Exception as exc:

        print()
        print(
            "ERROR during Phase 3.1.7:"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise

    # --------------------------------------------------------
    # No tables
    # --------------------------------------------------------

    if not analyzed_tables:

        print()
        print(
            "FAIL — No tables were analyzed."
        )

        return 1

    # ========================================================
    # RESULTS
    # ========================================================

    section(
        "PHASE 3.1.7 RESULTS"
    )

    for index, table in enumerate(
        analyzed_tables,
        start=1,
    ):

        print_structure_summary(
            table,
            index,
        )

        print_logical_structure(
            table
        )

        print_diagnostics(
            table
        )

        print_headers(
            table
        )

        print_title(
            table
        )

        print_data_rows(
            table
        )

    # ========================================================
    # AUTOMATED CHECKS
    # ========================================================

    passed, failed = (
        run_structure_checks(
            analyzed_tables
        )
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()

    line("=")

    if failed == 0:

        print(
            "PASS — Phase 3.1.7 "
            "Table Structure Analysis "
            "completed successfully."
        )

        line("=")

        return 0

    print(
        f"FAIL — {failed} checks failed."
    )

    print(
        "Please review the output above."
    )

    line("=")

    return 1


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    raise SystemExit(
        main()
    )