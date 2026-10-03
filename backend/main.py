from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag_pipeline import ask_shopb


app = FastAPI(
    title="ShopB.Africa AI Customer Support Assistant",
    description="RAG-powered customer support assistant for ShopB.Africa",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    history: list = []


class ChatResponse(BaseModel):
    answer: str
    sources: list
    search_query: str
    assessment: str


@app.get("/")
def home():
    return {
        "message": "ShopB.Africa AI Customer Support Assistant is running.",
        "status": "online"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = ask_shopb(
        question=request.question,
        history=request.history
    )

    return {
        "answer": result.get(
            "answer",
            "Sorry, I could not generate an answer."
        ),
        "sources": result.get(
            "sources",
            []
        ),
        "search_query": result.get(
            "search_query",
            request.question
        ),
        "assessment": result.get(
            "assessment",
            "unknown"
        )
    }