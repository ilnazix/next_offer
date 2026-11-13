from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import router
from app.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    yield
    # Shutdown
    engine.dispose()


app = FastAPI(
    title="Rozochka — Proactive Concierge Agent",
    description="MVP of an AI agent that analyzes transactions and proposes banking products.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router.api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
