import pytest

from app.seed import BANNER_SEEDS
from app.services.offers import handle_event

BANNERS_BY_TYPE = {banner.type: banner for banner in BANNER_SEEDS}


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
    assert offers[0]["title"] == BANNERS_BY_TYPE["salary"].title
    assert offers[0]["status"] == "shown"


SIMULATOR_BANNERS = [
    pytest.param(
        banner.type,
        banner.title,
        banner.subtitle,
        banner.background_color,
        banner.icon,
        id=banner.type,
    )
    for banner in BANNER_SEEDS
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
