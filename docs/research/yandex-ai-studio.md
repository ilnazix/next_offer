# Yandex AI Studio / YandexGPT — интеграционные заметки

**Дата:** 15.11.2026
**Контекст:** подключение LLM к worker'у next_offer для генерации текста оффера.
**Статус источников:** `aistudio.yandex.ru` и `yandex.cloud` отдают SmartCaptcha автоматическим клиентам. Использованы официальные primary sources:
- protobuf-контракты `yandex-cloud/cloudapi` (`foundation_models/v1/text_generation_service.proto`, `text_common.proto`);
- официальный Python SDK `yandex-cloud/yandex-cloud-ml-sdk` (пакет `yandex-ai-studio-sdk`), примеры и тестовые кассеты.

## REST-контракт

```
POST https://llm.api.cloud.yandex.net/foundationModels/v1/completion
Content-Type: application/json
Authorization: Api-Key <API_KEY>        # либо: Bearer <IAM_TOKEN>
```

Тело запроса:

```json
{
  "modelUri": "gpt://<folder_id>/yandexgpt-lite/latest",
  "completionOptions": {
    "stream": false,
    "temperature": 0.3,
    "maxTokens": "200"
  },
  "messages": [
    { "role": "system", "text": "..." },
    { "role": "user", "text": "..." }
  ]
}
```

Ответ (сокращённо):

```json
{
  "alternatives": [
    { "message": { "role": "assistant", "text": "..." }, "status": "ALTERNATIVE_STATUS_FINAL" }
  ],
  "usage": { "inputTextTokens": "...", "completionTokens": "...", "totalTokens": "..." },
  "modelVersion": "..."
}
```

## Ключевые факты

- **modelUri:** `gpt://<folder_id>/<model>/<version>`.
  Подтверждено кассетой официального SDK: `gpt://b1ghsjum2v37c2un8h64/yandexgpt/latest`.
- **Модели:** `yandexgpt`, `yandexgpt-lite`, `yandexgpt-32k`; версии `latest`, `rc`, `deprecated`.
  Для MVP хватает `yandexgpt-lite/latest` (дешевле и быстрее).
- **Auth:** API-ключ сервисного аккаунта → `Authorization: Api-Key <key>`; IAM-токен → `Bearer <token>`.
  В SDK: env `YC_API_KEY` / `YC_IAM_TOKEN`, folder — `YC_FOLDER_ID`.
- **Roles:** `system`, `user`, `assistant`.
- **`temperature`:** 0..1, дефолт 0.3. **`maxTokens`:** ограничение генерации.
- **`stream: false`** — простой синхронный ответ; streaming не нужен для оффера.
- **Статусы alternative:** `FINAL`, `TRUNCATED_FINAL`, `CONTENT_FILTER`, `TOOL_CALLS`, `PARTIAL`.
  При `CONTENT_FILTER`/`TRUNCATED_FINAL` текст может быть непригоден → fallback на шаблон.
- **Content filter** может отклонить prompt/ответ.
- **SDK (альтернатива raw HTTP):** `pip install yandex-ai-studio-sdk`,
  `AIStudio(folder_id="...", auth="<APIKey>")`, `sdk.models.completions("yandexgpt")`.
  Для нашего проекта достаточно `httpx` (уже в зависимостях), без нового SDK.

## Предлагаемая интеграция в next_offer

Точка вызова — **worker**, при создании оффера:

```
event → worker → контекст клиента + продукт + триггер → OfferTextGenerator
                                                         ├─ YandexGptTextGenerator (httpx)
                                                         └─ TemplateTextGenerator (fallback)
                                                         ↓
                                                   offers.title/subtitle
```

- Абстракция `OfferTextGenerator` с двумя реализациями: YandexGPT и шаблон.
- Конфиг через env (всё изменяемое — в конфигурации, не в коде):

  | Переменная | По умолчанию | Назначение |
  | --- | --- | --- |
  | `LLM_ENABLED` | `false` | Включает генерацию через LLM |
  | `YANDEX_API_KEY` | — | API-ключ сервисного аккаунта |
  | `YANDEX_FOLDER_ID` | — | Каталог Yandex Cloud |
  | `YANDEX_MODEL` | `yandexgpt-lite` | Имя модели |
  | `YANDEX_MODEL_VERSION` | `latest` | Версия модели (`latest`/`rc`/`deprecated`) |
  | `YANDEX_MODEL_URI` | — | Полный override `gpt://...`; если задан, перекрывает model/version |
  | `YANDEX_TIMEOUT_SECONDS` | `10` | Таймаут запроса |
  | `YANDEX_TEMPERATURE` | `0.3` | Температура генерации |
  | `YANDEX_MAX_TOKENS` | `200` | Лимит токенов ответа |

  Итоговый `modelUri` собирается как `gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}/{YANDEX_MODEL_VERSION}`, если не задан `YANDEX_MODEL_URI`.
- При ошибке/таймауте/content filter — fallback на текст из `banner_templates`.
- Генерируем только заголовок/подзаголовок; цвет/иконка остаются из шаблона.
- Данные клиента: только синтетические, минимальный контекст (сегмент, событие, продукт). Без ФИО/номеров счетов.
- Тесты: стаб-генератор, без реальных сетевых вызовов; опциональный live-тест под env-флагом.

## Что нужно от пользователя

- `YANDEX_API_KEY` — API-ключ сервисного аккаунта Yandex Cloud.
- `YANDEX_FOLDER_ID` — folder id каталога, где включён AI Studio.
- Подтвердить модель: `yandexgpt-lite` (рекомендуется для MVP) или `yandexgpt`.

## Открытые вопросы

- Квота/биллинг каталога.
- Нужен ли стриминг (сейчас нет).
- Нужно ли логировать usage/tokens для аналитики.
