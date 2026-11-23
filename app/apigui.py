"""REST-API und MCP: alles, was die GUI kann (ab 1.21.0).

Schreibende Aktionen laufen ueber gui(): ein interner Aufruf derselben Seite wie in der GUI, mit der Identitaet und den
Rechten des API-Keys. Dadurch gelten genau dieselben Pruefungen (Rechte, Beschraenkung auf Aufgaben/Speicherorte,
keine Rechteausweitung, letzter Admin, nicht selbst aussperren, Zeitplan-/Pfadpruefungen) und dasselbe Audit-Log.
Lesende Aktionen liefern die Daten direkt, Geheimnisse (Passwoerter, Tokens, Apprise-URLs, Schluessel) nie –
sie koennen nur gesetzt werden (write-only)."""
import base64
import io
import json
import re

from flask import Response, g, has_request_context, jsonify, request
from werkzeug.datastructures import MultiDict

import api
from api import ApiError, _schema, need

core = None
ACTIONS = []
ADMIN = "role:admin"      # Sicherung, Export und Import: wie in der GUI nur die Rolle Admin


# ---------------------------------------------------------------- interner GUI-Aufruf
def gui(method, path, form=None, js=None, files=None, client=None):
    br = {"user": g.user, "role": g.role, "access": g.access, "lang": g.get("user_lang") or "",
          "key": g.get("api_key"), "out": {},
          "via": "MCP" if has_request_context() and request.path.startswith("/mcp") else "REST-API"}
    data = None
    if form is not None or files:
        data = MultiDict()
        for k, v in (form or {}).items():
            if v is None or v is False:
                continue
            for x in (v if isinstance(v, (list, tuple)) else [v]):
                data.add(k, "on" if x is True else str(x))
        for k, (fname, blob) in (files or {}).items():
            data.add(k, (io.BytesIO(blob), fname))
    saved = dict(g.__dict__)
    c = client or core.app.test_client()
    try:
        resp = c.open(path, method=method, data=data, json=js,
                      environ_base={"REMOTE_ADDR": core._client_ip(), "mirrorsync.bridge": br})
    finally:   # g gehoert zum gemeinsamen App-Kontext: Zustand der aeusseren Anfrage wiederherstellen
        g.__dict__.clear()
        g.__dict__.update(saved)
        if g.get("audit_snap"):   # schon vom inneren Aufruf protokolliert, nicht doppelt
            g.audit_snap = {c: json.loads(json.dumps(core.AUDIT_SNAP[c]())) for c in g.audit_snap}
    return {"status": resp.status_code, "out": br["out"], "resp": resp}


def _t(text):
    return core.i18n.translate(str(text)) if text else text


def done(r):
    """Ergebnis eines GUI-Aufrufs auswerten: Fehler -> ApiError, sonst Meldung (Text)."""
    out, st, resp = r["out"], r["status"], r["resp"]
    body = resp.get_json(silent=True) if resp.mimetype == "application/json" else None
    if out.get("denied") or st == 403 or "denied.html" in out.get("pages", []):
        perm = out.get("denied")
        raise ApiError(403, _t("Keine Berechtigung") + (f" ({perm})" if perm and perm != "scope" else ""))
    if st == 404:
        raise ApiError(404, _t("Nicht gefunden."))
    err = out.get("err")
    fa = out.get("flash_access")
    if not err and isinstance(fa, (list, tuple)) and fa and fa[0] == "err":
        err = fa[1]
    if not err and isinstance(body, dict) and body.get("ok") is False:
        err = body.get("error") or "Fehler"
    if err:
        raise ApiError(400, _t(err))
    if st >= 400:
        raise ApiError(st, _t((body or {}).get("error") or f"HTTP {st}"))
    msg = out.get("msg") or out.get("flash") or (fa[1] if isinstance(fa, (list, tuple)) and fa else "")
    return _t(msg) if msg else ""


def ok(r, **extra):
    msg = done(r)
    return dict({"ok": True, "message": msg}, **extra)


def action(tool, method, path, perm, tag, summary, props=None, required=None, ro=False, files=False):
    def deco(fn):
        ACTIONS.append(dict(tool=tool, method=method, path=path, perm=perm, tag=tag, summary=summary,
                            props=props or {}, required=required or [], ro=ro, fn=fn, files=files))
        return fn
    return deco


def need_any(perm):
    if perm == ADMIN:
        if g.role != "admin":
            raise ApiError(403, _t("Keine Berechtigung") + " (admin)")
    elif perm:
        need(perm)


def _bool(v):
    return v if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes", "ja", "on")


def _lines(v):
    if v is None:
        return ""
    return "\n".join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v)


def _check_keys(data, allowed):
    bad = [k for k in data if k not in allowed and not k.startswith("_")]
    if bad:
        raise ApiError(400, core.i18n.t("Unbekanntes Feld: {0}", bad[0]))


S = lambda t, d="", **kw: dict({"type": t, "description": d} if d else {"type": t}, **kw)
STR, BOOL, INT, NUM, ARR = "string", "boolean", "integer", "number", "array"
STRS = {"type": "array", "items": {"type": "string"}}


# ================================================================= Aufgaben (Ergaenzungen)
@action("test_job_notification", "POST", "/jobs/{job_id}/notify-test", "jobs.notify", "Aufgaben",
        "Testnachricht mit den gespeicherten Benachrichtigungen einer Aufgabe senden.",
        {"job_id": S(STR)}, ["job_id"])
def a_job_notify_test(a):
    jid = a["job_id"]
    j = api._job(jid)
    form = {k: j.get(k) for k in core.notify.JOB_FIELDS if k not in ("notify_telegram_token", "notify_apprise_urls")}
    form.update(name=j["name"], source=j["source"], dest=j["dest"])
    if j.get("msg_tpl_on"):
        form["msg_tpl_on"] = True
        for ev, t in (j.get("msg_tpl") or {}).items():
            for k in ("title", "body"):
                if t.get(k):
                    form[f"jtpl_{ev}_{k}"] = t[k]
    r = gui("POST", f"/job/{jid}/notify-test", form=form)
    body = r["resp"].get_json(silent=True)
    if not isinstance(body, dict):
        done(r)
        body = {}
    if r["status"] >= 400:
        done(r)
    res = {"ok": bool(body.get("ok")), "results": {k: (None if v is None else _t(v)) for k, v in (body.get("results") or {}).items()}}
    if body.get("error"):
        res["message"] = _t(body["error"])
    return res


# ================================================================= Zeitplaene und Ketten
@action("set_job_trigger", "POST", "/schedules/jobs/{job_id}", "jobs.edit", "Zeitpläne",
        "Startart einer Aufgabe ändern: time (schedule), after (after_job, when ok|always), live (mode, interval, full) oder manual.",
        {"job_id": S(STR), "trigger": S(STR, enum=["time", "after", "live", "manual"]), "schedule": S(STR, "Cron, z. B. 0 3 * * *"),
         "enabled": S(BOOL), "after_job": S(STR), "when": S(STR, enum=["ok", "always"]), "interval": S(INT, "Minuten"),
         "full": S(STR, "Nur bei mode=fast: voller Abgleich als Cron (0 3 * * *) oder Intervall (@every 6h, @every 90m)"),
         "mode": S(STR, "Live: mirror = jede Runde wie Spiegeln inkl. Löschen, fast = nur neue/geänderte Dateien", enum=["mirror", "fast"])}, ["job_id", "trigger"])
def a_set_trigger(a):
    jid = a.pop("job_id")
    api._job(jid)
    r = gui("POST", f"/schedules/job/{jid}", js=a)
    done(r)
    return api.public_job(jid, core.load_jobs()[jid])


@action("set_chains", "PUT", "/schedules/chains", "jobs.edit", "Zeitpläne",
        "Reihenfolge der Ketten setzen: chains=[{root, items:[{id, when ok|always, enabled}]}]. Nicht genannte Folgeaufgaben werden manuell.",
        {"chains": {"type": "array", "items": {"type": "object"}}}, ["chains"])
def a_set_chains(a):
    r = gui("POST", "/schedules/chains", js={"chains": a.get("chains") or []})
    done(r)
    body = r["resp"].get_json(silent=True) or {}
    return {"ok": True, "changed": body.get("changed", [])}


# ================================================================= Speicherorte
SECRET_OPT = re.compile(r"(pass|secret|token|credentials|sas_url|private|^key$|_key$|api_key|access_key)", re.I)


def _sensitive(typ):
    """Optionen, die nie ausgegeben werden: Passwoerter (IsPassword) und Schluessel/Tokens nach Namen."""
    prov = next((p for p in core.providers() if p["name"] == typ), {"options": []})
    return {o["Name"] for o in prov["options"] if o.get("IsPassword") or (o.get("Sensitive") and SECRET_OPT.search(o["Name"]))} \
        | {"token"}


def _remote_view(name):
    conf = core.remote_config(name)
    if conf is None or not g.access.remote_ok(name):
        raise ApiError(404, core.i18n.t("Speicherort {0} nicht gefunden.", name))
    sec = _sensitive(conf.get("type"))
    q = core._pending.get(name)
    return {"name": name, "type": conf.get("type"),
            "options": {k: v for k, v in conf.items() if k not in sec and k != "type"},
            "secrets_set": sorted(k for k in conf if k in sec),
            "visible_to": core.remote_vis_map().get(name, "all"),
            "pending_question": _question(q)}


VIS_PROP = {"description": "\"all\" (alle mit Recht) oder Liste aus user:<Name> und group:<Gruppen-ID>; Admins sehen immer alles"}


def _vis_form(form, v):
    if v is None or v == "all":
        form["vis_mode"] = "all"
    elif isinstance(v, list):
        form["vis_mode"] = "some"
        form["vis"] = [str(x) for x in v]
    else:
        raise ApiError(400, _t("visible_to muss \"all\" oder eine Liste sein."))
    return form


def _question(q):
    if not q:
        return None
    o = q.get("Option") or {}
    return {"name": o.get("Name"), "help": o.get("Help"), "default": o.get("DefaultStr"),
            "examples": [e.get("Value") for e in (o.get("Examples") or [])], "required": o.get("Required"),
            "is_password": o.get("IsPassword")}


@action("get_remote", "GET", "/remotes/{name}", "remotes.view", "Speicherorte",
        "Ein Speicherort mit seinen Einstellungen (ohne Passwörter/Tokens) und einer offenen Rückfrage der Einrichtung.",
        {"name": S(STR)}, ["name"], ro=True)
def a_get_remote(a):
    need("remotes.view")
    return _remote_view(a["name"])


@action("list_remote_types", "GET", "/remote-types", "remotes.view", "Speicherorte",
        "Alle Speicherarten (rclone) mit ihren Optionen, für create_remote.", {"type": S(STR, "nur diese Art")}, ro=True)
def a_remote_types(a):
    need("remotes.view")
    out = []
    for p in core.providers():
        if a.get("type") and p["name"] != a["type"]:
            continue
        out.append({"name": p["name"], "label": _t(p["label"]), "oauth": p["oauth"],
                    "options": [{"name": o["Name"], "help": (o.get("Help") or "").split("\n")[0], "required": o.get("Required"),
                                 "secret": bool(o.get("IsPassword") or (o.get("Sensitive") and SECRET_OPT.search(o["Name"]))), "advanced": o.get("Advanced"),
                                 "default": o.get("DefaultStr"), "provider": o.get("Provider") or None} for o in p["options"]]
                    if a.get("type") else len(p["options"])})
    return out


def _remote_result(r, name):
    msg = done(r)
    res = {"ok": True, "message": msg, "name": name}
    q = core._pending.get(name)
    if q:
        res["pending_question"] = _question(q)
        res["message"] = _t("Die Einrichtung braucht noch eine Antwort, siehe pending_question (answer_remote).")
    return res


@action("create_remote", "POST", "/remotes", "remotes.create", "Speicherorte",
        "Speicherort anlegen. options = rclone-Optionen, z. B. {host, user, pass}. Passwörter werden verschleiert gespeichert.",
        {"name": S(STR), "type": S(STR, "z. B. smb, sftp, webdav, s3, drive"), "options": {"type": "object"}, "visible_to": VIS_PROP},
        ["name", "type"])
