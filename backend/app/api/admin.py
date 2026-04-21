import json
import os
import subprocess
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Admin, ChatLog, LeaveRequest
from app.models.schemas import (
    ChatLogResponse,
    IntentCreateRequest,
    IntentModel,
    IntentUpdateRequest,
    LeaveRequestResponse,
    LeaveStatusUpdate,
)
from app.services.auth_service import require_teams
from app.services.nlp_service import INTENTS_PATH, get_intents, reload_intents, reload_model
from app.services.rag_service import build_index, reload_index

router = APIRouter()


@router.get("/chat-logs", response_model=list[ChatLogResponse])
def get_chat_logs(
    promoted: bool | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Returns all student chat logs ordered by most recent first.
    Optional promoted query parameter filters by promotion status.
    promoted=false returns only messages pending admin review.
    promoted=true returns only already promoted messages.
    Omitting the parameter returns all logs.
    Accessible by CSO and IT teams only.
    """

    query = db.query(ChatLog)
    if promoted is not None:
        query = query.filter(ChatLog.promoted == promoted)
    logs = query.order_by(ChatLog.timestamp.desc()).all()

    return [
        ChatLogResponse(
            id=log.id,
            studentId=log.student_id,
            message=log.message,
            predictedTag=log.predicted_tag,
            confidence=log.confidence,
            botResponse=log.bot_response,
            timestamp=log.timestamp,
            promoted=log.promoted,
        )
        for log in logs
    ]


@router.post("/promote/{log_id}", response_model=dict)
def promote_chat_log(
    log_id: int, db: Session = Depends(get_db), admin: Admin = Depends(require_teams("cso", "it"))
):
    """
    Adds the student message from the specified chat log as a new
    training pattern under its predicted intent tag in intents.json.
    Marks the log as promoted so it does not appear in the review
    queue again. Calls reload_intents so the change is immediately
    active without requiring a full model retrain.
    Model is not retrained here, the new pattern will only improve model predictions
    after retrain is called separately.
    Accessible by CSO and IT teams only.
    """

    # Search for chat log
    log = db.query(ChatLog).filter(ChatLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Chat log not found.")
    if log.promoted:
        raise HTTPException(status_code=400, detail="This message has already been promoted")

    # Load intents, find matching intent and add the message as a pattern
    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    intent_found = False
    for intent in intents_data["intents"]:
        if intent["tag"] == log.predicted_tag:
            if log.message not in intent["patterns"]:
                intent["patterns"].append(log.message)
        intent_found = True
        break

    if not intent_found:
        raise HTTPException(
            status_code=400, detail=f"Intent tag `{log.predicted_tag}` not found in intents.json."
        )

    # Update intents.json, mark log as promoted and reload intents
    with open(INTENTS_PATH, "w") as f:
        json.dump(intents_data, f, indent=4)

    log.promoted = True
    db.commit()
    reload_intents()

    return {"message": f"Message promoted as pattern under `{log.predicted_tag}`."}


@router.get("/intents", response_model=list[IntentModel])
def get_all_intents(admin: Admin = Depends(require_teams("cso", "it"))):
    """
    Returns all intents currently loaded in the NLP service.
    Reads from the in-memory _state in nlp_service.
    Accessible by CSO and IT teams only.
    """
    return get_intents()["intents"]


@router.post("/intents", response_model=dict)
def create_intent(
    request: IntentCreateRequest,
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Adds a new intent to intents.json.
    Validates that the tag does not already exist.
    Calls reload_intents after writing so the change is immediately active in get_response.
    The model must be retrained separately for the new intent
    to be recognized by predict_intent.
    Accessible by CSO and IT teams only.
    """

    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    # Check tag does not already exist
    for intent in intents_data["intents"]:
        if intent["tag"] == request.tag:
            raise HTTPException(status_code=409, detail=f"Intent tag '{request.tag}' already exists.")

    intents_data["intents"].append(
        {
            "tag": request.tag,
            "patterns": request.patterns,
            "responses": request.responses,
        }
    )

    with open(INTENTS_PATH, "w") as f:
        json.dump(intents_data, f, indent=2)

    reload_intents()

    return {"message": f"Intent '{request.tag}' created successfully."}


@router.put("/intents/{tag}", response_model=dict)
def update_intent(
    tag: str,
    request: IntentUpdateRequest,
    admin: Admin = Depends(require_teams("cso", "it")),
):
    """
    Updates the patterns or responses or both for an existing intent.
    Fields omitted from the request body are left unchanged.
    Calls reload_intents after writing.
    Accessible by CSO and IT teams only.
    """

    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    intent_found = False
    for intent in intents_data["intents"]:
        if intent["tag"] == tag:
            if request.patterns is not None:
                intent["patterns"] = request.patterns
            if request.responses is not None:
                intent["responses"] = request.responses
            intent_found = True
            break

    if not intent_found:
        raise HTTPException(status_code=404, detail=f"Intent tag '{tag}' not found.")

    with open(INTENTS_PATH, "w") as f:
        json.dump(intents_data, f, indent=2)

    reload_intents()

    return {"message": f"Intent '{tag}' updated successfully."}


@router.delete("/intents/{tag}", response_model=dict)
def delete_intent(
    tag: str,
    admin: Admin = Depends(require_teams("cso")),
):
    """
    Removes an intent and all its patterns and responses from intents.json.
    This action is irreversible. The model must be retrained after deletion
    for the change to take effect in predict_intent.
    Restricted to CSO team only.
    """
    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    original_count = len(intents_data["intents"])
    intents_data["intents"] = [i for i in intents_data["intents"] if i["tag"] != tag]

    if len(intents_data["intents"]) == original_count:
        raise HTTPException(status_code=404, detail=f"Intent tag '{tag}' not found.")

    with open(INTENTS_PATH, "w") as f:
        json.dump(intents_data, f, indent=2)

    reload_intents()

    return {"message": f"Intent '{tag}' deleted successfully."}


@router.post("/retrain", response_model=dict)
def retrain_model(admin: Admin = Depends(require_teams("cso", "it"))):
    """
    Runs train.py as a subprocess to retrain the NLP model on the
    current intents.json. After training completes, calls reload_model
    to load the new model files into the running server without restart.
    Returns the reload status message from nlp_service.
    Accessible by CSO and IT teams only.
    """

    train_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml", "train.py"
    )

    result = subprocess.run(["python", train_script], capture_output=True, text=True)

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Training failed: {result.stderr}")

    reload_message = reload_model()

    return {"message": "Model retrained and reloaded successfully.", "detail": reload_message}


