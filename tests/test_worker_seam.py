import pytest

from app.llm import OfferText
from app.models import BannerTemplate, Client, Offer
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


def test_worker_skips_client_with_active_savings_account(session, seeded):
    client = session.get(Client, seeded["client_id"])
    client.has_savings_account = True
    session.commit()

    offer = handle_event(salary_event(seeded["client_id"], "evt-ineligible"), session)

    assert offer is None
    assert session.query(Offer).count() == 0


def test_worker_skips_client_with_more_than_one_active_deposit(session, seeded):
    client = session.get(Client, seeded["client_id"])
    client.active_deposits_count = 2
    session.commit()

    offer = handle_event(salary_event(seeded["client_id"], "evt-two-deposits"), session)

    assert offer is None
    assert session.query(Offer).count() == 0


def test_worker_creates_offer_for_client_with_one_active_deposit(session, seeded):
    client = session.get(Client, seeded["client_id"])
    client.active_deposits_count = 1
    session.commit()

    offer = handle_event(salary_event(seeded["client_id"], "evt-one-deposit"), session)

    assert offer is not None
    assert offer.client_id == seeded["client_id"]
    assert session.query(Offer).filter_by(event_id="evt-one-deposit").count() == 1


def test_worker_redelivery_in_fresh_session_does_not_duplicate_offer(
    session, session_factory, seeded
):
    first = handle_event(salary_event(seeded["client_id"], "evt-fresh-session"), session)
    assert first is not None

    with session_factory() as other_session:
        second = handle_event(
            salary_event(seeded["client_id"], "evt-fresh-session"), other_session
        )

        assert second is not None
        assert second.id == first.id
        assert other_session.query(Offer).filter_by(event_id="evt-fresh-session").count() == 1


def test_worker_redelivery_returns_existing_offer_after_status_change(session, seeded):
    first = handle_event(salary_event(seeded["client_id"], "evt-after-status"), session)
    assert first is not None
    first.status = "accepted"
    session.commit()

    second = handle_event(salary_event(seeded["client_id"], "evt-after-status"), session)

    assert second is not None
    assert second.id == first.id
    assert second.status == "accepted"
    assert session.query(Offer).filter_by(event_id="evt-after-status").count() == 1


def test_worker_creates_distinct_offers_for_distinct_events(session, seeded):
    first = handle_event(salary_event(seeded["client_id"], "evt-distinct-1"), session)
    second = handle_event(salary_event(seeded["client_id"], "evt-distinct-2"), session)

    assert first is not None
    assert second is not None
    assert first.id != second.id
    assert session.query(Offer).count() == 2


EVENT_BANNER_TYPES = ["salary", "purchase", "deposit_view", "high_balance"]


@pytest.mark.parametrize("event_type", EVENT_BANNER_TYPES)
def test_worker_maps_event_type_to_matching_banner_template(
    session, seeded, event_type
):
    offer = handle_event(
        {
            "event_id": f"evt-{event_type}",
            "client_id": seeded["client_id"],
            "event_type": event_type,
            "payload": {},
            "occurred_at": "2026-11-14T10:00:00+00:00",
        },
        session,
    )

    assert offer is not None
    assert offer.trigger_type == event_type
    template = session.get(BannerTemplate, offer.banner_template_id)
    assert template is not None
    assert template.type == event_type


class FakeTextGenerator:
    def __init__(self, text: OfferText | None) -> None:
        self.text = text
        self.calls = 0

    def generate(self, context):
        self.calls += 1
        return self.text


def test_worker_stores_generated_offer_text(session, seeded):
    generator = FakeTextGenerator(OfferText("Премия под 8%", "Отложите часть дохода"))

    offer = handle_event(
        salary_event(seeded["client_id"], "evt-generated"),
        session,
        text_generator=generator,
    )

    assert offer is not None
    assert generator.calls == 1
    assert offer.title == "Премия под 8%"
    assert offer.subtitle == "Отложите часть дохода"
    assert offer.message_text == "Премия под 8%"


def test_worker_falls_back_to_template_when_generation_fails(session, seeded):
    template = session.get(BannerTemplate, seeded["banner_template_id"])
    generator = FakeTextGenerator(None)

    offer = handle_event(
        salary_event(seeded["client_id"], "evt-fallback"),
        session,
        text_generator=generator,
    )

    assert offer is not None
    assert offer.title == template.title
    assert offer.subtitle == template.subtitle


class RecordingTextGenerator:
    def __init__(self) -> None:
        self.contexts = []

    def generate(self, context):
        self.contexts.append(context)
        index = len(self.contexts)
        return OfferText(f"Заголовок {index}", f"Подзаголовок {index}")


def test_worker_passes_previous_titles_to_next_generation(session, seeded):
    generator = RecordingTextGenerator()

    first = handle_event(
        salary_event(seeded["client_id"], "evt-repeat-1"),
        session,
        text_generator=generator,
    )
    second = handle_event(
        salary_event(seeded["client_id"], "evt-repeat-2"),
        session,
        text_generator=generator,
    )

    assert first is not None and second is not None
    assert generator.contexts[0].recent_titles == ()
    assert generator.contexts[1].recent_titles == ("Заголовок 1",)
    assert generator.contexts[1].style_hint
