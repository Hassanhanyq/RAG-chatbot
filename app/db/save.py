from app.db.models import Message
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone


async def save_message(db: AsyncSession, conversation_id: UUID, sender: str, content: str):
    """
    Saves a message to the database.

    Args:
        db (Session): SQLAlchemy session.
        conversation_id (UUID): ID of the conversation.
        sender (str): 'user' or 'assistant'.
        content (str): Message text.
    """
    message = Message(
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(message)
    return(message)