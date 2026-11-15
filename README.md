# next_offer

ИИ-агент «проактивный консьерж» для мобильного банка. Анализирует события клиента
и превращает их в персональные предложения банковских продуктов в веб-интерфейсе.

Поток данных:

```
UI (React) -> POST /api/v1/events -> FastAPI producer -> RabbitMQ
           -> worker -> PostgreSQL -> GET /api/v1/clients/{id}/offers -> UI
```

## Что умеет MVP

- Принимает события клиента (`salary`, `purchase`, `deposit_view`, `high_balance`)
  и публикует их в durable-очередь RabbitMQ.
- Отдельный worker вычитывает события, подбирает шаблон баннера и создаёт оффер.
- Дашборд опрашивает API раз в 3 секунды, показывает офферы в карусели и
  toast-уведомлениях.
- Оффер можно принять, отклонить или закрыть (`accepted`, `declined`, `dismissed`).
- Повторная доставка события не создаёт дубль оффера (идемпотентность по `event_id`).
- Панель оператора позволяет выбрать клиента и симулировать события демо.

## Требования

- Docker Engine / Docker Desktop с Docker Compose v2.
- Python 3.11+ — только для локального запуска backend и тестов без Docker.
- Node.js 20+ и npm — только для локального запуска frontend и его тестов.

## Быстрый старт: весь стек одной командой

```bash
# 1. Скопируй env-файл
cp .env.example .env               # Linux/macOS
Copy-Item .env.example .env        # Windows PowerShell

# 2. Подними postgres, rabbitmq, app, worker и frontend
docker compose up --build
# Эквивалент: docker-compose up --build
```

Дождись статуса `healthy` у зависимостей и открой UI:
<http://localhost:5173>. API: <http://localhost:8000>, Swagger:
<http://localhost:8000/docs>.

Проверь приложение:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ при доступных PostgreSQL и RabbitMQ:

```json
{
  "status": "ok",
  "checks": { "database": "ok", "rabbitmq": "ok" }
}
```

Если зависимость недоступна, `/health` возвращает `503` и статус `degraded` с
причиной в `checks`. Этот же endpoint использует healthcheck контейнера `app`.

RabbitMQ management UI: <http://localhost:15672> (по умолчанию `nextoffer` /
`nextoffer`).

### Обновление уже существующего Docker-тома

`migrations/init.sql` выполняется PostgreSQL только при создании пустого тома.
Чтобы аддитивные изменения схемы (таблица `banner_templates`, колонки
`banner_template_id`, `event_id`, `shown_at`, `responded_at`) применились к уже
существующей базе, API и worker при старте выполняют идемпотентную миграцию
(`app/migrations.py`): они проверяют наличие таблиц/колонок и добавляют
недостающие. Ничего вручную делать не нужно — достаточно перезапустить стек.

Если вы хотите начать с полностью чистых демо-данных, удалите том явно:

```bash
docker compose down -v   # ВНИМАНИЕ: удаляет данные PostgreSQL и RabbitMQ
docker compose up --build
```

## Демо-сценарий

1. Запусти весь стек: `docker compose up --build`.
2. Открой <http://localhost:5173>.
3. В правой панели «Симулятор событий» выбери клиента (например, «Иван Петров»).
4. Нажми «Пришла зарплата +150 000 ₽».
5. В течение ~3 секунд в карусели появится баннер «Сохраните зарплату под 8%»,
   а справа сверху — toast-уведомление.
6. Нажми «Открыть счёт» (accepted), «Отклонить» (declined) или закрой
   предложение — оно исчезнет из активной карусели, а связанный toast закроется.
7. Повтори сценарий для `purchase`, `deposit_view` или `high_balance`.

Полный сценарий можно проверить скриптом против запущенного стека:

```bash
python scripts/e2e_demo.py --base-url http://localhost:8000 --client-id 1
```

Скрипт проверяет `/health`, отправляет событие, ждёт новый оффер в API,
отправляет `accepted` и убеждается, что оффер ушёл из активного списка.

### Локальный запуск frontend без Docker

Для разработки UI удобнее dev-сервер Vite на хосте:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

UI по-прежнему обращается к API по `VITE_API_BASE_URL`
(по умолчанию `http://localhost:8000`).

## Переменные окружения

Backend и инфраструктура (см. `.env.example`):

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `POSTGRES_USER` | `next_offer` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | `change_me` | Пароль PostgreSQL |
| `POSTGRES_DB` | `next_offer` | Имя базы |
| `POSTGRES_PORT` | `5432` | Порт PostgreSQL на хосте |
| `APP_PORT` | `8000` | Порт API на хосте |
| `RABBITMQ_USER` | `next_offer` | Пользователь RabbitMQ |
| `RABBITMQ_PASSWORD` | `change_me` | Пароль RabbitMQ |
| `RABBITMQ_PORT` | `5672` | AMQP-порт на хосте |
| `RABBITMQ_MANAGEMENT_PORT` | `15672` | Порт management UI на хосте |
| `FRONTEND_PORT` | `5173` | Порт UI (Vite dev server) на хосте |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Базовый URL API для frontend-контейнера |
| `VITE_CLIENT_ID` | `1` | Клиент, выбранный при загрузке UI |
| `CORS_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` | JSON-список origin'ов фронтенда |
| `DATABASE_URL` | собирается в `docker-compose.yml` | SQLAlchemy URL PostgreSQL |
| `RABBITMQ_URL` | собирается в `docker-compose.yml` | AMQP URL брокера |
| `UVICORN_HOST` / `UVICORN_PORT` | `0.0.0.0` / `8000` | Адрес API внутри контейнера |
| `WORKER_HEARTBEAT_PATH` | `/tmp/next_offer_worker_heartbeat` | Файл heartbeat worker'а для healthcheck |
| `WORKER_HEARTBEAT_MAX_AGE_SECONDS` | `20` | Допустимый возраст heartbeat |

