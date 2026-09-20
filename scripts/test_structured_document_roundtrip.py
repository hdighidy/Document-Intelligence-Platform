"""
Phase 3.1.14.1
Canonical StructuredDocument Round-Trip Validation
"""

from pathlib import Path

from app.extraction.document_structurer import (
    build_structured_document,
)

from app.extraction.image_extractor import (
    extract_images_from_pdf,
)

from app.storage.structured_document_storage import (
    save_structured_document,
    load_structured_document,
)

from app.models.document import (
    DocumentPage,
)


DOCUMENT_ID = "TEST-3-1-14"

PDF_PATH = Path(
    "data/test/sample.pdf"
)


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.14.1 — "
        "STRUCTURED DOCUMENT ROUND-TRIP VALIDATION"
    )
    print("=" * 70)

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    print("\nTEST 1 — INPUT")

    assert PDF_PATH.exists(), (
        f"Missing PDF: {PDF_PATH}"
    )

    assert PDF_PATH.is_file()

    print("[PASS] Sample PDF exists")
    print(f"       {PDF_PATH}")

    # ========================================================
    # TEST 2 — TEXT EXTRACTION
    # ========================================================

    print("\nTEST 2 — TEXT")

    from app.extraction.text_extractor import (
        extract_text_from_pdf,
    )

    page_texts = extract_text_from_pdf(
        PDF_PATH
    )

    assert len(page_texts) > 0

    pages = []

    for page in page_texts:

        text = "\n".join(
            block.text
            for block in page.blocks
        )

        pages.append(
            DocumentPage(
                page_number=page.page_number,
                width=page.width,
                height=page.height,
                text=text,
                blocks=page.blocks,
            )
        )

    assert len(pages) == 16

    print(
        "[PASS] Text pages extracted"
    )
    print(
        f"       Pages: {len(pages)}"
    )

    # ========================================================
    # TEST 3 — IMAGES
    # ========================================================

    print("\nTEST 3 — IMAGES")

    images = extract_images_from_pdf(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    assert len(images) == 19

    print("[PASS] Images extracted")
    print(
        f"       Images: {len(images)}"
    )

    # ========================================================
    # TEST 4 — BUILD CANONICAL DOCUMENT
    # ========================================================

    print(
        "\nTEST 4 — BUILD "
        "STRUCTUREDDOCUMENT"
    )

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pages=pages,
        images=images,
    )

    assert (
        document.document_id
        == DOCUMENT_ID
    )

    assert (
        document.page_count
        == 16
    )

    assert (
        document.image_count
        == 19
    )

    assert document.has_images

    print(
        "[PASS] StructuredDocument built"
    )

    # ========================================================
    # TEST 5 — PAGE IMAGE RELATIONSHIPS
    # ========================================================

    print(
        "\nTEST 5 — PAGE IMAGE "
        "RELATIONSHIPS"
    )

    pages_with_images = [
        page
        for page in document.pages
        if page.image_ids
    ]

    assert len(
        pages_with_images
    ) > 0

    total_page_image_refs = sum(
        len(page.image_ids)
        for page in document.pages
    )

    assert (
        total_page_image_refs
        == 19
    )

    print(
        "[PASS] Page image references preserved"
    )
    print(
        f"       References: "
        f"{total_page_image_refs}"
    )

    # ========================================================
    # TEST 6 — SAVE
    # ========================================================

    print(
        "\nTEST 6 — PERSIST"
    )

    output_file = (
        save_structured_document(
            document
        )
    )

    assert output_file.exists()
    assert output_file.is_file()

    print(
        "[PASS] Canonical document persisted"
    )
    print(
        f"       {output_file}"
    )

    # ========================================================
    # TEST 7 — RELOAD
    # ========================================================

    print(
        "\nTEST 7 — RELOAD"
    )

    loaded = (
        load_structured_document(
            DOCUMENT_ID
        )
    )

    assert (
        loaded.document_id
        == DOCUMENT_ID
    )

    print(
        "[PASS] Canonical document reloaded"
    )

    # ========================================================
    # TEST 8 — PAGE COUNT
    # ========================================================

    print(
        "\nTEST 8 — PAGE COUNT"
    )

    assert (
        loaded.page_count
        == document.page_count
    )

    print(
        "[PASS] Page count preserved"
    )

    # ========================================================
    # TEST 9 — IMAGE COUNT
    # ========================================================

    print(
        "\nTEST 9 — IMAGE COUNT"
    )

    assert (
        loaded.image_count
        == document.image_count
    )

    assert (
        len(loaded.images)
        == 19
    )

    print(
        "[PASS] Image count preserved"
    )

    # ========================================================
    # TEST 10 — IMAGE REFERENCES
    # ========================================================

    print(
        "\nTEST 10 — IMAGE REFERENCES"
    )

    original_refs = {
        page.page_number:
        list(page.image_ids)
        for page in document.pages
    }

    loaded_refs = {
        page.page_number:
        list(page.image_ids)
        for page in loaded.pages
    }

    assert (
        loaded_refs
        == original_refs
    )

    print(
        "[PASS] Page image references preserved"
    )

    # ========================================================
    # TEST 11 — TEXT BLOCKS
    # ========================================================

    print(
        "\nTEST 11 — TEXT BLOCKS"
    )

    original_blocks = sum(
        len(page.blocks)
        for page in document.pages
    )

    loaded_blocks = sum(
        len(page.blocks)
        for page in loaded.pages
    )

    assert (
        loaded_blocks
        == original_blocks
    )

    print(
        "[PASS] Text blocks preserved"
    )
    print(
        f"       Blocks: {loaded_blocks}"
    )

    # ========================================================
    # TEST 12 — IMAGE OBJECTS
    # ========================================================

    print(
        "\nTEST 12 — IMAGE OBJECTS"
    )

    original_images = {
        image.image_id:
        image.model_dump(mode="json")
        for image in document.images
    }

    loaded_images = {
        image.image_id:
        image.model_dump(mode="json")
        for image in loaded.images
    }

    assert (
        loaded_images
        == original_images
    )

    print(
        "[PASS] Image metadata preserved"
    )

    # ========================================================
    # TEST 13 — COMPLETE ROUND TRIP
    # ========================================================

    print(
        "\nTEST 13 — COMPLETE ROUND TRIP"
    )

    original_data = (
        document.model_dump(
            mode="json"
        )
    )

    loaded_data = (
        loaded.model_dump(
            mode="json"
        )
    )

    assert (
        loaded_data
        == original_data
    )

    print(
        "[PASS] Complete canonical "
        "round-trip integrity"
    )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print(
        "PHASE 3.1.14.1 RESULTS"
    )
    print("=" * 70)

    print(
        "ALL TESTS PASSED"
    )


if __name__ == "__main__":
    main()