from app.models import Client, Offer
from app.services.offers import handle_event


def salary_event(client_id: int, event_id: str = "evt-worker-1") -> dict:
    return {
        "event_id": event_id,
        "client_id": client_id,
        "event_type": "salary",
        "payload": {"amount": 150000},
        "occurred_at": "2026-11-14T10:00:00+00:00",
    }


def test_worker_creates_salary_offer_with_salary_banner(session, seeded):
    offer = handle_event(salary_event(seeded["client_id"]), session)

    assert offer is not None
    assert offer.client_id == seeded["client_id"]
    assert offer.product_id == seeded["product_id"]
    assert offer.banner_template_id == seeded["banner_template_id"]
    assert offer.trigger_type == "salary"
    assert offer.status == "pending"
    assert offer.event_id == "evt-worker-1"

    stored = session.get(Offer, offer.id)
    assert stored is not None
    assert stored.banner_template_id == seeded["banner_template_id"]


def test_worker_redelivery_does_not_duplicate_offer(session, seeded):
    first = handle_event(salary_event(seeded["client_id"]), session)
    second = handle_event(salary_event(seeded["client_id"]), session)

    assert first is not None
    assert second is not None
    assert second.id == first.id
    assert session.query(Offer).filter_by(event_id="evt-worker-1").count() == 1


def test_worker_skips_ineligible_client(session, seeded):
    client = session.get(Client, seeded["client_id"])
    client.has_savings_account = True
    session.commit()

    offer = handle_event(salary_event(seeded["client_id"], "evt-ineligible"), session)

    assert offer is None
    assert session.query(Offer).count() == 0
