from app.models.content_unit import (
    ContentUnit,
    ContentUnitType,
)

from app.extraction.semantic_chunker import (
    semantic_chunk_content_units,
)


def main() -> None:

    units = [

        ContentUnit(
            content_unit_id="CU-P001-T001",
            document_id="DOC-001",
            unit_type=ContentUnitType.TEXT,
            page_number=1,
            source_id="P001-B001",
            text="1. PURPOSE",
            reading_order=1,
        ),

        ContentUnit(
            content_unit_id="CU-P001-T002",
            document_id="DOC-001",
            unit_type=ContentUnitType.TEXT,
            page_number=1,
            source_id="P001-B002",
            text="The purpose of this method statement.",
            reading_order=2,
        ),

        ContentUnit(
            content_unit_id="CU-P001-T003",
            document_id="DOC-001",
            unit_type=ContentUnitType.TEXT,
            page_number=1,
            source_id="P001-B003",
            text="This procedure defines the required activities.",
            reading_order=3,
        ),

        ContentUnit(
            content_unit_id="CU-P002-T001",
            document_id="DOC-001",
            unit_type=ContentUnitType.TEXT,
            page_number=2,
            source_id="P002-B001",
            text="2. SCOPE",
            reading_order=4,
        ),

        ContentUnit(
            content_unit_id="CU-P002-T002",
            document_id="DOC-001",
            unit_type=ContentUnitType.TEXT,
            page_number=2,
            source_id="P002-B002",
            text="This method applies to the project works.",
            reading_order=5,
        ),
    ]

    chunks = semantic_chunk_content_units(
        units
    )

    assert len(chunks) == 2

    assert chunks[0].chunk_id == (
        "CHUNK-DOC-001-0000"
    )

    assert chunks[1].chunk_id == (
        "CHUNK-DOC-001-0001"
    )

    assert chunks[0].section == "1. PURPOSE"

    assert chunks[1].section == "2. SCOPE"

    assert chunks[0].page_numbers == [1]

    assert chunks[1].page_numbers == [2]

    assert chunks[0].content_unit_ids == [
        "CU-P001-T001",
        "CU-P001-T002",
        "CU-P001-T003",
    ]

    assert chunks[1].content_unit_ids == [
        "CU-P002-T001",
        "CU-P002-T002",
    ]

    assert chunks[0].character_count > 0

    assert chunks[0].word_count > 0

    assert not chunks[0].has_multiple_pages

    print("SemanticChunk model: PASS")
    print("Heading detection: PASS")
    print("Section grouping: PASS")
    print("Reading order: PASS")
    print("Page provenance: PASS")
    print("ContentUnit provenance: PASS")
    print("Deterministic IDs: PASS")
    print("Chunk statistics: PASS")

    print("\nPHASE 3.2.3 — ALL TESTS PASSED")


if __name__ == "__main__":
    main()