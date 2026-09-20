from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RetrievalDocument(BaseModel):
    """
    Canonical retrieval-ready representation of one semantic chunk.

    This model forms the boundary between document processing
    and information retrieval.

    The original SemanticChunk remains the canonical source.
    This model contains the normalized information required by
    lexical, vector, and hybrid retrieval systems.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # ========================================================
    # IDENTITY
    # ========================================================

    retrieval_id: str = ""

    document_id: str = ""

    chunk_id: str = ""

    # ========================================================
    # RETRIEVAL CONTENT
    # ========================================================

    text: str = ""

    # ========================================================
    # SEMANTIC CONTEXT
    # ========================================================

    section: str | None = None

    # ========================================================
    # SOURCE PROVENANCE
    # ========================================================

    page_numbers: list[int] = Field(
        default_factory=list
    )

    content_unit_ids: list[str] = Field(
        default_factory=list
    )

    # ========================================================
    # ORDER
    # ========================================================

    chunk_index: int = 0

    reading_order: int = 0

    # ========================================================
    # RETRIEVAL METADATA
    # ========================================================

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


__all__ = [
    "RetrievalDocument",
]