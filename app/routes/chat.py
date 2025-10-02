from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.db.db import get_db
from app.db.models import User
from app.schemas.schemas import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat_llm(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService.chat_llm(data, current_user, db)
