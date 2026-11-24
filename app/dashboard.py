"""Dashboard als Baukasten: jede Kachel = Datenquelle + Darstellung + Filter, frei in Groesse und Reihenfolge.

Layout je Benutzer (auch API-Keys) in der Datenbank, Bereich "dashboard":
[{"id": "running", "title": "", "source": "running", "view": "list", "filters": {...}, "w": 1-12, "h": 1-24}, ...]
- Die Standardkacheln sind Vorlagen (PRESETS) und lassen sich wie eigene Kacheln bearbeiten.
- Jede Datenquelle braucht ein Recht; Kacheln ohne Recht werden weder angezeigt noch geliefert.
- Raster: 12 Spalten, Zeilen zu je 40 px, dicht gepackt (kleinere Kacheln ruecken in freie Luecken).
"""
import secrets

COLS, MAX_H, MAX_TILES = 12, 24, 40

VIEWS = {"number": "Zahl", "list": "Liste", "bar": "Balken", "ampel": "Statusampel"}

# Filter-Bausteine: type jobs (Mehrfachauswahl), select (options) oder int
PERIODS = [("", "gesamter Zeitraum"), ("1d", "letzte 24 Stunden"), ("7d", "letzte 7 Tage"), ("30d", "letzte 30 Tage")]
FILTERS = {
    "jobs": {"type": "jobs", "label": "Aufgaben", "hint": "keine Auswahl = alle Aufgaben"},
    "job_status": {"type": "select", "label": "Status", "options": [
        ("", "alle"), ("ok", "OK"), ("fehler", "Fehler"), ("laeuft", "läuft"), ("paused", "pausiert"),
        ("off", "ausgeschaltet"), ("never", "noch nie gelaufen")]},
    "run_status": {"type": "select", "label": "Status", "options": [
        ("", "alle"), ("ok", "OK"), ("fehler", "Fehler"), ("gestoppt", "gestoppt")]},
    "run_kind": {"type": "select", "label": "Art", "options": [("", "alle Läufe"), ("real", "ohne Testläufe"), ("dry", "nur Testläufe")]},
    "login_result": {"type": "select", "label": "Ergebnis", "options": [("", "alle"), ("ok", "erfolgreich"), ("fail", "fehlgeschlagen")]},
    "audit_cat": {"type": "select", "label": "Bereich", "options": [("", "alle")]},   # wird aus audit.CATEGORIES gefuellt
    "period": {"type": "select", "label": "Zeitraum", "options": PERIODS},
    "limit": {"type": "int", "label": "Höchstens so viele Einträge", "min": 1, "max": 50, "default": 10},
}

