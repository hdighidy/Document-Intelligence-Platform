import json

from app.config import settings
from app.models.document import DocumentMetadata


# ============================================================
# Registry File
# ============================================================

REGISTRY_FILE = (
    settings.metadata_dir
    / "document_registry.json"
)


# ============================================================
# Internal: Load Registry
# ============================================================

def _load_registry() -> list[dict]:
    """
    Load all registered documents from the registry.

    Returns:
        List of document dictionaries.
    """

    if not REGISTRY_FILE.exists():
        return []

    try:

        content = REGISTRY_FILE.read_text(
            encoding="utf-8"
        )

        if not content.strip():
            return []

        return json.loads(content)

    except json.JSONDecodeError:

        return []


# ============================================================
# Internal: Save Registry
# ============================================================

def _save_registry(
    documents: list[dict],
) -> None:
    """
    Save all documents to the registry.
    """

    settings.metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    REGISTRY_FILE.write_text(
        json.dumps(
            documents,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# Register Document
# ============================================================

def register_document(
    document: DocumentMetadata,
) -> None:
    """
    Add a document to the registry.

    If the document ID already exists,
    the existing record will be updated.
    """

    documents = _load_registry()

    document_data = document.model_dump(
        mode="json"
    )

    document_id = document.document_id

    # ----------------------------------------
    # Update existing document
    # ----------------------------------------

    for index, existing in enumerate(documents):

        if existing.get("document_id") == document_id:

            documents[index] = document_data

            _save_registry(documents)

            return

    # ----------------------------------------
    # Add new document
    # ----------------------------------------

    documents.append(
        document_data
    )

    _save_registry(
        documents
    )


# ============================================================
# Get One Document
# ============================================================

def get_document(
    document_id: str,
) -> DocumentMetadata | None:
    """
    Retrieve a document by its Document ID.
    """

    documents = _load_registry()

    for item in documents:

        if item.get("document_id") == document_id:

            return DocumentMetadata.model_validate(
                item
            )

    return None


# ============================================================
# Get Document By SHA-256
# ============================================================

def get_document_by_sha256(
    sha256: str,
) -> DocumentMetadata | None:
    """
    Retrieve a document by its SHA-256 hash.

    Used to detect duplicate uploads of the same file content
    (regardless of filename) before creating a new document.
    """

    documents = _load_registry()

    for item in documents:

        if item.get("sha256") == sha256:

            return DocumentMetadata.model_validate(
                item
            )

    return None


# ============================================================
# Get All Documents
# ============================================================

def list_documents() -> list[DocumentMetadata]:
    """
    Return all registered documents.
    """

    documents = _load_registry()

    return [
        DocumentMetadata.model_validate(
            item
        )
        for item in documents
    ]


# ============================================================
# Delete Document From Registry
# ============================================================

def delete_document(
    document_id: str,
) -> bool:
    """
    Remove a document from the registry.

    Note:
        This only removes the registry record.
        It does NOT delete the physical PDF.
    """

    documents = _load_registry()

    original_count = len(documents)

    documents = [
        item
        for item in documents
        if item.get("document_id") != document_id
    ]

    if len(documents) == original_count:
        return False

    _save_registry(
        documents
    )

    return True