"""
Phase 3.1.4.3
Table Value Normalization Test
"""

from app.extraction.table_value_normalizer import (
    normalize_cell_value,
)

from app.models.table import (
    TableCell,
)


def test_case(
    value: str,
    expected_type: str,
    expected_semantic: str,
    expected_value,
) -> bool:

    cell = TableCell(
        row_index=0,
        column_index=0,
        raw_text=value,
        text=value,
    )

    normalize_cell_value(
        cell
    )

    passed = (
        cell.data_type
        == expected_type
        and
        cell.semantic_type
        == expected_semantic
        and
        cell.normalized_value
        == expected_value
    )

    print()
    print(
        f"Input       : {value!r}"
    )

    print(
        f"Data type   : "
        f"{cell.data_type}"
    )

    print(
        f"Semantic    : "
        f"{cell.semantic_type}"
    )

    print(
        f"Normalized  : "
        f"{cell.normalized_value!r}"
    )

    print(
        f"Expected    : "
        f"{expected_value!r}"
    )

    print(
        f"Status      : "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return passed


def main():

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.4.3 — "
        "DATA TYPE & SEMANTIC NORMALIZATION"
    )
    print("=" * 70)

    tests = [

        (
            "2",
            "integer",
            "number",
            2,
        ),

        (
            "1,250,000",
            "integer",
            "number",
            1250000,
        ),

        (
            "260,000",
            "integer",
            "number",
            260000,
        ),

        (
            "95%",
            "percentage",
            "percentage",
            95.0,
        ),

        (
            "26-05-2025",
            "date",
            "date",
            "2025-05-26",
        ),

        (
            "2026-08-09",
            "date",
            "date",
            "2026-08-09",
        ),

        (
            "$1,250",
            "number",
            "currency:USD",
            1250.0,
        ),

        (
            "Done",
            "string",
            "status",
            "DONE",
        ),

        (
            "Pending",
            "string",
            "status",
            "PENDING",
        ),

        (
            "AHU-B50",
            "string",
            "identifier",
            "AHU-B50",
        ),

        (
            "Air Handlig unit",
            "string",
            "text",
            "Air Handlig unit",
        ),
    ]

    passed = 0

    for test in tests:

        if test_case(*test):

            passed += 1

    print()
    print("=" * 70)

    print(
        f"Passed: "
        f"{passed}/{len(tests)}"
    )

    print("=" * 70)

    if passed != len(tests):

        raise SystemExit(
            "NORMALIZATION TEST FAILED"
        )

    print(
        "ALL NORMALIZATION TESTS PASSED"
    )


if __name__ == "__main__":

    main()