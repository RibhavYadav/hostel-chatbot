from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.admin import router as admin_router
from app.api.admin_auth import router as admin_auth_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.leave import router as leave_router
from app.database import init_db

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Hostel Chatbot API",
    swagger_ui_init_oauth={},
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router)
app.include_router(leave_router, prefix="/leave")
app.include_router(admin_auth_router, prefix="/admin")
app.include_router(admin_router, prefix="/admin")
