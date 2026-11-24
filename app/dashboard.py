"""Dashboard als Baukasten: jede Kachel = Datenquelle + Darstellung + Filter, frei in Groesse und Reihenfolge.

Layout je Benutzer (auch API-Keys) in der Datenbank, Bereich "dashboard":
[{"id": "running", "title": "", "source": "running", "view": "list", "filters": {...}, "w": 1-12, "h": 1-24}, ...]
- Die Standardkacheln sind Vorlagen (PRESETS) und lassen sich wie eigene Kacheln bearbeiten.
- Jede Datenquelle braucht ein Recht; Kacheln ohne Recht werden weder angezeigt noch geliefert.
- Raster: 12 Spalten, Zeilen zu je 40 px, dicht gepackt (kleinere Kacheln ruecken in freie Luecken).
"""
import datetime
import math
import secrets

COLS, MAX_H, MAX_TILES = 12, 24, 40

VIEWS = {"number": "Zahl", "spark": "Zahl mit Verlauf", "list": "Liste", "bar": "Balken", "stacked": "Gestapelte Balken pro Tag",
         "pie": "Tortendiagramm", "gauge": "Tacho", "line": "Liniendiagramm", "heatmap": "Kalender-Heatmap", "timeline": "Zeitleiste",
         "ampel": "Statusampel"}
# Darstellungen ueber die Zeit: Standard-Zeitraum in Tagen, wenn im Filter keiner gewaehlt ist
TIME_VIEWS = {"spark": 30, "stacked": 30, "line": 30, "heatmap": 90, "timeline": 1}

# Filter-Bausteine: type jobs (Mehrfachauswahl), select (options) oder int
PERIODS = [("", "gesamter Zeitraum"), ("1d", "letzte 24 Stunden"), ("7d", "letzte 7 Tage"), ("30d", "letzte 30 Tage"),
           ("90d", "letzte 90 Tage"), ("365d", "letzte 365 Tage")]
