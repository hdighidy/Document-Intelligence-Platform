"""
Table Value Normalization
=========================

Phase 3.1.4.3

Responsibilities
----------------

    - Detect semantic data types
    - Normalize numeric values
    - Normalize percentages
    - Normalize dates
    - Normalize currencies
    - Detect status values
    - Detect engineering/material identifiers
    - Preserve original extracted values
    - Store normalized values separately

Important
---------

This module:

    - DOES NOT perform PDF extraction
    - DOES NOT perform OCR
    - DOES NOT perform spelling correction
    - DOES NOT modify raw_text
    - DOES NOT modify the original extracted text

Normalization is stored separately.

Example
-------

Raw:

    "Air Handlig\\nunit"

Normalized text:

    "Air Handlig unit"

Normalized value:

    "Air Handlig unit"

The spelling "Handlig" is intentionally preserved.

Spelling correction belongs to a future semantic/text
correction phase.

Architecture
------------

    table_cleaner.py
            |
            v
    table_value_normalizer.py
            |
            v
       models/table.py

IMPORTANT:

    This module must NEVER import itself.
"""

from __future__ import annotations

import re
from datetime import datetime

from app.models.table import (
    Table,
    TableCell,
)


# ============================================================
# CONSTANTS
# ============================================================


NORMALIZATION_VERSION = "3.1.4.3"


# ============================================================
# DATE FORMATS
# ============================================================

DATE_FORMATS = (
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d.%m.%Y",
)


# ============================================================
# CURRENCY PATTERNS
# ============================================================

CURRENCY_PATTERNS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "EGP": "EGP",
}


# ============================================================
# STATUS DICTIONARY
# ============================================================

STATUS_DICTIONARY = {
    "done": "DONE",
    "completed": "COMPLETED",
    "complete": "COMPLETED",
    "not": "NOT",
    "pending": "PENDING",
    "open": "OPEN",
    "closed": "CLOSED",
    "cancelled": "CANCELLED",
    "canceled": "CANCELLED",
    "approved": "APPROVED",
    "rejected": "REJECTED",
    "in progress": "IN_PROGRESS",
    "in-progress": "IN_PROGRESS",
}


# ============================================================
# PUBLIC API
# ============================================================


def normalize_table_values(table: Table,) -> Table:
    """
    Normalize semantic values for every table cell.

    The Table object is modified in-place and then returned.

    raw_text is NEVER modified.

    text is NEVER replaced with normalized_value.

    Normalized information is stored in:

        cell.normalized_value
        cell.semantic_type
        cell.normalization_source
        cell.data_type

    Returns
    -------

    Table
        The same Table instance after normalization.
    """

    for cell in table.cells:
        normalize_cell_value(cell)

    # --------------------------------------------------------
    # Store normalization version when supported
    # --------------------------------------------------------

    if hasattr(
        table,
        "normalization_version",
    ):

        table.normalization_version = (
            NORMALIZATION_VERSION
        )

    return table


# ============================================================
# CELL NORMALIZATION
# ============================================================


