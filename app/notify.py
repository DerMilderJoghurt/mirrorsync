"""Benachrichtigungen: Webhook, E-Mail (SMTP), Telegram und Apprise."""
import json
import re
import os
import smtplib
import ssl
import urllib.error
import urllib.parse
import urllib.request
import time

import i18n
import msgtpl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

TELEGRAM_API = os.environ.get("TELEGRAM_API_BASE", "https://api.telegram.org")
SECRET_FIELDS = {"smtp_pass", "telegram_token", "apprise_urls", "apprise_api_key"}

DEFAULTS = {
    "when": "fail",  # always | fail | never
    "webhook_enabled": False, "webhook_url": "", "webhook_method": "POST", "webhook_body": "",
    "smtp_enabled": False, "smtp_host": "", "smtp_port": "587", "smtp_security": "starttls",
    "smtp_user": "", "smtp_pass": "", "smtp_from": "", "smtp_to": "",
    "telegram_enabled": False, "telegram_token": "", "telegram_chat_id": "",
    # Apprise: "lib" = URLs direkt im Container senden, "api" = an einen Apprise-API-Server
    "apprise_enabled": False, "apprise_mode": "lib", "apprise_urls": "", "apprise_api_url": "",
    "apprise_api_key": "", "apprise_tag": "",
    # Ruhezeiten und Wochenbericht (Listen quiet_days, report_days, report_channels stehen in LIST_DEFAULTS)
    "quiet_enabled": False, "quiet_start": "22:00", "quiet_end": "07:00", "quiet_mode": "errors",
    "report_enabled": False, "report_time": "08:00", "report_period": "7",
}
LIST_DEFAULTS = {"quiet_days": [], "report_days": [0], "report_channels": []}


JOB_FIELDS = ("notify_mode", "notify_when", "notify_webhook", "notify_webhook_url", "notify_smtp",
              "notify_smtp_to", "notify_telegram", "notify_telegram_chat_id", "notify_telegram_token",
              "notify_apprise", "notify_apprise_urls", "notify_apprise_tag")


def job_config(settings, job):
    """Benachrichtigungs-Einstellungen einer Aufgabe, aeltere Versionen (Feld 'notify') werden uebernommen."""
    if "notify_mode" in job:
        cfg = {k: job.get(k) for k in JOB_FIELDS}
    else:
        old = job.get("notify") or "global"
        cfg = {"notify_mode": {"global": "global", "never": "off"}.get(old, "custom"),
               "notify_when": old if old in ("always", "fail") else "fail",
               "notify_webhook": bool(settings.get("webhook_enabled")), "notify_webhook_url": "",
               "notify_smtp": bool(settings.get("smtp_enabled")), "notify_smtp_to": "",
               "notify_telegram": bool(settings.get("telegram_enabled")), "notify_telegram_chat_id": "",
               "notify_telegram_token": ""}
    cfg["notify_mode"] = cfg.get("notify_mode") or "global"
    cfg["notify_when"] = cfg.get("notify_when") or "fail"
    return cfg


def effective(settings, job):
    """Liefert (wann, Einstellungen mit den Kanaelen und Zielen dieser Aufgabe)."""
    cfg = job_config(settings, job)
    if cfg["notify_mode"] == "off":
        return "never", settings
    if cfg["notify_mode"] == "global":
        return settings.get("when", "fail"), settings
    eff = dict(settings)
    eff["webhook_enabled"] = bool(cfg.get("notify_webhook"))
    eff["smtp_enabled"] = bool(cfg.get("notify_smtp"))
    eff["telegram_enabled"] = bool(cfg.get("notify_telegram"))
    eff["apprise_enabled"] = bool(cfg.get("notify_apprise"))
    for src, dst in (("notify_webhook_url", "webhook_url"), ("notify_smtp_to", "smtp_to"),
                     ("notify_telegram_chat_id", "telegram_chat_id"), ("notify_telegram_token", "telegram_token"),
                     ("notify_apprise_urls", "apprise_urls"), ("notify_apprise_tag", "apprise_tag")):
        if (cfg.get(src) or "").strip():
            eff[dst] = cfg[src].strip()
    return cfg["notify_when"], eff


def should_send(when, ok):
    return when == "always" or (when == "fail" and not ok)


