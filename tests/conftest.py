import os

os.environ["LLM_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL or "sqlite://"

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.messaging import get_publisher  # noqa: E402
from app.models import Base  # noqa: E402
from app.seed import seed_demo_data  # noqa: E402


class RecordingPublisher:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    def publish(self, message: dict) -> None:
        self.messages.append(message)


@pytest.fixture
def engine():
    if TEST_DATABASE_URL:
        engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    else:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory


@pytest.fixture
def session(session_factory):
    with session_factory() as db:
        yield db


@pytest.fixture
def seeded(session):
    return seed_demo_data(session)


@pytest.fixture
def publisher():
    return RecordingPublisher()


@pytest.fixture
def client(session_factory, publisher):
    def override_get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_publisher] = lambda: publisher
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
