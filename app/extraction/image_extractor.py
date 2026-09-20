"""
Document Image Extraction
==========================

Phase 3.1.12.3

Responsibilities:
    1. Open PDF
    2. Detect embedded images
    3. Extract image binary data
    4. Determine image dimensions
    5. Determine image format
    6. Determine image position on page
    7. Generate canonical image IDs
    8. Persist extracted images
    9. Return DocumentImage objects

This module does NOT:
    - Perform OCR
    - Generate embeddings
    - Perform CLIP inference
    - Generate image captions
    - Perform image classification
"""

from __future__ import annotations

from pathlib import Path

import fitz

from app.config import settings
from app.models.document import DocumentImage


def _build_image_id(
    page_number: int,
    image_index: int,
) -> str:
    """
    Build a deterministic application-level image ID.

    Example:
        P006-I001
        P008-I002
    """

    return (
        f"P{page_number:03d}"
        f"-I{image_index:03d}"
    )


def _build_image_path(
    image_dir: Path,
    image_id: str,
    image_format: str,
) -> Path:
    """
    Build the physical storage path for an extracted image.
    """

    return (
        image_dir
        / f"{image_id}.{image_format}"
    )


def _get_image_rect(
    page: fitz.Page,
    xref: int,
) -> tuple[
    float | None,
    float | None,
    float | None,
    float | None,
]:
    """
    Return the first page rectangle associated with an image.

    An image can theoretically appear more than once on the
    same page. The current canonical DocumentImage represents
    one extracted image instance, so the first rectangle is
    used here.

    Returns
    -------
    tuple
        (x0, y0, x1, y1)

    If no rectangle can be determined, all values are None.
    """

    try:

        rects = page.get_image_rects(
            xref
        )

    except Exception:
        return (
            None,
            None,
            None,
            None,
        )

    if not rects:
        return (
            None,
            None,
            None,
            None,
        )

    rect = rects[0]

    return (
        float(rect.x0),
        float(rect.y0),
        float(rect.x1),
        float(rect.y1),
    )


def extract_images_from_pdf(
    pdf_path: Path,
    document_id: str,
    *,
    output_dir: Path | None = None,
) -> list[DocumentImage]:
    """
    Extract embedded images from a PDF.

    Parameters
    ----------
    pdf_path:
        Source PDF.

    document_id:
        Document identifier used to determine the default
        processed storage location.

    output_dir:
        Optional explicit directory where extracted images
        will be stored.

        When omitted:

            data/processed/{document_id}/images/

    Returns
    -------
    list[DocumentImage]
        Canonical image metadata objects.

    Notes
    -----
    Image IDs are page-local and deterministic:

        P001-I001
        P001-I002
        P002-I001

    The PDF xref is preserved separately as source_xref.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF does not exist: {pdf_path}"
        )

    if not pdf_path.is_file():

        raise ValueError(
            f"PDF path is not a file: {pdf_path}"
        )

    # --------------------------------------------------------
    # Image storage directory
    # --------------------------------------------------------

    if output_dir is None:

        image_dir = (
            settings.processed_dir
            / document_id
            / "images"
        )

    else:

        image_dir = Path(
            output_dir
        )

    image_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Relative path prefix
    # --------------------------------------------------------

    relative_prefix = "images"

    images: list[DocumentImage] = []

    # --------------------------------------------------------
    # Open PDF
    # --------------------------------------------------------

    with fitz.open(pdf_path) as pdf:

        for page_index, page in enumerate(
            pdf
        ):

            page_number = (
                page_index + 1
            )

            # ------------------------------------------------
            # Discover embedded images
            # ------------------------------------------------

            image_infos = page.get_images(
                full=True
            )

            image_counter = 0

            for image_info in image_infos:

                if not image_info:
                    continue

                # PyMuPDF image tuple:
                #
                # (
                #   xref,
                #   smask,
                #   width,
                #   height,
                #   bpc,
                #   colorspace,
                #   alt_colorspace,
                #   name,
                #   filter,
                #   ...
                # )

                xref = int(
                    image_info[0]
                )

                if xref <= 0:
                    continue

                # --------------------------------------------
                # Extract binary image
                # --------------------------------------------

                extracted = pdf.extract_image(
                    xref
                )

                if not extracted:
                    continue

                image_bytes = extracted.get(
                    "image"
                )

                image_format = extracted.get(
                    "ext"
                )

                if not image_bytes:
                    continue

                if not image_format:
                    image_format = "bin"

                image_format = str(
                    image_format
                ).lower()

                # --------------------------------------------
                # Dimensions
                # --------------------------------------------

                width = extracted.get(
                    "width"
                )

                height = extracted.get(
                    "height"
                )

                if width is None:
                    width = image_info[2]

                if height is None:
                    height = image_info[3]

                # --------------------------------------------
                # Generate canonical ID
                # --------------------------------------------

                image_counter += 1

                image_id = _build_image_id(
                    page_number=page_number,
                    image_index=image_counter,
                )

                # --------------------------------------------
                # Determine page position
                # --------------------------------------------

                (
                    x0,
                    y0,
                    x1,
                    y1,
                ) = _get_image_rect(
                    page,
                    xref,
                )

                # --------------------------------------------
                # Physical file
                # --------------------------------------------

                image_file = _build_image_path(
                    image_dir=image_dir,
                    image_id=image_id,
                    image_format=image_format,
                )

                image_file.write_bytes(
                    image_bytes
                )

                # --------------------------------------------
                # Relative document path
                # --------------------------------------------

                image_path = (
                    Path(relative_prefix)
                    / image_file.name
                )

                # --------------------------------------------
                # Additional metadata
                # --------------------------------------------

                metadata = {
                    "document_id": document_id,
                    "xref": xref,
                    "smask": image_info[1],
                    "bits_per_component": image_info[4],
                    "colorspace": image_info[5],
                    "resource_name": image_info[7],
                    "filter": image_info[8],
                    "source_pdf": str(pdf_path),
                    "file_size_bytes": len(
                        image_bytes
                    ),
                }

                # --------------------------------------------
                # Canonical model
                # --------------------------------------------

                document_image = DocumentImage(

                    image_id=image_id,

                    page_number=page_number,

                    source_xref=xref,

                    width=int(width)
                    if width is not None
                    else None,

                    height=int(height)
                    if height is not None
                    else None,

                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,

                    image_format=image_format,

                    image_path=str(
                        image_path
                    ),

                    metadata=metadata,
                )

                images.append(
                    document_image
                )

    return images


__all__ = [
    "extract_images_from_pdf",
]