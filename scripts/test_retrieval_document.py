from app.models.semantic_chunk import SemanticChunk
from app.extraction.retrieval_document_builder import (
    build_retrieval_document,
)


def main() -> None:

    chunk = SemanticChunk(
        chunk_id="CHUNK-DOC-001-0000",
        document_id="DOC-001",
        text="The purpose of this method statement.",
        content_unit_ids=[
            "CU-P001-T001",
            "CU-P001-T002",
        ],
        page_numbers=[1],
        section="1. PURPOSE",
        reading_order=1,
        chunk_index=0,
        chunking_strategy="semantic",
        metadata={
            "content_unit_count": 2,
        },
    )

    retrieval = build_retrieval_document(
        chunk
    )

    assert retrieval.retrieval_id == (
        "RET-DOC-001-0000"
    )

    assert retrieval.document_id == "DOC-001"

    assert retrieval.chunk_id == (
        "CHUNK-DOC-001-0000"
    )

    assert retrieval.text == (
        "The purpose of this method statement."
    )

    assert retrieval.section == "1. PURPOSE"

    assert retrieval.page_numbers == [1]

    assert retrieval.content_unit_ids == [
        "CU-P001-T001",
        "CU-P001-T002",
    ]

    assert retrieval.chunk_index == 0

    assert retrieval.reading_order == 1

    assert retrieval.metadata[
        "content_unit_count"
    ] == 2

    print("RetrievalDocument model: PASS")
    print("SemanticChunk conversion: PASS")
    print("Deterministic retrieval ID: PASS")
    print("Provenance preservation: PASS")
    print("Metadata preservation: PASS")
    print("\nPHASE 3.3.1 — ALL TESTS PASSED")


if __name__ == "__main__":
    main()