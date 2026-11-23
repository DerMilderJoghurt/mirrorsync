"""Pruefung auf eine neuere MirrorSync-Version ueber die GitHub-Releases-API.

Abgefragt wird nur https://api.github.com/repos/<UPDATE_REPO>/releases/latest (ohne Daten ueber diese
Installation, ausser der Version im User-Agent). Das Ergebnis liegt in der Datenbank (meta "update"), damit es
einen Neustart uebersteht. Geprueft wird hoechstens alle INTERVAL Sekunden, abschaltbar in den Einstellungen.
"""
import json
import os
import re
import time
import urllib.request

REPO = os.environ.get("UPDATE_REPO", "DerMilderJoghurt/mirrorsync")
INTERVAL = 6 * 3600
TIMEOUT = 10
_db = None
_version = "0"


def init(db, version):
    global _db, _version
    _db, _version = db, version


def parse(v):
    """'v1.33.2' -> (1, 33, 2); unbrauchbar -> None."""
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", (v or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def newer(latest, current):
    a, b = parse(latest), parse(current)
    return bool(a and b and a > b)


def _state():
    st = (_db.meta("update") if _db else None) or {}
    if isinstance(st, str):
        try:
            st = json.loads(st)
        except ValueError:
            st = {}
    return st if isinstance(st, dict) else {}


def check():
    """Jetzt bei GitHub nachfragen. Gibt den neuen Zustand zurueck, Fehler stehen in 'error'."""
    st = _state()
    st["checked"] = time.strftime("%Y-%m-%d %H:%M:%S")
    st["checked_ts"] = int(time.time())
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                     headers={"Accept": "application/vnd.github+json",
                                              "User-Agent": f"MirrorSync/{_version}"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
        tag = str(data.get("tag_name") or "")
        if not parse(tag):
            raise ValueError(f"unbekannte Versionsangabe {tag!r}")
        st.update(latest=tag.lstrip("v"), url=str(data.get("html_url") or f"https://github.com/{REPO}/releases"),
                  published=str(data.get("published_at") or "")[:10], error="")
    except Exception as e:  # noqa: BLE001 - Netzwerk, JSON, HTTP: alles nur melden
        st["error"] = str(e)[:300]
    if _db:
        _db.set_meta("update", json.dumps(st))
    return st


def due():
    return int(time.time()) - int(_state().get("checked_ts") or 0) >= INTERVAL


def status(enabled=True):
    st = _state()
    latest = st.get("latest") or ""
    return {"enabled": bool(enabled), "current": _version, "latest": latest,
            "update_available": bool(enabled) and newer(latest, _version),
            "url": st.get("url") or f"https://github.com/{REPO}/releases", "published": st.get("published") or "",
            "checked": st.get("checked") or "", "error": st.get("error") or "", "repo": REPO}
