from fastapi import APIRouter, HTTPException, Depends, status
from app.auth.security import get_current_user
from app.rag.rag_chain import RAG_pipeline
from app.schemas.schemas import ChatRequest
from app.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.save import save_message
from app.db.models import Conversation, User
from uuid import uuid4
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat_llm(data: ChatRequest, current_user: User= Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    """
    Route to send messages
    
    """
    try:
        if not data.conversation_id:
            new_convo = Conversation(
                id=uuid4(),
                user_id=current_user.id,
                title="New Conversation"  
            )
            db.add(new_convo)
            conversation_id = new_convo.id
        else:
            result = await db.execute(
                select(Conversation).filter(
                    Conversation.id == data.conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
            existing_convo = result.scalar_one_or_none()
            if not existing_convo:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conversation not found or does not belong to the current user."
                )

        user_message_obj = await save_message(
            db, conversation_id=conversation_id, sender="user", content=data.query
        )
        response=RAG_pipeline(data.query)
        assistant_message_obj = await save_message(
            db, conversation_id=conversation_id, sender="assistant", content=response
        )
        await db.commit()
        await db.refresh(user_message_obj)
        await db.refresh(assistant_message_obj)
        if new_convo: 
            await db.refresh(new_convo)

        return{"response": response,
               "conversation_id": str(conversation_id)}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback() 
        print(f"Error in chat_llm route: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing your request."
        )
    