def a_create_remote(a):
    _check_keys(a, ("name", "type", "options", "visible_to"))
    form = _vis_form({"name": a.get("name", ""), "type": a.get("type", "")}, a.get("visible_to"))
    for k, v in (a.get("options") or {}).items():
        form[f"opt_{k}"] = "true" if v is True else "false" if v is False else str(v)
    return _remote_result(gui("POST", "/remotes/new", form=form), a.get("name", ""))


@action("update_remote", "PATCH", "/remotes/{name}", "remotes.edit", "Speicherorte",
        "Optionen eines Speicherorts ändern (nur die angegebenen; Passwörter nur setzen) und/oder visible_to.",
        {"name": S(STR), "options": {"type": "object"}, "visible_to": VIS_PROP}, ["name"])
def a_update_remote(a):
    _check_keys(a, ("name", "options", "visible_to"))
    name = a["name"]
    _remote_view(name)
    form = {f"opt_{k}": ("true" if v is True else "false" if v is False else str(v)) for k, v in (a.get("options") or {}).items()}
    _vis_form(form, a["visible_to"] if "visible_to" in a else core.remote_vis_map().get(name, "all"))
    return _remote_result(gui("POST", f"/remotes/{name}/edit", form=form), name)


@action("answer_remote", "POST", "/remotes/{name}/answer", "remotes.edit", "Speicherorte",
        "Offene Rückfrage der Einrichtung beantworten (z. B. OAuth-Token aus 'rclone authorize').",
        {"name": S(STR), "result": S(STR)}, ["name", "result"])
def a_answer_remote(a):
    name = a["name"]
    if not core._pending.get(name):
        raise ApiError(409, _t("Für diesen Speicherort ist keine Rückfrage offen."))
    return _remote_result(gui("POST", f"/remotes/{name}/wizard", form={"result": a.get("result", "")}), name)


@action("reauth_remote", "POST", "/remotes/{name}/auth", "remotes.edit", "Speicherorte",
        "Browser-Anmeldung (OAuth) neu starten; danach pending_question mit answer_remote beantworten.",
        {"name": S(STR)}, ["name"])
def a_reauth_remote(a):
    return _remote_result(gui("POST", f"/remotes/{a['name']}/auth", form={}), a["name"])


@action("test_remote", "POST", "/remotes/{name}/test", "remotes.test", "Speicherorte",
        "Verbindung eines Speicherorts testen (listet die Ordner der obersten Ebene, bei SFTP und FTP das "
        "Stammverzeichnis /).", {"name": S(STR)}, ["name"])
def a_test_remote(a):
    r = gui("POST", f"/remotes/{a['name']}/test", form={})
    try:
        msg = done(r)
        return {"ok": True, "message": msg}
    except ApiError as e:
        if e.status == 400:
            return {"ok": False, "message": e.msg}
        raise


@action("delete_remote", "DELETE", "/remotes/{name}", "remotes.delete", "Speicherorte",
        "Speicherort löschen. Nicht umkehrbar.", {"name": S(STR)}, ["name"])
def a_delete_remote(a):
    name = a["name"]
    if core.remote_config(name) is None:
        raise ApiError(404, core.i18n.t("Speicherort {0} nicht gefunden.", name))
    return ok(gui("POST", f"/remotes/{name}/delete", form={}), deleted=name)


# ================================================================= Benachrichtigungen und Vorlagen
def _notify_view():
    s = core.load_settings()
    out = {k: s.get(k, d) for k, d in core.notify.DEFAULTS.items() if k not in core.notify.SECRET_FIELDS}
    for k in core.notify.SECRET_FIELDS:
        out[f"{k}_set"] = bool(s.get(k))
    out["apprise_urls_masked"] = [core.notify.mask_url(u) for u in core.notify.apprise_list(s.get("apprise_urls"))]
    return out


@action("get_notifications", "GET", "/settings/notifications", "notify.view", "Benachrichtigungen",
        "Standard-Benachrichtigungen (Webhook, E-Mail, Telegram, Apprise). Geheimnisse nur als *_set.", ro=True)
def a_get_notify(a):
    need("notify.view")
    return _notify_view()


@action("update_notifications", "PATCH", "/settings/notifications", "notify.edit", "Benachrichtigungen",
        "Benachrichtigungen ändern (nur angegebene Felder). when: always|fail|never. Geheimnisse (smtp_pass, telegram_token, "
        "apprise_urls, apprise_api_key) nur setzen; leerer Text löscht sie.", {"fields": {"type": "object"}}, ["fields"])
def a_update_notify(a):
    ch = a.get("fields") or {}
    if not isinstance(ch, dict):
        raise ApiError(400, _t("JSON-Objekt erwartet."))
    _check_keys(ch, core.notify.DEFAULTS)
    return {"ok": True, "message": _save_notify(ch), "settings": _notify_view()}


def _save_notify(ch, test=None):
    s = core.load_settings()
    form = {}
    for k, d in core.notify.DEFAULTS.items():
        v = ch.get(k, s.get(k, d))
        if isinstance(d, bool):
            form[k] = _bool(v)
        elif k in core.notify.SECRET_FIELDS:
            if k in ch:
                if str(_lines(ch[k])).strip():
                    form[k] = _lines(ch[k])
                else:
                    form[k + "_clear"] = True
        else:
            form[k] = "" if v is None else str(v)
    if test:
        form["test"] = test
    return done(gui("POST", "/settings", form=form))


@action("test_notification", "POST", "/settings/notifications/test", "notify.edit", "Benachrichtigungen",
        "Testnachricht über einen Kanal senden: webhook, smtp, telegram oder apprise.",
        {"channel": S(STR, enum=["webhook", "smtp", "telegram", "apprise"])}, ["channel"])
def a_test_notify(a):
    if a.get("channel") not in core.notify.CHANNELS:
        raise ApiError(400, _t("Unbekannter Kanal."))
    try:
        return {"ok": True, "message": _save_notify({}, test=a["channel"])}
    except ApiError as e:
        if e.status == 400:
            return {"ok": False, "message": e.msg}
        raise


# Kanal einrichten: kurze Feldnamen je Kanal -> Einstellungen
CHANNEL_FIELDS = {
    "webhook": {"url": "webhook_url", "method": "webhook_method", "body": "webhook_body"},
    "smtp": {"host": "smtp_host", "port": "smtp_port", "security": "smtp_security", "user": "smtp_user",
             "password": "smtp_pass", "from": "smtp_from", "to": "smtp_to"},
    "telegram": {"token": "telegram_token", "chat_id": "telegram_chat_id"},
    "apprise": {"mode": "apprise_mode", "urls": "apprise_urls", "api_url": "apprise_api_url", "api_key": "apprise_api_key",
                "tag": "apprise_tag"},
}
CHANNEL_PROPS = {
    "channel": S(STR, "webhook, smtp (E-Mail), telegram oder apprise", enum=["webhook", "smtp", "telegram", "apprise"]),
    "enabled": S(BOOL, "Kanal einschalten (Standard: true)"),
    "url": S(STR, "webhook: Adresse"), "method": S(STR, "webhook: POST oder PUT", enum=["POST", "PUT"]),
    "body": S(STR, "webhook: eigener Body (leer = Standard-JSON)"),
    "host": S(STR, "smtp: Server"), "port": S(INT, "smtp: Port, z. B. 587"),
    "security": S(STR, "smtp: starttls, ssl oder none", enum=["starttls", "ssl", "none"]),
    "user": S(STR, "smtp: Benutzer"), "password": S(STR, "smtp: Passwort (wird nur gesetzt, nie angezeigt)"),
    "from": S(STR, "smtp: Absender"), "to": S(STR, "smtp: Empfänger, mehrere mit Komma"),
    "token": S(STR, "telegram: Bot-Token (wird nur gesetzt, nie angezeigt)"), "chat_id": S(STR, "telegram: Chat-ID"),
    "mode": S(STR, "apprise: lib = URLs direkt senden, api = über einen Apprise-API-Server", enum=["lib", "api"]),
    "urls": dict(STRS, description="apprise: URLs (ersetzt die vorhandenen)"),
    "add_urls": dict(STRS, description="apprise: URLs zu den vorhandenen hinzufügen"),
    "api_url": S(STR, "apprise: Adresse des Apprise-API-Servers"), "api_key": S(STR, "apprise: Schlüssel/Konfiguration (wird nur gesetzt)"),
    "tag": S(STR, "apprise: Tag"),
    "test": S(BOOL, "danach gleich eine Testnachricht über diesen Kanal senden"),
}


@action("setup_notification_channel", "POST", "/settings/notifications/channels/{channel}", "notify.edit", "Benachrichtigungen",
        "Benachrichtigungs-Kanal anlegen bzw. einrichten (webhook, smtp, telegram, apprise) und einschalten. Nur die angegebenen "
        "Felder werden geändert. Mit test=true wird gleich eine Testnachricht gesendet. Wann benachrichtigt wird (when) steht in update_notifications.",
        CHANNEL_PROPS, ["channel"])
def a_setup_channel(a):
    ch = a.get("channel")
    if ch not in CHANNEL_FIELDS:
        raise ApiError(400, _t("Unbekannter Kanal."))
    allowed = set(CHANNEL_FIELDS[ch]) | {"channel", "enabled", "test"} | ({"add_urls"} if ch == "apprise" else set())
    _check_keys(a, allowed)
    fields = {f"{ch}_enabled": _bool(a.get("enabled", True))}
    for short, key in CHANNEL_FIELDS[ch].items():
        if short in a:
            fields[key] = a[short]
    if a.get("add_urls"):
        have = core.notify.apprise_list(_lines(fields.get("apprise_urls")) if "apprise_urls" in fields else core.load_settings().get("apprise_urls"))
        add = a["add_urls"] if isinstance(a["add_urls"], list) else [a["add_urls"]]
        fields["apprise_urls"] = have + [str(u).strip() for u in add if str(u).strip() and str(u).strip() not in have]
    test = None
    if _bool(a.get("test", False)):
        test = ch
    try:
        msg = _save_notify(fields, test=test)
    except ApiError as e:
        if test and e.status == 400:
            return {"ok": False, "message": e.msg, "settings": _notify_view()}
        raise
    return {"ok": True, "message": msg, "settings": _notify_view()}


@action("remove_notification_channel", "DELETE", "/settings/notifications/channels/{channel}", "notify.edit", "Benachrichtigungen",
        "Benachrichtigungs-Kanal ausschalten. forget=true löscht zusätzlich die gespeicherten Zugangsdaten und Adressen des Kanals.",
        {"channel": CHANNEL_PROPS["channel"], "forget": S(BOOL, "Zugangsdaten und Adressen löschen")}, ["channel"])
def a_remove_channel(a):
    ch = a.get("channel")
    if ch not in CHANNEL_FIELDS:
        raise ApiError(400, _t("Unbekannter Kanal."))
    fields = {f"{ch}_enabled": False}
    if _bool(a.get("forget", False)):
        for key in CHANNEL_FIELDS[ch].values():
            d = core.notify.DEFAULTS[key]
            fields[key] = "" if key in core.notify.SECRET_FIELDS else d
    return {"ok": True, "message": _save_notify(fields), "settings": _notify_view()}


def _templates_view():
    s = core.load_settings()
    d = core.msgtpl.editor_data(list(core.msgtpl.EVENTS), s.get("msg_templates"))
    return {"events": {ev: {"label": v["label"], "title": v["title"], "body": v["body"], "custom": v["custom"],
                            "default": v["default"], "variables": dict(v["vars"])} for ev, v in d.items()},
            "webhook_body": s.get("webhook_body", "")}


@action("get_templates", "GET", "/settings/templates", "notify.view", "Benachrichtigungen",
        "Vorlagen für Betreff und Text je Ereignis (mit Standard und Variablen) und eigener Webhook-Body.", ro=True)
def a_get_templates(a):
    need("notify.view")
    return _templates_view()


@action("update_templates", "PATCH", "/settings/templates", "notify.edit", "Benachrichtigungen",
        "Vorlagen ändern: events={run_fail: {title, body}, …}; null oder leerer Text = Standard. webhook_body optional.",
        {"events": {"type": "object"}, "webhook_body": S(STR)})
