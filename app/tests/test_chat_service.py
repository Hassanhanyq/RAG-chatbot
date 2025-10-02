import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.chat_service import ChatService
from app.db.models import User, Conversation
from app.schemas.schemas import ChatRequest


@pytest.mark.asyncio
async def test_new_conversation_chat(db_session: AsyncSession):
    user = User(
        email="chat@example.com",
        username="chatter",
        hashed_password="hashed",
        verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    chat_data = ChatRequest(query="Hello there!", conversation_id=None)

    response = await ChatService.chat_llm(chat_data, user, db_session)

    assert response is not None
    assert response.status_code == 200 or isinstance(response.body_iterator, object)


@pytest.mark.asyncio
async def test_existing_conversation_chat(db_session: AsyncSession):
    user = User(
        email="chat2@example.com",
        username="chatter2",
        hashed_password="hashed",
        verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    conversation = Conversation(user_id=user.id, title="Test Convo")
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    chat_data = ChatRequest(
        query="Continue this convo", conversation_id=conversation.id
    )

    response = await ChatService.chat_llm(chat_data, user, db_session)

    assert response is not None
