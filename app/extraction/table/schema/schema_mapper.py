"""
Table Schema & Semantic Mapper
==============================

Phase 3.1.8
Phase 3.1.11 — End-to-End Integration

Responsibilities
----------------
1. Inspect table headers.
2. Normalize headers.
3. Map headers to canonical fields.
4. Determine field roles.
5. Determine semantic types.
6. Build TableColumnMapping objects.
7. Build TableFieldDefinition objects.
8. Attach TableSchema to Table.
9. Populate cell-level schema mapping metadata.

This module is deterministic by design.

Future AI/LLM semantic mapping can be added later
without changing the Table or CanonicalTable contracts.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from app.models.table import (
    SemanticMappingSource,
    SchemaMappingStatus,
    Table,
    TableCell,
    TableColumnMapping,
    TableFieldDefinition,
    TableFieldRequirement,
    TableFieldRole,
    TableSchema,
    TableSemanticType,
)


SCHEMA_MAPPER_VERSION = "3.1.8"


# ============================================================
# HEADER NORMALIZATION
# ============================================================

def normalize_header(value: str | None) -> str:
    """
    Normalize a source header for deterministic matching.
    """

    if not value:
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    value = value.strip().lower()

    value = re.sub(
        r"[\n\r\t]+",
        " ",
        value,
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    value = re.sub(
        r"_+",
        "_",
        value,
    )

    return value.strip("_")


# ============================================================
# CANONICAL HEADER DEFINITIONS
# ============================================================

HEADER_DEFINITIONS = {

    "id": {
        "aliases": {
            "id",
            "item_id",
            "record_id",
            "identifier",
        },
        "role": TableFieldRole.IDENTIFIER,
        "semantic_type": TableSemanticType.IDENTIFIER,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "code": {
        "aliases": {
            "code",
            "item_code",
            "material_code",
            "material_id",
            "part_number",
            "part_no",
            "item_no",
            "reference_code",
        },
        "role": TableFieldRole.IDENTIFIER,
        "semantic_type": TableSemanticType.IDENTIFIER,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "description": {
        "aliases": {
            "description",
            "item_description",
            "material_description",
            "material",
            "item",
            "name",
            "item_name",
        },
        "role": TableFieldRole.DESCRIPTION,
        "semantic_type": TableSemanticType.TEXT,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "quantity": {
        "aliases": {
            "quantity",
            "qty",
            "qnty",
            "amount",
        },
        "role": TableFieldRole.QUANTITY,
        "semantic_type": TableSemanticType.QUANTITY,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "unit": {
        "aliases": {
            "unit",
            "uom",
            "unit_of_measure",
            "measurement_unit",
        },
        "role": TableFieldRole.UNIT,
        "semantic_type": TableSemanticType.UNIT,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "date": {
        "aliases": {
            "date",
            "order_date",
            "delivery_date",
            "inspection_date",
            "approval_date",
            "submission_date",
            "received_date",
        },
        "role": TableFieldRole.DATE,
        "semantic_type": TableSemanticType.DATE,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "status": {
        "aliases": {
            "status",
            "state",
            "condition",
            "approval_status",
            "delivery_status",
            "inspection_status",
        },
        "role": TableFieldRole.STATUS,
        "semantic_type": TableSemanticType.STATUS,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "amount": {
        "aliases": {
            "amount",
            "value",
            "total",
            "total_amount",
            "price",
            "unit_price",
            "cost",
        },
        "role": TableFieldRole.CURRENCY,
        "semantic_type": TableSemanticType.CURRENCY,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "percentage": {
        "aliases": {
            "percentage",
            "percent",
            "completion",
            "completion_percentage",
            "progress",
            "progress_percentage",
        },
        "role": TableFieldRole.PERCENTAGE,
        "semantic_type": TableSemanticType.PERCENTAGE,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "category": {
        "aliases": {
            "category",
            "type",
            "class",
            "classification",
        },
        "role": TableFieldRole.CATEGORY,
        "semantic_type": TableSemanticType.TEXT,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "location": {
        "aliases": {
            "location",
            "site",
            "area",
            "zone",
            "room",
        },
        "role": TableFieldRole.LOCATION,
        "semantic_type": TableSemanticType.TEXT,
        "requirement": TableFieldRequirement.OPTIONAL,
    },

    "reference": {
        "aliases": {
            "reference",
            "ref",
            "reference_no",
            "reference_number",
            "document_no",
            "document_number",
        },
        "role": TableFieldRole.REFERENCE,
        "semantic_type": TableSemanticType.REFERENCE,
        "requirement": TableFieldRequirement.OPTIONAL,
    },
}


# ============================================================
# HEADER MATCHING
# ============================================================

def match_header(
    header: str,
) -> tuple[
    str | None,
    SemanticMappingSource,
    float,
    str | None,
]:

    normalized = normalize_header(header)

    if not normalized:
        return (
            None,
            SemanticMappingSource.UNKNOWN,
            0.0,
            None,
        )

    # --------------------------------------------------------
    # Exact canonical field
    # --------------------------------------------------------

    if normalized in HEADER_DEFINITIONS:

        return (
            normalized,
            SemanticMappingSource.HEADER_EXACT,
            1.0,
            normalized,
        )

    # --------------------------------------------------------
    # Alias matching
    # --------------------------------------------------------

    for canonical_field, definition in HEADER_DEFINITIONS.items():

        if normalized in definition["aliases"]:

            return (
                canonical_field,
                SemanticMappingSource.HEADER_ALIAS,
                0.95,
                normalized,
            )

    # --------------------------------------------------------
    # Pattern matching
    # --------------------------------------------------------

    pattern_rules = [
        (
            r".*(date|datum)$",
            "date",
        ),
        (
            r".*(qty|quantity|amount)$",
            "quantity",
        ),
        (
            r".*(status|state)$",
            "status",
        ),
        (
            r".*(percent|percentage|progress)$",
            "percentage",
        ),
        (
            r".*(code|number|no)$",
            "code",
        ),
        (
            r".*(description|desc|name)$",
            "description",
        ),
    ]

    for pattern, canonical_field in pattern_rules:

        if re.match(pattern, normalized):

            definition = HEADER_DEFINITIONS[
                canonical_field
            ]

            return (
                canonical_field,
                SemanticMappingSource.HEADER_PATTERN,
                0.80,
                None,
            )

    return (
        None,
        SemanticMappingSource.UNKNOWN,
        0.0,
        None,
    )


# ============================================================
# TABLE ROW ACCESS
# ============================================================

def get_table_rows(
    table: Table,
) -> list[list[str]]:

    if table.rows:
        return [
            list(row)
            for row in table.rows
        ]

    rows: list[list[str]] = []

    if not table.cells:
        return rows

    max_row = max(
        (
            cell.row_index
            for cell in table.cells
        ),
        default=-1,
    )

    max_column = max(
        (
            cell.column_index
            for cell in table.cells
        ),
        default=-1,
    )

    if max_row < 0:
        return rows

    rows = [
        ["" for _ in range(max_column + 1)]
        for _ in range(max_row + 1)
    ]

    for cell in table.cells:

        value = (
            cell.normalized_text
            if cell.normalized_text is not None
            else cell.text
        )

        rows[
            cell.row_index
        ][
            cell.column_index
        ] = value or ""

    return rows


# ============================================================
# SAMPLE VALUES
# ============================================================

def sample_column_values(
    table: Table,
    column_index: int,
    limit: int = 5,
) -> list[str]:

    rows = get_table_rows(table)

    values: list[str] = []

    start_index = (
        table.data_start_row_index
        if table.data_start_row_index is not None
        else 1
    )

    for row in rows[start_index:]:

        if column_index >= len(row):
            continue

        value = str(
            row[column_index]
        ).strip()

        if value:
            values.append(value)

        if len(values) >= limit:
            break

    return values


# ============================================================
# BUILD FIELD DEFINITION
# ============================================================

def build_field_definition(
    table: Table,
    column_index: int,
    header: str,
    canonical_field: str,
    source: SemanticMappingSource,
    confidence: float,
    alias: str | None,
) -> TableFieldDefinition:

    definition = HEADER_DEFINITIONS[
        canonical_field
    ]

    samples = sample_column_values(
        table,
        column_index,
    )

    non_empty = len(
        [
            value
            for value in samples
            if value
        ]
    )

    return TableFieldDefinition(
        column_index=column_index,
        source_header=header,
        field_name=canonical_field,
        display_name=header.strip(),
        field_role=definition["role"],
        semantic_type=definition["semantic_type"],
        requirement=definition["requirement"],
        mapping_source=source,
        mapping_confidence=confidence,
        matched_alias=alias,
        non_empty_count=non_empty,
        empty_count=max(
            0,
            len(samples) - non_empty,
        ),
        sample_values=samples,
        description=(
            f"Mapped from source column "
            f"'{header}'."
        ),
    )


# ============================================================
# MAP TABLE
# ============================================================

def map_table_schema(
    table: Table,
) -> Table:

    headers = list(
        table.headers
    )

    if not headers and table.rows:

        header_index = (
            table.header_row_index
            if table.header_row_index is not None
            else 0
        )

        if header_index < len(table.rows):

            headers = [
                str(value)
                for value in table.rows[
                    header_index
                ]
            ]

    schema = TableSchema(
        schema_id=(
            f"SCHEMA-{table.table_id}"
        ),
        schema_version=SCHEMA_MAPPER_VERSION,
        schema_name="generic_table_schema",
        source_headers=headers,
        created_at=datetime.now(
            timezone.utc
        ),
        mapper_version=SCHEMA_MAPPER_VERSION,
    )

    mappings: list[
        TableColumnMapping
    ] = []

    fields: list[
        TableFieldDefinition
    ] = []

    mapped_count = 0

    for column_index, header in enumerate(
        headers
    ):

        (
            canonical_field,
            source,
            confidence,
            alias,
        ) = match_header(header)

        if canonical_field is not None:

            definition = (
                HEADER_DEFINITIONS[
                    canonical_field
                ]
            )

            mapping = TableColumnMapping(
                column_index=column_index,
                source_header=header,
                normalized_header=normalize_header(
                    header
                ),
                canonical_field=canonical_field,
                field_role=definition["role"],
                semantic_type=definition[
                    "semantic_type"
                ],
                mapping_source=source,
                confidence=confidence,
                matched_alias=alias,
                is_mapped=True,
            )

            field = build_field_definition(
                table=table,
                column_index=column_index,
                header=header,
                canonical_field=canonical_field,
                source=source,
                confidence=confidence,
                alias=alias,
            )

            fields.append(field)
            mapped_count += 1

        else:

            mapping = TableColumnMapping(
                column_index=column_index,
                source_header=header,
                normalized_header=normalize_header(
                    header
                ),
                canonical_field="",
                mapping_source=SemanticMappingSource.UNKNOWN,
                confidence=0.0,
                is_mapped=False,
            )

        mappings.append(mapping)

    total_columns = len(headers)
    unmapped_count = (
        total_columns - mapped_count
    )

    if total_columns == 0:

        mapping_status = (
            SchemaMappingStatus.FAILED
        )

        mapping_confidence = 0.0

    elif mapped_count == total_columns:

        mapping_status = (
            SchemaMappingStatus.COMPLETE
        )

        mapping_confidence = (
            sum(
                mapping.confidence
                for mapping in mappings
            )
            / total_columns
        )

    else:

        mapping_status = (
            SchemaMappingStatus.PARTIAL
        )

        mapping_confidence = (
            mapped_count / total_columns
        )

    schema.mapping_status = mapping_status
    schema.mapping_confidence = (
        mapping_confidence
    )

    schema.fields = fields
    schema.column_mappings = mappings

    schema.total_columns = total_columns
    schema.mapped_columns = mapped_count
    schema.unmapped_columns = (
        unmapped_count
    )

    schema.required_fields = len(
        [
            field
            for field in fields
            if field.requirement
            == TableFieldRequirement.REQUIRED
        ]
    )

    schema.optional_fields = len(
        [
            field
            for field in fields
            if field.requirement
            == TableFieldRequirement.OPTIONAL
        ]
    )

    schema.canonical_fields = [
        field.field_name
        for field in fields
    ]

    if unmapped_count:

        schema.notes.append(
            f"{unmapped_count} source "
            f"column(s) could not be "
            f"mapped deterministically."
        )

    # --------------------------------------------------------
    # Attach schema to table
    # --------------------------------------------------------

    table.schema = schema

    table.schema_mapping_status = (
        mapping_status
    )

    table.schema_mapping_confidence = (
        mapping_confidence
    )

    # --------------------------------------------------------
    # Attach mapping information to cells
    # --------------------------------------------------------

    mapping_by_column = {
        mapping.column_index: mapping
        for mapping in mappings
    }

    for cell in table.cells:

        mapping = mapping_by_column.get(
            cell.column_index
        )

        if mapping is None:
            continue

        if not mapping.is_mapped:
            continue

        cell.canonical_field = (
            mapping.canonical_field
        )

        cell.field_role = (
            mapping.field_role
        )

        cell.field_semantic_type = (
            mapping.semantic_type
        )

        cell.schema_mapping_confidence = (
            mapping.confidence
        )

    return table


# ============================================================
# PUBLIC API
# ============================================================

def map_table(
    table: Table,
) -> Table:

    return map_table_schema(
        table
    )


__all__ = [
    "SCHEMA_MAPPER_VERSION",
    "normalize_header",
    "match_header",
    "map_table_schema",
    "map_table",
]