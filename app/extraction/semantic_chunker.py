from __future__ import annotations

import re
from typing import Iterable

from app.models.content_unit import ContentUnit
from app.models.semantic_chunk import SemanticChunk


_HEADING_PATTERN = re.compile(
    r"^("
    r"\d+(?:\.\d+)*\.?\s+.+"
    r"|"
    r"[A-Z][A-Z0-9\s\-:&/]{3,}$"
    r")$"
)


def _is_heading(text: str) -> bool:
    """
    Determine whether a ContentUnit looks like a structural
    heading.

    This is intentionally conservative.
    """

    text = text.strip()

    if not text:
        return False

    return bool(
        _HEADING_PATTERN.match(text)
    )


def _build_chunk_id(
    document_id: str,
    chunk_index: int,
) -> str:

    return (
        f"CHUNK-{document_id}-"
        f"{chunk_index:04d}"
    )


def _append_unit(
    units: list[ContentUnit],
    unit: ContentUnit,
    max_characters: int,
) -> bool:
    """
    Determine whether a unit can be appended without
    exceeding the configured chunk size.
    """

    current_text = "\n".join(
        item.text.strip()
        for item in units
        if item.text.strip()
    )

    candidate = unit.text.strip()

    if not candidate:
        return True

    if not current_text:
        return len(candidate) <= max_characters

    return (
        len(current_text)
        + 1
        + len(candidate)
        <= max_characters
    )


def _create_chunk(
    document_id: str,
    units: list[ContentUnit],
    chunk_index: int,
    section: str | None,
) -> SemanticChunk | None:

    if not units:
        return None

    text_parts = [
        unit.text.strip()
        for unit in units
        if unit.text.strip()
    ]

    text = "\n".join(
        text_parts
    )

    if not text:
        return None

    content_unit_ids = [
        unit.content_unit_id
        for unit in units
    ]

    page_numbers = []

    for unit in units:

        if unit.page_number not in page_numbers:

            page_numbers.append(
                unit.page_number
            )

    x_values = [
        unit.x0
        for unit in units
        if unit.x0 is not None
    ]

    y_values = [
        unit.y0
        for unit in units
        if unit.y0 is not None
    ]

    x1_values = [
        unit.x1
        for unit in units
        if unit.x1 is not None
    ]

    y1_values = [
        unit.y1
        for unit in units
        if unit.y1 is not None
    ]

    return SemanticChunk(

        chunk_id=_build_chunk_id(
            document_id,
            chunk_index,
        ),

        document_id=document_id,

        text=text,

        content_unit_ids=content_unit_ids,

        page_numbers=page_numbers,

        section=section,

        reading_order=units[0].reading_order,

        chunk_index=chunk_index,

        chunking_strategy="semantic",

        x0=min(x_values)
        if x_values
        else None,

        y0=min(y_values)
        if y_values
        else None,

        x1=max(x1_values)
        if x1_values
        else None,

        y1=max(y1_values)
        if y1_values
        else None,

        metadata={
            "content_unit_count": len(
                units
            ),
        },
    )


def semantic_chunk_content_units(
    content_units: Iterable[ContentUnit],
    *,
    max_characters: int = 1500,
) -> list[SemanticChunk]:
    """
    Convert canonical ContentUnits into semantic chunks.

    Initial strategy:

        - preserve reading order
        - detect headings
        - group related content
        - split oversized groups
        - preserve provenance
    """

    units = sorted(
        list(content_units),
        key=lambda unit: (
            unit.page_number,
            unit.reading_order,
        ),
    )

    if not units:
        return []

    document_id = units[0].document_id

    chunks: list[SemanticChunk] = []

    current_units: list[ContentUnit] = []

    current_section: str | None = None

    chunk_index = 0

    for unit in units:

        text = unit.text.strip()

        if not text:
            continue

        # ----------------------------------------------------
        # Heading
        # ----------------------------------------------------

        if _is_heading(text):

            if current_units:

                chunk = _create_chunk(
                    document_id=document_id,
                    units=current_units,
                    chunk_index=chunk_index,
                    section=current_section,
                )

                if chunk:

                    chunks.append(
                        chunk
                    )

                    chunk_index += 1

                current_units = []

            current_section = text

            current_units.append(
                unit
            )

            continue

        # ----------------------------------------------------
        # Normal content
        # ----------------------------------------------------

        if not _append_unit(
            current_units,
            unit,
            max_characters,
        ):

            chunk = _create_chunk(
                document_id=document_id,
                units=current_units,
                chunk_index=chunk_index,
                section=current_section,
            )

            if chunk:

                chunks.append(
                    chunk
                )

                chunk_index += 1

            current_units = []

        current_units.append(
            unit
        )

    # --------------------------------------------------------
    # Final chunk
    # --------------------------------------------------------

    if current_units:

        chunk = _create_chunk(
            document_id=document_id,
            units=current_units,
            chunk_index=chunk_index,
            section=current_section,
        )

        if chunk:

            chunks.append(
                chunk
            )

    return chunks


__all__ = [
    "semantic_chunk_content_units",
]