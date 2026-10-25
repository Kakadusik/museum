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
| `violation_type` | varchar(80) | обязательное, индекс — код области науки |
| `material` | varchar(120) | nullable |
| `epoch` | varchar(120) | nullable |
| `origin` | varchar(240) | nullable |
| `scientific_explanation` | text | nullable — научное объяснение |
| `source_title` | varchar(200) | nullable — название публикации |
| `source_url` | varchar(400) | nullable — DOI или ссылка на источник |
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

При первом запуске (пустая БД) создаются:

- **7 исследователей:** Тони Фрит, Иан Фристоун, Даниэла Комелли, Адмир Масич,
  Петер Райбольд, Харальд Меллер, Дорис Стоун
- **7 предметов:** Антикитерский механизм, Кубок Ликурга, кинжал Тутанхамона,
  римский бетон, дамасская сабля, Небрский небесный диск, каменные шары Дикис
- **3 выставки:** «Небо древних», «Секреты материала», «Камень и время»
- **7 связей** предмет ↔ выставка
- у каждого предмета заполнены `scientific_explanation`, `source_title`, `source_url`

Сид идемпотентен. База со старыми демо-данными (шар, часы, кольцо и т. д.)
автоматически перезаполняется новыми; база с пользовательскими записями
не изменяется. Новые колонки добавляются через `ALTER TABLE ... ADD COLUMN
IF NOT EXISTS` при старте бекенда.
