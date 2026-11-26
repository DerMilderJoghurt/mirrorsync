"""REST-API (/api/v1), OpenAPI/Swagger (/api/docs), MCP-Server (/mcp) und API-Keys.

Ein API-Key hat einen Namen und eine Rolle (dieselben Rechte und Beschraenkungen wie bei Benutzern), optional
ein Ablaufdatum und erlaubte IP-Adressen. Gespeichert wird nur ein SHA-256-Hash. Alle Aktionen laufen ueber
dieselben Funktionen wie die Web-GUI und landen im Audit-Log unter "API:<Name>"."""
import datetime
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import threading
import time

from flask import g, jsonify, request, session

core = None          # das app-Modul, wird in register() gesetzt
PREFIX = "msk_"
RATE_PER_MIN = 300
_rate = {}           # key_id -> [fenster_start, anzahl]
_rate_lock = threading.Lock()
MCP_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")


class ApiError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status, self.msg = status, msg


# ---------------------------------------------------------------- Keys
def keys():
    return core.DB.get_map("apikey")


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _seal_key():
    """Schluessel fuer die verschluesselte Ablage der API-Keys, abgeleitet aus config/secret_key.
    secret_key ist nicht im Export, ein Export allein verraet die Keys also nicht."""
    return hashlib.sha256(("mirrorsync-apikey-v1|" + str(core.app.secret_key)).encode()).digest()


def seal(token):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except Exception:   # ohne cryptography: nur Hash, Key spaeter nicht anzeigbar
        return ""
    import base64
    nonce = secrets.token_bytes(12)
    return base64.b64encode(nonce + AESGCM(_seal_key()).encrypt(nonce, token.encode(), b"apikey")).decode()


def unseal(blob):
    """Klartext-Key oder None (fehlt, andere Installation, beschaedigt)."""
    if not blob:
        return None
    try:
        import base64
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        raw = base64.b64decode(blob)
        return AESGCM(_seal_key()).decrypt(raw[:12], raw[12:], b"apikey").decode()
    except Exception:
        return None


def create_key(name, role, expires="", ips=None, by="", lang=""):
    kid = secrets.token_hex(4)
    token = f"{PREFIX}{kid}_{secrets.token_urlsafe(32)}"
    entry = {"name": name, "role": role, "hash": _hash(token), "enc": seal(token), "expires": expires, "ips": ips or [],
             "created": time.strftime("%Y-%m-%d %H:%M"), "created_by": by, "last_used": "", "last_ip": "",
             "uses": 0, "revoked": False, "lang": lang if core.i18n.valid(lang or "") else ""}
    core.DB.put("apikey", kid, entry)
    return kid, token, entry


def parse_ips(text):
    """'192.168.1.0/24, 10.0.0.7' -> Liste. Wirft ValueError bei ungueltigem Eintrag."""
    out = []
    for part in re.split(r"[\s,;]+", text or ""):
        if part:
            out.append(str(ipaddress.ip_network(part, strict=False)))
    return out


def _ip_ok(ip, nets):
    if not nets:
        return True
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(a in ipaddress.ip_network(n, strict=False) for n in nets)


def key_status(k, now=None):
    """aktiv | widerrufen | abgelaufen | deaktiviert | pausiert (Sperrzeitraum) | außerhalb der Zeiten (Zeitfenster)."""
    if k.get("revoked"):
        return "widerrufen"
    if k.get("expires") and k["expires"] < datetime.date.today().isoformat():
        return "abgelaufen"
    if k.get("disabled"):
        return "deaktiviert"
    now = now or datetime.datetime.now()
    stamp = now.strftime("%Y-%m-%dT%H:%M")
    lf, lu = k.get("lock_from") or "", k.get("lock_until") or ""
    if (lf or lu) and (not lf or lf <= stamp) and (not lu or stamp < lu):
        return "pausiert"
    wins = k.get("windows") or []
    if wins and not any(_in_window(w, now) for w in wins):
        return "außerhalb der Zeiten"
    return "aktiv"


def windows_text(wins):
    dd = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    out = []
    for w in wins or []:
        d = w.get("days") or []
        txt = "Mo–Fr" if d == [0, 1, 2, 3, 4] else "täglich" if d == list(range(7)) else "Sa–So" if d == [5, 6] else ", ".join(dd[i] for i in d)
        out.append(core.i18n.t(txt) if txt in ("Mo–Fr", "täglich", "Sa–So") else ", ".join(core.i18n.t(dd[i]) for i in d))
        out[-1] += f" {w.get('start')}–{w.get('end')}"
    return "; ".join(out)


def _in_window(w, now):
    """w = {days:[0-6], start:"HH:MM", end:"HH:MM"}; Ende vor Beginn = ueber Mitternacht."""
    t = now.strftime("%H:%M")
    s, e = w.get("start") or "00:00", w.get("end") or "24:00"
    days = w.get("days") or []
    if s < e:
        return now.weekday() in days and s <= t < e
    # ueber Mitternacht: Teil vor Mitternacht am Tag selbst, Rest am Folgetag
    return (now.weekday() in days and t >= s) or (((now.weekday() - 1) % 7) in days and t < e)


def clean_windows(raw):
    """Liste von Zeitfenstern pruefen. Liefert (liste, fehler)."""
    out = []
    for i, w in enumerate(raw or [], 1):
        if not isinstance(w, dict):
            return [], core.i18n.t("Zeitfenster {0}: ungültig.", i)
        try:
            days = sorted({int(d) for d in w.get("days") or [] if 0 <= int(d) <= 6})
        except (TypeError, ValueError):
            return [], core.i18n.t("Zeitfenster {0}: ungültig.", i)
        s, e = str(w.get("start") or "").strip(), str(w.get("end") or "").strip()
        if not days and not s and not e:
            continue
        if not days:
            return [], core.i18n.t("Zeitfenster {0}: bitte mindestens einen Wochentag wählen.", i)
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", s) or not re.match(r"^([01]\d|2[0-3]):[0-5]\d$|^24:00$", e) or s == e:
            return [], core.i18n.t("Zeitfenster {0}: Uhrzeiten von–bis im Format HH:MM, verschieden.", i)
        out.append({"days": days, "start": s, "end": e})
    return out[:10], None


def _deny(status, msg):
    resp = jsonify({"error": msg})
    resp.status_code = status
    if status == 401:
        resp.headers["WWW-Authenticate"] = 'Bearer realm="MirrorSync"'
    return resp


def owner_lang(k, depth=0):
    """Sprache des Benutzers, dem der Key gehoert (created_by; bei 'API:<Key>' dessen Besitzer).
    Leer = Benutzer nutzt die Systemsprache, None = kein Besitzer bekannt."""
    by = (k or {}).get("created_by") or ""
    if by.startswith("API:") and depth < 3:
        parent = next((x for x in keys().values() if x.get("name") == by[4:]), None)
        return owner_lang(parent, depth + 1) if parent else None
    u = core.store.get(by) if by else None
    return (u.get("lang") or "") if u else None


def key_lang(k):
    """Sprache der API-Antworten fuer diesen Key: eigene Einstellung, sonst wie der Besitzer, sonst Englisch."""
    if core.i18n.valid((k or {}).get("lang") or ""):
        return k["lang"]
    o = owner_lang(k)
    return "en" if o is None else (o or core.i18n.default_lang)


def authenticate():
    """before_request fuer /api/v1 und /mcp. Setzt g.user, g.role, g.access."""
    # Sprache der Antworttexte: ?lang=xx, sonst Accept-Language, sonst Sprache des Keys/Benutzers, sonst Englisch
    want = request.args.get("lang", "")
    explicit = want if core.i18n.valid(want) else ""
    header = core.i18n.from_header(request.headers.get("Accept-Language")) or ""
    g.user_lang = explicit or header or "en"
    h = request.headers.get("Authorization", "")
    token = h[7:].strip() if h.lower().startswith("bearer ") else request.headers.get("X-API-Key", "").strip()
    if not token:
        # Swagger-UI im Browser: angemeldete GUI-Sitzung genuegt (nicht fuer MCP)
        name, u = core.current_user()
        if name and not request.path.startswith("/mcp"):
            g.user, g.role = name, u["role"]
            g.user_lang = explicit or u.get("lang") or core.i18n.default_lang
            g.access = core.make_access(name, u["role"])
            g.api_key = None
            return None
        return _deny(401, core.i18n.t("API-Key fehlt. Header: Authorization: Bearer msk_…"))
    if core._locked():
        return _deny(429, core.i18n.t("Zu viele fehlgeschlagene Versuche von dieser IP-Adresse. Bitte 5 Minuten warten."))
    m = re.match(r"^msk_([0-9a-f]{8})_[A-Za-z0-9_-]{20,}$", token)
    k = core.DB.get("apikey", m.group(1)) if m else None
    if not k or not hmac.compare_digest(k.get("hash", ""), _hash(token)):
        core._fail()
        core._record_login("API", False, "API-Key ungültig")
        return _deny(401, core.i18n.t("API-Key ungültig."))
    kid = m.group(1)
    g.user_lang = explicit or header or key_lang(k)
    st = key_status(k)
    if st != "aktiv":
        return _deny(401, core.i18n.t("API-Key ist {0}.", core.i18n.t(st)))
    ip = core._client_ip()
    if not _ip_ok(ip, k.get("ips")):
        core._record_login(f"API:{k['name']}", False, f"API-Key von nicht erlaubter IP {ip}")
        return _deny(403, core.i18n.t("Dieser API-Key ist für die IP-Adresse {0} nicht freigegeben.", ip))
    role = core.role_store.get(k.get("role"))
    if not role:
        return _deny(403, core.i18n.t("Die Rolle dieses API-Keys gibt es nicht mehr."))
    with _rate_lock:
        w = _rate.setdefault(kid, [time.time(), 0])
        if time.time() - w[0] > 60:
            w[0], w[1] = time.time(), 0
        w[1] += 1
        if w[1] > RATE_PER_MIN:
            return _deny(429, core.i18n.t("Zu viele Anfragen (höchstens {0} pro Minute und Key).", RATE_PER_MIN))
    now = time.strftime("%Y-%m-%d %H:%M")
    if k.get("last_used") != now or k.get("last_ip") != ip:   # hoechstens einmal pro Minute schreiben
        k.update(last_used=now, last_ip=ip, uses=int(k.get("uses") or 0) + 1)
        core.DB.put("apikey", kid, k)
    g.user, g.role = f"API:{k['name']}", k["role"]
    g.access = core.make_access(g.user, k["role"], key_id=kid)
    g.api_key = kid
    return None


