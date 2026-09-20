"""
Table Detection Test Script
===========================

Phase 3.1.2

Purpose:
    - Validate the test PDF path
    - Validate that the file is a PDF
    - Run table detection
    - Display detected tables
    - Display detection statistics

This is a DEVELOPMENT / QC script.

It does NOT belong to the production ingestion pipeline.
"""

from pathlib import Path

from app.extraction.table_detector import (
    detect_tables,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Test PDF
PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)


# Temporary document ID for testing
DOCUMENT_ID = "DOC-TEST001"


# ============================================================
# VALIDATE INPUT PDF
# ============================================================


def validate_input_pdf(
    pdf_path: Path,
) -> None:
    """
    Validate that the input PDF exists
    and is actually a PDF file.
    """

    print()
    print("=" * 70)
    print("INPUT VALIDATION")
    print("=" * 70)

    print(
        f"Expected PDF:\n"
        f"{pdf_path}"
    )

    # --------------------------------------------------------
    # Check existence
    # --------------------------------------------------------

    if not pdf_path.exists():

        raise FileNotFoundError(
            "\n"
            "PDF file was not found.\n\n"
            f"Expected location:\n"
            f"{pdf_path}\n\n"
            "Please place your test PDF at:\n"
            f"{PROJECT_ROOT / 'data' / 'test' / 'sample.pdf'}"
        )

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not pdf_path.is_file():

        raise ValueError(
            f"\nThe path exists but is not a file:\n"
            f"{pdf_path}"
        )

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if pdf_path.suffix.lower() != ".pdf":

        raise ValueError(
            "\nThe input file must have a .pdf extension.\n"
            f"Received: {pdf_path.name}"
        )

    # --------------------------------------------------------
    # Check file size
    # --------------------------------------------------------

    file_size = pdf_path.stat().st_size

    if file_size == 0:

        raise ValueError(
            "\nThe PDF file is empty:\n"
            f"{pdf_path}"
        )

    print(
        "✓ File exists"
    )

    print(
        f"✓ File name: {pdf_path.name}"
    )

    print(
        f"✓ File size: "
        f"{file_size / 1024:.2f} KB"
    )

    print(
        "✓ PDF path validation passed"
    )


# ============================================================
# PRINT TABLE
# ============================================================


def print_table_details(
    table,
    index: int,
) -> None:
    """
    Print details for one detected table.
    """

    print()
    print(
        f"TABLE #{index}"
    )

    print(
        "-" * 70
    )

    print(
        f"Table ID       : "
        f"{table.table_id}"
    )

    print(
        f"Document ID    : "
        f"{table.document_id}"
    )

    print(
        f"Page Number    : "
        f"{table.page_number}"
    )

    print(
        f"Extraction     : "
        f"{table.extraction_method}"
    )

    if table.source_filename:

        print(
            f"Source File    : "
            f"{table.source_filename}"
        )

    # --------------------------------------------------------
    # Bounding box
    # --------------------------------------------------------

    if table.bbox:

        print(
            "Bounding Box   : "
            f"x0={table.bbox.x0:.2f}, "
            f"y0={table.bbox.y0:.2f}, "
            f"x1={table.bbox.x1:.2f}, "
            f"y1={table.bbox.y1:.2f}"
        )

        width = (
            table.bbox.x1
            - table.bbox.x0
        )

        height = (
            table.bbox.y1
            - table.bbox.y0
        )

        print(
            f"Dimensions     : "
            f"{width:.2f} x "
            f"{height:.2f}"
        )

    else:

        print(
            "Bounding Box   : NOT AVAILABLE"
        )


# ============================================================
# DETECTION SUMMARY
# ============================================================


def print_detection_summary(
    tables,
) -> None:
    """
    Print summary statistics.
    """

    print()
    print("=" * 70)
    print("TABLE DETECTION SUMMARY")
    print("=" * 70)

    total_tables = len(
        tables
    )

    unique_pages = sorted(
        {
            table.page_number
            for table in tables
        }
    )

    print(
        f"Total tables detected : "
        f"{total_tables}"
    )

    print(
        f"Pages containing tables: "
        f"{len(unique_pages)}"
    )

    if unique_pages:

        print(
            f"Table pages           : "
            f"{unique_pages}"
        )

    else:

        print(
            "Table pages           : None"
        )

    # --------------------------------------------------------
    # Tables per page
    # --------------------------------------------------------

    if tables:

        print()
        print(
            "Tables per page:"
        )

        page_counts = {}

        for table in tables:

            page_counts[
                table.page_number
            ] = (
                page_counts.get(
                    table.page_number,
                    0,
                )
                + 1
            )

        for page_number in sorted(
            page_counts
        ):

            print(
                f"  Page {page_number}: "
                f"{page_counts[page_number]} table(s)"
            )


# ============================================================
# MAIN
# ============================================================


def main():
    """
    Main test execution.
    """

    print()
    print("=" * 70)
    print("PHASE 3.1.2 — TABLE DETECTION")
    print("=" * 70)

    print(
        f"Project root:\n"
        f"{PROJECT_ROOT}"
    )

    # ========================================================
    # 1. Validate PDF
    # ========================================================

    validate_input_pdf(
        PDF_PATH
    )

    # ========================================================
    # 2. Run table detection
    # ========================================================

    print()
    print("=" * 70)
    print("TABLE DETECTION")
    print("=" * 70)

    print(
        "Starting table detection..."
    )

    print(
        f"PDF:\n{PDF_PATH}"
    )

    print(
        f"Document ID:\n{DOCUMENT_ID}"
    )

    try:

        tables = detect_tables(
            pdf_path=PDF_PATH,
            document_id=DOCUMENT_ID,
        )

    except Exception as exc:

        print()
        print(
            "ERROR: Table detection failed."
        )

        print(
            f"Error type: "
            f"{type(exc).__name__}"
        )

        print(
            f"Error message:\n"
            f"{exc}"
        )

        raise

    # ========================================================
    # 3. Print results
    # ========================================================

    print()
    print(
        f"Detection completed successfully."
    )

    print(
        f"Tables detected: "
        f"{len(tables)}"
    )

    # ========================================================
    # 4. Display individual tables
    # ========================================================

    if tables:

        for index, table in enumerate(
            tables,
            start=1,
        ):

            print_table_details(
                table=table,
                index=index,
            )

    else:

        print()
        print(
            "No tables were detected."
        )

        print()
        print(
            "This does NOT necessarily mean "
            "the PDF contains no tables."
        )

        print(
            "The table may use a layout that "
            "requires a different detection strategy."
        )

    # ========================================================
    # 5. Summary
    # ========================================================

    print_detection_summary(
        tables
    )

    # ========================================================
    # 6. Completion
    # ========================================================

    print()
    print("=" * 70)
    print("PHASE 3.1.2 TEST COMPLETED")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    main()