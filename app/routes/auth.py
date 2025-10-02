from fastapi import APIRouter, Depends
from app.db.db import get_db
from app.schemas.schemas import SignupRequest, LoginRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.signup(data, db)

@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    return await AuthService.verify_email(token, db)

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(data, db)
