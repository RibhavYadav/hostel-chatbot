from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import ChatLog, Student
from app.models.schemas import ChatRequest, ChatResponse, IntentResult
from app.services.auth_service import get_current_student
from app.services.nlp_service import get_response, predict_intent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Receives a student message, runs it through the NLP model, and returns the prediction intent
    and bot response. Requires a valid JWT token, unauthenticated requests are rejected.
    Every message and its prediction are logged to the chat_logs table.
    Log failures do not affect the response returned to the student.
    """

    intent = predict_intent(request.message)
    response_message = get_response(intent["tag"])

    try:
        log = ChatLog(
            student_id=current_student.id,
            message=request.message,
            predicted_tag=intent["tag"],
            confidence=intent["confidence"],
            bot_response=response_message,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Chat log write failed: {e}")

    return ChatResponse(
        message=response_message,
        intent=IntentResult(tag=intent["tag"], confidence=intent["confidence"]),
        requiresForm=intent["tag"] == "leave_request",
    )
