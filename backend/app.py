import os
import re

from sanic import Sanic, empty, json
from sanic.response import file, html

from config import AUTO_RELOAD, DEBUG, FRONTEND_DIST, HOST, PORT
from db import init_db
from routes.exhibitions import exhibitions_bp
from routes.explorers import explorers_bp
from routes.items import items_bp
from routes.meta import meta_bp
from routes.sql import sql_bp
from routes.stats import stats_bp

app = Sanic("museum")

app.blueprint(items_bp)
app.blueprint(explorers_bp)
app.blueprint(exhibitions_bp)
app.blueprint(meta_bp)
app.blueprint(sql_bp)
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


def _fix_index_mount_order(html_text: str) -> str:
    imap_re = re.compile(r'<script type="importmap">.*?</script>', re.S)
    mount_re = re.compile(r'<script src="/@nue/mount\.js"[^>]*></script>')
    imap = imap_re.search(html_text)
    mount = mount_re.search(html_text)
    if not imap or not mount or mount.start() > imap.start():
        return html_text
    mount_tag = mount.group(0)
    rest = html_text[: mount.start()] + html_text[mount.end():]
    imap = imap_re.search(rest)
    return rest[: imap.end()] + "\n" + mount_tag + rest[imap.end():]


async def _serve_asset(request, path: str):
    if not os.path.isdir(FRONTEND_DIST):
        return json({"error": "frontend not built"}, status=404)
    asset = _safe_resolve(FRONTEND_DIST, path)
    if asset:
        if os.path.normpath(asset) == os.path.normpath(os.path.join(FRONTEND_DIST, "index.html")):
            with open(asset, encoding="utf-8") as f:
                return html(_fix_index_mount_order(f.read()))
        return await file(asset)
    index_path = os.path.normpath(os.path.join(FRONTEND_DIST, "index.html"))
    if os.path.isfile(index_path):
        with open(index_path, encoding="utf-8") as f:
            return html(_fix_index_mount_order(f.read()))
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