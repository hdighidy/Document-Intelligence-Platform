import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import fitz

from app.models.document import PDFMetadata


# PDF date format: D:YYYYMMDDHHmmSS+HH'mm' (or Z, or truncated)
# Example: D:20230415120000+00'00'
_PDF_DATE_RE = re.compile(
    r"^D:(?P<year>\d{4})(?P<month>\d{2})?(?P<day>\d{2})?"
    r"(?P<hour>\d{2})?(?P<minute>\d{2})?(?P<second>\d{2})?"
    r"(?P<tz>[+\-Z])?(?P<tz_hour>\d{2})?'?(?P<tz_minute>\d{2})?'?"
)


def _parse_pdf_date(raw: str | None) -> datetime | None:
    """
    Parse a raw PDF metadata date string into a timezone-aware datetime.

    PyMuPDF returns dates in the native PDF format (ISO 8601-like but
    not ISO compliant), e.g. "D:20230415120000+00'00'". Malformed or
    missing dates return None rather than raising, since this is
    metadata enrichment, not critical-path data.
    """

    if not raw:
        return None

    match = _PDF_DATE_RE.match(raw)

    if not match:
        return None

    parts = match.groupdict()

    try:
        dt = datetime(
            year=int(parts["year"]),
            month=int(parts["month"] or 1),
            day=int(parts["day"] or 1),
            hour=int(parts["hour"] or 0),
            minute=int(parts["minute"] or 0),
            second=int(parts["second"] or 0),
        )
    except ValueError:
        return None

    tz_sign = parts["tz"]

    if tz_sign in ("+", "-"):
        tz_hour = int(parts["tz_hour"] or 0)
        tz_minute = int(parts["tz_minute"] or 0)
        offset = timedelta(hours=tz_hour, minutes=tz_minute)

        if tz_sign == "-":
            offset = -offset

        dt = dt.replace(tzinfo=timezone(offset))
    else:
        # "Z" or missing timezone info: assume UTC
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def extract_pdf_metadata(file_path: Path) -> PDFMetadata:

    document = fitz.open(file_path)

    metadata = document.metadata or {}

    result = PDFMetadata(
        page_count=document.page_count,

        title=metadata.get("title") or None,

        author=metadata.get("author") or None,

        subject=metadata.get("subject") or None,

        keywords=metadata.get("keywords") or None,

        creator=metadata.get("creator") or None,

        producer=metadata.get("producer") or None,

        creation_date=_parse_pdf_date(metadata.get("creationDate")),

        modification_date=_parse_pdf_date(metadata.get("modDate")),
    )

    document.close()

    return result