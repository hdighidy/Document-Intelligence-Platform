"""
Phase 3.1.4.2
Multi-line Cell Reconstruction Test
"""

from pathlib import Path

from app.extraction.table_detector import (
    detect_tables,
)

from app.extraction.table_extractor import (
    extract_tables,
)

from app.extraction.multiline_cell_reconstructor import (
    reconstruct_multiline_cells,
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

DOCUMENT_ID = "DOC-TEST001"


# ============================================================
# MAIN
# ============================================================


def main():

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.4.2 — "
        "MULTI-LINE CELL RECONSTRUCTION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not PDF_PATH.exists():

        raise FileNotFoundError(
            f"PDF not found:\n{PDF_PATH}"
        )

    # --------------------------------------------------------
    # Step 1
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
        f"Detected: "
        f"{len(detected_tables)}"
    )

    # --------------------------------------------------------
    # Step 2
    # --------------------------------------------------------

    print()
    print(
        "Step 2 — Extracting tables..."
    )

    extracted_tables = extract_tables(
        pdf_path=PDF_PATH,
        detected_tables=detected_tables,
    )

    print(
        f"Extracted: "
        f"{len(extracted_tables)}"
    )

    # --------------------------------------------------------
    # Step 3
    # --------------------------------------------------------

    print()
    print(
        "Step 3 — Reconstructing "
        "multi-line cells..."
    )

    reconstructed_tables = []

    for table in extracted_tables:

        reconstructed = (
            reconstruct_multiline_cells(
                table
            )
        )

        reconstructed_tables.append(
            reconstructed
        )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "RECONSTRUCTION RESULTS"
    )
    print("=" * 70)

    for table_number, table in enumerate(
        reconstructed_tables,
        start=1,
    ):

        print()
        print(
            f"TABLE #{table_number}"
        )

        print("-" * 70)

        print(
            f"Table ID: "
            f"{table.table_id}"
        )

        print(
            f"Page: "
            f"{table.page_number}"
        )

        print()

        for cell in table.cells:

            if (
                cell.raw_text
                and "\n" in cell.raw_text
            ):

                print(
                    f"Cell "
                    f"[{cell.row_index},"
                    f"{cell.column_index}]"
                )

                print(
                    f"RAW        : "
                    f"{cell.raw_text!r}"
                )

                print(
                    f"NORMALIZED : "
                    f"{cell.normalized_text!r}"
                )

                print()

        print(
            "Final rows:"
        )

        for row in table.rows:

            print(
                row
            )

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.4.2 TEST COMPLETED"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    main()