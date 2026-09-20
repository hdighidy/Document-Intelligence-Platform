"""
Phase 3.1.14.3
============================================================

Persistence Failure / Recovery / Corruption Handling

Objectives
----------
1. Verify missing persistence is detected.
2. Verify malformed JSON is detected.
3. Verify empty JSON is detected.
4. Verify structurally invalid JSON is rejected.
5. Verify corrupted tables are rejected.
6. Verify corrupted images are rejected.
7. Verify corrupted pages are rejected.
8. Verify truncated JSON is rejected.
9. Verify failed loads do not silently recreate data.
10. Verify the original valid document remains recoverable.
11. Verify valid persistence still works after corruption tests.
12. Verify canonical equality after recovery.

This phase does NOT silently repair corrupted data.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from app.config import settings
from app.models.document import DocumentPage

from pydantic import ValidationError

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
from app.storage.structured_document_storage import (
    load_structured_document,
    save_structured_document,
)



# ============================================================
# CONFIGURATION
# ============================================================

DOCUMENT_ID = "TEST-3-1-14-3"

PDF_PATH = (
    Path("data")
    / "test"
    / "sample.pdf"
)

DOCUMENT_DIR = (
    settings.processed_dir
    / DOCUMENT_ID
)

STRUCTURED_FILE = (
    DOCUMENT_DIR
    / "structured_document.json"
)


# ============================================================
# TEST HELPERS
# ============================================================

checks_passed = 0
checks_failed = 0


def check(
    condition: bool,
    message: str,
) -> None:

    global checks_passed
    global checks_failed

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


def restore_json(
    data: dict,
) -> None:

    STRUCTURED_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def read_json() -> dict:

    return json.loads(
        STRUCTURED_FILE.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    global checks_passed
    global checks_failed

    print("=" * 70)
    print(
        "PHASE 3.1.14.3 — "
        "PERSISTENCE FAILURE / RECOVERY / CORRUPTION"
    )
    print("=" * 70)

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

    # ========================================================
    # CLEAN TEST STORAGE
    # ========================================================

    if DOCUMENT_DIR.exists():

        import shutil

        shutil.rmtree(
            DOCUMENT_DIR
        )

    # ========================================================
    # BUILD CANONICAL DOCUMENT
    # ========================================================

    print(
        "\nBUILDING CANONICAL DOCUMENT"
    )

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

    

    document = build_structured_document(
        document_id=DOCUMENT_ID,
        pages=pages,
        images=images,
       
    )

    

    check(
        document is not None,
        "Canonical document created",
    )

    # ========================================================
    # SAVE VALID DOCUMENT
    # ========================================================

    print(
        "\nTEST 2 — VALID PERSISTENCE"
    )

    persisted_path = (
        save_structured_document(
            document
        )
    )

    check(
        persisted_path.exists(),
        "Structured document persisted",
    )

    check(
        persisted_path == STRUCTURED_FILE,
        "Expected persistence path used",
    )

    original_data = (
        document.model_dump(
            mode="json"
        )
    )

    print(original_data["tables"])

    # Keep a pristine copy for recovery tests.

    pristine_data = copy.deepcopy(
        original_data
    )

    print(pristine_data["tables"])
    print(original_data["tables"])

    # ========================================================
    # TEST 3 — VALID RELOAD
    # ========================================================

    print(
        "\nTEST 3 — VALID RELOAD"
    )

    loaded = (
        load_structured_document(
            DOCUMENT_ID
        )
    )

    check(
        loaded is not None,
        "Valid document reload succeeds",
    )

    check(
        loaded.model_dump(
            mode="json"
        )
        == pristine_data,
        "Valid document survives round-trip",
    )

    # ========================================================
    # TEST 4 — MISSING FILE
    # ========================================================

    print(
        "\nTEST 4 — MISSING FILE"
    )

    backup_path = (
        DOCUMENT_DIR
        / "structured_document.backup.json"
    )

    STRUCTURED_FILE.rename(
        backup_path
    )

    try:

        missing_detected = False

        try:

            load_structured_document(
                DOCUMENT_ID
            )

        except FileNotFoundError:

            missing_detected = True

        check(
            missing_detected,
            "Missing structured document detected",
        )

    finally:

        backup_path.rename(
            STRUCTURED_FILE
        )

    # ========================================================
    # TEST 5 — EMPTY FILE
    # ========================================================

    print(
        "\nTEST 5 — EMPTY FILE"
    )

    STRUCTURED_FILE.write_text(
        "",
        encoding="utf-8",
    )

    empty_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except json.JSONDecodeError:

        empty_detected = True

    check(
        empty_detected,
        "Empty JSON file detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 6 — MALFORMED JSON
    # ========================================================

    print(
        "\nTEST 6 — MALFORMED JSON"
    )

    STRUCTURED_FILE.write_text(
        '{"document_id": "BROKEN"',
        encoding="utf-8",
    )

    malformed_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except json.JSONDecodeError:

        malformed_detected = True

    check(
        malformed_detected,
        "Malformed JSON detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 7 — TRUNCATED JSON
    # ========================================================

    print(
        "\nTEST 7 — TRUNCATED JSON"
    )

    valid_json = json.dumps(
        pristine_data,
        indent=4,
        ensure_ascii=False,
    )

    truncated_json = (
        valid_json[
            :len(valid_json) // 2
        ]
    )

    STRUCTURED_FILE.write_text(
        truncated_json,
        encoding="utf-8",
    )

    truncated_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except json.JSONDecodeError:

        truncated_detected = True

    check(
        truncated_detected,
        "Truncated JSON detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 8 — INVALID ROOT STRUCTURE
    # ========================================================

    print(
        "\nTEST 8 — INVALID ROOT STRUCTURE"
    )

    invalid_root = []

    STRUCTURED_FILE.write_text(
        json.dumps(
            invalid_root
        ),
        encoding="utf-8",
    )

    root_validation_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except ValidationError:

        root_validation_detected = True

    except Exception:

        root_validation_detected = True

    check(
        root_validation_detected,
        "Invalid root structure detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 9 — INVALID PAGE
    # ========================================================

    print(
        "\nTEST 9 — CORRUPTED PAGE"
    )

    corrupted_pages = copy.deepcopy(
        pristine_data
    )

    if corrupted_pages["pages"]:

        corrupted_pages["pages"][0][
            "page_number"
        ] = "INVALID_PAGE"

    STRUCTURED_FILE.write_text(
        json.dumps(
            corrupted_pages,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    page_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except ValidationError:

        page_detected = True

    check(
        page_detected,
        "Corrupted page detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 10 — CORRUPTED IMAGE
    # ========================================================

    print(
        "\nTEST 10 — CORRUPTED IMAGE"
    )

    corrupted_images = copy.deepcopy(
        pristine_data
    )

    if corrupted_images["images"]:

        corrupted_images["images"][0][
            "page_number"
        ] = "INVALID_IMAGE_PAGE"

    STRUCTURED_FILE.write_text(
        json.dumps(
            corrupted_images,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    image_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except ValidationError:

        image_detected = True

    check(
        image_detected,
        "Corrupted image detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 11 — CORRUPTED TABLE
    # ========================================================

    print(
        "\nTEST 11 — CORRUPTED TABLE"
    )

    corrupted_tables = copy.deepcopy(
        pristine_data
    )

    # --------------------------------------------------------
    # We intentionally inject a malformed table.
    #
    # This test must verify schema validation independently
    # of whether the original sample PDF contains tables.
    # --------------------------------------------------------

    if corrupted_tables["tables"]:

        corrupted_tables["tables"][0][
            "table_id"
        ] = 123456789

    else:

        corrupted_tables["tables"].append(
            {
                "table_id": 123456789
            }
        )

    STRUCTURED_FILE.write_text(
        json.dumps(
            corrupted_tables,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    table_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except ValidationError:

        table_detected = True

    check(
        table_detected,
        "Corrupted table detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 12 — MISSING DOCUMENT ID
    # ========================================================

    print(
        "\nTEST 12 — INVALID DOCUMENT ID"
    )

    invalid_document = copy.deepcopy(
        pristine_data
    )

    invalid_document[
        "document_id"
    ] = 123456789

    restore_json(
        invalid_document
    )

    document_id_detected = False

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except ValidationError:

        document_id_detected = True

    check(
        document_id_detected,
        "Invalid document ID detected",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 13 — FILE NOT SILENTLY RECREATED
    # ========================================================

    print(
        "\nTEST 13 — NO SILENT RECREATION"
    )

    STRUCTURED_FILE.write_text(
        '{"broken": true}',
        encoding="utf-8",
    )

    try:

        load_structured_document(
            DOCUMENT_ID
        )

    except Exception:

        pass

    current_data = (
        read_json()
    )

    check(
        current_data
        == {"broken": True},
        "Failed load does not silently rewrite file",
    )

    restore_json(
        pristine_data
    )

    # ========================================================
    # TEST 14 — RECOVERY
    # ========================================================

    print(
        "\nTEST 14 — RECOVERY"
    )

    recovered = (
        load_structured_document(
            DOCUMENT_ID
        )
    )

    check(
        recovered is not None,
        "Valid document recovered after corruption tests",
    )

    recovered_data = (
        recovered.model_dump(
            mode="json"
        )
    )

    check(
        recovered_data
        == pristine_data,
        "Recovered document equals pristine canonical document",
    )

    # ========================================================
    # TEST 15 — FINAL VALIDITY
    # ========================================================

    print(
        "\nTEST 15 — FINAL VALIDITY"
    )

    final_file_data = read_json()

    check(
        final_file_data
        == pristine_data,
        "Persistence file restored to canonical state",
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)

    print(
        "PHASE 3.1.14.3 RESULTS"
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