# ---------------------------------------------------------------- Hilfen
def need(perm):
    if not g.access.has(perm):
        raise ApiError(403, f"Dem Key fehlt das Recht „{core.roles.PERM_LABELS.get(perm, perm)}“ ({perm}).")


def _job(jid):
    j = core.load_jobs().get(jid)
    if not j or not g.access.job_ok(jid, j):
        raise ApiError(404, f"Aufgabe {jid} nicht gefunden.")
    return j


SECRET_JOB = ("notify_telegram_token", "notify_apprise_urls", "notify_webhook_url")
ENC_WRITE_ONLY = ("encrypt_password", "encrypt_password_confirm", "encrypt_password2", "encrypt_ack")


def _next_start(jid):
    """Naechster voraussichtlicher Start (auch Live-Runde bzw. geschaetzt ueber den Vorgaenger einer Kette)."""
    t, kind = core.next_start(core.load_jobs(), jid)
    return {"next_start": t.isoformat(timespec="minutes") if t else None, "next_start_kind": kind}


def public_job(jid, j, history=False):
    out = {k: v for k, v in j.items() if k not in SECRET_JOB and k != "history"}
    if not g.access.has("jobs.scripts"):   # Befehle koennen Zugangsdaten enthalten
        for k in SCRIPT_TEXT:
            if out.get(k):
                out[k] = "•••"
    out.update(nosync=core.nosync_on(j), verify=core.verify_of(j), delete_hold=j.get("delete_hold") or None,
               retry_pending=j.get("retry_pending") or None)
    out.setdefault("msg_tpl_on", False)
    out.setdefault("visible_to", "all")
    out["live_mode"] = core.live_mode(j)
    out.update(encrypt=bool(j.get("encrypt")), encrypted=core.is_encrypted(j),
               encrypt_names=j.get("encrypt_names") or "standard", encrypt_dirnames=j.get("encrypt_dirnames", True) is not False)
    out.update(compare=core.compare_of(j), compare_window=core.compare_window(j), speed=core.speed_of(j),
               checksum=core.compare_of(j) == "checksum")
    out["direction"] = "bisync" if core.is_bisync(j) else "mirror"
    if core.is_bisync(j):
        out.update(bisync_conflict=j.get("bisync_conflict") or "newer", bisync_max_delete=str(core.bisync_max_delete(j)),
                   bisync_ready=bool(j.get("bisync_ready")), bisync_need_resync=bool(j.get("bisync_need_resync")))
    out.setdefault("msg_tpl", {})
    out.update(id=jid, trigger=core.trigger_of(j), effective_dest=core.effective_dest(j),
               running=jid in core._running, next_run=core.next_run(jid), **_next_start(jid), is_paused=bool(core.is_paused(j)),
               has_telegram_token=bool(j.get("notify_telegram_token")),
               apprise_urls=[core.notify.mask_url(u) for u in core.notify.apprise_list(j.get("notify_apprise_urls"))],
               webhook_set=bool(j.get("notify_webhook_url")))
    if history:
        out["history"] = j.get("history", [])
    return out


BOOL_FIELDS = ("enabled", "dry_run", "versioning", "checksum", "delete_excluded", "no_delete", "include_source_dir", "paused",
               "notify_webhook", "notify_smtp", "notify_telegram", "notify_apprise", "nosync", "snapshot_sudo", "wol_sleep",
               "encrypt", "encrypt_dirnames", "encrypt_ack")
TEXT_FIELDS = ("name", "source", "dest", "schedule", "max_delete", "extra_flags", "excludes", "selection", "trigger",
               "after_job", "after_when", "paused_until", "pause_chain", "live_interval", "live_full", "live_mode", "direction", "bisync_conflict", "bisync_max_delete", "bw_mode", "versions_keep", "versions_days",
               "notify_mode", "notify_when", "notify_webhook_url", "notify_smtp_to", "notify_telegram_chat_id",
               "notify_telegram_token", "notify_apprise_urls", "notify_apprise_tag", "compare", "compare_window", "speed",
               "verify", "verify_method", "delete_guard", "delete_guard_min", "space_check", "space_min_gb", "retry", "retry_on",
               "health_max_age", "script_pre", "script_post", "script_host", "script_timeout", "script_pre_fail", "script_post_when",
               "snapshot", "snapshot_host", "snapshot_target", "snapshot_dir", "snapshot_cmd", "snapshot_keep",
               "wol_mac", "wol_broadcast", "wol_port", "wol_wait", "wol_check", "wol_sleep_cmd", "wol_sleep_host",
               "encrypt_names", "encrypt_password", "encrypt_password_confirm", "encrypt_password2")
SCRIPT_TEXT = ("script_pre", "script_post", "snapshot_cmd")


class Fields(dict):
    """Wie ein Formular: Haekchen sind vorhanden oder fehlen."""
    def get(self, k, default=None):
        v = dict.get(self, k, default)
        return default if v is None else v


def _fields(base, data):
    f = Fields()
    src = {k: v for k, v in base.items() if k != "_notify"}
    data = data or {}
    if any(k.startswith(("notify_", "msg_tpl")) for k in data):
        # Benachrichtigung wird geaendert: fehlende Felder aus der Aufgabe uebernehmen (Haekchen wie im Formular)
        src.update(base.get("_notify") or {})
    for k, v in data.items():
        if k in BOOL_FIELDS or k in TEXT_FIELDS or k in ("bw", "window"):
            src[k] = v
        elif k == "msg_tpl_on":
            src[k] = v
        elif k == "visible_to":
            if v is not None and v != "all" and not isinstance(v, list):
                raise ApiError(400, core.i18n.t("visible_to muss \"all\" oder eine Liste sein."))
            src["_vis"] = v if v is not None else "all"
        elif k == "msg_tpl":
            if not isinstance(v, dict) or any(e not in core.msgtpl.JOB_EVENTS for e in v):
                raise ApiError(400, core.i18n.t("msg_tpl: nur die Ereignisse {0}.", ", ".join(core.msgtpl.JOB_EVENTS)))
            src[k] = v
        elif k not in ("id", "history", "running", "next_run", "next_start", "next_start_kind", "effective_dest", "is_paused", "owner",
                       "bisync_ready", "bisync_need_resync", "delete_hold", "retry_pending", "last_verify", "dest_space", "nosync_dirs",
                       "encrypt_remote", "encrypted"):
            raise ApiError(400, f"Unbekanntes Feld: {k}")
    for k, allowed in (("compare", core.COMPARE_MODES), ("speed", core.SPEEDS)):
        if k in data and data[k] not in allowed:
            raise ApiError(400, core.i18n.t("{0}: nur {1}.", k, ", ".join(allowed)))
    if "compare" in data:
        src["checksum"] = False
    elif "checksum" in data:   # alte Einstellung: true = Pruefsumme, false = zurueck auf Standard (falls vorher Pruefsumme)
        old = core.compare_of(base)
        src["compare"] = "checksum" if data["checksum"] else ("standard" if old == "checksum" else old)
    else:
        src["compare"] = core.compare_of(base)
    for k in BOOL_FIELDS:
        if src.get(k):
            f[k] = "on"
    for k in TEXT_FIELDS:
        v = src.get(k)
        if v is None:
            continue
        if isinstance(v, list):
            v = "\n".join(str(x) for x in v)
        f[k] = str(v)
    if src.get("bw") is not None:
        f["bw_json"] = json.dumps(src["bw"])
    w = src.get("window")
    if w:
        if not isinstance(w, dict):
            raise ApiError(400, core.i18n.t("window muss ein Objekt {start, end, days, mode} oder null sein."))
        f.update(window_on="on", window_start=str(w.get("start") or ""), window_end=str(w.get("end") or ""),
                 window_mode=str(w.get("mode") or "finish"))
        days = w.get("days")
        days = core.timewin.ALL_DAYS if days in (None, "", "all") else days
        for d in (days if isinstance(days, list) else str(days).split(",")):
            f[f"window_day_{str(d).strip()}"] = "on"
    if "_vis" in src:
        f["vis_mode"] = "all" if src["_vis"] == "all" else "some"
        if src["_vis"] != "all":
            f["vis"] = "\n".join(str(x) for x in src["_vis"])
    if "msg_tpl_on" in src or "msg_tpl" in src:
        f["tpl_api"] = "1"
        if src.get("msg_tpl_on"):
            f["msg_tpl_on"] = "on"
        for ev, t in (src.get("msg_tpl") or {}).items():
            for k in ("title", "body"):
                if (t or {}).get(k):
                    f[f"jtpl_{ev}_{k}"] = str(t[k])
        if "notify_mode" not in f:
            f["notify_mode"] = "global"
    return f


