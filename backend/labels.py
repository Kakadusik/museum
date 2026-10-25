"""Единый справочник отображаемых подписей.

Ключи (on_exhibition, in_storage) используются в БД, API и CSS-классах,
менять их нельзя. Меняются только значения label.
"""

STATUS_LABELS = {
    "on_exhibition": "На выставке",
    "in_storage": "В хранилище",
}

STATUSES = [{"value": value, "label": label} for value, label in STATUS_LABELS.items()]

SCIENCE_FIELDS = [
    {"value": "astronomy", "label": "астрономия"},
    {"value": "materials", "label": "материаловедение"},
    {"value": "metallurgy", "label": "металлургия"},
    {"value": "engineering", "label": "инженерия"},
    {"value": "geology", "label": "геология"},
]


def status_label(value: str) -> str:
    return STATUS_LABELS.get(value, value)
