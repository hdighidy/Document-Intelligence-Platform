"""
Table Detection Visualization
=============================

Phase 3.1.2 QC tool.

Draws detected table bounding boxes
on PDF pages.
"""

from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from app.extraction.table_detector import (
    detect_tables,
)


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = Path(
    r"data\test\sample.pdf"
)

DOCUMENT_ID = (
    "DOC-TEST001"
)

OUTPUT_DIR = Path(
    r"data\validation\tables"
)

SCALE = 2.0


# ============================================================
# MAIN
# ============================================================


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Detecting tables..."
    )

    tables = detect_tables(
        pdf_path=PDF_PATH,
        document_id=DOCUMENT_ID,
    )

    print(
        f"Detected {len(tables)} tables."
    )

    pdf = fitz.open(
        PDF_PATH
    )

    try:

        for page_number in sorted(
            {
                table.page_number
                for table in tables
            }
        ):

            page = pdf[
                page_number - 1
            ]

            matrix = fitz.Matrix(
                SCALE,
                SCALE,
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                (
                    pixmap.width,
                    pixmap.height,
                ),
                pixmap.samples,
            )

            draw = ImageDraw.Draw(
                image
            )

            page_tables = [
                table
                for table in tables
                if table.page_number
                == page_number
            ]

            for index, table in enumerate(
                page_tables,
                start=1,
            ):

                if not table.bbox:
                    continue

                bbox = table.bbox

                x0 = bbox.x0 * SCALE
                y0 = bbox.y0 * SCALE
                x1 = bbox.x1 * SCALE
                y1 = bbox.y1 * SCALE

                draw.rectangle(
                    [
                        x0,
                        y0,
                        x1,
                        y1,
                    ],
                    outline="red",
                    width=5,
                )

                label = (
                    f"TABLE {index}"
                    f" | "
                    f"{table.table_id}"
                )

                draw.text(
                    (
                        x0,
                        max(
                            0,
                            y0 - 20,
                        ),
                    ),
                    label,
                    fill="red",
                )

            output_path = (
                OUTPUT_DIR
                / (
                    f"page_"
                    f"{page_number:03d}"
                    f"_tables.png"
                )
            )

            image.save(
                output_path
            )

            print(
                f"Created: "
                f"{output_path}"
            )

    finally:

        pdf.close()


if __name__ == "__main__":

    main()