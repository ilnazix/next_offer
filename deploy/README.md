# Деплой демо: GitHub Pages + VPS

```
GitHub Pages (React, статика)          VPS (Docker Compose)
https://<owner>.github.io/next_offer/  ──►  Caddy (TLS) ──► app ──► Postgres
                                                              └──► RabbitMQ
                                                              └──► worker ──► YandexGPT
```

GitHub Pages хостит только фронтенд. Бэкенд (FastAPI, worker, Postgres, RabbitMQ)
живёт на VPS и доступен по HTTPS через Caddy.

## 1. GitHub Pages

1. Сделай репозиторий публичным (Settings → General → Danger Zone → Change visibility).
2. Settings → Pages → **Source: GitHub Actions**.
3. Задай переменные репозитория (Settings → Secrets and variables → Actions → Variables):
   - `VITE_API_BASE_URL` = `https://<API_DOMAIN>`
   - `VITE_CLIENT_ID` = `1` (опционально)
4. Пуш в `master` запускает `.github/workflows/pages.yml`.
5. Сайт: `https://<owner>.github.io/next_offer/`.

Воркфлоу собирает фронт с `VITE_BASE_PATH=/next_offer/`, иначе ассеты не найдутся
на project page.

## 2. VPS (бэкенд)

Требования: Ubuntu 22.04+, Docker Engine + Compose plugin, открытые порты 80/443.

```bash
sudo mkdir -p /opt/next_offer && sudo chown "$USER" /opt/next_offer
git clone https://github.com/ilnazix/next_offer.git /opt/next_offer
cd /opt/next_offer

cp deploy/.env.production.example .env
# отредактируй .env: пароли, API_DOMAIN, CORS_ORIGINS, YANDEX_*
chmod 600 .env

docker compose -f docker-compose.prod.yml up -d --build
```

DNS:

- если есть домен — A-запись `api` → IP сервера;
- если нет — используй `sslip.io`: `API_DOMAIN=next-offer-api.<IP>.sslip.io`
  (Caddy выпустит TLS-сертификат автоматически).

Проверка:

```bash
curl "https://$API_DOMAIN/health"
```

Ожидаемо: `{"status":"ok","checks":{"database":"ok","rabbitmq":"ok"}}`.

Демо-данные (клиенты, продукты, 4 шаблона) заливаются из `migrations/init.sql`
при создании пустого тома Postgres.

## 3. GitHub Actions для бэкенда

`.github/workflows/backend.yml`:

1. На PR и push гоняет `pytest`.
2. На push в `master` заходит по SSH на VPS, делает `git reset --hard origin/master`
   и `docker compose -f docker-compose.prod.yml up -d --build`.
3. Если задана переменная `API_BASE_URL`, прогоняет `scripts/e2e_demo.py`.

Нужные секреты репозитория (Settings → Secrets and variables → Actions → Secrets):

| Секрет | Значение |
| --- | --- |
| `DEPLOY_HOST` | IP или DNS сервера |
| `DEPLOY_USER` | SSH-пользователь |
| `DEPLOY_SSH_KEY` | приватный SSH-ключ |
| `DEPLOY_PORT` | SSH-порт (по умолчанию 22) |
| `DEPLOY_PATH` | `/opt/next_offer` |

Переменная: `API_BASE_URL` = `https://<API_DOMAIN>`.

Рекомендуется создать Environment `production` с ручным подтверждением деплоя.

## 4. Как это связано

- Фронтенд ходит на абсолютный `VITE_API_BASE_URL` (Pages не умеет проксировать `/api`).
- `CORS_ORIGINS` на сервере должен содержать `https://<owner>.github.io`.
- Наружу открыты только 80/443 (Caddy). Postgres, RabbitMQ и app доступны
  только внутри compose-сети.
- Секреты лежат только в `/opt/next_offer/.env` (`chmod 600`), в git не попадают.

## 5. Обновление и откат

Деплой — пуш в `master`.

Откат:

```bash
cd /opt/next_offer
git reset --hard <previous-sha>
docker compose -f docker-compose.prod.yml up -d --build
```

Миграции аддитивные, поэтому откат кода не ломает схему.

## 6. Публичное демо: риски

- API без авторизации: любой может слать события и расходовать квоту YandexGPT.
  Минимально: бюджетный алерт в Yandex Cloud, `YANDEX_MAX_TOKENS`, лимиты Yandex.
  Дальше: rate limit на прокси/Cloudflare или demo-token на `POST /events`.
- Только синтетические данные; не подключать реальные ПДн.
- Management UI RabbitMQ наружу не публикуется.
- Не коммитить `.env` и ключи.

## 7. Локальная проверка prod-compose

Prod-compose рассчитан на сервер с доменом. Для локального запуска используй
обычный `docker compose up --build` и фронтенд отдельно (`npm run dev`).