def _base_fields(j):
    b = {k: j.get(k) for k in BOOL_FIELDS + TEXT_FIELDS if k not in ("notify_telegram_token", "notify_apprise_urls") + ENC_WRITE_ONLY}
    if "encrypt_dirnames" not in j:
        b["encrypt_dirnames"] = True
    b["trigger"] = core.trigger_of(j)
    b["bw"] = j.get("bw")
    b["window"] = j.get("window")
    b["_notify"] = {k: b.pop(k) for k in [k for k in b if k.startswith("notify_")]}   # nur bei Bedarf (siehe _fields)
    b["_notify"].update(msg_tpl_on=bool(j.get("msg_tpl_on")), msg_tpl=j.get("msg_tpl") or {})
    return b


# ---------------------------------------------------------------- Operationen (REST und MCP)
def op_status():
    jobs = {jid: j for jid, j in core.load_jobs().items() if g.access.job_ok(jid, j)}
    return {"version": core.VERSION, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "jobs": len(jobs),
            "running": [{"id": jid, "name": jobs[jid]["name"]} for jid in core._running if jid in jobs],
            "failed": [{"id": jid, "name": j["name"], "last_run": j.get("last_run")} for jid, j in jobs.items()
                       if j.get("last_status") == "fehler"],
            "paused": [{"id": jid, "name": j["name"]} for jid, j in jobs.items() if core.is_paused(j)],
            "key": g.user, "permissions": sorted(g.access.perms), "update": core.update_status()}


def op_jobs():
    need("jobs.view")
    return [public_job(jid, j) for jid, j in sorted(core.load_jobs().items(), key=lambda kv: kv[1]["name"].lower())
            if g.access.job_ok(jid, j)]


def op_job(jid):
    need("jobs.view")
    return public_job(jid, _job(jid))


def _save_job(jid, data):
    jobs = core.load_jobs()
    if jid:
        old = _job(jid)
        job = dict(old)
        base = _base_fields(old)
    else:
        old, job, base = dict(core.EMPTY_JOB), dict(core.EMPTY_JOB), {k: v for k, v in core.EMPTY_JOB.items()
                                                                       if not k.startswith("notify_")}
        base["trigger"] = "time"
    if not isinstance(data, dict):
        raise ApiError(400, "JSON-Objekt erwartet.")
    err = core.apply_job_form(_fields(base, data), job, old, jid, jobs, api=True)
    if err:
        raise ApiError(400, err)
    jid, err = core.save_job_with_crypt(jid, job)
    if err:
        raise ApiError(400, err)
    core.schedule_all()
    return public_job(jid, job)


def op_job_create(data):
    need("jobs.create")
    return _save_job(None, data)


def op_job_update(jid, data):
    need("jobs.edit")
    return _save_job(jid, data)


def op_job_delete(jid):
    need("jobs.delete")
    j = _job(jid)
    core.stop_job(jid)
    with core._lock:
        jobs = core.load_jobs()
        jobs.pop(jid, None)
        for o in jobs.values():
            if core.trigger_of(o) == "after" and o.get("after_job") == jid:
                o.update(trigger="manual", after_job="")
        core.save_jobs(jobs)
    core.shutil.rmtree(os.path.join(core.LOG_DIR, jid), ignore_errors=True)
    core.schedule_all()
    return {"deleted": jid, "name": j["name"]}


def op_job_run(jid, dry=False):
    need("jobs.dryrun" if dry else "jobs.run")
    j = _job(jid)
    if jid in core._running:
        raise ApiError(409, "Die Aufgabe läuft bereits.")
    ok = core.start_job(jid, dry_run=bool(dry), by=g.user, manual=True)
    if ok is False:
        raise ApiError(409, "Die Aufgabe konnte nicht gestartet werden (läuft bereits).")
    core.audit_add("run", "Testlauf gestartet" if dry else "gestartet", j["name"], detail="über API")
    return {"started": jid, "name": j["name"], "dry_run": bool(dry), "run": core._current_run.get(jid)}


def op_job_resync(jid, dry=False):
    need("jobs.dryrun" if dry else "jobs.run")
    j = _job(jid)
    if not core.is_bisync(j):
        raise ApiError(400, "Nur bei Zwei-Wege-Sync möglich.")
    if jid in core._running:
        raise ApiError(409, "Die Aufgabe läuft bereits.")
    if core.start_job(jid, dry_run=bool(dry), by=g.user, manual=True, resync=True) is False:
        raise ApiError(409, "Die Aufgabe konnte nicht gestartet werden (läuft bereits).")
    core.update_job(jid, bisync_need_resync=False)
    core.audit_add("run", "neu zusammengeführt (Zwei-Wege)", j["name"], detail="über API")
    return {"started": jid, "name": j["name"], "dry_run": bool(dry), "resync": True, "run": core._current_run.get(jid)}


def op_job_stop(jid):
    need("jobs.run")
    j = _job(jid)
    was = jid in core._running
    core.stop_job(jid)
    if was:
        core.audit_add("run", "gestoppt", j["name"], detail="über API")
    return {"stopped": was, "id": jid}


def op_job_pause(jid, hours=None, until=None, resume=False):
    need("jobs.edit")
    _job(jid)
    with core._lock:
        jobs = core.load_jobs()
        job = jobs[jid]
        before = dict(job)
        if resume:
            job.update(paused=False, paused_until="", paused_by="")
        else:
            u = ""
            if hours:
                try:
                    u = (datetime.datetime.now() + datetime.timedelta(hours=float(hours))).strftime("%Y-%m-%dT%H:%M")
                except (TypeError, ValueError):
                    raise ApiError(400, "hours muss eine Zahl sein.")
            elif until:
                if not re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}$", str(until)):
                    raise ApiError(400, "until im Format JJJJ-MM-TTTHH:MM angeben.")
                u = str(until).replace(" ", "T")[:16]
                if u <= datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"):
                    raise ApiError(400, "until liegt in der Vergangenheit.")
            job.update(paused=True, paused_until=u, paused_by=g.user)
        core.save_jobs(jobs)
    core.schedule_all()
    ch = core.audit.diff(before, job, "job")
    if ch and request.endpoint != "mcp":   # MCP: Vorher/Nachher-Vergleich protokolliert schon
        core.audit_add("job", "geändert", job["name"], ch, detail="über API")
    return public_job(jid, job)


def op_history(jid, limit=50):
    need("jobs.logs")
    return _job(jid).get("history", [])[:max(1, min(int(limit or 50), 1000))]


def op_log(jid, run_id=None, flt="all", q="", max_lines=500):
    need("jobs.logs")
    j = _job(jid)
    hist = j.get("history", [])
    run_id = run_id or core._current_run.get(jid) or (hist[0].get("run") if hist else None)
    if not run_id or not core.RUN_ID_RE.match(run_id) or not os.path.exists(core.run_log_path(jid, run_id)):
        raise ApiError(404, "Kein Log für diesen Lauf.")
    max_lines = max(1, min(int(max_lines or 500), core.MAX_LINES))
    lines, total = [], 0
    with open(core.run_log_path(jid, run_id), encoding="utf-8", errors="replace") as f:
        for line in f:
            kind = core.notify.classify(line)
            if (flt in ("all", "", None) or kind == flt) and (not q or q.lower() in line.lower()):
                total += 1
                lines.append(line.rstrip("\n"))
                if len(lines) > max_lines:
                    lines.pop(0)
    entry = next((h for h in hist if h.get("run") == run_id), None)
    return {"job": jid, "run": run_id, "running": core._current_run.get(jid) == run_id, "entry": entry,
            "matching_lines": total, "lines": lines}


def op_remotes():
    need("remotes.view")
    vis = core.remote_vis_map()
    return [dict(r, visible_to=vis.get(r["name"], "all")) for r in core.list_remotes() if g.access.remote_ok(r["name"])]


def op_browse(path):
    need("remotes.browse")
    if not path:
        return core.browse()   # Liste der Speicherorte (liest request.args nicht bei leerem Pfad)
    res = core.browse_entries(path)
    if isinstance(res, tuple):
        raise ApiError(res[1], res[0].get("error", "Fehler"))
    if res.get("ok") is False:
        raise ApiError(502, res.get("error", "Fehler"))
    return res


def op_schedules():
    need("jobs.view")
    return core.schedules_data()


def op_audit(cat="", user="", q="", day_from="", day_to="", limit=100):
    need("system.audit")
    e = core.audit_log.query(cat=cat or "", user=user or "", q=q or "", day_from=day_from or "", day_to=day_to or "")
    return {"total": len(e), "entries": e[:max(1, min(int(limit or 100), 5000))]}


