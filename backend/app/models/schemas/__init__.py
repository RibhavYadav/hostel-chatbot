"""
Re-exports all schemas from submodules so existing imports
using 'from app.models.schemas import X' continue to work
without modification after the schemas split.
"""

from app.models.schemas.auth_schemas import (
    AdminLoginRequest,
    AdminRegisterRequest,
    AdminResponse,
    AdminTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    StudentResponse,
    TokenResponse,
)
from app.models.schemas.chat_schemas import (
    ChatLogResponse,
    ChatRequest,
    ChatResponse,
    IntentResult,
)
from app.models.schemas.document_schemas import (
    ApplySuggestionsRequest,
    DocumentInfo,
    IntentSuggestion,
    SuggestionResult,
)
from app.models.schemas.intent_schemas import (
    IntentCreateRequest,
    IntentModel,
    IntentUpdateRequest,
    PromoteRequest,
)
from app.models.schemas.leave_schemas import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveStatusUpdate,
)
