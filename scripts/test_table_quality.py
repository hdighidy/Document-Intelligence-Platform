"""
Phase 3.1.5
Table Quality Scoring Test
"""

from app.models.table import (
    Table,
    TableCell,
    TableQualityScore,
)

from app.extraction.table_quality_scorer import (
    score_table_quality,
)


def main():

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.5 — TABLE QUALITY & CONFIDENCE SCORING"
    )
    print("=" * 70)

    # ========================================================
    # Create test cells
    # ========================================================

    cells = []

    values = [
        "Unit Description",
        "Unit Code",
        "Quantity",
        "Air Handling Unit",
        "AHU-B50",
        "2",
        "Exhaust Fans",
        "EXF-B40",
        "6",
    ]

    for index, value in enumerate(values):

        cell = TableCell(
            row_index=index // 3,
            column_index=index % 3,
            raw_text=value,
            text=value,
        )

        # Simulate semantic normalization
        cell.normalized_value = value

        cells.append(
            cell
        )

    # ========================================================
    # Create test table
    # ========================================================

    table = Table(
        table_id="TEST-QUALITY-001",
        page_number=1,
        rows=[
            [
                "Unit Description",
                "Unit Code",
                "Quantity",
            ],
            [
                "Air Handling Unit",
                "AHU-B50",
                "2",
            ],
            [
                "Exhaust Fans",
                "EXF-B40",
                "6",
            ],
        ],
        cells=cells,
        headers=[
            "Unit Description",
            "Unit Code",
            "Quantity",
        ],
        column_count=3,
    )

    # ========================================================
    # Score
    # ========================================================

    table = score_table_quality(
        table
    )

    quality = (
        table.quality_score
    )

    # ========================================================
    # Display
    # ========================================================

    print()
    print(
        "QUALITY RESULTS"
    )
    print("-" * 70)

    print(
        f"Structure Score       : "
        f"{quality.structure_score:.2f}"
        if quality.structure_score is not None
        else "Structure Score       : None"
    )

    print(
        f"Header Score          : "
        f"{quality.header_score:.2f}"
    )

    print(
        f"Cell Quality Score    : "
        f"{quality.cell_quality_score:.2f}"
        if quality.cell_quality_score is not None
        else "Cell Quality Score    : None"
    )

    print(
        f"Normalization Score   : "
        f"{quality.normalization_score:.2f}"
        if quality.normalization_score is not None
        else "Normalization Score   : None" 
    )

    print(
        f"Consistency Score     : "
        f"{quality.consistency_score:.2f}"
        if quality.consistency_score is not None
        else "Consistency Score     : None"
    )

    print(
        f"Overall Score         : "
        f"{quality.overall_score:.2f}"
        if quality.overall_score is not None
        else "Overall Score         : None" 
    )

    print(
        f"Confidence Level      : "
        f"{quality.confidence_level}"
        if quality.confidence_level is not None 
        else "Confidence Level      : None"
    )

    print(
        f"Total Cells           : "
        f"{quality.total_cells}"
        if quality.total_cells is not None
        else "Total Cells           : None"
    )

    print(
        f"Populated Cells       : "
        f"{quality.populated_cells}"
        if quality.populated_cells is not None
        else "Populated Cells       : None"
    )

    print(
        f"Empty Cells           : "
        f"{quality.empty_cells}"
        if quality.empty_cells is not None
        else "Empty Cells           : None"
    )

    print(
        f"Normalized Cells      : "
        f"{quality.normalized_cells}"
        if quality.normalized_cells is not None
        else "Normalized Cells      : None"
    )

    print()
    print(
        "Issues:"
    )

    if quality.issues:

        for issue in quality.issues:

            print(
                f"  - {issue}"
            )

    else:

        print(
            "  None"
        )

    print()
    print("=" * 70)

    if (
        quality.overall_score >= 90.0
        and quality.confidence_level
        == "HIGH"
    ):

        print(
            "QUALITY TEST PASSED"
        )

    else:

        raise AssertionError(
            "Quality scoring test failed."
        )


if __name__ == "__main__":

    main()