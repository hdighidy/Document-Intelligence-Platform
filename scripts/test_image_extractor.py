"""
Phase 3.1.12.3
Document Image Extraction Test
"""

from pathlib import Path

from app.extraction.image_extractor import (
    extract_images_from_pdf,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "sample.pdf"
)

DOCUMENT_ID = (
    "DOC-IMAGE-3.1.12.3"
)


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.12.3 — IMAGE EXTRACTION"
    )
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1 — Input
    # ---------------------------------------------------------

    print("\nTEST 1 — INPUT")

    assert PDF_PATH.exists()

    print(
        "[PASS] Sample PDF exists"
    )

    assert PDF_PATH.is_file()

    print(
        "[PASS] Sample PDF is a file"
    )

    # ---------------------------------------------------------
    # TEST 2 — Extraction
    # ---------------------------------------------------------

    print("\nTEST 2 — IMAGE EXTRACTION")

    images = extract_images_from_pdf(
        PDF_PATH,
        DOCUMENT_ID,
    )

    print(
        f"Extracted images: {len(images)}"
    )

    assert images

    print(
        "[PASS] Images extracted"
    )

    # ---------------------------------------------------------
    # TEST 3 — Expected count
    # ---------------------------------------------------------

    print("\nTEST 3 — IMAGE COUNT")

    expected_count = 19

    assert len(images) == expected_count, (
        f"Expected {expected_count}, "
        f"got {len(images)}"
    )

    print(
        f"[PASS] Expected image count: "
        f"{expected_count}"
    )

    # ---------------------------------------------------------
    # TEST 4 — IDs
    # ---------------------------------------------------------

    print("\nTEST 4 — IMAGE IDs")

    image_ids = [
        image.image_id
        for image in images
    ]

    assert len(image_ids) == len(
        set(image_ids)
    )

    print(
        "[PASS] Image IDs are unique"
    )

    assert (
        "P006-I001"
        in image_ids
    )

    assert (
        "P008-I001"
        in image_ids
    )

    assert (
        "P008-I002"
        in image_ids
    )

    print(
        "[PASS] Expected page/image IDs exist"
    )

    # ---------------------------------------------------------
    # TEST 5 — Page numbers
    # ---------------------------------------------------------

    print("\nTEST 5 — PAGE RELATIONSHIPS")

    page_numbers = {
        image.page_number
        for image in images
    }

    expected_pages = {
        6,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
    }

    assert page_numbers == expected_pages

    print(
        "[PASS] Image page relationships correct"
    )

    # ---------------------------------------------------------
    # TEST 6 — XREF
    # ---------------------------------------------------------

    print("\nTEST 6 — PDF XREF")

    for image in images:

        assert (
            image.source_xref
            is not None
        )

        assert (
            image.source_xref > 0
        )

    print(
        "[PASS] All images have valid source xref"
    )

    # ---------------------------------------------------------
    # TEST 7 — Dimensions
    # ---------------------------------------------------------

    print("\nTEST 7 — DIMENSIONS")

    for image in images:

        assert (
            image.width is not None
        )

        assert (
            image.height is not None
        )

        assert image.width > 0
        assert image.height > 0

    print(
        "[PASS] All image dimensions valid"
    )

    # ---------------------------------------------------------
    # TEST 8 — Format
    # ---------------------------------------------------------

    print("\nTEST 8 — IMAGE FORMAT")

    for image in images:

        assert image.image_format

        assert (
            image.image_format
            in {
                "png",
                "jpg",
                "jpeg",
                "jpx",
                "bmp",
                "tiff",
                "tif",
                "gif",
                "webp",
                "bin",
            }
        )

    print(
        "[PASS] Image formats valid"
    )

    # ---------------------------------------------------------
    # TEST 9 — Physical files
    # ---------------------------------------------------------

    print("\nTEST 9 — IMAGE FILES")

    for image in images:

        image_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / DOCUMENT_ID
            / image.image_path
        )

        assert image_file.exists(), (
            f"Missing image file: "
            f"{image_file}"
        )

        assert image_file.is_file()

        assert image_file.stat().st_size > 0

    print(
        "[PASS] All image files exist"
    )

    # ---------------------------------------------------------
    # TEST 10 — Metadata
    # ---------------------------------------------------------

    print("\nTEST 10 — IMAGE METADATA")

    for image in images:

        assert isinstance(
            image.metadata,
            dict,
        )

        assert (
            image.metadata.get(
                "document_id"
            )
            == DOCUMENT_ID
        )

        assert (
            image.metadata.get(
                "xref"
            )
            == image.source_xref
        )

    print(
        "[PASS] Image metadata valid"
    )

    # ---------------------------------------------------------
    # TEST 11 — Coordinates
    # ---------------------------------------------------------

    print("\nTEST 11 — IMAGE COORDINATES")

    coordinates_found = 0

    for image in images:

        if (
            image.x0 is not None
            and image.y0 is not None
            and image.x1 is not None
            and image.y1 is not None
        ):

            coordinates_found += 1

            assert image.x1 >= image.x0
            assert image.y1 >= image.y0

    print(
        "[PASS] Coordinate extraction executed"
    )

    print(
        f"       Images with coordinates: "
        f"{coordinates_found}/{len(images)}"
    )

    # ---------------------------------------------------------
    # TEST 12 — Serialization
    # ---------------------------------------------------------

    print("\nTEST 12 — SERIALIZATION")

    for image in images:

        dumped = image.model_dump()

        assert isinstance(
            dumped,
            dict,
        )

        json_text = (
            image.model_dump_json()
        )

        assert json_text

    print(
        "[PASS] Image serialization works"
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "PHASE 3.1.12.3 RESULTS"
    )
    print("=" * 70)

    print(
        f"Images extracted: {len(images)}"
    )

    print(
        "ALL TESTS PASSED"
    )


if __name__ == "__main__":
    main()