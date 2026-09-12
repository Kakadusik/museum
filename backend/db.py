from tortoise import Tortoise

from config import DATABASE_URL
from models import Exhibition, Explorer, ImpossibleObject, ObjectExhibition


async def init_db() -> None:
    """Создание таблиц и тестовых данных при старте бекенда."""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["models"]},
    )
    await Tortoise.generate_schemas()
    await seed()


async def seed() -> None:
    if await Explorer.all().count() > 0:
        return

    aristarch = await Explorer.create(
        name="Аристарх Осколков",
        specialization="Парадоксология",
        birth_year=1972,
        nationality="русский",
        biography=(
            "Бывший смотритель обсерватории. Первым задокументировал шар, "
            "падающий вверх, наблюдая его в течение трёх лунных затмений."
        ),
    )
    emerald = await Explorer.create(
        name="Эмеральд Хиггс",
        specialization="Хронофизика",
        birth_year=1965,
        nationality="британка",
        biography=(
            "Знаток временных аномалий. Коллекционирует настольные хронометры, "
            "которые отсчитывают время, которого ещё не наступило."
        ),
    )
    yuki = await Explorer.create(
        name="Юки Цубаки",
        specialization="Логическая топология",
        birth_year=1988,
        nationality="японка",
        biography=(
            "Исследует предметы, противоречащие самим себе. Утверждает, что "
            "кольцо, которое никогда не существовало, пришлось ей по размеру."
        ),
    )

    ball = await ImpossibleObject.create(
        name="Шар, падающий вверх",
        description=(
            "Латунный шар, который вопреки гравитации поднимается вверх "
            "с ускорением ровно 9.8 м/с². Требует держать его под крышкой."
        ),
        violation_type="gravity",
        material="латунь",
        epoch="неопределённая",
        origin="чердак обсерватории Архунья",
        status="on_exhibition",
        explorer=aristarch,
    )
    clock = await ImpossibleObject.create(
        name="Часы, идущие вчера",
        description=(
            "Серебряные карманные часы, стрелки которых всегда показывают "
            "время суток на сутки раньше текущего. Владелец их дважды отматывал назад."
        ),
        violation_type="time",
        material="серебро",
        epoch="викторианская",
        origin="разграбленная антикварная лавка в Лондоне",
        status="on_exhibition",
        explorer=emerald,
    )
    ring = await ImpossibleObject.create(
        name="Кольцо, которое никогда не существовало",
        description=(
            "Обсидиановое кольцо, отсутствующее в реестрах всего музея. "
            "Фактически его нет, и тем не менее оно экспонируется."
        ),
        violation_type="logic",
        material="обсидиан",
        epoch="доисторическая",
        origin="оно само представило себя в витрине",
        status="on_exhibition",
        explorer=yuki,
    )
    mirror = await ImpossibleObject.create(
        name="Зеркало, отражающее причину",
        description=(
            "Венецианское зеркало, в котором видно не отражение предмета, "
            "а причину его появления. Смотреться в него смотрителям запрещено."
        ),
        violation_type="logic",
        material="стекло, ртуть",
        epoch="ренессанс",
        origin="венецианская мастерская Мурано",
        status="in_storage",
        explorer=emerald,
    )
    compass = await ImpossibleObject.create(
        name="Компас, указывающий на вчера",
        description=(
            "Магнитный компас, стрелка которого всегда направлена на точку, "
            "где он находился сутки назад, а не на север."
        ),
        violation_type="time",
        material="магнетит, медь",
        epoch="эпоха великих географических открытий",
        origin="трюм испанского галеона",
        status="on_exhibition",
        explorer=aristarch,
    )
    cube = await ImpossibleObject.create(
        name="Куб, у которого больше граней, чем у куба",
        description=(
            "Гранитный многогранник с семью гранями, хотя при любом пересчёте "
            "их шесть. Отличить подделку пока не удалось."
        ),
        violation_type="geometry",
        material="гранит",
        epoch="мезозой",
        origin="раскопки в сибирской мерзлоте",
        status="in_storage",
        explorer=yuki,
    )
    fork = await ImpossibleObject.create(
        name="Камертон, заставляющий звучать тишину",
        description=(
            "Стальной камертон, при ударе о который комната наполняется "
            "абсолютной тишиной, слышной за километр."
        ),
        violation_type="sound",
        material="сталь",
        epoch="современная",
        origin="репетиционный зал филармонии",
        status="in_storage",
        explorer=aristarch,
    )

    g_evh = await Exhibition.create(
        title="Нарушенная гравитация",
        description="Экспозиция предметов, отменивших закон всемирного тяготения.",
        location="Зал «Анти-небо»",
    )
    time_evh = await Exhibition.create(
        title="Хронометры невозможного времени",
        description="Выставка часовых механизмов, живущих не в том времени.",
        location="Зал «Вчерашний день»",
    )
    logic_evh = await Exhibition.create(
        title="Логические парадоксы",
        description="Предметы, которые не могут существовать и всё же существуют.",
        location="Зал «Круглый квадрат»",
    )

    await ObjectExhibition.bulk_create([
        ObjectExhibition(planned_object=ball, exhibition=g_evh),
        ObjectExhibition(planned_object=clock, exhibition=time_evh),
        ObjectExhibition(planned_object=ring, exhibition=logic_evh),
        ObjectExhibition(planned_object=mirror, exhibition=logic_evh),
        ObjectExhibition(planned_object=compass, exhibition=time_evh),
        ObjectExhibition(planned_object=cube, exhibition=logic_evh),
        ObjectExhibition(planned_object=fork, exhibition=g_evh),
    ])