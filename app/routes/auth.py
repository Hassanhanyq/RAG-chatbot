from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.models import User
from app.schemas.schemas import SignupRequest, LoginRequest
from app.auth.security import hash_password, verify_password, create_access_token, create_email_verification_token, verify_email_token
from app.utils.email import send_verification_email
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    result = await db.execute(select(User).filter(User.email == data.email))
    user_exists = result.scalar_one_or_none()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    result = await db.execute(select(User).filter(User.username == data.username))
    username_exists = result.scalar_one_or_none()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken.")


    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        verified=False 
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_email_verification_token(data.email)
    await send_verification_email(data.email, token)

    return {"msg": "Check your email to verify your account."}

@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    result = await db.execute(select(User).filter(User.email == email)) 
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.verified= True 
    await db.commit()

    return {"msg": "Email verified successfully!"}

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
   result = await db.execute(select(User).filter(User.email == data.email))
   user = result.scalar_one_or_none()
   if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
   if not user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified.")

   token = create_access_token({"sub": user.email})
   return {"access_token": token, "token_type": "bearer"}