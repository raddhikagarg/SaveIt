"""
SaveIt backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.scheduler import start_scheduler
from app.database import Base, engine
from app.routers import (
    tracker,
    extract,
    resources,
    webhooks,
    calender_sync,
    auth,
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaveIt API",
    description="From Reel to Reminder — a deadline-aware opportunity tracker.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    start_scheduler()


# CORS (Frontend → Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(tracker.router)
app.include_router(extract.router)
app.include_router(resources.router)
app.include_router(webhooks.router)
app.include_router(calender_sync.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "SaveIt backend",
    }