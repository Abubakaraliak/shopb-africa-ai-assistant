from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from rag_pipeline import ask_shopb


app = FastAPI(
    title="ShopB.Africa AI Customer Support API",
    description="RAG-powered customer support API for ShopB.Africa",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = Field(default_factory=list)

@app.get("/")
def home():
    return {
        "message": "ShopB.Africa AI Customer Support API is running"
    }



@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        history = [
            message.model_dump()
            for message in request.history[-6:]
        ]

        result = ask_shopb(
            question=question,
            history=history
        )

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(error)}"
        )