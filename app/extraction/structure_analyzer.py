"""
Document Structure Analyzer
============================

Phase 2.2

Responsibilities:
    1. Document-level font statistics
    2. Header detection
    3. Footer detection
    4. Page-number detection
    5. Reading-order detection
    6. Basic column detection
    7. Text structure classification

This module does NOT:
    - Perform OCR
    - Extract tables
    - Extract images
    - Generate embeddings
    - Perform RAG
"""

from collections import Counter
import re

from app.models.document import (
    PageText,
    TextBlock,
)


# ============================================================
# PUBLIC FUNCTION
# ============================================================


def analyze_document_structure(
    pages: list[PageText],
) -> list[PageText]:
    """
    Analyze the complete PDF document.

    The analysis is performed at document level rather
    than independently for each page.

    Processing steps:

        1. Calculate document font statistics
        2. Detect repeated headers
        3. Detect repeated footers
        4. Detect reading order
        5. Detect document structure

    Args:
        pages:
            List of extracted PDF pages.

    Returns:
        The same pages with enriched TextBlock information.
    """

    if not pages:
        return pages

    # --------------------------------------------------------
    # 1. Document-level font statistics
    # --------------------------------------------------------

    average_font_size = calculate_average_font_size(
        pages
    )

    # --------------------------------------------------------
    # 2. Detect repeated headers
    # --------------------------------------------------------

    header_texts = detect_repeated_headers(
        pages
    )

    # --------------------------------------------------------
    # 3. Detect repeated footers
    # --------------------------------------------------------

    footer_texts = detect_repeated_footers(
        pages
    )

    # --------------------------------------------------------
    # 4. Analyze each page
    # --------------------------------------------------------

    for page in pages:

        # --------------------------------------------
        # Determine reading order
        # --------------------------------------------

        sort_blocks_by_reading_order(
            page
        )

        # --------------------------------------------
        # Classify blocks
        # --------------------------------------------

        for reading_order, block in enumerate(
            page.blocks,
            start=1,
        ):

            block.reading_order = reading_order

            normalized_text = normalize_text(
                block.text
            )

            # Reset flags
            block.is_header = False
            block.is_footer = False

            # ----------------------------------------
            # Header detection
            # ----------------------------------------

            if normalized_text in header_texts:

                block.is_header = True
                block.structure = "header"

                continue

            # ----------------------------------------
            # Footer detection
            # ----------------------------------------

            if normalized_text in footer_texts:

                block.is_footer = True
                block.structure = "footer"

                continue

            # ----------------------------------------
            # Page number detection
            # ----------------------------------------

            if (
                block.y1 >= page.height * 0.88
                and is_page_number(
                    block.text
                )
            ):

                block.is_footer = True
                block.structure = "footer"

                continue

            # ----------------------------------------
            # Normal structure classification
            # ----------------------------------------

            block.structure = classify_block(
                block=block,
                average_font_size=average_font_size,
            )

    return pages


# ============================================================
# FONT STATISTICS
# ============================================================


def calculate_average_font_size(
    pages: list[PageText],
) -> float:
    """
    Calculate the average font size across
    the complete document.
    """

    sizes: list[float] = []

    for page in pages:

        for block in page.blocks:

            if block.font_size is not None:

                sizes.append(
                    block.font_size
                )

    if not sizes:
        return 10.0

    return sum(sizes) / len(sizes)


# ============================================================
# HEADER DETECTION
# ============================================================


def detect_repeated_headers(
    pages: list[PageText],
) -> set[str]:
    """
    Detect text repeated near the top of multiple pages.

    A block is considered a header candidate when its
    vertical position is within the top 12% of the page.
    """

    candidates: list[str] = []

    for page in pages:

        for block in page.blocks:

            if block.y0 <= page.height * 0.12:

                text = normalize_text(
                    block.text
                )

                if text:

                    candidates.append(
                        text
                    )

    return find_repeated_text(
        candidates=candidates,
        page_count=len(pages),
    )


# ============================================================
# FOOTER DETECTION
# ============================================================


def detect_repeated_footers(
    pages: list[PageText],
) -> set[str]:
    """
    Detect text repeated near the bottom of multiple pages.

    A block is considered a footer candidate when its
    bottom coordinate is within the bottom 12% of the page.
    """

    candidates: list[str] = []

    for page in pages:

        for block in page.blocks:

            if block.y1 >= page.height * 0.88:

                text = normalize_text(
                    block.text
                )

                if text:

                    candidates.append(
                        text
                    )

    return find_repeated_text(
        candidates=candidates,
        page_count=len(pages),
    )


# ============================================================
# REPEATED TEXT DETECTION
# ============================================================


def find_repeated_text(
    candidates: list[str],
    page_count: int,
) -> set[str]:
    """
    Find text appearing repeatedly across pages.

    Current rule:
        - At least 2 occurrences
        - OR approximately 20% of the document pages

    Examples:

        SIAC PROJECT
        Technical Specification
        Confidential
    """

    if not candidates:
        return set()

    counts = Counter(
        candidates
    )

    repeated: set[str] = set()

    minimum_occurrences = max(
        2,
        int(page_count * 0.20),
    )

    for text, count in counts.items():

        if count >= minimum_occurrences:

            repeated.add(
                text
            )

    return repeated


