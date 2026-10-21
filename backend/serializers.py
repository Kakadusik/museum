async def object_to_dict(obj) -> dict:
    explorer_ref = obj.explorer
    explorer = await explorer_ref if explorer_ref is not None else None
    links = await obj.exhibition_links.all().prefetch_related("exhibition")
    exhibitions = [
        {"id": link.exhibition.id, "title": link.exhibition.title, "location": link.exhibition.location}
        for link in links
    ]
    return {
        "id": obj.id,
        "name": obj.name,
        "description": obj.description,
        "violation_type": obj.violation_type,
        "material": obj.material,
        "epoch": obj.epoch,
        "origin": obj.origin,
        "status": obj.status,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "explorer": (
            {"id": explorer.id, "name": explorer.name, "specialization": explorer.specialization}
            if explorer
            else None
        ),
        "exhibition_ids": [e["id"] for e in exhibitions],
        "exhibitions": exhibitions,
    }


def explorer_to_dict(explorer) -> dict:
    return {
        "id": explorer.id,
        "name": explorer.name,
        "specialization": explorer.specialization,
        "birth_year": explorer.birth_year,
        "nationality": explorer.nationality,
        "biography": explorer.biography,
    }


def exhibition_to_dict(exhibition) -> dict:
    return {
        "id": exhibition.id,
        "title": exhibition.title,
        "description": exhibition.description,
        "location": exhibition.location,
    }