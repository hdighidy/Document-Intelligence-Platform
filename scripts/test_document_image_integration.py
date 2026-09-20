"""
Phase 3.1.12.4
DocumentStructurer Image Integration Test
"""

from __future__ import annotations

from pathlib import Path

from app.extraction.document_structurer import (
    build_structured_document,
)
from app.extraction.image_extractor import (
    extract_images_from_pdf,
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

DOCUMENT_ID = "DOC-IMAGE-INTEGRATION-001"


passed = 0
failed = 0


def check(
    name: str,
    condition: bool,
    details: str = "",
) -> None:

    global passed, failed

    if condition:

        passed += 1
        print(f"[PASS] {name}")

        if details:
            print(f"       {details}")

    else:

        failed += 1
        print(f"[FAIL] {name}")

        if details:
            print(f"       {details}")


def section(title: str) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.12.4 — "
        "DOCUMENTSTRUCTURER IMAGE INTEGRATION"
    )
    print("=" * 70)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"PDF: {PDF_PATH}")

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    section("TEST 1 — INPUT")

    check(
        "Sample PDF exists",
        PDF_PATH.exists(),
        str(PDF_PATH),
    )

    check(
        "Sample PDF is a file",
        PDF_PATH.is_file(),
    )

    if not PDF_PATH.exists():
        print()
        print("ERROR: sample PDF not found.")
        return

    # ========================================================
    # TEST 2 — IMAGE EXTRACTION
    # ========================================================

    section("TEST 2 — IMAGE EXTRACTION")

    images = extract_images_from_pdf(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    # ========================================================
    # Extract text pages for document integration
    # ========================================================

    page_texts = extract_text_from_pdf(
        PDF_PATH
    )

    pages = []

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
        "Images extracted",
        len(images) > 0,
        str(len(images)),
    )

    check(
        "Expected image count",
        len(images) == 19,
        str(len(images)),
    )

    # ========================================================
    # TEST 3 — IMAGE MODEL
    # ========================================================

    section("TEST 3 — IMAGE MODEL")

    if images:

        first_image = images[0]

        check(
            "Image ID exists",
            bool(first_image.image_id),
            first_image.image_id,
        )

        check(
            "Page number exists",
            first_image.page_number > 0,
            str(first_image.page_number),
        )

        check(
            "Image format exists",
            bool(first_image.image_format),
            first_image.image_format,
        )

        check(
            "Image path exists",
            bool(first_image.image_path),
            first_image.image_path,
        )

        check(
            "Source XREF exists",
            first_image.source_xref is not None,
            str(first_image.source_xref),
        )

    # ========================================================
    # TEST 4 — DOCUMENT STRUCTURER
    # ========================================================

    section("TEST 4 — DOCUMENT STRUCTURER")

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pdf_path=PDF_PATH,
        pages=pages,
        images=images,
    )

    check(
        "StructuredDocument created",
        document is not None,
    )

    # ========================================================
    # TEST 5 — DOCUMENT IMAGE COLLECTION
    # ========================================================

    section("TEST 5 — DOCUMENT IMAGE COLLECTION")

    check(
        "Document has images attribute",
        hasattr(document, "images"),
    )

    if hasattr(document, "images"):

        check(
            "Document image count > 0",
            len(document.images) > 0,
            str(len(document.images)),
        )

        check(
            "Document image count = extracted count",
            len(document.images) == len(images),
            f"{len(document.images)}/{len(images)}",
        )

    # ========================================================
    # TEST 6 — PAGE IMAGE REFERENCES
    # ========================================================

    section("TEST 6 — PAGE IMAGE REFERENCES")

    pages_with_images = [
        page for page in document.pages
        if getattr(page, "image_ids", [])
    ]

    check(
        "Pages contain image references",
        len(pages_with_images) > 0,
        str(len(pages_with_images)),
    )

    referenced_image_ids = []

    for page in document.pages:

        referenced_image_ids.extend(
            getattr(
                page,
                "image_ids",
                [],
            )
        )

    check(
        "Page image references exist",
        len(referenced_image_ids) > 0,
        str(len(referenced_image_ids)),
    )

    # ========================================================
    # TEST 7 — REFERENCE INTEGRITY
    # ========================================================

    section("TEST 7 — IMAGE REFERENCE INTEGRITY")

    document_image_ids = {
        image.image_id
        for image in document.images
    }

    orphan_references = [
        image_id
        for image_id in referenced_image_ids
        if image_id not in document_image_ids
    ]

    check(
        "No orphan image references",
        len(orphan_references) == 0,
        str(orphan_references),
    )

    # ========================================================
    # TEST 8 — IMAGE FILES
    # ========================================================

    section("TEST 8 — IMAGE FILES")

    existing_files = 0

    for image in document.images:

        image_path = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / DOCUMENT_ID
            / image.image_path
        )

        if image_path.exists():

            existing_files += 1

    check(
        "All extracted image files exist",
        existing_files == len(document.images),
        f"{existing_files}/{len(document.images)}",
    )

    # ========================================================
    # TEST 9 — SERIALIZATION
    # ========================================================

    section("TEST 9 — SERIALIZATION")

    dumped = document.model_dump()

    check(
        "StructuredDocument model_dump works",
        isinstance(dumped, dict),
    )

    check(
        "Images serialized",
        "images" in dumped,
    )

    if "images" in dumped:

        check(
            "Serialized image count",
            len(dumped["images"])
            == len(document.images),
            str(len(dumped["images"])),
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    section("PHASE 3.1.12.4 RESULTS")

    print(
        f"Checks passed: {passed}"
    )

    print(
        f"Checks failed: {failed}"
    )

    print()

    if failed == 0:

        print(
            "ALL TESTS PASSED"
        )

    else:

        print(
            f"FAIL — {failed} checks failed."
        )


if __name__ == "__main__":
    main()