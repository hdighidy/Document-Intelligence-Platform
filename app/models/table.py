"""
Table Models
============

Document AI — Table Processing

Supported phases:

    Phase 3.1.1
        Core table models

    Phase 3.1.2
        Table Detection

    Phase 3.1.3
        Table Extraction

    Phase 3.1.4
        Table Cleaning & Normalization

    Phase 3.1.4.1
        Intelligent Header & Title Detection

    Phase 3.1.4.2
        Multi-line Cell Reconstruction

    Phase 3.1.4.3
        Intelligent Data Type & Semantic Normalization

    Phase 3.1.5
        Table Quality & Confidence Scoring

    Phase 3.1.6.1
        Table Validation Models

    Phase 3.1.7
        Table Structure Analysis

    Phase 3.1.8
        Table Schema & Semantic Mapping

    Phase 3.1.9
        Canonical Structured Table Generation & Integration

IMPORTANT
=========

This module contains DATA MODELS only.

It does not perform:

    - table detection
    - table extraction
    - table cleaning
    - normalization
    - quality scoring
    - validation
    - structure analysis
    - semantic mapping
    - canonical generation

Those responsibilities belong to modules under:

    app/extraction/
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# ENUMS
# ============================================================


class TableValidationStatus(str, Enum):
    """Overall table validation status."""

    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"


class ValidationSeverity(str, Enum):
    """Severity of a validation issue."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


ValidationStatus = TableValidationStatus


# ============================================================
# BOUNDING BOX
# ============================================================


class BoundingBox(BaseModel):
    """
    Position of an object on a PDF page.

    Supports both:

        x0 / y0 / x1 / y1

    and:

        x0 / top / x1 / bottom
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    x0: float = 0.0

    top: float = Field(
        default=0.0,
        alias="y0",
    )

    x1: float = 0.0

    bottom: float = Field(
        default=0.0,
        alias="y1",
    )

    @property
    def y0(self) -> float:
        return self.top

    @property
    def y1(self) -> float:
        return self.bottom

    @property
    def width(self) -> float:
        return max(
            0.0,
            self.x1 - self.x0,
        )

    @property
    def height(self) -> float:
        return max(
            0.0,
            self.bottom - self.top,
        )

    @property
    def area(self) -> float:
        return self.width * self.height


# ============================================================
# VALIDATION MODELS
# ============================================================


class ValidationIssue(BaseModel):
    """Represents one validation issue."""

    model_config = ConfigDict(
        extra="ignore",
    )

    code: str

    message: str

    severity: ValidationSeverity = (
        ValidationSeverity.WARNING
    )

    row_index: int | None = None

    column_index: int | None = None

    cell_id: str | None = None

    field: str | None = None

    value: Any | None = None

    expected: Any | None = None

    actual: Any | None = None


class ValidationCheck(BaseModel):
    """Represents one validation check."""

    model_config = ConfigDict(
        extra="ignore",
    )

    name: str

    passed: bool

    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    message: str = ""

    issues_count: int = 0


class TableValidationResult(BaseModel):
    """Complete validation result."""

    model_config = ConfigDict(
        extra="ignore",
    )

    status: TableValidationStatus = (
        TableValidationStatus.VALID
    )

    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    checks: list[ValidationCheck] = Field(
        default_factory=list
    )

    issues: list[ValidationIssue] = Field(
        default_factory=list
    )

    validated_at: datetime | None = None

    validator_version: str | None = None

    total_checks: int = 0

    passed_checks: int = 0

    failed_checks: int = 0

    error_count: int = 0

    warning_count: int = 0

    @property
    def is_valid(self) -> bool:
        return (
            self.status
            == TableValidationStatus.VALID
        )

    @property
    def has_warnings(self) -> bool:
        return (
            self.status
            == TableValidationStatus.WARNING
            or self.warning_count > 0
        )

    @property
    def has_errors(self) -> bool:
        return (
            self.error_count > 0
            or self.status
            == TableValidationStatus.INVALID
        )


# ============================================================
# QUALITY MODELS
# ============================================================


class TableQualityLevel(str, Enum):
    """Overall table quality classification."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class QualityFlag(str, Enum):
    """Standard quality flags."""

    HIGH_EMPTY_CELL_RATIO = (
        "HIGH_EMPTY_CELL_RATIO"
    )

    MISSING_HEADER = "MISSING_HEADER"

    INCONSISTENT_ROW_LENGTH = (
        "INCONSISTENT_ROW_LENGTH"
    )

    DUPLICATE_ROWS = "DUPLICATE_ROWS"

    LOW_CELL_CONFIDENCE = (
        "LOW_CELL_CONFIDENCE"
    )

    SUSPICIOUS_CELL = "SUSPICIOUS_CELL"

    INVALID_DATE = "INVALID_DATE"

    INVALID_NUMERIC_VALUE = (
        "INVALID_NUMERIC_VALUE"
    )


