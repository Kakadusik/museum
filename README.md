# Музей Невозможных Предметов

Web-приложение на стеку **Sanic + NueJS + PostgreSQL**.

Архив-музей предметов, нарушающих законы физики, времени и логики
(шар, падающий вверх; часы, идущие вчера; кольцо, которое никогда не существовало, — и т. д.).

## Требования

- Python 3.10+
- PostgreSQL (локально или в Docker)
- [Bun](https://bun.sh/) 1.2+ (для фронтенда на Nue 2.0 / Nuekit)
- Docker Engine/Desktop + Compose v2 — для запуска в контейнерах

## Docker (dev и prod)

Для этого варианта Python, Bun и PostgreSQL на хосте не нужны. Все команды — из корня репозитория.

Скопируйте `.env.example` в `.env` и задайте пароль (URL-safe: без `@ : / ? # %`):

```bash
cp .env.example .env
```

```dotenv
DOCKERHUB_USER=kakadusik
POSTGRES_PASSWORD=change-me
```

### Разработка (HMR + авто-reload)

```bash
docker compose up --build
```

| Сервис | Адрес | Что внутри |
|---|---|---|
| UI | http://localhost:4000 | Nue dev-сервер, HMR (`/@nue/hmr.js`) |
| API | http://localhost:8010 | Sanic, авто-reload при изменении `backend/` |
| PostgreSQL | localhost:5433 | `postgres:16-alpine`, том `museum-dev_pgdata_dev` |

`frontend/` и `backend/` смонтированы в контейнеры, правки подхватываются без пересборки.
UI проксирует `/api/` на `backend:8000` (см. `docker/site.dev.yaml`).

Остановить / удалить вместе с данными:

```bash
docker compose down
docker compose down -v
```

Если локальный бэкенд уже занимает порт `8010`, остановите его перед `up`.

### Production

Образ: [`kakadusik/museum`](https://hub.docker.com/r/kakadusik/museum) (multi-stage: Bun собирает `.dist`, Sanic раздаёт статику и API на одном порту).

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Приложение: http://localhost:8000 (`APP_PORT` в `.env`). PostgreSQL наружу не публикуется; данные — в томе `museum_pgdata`.
Пароль БД фиксируется при создании тома: чтобы его сменить, удалите том (`docker compose -f docker-compose.prod.yml down -v` — вместе с данными).

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f app
```

### Сборка и публикация образа

```bash
docker login
docker build -t kakadusik/museum:latest .
docker tag kakadusik/museum:latest kakadusik/museum:1.0.0
docker push kakadusik/museum:latest
docker push kakadusik/museum:1.0.0
```

### e2e

```bash
.venv\Scripts\python e2e_test.py 4000   # dev: UI-оригин, API через прокси
.venv\Scripts\python e2e_test.py 8000   # prod
```

Ожидается 7 предметов / 3 исследователя / 3 выставки и `RESULT: ALL PASS`.

## Локальный запуск (без Docker)

### База данных

Создайте базу один раз:

```sql
CREATE DATABASE museum ENCODING 'UTF8';
```

Учётные данные — в `backend/.env` (см. `backend/.env.example`):

```
DATABASE_URL=postgres://postgres:PASSWORD@localhost:5432/museum
DEBUG=1
PORT=8010
AUTO_RELOAD=0
```

Таблицы и демоданные создаются автоматически при старте бекенда (`db.py`).

### Бэкенд (Sanic + Tortoise ORM)

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd backend
..\.venv\Scripts\python app.py        # порт PORT из backend/.env (в примере 8010)
```

Все запросы к API — асинхронные (`async`/`await`, `asyncpg`).

### Фронтенд (Nue 2.0 / Nuekit)

Зависимости ставит сам `nuekit`:

```bash
bun install --global nuekit          # один раз
cd frontend
nue dev                              # http://localhost:4000, /api проксируется на 8010
```

Прокси-настройка — в `frontend/site.yaml` (`server.url` → адрес бекенда).

Сборка для продакшена:

```bash
cd frontend
nue build                            # статика в frontend/.dist
```

**Продакшен-режим:** запускаем только бекенд — Sanic раздаёт `frontend/.dist`
(одно приложение на одном порту, без CORS), с SPA-fallback для клиентских маршрутов
(`/items`, `/items/1`, ...).

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/items` | Список предметов (фильтры: `q`, `status`, `violation_type`, `material`, `epoch`) |
| GET | `/api/items/:id` | Детали предмета |
| POST | `/api/items` | Добавить предмет |
| PUT | `/api/items/:id` | Обновить предмет |
| DELETE | `/api/items/:id` | Удалить предмет |
| GET | `/api/explorers` | Исследователи |
| GET | `/api/explorers/:id` | Детали исследователя |
| POST | `/api/explorers` | Добавить исследователя |
| PUT | `/api/explorers/:id` | Обновить исследователя |
| DELETE | `/api/explorers/:id` | Удалить исследователя |
| GET | `/api/exhibitions` | Выставки |
| GET | `/api/exhibitions/:id` | Детали выставки |
| POST | `/api/exhibitions` | Добавить выставку |
| PUT | `/api/exhibitions/:id` | Обновить выставку |
| DELETE | `/api/exhibitions/:id` | Удалить выставку |
| GET | `/api/stats` | Сводка по фондам (только чтение) |
| GET | `/api/meta` | Справочник типов нарушений, материалов и эпох |
| POST | `/api/sql` | Read-only SQL-консоль (SELECT, WITH, EXPLAIN, SHOW) |
| GET | `/api/health` | Healthcheck (SELECT 1; 503 при недоступной БД) |

## ER-модель

```
explorers ───────1:N──────── impossible_objects ───────N:M─────── exhibitions
                                        │
                              object_exhibitions (связка N:M)
```

- `explorers` — id, name, specialization, birth_year, nationality, biography
- `impossible_objects` — id, name, description, violation_type, material, epoch, origin, status, explorer_id (FK), created_at
- `exhibitions` — id, title, description, location
- `object_exhibitions` — object_id (FK), exhibition_id (FK)

Связанные предметы/исследователя нельзя удалить, пока на них ссылаются записи.
Удаление выставки каскадно снимает связь с экспонатами, но сами предметы сохраняются.