def op_users():
    need("users.view")
    grs = core.load_groups()
    return [{"name": n, "role": u.get("role"), "disabled": bool(u.get("disabled")), "locked": users_reason(u),
             "totp": bool(u.get("totp_enabled")), "passkeys": len(u.get("passkeys") or []),
             "last_login": u.get("last_login"), "created": u.get("created"), "groups": core.roles.groups_of(grs, n),
             "sidebar": "mini" if u.get("sidebar") == "mini" else "full"}
            for n, u in sorted(core.store.load().items())]


def users_reason(u):
    return core.users.inactive_reason(u) or ""


# ---------------------------------------------------------------- MCP-Tools
def _schema(props=None, required=None):
    return {"type": "object", "properties": props or {}, "required": required or [], "additionalProperties": False}


JOB_ID = {"job_id": {"type": "string", "description": "ID der Aufgabe (siehe list_jobs)"}}
JOB_FIELDS = {"type": "object", "description": "Felder der Aufgabe, z. B. name, source, dest, trigger (time|after|live|manual), "
              "schedule (Cron), selection, excludes, enabled, dry_run, versioning, max_delete, compare (standard|size|checksum|tolerant: "
              "woran eine Änderung erkannt wird), compare_window (Sekunden bei tolerant), speed (gentle|normal|fast|max), no_delete "
              "(im Ziel nichts löschen), window ({start, end, days, mode} Zeitfenster oder null), verify (off|always|daily|weekly: Prüflauf), "
              "verify_method (auto|size|download), delete_guard (Prozent, Löschwarnung), space_check (off|warn|stop), space_min_gb, retry "
              "(Minuten, z. B. \"5, 15, 60\"), retry_on (network|any), nosync, health_max_age (Stunden), script_pre, script_post, script_host, "
              "snapshot (off|zfs|btrfs|command), snapshot_target, snapshot_dir, snapshot_cmd, snapshot_keep, wol_mac, wol_broadcast, wol_wait, "
              "wol_check, wol_sleep, wol_sleep_cmd, wol_sleep_host, encrypt, encrypt_password, encrypt_password_confirm, encrypt_ack, "
              "encrypt_names (standard|obfuscate|off), encrypt_dirnames, encrypt_password2 (vollständig in der OpenAPI-Beschreibung)", "additionalProperties": True}
TOOLS = [
    ("status", "Überblick: Version, laufende, fehlgeschlagene und pausierte Aufgaben, Rechte des Keys.", None,
     _schema(), lambda a: op_status(), True),
    ("list_jobs", "Alle Aufgaben mit Status, letztem Lauf und nächstem Start (next_start als ISO-Zeit, auch Live-Runde oder geschätzt über die Kette; next_start_kind: time, live, after, parent_running, manual, paused, off).", "jobs.view", _schema(),
     lambda a: op_jobs(), True),
    ("get_job", "Eine Aufgabe mit allen Einstellungen.", "jobs.view", _schema(JOB_ID, ["job_id"]),
     lambda a: op_job(a["job_id"]), True),
    ("job_history", "Verlauf der letzten Läufe einer Aufgabe (Status, Dauer, kopiert, gelöscht, Fehler).", "jobs.logs",
     _schema(dict(JOB_ID, limit={"type": "integer", "default": 20}), ["job_id"]),
     lambda a: op_history(a["job_id"], a.get("limit", 20)), True),
    ("job_log", "Log eines Laufs (ohne run_id: letzter bzw. laufender Lauf). Filter: all, error, copied, deleted, notice.",
     "jobs.logs", _schema(dict(JOB_ID, run_id={"type": "string"}, filter={"type": "string", "enum": ["all", "error", "copied", "deleted", "notice"]},
                               search={"type": "string"}, max_lines={"type": "integer", "default": 200}), ["job_id"]),
     lambda a: op_log(a["job_id"], a.get("run_id"), a.get("filter", "all"), a.get("search", ""), a.get("max_lines", 200)), True),
    ("run_job", "Aufgabe jetzt starten (dry_run=true: nur Testlauf, ändert nichts).", "jobs.run",
     _schema(dict(JOB_ID, dry_run={"type": "boolean", "default": False}), ["job_id"]),
     lambda a: op_job_run(a["job_id"], a.get("dry_run", False)), False),
    ("resync_job", "Zwei-Wege-Sync neu zusammenführen (--resync): beide Seiten vereinen, ohne zu löschen. Nötig nach einem Abbruch.",
     "jobs.run", _schema(dict(JOB_ID, dry_run={"type": "boolean", "default": False}), ["job_id"]),
     lambda a: op_job_resync(a["job_id"], a.get("dry_run", False)), False),
    ("stop_job", "Laufende Aufgabe stoppen.", "jobs.run", _schema(JOB_ID, ["job_id"]),
     lambda a: op_job_stop(a["job_id"]), False),
    ("pause_job", "Aufgabe pausieren (ohne Angabe bis zum Fortsetzen, sonst hours oder until JJJJ-MM-TTTHH:MM).", "jobs.edit",
     _schema(dict(JOB_ID, hours={"type": "number"}, until={"type": "string"}), ["job_id"]),
     lambda a: op_job_pause(a["job_id"], a.get("hours"), a.get("until")), False),
    ("resume_job", "Pause einer Aufgabe beenden.", "jobs.edit", _schema(JOB_ID, ["job_id"]),
     lambda a: op_job_pause(a["job_id"], resume=True), False),
    ("create_job", "Neue Aufgabe anlegen. Pflicht: name, source, dest.", "jobs.create",
     _schema({"fields": JOB_FIELDS}, ["fields"]), lambda a: op_job_create(a["fields"]), False),
    ("update_job", "Felder einer Aufgabe ändern (nur die angegebenen).", "jobs.edit",
     _schema(dict(JOB_ID, fields=JOB_FIELDS), ["job_id", "fields"]), lambda a: op_job_update(a["job_id"], a["fields"]), False),
    ("delete_job", "Aufgabe samt Logs löschen. Nicht umkehrbar.", "jobs.delete", _schema(JOB_ID, ["job_id"]),
     lambda a: op_job_delete(a["job_id"]), False),
    ("list_remotes", "Speicherorte (Name und Typ, ohne Zugangsdaten).", "remotes.view", _schema(),
     lambda a: op_remotes(), True),
    ("browse", "Ordner und Dateien eines Pfades auflisten, z. B. 'NAS:daten'. Leer = Speicherorte.", "remotes.browse",
     _schema({"path": {"type": "string", "default": ""}}), lambda a: op_browse(a.get("path", "")), True),
    ("list_schedules", "Zeitpläne, Ketten, Live- und manuelle Aufgaben.", "jobs.view", _schema(),
     lambda a: op_schedules(), True),
    ("audit_log", "Audit-Log durchsuchen (wer hat wann was gemacht).", "system.audit",
     _schema({"category": {"type": "string"}, "user": {"type": "string"}, "search": {"type": "string"},
              "from": {"type": "string", "description": "JJJJ-MM-TT"}, "to": {"type": "string"},
              "limit": {"type": "integer", "default": 50}}),
     lambda a: op_audit(a.get("category"), a.get("user"), a.get("search"), a.get("from"), a.get("to"), a.get("limit", 50)), True),
    ("list_users", "Benutzer mit Rolle, 2FA und letzter Anmeldung (ohne Geheimnisse).", "users.view", _schema(),
     lambda a: op_users(), True),
]


EXTRA_PATHS = None   # von apigui gesetzt: weitere OpenAPI-Pfade


def _tool_allowed(perm, name):
    if perm == "role:admin":
        return g.role == "admin"
    if perm and not g.access.has(perm):
        return False
    return True


def mcp_tools():
    out = []
    for name, desc, perm, schema, _, ro in TOOLS:
        if _tool_allowed(perm, name):
            out.append({"name": name, "description": desc, "inputSchema": schema,
                        "annotations": {"readOnlyHint": ro, "destructiveHint": name == "delete_job",
                                        "idempotentHint": ro, "openWorldHint": name == "browse"}})
    return out


def _rpc_error(rid, code, msg):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}


def mcp_handle(msg):
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return _rpc_error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Ungültige Anfrage")
    rid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
    if "id" not in msg:   # Benachrichtigung
        return None
    if method == "initialize":
        want = params.get("protocolVersion")
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": want if want in MCP_PROTOCOLS else MCP_PROTOCOLS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "MirrorSync", "title": "MirrorSync", "version": core.VERSION},
            "instructions": core.i18n.translate("MirrorSync spiegelt Ordner per rclone (einweg, 1:1). Mit list_jobs die Aufgaben finden, "
                            "mit run_job starten (dry_run=true zum Testen), mit job_log und job_history Ergebnisse prüfen.") + " " + core.i18n.t("Angemeldet als {0}; nur Tools mit passendem Recht sind sichtbar.", g.user) + " " + core.i18n.translate(
                "Außerdem lassen sich Speicherorte, Zeitpläne, Benutzer, Rollen, API-Keys, Benachrichtigungen, Vorlagen, "
                "Einstellungen, Zugriffsregeln und Sicherungen ansehen, ändern und löschen, mit denselben Prüfungen wie in der GUI.") + " " + core.i18n.translate(
                "Prüfen: verify_job und get_health. Löschwarnungen mit approve_job freigeben. Gelöschte oder überschriebene Dateien "
                "mit list_versions und restore_versions zurückholen. Statistik mit get_stats, Versionshinweise mit get_changelog.")}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": core.i18n.translate_deep(mcp_tools())}}
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        tool = next((t for t in TOOLS if t[0] == name), None)
        if not tool or not _tool_allowed(tool[2], name):
            return _rpc_error(rid, -32602, f"Unbekanntes oder nicht erlaubtes Tool: {name}")
        try:
            data = tool[4](args)
            if isinstance(data, tuple):
                data = data[0]
            text = json.dumps(data, ensure_ascii=False, indent=1, default=str)
            res = {"content": [{"type": "text", "text": text}], "isError": False}
            if isinstance(data, dict):
                res["structuredContent"] = data
            return {"jsonrpc": "2.0", "id": rid, "result": res}
        except ApiError as e:
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": core.i18n.translate(e.msg)}],
                                                            "isError": True}}
        except KeyError as e:
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": f"Argument fehlt: {e}"}], "isError": True}}
    if method in ("resources/list", "prompts/list"):
        return {"jsonrpc": "2.0", "id": rid, "result": {method.split("/")[0]: []}}
    return _rpc_error(rid, -32601, f"Methode nicht unterstützt: {method}")


