from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, User
from app.db.save import save_message
from app.rag.rag_chain import RAG_pipeline
from app.schemas.schemas import ChatRequest


class ChatService:
    @staticmethod
    async def chat_llm(data: ChatRequest, current_user: User, db: AsyncSession):
        try:
            is_new_conversation = False

            if not data.conversation_id:
                new_convo = Conversation(
                    id=uuid4(), user_id=current_user.id, title="New Conversation"
                )
                db.add(new_convo)
                conversation_id = new_convo.id
                is_new_conversation = True
            else:
                result = await db.execute(
                    select(Conversation).filter(
                        Conversation.id == data.conversation_id,
                        Conversation.user_id == current_user.id,
                    )
                )
                existing_convo = result.scalar_one_or_none()
                if not existing_convo:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Conversation not found or does not belong to the current user.",
                    )
                conversation_id = existing_convo.id

            async def stream_and_save_response_generator():
                full_assistant_response = ""
                try:
                    await save_message(
                        db,
                        conversation_id=conversation_id,
                        sender="user",
                        content=data.query,
                    )

                    for token_chunk in RAG_pipeline(data.query):
                        full_assistant_response += token_chunk
                        yield token_chunk

                    await save_message(
                        db,
                        conversation_id=conversation_id,
                        sender="assistant",
                        content=full_assistant_response,
                    )
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    print(f"Error during stream processing or saving: {e}")

            headers = {}
            if is_new_conversation:
                headers["X-Conversation-ID"] = str(conversation_id)

            return StreamingResponse(
                stream_and_save_response_generator(),
                media_type="text/plain",
                headers=headers,
            )
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            print(f"Error in chat_llm route: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred while processing your request.",
            )
