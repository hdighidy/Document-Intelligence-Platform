"""
Phase 3.1.4
============

Table Cleaning & Normalization Test

Pipeline:

    PDF
     ↓
    Detection
     ↓
    Extraction
     ↓
    Cleaning
     ↓
    Multi-line Reconstruction
     ↓
    Semantic Normalization
     ↓
    Validation / Reporting
     ↓
    Normalized Table


Purpose
-------

This script is ONLY a test/validation script.

It does NOT contain production extraction logic.

It validates:

    Phase 3.1.4
        - whitespace cleaning
        - line-break normalization
        - row normalization
        - duplicate detection

    Phase 3.1.4.1
        - header/title information

    Phase 3.1.4.2
        - multi-line reconstruction
        - raw_text preservation
        - normalized_text

    Phase 3.1.4.3
        - normalized_value
        - semantic_type
        - data_type
        - numeric_value
        - normalization_source
"""

from pathlib import Path

from app.extraction.table_cleaner import clean_table
from app.extraction.table_detector import detect_tables
from app.extraction.table_extractor import extract_tables


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
# SAFE ATTRIBUTE HELPER
# ============================================================

def get_attr(
    obj,
    name,
    default=None,
):
    """
    Safely read a model attribute.

    This is intentionally used in the test script so that
    the diagnostic script does not crash if an optional field
    has not yet been added to the model.
    """

    return getattr(
        obj,
        name,
        default,
    )


# ============================================================
# VALUE DISPLAY HELPER
# ============================================================

def display_value(
    value,
):
    """
    Convert a value into a readable diagnostic representation.
    """

    if value is None:
        return "None"

    return repr(value)


# ============================================================
# CELL REPORT
# ============================================================

def print_cell_report(
    table,
):
    """
    Print the complete state of every TableCell.

    This is the most important diagnostic section.

    It allows us to distinguish between:

        raw extraction problem
        cleaning problem
        reconstruction problem
        semantic normalization problem
        reporting/test-script problem
    """

    print()
    print("=" * 100)
    print("CELL-LEVEL DIAGNOSTIC REPORT")
    print("=" * 100)

    for cell in table.cells:

        raw_text = get_attr(
            cell,
            "raw_text",
            None,
        )

        text = get_attr(
            cell,
            "text",
            None,
        )

        normalized_text = get_attr(
            cell,
            "normalized_text",
            None,
        )

        normalized_value = get_attr(
            cell,
            "normalized_value",
            None,
        )

        data_type = get_attr(
            cell,
            "data_type",
            None,
        )

        semantic_type = get_attr(
            cell,
            "semantic_type",
            None,
        )

        numeric_value = get_attr(
            cell,
            "numeric_value",
            None,
        )

        normalization_source = get_attr(
            cell,
            "normalization_source",
            None,
        )

        print()
        print(
            f"[{cell.row_index},"
            f"{cell.column_index}]"
        )

        print(
            f"  raw_text             : "
            f"{display_value(raw_text)}"
        )

        print(
            f"  text                 : "
            f"{display_value(text)}"
        )

        print(
            f"  normalized_text      : "
            f"{display_value(normalized_text)}"
        )

        print(
            f"  normalized_value     : "
            f"{display_value(normalized_value)}"
        )

        print(
            f"  data_type            : "
            f"{display_value(data_type)}"
        )

        print(
            f"  semantic_type        : "
            f"{display_value(semantic_type)}"
        )

        print(
            f"  numeric_value        : "
            f"{display_value(numeric_value)}"
        )

        print(
            f"  normalization_source : "
            f"{display_value(normalization_source)}"
        )


# ============================================================
# MULTI-LINE TEST
# ============================================================

def test_multiline_reconstruction(
    table,
):
    """
    Explicitly validate Phase 3.1.4.2.

    Expected examples:

        Air Handlig\\nunit
            →
        Air Handlig unit

        Fire Fighting\\npump
            →
        Fire Fighting pump
    """

    print()
    print("=" * 100)
    print("MULTI-LINE RECONSTRUCTION CHECK")
    print("=" * 100)

    found_multiline = False

    for cell in table.cells:

        raw_text = get_attr(
            cell,
            "raw_text",
            "",
        )

        normalized_text = get_attr(
            cell,
            "normalized_text",
            None,
        )

        if raw_text and (
            "\n" in str(raw_text)
            or "\r" in str(raw_text)
        ):

            found_multiline = True

            print()
            print(
                f"Cell [{cell.row_index},"
                f"{cell.column_index}]"
            )

            print(
                f"  RAW        : "
                f"{repr(raw_text)}"
            )

            print(
                f"  NORMALIZED : "
                f"{repr(normalized_text)}"
            )

    if not found_multiline:

        print(
            "No raw multi-line cells detected."
        )


# ============================================================
# SEMANTIC NORMALIZATION CHECK
# ============================================================

def test_semantic_normalization(
    table,
):
    """
    Display Phase 3.1.4.3 semantic normalization results.
    """

    print()
    print("=" * 100)
    print("SEMANTIC NORMALIZATION CHECK")
    print("=" * 100)

    for cell in table.cells:

        normalized_value = get_attr(
            cell,
            "normalized_value",
            None,
        )

        semantic_type = get_attr(
            cell,
            "semantic_type",
            None,
        )

        data_type = get_attr(
            cell,
            "data_type",
            None,
        )

        normalization_source = get_attr(
            cell,
            "normalization_source",
            None,
        )

        text = get_attr(
            cell,
            "text",
            None,
        )

        print(
            f"[{cell.row_index},"
            f"{cell.column_index}] "
            f"{display_value(text)}"
        )

        print(
            f"    data_type            = "
            f"{display_value(data_type)}"
        )

        print(
            f"    semantic_type        = "
            f"{display_value(semantic_type)}"
        )

        print(
            f"    normalized_value     = "
            f"{display_value(normalized_value)}"
        )

        print(
            f"    normalization_source = "
            f"{display_value(normalization_source)}"
        )


