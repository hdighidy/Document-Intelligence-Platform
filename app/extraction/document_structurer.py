"""
Document Structurer
===================

DocumentAI — Document-Level Structured Output Integration

Phase:
    3.1.10.2 — Document Integration Service

Purpose
-------
Integrates the existing DocumentAI processing components into
one document-level StructuredDocument object.

Responsibilities
----------------
This module:

    - creates StructuredDocument
    - integrates document metadata
    - integrates pages
    - integrates processed tables
    - creates lightweight table references
    - calculates processing statistics
    - propagates table validation status
    - propagates schema mapping status
    - propagates canonical-table status
    - calculates document-level warnings/errors
    - tracks processing time

This module does NOT:

    - detect tables
    - extract tables
    - clean tables
    - normalize cells
    - validate tables
    - analyze table structure
    - perform semantic mapping
    - generate canonical tables

Those responsibilities belong to their respective modules.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
from time import perf_counter
from typing import Any

from app.models.document import (
    DocumentMetadata,
    DocumentPage,
    DocumentProcessingResult,
    DocumentProcessingStatus,
    DocumentTableReference,
    PDFMetadata,
    ProcessingStatus,
    StructuredDocument,
)

from app.models.document import (
    DocumentImage,
    DocumentMetadata,
    DocumentPage,
    StructuredDocument,
)

from app.models.table import (
    SchemaMappingStatus,
    Table,
    TableValidationStatus,
)


# ============================================================
# VERSION
# ============================================================

DOCUMENT_STRUCTURER_VERSION = "3.1.10.2"


# ============================================================
# DOCUMENT STRUCTURER
# ============================================================


class DocumentStructurer:
    """
    Document-level integration service.

    This class receives already-processed document components
    and combines them into a StructuredDocument.
    """

    def __init__(
        self,
        pipeline_version: str = DOCUMENT_STRUCTURER_VERSION,
    ) -> None:

        self.pipeline_version = pipeline_version

    # ========================================================
    # PUBLIC API
    # ========================================================

    def build(
        self,
        document_id: str,
        metadata: DocumentMetadata | None = None,
        pages: list[DocumentPage] | None = None,
        tables: list[Table] | None = None,
        images: list[DocumentImage] | None = None,
        extra_metadata: dict[str, Any] | None = None,
        started_at: datetime | None = None,
    ) -> StructuredDocument:
        """
        Build a complete StructuredDocument.

        Parameters
        ----------
        document_id:
            Unique document identifier.

        metadata:
            Document-level metadata.

        pages:
            Already extracted document pages.

        tables:
            Already processed tables.

        extra_metadata:
            Optional additional metadata.

        started_at:
            Optional processing start timestamp.

        Returns
        -------
        StructuredDocument
            Integrated document-level structured object.
        """

        processing_start = perf_counter()

        pages = pages or []

        tables = tables or []

        images = images or []

        extra_metadata = extra_metadata or {}

        for page in pages:

            page.image_ids = []

        for image in images:

            for page in pages:

                if page.page_number == image.page_number:

                    page.image_ids.append(
                        image.image_id
                    )

                    break

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        if metadata is None:
            now = datetime.now()
            page_count = len(pages or [])
            table_count = len(tables or [])

            metadata = DocumentMetadata(
                document_id=document_id,
                filename="",
                original_filename="",
                stored_filename="",
                file_path=None,
                file_type="application/pdf",
                file_size=None,
                page_count=page_count,
                created_at=now,
                modified_at=now,
                source="document_structurer",
                sha256="",
                mime_type="application/pdf",
                uploaded_at=now,
                status=ProcessingStatus.UPLOADED,
                pdf=PDFMetadata(
                    page_count=page_count
                ),
                table_count=table_count,
            )

        else:

            metadata.document_id = (
                metadata.document_id
                or document_id
            )

        # ----------------------------------------------------
        # Create table references
        # ----------------------------------------------------

        table_references = (
            self._build_table_references(
                tables
            )
        )

        # ----------------------------------------------------
        # Processing result
        # ----------------------------------------------------

        processing = (
            self._build_processing_result(
                tables=tables,
                started_at=started_at,
                processing_start=processing_start,
            )
        )

        # ----------------------------------------------------
        # Final document
        # ----------------------------------------------------

        document = StructuredDocument(
            document_id=document_id,
            metadata=metadata,
            pages=pages,
            tables=tables,
            images=images,
            table_references=table_references,
            processing=processing,
            extra_metadata=extra_metadata,
        )

        return document

    # ========================================================
    # TABLE REFERENCES
    # ========================================================

    def _build_table_references(
        self,
        tables: list[Table],
    ) -> list[DocumentTableReference]:
        """
        Build lightweight document-level references
        for processed tables.
        """

        references: list[
            DocumentTableReference
        ] = []

        for table in tables:

            reference = (
                DocumentTableReference(
                    table_id=table.table_id,
                    page_number=table.page_number,
                    table_index=table.table_index,

                    structure_analyzed=(
                        self._is_structure_analyzed(
                            table
                        )
                    ),

                    validated=(
                        table.validation_result
                        is not None
                    ),

                    schema_mapped=(
                        table.schema is not None
                    ),

                    canonical_generated=(
                        table.canonical_table
                        is not None
                    ),

                    confidence=(
                        self._get_table_confidence(
                            table
                        )
                    ),
                )
            )

            references.append(reference)

        return references

    # ========================================================
    # PROCESSING RESULT
    # ========================================================

    def _build_processing_result(
        self,
        tables: list[Table],
        started_at: datetime | None,
        processing_start: float,
    ) -> DocumentProcessingResult:
        """
        Build document-level processing statistics.
        """

        total_tables = len(tables)

        extracted_count = self._count_extracted(
            tables
        )

        cleaned_count = self._count_cleaned(
            tables
        )

        validated_count = self._count_validated(
            tables
        )

        schema_count = self._count_schema_mapped(
            tables
        )

        canonical_count = (
            self._count_canonical_tables(
                tables
            )
        )

        warnings = self._collect_warnings(
            tables
        )

        errors = self._collect_errors(
            tables
        )

        status = self._determine_status(
            tables=tables,
            warnings=warnings,
            errors=errors,
        )

        completed_at = datetime.now()

        processing_time = (
            perf_counter()
            - processing_start
        )

        return DocumentProcessingResult(
            status=status,

            pipeline_version=(
                self.pipeline_version
            ),

            started_at=started_at,

            completed_at=completed_at,

            processing_time_seconds=(
                processing_time
            ),

            total_tables_detected=(
                total_tables
            ),

            total_tables_extracted=(
                extracted_count
            ),

            total_tables_cleaned=(
                cleaned_count
            ),

            total_tables_validated=(
                validated_count
            ),

            total_tables_schema_mapped=(
                schema_count
            ),

            total_canonical_tables=(
                canonical_count
            ),

            warnings=warnings,

            errors=errors,
        )

    # ========================================================
    # EXTRACTION
    # ========================================================

    @staticmethod
    def _count_extracted(
        tables: list[Table],
    ) -> int:
        """
        Count tables that contain extracted data.
        """

        count = 0

        for table in tables:

            if (
                table.rows
                or table.cells
                or table.data_rows
            ):
                count += 1

        return count

    # ========================================================
    # CLEANING
    # ========================================================

    @staticmethod
    def _count_cleaned(
        tables: list[Table],
    ) -> int:
        """
        Count tables where cleaning was applied.
        """

        return sum(
            1
            for table in tables
            if table.cleaning_applied
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _count_validated(
        tables: list[Table],
    ) -> int:
        """
        Count tables with validation results.
        """

        return sum(
            1
            for table in tables
            if (
                table.validation_result
                is not None
                or table.validation_status
                is not None
            )
        )

    # ========================================================
    # SCHEMA MAPPING
    # ========================================================

    @staticmethod
    def _count_schema_mapped(
        tables: list[Table],
    ) -> int:
        """
        Count tables with semantic schema mapping.
        """

        return sum(
            1
            for table in tables
            if (
                table.schema is not None
                or table.schema_mapping_status
                is not None
            )
        )

    # ========================================================
    # CANONICAL TABLE
    # ========================================================

    @staticmethod
    def _count_canonical_tables(
        tables: list[Table],
    ) -> int:
        """
        Count tables with canonical structured output.
        """

        return sum(
            1
            for table in tables
            if table.canonical_table is not None
        )

    # ========================================================
    # STRUCTURE
    # ========================================================

    @staticmethod
    def _is_structure_analyzed(
        table: Table,
    ) -> bool:
        """
        Determine whether structure analysis has been
        completed.

        The method intentionally supports multiple
        representations because the Table model evolved
        across Phase 3.1.7.
        """

        # New explicit flag
        if hasattr(table, "structure_analyzed"):

            value = getattr(
                table,
                "structure_analyzed",
                False,
            )

            if value is True:
                return True

        # Existing structure information
        if table.structure_type is not None:
            return True

        if table.structure_confidence is not None:
            return True

        if table.data_start_row_index is not None:
            return True

        if table.data_end_row_index is not None:
            return True

        return False

    # ========================================================
    # CONFIDENCE
    # ========================================================

    @staticmethod
    def _get_table_confidence(
        table: Table,
    ) -> float | None:
        """
        Determine the best available table confidence.
        """

        candidates: list[float] = []

        if table.confidence_score is not None:
            candidates.append(
                table.confidence_score
            )

        if table.quality_score is not None:
            candidates.append(
                table.quality_score
            )

        if table.validation_score is not None:
            candidates.append(
                table.validation_score
            )

        if table.structure_confidence is not None:
            candidates.append(
                table.structure_confidence
            )

        if (
            table.schema_mapping_confidence
            is not None
        ):
            candidates.append(
                table.schema_mapping_confidence
            )

        if (
            table.canonical_table is not None
            and table.canonical_table.mapping_confidence
            is not None
        ):
            candidates.append(
                table.canonical_table.mapping_confidence
            )

        if not candidates:
            return None

        return sum(candidates) / len(candidates)

    # ========================================================
    # WARNINGS
    # ========================================================

    @staticmethod
    def _collect_warnings(
        tables: list[Table],
    ) -> list[str]:
        """
        Collect document-level warnings from tables.
        """

        warnings: list[str] = []

        for table in tables:

            # ----------------------------------------------
            # Validation warnings
            # ----------------------------------------------

            if (
                table.validation_result is not None
                and table.validation_result.has_warnings
            ):

                warnings.append(
                    (
                        f"Table "
                        f"{table.table_id} "
                        f"contains validation warnings."
                    )
                )

            # ----------------------------------------------
            # Quality warnings
            # ----------------------------------------------

            if table.quality_flags:

                warnings.append(
                    (
                        f"Table "
                        f"{table.table_id} "
                        f"contains quality flags: "
                        f"{', '.join(table.quality_flags)}"
                    )
                )

            # ----------------------------------------------
            # Schema mapping
            # ----------------------------------------------

            if (
                table.schema_mapping_status
                == SchemaMappingStatus.PARTIAL
            ):

                warnings.append(
                    (
                        f"Table "
                        f"{table.table_id} "
                        f"has partial schema mapping."
                    )
                )

            # ----------------------------------------------
            # Structure
            # ----------------------------------------------

            if table.structure_warnings:

                for warning in (
                    table.structure_warnings
                ):

                    warnings.append(
                        (
                            f"Table "
                            f"{table.table_id}: "
                            f"{warning}"
                        )
                    )

        return warnings

    # ========================================================
    # ERRORS
    # ========================================================

    @staticmethod
    def _collect_errors(
        tables: list[Table],
    ) -> list[str]:
        """
        Collect document-level errors from tables.
        """

        errors: list[str] = []

        for table in tables:

            # ----------------------------------------------
            # Validation errors
            # ----------------------------------------------

            if (
                table.validation_result is not None
                and table.validation_result.has_errors
            ):

                errors.append(
                    (
                        f"Table "
                        f"{table.table_id} "
                        f"contains validation errors."
                    )
                )

            # ----------------------------------------------
            # Validation issues
            # ----------------------------------------------

            for issue in (
                table.validation_issues
            ):

                severity = str(
                    issue.severity
                )

                if (
                    "ERROR" in severity
                    or "CRITICAL" in severity
                ):

                    errors.append(
                        (
                            f"Table "
                            f"{table.table_id}: "
                            f"{issue.message}"
                        )
                    )

        return errors

    # ========================================================
    # STATUS
    # ========================================================

    @staticmethod
    def _determine_status(
        tables: list[Table],
        warnings: list[str],
        errors: list[str],
    ) -> DocumentProcessingStatus:
        """
        Determine overall document processing status.
        """

        if errors:

            return (
                DocumentProcessingStatus.FAILED
            )

        if warnings:

            return (
                DocumentProcessingStatus
                .COMPLETED_WITH_WARNINGS
            )

        return (
            DocumentProcessingStatus.COMPLETED
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def build_structured_document(
        document_id: str,
        pdf_path: Path | None = None,
        metadata: DocumentMetadata | None = None,
        pages: list[DocumentPage] | None = None,
        tables: list[Table] | None = None,
        images: list[DocumentImage] | None = None,
        extra_metadata: dict[str, Any] | None = None,
        started_at: datetime | None = None,
    ) -> StructuredDocument:
    """
    Convenience wrapper around DocumentStructurer.build().
    """

    structurer = DocumentStructurer()

    return structurer.build(
        document_id=document_id,
        metadata=metadata,
        pages=pages,
        tables=tables,
        images=images,
        extra_metadata=extra_metadata,
        started_at=started_at,
    )


# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "DOCUMENT_STRUCTURER_VERSION",
    "DocumentStructurer",
    "build_structured_document",
]