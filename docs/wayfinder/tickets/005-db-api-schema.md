# 005: Схема БД и API

**Label:** `wayfinder:prototype`

## Question

Как должны быть организованы таблицы PostgreSQL и endpoints FastAPI для MVP?

Конкретно нужно решить:
1. Какие таблицы нужны (clients, accounts, transactions, events, products, offers, offer_history)?
2. Какие поля и связи между таблицами?
3. Какие endpoints необходимы (POST /events, GET /clients/{id}/offers, POST /offers/{id}/feedback, POST /generate-data)?
4. Какой формат ответа API (JSON schema для оффера)?
5. Нужна ли версионность схемы / миграции?

## Context

- Зависит от выбранных триггеров и стека docker-compose + PostgreSQL.
- API должен быть готов к интеграции с mock UI чата.

## Blocking

- Blocked by: [002: Настройка docker-compose и PostgreSQL](002-docker-postgres.md), [004: Финализация триггеров MVP](004-mvp-triggers.md)
- Unblocks: [006: Rule engine и генерация офферов](006-rule-engine.md), [007: Mock UI чата](007-mock-ui.md)

## Resolution

<!-- Заполняется при закрытии тикета -->