# ============================================================
# EXPECTED VALUE CHECKS
# ============================================================

def run_expected_value_checks(
    table,
):
    """
    Validate the known values from sample.pdf.

    These checks are intentionally based on the current
    sample table shown during Phase 3.1.4 testing.
    """

    print()
    print("=" * 100)
    print("EXPECTED VALUE CHECKS")
    print("=" * 100)

    checks = []

    # --------------------------------------------------------
    # Find cells by their raw/cleaned content
    # --------------------------------------------------------

    for cell in table.cells:

        raw_text = str(
            get_attr(
                cell,
                "raw_text",
                "",
            )
            or ""
        )

        normalized_text = get_attr(
            cell,
            "normalized_text",
            None,
        )

        normalized_value = get_attr(
            cell,
            "normalized_value",
            None,
        )

        semantic_type = get_attr(
            cell,
            "semantic_type",
            None,
        )

        # ----------------------------------------------------
        # Air Handling Unit
        # ----------------------------------------------------

        if "Air Handlig" in raw_text:

            checks.append(
                (
                    "Air Handlig multiline reconstruction",
                    normalized_text
                    == "Air Handlig unit",
                )
            )

        # ----------------------------------------------------
        # Fire Fighting pump
        # ----------------------------------------------------

        if "Fire Fighting" in raw_text:

            checks.append(
                (
                    "Fire Fighting multiline reconstruction",
                    normalized_text
                    == "Fire Fighting pump",
                )
            )

        # ----------------------------------------------------
        # AHU identifier
        # ----------------------------------------------------

        if raw_text.strip() == "AHU-B50":

            checks.append(
                (
                    "AHU-B50 identifier detection",
                    semantic_type
                    == "identifier",
                )
            )

        # ----------------------------------------------------
        # Quantity = 2
        # ----------------------------------------------------

        if raw_text.strip() == "2":

            checks.append(
                (
                    "Quantity 2 numeric normalization",
                    normalized_value == 2,
                )
            )

        # ----------------------------------------------------
        # Unit price
        # ----------------------------------------------------

        if raw_text.strip() == "1,250,000":

            checks.append(
                (
                    "Unit price numeric normalization",
                    normalized_value == 1250000,
                )
            )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if raw_text.strip().lower() == "done":

            checks.append(
                (
                    "Done status normalization",
                    normalized_value == "DONE",
                )
            )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    if not checks:

        print(
            "No known sample-value checks were triggered."
        )

        return

    passed = 0

    for description, result in checks:

        status = (
            "PASS"
            if result
            else "FAIL"
        )

        print(
            f"[{status}] {description}"
        )

        if result:
            passed += 1

    print()
    print(
        f"Checks passed: "
        f"{passed}/{len(checks)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.4 — TABLE CLEANING & NORMALIZATION"
    )
    print("=" * 70)

    # ========================================================
    # Validate PDF
    # ========================================================

    if not PDF_PATH.exists():

        raise FileNotFoundError(
            f"\nPDF not found:\n"
            f"{PDF_PATH}"
        )

    print()
    print(
        f"PDF: {PDF_PATH}"
    )

    # ========================================================
    # Step 1 — Detection
    # ========================================================

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

    if not detected_tables:

        print(
            "No tables detected."
        )

        return

    # ========================================================
    # Step 2 — Extraction
    # ========================================================

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

    if not extracted_tables:

        print(
            "No tables extracted."
        )

        return

    # ========================================================
    # Step 3 — Cleaning
    # ========================================================

    print()
    print(
        "Step 3 — Cleaning tables..."
    )

    cleaned_tables = []

    for table in extracted_tables:

        cleaned = clean_table(
            table
        )

        cleaned_tables.append(
            cleaned
        )

    # ========================================================
    # Results
    # ========================================================

    print()
    print("=" * 70)
    print(
        "CLEANING RESULTS"
    )
    print("=" * 70)

    for index, table in enumerate(
        cleaned_tables,
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
            f"Table ID          : "
            f"{table.table_id}"
        )

        print(
            f"Page              : "
            f"{table.page_number}"
        )

        print(
            f"Rows              : "
            f"{table.row_count}"
        )

        print(
            f"Columns           : "
            f"{table.column_count}"
        )

        print(
            f"Cleaning applied   : "
            f"{table.cleaning_applied}"
        )

        print(
            f"Empty cells       : "
            f"{table.empty_cell_count}"
        )

        print(
            f"Duplicate rows    : "
            f"{table.duplicate_row_count}"
        )

        print()

        # ----------------------------------------------------
        # Headers
        # ----------------------------------------------------

        print(
            "Headers:"
        )

        print(
            table.headers
        )

        # ----------------------------------------------------
        # Rows
        # ----------------------------------------------------

        print()

        print(
            "Normalized rows:"
        )

        for row_index, row in enumerate(
            table.rows
        ):

            print(
                f"  Row {row_index}: "
                f"{row}"
            )

        # ----------------------------------------------------
        # Cell diagnostics
        # ----------------------------------------------------

        print_cell_report(
            table
        )

        # ----------------------------------------------------
        # Multi-line reconstruction
        # ----------------------------------------------------

        test_multiline_reconstruction(
            table
        )

        # ----------------------------------------------------
        # Semantic normalization
        # ----------------------------------------------------

        test_semantic_normalization(
            table
        )

        # ----------------------------------------------------
        # Expected values
        # ----------------------------------------------------

        run_expected_value_checks(
            table
        )

    # ========================================================
    # Completion
    # ========================================================

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.4 TEST COMPLETED"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()