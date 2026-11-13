import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import BannerTemplate, Client, Offer

logger = logging.getLogger(__name__)

EVENT_TYPE_TO_BANNER_TYPE = {
    "salary": "salary",
    "salary_received": "salary",
    "purchase": "purchase",
    "deposit_view": "deposit_view",
    "high_balance": "high_balance",
}


def banner_type_for_event(event_type: str | None) -> str | None:
    return EVENT_TYPE_TO_BANNER_TYPE.get(event_type or "")


def is_client_eligible(client: Client) -> bool:
    return (
        not client.has_savings_account
        and (client.active_deposits_count or 0) <= 1
    )


def handle_event(message: dict[str, Any], db: Session) -> Offer | None:
    event_id = message.get("event_id")
    if not event_id:
        logger.warning("Skipping event without event_id: %s", message)
        return None

    existing = db.scalar(select(Offer).where(Offer.event_id == event_id))
    if existing is not None:
        logger.info("Event %s already produced offer %s", event_id, existing.id)
        return existing

    banner_type = banner_type_for_event(message.get("event_type"))
    if banner_type is None:
        logger.info("No banner template mapped for event type %s", message.get("event_type"))
        return None

    template = db.scalar(
        select(BannerTemplate).where(BannerTemplate.type == banner_type)
    )
    if template is None or template.product_id is None:
        logger.warning("Banner template %s is not configured", banner_type)
        return None

    client = db.get(Client, message.get("client_id"))
    if client is None:
        logger.warning("Client %s not found for event %s", message.get("client_id"), event_id)
        return None

    if not is_client_eligible(client):
        logger.info("Client %s is not eligible for offer on event %s", client.id, event_id)
        return None

    offer = Offer(
        client_id=client.id,
        product_id=template.product_id,
        banner_template_id=template.id,
        event_id=event_id,
        trigger_type=message.get("event_type"),
        trigger_payload=message.get("payload"),
        message_text=template.title,
        status="pending",
    )
    db.add(offer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return db.scalar(select(Offer).where(Offer.event_id == event_id))

    db.refresh(offer)
    logger.info("Created offer %s for event %s", offer.id, event_id)
    return offer
