"""Uebertragungs-Statistik pro Monat, Health-Status (/health/jobs) und Prometheus-Metriken (/metrics).

Die Statistik liegt im DB-Bereich "stats" (Schluessel = Monat JJJJ-MM) und wird nach jedem Lauf fortgeschrieben. Sie ist
unabhaengig vom Verlauf der Aufgaben, der nach der Log-Aufbewahrung gekuerzt wird."""
import datetime
import threading
import time

core = None
_lock = threading.RLock()
FIELDS = ("runs", "ok", "fail", "stopped", "dry", "bytes", "copied", "deleted", "duration", "verify_ok", "verify_fail")


def init(core_module):
    global core
    core = core_module


# ---------------------------------------------------------------- Statistik
def month_of(start):
    return (start or time.strftime("%Y-%m-%d"))[:7]


def add_run(job_id, name, entry):
    """Einen Lauf (Eintrag aus dem Verlauf) in die Monatsstatistik uebernehmen."""
    m = month_of(entry.get("start"))
    with _lock:
        data = core.DB.get("stats", m) or {"jobs": {}}
        js = data.setdefault("jobs", {}).setdefault(job_id, {k: 0 for k in FIELDS})
        js["name"] = name
        for k in FIELDS:
            js.setdefault(k, 0)
        js["runs"] += 1
        st = entry.get("status")
        if entry.get("dry_run"):
            js["dry"] += 1
        if st == "ok":
            js["ok"] += 1
        elif st in ("gestoppt", "freigabe"):
            js["stopped"] += 1
        else:
            js["fail"] += 1
        if not entry.get("dry_run"):
            js["bytes"] += int(entry.get("bytes") or 0)
            js["copied"] += int(entry.get("copied") or 0)
            js["deleted"] += int(entry.get("deleted") or 0)
        js["duration"] += int(entry.get("duration") or 0)
        v = entry.get("verify") or {}
        if v.get("result") == "ok":
            js["verify_ok"] += 1
        elif v.get("result") in ("diff", "error"):
            js["verify_fail"] += 1
        core.DB.put("stats", m, data)
    return m


def backfill():
    """Einmalig: bestehenden Verlauf aller Aufgaben in die Statistik uebernehmen (Update auf 1.52.0)."""
    if core.DB.meta("stats_backfilled"):
        return 0
    n = 0
    for jid, j in core.load_jobs().items():
        for h in reversed(j.get("history", [])):
            if h.get("mode") == "verify":
                continue
            add_run(jid, j.get("name", jid), h)
            n += 1
    core.DB.set_meta("stats_backfilled", time.strftime("%Y-%m-%d %H:%M:%S"))
    return n


def months(limit=24, visible=None):
    """[{month, totals, jobs:[...]}] neueste zuerst. visible(jid) filtert Aufgaben."""
    out = []
    data = core.DB.get_map("stats")
    for m in sorted(data, reverse=True)[:limit]:
        jobs = []
        tot = {k: 0 for k in FIELDS}
        for jid, js in (data[m].get("jobs") or {}).items():
            if visible and not visible(jid):
                continue
            row = dict({k: int(js.get(k) or 0) for k in FIELDS}, id=jid, name=js.get("name") or jid)
            jobs.append(row)
            for k in FIELDS:
                tot[k] += row[k]
        jobs.sort(key=lambda r: -r["bytes"])
        out.append({"month": m, "totals": tot, "jobs": jobs})
    return out


def month_bytes(m=None):
    m = m or time.strftime("%Y-%m")
    data = core.DB.get("stats", m) or {}
    return sum(int(j.get("bytes") or 0) for j in (data.get("jobs") or {}).values())


def volume_state(settings=None):
    """Datenvolumen dieses Monats gegen das Limit. None, wenn kein Limit eingestellt ist."""
    s = settings or core.load_settings()
    try:
        limit_gb = float(str(s.get("volume_limit_gb") or "0").replace(",", "."))
    except ValueError:
        limit_gb = 0
    if limit_gb <= 0:
        return None
    used = month_bytes()
    limit = int(limit_gb * 1024 ** 3)
    try:
        warn = max(1, min(100, int(s.get("volume_warn_pct") or 80)))
    except ValueError:
        warn = 80
    pct = used * 100 / limit if limit else 0
    return {"month": time.strftime("%Y-%m"), "used": used, "limit": limit, "limit_gb": limit_gb, "pct": round(pct, 1),
            "warn_pct": warn, "warn": pct >= warn, "exceeded": pct >= 100, "stop": bool(s.get("volume_stop"))}


