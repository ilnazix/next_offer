import logging
import random
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.constants import EventType, OfferStatus
from app.llm import (
    OfferContext,
    OfferTextGenerator,
    build_text_generator,
    describe_event,
)
from app.models import BannerTemplate, Client, Offer, Product

logger = logging.getLogger(__name__)

EVENT_TYPE_TO_BANNER_TYPE = {
    EventType.SALARY.value: "salary",
    EventType.SALARY_RECEIVED.value: "salary",
    EventType.PURCHASE.value: "purchase",
    EventType.DEPOSIT_VIEW.value: "deposit_view",
    EventType.HIGH_BALANCE.value: "high_balance",
}

STYLE_HINTS = (
    "выгода в процентах",
    "простота оформления онлайн",
    "сохранность и безопасность средств",
    "конкретная сумма на счёте",
    "цель: ремонт, отпуск или крупная покупка",
    "ежемесячная капитализация",
)


def banner_type_for_event(event_type: str | None) -> str | None:
    return EVENT_TYPE_TO_BANNER_TYPE.get(event_type or "")


def is_client_eligible(client: Client) -> bool:
    return (
        not client.has_savings_account
        and (client.active_deposits_count or 0) <= 1
    )


def handle_event(
    message: dict[str, Any],
    db: Session,
    text_generator: OfferTextGenerator | None = None,
) -> Offer | None:
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

    product = db.get(Product, template.product_id)
    event_type = str(message.get("event_type"))
    payload = message.get("payload")
    recent_titles = tuple(
        title
        for title in db.scalars(
            select(Offer.title)
            .where(
                Offer.client_id == client.id,
                Offer.trigger_type == event_type,
                Offer.title.is_not(None),
            )
            .order_by(Offer.created_at.desc(), Offer.id.desc())
            .limit(5)
        ).all()
        if title
    )
    context = OfferContext(
        event_type=event_type,
        event_description=describe_event(event_type),
        client_segment=client.segment,
        product_name=product.name if product else template.title,
        product_rate=(
            f"{product.annual_rate:g}"
            if product is not None and product.annual_rate is not None
            else None
        ),
        product_min_amount=(
            str(product.min_amount)
            if product is not None and product.min_amount is not None
            else None
        ),
        product_term_months=product.term_months if product is not None else None,
        event_details=payload if isinstance(payload, dict) else {},
        template_title=template.title,
        template_subtitle=template.subtitle,
        recent_titles=recent_titles,
        style_hint=random.choice(STYLE_HINTS),
    )

    generator = text_generator or build_text_generator()
    try:
        generated = generator.generate(context)
    except Exception:
        logger.exception("Offer text generation failed for event %s", event_id)
        generated = None

    title = generated.title if generated else template.title
    subtitle = generated.subtitle if generated else template.subtitle

    offer = Offer(
        client_id=client.id,
        product_id=template.product_id,
        banner_template_id=template.id,
        event_id=event_id,
        trigger_type=message.get("event_type"),
        trigger_payload=message.get("payload"),
        message_text=title,
        title=title,
        subtitle=subtitle,
        status=OfferStatus.PENDING.value,
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
