from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContentUnitType(str, Enum):
    """
    Canonical type of a retrievable document content unit.
    """

    TEXT = "TEXT"
    TABLE = "TABLE"
    IMAGE = "IMAGE"


class ContentUnit(BaseModel):
    """
    Canonical representation of one retrievable piece
    of document content.

    A ContentUnit provides a common abstraction over
    heterogeneous document components such as text,
    tables, and images.

    The model intentionally stores references to the
    original canonical components rather than duplicating
    their complete contents.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # ========================================================
    # IDENTITY
    # ========================================================

    content_unit_id: str = ""

    document_id: str = ""

    unit_type: ContentUnitType

    # ========================================================
    # SOURCE LOCATION
    # ========================================================

    page_number: int = 1

    # ========================================================
    # SOURCE REFERENCE
    # ========================================================

    source_id: str = ""

    # ========================================================
    # POSITION ON PAGE
    # ========================================================

    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None

    # ========================================================
    # RETRIEVAL TEXT
    # ========================================================

    text: str = ""

    # ========================================================
    # ORDER
    # ========================================================

    reading_order: int = 0

    # ========================================================
    # METADATA
    # ========================================================

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )



    @property
    def is_text(self) -> bool:
        return self.unit_type == ContentUnitType.TEXT


    @property
    def is_table(self) -> bool:
        return self.unit_type == ContentUnitType.TABLE


    @property
    def is_image(self) -> bool:
        return self.unit_type == ContentUnitType.IMAGE


__all__ = [
    "ContentUnitType",
    "ContentUnit",
]