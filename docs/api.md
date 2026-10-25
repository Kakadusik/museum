# API

Базовый префикс: `/api`. Все запросы асинхронные. Формат — JSON.

## Предметы

### `GET /api/items`

Список предметов с фильтрами (все параметры необязательны):

| Параметр | Описание |
|---|---|
| `q` | Поиск по названию или описанию (без учёта регистра) |
| `status` | Точное совпадение: `in_storage` / `on_exhibition` |
| `violation_type` | Область науки: `astronomy` / `materials` / `metallurgy` / `engineering` / `geology` |
| `material` | Поиск по материалу (без учёта регистра) |
| `epoch` | Точное совпадение с эпохой |

**Ответ `200`:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Антикитерский механизм",
      "description": "Бронзовый прибор II–I вв. до н.э. ...",
      "violation_type": "astronomy",
      "material": "бронза",
      "epoch": "II–I вв. до н.э.",
      "origin": "Эгейское море, у острова Антикитера",
      "scientific_explanation": "Механизм был моделью Солнечной системы ...",
      "source_title": "Decoding the ancient Greek astronomical calculator ...",
      "source_url": "https://doi.org/10.1038/nature05357",
      "status": "on_exhibition",
      "status_label": "На выставке",
      "created_at": "2026-09-12T17:13:00",
      "explorer": { "id": 1, "name": "Тони Фрит", "specialization": "История античной астрономии и механики" },
      "exhibition_ids": [1],
      "exhibitions": [
        { "id": 1, "title": "Небо древних", "location": "Зал астрономии" }
      ]
    }
  ]
}
```

### `GET /api/items/:id`

Детали предмета. Ответ `200` — объект предмета (как в списке). Ошибка `404`: `{"error": "Предмет не найден"}`.

### `POST /api/items`

Создание предмета.

**Обязательные поля:** `name`, `violation_type`.

**Опциональные поля:** `description`, `material`, `epoch`, `origin`, `scientific_explanation`, `source_title`, `source_url`, `status` (по умолчанию `in_storage`), `explorer_id`, `exhibition_ids` (массив ID выставок).

**Ответ `201`** — созданный предмет. Ошибки:
- `400` — не заполнены обязательные поля или не найдены исследователь/выставка.

### `PUT /api/items/:id`

Обновление предмета. Обязательные поля — как при создании. Поле `explorer_id` обновляется, только если передано в теле запроса (иначе исследователь сохраняется). `exhibition_ids` заменяет набор связей целиком.

**Ответ `200`** — обновлённый предмет. Ошибки: `400`, `404`.

### `DELETE /api/items/:id`

Удаление предмета. Ответ `204` (пустое тело). Ошибки:
- `400` — у предмета есть связанные выставки (сначала снимите связи);
- `404` — предмет не найден.

## Исследователи

### `GET /api/explorers`

Список исследователей. Ответ `200`:
```json
{
  "explorers": [
    { "id": 1, "name": "Тони Фрит", "specialization": "История античной астрономии и механики",
      "birth_year": null, "nationality": "британский", "biography": "...", "objects_count": 1 }
  ]
}
```

### `GET /api/explorers/:id`

Детали исследователя + список ID найденных предметов (`objects`). Ошибка `404`: `{"error": "Исследователь не найден"}`.

### `POST /api/explorers`

**Обязательные поля:** `name`, `specialization`. **Опциональные:** `birth_year` (число), `nationality`, `biography`.

**Ответ `201`** — созданный исследователь. Ошибки: `400` — валидация.

### `PUT /api/explorers/:id`

Обновление. Обязательные поля — как при создании. Ответ `200`. Ошибки: `400`, `404`.

### `DELETE /api/explorers/:id`

Удаление. Ответ `204`. Ошибки:
- `400` — у исследователя есть найденные предметы;
- `404` — не найден.

## Выставки

### `GET /api/exhibitions`

Список выставок с количеством экспонатов (`objects_count`). Ответ `200`:
```json
{
  "exhibitions": [
    { "id": 1, "title": "Небо древних", "description": "...",
      "location": "Зал астрономии", "objects_count": 2 }
  ]
}
```

### `GET /api/exhibitions/:id`

Детали выставки + список экспонатов (`objects`: `[{ "id", "name" }]`). Ошибка `404`: `{"error": "Выставка не найдена"}`.

### `POST /api/exhibitions`

**Обязательное поле:** `title`. **Опциональные:** `description`, `location`. Ответ `201`. Ошибки: `400`.

### `PUT /api/exhibitions/:id`

Обновление. Ответ `200`. Ошибки: `400`, `404`.

### `DELETE /api/exhibitions/:id`

Удаление выставки. Связи с экспонатами снимаются каскадно, сами предметы сохраняются. Ответ `204`. Ошибка `404`.

## Сводка и здоровье

### `GET /api/meta`

Единый справочник значений для форм и фильтров:

```json
{
  "violation_types": [
    { "value": "astronomy", "label": "астрономия" },
    { "value": "materials", "label": "материаловедение" }
  ],
  "science_fields": [
    { "value": "astronomy", "label": "астрономия" },
    { "value": "materials", "label": "материаловедение" }
  ],
  "statuses": [
    { "value": "on_exhibition", "label": "На выставке" },
    { "value": "in_storage", "label": "В хранилище" }
  ],
  "materials": ["бронза", "стекло с наночастицами золота и серебра", "..."],
  "epochs": ["II–I вв. до н.э.", "IV в. н.э.", "..."]
}
```

`violation_types` и `science_fields` — один и тот же фиксированный справочник
областей науки (поле называется `violation_type` для совместимости API).
`statuses` — единый источник подписей статусов; ключи `on_exhibition` и
`in_storage` не меняются. `materials` и `epochs` — различные непустые значения
из таблицы `impossible_objects`.

### `GET /api/stats`

```json
{
  "total_objects": 7,
  "total_explorers": 7,
  "total_exhibitions": 3,
  "by_status": { "on_exhibition": 4, "in_storage": 3 },
  "by_violation_type": { "astronomy": 2, "materials": 2, "metallurgy": 1, "engineering": 1, "geology": 1 },
  "by_science_field": { "astronomy": 2, "materials": 2, "metallurgy": 1, "engineering": 1, "geology": 1 },
  "by_material": { "бронза": 1, "дамасская сталь": 1, "...": 1 },
  "by_epoch": { "...": 1 },
  "by_origin": { "...": 1 }
}
```

### `GET /api/health`

Проверка доступности БД (`SELECT 1`). Ответ `200`: `{"status": "ok", "db": "ok"}`. При недоступной БД — `503`: `{"status": "error", "db": "unreachable"}`.

## SQL-консоль

### `POST /api/sql`

Выполняет **read-only** SQL-запрос к базе музея.

**Тело запроса:**
```json
{ "query": "SELECT name, status FROM impossible_objects LIMIT 10" }
```

**Ответ `200`:**
```json
{
  "columns": ["name", "status"],
  "rows": [
    { "name": "Антикитерский механизм", "status": "on_exhibition" }
  ],
  "count": 1
}
```

**Ограничения:**
- разрешены только запросы, начинающиеся с `SELECT`, `WITH`, `EXPLAIN`, `SHOW`
- запись, изменение и удаление (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, ...) запрещены
- максимум 1000 строк в ответе
- длина запроса — до 5000 символов

**Ошибки:** `400` — пустой запрос, превышение лимитов, запрещённый тип запроса или ошибка SQL.

## Коды ошибок

| Код | Ситуация |
|---|---|
| `400` | Ошибка валидации или нарушение ограничений (есть связанные записи) |
| `404` | Запись не найдена |
| `201` | Запись создана |
| `204` | Запись удалена (тело пустое) |
| `503` | База данных недоступна |