class CellQualityResult(BaseModel):
    """Quality information for one cell."""

    model_config = ConfigDict(
        extra="ignore",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    quality_level: TableQualityLevel = (
        TableQualityLevel.HIGH
    )

    flags: list[str] = Field(
        default_factory=list
    )

    reason: str = ""


class TableQualityResult(BaseModel):
    """Table-level quality and confidence."""

    model_config = ConfigDict(
        extra="ignore",
    )

    overall_score: float = Field(
        default=1.0,
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    quality_level: TableQualityLevel = (
        TableQualityLevel.HIGH
    )

    structural_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    extraction_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    semantic_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    completeness_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    flags: list[str] = Field(
        default_factory=list
    )

    cell_results: dict[str, CellQualityResult] = Field(
        default_factory=dict
    )


# ============================================================
# PHASE 3.1.8
# SEMANTIC ENUMS
# ============================================================


class TableFieldRole(str, Enum):
    """Logical role of a table column."""

    IDENTIFIER = "IDENTIFIER"
    DESCRIPTION = "DESCRIPTION"
    QUANTITY = "QUANTITY"
    UNIT = "UNIT"
    DATE = "DATE"
    STATUS = "STATUS"
    CURRENCY = "CURRENCY"
    NUMBER = "NUMBER"
    PERCENTAGE = "PERCENTAGE"
    CATEGORY = "CATEGORY"
    REFERENCE = "REFERENCE"
    LOCATION = "LOCATION"
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    TEXT = "TEXT"
    UNKNOWN = "UNKNOWN"


class TableSemanticType(str, Enum):
    """Semantic data type."""

    TEXT = "TEXT"
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    NUMBER = "NUMBER"
    PERCENTAGE = "PERCENTAGE"
    DATE = "DATE"
    CURRENCY = "CURRENCY"
    STATUS = "STATUS"
    BOOLEAN = "BOOLEAN"
    QUANTITY = "QUANTITY"
    UNIT = "UNIT"
    REFERENCE = "REFERENCE"
    UNKNOWN = "UNKNOWN"


class TableFieldRequirement(str, Enum):
    """Requiredness classification."""

    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    UNKNOWN = "UNKNOWN"


class SemanticMappingSource(str, Enum):
    """Source used for semantic mapping."""

    HEADER_EXACT = "HEADER_EXACT"
    HEADER_ALIAS = "HEADER_ALIAS"
    HEADER_PATTERN = "HEADER_PATTERN"
    CELL_DATA = "CELL_DATA"
    STRUCTURE = "STRUCTURE"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class SchemaMappingStatus(str, Enum):
    """Overall schema mapping status."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


# ============================================================
# PHASE 3.1.8
# FIELD DEFINITION
# ============================================================


class TableFieldDefinition(BaseModel):
    """Canonical definition of one table field."""

    model_config = ConfigDict(
        extra="ignore",
    )

    column_index: int = 0

    source_header: str = ""

    field_name: str = ""

    display_name: str = ""

    field_role: TableFieldRole = (
        TableFieldRole.UNKNOWN
    )

    semantic_type: TableSemanticType = (
        TableSemanticType.UNKNOWN
    )

    requirement: TableFieldRequirement = (
        TableFieldRequirement.UNKNOWN
    )

    mapping_source: SemanticMappingSource = (
        SemanticMappingSource.UNKNOWN
    )

    mapping_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    matched_alias: str | None = None

    non_empty_count: int = 0

    empty_count: int = 0

    sample_values: list[str] = Field(
        default_factory=list
    )

    description: str = ""

    unit: str | None = None

    currency: str | None = None


# ============================================================
# COLUMN MAPPING
# ============================================================


class TableColumnMapping(BaseModel):
    """Maps a source column to a canonical field."""

    model_config = ConfigDict(
        extra="ignore",
    )

    column_index: int = 0

    source_header: str = ""

    normalized_header: str = ""

    canonical_field: str = ""

    field_role: TableFieldRole = (
        TableFieldRole.UNKNOWN
    )

    semantic_type: TableSemanticType = (
        TableSemanticType.UNKNOWN
    )

    mapping_source: SemanticMappingSource = (
        SemanticMappingSource.UNKNOWN
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    matched_alias: str | None = None

    is_mapped: bool = False


# ============================================================
# TABLE SCHEMA
# ============================================================


class TableSchema(BaseModel):
    """
    Machine-readable semantic schema.

    Phase 3.1.8 principal output.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    schema_id: str = ""

    schema_version: str = "3.1.8"

    schema_name: str = ""

    mapping_status: SchemaMappingStatus = (
        SchemaMappingStatus.PARTIAL
    )

    mapping_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    fields: list[TableFieldDefinition] = Field(
        default_factory=list
    )

    column_mappings: list[TableColumnMapping] = Field(
        default_factory=list
    )

    total_columns: int = 0

    mapped_columns: int = 0

    unmapped_columns: int = 0

    required_fields: int = 0

    optional_fields: int = 0

    source_headers: list[str] = Field(
        default_factory=list
    )

    canonical_fields: list[str] = Field(
        default_factory=list
    )

    created_at: datetime | None = None

    mapper_version: str | None = None

    notes: list[str] = Field(
        default_factory=list
    )

    @property
    def is_complete(self) -> bool:
        return (
            self.mapping_status
            == SchemaMappingStatus.COMPLETE
        )

    @property
    def is_partial(self) -> bool:
        return (
            self.mapping_status
            == SchemaMappingStatus.PARTIAL
        )

    @property
    def has_unmapped_columns(self) -> bool:
        return self.unmapped_columns > 0


# ============================================================
# PHASE 3.1.8 / 3.1.9
# CANONICAL ROW
# ============================================================


class CanonicalTableRow(BaseModel):
    """
    Canonical representation of one logical table row.
    """

    model_config = ConfigDict(
        extra="allow",
    )

    row_index: int = 0

    values: dict[str, Any] = Field(
        default_factory=dict
    )

    source_values: dict[str, Any] = Field(
        default_factory=dict
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    source_row_index: int | None = None

    validation_status: TableValidationStatus | None = None

    validation_issues: list[ValidationIssue] = Field(
        default_factory=list
    )


# ============================================================
# PHASE 3.1.9
# CANONICAL TABLE
# ============================================================


class CanonicalTable(BaseModel):
    """
    Canonical structured representation of a table.

    Designed for:

        - analytics
        - SQL
        - Power BI
        - APIs
        - RAG
        - AI agents
        - business automation
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    canonical_table_id: str = ""

    source_table_id: str = ""

    document_id: str = ""

    source_filename: str = ""

    page_number: int = 1

    # --------------------------------------------------------
    # Schema
    # --------------------------------------------------------

    table_schema: TableSchema = Field(
        default_factory=TableSchema
    )

    # Compatibility alias handled through property.
    # This avoids Pydantic's BaseModel.schema collision.

    # --------------------------------------------------------
    # Rows
    # --------------------------------------------------------

    rows: list[CanonicalTableRow] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    row_count: int = 0

    column_count: int = 0

    # --------------------------------------------------------
    # Mapping
    # --------------------------------------------------------

    mapping_status: SchemaMappingStatus = (
        SchemaMappingStatus.PARTIAL
    )

    mapping_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    # --------------------------------------------------------
    # Generation
    # --------------------------------------------------------

    generated_at: datetime | None = None

    generator_version: str | None = None

    generation_method: str | None = None

    # --------------------------------------------------------
    # Traceability
    # --------------------------------------------------------

    source_row_count: int = 0

    source_column_count: int = 0

    source_headers: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    quality_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    validation_result: TableValidationResult | None = None

    notes: list[str] = Field(
        default_factory=list
    )

    @property
    def schema(self) -> TableSchema:
        """
        Compatibility accessor.

        Allows:

            canonical_table.schema

        without declaring a Pydantic field called
        `schema`, avoiding the BaseModel shadowing warning.
        """

        return self.table_schema


# ============================================================
# TABLE CELL
# ============================================================


class TableCell(BaseModel):
    """
    One extracted table cell.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    cell_id: str = ""

    row_index: int = 0

    column_index: int = 0

    raw_text: str | None = None

    text: str = ""

    normalized_text: str | None = None

    normalized_value: Any | None = None

    data_type: str = "string"

    semantic_type: str | None = None

    numeric_value: float | None = None

    normalization_source: str | None = None

    is_multiline: bool = False

    bbox: BoundingBox | None = None

    confidence: float = Field(default=1.0, ge=0.0, le=1.0,)

    quality_result: CellQualityResult | None = None

    validation_issues: list[ValidationIssue] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Phase 3.1.8
    # --------------------------------------------------------

    canonical_field: str | None = None

    field_role: TableFieldRole | None = None

    field_semantic_type: TableSemanticType | None = None

    schema_mapping_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

# ============================================================ 
# TABLE QUALITY SCORE  
# ============================================================ 
class TableQualityScore(BaseModel):
     
     """ Quality and confidence metrics for an extracted table. 
     All score values are percentages from 0 to 100. Components:
     structure_score header_score cell_quality_score normalization_score consistency_score Overall score:
     Structure 25% Header 15% Cell Quality 20% Normalization 20% Consistency 20% """ 
     model_config = ConfigDict( extra="ignore", ) 
    # -------------------------------------------------------- 
    # Individual quality scores 
    # -------------------------------------------------------- 
     structure_score: float = Field( default=0.0, ge=0.0, le=100.0, )
     header_score: float = Field( default=0.0, ge=0.0, le=100.0, ) 
     cell_quality_score: float = Field( default=0.0, ge=0.0, le=100.0, )
     normalization_score: float = Field( default=0.0, ge=0.0, le=100.0, ) 
     consistency_score: float = Field( default=0.0, ge=0.0, le=100.0, ) 
    # -------------------------------------------------------- 
    # Overall result 
    # -------------------------------------------------------- 
     overall_score: float = Field( default=0.0, ge=0.0, le=100.0, ) 
     confidence_level: str = ( "REVIEW_REQUIRED" ) 
    # -------------------------------------------------------- #
    # Statistics 
    # -------------------------------------------------------- 
     total_cells: int = Field( default=0, ge=0, ) 
     populated_cells: int = Field( default=0, ge=0, ) 
     empty_cells: int = Field( default=0, ge=0, ) 
     normalized_cells: int = Field( default=0, ge=0, ) 
     # -------------------------------------------------------- 
     #  Quality issues 
     # -------------------------------------------------------- 
     issues: list[str] = Field( default_factory=list )



# ============================================================
# TABLE METADATA
# ============================================================


class TableMetadata(BaseModel):
    """Metadata describing a detected/extracted table."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    table_id: str = ""

    document_id: str = ""

    table_index: int = 0

    source_filename: str = ""

    page_number: int = 1

    bbox: BoundingBox | None = None

    row_count: int = 0

    column_count: int = 0

    detection_method: str | None = None

    detection_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    extraction_method: str | None = None

    extraction_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    title: str | None = None

    header_row_index: int | None = None


# ============================================================
# TABLE
# ============================================================


class Table(BaseModel):
    """
    Central table model shared across all table phases.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # ========================================================
    # IDENTITY
    # ========================================================

    table_id: str = ""

    document_id: str = ""

    table_index: int = 0

    # ========================================================
    # SOURCE
    # ========================================================

    source_filename: str = ""

    page_number: int = 1

    # ========================================================
    # GEOMETRY
    # ========================================================

    bbox: BoundingBox | None = None

    # ========================================================
    # RAW / CLEANED STRUCTURE
    # ========================================================

    rows: list[list[str]] = Field(
        default_factory=list
    )

    headers: list[str] = Field(
        default_factory=list
    )

    cells: list[TableCell] = Field(
        default_factory=list
    )

    data_rows: list[list[str]] = Field(
        default_factory=list
    )

    row_count: int = 0

    column_count: int = 0

    # ========================================================
    # HEADER / TITLE
    # ========================================================

    title: str | None = None

    title_row_index: int | None = None

    header_row_index: int | None = None

    # ========================================================
    # STRUCTURE ANALYSIS
    # Phase 3.1.7
    # ========================================================

    data_start_row_index: int | None = None

    data_end_row_index: int | None = None

    data_row_indices: list[int] = Field(
        default_factory=list
    )

    data_row_count: int = 0

    has_data_rows: bool = False

    structure_analyzed: bool = False

    data_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    data_boundary_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    data_boundary_detected: bool = False

    data_boundary_warnings: list[str] = Field(
        default_factory=list
    )

    header_row_index: int | None = None

    header_row_indices: list[int] = Field(
        default_factory=list
    )

    empty_row_indices: list[int] = Field(
        default_factory=list
    )

    structural_row_indices: list[int] = Field(
        default_factory=list
    )

    title_row_count: int = 0

    header_row_count: int = 0

    empty_row_count: int = 0

    structural_row_count: int = 0

    has_title: bool = False

    has_header: bool = False

    has_empty_rows: bool = False

    structure_type: str | None = None

    structure_category: str | None = None

    has_multi_level_header: bool = False

    has_merged_cells: bool = False

    header_type: str | None = None

    title_type: str | None = None

    structure_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    header_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    title_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    row_consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    column_consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    structure_warnings: list[str] = Field(
        default_factory=list
    )

    structure_analysis_notes: list[str] = Field(
        default_factory=list
    )

    structure_analysis_version: str | None = None

    # --------------------------------------------------------
    # Logical row boundaries
    # --------------------------------------------------------


    # --------------------------------------------------------
    # Row classifications
    # --------------------------------------------------------

    title_row_index: int | None = None

    title_row_indices: list[int] = Field(
        default_factory=list
    )

    header_row_index: int | None = None

    header_row_indices: list[int] = Field(
        default_factory=list
    )

    data_row_indices: list[int] = Field(
        default_factory=list
    )


    structural_row_indices: list[int] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Row counts
    # --------------------------------------------------------

    title_row_count: int = 0

    header_row_count: int = 0

    data_row_count: int = 0

    empty_row_count: int = 0

    structural_row_count: int = 0

    # --------------------------------------------------------
    # Structure flags
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Structure classification
    # --------------------------------------------------------


    structure_category: str | None = None

    header_type: str | None = None

    title_type: str | None = None

    # --------------------------------------------------------
    # Structural confidence
    # --------------------------------------------------------

    header_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    title_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    data_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    # --------------------------------------------------------
    # Structural consistency
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Structural warnings / notes
    # --------------------------------------------------------


    structure_analysis_notes: list[str] = Field(
        default_factory=list
    )

    structure_analysis_version: str | None = None

    # --------------------------------------------------------
    # Structural quality metrics
    # --------------------------------------------------------

    header_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    title_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    data_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    empty_row_count: int = 0

    # --------------------------------------------------------
    # Structural counts
    # --------------------------------------------------------

    header_row_count: int = 0

    title_row_count: int = 0

    data_row_count: int = 0

    structural_row_count: int = 0

    # --------------------------------------------------------
    # Structural classification
    # --------------------------------------------------------

    structure_category: str | None = None

    header_type: str | None = None

    title_type: str | None = None

    # --------------------------------------------------------
    # Analysis metadata
    # --------------------------------------------------------

    structure_analysis_version: str | None = None

    structure_analysis_notes: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Critical structure-analysis fields
    # --------------------------------------------------------

    empty_column_indices: list[int] = Field(
        default_factory=list
    )

    sparse_row_indices: list[int] = Field(
        default_factory=list
    )

    sparse_column_indices: list[int] = Field(
        default_factory=list
    )

    merged_row_indices: list[int] = Field(
        default_factory=list
    )

    multiline_row_indices: list[int] = Field(
        default_factory=list
    )

    header_candidates: list[int] = Field(
        default_factory=list
    )

    title_candidates: list[int] = Field(
        default_factory=list
    )

    structure_issues: list[str] = Field(
        default_factory=list
    )

    # ========================================================
    # MULTI-LINE ANALYSIS
    # ========================================================

    multiline_cells_detected: int = 0

    # ========================================================
    # SCHEMA & SEMANTIC MAPPING
    # ========================================================

    table_schema: TableSchema | None = None

    schema_mapping_status: SchemaMappingStatus | None = None

    schema_mapping_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    canonical_table: CanonicalTable | None = None

    # ========================================================
    # EXTRACTION
    # ========================================================

    extraction_method: str | None = None

    extraction_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    # ========================================================
    # CLEANING
    # ========================================================

    cleaning_applied: bool = False

    normalization_version: str | None = None

    empty_cell_count: int = 0

    duplicate_row_count: int = 0

    # ========================================================
    # QUALITY
    # ========================================================

    quality_result: TableQualityScore  | None = None

    quality_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    quality_level: TableQualityLevel | None = None

    quality_flags: list[str] = Field(
        default_factory=list
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    validation_result: TableValidationResult | None = None

    validation_status: TableValidationStatus | None = None

    validation_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    validation_issues: list[ValidationIssue] = Field(
        default_factory=list
    )


    # ========================================================
    # PHASE 3.1.9
    # CANONICAL OUTPUT
    # ========================================================

    canonical_table: CanonicalTable | None = None

    canonical_generation_status: str | None = None

    canonical_generation_version: str | None = None

    canonical_generation_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    canonical_generated_at: datetime | None = None

    canonical_row_count: int = 0

    canonical_column_count: int = 0

    # ========================================================
    # OPTIONAL METADATA
    # ========================================================

    metadata: TableMetadata | None = None

    # ========================================================
    # COMPATIBILITY PROPERTY
    # ========================================================

    @property
    def schema(self) -> TableSchema | None:
        """
        Compatibility accessor for:

            table.schema

        Internally stored as:

            table.table_schema
        """

        return self.table_schema

    @schema.setter
    def schema(self, value: TableSchema | None) -> None:
        self.table_schema = value

    # ========================================================
    # CONVENIENCE PROPERTIES
    # ========================================================

    @property
    def total_cells(self) -> int:
        return len(self.cells)

    @property
    def is_validated(self) -> bool:
        return self.validation_result is not None

    @property
    def is_valid(self) -> bool:

        if self.validation_result is not None:
            return (
                self.validation_result.status
                == TableValidationStatus.VALID
            )

        return (
            self.validation_status
            == TableValidationStatus.VALID
        )

    @property
    def has_validation_warnings(self) -> bool:

        if self.validation_result is not None:
            return self.validation_result.has_warnings

        return False

    @property
    def has_validation_errors(self) -> bool:

        if self.validation_result is not None:
            return self.validation_result.has_errors

        return False

    @property
    def is_schema_mapped(self) -> bool:
        return self.table_schema is not None

    @property
    def has_canonical_table(self) -> bool:
        return self.canonical_table is not None

    @property
    def schema_is_complete(self) -> bool:

        if self.table_schema is not None:
            return self.table_schema.is_complete

        return (
            self.schema_mapping_status
            == SchemaMappingStatus.COMPLETE
        )


    @property
    def has_empty_columns(self) -> bool:
        return bool(self.empty_column_indices)


# ============================================================
# EXPORTS
# ============================================================


__all__ = [

    # Geometry
    "BoundingBox",

    # Validation
    "TableValidationStatus",
    "ValidationStatus",
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationCheck",
    "TableValidationResult",

    # Quality
    "TableQualityLevel",
    "QualityFlag",
    "CellQualityResult",
    "TableQualityResult",

    # Semantic mapping
    "TableFieldRole",
    "TableSemanticType",
    "TableFieldRequirement",
    "SemanticMappingSource",
    "SchemaMappingStatus",

    # Schema
    "TableFieldDefinition",
    "TableColumnMapping",
    "TableSchema",

    # Canonical
    "CanonicalTableRow",
    "CanonicalTable",

    # Core
    "TableCell",
    "TableMetadata",
    "Table",
]