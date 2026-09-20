"""
Canonical Structured Table Generator
=====================================

Document AI — Phase 3.1.9

Responsibilities
----------------

Convert a schema-mapped Table into a CanonicalTable.

Pipeline:

    Structured Table
          ↓
    Schema Mapping
          ↓
    Canonical Generation
          ↓
    CanonicalTable
          ↓
    CanonicalTableRow[]

Design principles
-----------------

1. Never destroy source information.
2. Preserve normalized values whenever available.
3. Preserve original source values.
4. Use schema mappings as the authoritative column mapping.
5. Never invent a canonical field for an unmapped column.
6. Preserve unmapped columns using deterministic fallback names.
7. Preserve row indexes.
8. Propagate confidence.
9. Generate deterministic canonical IDs.
10. Attach the generated canonical table to the source Table.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

from app.models.table import (
    CanonicalTable,
    CanonicalTableRow,
    SchemaMappingStatus,
    Table,
    TableColumnMapping,
    TableFieldDefinition,
    TableSchema,
)


# ============================================================
# VERSION
# ============================================================

GENERATOR_VERSION = "3.1.9"


# ============================================================
# PUBLIC API
# ============================================================


def generate_canonical_table(
    table: Table,
    *,
    attach: bool = True,
) -> CanonicalTable:
    """
    Generate a canonical structured representation.

    Parameters
    ----------
    table:
        Schema-mapped Table.

    attach:
        When True, assign the generated CanonicalTable to
        table.canonical_table.

    Returns
    -------
    CanonicalTable

    Raises
    ------
    ValueError
        When no schema is available.
    """

    if table is None:
        raise ValueError(
            "Cannot generate canonical table from None."
        )

    schema = table.schema

    if schema is None:
        raise ValueError(
            "Cannot generate canonical table: "
            "table.schema is None."
        )

    mappings = _build_effective_mappings(
        table=table,
        schema=schema,
    )

    canonical_rows = _generate_rows(
        table=table,
        mappings=mappings,
    )

    canonical_id = _generate_canonical_id(
        table=table,
        schema=schema,
    )

    mapping_status = _resolve_mapping_status(
        schema=schema,
        mappings=mappings,
    )

    mapping_confidence = _calculate_mapping_confidence(
        schema=schema,
        mappings=mappings,
    )

    canonical_table = CanonicalTable(
        canonical_table_id=canonical_id,
        source_table_id=table.table_id,
        document_id=table.document_id,
        schema=schema,
        rows=canonical_rows,
        row_count=len(canonical_rows),
        column_count=_canonical_column_count(
            mappings
        ),
        mapping_status=mapping_status,
        mapping_confidence=mapping_confidence,
        generated_at=datetime.now(
            timezone.utc
        ),
        generator_version=GENERATOR_VERSION,
    )

    if attach:
        table.canonical_table = canonical_table
        table.schema_mapping_status = (
            mapping_status
        )
        table.schema_mapping_confidence = (
            mapping_confidence
        )

    return canonical_table


# ============================================================
# ALIAS
# ============================================================


build_canonical_table = (
    generate_canonical_table
)


# ============================================================
# MAPPING
# ============================================================


def _build_effective_mappings(
    *,
    table: Table,
    schema: TableSchema,
) -> list[TableColumnMapping]:
    """
    Build a complete physical-column mapping.

    Existing schema.column_mappings are authoritative.

    If a schema contains fields but does not contain
    column_mappings, derive mappings from the field definitions.
    """

    if schema.column_mappings:
        return list(
            sorted(
                schema.column_mappings,
                key=lambda item: item.column_index,
            )
        )

    mappings: list[TableColumnMapping] = []

    for field in sorted(
        schema.fields,
        key=lambda item: item.column_index,
    ):
        mappings.append(
            TableColumnMapping(
                column_index=field.column_index,
                source_header=field.source_header,
                normalized_header=_normalize_header(
                    field.source_header
                ),
                canonical_field=field.field_name,
                field_role=field.field_role,
                semantic_type=field.semantic_type,
                mapping_source=field.mapping_source,
                confidence=field.mapping_confidence,
                matched_alias=field.matched_alias,
                is_mapped=bool(
                    field.field_name
                ),
            )
        )

    if mappings:
        return mappings

    return _derive_unmapped_mappings(
        table
    )


def _derive_unmapped_mappings(
    table: Table,
) -> list[TableColumnMapping]:
    """
    Create safe fallback mappings when the schema has
    no explicit mappings.

    These fields are intentionally marked as unmapped.
    """

    column_count = max(
        table.column_count,
        _infer_column_count(table),
    )

    mappings: list[TableColumnMapping] = []

    for column_index in range(
        column_count
    ):
        header = ""

        if (
            table.headers
            and column_index < len(table.headers)
        ):
            header = table.headers[
                column_index
            ]

        mappings.append(
            TableColumnMapping(
                column_index=column_index,
                source_header=header,
                normalized_header=_normalize_header(
                    header
                ),
                canonical_field="",
                is_mapped=False,
                confidence=0.0,
            )
        )

    return mappings


# ============================================================
# ROW GENERATION
# ============================================================


def _generate_rows(
    *,
    table: Table,
    mappings: list[TableColumnMapping],
) -> list[CanonicalTableRow]:
    """
    Convert every logical data row into a canonical row.

    The function prefers:

        table.data_rows

    when available.

    Otherwise it derives data rows from:

        table.rows

    using header/data structure metadata.
    """

    source_rows = _get_data_rows(
        table
    )

    result: list[CanonicalTableRow] = []

    for logical_index, source_row in enumerate(
        source_rows
    ):
        source_row_index = _resolve_source_row_index(
            table=table,
            logical_index=logical_index,
        )

        values: dict[str, Any] = {}
        source_values: dict[str, Any] = {}

        row_confidences: list[float] = []

        for mapping in mappings:
            column_index = mapping.column_index

            raw_value = _get_row_value(
                source_row,
                column_index,
            )

            normalized_value = _get_normalized_cell_value(
                table=table,
                source_row_index=source_row_index,
                column_index=column_index,
                fallback=raw_value,
            )

            source_key = (
                mapping.source_header
                or f"column_{column_index + 1}"
            )

            source_values[
                source_key
            ] = raw_value

            canonical_field = (
                mapping.canonical_field.strip()
                if mapping.canonical_field
                else ""
            )

            if not canonical_field:
                canonical_field = (
                    _fallback_field_name(
                        mapping=mapping,
                        column_index=column_index,
                    )
                )

            values[
                canonical_field
            ] = normalized_value

            row_confidences.append(
                _cell_confidence(
                    table=table,
                    source_row_index=source_row_index,
                    column_index=column_index,
                    mapping=mapping,
                )
            )

        confidence = _average(
            row_confidences
        )

        result.append(
            CanonicalTableRow(
                row_index=source_row_index,
                values=values,
                source_values=source_values,
                confidence=confidence,
            )
        )

    return result


# ============================================================
# SOURCE ROW RESOLUTION
# ============================================================


def _get_data_rows(
    table: Table,
) -> list[list[str]]:
    """
    Return logical data rows.

    Priority:

        1. data_rows
        2. rows after data_start_row_index
        3. rows after header_row_index
        4. rows[1:]
        5. rows
    """

    if table.data_rows:
        return [
            list(row)
            for row in table.data_rows
        ]

    rows = table.rows or []

    if not rows:
        return []

    if (
        table.data_start_row_index
        is not None
    ):
        start = max(
            0,
            table.data_start_row_index,
        )

        end = (
            table.data_end_row_index
            if table.data_end_row_index
            is not None
            else len(rows) - 1
        )

        return [
            list(row)
            for row in rows[
                start : end + 1
            ]
        ]

    if (
        table.header_row_index
        is not None
    ):
        start = (
            table.header_row_index
            + 1
        )

        return [
            list(row)
            for row in rows[start:]
        ]

    if len(rows) > 1:
        return [
            list(row)
            for row in rows[1:]
        ]

    return [
        list(row)
        for row in rows
    ]


def _resolve_source_row_index(
    *,
    table: Table,
    logical_index: int,
) -> int:
    """
    Resolve logical data-row index to source row index.
    """

    if table.data_start_row_index is not None:
        return (
            table.data_start_row_index
            + logical_index
        )

    if table.header_row_index is not None:
        return (
            table.header_row_index
            + 1
            + logical_index
        )

    if table.rows and len(table.rows) > 1:
        return logical_index + 1

    return logical_index


# ============================================================
# CELL VALUE RESOLUTION
# ============================================================


def _get_normalized_cell_value(
    *,
    table: Table,
    source_row_index: int,
    column_index: int,
    fallback: Any,
) -> Any:
    """
    Retrieve the highest-quality normalized cell value.

    Priority:

        normalized_value
        numeric_value
        normalized_text
        text
        fallback
    """

    cell = _find_cell(
        table=table,
        row_index=source_row_index,
        column_index=column_index,
    )

    if cell is None:
        return _safe_value(
            fallback
        )

    if cell.normalized_value is not None:
        return _safe_value(
            cell.normalized_value
        )

    if cell.numeric_value is not None:
        return _safe_value(
            cell.numeric_value
        )

    if (
        cell.normalized_text is not None
        and cell.normalized_text != ""
    ):
        return cell.normalized_text

    if cell.text != "":
        return cell.text

    if cell.raw_text is not None:
        return cell.raw_text

    return _safe_value(
        fallback
    )


def _find_cell(
    *,
    table: Table,
    row_index: int,
    column_index: int,
):
    """
    Locate a TableCell by physical coordinates.
    """

    for cell in table.cells:
        if (
            cell.row_index == row_index
            and cell.column_index
            == column_index
        ):
            return cell

    return None


# ============================================================
# CONFIDENCE
# ============================================================


def _cell_confidence(
    *,
    table: Table,
    source_row_index: int,
    column_index: int,
    mapping: TableColumnMapping,
) -> float:
    """
    Calculate canonical value confidence.

    Combines:

        cell confidence
        schema mapping confidence
    """

    cell = _find_cell(
        table=table,
        row_index=source_row_index,
        column_index=column_index,
    )

    cell_confidence = (
        cell.confidence
        if cell is not None
        else 1.0
    )

    mapping_confidence = (
        mapping.confidence
        if mapping.is_mapped
        else 0.0
    )

    if mapping.is_mapped:
        return _clamp(
            cell_confidence
            * mapping_confidence
        )

    return _clamp(
        cell_confidence
        * 0.5
    )


def _calculate_mapping_confidence(
    *,
    schema: TableSchema,
    mappings: list[TableColumnMapping],
) -> float:
    """
    Calculate final mapping confidence.
    """

    if not mappings:
        return 0.0

    scores = []

    for mapping in mappings:
        if mapping.is_mapped:
            scores.append(
                mapping.confidence
            )
        else:
            scores.append(0.0)

    return _clamp(
        _average(scores)
    )


# ============================================================
# STATUS
# ============================================================


def _resolve_mapping_status(
    *,
    schema: TableSchema,
    mappings: list[TableColumnMapping],
) -> SchemaMappingStatus:
    """
    Determine final canonical mapping status.
    """

    if not mappings:
        return SchemaMappingStatus.FAILED

    mapped = sum(
        1
        for item in mappings
        if item.is_mapped
        and item.canonical_field
    )

    if mapped == 0:
        return SchemaMappingStatus.FAILED

    if mapped == len(mappings):
        return SchemaMappingStatus.COMPLETE

    return SchemaMappingStatus.PARTIAL


# ============================================================
# FIELD COUNT
# ============================================================


def _canonical_column_count(
    mappings: list[TableColumnMapping],
) -> int:
    """
    Return number of source columns represented.
    """

    return len(mappings)


# ============================================================
# FALLBACK FIELD NAMES
# ============================================================


def _fallback_field_name(
    *,
    mapping: TableColumnMapping,
    column_index: int,
) -> str:
    """
    Generate a deterministic fallback field name.

    Example:

        "Delivery Date" → delivery_date

    If no header exists:

        column_7
    """

    if mapping.normalized_header:
        candidate = _normalize_header(
            mapping.normalized_header
        )

        if candidate:
            return candidate

    if mapping.source_header:
        candidate = _normalize_header(
            mapping.source_header
        )

        if candidate:
            return candidate

    return (
        f"column_{column_index + 1}"
    )


# ============================================================
# HEADER NORMALIZATION
# ============================================================


def _normalize_header(
    value: Any,
) -> str:
    """
    Convert a source header into a stable field-like name.

    No semantic correction is performed here.

    Example:

        "Delivary Date"
            →
        "delivary_date"

    The original spelling remains available through
    source_header.
    """

    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        text,
    )

    text = re.sub(
        r"_+",
        "_",
        text,
    )

    return text.strip(
        "_"
    ).lower()


# ============================================================
# TABLE DIMENSIONS
# ============================================================


def _infer_column_count(
    table: Table,
) -> int:
    """
    Infer physical column count from the table.
    """

    counts = []

    if table.headers:
        counts.append(
            len(table.headers)
        )

    for row in table.rows:
        counts.append(
            len(row)
        )

    for row in table.data_rows:
        counts.append(
            len(row)
        )

    if not counts:
        return 0

    return max(
        counts
    )


def _get_row_value(
    row: list[Any],
    column_index: int,
) -> Any:
    """
    Safely retrieve a column value.
    """

    if (
        column_index < 0
        or column_index >= len(row)
    ):
        return None

    return row[column_index]


# ============================================================
# IDS
# ============================================================


def _generate_canonical_id(
    *,
    table: Table,
    schema: TableSchema,
) -> str:
    """
    Generate deterministic canonical table ID.

    Same source table + same schema produces the same ID.
    """

    source = "|".join(
        [
            table.document_id or "",
            table.table_id or "",
            schema.schema_id or "",
            schema.schema_version or "",
        ]
    )

    digest = hashlib.sha256(
        source.encode(
            "utf-8"
        )
    ).hexdigest()[:12].upper()

    return (
        f"CANON-{digest}"
    )


# ============================================================
# SAFE VALUE
# ============================================================


def _safe_value(
    value: Any,
) -> Any:
    """
    Convert values into safe JSON-compatible primitives
    where possible.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    if isinstance(
        value,
        list,
    ):
        return [
            _safe_value(item)
            for item in value
        ]

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key): _safe_value(
                item
            )
            for key, item in value.items()
        }

    return str(value)


# ============================================================
# HELPERS
# ============================================================


def _average(
    values: list[float],
) -> float:
    if not values:
        return 0.0

    return sum(
        values
    ) / len(values)


def _clamp(
    value: float,
) -> float:
    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "GENERATOR_VERSION",
    "generate_canonical_table",
    "build_canonical_table",
]