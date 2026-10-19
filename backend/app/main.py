
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.ai import router as ai_router

app = FastAPI(
    title="AI Customer Support & Ticket Management System",
    description="REST API for customer support and AI-assisted ticket management.",
    version="0.1.0",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")

if frontend_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "AI Customer Support API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "customer-support-api",
    }
