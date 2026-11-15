import json

from sqlalchemy import select

from app.models import Offer
from app.worker import process_message


def test_event_becomes_offer_in_db_and_api_then_accepts_feedback(
    client, publisher, seeded, session_factory
):
    event_response = client.post(
        "/api/v1/events",
        json={
            "client_id": seeded["client_id"],
            "event_type": "salary",
            "payload": {"amount": 150000},
        },
    )
    assert event_response.status_code == 202

    event = publisher.messages[-1]
    process_message(json.dumps(event).encode(), session_factory=session_factory)

    with session_factory() as db:
        offer = db.scalar(select(Offer).where(Offer.event_id == event["event_id"]))
        assert offer is not None
        assert offer.client_id == seeded["client_id"]
        assert offer.status == "pending"

    offers_response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")
    assert offers_response.status_code == 200
    offers = offers_response.json()["offers"]
    assert len(offers) == 1
    assert offers[0]["id"] == offer.id
    assert offers[0]["type"] == "salary"
    assert offers[0]["title"] == "Сохраните зарплату под 8%"
    assert offers[0]["status"] == "shown"

    with session_factory() as db:
        shown = db.get(Offer, offer.id)
        assert shown is not None
        assert shown.shown_at is not None

    feedback_response = client.post(
        f"/api/v1/offers/{offer.id}/feedback",
        json={"action": "accepted"},
    )
    assert feedback_response.status_code == 200
    assert feedback_response.json()["status"] == "accepted"

    with session_factory() as db:
        stored = db.get(Offer, offer.id)
        assert stored is not None
        assert stored.status == "accepted"
        assert stored.responded_at is not None

    after_feedback = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")
    assert after_feedback.status_code == 200
    assert after_feedback.json()["offers"] == []


def test_redelivered_event_does_not_create_a_second_offer(
    client, publisher, seeded, session_factory
):
    event_response = client.post(
        "/api/v1/events",
        json={
            "client_id": seeded["client_id"],
            "event_type": "purchase",
            "payload": {"amount": 80000},
        },
    )
    assert event_response.status_code == 202

    event = publisher.messages[-1]
    body = json.dumps(event).encode()
    process_message(body, session_factory=session_factory)
    process_message(body, session_factory=session_factory)

    with session_factory() as db:
        offers = db.scalars(select(Offer)).all()

    assert len(offers) == 1
    assert offers[0].trigger_type == "purchase"