# ---------------------------------------------------------------- OpenAPI
def openapi():
    def op(summary, perm=None, params=None, body=None, tag="Aufgaben", ok="Erfolg"):
        o = {"summary": summary, "tags": [tag], "responses": {"200": {"description": ok},
                                                               "401": {"description": "API-Key fehlt oder ungültig"},
                                                               "403": {"description": "Recht fehlt"}}}
        if perm:
            o["description"] = f"Benötigtes Recht: `{perm}`"
        if params:
            o["parameters"] = params
        if body:
            o["requestBody"] = {"required": True, "content": {"application/json": {"schema": body}}}
        return o
    jid = {"name": "job_id", "in": "path", "required": True, "schema": {"type": "string"}}
    q = lambda n, t="string", d="": {"name": n, "in": "query", "required": False, "schema": {"type": t}, "description": d}
    job_body = {"$ref": "#/components/schemas/JobFields"}
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "MirrorSync API", "version": core.VERSION,
                 "description": "Steuerung von MirrorSync per API-Key (Einstellungen → API). Es gelten die Rechte der Rolle "
                                "des Keys, dieselben IP-Sperren wie in der GUI und höchstens "
                                f"{RATE_PER_MIN} Anfragen pro Minute. MCP-Server: `POST /mcp`."},
        "servers": [{"url": "/api/v1"}],
        "components": {
            "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "msk_…"}},
            "schemas": {"JobFields": {"type": "object", "properties": {
                "name": {"type": "string"}, "source": {"type": "string", "example": "NAS:daten"},
                "dest": {"type": "string", "example": "Server:/backup/daten"},
                "trigger": {"type": "string", "enum": ["time", "after", "live", "manual"]},
                "schedule": {"type": "string", "example": "0 3 * * *"}, "after_job": {"type": "string"},
                "after_when": {"type": "string", "enum": ["ok", "always"]},
                "live_interval": {"type": "integer"},
                "live_full": {"type": "string", "description": "Nur bei live_mode=fast: Cron (0 3 * * *) oder Intervall (@every 6h, @every 90m)"},
                "direction": {"type": "string", "enum": ["mirror", "bisync"], "description": "mirror: Einweg Quelle → Ziel (Standard); bisync: Zwei-Wege-Sync zwischen Seite A (source) und Seite B (dest), braucht Recht jobs.twoway"},
                "bisync_conflict": {"type": "string", "enum": ["newer", "path1", "path2", "none"], "description": "Zwei-Wege: bei Änderung auf beiden Seiten gewinnt newer = die neuere, path1 = Seite A, path2 = Seite B, none = beide behalten. Die unterlegene Fassung bleibt umbenannt erhalten (.konflikt1)"},
                "bisync_max_delete": {"type": "string", "description": "Zwei-Wege: Abbruch, wenn mehr als so viel Prozent der Dateien einer Seite gelöscht würden (1–100, Standard 50)"},
                "live_mode": {"type": "string", "enum": ["mirror", "fast"], "description": "mirror: jede Live-Runde wie Spiegeln inkl. Löschen (Standard); fast: nur neue/geänderte Dateien"},
                "selection": {"type": "array", "items": {"type": "string"}, "example": ["Projekte/", "bericht.docx"]},
                "excludes": {"type": "array", "items": {"type": "string"}, "example": ["*.tmp"]},
                "enabled": {"type": "boolean"}, "dry_run": {"type": "boolean"}, "versioning": {"type": "boolean"},
                "checksum": {"type": "boolean", "description": "veraltet, wie compare=checksum"}, "include_source_dir": {"type": "boolean"},
                "compare": {"type": "string", "enum": ["standard", "size", "checksum", "tolerant"],
                            "description": "Woran eine Änderung erkannt wird: standard = Größe + Änderungszeit (Standard), size = nur Größe (am schnellsten), checksum = Prüfsumme (am sichersten, liest jede Datei), tolerant = Änderungszeit mit großzügiger Toleranz (z. B. SMB, FAT, Zeitumstellung)"},
                "compare_window": {"type": "integer", "description": "bei compare=tolerant: erlaubte Abweichung der Änderungszeit in Sekunden (1–86400, Standard 2)"},
                "speed": {"type": "string", "enum": ["gentle", "normal", "fast", "max"],
                          "description": "Tempo: gentle = 2 parallele Übertragungen (schont Server und Leitung), normal = rclone-Standard (4), fast = 8 und schnelles Auflisten, max = 16 und schnelles Auflisten. Eigene --transfers/--checkers in extra_flags haben Vorrang"},
                "delete_excluded": {"type": "boolean"},
                "no_delete": {"type": "boolean", "description": "Spiegeln: im Ziel nichts löschen, nur Neues und Geändertes kopieren (rclone copy statt sync)"},
                "max_delete": {"type": "string", "example": "500"},
                "paused": {"type": "boolean"}, "notify_mode": {"type": "string", "enum": ["global", "custom", "off"]},
                "notify_when": {"type": "string", "enum": ["fail", "always"]},
                "notify_webhook": {"type": "boolean"}, "notify_webhook_url": {"type": "string"},
                "notify_smtp": {"type": "boolean"}, "notify_smtp_to": {"type": "string"},
                "notify_telegram": {"type": "boolean"}, "notify_telegram_chat_id": {"type": "string"},
                "notify_telegram_token": {"type": "string", "description": "nur setzen, wird nie ausgegeben"},
                "notify_apprise": {"type": "boolean"}, "notify_apprise_tag": {"type": "string"},
                "notify_apprise_urls": {"type": "array", "items": {"type": "string"}, "description": "nur setzen, wird nie ausgegeben"},
                "msg_tpl_on": {"type": "boolean", "description": "eigene Texte für diese Aufgabe"},
                "msg_tpl": {"type": "object", "description": "{run_ok|run_fail: {title, body}}"},
                "bw_mode": {"type": "string", "enum": ["global", "custom", "off"]},
                "bw": {"type": "object", "description": "wie /settings/bandwidth"},
                "window": {"type": "object", "nullable": True, "description": "Zeitfenster: {start: \"22:00\", end: \"06:00\", days: [0..6] (0 = Montag, Standard alle), mode: finish (durchlaufen lassen) | resume (am Ende anhalten, im nächsten Fenster weitermachen) | stop (am Ende anhalten)}; null = immer. Automatische Starts außerhalb warten auf das Fenster. Im Ergebnis zeigt window_wait, ob die Aufgabe gerade wartet (deferred oder resume)"},
                "pause_chain": {"type": "string", "enum": ["skip", "stop"]},
                "versions_keep": {"type": "string", "description": "bei versioning: so viele Stände behalten (leer = alle)"},
                "versions_days": {"type": "string", "description": "bei versioning: Stände älter als so viele Tage entfernen (leer = unbegrenzt)"},
                "visible_to": {"description": "\"all\" (alle mit Recht) oder Liste aus user:<Name> und group:<Gruppen-ID>; Admins und Besitzer sehen die Aufgabe immer"},
                "verify": {"type": "string", "enum": ["off", "always", "daily", "weekly"], "description": "Prüflauf nach dem Lauf (rclone check): off, always = nach jedem Lauf, daily/weekly = höchstens einmal am Tag bzw. in der Woche. Abweichungen machen den Lauf zum Fehler"},
                "verify_method": {"type": "string", "enum": ["auto", "size", "download"], "description": "auto = Prüfsumme, wenn beide Seiten eine gemeinsame haben, sonst Größe; size = nur Größe; download = Inhalt Byte für Byte (liest alles)"},
                "delete_guard": {"type": "string", "description": "Löschwarnung: Lauf anhalten und Freigabe verlangen, wenn mindestens so viel Prozent der Dateien im Ziel gelöscht würden (1–100, leer = aus)"},
                "delete_guard_min": {"type": "string", "description": "Löschwarnung erst ab so vielen Löschungen (Standard 10)"},
                "space_check": {"type": "string", "enum": ["off", "warn", "stop"], "description": "Speicher am Ziel vor dem Lauf prüfen: warn = melden und trotzdem laufen, stop = abbrechen"},
                "space_min_gb": {"type": "string", "description": "Mindestens so viel GB sollen am Ziel nach dem Lauf frei bleiben (leer = nur benötigten Platz prüfen)"},
                "retry": {"type": "string", "example": "5, 15, 60", "description": "Nach einem Fehler neu versuchen nach so vielen Minuten (durch Komma, höchstens 10 Versuche; leer = aus)"},
                "retry_on": {"type": "string", "enum": ["network", "any"], "description": "network = nur bei Netzwerkfehlern (Standard), any = bei jedem Fehler"},
                "nosync": {"type": "boolean", "description": "Ordner mit einer Datei .nosync überspringen (im Ziel bleiben sie unberührt)"},
                "health_max_age": {"type": "string", "description": "Für /health/jobs: überfällig, wenn der letzte Lauf älter als so viele Stunden ist (leer = aus dem Zeitplan berechnet)"},
                "script_pre": {"type": "string", "description": "Befehl(e) vor dem Lauf (sh). Braucht Recht jobs.scripts"},
                "script_post": {"type": "string", "description": "Befehl(e) nach dem Lauf; Umgebungsvariable MS_STATUS = ok oder fehler"},
                "script_host": {"type": "string", "description": "leer = im Container, sonst Name eines SFTP-Speicherorts (per SSH)"},
                "script_timeout": {"type": "string", "description": "Zeitlimit je Skript in Sekunden (Standard 600)"},
                "script_pre_fail": {"type": "string", "enum": ["abort", "continue"]},
                "script_post_when": {"type": "string", "enum": ["always", "ok", "fail"]},
                "snapshot": {"type": "string", "enum": ["off", "zfs", "btrfs", "command"], "description": "Snapshot am Ziel nach jedem erfolgreichen Lauf"},
                "snapshot_host": {"type": "string", "description": "leer = im Container, sonst SFTP-Speicherort (SSH)"},
                "snapshot_target": {"type": "string", "description": "ZFS-Dataset (pool/backup) bzw. Btrfs-Subvolume (/mnt/backup)"},
                "snapshot_dir": {"type": "string", "description": "Btrfs: Ordner für die Snapshots (außerhalb des Ziels)"},
                "snapshot_cmd": {"type": "string", "description": "Eigener Befehl, Platzhalter {name}, {date}, {job}, {job_id}, {dest}"},
                "snapshot_keep": {"type": "string", "description": "so viele MirrorSync-Snapshots behalten (leer = alle)"},
                "snapshot_sudo": {"type": "boolean", "description": "Befehle mit sudo -n ausführen"},
                "encrypt": {"type": "boolean", "description": "Ziel verschlüsseln (rclone crypt über dem Ziel, darin Ordner data). Braucht Recht jobs.encrypt; nicht mit Zwei-Wege-Sync"},
                "encrypt_password": {"type": "string", "writeOnly": True, "description": "Passwort beim ersten Einschalten (mind. 8 Zeichen). Wird nie ausgegeben und lässt sich später nicht ändern. Ohne Passwort sind die Daten verloren"},
                "encrypt_password_confirm": {"type": "string", "writeOnly": True, "description": "Passwort wiederholen"},
                "encrypt_password2": {"type": "string", "writeOnly": True, "description": "Optional: zweites Passwort (Salt) für mehr Sicherheit, ebenfalls aufbewahren"},
                "encrypt_ack": {"type": "boolean", "writeOnly": True, "description": "Bestätigung: Passwort ist sicher aufbewahrt (beim ersten Einschalten nötig)"},
                "encrypt_names": {"type": "string", "enum": ["standard", "obfuscate", "off"], "description": "Dateinamen: standard = verschlüsselt, obfuscate = nur verschleiert, off = lesbar. Nur beim ersten Einschalten"},
                "encrypt_dirnames": {"type": "boolean", "description": "Ordnernamen ebenfalls verschlüsseln (Standard true). Nur beim ersten Einschalten"},
                "encrypted": {"type": "boolean", "readOnly": True, "description": "Verschlüsselung ist aktiv"},
                "wol_mac": {"type": "string", "description": "Wake-on-LAN: MAC-Adresse des Zielservers (leer = aus)"},
                "wol_broadcast": {"type": "string", "description": "Broadcast-Adresse (Standard 255.255.255.255, z. B. 192.168.1.255)"},
                "wol_port": {"type": "string", "description": "UDP-Port (Standard 9)"},
                "wol_wait": {"type": "string", "description": "höchstens so viele Sekunden auf das Aufwachen warten (Standard 300)"},
                "wol_check": {"type": "string", "description": "Erreichbarkeit prüfen über Host:Port (leer = Host des Ziel-Speicherorts)"},
                "wol_sleep": {"type": "boolean", "description": "nach dem Lauf wieder schlafen legen (nur, wenn MirrorSync ihn geweckt hat)"},
                "wol_sleep_cmd": {"type": "string", "description": "Befehl zum Schlafenlegen (Standard systemctl suspend)"},
                "wol_sleep_host": {"type": "string", "description": "SFTP-Speicherort, über den der Befehl läuft (leer = Ziel, wenn SFTP)"}}}}},
        "security": [{"bearer": []}],
        "paths": {
            "/status": {"get": op("Überblick und Rechte des Keys", tag="System")},
            "/jobs": {"get": op("Aufgaben auflisten", "jobs.view"),
                      "post": op("Aufgabe anlegen", "jobs.create", body=job_body)},
            "/jobs/{job_id}": {"get": op("Aufgabe lesen", "jobs.view", [jid]),
                               "patch": op("Aufgabe ändern (nur angegebene Felder)", "jobs.edit", [jid], job_body),
                               "delete": op("Aufgabe löschen", "jobs.delete", [jid])},
            "/jobs/{job_id}/run": {"post": op("Jetzt starten", "jobs.run bzw. jobs.dryrun", [jid, q("dry_run", "boolean", "nur Testlauf")])},
            "/jobs/{job_id}/resync": {"post": op("Zwei-Wege-Sync neu zusammenführen", "jobs.run bzw. jobs.dryrun", [jid, q("dry_run", "boolean", "nur Testlauf")])},
            "/jobs/{job_id}/stop": {"post": op("Stoppen", "jobs.run", [jid])},
            "/jobs/{job_id}/pause": {"post": op("Pausieren", "jobs.edit", [jid, q("hours", "number"), q("until", d="JJJJ-MM-TTTHH:MM")])},
            "/jobs/{job_id}/resume": {"post": op("Pause beenden", "jobs.edit", [jid])},
            "/jobs/{job_id}/history": {"get": op("Verlauf", "jobs.logs", [jid, q("limit", "integer")])},
            "/jobs/{job_id}/log": {"get": op("Log des letzten Laufs", "jobs.logs", [jid, q("run_id"), q("filter", d="all|error|copied|deleted|notice"),
                                                                                   q("q", d="Suchtext"), q("max_lines", "integer")])},
            "/remotes": {"get": op("Speicherorte (ohne Zugangsdaten)", "remotes.view", tag="Speicherorte")},
            "/browse": {"get": op("Ordner und Dateien auflisten", "remotes.browse", [q("path", d="z. B. NAS:daten")], tag="Speicherorte")},
            "/schedules": {"get": op("Zeitpläne und Ketten", "jobs.view", tag="Zeitpläne")},
            "/audit": {"get": op("Audit-Log", "system.audit", [q("cat"), q("user"), q("q"), q("from", d="JJJJ-MM-TT"), q("to"), q("limit", "integer")], tag="System")},
            "/users": {"get": op("Benutzer (ohne Geheimnisse)", "users.view", tag="Benutzer")},
        }}
    for path, ops in (EXTRA_PATHS() if EXTRA_PATHS else {}).items():
        spec["paths"].setdefault(path, {}).update(ops)
    return spec


