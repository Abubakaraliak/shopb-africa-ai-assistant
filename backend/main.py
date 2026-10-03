from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

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


@app.get("/api")
def api_home():
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


frontend_path = "/app/frontend/dist"


if os.path.exists(frontend_path):

    app.mount(
        "/assets",
        StaticFiles(
            directory=f"{frontend_path}/assets"
        ),
        name="assets"
    )


    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):

        requested_file = os.path.join(
            frontend_path,
            full_path
        )

        if os.path.isfile(requested_file):
            return FileResponse(requested_file)

        return FileResponse(
            os.path.join(
                frontend_path,
                "index.html"
            )
        )