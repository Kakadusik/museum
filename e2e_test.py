import json
import os
import sys
import urllib.request
import urllib.parse

BASE = os.environ.get("MUSEUM_URL", "http://127.0.0.1:8010")
if len(sys.argv) > 1:
    BASE = f"http://127.0.0.1:{sys.argv[1]}"


def req(method, path, payload=None, query=None):
    url = BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if data:
        r.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(r) as resp:
            body = resp.read()
            if method == "DELETE":
                return resp.status, None
            ct = resp.headers.get("Content-Type", "")
            if "json" in ct:
                return resp.status, json.loads(body)
            if "html" in ct:
                return resp.status, body.decode("utf-8", "replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", "replace"))


def check(name, got, want, detail=""):
    ok = got == want
    print(f"{'OK ' if ok else 'FAIL'} {name}: {got} (expect {want}){(' ' + detail) if detail and not ok else ''}")
    return ok


all_ok = True

for path in ("/", "/items", "/items/1", "/explorers", "/explorers/1", "/exhibitions", "/exhibitions/1", "/index.html.js", "/@nue/mount.js", "/@nue/state.js", "/css/style.css", "/ui/items.html.js"):
    s, body = req("GET", path)
    all_ok &= check(f"GET {path}", s, 200)

s, body = req("GET", "/api/health")
all_ok &= check("health status", body.get("status"), "ok")
all_ok &= check("health db", body.get("db"), "ok")

s, body = req("GET", "/api/stats")
all_ok &= check("stats total_objects", body["total_objects"], 7)
all_ok &= check("stats by_status keys", sorted(body["by_status"]), ["in_storage", "on_exhibition"])

# items with filters
s, body = req("GET", "/api/items", query={"violation_type": "time"})
all_ok &= check("items filtered time", len(body["items"]), 2)
s, body = req("GET", "/api/items", query={"q": "шар"})
all_ok &= check("items q=шар", len(body["items"]), 1)

# full CRUD cycle: explorer -> item -> exhibition -> relink
s, ex = req("POST", "/api/explorers", {"name": "Тест Крот", "specialization": "Подземное время", "birth_year": 1980})
all_ok &= check("create explorer", s, 201)
expl_id = ex["id"]

s, it = req("POST", "/api/items", {"name": "Часы, копающие вглубь", "violation_type": "time", "status": "in_storage", "explorer_id": expl_id, "description": "Идут назад в геологическом смысле", "material": "базальт"})
all_ok &= check("create item", s, 201)
item_id = it["id"]
all_ok &= check("item explorer attached", it["explorer"]["id"], expl_id)

s, exb = req("POST", "/api/exhibitions", {"title": "Временные раскопки", "description": "Выставка недокопанного времени", "location": "Зал Шурф"})
all_ok &= check("create exhibition", s, 201)
exb_id = exb["id"]

s, it2 = req("PUT", f"/api/items/{item_id}", {"name": "Часы, копающие вглубь", "violation_type": "time", "status": "on_exhibition", "exhibition_ids": [exb_id]})
all_ok &= check("update item + exhibition", s, 200)
all_ok &= check("item exhibition linked", len(it2["exhibitions"]), 1)

s, det = req("GET", f"/api/items/{item_id}")
all_ok &= check("item detail exhibitions", len(det["exhibitions"]), 1)
all_ok &= check("item detail explorer", det["explorer"]["name"], "Тест Крот")

# guards
s, _ = req("DELETE", f"/api/explorers/{expl_id}")
all_ok &= check("cannot delete explorer with items", s, 400)

s, _ = req("DELETE", f"/api/exhibitions/{exb_id}")
all_ok &= check("delete exhibition cascades", s, 204)

s, det = req("GET", f"/api/items/{item_id}")
all_ok &= check("item survives exhibition delete", len(det["exhibitions"]), 0)

s, _ = req("DELETE", f"/api/items/{item_id}")
all_ok &= check("delete item", s, 204)
s, _ = req("DELETE", f"/api/explorers/{expl_id}")
all_ok &= check("delete freed explorer", s, 204)

# not found
s, err = req("GET", "/api/items/999999")
all_ok &= check("item 404", s, 404)

# restore demo data intact
s, body = req("GET", "/api/stats")
all_ok &= check("final total_objects", body["total_objects"], 7)
all_ok &= check("final total_explorers", body["total_explorers"], 3)
all_ok &= check("final total_exhibitions", body["total_exhibitions"], 3)

print("\nRESULT:", "ALL PASS" if all_ok else "SOME FAILED")