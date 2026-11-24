"""Dashboard: Kacheln, die jeder Benutzer selbst auswaehlt, anordnet und in der Breite einstellt.

Layout je Benutzer (auch API-Keys) in der Datenbank, Bereich "dashboard": [{"id": "running", "w": 1-12, "h": 1-24}, ...].
Jede Kachel braucht ein Recht; Kacheln ohne Recht werden weder angezeigt noch geliefert.
"""

# id: (Titel, Recht, Beschreibung, Standardbreite, Standardhoehe)
# Raster: 12 Spalten, Zeilen zu je ROW_PX Pixel. Kacheln werden dicht gepackt (kleine Kacheln fuellen Luecken),
# so passen z. B. zwei Kacheln mit Hoehe 3 untereinander neben eine Kachel mit Hoehe 6.
COLS, MAX_H, ROW_PX = 12, 24, 40
TILES = {
    "running": ("Laufende Aufträge", "jobs.view", "Aufgaben, die gerade laufen, mit Fortschritt", 8, 4),
    "stats": ("Überblick", "jobs.view", "Anzahl Aufgaben, laufend, pausiert, mit Fehler, Speicherorte", 4, 6),
    "failed": ("Aufgaben mit Fehler", "jobs.view", "Aufgaben, deren letzter Lauf fehlgeschlagen ist", 4, 4),
    "last_runs": ("Letzte Läufe", "jobs.view", "Die letzten 10 Läufe aller Aufgaben", 8, 8),
    "next_runs": ("Nächste Starts", "jobs.view", "Die nächsten 10 geplanten Starts", 4, 6),
    "logins": ("Letzte Anmeldungen", "users.view", "Die letzten 10 Anmeldungen und Fehlversuche", 8, 10),
    "audit": ("Letzte Änderungen", "system.audit", "Die letzten 10 Einträge im Audit-Log", 8, 10),
    "system": ("System", None, "Version, Updates, Laufzeit seit dem letzten Start", 4, 5),
}
DEFAULT = ["running", "stats", "failed", "last_runs", "next_runs", "logins", "audit", "system"]
OLD_SIZE = {"s": 4, "w": 8}   # Layouts aus 1.54.0: size s/w


def allowed(tile_id, has):
    perm = TILES[tile_id][1]
    return perm is None or has(perm)


def _tile(tid, w=None, h=None):
    return {"id": tid, "w": w or TILES[tid][3], "h": h or TILES[tid][4]}


def default_layout(has):
    return [_tile(t) for t in DEFAULT if allowed(t, has)]


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def clean(raw, has):
    """Layout pruefen. raw: Liste aus {"id", "w", "h"} (oder alt {"id", "size"}) oder Kachel-IDs.
    Liefert (layout, None) oder (None, (text, *args))."""
    if not isinstance(raw, list):
        return None, ("Kacheln als Liste angeben.",)
    out, seen = [], set()
    for item in raw:
        if isinstance(item, str):
            item = {"id": item}
        if not isinstance(item, dict) or item.get("id") not in TILES:
            return None, ("Unbekannte Kachel: {0}", str(item.get("id") if isinstance(item, dict) else item))
        tid = item["id"]
        w = _int(item.get("w")) if item.get("w") is not None else OLD_SIZE.get(item.get("size"), TILES[tid][3])
        h = _int(item.get("h")) if item.get("h") is not None else TILES[tid][4]
        if w is None or not 1 <= w <= COLS:
            return None, ("Breite w ist 1 bis {0} Spalten.", COLS)
        if h is None or not 1 <= h <= MAX_H:
            return None, ("Höhe h ist 1 bis {0} Zeilen.", MAX_H)
        if tid in seen:
            continue
        if not allowed(tid, has):
            return None, ("Keine Berechtigung für die Kachel {0}.", tid)
        seen.add(tid)
        out.append(_tile(tid, w, h))
    return out, None


def layout_for(stored, has):
    """Gespeichertes Layout (oder Standard), ohne Kacheln, fuer die das Recht fehlt."""
    if not isinstance(stored, list):
        return default_layout(has)
    out = []
    for t in stored:
        if isinstance(t, dict) and t.get("id") in TILES and allowed(t["id"], has):
            out.append(_tile(t["id"], t.get("w") or OLD_SIZE.get(t.get("size")), t.get("h")))
    return out


def catalog(has, tr=lambda x: x):
    return [{"id": t, "title": tr(v[0]), "description": tr(v[2]), "permission": v[1], "w": v[3], "h": v[4]}
            for t, v in TILES.items() if allowed(t, has)]
