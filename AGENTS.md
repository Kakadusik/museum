# Музей невероятных предметов

Web-приложение на стеку **Sanic + NueJS + PostgreSQL**.

Можно ещё добавить какую-нибудь легкую ORM для работы с БД в коде.

Предметная область: музей реальных артефактов, которые кажутся невозможными,
но объясняются наукой (Антикитерский механизм, Кубок Ликурга, кинжал
Тутанхамона, римский бетон, дамасская сабля, Небрский небесный диск,
каменные шары Дикис). У каждого предмета есть научное объяснение и ссылка
на научную публикацию.

## Функционал

Все запросы к бекенду выполняются **асинхронно**.

## ER-модель (4 таблицы)

```
explorers ───────┐  1:N    impossible_objects ───── N:M ───── exhibitions
                                              │
                                    object_exhibitions (связь N:M)
```

- `explorers` — исследователи, изучавшие предметы (id, name, specialization, birth_year, nationality, biography)
- `impossible_objects` — предметы (id, name, description, violation_type, material, epoch, origin, scientific_explanation, source_title, source_url, status)
- `exhibitions` — выставки (id, title, description, location)
- `object_exhibitions` — связка предмет ↔ выставка (object_id FK, exhibition_id FK)

Таблицы и демоданные создаются автоматически при старте бекенда (`db.py`).
`violation_type` хранит код области науки (`astronomy`, `materials`, `metallurgy`,
`engineering`, `geology`), а отображаемая подпись — «Область науки».

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/items` | Список предметов (фильтры: `q`, `status`, `violation_type` — область науки, `material`, `epoch`) |
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
| GET | `/api/exhibitions/:id` | Детали выставку |
| POST | `/api/exhibitions` | Добавить выставку |
| PUT | `/api/exhibitions/:id` | Обновить выставку |
| DELETE | `/api/exhibitions/:id` | Удалить выставку |
| GET | `/api/stats` | Сводка по фондам |
| GET | `/api/meta` | Справочник областей науки, статусов, материалов и эпох |
| GET | `/api/health` | Healthcheck |

## Процесс работы

Каждый этап проекта согласовывай со мной, работаем итерационно по этапам