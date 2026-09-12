import os

from sanic import Sanic, empty, json
from sanic.response import file

from config import AUTO_RELOAD, DEBUG, FRONTEND_DIST, HOST, PORT
from db import init_db
from routes.exhibitions import exhibitions_bp
from routes.explorers import explorers_bp
from routes.items import items_bp
from routes.stats import stats_bp

app = Sanic("museum")

app.blueprint(items_bp)
app.blueprint(explorers_bp)
app.blueprint(exhibitions_bp)
app.blueprint(stats_bp)


@app.listener("before_server_start")
async def setup_database(app, loop):
    await init_db()


def _safe_resolve(dist_root: str, path: str) -> str | None:
    base = os.path.normpath(dist_root)
    candidate = os.path.normpath(os.path.join(base, path))
    if candidate != base and not candidate.startswith(base + os.sep):
        return None
    if os.path.isfile(candidate):
        return candidate
    return None


async def _serve_asset(request, path: str):
    if not os.path.isdir(FRONTEND_DIST):
        return json({"error": "frontend not built"}, status=404)
    asset = _safe_resolve(FRONTEND_DIST, path)
    if asset:
        return await file(asset)
    index_path = os.path.normpath(os.path.join(FRONTEND_DIST, "index.html"))
    if os.path.isfile(index_path):
        return await file(index_path)
    return json({"error": "not found"}, status=404)


@app.get("/")
async def index(request):
    return await _serve_asset(request, "")


@app.get("/<path:path>")
async def spa_fallback(request, path: str):
    if path == "favicon.ico":
        return empty(status=404)
    if path.startswith("api/"):
        return json({"error": "not found"}, status=404)
    return await _serve_asset(request, path)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG, auto_reload=AUTO_RELOAD)