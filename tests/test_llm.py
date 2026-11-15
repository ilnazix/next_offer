import json
from dataclasses import replace

import httpx
import pytest

from app.config import Settings
from app.llm import (
    OfferContext,
    TemplateTextGenerator,
    YandexGptTextGenerator,
    build_text_generator,
    parse_offer_text,
)


def make_context() -> OfferContext:
    return OfferContext(
        event_type="salary",
        event_description="на счёт поступила крупная сумма — зарплата или премия",
        client_segment="mass",
        product_name="Накопительный счёт",
        product_rate="8",
        product_min_amount="1000",
        product_term_months=None,
        event_details={"amount": 150000},
        template_title="Сохраните зарплату под 8%",
        template_subtitle="Отложите часть на накопительный счёт",
    )


def yandex_generator(handler, **overrides) -> YandexGptTextGenerator:
    kwargs = {
        "api_key": "test-key",
        "folder_id": "b1g-test-folder",
        "model": "yandexgpt",
        "model_version": "latest",
        "transport": httpx.MockTransport(handler),
    }
    kwargs.update(overrides)
    return YandexGptTextGenerator(**kwargs)


def test_parse_offer_text_accepts_json():
    text = parse_offer_text('{"title": "Отложите премию", "subtitle": "Под 8% годовых"}')

    assert text is not None
    assert text.title == "Отложите премию"
    assert text.subtitle == "Под 8% годовых"


def test_parse_offer_text_falls_back_to_plain_text():
    text = parse_offer_text("Отложите премию\nПод 8% годовых")

    assert text is not None
    assert text.title == "Отложите премию"
    assert text.subtitle == "Под 8% годовых"


def test_parse_offer_text_returns_none_for_empty_answer():
    assert parse_offer_text("   ") is None


def test_yandex_generator_builds_request_and_parses_answer():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["body"] = json.loads(request.read())
        return httpx.Response(
            200,
            json={
                "result": {
                    "alternatives": [
                        {
                            "status": "ALTERNATIVE_STATUS_FINAL",
                            "message": {
                                "role": "assistant",
                                "text": '{"title": "Сохраните премию", "subtitle": "Накопительный счёт под 8%"}',
                            },
                        }
                    ]
                }
            },
        )

    generator = yandex_generator(handler)
    result = generator.generate(make_context())

    assert result is not None
    assert result.title == "Сохраните премию"
    assert result.subtitle == "Накопительный счёт под 8%"
    assert captured["url"].endswith("/foundationModels/v1/completion")
    assert captured["auth"] == "Api-Key test-key"
    assert captured["body"]["modelUri"] == "gpt://b1g-test-folder/yandexgpt/latest"
    assert captured["body"]["jsonObject"] is True


def test_yandex_generator_uses_model_uri_override():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.read())
        return httpx.Response(
            200,
            json={
                "alternatives": [
                    {
                        "status": "ALTERNATIVE_STATUS_FINAL",
                        "message": {"text": '{"title": "A", "subtitle": "B"}'},
                    }
                ]
            },
        )

    generator = yandex_generator(
        handler, model_uri="gpt://custom/folder/model/latest"
    )
    generator.generate(make_context())

    assert captured["body"]["modelUri"] == "gpt://custom/folder/model/latest"


def test_yandex_prompt_includes_event_facts():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        captured["user"] = body["messages"][-1]["text"]
        return httpx.Response(
            200,
            json={
                "result": {
                    "alternatives": [
                        {
                            "status": "ALTERNATIVE_STATUS_FINAL",
                            "message": {"text": '{"title": "A", "subtitle": "B"}'},
                        }
                    ]
                }
            },
        )

    yandex_generator(handler).generate(make_context())

    assert "зарплата или премия" in captured["user"]
    assert "150 000" in captured["user"]
    assert "не копируй" in captured["user"]
    assert "массовый сегмент" in captured["user"]


def test_yandex_prompt_avoids_recent_titles_and_uses_style_hint():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        captured["user"] = body["messages"][-1]["text"]
        return httpx.Response(
            200,
            json={
                "result": {
                    "alternatives": [
                        {
                            "status": "ALTERNATIVE_STATUS_FINAL",
                            "message": {"text": '{"title": "A", "subtitle": "B"}'},
                        }
                    ]
                }
            },
        )

    context = replace(
        make_context(),
        recent_titles=("Старый заголовок", "Ещё один"),
        style_hint="выгода в процентах",
    )
    yandex_generator(handler).generate(context)

    assert "Старый заголовок" in captured["user"]
    assert "Не повторяй" in captured["user"]
    assert "выгода в процентах" in captured["user"]


def test_yandex_generator_returns_none_on_content_filter():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "result": {
                    "alternatives": [
                        {"status": "ALTERNATIVE_STATUS_CONTENT_FILTER", "message": {}}
                    ]
                }
            },
        )

    assert yandex_generator(handler).generate(make_context()) is None


def test_yandex_generator_returns_none_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "boom"})

    assert yandex_generator(handler).generate(make_context()) is None


def test_build_text_generator_disabled_returns_template():
    generator = build_text_generator(Settings(llm_enabled=False))

    assert isinstance(generator, TemplateTextGenerator)


def test_build_text_generator_without_credentials_returns_template():
    generator = build_text_generator(
        Settings(llm_enabled=True, yandex_api_key="", yandex_folder_id="")
    )

    assert isinstance(generator, TemplateTextGenerator)


def test_template_generator_returns_template_text():
    result = TemplateTextGenerator().generate(make_context())

    assert result is not None
    assert result.title == "Сохраните зарплату под 8%"
    assert result.subtitle == "Отложите часть на накопительный счёт"
