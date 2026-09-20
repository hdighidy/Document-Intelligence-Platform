"""
Unit test for multi-line cell reconstruction.
"""

from app.extraction.multiline_cell_reconstructor import (
    reconstruct_cell_text,
)


def main():

    test_cases = [
        (
            "Air Handling\nUnit",
            "Air Handling Unit",
        ),
        (
            "Fire Fighting\nPump",
            "Fire Fighting Pump",
        ),
        (
            "Exhaust Fans",
            "Exhaust Fans",
        ),
        (
            "  Air   Handling\n  Unit  ",
            "Air Handling Unit",
        ),
    ]

    print()
    print("=" * 70)
    print(
        "MULTI-LINE RECONSTRUCTION UNIT TEST"
    )
    print("=" * 70)

    passed = 0

    for original, expected in test_cases:

        result = reconstruct_cell_text(
            original
        )

        success = (
            result == expected
        )

        if success:
            passed += 1

        print()
        print(
            f"Input    : {original!r}"
        )

        print(
            f"Expected : {expected!r}"
        )

        print(
            f"Result   : {result!r}"
        )

        print(
            f"Status   : "
            f"{'PASS' if success else 'FAIL'}"
        )

    print()
    print("-" * 70)

    print(
        f"Passed: "
        f"{passed}/{len(test_cases)}"
    )

    print("=" * 70)

    if passed != len(test_cases):

        raise SystemExit(
            "MULTI-LINE TEST FAILED"
        )

    print(
        "ALL TESTS PASSED"
    )


if __name__ == "__main__":

    main()