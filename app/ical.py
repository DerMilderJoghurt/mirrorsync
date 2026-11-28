"""Kalender-Export (iCal) der geplanten Laeufe (seit 1.58.0).

Feste Zeitplaene (Cron) werden fuer die naechsten Tage ausgerechnet. Folgeaufgaben einer Kette erscheinen geschaetzt
nach ihrem Vorgaenger (Dauer = Mittel der letzten erfolgreichen Laeufe). Live-Aufgaben und manuelle Aufgaben fehlen,
pausierte Zeitraeume und der Wartungsmodus werden ausgelassen. Abo-Adresse: /calendar/<token>.ics (Token pro Benutzer)."""
import datetime
import hashlib

core = None
MAX_EVENTS = 3000
MAX_PER_JOB = 400


def _esc(t):
    return str(t or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r\n", "\\n").replace("\n", "\\n")


def _fold(line):
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > (75 if not out else 74):
            out.append(cur.decode("utf-8"))
            cur = b""
        cur += b
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)


def _utc(d):
    if d.tzinfo is None:
        d = d.replace(tzinfo=core.TZINFO)
    return d.astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def avg_minutes(job):
    ds = [h.get("duration") for h in job.get("history", [])[:10] if h.get("status") == "ok" and isinstance(h.get("duration"), (int, float))
          and h.get("mode") != "verify"]
    m = (sum(ds) / len(ds) / 60) if ds else 0
    return max(5, int(round(m)))


def _blocked(job, t, maint_until):
    if job.get("paused") and core.is_paused(job):
        until = (job.get("paused_until") or "").strip()
        if not until or t.strftime("%Y-%m-%dT%H:%M") < until:
            return True
    if maint_until is not None and (maint_until == "" or t.strftime("%Y-%m-%dT%H:%M") < maint_until):
        return True
    return False


def events(jobs, days=14, now=None, visible=None):
    """[(start datetime, minuten, jid, job, art)] art: time | after."""
    from apscheduler.triggers.cron import CronTrigger
    now = now or datetime.datetime.now(core.TZINFO)
    end = now + datetime.timedelta(days=days)
    m = core.maintenance_state()
    maint_until = None if not m else (m.get("until") or "")
    vis = {jid: j for jid, j in jobs.items() if not visible or visible(jid, j)}
    out = []
    starts = {}
    for jid, j in vis.items():
        if core.trigger_of(j) != "time" or not j.get("enabled") or not j.get("schedule"):
            continue
        try:
            trig = CronTrigger.from_crontab(j["schedule"], timezone=core.TZ)
        except ValueError:
            continue
        prev, t, n = None, trig.get_next_fire_time(None, now), 0
        while t and t <= end and n < MAX_PER_JOB:
            if not _blocked(j, t, maint_until):
                out.append((t, avg_minutes(j), jid, j, "time"))
                starts.setdefault(jid, []).append(t)
            n += 1
            prev, t = t, trig.get_next_fire_time(t, t + datetime.timedelta(seconds=1))
    # Folgeaufgaben: geschaetzt nach dem Vorgaenger (bis 5 Ebenen)
    for _ in range(5):
        added = False
        for jid, j in vis.items():
            if core.trigger_of(j) != "after" or not j.get("enabled") or jid in starts:
                continue
            parent = j.get("after_job")
            if parent not in starts or parent not in jobs:
                continue
            mins = avg_minutes(jobs[parent])
            lst = []
            for t in starts[parent]:
                st = t + datetime.timedelta(minutes=mins)
                if not core.is_paused(j):
                    out.append((st, avg_minutes(j), jid, j, "after"))
                    lst.append(st)
            starts[jid] = lst
            added = True
        if not added:
            break
    out.sort(key=lambda x: x[0])
    return out[:MAX_EVENTS]


def build(jobs, days=14, visible=None, name="MirrorSync"):
    base = (core.load_settings().get("public_url") or "").strip().rstrip("/")
    stamp = _utc(datetime.datetime.now(core.TZINFO))
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MirrorSync//Kalender//DE", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "X-WR-CALNAME:" + _esc(name), "X-WR-TIMEZONE:" + core.TZ, "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
             "X-PUBLISHED-TTL:PT1H"]
    t = lambda x, *a: core.i18n.t(x, *a, lang=core.i18n.default_lang)
    for start, mins, jid, j, kind in events(jobs, days, visible=visible):
        uid = hashlib.sha1(f"{jid}|{start.isoformat()}".encode()).hexdigest()[:20] + "@mirrorsync"
        title = "MirrorSync: " + j.get("name", jid) + (" (" + t("Testlauf") + ")" if j.get("dry_run") else "")
        if kind == "after":
            parent = jobs.get(j.get("after_job"), {}).get("name", "")
            title += " (" + t("geschätzt, nach „{0}“", parent) + ")"
        desc = [f"{j.get('source', '')} {'⇄' if core.is_bisync(j) else '→'} {core.effective_dest(j)}",
                t("Dauer geschätzt: {0} Minuten", mins)]
        if j.get("note"):
            desc.append(j["note"])
        if base:
            desc.append(base + f"/job/{jid}/log")
        ev = ["BEGIN:VEVENT", "UID:" + uid, "DTSTAMP:" + stamp, "DTSTART:" + _utc(start),
              "DTEND:" + _utc(start + datetime.timedelta(minutes=mins)), "SUMMARY:" + _esc(title), "DESCRIPTION:" + _esc("\n".join(desc)),
              "TRANSP:TRANSPARENT"]
        tags = core.job_tags(j)
        if tags:
            ev.append("CATEGORIES:" + ",".join(_esc(x) for x in tags))
        if base:
            ev.append("URL:" + base + f"/job/{jid}/log")
        ev.append("END:VEVENT")
        lines += ev
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(x) for x in lines) + "\r\n"
