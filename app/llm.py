"""Offer text generation.

The worker asks an ``OfferTextGenerator`` for the banner title and subtitle.
When LLM generation is disabled or fails for any reason, the template text is
used instead so an offer is still created.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from app.config import Settings, settings

logger = logging.getLogger(__name__)

YANDEX_COMPLETION_URL = (
    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
)

SYSTEM_PROMPT = (
    "Ты — персональный финансовый консьерж банка. Пишешь короткие персональные "
    "предложения по конкретному событию клиента. Опирайся на факты из контекста "
    "(сумма, остаток, продукт, ставка), не пересказывай черновой шаблон дословно. "
    "Не обещай гарантированную доходность и не выдумывай условия продукта. "
    "Верни строго JSON без пояснений."
)

EVENT_DESCRIPTIONS = {
    "salary": "на счёт поступила крупная сумма — зарплата или премия",
    "salary_received": "на счёт поступила зарплата",
    "purchase": "клиент совершил крупную покупку",
    "deposit_view": "клиент интересовался вкладами, но не открыл продукт",
    "high_balance": "на счету держится высокий остаток",
}

SEGMENT_LABELS = {
    "mass": "массовый сегмент",
    "premium": "премиальный сегмент",
    "salary": "зарплатный клиент",
    "pension": "пенсионер",
}

_EVENT_DETAIL_LABELS = {
    "amount": "сумма",
    "balance": "остаток",
    "category": "категория",
    "merchant": "магазин",
}


def describe_event(event_type: str) -> str:
    return EVENT_DESCRIPTIONS.get(event_type, event_type)


def describe_segment(segment: str | None) -> str:
    if not segment:
        return "неизвестен"
    return SEGMENT_LABELS.get(segment, segment)


def format_amount(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", " ")
    return f"{number:,.2f}".replace(",", " ").replace(".", ",")


def format_event_details(details: dict[str, Any]) -> str:
    parts = []
    for key, label in _EVENT_DETAIL_LABELS.items():
        value = details.get(key)
        if value in (None, ""):
            continue
        if key in ("amount", "balance"):
            value = format_amount(value)
        parts.append(f"{label}: {value}")
    return "; ".join(parts) if parts else "нет"


@dataclass(frozen=True)
class OfferContext:
    event_type: str
    event_description: str = ""
    client_segment: str | None = None
    product_name: str = ""
    product_rate: str | None = None
    product_min_amount: str | None = None
    product_term_months: int | None = None
    event_details: dict[str, Any] = field(default_factory=dict)
    template_title: str = ""
    template_subtitle: str | None = None
    recent_titles: tuple[str, ...] = ()
    style_hint: str | None = None


@dataclass(frozen=True)
class OfferText:
    title: str
    subtitle: str | None = None


class OfferTextGenerator(Protocol):
    def generate(self, context: OfferContext) -> OfferText | None:
        ...


class TemplateTextGenerator:
    """Deterministic fallback that reuses the banner template text."""

    def generate(self, context: OfferContext) -> OfferText | None:
        return OfferText(context.template_title, context.template_subtitle)


def _truncate(value: str, limit: int) -> str:
    value = value.strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def parse_offer_text(raw: str) -> OfferText | None:
    """Parse an LLM answer into a title/subtitle pair.

    Accepts the requested JSON shape and degrades gracefully to a plain-text
    answer (first line = title, the rest = subtitle).
    """

    raw = (raw or "").strip()
    if not raw:
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, dict):
        title = str(data.get("title") or "").strip()
        subtitle = str(data.get("subtitle") or "").strip()
        if title:
            return OfferText(_truncate(title, 255), _truncate(subtitle, 500) or None)

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return None
    title = _truncate(lines[0], 255)
    subtitle = _truncate(" ".join(lines[1:]), 500) or None
    return OfferText(title, subtitle)


class YandexGptTextGenerator:
    def __init__(
        self,
        *,
        api_key: str,
        folder_id: str,
        model: str,
        model_version: str,
        model_uri: str = "",
        timeout: float = 10.0,
        temperature: float = 0.5,
        max_tokens: int = 200,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = model
        self.model_version = model_version
        self.model_uri = model_uri
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._transport = transport

    @property
    def resolved_model_uri(self) -> str:
        if self.model_uri:
            return self.model_uri
        return f"gpt://{self.folder_id}/{self.model}/{self.model_version}"

    def _build_user_prompt(self, context: OfferContext) -> str:
        rate = f"{context.product_rate}% годовых" if context.product_rate else "не указана"
        min_amount = (
            f"{format_amount(context.product_min_amount)} ₽"
            if context.product_min_amount
            else "не указана"
        )
        term = (
            f"{context.product_term_months} мес."
            if context.product_term_months
            else "не указан"
        )
        segment = describe_segment(context.client_segment)
        details = format_event_details(context.event_details)

        lines = [
            "Примеры стиля (не копируй числа):",
            '{"title": "150 000 ₽ уже на счёте", "subtitle": "Отложите часть на накопительный счёт под 8% — деньги начнут работать"}',
            '{"title": "Вклад под 8,5% ещё доступен", "subtitle": "Вы смотрели вклады — оформите онлайн за пару минут"}',
            "",
            "Факты:",
            f"- Событие: {context.event_description}",
            f"- Клиент: {segment}",
            f"- Детали события: {details}",
            f"- Продукт: {context.product_name}; ставка: {rate}; "
            f"мин. сумма: {min_amount}; срок: {term}",
            f"- Черновой вариант банка (не копируй дословно): "
            f"{context.template_title} — {context.template_subtitle or ''}",
        ]
        if context.recent_titles:
            lines.append(
                "- Ранее клиенту уже показывали: "
                + "; ".join(context.recent_titles)
                + ". Не повторяй эти формулировки."
            )
        if context.style_hint:
            lines.append(f"- Сделай акцент: {context.style_hint}.")

        lines.extend(
            [
                "",
                "Задача: придумай персональное предложение.",
                "Требования:",
                "- title до 60 символов, конкретный и цепляющий;",
                "- subtitle до 120 символов, объясняет выгоду и следующий шаг;",
                "- используй максимум одно число из фактов;",
                "- не повторяй черновой вариант дословно;",
                "- без гарантий доходности и выдуманных условий.",
                'Верни JSON: {"title": "...", "subtitle": "..."}',
            ]
        )
        return "\n".join(lines)

    def _payload(self, context: OfferContext) -> dict:
        return {
            "modelUri": self.resolved_model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": str(self.max_tokens),
            },
            "messages": [
                {"role": "system", "text": SYSTEM_PROMPT},
                {"role": "user", "text": self._build_user_prompt(context)},
            ],
            "jsonObject": True,
        }

    def generate(self, context: OfferContext) -> OfferText | None:
        try:
            with httpx.Client(
                timeout=self.timeout, transport=self._transport
            ) as client:
                response = client.post(
                    YANDEX_COMPLETION_URL,
                    headers={
                        "Authorization": f"Api-Key {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=self._payload(context),
                )
        except Exception:
            logger.exception("YandexGPT request failed; falling back to template text")
            return None

        if response.status_code >= 400:
            logger.warning(
                "YandexGPT HTTP %s: %s (falling back to template text)",
                response.status_code,
                response.text[:500],
            )
            return None

        try:
            data = response.json()
        except ValueError:
            logger.warning("YandexGPT returned a non-JSON response; using template text")
            return None

        result = data.get("result", data)
        alternatives = result.get("alternatives") or []
        if not alternatives:
            logger.warning("YandexGPT returned no alternatives")
            return None

        alternative = alternatives[0]
        if alternative.get("status") == "ALTERNATIVE_STATUS_CONTENT_FILTER":
            logger.warning("YandexGPT response was filtered; using template text")
            return None

        text = (alternative.get("message") or {}).get("text") or ""
        parsed = parse_offer_text(text)
        if parsed is None:
            logger.warning("Could not parse YandexGPT answer; using template text")
        return parsed


def build_text_generator(
    config: Settings = settings,
    transport: httpx.BaseTransport | None = None,
) -> OfferTextGenerator:
    if not config.llm_enabled:
        return TemplateTextGenerator()

    if not config.yandex_api_key:
        logger.warning("LLM_ENABLED is true but YANDEX_API_KEY is empty; using templates")
        return TemplateTextGenerator()

    if not config.yandex_folder_id and not config.yandex_model_uri:
        logger.warning(
            "LLM_ENABLED is true but neither YANDEX_FOLDER_ID nor "
            "YANDEX_MODEL_URI is set; using templates"
        )
        return TemplateTextGenerator()

    return YandexGptTextGenerator(
        api_key=config.yandex_api_key,
        folder_id=config.yandex_folder_id,
        model=config.yandex_model,
        model_version=config.yandex_model_version,
        model_uri=config.yandex_model_uri,
        timeout=config.yandex_timeout_seconds,
        temperature=config.yandex_temperature,
        max_tokens=config.yandex_max_tokens,
        transport=transport,
    )
