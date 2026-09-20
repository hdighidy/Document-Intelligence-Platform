"""
Phase 3.1.9 — Canonical Structured Table Generation

Test pipeline:

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
    Schema Mapping
      ↓
    Canonical Generation
      ↓
    CanonicalTable
"""

from __future__ import annotations

from datetime import datetime

from pdfplumber import table

from app.extraction.table.canonical.canonical_generator import (
    generate_canonical_table,
)
from app.models.table import (
    CanonicalTable,
    CanonicalTableRow,
    SchemaMappingStatus,
    Table,
    TableColumnMapping,
    TableFieldDefinition,
    TableFieldRole,
    TableSchema,
    TableSemanticType,
    SemanticMappingSource,
)


# ============================================================
# TEST DATA
# ============================================================


def build_test_table() -> Table:
    """
    Build a deterministic Phase 3.1.8-compatible table.

    This intentionally tests the canonical generator
    independently of PDF extraction.
    """

    headers = [
        "Unit Description",
        "Unit Code",
        "Quantity",
        "Order Date",
        "Delivery Date",
        "Delivery Status",
        "Unit Price",
    ]

    rows = [
        headers,
        [
            "Air Handlig unit",
            "AHU-B50",
            "2",
            "26-05-2025",
            "8/9/2026",
            "Done",
            "1,250,000",
        ],
        [
            "Exhaust Fans",
            "EXF-B40",
            "6",
            "15-05-2025",
            "18-10-2025",
            "Done",
            "260,000",
        ],
        [
            "Fire Fighting pump",
            "FFP-B21",
            "3",
            "11/12/2025",
            "6/1/2026",
            "Not",
            "1,365,000",
        ],
    ]

    schema = TableSchema(
        schema_id="SCHEMA-TEST001",
        schema_version="3.1.8",
        schema_name="material_delivery",
        mapping_status=(
            SchemaMappingStatus.COMPLETE
        ),
        mapping_confidence=0.98,
        source_headers=headers,
        canonical_fields=[
            "unit_description",
            "unit_code",
            "quantity",
            "order_date",
            "delivery_date",
            "delivery_status",
            "unit_price",
        ],
        fields=[
            TableFieldDefinition(
                column_index=0,
                source_header="Unit Description",
                field_name="unit_description",
                display_name="Unit Description",
                field_role=(
                    TableFieldRole.DESCRIPTION
                ),
                semantic_type=(
                    TableSemanticType.TEXT
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=1,
                source_header="Unit Code",
                field_name="unit_code",
                display_name="Unit Code",
                field_role=(
                    TableFieldRole.IDENTIFIER
                ),
                semantic_type=(
                    TableSemanticType.IDENTIFIER
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=2,
                source_header="Quantity",
                field_name="quantity",
                display_name="Quantity",
                field_role=(
                    TableFieldRole.QUANTITY
                ),
                semantic_type=(
                    TableSemanticType.INTEGER
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=3,
                source_header="Order Date",
                field_name="order_date",
                display_name="Order Date",
                field_role=(
                    TableFieldRole.DATE
                ),
                semantic_type=(
                    TableSemanticType.DATE
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=4,
                source_header="Delivery Date",
                field_name="delivery_date",
                display_name="Delivery Date",
                field_role=(
                    TableFieldRole.DATE
                ),
                semantic_type=(
                    TableSemanticType.DATE
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=5,
                source_header="Delivery Status",
                field_name="delivery_status",
                display_name="Delivery Status",
                field_role=(
                    TableFieldRole.STATUS
                ),
                semantic_type=(
                    TableSemanticType.STATUS
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
            TableFieldDefinition(
                column_index=6,
                source_header="Unit Price",
                field_name="unit_price",
                display_name="Unit Price",
                field_role=(
                    TableFieldRole.CURRENCY
                ),
                semantic_type=(
                    TableSemanticType.CURRENCY
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                mapping_confidence=0.99,
            ),
        ],
        column_mappings=[
            TableColumnMapping(
                column_index=0,
                source_header="Unit Description",
                normalized_header="unit_description",
                canonical_field="unit_description",
                field_role=(
                    TableFieldRole.DESCRIPTION
                ),
                semantic_type=(
                    TableSemanticType.TEXT
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=1,
                source_header="Unit Code",
                normalized_header="unit_code",
                canonical_field="unit_code",
                field_role=(
                    TableFieldRole.IDENTIFIER
                ),
                semantic_type=(
                    TableSemanticType.IDENTIFIER
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=2,
                source_header="Quantity",
                normalized_header="quantity",
                canonical_field="quantity",
                field_role=(
                    TableFieldRole.QUANTITY
                ),
                semantic_type=(
                    TableSemanticType.INTEGER
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=3,
                source_header="Order Date",
                normalized_header="order_date",
                canonical_field="order_date",
                field_role=(
                    TableFieldRole.DATE
                ),
                semantic_type=(
                    TableSemanticType.DATE
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=4,
                source_header="Delivery Date",
                normalized_header="delivery_date",
                canonical_field="delivery_date",
                field_role=(
                    TableFieldRole.DATE
                ),
                semantic_type=(
                    TableSemanticType.DATE
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=5,
                source_header="Delivery Status",
                normalized_header="delivery_status",
                canonical_field="delivery_status",
                field_role=(
                    TableFieldRole.STATUS
                ),
                semantic_type=(
                    TableSemanticType.STATUS
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
            TableColumnMapping(
                column_index=6,
                source_header="Unit Price",
                normalized_header="unit_price",
                canonical_field="unit_price",
                field_role=(
                    TableFieldRole.CURRENCY
                ),
                semantic_type=(
                    TableSemanticType.CURRENCY
                ),
                mapping_source=(
                    SemanticMappingSource.HEADER_EXACT
                ),
                confidence=0.99,
                is_mapped=True,
            ),
        ],
    )

    return Table(
        table_id="TABLE-A71DEB2D0F7D",
        document_id="DOC-TEST001",
        table_index=0,
        page_number=1,
        rows=rows,
        headers=headers,
        data_rows=rows[1:],
        row_count=4,
        column_count=7,
        header_row_index=0,
        data_start_row_index=1,
        data_end_row_index=3,
        has_header=True,
        has_data_rows=True,
        schema=schema,
        schema_mapping_status=(
            SchemaMappingStatus.COMPLETE
        ),
        schema_mapping_confidence=0.98,
    )


# ============================================================
# CHECK HELPERS
# ============================================================


passed = 0
failed = 0


def check(
    name: str,
    condition: bool,
) -> None:
    global passed
    global failed

    if condition:
        print(
            f"[PASS] {name}"
        )
        passed += 1
    else:
        print(
            f"[FAIL] {name}"
        )
        failed += 1


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.9 — CANONICAL STRUCTURED TABLE GENERATION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Build source table
    # --------------------------------------------------------

    print()
    print(
        "Step 1 — Building schema-mapped table..."
    )

    table = build_test_table()

    print(
        f"Table ID : {table.table_id}"
    )

    print(f"Schema   : {table.schema.schema_name} " )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    print()
    print(
        "Step 2 — Generating canonical table..."
    )

    canonical = generate_canonical_table(
        table
    )

    print(
        f"Canonical ID : "
        f"{canonical.canonical_table_id}"
    )

    print(
        f"Rows         : "
        f"{canonical.row_count}"
    )

    print(
        f"Columns      : "
        f"{canonical.column_count}"
    )

    print(
        f"Status       : "
        f"{canonical.mapping_status}"
    )

    print(
        f"Confidence   : "
        f"{canonical.mapping_confidence:.4f}"
    )

    # --------------------------------------------------------
    # Checks
    # --------------------------------------------------------

    print()
    print(
        "Step 3 — Running Phase 3.1.9 checks..."
    )

    check(
        "CanonicalTable instance created",
        isinstance(
            canonical,
            CanonicalTable,
        ),
    )

    check(
        "Canonical table attached to source table",
        table.canonical_table is canonical,
    )

    check(
        "Source table ID preserved",
        canonical.source_table_id
        == table.table_id,
    )

    check(
        "Document ID preserved",
        canonical.document_id
        == table.document_id,
    )

    check(
        "Schema preserved",
        canonical.schema.schema_id
        == table.schema.schema_id,
    )

    check(
        "Correct canonical row count",
        canonical.row_count == 3,
    )

    check(
        "Correct canonical column count",
        canonical.column_count == 7,
    )

    check(
        "Mapping status is COMPLETE",
        canonical.mapping_status
        == SchemaMappingStatus.COMPLETE,
    )

    check(
        "Canonical rows are correct models",
        all(
            isinstance(
                row,
                CanonicalTableRow,
            )
            for row in canonical.rows
        ),
    )

    # --------------------------------------------------------
    # Field checks
    # --------------------------------------------------------

    first_row = canonical.rows[0]

    expected_fields = {
        "unit_description",
        "unit_code",
        "quantity",
        "order_date",
        "delivery_date",
        "delivery_status",
        "unit_price",
    }

    check(
        "Canonical fields generated",
        set(
            first_row.values.keys()
        )
        == expected_fields,
    )

    check(
        "Unit description preserved",
        first_row.values[
            "unit_description"
        ]
        == "Air Handlig unit",
    )

    check(
        "Unit code preserved",
        first_row.values[
            "unit_code"
        ]
        == "AHU-B50",
    )

    check(
        "Quantity preserved",
        first_row.values[
            "quantity"
        ]
        == "2",
    )

    check(
        "Source values preserved",
        first_row.source_values[
            "Unit Code"
        ]
        == "AHU-B50",
    )

    check(
        "Row confidence valid",
        0.0
        <= first_row.confidence
        <= 1.0,
    )

    # --------------------------------------------------------
    # Deterministic ID check
    # --------------------------------------------------------

    second = generate_canonical_table(
        build_test_table(),
        attach=False,
    )

    check(
        "Canonical ID deterministic",
        second.canonical_table_id
        == canonical.canonical_table_id,
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)

    print(
        f"Checks passed: {passed}"
    )

    print(
        f"Checks failed: {failed}"
    )

    print("=" * 70)

    if failed:
        print()
        print(
            "FAIL"
        )

        raise SystemExit(1)

    print()
    print(
        "PASS"
    )

    print(
        "Phase 3.1.9 — Canonical Structured "
        "Table Generation completed successfully."
    )


if __name__ == "__main__":
    main()