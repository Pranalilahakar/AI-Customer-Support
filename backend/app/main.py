
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.ai import router as ai_router

app = FastAPI(
    title="AI Customer Support & Ticket Management System",
    description="REST API for customer support and AI-assisted ticket management.",
    version="0.1.0",
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
