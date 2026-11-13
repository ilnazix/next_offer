# 002: Настройка docker-compose и PostgreSQL

**Label:** `wayfinder:task`

## Question

Какой базовый стек развёртывания использовать для локального MVP?

Конкретно нужно решить:
1. Какие сервисы поднимаем в docker-compose (PostgreSQL, FastAPI, возможно генератор данных, возможно LLM)?
2. Как организуем миграции БД (ручные SQL, Alembic, или init-скрипты)?
3. Какие версии образов использовать?
4. Как пробрасывать порты и переменные окружения?
5. Нужен ли healthcheck / зависимости сервисов (FastAPI ждёт PostgreSQL)?

## Context

- Пользователь хочет локальный docker-compose + PostgreSQL.
- MVP за вечер: конфигурация должна быть минимальной, но воспроизводимой.
- Стек: Python + FastAPI.

## Blocking

- Blocks: [003: Генератор тестовых данных](003-data-generator.md), [005: Схема БД и API](005-db-api-schema.md)
- Unblocks: —

## Resolution

<!-- Заполняется при закрытии тикета -->
