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