def a_update_templates(a):
    ev_in = a.get("events") or {}
    unknown = [e for e in ev_in if e not in core.msgtpl.EVENTS]
    if unknown:
        raise ApiError(400, core.i18n.t("Unbekanntes Ereignis: {0}", unknown[0]))
    s = core.load_settings()
    cur = s.get("msg_templates") or {}
    form = {k: (s.get(k, d) if isinstance(d, bool) else (s.get(k, d) or "")) for k, d in core.notify.DEFAULTS.items()
            if k not in core.notify.SECRET_FIELDS}
    form["tpl_present"] = "1"
    form["webhook_body"] = a["webhook_body"] if "webhook_body" in a else s.get("webhook_body", "")
    for ev in core.msgtpl.EVENTS:
        for k in ("title", "body"):
            if ev in ev_in:
                v = (ev_in[ev] or {}).get(k) if isinstance(ev_in[ev], dict) or ev_in[ev] is None else None
                if ev_in[ev] is not None and k not in (ev_in[ev] or {}):
                    v = (cur.get(ev) or {}).get(k)
            else:
                v = (cur.get(ev) or {}).get(k)
            form[f"tpl_{ev}_{k}"] = v or core.msgtpl.default(ev, k)
    msg = done(gui("POST", "/settings", form=form))
    return {"ok": True, "message": msg, "templates": _templates_view()}


# ================================================================= Vorschau der Ordnerstruktur
PREVIEW_PROPS = {
    "source": S(STR, "Quelle (überschreibt die gespeicherte)"), "dest": S(STR, "Ziel (überschreibt das gespeicherte)"),
    "selection": dict(STRS, description="nur diese Dateien/Ordner (relativ zur Quelle, Ordner mit / am Ende)"),
    "excludes": dict(STRS, description="Ausschlüsse"), "include_source_dir": S(BOOL, "Quellordner selbst mitkopieren"),
    "direction": S(STR, "mirror oder bisync", enum=["mirror", "bisync"]), "delete_excluded": S(BOOL, "Ausgeschlossenes im Ziel löschen"),
    "tree": S(BOOL, "zusätzlich den Baum als JSON liefern (sonst nur Text und Zusammenfassung)"),
    "path": S(STR, "Ordner im Ziel wie im Datei-Browser öffnen (relativ zum Ziel, z. B. Fotos/2024): liefert entries mit "
                   "name, dir, status, size, modified und bei Ordnern counts; leer = oberste Ebene. Mit ../ geht es über "
                   "das Ziel hinaus bis zum Stammverzeichnis (echte Ordner, so wie sie jetzt sind, braucht remotes.browse)"),
    "only_changes": S(BOOL, "nur Einträge zeigen, die sich ändern (neu, aktualisiert, gelöscht, nach A)"),
    "result": S(BOOL, "Ergebnis-Ansicht: das Ziel so, wie es nach dem Lauf aussieht, Gelöschtes fehlt (gilt für text, entries und tree)"),
}


def _pv_split(dest):
    """'NAS:a/b' -> ('NAS:', ['a', 'b']); '/data/x' -> ('/', ['data', 'x'])."""
    dest = (dest or "").rstrip("/")
    if dest.startswith("/"):
        base, rest = "/", dest[1:]
    else:
        i = dest.find(":")
        base = dest[:i + 1] + ("/" if dest[i + 1:].startswith("/") else "")
        rest = dest[len(base):]
    return base, [x for x in rest.split("/") if x]


