"""FastAPI application — DocuMind RAG Backend."""

import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    QueryRequest,
    QueryResponse,
    UploadResponse,
    DocumentListResponse,
)
from app.document_processor import load_document, chunk_documents
from app.vector_store import add_documents, list_indexed_sources, clear_vector_store
from app.rag_chain import query as rag_query

app = FastAPI(
    title="DocuMind API",
    description="RAG-based Document Q&A Assistant",
    version="1.0.0",
)

# CORS — allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or DOCX document, process, chunk, and index it."""

    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50 MB limit.")

    # Save to disk
    safe_filename = Path(file.filename).name  # prevent path traversal
    save_path = settings.upload_dir / safe_filename
    save_path.write_bytes(contents)

    try:
        # Load → chunk → embed → index
        raw_docs = load_document(save_path)
        chunks = chunk_documents(raw_docs)
        add_documents(chunks)
    except Exception as e:
        # Clean up the saved file on failure
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return UploadResponse(
        filename=safe_filename,
        chunks=len(chunks),
        message=f"Successfully processed '{safe_filename}' into {len(chunks)} chunks.",
    )


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """Ask a question about the uploaded documents."""
    history = [{"role": m.role, "content": m.content} for m in request.chat_history]
    result = rag_query(request.question, history)
    return QueryResponse(answer=result["answer"], sources=result["sources"])


@app.get("/documents", response_model=DocumentListResponse)
def list_documents():
    """List all indexed document sources."""
    return DocumentListResponse(documents=list_indexed_sources())


@app.delete("/documents")
def delete_all_documents():
    """Clear the vector store and remove all uploaded files."""
    clear_vector_store()
    # Remove uploaded files
    for f in settings.upload_dir.iterdir():
        if f.is_file():
            f.unlink()
    return {"message": "All documents and index cleared."}
