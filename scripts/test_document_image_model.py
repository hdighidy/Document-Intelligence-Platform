"""
Phase 3.1.12.2
Canonical DocumentImage Model Test
"""

from app.models.document import DocumentImage


def main() -> None:

    print("=" * 70)
    print(
        "PHASE 3.1.12.2 — DOCUMENT IMAGE MODEL"
    )
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1 — Import
    # ---------------------------------------------------------

    print("\nTEST 1 — IMPORT")

    assert DocumentImage is not None

    print("[PASS] DocumentImage imported")

    # ---------------------------------------------------------
    # TEST 2 — Minimal construction
    # ---------------------------------------------------------

    print("\nTEST 2 — MINIMAL MODEL")

    image = DocumentImage()

    assert image.image_id == ""
    assert image.page_number == 1
    assert image.source_xref is None
    assert image.width is None
    assert image.height is None
    assert image.image_format == ""
    assert image.image_path == ""
    assert image.metadata == {}

    print("[PASS] Minimal DocumentImage created")

    # ---------------------------------------------------------
    # TEST 3 — Full construction
    # ---------------------------------------------------------

    print("\nTEST 3 — FULL MODEL")

    image = DocumentImage(
        image_id="P008-I001",
        page_number=8,
        source_xref=161,
        width=281,
        height=74,
        x0=72.0,
        y0=100.0,
        x1=353.0,
        y1=174.0,
        image_format="png",
        image_path="images/P008-I001.png",
        metadata={
            "colorspace": "DeviceRGB",
            "bpc": 8,
        },
    )

    assert image.image_id == "P008-I001"
    assert image.page_number == 8
    assert image.source_xref == 161
    assert image.width == 281
    assert image.height == 74
    assert image.image_format == "png"
    assert image.image_path == (
        "images/P008-I001.png"
    )

    print("[PASS] Full DocumentImage created")

    # ---------------------------------------------------------
    # TEST 4 — Serialization
    # ---------------------------------------------------------

    print("\nTEST 4 — SERIALIZATION")

    dumped = image.model_dump()

    assert isinstance(dumped, dict)
    assert dumped["image_id"] == "P008-I001"
    assert dumped["page_number"] == 8
    assert dumped["source_xref"] == 161

    print("[PASS] model_dump() works")

    json_text = image.model_dump_json()

    assert json_text
    assert "P008-I001" in json_text

    print("[PASS] model_dump_json() works")

    # ---------------------------------------------------------
    # TEST 5 — Metadata isolation
    # ---------------------------------------------------------

    print("\nTEST 5 — DEFAULT METADATA ISOLATION")

    image_a = DocumentImage()
    image_b = DocumentImage()

    image_a.metadata["test"] = "A"

    assert image_b.metadata == {}

    print("[PASS] metadata uses independent default")

    # ---------------------------------------------------------
    # TEST 6 — Page relationship
    # ---------------------------------------------------------

    print("\nTEST 6 — PAGE RELATIONSHIP")

    assert image.page_number == 8

    print(
        "[PASS] Image page relationship preserved"
    )

    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "PHASE 3.1.12.2 RESULTS"
    )
    print("=" * 70)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()