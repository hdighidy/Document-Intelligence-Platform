"""
Phase 3.1.10.2
Document Integration Service Test

Run:
    python -m scripts.test_document_structurer
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import traceback


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from app.models.document import (
    DocumentMetadata,
    DocumentPage,
    DocumentProcessingStatus,
    StructuredDocument,
)

from app.models.table import (
    SchemaMappingStatus,
    Table,
    TableValidationStatus,
)

from app.extraction.document_structurer import (
    DOCUMENT_STRUCTURER_VERSION,
    DocumentStructurer,
    build_structured_document,
)


# ============================================================
# TEST HELPERS
# ============================================================

passed = 0
failed = 0


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> None:

    global passed
    global failed

    if condition:

        passed += 1

        print(
            f"[PASS] {name}"
        )

        if detail:
            print(
                f"       {detail}"
            )

    else:

        failed += 1

        print(
            f"[FAIL] {name}"
        )

        if detail:
            print(
                f"       {detail}"
            )


def section(title: str) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# SAMPLE TABLE
# ============================================================

def create_sample_table(
    table_id: str,
    table_index: int,
) -> Table:

    table = Table(
        table_id=table_id,

        document_id="DOC-TEST-001",

        table_index=table_index,

        source_filename="sample.pdf",

        page_number=1,

        rows=[
            [
                "Unit Description",
                "Unit Code",
                "Quantity",
            ],
            [
                "Air Handling Unit",
                "AHU-B50",
                "2",
            ],
        ],

        headers=[
            "Unit Description",
            "Unit Code",
            "Quantity",
        ],

        row_count=2,

        column_count=3,

        data_rows=[
            [
                "Air Handling Unit",
                "AHU-B50",
                "2",
            ]
        ],

        title="Material Delivery",

        title_row_index=0,

        header_row_index=0,

        data_start_row_index=1,

        data_end_row_index=1,

        structure_confidence=0.95,

        structure_type="STANDARD_TABLE",

        has_header=True,

        has_title=True,

        has_data_rows=True,

        cleaning_applied=True,

        extraction_method="pdfplumber",

        extraction_confidence=0.98,

        quality_score=0.96,

        confidence_score=0.95,

        schema_mapping_status=(
            SchemaMappingStatus.COMPLETE
        ),

        schema_mapping_confidence=0.94,

        validation_status=(
            TableValidationStatus.VALID
        ),

        validation_score=0.99,
    )

    return table


# ============================================================
# TEST 1 — IMPORTS
# ============================================================

def test_imports() -> None:

    section(
        "TEST 1 — MODULE IMPORTS"
    )

    check(
        "DocumentStructurer import",
        DocumentStructurer is not None,
    )

    check(
        "build_structured_document import",
        build_structured_document is not None,
    )

    check(
        "Document models import",
        StructuredDocument is not None,
    )

    check(
        "Pipeline version",
        DOCUMENT_STRUCTURER_VERSION
        == "3.1.10.2",
    )


# ============================================================
# TEST 2 — METADATA
# ============================================================

def test_metadata() -> DocumentMetadata:

    section(
        "TEST 2 — DOCUMENT METADATA"
    )

    from app.models.document import (
        PDFMetadata,
        ProcessingStatus,
    )

    metadata = DocumentMetadata(
        # ----------------------------------------------------
        # Identity
        # ----------------------------------------------------

        document_id="DOC-TEST-001",

        filename="sample.pdf",

        original_filename="sample.pdf",

        stored_filename="sample_test_001.pdf",

        # ----------------------------------------------------
        # File information
        # ----------------------------------------------------

        file_path=(
            "data/test/sample.pdf"
        ),

        file_type="application/pdf",

        mime_type="application/pdf",

        file_size=1024,

        page_count=1,

        # ----------------------------------------------------
        # Hash
        # ----------------------------------------------------

        sha256=(
            "a" * 64
        ),

        # ----------------------------------------------------
        # Dates
        # ----------------------------------------------------

        uploaded_at=datetime.now(),

        created_at=datetime.now(),

        modified_at=datetime.now(),

        # ----------------------------------------------------
        # Source
        # ----------------------------------------------------

        source="Phase 3.1.10.2 test",

        # ----------------------------------------------------
        # Processing status
        # ----------------------------------------------------

        status=ProcessingStatus.UPLOADED,

        # ----------------------------------------------------
        # PDF metadata
        # ----------------------------------------------------

        pdf=PDFMetadata(),

        # ----------------------------------------------------
        # Table count
        # ----------------------------------------------------

        table_count=2,
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    check(
        "Metadata creation",
        metadata is not None,
    )

    check(
        "Document ID",
        metadata.document_id
        == "DOC-TEST-001",
    )

    check(
        "Original filename",
        metadata.original_filename
        == "sample.pdf",
    )

    check(
        "Stored filename",
        metadata.stored_filename
        == "sample_test_001.pdf",
    )

    check(
        "SHA256",
        len(metadata.sha256)
        == 64,
    )

    check(
        "Upload timestamp",
        metadata.uploaded_at is not None,
    )

    check(
        "Processing status",
        metadata.status
        == ProcessingStatus,
    )

    check(
        "PDF metadata",
        metadata.pdf is not None,
    )

    check(
        "Table count",
        metadata.table_count == 2,
    )

    return metadata

# ============================================================
# TEST 3 — PAGES
# ============================================================

def test_pages() -> list[DocumentPage]:

    section(
        "TEST 3 — DOCUMENT PAGES"
    )

    pages = [
        DocumentPage(
            page_number=1,
        ),
        DocumentPage(
            page_number=2,
        ),
    ]

    check(
        "Page objects created",
        len(pages) == 2,
    )

    check(
        "First page number",
        pages[0].page_number == 1,
    )

    check(
        "Second page number",
        pages[1].page_number == 2,
    )

    return pages


# ============================================================
# TEST 4 — TABLES
# ============================================================

def test_tables() -> list[Table]:

    section(
        "TEST 4 — PROCESSED TABLES"
    )

    tables = [
        create_sample_table(
            "TABLE-TEST-001",
            0,
        ),
        create_sample_table(
            "TABLE-TEST-002",
            1,
        ),
    ]

    check(
        "Tables created",
        len(tables) == 2,
    )

    check(
        "Table 1 ID",
        tables[0].table_id
        == "TABLE-TEST-001",
    )

    check(
        "Table 2 ID",
        tables[1].table_id
        == "TABLE-TEST-002",
    )

    check(
        "Table validation status",
        tables[0].validation_status
        == TableValidationStatus.VALID,
    )

    check(
        "Table schema status",
        tables[0].schema_mapping_status
        == SchemaMappingStatus.COMPLETE,
    )

    return tables


# ============================================================
# TEST 5 — BUILD DOCUMENT
# ============================================================

def test_document_build(
    metadata: DocumentMetadata,
    pages: list[DocumentPage],
    tables: list[Table],
) -> StructuredDocument:

    section(
        "TEST 5 — STRUCTURED DOCUMENT BUILD"
    )

    structurer = DocumentStructurer()

    document = structurer.build(
        document_id="DOC-TEST-001",

        metadata=metadata,

        pages=pages,

        tables=tables,

        extra_metadata={
            "project": "DocumentAI",
            "test": True,
        },

        started_at=datetime.now(),
    )

    check(
        "StructuredDocument created",
        document is not None,
    )

    check(
        "Document ID propagated",
        document.document_id
        == "DOC-TEST-001",
    )

    check(
        "Metadata propagated",
        document.metadata is not None,
    )

    check(
        "Pages integrated",
        len(document.pages) == 2,
    )

    check(
        "Tables integrated",
        len(document.tables) == 2,
    )

    check(
        "Table references created",
        len(document.table_references) == 2,
    )

    check(
        "Processing result created",
        document.processing is not None,
    )

    return document


# ============================================================
# TEST 6 — TABLE REFERENCES
# ============================================================

def test_table_references(
    document: StructuredDocument,
) -> None:

    section(
        "TEST 6 — TABLE REFERENCES"
    )

    references = document.table_references

    check(
        "Reference count",
        len(references) == 2,
    )

    first = references[0]

    check(
        "Reference table ID",
        first.table_id
        == "TABLE-TEST-001",
    )

    check(
        "Reference page number",
        first.page_number == 1,
    )

    check(
        "Structure analyzed",
        first.structure_analyzed is True,
    )

    check(
        "Validation propagated",
        first.validated is True,
    )

    check(
        "Schema mapping propagated",
        first.schema_mapped is True,
    )

    check(
        "Canonical status available",
        hasattr(
            first,
            "canonical_generated",
        ),
    )


# ============================================================
# TEST 7 — PROCESSING STATISTICS
# ============================================================

def test_processing(
    document: StructuredDocument,
) -> None:

    section(
        "TEST 7 — PROCESSING STATISTICS"
    )

    processing = document.processing

    check(
        "Processing result exists",
        processing is not None,
    )

    check(
        "Processing status exists",
        processing.status
        in (
            DocumentProcessingStatus,
            DocumentProcessingStatus
            .COMPLETED_WITH_WARNINGS,
        ),
    )

    check(
        "Tables detected",
        processing.total_tables_detected
        == 2,
    )

    check(
        "Tables extracted",
        processing.total_tables_extracted
        == 2,
    )

    check(
        "Tables cleaned",
        processing.total_tables_cleaned
        == 2,
    )

    check(
        "Tables validated",
        processing.total_tables_validated
        == 2,
    )

    check(
        "Tables schema mapped",
        processing.total_tables_schema_mapped
        == 2,
    )

    check(
        "Processing time available",
        processing.processing_time_seconds
        >= 0,
    )


# ============================================================
# TEST 8 — CONVENIENCE FUNCTION
# ============================================================

def test_convenience_function() -> None:

    section(
        "TEST 8 — CONVENIENCE FUNCTION"
    )

    table = create_sample_table(
        "TABLE-CONVENIENCE-001",
        0,
    )

    document = build_structured_document(
        document_id="DOC-CONVENIENCE-001",

        tables=[table],
    )

    check(
        "Convenience function",
        document is not None,
    )

    check(
        "Convenience document ID",
        document.document_id
        == "DOC-CONVENIENCE-001",
    )

    check(
        "Convenience table integration",
        len(document.tables) == 1,
    )


# ============================================================
# TEST 9 — DOCUMENT INTEGRITY
# ============================================================

def test_document_integrity(
    document: StructuredDocument,
) -> None:

    section(
        "TEST 9 — DOCUMENT INTEGRITY"
    )

    check(
        "Document has metadata",
        document.metadata is not None,
    )

    check(
        "Document has pages",
        len(document.pages) > 0,
    )

    check(
        "Document has tables",
        len(document.tables) > 0,
    )

    check(
        "Document has table references",
        len(document.table_references)
        == len(document.tables),
    )

    check(
        "Document has processing result",
        document.processing is not None,
    )

    check(
        "Pipeline version",
        document.processing.pipeline_version
        == DOCUMENT_STRUCTURER_VERSION,
    )


# ============================================================
# TEST 10 — SERIALIZATION
# ============================================================

def test_serialization(
    document: StructuredDocument,
) -> None:

    section(
        "TEST 10 — SERIALIZATION"
    )

    try:

        data = document.model_dump()

        check(
            "model_dump()",
            isinstance(data, dict),
        )

        check(
            "Document ID serialized",
            data.get("document_id")
            == document.document_id,
        )

        check(
            "Tables serialized",
            "tables" in data,
        )

        check(
            "Pages serialized",
            "pages" in data,
        )

        check(
            "Processing serialized",
            "processing" in data,
        )

    except Exception as exc:

        check(
            "Serialization",
            False,
            str(exc),
        )


# ============================================================
# TEST 11 — JSON SERIALIZATION
# ============================================================

def test_json_serialization(
    document: StructuredDocument,
) -> None:

    section(
        "TEST 11 — JSON SERIALIZATION"
    )

    try:

        json_data = document.model_dump_json()

        check(
            "JSON serialization",
            isinstance(
                json_data,
                str,
            ),
        )

        check(
            "JSON is not empty",
            len(json_data) > 0,
        )

        check(
            "Document ID in JSON",
            "DOC-TEST-001"
            in json_data,
        )

    except Exception as exc:

        check(
            "JSON serialization",
            False,
            str(exc),
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    global passed
    global failed

    passed = 0
    failed = 0

    section(
        "PHASE 3.1.10.2 — DOCUMENT INTEGRATION SERVICE"
    )

    print()
    print(
        f"Project root: {PROJECT_ROOT}"
    )

    try:

        # ----------------------------------------------------
        # Tests
        # ----------------------------------------------------

        test_imports()

        metadata = test_metadata()

        pages = test_pages()

        tables = test_tables()

        document = test_document_build(
            metadata,
            pages,
            tables,
        )

        test_table_references(
            document
        )

        test_processing(
            document
        )

        test_convenience_function()

        test_document_integrity(
            document
        )

        test_serialization(
            document
        )

        test_json_serialization(
            document
        )

    except Exception as exc:

        print()
        print(
            "ERROR during Phase 3.1.10.2:"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        failed += 1

    # ========================================================
    # RESULTS
    # ========================================================

    print()

    section(
        "PHASE 3.1.10.2 RESULTS"
    )

    print(
        f"Checks passed: {passed}"
    )

    print(
        f"Checks failed: {failed}"
    )

    print()

    if failed == 0:

        print(
            "PASS"
        )

        print()
        print(
            "Phase 3.1.10.2 — "
            "Document Integration Service "
            "completed successfully."
        )

        return

    print(
        "FAIL"
    )

    print()
    print(
        "Please review the failed checks above."
    )

    raise SystemExit(1)


if __name__ == "__main__":
    main()