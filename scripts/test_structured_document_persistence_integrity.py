"""
Phase 3.1.14.2
============================================================

Persistence Integrity Test

Validates that Text + Tables + Images remain structurally
and relationally intact after StructuredDocument persistence
and reload.

This test verifies not only object serialization but also
cross-component relationships.

Expected sample baseline:

    Pages  : 16
    Images : 19
"""

from pathlib import Path

from app.extraction.text_extractor import (
    extract_text_from_pdf,
)

from app.extraction.table_pipeline import (
    extract_document_tables,
)

from app.extraction.image_extractor import (
    extract_images_from_pdf,
)

from app.extraction.document_structurer import (
    build_structured_document,
)

from app.models.document import (
    DocumentPage,
)

from app.storage.structured_document_storage import (
    save_structured_document,
    load_structured_document,
)


# ============================================================
# CONFIGURATION
# ============================================================

DOCUMENT_ID = (
    "TEST-3-1-14-2"
)

PDF_PATH = Path(
    "data/test/sample.pdf"
)


# ============================================================
# ASSERTION HELPER
# ============================================================

checks_passed = 0
checks_failed = 0


def check(
    condition: bool,
    message: str,
    details: str | None = None,
) -> None:

    global checks_passed
    global checks_failed

    if condition:

        checks_passed += 1

        print(
            f"[PASS] {message}"
        )

        if details:
            print(
                f"       {details}"
            )

    else:

        checks_failed += 1

        print(
            f"[FAIL] {message}"
        )

        if details:
            print(
                f"       {details}"
            )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    global checks_passed
    global checks_failed

    print("=" * 70)
    print(
        "PHASE 3.1.14.2 — "
        "TEXT + TABLE + IMAGE "
        "PERSISTENCE INTEGRITY"
    )
    print("=" * 70)

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    print(
        "\nTEST 1 — INPUT"
    )

    check(
        PDF_PATH.exists(),
        "Sample PDF exists",
        str(PDF_PATH),
    )

    check(
        PDF_PATH.is_file(),
        "Sample PDF is a file",
    )

    # ========================================================
    # TEST 2 — TEXT EXTRACTION
    # ========================================================

    print(
        "\nTEST 2 — TEXT EXTRACTION"
    )

    page_texts = (
        extract_text_from_pdf(
            PDF_PATH
        )
    )

    check(
        len(page_texts) == 16,
        "Expected page count",
        f"Pages: {len(page_texts)}",
    )

    pages: list[DocumentPage] = []

    for page in page_texts:

        page_text = "\n".join(
            block.text
            for block in page.blocks
        )

        pages.append(
            DocumentPage(
                page_number=page.page_number,
                width=page.width,
                height=page.height,
                text=page_text,
                blocks=page.blocks,
            )
        )

    original_text_block_count = sum(
        len(page.blocks)
        for page in pages
    )

    check(
        original_text_block_count > 0,
        "Text blocks extracted",
        f"Blocks: {original_text_block_count}",
    )

    # ========================================================
    # TEST 3 — TABLE EXTRACTION
    # ========================================================

    print(
        "\nTEST 3 — TABLE EXTRACTION"
    )

    tables = extract_document_tables(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    check(
        isinstance(tables, list),
        "Table extraction returned list",
    )

    original_table_count = len(
        tables
    )

    print(
        f"       Tables: {original_table_count}"
    )

    # ========================================================
    # TEST 4 — IMAGE EXTRACTION
    # ========================================================

    print(
        "\nTEST 4 — IMAGE EXTRACTION"
    )

    images = extract_images_from_pdf(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    check(
        len(images) == 19,
        "Expected image count",
        f"Images: {len(images)}",
    )

    original_image_count = len(
        images
    )

    # ========================================================
    # TEST 5 — BUILD CANONICAL DOCUMENT
    # ========================================================

    print(
        "\nTEST 5 — BUILD CANONICAL DOCUMENT"
    )

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pages=pages,
        tables=tables,
        images=images,
    )

    check(
        document.document_id
        == DOCUMENT_ID,
        "Document ID correct",
    )

    check(
        document.page_count
        == 16,
        "Canonical page count correct",
        f"Pages: {document.page_count}",
    )

    check(
        len(document.images)
        == original_image_count,
        "Canonical image count correct",
    )

    check(
        len(document.tables)
        == original_table_count,
        "Canonical table count correct",
    )

    # ========================================================
    # TEST 6 — IMAGE RELATIONSHIPS
    # ========================================================

    print(
        "\nTEST 6 — IMAGE RELATIONSHIPS"
    )

    image_ids = {
        image.image_id
        for image in document.images
    }

    page_image_ids = set()

    for page in document.pages:

        page_image_ids.update(
            page.image_ids
        )

    check(
        len(image_ids)
        == len(document.images),
        "Image IDs are unique",
    )

    check(
        page_image_ids
        == image_ids,
        "All images have page references",
        (
            f"Document images: "
            f"{len(image_ids)}, "
            f"Page references: "
            f"{len(page_image_ids)}"
        ),
    )

    # ========================================================
    # TEST 7 — IMAGE PAGE CONSISTENCY
    # ========================================================

    print(
        "\nTEST 7 — IMAGE PAGE CONSISTENCY"
    )

    image_by_id = {
        image.image_id: image
        for image in document.images
    }

    image_relationships_valid = True

    for page in document.pages:

        for image_id in page.image_ids:

            image = image_by_id.get(
                image_id
            )

            if image is None:

                image_relationships_valid = False

                print(
                    f"       Missing image: "
                    f"{image_id}"
                )

                continue

            if (
                image.page_number
                != page.page_number
            ):

                image_relationships_valid = False

                print(
                    f"       Page mismatch: "
                    f"{image_id} "
                    f"declared page "
                    f"{image.page_number}, "
                    f"referenced from "
                    f"page "
                    f"{page.page_number}"
                )

    check(
        image_relationships_valid,
        "Image page relationships are consistent",
    )

    # ========================================================
    # TEST 8 — TABLE RELATIONSHIPS
    # ========================================================

    print(
        "\nTEST 8 — TABLE RELATIONSHIPS"
    )

    table_ids = {
        table.table_id
        for table in document.tables
    }

    referenced_table_ids = set()

    for page in document.pages:

        referenced_table_ids.update(
            page.table_ids
        )

    check(
        len(table_ids)
        == len(document.tables),
        "Table IDs are unique",
    )

    # Some earlier table pipeline versions may not populate
    # page.table_ids. Therefore, distinguish between:
    #
    # 1. table objects
    # 2. explicit page references

    if document.tables:

        check(
            referenced_table_ids.issubset(
                table_ids
            ),
            "No orphan table references",
        )

    else:

        check(
            len(referenced_table_ids)
            == 0,
            "No orphan table references",
        )

    # ========================================================
    # TEST 9 — TABLE REFERENCE OBJECTS
    # ========================================================

    print(
        "\nTEST 9 — TABLE REFERENCE OBJECTS"
    )

    reference_ids = {
        reference.table_id
        for reference
        in document.table_references
    }

    check(
        reference_ids
        == table_ids,
        "Document table references match tables",
        (
            f"Tables: {len(table_ids)}, "
            f"References: {len(reference_ids)}"
        ),
    )

    # ========================================================
    # TEST 10 — TEXT INTEGRITY
    # ========================================================

    print(
        "\nTEST 10 — TEXT INTEGRITY"
    )

    canonical_text_block_count = sum(
        len(page.blocks)
        for page in document.pages
    )

    check(
        canonical_text_block_count
        == original_text_block_count,
        "Text block count preserved",
        (
            f"Blocks: "
            f"{canonical_text_block_count}"
        ),
    )

    # ========================================================
    # TEST 11 — SAVE
    # ========================================================

    print(
        "\nTEST 11 — PERSISTENCE"
    )

    output_file = (
        save_structured_document(
            document
        )
    )

    check(
        output_file.exists(),
        "StructuredDocument JSON exists",
        str(output_file),
    )

    check(
        output_file.stat().st_size > 0,
        "StructuredDocument JSON is not empty",
        (
            f"Size: "
            f"{output_file.stat().st_size} bytes"
        ),
    )

    # ========================================================
    # TEST 12 — RELOAD
    # ========================================================

    print(
        "\nTEST 12 — RELOAD"
    )

    loaded = (
        load_structured_document(
            document_id=DOCUMENT_ID,
            pages=pages,
            tables=tables,
            images=images,
        )
    )
    

    check(
        loaded.document_id
        == document.document_id,
        "Document ID preserved",
    )

    # ========================================================
    # TEST 13 — PAGE INTEGRITY
    # ========================================================

    print(
        "\nTEST 13 — PAGE INTEGRITY"
    )

    check(
        loaded.page_count
        == document.page_count,
        "Page count preserved",
    )

    check(
        [
            page.page_number
            for page in loaded.pages
        ]
        ==
        [
            page.page_number
            for page in document.pages
        ],
        "Page ordering preserved",
    )

    # ========================================================
    # TEST 14 — TEXT INTEGRITY AFTER RELOAD
    # ========================================================

    print(
        "\nTEST 14 — TEXT AFTER RELOAD"
    )

    loaded_text_blocks = sum(
        len(page.blocks)
        for page in loaded.pages
    )

    check(
        loaded_text_blocks
        == original_text_block_count,
        "Text blocks survive reload",
        f"Blocks: {loaded_text_blocks}",
    )

    # ========================================================
    # TEST 15 — TABLE INTEGRITY AFTER RELOAD
    # ========================================================

    print(
        "\nTEST 15 — TABLES AFTER RELOAD"
    )

    check(
        len(loaded.tables)
        == original_table_count,
        "Table count survives reload",
    )

    loaded_table_ids = {
        table.table_id
        for table in loaded.tables
    }

    check(
        loaded_table_ids
        == table_ids,
        "Table IDs survive reload",
    )

    loaded_reference_ids = {
        reference.table_id
        for reference
        in loaded.table_references
    }

    check(
        loaded_reference_ids
        == loaded_table_ids,
        "Table references survive reload",
    )

    # ========================================================
    # TEST 16 — IMAGE INTEGRITY AFTER RELOAD
    # ========================================================

    print(
        "\nTEST 16 — IMAGES AFTER RELOAD"
    )

    check(
        len(loaded.images)
        == original_image_count,
        "Image count survives reload",
    )

    loaded_image_ids = {
        image.image_id
        for image in loaded.images
    }

    check(
        loaded_image_ids
        == image_ids,
        "Image IDs survive reload",
    )

    # ========================================================
    # TEST 17 — PAGE IMAGE REFERENCES AFTER RELOAD
    # ========================================================

    print(
        "\nTEST 17 — PAGE IMAGE REFERENCES"
    )

    original_page_image_map = {
        page.page_number:
        list(page.image_ids)
        for page in document.pages
    }

    loaded_page_image_map = {
        page.page_number:
        list(page.image_ids)
        for page in loaded.pages
    }

    check(
        loaded_page_image_map
        == original_page_image_map,
        "Page image references survive reload",
    )

    # ========================================================
    # TEST 18 — CROSS-COMPONENT IMAGE VALIDATION
    # ========================================================

    print(
        "\nTEST 18 — CROSS-COMPONENT IMAGE VALIDATION"
    )

    loaded_image_by_id = {
        image.image_id: image
        for image in loaded.images
    }

    cross_component_image_integrity = True

    for page in loaded.pages:

        for image_id in page.image_ids:

            image = loaded_image_by_id.get(
                image_id
            )

            if image is None:

                cross_component_image_integrity = False
                break

            if (
                image.page_number
                != page.page_number
            ):

                cross_component_image_integrity = False
                break

    check(
        cross_component_image_integrity,
        "Reloaded image relationships remain valid",
    )

    # ========================================================
    # TEST 19 — COMPLETE CANONICAL EQUALITY
    # ========================================================

    print(
        "\nTEST 19 — COMPLETE CANONICAL EQUALITY"
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

    print(
        f"Original data keys: {set(original_data)}, "
        f"Loaded data keys: {set(loaded_data)}"
    )

    if loaded_data != original_data:


        all_keys = set(original_data) | set(loaded_data)
        print(f"All keys: {all_keys}")

        for key in sorted(all_keys):

            original_value = original_data.get(key)
            loaded_value = loaded_data.get(key)

            if key == "tables" and original_value != loaded_value:

                print("\n" + "=" * 70)
                print("TABLE-LEVEL DIFFERENCE ANALYSIS")
                print("=" * 70)

                print(
                    f"Original table count: {len(original_value)}"
                )

                print(
                    f"Loaded table count:   {len(loaded_value)}"
                )

                for index, (original_table, loaded_table) in enumerate(
                    zip(original_value, loaded_value)
                ):

                    if original_table != loaded_table:

                        print(
                            f"\n--- TABLE INDEX {index} DIFFERENCE ---"
                        )

                        all_table_keys = (
                            set(original_table)
                            | set(loaded_table)
                        )

                        for table_key in sorted(
                            all_table_keys
                        ):

                            original_field = (
                                original_table.get(
                                    table_key
                                )
                            )

                            loaded_field = (
                                loaded_table.get(
                                    table_key
                                )
                            )

                            if (
                                original_field
                                != loaded_field
                            ):

                                print(
                                    f"\nFIELD: {table_key}"
                                )

                                print(
                                    "ORIGINAL:"
                                )

                                print(
                                    original_field
                                )

                                print(
                                    "\nLOADED:"
                                )

                                print(
                                    loaded_field
                                )

    check(
        loaded_data == original_data,
        "Complete canonical structure preserved",
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print(
        "PHASE 3.1.14.2 RESULTS"
    )
    print("=" * 70)

    print(
        f"Checks passed: "
        f"{checks_passed}"
    )

    print(
        f"Checks failed: "
        f"{checks_failed}"
    )

    if checks_failed == 0:

        print(
            "\nALL TESTS PASSED"
        )

    else:

        raise AssertionError(
            f"{checks_failed} "
            f"checks failed"
        )


if __name__ == "__main__":
    main()