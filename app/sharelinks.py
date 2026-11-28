"""Zeitlich begrenzte Freigabelinks fuer Dateien aus dem Dateimanager (seit 1.58.0).

Ein Link /s/<token> laesst jeden, der ihn kennt, genau eine Datei herunterladen, bis er ablaeuft (optional mit Passwort
und hoechstens N Downloads). Angemeldet sein muss man dafuer nicht; die Zugriffsregeln (IP und Land) gelten trotzdem.
Gespeichert wird der rclone-Pfad, den der Ersteller beim Anlegen sehen durfte. Recht: files.share."""
import secrets
import subprocess
import time
from urllib.parse import quote

from flask import Response, g, jsonify, render_template_string, request, stream_with_context
from werkzeug.security import check_password_hash, generate_password_hash

core = None
fm = None
NS = "share"
DURATIONS = {"1h": 3600, "24h": 86400, "7d": 7 * 86400, "30d": 30 * 86400, "90d": 90 * 86400}


def _all():
    return core.DB.get_map(NS)


def _save(sid, entry):
    core.DB.put(NS, sid, entry)


def _delete(sid):
    data = _all()
    if sid in data:
        data.pop(sid)
        core.DB.put_map(NS, data)


def max_seconds():
    try:
        return max(1, int(core.load_settings().get("share_max_days") or 30)) * 86400
    except ValueError:
        return 30 * 86400


def enabled():
    return bool(core.load_settings().get("share_enabled", True))


def link(sid):
    base = (core.load_settings().get("public_url") or "").strip().rstrip("/")
    if not base:
        try:
            base = request.host_url.rstrip("/")
        except RuntimeError:
            base = ""
    return f"{base}/s/{sid}"


def state(e, now=None):
    now = now or time.time()
    if e.get("revoked"):
        return "revoked"
    if e.get("expires", 0) <= now:
        return "expired"
    if e.get("max_downloads") and e.get("downloads", 0) >= e["max_downloads"]:
        return "used"
    return "active"


def view(sid, e):
    return {"id": sid, "url": link(sid), "name": e.get("name"), "display": e.get("display"), "size": e.get("size"),
            "created": e.get("created"), "created_by": e.get("created_by"),
            "expires": time.strftime("%Y-%m-%d %H:%M", time.localtime(e.get("expires", 0))),
            "max_downloads": e.get("max_downloads") or 0, "downloads": e.get("downloads", 0), "password": bool(e.get("pw")),
            "last_download": e.get("last_download", ""), "state": state(e)}


def visible():
    """Links, die der Benutzer sehen darf: Admins alle, sonst die eigenen."""
    out = []
    for sid, e in sorted(_all().items(), key=lambda kv: kv[1].get("created", ""), reverse=True):
        if g.role == "admin" or (e.get("created_by") or "").lower() == (g.user or "").lower():
            out.append(view(sid, e))
    return out


def create(loc, path, duration="24h", seconds=None, max_downloads=0, password="", note=""):
    if not enabled():
        raise fm.FileError(403, "Freigabelinks sind ausgeschaltet (Einstellungen → Allgemein → Dateimanager).")
    full, rel, disp = fm.resolve(loc, path)
    it = fm._stat(full) if rel else None
    if not it or it.get("IsDir"):
        raise fm.FileError(404, "Datei nicht gefunden. Freigeben lassen sich nur einzelne Dateien.")
    secs = int(seconds) if seconds else DURATIONS.get(duration, 86400)
    secs = max(60, min(secs, max_seconds()))
    try:
        md = max(0, min(int(max_downloads or 0), 100000))
    except (TypeError, ValueError):
        md = 0
    sid = secrets.token_urlsafe(24)
    entry = {"full": full, "display": disp, "name": rel.rsplit("/", 1)[-1], "size": it.get("Size"), "loc": loc, "path": rel,
             "created": time.strftime("%Y-%m-%d %H:%M"), "created_by": g.user or "", "expires": int(time.time() + secs),
             "max_downloads": md, "downloads": 0, "note": str(note or "")[:200]}
    if password:
        entry["pw"] = generate_password_hash(str(password))
    _save(sid, entry)
    core.audit_add("files", "Freigabelink erstellt", disp, detail=f"gültig bis {time.strftime('%Y-%m-%d %H:%M', time.localtime(entry['expires']))}"
                   + (f", höchstens {md} Downloads" if md else "") + (", mit Passwort" if password else ""))
    return view(sid, entry)


def revoke(sid):
    e = _all().get(sid)
    if not e:
        raise fm.FileError(404, "Freigabelink nicht gefunden.")
    if g.role != "admin" and (e.get("created_by") or "").lower() != (g.user or "").lower():
        raise fm.FileError(403, "Nur der Ersteller oder ein Admin kann den Link löschen.")
    _delete(sid)
    core.audit_add("files", "Freigabelink gelöscht", e.get("display", ""))
    return True


def cleanup(days=7):
    """Abgelaufene bzw. verbrauchte Links nach einigen Tagen entfernen."""
    now = time.time()
    data = _all()
    keep = {k: v for k, v in data.items() if state(v, now) == "active" or v.get("expires", 0) > now - days * 86400}
    if len(keep) != len(data):
        core.DB.put_map(NS, keep)


