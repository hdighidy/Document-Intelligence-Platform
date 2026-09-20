from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SemanticChunk(BaseModel):
    """
    Canonical semantic retrieval chunk.

    A SemanticChunk is a retrieval-oriented representation
    derived from one or more ContentUnit objects.

    The chunk preserves provenance back to the original
    document components.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # ========================================================
    # IDENTITY
    # ========================================================

    chunk_id: str = ""

    document_id: str = ""

    # ========================================================
    # CONTENT
    # ========================================================

    text: str = ""

    # ========================================================
    # SOURCE CONTENT UNITS
    # ========================================================

    content_unit_ids: list[str] = Field(
        default_factory=list
    )

    # ========================================================
    # SOURCE LOCATION
    # ========================================================

    page_numbers: list[int] = Field(
        default_factory=list
    )

    # ========================================================
    # STRUCTURAL CONTEXT
    # ========================================================

    section: str | None = None

    subsection: str | None = None

    # ========================================================
    # READING ORDER
    # ========================================================

    reading_order: int = 0

    # ========================================================
    # CHUNK POSITION
    # ========================================================

    chunk_index: int = 0

    # ========================================================
    # CHUNKING INFORMATION
    # ========================================================

    chunking_strategy: str = "semantic"

    # ========================================================
    # PAGE BOUNDING BOX
    # ========================================================

    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None

    # ========================================================
    # METADATA
    # ========================================================

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # ========================================================
    # CONVENIENCE PROPERTIES
    # ========================================================

    @property
    def page_number(self) -> int | None:
        """
        Return the first page associated with the chunk.
        """

        if not self.page_numbers:
            return None

        return self.page_numbers[0]

    @property
    def has_multiple_pages(self) -> bool:
        """
        Return True when the chunk spans multiple pages.
        """

        return len(self.page_numbers) > 1

    @property
    def character_count(self) -> int:
        """
        Return number of characters in the chunk.
        """

        return len(self.text)

    @property
    def word_count(self) -> int:
        """
        Return approximate word count.
        """

        return len(self.text.split())


__all__ = [
    "SemanticChunk",
]