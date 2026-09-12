from sanic import Blueprint, empty, json

from models import Exhibition, ObjectExhibition
from serializers import exhibition_to_dict

exhibitions_bp = Blueprint("exhibitions", url_prefix="/api/exhibitions")


def _validate_exhibition_payload(body) -> tuple[dict, str | None]:
    title = body.get("title")
    if not title or not str(title).strip():
        return {}, "Поле 'title' обязательно"
    return {"title": str(title).strip()}, None


async def _attach_counts(exhibition) -> dict:
    data = exhibition_to_dict(exhibition)
    data["objects_count"] = await ObjectExhibition.filter(exhibition_id=exhibition.id).count()
    return data


@exhibitions_bp.get("/")
async def list_exhibitions(request):
    exhibitions = await Exhibition.all()
    return json({"exhibitions": [await _attach_counts(e) for e in exhibitions]})


@exhibitions_bp.get("/<exhibition_id:int>")
async def get_exhibition(request, exhibition_id: int):
    exhibition = await Exhibition.get_or_none(id=exhibition_id)
    if not exhibition:
        return json({"error": "Выставка не найдена"}, status=404)
    links = await ObjectExhibition.filter(exhibition_id=exhibition_id).prefetch_related("planned_object")
    data = await _attach_counts(exhibition)
    data["objects"] = [
        {"id": link.planned_object.id, "name": link.planned_object.name}
        for link in links
    ]
    return json(data)


@exhibitions_bp.post("/")
async def create_exhibition(request):
    body = request.json or {}
    data, error = _validate_exhibition_payload(body)
    if error:
        return json({"error": error}, status=400)
    exhibition = await Exhibition.create(
        **data,
        description=body.get("description"),
        location=body.get("location"),
    )
    return json(exhibition_to_dict(exhibition), status=201)


@exhibitions_bp.put("/<exhibition_id:int>")
async def update_exhibition(request, exhibition_id: int):
    exhibition = await Exhibition.get_or_none(id=exhibition_id)
    if not exhibition:
        return json({"error": "Выставка не найдена"}, status=404)
    body = request.json or {}
    data, error = _validate_exhibition_payload(body)
    if error:
        return json({"error": error}, status=400)
    exhibition.title = data["title"]
    for field in ("description", "location"):
        if field in body:
            setattr(exhibition, field, body[field])
    await exhibition.save()
    return json(exhibition_to_dict(exhibition))


@exhibitions_bp.delete("/<exhibition_id:int>")
async def delete_exhibition(request, exhibition_id: int):
    exhibition = await Exhibition.get_or_none(id=exhibition_id)
    if not exhibition:
        return json({"error": "Выставка не найдена"}, status=404)
    await exhibition.delete()
    return empty(status=204)