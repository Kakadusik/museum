from sanic import Blueprint, json

from labels import SCIENCE_FIELDS, STATUSES
from models import ImpossibleObject

meta_bp = Blueprint("meta", url_prefix="/api")


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
            "violation_types": SCIENCE_FIELDS,
            "science_fields": SCIENCE_FIELDS,
            "statuses": STATUSES,
            "materials": await _distinct_values("material"),
            "epochs": await _distinct_values("epoch"),
        }
    )
