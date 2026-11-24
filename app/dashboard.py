"""Dashboard: Kacheln, die jeder Benutzer selbst auswaehlt, anordnet und in der Breite einstellt.

Layout je Benutzer (auch API-Keys) in der Datenbank, Bereich "dashboard": [{"id": "running", "size": "s" | "w"}, ...].
Jede Kachel braucht ein Recht; Kacheln ohne Recht werden weder angezeigt noch geliefert.
"""

# id: (Titel, Recht, Beschreibung, Standardbreite)
TILES = {
    "running": ("Laufende Aufträge", "jobs.view", "Aufgaben, die gerade laufen, mit Fortschritt", "w"),
    "stats": ("Überblick", "jobs.view", "Anzahl Aufgaben, laufend, pausiert, mit Fehler, Speicherorte", "s"),
    "failed": ("Aufgaben mit Fehler", "jobs.view", "Aufgaben, deren letzter Lauf fehlgeschlagen ist", "s"),
    "last_runs": ("Letzte Läufe", "jobs.view", "Die letzten 10 Läufe aller Aufgaben", "w"),
    "next_runs": ("Nächste Starts", "jobs.view", "Die nächsten 10 geplanten Starts", "s"),
    "logins": ("Letzte Anmeldungen", "users.view", "Die letzten 10 Anmeldungen und Fehlversuche", "w"),
    "audit": ("Letzte Änderungen", "system.audit", "Die letzten 10 Einträge im Audit-Log", "w"),
    "system": ("System", None, "Version, Updates, Laufzeit seit dem letzten Start", "s"),
}
DEFAULT = ["running", "stats", "failed", "last_runs", "next_runs", "logins", "audit", "system"]
SIZES = ("s", "w")


def allowed(tile_id, has):
    perm = TILES[tile_id][1]
    return perm is None or has(perm)


def default_layout(has):
    return [{"id": t, "size": TILES[t][3]} for t in DEFAULT if allowed(t, has)]


def clean(raw, has):
    """Layout pruefen. raw: Liste aus {"id", "size"} oder Kachel-IDs. Liefert (layout, None) oder (None, (text, *args))."""
    if not isinstance(raw, list):
        return None, ("Kacheln als Liste angeben.",)
    out, seen = [], set()
    for item in raw:
        if isinstance(item, str):
            item = {"id": item}
        if not isinstance(item, dict) or item.get("id") not in TILES:
            return None, ("Unbekannte Kachel: {0}", str(item.get("id") if isinstance(item, dict) else item))
        tid = item["id"]
        size = item.get("size") or TILES[tid][3]
        if size not in SIZES:
            return None, ("Breite ist s (schmal) oder w (breit).",)
        if tid in seen:
            continue
        if not allowed(tid, has):
            return None, ("Keine Berechtigung für die Kachel {0}.", tid)
        seen.add(tid)
        out.append({"id": tid, "size": size})
    return out, None


def layout_for(stored, has):
    """Gespeichertes Layout (oder Standard), ohne Kacheln, fuer die das Recht fehlt."""
    if not isinstance(stored, list):
        return default_layout(has)
    return [t for t in stored if isinstance(t, dict) and t.get("id") in TILES and allowed(t["id"], has)]


def catalog(has, tr=lambda x: x):
    return [{"id": t, "title": tr(v[0]), "description": tr(v[2]), "permission": v[1], "size": v[3]}
            for t, v in TILES.items() if allowed(t, has)]
