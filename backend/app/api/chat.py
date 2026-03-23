from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse, IntentResult
from app.services.nlp_service import predict_intent, get_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    intent = predict_intent(request.message)
    response_message = get_response(intent["tag"])

    return ChatResponse(
        message=response_message,
        intent=IntentResult(tag=intent["tag"], confidence=intent["confidence"]),
        requiresForm=intent["tag"] == "leave_request",
    )
