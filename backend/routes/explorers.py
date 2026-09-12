from sanic import Blueprint, empty, json

from models import Explorer, ImpossibleObject
from serializers import explorer_to_dict

explorers_bp = Blueprint("explorers", url_prefix="/api/explorers")


def _validate_explorer_payload(body) -> tuple[dict, str | None]:
    name = body.get("name")
    specialization = body.get("specialization")
    if not name or not str(name).strip():
        return {}, "Поле 'name' обязательно"
    if not specialization or not str(specialization).strip():
        return {}, "Поле 'specialization' обязательно"
    birth_year = body.get("birth_year")
    if birth_year is not None:
        try:
            birth_year = int(birth_year)
        except (TypeError, ValueError):
            return {}, "Поле 'birth_year' должно быть числом"
    return {"name": str(name).strip(), "specialization": str(specialization).strip(), "birth_year": birth_year}, None


@explorers_bp.get("/")
async def list_explorers(request):
    explorers = await Explorer.all().prefetch_related("objects")
    return json(
        {
            "explorers": [
                {**explorer_to_dict(e), "objects_count": len(await e.objects.all())}
                for e in explorers
            ]
        }
    )


@explorers_bp.get("/<explorer_id:int>")
async def get_explorer(request, explorer_id: int):
    explorer = await Explorer.get_or_none(id=explorer_id)
    if not explorer:
        return json({"error": "Исследователь не найден"}, status=404)
    objs = await explorer.objects.all()
    return json({**explorer_to_dict(explorer), "objects": [o.id for o in objs]})


@explorers_bp.post("/")
async def create_explorer(request):
    body = request.json or {}
    data, error = _validate_explorer_payload(body)
    if error:
        return json({"error": error}, status=400)
    explorer = await Explorer.create(
        **data,
        nationality=body.get("nationality"),
        biography=body.get("biography"),
    )
    return json(explorer_to_dict(explorer), status=201)


@explorers_bp.put("/<explorer_id:int>")
async def update_explorer(request, explorer_id: int):
    explorer = await Explorer.get_or_none(id=explorer_id)
    if not explorer:
        return json({"error": "Исследователь не найден"}, status=404)
    body = request.json or {}
    data, error = _validate_explorer_payload(body)
    if error:
        return json({"error": error}, status=400)
    for field, value in data.items():
        setattr(explorer, field, value)
    for field in ("nationality", "biography"):
        if field in body:
            setattr(explorer, field, body[field])
    await explorer.save()
    return json(explorer_to_dict(explorer))


@explorers_bp.delete("/<explorer_id:int>")
async def delete_explorer(request, explorer_id: int):
    explorer = await Explorer.get_or_none(id=explorer_id)
    if not explorer:
        return json({"error": "Исследователь не найден"}, status=404)
    count = await explorer.objects.all().count()
    if count:
        return json({"error": "Нельзя удалить исследователя, нашедшего предметы"}, status=400)
    await explorer.delete()
    return empty(status=204)