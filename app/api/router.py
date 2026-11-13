from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.messaging import EventPublisher, get_publisher
from app.models import BannerTemplate, Client, Offer
from app.schemas import (
    ClientOut,
    ClientsResponse,
    EventAccepted,
    EventIn,
    FeedbackIn,
    FeedbackOut,
    OfferOut,
    OffersResponse,
)

api_router = APIRouter()

ACTIVE_OFFER_STATUSES = ("pending", "shown")


@api_router.post(
    "/events",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=EventAccepted,
)
def post_event(
    event: EventIn,
    publisher: EventPublisher = Depends(get_publisher),
):
    event_id = str(uuid4())
    occurred_at = event.occurred_at or datetime.now(timezone.utc)
    publisher.publish(
        {
            "event_id": event_id,
            "client_id": event.client_id,
            "event_type": event.event_type,
            "payload": event.payload,
            "occurred_at": occurred_at.isoformat(),
        }
    )
    return EventAccepted(event_id=event_id)


@api_router.get(
    "/clients",
    response_model=ClientsResponse,
)
def list_clients(db: Session = Depends(get_db)):
    clients = db.scalars(select(Client).order_by(Client.id)).all()
    return ClientsResponse(
        clients=[
            ClientOut(id=client.id, full_name=client.full_name) for client in clients
        ]
    )


@api_router.get(
    "/clients/{client_id}/offers",
    response_model=OffersResponse,
)
def get_client_offers(client_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Offer, BannerTemplate)
        .join(BannerTemplate, Offer.banner_template_id == BannerTemplate.id)
        .where(
            Offer.client_id == client_id,
            Offer.status.in_(ACTIVE_OFFER_STATUSES),
        )
        .order_by(Offer.created_at.desc(), Offer.id.desc())
    ).all()

    offers = [
        OfferOut(
            id=offer.id,
            type=template.type,
            title=template.title,
            subtitle=template.subtitle,
            background_color=template.background_color,
            icon=template.icon,
            action_text=template.action_text,
            status=offer.status,
            created_at=offer.created_at,
        )
        for offer, template in rows
    ]
    return OffersResponse(client_id=client_id, offers=offers)


@api_router.post(
    "/offers/{offer_id}/feedback",
    response_model=FeedbackOut,
)
def post_feedback(
    offer_id: int,
    feedback: FeedbackIn,
    db: Session = Depends(get_db),
):
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")

    offer.status = feedback.action
    offer.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(offer)

    return FeedbackOut(
        id=offer.id,
        status=offer.status,
        responded_at=offer.responded_at,
    )