def normalize_cell_value(
    cell: TableCell,
) -> None:
    """
    Normalize one TableCell.

    Processing priority:

        1. Empty
        2. Date
        3. Percentage
        4. Currency
        5. Number
        6. Status
        7. Identifier
        8. Text

    The original value remains untouched.
    """

    # --------------------------------------------------------
    # Determine source value
    # --------------------------------------------------------

    value = get_source_value(
        cell
    )

    value = value.strip()

    # --------------------------------------------------------
    # EMPTY
    # --------------------------------------------------------

    if not value:

        set_normalized_result(
            cell=cell,
            normalized_value=None,
            semantic_type="empty",
            data_type="empty",
            source="empty_value",
        )

        return

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    date_result = parse_date(
        value
    )

    if date_result is not None:

        set_normalized_result(
            cell=cell,
            normalized_value=date_result,
            semantic_type="date",
            data_type="date",
            source="date_parser",
        )

        return

    # --------------------------------------------------------
    # PERCENTAGE
    # --------------------------------------------------------

    percentage_result = parse_percentage(
        value
    )

    if percentage_result is not None:

        set_normalized_result(
            cell=cell,
            normalized_value=percentage_result,
            semantic_type="percentage",
            data_type="percentage",
            source="percentage_parser",
        )

        return

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    currency_result = parse_currency(
        value
    )

    if currency_result is not None:

        numeric_value, currency = (
            currency_result
        )

        set_normalized_result(
            cell=cell,
            normalized_value=numeric_value,
            semantic_type=f"currency:{currency}",
            data_type="number",
            source="currency_parser",
        )

        return

    # --------------------------------------------------------
    # NUMBER
    # --------------------------------------------------------

    number_result = parse_number(
        value
    )

    if number_result is not None:

        if isinstance(
            number_result,
            int,
        ):

            data_type = "integer"

        else:

            data_type = "float"

        set_normalized_result(
            cell=cell,
            normalized_value=number_result,
            semantic_type="number",
            data_type=data_type,
            source="numeric_parser",
        )

        return

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_result = normalize_status(
        value
    )

    if status_result is not None:

        set_normalized_result(
            cell=cell,
            normalized_value=status_result,
            semantic_type="status",
            data_type="string",
            source="status_dictionary",
        )

        return

    # --------------------------------------------------------
    # ENGINEERING / MATERIAL IDENTIFIER
    # --------------------------------------------------------

    if looks_like_identifier(
        value
    ):

        set_normalized_result(
            cell=cell,
            normalized_value=value,
            semantic_type="identifier",
            data_type="string",
            source="identifier_pattern",
        )

        return

    # --------------------------------------------------------
    # NORMAL TEXT
    # --------------------------------------------------------

    set_normalized_result(
        cell=cell,
        normalized_value=value,
        semantic_type="text",
        data_type="string",
        source="text_fallback",
    )


# ============================================================
# SOURCE VALUE
# ============================================================


def get_source_value(
    cell: TableCell,
) -> str:
    """
    Determine the best source value for semantic normalization.

    Priority:

        normalized_text
            ↓
        text
            ↓
        raw_text
            ↓
        empty string

    Important:

        raw_text itself is never changed.
    """

    normalized_text = getattr(
        cell,
        "normalized_text",
        None,
    )

    if normalized_text is not None:

        return str(
            normalized_text
        )

    if cell.text:

        return str(
            cell.text
        )

    if cell.raw_text:

        return str(
            cell.raw_text
        )

    return ""


# ============================================================
# RESULT STORAGE
# ============================================================


def set_normalized_result(
    cell: TableCell,
    normalized_value,
    semantic_type: str,
    data_type: str,
    source: str,
) -> None:
    """
    Store normalization results safely.

    Only fields that exist on TableCell are updated.

    This makes the normalizer compatible with the current
    Pydantic TableCell model while still supporting the
    Phase 3.1.4.3 fields.
    """

    # --------------------------------------------------------
    # Normalized value
    # --------------------------------------------------------

    if hasattr(
        cell,
        "normalized_value",
    ):

        cell.normalized_value = (
            normalized_value
        )

    # --------------------------------------------------------
    # Semantic type
    # --------------------------------------------------------

    if hasattr(
        cell,
        "semantic_type",
    ):

        cell.semantic_type = (
            semantic_type
        )

    # --------------------------------------------------------
    # Data type
    # --------------------------------------------------------

    cell.data_type = data_type

    # --------------------------------------------------------
    # Normalization source
    # --------------------------------------------------------

    if hasattr(
        cell,
        "normalization_source",
    ):

        cell.normalization_source = (
            source
        )


# ============================================================
# DATE PARSER
# ============================================================


def parse_date(
    value: str,
) -> str | None:
    """
    Parse supported date formats.

    Returns ISO format:

        YYYY-MM-DD

    Examples:

        26-05-2025
            ↓
        2025-05-26

        8/9/2026
            ↓
        2026-09-08
    """

    value = value.strip()

    if not value:
        return None

    for date_format in DATE_FORMATS:

        try:

            parsed = datetime.strptime(
                value,
                date_format,
            )

            return parsed.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            continue

    return None


# ============================================================
# PERCENTAGE PARSER
# ============================================================


