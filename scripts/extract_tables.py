"""
Table Extraction Test Script
============================

Phase 3.1.3

Pipeline:

    PDF
     ↓
    Table Detection
     ↓
    Table Extraction
     ↓
    Table / TableCell models

This script is for development and QC.
"""

from pathlib import Path

from app.extraction.table_detector import (
    detect_tables,
)

from app.extraction.table_extractor import (
    extract_tables,
)


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)

DOCUMENT_ID = (
    "DOC-TEST001"
)


# ============================================================
# MAIN
# ============================================================


def main():

    print()
    print("=" * 70)
    print("PHASE 3.1.3 — TABLE EXTRACTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not PDF_PATH.exists():

        raise FileNotFoundError(
            "\nPDF file not found:\n"
            f"{PDF_PATH}\n"
        )

    print(
        f"PDF:\n{PDF_PATH}"
    )

    # --------------------------------------------------------
    # Phase 3.1.2
    # Detect tables
    # --------------------------------------------------------

    print()
    print(
        "Step 1 — Detecting tables..."
    )

    detected_tables = detect_tables(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    print(
        f"Detected tables: "
        f"{len(detected_tables)}"
    )

    if not detected_tables:

        print()
        print(
            "No tables detected."
        )

        return

    # --------------------------------------------------------
    # Phase 3.1.3
    # Extract tables
    # --------------------------------------------------------

    print()
    print(
        "Step 2 — Extracting tables..."
    )

    extracted_tables = (
        extract_tables(
            pdf_path=PDF_PATH,
            detected_tables=detected_tables,
        )
    )

    print(
        f"Extracted tables: "
        f"{len(extracted_tables)}"
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EXTRACTION RESULTS")
    print("=" * 70)

    for index, table in enumerate(
        extracted_tables,
        start=1,
    ):

        print()
        print(
            f"TABLE #{index}"
        )

        print(
            "-" * 70
        )

        print(
            f"ID       : "
            f"{table.table_id}"
        )

        print(
            f"Page     : "
            f"{table.page_number}"
        )

        print(
            f"Rows     : "
            f"{table.row_count}"
        )

        print(
            f"Columns  : "
            f"{table.column_count}"
        )

        print(
            f"Headers  : "
            f"{table.headers}"
        )

        print()

        print(
            "Rows:"
        )

        for row_index, row in enumerate(
            table.rows
        ):

            print(
                f"  {row_index}: "
                f"{row}"
            )

        print()

        print(
            f"Cells extracted: "
            f"{len(table.cells)}"
        )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.3 TEST COMPLETED"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    main()