# Datenquellen. cols: Spalten fuer die Liste; status: Feld fuer Ampel und Balken (gezaehlt je Status);
# value/max: Feld fuer Balken je Eintrag; noun: Beschriftung der Zahl; kind metrics = jede Zeile ist eine eigene Zahl.
SOURCES = {
    "overview": {"title": "Überblick", "perm": "jobs.view", "views": ["number", "list", "bar"], "filters": [], "kind": "metrics",
                 "cols": [("label", ""), ("value", "")],
                 "desc": "Anzahl Aufgaben, eingeschaltet, laufen, pausiert, mit Fehler, Speicherorte"},
    "running": {"title": "Laufende Aufträge", "perm": "jobs.view", "views": ["list", "bar", "number", "ampel"], "filters": ["jobs"],
                "cols": [("name", "Aufgabe"), ("started", "seit"), ("progress_text", "Fortschritt")], "status": "status",
                "value": "progress", "max": 100, "noun": "laufen gerade", "desc": "Aufgaben, die gerade laufen, mit Fortschritt"},
    "jobs": {"title": "Aufgaben", "perm": "jobs.view", "views": ["ampel", "list", "number", "bar"], "filters": ["jobs", "job_status", "limit"],
             "cols": [("name", "Aufgabe"), ("status_text", "Status"), ("last_run", "Letzter Lauf")], "status": "status",
             "noun": "Aufgaben", "desc": "Aufgaben mit dem Status ihres letzten Laufs"},
    "runs": {"title": "Läufe", "perm": "jobs.view", "views": ["list", "number", "bar", "ampel"],
             "filters": ["jobs", "run_status", "run_kind", "period", "limit"],
             "cols": [("name", "Aufgabe"), ("start", "Start"), ("status_text", "Status"), ("duration_text", "Dauer"),
                      ("copied", "Kopiert"), ("deleted", "Gelöscht"), ("errors", "Fehler")], "status": "status",
             "noun": "Läufe", "desc": "Läufe aus dem Verlauf aller oder ausgewählter Aufgaben"},
    "next_runs": {"title": "Nächste Starts", "perm": "jobs.view", "views": ["list", "number"], "filters": ["jobs", "limit"],
                  "cols": [("name", "Aufgabe"), ("at", "Start"), ("kind_text", "Art")], "noun": "geplante Starts",
                  "desc": "Die nächsten geplanten Starts"},
    "logins": {"title": "Anmeldungen", "perm": "users.view", "views": ["list", "number", "bar", "ampel"],
               "filters": ["login_result", "period", "limit"],
               "cols": [("time", "Zeit"), ("user", "Benutzer"), ("status_text", "Ergebnis"), ("where", "IP-Adresse")], "status": "status",
               "noun": "Anmeldungen", "desc": "Anmeldungen und Fehlversuche"},
    "audit": {"title": "Änderungen (Audit-Log)", "perm": "system.audit", "views": ["list", "number", "bar"], "filters": ["audit_cat", "period", "limit"],
              "cols": [("ts", "Zeit"), ("user", "Benutzer"), ("action", "Aktion"), ("target", "Objekt")], "status": "cat_text",
              "noun": "Einträge", "desc": "Einträge im Audit-Log"},
    "storage": {"title": "Speicherplatz", "perm": "system.settings", "views": ["bar", "list", "number", "ampel"], "filters": [], "kind": "metrics",
                "value": "pct", "max": 100, "status": "status",
                "cols": [("label", "Ort"), ("used_text", "belegt"), ("free_text", "frei"), ("value_text", "Anteil")],
                "desc": "Belegter Platz auf den Laufwerken von /config und /logs sowie Größe der Logs"},
    "system": {"title": "System", "perm": None, "views": ["list", "ampel"], "filters": [], "kind": "kv", "status": "status",
               "cols": [("label", ""), ("value", "")], "desc": "Version, Updates, Laufzeit seit dem letzten Start"},
}

# Standardkacheln (Vorlagen). Sie lassen sich wie eigene Kacheln aendern; "Standard wiederherstellen" holt sie zurueck.
PRESETS = {
    "running": {"title": "Laufende Aufträge", "source": "running", "view": "list", "filters": {}, "w": 8, "h": 4},
    "stats": {"title": "Überblick", "source": "overview", "view": "number", "filters": {}, "w": 4, "h": 6},
    "failed": {"title": "Aufgaben mit Fehler", "source": "jobs", "view": "list", "filters": {"job_status": "fehler"}, "w": 4, "h": 4},
    "last_runs": {"title": "Letzte Läufe", "source": "runs", "view": "list", "filters": {"limit": 10}, "w": 8, "h": 8},
    "next_runs": {"title": "Nächste Starts", "source": "next_runs", "view": "list", "filters": {"limit": 10}, "w": 4, "h": 6},
    "logins": {"title": "Letzte Anmeldungen", "source": "logins", "view": "list", "filters": {"limit": 10}, "w": 8, "h": 10},
    "audit": {"title": "Letzte Änderungen", "source": "audit", "view": "list", "filters": {"limit": 10}, "w": 8, "h": 10},
    "system": {"title": "System", "source": "system", "view": "list", "filters": {}, "w": 4, "h": 5},
    # zusaetzliche Vorlagen, nicht im Standard
    "job_lights": {"title": "Statusampel der Aufgaben", "source": "jobs", "view": "ampel", "filters": {"limit": 20}, "w": 4, "h": 6},
    "errors_7d": {"title": "Fehler der letzten 7 Tage", "source": "runs", "view": "number", "filters": {"run_status": "fehler", "period": "7d"}, "w": 4, "h": 3},
    "runs_bar": {"title": "Läufe der letzten 7 Tage", "source": "runs", "view": "bar", "filters": {"period": "7d"}, "w": 4, "h": 5},
    "failed_logins": {"title": "Fehlgeschlagene Anmeldungen (7 Tage)", "source": "logins", "view": "number", "filters": {"login_result": "fail", "period": "7d"}, "w": 4, "h": 3},
    "storage": {"title": "Speicherplatz", "source": "storage", "view": "bar", "filters": {}, "w": 4, "h": 5},
}
DEFAULT = ["running", "stats", "failed", "last_runs", "next_runs", "logins", "audit", "system"]
OLD_SIZE = {"s": 4, "w": 8}   # Layouts aus 1.54.0: size s/w


