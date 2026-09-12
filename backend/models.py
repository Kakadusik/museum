from tortoise import fields
from tortoise.models import Model


class Explorer(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=160)
    specialization = fields.CharField(max_length=160)
    birth_year = fields.IntField(null=True)
    nationality = fields.CharField(max_length=120, null=True)
    biography = fields.TextField(null=True)

    class Meta:
        table = "explorers"


class ImpossibleObject(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    violation_type = fields.CharField(max_length=80, index=True)
    material = fields.CharField(max_length=120, null=True)
    epoch = fields.CharField(max_length=120, null=True)
    origin = fields.CharField(max_length=240, null=True)
    status = fields.CharField(max_length=40, index=True, default="in_storage")
    created_at = fields.DatetimeField(auto_now_add=True)
    explorer = fields.ForeignKeyField(
        "models.Explorer", related_name="objects", null=True, on_delete=fields.SET_NULL
    )

    class Meta:
        table = "impossible_objects"


class Exhibition(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    location = fields.CharField(max_length=200, null=True)

    class Meta:
        table = "exhibitions"


class ObjectExhibition(Model):
    id = fields.IntField(pk=True)
    planned_object = fields.ForeignKeyField(
        "models.ImpossibleObject", related_name="exhibition_links", on_delete=fields.CASCADE
    )
    exhibition = fields.ForeignKeyField(
        "models.Exhibition", related_name="object_links", on_delete=fields.CASCADE
    )

    class Meta:
        table = "object_exhibitions"