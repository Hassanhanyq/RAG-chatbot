from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="TherapistLLM API",
    description="Backend API for the RAG-based chatbot",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Welcome to the TherapistLLM API!"}
