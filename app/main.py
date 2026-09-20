import asyncio
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.ingestion.service import ingest_pdf
from app.ingestion.validator import PDFValidationError


# ==========================================
# Create FastAPI Application
# ==========================================

app = FastAPI(
    title="Document Intelligence Platform",
    version="0.1.0",
)


# ==========================================
# Health Check
# ==========================================

@app.get("/")
def health_check():

    return {
        "status": "running",
        "service": "Document Intelligence Platform",
        "phase": "PDF Ingestion",
    }


# ==========================================
# PDF Upload
# ==========================================

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    suffix = Path(file.filename).suffix.lower()

    if suffix != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    temp_path = None

    try:

        # Create temporary PDF file

        with NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp:

            temp_path = Path(temp.name) 

            while chunk := await file.read(1024 * 1024):

                temp.write(chunk)

        # Send PDF to ingestion service.
        #
        # ingest_pdf() is fully synchronous (PDF parsing, hashing,
        # disk I/O). Running it directly here would block the
        # entire async event loop for the duration of processing,
        # preventing this server from handling any other request
        # concurrently. Offload it to the default thread pool.

        loop = asyncio.get_running_loop()

        metadata = await loop.run_in_executor(
            None,
            partial(
                ingest_pdf,
                source_file=temp_path,
                original_filename=file.filename,
            ),
        )

        return {
            "status": "success",
            "document": metadata.model_dump(mode="json"),
        }

    except PDFValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        )

    finally:

        if temp_path:

            temp_path.unlink(
                missing_ok=True
            )