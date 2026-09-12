# Музей Невозможных Предметов

Web-приложение на стеку **Sanic + NueJS + PostgreSQL**.

Архив-музей предметов, нарушающих законы физики, времени и логики
(шар, падающий вверх; часы, идущие вчера; кольцо, которое никогда не существовало, — и т. д.).

## Требования

- Python 3.10+
- PostgreSQL (локально или в Docker)
- [Bun](https://bun.sh/) 1.2+ (для фронтенда на Nue 2.0 / Nuekit)

## База данных

Создайте базу один раз:

```sql
CREATE DATABASE museum ENCODING 'UTF8';
```

Учётные данные — в `backend/.env` (см. `backend/.env.example`):

```
DATABASE_URL=postgres://postgres:PASSWORD@localhost:5432/museum
DEBUG=1
PORT=8000
AUTO_RELOAD=0
```

Таблицы и демоданные создаются автоматически при старте бекенда (`db.py`).

## Бэкенд (Sanic + Tortoise ORM)

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd backend
..\.venv\Scripts\python app.py        # слушает http://127.0.0.1:8000
```

Все запросы к API — асинхронные (`async`/`await`, `asyncpg`).

## Фронтенд (Nue 2.0 / Nuekit)

Зависимости ставит сам `nuekit`:

```bash
bun install --global nuekit          # один раз
cd frontend
nue dev                              # http://localhost:4000, /api проксируется на бекенд
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
| GET | `/api/items` | Список предметов (фильтры: `q`, `status`, `violation_type`, `material`) |
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