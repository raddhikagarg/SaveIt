"""
DeadlineDrop backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import tracker, extract, resources, webhooks, calender_sync

# Create tables on startup if they don't exist yet.
# For production, swap this for Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaveIt API",
    description="From Reel to Reminder — a deadline-aware opportunity tracker.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracker.router)
app.include_router(extract.router)
app.include_router(resources.router)
app.include_router(webhooks.router)
app.include_router(calender_sync.router)

from app.routers import tracker, extract, resources, webhooks, calender_sync, auth
...
app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "SaveIt backend"}
