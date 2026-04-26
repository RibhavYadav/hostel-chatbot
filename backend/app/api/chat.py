from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import ChatLog, Student
from app.models.schemas import ChatRequest, ChatResponse, IntentResult
from app.services.auth_service import get_current_student
from app.services.nlp_service import get_response, is_off_topic, predict_intent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Receives a student message, runs it through the NLP model,
    and returns the predicted intent and bot response.
    Applies an off-topic filter before classification - queries that
    match known non-hostel patterns are rejected immediately without
    running predict_intent, preventing topic keyword overlap from
    causing false high-confidence classifications.
    Every message is logged to the chat_logs table regardless of
    whether it was classified or rejected as off-topic.
    requiresForm is True when the predicted tag is 'leave_request'.
    """

    if is_off_topic(request.message):
        intent = {"tag": "unknown", "confidence": 0.0}
        off_topic_response = (
            "I can only help with hostel-related questions such as "
            "mess timings, curfew rules, laundry, leave requests, "
            "and hostel facilities."
        )
    else:
        intent = predict_intent(request.message)
        off_topic_response = get_response(intent["tag"], original_query=request.message)

    response_message = off_topic_response

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
