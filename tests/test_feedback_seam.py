import pytest

from app.models import Offer


def create_offer(session, seeded, status="pending", event_id="evt-feedback-1"):
    offer = Offer(
        client_id=seeded["client_id"],
        product_id=seeded["product_id"],
        banner_template_id=seeded["banner_template_id"],
        event_id=event_id,
        trigger_type="salary",
        status=status,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


@pytest.mark.parametrize("action", ["accepted", "declined", "dismissed"])
def test_feedback_updates_status_and_responded_at(
    client, seeded, session, action
):
    offer = create_offer(session, seeded, event_id=f"evt-feedback-{action}")

    response = client.post(
        f"/api/v1/offers/{offer.id}/feedback",
        json={"action": action},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == offer.id
    assert body["status"] == action
    assert body["responded_at"] is not None

    session.expire_all()
    stored = session.get(Offer, offer.id)
    assert stored is not None
    assert stored.status == action
    assert stored.responded_at is not None


def test_invalid_feedback_action_is_rejected(client, seeded, session):
    offer = create_offer(session, seeded, event_id="evt-feedback-invalid")

    response = client.post(
        f"/api/v1/offers/{offer.id}/feedback",
        json={"action": "maybe"},
    )

    assert 400 <= response.status_code < 500

    session.expire_all()
    stored = session.get(Offer, offer.id)
    assert stored is not None
    assert stored.status == "pending"
    assert stored.responded_at is None


def test_feedback_for_unknown_offer_returns_404(client):
    response = client.post(
        "/api/v1/offers/9999/feedback",
        json={"action": "declined"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("action", ["declined", "dismissed"])
def test_responded_offers_leave_the_active_offers_list(
    client, seeded, session, action
):
    offer = create_offer(session, seeded, event_id=f"evt-leaves-{action}")

    feedback = client.post(
        f"/api/v1/offers/{offer.id}/feedback",
        json={"action": action},
    )
    assert feedback.status_code == 200

    response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert response.status_code == 200
    assert response.json()["offers"] == []


def test_active_offers_expose_status(client, seeded, session):
    offer = create_offer(session, seeded, event_id="evt-status-visible")

    response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert response.status_code == 200
    offers = response.json()["offers"]
    assert len(offers) == 1
    assert offers[0]["id"] == offer.id
    assert offers[0]["status"] == "shown"


def test_responded_offer_status_is_available_with_include_responded(
    client, seeded, session
):
    offer = create_offer(session, seeded, event_id="evt-status-after-response")

    feedback = client.post(
        f"/api/v1/offers/{offer.id}/feedback",
        json={"action": "declined"},
    )
    assert feedback.status_code == 200

    response = client.get(
        f"/api/v1/clients/{seeded['client_id']}/offers",
        params={"include_responded": "true"},
    )

    assert response.status_code == 200
    offers = response.json()["offers"]
    assert len(offers) == 1
    assert offers[0]["id"] == offer.id
    assert offers[0]["status"] == "declined"


def test_active_offers_are_limited_to_latest_five(client, seeded, session):
    created = [
        create_offer(session, seeded, event_id=f"evt-limit-{index}")
        for index in range(7)
    ]
    # The two oldest offers were already handled and must not be shown again.
    for offer, action in zip(created[:2], ("accepted", "declined")):
        response = client.post(
            f"/api/v1/offers/{offer.id}/feedback", json={"action": action}
        )
        assert response.status_code == 200

    response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert response.status_code == 200
    offers = response.json()["offers"]
    assert len(offers) == 5
    assert [offer["id"] for offer in offers] == [
        created[6].id,
        created[5].id,
        created[4].id,
        created[3].id,
        created[2].id,
    ]
    assert all(offer["status"] == "shown" for offer in offers)


def test_offers_limit_can_be_overridden(client, seeded, session):
    for index in range(4):
        create_offer(session, seeded, event_id=f"evt-limit-override-{index}")

    response = client.get(
        f"/api/v1/clients/{seeded['client_id']}/offers",
        params={"limit": 2},
    )

    assert response.status_code == 200
    assert len(response.json()["offers"]) == 2
