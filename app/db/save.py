from app.db.models import Message
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime


def save_message(db: Session, conversation_id: UUID, sender: str, content: str):
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
        timestamp=datetime.now(datetime.timezone.utc)
    )
    db.add(message)
    db.commit()
    db.refresh(message)