Yandex AI Studio / YandexGPT (опционально):

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `LLM_ENABLED` | `false` | Генерировать текст оффера через LLM |
| `YANDEX_API_KEY` | — | API-ключ сервисного аккаунта |
| `YANDEX_FOLDER_ID` | — | Каталог Yandex Cloud |
| `YANDEX_MODEL` | `yandexgpt-lite` | Модель |
| `YANDEX_MODEL_VERSION` | `latest` | Версия модели |
| `YANDEX_MODEL_URI` | — | Полный `gpt://...` override (перекрывает model/version) |
| `YANDEX_TIMEOUT_SECONDS` | `10` | Таймаут запроса |
| `YANDEX_TEMPERATURE` | `0.7` | Температура генерации |
| `YANDEX_MAX_TOKENS` | `200` | Лимит токенов ответа |

При `LLM_ENABLED=false` или ошибке LLM worker использует текст из `banner_templates`.

Frontend (см. `frontend/.env.example`):

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Базовый URL API |
| `VITE_CLIENT_ID` | `1` | Клиент, выбранный при загрузке UI |

## Healthchecks

| Сервис | Проверка |
| --- | --- |
| `postgres` | `pg_isready` |
| `rabbitmq` | `rabbitmq-diagnostics -q ping` |
| `app` | `GET /health` (PostgreSQL + RabbitMQ) |
| `worker` | Свежесть heartbeat-файла, который обновляет consumer-процесс |

`app` и `worker` стартуют только после `healthy` у `postgres` и `rabbitmq`.

## API

- `GET /health` — `200 {"status": "ok", "checks": {...}}` или `503` при degraded.
- `POST /api/v1/events` — принять событие, опубликовать в RabbitMQ, вернуть `202`.
- `GET /api/v1/clients` — список клиентов для панели оператора.
- `GET /api/v1/clients/{client_id}/offers` — офферы с полями баннера. По
  умолчанию возвращает только активные (`pending`, `shown`), не более 5
  последних (`?limit=1..50`); принятые, отклонённые и закрытые в список не
  попадают. При первом показе `pending` переходит в `shown` и заполняется
  `shown_at`. Параметр `?include_responded=true` возвращает все статусы,
  включая `accepted`, `declined` и `dismissed`.
- `POST /api/v1/offers/{offer_id}/feedback` — `accepted`, `declined` или
  `dismissed`; обновляет статус и `responded_at`.

Пример события:

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "event_type": "salary", "payload": {"amount": 150000}}'
```

## Тесты

Backend (Docker не нужен: SQLite in-memory + записывающий publisher + worker seam,
плюс in-process E2E-тест полного сценария):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

По умолчанию тесты идут на in-memory SQLite. Чтобы прогнать их на реальном
PostgreSQL (рекомендуется перед релизом), задайте `TEST_DATABASE_URL` — тестовая
база должна быть пустой и доступной, схема создаётся/удаляется на каждом тесте:

```bash
export TEST_DATABASE_URL=postgresql+psycopg://next_offer:change_me@localhost:5432/next_offer_test
pytest
```

Без `TEST_DATABASE_URL` тест PostgreSQL-пути помечается `skipped`.

Frontend:

```bash
cd frontend
npm install
npm test        # vitest
npm run build   # tsc --noEmit + vite build
```

## Структура

```
.
├── app/
│   ├── api/          # API-роутеры
│   ├── services/     # Обработка событий и создание офферов
│   ├── config.py     # Настройки из окружения
│   ├── db.py         # SQLAlchemy подключение
│   ├── health.py     # Проверки PostgreSQL и RabbitMQ
│   ├── messaging.py  # RabbitMQ publisher
│   ├── migrations.py # Идемпотентная миграция существующих томов
│   ├── models.py     # SQLAlchemy модели
│   ├── seed.py       # Демо-данные для тестов
│   ├── worker.py     # Consumer очереди + heartbeat
│   └── main.py       # FastAPI entrypoint
├── frontend/         # React + Vite + TypeScript дашборд (+ Dockerfile)
├── migrations/       # init.sql + demo seed
├── scripts/          # Генератор данных, healthcheck, e2e_demo.py
├── tests/            # HTTP seam, worker seam, health, E2E
├── docs/             # Требования и wayfinder-карта
├── docker-compose.yml
└── Dockerfile
```

## Локальная разработка backend без Docker

Нужны доступные PostgreSQL и RabbitMQ (можно поднять только их:
`docker compose up postgres rabbitmq`).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://next_offer:change_me@localhost:5432/next_offer
export RABBITMQ_URL=amqp://nextoffer:nextoffer@localhost:5672/
uvicorn app.main:app --reload
# в другом терминале:
python -m app.worker
```

## Деплой демо

Фронтенд — GitHub Pages, бэкенд — VPS с Docker Compose и Caddy. Пошаговая
инструкция: [deploy/README.md](deploy/README.md).

## Документация

- [Требования](docs/requirements.md)
- [Wayfinder map](docs/wayfinder/map.md)
