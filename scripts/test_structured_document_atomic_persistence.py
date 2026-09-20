"""
Phase 3.1.14.4
Atomic Persistence & Safe-Write Protection
"""

from __future__ import annotations

import json
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
    save_structured_document,
    load_structured_document,
)


DOCUMENT_ID = "PHASE-3-1-14-4"

PDF_PATH = Path(
    "data/test/sample.pdf"
)


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.14.4 — "
        "ATOMIC PERSISTENCE & SAFE-WRITE PROTECTION"
    )
    print("=" * 70)

    # ========================================================
    # TEST 1 — INPUT
    # ========================================================

    print("\nTEST 1 — INPUT")

    assert PDF_PATH.exists()
    print("[PASS] Sample PDF exists")

    assert PDF_PATH.is_file()
    print("[PASS] Sample PDF is a file")

    # ========================================================
    # TEST 2 — EXTRACTION
    # ========================================================

    print("\nTEST 2 — EXTRACTION")

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
        document_id=DOCUMENT_ID,
    )

    print(
        f"[PASS] Pages extracted: "
        f"{len(pages)}"
    )

    print(
        f"[PASS] Images extracted: "
        f"{len(images)}"
    )

    # ========================================================
    # TEST 3 — BUILD CANONICAL DOCUMENT
    # ========================================================

    print(
        "\nTEST 3 — BUILD CANONICAL DOCUMENT"
    )

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pages=pages,
        images=images,
    )

    assert document.document_id == DOCUMENT_ID

    print(
        "[PASS] Canonical document created"
    )

    # ========================================================
    # TEST 4 — ATOMIC SAVE
    # ========================================================

    print(
        "\nTEST 4 — ATOMIC SAVE"
    )

    output_file = save_structured_document(
        document
    )

    assert output_file.exists()

    print(
        "[PASS] Structured document persisted"
    )

    # ========================================================
    # TEST 5 — VALID JSON
    # ========================================================

    print(
        "\nTEST 5 — VALID JSON"
    )

    raw_text = output_file.read_text(
        encoding="utf-8"
    )

    data = json.loads(
        raw_text
    )

    assert isinstance(
        data,
        dict,
    )

    print(
        "[PASS] Persisted file contains valid JSON"
    )

    # ========================================================
    # TEST 6 — CANONICAL RELOAD
    # ========================================================

    print(
        "\nTEST 6 — CANONICAL RELOAD"
    )

    loaded = load_structured_document(
        DOCUMENT_ID
    )

    assert (
        loaded.model_dump(
            mode="json"
        )
        ==
        document.model_dump(
            mode="json"
        )
    )

    print(
        "[PASS] Canonical document reload preserved"
    )

    # ========================================================
    # TEST 7 — NO TEMPORARY FILES REMAIN
    # ========================================================

    print(
        "\nTEST 7 — TEMPORARY FILE CLEANUP"
    )

    temp_files = list(
        output_file.parent.glob(
            f".{output_file.stem}.*.tmp"
        )
    )

    assert temp_files == []

    print(
        "[PASS] No temporary persistence files remain"
    )

    # ========================================================
    # TEST 8 — REPEATED ATOMIC SAVE
    # ========================================================

    print(
        "\nTEST 8 — REPEATED ATOMIC SAVE"
    )

    for _ in range(5):

        saved = save_structured_document(
            document
        )

        assert saved.exists()

    loaded_again = load_structured_document(
        DOCUMENT_ID
    )

    assert (
        loaded_again.model_dump(
            mode="json"
        )
        ==
        document.model_dump(
            mode="json"
        )
    )

    print(
        "[PASS] Repeated atomic saves preserved integrity"
    )

    # ========================================================
    # TEST 9 — FINAL TEMPORARY FILE CHECK
    # ========================================================

    print(
        "\nTEST 9 — FINAL TEMPORARY FILE CHECK"
    )

    temp_files = list(
        output_file.parent.glob(
            f".{output_file.stem}.*.tmp"
        )
    )

    assert temp_files == []

    print(
        "[PASS] No orphan temporary files detected"
    )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print(
        "PHASE 3.1.14.4 RESULTS"
    )
    print("=" * 70)

    print(
        "Checks passed: 9"
    )

    print(
        "Checks failed: 0"
    )

    print(
        "\nALL TESTS PASSED"
    )


if __name__ == "__main__":
    main()