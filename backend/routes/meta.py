from sanic import Blueprint, json

from models import ImpossibleObject

meta_bp = Blueprint("meta", url_prefix="/api")

VIOLATION_TYPES = [
    {"value": "gravity", "label": "гравитация"},
    {"value": "time", "label": "время"},
    {"value": "logic", "label": "логика"},
    {"value": "geometry", "label": "геометрия"},
    {"value": "sound", "label": "звук"},
]


async def _distinct_values(field: str) -> list[str]:
    rows = (
        await ImpossibleObject.all()
        .exclude(**{f"{field}__isnull": True})
        .exclude(**{f"{field}": ""})
        .distinct()
        .values_list(field, flat=True)
    )
    return sorted({value for value in rows if value})


@meta_bp.get("/meta")
async def meta(request):
    return json(
        {
            "violation_types": VIOLATION_TYPES,
            "materials": await _distinct_values("material"),
            "epochs": await _distinct_values("epoch"),
        }
    )