def parse_percentage(
    value: str,
) -> float | None:
    """
    Parse percentage values.

    Examples:

        95%
        12.5 %
        -5%
        +20%
    """

    value = value.strip()

    match = re.fullmatch(
        r"([-+]?\d+(?:\.\d+)?)\s*%",
        value,
    )

    if not match:

        return None

    try:

        return float(
            match.group(1)
        )

    except ValueError:

        return None


# ============================================================
# CURRENCY PARSER
# ============================================================


def parse_currency(
    value: str,
) -> tuple[float, str] | None:
    """
    Parse monetary values.

    Supported currencies:

        USD
        EUR
        GBP
        EGP

    Examples:

        $1,250
        €500
        £2,000
        EGP 100000
        USD 1250
        1250 EGP
    """

    normalized = (
        value
        .strip()
        .upper()
    )

    if not normalized:
        return None

    detected_currency: str | None = None

    # --------------------------------------------------------
    # Currency symbols
    # --------------------------------------------------------

    for symbol, currency in (
        CURRENCY_PATTERNS.items()
    ):

        if symbol in normalized:

            detected_currency = currency

            normalized = normalized.replace(
                symbol,
                "",
            )

            break

    # --------------------------------------------------------
    # Currency code at beginning
    # --------------------------------------------------------

    if detected_currency is None:

        for code in (
            "USD",
            "EUR",
            "GBP",
            "EGP",
        ):

            if normalized.startswith(
                code
            ):

                detected_currency = code

                normalized = (
                    normalized[
                        len(code):
                    ].strip()
                )

                break

    # --------------------------------------------------------
    # Currency code at end
    # --------------------------------------------------------

    if detected_currency is None:

        for code in (
            "USD",
            "EUR",
            "GBP",
            "EGP",
        ):

            if normalized.endswith(
                code
            ):

                detected_currency = code

                normalized = (
                    normalized[
                        :-len(code)
                    ].strip()
                )

                break

    # --------------------------------------------------------
    # No currency
    # --------------------------------------------------------

    if detected_currency is None:

        return None

    # --------------------------------------------------------
    # Parse numeric component
    # --------------------------------------------------------

    numeric = parse_number(
        normalized
    )

    if numeric is None:

        return None

    return (
        float(numeric),
        detected_currency,
    )


# ============================================================
# NUMBER PARSER
# ============================================================


def parse_number(
    value: str,
) -> int | float | None:
    """
    Parse integer or decimal numbers.

    Supports:

        2
        1250
        1,250
        1,250,000
        1,250.50
        -25
        +25
        0.75
    """

    normalized = (
        value
        .strip()
        .replace(",", "")
        .replace(" ", "")
    )

    if not normalized:
        return None

    # --------------------------------------------------------
    # Integer
    # --------------------------------------------------------

    if re.fullmatch(
        r"[-+]?\d+",
        normalized,
    ):

        try:

            return int(
                normalized
            )

        except ValueError:

            return None

    # --------------------------------------------------------
    # Decimal
    # --------------------------------------------------------

    if re.fullmatch(
        r"[-+]?(?:\d+\.\d*|\.\d+)",
        normalized,
    ):

        try:

            return float(
                normalized
            )

        except ValueError:

            return None

    return None


# ============================================================
# STATUS NORMALIZATION
# ============================================================


def normalize_status(
    value: str,
) -> str | None:
    """
    Normalize known status values.

    Examples:

        Done
            ↓
        DONE

        Completed
            ↓
        COMPLETED

        In Progress
            ↓
        IN_PROGRESS

    Unknown text returns None.
    """

    normalized = (
        value
        .strip()
        .lower()
    )

    if not normalized:
        return None

    return STATUS_DICTIONARY.get(
        normalized
    )


# ============================================================
# IDENTIFIER DETECTION
# ============================================================


def looks_like_identifier(
    value: str,
) -> bool:
    """
    Detect common engineering/material identifiers.

    Examples:

        AHU-B50
        EXF-B40
        FFP-B21
        MEP-001
        HVAC-200-A

    Rules:

        - No spaces
        - Starts with 2-10 letters
        - Contains at least one '-' or '_'
        - Contains alphanumeric segments
    """

    value = value.strip()

    if not value:
        return False

    if " " in value:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-z]{2,10}"
            r"(?:[-_][A-Za-z0-9]+)+",
            value,
        )
    )