def describe(settings, job):
    """Kurzbeschreibung fuer die Uebersicht, z. B. 'bei Fehler: Telegram, E-Mail'."""
    when, eff = effective(settings, job)
    names = [n for k, n in (("webhook", "Webhook"), ("smtp", "E-Mail"), ("telegram", "Telegram"), ("apprise", "Apprise")) if eff.get(f"{k}_enabled")]
    if when == "never" or not names:
        return ""
    return ("immer" if when == "always" else "bei Fehler") + ": " + ", ".join(names)


def classify(line):
    """Ordnet eine rclone-Logzeile ein: error, copied, deleted, warn, notice oder other."""
    if "ERROR :" in line or "CRITICAL:" in line:
        return "error"
    if "Copied (" in line or "Skipped copy as --dry-run" in line or "Skipped update modification time as --dry-run" in line:
        return "copied"
    if ("Deleted" in line and "INFO  :" in line) or "Moved into backup dir" in line or "Skipped delete as --dry-run" in line \
            or "Skipped move as --dry-run" in line:
        return "deleted"
    if "WARNING" in line or "WARN :" in line or ("NOTICE:" in line and not _STATS_LINE.search(line)
                                                   and not _QUIET_NOTICE.search(line)):
        return "warn"   # rclone meldet Warnungen als NOTICE (z. B. Symlinks, fehlende Prüfsumme, --max-delete); seit 1.58.0
    if "NOTICE:" in line or line.startswith("==="):
        return "notice"
    return "other"


# Statuszeilen (--stats-one-line) und reine Hinweise von rclone sind keine Warnungen
_STATS_LINE = re.compile(r"NOTICE:\s*(?:[\d.]+\s*[KMGTPE]?i?B(?:ytes)?\s*/|Transferred:|Checks:|Elapsed time:|Errors:|Deleted:|Renamed:|Server Side)")
_QUIET_NOTICE = re.compile(r"NOTICE: (?:Config file .* not found|Encrypted drive|.*: Dry run|.*Skipped (?:copy|delete|update|move|make directory|remove directory|set directory modification time) as --dry-run)")


def summarize_log(path):
    """Zaehlt Kopiert/Geloescht/Fehler und holt die letzten Fehlerzeilen aus dem Log."""
    copied = deleted = 0
    errors = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                kind = classify(line)
                if kind == "copied":
                    copied += 1
                elif kind == "deleted":
                    deleted += 1
                elif kind == "error":
                    errors.append(line.split(":", 3)[-1].strip() if "ERROR :" not in line else line.split("ERROR :", 1)[1].strip())
    except OSError:
        pass
    return copied, deleted, errors


VERSION = ""


def _dur(sec):
    sec = int(sec)
    if sec < 60:
        return f"{sec} s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m} min {s} s"
    h, m = divmod(m, 60)
    return f"{h} h {m} min"


def base_values():
    return {"datum": time.strftime("%d.%m.%Y"), "zeit": time.strftime("%H:%M:%S"), "version": VERSION}


TR_VALUES = ("status", "testlauf", "fehler_block", "art", "gestartet_von", "anmeldungen", "sperre", "wie_lange",
             "verschluesselt", "dauer")


def event(settings, kind, values, job_cfg=None, **fields):
    """Ereignis mit Betreff/Text aus der Vorlage bauen. fields: weitere Felder fuer den Webhook (status, ok …)."""
    vals = dict(base_values(), **values)
    for k in TR_VALUES:   # feste Texte in den Werten in der Systemsprache
        if isinstance(vals.get(k), str) and vals[k]:
            vals[k] = i18n.translate(vals[k], lang=i18n.default_lang)
    title, body = msgtpl.make(settings, kind, vals, job_cfg)
    vals.update(titel=title, nachricht=body, ereignis=kind)
    ev = {"title": title, "message": body, "event": kind, "vars": vals, "job": "", "status": kind, "ok": False,
          "dry_run": False, "duration": 0, "source": "", "dest": "", "copied": 0, "deleted": 0, "errors": []}
    ev.update(fields)
    vals["ok"] = "true" if ev.get("ok") else "false"
    return ev