def set_audit_categories(cats):
    FILTERS["audit_cat"]["options"] = [("", "alle")] + list(cats.items())


def allowed_source(src, has):
    perm = SOURCES[src]["perm"]
    return perm is None or has(perm)


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _preset_tile(pid):
    p = PRESETS[pid]
    return {"id": pid, "title": "", "source": p["source"], "view": p["view"], "filters": dict(p["filters"]), "w": p["w"], "h": p["h"]}


def default_layout(has):
    return [_preset_tile(p) for p in DEFAULT if allowed_source(PRESETS[p]["source"], has)]


def clean_filters(src, raw):
    """Filter einer Kachel pruefen. Liefert (filters, None) oder (None, (text, *args))."""
    raw = raw or {}
    if not isinstance(raw, dict):
        return None, ("Filter als Objekt angeben.",)
    out = {}
    for k, v in raw.items():
        if k not in SOURCES[src]["filters"]:
            return None, ("Filter {0} passt nicht zur Datenquelle {1}.", k, src)
        f = FILTERS[k]
        if f["type"] == "jobs":
            if isinstance(v, str):
                v = [x for x in v.replace(",", " ").split() if x]
            if not isinstance(v, list) or len(v) > 100 or any(not isinstance(x, str) or len(x) > 64 for x in v):
                return None, ("Aufgaben als Liste von IDs angeben.",)
            if v:
                out[k] = v
        elif f["type"] == "select":
            v = "" if v is None else str(v)
            if v not in [o[0] for o in f["options"]]:
                return None, ("Ungültiger Wert für {0}: {1}", k, v)
            if v:
                out[k] = v
        else:
            n = _int(v)
            if n is None or not f["min"] <= n <= f["max"]:
                return None, ("{0} ist {1} bis {2}.", k, f["min"], f["max"])
            out[k] = n
    return out, None


def clean_tile(item, has):
    """Eine Kachel pruefen und vervollstaendigen. Liefert (tile, None) oder (None, (text, *args))."""
    if isinstance(item, str):
        item = {"id": item}
    if not isinstance(item, dict):
        return None, ("Kachel als Objekt angeben.",)
    tid = str(item.get("id") or "").strip()
    base = _preset_tile(tid) if tid in PRESETS else None
    src = item.get("source") or (base and base["source"])
    if not src:
        return None, (("Unbekannte Kachel: {0}", tid) if tid else ("Datenquelle (source) fehlt.",))
    if src not in SOURCES:
        return None, ("Unbekannte Datenquelle: {0}", str(src))
    if not allowed_source(src, has):
        return None, ("Keine Berechtigung für die Datenquelle {0}.", src)
    same_src = bool(base) and base["source"] == src
    view = item.get("view") or (base["view"] if same_src else SOURCES[src]["views"][0])
    if view not in SOURCES[src]["views"]:
        return None, ("Darstellung {0} passt nicht zur Datenquelle {1}.", str(view), src)
    filters, err = clean_filters(src, item["filters"] if "filters" in item else (base["filters"] if same_src else {}))
    if err:
        return None, err
    w = _int(item.get("w")) if item.get("w") is not None else OLD_SIZE.get(item.get("size"), base["w"] if base else 4)
    h = _int(item.get("h")) if item.get("h") is not None else (base["h"] if base else 5)
    if w is None or not 1 <= w <= COLS:
        return None, ("Breite w ist 1 bis {0} Spalten.", COLS)
    if h is None or not 1 <= h <= MAX_H:
        return None, ("Höhe h ist 1 bis {0} Zeilen.", MAX_H)
    title = str(item.get("title") or "").strip()[:80]
    if not tid or len(tid) > 40:
        tid = "t" + secrets.token_hex(4)
    return {"id": tid, "title": title, "source": src, "view": view, "filters": filters, "w": w, "h": h}, None


