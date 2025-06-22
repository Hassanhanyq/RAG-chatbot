from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.models import User
from app.schemas.schemas import SignupRequest, LoginRequest
from app.auth.security import hash_password, verify_password, create_access_token, create_email_verification_token, verify_email_token
from app.utils.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    user_exists = db.query(User).filter(User.email == data.email).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered.")
    username_exists=db.query(User).filter(User.username== data.username).first()
    if(username_exists):
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        verified=False 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_email_verification_token(data.email)
    await send_verification_email(data.email, token)

    return {"msg": "Check your email to verify your account."}

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.verified= True 
    db.commit()

    return {"msg": "Email verified successfully!"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not user.verified:
        raise HTTPException(status_code=403, detail="Email not verified.")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}