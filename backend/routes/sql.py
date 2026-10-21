import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from sanic import Blueprint, json
from tortoise.connection import connections

sql_bp = Blueprint("sql", url_prefix="/api")

READONLY_KEYWORDS = {"SELECT", "WITH", "EXPLAIN", "SHOW"}
MAX_ROWS = 1000
MAX_QUERY_LENGTH = 5000


def _jsonable(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return value


def _normalize(rows):
    return [{key: _jsonable(val) for key, val in row.items()} for row in rows]


def _first_keyword(query: str) -> str:
    cleaned = re.sub(r"--[^\n]*", "", query)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.S).strip()
    return cleaned.split(None, 1)[0].upper() if cleaned else ""


@sql_bp.post("/sql")
async def run_sql(request):
    body = request.json or {}
    query = (body.get("query") or "").strip()

    if not query:
        return json({"error": "Пустой запрос"}, status=400)
    if len(query) > MAX_QUERY_LENGTH:
        return json({"error": f"Запрос длиннее {MAX_QUERY_LENGTH} символов"}, status=400)

    keyword = _first_keyword(query)
    if keyword not in READONLY_KEYWORDS:
        return json(
            {"error": "Разрешены только read-only запросы (SELECT, WITH, EXPLAIN, SHOW)"},
            status=400,
        )

    conn = connections.get("default")
    try:
        rows = await conn.execute_query_dict(query)
        if len(rows) > MAX_ROWS:
            rows = rows[:MAX_ROWS]
        rows = _normalize(rows)
        columns = list(rows[0].keys()) if rows else []
    except Exception as exc:
        return json({"error": str(exc)}, status=400)

    return json({"columns": columns, "rows": rows, "count": len(rows)})
