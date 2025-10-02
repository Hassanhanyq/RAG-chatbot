import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from fastapi_mail import ConnectionConfig

@pytest_asyncio.fixture(autouse=True)
def fake_mail_settings(monkeypatch):
    test_conf = ConnectionConfig(
        MAIL_USERNAME="test@example.com",
        MAIL_PASSWORD="fakepassword",
        MAIL_FROM="test@example.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.example.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=False,
        SUPPRESS_SEND=True,  
    )
    monkeypatch.setattr("app.utils.email.conf", test_conf)
@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.close()
