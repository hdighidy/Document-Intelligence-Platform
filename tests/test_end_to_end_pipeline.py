"""
Phase 3.1.11
End-to-End Document Structured Pipeline Test
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path

from app.extraction.end_to_end_pipeline import (
    PIPELINE_VERSION,
    run_end_to_end_pipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)


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

    global passed, failed

    print("=" * 70)
    print(
        "PHASE 3.1.11 — "
        "END-TO-END DOCUMENT STRUCTURED PIPELINE"
    )
    print("=" * 70)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"PDF: {PDF_PATH}")
    print(f"Pipeline version: {PIPELINE_VERSION}")

    try:

        # =====================================================
        # TEST 1 — INPUT
        # =====================================================

        section("TEST 1 — INPUT VALIDATION")

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
            raise RuntimeError(
                f"Sample PDF not found: {PDF_PATH}"
            )

        # =====================================================
        # RUN PIPELINE
        # =====================================================

        print()
        print(
            "Running complete end-to-end pipeline..."
        )

        result = run_end_to_end_pipeline(
            PDF_PATH,
            document_id="DOC-E2E-3.1.11-001",
        )

        # =====================================================
        # TEST 2 — PIPELINE RESULT
        # =====================================================

        section("TEST 2 — PIPELINE RESULT")

        check(
            "Pipeline result created",
            result is not None,
        )

        check(
            "Document ID",
            result.document_id
            == "DOC-E2E-3.1.11-001",
        )

        check(
            "Pipeline version",
            result.pipeline_version
            == PIPELINE_VERSION,
        )

        check(
            "Canonical generator version",
            bool(
                result.canonical_generator_version
            ),
            result.canonical_generator_version,
        )

        # =====================================================
        # TEST 3 — DETECTION
        # =====================================================

        section("TEST 3 — TABLE DETECTION")

        check(
            "Tables detected",
            result.statistics.tables_detected > 0,
            str(
                result.statistics.tables_detected
            ),
        )

        # =====================================================
        # TEST 4 — EXTRACTION
        # =====================================================

        section("TEST 4 — TABLE EXTRACTION")

        check(
            "Tables extracted",
            result.statistics.tables_extracted > 0,
            str(
                result.statistics.tables_extracted
            ),
        )

        check(
            "Extracted <= detected",
            result.statistics.tables_extracted
            <= result.statistics.tables_detected,
        )

        # =====================================================
        # TEST 5 — PROCESSING
        # =====================================================

        section("TEST 5 — TABLE PROCESSING")

        check(
            "Tables cleaned",
            result.statistics.tables_cleaned
            == result.statistics.tables_extracted,
        )

        check(
            "Structure analysis executed",
            result.statistics.tables_structure_analyzed
            == result.statistics.tables_extracted,
        )

        check(
            "Quality scoring executed",
            result.statistics.tables_quality_scored
            == result.statistics.tables_extracted,
        )

        check(
            "Validation executed",
            result.statistics.tables_validated
            == result.statistics.tables_extracted,
        )

        # =====================================================
        # TEST 6 — CANONICAL
        # =====================================================

        section("TEST 6 — CANONICAL GENERATION")

        check(
            "Canonical tables generated",
            result.statistics.tables_canonical_generated
            == result.statistics.tables_extracted,
            str(
                result.statistics.tables_canonical_generated
            ),
        )

        # =====================================================
        # TEST 7 — DOCUMENT
        # =====================================================

        section(
            "TEST 7 — STRUCTURED DOCUMENT INTEGRATION"
        )

        document = result.document

        check(
            "StructuredDocument created",
            document is not None,
        )

        if document is not None:

            check(
                "Document ID propagated",
                document.document_id
                == result.document_id,
            )

            check(
                "Document metadata exists",
                document.metadata is not None,
            )

            check(
                "Document tables exist",
                hasattr(document, "tables"),
            )

            check(
                "Document table references exist",
                hasattr(
                    document,
                    "table_references",
                ),
            )

            check(
                "Document processing result exists",
                hasattr(
                    document,
                    "processing_result",
                ),
            )

        # =====================================================
        # TEST 8 — TABLE INTEGRITY
        # =====================================================

        section("TEST 8 — TABLE INTEGRITY")

        if document is not None:

            tables = getattr(
                document,
                "tables",
                [],
            )

            check(
                "Structured tables count > 0",
                len(tables) > 0,
                str(len(tables)),
            )

            canonical_count = 0

            for table in tables:

                canonical = getattr(
                    table,
                    "canonical_table",
                    None,
                )

                if canonical is not None:

                    canonical_count += 1

            check(
                "Canonical table attachments",
                canonical_count
                == len(tables),
                f"{canonical_count}/{len(tables)}",
            )

        # =====================================================
        # TEST 9 — PROCESSING STATISTICS
        # =====================================================

        section("TEST 9 — PROCESSING STATISTICS")

        statistics = result.statistics

        check(
            "Processing time available",
            statistics.processing_time_seconds
            is not None,
        )

        check(
            "Processing time non-negative",
            (
                statistics.processing_time_seconds
                is not None
                and statistics.processing_time_seconds >= 0
            ),
        )

        check(
            "Started timestamp",
            result.started_at is not None,
        )

        check(
            "Completed timestamp",
            result.completed_at is not None,
        )

        # =====================================================
        # TEST 10 — STATUS
        # =====================================================

        section("TEST 10 — FINAL STATUS")

        check(
            "Pipeline completed",
            result.status == "COMPLETED",
            result.status,
        )

        check(
            "No pipeline errors",
            len(statistics.errors) == 0,
            str(statistics.errors),
        )

        # =====================================================
        # TEST 11 — SERIALIZATION
        # =====================================================

        section("TEST 11 — SERIALIZATION")

        if document is not None:

            dumped = document.model_dump()

            check(
                "model_dump() works",
                isinstance(dumped, dict),
            )

            check(
                "Serialized document ID",
                dumped.get("document_id")
                == result.document_id,
            )

            json_text = document.model_dump_json()

            check(
                "JSON serialization works",
                bool(json_text),
            )

            check(
                "JSON contains document ID",
                result.document_id
                in json_text,
            )

            # Ensure it is actually valid JSON.
            parsed = json.loads(json_text)

            check(
                "JSON is valid",
                isinstance(parsed, dict),
            )

    except Exception as exc:

        failed += 1

        print()
        print(
            "ERROR during Phase 3.1.11:"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

    # =========================================================
    # FINAL RESULT
    # =========================================================

    section("PHASE 3.1.11 RESULTS")

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

        print(
            "Please review the output above."
        )


if __name__ == "__main__":
    main()