def build_event(job, status, duration, dry, log_path, settings=None, by="", mode="full", extra=None):
    copied, deleted, errors = summarize_log(log_path)
    ok = status == "ok"
    end = time.time()
    err5 = ["• " + e[:300] for e in errors[-5:]]
    values = {
        "job": job["name"], "status": "OK" if ok else status.upper(), "status_icon": "✅" if ok else "❌",
        "testlauf": " (Testlauf)" if dry else "", "quelle": job["source"], "ziel": job["dest"],
        "start": time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(end - duration)),
        "ende": time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(end)), "dauer": _dur(duration), "dauer_s": str(duration),
        "kopiert": str(copied), "geloescht": str(deleted), "fehler": str(len(errors)), "fehler_liste": "\n".join(err5),
        "fehler_block": ("\nLetzte Fehler:\n" + "\n".join(err5)) if errors else "", "gestartet_von": by,
        "art": "Live" if mode == "delta" else "Spiegel", "pruefung": "", "pruefung_block": "", "versuch": "",
    }
    values.update(extra or {})
    return event(settings or {}, "run_ok" if ok else "run_fail", values, job,
                 job=job["name"], status=status, ok=ok, dry_run=dry, duration=duration, source=job["source"],
                 dest=job["dest"], copied=copied, deleted=deleted, errors=errors[-5:])


def send_webhook(s, ev):
    tpl = (s.get("webhook_body") or "").strip()
    data = None
    if tpl:
        vals = msgtpl.all_blank()   # Variablen anderer Ereignisse leer bzw. 0, damit das JSON gueltig bleibt
        vals.update(ev.get("vars") or {"titel": ev["title"], "nachricht": ev["message"]})
        out = msgtpl.webhook_body(tpl, vals)
        try:
            json.loads(out)
            data = out.encode()
        except ValueError:
            data = None   # Vorlage passt nicht zu diesem Ereignis: Standard-JSON senden
    if data is None:
        body = {k: v for k, v in ev.items() if k != "vars"}
        body["text"] = body["content"] = ev["message"]  # passt fuer Slack, Mattermost, Discord, ntfy
        data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(s["webhook_url"], data=data, method=s.get("webhook_method") or "POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "MirrorSync",
                                          "Title": ev["title"].encode("ascii", "ignore").decode().strip()})
    with urllib.request.urlopen(req, timeout=15) as r:
        r.read()


def send_mail(s, ev):
    msg = EmailMessage()
    msg["Subject"] = ev["title"]
    msg["From"] = s["smtp_from"] or s["smtp_user"]
    msg["To"] = s["smtp_to"]
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid("mirrorsync")
    msg.set_content(ev["message"])
    port = int(s.get("smtp_port") or 587)
    ctx = ssl.create_default_context()
    if s.get("smtp_security") == "ssl":
        server = smtplib.SMTP_SSL(s["smtp_host"], port, timeout=20, context=ctx)
    else:
        server = smtplib.SMTP(s["smtp_host"], port, timeout=20)
        if s.get("smtp_security") == "starttls":
            server.starttls(context=ctx)
    with server:
        if s.get("smtp_user"):
            server.login(s["smtp_user"], s["smtp_pass"])
        server.send_message(msg, to_addrs=[a.strip() for a in s["smtp_to"].replace(";", ",").split(",") if a.strip()])


def send_telegram(s, ev):
    url = f"{TELEGRAM_API}/bot{s['telegram_token']}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": s["telegram_chat_id"], "text": ev["message"][:4000],
                                   "disable_web_page_preview": "true"}).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        res = json.loads(r.read() or b"{}")
        if not res.get("ok", False):
            raise RuntimeError(res.get("description", "Telegram-Fehler"))


def apprise_list(text):
    """Apprise-URLs aus Textfeld: eine pro Zeile, auch mit Komma/Leerzeichen getrennt; # = Kommentar."""
    out = []
    for line in (text or "").replace("\r", "").split("\n"):
        line = line.split("#", 1)[0].strip() if line.strip().startswith("#") else line.strip()
        for part in line.replace(",", " ").split():
            if "://" in part:
                out.append(part)
    return out


def mask_url(u):
    """'discord://123/abc' -> 'discord://•••' fuer die Anzeige."""
    scheme = u.split("://", 1)[0]
    return f"{scheme}://•••"


def _apprise_type(ev):
    if ev.get("status") == "test" or ev.get("ok"):
        return "success" if ev.get("status") != "test" else "info"
    return "failure"


