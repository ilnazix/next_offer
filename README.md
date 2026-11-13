# Rozochka — Проактивный консьерж

MVP ИИ-агента для мобильного приложения банка. Анализирует транзакции и поведение клиентов, чтобы предложить подходящий банковский продукт в нужный момент.

## Быстрый старт

```bash
# 1. Скопируй env-файл
Copy-Item .env.example .env        # Windows PowerShell
cp .env.example .env               # Linux/macOS

# 2. Подними стек
docker-compose up --build

# 3. Проверь health
open http://localhost:8000/health  # или curl http://localhost:8000/health
```

## Структура

```
.
├── app/              # FastAPI приложение
│   ├── api/          # API роутеры
│   ├── config.py     # Настройки
│   ├── db.py         # SQLAlchemy подключение
│   └── main.py       # Точка входа
├── migrations/       # SQL-миграции (init.sql)
├── scripts/          # Генератор данных
├── docs/             # Требования и wayfinder-карта
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API (заглушки)

- `GET /health` — проверка состояния
- `GET /api/v1/offers/{client_id}` — офферы клиента
- `POST /api/v1/events` — событие от клиента/транзакции
- `POST /api/v1/offers/{offer_id}/feedback` — реакция на оффер

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
