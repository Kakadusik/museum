from tortoise import Tortoise
from tortoise.connection import connections

from config import DATABASE_URL
from models import Exhibition, Explorer, ImpossibleObject, ObjectExhibition

# Демоданные предыдущей версии музея. Нужны, чтобы отличить старую демо-базу
# от базы с пользовательскими записями: старые демо-данные можно безопасно
# заменить новыми, пользовательские — нельзя.
LEGACY_EXPLORER_NAMES = {
    "Аристарх Осколков",
    "Эмеральд Хиггс",
    "Юки Цубаки",
}
LEGACY_OBJECT_NAMES = {
    "Шар, падающий вверх",
    "Часы, идущие вчера",
    "Кольцо, которое никогда не существовало",
    "Зеркало, отражающее причину",
    "Компас, указывающий на вчера",
    "Куб, у которого больше граней, чем у куба",
    "Камертон, заставляющий звучать тишину",
}

# generate_schemas() создаёт только отсутствующие таблицы и не добавляет
# новые колонки в уже существующие, поэтому мигрируем их вручную.
COLUMN_MIGRATIONS = (
    "ALTER TABLE impossible_objects ADD COLUMN IF NOT EXISTS scientific_explanation TEXT",
    "ALTER TABLE impossible_objects ADD COLUMN IF NOT EXISTS source_title VARCHAR(200)",
    "ALTER TABLE impossible_objects ADD COLUMN IF NOT EXISTS source_url VARCHAR(400)",
)


async def init_db() -> None:
    """Создание таблиц, миграция колонок и тестовых данных при старте бекенда."""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["models"]},
    )
    await Tortoise.generate_schemas()
    await _ensure_columns()
    await seed()


async def _ensure_columns() -> None:
    conn = connections.get("default")
    for statement in COLUMN_MIGRATIONS:
        await conn.execute_script(statement)


async def seed() -> None:
    """Идемпотентный сид демонстрационных данных.

    - пустая база заполняется новыми демо-данными;
    - база со старыми демо-данными перезаполняется новыми;
    - база с пользовательскими записями не изменяется.
    """
    explorer_count = await Explorer.all().count()
    object_count = await ImpossibleObject.all().count()

    if explorer_count == 0 and object_count == 0:
        await _seed_demo()
        return

    if await _is_legacy_demo():
        await _clear_demo()
        await _seed_demo()


async def _is_legacy_demo() -> bool:
    explorer_names = set(await Explorer.all().values_list("name", flat=True))
    object_names = set(await ImpossibleObject.all().values_list("name", flat=True))
    if not explorer_names or not object_names:
        return False
    return (
        explorer_names <= LEGACY_EXPLORER_NAMES
        and object_names <= LEGACY_OBJECT_NAMES
    )


async def _clear_demo() -> None:
    await ObjectExhibition.all().delete()
    await ImpossibleObject.all().delete()
    await Exhibition.all().delete()
    await Explorer.all().delete()


