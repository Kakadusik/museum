from sanic import Blueprint, empty, json
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q

from models import Exhibition, Explorer, ImpossibleObject, ObjectExhibition
from serializers import object_to_dict

items_bp = Blueprint("items", url_prefix="/api/items")


@items_bp.get("/")
async def list_items(request):
    filters = []

    q = request.args.get("q")
    status = request.args.get("status")
    violation_type = request.args.get("violation_type")
    material = request.args.get("material")
    epoch = request.args.get("epoch")

    if q:
        filters.append(Q(name__icontains=q) | Q(description__icontains=q))
    if status:
        filters.append(Q(status=status))
    if violation_type:
        filters.append(Q(violation_type=violation_type))
    if material:
        filters.append(Q(material__icontains=material))
    if epoch:
        filters.append(Q(epoch=epoch))

    query = ImpossibleObject.all()
    if filters:
        query = query.filter(*filters)

    objs = await query.prefetch_related("explorer", "exhibition_links__exhibition")
    return json({"items": [await object_to_dict(o) for o in objs]})


@items_bp.get("/<item_id:int>")
async def get_item(request, item_id: int):
    obj = await ImpossibleObject.get_or_none(id=item_id).prefetch_related(
        "explorer", "exhibition_links__exhibition"
    )
    if not obj:
        return json({"error": "Предмет не найден"}, status=404)
    return json(await object_to_dict(obj))


def _validate_item_payload(body) -> tuple[dict, str | None]:
    name = body.get("name")
    violation_type = body.get("violation_type")
    if not name or not str(name).strip():
        return {}, "Поле 'name' обязательно"
    if not violation_type or not str(violation_type).strip():
        return {}, "Поле 'violation_type' обязательно"
    return {"name": str(name).strip(), "violation_type": str(violation_type).strip()}, None


async def _resolve_explorer(body) -> tuple:
    explorer_id = body.get("explorer_id")
    if explorer_id is None:
        return None, None
    explorer = await Explorer.get_or_none(id=explorer_id)
    if not explorer:
        return None, "Исследователь не найден"
    return explorer, None


async def _replace_exhibitions(obj, exhibition_ids) -> str | None:
    if exhibition_ids is None:
        return None
    count = await Exhibition.filter(id__in=exhibition_ids).count()
    if count != len(set(exhibition_ids)):
        return "Одна из выставок не найдена"
    await obj.exhibition_links.all().delete()
    await ObjectExhibition.bulk_create(
        [ObjectExhibition(planned_object=obj, exhibition_id=ex_id) for ex_id in exhibition_ids]
    )
    return None


@items_bp.post("/")
async def create_item(request):
    body = request.json or {}
    data, error = _validate_item_payload(body)
    if error:
        return json({"error": error}, status=400)

    explorer, error = await _resolve_explorer(body)
    if error:
        return json({"error": error}, status=400)

    obj = await ImpossibleObject.create(
        **data,
        description=body.get("description"),
        material=body.get("material"),
        epoch=body.get("epoch"),
        origin=body.get("origin"),
        scientific_explanation=body.get("scientific_explanation"),
        source_title=body.get("source_title"),
        source_url=body.get("source_url"),
        status=body.get("status") or "in_storage",
        explorer=explorer,
    )

    error = await _replace_exhibitions(obj, body.get("exhibition_ids") or [])
    if error:
        return json({"error": error}, status=400)

    fresh = await ImpossibleObject.get(id=obj.id).prefetch_related(
        "explorer", "exhibition_links__exhibition"
    )
    return json(await object_to_dict(fresh), status=201)


@items_bp.put("/<item_id:int>")
async def update_item(request, item_id: int):
    obj = await ImpossibleObject.get_or_none(id=item_id)
    if not obj:
        return json({"error": "Предмет не найден"}, status=404)

    body = request.json or {}
    data, error = _validate_item_payload(body)
    if error:
        return json({"error": error}, status=400)

    explorer, error = await _resolve_explorer(body)
    if error:
        return json({"error": error}, status=400)

    for field, value in data.items():
        setattr(obj, field, value)
    for field in (
        "description",
        "material",
        "epoch",
        "origin",
        "scientific_explanation",
        "source_title",
        "source_url",
        "status",
    ):
        if field in body:
            setattr(obj, field, body[field])
    if "explorer_id" in body:
        obj.explorer = explorer
    await obj.save()

    error = await _replace_exhibitions(obj, body.get("exhibition_ids"))
    if error:
        return json({"error": error}, status=400)

    fresh = await ImpossibleObject.get(id=obj.id).prefetch_related(
        "explorer", "exhibition_links__exhibition"
    )
    return json(await object_to_dict(fresh))


@items_bp.delete("/<item_id:int>")
async def delete_item(request, item_id: int):
    obj = await ImpossibleObject.get_or_none(id=item_id)
    if not obj:
        return json({"error": "Предмет не найден"}, status=404)
    try:
        await obj.delete()
    except IntegrityError:
        return json({"error": "Нельзя удалить предмет со связанными выставками"}, status=400)
    return empty(status=204)