PAGE = """<!doctype html><html lang="{{ lang }}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{{ name or 'MirrorSync' }}</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<style>body{font:15px/1.5 system-ui,sans-serif;background:#f6f7f9;color:#18181b;margin:0;display:grid;place-items:center;min-height:100vh}
@media(prefers-color-scheme:dark){body{background:#09090b;color:#f4f4f5}.box{background:#18181b!important;border-color:#27272a!important}input{background:#09090b;color:#f4f4f5;border-color:#3f3f46}}
.box{background:#fff;border:1px solid #e4e4e7;border-radius:14px;padding:28px;width:min(440px,92vw);box-sizing:border-box}h1{font-size:19px;margin:0 0 4px;overflow-wrap:anywhere}
.mut{color:#71717a;font-size:13px}.btn{display:inline-block;background:#4f46e5;color:#fff;border:0;border-radius:8px;padding:10px 18px;font:inherit;text-decoration:none;cursor:pointer;margin-top:14px}
input{width:100%;box-sizing:border-box;padding:9px 10px;border:1px solid #d4d4d8;border-radius:8px;font:inherit;margin-top:10px}.err{color:#dc2626}</style></head>
<body><div class="box">{% if msg %}<h1>{{ msg }}</h1><p class="mut">{{ hint }}</p>{% else %}
<div class="mut">{{ t_shared }}</div><h1>📄 {{ name }}</h1><p class="mut">{{ size }} · {{ t_until }}</p>
{% if need_pw %}<form method="post" action="/s/{{ sid }}/dl">{% if bad %}<p class="err">{{ t_bad }}</p>{% endif %}<input type="password" name="password" placeholder="{{ t_pw }}" required autofocus><button class="btn">⬇ {{ t_dl }}</button></form>
{% else %}<a class="btn" href="/s/{{ sid }}/dl">⬇ {{ t_dl }}</a>{% endif %}{% endif %}
<p class="mut" style="margin:18px 0 0">MirrorSync</p></div></body></html>"""


def _page(sid=None, e=None, msg=None, hint="", bad=False, status=200):
    t = core.i18n.t
    lang = core.i18n.current()
    ctx = {"lang": lang, "msg": t(msg) if msg else None, "hint": t(hint) if hint else "", "sid": sid, "bad": bad,
           "t_shared": t("Jemand hat eine Datei mit dir geteilt."), "t_dl": t("Herunterladen"), "t_pw": t("Passwort"),
           "t_bad": t("Passwort falsch.")}
    if e:
        ctx.update(name=e.get("name"), size=core.human_bytes(e.get("size") or 0), need_pw=bool(e.get("pw")),
                   t_until=t("Link gültig bis {0}", time.strftime("%d.%m.%Y %H:%M", time.localtime(e.get("expires", 0)))))
    resp = Response(render_template_string(PAGE, **ctx), status=status, mimetype="text/html")
    resp.headers["X-Robots-Tag"] = "noindex"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


_fails = {}


def register(app, core_module, files_module):
    global core, fm
    core, fm = core_module, files_module
    core.ENDPOINT_PERMS.update({"share_create": "files.share", "share_list": "files.share", "share_delete": "files.share"})

    @app.post("/files/share")
    def share_create():
        a = request.get_json(silent=True) or request.form.to_dict()
        try:
            return jsonify(dict(ok=True, **create(a.get("loc"), a.get("path"), a.get("duration", "24h"), a.get("seconds"),
                                                  a.get("max_downloads"), a.get("password", ""), a.get("note", ""))))
        except fm.FileError as e:
            return fm._fail(e)

    @app.get("/files/shares")
    def share_list():
        return jsonify({"ok": True, "links": visible(), "max_days": max_seconds() // 86400, "enabled": enabled()})

    @app.post("/files/share/<sid>/delete")
    def share_delete(sid):
        try:
            revoke(sid)
            return jsonify({"ok": True})
        except fm.FileError as e:
            return fm._fail(e)

    def _get(sid):
        e = _all().get(sid) if sid and len(sid) < 80 else None
        if not e:
            return None, _page(msg="Link nicht gefunden.", hint="Vielleicht wurde er gelöscht oder falsch kopiert.", status=404)
        st = state(e)
        if st != "active" or not enabled():
            return None, _page(msg="Dieser Link ist nicht mehr gültig.",
                               hint="Er ist abgelaufen, wurde zu oft benutzt oder gelöscht. Bitte um einen neuen Link.", status=410)
        return e, None

    @app.get("/s/<sid>")
    def share_page(sid):
        e, err = _get(sid)
        return err or _page(sid, e)

    @app.route("/s/<sid>/dl", methods=["GET", "POST"])
    def share_download(sid):
        e, err = _get(sid)
        if err:
            return err
        ip = core._client_ip()
        if e.get("pw"):
            fails = [x for x in _fails.get(ip, []) if x > time.time() - 600]
            if len(fails) >= 10:
                return _page(sid, e, bad=True, status=429)
            if request.method != "POST" or not check_password_hash(e["pw"], request.form.get("password", "")):
                if request.method == "POST":
                    _fails[ip] = fails + [time.time()]
                return _page(sid, e, bad=request.method == "POST", status=403 if request.method == "POST" else 200)
        e["downloads"] = e.get("downloads", 0) + 1
        e["last_download"] = time.strftime("%Y-%m-%d %H:%M") + f" ({ip})"
        _save(sid, e)
        core.audit_add("files", "Freigabelink heruntergeladen", e.get("display", ""), detail=f"{e['downloads']}. Download",
                       user="Freigabelink")
        p = subprocess.Popen(["rclone", "--config", core.RCLONE_CONF, "cat", e["full"]], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)

        def gen():
            try:
                while True:
                    chunk = p.stdout.read(256 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                p.kill()
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(e.get('name') or 'download')}",
                   "X-Robots-Tag": "noindex", "Referrer-Policy": "no-referrer", "Cache-Control": "no-store"}
        if (e.get("size") or -1) >= 0:
            headers["Content-Length"] = str(e["size"])
        return Response(stream_with_context(gen()), mimetype="application/octet-stream", headers=headers, direct_passthrough=True)
