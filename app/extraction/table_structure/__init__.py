"""
Table Structure Analysis
========================

Phase 3.1.7

Provides logical structural analysis for extracted tables.

Responsibilities:

    - Title detection
    - Header detection
    - Data-row detection
    - Empty-row detection
    - Data boundary detection
    - Row consistency analysis
    - Column consistency analysis
    - Basic merged-cell indicators
    - Structure classification
    - Structure confidence scoring
"""

from app.extraction.table_structure.structure_analyzer import (
    analyze_table_structure,
    analyze_structure,
    detect_title_rows,
    detect_header_rows,
    detect_data_rows,
    detect_empty_rows,
)


__all__ = [
    "analyze_table_structure",
    "analyze_structure",
    "detect_title_rows",
    "detect_header_rows",
    "detect_data_rows",
    "detect_empty_rows",
]