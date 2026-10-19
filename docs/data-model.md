# Модель данных

Четыре таблицы PostgreSQL. Создаются автоматически при старте бекенда (`db.py`).

## ER-схема

```
explorers ───────1:N──────── impossible_objects ───────N:M─────── exhibitions
                                              │
                                    object_exhibitions (связь N:M)
```

## Таблицы

### `explorers` — исследователи

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | integer | PK |
| `name` | varchar(160) | обязательное |
| `specialization` | varchar(160) | обязательное |
| `birth_year` | integer | nullable |
| `nationality` | varchar(120) | nullable |
| `biography` | text | nullable |

### `impossible_objects` — предметы

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | integer | PK |
| `name` | varchar(200) | обязательное |
| `description` | text | nullable |
| `violation_type` | varchar(80) | обязательное, индекс |
| `material` | varchar(120) | nullable |
| `epoch` | varchar(120) | nullable |
| `origin` | varchar(240) | nullable |
| `status` | varchar(40) | индекс, по умолчанию `in_storage` |
| `created_at` | timestamp | автоматически при создании |
| `explorer_id` | integer | FK → `explorers.id`, nullable, `ON DELETE SET NULL` |

### `exhibitions` — выставки

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | integer | PK |
| `title` | varchar(200) | обязательное |
| `description` | text | nullable |
| `location` | varchar(200) | nullable |

### `object_exhibitions` — связь N:M

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | integer | PK |
| `planned_object_id` | integer | FK → `impossible_objects.id`, `ON DELETE CASCADE` |
| `exhibition_id` | integer | FK → `exhibitions.id`, `ON DELETE CASCADE` |

## Связи и ограничения

- **Предмет → исследователь** (N:1): у предмета может быть один исследователь. При удалении исследователя предметы сохраняются, `explorer_id` становится `NULL`.
- **Предмет ↔ выставка** (N:M): через `object_exhibitions`. При удалении предмета или выставки связи удаляются каскадно.
- **Защита от удаления:**
  - исследователя, у которого есть предметы, удалить нельзя (400);
  - предмета, связанного с выставками, удалить нельзя (400) — сначала снимите связи через `PUT`.

## Демоданные

При первом запуске (пустой БД) создаются:

- **3 исследователя:** Аристарх Осколков (парадоксология), Эмеральд Хиггс (хронофизика), Юки Цубаки (логическая топология)
- **7 предметов:** шар, падающий вверх; часы, идущие вчера; кольцо, которое никогда не существовало; зеркало, отражающее причину; компас, указывающий на вчера; куб с семью гранями; камертон, заставляющий звучать тишину
- **3 выставки:** «Нарушенная гравитация», «Хронометры невозможного времени», «Логические парадоксы»
- **7 связей** предмет ↔ выставка

Сид выполняется один раз — только если таблица `explorers` пуста.