async def _seed_demo() -> None:
    freeth = await Explorer.create(
        name="Тони Фрит",
        specialization="История античной астрономии и механики",
        birth_year=None,
        nationality="британский",
        biography=(
            "Математик и исследователь Антикитерского механизма, почётный "
            "старший научный сотрудник Университетского колледжа Лондона (UCL). "
            "Руководил расшифровкой надписей и зубчатых передач прибора."
        ),
    )
    freestone = await Explorer.create(
        name="Иан Фристоун",
        specialization="Археометрия и материаловедение",
        birth_year=None,
        nationality="британский",
        biography=(
            "Профессор археометрии Университетского колледжа Лондона, ранее "
            "сотрудник Британского музея. Исследует древнее стекло и "
            "нанотехнологии римских мастеров."
        ),
    )
    comelli = await Explorer.create(
        name="Даниэла Комелли",
        specialization="Физика и археометрия",
        birth_year=None,
        nationality="итальянка",
        biography=(
            "Профессор Политехнического университета Милана. Применила "
            "рентгенофлуоресцентный анализ для изучения металла кинжала "
            "Тутанхамона."
        ),
    )
    masic = await Explorer.create(
        name="Адмир Масич",
        specialization="Материаловедение и инженерия",
        birth_year=None,
        nationality="американский",
        biography=(
            "Профессор MIT, руководитель исследования древнего римского "
            "бетона и его способности к самовосстановлению."
        ),
    )
    reibold = await Explorer.create(
        name="Петер Райбольд",
        specialization="Физика твёрдого тела и металлография",
        birth_year=None,
        nationality="немецкий",
        biography=(
            "Исследователь Технического университета Дрездена. Обнаружил "
            "углеродные нанотрубки и цементитные нанопроволоки в стали "
            "дамасской сабли."
        ),
    )
    meller = await Explorer.create(
        name="Харальд Меллер",
        specialization="Археология и археометаллургия",
        birth_year=1960,
        nationality="немецкий",
        biography=(
            "Директор Государственного музея первобытной истории в Галле и "
            "государственный археолог земли Саксония-Анхальт. Исследует "
            "Небрский небесный диск."
        ),
    )
    stone = await Explorer.create(
        name="Дорис Стоун",
        specialization="Археология Центральной Америки",
        birth_year=1909,
        nationality="американка",
        biography=(
            "Археолог и этнограф, одна из первых научно описавших каменные "
            "шары Дикис в Коста-Рике."
        ),
    )

    antikythera = await ImpossibleObject.create(
        name="Антикитерский механизм",
        description=(
            "Бронзовый прибор II–I вв. до н.э., поднятый в 1901 году с "
            "затонувшего корабля у острова Антикитера. Содержит десятки "
            "зубчатых колёс и надписи, которые выглядят как инструкция к "
            "астрономическому компьютеру."
        ),
        violation_type="astronomy",
        material="бронза",
        epoch="II–I вв. до н.э.",
        origin="Эгейское море, у острова Антикитера",
        scientific_explanation=(
            "Механизм был моделью Солнечной системы: он рассчитывал положение "
            "Солнца, Луны и планет, фазы Луны и солнечные затмения. Расшифровка "
            "надписей и рентгеновские исследования показали, что это не "
            "аномалия, а вершина античной механики."
        ),
        source_title=(
            "Decoding the ancient Greek astronomical calculator known as the "
            "Antikythera Mechanism"
        ),
        source_url="https://doi.org/10.1038/nature05357",
        status="on_exhibition",
        explorer=freeth,
    )
    lycurgus = await ImpossibleObject.create(
        name="Кубок Ликурга",
        description=(
            "Римский стеклянный кубок IV века н.э. из дихроичного стекла: "
            "при отражённом свете он кажется зелёным, а при проходящем — "
            "рубиново-красным."
        ),
        violation_type="materials",
        material="стекло с наночастицами золота и серебра",
        epoch="IV в. н.э.",
        origin="Римская империя; ныне Британский музей",
        scientific_explanation=(
            "Цвет меняется из-за наночастиц золота и серебра размером около "
            "10–100 нм, распределённых в стекле. Они рассеивают и поглощают "
            "свет по-разному в зависимости от угла и способа освещения — это "
            "ранний пример нанотехнологии."
        ),
        source_title=(
            "An investigation of the origin of the colour of the Lycurgus Cup "
            "by analytical transmission electron microscopy"
        ),
        source_url="https://doi.org/10.1111/j.1475-4754.1990.tb01079.x",
        status="on_exhibition",
        explorer=freestone,
    )
    dagger = await ImpossibleObject.create(
        name="Кинжал Тутанхамона",
        description=(
            "Железный кинжал из гробницы Тутанхамона (XIV в. до н.э.). Для "
            "эпохи, когда железо ещё не выплавляли в промышленных масштабах, "
            "сам материал клинка выглядит невозможным."
        ),
        violation_type="metallurgy",
        material="метеоритное железо, золото",
        epoch="XIV в. до н.э.",
        origin="Долина царей, Египет",
        scientific_explanation=(
            "Клинок изготовлен из метеоритного железа. Рентгенофлуоресцентный "
            "анализ показал высокое содержание никеля и кобальта и характерное "
            "соотношение элементов, совпадающее с составом железных метеоритов."
        ),
        source_title="The meteoritic origin of Tutankhamun's iron dagger blade",
        source_url="https://doi.org/10.1111/maps.12664",
        status="in_storage",
        explorer=comelli,
    )
    roman_concrete = await ImpossibleObject.create(
        name="Римский бетон",
        description=(
            "Бетон римских портов и куполов, который стоит две тысячи лет и в "
            "ряде случаев сам залечивает трещины после попадания воды."
        ),
        violation_type="engineering",
        material="известь, вулканический пепел, обломки камня",
        epoch="I в. до н.э. — II в. н.э.",
        origin="Римская империя, Средиземноморье",
        scientific_explanation=(
            "Римляне применяли горячее смешивание: негашёная известь "
            "реагировала с вулканическим пеплом, а в бетоне оставались "
            "известковые включения. При попадании воды они растворяются и "
            "заполняют трещины карбонатом кальция — происходит "
            "самовосстановление."
        ),
        source_title=(
            "Hot mixing: Mechanistic insights into the durability of ancient "
            "Roman concrete"
        ),
        source_url="https://doi.org/10.1126/sciadv.add1602",
        status="on_exhibition",
        explorer=masic,
    )
    damascus = await ImpossibleObject.create(
        name="Дамасская сабля",
        description=(
            "Сабля XVII века из дамасской стали с характерным узором. При "
            "электронной микроскопии в древнем металле обнаружились структуры, "
            "похожие на современные наноматериалы."
        ),
        violation_type="materials",
        material="дамасская сталь",
        epoch="XVII в.",
        origin="Ближний Восток",
        scientific_explanation=(
            "В стали найдены цементитные нанопроволоки и углеродные "
            "нанотрубки. Они возникли не случайно, а в результате длительной "
            "ковки и травления: углерод перестраивался в наноструктуры, "
            "которые придавали клинку прочность и узор."
        ),
        source_title="Carbon nanotubes in an ancient Damascus sabre",
        source_url="https://doi.org/10.1038/444286a",
        status="in_storage",
        explorer=reibold,
    )
    nebra = await ImpossibleObject.create(
        name="Небрский небесный диск",
        description=(
            "Бронзовый диск около 30 см в диаметре с золотыми вставками, "
            "изображающими Солнце, Луну, звёзды и, вероятно, Плеяды. "
            "Датируется около 1600 г. до н.э."
        ),
        violation_type="astronomy",
        material="бронза, золото",
        epoch="около 1600 г. до н.э.",
        origin="Небра, Саксония-Анхальт, Германия",
        scientific_explanation=(
            "Археометаллургические исследования показали, что диск изготовлен "
            "в раннем бронзовом веке. Его изображения связаны с "
            "астрономическими наблюдениями: положение Солнца и Луны, "
            "возможно, использовалось для определения дней солнцестояния и "
            "лунных циклов."
        ),
        source_title="Archaeometallurgical investigation of the Nebra Sky Disc",
        source_url="https://doi.org/10.1038/s41598-024-80545-5",
        status="on_exhibition",
        explorer=meller,
    )
    diquis_spheres = await ImpossibleObject.create(
        name="Каменные шары Дикис",
        description=(
            "Почти идеальные каменные сферы диаметром от нескольких "
            "сантиметров до двух метров, найденные в дельте реки Дикис в "
            "Коста-Рике."
        ),
        violation_type="geology",
        material="магматические породы",
        epoch="500–1500 гг. н.э.",
        origin="Дельта Дикис, Коста-Рика",
        scientific_explanation=(
            "Шары изготовлены людьми доколумбовой эпохи из местных "
            "магматических пород: заготовку оббивали и шлифовали до "
            "правильной сферы. Назначение и способ перемещения крупных шаров "
            "до сих пор обсуждаются, но их искусственное происхождение не "
            "вызывает сомнений."
        ),
        source_title=(
            "A Preliminary Investigation of the Flood Plain of the Rio Grande "
            "de Térraba, Costa Rica"
        ),
        source_url="https://doi.org/10.2307/275453",
        status="in_storage",
        explorer=stone,
    )

    sky_evh = await Exhibition.create(
        title="Небо древних",
        description=(
            "Как люди бронзового и античного мира наблюдали небо и строили "
            "приборы, опередившие своё время."
        ),
        location="Зал астрономии",
    )
    materials_evh = await Exhibition.create(
        title="Секреты материала",
        description=(
            "Металлы и стекло, в которых древние мастера неосознанно "
            "использовали нанотехнологии."
        ),
        location="Зал материалов",
    )
    stone_evh = await Exhibition.create(
        title="Камень и время",
        description=(
            "Строительные технологии и каменные сферы, которые выглядят "
            "загадочно, но объясняются геологией и археологией."
        ),
        location="Зал геологии и строительства",
    )

    await ObjectExhibition.bulk_create(
        [
            ObjectExhibition(planned_object=antikythera, exhibition=sky_evh),
            ObjectExhibition(planned_object=nebra, exhibition=sky_evh),
            ObjectExhibition(planned_object=lycurgus, exhibition=materials_evh),
            ObjectExhibition(planned_object=damascus, exhibition=materials_evh),
            ObjectExhibition(planned_object=dagger, exhibition=materials_evh),
            ObjectExhibition(planned_object=roman_concrete, exhibition=stone_evh),
            ObjectExhibition(planned_object=diquis_spheres, exhibition=stone_evh),
        ]
    )