def send_apprise(s, ev):
    mode = s.get("apprise_mode") or "lib"
    urls = apprise_list(s.get("apprise_urls"))
    tag = (s.get("apprise_tag") or "").strip()
    if mode == "api":
        base = (s.get("apprise_api_url") or "").strip().rstrip("/")
        if not base:
            raise ValueError("Keine Adresse des Apprise-API-Servers eingetragen.")
        key = (s.get("apprise_api_key") or "").strip()
        body = {"title": ev["title"], "body": ev["message"], "type": _apprise_type(ev), "format": "text"}
        if key:   # gespeicherte Konfiguration auf dem Server
            url = f"{base}/notify/{urllib.parse.quote(key, safe='')}"
            if tag:
                body["tag"] = tag
        else:     # zustandslos: URLs mitschicken
            if not urls:
                raise ValueError("Ohne Konfigurations-Key bitte Apprise-URLs eintragen.")
            url, body["urls"] = f"{base}/notify", ",".join(urls)
        req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "Accept": "application/json",
                                              "User-Agent": "MirrorSync"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                r.read()
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode("utf-8", "replace")
            raise RuntimeError(f"Apprise-API antwortet {e.code}: {detail}") from None
        return
    if not urls:
        raise ValueError("Keine Apprise-URLs eingetragen.")
    try:
        import apprise
    except ImportError:
        raise RuntimeError("Apprise-Bibliothek fehlt im Container. Bitte Image neu bauen.") from None
    ap = apprise.Apprise()
    bad = [mask_url(u) for u in urls if not ap.add(u)]
    if bad:
        raise ValueError("Ungültige oder unbekannte Apprise-URL: " + ", ".join(bad))
    ntype = {"success": apprise.NotifyType.SUCCESS, "failure": apprise.NotifyType.FAILURE}.get(_apprise_type(ev),
                                                                                               apprise.NotifyType.INFO)
    if not ap.notify(body=ev["message"], title=ev["title"], notify_type=ntype, body_format=apprise.NotifyFormat.TEXT):
        raise RuntimeError("Apprise konnte nicht an alle Ziele senden (Details im Container-Log).")


CHANNELS = {"webhook": send_webhook, "smtp": send_mail, "telegram": send_telegram, "apprise": send_apprise}


# Ruhezeiten: Hinweise (Erfolg, Sicherung, Update) werden unterdrueckt, Fehler je nach Einstellung auch
INFO_EVENTS = {"run_ok", "backup_ok", "backup_skip", "update_available"}
NEVER_QUIET = {"test", "report"}


def _hm(v, default):
    v = (v or "").strip()
    return v if len(v) == 5 and v[2] == ":" and v[:2].isdigit() and v[3:].isdigit() else default


def quiet_now(settings, now=None):
    """True, wenn gerade Ruhezeit ist (Beginn bis Ende, auch ueber Mitternacht; Tage = Wochentag des Beginns)."""
    if not settings.get("quiet_enabled"):
        return False
    now = now or time.localtime()
    t = f"{now.tm_hour:02d}:{now.tm_min:02d}"
    a, b = _hm(settings.get("quiet_start"), "22:00"), _hm(settings.get("quiet_end"), "07:00")
    days = settings.get("quiet_days")
    days = list(range(7)) if days in (None, "", []) else [int(d) for d in days]
    wd = now.tm_wday
    if a == b:
        return wd in days
    if a < b:
        return wd in days and a <= t < b
    return (wd in days and t >= a) or (((wd - 1) % 7) in days and t < b)


def quiet_blocks(settings, ev):
    """Soll dieses Ereignis wegen der Ruhezeit nicht gesendet werden?"""
    kind = ev.get("event") or ""
    if kind in NEVER_QUIET or not quiet_now(settings):
        return False
    if kind in INFO_EVENTS or (kind in ("run_ok", "run_fail") and ev.get("ok")):
        return True
    return settings.get("quiet_mode") == "none"


def send(settings, ev, only=None, force=False):
    """Schickt an alle aktiven Kanaele (oder nur einen). Liefert {kanal: None | Fehlertext}.
    In der Ruhezeit bleibt das Ergebnis leer, ausser force=True (Tests)."""
    results = {}
    if not only and not force and quiet_blocks(settings, ev):
        return results
    for name, fn in CHANNELS.items():
        if only and name != only:
            continue
        if not only and not settings.get(f"{name}_enabled"):
            continue
        try:
            fn(settings, ev)
            results[name] = None
        except Exception as e:  # Benachrichtigung darf den Sync nie stoeren
            results[name] = f"{type(e).__name__}: {e}"
    return results
