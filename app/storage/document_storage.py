import json
from pathlib import Path

from app.config import settings
from app.models.document import PageText
from app.models.table import Table


def save_extracted_text(
    document_id: str,
    pages: list[PageText],
) -> Path:

    output_dir = (
        settings.processed_dir
        / document_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "pages.json"
    )

    data = [
        page.model_dump(mode="json")
        for page in pages
    ]

    output_file.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_file


def save_extracted_tables(
    document_id: str,
    tables: list[Table],
) -> Path:
    """
    Save extracted/cleaned/validated tables as JSON.

    Mirrors save_extracted_text's layout convention:
    data/processed/{document_id}/tables.json
    """

    output_dir = (
        settings.processed_dir
        / document_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "tables.json"
    )

    data = [
        table.model_dump(mode="json")
        for table in tables
    ]

    output_file.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_file