def clean(raw, has):
    """Ganzes Layout pruefen. raw: Liste von Kacheln (Objekte oder Vorlagen-IDs). Liefert (layout, None) oder (None, fehler)."""
    if not isinstance(raw, list):
        return None, ("Kacheln als Liste angeben.",)
    if len(raw) > MAX_TILES:
        return None, ("Höchstens {0} Kacheln.", MAX_TILES)
    out, seen = [], set()
    for item in raw:
        t, err = clean_tile(item, has)
        if err:
            return None, err
        while t["id"] in seen:
            t["id"] = "t" + secrets.token_hex(4)
        seen.add(t["id"])
        out.append(t)
    return out, None


def layout_for(stored, has):
    """Gespeichertes Layout (oder Standard), ohne Kacheln, fuer die das Recht fehlt. Alte Layouts werden ergaenzt."""
    if not isinstance(stored, list):
        return default_layout(has)
    out = []
    for t in stored:
        t, err = clean_tile(t, lambda p: True)
        if not err and allowed_source(t["source"], has):
            out.append(t)
    return out


def tile_title(t, tr=lambda x: x):
    if t.get("title"):
        return t["title"]
    if t["id"] in PRESETS and PRESETS[t["id"]]["source"] == t["source"]:
        return tr(PRESETS[t["id"]]["title"])
    return tr(SOURCES[t["source"]]["title"])


def catalog(has, tr=lambda x: x):
    """Bausteine fuer den Editor und die API: Datenquellen (mit Darstellungen und Filtern), Darstellungen, Vorlagen."""
    def fil(k):
        f = FILTERS[k]
        d = {"key": k, "type": f["type"], "label": tr(f["label"])}
        if f["type"] == "select":
            d["options"] = [{"value": v, "label": tr(lbl)} for v, lbl in f["options"]]
        if f["type"] == "int":
            d.update(min=f["min"], max=f["max"], default=f["default"])
        if f.get("hint"):
            d["hint"] = tr(f["hint"])
        return d
    sources = [{"id": s, "title": tr(v["title"]), "description": tr(v["desc"]), "permission": v["perm"], "views": v["views"],
                "filters": [fil(k) for k in v["filters"]]} for s, v in SOURCES.items() if allowed_source(s, has)]
    presets = [dict(_preset_tile(p), title=tr(PRESETS[p]["title"])) for p in PRESETS if allowed_source(PRESETS[p]["source"], has)]
    return {"sources": sources, "views": [{"id": k, "title": tr(v)} for k, v in VIEWS.items()], "presets": presets}


# ----------------------------------------------------------------- Darstellung
LIGHT = {"ok": "green", "laeuft": "blue", "fehler": "red", "fail": "red", "gestoppt": "yellow", "paused": "yellow",
         "off": "grey", "never": "grey", "warn": "yellow", "info": "green"}
LIGHT_ORDER = ["red", "yellow", "blue", "green", "grey"]


