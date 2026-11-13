import pytest

from app.seed import (
    DEPOSIT_VIEW_GRADIENT,
    DEPOSIT_VIEW_ICON,
    DEPOSIT_VIEW_SUBTITLE,
    DEPOSIT_VIEW_TITLE,
    HIGH_BALANCE_GRADIENT,
    HIGH_BALANCE_ICON,
    HIGH_BALANCE_SUBTITLE,
    HIGH_BALANCE_TITLE,
    PURCHASE_GRADIENT,
    PURCHASE_ICON,
    PURCHASE_SUBTITLE,
    PURCHASE_TITLE,
    SALARY_GRADIENT,
    SALARY_ICON,
    SALARY_SUBTITLE,
    SALARY_TITLE,
)
from app.services.offers import handle_event


def test_salary_event_becomes_visible_offer(client, publisher, seeded, session):
    response = client.post(
        "/api/v1/events",
        json={
            "client_id": seeded["client_id"],
            "event_type": "salary",
            "payload": {"amount": 150000},
        },
    )
    assert response.status_code == 202

    event = publisher.messages[0]
    offer = handle_event(event, session)
    assert offer is not None

    offers_response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert offers_response.status_code == 200
    offers = offers_response.json()["offers"]
    assert len(offers) == 1
    assert offers[0]["type"] == "salary"
    assert offers[0]["title"] == "Сохраните зарплату под 8%"
    assert offers[0]["status"] == "pending"


SIMULATOR_BANNERS = [
    pytest.param(
        "salary",
        SALARY_TITLE,
        SALARY_SUBTITLE,
        SALARY_GRADIENT,
        SALARY_ICON,
        id="salary",
    ),
    pytest.param(
        "purchase",
        PURCHASE_TITLE,
        PURCHASE_SUBTITLE,
        PURCHASE_GRADIENT,
        PURCHASE_ICON,
        id="purchase",
    ),
    pytest.param(
        "deposit_view",
        DEPOSIT_VIEW_TITLE,
        DEPOSIT_VIEW_SUBTITLE,
        DEPOSIT_VIEW_GRADIENT,
        DEPOSIT_VIEW_ICON,
        id="deposit_view",
    ),
    pytest.param(
        "high_balance",
        HIGH_BALANCE_TITLE,
        HIGH_BALANCE_SUBTITLE,
        HIGH_BALANCE_GRADIENT,
        HIGH_BALANCE_ICON,
        id="high_balance",
    ),
]


@pytest.mark.parametrize(
    ("event_type", "title", "subtitle", "gradient", "icon"),
    SIMULATOR_BANNERS,
)
def test_every_simulator_event_becomes_offer_with_matching_banner(
    client, publisher, seeded, session, event_type, title, subtitle, gradient, icon
):
    response = client.post(
        "/api/v1/events",
        json={
            "client_id": seeded["client_id"],
            "event_type": event_type,
            "payload": {},
        },
    )
    assert response.status_code == 202

    offer = handle_event(publisher.messages[-1], session)
    assert offer is not None

    offers_response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")
    assert offers_response.status_code == 200
    returned = offers_response.json()["offers"][0]

    assert returned["type"] == event_type
    assert returned["title"] == title
    assert returned["subtitle"] == subtitle
    assert returned["background_color"] == gradient
    assert returned["icon"] == icon
