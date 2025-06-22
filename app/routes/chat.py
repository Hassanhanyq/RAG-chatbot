from fastapi import APIRouter, HTTPException, Depends
from app.auth.security import get_current_user
from app.rag.rag_chain import RAG_pipeline
from app.schemas.schemas import ChatRequest
from app.db.db import get_db
from sqlalchemy.orm import Session
from app.db.save import save_message
from app.db.models import Conversation
from uuid import uuid4
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat_llm(data: ChatRequest, current_user= Depends(get_current_user), db: Session=Depends(get_db)):
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
            db.commit()
            db.refresh(new_convo)
            conversation_id = new_convo.id
        else:
            conversation_id = data.conversation_id

        save_message(db, conversation_id,sender="user", content=data.query)
        response=RAG_pipeline(data.query)
        save_message(db, conversation_id, sender="assistant", content=response)
        return{"response": response,
               "conversation_id": str(conversation_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