@router.post("/reindex", response_model=dict)
def reindex_documents(admin: Admin = Depends(require_teams("cso", "it"))):
    """
    Reads all PDF files from the documents directory, rebuilds the
    RAG vector index, and reloads it into the running server.
    Run this after adding or updating any PDF files in the knowledge_base/documents directory.
    Accessible by CSO and IT teams only.
    """
    build_message = build_index()
    reload_message = reload_index()

    return {"message": "Document index rebuilt successfully.", "detail": f"{build_message} {reload_message}"}


@router.get("/leave/all", response_model=list[LeaveRequestResponse])
def get_all_leave_requests(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_teams("cso", "warden")),
):
    """
    Returns all leave requests across all students ordered by
    most recent submission first.
    Accessible by CSO and Warden teams only.
    """
    requests = db.query(LeaveRequest).order_by(LeaveRequest.submitted_at.desc()).all()

    return [
        LeaveRequestResponse(
            id=r.id,
            studentId=r.student_id,
            departureDate=r.departure_date,
            returnDate=r.return_date,
            reason=r.reason,
            status=r.status,
            submittedAt=r.submitted_at,
        )
        for r in requests
    ]


@router.put("/leave/{leave_id}/status", response_model=dict)
def update_leave_status(
    leave_id: int,
    request: LeaveStatusUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_teams("cso", "warden")),
):
    """
    Updates the status of a leave request to approved or rejected.
    Sets reviewed_at to the current UTC timestamp.
    The LeaveStatusUpdate schema validator ensures only
    approved or rejected are accepted as status values.
    Accessible by CSO and Warden teams only.
    """

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found.")

    if leave.status != "pending":
        raise HTTPException(status_code=400, detail=f"Leave request has already been {leave.status}.")

    leave.status = request.status
    leave.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": f"Leave request {leave_id} marked as {request.status}."}
