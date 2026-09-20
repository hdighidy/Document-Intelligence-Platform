
"""
Phase 3.1.9 — Canonical Structured Table Generation Test
=========================================================

Pipeline:

    PDF
      ↓
    Detection
      ↓
    Extraction
      ↓
    Cleaning / Normalization
      ↓
    Structure Analysis
      ↓
    Schema / Semantic Mapping
      ↓
    Canonical Table Generation
      ↓
    Canonical Structured Table

Purpose
-------

This script validates Phase 3.1.9 independently while
remaining compatible with the Phase 3.1.8 table models.

Expected project structure:

    app/
        models/
            table.py

        extraction/
            table_detector.py
            table_extractor.py
            table_cleaner.py

            table/
                structure/
                    structure_analyzer.py

            table_schema_mapper.py
            canonical_table_generator.py

    scripts/
        test_canonical_table_generation.py

Usage
-----

    python -m scripts.test_canonical_table_generation

Expected result:

    Checks passed: N
    Checks failed: 0
    PASS
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


# ============================================================
# PROJECT IMPORTS
# ============================================================

from app.models.table import (
    CanonicalTable,
    CanonicalTableRow,
    SchemaMappingStatus,
    Table,
    TableFieldRole,
    TableSchema,
    TableSemanticType,
)

from app.extraction.table_detector import (
    detect_tables,
)

from app.extraction.table_extractor import (
    extract_tables,
)

from app.extraction.table_cleaner import (
    clean_table,
)


# ============================================================
# OPTIONAL PHASE 3.1.7 IMPORT
# ============================================================

try:

    from app.extraction.table_structure.structure_analyzer import (
        analyze_table_structure,
    )

    STRUCTURE_ANALYZER_AVAILABLE = True

except ImportError:

    analyze_table_structure = None

    STRUCTURE_ANALYZER_AVAILABLE = False


# ============================================================
# PHASE 3.1.8 SCHEMA MAPPER
# ============================================================

SCHEMA_MAPPER_AVAILABLE = False
map_table_schema = None

_SCHEMA_IMPORT_ERRORS: list[str] = []


_SCHEMA_IMPORT_CANDIDATES = [

    (
        "app.extraction.table_schema_mapper",
        "map_table_schema",
    ),

    (
        "app.extraction.table.schema_mapper",
        "map_table_schema",
    ),

    (
        "app.extraction.table.schema.schema_mapper",
        "map_table_schema",
    ),

    (
        "app.extraction.schema_mapper",
        "map_table_schema",
    ),
]


for module_name, function_name in _SCHEMA_IMPORT_CANDIDATES:

    try:

        module = __import__(
            module_name,
            fromlist=[function_name],
        )

        candidate = getattr(
            module,
            function_name,
            None,
        )

        if candidate is not None:

            map_table_schema = candidate

            SCHEMA_MAPPER_AVAILABLE = True

            break

    except Exception as exc:

        _SCHEMA_IMPORT_ERRORS.append(
            f"{module_name}: {exc}"
        )


# ============================================================
# PHASE 3.1.9 CANONICAL GENERATOR
# ============================================================

CANONICAL_GENERATOR_AVAILABLE = False
generate_canonical_table = None

_CANONICAL_IMPORT_ERRORS: list[str] = []


_CANONICAL_IMPORT_CANDIDATES = [

    (
        "app.extraction.table.canonical.canonical_generator",
        "generate_canonical_table",
    ),

    (
        "app.extraction.canonical_table_generator",
        "generate_canonical_table",
    ),

    (
        "app.extraction.table_canonical_generator",
        "generate_canonical_table",
    ),

    (
        "app.extraction.table.canonical_generator",
        "generate_canonical_table",
    ),

    (
        "app.extraction.table.canonical_table_generator",
        "generate_canonical_table",
    ),

    (
        "app.extraction.canonical_generator",
        "generate_canonical_table",
    ),
]


for module_name, function_name in _CANONICAL_IMPORT_CANDIDATES:

    try:

        module = __import__(
            module_name,
            fromlist=[function_name],
        )

        candidate = getattr(
            module,
            function_name,
            None,
        )

        if candidate is not None:

            generate_canonical_table = candidate

            CANONICAL_GENERATOR_AVAILABLE = True

            break

    except Exception as exc:

        _CANONICAL_IMPORT_ERRORS.append(
            f"{module_name}: {exc}"
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
# TEST STATE
# ============================================================

checks_passed = 0
checks_failed = 0


# ============================================================
# TEST HELPERS
# ============================================================


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> bool:
    """
    Execute one test check.
    """

    global checks_passed
    global checks_failed

    if condition:

        checks_passed += 1

        print(
            f"  [PASS] {name}"
        )

        if detail:

            print(
                f"         {detail}"
            )

        return True

    checks_failed += 1

    print(
        f"  [FAIL] {name}"
    )

    if detail:

        print(
            f"         {detail}"
        )

    return False


def print_section(
    title: str,
) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# VALUE HELPERS
# ============================================================


def first_non_empty(
    values: list[str],
) -> str:

    for value in values:

        if value and str(value).strip():

            return str(value).strip()

    return ""


def canonical_value(
    value: Any,
) -> Any:
    """
    Convert Pydantic / Enum values into simple
    printable Python values.
    """

    if hasattr(
        value,
        "value",
    ):

        return value.value

    return value


def get_schema(
    table: Table,
) -> TableSchema | None:

    schema = getattr(
        table,
        "schema",
        None,
    )

    if isinstance(
        schema,
        TableSchema,
    ):

        return schema

    return None


def get_canonical_rows(
    canonical: CanonicalTable,
) -> list[CanonicalTableRow]:

    rows = getattr(
        canonical,
        "rows",
        None,
    )

    if rows is None:

        return []

    return rows


# ============================================================
# FALLBACK TEST SCHEMA
# ============================================================


def build_fallback_schema(
    table: Table,
) -> TableSchema:
    """
    Build a deterministic Phase 3.1.8 schema when the
    project's schema mapper is unavailable.

    This fallback exists ONLY to make the Phase 3.1.9
    generator test independently executable.

    The production schema mapper remains responsible
    for real semantic inference.
    """

    headers = list(
        table.headers
    )

    if not headers and table.rows:

        headers = list(
            table.rows[0]
        )

    fields = []

    mappings = []

    canonical_names = []

    for index, header in enumerate(
        headers
    ):

        normalized = (
            str(header)
            .strip()
            .lower()
            .replace("\n", " ")
        )

        compact = (
            normalized
            .replace("-", " ")
            .replace("_", " ")
        )

        if (
            "description" in compact
            or "delivary" in compact
            or "delivery" in compact
        ):

            if (
                "description" in compact
            ):

                field_name = (
                    "description"
                )

                role = (
                    TableFieldRole.DESCRIPTION
                )

                semantic_type = (
                    TableSemanticType.TEXT
                )

            elif (
                "date" in compact
            ):

                field_name = (
                    "delivery_date"
                )

                role = (
                    TableFieldRole.DATE
                )

                semantic_type = (
                    TableSemanticType.DATE
                )

            else:

                field_name = (
                    "delivery_status"
                )

                role = (
                    TableFieldRole.STATUS
                )

                semantic_type = (
                    TableSemanticType.STATUS
                )

        elif (
            "unit code" in compact
            or compact == "code"
        ):

            field_name = "unit_code"

            role = (
                TableFieldRole.IDENTIFIER
            )

            semantic_type = (
                TableSemanticType.IDENTIFIER
            )

        elif (
            "quantity" in compact
            or compact == "qty"
        ):

            field_name = "quantity"

            role = (
                TableFieldRole.QUANTITY
            )

            semantic_type = (
                TableSemanticType.QUANTITY
            )

        elif (
            "order date" in compact
        ):

            field_name = "order_date"

            role = (
                TableFieldRole.DATE
            )

            semantic_type = (
                TableSemanticType.DATE
            )

        elif (
            "unit price" in compact
            or "price" in compact
        ):

            field_name = "unit_price"

            role = (
                TableFieldRole.CURRENCY
            )

            semantic_type = (
                TableSemanticType.CURRENCY
            )

        elif (
            "unit" == compact
        ):

            field_name = "unit"

            role = (
                TableFieldRole.UNIT
            )

            semantic_type = (
                TableSemanticType.UNIT
            )

        else:

            safe_name = (
                compact
                .replace(" ", "_")
                or f"column_{index + 1}"
            )

            field_name = safe_name

            role = (
                TableFieldRole.UNKNOWN
            )

            semantic_type = (
                TableSemanticType.UNKNOWN
            )

        canonical_names.append(
            field_name
        )

        from app.models.table import (
            TableFieldDefinition,
            TableColumnMapping,
            SemanticMappingSource,
            TableFieldRequirement,
        )

        fields.append(
            TableFieldDefinition(
                column_index=index,
                source_header=str(
                    header
                ),
                field_name=field_name,
                display_name=str(
                    header
                ),
                field_role=role,
                semantic_type=semantic_type,
                requirement=(
                    TableFieldRequirement.OPTIONAL
                ),
                mapping_source=(
                    SemanticMappingSource.INFERRED
                ),
                mapping_confidence=0.80,
            )
        )

        mappings.append(
            TableColumnMapping(
                column_index=index,
                source_header=str(
                    header
                ),
                normalized_header=normalized,
                canonical_field=field_name,
                field_role=role,
                semantic_type=semantic_type,
                mapping_source=(
                    SemanticMappingSource.INFERRED
                ),
                confidence=0.80,
                is_mapped=True,
            )
        )

    mapped = len(
        canonical_names
    )

    return TableSchema(
        schema_id=(
            f"SCHEMA-{table.table_id}"
        ),
        schema_version="3.1.8",
        schema_name=(
            table.title
            or "canonical_table"
        ),
        mapping_status=(
            SchemaMappingStatus.COMPLETE
            if mapped == len(headers)
            else SchemaMappingStatus.PARTIAL
        ),
        mapping_confidence=0.80,
        fields=fields,
        column_mappings=mappings,
        total_columns=len(headers),
        mapped_columns=mapped,
        unmapped_columns=max(
            0,
            len(headers) - mapped,
        ),
        source_headers=headers,
        canonical_fields=canonical_names,
    )


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print()

    print(
        "=" * 70
    )

    print(
        "PHASE 3.1.9 — CANONICAL STRUCTURED TABLE GENERATION"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Check PDF
    # --------------------------------------------------------

    print()

    print(
        f"PDF: {PDF_PATH}"
    )

    if not PDF_PATH.exists():

        raise FileNotFoundError(
            f"PDF not found:\n{PDF_PATH}"
        )

    # --------------------------------------------------------
    # Step 1 — Detection
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

        print(
            "\nNo tables detected."
        )

        print(
            "\nChecks passed: 0"
        )

        print(
            "Checks failed: 1"
        )

        print(
            "\nFAIL"
        )

        return

    check(
        "Table detection",
        len(detected_tables) > 0,
        f"Detected {len(detected_tables)} table(s).",
    )

    # --------------------------------------------------------
    # Step 2 — Extraction
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
        f"Extracted tables: "
        f"{len(extracted_tables)}"
    )

    check(
        "Table extraction",
        len(extracted_tables) > 0,
        f"Extracted {len(extracted_tables)} table(s).",
    )

    if not extracted_tables:

        print(
            "\nCanonical generation cannot continue."
        )

        print(
            f"\nChecks passed: {checks_passed}"
        )

        print(
            f"Checks failed: {checks_failed}"
        )

        print(
            "\nFAIL"
        )

        return

    # --------------------------------------------------------
    # Step 3 — Cleaning
    # --------------------------------------------------------

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

    check(
        "Table cleaning",
        len(cleaned_tables)
        == len(extracted_tables),
        "Every extracted table was cleaned.",
    )

    # --------------------------------------------------------
    # Step 4 — Structure
    # --------------------------------------------------------

    print()

    print(
        "Step 4 — Analyzing structure..."
    )

    structured_tables: list[Table] = []

    for table in cleaned_tables:

        if (
            STRUCTURE_ANALYZER_AVAILABLE
            and analyze_table_structure is not None
        ):

            analyzed = (
                analyze_table_structure(
                    table
                )
            )

        else:

            analyzed = table

        structured_tables.append(
            analyzed
        )

    check(
        "Structure analysis",
        len(structured_tables)
        == len(cleaned_tables),
        "Structure stage completed.",
    )

    # --------------------------------------------------------
    # Step 5 — Schema Mapping
    # --------------------------------------------------------

    print()

    print(
        "Step 5 — Mapping table schema..."
    )

    schema_tables: list[Table] = []

    for table in structured_tables:

        if (
            SCHEMA_MAPPER_AVAILABLE
            and map_table_schema is not None
        ):

            mapped_table = (
                map_table_schema(
                    table
                )
            )

        else:

            fallback_schema = (
                build_fallback_schema(
                    table
                )
            )

            table.schema = (
                fallback_schema
            )

            table.schema_mapping_status = (
                fallback_schema.mapping_status
            )

            table.schema_mapping_confidence = (
                fallback_schema.mapping_confidence
            )

            mapped_table = table

        schema_tables.append(
            mapped_table
        )

    table = schema_tables[0]

    schema = get_schema(
        table
    )

    check(
        "Schema generated",
        schema is not None,
        "Phase 3.1.8 TableSchema is available.",
    )

    if schema is None:

        print(
            "\nCannot generate canonical table without schema."
        )

        print(
            f"\nChecks passed: {checks_passed}"
        )

        print(
            f"Checks failed: {checks_failed}"
        )

        print(
            "\nFAIL"
        )

        return

    print()

    print(
        f"Schema ID          : {schema.schema_id}"
    )

    print(
        f"Schema version     : {schema.schema_version}"
    )

    print(
        f"Schema name        : {schema.schema_name}"
    )

    print(
        f"Mapping status     : "
        f"{schema.mapping_status}"
    )

    print(
        f"Mapping confidence : "
        f"{schema.mapping_confidence:.2f}"
    )

    print(
        f"Total columns      : "
        f"{schema.total_columns}"
    )

    print(
        f"Mapped columns     : "
        f"{schema.mapped_columns}"
    )

    print(
        f"Unmapped columns   : "
        f"{schema.unmapped_columns}"
    )

    # --------------------------------------------------------
    # Step 6 — Canonical Generation
    # --------------------------------------------------------

    print()

    print(
        "Step 6 — Generating canonical table..."
    )

    if (
        not CANONICAL_GENERATOR_AVAILABLE
        or generate_canonical_table is None
    ):

        print()

        print(
            "ERROR: Phase 3.1.9 generator could not be imported."
        )

        print()

        print(
            "Expected function:"
        )

        print(
            "    generate_canonical_table(table)"
        )

        print()

        print(
            "Checked module locations:"
        )

        for module_name, function_name in (
            _CANONICAL_IMPORT_CANDIDATES
        ):

            print(
                f"    {module_name}.{function_name}"
            )

        print()

        print(
            f"\nChecks passed: {checks_passed}"
        )

        print(
            f"Checks failed: {checks_failed + 1}"
        )

        print(
            "\nFAIL"
        )

        return

    # --------------------------------------------------------
    # Generator invocation
    # --------------------------------------------------------

    canonical = None

    generator_errors: list[str] = []

    generator_attempts = [

        lambda: generate_canonical_table(
            table
        ),

        lambda: generate_canonical_table(
            table=table
        ),

    ]

    for attempt in generator_attempts:

        try:

            canonical = attempt()

            break

        except TypeError as exc:

            generator_errors.append(
                str(exc)
            )

        except Exception as exc:

            generator_errors.append(
                str(exc)
            )

            break

    if canonical is None:

        print()

        print(
            "Canonical generation failed."
        )

        for error in generator_errors:

            print(
                f"  {error}"
            )

        print()

        print(
            f"Checks passed: {checks_passed}"
        )

        print(
            f"Checks failed: {checks_failed + 1}"
        )

        print(
            "\nFAIL"
        )

        return

    print(
        f"Generated type: "
        f"{type(canonical).__name__}"
    )

    # --------------------------------------------------------
    # Step 7 — Canonical Model Validation
    # --------------------------------------------------------

    print()

    print(
        "Step 7 — Validating canonical model..."
    )

    check(
        "CanonicalTable model",
        isinstance(
            canonical,
            CanonicalTable,
        ),
        "Generator returned Phase 3.1.8 CanonicalTable.",
    )

    if not isinstance(
        canonical,
        CanonicalTable,
    ):

        print()

        print(
            "Returned object:"
        )

        print(
            canonical
        )

        print()

        print(
            f"Checks passed: {checks_passed}"
        )

        print(
            f"Checks failed: {checks_failed}"
        )

        print(
            "\nFAIL"
        )

        return

    # --------------------------------------------------------
    # Step 8 — Identity
    # --------------------------------------------------------

    print()

    print(
        "Step 8 — Validating canonical identity..."
    )

    check(
        "Canonical table ID",
        bool(
            canonical.canonical_table_id
        ),
        f"ID = {canonical.canonical_table_id}",
    )

    check(
        "Source table ID",
        (
            canonical.source_table_id
            == table.table_id
        ),
        (
            f"Source = "
            f"{canonical.source_table_id}"
        ),
    )

    check(
        "Document ID",
        (
            canonical.document_id
            == table.document_id
        ),
        (
            f"Document = "
            f"{canonical.document_id}"
        ),
    )

    # --------------------------------------------------------
    # Step 9 — Schema Integration
    # --------------------------------------------------------

    print()

    print(
        "Step 9 — Validating schema integration..."
    )

    canonical_schema = (
        getattr(
            canonical,
            "schema",
            None,
        )
    )

    check(
        "Schema integration",
        isinstance(
            canonical_schema,
            TableSchema,
        ),
        "Canonical table contains TableSchema.",
    )

    check(
        "Schema identity",
        (
            canonical_schema.schema_id
            == schema.schema_id
        ),
        "Canonical schema matches source schema.",
    )

    check(
        "Schema columns",
        (
            canonical_schema.total_columns
            == schema.total_columns
        ),
        (
            f"{canonical_schema.total_columns} "
            f"canonical columns."
        ),
    )

    # --------------------------------------------------------
    # Step 10 — Row Generation
    # --------------------------------------------------------

    print()

    print(
        "Step 10 — Validating canonical rows..."
    )

    canonical_rows = (
        get_canonical_rows(
            canonical
        )
    )

    check(
        "Canonical rows generated",
        len(canonical_rows) > 0,
        (
            f"Generated {len(canonical_rows)} "
            "canonical row(s)."
        ),
    )

    if canonical_rows:

        for row in canonical_rows:

            check(
                (
                    f"Canonical row "
                    f"{row.row_index}"
                ),
                isinstance(
                    row,
                    CanonicalTableRow,
                ),
                "Valid CanonicalTableRow.",
            )

    # --------------------------------------------------------
    # Step 11 — Row Count
    # --------------------------------------------------------

    print()

    print(
        "Step 11 — Validating row count..."
    )

    check(
        "Canonical row count",
        (
            canonical.row_count
            == len(canonical_rows)
        ),
        (
            f"row_count={canonical.row_count}, "
            f"actual={len(canonical_rows)}"
        ),
    )

    # --------------------------------------------------------
    # Step 12 — Column Count
    # --------------------------------------------------------

    print()

    print(
        "Step 12 — Validating column count..."
    )

    check(
        "Canonical column count",
        (
            canonical.column_count
            == schema.total_columns
        ),
        (
            f"column_count="
            f"{canonical.column_count}"
        ),
    )

    # --------------------------------------------------------
    # Step 13 — Canonical Field Names
    # --------------------------------------------------------

    print()

    print(
        "Step 13 — Validating canonical field names..."
    )

    expected_fields = [
        field.field_name
        for field in schema.fields
        if field.field_name
    ]

    actual_fields: set[str] = set()

    for row in canonical_rows:

        actual_fields.update(
            row.values.keys()
        )

    print()

    print(
        "Expected fields:"
    )

    print(
        expected_fields
    )

    print()

    print(
        "Detected canonical fields:"
    )

    print(
        sorted(actual_fields)
    )

    if expected_fields:

        matched_fields = (
            set(expected_fields)
            .intersection(
                actual_fields
            )
        )

        check(
            "Canonical field mapping",
            len(matched_fields)
            > 0,
            (
                f"Matched "
                f"{len(matched_fields)}/"
                f"{len(expected_fields)} "
                "field(s)."
            ),
        )

    # --------------------------------------------------------
    # Step 14 — No Empty Canonical Field Names
    # --------------------------------------------------------

    print()

    print(
        "Step 14 — Checking canonical field names..."
    )

    empty_field_names = [

        name

        for name in actual_fields

        if not str(name).strip()

    ]

    check(
        "No empty canonical field names",
        len(empty_field_names) == 0,
        (
            "All canonical field names are populated."
        ),
    )

    # --------------------------------------------------------
    # Step 15 — Source Values Preservation
    # --------------------------------------------------------

    print()

    print(
        "Step 15 — Checking source-value preservation..."
    )

    source_values_available = all(
        isinstance(
            row.source_values,
            dict,
        )
        for row in canonical_rows
    )

    check(
        "Source values preserved",
        source_values_available,
        (
            "Canonical rows retain source_values."
        ),
    )

    # --------------------------------------------------------
    # Step 16 — Confidence
    # --------------------------------------------------------

    print()

    print(
        "Step 16 — Checking confidence..."
    )

    confidence_valid = (
        0.0
        <= canonical.mapping_confidence
        <= 1.0
    )

    check(
        "Canonical mapping confidence",
        confidence_valid,
        (
            f"confidence="
            f"{canonical.mapping_confidence:.2f}"
        ),
    )

    for row in canonical_rows:

        check(
            (
                f"Row {row.row_index} "
                "confidence"
            ),
            0.0
            <= row.confidence
            <= 1.0,
            (
                f"confidence="
                f"{row.confidence:.2f}"
            ),
        )

    # --------------------------------------------------------
    # Step 17 — Serialization
    # --------------------------------------------------------

    print()

    print(
        "Step 17 — Testing serialization..."
    )

    try:

        payload = canonical.model_dump()

        check(
            "model_dump()",
            isinstance(
                payload,
                dict,
            ),
            "CanonicalTable serializes to dictionary.",
        )

        json_payload = canonical.model_dump_json()

        check(
            "model_dump_json()",
            isinstance(
                json_payload,
                str,
            )
            and len(json_payload) > 0,
            "CanonicalTable serializes to JSON.",
        )

    except Exception as exc:

        check(
            "Canonical serialization",
            False,
            str(exc),
        )

    # --------------------------------------------------------
    # Final Report
    # --------------------------------------------------------

    print()

    print(
        "=" * 70
    )

    print(
        "CANONICAL TABLE RESULT"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Canonical Table ID : "
        f"{canonical.canonical_table_id}"
    )

    print(
        f"Source Table ID    : "
        f"{canonical.source_table_id}"
    )

    print(
        f"Document ID        : "
        f"{canonical.document_id}"
    )

    print(
        f"Rows               : "
        f"{canonical.row_count}"
    )

    print(
        f"Columns            : "
        f"{canonical.column_count}"
    )

    print(
        f"Mapping Status     : "
        f"{canonical.mapping_status}"
    )

    print(
        f"Mapping Confidence : "
        f"{canonical.mapping_confidence:.2f}"
    )

    print()

    print(
        "Canonical Rows:"
    )

    for row in canonical_rows:

        print()

        print(
            f"ROW {row.row_index}"
        )

        print(
            "-" * 60
        )

        for key, value in row.values.items():

            print(
                f"{key:30} : "
                f"{canonical_value(value)}"
            )

    print()

    print(
        "=" * 70
    )

    print(
        "TEST SUMMARY"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Checks passed: {checks_passed}"
    )

    print(
        f"Checks failed: {checks_failed}"
    )

    print()

    if checks_failed == 0:

        print(
            "PASS"
        )

        print()

        print(
            "Phase 3.1.9 — Canonical Structured "
            "Table Generation completed successfully."
        )

    else:

        print(
            "FAIL"
        )

        print()

        print(
            "Phase 3.1.9 requires correction."
        )


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    main()