from sanic import Blueprint, json
from tortoise.connection import connections
from tortoise.functions import Count

from models import Exhibition, Explorer, ImpossibleObject

stats_bp = Blueprint("stats", url_prefix="/api")


async def _group_by(model, field: str) -> dict:
    rows = await model.annotate(count=Count("id")).group_by(field).values(field, "count")
    return {row[field]: row["count"] for row in rows}


@stats_bp.get("/stats")
async def stats(request):
    by_violation_type = await _group_by(ImpossibleObject, "violation_type")
    return json(
        {
            "total_objects": await ImpossibleObject.all().count(),
            "total_explorers": await Explorer.all().count(),
            "total_exhibitions": await Exhibition.all().count(),
            "by_status": await _group_by(ImpossibleObject, "status"),
            "by_violation_type": by_violation_type,
            "by_science_field": by_violation_type,
            "by_material": await _group_by(ImpossibleObject, "material"),
            "by_epoch": await _group_by(ImpossibleObject, "epoch"),
            "by_origin": await _group_by(ImpossibleObject, "origin"),
        }
    )


@stats_bp.get("/health")
async def health(request):
    try:
        await connections.get("default").execute_query("SELECT 1")
    except Exception:
        return json({"status": "error", "db": "unreachable"}, status=503)
    return json({"status": "ok", "db": "ok"})