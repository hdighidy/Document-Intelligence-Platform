from app.models.content_unit import (
    ContentUnit,
    ContentUnitType,
)


def main() -> None:

    text_unit = ContentUnit(
        content_unit_id="CU-P001-T001",
        document_id="DOC-001",
        unit_type=ContentUnitType.TEXT,
        page_number=1,
        source_id="P001-B001",
        text="METHOD STATEMENT",
        reading_order=1,
    )

    table_unit = ContentUnit(
        content_unit_id="CU-P001-TBL001",
        document_id="DOC-001",
        unit_type=ContentUnitType.TABLE,
        page_number=1,
        source_id="TABLE-001",
        text="Equipment | Quantity",
        reading_order=2,
    )

    image_unit = ContentUnit(
        content_unit_id="CU-P006-I001",
        document_id="DOC-001",
        unit_type=ContentUnitType.IMAGE,
        page_number=6,
        source_id="P006-I001",
    )

    assert text_unit.is_text
    assert table_unit.is_table
    assert image_unit.is_image

    assert text_unit.source_id == "P001-B001"
    assert table_unit.source_id == "TABLE-001"
    assert image_unit.source_id == "P006-I001"

    assert (
        text_unit.model_dump(mode="json")["unit_type"]
        == "TEXT"
    )

    assert (
        table_unit.model_dump(mode="json")["unit_type"]
        == "TABLE"
    )

    assert (
        image_unit.model_dump(mode="json")["unit_type"]
        == "IMAGE"
    )

    print("ContentUnit model: PASS")
    print("TEXT: PASS")
    print("TABLE: PASS")
    print("IMAGE: PASS")
    print("Serialization: PASS")
    print("\nPHASE 3.2.1 — ALL TESTS PASSED")


if __name__ == "__main__":
    main()