from __future__ import annotations

from app.models.retrieval import RetrievalDocument
from app.models.semantic_chunk import SemanticChunk


def _build_retrieval_id(
    document_id: str,
    chunk_index: int,
) -> str:
    return (
        f"RET-{document_id}-"
        f"{chunk_index:04d}"
    )


def build_retrieval_document(
    chunk: SemanticChunk,
) -> RetrievalDocument:
    """
    Convert one canonical SemanticChunk into a retrieval-ready
    RetrievalDocument.
    """

    return RetrievalDocument(
        retrieval_id=_build_retrieval_id(
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
        ),

        document_id=chunk.document_id,

        chunk_id=chunk.chunk_id,

        text=chunk.text,

        section=chunk.section,

        page_numbers=list(
            chunk.page_numbers
        ),

        content_unit_ids=list(
            chunk.content_unit_ids
        ),

        chunk_index=chunk.chunk_index,

        reading_order=chunk.reading_order,

        metadata={
            **chunk.metadata,
            "chunking_strategy": (
                chunk.chunking_strategy
            ),
        },
    )


def build_retrieval_documents(
    chunks: list[SemanticChunk],
) -> list[RetrievalDocument]:
    """
    Convert semantic chunks into deterministic retrieval records.
    """

    return [
        build_retrieval_document(chunk)
        for chunk in chunks
    ]


__all__ = [
    "build_retrieval_document",
    "build_retrieval_documents",
]