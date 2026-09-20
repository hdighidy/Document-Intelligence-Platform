"""
Table Extraction Pipeline (Orchestration)
==========================================

Wires together the individual table-processing stages into a single
entry point that the ingestion service can call.

Pipeline:

    PDF
     |
    Detect tables            (table_detector.detect_tables)
     |
    Extract table content    (table_extractor.extract_tables)
     |
    Clean cells/rows         (table_cleaner.clean_table)
     |
    Analyze structure        (table_structure/structure_analyzer.analyze_table_structure)
     |
    Score quality            (table_quality_scorer.score_table_quality)
     |
    Validate                 (validation/table_validator.validate_table)
     |
    list[Table]

Deliberately NOT included: canonical/schema-mapped table generation
(app/extraction/table/canonical/canonical_generator.py). That step
requires a schema-mapping stage that does not exist yet in this
codebase (generate_canonical_table() raises ValueError without a
populated table.schema). For RAG purposes, a cleaned + validated
Table (headers + rows) is sufficient input for chunking; canonical
generation can be revisited separately if a use case needs it.
"""

from __future__ import annotations

from pathlib import Path

from app.extraction.table_cleaner import clean_table
from app.extraction.table_detector import detect_tables
from app.extraction.table_extractor import extract_tables
from app.extraction.table_quality_scorer import score_table_quality
from app.extraction.table_structure.structure_analyzer import (
    analyze_table_structure,
)
from app.models.table import Table
from app.validation.table_validator import validate_table


def extract_document_tables(
    pdf_path: Path,
    document_id: str,
) -> list[Table]:
    """
    Run the complete table extraction pipeline for one document.

    Any table that fails at the clean/analyze/score/validate stage
    is skipped rather than aborting the whole document — a single
    malformed table should not prevent the rest of the document's
    tables (or its text content) from being usable.

    Returns:
        List of fully processed Table objects (cleaned, structure
        analyzed, quality scored, and validated). Empty list if
        no tables were detected.
    """

    detected_tables = detect_tables(
        pdf_path=pdf_path,
        document_id=document_id,
    )

    if not detected_tables:
        return []

    extracted_tables = extract_tables(
        pdf_path=pdf_path,
        detected_tables=detected_tables,
    )

    processed_tables: list[Table] = []

    for table in extracted_tables:

        try:
            table = clean_table(table)
            table = analyze_table_structure(table)
            table = score_table_quality(table)
            table.validation_result = validate_table(table)

        except Exception as exc:
            # Table-level failure: skip this table, keep the rest
            # of the document's tables and text usable.
            print(
                f"Warning: failed to process table "
                f"{getattr(table, 'table_id', '<unknown>')} "
                f"on page {getattr(table, 'page_number', '?')}: {exc}"
            )
            continue

        processed_tables.append(table)

    return processed_tables
