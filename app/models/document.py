from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any


from pydantic import BaseModel, ConfigDict, Field
from app.models.table import Table 



# ============================================================
# DOCUMENT PROCESSING STATUS
# ============================================================

class DocumentProcessingStatus(str, Enum):
    """
    Overall document processing status.
    """
    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    INGESTED = "INGESTED"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    TABLES_EXTRACTED = "TABLES_EXTRACTED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = (
        "COMPLETED_WITH_WARNINGS"
    )
    FAILED = "FAILED"

#==================================================================

class ProcessingStatus(str, Enum):

    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    INGESTED = "INGESTED"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    TABLES_EXTRACTED = "TABLES_EXTRACTED"
    FAILED = "FAILED"


class PDFMetadata(BaseModel):

    page_count: int | None = None
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: datetime | None = None
    modification_date: datetime | None = None


class TextBlock(BaseModel):

    block_id: str
    page_number: int
    text: str

    # Position
    x0: float
    y0: float
    x1: float
    y1: float

    # Typography
    font: str | None = None
    font_size: float | None = None
    bold: bool = False
    italic: bool = False
    color: int | None = None

    # Structure
    structure: str = "paragraph"

    # Layout classification
    is_header: bool = False
    is_footer: bool = False

    # Reading order
    reading_order: int = 0


class PageText(BaseModel):

    page_number: int
    width: float
    height: float
    blocks: list[TextBlock]




class DocumentMetadata(BaseModel):

    """
    Metadata describing the source document.
    """
    model_config = ConfigDict(
        extra="ignore",
    )


    document_id: str = ""
    filename: str = ""
    original_filename: str
    stored_filename: str
    file_path: str | None = None
    file_type: str = "application/pdf"
    file_size: int | None = None
    page_count: int = 0
    created_at: datetime | None = None
    modified_at: datetime | None = None
    source: str | None = None
    sha256: str
    mime_type: str = "application/pdf"
    uploaded_at: datetime
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    pdf: PDFMetadata
    table_count: int | None = None

class DocumentImage(BaseModel):
    """
    Canonical representation of an image extracted from a document.

    The model stores image metadata and the reference to the
    persisted image file. Binary image data is intentionally not
    stored inside the Pydantic model.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    image_id: str = ""

    # --------------------------------------------------------
    # Document / Page relationship
    # --------------------------------------------------------

    page_number: int = 1

    # --------------------------------------------------------
    # Source PDF information
    # --------------------------------------------------------

    source_xref: int | None = None

    # --------------------------------------------------------
    # Image dimensions
    # --------------------------------------------------------

    width: int | None = None

    height: int | None = None

    # --------------------------------------------------------
    # Position on PDF page
    # --------------------------------------------------------

    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None

    # --------------------------------------------------------
    # Image format / storage
    # --------------------------------------------------------

    image_format: str = ""

    image_path: str = ""

    # --------------------------------------------------------
    # Additional metadata
    # --------------------------------------------------------

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

# ============================================================
# DOCUMENT PAGE
# ============================================================

class DocumentPage(BaseModel):
    """
    Structured representation of one document page.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    page_number: int = 1

    # --------------------------------------------------------
    # Page geometry
    # --------------------------------------------------------

    width: float | None = None
    height: float | None = None

    # --------------------------------------------------------
    # Page text
    # --------------------------------------------------------

    text: str = ""

    text_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    # --------------------------------------------------------
    # Structured text blocks
    # --------------------------------------------------------

    blocks: list[TextBlock] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Table references
    # --------------------------------------------------------

    table_ids: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Image references
    # --------------------------------------------------------

    image_ids: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Additional page metadata
    # --------------------------------------------------------

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

# ============================================================
# DOCUMENT TABLE REFERENCE
# ============================================================


class DocumentTableReference(BaseModel):
    """
    Lightweight reference to a processed table.

    Keeps document-level output compact while allowing
    the complete Table object to remain available.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    table_id: str = ""
    page_number: int = 1
    table_index: int = 0
    structure_analyzed: bool = False
    validated: bool = False
    schema_mapped: bool = False
    canonical_generated: bool = False
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

# ============================================================
# DOCUMENT PROCESSING RESULT
# ============================================================


class DocumentProcessingResult(BaseModel):
    """
    Processing information for the document.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    status: DocumentProcessingStatus = (
        DocumentProcessingStatus.PENDING
    )

    pipeline_version: str = "3.1.10"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processing_time_seconds: float | None = None
    total_tables_detected: int = 0
    total_tables_extracted: int = 0
    total_tables_cleaned: int = 0
    total_tables_validated: int = 0
    total_tables_schema_mapped: int = 0
    total_canonical_tables: int = 0
    warnings: list[str] = Field(
        default_factory=list
    )

    errors: list[str] = Field(
        default_factory=list
    )

# ============================================================
# STRUCTURED DOCUMENT
# ============================================================


class StructuredDocument(BaseModel):
    """
    Canonical document-level structured representation.

    This is the primary output model of Phase 3.1.10.

    It integrates the complete DocumentAI pipeline into
    one machine-readable object.
    """

    model_config = ConfigDict(extra="ignore",)

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    document_id: str = ""

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata: DocumentMetadata = Field(
        default_factory=DocumentMetadata
    )

    # --------------------------------------------------------
    # Pages
    # --------------------------------------------------------

    pages: list[DocumentPage] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    tables: list[Table] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    images: list[DocumentImage] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Lightweight table references
    # --------------------------------------------------------

    table_references: list[
        DocumentTableReference
    ] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Processing
    # --------------------------------------------------------

    processing: DocumentProcessingResult = Field(
        default_factory=DocumentProcessingResult
    )

    # --------------------------------------------------------
    # Arbitrary document-level metadata
    # --------------------------------------------------------

    extra_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # ========================================================
    # CONVENIENCE PROPERTIES
    # ========================================================

    @property
    def page_count(self) -> int:
        """
        Return number of pages.
        """

        return len(self.pages)

    @property
    def table_count(self) -> int:
        """
        Return number of tables.
        """

        return len(self.tables)

    @property
    def has_tables(self) -> bool:
        """
        Return True when the document contains tables.
        """

        return len(self.tables) > 0

    @property
    def image_count(self) -> int:
        """
        Return number of document images.
        """

        return len(self.images)

    @property
    def has_images(self) -> bool:
        """
        Return True when the document contains images.
        """

        return len(self.images) > 0

    @property
    def is_completed(self) -> bool:
        """
        Return True when document processing completed
        successfully.
        """

        return (
            self.processing.status
            in {
                DocumentProcessingStatus.COMPLETED,
                DocumentProcessingStatus.COMPLETED_WITH_WARNINGS,
            }
        )

    @property
    def has_errors(self) -> bool:
        """
        Return True when document processing produced
        errors.
        """

        return len(self.processing.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """
        Return True when document processing produced
        warnings.
        """

        return len(self.processing.warnings) > 0

# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "DocumentProcessingStatus",
    "DocumentMetadata",
    "DocumentPage",
    "DocumentTableReference",
    "DocumentProcessingResult",
    "StructuredDocument",
]