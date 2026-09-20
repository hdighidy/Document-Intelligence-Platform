"""
Phase 3.1.11
End-to-End Document Structured Pipeline

Pipeline:

PDF
 -> table detection
 -> table extraction
 -> table cleaning
 -> structure analysis
 -> quality scoring
 -> validation
 -> canonical generation
 -> document structured integration

This module intentionally reuses the already-tested Phase 3.1.x
components instead of duplicating their implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.extraction.table_pipeline import (
    detect_tables,
    extract_tables,
    clean_table,
    analyze_table_structure,
    score_table_quality,
    validate_table,
)

from app.extraction.table.canonical_generator import (
    generate_canonical_table,
)

from app.extraction.document_structurer import (
    build_structured_document,
)

from app.models.document import (
    DocumentMetadata,
    DocumentProcessingStatus,
    StructuredDocument,
)

from app.extraction.table.schema.schema_mapper import (
    map_table_schema,
)



PIPELINE_VERSION = "3.1.11"


@dataclass
class PipelineStatistics:
    """Runtime statistics for the end-to-end pipeline."""

    tables_detected: int = 0
    tables_extracted: int = 0
    tables_cleaned: int = 0
    tables_structure_analyzed: int = 0
    tables_quality_scored: int = 0
    tables_validated: int = 0
    tables_canonical_generated: int = 0

    processing_time_seconds: float | None = None

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EndToEndPipelineResult:
    """Final result returned by the Phase 3.1.11 pipeline."""

    document: StructuredDocument | None = None

    document_id: str = ""

    status: str = "PENDING"

    statistics: PipelineStatistics = field(
        default_factory=PipelineStatistics
    )

    pipeline_version: str = PIPELINE_VERSION

    canonical_generator_version: str = "3.1.10"

    started_at: datetime | None = None

    completed_at: datetime | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _build_document_id(pdf_path: Path) -> str:
    """
    Generate a deterministic document identifier for the test/runtime
    pipeline.

    The upload layer may provide its own document ID. Therefore this
    function is only a fallback.
    """

    import hashlib

    digest = hashlib.sha256(
        str(pdf_path.resolve()).encode("utf-8")
    ).hexdigest()[:12].upper()

    return f"DOC-{digest}"


def run_end_to_end_pipeline(
    pdf_path: Path,
    *,
    document_id: str | None = None,
    metadata: DocumentMetadata | None = None,
) -> EndToEndPipelineResult:
    """
    Execute the complete Phase 3.1.11 pipeline.

    Parameters
    ----------
    pdf_path:
        Path to the source PDF.

    document_id:
        Optional existing document ID.

    metadata:
        Optional DocumentMetadata already created by the ingestion
        layer.

    Returns
    -------
    EndToEndPipelineResult
    """

    pdf_path = Path(pdf_path)

    started_at = _utc_now()

    result = EndToEndPipelineResult(
        started_at=started_at,
    )

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    if not pdf_path.exists():
        result.status = "FAILED"

        result.statistics.errors.append(
            f"PDF does not exist: {pdf_path}"
        )

        result.completed_at = _utc_now()

        result.statistics.processing_time_seconds = (
            result.completed_at - started_at
        ).total_seconds()

        return result

    if not pdf_path.is_file():
        result.status = "FAILED"

        result.statistics.errors.append(
            f"PDF path is not a file: {pdf_path}"
        )

        result.completed_at = _utc_now()

        result.statistics.processing_time_seconds = (
            result.completed_at - started_at
        ).total_seconds()

        return result

    if document_id is None:
        document_id = _build_document_id(pdf_path)

    result.document_id = document_id

    try:

        # =====================================================
        # STEP 1 — TABLE DETECTION
        # =====================================================

        detected_tables = detect_tables(
            pdf_path,
            document_id,
        )

        result.statistics.tables_detected = len(
            detected_tables
        )

        # =====================================================
        # STEP 2 — TABLE EXTRACTION
        # =====================================================

        extracted_tables = extract_tables(
            pdf_path,
            detected_tables,
        )

        result.statistics.tables_extracted = len(
            extracted_tables
        )

        # =====================================================
        # STEP 3 — TABLE PROCESSING
        # =====================================================

        processed_tables = []

        for table in extracted_tables:

            # -------------------------------------------------
            # Cleaning
            # -------------------------------------------------

            table = clean_table(table)

            result.statistics.tables_cleaned += 1

            # -------------------------------------------------
            # Structure analysis
            # -------------------------------------------------

            table = analyze_table_structure(table)

            if getattr(
                table,
                "structure_analyzed",
                False,
            ):
                result.statistics.tables_structure_analyzed += 1

            # -------------------------------------------------
            # Quality scoring
            # -------------------------------------------------

            table = score_table_quality(table)

            result.statistics.tables_quality_scored += 1

            # -------------------------------------------------
            # Validation
            # -------------------------------------------------

            validation_result = validate_table(
                table
            )

            # Some implementations attach the validation result
            # themselves. If not, preserve it here.

            if getattr(
                table,
                "validation_result",
                None,
            ) is None:

                try:
                    table.validation_result = (
                        validation_result
                    )
                except Exception:
                    pass

            result.statistics.tables_validated += 1

            # =================================================
            # PHASE 3.1.8 — SCHEMA / SEMANTIC MAPPING
            # =================================================

            table = map_table_schema(table)

            # -------------------------------------------------
            # Verify schema mapping before canonical generation
            # -------------------------------------------------

            if getattr(table, "schema", None) is None:
                raise ValueError(
                    f"Schema mapping failed for table "
                    f"{getattr(table, 'table_id', '<unknown>')}"
                )

            # -------------------------------------------------
            # Canonical generation
            # -------------------------------------------------

            canonical_table = generate_canonical_table(
                table,
                attach=True,
            )

            if canonical_table is not None:
                result.statistics.tables_canonical_generated += 1

            # -------------------------------------------------
            # Store processed table
            # -------------------------------------------------

            processed_tables.append(table)

        # =====================================================
        # STEP 4 — DOCUMENT STRUCTURED OUTPUT
        # =====================================================

        structured_document = build_structured_document(
            document_id=document_id,
            metadata=metadata,
            tables=processed_tables,
            extra_metadata={
                "pipeline_version": PIPELINE_VERSION,
                "canonical_generator_version": (
                    "3.1.10"
                ),
                "source_pdf": str(pdf_path),
                "tables_detected": (
                    result.statistics.tables_detected
                ),
                "tables_extracted": (
                    result.statistics.tables_extracted
                ),
                "tables_cleaned": (
                    result.statistics.tables_cleaned
                ),
                "tables_structure_analyzed": (
                    result.statistics.tables_structure_analyzed
                ),
                "tables_quality_scored": (
                    result.statistics.tables_quality_scored
                ),
                "tables_validated": (
                    result.statistics.tables_validated
                ),
                "tables_canonical_generated": (
                    result.statistics.tables_canonical_generated
                ),
            },
            started_at=started_at,
        )

        result.document = structured_document

        # =====================================================
        # SUCCESS
        # =====================================================

        result.status = "COMPLETED"

    except Exception as exc:

        result.status = "FAILED"

        result.statistics.errors.append(
            f"{type(exc).__name__}: {exc}"
        )

    finally:

        result.completed_at = _utc_now()

        result.statistics.processing_time_seconds = (
            result.completed_at - started_at
        ).total_seconds()

    return result


def process_document(
    pdf_path: Path,
    *,
    document_id: str | None = None,
    metadata: DocumentMetadata | None = None,
) -> EndToEndPipelineResult:
    """
    Convenience wrapper around run_end_to_end_pipeline().
    """

    return run_end_to_end_pipeline(
        pdf_path,
        document_id=document_id,
        metadata=metadata,
    )


__all__ = [
    "PIPELINE_VERSION",
    "PipelineStatistics",
    "EndToEndPipelineResult",
    "run_end_to_end_pipeline",
    "process_document",
]