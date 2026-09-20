"""
Canonical StructuredDocument Storage
====================================

Phase 3.1.13

Responsibilities:
    1. Persist StructuredDocument as JSON.
    2. Load StructuredDocument from JSON.
    3. Preserve the canonical Pydantic model structure.
"""

from __future__ import annotations


import json
import os
import tempfile
from pathlib import Path
from typing import Any
from datetime import datetime

from app.config import settings
from app.models.document import StructuredDocument

from app.models.document import (
    DocumentMetadata,
    DocumentPage,
    StructuredDocument,
)

from app.models.table import (
    Table) 
from app.models.document import (
    DocumentImage,)



def _atomic_write_json(
    output_file: Path,
    data: dict[str, Any],
) -> None:
    """
    Atomically persist JSON data.

    The JSON is first written to a temporary file in the
    same directory as the final destination.

    Once the temporary file has been completely written and
    flushed, os.replace() atomically replaces the destination.

    This prevents the final JSON file from being left partially
    written if the process fails during serialization/write.
    """

    output_file = Path(output_file)

    output_dir = output_file.parent

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file: Path | None = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_dir,
            prefix=f".{output_file.stem}.",
            suffix=".tmp",
            delete=False,
        ) as temp:

            temporary_file = Path(
                temp.name
            )

            json.dump(
                data,
                temp,
                indent=4,
                ensure_ascii=False,
            )

            temp.flush()

            os.fsync(
                temp.fileno()
            )

        os.replace(
            temporary_file,
            output_file,
        )

        temporary_file = None

    finally:

        if (
            temporary_file is not None
            and temporary_file.exists()
        ):

            try:
                temporary_file.unlink()

            except OSError:
                pass


def save_structured_document(
    document: StructuredDocument,
) -> Path:
    """
    Persist a canonical StructuredDocument atomically.

    Storage:

        data/processed/{document_id}/
            structured_document.json

    Returns
    -------
    Path
        Path to the persisted JSON file.
    """

    output_dir = (
        settings.processed_dir
        / document.document_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "structured_document.json"
    )

    data = document.model_dump(
        mode="json"
    )

    _atomic_write_json(
        output_file=output_file,
        data=data,
    )

    return output_file


def load_structured_document(
    document_id: str,
    pdf_path: Path | None = None,
    metadata: DocumentMetadata | None = None,
    pages: list[DocumentPage] | None = None,
    tables: list[Table] | None = None,
    images: list[DocumentImage] | None = None,
    extra_metadata: dict[str, Any] | None = None,
    started_at: datetime | None = None,
) -> StructuredDocument:
    """
    Load a persisted canonical StructuredDocument.

    """

    input_file = (
        settings.processed_dir
        / document_id
        / "structured_document.json"
    )

    

    if not input_file.exists():

        raise FileNotFoundError(
            f"Structured document not found: "
            f"{input_file}"
        )

    data = json.loads(
        input_file.read_text(
            encoding="utf-8"
        )
    )

    return StructuredDocument.model_validate(
        data
    )


__all__ = [
    "save_structured_document",
    "load_structured_document",
]