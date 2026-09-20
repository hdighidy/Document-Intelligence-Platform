"""
Phase 3.1.14.5
Persistence Concurrency & Overwrite Integrity
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.config import settings
from app.extraction.document_structurer import (
    build_structured_document,
)
from app.extraction.image_extractor import (
    extract_images_from_pdf,
)
from app.extraction.text_extractor import (
    extract_text_from_pdf,
)
from app.models.document import DocumentPage
from app.storage.structured_document_storage import (
    load_structured_document,
    save_structured_document,
)


DOCUMENT_ID = "PHASE-3-1-14-5"

PDF_PATH = Path(
    "data/test/sample.pdf"
)


def build_document(
    document_id: str,
):
    page_texts = extract_text_from_pdf(
        PDF_PATH
    )

    pages = [
        DocumentPage(
            page_number=page.page_number,
            width=page.width,
            height=page.height,
            blocks=page.blocks,
        )
        for page in page_texts
    ]

    images = extract_images_from_pdf(
        pdf_path=PDF_PATH,
        document_id=document_id,
    )

    return build_structured_document(
        document_id=document_id,
        pages=pages,
        images=images,
    )


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.14.5 — "
        "PERSISTENCE CONCURRENCY & OVERWRITE INTEGRITY"
    )
    print("=" * 70)

    checks_passed = 0
    checks_failed = 0

    def check(
        condition: bool,
        message: str,
    ) -> None:

        nonlocal checks_passed
        nonlocal checks_failed

        if condition:

            checks_passed += 1
            print(
                f"[PASS] {message}"
            )

        else:

            checks_failed += 1
            print(
                f"[FAIL] {message}"
            )

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    print("\nTEST 1 — INPUT")

    check(
        PDF_PATH.exists(),
        "Sample PDF exists",
    )

    check(
        PDF_PATH.is_file(),
        "Sample PDF is a file",
    )

    if (
        not PDF_PATH.exists()
        or not PDF_PATH.is_file()
    ):
        raise FileNotFoundError(
            PDF_PATH
        )

    # ========================================================
    # TEST 2 — BUILD BASE DOCUMENT
    # ========================================================

    print(
        "\nTEST 2 — BUILD BASE DOCUMENT"
    )

    document = build_document(
        DOCUMENT_ID
    )

    check(
        document.document_id
        == DOCUMENT_ID,
        "Canonical document created",
    )

    check(
        len(document.pages) == 16,
        "Expected page count preserved",
    )

    check(
        len(document.images) == 19,
        "Expected image count preserved",
    )

    # ========================================================
    # TEST 3 — INITIAL SAVE
    # ========================================================

    print(
        "\nTEST 3 — INITIAL SAVE"
    )

    output_file = save_structured_document(
        document
    )

    check(
        output_file.exists(),
        "Initial structured document persisted",
    )

    # ========================================================
    # TEST 4 — BASELINE RELOAD
    # ========================================================

    print(
        "\nTEST 4 — BASELINE RELOAD"
    )

    baseline = load_structured_document(
        DOCUMENT_ID
    )

    baseline_data = baseline.model_dump(
        mode="json"
    )

    original_data = document.model_dump(
        mode="json"
    )

    check(
        baseline_data == original_data,
        "Baseline canonical equality preserved",
    )

    # ========================================================
    # TEST 5 — CONCURRENT OVERWRITE
    # ========================================================

    print(
        "\nTEST 5 — CONCURRENT OVERWRITE"
    )

    documents = [
        build_document(
            DOCUMENT_ID
        )
        for _ in range(8)
    ]

    def save_worker(
        index: int,
    ) -> str:

        saved = save_structured_document(
            documents[index]
        )

        return str(saved)

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:

        results = list(
            executor.map(
                save_worker,
                range(len(documents)),
            )
        )

    check(
        len(results) == 8,
        "All concurrent save operations completed",
    )

    check(
        all(
            Path(path).exists()
            for path in results
        ),
        "All concurrent saves targeted a valid destination",
    )

    # ========================================================
    # TEST 6 — FINAL JSON VALIDITY
    # ========================================================

    print(
        "\nTEST 6 — FINAL JSON VALIDITY"
    )

    try:

        raw_data = json.loads(
            output_file.read_text(
                encoding="utf-8"
            )
        )

        json_valid = True

    except (
        json.JSONDecodeError,
        OSError,
    ):

        raw_data = None
        json_valid = False

    check(
        json_valid,
        "Final persisted file contains valid JSON",
    )

    check(
        isinstance(
            raw_data,
            dict,
        ),
        "Final persisted JSON is an object",
    )

    # ========================================================
    # TEST 7 — FINAL CANONICAL RELOAD
    # ========================================================

    print(
        "\nTEST 7 — FINAL CANONICAL RELOAD"
    )

    try:

        final_document = load_structured_document(
            DOCUMENT_ID
        )

        reload_success = True

    except Exception as exc:

        print(
            f"Reload error: {exc}"
        )

        final_document = None
        reload_success = False

    check(
        reload_success,
        "Final persisted document can be reloaded",
    )

    # ========================================================
    # TEST 8 — STRUCTURAL INTEGRITY
    # ========================================================

    print(
        "\nTEST 8 — STRUCTURAL INTEGRITY"
    )

    if final_document is not None:

        check(
            len(final_document.pages) == 16,
            "Final page structure preserved",
        )

        check(
            len(final_document.images) == 19,
            "Final image structure preserved",
        )

        check(
            all(
                image.image_id
                in {
                    image_ref.image_id
                    for page in final_document.pages
                    for image_ref in final_document.images
                    if image_ref.page_number
                    == page.page_number
                }
                for image in final_document.images
            ),
            "Image relationships remain structurally valid",
        )

    # ========================================================
    # TEST 9 — CANONICAL DOCUMENT INTEGRITY
    # ========================================================

    print(
        "\nTEST 9 — CANONICAL DOCUMENT INTEGRITY"
    )

    if final_document is not None:

        final_data = final_document.model_dump(
            mode="json"
        )

        required_keys = {
            "document_id",
            "metadata",
            "pages",
            "tables",
            "images",
            "table_references",
            "processing",
            "extra_metadata",
        }

        check(
            set(final_data)
            == required_keys,
            "Canonical top-level structure preserved",
        )

        check(
            final_data["document_id"]
            == DOCUMENT_ID,
            "Document identity preserved",
        )

    # ========================================================
    # TEST 10 — NO TEMPORARY FILES
    # ========================================================

    print(
        "\nTEST 10 — TEMPORARY FILE CLEANUP"
    )

    temporary_files = list(
        output_file.parent.glob(
            f".{output_file.stem}.*.tmp"
        )
    )

    check(
        temporary_files == [],
        "No orphan temporary files remain",
    )

    # ========================================================
    # TEST 11 — SEQUENTIAL OVERWRITE
    # ========================================================

    print(
        "\nTEST 11 — SEQUENTIAL OVERWRITE"
    )

    sequential_success = True

    try:

        for _ in range(10):

            save_structured_document(
                document
            )

            reloaded = (
                load_structured_document(
                    DOCUMENT_ID
                )
            )

            if (
                reloaded.model_dump(
                    mode="json"
                )
                != original_data
            ):

                sequential_success = False
                break

    except Exception as exc:

        print(
            f"Sequential overwrite error: {exc}"
        )

        sequential_success = False

    check(
        sequential_success,
        "Repeated overwrite preserves canonical equality",
    )

    # ========================================================
    # TEST 12 — FINAL TEMP FILE CHECK
    # ========================================================

    print(
        "\nTEST 12 — FINAL TEMPORARY FILE CHECK"
    )

    temporary_files = list(
        output_file.parent.glob(
            f".{output_file.stem}.*.tmp"
        )
    )

    check(
        temporary_files == [],
        "Final storage directory contains no temporary files",
    )

    # ========================================================
    # RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print(
        "PHASE 3.1.14.5 RESULTS"
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