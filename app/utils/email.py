from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from pydantic import EmailStr
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
fm = FastMail(conf)
async def send_verification_email(email: EmailStr, token: str):
    """
    Sends an email verification message to the user's email address.

    Args:
        email (EmailStr): The recipient's email address.
        token (str): The JWT token used to verify the user's email.

    This function constructs a verification link containing the token
    and sends it to the specified email using FastAPI-Mail with SMTP.
    """
    verify_link = f"http://localhost:8000/auth/verify?token={token}"  

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"""
            <h3>Welcome to TherapistLLM!</h3>
            <p>Please click the link below to verify your email address:</p>
            <a href="{verify_link}">{verify_link}</a>
            <br><br>
            <p>If you didn't sign up, you can ignore this email.</p>
        """,
        subtype="html"
    )

    
    await fm.send_message(message)