def _pv_resolve(dest, path):
    """Pfad relativ zum Ziel (auch mit ..) -> (base, absolute Teile, innerhalb des Ziels?)."""
    base, segs = _pv_split(dest)
    cur = list(segs)
    for part in (path or "").strip("/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not cur:
                raise ApiError(400, _t("Höher als das Stammverzeichnis geht es nicht."))
            cur.pop()
        else:
            cur.append(part)
    return base, cur, cur[:len(segs)] == segs


def _pv_outside(dest, base, cur):
    """Echter Ordner oberhalb/neben dem Ziel (nur lesen), der Weg zum Ziel ist markiert."""
    from urllib.parse import urlencode
    r = gui("GET", "/browse/list?" + urlencode({"path": base + "/".join(cur)}))
    d = r["resp"].get_json(silent=True) or {}
    _, segs = _pv_split(dest)
    if r["status"] == 200 and d.get("ok") is False and cur == segs[:len(cur)]:
        d = {"entries": []}   # Ordner auf dem Weg zum Ziel gibt es noch nicht, er wird beim Lauf angelegt
    elif r["status"] >= 400 or d.get("ok") is False:
        raise ApiError(r["status"] if r["status"] >= 400 else 400, _t(d.get("error") or "Fehler"))
    out = [{"name": e["name"], "dir": e["dir"], "status": "outside", "size": e.get("size"), "modified": e.get("mod") or None}
           for e in d.get("entries", [])]
    if cur == segs[:len(cur)] and len(cur) < len(segs):
        nxt = segs[len(cur)]
        hit = next((e for e in out if e["dir"] and e["name"] == nxt), None)
        if hit is None:
            hit = {"name": nxt, "dir": True, "status": "missing", "size": None, "modified": None}
            out.append(hit)
        hit["target"] = "dest" if len(cur) == len(segs) - 1 else "way"
    return out


def _pv_folder(root, path, only):
    """Einen Ordner des Vorschau-Baums wie im Datei-Browser auflisten."""
    node, parts = root, [x for x in (path or "").strip("/").split("/") if x]
    for i, part in enumerate(parts):
        nxt = next((k for k in node.get("ch", []) if k["d"] and k["n"] == part), None)
        if nxt is None:
            raise ApiError(404, _t("Ordner {0} gibt es in der Vorschau nicht.").replace("{0}", "/".join(parts[:i + 1])))
        node = nxt

    def changed(k):
        return k["s"] != "same" or (k["d"] and any(k["c"].get(x) for x in ("new", "update", "delete", "to_a")))
    out = []
    for k in node.get("ch", []):
        if only and not changed(k):
            continue
        e = {"name": k["n"], "dir": k["d"], "status": k["s"]}
        if k["d"]:
            e["counts"] = k["c"]
            e["size"] = sum(v for x, v in k["b"].items() if x != "delete")
        else:
            e["size"] = k.get("size", 0)
            e["modified"] = k.get("m") or None
        out.append(e)
    return "/".join(parts), out


def _preview(path, a):
    _check_keys(a, set(PREVIEW_PROPS) | {"job_id"})
    a = dict(a)
    folder, only = a.pop("path", None), _bool(a.pop("only_changes", False))
    res = _bool(a.pop("result", False))
    form = None
    if "source" in a or "dest" in a:
        if "job_id" in a:
            saved = core.load_jobs().get(a["job_id"]) or {}
            base = {k: saved.get(k) for k in core.PREVIEW_KEYS}
        else:
            base = {}
        base.update({k: a[k] for k in core.PREVIEW_KEYS if k in a})
        form = {"source": base.get("source") or "", "dest": base.get("dest") or "",
                "selection": _lines(base.get("selection")), "excludes": _lines(base.get("excludes")),
                "include_source_dir": _bool(base.get("include_source_dir") or False),
                "direction": base.get("direction") or "mirror", "delete_excluded": _bool(base.get("delete_excluded") or False)}
    r = gui("POST", path, form=form or {})
    body = r["resp"].get_json(silent=True) or {}
    if r["status"] in (400, 404) and body.get("error"):
        raise ApiError(r["status"], _t(body["error"]))
    done(r)
    out = {k: body.get(k) for k in ("source", "dest", "mode", "dest_missing", "selection", "summary", "truncated")}
    tree = core.preview.result_tree(body["tree"]) if res else body["tree"]
    out["view"] = "result" if res else "changes"
    out["text"] = core.preview.as_text(tree)
    out["legend"] = _t("+ neu, ~ wird aktualisiert, - wird gelöscht, < kommt nach Seite A (Zwei-Wege)")
    if folder is not None and ".." in (folder or "").replace("\\", "/").split("/"):
        base, cur, inside = _pv_resolve(body.get("dest"), folder)
        if inside:
            folder = "/".join(cur[len(_pv_split(body.get("dest"))[1]):])
        else:
            out["path"], out["outside"] = base + "/".join(cur), True
            out["entries"] = _pv_outside(body.get("dest"), base, cur)
            folder = None
            only = False
    if folder is not None or only:
        out["path"], out["entries"] = _pv_folder(tree, folder, only)
    if _bool(a.get("tree", False)):
        out["tree"] = tree
    return dict(out, ok=True)


@action("preview_job", "POST", "/jobs/{job_id}/preview", "jobs.preview", "Aufgaben",
        "Vorschau: wie die Ordnerstruktur im Ziel nach dem nächsten Lauf aussieht, mit denselben Filtern wie der echte Lauf. "
        "Ändert nichts. Liefert summary (Dateien neu/aktualisiert/gelöscht/gleich) und text (Baum, + neu, ~ aktualisiert, "
        "- gelöscht, < nach Seite A). Mit path einen Ordner wie im Datei-Browser öffnen (entries), mit only_changes nur "
        "Änderungen, mit result das Ergebnis ohne Gelöschtes. Optional Felder überschreiben (z. B. anderes Ziel ausprobieren).",
        dict({"job_id": S(STR)}, **PREVIEW_PROPS), ["job_id"], ro=True)
def a_preview_job(a):
    return _preview(f"/job/{a['job_id']}/preview", a)


@action("preview_paths", "POST", "/jobs/preview", "jobs.preview", "Aufgaben",
        "Vorschau ohne gespeicherte Aufgabe: Ordnerstruktur im Ziel, wenn source nach dest gespiegelt würde "
        "(optional selection, excludes, include_source_dir, direction, delete_excluded). Mit path einen Ordner wie im "
        "Datei-Browser öffnen, mit result das Ergebnis ohne Gelöschtes. Ändert nichts.",
        PREVIEW_PROPS, ["source", "dest"], ro=True)
def a_preview_paths(a):
    return _preview("/job/preview", a)


# ================================================================= Allgemeine Einstellungen
LOG_KEYS = ("log_keep_runs", "log_keep_days", "audit_keep_days")
SEC_KEYS = ("lock_attempts", "lock_minutes", "fail_notify", "fail_notify_minutes", "trust_proxy", "geoip_auto", "geoip_days", "geoip_mode", "geoip_time", "geoip_dow", "public_url", "require_2fa_mode")


@action("get_settings", "GET", "/settings/general", "system.settings", "Einstellungen",
        "Allgemeine Einstellungen: Logs, Sperre nach Fehlversuchen, Reverse-Proxy, öffentliche Adresse, Sprache, GeoIP.", ro=True)
def a_get_general(a):
    need("system.settings")
    s = core.load_settings()
    return {"logs": {k: s.get(k) for k in LOG_KEYS}, "security": {k: s.get(k) for k in SEC_KEYS},
            "language": s.get("language") or core.i18n.default_lang,
            "languages": [{"code": c, "name": n} for c, n in core.i18n.languages()],
            "geoip": core.geoip.status(), "update": core.update_status()}


@action("get_update", "GET", "/update", None, "System",
        "Prüfung auf eine neuere MirrorSync-Version: installierte (current) und neueste Version (latest), "
        "update_available, Link zum Release (url), Zeitpunkt der letzten Prüfung, enabled.", ro=True)
def a_get_update(a):
    return core.update_status()


@action("check_update", "POST", "/update/check", "system.settings", "System",
        "Jetzt bei GitHub nach einer neueren Version fragen und das Ergebnis zurückgeben (wie „Jetzt prüfen“ in den "
        "Einstellungen, ändert keine Einstellungen). Ist die Benachrichtigung bei neuen Versionen eingeschaltet, wird "
        "sie für eine neue Version einmal verschickt.")
def a_check_update(a):
    r = gui("POST", "/settings/general", form={"section": "update", "check_only": "1"})
    return dict(core.update_status(), message=done(r))


@action("get_self_update", "GET", "/update/self", "system.update", "System",
        "Selbst-Update über den Docker-Socket: available (Socket eingebunden und Docker erreichbar), container, image, "
        "compose_project, pinned (fester Versions-Tag), local_only (lokal gebautes Image, kein Update möglich), auto, time, "
        "jobs_running und state (letzter Stand: pulling, running, ok, failed, error, current mit log).", ro=True)
def a_get_self_update(a):
    need("system.update")
    return core.selfupdate_status()


@action("self_update", "POST", "/update/apply", "system.update", "System",
        "MirrorSync jetzt selbst aktualisieren: Image neu holen und, wenn es neuer ist, den Container mit identischen "
        "Einstellungen neu anlegen (Rollback, wenn die neue Version nicht startet). Braucht den eingebundenen Docker-Socket. "
        "Nicht möglich, solange Aufgaben laufen. Läuft im Hintergrund; den Stand liefert get_self_update. "
        "Die Verbindung zu MirrorSync bricht während des Neustarts etwa eine Minute ab.")
def a_self_update(a):
    need("system.update")
    st, text = core.run_selfupdate(g.user)
    if st != "started":
        raise ApiError(409 if st == "busy" else 400, _t(text))
    return {"ok": True, "status": st, "message": _t(text)}


@action("update_update_settings", "PATCH", "/settings/update", "system.settings", "Einstellungen",
        "Automatische Prüfung auf neue Versionen ein- oder ausschalten (update_check) und den Abstand in Minuten "
        "festlegen (update_interval, 5–43200, Standard 60). Selbst-Update: selfupdate_auto (einmal am Tag automatisch "
        "aktualisieren, braucht den Docker-Socket) ab selfupdate_time (HH:MM). update_notify: Benachrichtigung schicken, "
        "wenn eine neue Version verfügbar ist (je Version einmal), update_notify_channels: Kanäle (webhook, smtp, "
        "telegram, apprise; leer = alle eingeschalteten). Nicht angegebene Felder bleiben unverändert.",
        {"update_check": S(BOOL), "update_interval": S(INT), "selfupdate_auto": S(BOOL), "selfupdate_time": S(STR, "HH:MM"),
         "update_notify": S(BOOL), "update_notify_channels": dict(STRS, description="webhook, smtp, telegram, apprise")})
def a_update_update_settings(a):
    _check_keys(a, ("update_check", "update_interval", "selfupdate_auto", "selfupdate_time", "update_notify",
                    "update_notify_channels"))
    chans = ([x.strip() for x in _lines(a["update_notify_channels"]).replace(",", "\n").split("\n") if x.strip()]
             if "update_notify_channels" in a else None)
    if chans is not None:
        bad = [c for c in chans if c not in core.notify.CHANNELS]
        if bad:
            raise ApiError(400, _t("Unbekannter Kanal.") + " " + ", ".join(bad))
    if "selfupdate_auto" in a or "selfupdate_time" in a:
        s = core.load_settings()
        form = {"section": "selfupdate", "selfupdate_time": str(a.get("selfupdate_time", s.get("selfupdate_time") or "04:00"))}
        if _bool(a["selfupdate_auto"]) if "selfupdate_auto" in a else s.get("selfupdate_auto"):
            form["selfupdate_auto"] = "on"
        done(gui("POST", "/settings/general", form=form))
        if not ({"update_check", "update_interval", "update_notify", "update_notify_channels"} & set(a)):
            return {"ok": True, "message": _t("Gespeichert."), "update": core.update_status(),
                    "selfupdate": {k: core.selfupdate_status()[k] for k in ("auto", "time")}}
    cur = core.update_status()
    form = {"section": "update", "update_interval_unit": "min",
            "update_interval_value": str(a.get("update_interval", cur["interval_minutes"]))}
    if _bool(a["update_check"]) if "update_check" in a else cur["enabled"]:
        form["update_check"] = "on"
    if _bool(a["update_notify"]) if "update_notify" in a else cur["notify"]:
        form["update_notify"] = "on"
    for c in (chans if chans is not None else cur["notify_channels"]):
        form[f"update_ch_{c}"] = "on"
    msg = done(gui("POST", "/settings/general", form=form))
    s = core.load_settings()
    return {"ok": True, "message": msg, "update": core.update_status(),
            "selfupdate": {"auto": bool(s.get("selfupdate_auto")), "time": s.get("selfupdate_time") or "04:00"}}


@action("purge_logs", "POST", "/logs/purge", "system.settings", "Einstellungen",
        "Einmalig alle Läufe samt Log löschen, die vor einem Datum gestartet sind (before: JJJJ-MM-TT). "
        "Laufende Aufgaben bleiben unberührt. dry_run=true zählt nur (runs, jobs), ohne zu löschen.",
        {"before": S(STR), "dry_run": S(BOOL)}, ["before"])
def a_purge_logs(a):
    _check_keys(a, ("before", "dry_run"))
    ts = core.keep_from_ts(str(a.get("before") or ""))
    if not ts:
        raise ApiError(400, _t("Datum bitte als JJJJ-MM-TT angeben."))
    if a.get("dry_run") is not None and _bool(a["dry_run"]):
        n, nj = core.purge_logs_before(ts, dry=True)
        return {"ok": True, "dry_run": True, "before": a["before"], "runs": n, "jobs": nj}
    n, nj = core.purge_logs_before(ts, dry=True)
    msg = done(gui("POST", "/settings/general", form={"section": "purge", "purge_before": a["before"], "purge_action": "delete"}))
    return {"ok": True, "dry_run": False, "before": a["before"], "runs": n, "jobs": nj, "message": msg}


@action("update_log_settings", "PATCH", "/settings/logs", "system.settings", "Einstellungen",
        "Aufbewahrung: log_keep_runs (0–1000), log_keep_days und audit_keep_days (0–3650); 0 = unbegrenzt.",
        {k: S(INT) for k in LOG_KEYS})
def a_update_logs(a):
    _check_keys(a, LOG_KEYS)
    s = core.load_settings()
    return ok(gui("POST", "/settings/general", form={k: a.get(k, s.get(k)) for k in LOG_KEYS}))


@action("update_security_settings", "PATCH", "/settings/security", "system.settings", "Einstellungen",
        "Sperre nach Fehlversuchen (lock_attempts, lock_minutes), Meldung (fail_notify off|lock|every, fail_notify_minutes), "
        "require_2fa_mode (2FA erzwingen: off = nur pro Benutzer, new = neue Benutzer bekommen require_2fa, all = für alle Benutzer), "
        "trust_proxy, geoip_auto, geoip_mode (interval = alle geoip_days Tage: 1, 7, 14, 30, 60, 90; schedule = zu geoip_time HH:MM an den "
        "Wochentagen geoip_dow, z. B. \"mon,thu\"), public_url.",
        {"lock_attempts": S(INT), "lock_minutes": S(INT), "fail_notify": S(STR, enum=["off", "lock", "every"]),
         "fail_notify_minutes": S(INT), "trust_proxy": S(BOOL), "geoip_auto": S(BOOL),
         "geoip_days": S(INT, enum=[1, 7, 14, 30, 60, 90]), "geoip_mode": S(STR, enum=["interval", "schedule"]),
         "geoip_time": S(STR, "HH:MM"), "geoip_dow": S(STR, "mon,tue,wed,thu,fri,sat,sun (kommagetrennt)"), "public_url": S(STR),
         "require_2fa_mode": S(STR, enum=["off", "new", "all"])})
def a_update_security(a):
    _check_keys(a, SEC_KEYS)
    s = core.load_settings()
    form = {"section": "security"}
    for k in SEC_KEYS:
        v = a.get(k, s.get(k))
        form[k] = _bool(v) if k in ("trust_proxy", "geoip_auto") else ("" if v is None else str(v))
    if "require_2fa_mode" in a and a["require_2fa_mode"] not in ("off", "new", "all"):
        raise ApiError(400, "require_2fa_mode: erlaubt sind off, new oder all.")
    if "geoip_days" in a and str(a["geoip_days"]) not in {str(d) for d in core.geoip.INTERVALS}:
        raise ApiError(400, "geoip_days: erlaubt sind 1, 7, 14, 30, 60 oder 90.")
    return ok(gui("POST", "/settings/general", form=form))


@action("update_geoip", "POST", "/settings/geoip/update", "system.settings", "Einstellungen",
        "Länder-Datenbank (GeoIP) jetzt herunterladen.")
def a_geoip(a):
    s = core.load_settings()
    form = {"section": "security", "geoip_now": True}
    for k in SEC_KEYS:
        form[k] = _bool(s.get(k)) if k in ("trust_proxy", "geoip_auto") else (s.get(k) or "")
    return ok(gui("POST", "/settings/general", form=form), geoip=core.geoip.status())


@action("set_language", "PUT", "/settings/language", "system.settings", "Einstellungen",
        "Systemsprache setzen (en, de, es, it, fr …).", {"language": S(STR)}, ["language"])
def a_set_language(a):
    return ok(gui("POST", "/settings/general", form={"section": "lang", "language": a.get("language", "")}))


@action("get_bandwidth", "GET", "/settings/bandwidth", "system.settings", "Einstellungen",
        "Standard-Bandbreite: up/down immer in MB/s gespeichert (leer = unbegrenzt) und Zeitfenster rules=[{days:[0-6], start, end, up, down}]. "
        "unit ist die Anzeige-Einheit der GUI (MB/s oder Mbit/s, 1 MB/s = 8 Mbit/s).", ro=True)
def a_get_bw(a):
    need("system.settings")
    s = core.load_settings()
    cfg = s.get("bw") or core.bwlimit.EMPTY
    unit = s.get("bw_unit") or "MB/s"
    return {"bw": cfg, "unit": unit, "description": _t(core.bwlimit.describe(cfg, unit))}


@action("set_bandwidth", "PUT", "/settings/bandwidth", "system.settings", "Einstellungen",
        "Standard-Bandbreite setzen (gilt ab dem nächsten Lauf). Werte in bw sind in der Einheit input_unit "
        "(Standard MB/s, oder Mbit/s, wird umgerechnet). unit ändert die Anzeige-Einheit der GUI. Fehlt bw, bleiben die Grenzen.",
        {"bw": {"type": "object"}, "input_unit": S(STR, enum=["MB/s", "Mbit/s"]), "unit": S(STR, enum=["MB/s", "Mbit/s"])})
def a_set_bw(a):
    _check_keys(a, ("bw", "input_unit", "unit"))
    s = core.load_settings()
    units = core.bwlimit.UNITS
    for k in ("unit", "input_unit"):
        if a.get(k) is not None and a[k] not in units:
            raise ApiError(400, core.i18n.t("{0}: erlaubt sind MB/s oder Mbit/s.", k))
    if "bw" not in a and "unit" not in a:
        raise ApiError(400, "bw oder unit angeben.")
    cfg = a["bw"] if "bw" in a else (s.get("bw") or core.bwlimit.EMPTY)
    if not isinstance(cfg, dict):
        raise ApiError(400, "bw muss ein Objekt sein.")
    if "bw" in a and a.get("input_unit") == "Mbit/s":
        cfg = core.bwlimit.convert(cfg, 1 / 8)
    form = {"section": "bw", "bw_json": json.dumps(cfg), "bw_unit": a.get("unit") or s.get("bw_unit") or "MB/s"}
    r = ok(gui("POST", "/settings/general", form=form))
    s = core.load_settings()
    r.update(bw=s.get("bw"), unit=s.get("bw_unit") or "MB/s")
    return r


# ================================================================= Zugriff nach IP und Land
ACCESS_KEYS = ("allow", "countries", "country_mode", "auto_exempt_lan", "notify", "auto_attempts", "auto_minutes", "auto_window")


def _access_view():
    cfg = core.guard.load()
    ip = core._client_ip()
    blocks = []
    for e in cfg.get("block", []):
        n, last = core.guard.hits.get(e["net"], (0, ""))
        b = dict(e, hits=n, last_hit=last, active=bool(core.ipguard.active_block(e)))
        host = core.ipguard.parse_host(e.get("net", ""))
        if host:
            b["resolved"] = sorted(str(x) for x in core.ipguard.resolve(host)[0])
        blocks.append(b)
    hosts = {}
    for x in cfg.get("allow", []):
        host = core.ipguard.parse_host(x)
        if host:
            hosts[host] = sorted(str(i) for i in core.ipguard.resolve(host)[0])
    return {"rules": {k: cfg.get(k) for k in ACCESS_KEYS}, "blocks": blocks, "allow_resolved": hosts, "your_ip": ip,
            "your_country": core.geoip.locate(ip).get("iso", ""), "disabled_by_env": core.IPGUARD_OFF}


@action("get_access_rules", "GET", "/settings/access", "system.access", "Zugriff",
        "Zugriffsregeln: Erlaubt-Liste, Länderregel, automatische Sperre und gesperrte Adressen.", ro=True)
def a_get_access(a):
    need("system.access")
    return _access_view()


@action("update_access_rules", "PATCH", "/settings/access", "system.access", "Zugriff",
        "Zugriffsregeln ändern (nur angegebene Felder): allow (Liste aus IPs, Netzen oder Hostnamen wie buero.example.de), countries (z. B. [DE, AT]), country_mode off|allow|block, "
        "auto_exempt_lan, notify, auto_attempts, auto_minutes, auto_window. Wer sich selbst aussperren würde, bekommt einen Fehler.",
        {"allow": STRS, "countries": STRS, "country_mode": S(STR, enum=["off", "allow", "block"]), "auto_exempt_lan": S(BOOL),
         "notify": S(BOOL), "auto_attempts": S(INT), "auto_minutes": S(INT), "auto_window": S(INT)})
def a_update_access(a):
    _check_keys(a, ACCESS_KEYS)
    cfg = core.guard.load()
    v = {k: a.get(k, cfg.get(k)) for k in ACCESS_KEYS}
    form = {"allow": _lines(v["allow"] or []), "countries": ",".join(v["countries"] or []) if isinstance(v["countries"], list)
            else (v["countries"] or ""), "country_mode": v["country_mode"] or "off",
            "auto_exempt_lan": _bool(v["auto_exempt_lan"]), "notify": _bool(v["notify"])}
    for k in ("auto_attempts", "auto_minutes", "auto_window"):
        form[k] = "" if v[k] is None else v[k]
    return ok(gui("POST", "/settings/access", form=form), rules=_access_view()["rules"])


@action("block_ip", "POST", "/settings/access/blocks", "system.access", "Zugriff",
        "IP-Adresse, Netz oder Hostname sperren (minutes 0 = dauerhaft). Hostnamen werden bei jeder Anfrage per DNS aufgelöst (5 Minuten Cache). Die eigene Adresse lässt sich nicht sperren.",
        {"net": S(STR, "z. B. 203.0.113.7, 203.0.113.0/24 oder facebook.com"), "minutes": S(INT), "note": S(STR)}, ["net"])
def a_block(a):
    return ok(gui("POST", "/settings/access/block", form={"net": a.get("net", ""), "minutes": a.get("minutes", 0),
                                                          "note": a.get("note", ""), "back": "/settings/access"}))


@action("unblock_ip", "DELETE", "/settings/access/blocks", "system.access", "Zugriff",
        "Sperre einer IP-Adresse, eines Netzes oder Hostnamens aufheben.", {"net": S(STR)}, ["net"])
def a_unblock(a):
    if not any(e["net"] == a.get("net") for e in core.guard.load().get("block", [])):
        raise ApiError(404, _t("Nicht gefunden."))
    return ok(gui("POST", "/settings/access/unblock", form={"net": a.get("net", "")}))


# ================================================================= Benutzer
def _user_view(name, u):
    return {"name": name, "role": u.get("role"), "disabled": bool(u.get("disabled")), "disabled_by": u.get("disabled_by", ""),
            "lock_from": u.get("lock_from", ""), "lock_until": u.get("lock_until", ""),
            "auto_lock_until": u.get("auto_lock_until", ""), "inactive_reason": core.users.inactive_reason(u) or "",
            "totp": bool(u.get("totp_enabled")), "require_2fa": bool(u.get("require_2fa")),
            "must_2fa": core.must_2fa(u), "totp_setup_pending": core.needs_2fa(u), "backup_codes_left": len(u.get("backup_codes") or []),
            "passkeys": [{k: p.get(k) for k in ("name", "created", "last_used", "count") if k in p} for p in u.get("passkeys") or []],
            "fail_count": u.get("fail_count", 0), "last_login": u.get("last_login", ""), "last_ip": u.get("last_ip", ""),
            "last_country": u.get("last_country", ""), "created": u.get("created", ""), "language": u.get("lang", ""),
            "sidebar": "mini" if u.get("sidebar") == "mini" else "full",
            "groups": core.roles.groups_of(core.load_groups(), name)}


def _user(name):
    real = core.store.find(name) or name
    u = core.store.get(real)
    if not u:
        raise ApiError(404, core.i18n.t("Benutzer {0} nicht gefunden.", name))
    return real, u


@action("get_user", "GET", "/users/{name}", "users.view", "Benutzer",
        "Ein Benutzer mit Rolle, Sperren, 2FA, Passkeys und letzter Anmeldung (ohne Geheimnisse).", {"name": S(STR)}, ["name"], ro=True)
def a_get_user(a):
    need("users.view")
    return _user_view(*_user(a["name"]))


USER_KEYS = ("name", "password", "role", "disabled", "lock_from", "lock_until", "unlock", "reset_2fa", "reset_passkeys", "require_2fa", "groups", "sidebar")
USER_PROPS = {"password": S(STR, "mindestens 8 Zeichen"), "role": S(STR, "Rollen-ID, siehe list_roles"), "disabled": S(BOOL),
              "lock_from": S(STR, "JJJJ-MM-TTTHH:MM, leer = keine"), "lock_until": S(STR, "JJJJ-MM-TTTHH:MM, leer = keine"),
              "unlock": S(BOOL, "automatische Sperre aufheben"), "reset_2fa": S(BOOL, "2FA zurücksetzen"),
              "require_2fa": S(BOOL, "2FA erzwingen: der Benutzer muss nach der Anmeldung zuerst 2FA einrichten und kann sie nicht selbst ausschalten. "
                                     "Beim Anlegen ohne Angabe gilt die globale Einstellung (require_2fa_mode)"),
              "reset_passkeys": S(BOOL, "alle Passkeys entfernen"),
              "groups": dict(STRS, description="Gruppen-IDs (ersetzt die Mitgliedschaften; braucht groups.manage)"),
              "sidebar": {"type": "string", "enum": ["full", "mini"], "description": "Seitenleiste der Oberfläche: full = ausgeklappt, mini = eingeklappt (nur Symbole)"}}


def _user_form(u, a):
    lf = a.get("lock_from", u.get("lock_from", "")) or ""
    lu = a.get("lock_until", u.get("lock_until", "")) or ""
    form = {"role": a.get("role", u.get("role")), "active": "0" if _bool(a.get("disabled", u.get("disabled", False))) else "1",
            "lock": bool(lf or lu), "lock_from": lf, "lock_until": lu}
    if a.get("password"):
        form.update(password=a["password"], password2=a["password"])
    for k in ("unlock", "reset_2fa", "reset_passkeys"):
        form[k] = _bool(a.get(k, False))
    if "require_2fa" in a:
        form.update(r2fa_form="1", require_2fa=_bool(a["require_2fa"]))
    if "groups" in a:
        need("groups.manage")
        grs = core.load_groups()
        gl = a["groups"] if isinstance(a["groups"], list) else None
        if gl is None or any(x not in grs for x in gl):
            raise ApiError(400, core.i18n.t("Unbekannte Gruppe: {0}", next((x for x in gl or [] if x not in grs), str(a["groups"]))))
        forbidden = [x for x in grs if not core.group_within(grs[x]) and ((x in gl) != (x in core.roles.groups_of(grs, a.get("name") or u.get("_name", ""))))]
        if forbidden:
            raise ApiError(403, core.i18n.t("Gruppe {0} hat Rechte, die du selbst nicht hast.", forbidden[0]))
        form.update(grp_form="1", grp=list(gl))
    return form


@action("create_user", "POST", "/users", "users.manage", "Benutzer", "Benutzer anlegen.",
        dict({"name": S(STR)}, **{k: v for k, v in USER_PROPS.items() if k in ("password", "role", "disabled", "lock_from", "lock_until", "require_2fa")}),
        ["name", "password", "role"])
def a_create_user(a):
    _check_keys(a, USER_KEYS)
    form = _user_form({}, a)
    form["name"] = a.get("name", "")
    form.setdefault("password", a.get("password", ""))
    form.setdefault("password2", a.get("password", ""))
    msg = done(gui("POST", "/users/new", form=form))
    return {"ok": True, "message": msg, "user": _user_view(*_user(a["name"]))}


@action("update_user", "PATCH", "/users/{name}", "users.manage", "Benutzer",
        "Benutzer ändern: Rolle, Passwort, deaktivieren, Sperrzeitraum, Sperre aufheben, 2FA oder Passkeys zurücksetzen, "
        "Seitenleiste ein- oder ausklappen (sidebar). "
        "Der letzte Admin bleibt immer erhalten.", dict({"name": S(STR)}, **USER_PROPS), ["name"])
def a_update_user(a):
    _check_keys(a, USER_KEYS)
    name, u = _user(a.pop("name"))
    side = a.pop("sidebar", None)
    if side is not None and side not in ("full", "mini"):
        raise ApiError(400, core.i18n.t("Ungültiger Wert für die Seitenleiste (mini oder full)."))
    a["name"] = name
    msg = done(gui("POST", f"/users/{name}/edit", form=_user_form(u, a))) if len(a) > 1 or side is None else ""
    if side is not None and ("mini" if u.get("sidebar") == "mini" else "full") != side:
        core.store.update(name, sidebar="mini" if side == "mini" else "")
        txt = {"mini": "eingeklappt", "full": "ausgeklappt"}
        core.audit_add("user", "geändert", name, detail="über MCP" if request.path.startswith("/mcp") else "über API",
                       changes=core.audit.diff({"sidebar": txt["full" if side == "mini" else "mini"]}, {"sidebar": txt[side]}, "user"))
        msg = msg or core.i18n.t("Seitenleiste gespeichert.")
    return {"ok": True, "message": msg, "user": _user_view(*_user(name))}


@action("unlock_user", "POST", "/users/{name}/unlock", "users.manage", "Benutzer",
        "Gesperrten oder deaktivierten Benutzer wieder freischalten.", {"name": S(STR)}, ["name"])
def a_unlock_user(a):
    name, _ = _user(a["name"])
    return ok(gui("POST", f"/users/{name}/unlock", form={}), user=_user_view(*_user(name)))


@action("delete_user", "DELETE", "/users/{name}", "users.manage", "Benutzer",
        "Benutzer löschen. Der letzte Admin kann nicht gelöscht werden.", {"name": S(STR)}, ["name"])
def a_delete_user(a):
    name, _ = _user(a["name"])
    return ok(gui("POST", f"/users/{name}/delete", form={}), deleted=name)


# ================================================================= Anmeldeverlauf
@action("login_history", "GET", "/login-history", "users.view", "Benutzer",
        "Anmeldeverlauf (neueste zuerst). filter: all|ok|fail|new (unbestätigte Fehlversuche), user, limit.",
        {"filter": S(STR, enum=["all", "ok", "fail", "new"]), "user": S(STR), "limit": S(INT)}, ro=True)
def a_login_history(a):
    need("users.view")
    flt, who = a.get("filter") or "all", (a.get("user") or "").strip()
    e = core.login_log.load()
    if flt == "ok":
        e = [x for x in e if x.get("ok")]
    elif flt == "fail":
        e = [x for x in e if not x.get("ok")]
    elif flt == "new":
        e = [x for x in e if not x.get("ok") and not x.get("ack")]
    if who:
        e = [x for x in e if x.get("user") == who]
    lim = max(1, min(int(a.get("limit") or 200), 1000))
    return {"total": len(e), "unacknowledged": core.login_log.unacked(), "entries": e[:lim]}


def _log_action(a, act):
    ids = a.get("ids") or []
    form = {"action": act, "id": list(ids), "all": "1" if _bool(a.get("all", False)) else ""}
    if act == "delete":
        form["only_failed"] = "1" if _bool(a.get("only_failed", True)) else "0"
    return ok(gui("POST", "/users/log/action", form=form), unacknowledged=core.login_log.unacked())


@action("ack_login_failures", "POST", "/login-history/ack", "users.manage", "Benutzer",
        "Fehlversuche bestätigen: ids (Liste) oder all=true.", {"ids": STRS, "all": S(BOOL)})
def a_ack(a):
    return _log_action(a, "ack")


@action("delete_login_history", "DELETE", "/login-history", "users.manage", "Benutzer",
        "Einträge des Anmeldeverlaufs löschen: ids oder all=true; only_failed (Standard true) nur Fehlversuche.",
        {"ids": STRS, "all": S(BOOL), "only_failed": S(BOOL)})
def a_del_log(a):
    return _log_action(a, "delete")


# ================================================================= Rollen
def _role_view(rid, r, counts=None):
    return {"id": rid, "name": r.get("name"), "description": _t(r.get("description", "")), "perms": r.get("perms", []),
            "jobs": r.get("jobs", "all"), "remotes": r.get("remotes", "all"), "builtin": bool(r.get("builtin")),
            "locked": bool(r.get("locked")), "users": (counts or {}).get(rid, 0)}


def _counts():
    c = {}
    for u in core.store.load().values():
        c[u.get("role")] = c.get(u.get("role"), 0) + 1
    return c


@action("list_roles", "GET", "/roles", "roles.manage", "Rollen", "Alle Rollen mit Rechten und Beschränkungen.", ro=True)
def a_roles(a):
    need("roles.manage")
    c = _counts()
    return [_role_view(rid, r, c) for rid, r in core.role_store.load().items()]


@action("list_permissions", "GET", "/permissions", None, "Rollen", "Alle Einzelrechte mit Bezeichnung, nach Bereichen.", ro=True)
def a_perms(a):
    return [{"group": _t(gname), "perms": [{"id": p, "label": _t(lbl)} for p, lbl in perms]} for gname, perms in core.roles.PERM_GROUPS]


def _role(rid):
    r = core.role_store.load().get(rid)
    if not r:
        raise ApiError(404, core.i18n.t("Rolle {0} nicht gefunden.", rid))
    return r


@action("get_role", "GET", "/roles/{role_id}", "roles.manage", "Rollen", "Eine Rolle.", {"role_id": S(STR)}, ["role_id"], ro=True)
def a_role(a):
    need("roles.manage")
    return _role_view(a["role_id"], _role(a["role_id"]), _counts())


ROLE_KEYS = ("name", "description", "perms", "jobs", "remotes")
ROLE_PROPS = {"name": S(STR), "description": S(STR), "perms": STRS,
              "jobs": {"description": "\"all\" oder Liste von Aufgaben-IDs"}, "remotes": {"description": "\"all\" oder Liste von Speicherorten"}}


def _role_form(r, a):
    v = {k: a.get(k, r.get(k, "all" if k in ("jobs", "remotes") else "")) for k in ROLE_KEYS}
    form = {"name": v["name"] or "", "description": v["description"] or "", "perm": list(v["perms"] or [])}
    for k, item in (("jobs", "job"), ("remotes", "remote")):
        if v[k] == "all" or v[k] is None:
            form[f"{k}_scope"] = "all"
        else:
            form[f"{k}_scope"] = "some"
            form[item] = list(v[k])
    return form


@action("create_role", "POST", "/roles", "roles.manage", "Rollen",
        "Rolle anlegen (nicht mehr Rechte, als der Key selbst hat).", ROLE_PROPS, ["name", "perms"])
def a_create_role(a):
    _check_keys(a, ROLE_KEYS)
    before = set(core.role_store.load())
    msg = done(gui("POST", "/roles/new", form=_role_form({}, a)))
    new = [rid for rid in core.role_store.load() if rid not in before]
    return {"ok": True, "message": msg, "role": _role_view(new[0], _role(new[0])) if new else None}


@action("update_role", "PATCH", "/roles/{role_id}", "roles.manage", "Rollen", "Rolle ändern (nur angegebene Felder).",
        dict({"role_id": S(STR)}, **ROLE_PROPS), ["role_id"])
def a_update_role(a):
    rid = a.pop("role_id")
    _check_keys(a, ROLE_KEYS)
    r = _role(rid)
    if r.get("locked"):
        raise ApiError(400, _t("Die Rolle Admin kann nicht geändert werden."))
    msg = done(gui("POST", f"/roles/{rid}/edit", form=_role_form(r, a)))
    return {"ok": True, "message": msg, "role": _role_view(rid, _role(rid))}


@action("delete_role", "DELETE", "/roles/{role_id}", "roles.manage", "Rollen",
        "Rolle löschen (nur wenn kein Benutzer sie hat).", {"role_id": S(STR)}, ["role_id"])
def a_delete_role(a):
    _role(a["role_id"])
    return ok(gui("POST", f"/roles/{a['role_id']}/delete", form={}), deleted=a["role_id"])


# ================================================================= Gruppen
def _group_view(gid, x):
    jobs, rem = core.group_views(gid)
    return {"id": gid, "name": x.get("name"), "description": x.get("description", ""), "members": x.get("members") or [],
            "keys": x.get("keys") or [], "perms": x.get("perms") or [], "principal": "group:" + gid,
            "sees_jobs": [{"id": jid, "name": n} for n, jid in jobs], "sees_remotes": rem}


def _group(gid):
    x = core.load_groups().get(gid)
    if not x:
        raise ApiError(404, core.i18n.t("Gruppe {0} nicht gefunden.", gid))
    return x


GROUP_KEYS = ("name", "description", "members", "keys", "perms")
GROUP_PROPS = {"name": S(STR), "description": S(STR), "members": dict(STRS, description="Benutzernamen"),
               "keys": dict(STRS, description="IDs von API-Keys (siehe list_api_keys)"),
               "perms": dict(STRS, description="zusätzliche Rechte, siehe list_permissions")}


def _group_form(x, a):
    v = {k: a.get(k, x.get(k)) for k in GROUP_KEYS}
    for k in ("members", "keys", "perms"):
        if v[k] is not None and not isinstance(v[k], list):
            raise ApiError(400, core.i18n.t("{0} muss eine Liste sein.", k))
    if a.get("members") is not None:   # Schreibweise wie gespeichert
        v["members"] = [core.store.find(m) or m for m in a["members"]]
    return {"name": v["name"] or "", "description": v["description"] or "", "member": list(v["members"] or []),
            "key": list(v["keys"] or []), "perm": list(v["perms"] or [])}


@action("list_groups", "GET", "/groups", "groups.manage", "Gruppen",
        "Alle Gruppen mit Mitgliedern (Benutzer, API-Keys), zusätzlichen Rechten und dem, was sie eingeschränkt sehen.", ro=True)
def a_groups(a):
    need("groups.manage")
    return [_group_view(gid, x) for gid, x in sorted(core.load_groups().items(), key=lambda kv: kv[1].get("name", "").lower())]


@action("get_group", "GET", "/groups/{group_id}", "groups.manage", "Gruppen", "Eine Gruppe.", {"group_id": S(STR)}, ["group_id"], ro=True)
def a_group(a):
    need("groups.manage")
    return _group_view(a["group_id"], _group(a["group_id"]))


@action("create_group", "POST", "/groups", "groups.manage", "Gruppen",
        "Gruppe anlegen. Rechte der Mitglieder = Rolle + Rechte aller ihrer Gruppen (nur Rechte, die der Key selbst hat). "
        "Die Gruppe kann dann in visible_to von Aufgaben und Speicherorten stehen (group:<id>).", GROUP_PROPS, ["name"])
def a_create_group(a):
    _check_keys(a, GROUP_KEYS)
    before = set(core.load_groups())
    msg = done(gui("POST", "/groups/new", form=_group_form({}, a)))
    new = [gid for gid in core.load_groups() if gid not in before]
    return {"ok": True, "message": msg, "group": _group_view(new[0], _group(new[0])) if new else None}


@action("update_group", "PATCH", "/groups/{group_id}", "groups.manage", "Gruppen",
        "Gruppe ändern (nur angegebene Felder; members/keys/perms ersetzen die Liste).", dict({"group_id": S(STR)}, **GROUP_PROPS), ["group_id"])
def a_update_group(a):
    gid = a.pop("group_id")
    _check_keys(a, GROUP_KEYS)
    x = _group(gid)
    msg = done(gui("POST", f"/groups/{gid}/edit", form=_group_form(x, a)))
    return {"ok": True, "message": msg, "group": _group_view(gid, _group(gid))}


@action("delete_group", "DELETE", "/groups/{group_id}", "groups.manage", "Gruppen",
        "Gruppe löschen. Mitglieder verlieren ihre Rechte und Sichtbarkeit; sie wird aus allen visible_to entfernt.",
        {"group_id": S(STR)}, ["group_id"])
def a_delete_group(a):
    _group(a["group_id"])
    return ok(gui("POST", f"/groups/{a['group_id']}/delete", form={}), deleted=a["group_id"])


# ================================================================= API-Keys
def _key_view(kid, k):
    roles_ = core.role_store.load()
    return {"id": kid, "name": k.get("name"), "role": k.get("role"), "role_name": (roles_.get(k.get("role")) or {}).get("name"),
            "status": api.key_status(k), "expires": k.get("expires", ""), "ips": k.get("ips", []),
            "created": k.get("created", ""), "created_by": k.get("created_by", ""), "last_used": k.get("last_used", ""),
            "last_ip": k.get("last_ip", ""), "uses": k.get("uses", 0), "revoked_by": k.get("revoked_by", ""),
            "revoked_at": k.get("revoked_at", ""), "groups": core.roles.groups_of(core.load_groups(), None, kid),
            "disabled": bool(k.get("disabled")), "lock_from": k.get("lock_from", ""), "lock_until": k.get("lock_until", ""),
            "windows": k.get("windows") or [], "revealable": bool(k.get("enc")), "lang": k.get("lang") or "",
            "effective_lang": api.key_lang(k)}


KEY_EDIT = ("name", "role", "expires", "ips", "disabled", "lock_from", "lock_until", "windows", "groups", "lang")
LANG_PROP = S(STR, "Sprache der API-Antworten: de, en, es, it, fr; leer = wie der Benutzer, dem der Key gehört (ohne Benutzer Englisch)")


@action("update_api_key", "PATCH", "/api-keys/{key_id}", "system.api", "API-Keys",
        "API-Key ändern (nur angegebene Felder): Name, Rolle, Ablauf, IPs, deaktivieren/aktivieren (disabled), "
        "Pause von–bis (lock_from/lock_until JJJJ-MM-TTTHH:MM), wöchentliche Zeitfenster windows=[{days:[0-6], start, end}] "
        "(leer = immer), groups (Gruppen-IDs, braucht groups.manage), lang (Sprache der Antworten). Den Key selbst anzeigen geht nur in der Web-GUI.",
        {"key_id": S(STR), "name": S(STR), "role": S(STR), "expires": S(STR, "JJJJ-MM-TT, leer = unbegrenzt"), "ips": STRS,
         "disabled": S(BOOL), "lock_from": S(STR), "lock_until": S(STR),
         "windows": {"type": "array", "items": {"type": "object"}}, "groups": STRS, "lang": LANG_PROP}, ["key_id"])
def a_update_key(a):
    kid = a.pop("key_id")
    _check_keys(a, KEY_EDIT)
    k = api.keys().get(kid)
    if not k:
        raise ApiError(404, _t("Nicht gefunden."))
    v = {x: a.get(x, k.get(x)) for x in KEY_EDIT if x != "groups"}
    ips = v.get("ips") or []
    lf, lu = v.get("lock_from") or "", v.get("lock_until") or ""
    wins = v.get("windows") or []
    if not isinstance(wins, list):
        raise ApiError(400, core.i18n.t("{0} muss eine Liste sein.", "windows"))
    form = {"name": v.get("name") or "", "role": v.get("role") or "", "expires": v.get("expires") or "",
            "ips": ", ".join(ips) if isinstance(ips, list) else str(ips), "active": "0" if _bool(v.get("disabled")) else "1",
            "lock": bool(lf or lu), "lock_from": lf, "lock_until": lu, "win_on": bool(wins), "lang": v.get("lang") or ""}
    if form["lang"] and not core.i18n.valid(form["lang"]):
        raise ApiError(400, core.i18n.t("Unbekannte Sprache: {0}", form["lang"]))
    for i, w in enumerate(wins[:10]):
        w = w if isinstance(w, dict) else {}
        form[f"w{i}_d"] = [str(d) for d in w.get("days") or []]
        form[f"w{i}_s"], form[f"w{i}_e"] = str(w.get("start") or ""), str(w.get("end") or "")
    if "groups" in a:
        need("groups.manage")
        grs = core.load_groups()
        gl = a["groups"] if isinstance(a["groups"], list) else None
        if gl is None or any(x not in grs for x in gl):
            raise ApiError(400, core.i18n.t("Unbekannte Gruppe: {0}", next((x for x in gl or [] if x not in grs), str(a["groups"]))))
        form.update(grp_form="1", grp=list(gl))
    msg = done(gui("POST", f"/settings/api/{kid}/edit", form=form))
    return {"ok": True, "message": msg, "key": _key_view(kid, api.keys()[kid])}


@action("list_api_keys", "GET", "/api-keys", "system.api", "API-Keys",
        "Alle API-Keys (ohne Schlüssel) mit Status: aktiv, deaktiviert, pausiert, außerhalb der Zeiten, abgelaufen, widerrufen.", ro=True)
def a_keys(a):
    need("system.api")
    return [_key_view(kid, k) for kid, k in sorted(api.keys().items(), key=lambda kv: kv[1].get("name", "").lower())]


@action("create_api_key", "POST", "/api-keys", "system.api", "API-Keys",
        "API-Key erstellen. Der Schlüssel (token) steht nur in dieser Antwort.",
        {"name": S(STR), "role": S(STR), "expires": S(STR, "JJJJ-MM-TT, leer = unbegrenzt"), "ips": STRS, "lang": LANG_PROP}, ["name", "role"])
def a_create_key(a):
    _check_keys(a, ("name", "role", "expires", "ips", "lang"))
    if a.get("lang") and not core.i18n.valid(a["lang"]):
        raise ApiError(400, core.i18n.t("Unbekannte Sprache: {0}", a["lang"]))
    r = gui("POST", "/settings/api", form={"name": a.get("name", ""), "role": a.get("role", ""), "expires": a.get("expires", ""),
                                           "lang": a.get("lang") or "",
                                           "ips": ", ".join(a.get("ips") or []) if isinstance(a.get("ips"), list) else (a.get("ips") or "")})
    done(r)
    new = r["out"].get("new")
    if not new:
        raise ApiError(500, _t("Fehler"))
    return {"ok": True, "id": new["id"], "name": new["name"], "token": new["token"],
            "key": _key_view(new["id"], api.keys()[new["id"]])}


@action("revoke_api_key", "POST", "/api-keys/{key_id}/revoke", "system.api", "API-Keys",
        "API-Key widerrufen (wirkt sofort, bleibt in der Liste).", {"key_id": S(STR)}, ["key_id"])
def a_revoke_key(a):
    if a["key_id"] not in api.keys():
        raise ApiError(404, _t("Nicht gefunden."))
    return ok(gui("POST", f"/settings/api/{a['key_id']}/revoke", form={}), key=_key_view(a["key_id"], api.keys()[a["key_id"]]))


@action("delete_api_key", "DELETE", "/api-keys/{key_id}", "system.api", "API-Keys",
        "API-Key endgültig löschen (auch aus Gruppen; wirkt sofort, nicht umkehrbar). Audit-Einträge bleiben. "
        "Den Key, mit dem man gerade zugreift, kann man nicht löschen.", {"key_id": S(STR)}, ["key_id"])
def a_delete_key(a):
    if a["key_id"] not in api.keys():
        raise ApiError(404, _t("Nicht gefunden."))
    return ok(gui("POST", f"/settings/api/{a['key_id']}/delete", form={}), deleted=a["key_id"])


# ================================================================= Sicherung, Export, Import
AUTO_KEYS = ("enabled", "schedule", "dir", "keep", "days", "logs", "password", "notify", "notify_skip", "channels")


def _backup_list():
    return [{k: b.get(k) for k in ("name", "size", "time", "auto", "enc", "dir")} for b in core._backups()]


def _auto_view():
    v = core._autobackup_view()
    return {"enabled": v.get("autobackup_enabled"), "schedule": v.get("autobackup_schedule"), "dir": v.get("autobackup_dir"),
            "effective_dir": v.get("dir"), "keep": v.get("autobackup_keep"), "days": v.get("autobackup_days"),
            "logs": v.get("autobackup_logs"), "notify": v.get("autobackup_notify"), "notify_skip": v.get("autobackup_notify_skip"),
            "channels": v.get("autobackup_channels") or [], "password_set": v.get("has_password"), "next_run": v.get("next"),
            "last": v.get("status")}


@action("backup_overview", "GET", "/backup", ADMIN, "Sicherung",
        "Gespeicherte Sicherungen und Einstellungen der automatischen Sicherung.", ro=True)
def a_backup(a):
    need_any(ADMIN)
    return {"backups": _backup_list(), "auto": _auto_view(), "encryption": core.backup.CRYPTO}


@action("update_autobackup", "PATCH", "/backup/auto", ADMIN, "Sicherung",
        "Automatische Sicherung einstellen (nur angegebene Felder): enabled, schedule (Cron), dir (absoluter Pfad, leer = config/backups), "
        "keep, days, logs, password (≥ 8 Zeichen, leer = entfernen), notify never|fail|always, notify_skip, channels.",
        {"enabled": S(BOOL), "schedule": S(STR), "dir": S(STR), "keep": S(INT), "days": S(INT), "logs": S(BOOL),
         "password": S(STR), "notify": S(STR, enum=["never", "fail", "always"]), "notify_skip": S(BOOL),
         "channels": {"type": "array", "items": {"type": "string", "enum": ["webhook", "smtp", "telegram", "apprise"]}}})
def a_update_auto(a):
    need_any(ADMIN)
    _check_keys(a, AUTO_KEYS)
    st = core.load_settings()
    cur = {k: st.get("autobackup_" + k) for k in AUTO_KEYS if k != "password"}
    v = dict(cur, **{k: a[k] for k in a if k != "password"})
    form = {"autobackup_enabled": _bool(v["enabled"]), "autobackup_schedule": v["schedule"] or "", "autobackup_dir": v["dir"] or "",
            "autobackup_keep": v["keep"] if v["keep"] is not None else "", "autobackup_days": v["days"] if v["days"] is not None else "",
            "autobackup_logs": _bool(v["logs"]), "autobackup_notify": v["notify"] or "fail",
            "autobackup_notify_skip": _bool(v["notify_skip"])}
    for c in v["channels"] or []:
        form[f"autobackup_ch_{c}"] = True
    if "password" in a:
        if a["password"]:
            form.update(autobackup_password=a["password"], autobackup_password2=a["password"])
        else:
            form["autobackup_password_clear"] = True
    return ok(gui("POST", "/settings/backup/auto", form=form), auto=_auto_view())


@action("run_autobackup", "POST", "/backup/auto/run", ADMIN, "Sicherung",
        "Automatische Sicherung jetzt ausführen (force=true auch ohne Änderung).", {"force": S(BOOL)})
def a_run_auto(a):
    need_any(ADMIN)
    return ok(gui("POST", "/settings/backup/auto", form={"run": True, "force": _bool(a.get("force", False))}), auto=_auto_view())


def _file_response(r, mcp):
    done(r)
    resp = r["resp"]
    name = re.search(r'filename="?([^";]+)', resp.headers.get("Content-Disposition", "")) or None
    name = name.group(1) if name else "mirrorsync.zip"
    blob = resp.get_data()
    if not mcp:
        return Response(blob, mimetype=resp.mimetype, headers={"Content-Disposition": f'attachment; filename="{name}"'})
    if len(blob) > 25 * 1024 * 1024:
        raise ApiError(413, _t("Die Datei ist für MCP zu groß, bitte über die REST-API herunterladen."))
    return {"filename": name, "size": len(blob), "data_base64": base64.b64encode(blob).decode()}


@action("export_backup", "POST", "/backup/export", ADMIN, "Sicherung",
        "Gesamten Stand exportieren (REST: Datei, MCP: data_base64). Enthält Geheimnisse, daher password empfohlen (≥ 8 Zeichen).",
        {"password": S(STR), "logs": S(BOOL)})
def a_export(a):
    need_any(ADMIN)
    pw = a.get("password") or ""
    r = gui("POST", "/settings/backup/export", form={"password": pw, "password2": pw, "logs": _bool(a.get("logs", False))})
    return _file_response(r, a.get("_mcp"))


@action("download_backup", "GET", "/backup/files/{name}", ADMIN, "Sicherung",
        "Gespeicherte Sicherung herunterladen (REST: Datei, MCP: data_base64).", {"name": S(STR)}, ["name"], ro=True)
def a_download(a):
    need_any(ADMIN)
    return _file_response(gui("GET", f"/settings/backup/file/{a['name']}"), a.get("_mcp"))


@action("delete_backup", "DELETE", "/backup/files/{name}", ADMIN, "Sicherung", "Gespeicherte Sicherung löschen.",
        {"name": S(STR)}, ["name"])
def a_delete_backup(a):
    need_any(ADMIN)
    if not core._backup_by_name(a["name"]):
        raise ApiError(404, _t("Nicht gefunden."))
    return ok(gui("POST", f"/settings/backup/file/{a['name']}/delete", form={}), deleted=a["name"])


def _stage_and_apply(c, r, a):
    """Nach dem Hochladen: Vorschau liefern; mit confirm=true sofort uebernehmen (gleiche interne Sitzung)."""
    done(r)
    p = r["out"].get("preview") or {}
    preview = {"ok": p.get("ok"), "notes": [_t(n) for n in p.get("notes", [])], "manifest": p.get("m"),
               "counts": p.get("counts"), "files": p.get("files"), "logs": p.get("logs"), "encrypted": p.get("enc")}
    if not _bool(a.get("confirm", False)):
        gui("POST", "/settings/backup/apply", form={"cancel": True}, client=c)
        return {"ok": True, "applied": False, "preview": preview,
                "message": _t("Nur geprüft, nichts geändert. Mit confirm=true übernehmen.")}
    if not p.get("ok"):
        gui("POST", "/settings/backup/apply", form={"cancel": True}, client=c)
        raise ApiError(400, " ".join(preview["notes"]) or _t("Fehler"))
    r2 = gui("POST", "/settings/backup/apply", form={"confirm": True, "files": _bool(a.get("files", True)),
                                                       "logs": _bool(a.get("logs", False))}, client=c)
    return {"ok": True, "applied": True, "preview": preview, "message": done(r2)}


@action("import_backup", "POST", "/backup/import", ADMIN, "Sicherung",
        "Exportdatei prüfen und mit confirm=true übernehmen (vorher automatische Sicherung). REST: multipart 'file' oder JSON "
        "data_base64 + filename. files (Standard true): Dateien aus config übernehmen; logs: Lauf-Logs übernehmen.",
        {"data_base64": S(STR), "filename": S(STR), "password": S(STR), "confirm": S(BOOL), "files": S(BOOL), "logs": S(BOOL)},
        files=True)
def a_import(a):
    need_any(ADMIN)
    up = a.get("_file")
    if up:
        name, blob = up
    else:
        try:
            blob = base64.b64decode(a.get("data_base64") or "", validate=True)
        except ValueError:
            raise ApiError(400, _t("data_base64 ist kein gültiges Base64."))
        name = a.get("filename") or "import.zip"
    if not blob:
        raise ApiError(400, _t("Bitte eine Exportdatei auswählen."))
    c = core.app.test_client()
    r = gui("POST", "/settings/backup/import", form={"password": a.get("password", "")}, files={"file": (name, blob)}, client=c)
    return _stage_and_apply(c, r, a)


@action("restore_backup", "POST", "/backup/files/{name}/restore", ADMIN, "Sicherung",
        "Gespeicherte Sicherung prüfen und mit confirm=true wiederherstellen (Passwort der automatischen Sicherung wird genutzt).",
        {"name": S(STR), "password": S(STR), "confirm": S(BOOL), "files": S(BOOL), "logs": S(BOOL)}, ["name"])
def a_restore(a):
    need_any(ADMIN)
    if not core._backup_by_name(a["name"]):
        raise ApiError(404, _t("Nicht gefunden."))
    c = core.app.test_client()
    r = gui("POST", f"/settings/backup/file/{a['name']}/restore", form={"password": a.get("password", "")}, client=c)
    return _stage_and_apply(c, r, a)


# ================================================================= Registrierung
def _flask_path(p):
    return re.sub(r"\{(\w+)\}", r"<\1>", p)


def _openapi_paths():
    paths = {}
    for x in ACTIONS:
        params, body_props = [], {}
        path_names = re.findall(r"\{(\w+)\}", x["path"])
        for n in path_names:
            params.append({"name": n, "in": "path", "required": True, "schema": {"type": "string"}})
        for n, sch in x["props"].items():
            if n in path_names:
                continue
            if x["method"] == "GET":
                params.append({"name": n, "in": "query", "required": n in x["required"],
                               "schema": {k: v for k, v in sch.items() if k != "description"} or {"type": "string"},
                               "description": sch.get("description", "")})
            else:
                body_props[n] = sch
        perm = "admin" if x["perm"] == ADMIN else x["perm"]
        o = {"summary": x["summary"], "tags": [x["tag"]], "operationId": x["tool"],
             "responses": {"200": {"description": "Erfolg"}, "400": {"description": "Ungültige Anfrage"},
                           "401": {"description": "API-Key fehlt oder ungültig"}, "403": {"description": "Recht fehlt"}}}
        if perm:
            o["description"] = f"Benötigtes Recht: `{perm}`"
        if params:
            o["parameters"] = params
        if body_props:
            schema = {"type": "object", "properties": body_props,
                      "required": [n for n in x["required"] if n in body_props]}
            content = {"application/json": {"schema": schema}}
            if x["files"]:
                content["multipart/form-data"] = {"schema": {"type": "object", "properties": {
                    "file": {"type": "string", "format": "binary"}, "password": {"type": "string"},
                    "confirm": {"type": "boolean"}, "files": {"type": "boolean"}, "logs": {"type": "boolean"}}}}
            o["requestBody"] = {"required": bool(schema["required"]), "content": content}
        paths.setdefault(x["path"], {})[x["method"].lower()] = o
    return paths


# ================================================================= Dateimanager (ab 1.27.0)
LOC = S(STR, "Speicherort (Name wie bei list_file_locations, z. B. nas) oder /data")
FPATH = S(STR, "Pfad relativ zum Speicherort, z. B. Ordner/datei.txt; leer = oberste Ebene")


def _fop(op, payload):
    r = gui("POST", f"/files/op/{op}", js=payload)
    body = r["resp"].get_json(silent=True) or {}
    if r["out"].get("denied") or r["status"] == 403 and not body.get("error"):
        done(r)
    if r["status"] >= 400 or not body.get("ok", True):
        msg = body.get("error") or _t("Fehler")
        if body.get("exists"):
            msg += " (overwrite=true)"
        raise ApiError(r["status"] if r["status"] >= 400 else 400, msg)
    body.pop("status", None)
    return body


def _fargs(a, keys):
    _check_keys(a, keys)
    return {k: a[k] for k in keys if k in a}


@action("list_file_locations", "GET", "/files/locations", "files.view", "Dateien",
        "Speicherorte, die im Dateimanager sichtbar sind (inkl. /data mit Recht local.paths).", ro=True)
def a_flocs(a):
    return _fop("locations", {})


@action("list_files", "GET", "/files/list", "files.view", "Dateien",
        "Ordner auflisten: Name, Ordner ja/nein, Größe, Änderungszeit, Berechtigungen (mode, wenn der Typ sie liefert).",
        {"loc": LOC, "path": FPATH}, ["loc"], ro=True)
def a_flist(a):
    return _fop("list", _fargs(a, ("loc", "path")))


@action("file_size", "GET", "/files/size", "files.view", "Dateien", "Größe sowie Anzahl Dateien (files) und Unterordner (dirs) eines Ordners, rekursiv.",
        {"loc": LOC, "path": FPATH}, ["loc"], ro=True)
def a_fsize(a):
    return _fop("size", _fargs(a, ("loc", "path")))


@action("file_info", "GET", "/files/info", "files.view", "Dateien",
        "Eigenschaften einer Datei oder eines Ordners: Größe, Zeit, Berechtigungen (rwx), Besitzer uid:gid.",
        {"loc": LOC, "path": FPATH}, ["loc", "path"], ro=True)
def a_finfo(a):
    return _fop("info", _fargs(a, ("loc", "path")))


@action("read_file", "GET", "/files/read", "files.view", "Dateien",
        "Datei lesen: Text (UTF-8, bis 1 MB) als content, mit binary=true als content_base64 (bis 5 MB).",
        {"loc": LOC, "path": FPATH, "binary": S(BOOL)}, ["loc", "path"], ro=True)
def a_fread(a):
    return _fop("read", _fargs(a, ("loc", "path", "binary")))


@action("write_file", "POST", "/files/write", "files.edit", "Dateien",
        "Datei schreiben: content (Text) oder content_base64. Neue Datei mit path = Ordner und name. "
        "Eine bestehende Datei wird nur mit overwrite=true überschrieben.",
        {"loc": LOC, "path": FPATH, "name": S(STR), "content": S(STR), "content_base64": S(STR), "overwrite": S(BOOL)},
        ["loc", "path"])
def a_fwrite(a):
    return _fop("write", _fargs(a, ("loc", "path", "name", "content", "content_base64", "overwrite")))


@action("upload_file", "POST", "/files/upload", "files.edit", "Dateien",
        "Datei hochladen (REST: multipart mit file, loc, path = Zielordner, overwrite).",
        {"loc": LOC, "path": FPATH, "overwrite": S(BOOL)}, ["loc"], files=True)
def a_fupload(a):
    up = a.get("_file")
    if not up:
        raise ApiError(400, _t("Keine Datei."))
    r = gui("POST", "/files/upload", form={"loc": a.get("loc", ""), "path": a.get("path", ""),
                                           "overwrite": "1" if _bool(a.get("overwrite", False)) else ""}, files={"file": up})
    body = r["resp"].get_json(silent=True) or {}
    if r["status"] >= 400:
        raise ApiError(r["status"], (body.get("error") or _t("Fehler")) + (" (overwrite=true)" if body.get("exists") else ""))
    return body


@action("download_file", "GET", "/files/download", "files.view", "Dateien",
        "Datei herunterladen (REST: Datei, MCP: data_base64 bis 25 MB).", {"loc": LOC, "path": FPATH}, ["loc", "path"], ro=True)
def a_fdownload(a):
    from urllib.parse import urlencode
    r = gui("GET", "/files/download?" + urlencode({"loc": a.get("loc", ""), "path": a.get("path", "")}))
    if r["status"] >= 400:
        body = r["resp"].get_json(silent=True) or {}
        raise ApiError(r["status"], body.get("error") or _t("Fehler"))
    resp = r["resp"]
    name = (a.get("path") or "datei").rsplit("/", 1)[-1]
    blob = resp.get_data()
    if not a.get("_mcp"):
        from urllib.parse import quote
        return Response(blob, mimetype="application/octet-stream",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})
    if len(blob) > 25 * 1024 * 1024:
        raise ApiError(413, _t("Die Datei ist für MCP zu groß, bitte über die REST-API herunterladen."))
    return {"filename": name, "size": len(blob), "data_base64": base64.b64encode(blob).decode()}


