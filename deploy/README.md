# Деплой демо на один VPS

Один сервер отдаёт и статический фронтенд, и API. TLS — автоматически через
Caddy и бесплатный wildcard-DNS `sslip.io`, поэтому покупать домен не нужно.

```
https://next-offer.<IP>.sslip.io
  /        → Caddy → frontend/dist (статика React)
  /api/*   → Caddy → app:8000 (FastAPI)
  /health  → Caddy → app:8000
  /docs*   → Caddy → app:8000 (Swagger)
```

Фронт и API на одном origin, поэтому CORS для браузера не требуется.

## 1. Сервер

Требования: Ubuntu 22.04+, Docker Engine + Compose plugin, открытые порты 80/443.

```bash
sudo mkdir -p /opt/next_offer && sudo chown "$USER" /opt/next_offer
git clone https://github.com/ilnazix/next_offer.git /opt/next_offer
cd /opt/next_offer

cp deploy/.env.production.example .env
# отредактируй .env: пароли, API_DOMAIN (sslip.io с IP сервера), CORS_ORIGINS, YANDEX_*
chmod 600 .env
mkdir -p frontend/dist

docker compose -f docker-compose.prod.yml up -d --build
```

`API_DOMAIN` — например `next-offer.203.0.113.10.sslip.io`. Caddy сам получит
TLS-сертификат Let's Encrypt.

Проверка:

```bash
curl "https://<API_DOMAIN>/health"
```

Ожидаемо: `{"status":"ok","checks":{"database":"ok","rabbitmq":"ok"}}`.

Демо-данные (клиенты, продукты, 4 шаблона) заливаются из `migrations/init.sql`
при создании пустого тома Postgres.

## 2. GitHub Actions

`.github/workflows/backend.yml` на каждый push в `master`:

1. Гоняет backend-тесты и frontend-тесты.
2. Собирает фронт с `VITE_API_BASE_URL=same-origin` (относительные запросы к `/api`)
   и кладёт `frontend/dist` в артефакт.
3. По SSH заливает `dist` на сервер, делает `git reset --hard origin/master`
   и `docker compose -f docker-compose.prod.yml up -d --build`.
4. Если задана переменная `API_BASE_URL`, прогоняет `scripts/e2e_demo.py`.

Секреты репозитория (Settings → Secrets and variables → Actions → Secrets):

| Секрет | Значение |
| --- | --- |
| `DEPLOY_HOST` | IP или DNS сервера |
| `DEPLOY_USER` | SSH-пользователь |
| `DEPLOY_SSH_KEY` | приватный SSH-ключ |
| `DEPLOY_PORT` | SSH-порт (по умолчанию 22) |
| `DEPLOY_PATH` | `/opt/next_offer` |

Переменная: `API_BASE_URL` = `https://<API_DOMAIN>`.

Рекомендуется создать Environment `production` с ручным подтверждением деплоя.

## 3. Что открыто наружу

- Только 80/443 (Caddy).
- Postgres, RabbitMQ и app доступны только внутри compose-сети.
- Management UI RabbitMQ наружу не публикуется.
- Секреты лежат только в `/opt/next_offer/.env` (`chmod 600`), в git не попадают.

## 4. Обновление и откат

Деплой — пуш в `master`.

Откат:

```bash
cd /opt/next_offer
git reset --hard <previous-sha>
docker compose -f docker-compose.prod.yml up -d --build
```

Миграции аддитивные, поэтому откат кода не ломает схему.

## 5. Публичное демо: риски

- API без авторизации: любой может слать события и расходовать квоту YandexGPT.
  Минимально: бюджетный алерт в Yandex Cloud, `YANDEX_MAX_TOKENS`, лимиты Yandex.
  Дальше: rate limit на прокси/Cloudflare или demo-token на `POST /events`.
- Только синтетические данные; не подключать реальные ПДн.
- Не коммитить `.env` и ключи.