# ---------------------------------------------------------------- Health
def _ago_text(minutes):
    t = core.i18n.t
    if minutes is None:
        return t("noch nie")
    if minutes < 1:
        return t("gerade eben")
    if minutes < 120:
        return t("vor {0} Minuten", minutes) if minutes != 1 else t("vor 1 Minute")
    h = minutes // 60
    if h < 48:
        return t("vor {0} Stunden", h)
    return t("vor {0} Tagen", h // 24)


def _period_minutes(job):
    """Abstand zwischen zwei geplanten Starts in Minuten (Zeitplan bzw. Live), sonst None."""
    trig = core.trigger_of(job)
    if trig == "time" and job.get("schedule", "").strip():
        try:
            ct = core.CronTrigger.from_crontab(job["schedule"], timezone=core.TZ)
            now = datetime.datetime.now(ct.timezone)
            a = ct.get_next_fire_time(None, now)
            b = ct.get_next_fire_time(a, a + datetime.timedelta(seconds=1)) if a else None
            if a and b:
                return max(1, int((b - a).total_seconds() // 60))
        except Exception:  # noqa: BLE001
            return None
    if trig == "live":
        return core.live_interval(job)
    return None


def _ts(text):
    try:
        return time.mktime(time.strptime(text[:19], "%Y-%m-%d %H:%M:%S"))
    except (TypeError, ValueError):
        return None


def job_health(jid, j, now=None):
    now = now or time.time()
    hist = [h for h in j.get("history", []) if not h.get("dry_run") and h.get("mode") != "verify"]
    last = hist[0] if hist else None
    last_ts = _ts(last["start"]) if last else None
    if core.trigger_of(j) == "live" and j.get("live_checked"):
        lc = _ts(j["live_checked"])
        if lc and (not last_ts or lc > last_ts):
            last_ts = lc   # ruhige Live-Runden ohne Aenderung stehen nicht im Verlauf
    minutes = int((now - last_ts) // 60) if last_ts else None
    try:
        max_age = int(float(str(j.get("health_max_age") or "0").replace(",", ".")) * 60)
    except ValueError:
        max_age = 0
    if not max_age:
        per = _period_minutes(j)
        if per:
            max_age = per * 2 + 60 if core.trigger_of(j) == "time" else per * 3 + 15
    active = bool(j.get("enabled")) and not core.is_paused(j)
    running = jid in core._running
    overdue = bool(active and max_age and not running and (minutes is None or minutes > max_age)
                   and not j.get("window_wait"))
    last_status = (last or {}).get("status")
    v = j.get("last_verify") or {}
    mismatch = v.get("result") == "diff" and (not last or (v.get("at") or "") >= (last.get("start") or ""))
    status = "ok"
    if running:
        status = "running"
    if j.get("delete_hold"):
        status = "hold"
    elif last_status in ("fehler", "abgebrochen") and not running:
        status = "error"
    elif mismatch and not running:
        status = "mismatch"
    elif overdue:
        status = "overdue"
    elif last is None and not running:
        status = "never"
    if not active and status not in ("hold",):
        status = "inactive" if status in ("ok", "never", "overdue") else status
    return {"id": jid, "name": j.get("name", jid), "status": status, "ok": status in ("ok", "running", "inactive", "never"),
            "active": active, "running": running, "last_status": last_status, "last_run": (last or {}).get("start"),
            "minutes_ago": minutes, "ago": _ago_text(minutes), "max_age_minutes": max_age or None, "overdue": overdue,
            "delete_hold": bool(j.get("delete_hold")), "retry_pending": bool(j.get("retry_pending")),
            "last_bytes": (last or {}).get("bytes"), "last_duration": (last or {}).get("duration"),
            "verify": v.get("result"), "verify_at": v.get("at")}


STATUS_TEXT = {"ok": "letzter Sync ok", "running": "läuft gerade", "error": "letzter Sync fehlgeschlagen",
               "overdue": "überfällig", "hold": "wartet auf Freigabe (Löschwarnung)", "never": "noch nie gelaufen",
               "inactive": "ausgeschaltet oder pausiert",
               "mismatch": "Prüfung: Quelle und Ziel weichen ab"}


def health(visible=None, only=None):
    t = core.i18n.t
    rows = []
    for jid, j in sorted(core.load_jobs().items(), key=lambda kv: kv[1].get("name", "").lower()):
        if visible and not visible(jid, j):
            continue
        if only and only not in (jid, j.get("name")):
            continue
        rows.append(job_health(jid, j))
    for r in rows:
        r["text"] = f"{r['name']}: {t(STATUS_TEXT[r['status']])}, {r['ago']}"
    bad = [r for r in rows if r["active"] and not r["ok"]]
    active = [r for r in rows if r["active"]]
    newest = min((r["minutes_ago"] for r in active if r["minutes_ago"] is not None), default=None)
    if only and not rows:
        summary, ok = t("Aufgabe {0} nicht gefunden.", only), False
    elif bad:
        summary, ok = "; ".join(r["text"] for r in bad), False
    elif only:
        summary, ok = rows[0]["text"], True
    else:
        summary = t("{0} Aufgaben ok, letzter Sync {1}", len(active), _ago_text(newest)) if active else t("keine aktiven Aufgaben")
        ok = True
    vol = volume_state()
    return {"status": "ok" if ok else "error", "ok": ok, "summary": summary, "version": core.VERSION,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"), "jobs": rows,
            "volume": {k: vol[k] for k in ("used", "limit", "pct", "exceeded")} if vol else None}


# ---------------------------------------------------------------- Prometheus
def _esc(v):
    return str(v).replace("\\", "\\\\").replace("\n", " ").replace('"', '\\"')


def metrics(visible=None):
    lines = []

    def m(name, help_, typ, samples):
        lines.append(f"# HELP {name} {help_}")
        lines.append(f"# TYPE {name} {typ}")
        for labels, val in samples:
            lab = ",".join(f'{k}="{_esc(v)}"' for k, v in labels.items())
            lines.append(f"{name}{{{lab}}} {val}" if lab else f"{name} {val}")
    jobs = {jid: j for jid, j in core.load_jobs().items() if not visible or visible(jid, j)}
    m("mirrorsync_info", "MirrorSync version", "gauge", [({"version": core.VERSION}, 1)])
    m("mirrorsync_up", "MirrorSync is running", "gauge", [({}, 1)])
    hl = {jid: job_health(jid, j) for jid, j in jobs.items()}
    L = lambda jid: {"job_id": jid, "job": jobs[jid].get("name", jid)}
    m("mirrorsync_job_running", "1 while the job is running", "gauge", [(L(j), int(h["running"])) for j, h in hl.items()])
    m("mirrorsync_job_enabled", "1 if the job runs automatically (enabled and not paused)", "gauge",
      [(L(j), int(h["active"])) for j, h in hl.items()])
    m("mirrorsync_job_last_success", "1 if the last run was successful", "gauge",
      [(L(j), int(h["last_status"] == "ok")) for j, h in hl.items() if h["last_status"]])
    m("mirrorsync_job_healthy", "1 if the job is healthy (last run ok and not overdue)", "gauge",
      [(L(j), int(h["ok"])) for j, h in hl.items()])
    m("mirrorsync_job_overdue", "1 if the job has not run in time", "gauge", [(L(j), int(h["overdue"])) for j, h in hl.items()])
    m("mirrorsync_job_delete_hold", "1 if the job waits for approval because of many deletions", "gauge",
      [(L(j), int(h["delete_hold"])) for j, h in hl.items()])
    m("mirrorsync_job_last_run_timestamp_seconds", "Start of the last real run (unix time)", "gauge",
      [(L(j), int(_ts(h["last_run"]) or 0)) for j, h in hl.items() if h["last_run"]])
    m("mirrorsync_job_last_duration_seconds", "Duration of the last real run", "gauge",
      [(L(j), int(h["last_duration"] or 0)) for j, h in hl.items() if h["last_run"]])
    m("mirrorsync_job_last_transferred_bytes", "Bytes transferred by the last real run", "gauge",
      [(L(j), int(h["last_bytes"] or 0)) for j, h in hl.items() if h["last_run"]])
    m("mirrorsync_job_verify_ok", "1 if the last verification found source and destination identical", "gauge",
      [(L(j), int(h["verify"] == "ok")) for j, h in hl.items() if h["verify"]])
    free = []
    for jid, j in jobs.items():
        d = j.get("dest_space") or {}
        if d.get("free") is not None:
            free.append((L(jid), int(d["free"])))
    m("mirrorsync_job_destination_free_bytes", "Free space at the destination (last check)", "gauge", free)
    data = core.DB.get_map("stats")
    tot = {}
    for mo in data.values():
        for jid, js in (mo.get("jobs") or {}).items():
            if jid not in jobs:
                continue
            t = tot.setdefault(jid, {k: 0 for k in FIELDS})
            for k in FIELDS:
                t[k] += int(js.get(k) or 0)
    m("mirrorsync_job_runs_total", "Runs by result", "counter",
      [(dict(L(j), result=r), t[k]) for j, t in tot.items() for r, k in (("ok", "ok"), ("error", "fail"), ("stopped", "stopped"))])
    m("mirrorsync_job_transferred_bytes_total", "Bytes transferred (real runs)", "counter", [(L(j), t["bytes"]) for j, t in tot.items()])
    m("mirrorsync_job_files_copied_total", "Files copied or updated", "counter", [(L(j), t["copied"]) for j, t in tot.items()])
    m("mirrorsync_job_files_deleted_total", "Files deleted at the destination", "counter", [(L(j), t["deleted"]) for j, t in tot.items()])
    m("mirrorsync_job_duration_seconds_total", "Total run time", "counter", [(L(j), t["duration"]) for j, t in tot.items()])
    mo = time.strftime("%Y-%m")
    m("mirrorsync_month_transferred_bytes", "Bytes transferred in the current month (all jobs)", "gauge",
      [({"month": mo}, month_bytes(mo))])
    vol = volume_state()
    if vol:
        m("mirrorsync_month_volume_limit_bytes", "Monthly data volume limit", "gauge", [({"month": mo}, vol["limit"])])
    return "\n".join(lines) + "\n"