@action("create_folder", "POST", "/files/mkdir", "files.edit", "Dateien", "Ordner anlegen: name in path.",
        {"loc": LOC, "path": FPATH, "name": S(STR)}, ["loc", "name"])
def a_fmkdir(a):
    return _fop("mkdir", _fargs(a, ("loc", "path", "name")))


@action("rename_file", "POST", "/files/rename", "files.edit", "Dateien", "Datei oder Ordner umbenennen (im selben Ordner).",
        {"loc": LOC, "path": FPATH, "new_name": S(STR)}, ["loc", "path", "new_name"])
def a_frename(a):
    return _fop("rename", _fargs(a, ("loc", "path", "new_name")))


@action("delete_files", "POST", "/files/delete", "files.delete", "Dateien",
        "Dateien oder Ordner (mit Inhalt) endgültig löschen. paths = Liste oder path; nur mit confirm=true.",
        {"loc": LOC, "path": FPATH, "paths": STRS, "confirm": S(BOOL)}, ["loc", "confirm"])
def a_fdelete(a):
    return _fop("delete", _fargs(a, ("loc", "path", "paths", "confirm")))


TRANSFER = {"loc": LOC, "path": FPATH, "paths": STRS, "dst_loc": S(STR, "Ziel-Speicherort, leer = derselbe"),
            "dst_path": S(STR, "Zielordner"), "new_name": S(STR, "neuer Name (nur bei einem Eintrag)"),
            "overwrite": S(BOOL, "vorhandene Einträge im Ziel überschreiben")}
