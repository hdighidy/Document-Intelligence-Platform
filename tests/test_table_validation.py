"""
Phase 3.1.6.2
Table Validation Engine Test
"""

from app.models.table import (
    Table,
    TableCell,        #Line 844
    TableValidationStatus,
)

from app.validation.table_validator import (
    validate_table,
)


def build_test_table() -> Table:

    cells = [
        TableCell(
            cell_id="CELL-001",
            row_index=0,
            column_index=0,
            raw_text="Material",
            text="Material",
            normalized_text="Material",
            normalized_value="Material",
            data_type="string",
            semantic_type="text",
            confidence=0.99,
        ),
        TableCell(
            cell_id="CELL-002",
            row_index=0,
            column_index=1,
            raw_text="Quantity",
            text="Quantity",
            normalized_text="Quantity",
            normalized_value="Quantity",
            data_type="string",
            semantic_type="text",
            confidence=0.99,
        ),
        TableCell(
            cell_id="CELL-003",
            row_index=1,
            column_index=0,
            raw_text="AHU-B50",
            text="AHU-B50",
            normalized_text="AHU-B50",
            normalized_value="AHU-B50",
            data_type="string",
            semantic_type="identifier",
            confidence=0.98,
        ),
        TableCell(
            cell_id="CELL-004",
            row_index=1,
            column_index=1,
            raw_text="2",
            text="2",
            normalized_text="2",
            normalized_value=2,
            data_type="integer",
            semantic_type="number",
            confidence=0.98,
        ),
    ]

    return Table(
        table_id="TABLE-TEST-001",
        document_id="DOC-TEST-001",
        table_index=0,
        page_number=1,
        rows=[
            ["Material", "Quantity"],
            ["AHU-B50", "2"],
        ],
        headers=[
            "Material",
            "Quantity",
        ],
        cells=cells,
        row_count=2,
        column_count=2,
        header_row_index=0,
        cleaning_applied=True,
    )


def main():

    print()
    print("=" * 70)
    print("PHASE 3.1.6.2 — TABLE VALIDATION ENGINE")
    print("=" * 70)

    table = build_test_table()

    print()
    print("Validating table...")

    result = validate_table(
        table
    )

    print()
    print("=" * 70)
    print("VALIDATION RESULT")
    print("=" * 70)

    print(
        f"Status          : {result.status}"
    )

    print(
        f"Score           : {result.score:.4f}"
    )

    print(
        f"Total checks    : {result.total_checks}"
    )

    print(
        f"Passed checks   : {result.passed_checks}"
    )

    print(
        f"Failed checks   : {result.failed_checks}"
    )

    print(
        f"Errors          : {result.error_count}"
    )

    print(
        f"Warnings        : {result.warning_count}"
    )

    print()
    print("CHECKS")
    print("-" * 70)

    for check in result.checks:

        print(
            f"{check.name:25}"
            f" | "
            f"{'PASS' if check.passed else 'FAIL':4}"
            f" | "
            f"{check.score:.2f}"
            f" | "
            f"{check.message}"
        )

    print()
    print("ISSUES")
    print("-" * 70)

    if not result.issues:

        print("No validation issues detected.")

    else:

        for issue in result.issues:

            print(
                f"{issue.severity.value:10}"
                f" | "
                f"{issue.code:30}"
                f" | "
                f"{issue.message}"
            )

    print()
    print("=" * 70)

    if result.status == TableValidationStatus.VALID:

        print("PHASE 3.1.6.2 TEST PASSED")

    else:

        print(
            "PHASE 3.1.6.2 TEST FAILED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()