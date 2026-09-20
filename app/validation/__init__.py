"""
Document AI Validation Package
"""

from app.validation.table_validator import (
    VALIDATOR_VERSION,
    validate_table,
)

__all__ = [
    "VALIDATOR_VERSION",
    "validate_table",
]