def shape(src, view, rows, filters, tr=lambda x: x, status_text=lambda x: x):
    """Zeilen einer Datenquelle in die gewaehlte Darstellung bringen."""
    spec = SOURCES[src]
    limit = filters.get("limit") or FILTERS["limit"]["default"]
    st_key = spec.get("status")
    out = {"view": view, "total": len(rows)}
    if view == "number":
        if spec.get("kind") == "metrics":
            out["numbers"] = [{"label": r["label"], "value": r.get("value_text", r.get("value")), "cls": r.get("cls", ""),
                               "link": r.get("link", "")} for r in rows]
        else:
            bad = filters.get("run_status") == "fehler" or filters.get("job_status") == "fehler" or filters.get("login_result") == "fail"
            out["numbers"] = [{"label": tr(spec.get("noun", "")), "value": len(rows), "cls": "fehler" if bad and rows else "", "link": ""}]
    elif view == "list":
        out["cols"] = [{"key": k, "label": tr(lbl) if lbl else ""} for k, lbl in spec.get("cols", [])]
        out["rows"] = rows if spec.get("kind") in ("metrics", "kv") else rows[:limit]
    elif view == "bar":
        if spec.get("value"):
            out["bars"] = [{"label": r.get("label") or r.get("name", ""), "value": r.get(spec["value"]) or 0, "max": spec["max"],
                            "text": r.get("value_text") or f"{r.get(spec['value']) or 0} %", "cls": r.get("cls", ""),
                            "link": r.get("link", "")} for r in rows[:limit]]
        elif spec.get("kind") == "metrics":
            mx = max([r.get("value") or 0 for r in rows] + [1])
            out["bars"] = [{"label": r["label"], "value": r.get("value") or 0, "max": mx, "text": str(r.get("value")),
                            "cls": r.get("cls", ""), "link": r.get("link", "")} for r in rows]
        else:
            counts = {}
            for r in rows:
                k = r.get(st_key) or ""
                counts[k] = counts.get(k, 0) + 1
            mx = max(list(counts.values()) + [1])
            out["bars"] = [{"label": status_text(k) if st_key == "status" else k, "value": n, "max": mx, "text": str(n), "cls": k,
                            "link": ""} for k, n in sorted(counts.items(), key=lambda x: -x[1])]
    elif view == "ampel":
        lights = [{"label": r.get("label") or r.get("name") or r.get("user") or "", "state": LIGHT.get(r.get(st_key), "grey"),
                   "text": r.get("status_text") or r.get("value_text") or "", "link": r.get("link", "")} for r in rows]
        states = [x["state"] for x in lights]
        overall = next((s for s in ("red", "yellow") if s in states), "green" if states else "grey")
        out.update(overall=overall, lights=lights[:limit], counts={s: states.count(s) for s in LIGHT_ORDER if s in states})
    return out


# ----------------------------------------------------------------- Tabs
MAX_TABS = 12
DEFAULT_TAB = "Übersicht"


def _tab_id():
    return "tab" + secrets.token_hex(3)


def default_tabs(has, tr=lambda x: x):
    return [{"id": "main", "name": tr(DEFAULT_TAB), "tiles": default_layout(has)}]


def clean_tabs(raw, has):
    """Alle Tabs pruefen: [{"id"?, "name", "tiles": [...]}]. Liefert (tabs, None) oder (None, fehler)."""
    if not isinstance(raw, list) or not raw:
        return None, ("Mindestens einen Tab angeben.",)
    if len(raw) > MAX_TABS:
        return None, ("Höchstens {0} Tabs.", MAX_TABS)
    out, seen = [], set()
    for t in raw:
        if not isinstance(t, dict):
            return None, ("Tab als Objekt angeben.",)
        name = str(t.get("name") or "").strip()[:40]
        if not name:
            return None, ("Jeder Tab braucht einen Namen.",)
        tiles, err = clean(t.get("tiles") or [], has)
        if err:
            return None, err
        tid = str(t.get("id") or "").strip()
        if not tid or len(tid) > 20 or tid in seen:
            tid = _tab_id()
        seen.add(tid)
        out.append({"id": tid, "name": name, "tiles": tiles})
    return out, None


def tabs_for(stored, has, tr=lambda x: x):
    """Gespeicherte Tabs (oder Standard). Layouts bis 1.55.0 (nur eine Kachel-Liste) werden zum ersten Tab."""
    if isinstance(stored, list):
        return [{"id": "main", "name": tr(DEFAULT_TAB), "tiles": layout_for(stored, has)}]
    if not isinstance(stored, dict) or not stored.get("tabs"):
        return default_tabs(has, tr)
    out = []
    for t in stored["tabs"]:
        if isinstance(t, dict) and t.get("id"):
            out.append({"id": t["id"], "name": t.get("name") or tr(DEFAULT_TAB), "tiles": layout_for(t.get("tiles") or [], has)})
    return out or default_tabs(has, tr)