# ============================================================
# READING ORDER
# ============================================================


def sort_blocks_by_reading_order(
    page: PageText,
) -> None:
    """
    Determine a basic reading order for a page.

    Strategy:

        Single column:
            Top -> Bottom

        Two columns:
            Left column -> Right column

    This is intentionally a baseline implementation.
    Complex layouts will be improved later.
    """

    columns = detect_columns(
        page
    )

    # --------------------------------------------------------
    # Single-column page
    # --------------------------------------------------------

    if len(columns) == 1:

        page.blocks.sort(
            key=lambda block: (
                block.y0,
                block.x0,
            )
        )

        return

    # --------------------------------------------------------
    # Multi-column page
    # --------------------------------------------------------

    ordered_blocks: list[TextBlock] = []

    for column in columns:

        column.sort(
            key=lambda block: (
                block.y0,
                block.x0,
            )
        )

        ordered_blocks.extend(
            column
        )

    page.blocks = ordered_blocks


# ============================================================
# COLUMN DETECTION
# ============================================================


def detect_columns(
    page: PageText,
) -> list[list[TextBlock]]:
    """
    Detect basic one-column vs two-column layouts.

    The page is divided around its horizontal center.

    This is NOT a full document-layout engine.
    """

    # Not enough blocks to justify column detection
    if len(page.blocks) < 4:

        return [
            page.blocks
        ]

    page_center = page.width / 2

    left_column: list[TextBlock] = []

    right_column: list[TextBlock] = []

    for block in page.blocks:

        block_center = (
            block.x0 + block.x1
        ) / 2

        if block_center < page_center:

            left_column.append(
                block
            )

        else:

            right_column.append(
                block
            )

    # --------------------------------------------------------
    # If one side contains very few blocks,
    # treat the page as single-column.
    # --------------------------------------------------------

    if (
        len(left_column) < 2
        or len(right_column) < 2
    ):

        return [
            page.blocks
        ]

    return [
        left_column,
        right_column,
    ]


# ============================================================
# STRUCTURE CLASSIFICATION
# ============================================================


def classify_block(
    block: TextBlock,
    average_font_size: float,
) -> str:
    """
    Classify a text block into a basic document structure.

    Possible values:

        title
        heading
        subheading
        list_item
        paragraph
    """

    text = block.text.strip()

    font_size = (
        block.font_size
        if block.font_size is not None
        else average_font_size
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if (
        block.bold
        and font_size >= average_font_size * 1.60
        and len(text) < 150
    ):

        return "title"

    # --------------------------------------------------------
    # HEADING
    # --------------------------------------------------------

    if (
        block.bold
        and font_size >= average_font_size * 1.30
        and len(text) < 200
    ):

        return "heading"

    # --------------------------------------------------------
    # SUBHEADING
    # --------------------------------------------------------

    if (
        block.bold
        and font_size >= average_font_size * 1.10
        and len(text) < 250
    ):

        return "subheading"

    # --------------------------------------------------------
    # LIST ITEM
    # --------------------------------------------------------

    if is_list_item(text):

        return "list_item"

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "paragraph"


# ============================================================
# LIST DETECTION
# ============================================================


def is_list_item(
    text: str,
) -> bool:
    """
    Detect common list-item formats.

    Examples:

        - Item
        • Item
        * Item
        1. Item
        1) Item
        A. Item
        A) Item
        (a) Item
        (1) Item
    """

    patterns = [

        # Bullet
        r"^[-•*]\s+",

        # Numeric
        r"^\d+[.)]\s+",

        # Alphabetic
        r"^[A-Za-z][.)]\s+",

        # Parentheses
        r"^\([A-Za-z0-9]+\)\s+",

    ]

    return any(
        re.match(
            pattern,
            text
        )
        for pattern in patterns
    )


# ============================================================
# PAGE NUMBER DETECTION
# ============================================================


def is_page_number(
    text: str,
) -> bool:
    """
    Detect common page-number formats.

    Examples:

        Page 1
        Page 25
        1 / 25
        5/25
        1
        Page 5 of 25
    """

    normalized = (
        text.strip()
        .lower()
    )

    patterns = [

        # Page 1
        r"^page\s+\d+$",

        # Page 5 of 25
        r"^page\s+\d+\s+of\s+\d+$",

        # 1 / 25
        r"^\d+\s*/\s*\d+$",

        # 1
        r"^\d+$",

    ]

    return any(
        re.match(
            pattern,
            normalized
        )
        for pattern in patterns
    )


# ============================================================
# TEXT NORMALIZATION
# ============================================================


def normalize_text(
    text: str,
) -> str:
    """
    Normalize text for comparison.

    Example:

        '  SIAC   PROJECT  '
        
    becomes:

        'siac project'
    """

    return " ".join(
        text.lower().split()
    )