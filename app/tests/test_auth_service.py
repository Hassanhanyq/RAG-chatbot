import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.auth_service import AuthService
from app.db.models import User
from app.schemas.schemas import SignupRequest, LoginRequest
from app.auth.security import verify_password

@pytest.mark.asyncio
async def test_signup_and_login_success(db_session: AsyncSession):
    signup_data = SignupRequest(
        email="test@example.com",
        username="testuser",
        password="password123",
        confirm_password="password123",
    )

    signup_result = await AuthService.signup(signup_data, db_session)

    assert "Check your email" in signup_result["msg"]

    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one()
    user.verified = True
    await db_session.commit()
    assert user is not None
    assert verify_password("password123", user.hashed_password)

    login_data = LoginRequest(email="test@example.com", password="password123")
    login_result = await AuthService.login(login_data, db_session)

    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_signup_password_mismatch(db_session: AsyncSession):
    signup_data = SignupRequest(
        email="wrong@example.com",
        username="wronguser",
        password="password123",
        confirm_password="notmatching",
    )

    with pytest.raises(Exception) as excinfo:
        await AuthService.signup(signup_data, db_session)

    assert "Passwords do not match" in str(excinfo.value)
