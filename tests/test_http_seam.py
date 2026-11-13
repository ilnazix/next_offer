from app.models import Offer


def test_event_is_accepted_published_and_not_offered_synchronously(
    client, publisher, seeded, session
):
    response = client.post(
        "/api/v1/events",
        json={
            "client_id": seeded["client_id"],
            "event_type": "salary",
            "payload": {"amount": 150000},
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert body["event_id"]

    assert len(publisher.messages) == 1
    message = publisher.messages[0]
    assert message["event_id"] == body["event_id"]
    assert message["client_id"] == seeded["client_id"]
    assert message["event_type"] == "salary"
    assert message["payload"] == {"amount": 150000}

    session.expire_all()
    assert session.query(Offer).count() == 0


def test_client_offers_include_banner_template_fields(client, seeded, session):
    offer = Offer(
        client_id=seeded["client_id"],
        product_id=seeded["product_id"],
        banner_template_id=seeded["banner_template_id"],
        event_id="evt-http-1",
        trigger_type="salary",
        status="pending",
    )
    session.add(offer)
    session.commit()

    response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert response.status_code == 200
    body = response.json()
    assert body["client_id"] == seeded["client_id"]
    assert len(body["offers"]) == 1
    returned = body["offers"][0]
    assert returned["id"] == offer.id
    assert returned["type"] == "salary"
    assert returned["title"] == "Сохраните зарплату под 8%"
    assert returned["subtitle"] == (
        "Отложите часть на накопительный счёт с ежемесячной капитализацией"
    )
    assert returned["background_color"] == (
        "linear-gradient(135deg, #7c3aed 0%, #db2777 100%)"
    )
    assert returned["icon"] == "💰"
    assert returned["action_text"] == "Открыть счёт"
    assert returned["status"] == "pending"


def test_invalid_event_is_rejected_without_publishing(client, publisher):
    response = client.post(
        "/api/v1/events",
        json={"client_id": 0, "event_type": ""},
    )

    assert response.status_code == 422
    assert publisher.messages == []


def test_client_offers_exclude_inactive_offers(client, seeded, session):
    offer = Offer(
        client_id=seeded["client_id"],
        product_id=seeded["product_id"],
        banner_template_id=seeded["banner_template_id"],
        event_id="evt-inactive-1",
        trigger_type="salary",
        status="declined",
    )
    session.add(offer)
    session.commit()

    response = client.get(f"/api/v1/clients/{seeded['client_id']}/offers")

    assert response.status_code == 200
    assert response.json()["offers"] == []


def test_cors_allows_local_frontend_origin(client, seeded):
    response = client.get(
        f"/api/v1/clients/{seeded['client_id']}/offers",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_list_clients_exposes_seeded_demo_clients(client, seeded):
    response = client.get("/api/v1/clients")

    assert response.status_code == 200
    clients = response.json()["clients"]
    returned_ids = {client["id"] for client in clients}
    assert set(seeded["client_ids"]) <= returned_ids
    assert all(client["full_name"] for client in clients)
