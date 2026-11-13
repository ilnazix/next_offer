# next_offer

ИИ-агент «проактивный консьерж» для мобильного банка. Анализирует транзакции и жизненные сценарии клиентов, чтобы предложить подходящий банковский продукт в нужный момент.

## Быстрый старт

```bash
# 1. Скопируй env-файл
Copy-Item .env.example .env        # Windows PowerShell
cp .env.example .env               # Linux/macOS

# 2. Подними стек
docker-compose up --build

# 3. Проверь health
curl http://localhost:8000/health
```

## Структура

```
.
├── app/              # FastAPI приложение
│   ├── api/          # API роутеры
│   ├── services/     # Обработка событий и создание офферов
│   ├── config.py     # Настройки
│   ├── db.py         # SQLAlchemy подключение
│   ├── messaging.py  # RabbitMQ publisher
│   ├── models.py     # SQLAlchemy модели
│   ├── worker.py     # Consumer очереди событий
│   └── main.py       # Точка входа
├── migrations/       # SQL-миграции (init.sql + demo seed)
├── scripts/          # Генератор данных
├── tests/            # HTTP seam и worker seam тесты
├── docs/             # Требования и wayfinder-карта
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

## API

- `GET /health` — проверка состояния
- `POST /api/v1/events` — принять событие, опубликовать в RabbitMQ, вернуть `202`
- `GET /api/v1/clients` — список клиентов для панели оператора
- `GET /api/v1/clients/{client_id}/offers` — активные офферы клиента с полями баннера
- `POST /api/v1/offers/{offer_id}/feedback` — реакция на оффер (заглушка)

Сценарий зарплаты сразу после запуска: клиент `1`, событие `{"client_id": 1, "event_type": "salary", "payload": {"amount": 150000}}`.
Симулятор событий поддерживает типы `salary`, `purchase`, `deposit_view`, `high_balance`.

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

Тесты не требуют Docker: HTTP seam использует SQLite in-memory и подменяет
RabbitMQ publisher, worker seam вызывает обработчик события напрямую.

## Документация

- [Требования](docs/requirements.md)
- [Wayfinder map](docs/wayfinder/map.md)

## Локальная разработка без Docker

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
