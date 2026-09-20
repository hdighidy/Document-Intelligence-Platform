from pathlib import Path

from app.extraction.structure_analyzer import (
    analyze_document_structure,
)

from app.extraction.text_extractor import (
    extract_text_from_pdf,
)

from app.validation.structure_visualizer import (
    visualize_page,
)


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = Path(
    r"data\test\sample.pdf"
)

PAGE_NUMBER = 2


# ============================================================
# MAIN
# ============================================================


def main():

    print(
        "Loading PDF..."
    )

    pages = extract_text_from_pdf(
        PDF_PATH
    )

    print(
        f"Extracted {len(pages)} pages."
    )

    print(
        "Analyzing document structure..."
    )

    pages = analyze_document_structure(
        pages
    )

    print(
        "Generating visualization..."
    )

    output = visualize_page(
        pdf_path=PDF_PATH,
        pages=pages,
        page_number=PAGE_NUMBER,
    )

    print(
        f"Visualization created:"
    )

    print(
        output
    )


if __name__ == "__main__":

    main()