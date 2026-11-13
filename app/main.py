from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import router
from app.config import settings
from app.db import get_engine
from app.health import collect_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    yield
    # Shutdown
    get_engine().dispose()


app = FastAPI(
    title="next_offer — Proactive Concierge Agent",
    description="MVP of an AI agent that analyzes transactions and proposes banking products.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check(response: Response):
    report = collect_health()
    if report["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report
