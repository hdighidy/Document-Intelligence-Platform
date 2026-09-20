from pathlib import Path

import fitz

from app.models.document import (
    PageText,
    TextBlock,
)


def extract_text_from_pdf(
    pdf_path: Path,
) -> list[PageText]:

    pages = []

    with fitz.open(pdf_path) as pdf:

        for page_index, page in enumerate(pdf):

            page_number = page_index + 1

            page_text = PageText(
                page_number=page_number,
                width=page.rect.width,
                height=page.rect.height,
                blocks=[],
            )

            blocks = page.get_text(
                "dict"
            ).get("blocks", [])

            block_counter = 0

            for block in blocks:

                # Ignore image blocks
                if block.get("type") != 0:
                    continue

                lines = block.get(
                    "lines",
                    []
                )

                for line in lines:

                    spans = line.get(
                        "spans",
                        []
                    )

                    if not spans:
                        continue

                    text_parts = []

                    for span in spans:

                        span_text = span.get(
                            "text",
                            ""
                        )

                        if span_text:
                            text_parts.append(
                                span_text
                            )

                    text = "".join(
                        text_parts
                    ).strip()

                    if not text:
                        continue

                    # --------------------------------
                    # Bounding box
                    # --------------------------------

                    x0, y0, x1, y1 = line.get(
                        "bbox",
                        [0, 0, 0, 0]
                    )

                    # --------------------------------
                    # Typography
                    # --------------------------------

                    first_span = spans[0]

                    font = first_span.get(
                        "font"
                    )

                    font_size = first_span.get(
                        "size"
                    )

                    flags = first_span.get(
                        "flags",
                        0
                    )

                    color = first_span.get(
                        "color"
                    )

                    bold = bool(
                        flags & 16
                    )

                    italic = bool(
                        flags & 2
                    )

                    block_counter += 1

                    text_block = TextBlock(

                        block_id=(
                            f"P{page_number:03d}"
                            f"-B{block_counter:03d}"
                        ),

                        page_number=page_number,

                        text=text,

                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,

                        font=font,

                        font_size=font_size,

                        bold=bold,

                        italic=italic,

                        color=color,

                    )

                    page_text.blocks.append(
                        text_block
                    )

            pages.append(
                page_text
            )

    return pages