TKEYS = ("loc", "path", "paths", "dst_loc", "dst_path", "new_name", "overwrite")


@action("copy_files", "POST", "/files/copy", "files.edit", "Dateien",
        "Dateien/Ordner kopieren, auch in einen anderen Speicherort. Läuft im Hintergrund, Fortschritt mit list_file_tasks. "
        "Gibt es im Ziel schon etwas, Fehler 409, dann mit overwrite=true.", TRANSFER, ["loc", "dst_path"])
def a_fcopy(a):
    return _fop("copy", _fargs(a, TKEYS))


@action("move_files", "POST", "/files/move", "files.edit", "Dateien",
        "Dateien/Ordner verschieben, auch in einen anderen Speicherort (braucht auch files.delete). Läuft im Hintergrund.",
        TRANSFER, ["loc", "dst_path"])
def a_fmove(a):
    return _fop("move", _fargs(a, TKEYS))


@action("list_running_jobs", "GET", "/jobs/running", "jobs.view", "Aufgaben",
        "Gerade laufende Aufgaben mit Fortschritt in Prozent (nur solange sie laufen).", ro=True)
def a_running(a):
    r = gui("GET", "/jobs/running")
    done(r)
    return {"jobs": (r["resp"].get_json(silent=True) or {}).get("jobs", [])}


