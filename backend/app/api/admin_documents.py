import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.models.db_models import Admin
from app.models.schemas import ApplySuggestionsRequest
from app.services.auth_service import require_teams
from app.services.rag_service import (
    DOCUMENTS_DIR,
    analyze_document,
    apply_suggestions,
    build_index,
    list_documents,
    reload_index,
)

router = APIRouter()


@router.get("/documents", response_model=list[dict])
def get_documents(admin: Admin = Depends(require_teams("cso", "it"))):
    """
    Returns metadata for all PDF files in the documents directory.
    Includes filename, size in bytes, and upload timestamp.
    Accessible by CSO and IT teams only.
    """
    return list_documents()


@router.post("/documents/upload", response_model=dict)
def upload_document(
    file: UploadFile = File(...),
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Uploads a PDF file to the documents directory.
    Rejects non-PDF files. Overwrites existing files with the same name
    so updated rulebooks replace old versions automatically.
    Accessible by CSO and IT teams only.
    """
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    dest_path = os.path.join(DOCUMENTS_DIR, file.filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"{file.filename} uploaded successfully."}


@router.delete("/documents/{filename}", response_model=dict)
def delete_document(
    filename: str,
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Removes a PDF file from the documents directory.
    The RAG index must be rebuilt after deletion via POST /admin/reindex
    for the removal to take effect in retrieval.
    Accessible by CSO and IT teams only.
    """
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"{filename} not found.")

    os.remove(file_path)
    return {"message": f"{filename} deleted successfully."}


@router.post("/documents/analyze/{filename}", response_model=dict)
def analyze_pdf(
    filename: str,
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Runs the intent suggestion pipeline on the specified PDF.
    Extracts sentences, embeds them, and matches each to the closest
    existing intent by semantic similarity.
    Returns suggestions grouped by intent for admin review.
    This endpoint can take 10-30 seconds for large documents.
    Accessible by CSO and IT teams only.
    """
    try:
        result = analyze_document(filename)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/apply", response_model=dict)
def apply_reviewed_suggestions(
    request: ApplySuggestionsRequest,
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Applies accepted suggestions from admin review to intents.json.
    Only suggestions with accepted=True are written.
    Admin edits to suggestedIntent and type are respected.
    Calls reload_intents after writing so changes are immediately active.
    Returns counts of what was added and what was skipped as duplicates.
    Accessible by CSO and IT teams only.
    """
    suggestions = [s.model_dump() for s in request.suggestions]
    result = apply_suggestions(suggestions)
    return {
        "message": "Suggestions applied successfully.",
        "patternsAdded": result["patternsAdded"],
        "responsesAdded": result["responsesAdded"],
        "skipped": result["skipped"],
    }


@router.post("/documents/reindex", response_model=dict)
def reindex_documents(admin: Admin = Depends(require_teams("cso", "it"))):
    """
    Rebuilds the RAG vector index from all PDFs in the documents directory.
    Run after uploading, updating, or deleting any PDF files.
    Reloads the index into the running server after building.
    Accessible by CSO and IT teams only.
    """
    build_message = build_index()
    reload_message = reload_index()
    return {"message": "Document index rebuilt successfully.", "detail": f"{build_message} {reload_message}"}
