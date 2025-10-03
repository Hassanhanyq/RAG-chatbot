import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_email_verification_token
from app.db.models import User
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_verify_email_success(db_session: AsyncSession):
    user = User(
        email="verify@example.com",
        username="verifyuser",
        hashed_password="hashed",
        verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_email_verification_token("verify@example.com")
    result = await AuthService.verify_email(token, db_session)
    assert result["msg"] == "Email verified successfully!"
    user = (
        await db_session.execute(select(User).where(User.email == "verify@example.com"))
    ).scalar_one()
    assert user.verified is True