@action("list_file_tasks", "GET", "/files/tasks", "files.view", "Dateien",
        "Kopier- und Verschiebe-Aufträge mit Status (läuft, ok, fehler, abgebrochen) und Fortschritt in Prozent.", ro=True)
def a_ftasks(a):
    return _fop("tasks", {})


@action("cancel_file_task", "POST", "/files/tasks/{task_id}/cancel", "files.edit", "Dateien", "Laufenden Auftrag abbrechen.",
        {"task_id": S(STR)}, ["task_id"])
def a_fcancel(a):
    return _fop("cancel", {"task_id": a["task_id"]})


@action("delete_file_task", "DELETE", "/files/tasks/{task_id}", "files.edit", "Dateien",
        "Fertigen Auftrag (ok, fehler, abgebrochen) aus der Liste entfernen. Laufende erst abbrechen.",
        {"task_id": S(STR)}, ["task_id"])
def a_fdeltask(a):
    return _fop("remove_tasks", {"task_id": a["task_id"]})


@action("clear_file_tasks", "POST", "/files/tasks/clear", "files.edit", "Dateien",
        "Alle fertigen Aufträge aus der Liste entfernen (laufende bleiben).")
def a_fcleartasks(a):
    return _fop("remove_tasks", {"finished": True})


def register(app, core_module):
    global core
    core = core_module
    R = "/api/v1"

    def make_view(x):
        def view(**kw):
            a = {}
            for k, v in request.args.items():
                if k != "lang":   # ?lang= waehlt nur die Sprache der Antwort
                    a[k] = v
            if request.mimetype == "multipart/form-data":
                for k, v in request.form.items():
                    a[k] = v
                f = request.files.get("file")
                if f and f.filename:
                    a["_file"] = (f.filename, f.read(core.UPLOAD_MAX + 1))
            elif request.method != "GET" and request.get_data():
                body = request.get_json(silent=True)
                if not isinstance(body, dict):
                    return jsonify({"error": _t("JSON-Body erwartet (Content-Type: application/json).")}), 400
                a.update(body)
            a.update(kw)
            try:
                need_any(x["perm"])
                res = x["fn"](a)
            except ApiError as e:
                return jsonify({"error": e.msg}), e.status
            if isinstance(res, Response):
                return res
            return jsonify(res), (201 if x["method"] == "POST" and x["tool"].startswith("create_") else 200)
        return view

    for x in ACTIONS:
        app.add_url_rule(R + _flask_path(x["path"]), "apix_" + x["tool"], make_view(x), methods=[x["method"]])
        props = dict(x["props"])
        api.TOOLS.append((x["tool"], x["summary"], x["perm"], _schema(props, x["required"]),
                          (lambda fn: lambda a: fn(dict(a, _mcp=True)))(x["fn"]), x["ro"]))
    api.EXTRA_PATHS = _openapi_paths