PERIOD_DAYS = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "365d": 365}
METRICS = [("count", "Anzahl Läufe"), ("bytes", "übertragene Datenmenge"), ("duration", "Laufdauer (Durchschnitt)"),
           ("copied", "kopierte Dateien"), ("deleted", "gelöschte Dateien"), ("errors", "Fehler")]
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
    "limit": {"type": "int", "label": "Höchstens so viele Einträge", "min": 1, "max": 50, "default": 10,
              "views": ["list", "bar", "ampel"]},
    "metric": {"type": "select", "label": "Messwert", "options": METRICS, "views": ["line", "spark"]},
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
    "jobs": {"title": "Aufgaben", "perm": "jobs.view", "views": ["ampel", "list", "number", "bar", "pie", "gauge"], "filters": ["jobs", "job_status", "limit"],
             "cols": [("name", "Aufgabe"), ("status_text", "Status"), ("last_run", "Letzter Lauf")], "status": "status",
             "noun": "Aufgaben", "desc": "Aufgaben mit dem Status ihres letzten Laufs"},
    "runs": {"title": "Läufe", "perm": "jobs.view", "views": ["list", "number", "spark", "bar", "stacked", "pie", "gauge", "line",
                                                           "heatmap", "timeline", "ampel"],
             "filters": ["jobs", "run_status", "run_kind", "period", "metric", "limit"], "time": "start",
             "cols": [("name", "Aufgabe"), ("start", "Start"), ("status_text", "Status"), ("duration_text", "Dauer"),
                      ("bytes_text", "Übertragen"), ("copied", "Kopiert"), ("deleted", "Gelöscht"), ("errors", "Fehler")], "status": "status",
             "noun": "Läufe", "desc": "Läufe aus dem Verlauf aller oder ausgewählter Aufgaben"},
    "next_runs": {"title": "Nächste Starts", "perm": "jobs.view", "views": ["list", "number"], "filters": ["jobs", "limit"],
                  "cols": [("name", "Aufgabe"), ("at", "Start"), ("kind_text", "Art")], "noun": "geplante Starts",
                  "desc": "Die nächsten geplanten Starts"},
    "logins": {"title": "Anmeldungen", "perm": "users.view", "views": ["list", "number", "spark", "bar", "stacked", "pie", "gauge",
                                                                  "line", "heatmap", "ampel"],
               "filters": ["login_result", "period", "limit"], "time": "time",
               "cols": [("time", "Zeit"), ("user", "Benutzer"), ("status_text", "Ergebnis"), ("where", "IP-Adresse")], "status": "status",
               "noun": "Anmeldungen", "desc": "Anmeldungen und Fehlversuche"},
    "audit": {"title": "Änderungen (Audit-Log)", "perm": "system.audit", "views": ["list", "number", "spark", "bar", "stacked", "pie",
                                                                                "line", "heatmap"], "filters": ["audit_cat", "period", "limit"], "time": "ts",
              "cols": [("ts", "Zeit"), ("user", "Benutzer"), ("action", "Aktion"), ("target", "Objekt")], "status": "cat_text",
              "noun": "Einträge", "desc": "Einträge im Audit-Log"},
    "storage": {"title": "Speicherplatz", "perm": "system.settings", "views": ["bar", "pie", "gauge", "list", "number", "ampel"], "filters": [], "kind": "metrics",
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
    "runs_pie": {"title": "Läufe nach Status (30 Tage)", "source": "runs", "view": "pie", "filters": {"period": "30d"}, "w": 4, "h": 6},
    "bytes_line": {"title": "Übertragene Datenmenge pro Tag", "source": "runs", "view": "line", "filters": {"period": "30d", "metric": "bytes"}, "w": 6, "h": 6},
    "duration_line": {"title": "Laufdauer pro Tag", "source": "runs", "view": "line", "filters": {"period": "30d", "metric": "duration"}, "w": 6, "h": 6},
    "runs_stacked": {"title": "Läufe pro Tag", "source": "runs", "view": "stacked", "filters": {"period": "30d"}, "w": 6, "h": 6},
    "success_gauge": {"title": "Erfolgsquote (30 Tage)", "source": "runs", "view": "gauge", "filters": {"period": "30d"}, "w": 3, "h": 5},
    "storage_gauge": {"title": "Speicherplatz", "source": "storage", "view": "gauge", "filters": {}, "w": 4, "h": 5},
    "runs_heatmap": {"title": "Läufe im Kalender", "source": "runs", "view": "heatmap", "filters": {"period": "365d"}, "w": 12, "h": 5},
    "runs_today": {"title": "Läufe heute", "source": "runs", "view": "spark", "filters": {"period": "1d"}, "w": 3, "h": 3},
    "runs_timeline": {"title": "Zeitleiste der Läufe (24 Stunden)", "source": "runs", "view": "timeline", "filters": {"period": "1d"}, "w": 12, "h": 7},
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
        if f.get("views"):
            d["views"] = f["views"]
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
    elif view == "pie":
        if spec.get("value"):   # Speicherplatz: je Laufwerk belegt/frei
            pies = []
            for r in rows:
                if r.get("pct") is None or r.get("same"):
                    continue
                pies.append(pie(r["label"], [(tr("belegt") + f" ({r.get('used_text', '')})", r["pct"], "fehler" if r["pct"] >= 95 else "used"),
                                             (tr("frei") + f" ({r.get('free_text', '')})", 100 - r["pct"], "free")], f"{r['pct']} %"))
            out["pies"] = pies
        else:
            counts = {}
            for r in rows:
                k = r.get(st_key) or ""
                counts[k] = counts.get(k, 0) + 1
            items = [(status_text(k) if st_key == "status" else k, n, k) for k, n in sorted(counts.items(), key=lambda x: -x[1])]
            out["pies"] = [pie("", items, str(len(rows)))] if rows else []
    elif view in TIME_VIEWS:
        out.update(_time_view(src, view, rows, filters, tr, status_text))
    elif view == "gauge":
        out["gauges"] = _gauges(src, rows, tr)
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


# Farben fuer Tortenstuecke: Status-Farben, sonst eine feste Reihe
PIE_STATUS = {"ok": "var(--ok)", "fehler": "var(--err)", "fail": "var(--err)", "laeuft": "var(--run)", "gestoppt": "var(--warn)",
              "paused": "var(--warn)", "off": "var(--bd2)", "never": "var(--mut)", "used": "var(--acc)", "free": "var(--bd)"}
PIE_COLORS = ["#4f46e5", "#0ea5e9", "#16a34a", "#f59e0b", "#db2777", "#14b8a6", "#8b5cf6", "#ef4444", "#84cc16", "#64748b"]


def pie(title, items, center=""):
    """Tortendiagramm: items = [(label, wert, schluessel)] -> {"title", "center", "gradient" (CSS), "slices"}."""
    total = sum(v for _, v, _ in items) or 1
    slices, stops, pos, n = [], [], 0.0, 0
    for label, v, key in items:
        color = PIE_STATUS.get(key)
        if not color:
            color = PIE_COLORS[n % len(PIE_COLORS)]
            n += 1
        share = 100.0 * v / total
        stops.append(f"{color} {pos:.2f}% {pos + share:.2f}%")
        pos += share
        slices.append({"label": label, "value": v, "pct": round(share), "color": color})
    return {"title": title, "center": center, "slices": slices,
            "gradient": "conic-gradient(" + ", ".join(stops) + ")" if stops else "var(--bd)"}


# ----------------------------------------------------------------- Diagramme ueber die Zeit
def human_size(n):
    n = int(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n} B" if unit == "B" else f"{n:.0f} {unit}" if unit == "KB" else f"{n:.1f} {unit}"
        n /= 1024


def human_dur(sec):
    sec = int(round(sec or 0))
    if sec < 60:
        return f"{sec} s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m} min {s} s" if s else f"{m} min"
    h, m = divmod(m, 60)
    return f"{h} h {m} min"


def _ts(v):
    try:
        return datetime.datetime.strptime(str(v)[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _window(view, filters):
    return PERIOD_DAYS.get(filters.get("period")) or TIME_VIEWS.get(view, 30)


def _buckets(days, now):
    """Zeitabschnitte: bei 24 Stunden je Stunde, sonst je Tag. -> (start, schritt, anzahl, beschriftungen)"""
    if days <= 1:
        start = now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=23)
        return start, datetime.timedelta(hours=1), 24, [(start + datetime.timedelta(hours=i)).strftime("%H:00") for i in range(24)]
    start = (now - datetime.timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start, datetime.timedelta(days=1), days, [(start + datetime.timedelta(days=i)).strftime("%d.%m.") for i in range(days)]


def _bucketize(rows, tkey, start, step, n):
    out = [[] for _ in range(n)]
    for r in rows:
        t = _ts(r.get(tkey))
        if t and t >= start:
            i = int((t - start) / step)
            if 0 <= i < n:
                out[i].append(r)
    return out


def _metric(rows, metric):
    if metric == "duration":
        vals = [r.get("duration") or 0 for r in rows]
        return sum(vals) / len(vals) if vals else 0
    if metric in ("bytes", "copied", "deleted", "errors"):
        return sum(r.get(metric) or 0 for r in rows)
    return len(rows)


def _mtext(v, metric):
    if metric == "bytes":
        return human_size(v)
    if metric == "duration":
        return human_dur(v)
    return str(int(round(v)))


def _line_points(vals, mx, w=300.0, h=100.0, pad=6.0):
    n = len(vals)
    xs = [w * i / (n - 1) if n > 1 else w / 2 for i in range(n)]
    return " ".join(f"{x:.1f},{h - pad - (h - 2 * pad) * (v / mx if mx else 0):.1f}" for x, v in zip(xs, vals))


def _state_key(src, r):
    return r.get(SOURCES[src].get("status") or "status") or ""


def _color(key, n):
    c = PIE_STATUS.get(key)
    return (c, n) if c else (PIE_COLORS[n % len(PIE_COLORS)], n + 1)


def _time_view(src, view, rows, filters, tr, status_text):
    spec, now = SOURCES[src], datetime.datetime.now()
    tkey = spec.get("time")
    days = _window(view, filters)
    metric = filters.get("metric") if src == "runs" else ""
    metric = metric or "count"
    mlabel = tr(dict(METRICS).get(metric)) if src == "runs" else tr(spec.get("noun", ""))
    if view == "timeline":
        return _timeline(rows, days, now, tr, status_text)
    if view == "heatmap":
        return _heatmap(src, rows, max(days, 7), now, tr, status_text)
    start, step, n, labels = _buckets(days, now)
    groups = _bucketize(rows, tkey, start, step, n)
    hourly = days <= 1
    if view == "spark":
        inside = [r for g in groups for r in g]
        vals = [_metric(g, metric) for g in groups]
        return {"value": _mtext(_metric(inside, metric), metric), "label": mlabel, "points": _line_points(vals, max(vals + [0])),
                "range": f"{labels[0]} – {labels[-1]}" if not hourly else tr("letzte 24 Stunden")}
    if view == "line":
        series = []
        sel = filters.get("jobs") or []
        if src == "runs" and 2 <= len(sel) <= 8:   # mehrere Aufgaben gewaehlt: je Aufgabe eine Linie
            names = {}
            for r in rows:
                names.setdefault(r.get("id"), r.get("name", ""))
            for i, jid in enumerate(j for j in sel if j in names):
                series.append({"label": names[jid], "vals": [_metric([r for r in g if r.get("id") == jid], metric) for g in groups],
                               "color": PIE_COLORS[i % len(PIE_COLORS)]})
        if not series:
            series = [{"label": mlabel, "vals": [_metric(g, metric) for g in groups], "color": "var(--acc)"}]
        mx = max([v for s in series for v in s["vals"]] + [0])
        for s in series:
            s["points"] = _line_points(s["vals"], mx)
            s["total"] = _mtext(_metric([r for g in groups for r in g if len(series) == 1 or r.get("name") == s["label"]], metric), metric)
        cols = [{"label": labels[i], "text": " · ".join(f"{s['label']}: {_mtext(s['vals'][i], metric)}" for s in series)} for i in range(n)]
        for s in series:
            del s["vals"]
        if len(series) == 1:
            series[0]["area"] = "0,100 " + series[0]["points"] + " 300,100"
        return {"series": series, "cols": cols, "max_text": _mtext(mx, metric), "metric": mlabel,
                "first": labels[0], "mid": labels[n // 2], "last": labels[-1], "empty": not any(groups)}
    # stacked: je Abschnitt ein Balken, aufgeteilt nach Status
    keys, order = {}, []
    for g in groups:
        for r in g:
            k = _state_key(src, r)
            if k not in keys:
                keys[k] = 0
                order.append(k)
            keys[k] += 1
    pref = ["ok", "gestoppt", "paused", "fehler", "fail"]
    order.sort(key=lambda k: (pref.index(k) if k in pref else 9, -keys[k]))
    colors, ci = {}, 0
    for k in order:
        colors[k], ci = _color(k, ci)
    label = (lambda k: status_text(k)) if SOURCES[src].get("status") == "status" else (lambda k: k)
    mx = max([len(g) for g in groups] + [1])
    bars = []
    for i, g in enumerate(groups):
        cnt = {}
        for r in g:
            k = _state_key(src, r)
            cnt[k] = cnt.get(k, 0) + 1
        segs = [{"color": colors[k], "pct": round(100 * cnt[k] / len(g), 2), "n": cnt[k]} for k in order if cnt.get(k)]
        bars.append({"label": labels[i], "h": round(100 * len(g) / mx, 2), "total": len(g), "segs": segs,
                     "title": f"{labels[i]}: " + ", ".join(f"{label(k)} {cnt[k]}" for k in order if cnt.get(k)) if g else f"{labels[i]}: 0",
                     "tick": i == 0 or i == n - 1 or (n > 1 and i % max(1, math.ceil(n / 6)) == 0 and n - 1 - i >= math.ceil(n / 12))})
    return {"bars": bars, "legend": [{"label": label(k), "color": colors[k], "n": keys[k]} for k in order], "max_text": str(mx),
            "empty": not any(groups)}


def _heatmap(src, rows, days, now, tr, status_text):
    start, step, n, _ = _buckets(days, now)
    groups = _bucketize(rows, SOURCES[src]["time"], start, step, n)
    mx = max([len(g) for g in groups] + [1])
    lead = start.weekday()   # Spalten = Wochen ab Montag
    cells = [{"empty": True} for _ in range(lead)]
    for i, g in enumerate(groups):
        day = start + datetime.timedelta(days=i)
        states = {_state_key(src, r) for r in g}
        st = "fehler" if states & {"fehler", "fail"} else "warn" if "gestoppt" in states else ("ok" if src != "audit" else "info") if g else "none"
        level = 0 if not g else min(4, 1 + int(3 * len(g) / mx))
        bad = sum(1 for r in g if _state_key(src, r) in ("fehler", "fail"))
        cells.append({"state": st, "level": level, "date": day.strftime("%d.%m.%Y"), "n": len(g), "bad": bad,
                      "month": day.strftime("%m") if day.day <= 7 and day.weekday() == 0 else ""})
    weeks = math.ceil(len(cells) / 7)
    return {"cells": cells, "weeks": weeks, "noun": tr(SOURCES[src].get("noun", "")), "bad_label": tr("davon Fehler"),
            "legend": [{"cls": "ok", "label": status_text("ok")}, {"cls": "warn", "label": status_text("gestoppt")},
                       {"cls": "fehler", "label": status_text("fehler")}] if src != "audit" else
                      [{"cls": "info", "label": tr("mehr Einträge = kräftigere Farbe")}],
            "total": sum(len(g) for g in groups)}


def _timeline(rows, days, now, tr, status_text):
    t0 = now - datetime.timedelta(days=days)
    span = (now - t0).total_seconds()
    runs = []
    for r in rows:
        s = _ts(r.get("start"))
        if not s:
            continue
        e = s + datetime.timedelta(seconds=r.get("duration") or 0)
        if e < t0:
            continue
        runs.append((s, e, r))
    lanes, order = {}, []
    for s, e, r in sorted(runs, key=lambda x: x[0]):
        key = r.get("id") or r.get("name")
        if key not in lanes:
            lanes[key] = {"name": r.get("name", ""), "link": f"/job/{r.get('id')}/log" if r.get("id") else "", "bars": []}
            order.append(key)
        lanes[key]["bars"].append((s, e, r))
    overlaps, raw = 0, {k: list(lanes[k]["bars"]) for k in order}
    for key in order:
        out = []
        for s, e, r in lanes[key]["bars"]:
            ov = any(o_s < e and s < o_e for k2 in order if k2 != key for o_s, o_e, _ in raw[k2])
            overlaps += ov
            left = max(0.0, (s - t0).total_seconds() / span * 100)
            width = max(0.6, min(100 - left, ((e - max(s, t0)).total_seconds()) / span * 100))
            out.append({"left": round(left, 2), "width": round(width, 2), "status": r.get("status"), "overlap": ov,
                        "color": PIE_STATUS.get(r.get("status"), "var(--acc)"), "link": r.get("link", ""),
                        "title": f"{r.get('name', '')}: {s:%d.%m. %H:%M:%S} – {e:%H:%M:%S} ({human_dur(r.get('duration'))}) · {r.get('status_text', '')}"
                                 + (" · " + tr("überschneidet sich mit einer anderen Aufgabe") if ov else "")})
        lanes[key]["bars"] = out
    ticks = []
    if days <= 1:
        first = (t0 + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        for h in range(0, 24, 3):
            t = first + datetime.timedelta(hours=h)
            if t < now:
                ticks.append({"left": round((t - t0).total_seconds() / span * 100, 2), "label": t.strftime("%H:%M")})
    else:
        stepd = max(1, math.ceil(days / 7))
        first = (t0 + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        t = first
        while t < now:
            ticks.append({"left": round((t - t0).total_seconds() / span * 100, 2), "label": t.strftime("%d.%m.")})
            t += datetime.timedelta(days=stepd)
    return {"lanes": [lanes[k] for k in sorted(order, key=lambda k: lanes[k]["name"].lower())], "ticks": ticks, "overlaps": overlaps,
            "overlap_text": tr("Überschneidungen"), "empty": not runs}


def _gauge(title, pct, sub, good_high=True):
    pct = max(0, min(100, int(round(pct))))
    if good_high:
        cls = "ok" if pct >= 95 else "warn" if pct >= 80 else "fehler"
    else:
        cls = "fehler" if pct >= 95 else "warn" if pct >= 85 else "ok"
    return {"title": title, "pct": pct, "text": f"{pct} %", "sub": sub, "cls": cls}


def _gauges(src, rows, tr):
    if src == "storage":
        return [_gauge(r["label"], r["pct"], f"{tr('belegt')} {r.get('used_text', '')} · {tr('frei')} {r.get('free_text', '')}", False)
                for r in rows if r.get("pct") is not None and not r.get("same")]
    if src == "jobs":
        rel = [r for r in rows if r.get("status") not in ("off", "never")]
        good = sum(1 for r in rel if r.get("status") != "fehler")
        return [_gauge(tr("ohne Fehler"), 100 * good / len(rel), f"{good} / {len(rel)} {tr('Aufgaben')}")] if rel else []
    if src == "logins":
        good = sum(1 for r in rows if r.get("status") == "ok")
        return [_gauge(tr("Erfolgsquote"), 100 * good / len(rows), f"{good} / {len(rows)} {tr('Anmeldungen')}")] if rows else []
    done = [r for r in rows if r.get("status") in ("ok", "fehler", "gestoppt")]
    good = sum(1 for r in done if r.get("status") == "ok")
    return [_gauge(tr("Erfolgsquote"), 100 * good / len(done), f"{good} / {len(done)} {tr('Läufe')}")] if done else []
