"""
Canonical Table Processing
==========================

Phase 3.1.9
"""

from app.extraction.table.canonical_generator import (
    GENERATOR_VERSION,
    build_canonical_table,
    generate_canonical_table,
)

__all__ = [
    "GENERATOR_VERSION",
    "generate_canonical_table",
    "build_canonical_table",
]