# ---------------------------------------------------------------- Routen
def register(app, core_module):
    global core
    core = core_module
    app.json.ensure_ascii = False   # Umlaute lesbar in JSON-Antworten
    core.AUDIT_EP.update({"api_job_create": ["job"], "api_job_update": ["job"], "api_job_delete": ["job"],
                          "mcp": ["job"]})
    core.ENDPOINT_PERMS.update({"api_keys_page": "system.api", "api_key_revoke": "system.api", "api_key_delete": "system.api",
                                "api_key_reveal": "system.api", "api_key_reveal_options": "system.api",
                                "api_key_edit": "system.api"})

    def j(fn, *a, status=200, **kw):
        try:
            data = fn(*a, **kw)
        except ApiError as e:
            return jsonify({"error": e.msg}), e.status
        if isinstance(data, tuple):
            return data
        return jsonify(data), status

    def body():
        data = request.get_json(silent=True)
        if data is None:
            raise ApiError(400, "JSON-Body erwartet (Content-Type: application/json).")
        return data

    def wrap_body(fn, *a):
        try:
            return fn(*a, body())
        except ApiError:
            raise

    truthy = lambda v: str(v).lower() in ("1", "true", "yes", "ja", "on")
    R = "/api/v1"
    app.add_url_rule(R + "/openapi.json", "api_openapi", lambda: jsonify(core.i18n.translate_deep(openapi())))
    app.add_url_rule(R + "/status", "api_status", lambda: j(op_status))
    app.add_url_rule(R + "/jobs", "api_jobs", lambda: j(op_jobs))
    app.add_url_rule(R + "/jobs", "api_job_create", lambda: j(lambda: wrap_body(op_job_create), status=201), methods=["POST"])
    app.add_url_rule(R + "/jobs/<job_id>", "api_job", lambda job_id: j(op_job, job_id))
    app.add_url_rule(R + "/jobs/<job_id>", "api_job_update", lambda job_id: j(lambda: wrap_body(op_job_update, job_id)),
                     methods=["PATCH", "PUT"])
    app.add_url_rule(R + "/jobs/<job_id>", "api_job_delete", lambda job_id: j(op_job_delete, job_id), methods=["DELETE"])
    app.add_url_rule(R + "/jobs/<job_id>/run", "api_job_run", lambda job_id: j(
        op_job_run, job_id, truthy(request.args.get("dry_run") or (request.get_json(silent=True) or {}).get("dry_run", ""))),
        methods=["POST"])
    app.add_url_rule(R + "/jobs/<job_id>/resync", "api_job_resync", lambda job_id: j(
        op_job_resync, job_id, truthy(request.args.get("dry_run") or (request.get_json(silent=True) or {}).get("dry_run", ""))),
        methods=["POST"])
    app.add_url_rule(R + "/jobs/<job_id>/stop", "api_job_stop", lambda job_id: j(op_job_stop, job_id), methods=["POST"])

    def pause(job_id):
        d = request.get_json(silent=True) or {}
        return j(op_job_pause, job_id, request.args.get("hours") or d.get("hours"), request.args.get("until") or d.get("until"))
    app.add_url_rule(R + "/jobs/<job_id>/pause", "api_job_pause", pause, methods=["POST"])
    app.add_url_rule(R + "/jobs/<job_id>/resume", "api_job_resume", lambda job_id: j(op_job_pause, job_id, resume=True),
                     methods=["POST"])
    app.add_url_rule(R + "/jobs/<job_id>/history", "api_job_history",
                     lambda job_id: j(op_history, job_id, request.args.get("limit", 50)))
    app.add_url_rule(R + "/jobs/<job_id>/log", "api_job_log", lambda job_id: j(
        op_log, job_id, request.args.get("run_id"), request.args.get("filter", "all"), request.args.get("q", ""),
        request.args.get("max_lines", 500)))
    app.add_url_rule(R + "/remotes", "api_remotes", lambda: j(op_remotes))
    app.add_url_rule(R + "/browse", "api_browse", lambda: j(op_browse, request.args.get("path", "").strip()))
    app.add_url_rule(R + "/schedules", "api_schedules", lambda: j(op_schedules))
    app.add_url_rule(R + "/audit", "api_audit", lambda: j(op_audit, request.args.get("cat"), request.args.get("user"),
                                                          request.args.get("q"), request.args.get("from"),
                                                          request.args.get("to"), request.args.get("limit", 100)))
    app.add_url_rule(R + "/users", "api_users", lambda: j(op_users))
    app.add_url_rule(R + "/<path:rest>", "api_404", lambda rest: (jsonify({"error": f"Unbekannter Pfad: /api/v1/{rest}"}), 404),
                     methods=["GET", "POST", "PUT", "PATCH", "DELETE"])

    @app.route("/mcp", methods=["GET", "POST", "DELETE"])
    def mcp():
        if request.method != "POST":
            return jsonify({"error": "Nur POST (Streamable HTTP, JSON-Antworten)."}), 405, {"Allow": "POST"}
        origin = request.headers.get("Origin")
        if origin and origin.split("://", 1)[-1].split("/")[0] != request.host:
            return jsonify({"error": "Origin nicht erlaubt."}), 403
        msg = request.get_json(silent=True)
        if msg is None:
            return jsonify(_rpc_error(None, -32700, "Kein gültiges JSON")), 400
        if isinstance(msg, list):
            out = [r for r in (mcp_handle(m) for m in msg) if r is not None]
            return (jsonify(out), 200) if out else ("", 202)
        res = mcp_handle(msg)
        if res is None:
            return "", 202
        return jsonify(res)

    try:
        from swagger_ui_bundle import swagger_ui_path
        sw_dir = str(swagger_ui_path)
    except Exception:   # Paket fehlt: Swagger-UI vom CDN laden
        sw_dir = None

    @app.get("/api/docs")
    def api_docs():
        base = "/api/docs/static" if sw_dir else "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14"
        return core.render_template("api_docs.html", sw=base)

    @app.get("/api/docs/static/<name>")
    def api_docs_static(name):
        if not sw_dir or name not in ("swagger-ui-bundle.js", "swagger-ui.css"):
            core.abort(404)
        from flask import send_from_directory
        return send_from_directory(sw_dir, name, max_age=86400)

    @app.route("/settings/api", methods=["GET", "POST"])
    def api_keys_page():
        msg = err = new = None
        all_roles = core.role_store.load()
        grantable = {rid: r for rid, r in all_roles.items() if core.within(r)}
        if request.method == "POST":
            f = request.form
            name = f.get("name", "").strip()[:60]
            rid = f.get("role", "")
            exp = f.get("expires", "").strip()
            try:
                ips = parse_ips(f.get("ips", ""))
            except ValueError as e:
                ips, err = [], f"IP-Adresse ungültig: {e}"
            if not err and not name:
                err = "Bitte einen Namen angeben (z. B. n8n, Home Assistant, Claude)."
            elif not err and any(k.get("name") == name and not k.get("revoked") for k in keys().values()):
                err = "Einen aktiven Key mit diesem Namen gibt es schon."
            elif not err and rid not in grantable:
                err = "Diese Rolle darfst du nicht vergeben."
            elif not err and exp and (not re.match(r"^\d{4}-\d{2}-\d{2}$", exp) or exp < datetime.date.today().isoformat()):
                err = "Ablaufdatum ungültig oder in der Vergangenheit."
            if not err:
                kid, token, entry = create_key(name, rid, exp, ips, g.user, f.get("lang", ""))
                new = {"id": kid, "token": token, "name": name}
                core.audit_add("api", "API-Key erstellt", name,
                               detail=f"Rolle {all_roles[rid]['name']}" + (f", gültig bis {exp}" if exp else "") +
                                      (f", nur von {', '.join(ips)}" if ips else ""))
        grs = core.load_groups()
        rows = sorted(({"id": kid, **k, "revealable": bool(k.get("enc")), "enc": None, "hash": None, "status": key_status(k),
                        "windows_text": windows_text(k.get("windows")),
                        "group_names": [grs[x]["name"] for x in core.roles.groups_of(grs, None, kid)], "role_name": (all_roles.get(k.get("role")) or {}).get("name", k.get("role"))}
                       for kid, k in keys().items()), key=lambda r: (r["status"] != "aktiv", r["name"].lower()))
        base = (core.load_settings().get("public_url") or os.environ.get("PUBLIC_URL", "") or request.host_url).rstrip("/")
        me = core.store.get(g.user) or {} if g.get("user") else {}
        return core.render_template("api_keys.html", rows=rows, roles=grantable, msg=msg or session.pop("flash", None),
                               err=err, new=new, base=base, my_totp=bool(me.get("totp_enabled")),
                               my_pk=bool(me.get("passkeys")), can_reveal={r["id"]: core.within(all_roles.get(r.get("role"))) for r in rows})

    @app.post("/settings/api/<kid>/revoke")
    def api_key_revoke(kid):
        k = core.DB.get("apikey", kid)
        if k and not k.get("revoked"):
            k.update(revoked=True, revoked_by=g.user, revoked_at=time.strftime("%Y-%m-%d %H:%M"))
            core.DB.put("apikey", kid, k)
            core.audit_add("api", "API-Key widerrufen", k["name"])
            session["flash"] = f"API-Key „{k['name']}“ widerrufen. Er funktioniert ab sofort nicht mehr."
        return core.redirect("/settings/api")

    def _reveal_denied():
        if g.get("bridge") or g.get("api_key") or request.path.startswith(("/api/", "/mcp")):
            return "Einen API-Key anzeigen geht nur in der Web-GUI, nicht über API oder MCP."
        if not g.get("user") or g.user.startswith("API:"):
            return "Nicht angemeldet"
        return None

    @app.post("/settings/api/reveal/options")
    def api_key_reveal_options():
        """Passkey-Bestaetigung: Optionen nur fuer die Passkeys des angemeldeten Benutzers."""
        if _reveal_denied():
            return {"ok": False, "error": core.i18n.t(_reveal_denied())}, 403
        rp_id, _, problem = core._pk_rp()
        if problem:
            return {"ok": False, "error": problem}, 400
        if core._locked():
            return {"ok": False, "error": core.i18n.t("Zu viele Fehlversuche. Bitte 5 Minuten warten.")}, 429
        opts, chal = core.passkeys.authentication_options(rp_id)
        session["pk_reveal"] = {"c": chal, "t": time.time(), "rp": rp_id}
        return app.response_class(opts, mimetype="application/json")

    @app.post("/settings/api/<kid>/reveal")
    def api_key_reveal(kid):
        """Key noch einmal anzeigen: nur in der GUI, nach Passwort (+ 2FA-Code, falls aktiv) oder Passkey."""
        t = core.i18n.t
        deny = _reveal_denied()
        if deny:
            return {"ok": False, "error": t(deny)}, 403
        k = core.DB.get("apikey", kid)
        if not k:
            return {"ok": False, "error": t("Nicht gefunden.")}, 404
        if not core.within(core.role_store.get(k.get("role"))):
            return {"ok": False, "error": t("Dieser Key hat mehr Rechte als du, du kannst ihn nicht anzeigen.")}, 403
        if key_status(k) in ("widerrufen", "abgelaufen"):
            return {"ok": False, "error": t("Widerrufene oder abgelaufene Keys lassen sich nicht anzeigen.")}, 400
        if not k.get("enc"):
            return {"ok": False, "error": t("Dieser Key wurde vor Version 1.24.0 erstellt, gespeichert ist nur sein Hash. "
                                            "Er lässt sich nicht mehr anzeigen. Bei Bedarf einen neuen Key erstellen.")}, 400
        if core._locked():
            return {"ok": False, "error": t("Zu viele Fehlversuche. Bitte 5 Minuten warten.")}, 429
        data = request.get_json(silent=True) or {}
        u = core.store.get(g.user) or {}
        how = None
        if data.get("credential"):
            st = session.pop("pk_reveal", None)
            rp_id, origins, problem = core._pk_rp()
            if problem:
                return {"ok": False, "error": problem}, 400
            if not st or time.time() - st.get("t", 0) > core.passkeys.TIMEOUT_S or st.get("rp") != rp_id:
                return {"ok": False, "error": t("Die Anfrage ist abgelaufen. Bitte noch einmal versuchen.")}, 400
            cred = data["credential"]
            try:
                cid = core.passkeys.credential_id(cred)
            except Exception:
                cid = ""
            entry = next((p for p in u.get("passkeys") or [] if cid and secrets.compare_digest(p.get("id", ""), cid)), None)
            try:
                if not entry:
                    raise ValueError("fremder Passkey")
                count = core.passkeys.verify_authentication(cred, st["c"], rp_id, origins, entry)
            except Exception:
                count = None
            if count is not None:
                with core.users._lock:
                    pks = list(core.store.get(g.user).get("passkeys") or [])
                    for p in pks:
                        if p.get("id") == entry["id"]:
                            p.update(count=count, last_used=time.strftime("%Y-%m-%d %H:%M"))
                    core.store.update(g.user, passkeys=pks)
                how = "Passkey (" + entry.get("name", "") + ")"
        else:
            pw, code = str(data.get("password") or ""), str(data.get("code") or "").strip()
            if core.users.check_password(u, pw):
                if not u.get("totp_enabled"):
                    how = "Passwort"
                else:
                    counter = core.users.verify_totp(u.get("totp_secret"), code, u.get("totp_last", 0))
                    if counter:
                        core.store.update(g.user, totp_last=counter)
                        how = "Passwort + 2FA"
                    else:
                        rest = core.users.use_backup_code(u, code)
                        if rest is not None:
                            core.store.update(g.user, backup_codes=rest)
                            how = "Passwort + Backup-Code"
        if not how:
            core._fail()
            core.audit_add("api", "API-Key anzeigen abgelehnt", k["name"], detail="Bestätigung falsch")
            msg = "Bestätigung fehlgeschlagen: Passkey ungültig." if data.get("credential") else \
                ("Passwort oder 2FA-Code falsch." if u.get("totp_enabled") else "Passwort falsch.")
            return {"ok": False, "error": t(msg)}, 403
        token = unseal(k["enc"])
        if not token or not hmac.compare_digest(_hash(token), k.get("hash", "")):
            return {"ok": False, "error": t("Der Key lässt sich auf dieser Installation nicht entschlüsseln (z. B. nach einem Import "
                                            "oder wenn config/secret_key ersetzt wurde). Bei Bedarf einen neuen Key erstellen.")}, 400
        core.audit_add("api", "API-Key angezeigt", k["name"], detail=f"bestätigt mit {how}")
        resp = jsonify({"ok": True, "token": token})
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.route("/settings/api/<kid>/edit", methods=["GET", "POST"])
    def api_key_edit(kid):
        k = core.DB.get("apikey", kid)
        if not k:
            core.abort(404)
        all_roles = core.role_store.load()
        grantable = {rid: r for rid, r in all_roles.items() if core.within(r)}
        if not core.within(all_roles.get(k.get("role"))):
            core._flash_err("Dieser Key hat mehr Rechte als du, du kannst ihn nicht bearbeiten.")
            return core.redirect("/settings/api")
        if k.get("revoked"):
            core._flash_err("Ein widerrufener Key lässt sich nicht mehr bearbeiten.")
            return core.redirect("/settings/api")
        err = None
        key = dict(k)
        if request.method == "POST":
            f = request.form
            key.update(name=f.get("name", "").strip()[:60], role=f.get("role", ""), expires=f.get("expires", "").strip(),
                       disabled=f.get("active") == "0",
                       lang=f.get("lang", "") if core.i18n.valid(f.get("lang", "")) else "",
                       lock_from=f.get("lock_from", "").strip()[:16] if f.get("lock") else "",
                       lock_until=f.get("lock_until", "").strip()[:16] if f.get("lock") else "")
            try:
                key["ips"] = parse_ips(f.get("ips", ""))
            except ValueError as e:
                err = core.i18n.t("IP-Adresse ungültig: {0}", e)
            wins, werr = clean_windows([{"days": f.getlist(f"w{i}_d"), "start": f.get(f"w{i}_s", ""), "end": f.get(f"w{i}_e", "")}
                                        for i in range(10) if f"w{i}_s" in f or f"w{i}_d" in f]) if f.get("win_on") else ([], None)
            key["windows"] = wins
            dt_ok = lambda v: not v or re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", v)
            if err:
                pass
            elif werr:
                err = werr
            elif f.get("win_on") and not wins:
                err = "Bitte mindestens ein Zeitfenster angeben oder „Nur zu bestimmten Zeiten“ ausschalten."
            elif not key["name"]:
                err = "Bitte einen Namen angeben (z. B. n8n, Home Assistant, Claude)."
            elif any(x.get("name") == key["name"] and not x.get("revoked") and xid != kid for xid, x in keys().items()):
                err = "Einen aktiven Key mit diesem Namen gibt es schon."
            elif key["role"] not in grantable:
                err = "Diese Rolle darfst du nicht vergeben."
            elif key["expires"] and not re.match(r"^\d{4}-\d{2}-\d{2}$", key["expires"]):
                err = "Ablaufdatum ungültig oder in der Vergangenheit."
            elif not dt_ok(key["lock_from"]) or not dt_ok(key["lock_until"]):
                err = "Sperrzeitraum: bitte Datum und Uhrzeit angeben."
            elif f.get("lock") and not (key["lock_from"] or key["lock_until"]):
                err = "Sperrzeitraum: bitte mindestens „gesperrt ab“ oder „wieder aktiv ab“ angeben."
            elif key["lock_from"] and key["lock_until"] and key["lock_until"] <= key["lock_from"]:
                err = "Sperrzeitraum: „wieder aktiv ab“ muss nach „gesperrt ab“ liegen."
            elif g.get("api_key") == kid and (key["disabled"] or key["lock_from"] or key["lock_until"] or key["windows"] or key["role"] != k.get("role")):
                err = "Den API-Key, mit dem du gerade zugreifst, kannst du nicht deaktivieren, pausieren, zeitlich beschränken oder umstufen."
            if not err:
                cur = core.DB.get("apikey", kid) or k
                cur.update({x: key[x] for x in ("name", "role", "expires", "ips", "disabled", "lock_from", "lock_until", "windows", "lang")})
                core.DB.put("apikey", kid, cur)
                if g.access.has("groups.manage") and f.get("grp_form"):
                    grs = core.load_groups()
                    want = set(f.getlist("grp"))
                    for gid, x in grs.items():
                        if not core.group_within(x):
                            continue
                        ks = [y for y in x.get("keys") or [] if y != kid]
                        if gid in want:
                            ks.append(kid)
                        x["keys"] = ks
                    core.save_groups(grs)
                session["flash"] = core.i18n.t("API-Key „{0}“ gespeichert.", key["name"])
                return core.redirect("/settings/api")
        grs = core.load_groups()
        return core.render_template("api_key_edit.html", kid=kid, key=key, err=err, roles=grantable, status=key_status(key),
                                    owner=key.get("created_by") or "",
                                    all_groups=[(gid, dict(x, editable=core.group_within(x))) for gid, x in
                                                sorted(grs.items(), key=lambda kv: kv[1].get("name", "").lower())],
                                    my_groups=core.roles.groups_of(grs, None, kid))

    @app.post("/settings/api/<kid>/delete")
    def api_key_delete(kid):
        """Key ganz entfernen (auch aus Gruppen). Audit-Log und Anmeldeverlauf behalten seine Eintraege."""
        k = core.DB.get("apikey", kid)
        if not k:
            core.abort(404)
        if g.get("api_key") == kid:
            core._flash_err("Den API-Key, mit dem du gerade zugreifst, kannst du nicht löschen.")
            return core.redirect("/settings/api")
        all_k = keys()
        all_k.pop(kid, None)
        core.DB.put_map("apikey", all_k)
        grs = core.load_groups()
        if any(kid in (x.get("keys") or []) for x in grs.values()):
            for x in grs.values():
                x["keys"] = [y for y in x.get("keys") or [] if y != kid]
            core.save_groups(grs)
        core.audit_add("api", "API-Key gelöscht", k["name"], detail=f"msk_{kid}_…, " + key_status(k))
        session["flash"] = core.i18n.t("API-Key „{0}“ gelöscht.", k["name"])
        return core.redirect("/settings/api")
