# Wayfinder Map: Проактивный консьерж MVP

**Label:** `wayfinder:map`

## Destination

> Рабочий MVP ИИ-агента «Проактивный консьерж» для АК БАРС Онлайн, развёрнутый локально через `docker-compose` с PostgreSQL, с генератором синтетических клиентских данных и транзакций. Агент анализирует транзакции и цифровое поведение, по заданным правилам предлагает релевантные продукты (вклады/накопительные счёта в приоритете) и отдаёт офферы через API, готовый к интеграции с чатом мобильного приложения.

## Notes

- **Домен:** банковская розница, проактивные предложения, триггерный маркетинг.
- **Скиллы на каждую сессию:** `domain-modeling` (для терминов), `grilling` (для уточнений), `prototype` (для макетов), `research` (для LLM).
- **Предпочтения этого effort:** скорость (ASAP), локальная разработка, тестовые данные, минимальная регуляторика.
- **Канал:** MVP — чат; пуши архитектурно закладываются, но не реализуются.
- **Scope MVP:** 3 триггера максимум.

## Decisions so far

<!-- Индекс: одна строка на закрытый тикет -->

- [destination pinned by user](requirements.md): MVP = docker-compose + PostgreSQL + генератор данных + 3 триггера + чат-API, LLM пока не определён.

## Not yet specified

<!-- Туман войны: in-scope, но пока нечётко -->

- Как масштабировать с 3 триггеров MVP на полный набор из 26.
- Как интегрироваться с реальным API АК БАРС Онлайн (mobile backend).
- Безопасность и регуляторика при переходе от тестовых данных к реальным.
- A/B-тестирование офферов и метрики эффективности.
- Персистентность логов решений агента для аудита.
- Управление частотой показа офферов (fatigue rules).
- Персонализация текста оффера под сегмент клиента.

## Out of scope

<!-- Работа за пределами destination -->

- Интеграция с реальными банковскими системами в рамках MVP.
- Создание заявок на маркетинговые коммуникации в Jira.
- Production deployment, CI/CD, мониторинг.
- Реализация всех 26 триггеров в MVP.
- Пуш-уведомления в MVP (архитектурно закладываются).

---

## Frontier

Открытые, незаблокированные, не назначенные тикеты:

1. [001: Выбор LLM-провайдера](tickets/001-llm-provider.md)
2. [002: Настройка docker-compose и PostgreSQL](tickets/002-docker-postgres.md)
3. [004: Финализация триггеров MVP](tickets/004-mvp-triggers.md)

## Blocked tickets

- [003: Генератор тестовых данных](tickets/003-data-generator.md) ← blocked by [002](tickets/002-docker-postgres.md)
- [005: Схема БД и API](tickets/005-db-api-schema.md) ← blocked by [002](tickets/002-docker-postgres.md), [004](tickets/004-mvp-triggers.md)
- [006: Rule engine и генерация офферов](tickets/006-rule-engine.md) ← blocked by [001](tickets/001-llm-provider.md), [004](tickets/004-mvp-triggers.md), [005](tickets/005-db-api-schema.md)
- [007: Mock UI чата](tickets/007-mock-ui.md) ← blocked by [005](tickets/005-db-api-schema.md)
- [008: End-to-end тестирование MVP](tickets/008-e2e-test.md) ← blocked by [003](tickets/003-data-generator.md), [006](tickets/006-rule-engine.md), [007](tickets/007-mock-ui.md)
