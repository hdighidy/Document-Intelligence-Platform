"""
Phase 3.1.12.5
End-to-End Text + Tables + Images Integration
"""

from pathlib import Path

from app.extraction.document_structurer import (
    build_structured_document,
)

from app.extraction.image_extractor import (
    extract_images_from_pdf,
)

from app.extraction.table_pipeline import (
    extract_document_tables,
)

from app.extraction.text_extractor import (
    extract_text_from_pdf,
)

from app.models.document import (
    DocumentPage,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)

DOCUMENT_ID = "TEST-E2E-001"


def main() -> None:

    passed = 0
    failed = 0

    def check(
        condition: bool,
        message: str,
        value=None,
    ):

        nonlocal passed, failed

        if condition:
            passed += 1
            print(f"[PASS] {message}")

            if value is not None:
                print(f"       {value}")

        else:
            failed += 1
            print(f"[FAIL] {message}")

            if value is not None:
                print(f"       {value}")

    print("=" * 70)
    print(
        "PHASE 3.1.12.5 — "
        "END-TO-END TEXT + TABLES + IMAGES INTEGRATION"
    )
    print("=" * 70)

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    print("\nTEST 1 — INPUT")

    check(
        PDF_PATH.exists(),
        "Sample PDF exists",
        PDF_PATH,
    )

    check(
        PDF_PATH.is_file(),
        "Sample PDF is a file",
    )

    # ========================================================
    # TEST 2 — TEXT EXTRACTION
    # ========================================================

    print("\nTEST 2 — TEXT EXTRACTION")

    page_texts = extract_text_from_pdf(
        PDF_PATH
    )

    check(
        len(page_texts) == 16,
        "Expected page count",
        len(page_texts),
    )

    total_blocks = sum(
        len(page.blocks)
        for page in page_texts
    )

    check(
        total_blocks > 0,
        "Text blocks extracted",
        total_blocks,
    )

    # ========================================================
    # TEST 3 — CONVERT TO DOCUMENT PAGES
    # ========================================================

    print("\nTEST 3 — DOCUMENT PAGE CONVERSION")

    pages: list[DocumentPage] = []

    for page_text in page_texts:

        page = DocumentPage(
            page_number=page_text.page_number,
            width=page_text.width,
            height=page_text.height,
            blocks=page_text.blocks,
            text="\n".join(
                block.text
                for block in page_text.blocks
            ),
        )

        pages.append(page)

    check(
        len(pages) == 16,
        "DocumentPage objects created",
        len(pages),
    )

    check(
        all(
            page.page_number == index
            for index, page
            in enumerate(pages, start=1)
        ),
        "Page numbering is sequential",
    )

    # ========================================================
    # TEST 4 — TABLE EXTRACTION
    # ========================================================

    print("\nTEST 4 — TABLE EXTRACTION")

    tables = extract_document_tables(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    check(
        len(tables) > 0,
        "Tables extracted",
        len(tables),
    )

    # ========================================================
    # TEST 5 — IMAGE EXTRACTION
    # ========================================================

    print("\nTEST 5 — IMAGE EXTRACTION")

    images = extract_images_from_pdf(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    check(
        len(images) == 19,
        "Expected image count",
        len(images),
    )

    check(
        all(
            image.image_id
            for image in images
        ),
        "All images have IDs",
    )

    check(
        len({
            image.image_id
            for image in images
        }) == len(images),
        "Image IDs are unique",
    )

    # ========================================================
    # TEST 6 — BUILD STRUCTURED DOCUMENT
    # ========================================================

    print("\nTEST 6 — STRUCTURED DOCUMENT")

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pages=pages,
        tables=tables,
        images=images,
    )

    check(
        document is not None,
        "StructuredDocument created",
    )

    check(
        document.document_id == DOCUMENT_ID,
        "Document ID preserved",
        document.document_id,
    )

    # ========================================================
    # TEST 7 — TEXT INTEGRATION
    # ========================================================

    print("\nTEST 7 — TEXT INTEGRATION")

    check(
        document.page_count == 16,
        "All pages integrated",
        document.page_count,
    )

    check(
        sum(
            len(page.blocks)
            for page in document.pages
        ) > 0,
        "Text blocks preserved",
    )

    # ========================================================
    # TEST 8 — TABLE INTEGRATION
    # ========================================================

    print("\nTEST 8 — TABLE INTEGRATION")

    check(
        document.table_count == len(tables),
        "All tables integrated",
        document.table_count,
    )

    # ========================================================
    # TEST 9 — IMAGE INTEGRATION
    # ========================================================

    print("\nTEST 9 — IMAGE INTEGRATION")

    check(
        len(document.images) == 19,
        "All images integrated",
        len(document.images),
    )

    check(
        document.image_count == 19,
        "Image count property is correct",
        document.image_count,
    )

    check(
        document.has_images,
        "Document reports images",
    )

    # ========================================================
    # TEST 10 — PAGE → IMAGE REFERENCES
    # ========================================================

    print("\nTEST 10 — PAGE → IMAGE REFERENCES")

    referenced_image_ids = [
        image_id
        for page in document.pages
        for image_id in page.image_ids
    ]

    check(
        len(referenced_image_ids) == 19,
        "All images referenced by pages",
        len(referenced_image_ids),
    )

    check(
        set(referenced_image_ids)
        == {
            image.image_id
            for image in document.images
        },
        "Page image references match document images",
    )

    # ========================================================
    # TEST 11 — IMAGE → PAGE REFERENCES
    # ========================================================

    print("\nTEST 11 — IMAGE → PAGE REFERENCES")

    page_map = {
        page.page_number: page
        for page in document.pages
    }

    image_reference_errors = []

    for image in document.images:

        page = page_map.get(
            image.page_number
        )

        if page is None:

            image_reference_errors.append(
                f"{image.image_id}: missing page"
            )

            continue

        if image.image_id not in page.image_ids:

            image_reference_errors.append(
                f"{image.image_id}: "
                f"not referenced by page "
                f"{image.page_number}"
            )

    check(
        not image_reference_errors,
        "All images point to their correct pages",
        image_reference_errors
        if image_reference_errors
        else None,
    )

    # ========================================================
    # TEST 12 — IMAGE FILES
    # ========================================================

    print("\nTEST 12 — IMAGE FILES")

    missing_files = []

    for image in document.images:

        image_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / DOCUMENT_ID
            / image.image_path
        )

        if not image_file.exists():

            missing_files.append(
                str(image_file)
            )

    check(
        not missing_files,
        "All extracted image files exist",
        missing_files
        if missing_files
        else None,
    )

    # ========================================================
    # TEST 13 — SERIALIZATION
    # ========================================================

    print("\nTEST 13 — SERIALIZATION")

    data = document.model_dump(
        mode="json"
    )

    check(
        isinstance(data, dict),
        "StructuredDocument serializes to dictionary",
    )

    check(
        "pages" in data,
        "Serialized document contains pages",
    )

    check(
        "tables" in data,
        "Serialized document contains tables",
    )

    check(
        "images" in data,
        "Serialized document contains images",
    )

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    print("\n" + "=" * 70)

    print(
        "PHASE 3.1.12.5 RESULTS"
    )

    print("=" * 70)

    print(
        f"\nChecks passed: {passed}"
    )

    print(
        f"Checks failed: {failed}"
    )

    if failed == 0:

        print(
            "\nALL TESTS PASSED"
        )

    else:

        print(
            "\nTESTS FAILED"
        )

        raise SystemExit(1)


if __name__ == "__main__":
    main()