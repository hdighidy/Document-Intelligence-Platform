from pathlib import Path

from app.extraction.document_structurer import (
    build_structured_document,
)

from app.storage.structured_document_storage import (
    save_structured_document,
    load_structured_document,
)


DOCUMENT_ID = "TEST-3-1-13"

OUTPUT_DIR = (
    Path("data")
    / "processed"
    / DOCUMENT_ID
)


def main() -> None:

    print("=" * 70)
    print("PHASE 3.1.13.2 — STRUCTURED DOCUMENT STORAGE")
    print("=" * 70)

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    print("\nTEST 1 — BUILD DOCUMENT")

    document = build_structured_document(
        document_id=DOCUMENT_ID,
    )

    assert document.document_id == DOCUMENT_ID

    print("[PASS] StructuredDocument created")

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    print("\nTEST 2 — SAVE DOCUMENT")

    output_file = save_structured_document(
        document
    )

    assert output_file.exists()
    assert output_file.is_file()

    print("[PASS] structured_document.json created")
    print(f"       {output_file}")

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    print("\nTEST 3 — LOAD DOCUMENT")

    loaded = load_structured_document(
        DOCUMENT_ID
    )

    assert loaded.document_id == DOCUMENT_ID

    print("[PASS] StructuredDocument loaded")

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    print("\nTEST 4 — TYPE VALIDATION")

    from app.models.document import StructuredDocument

    assert isinstance(
        loaded,
        StructuredDocument,
    )

    print("[PASS] Loaded object is StructuredDocument")

    # --------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------

    print("\nTEST 5 — ROUND TRIP")

    assert (
        loaded.model_dump(mode="json")
        ==
        document.model_dump(mode="json")
    )

    print("[PASS] Round-trip data integrity")

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 3.1.13.2 RESULTS")
    print("=" * 70)

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()