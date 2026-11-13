from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.constants import FEEDBACK_ACTION_VALUES, SUPPORTED_EVENT_TYPES


class EventIn(BaseModel):
    client_id: int = Field(gt=0)
    event_type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if value not in SUPPORTED_EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {value}")
        return value


class EventAccepted(BaseModel):
    event_id: str
    status: str = "accepted"


class OfferOut(BaseModel):
    id: int
    type: str
    title: str
    subtitle: str | None = None
    background_color: str | None = None
    icon: str | None = None
    action_text: str | None = None
    status: str
    created_at: datetime | None = None


class OffersResponse(BaseModel):
    client_id: int
    offers: list[OfferOut]


class ClientOut(BaseModel):
    id: int
    full_name: str | None = None


class ClientsResponse(BaseModel):
    clients: list[ClientOut]


class FeedbackIn(BaseModel):
    action: Literal[*FEEDBACK_ACTION_VALUES]


class FeedbackOut(BaseModel):
    id: int
    status: str
    responded_at: datetime
