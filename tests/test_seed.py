from sqlalchemy import select

from app.models import BannerTemplate, Client


EVENT_BANNER_TYPES = {"salary", "purchase", "deposit_view", "high_balance"}


def test_seed_contains_templates_for_all_four_event_types(session, seeded):
    templates = session.scalars(select(BannerTemplate)).all()
    templates_by_type = {template.type: template for template in templates}

    assert EVENT_BANNER_TYPES <= set(templates_by_type)
    for banner_type in EVENT_BANNER_TYPES:
        template = templates_by_type[banner_type]
        assert template.title
        assert template.subtitle
        assert template.background_color
        assert template.icon
        assert template.action_text
        assert template.product_id is not None


def test_seed_contains_multiple_selectable_clients(session, seeded):
    clients = session.scalars(select(Client)).all()

    assert len(clients) >= 2
    assert len(seeded["client_ids"]) == len(clients)
