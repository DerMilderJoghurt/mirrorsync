"""Audit-Log: wer hat wann was gemacht. Eine JSON-Zeile pro Eintrag in /config/audit.jsonl."""
import csv
import io
import json
import os
import re
import threading
import time

_lock = threading.RLock()

CATEGORIES = {
    "job": "Aufgabe", "schedule": "Zeitplan", "remote": "Speicherort", "user": "Benutzer", "role": "Rolle", "group": "Gruppe",
    "settings": "Einstellungen", "access": "Zugriff (IP)", "login": "Anmeldung", "run": "Lauf", "system": "System", "api": "API-Key", "files": "Dateien",
}

# Werte, die nie im Klartext ins Log duerfen
SECRET_RE = re.compile(r"(pass|secret|token|apprise_urls|hash|backup_codes|private|key$|key_|_key|bearer|cookie|session)", re.I)
# Felder, die sich im Betrieb von selbst aendern und keine Benutzeraktion sind
NOISE = {
    "job": {"history", "last_status", "last_run", "live_last", "live_checked", "live_failing", "live_fail_count", "bisync_ready", "bisync_need_resync"},
    "user": {"last_login", "last_ip", "last_country", "last_flag", "fail_count", "auto_lock_until", "sv", "created", "totp_last", "passkeys", "webauthn_id"},
    "remote": set(), "role": set(), "group": set(), "apikey": set(), "settings": set(), "access": set(),
}

LABELS = {
    "sidebar": "Seitenleiste",
    "autobackup_enabled": "automatische Sicherung", "autobackup_schedule": "Sicherungs-Zeitplan", "autobackup_dir": "Sicherungsziel",
    "autobackup_keep": "Sicherungen behalten (Anzahl)", "autobackup_days": "Sicherungen behalten (Tage)",
    "autobackup_logs": "Logs mitsichern", "autobackup_password": "Sicherungs-Passwort", "autobackup_notify": "Sicherung melden",
    "autobackup_notify_skip": "auch ohne Änderung melden", "autobackup_channels": "Sicherung: Kanäle", "language": "Sprache", "lang": "Sprache",
    "name": "Name", "source": "Quelle", "dest": "Ziel", "schedule": "Zeitplan", "enabled": "aktiv", "dry_run": "nur Testlauf",
    "versioning": "Versionierung", "checksum": "Prüfsumme", "max_delete": "max. Löschungen", "extra_flags": "zusätzliche Optionen",
    "excludes": "Ausschlüsse", "selection": "Auswahl", "delete_excluded": "Ausgeschlossenes löschen", "include_source_dir": "Quellordner mitkopieren",
    "trigger": "Startart", "after_job": "nach Aufgabe", "after_when": "Bedingung", "live_interval": "Live-Intervall (Min.)",
    "live_full": "voller Abgleich", "live_mode": "Live-Modus", "direction": "Art", "bisync_conflict": "Konfliktregel", "bisync_max_delete": "Löschschutz (%)", "bw_mode": "Bandbreite", "bw": "eigene Bandbreite", "notify_mode": "Benachrichtigung",
    "notify_when": "benachrichtigen bei", "owner": "Besitzer", "role": "Rolle", "disabled": "deaktiviert",
    "lock_from": "gesperrt ab", "lock_until": "wieder aktiv ab", "totp_enabled": "2FA", "perms": "Rechte", "jobs": "Aufgaben",
    "remotes": "Speicherorte", "description": "Beschreibung", "type": "Typ", "allow": "Erlaubt-Liste", "block": "Sperrliste",
    "country_mode": "Länder-Regel", "countries": "Länder", "auto_attempts": "Auto-Sperre nach Fehlversuchen",
    "auto_minutes": "Auto-Sperre Minuten", "auto_window": "Zeitfenster Fehlversuche", "auto_exempt_lan": "LAN ausnehmen",
    "notify": "Benachrichtigen", "trust_proxy": "Reverse-Proxy vertrauen", "public_url": "Öffentliche Adresse", "log_keep_runs": "Logs behalten (Läufe)",
    "log_keep_days": "Logs behalten (Tage)", "audit_keep_days": "Audit-Log behalten (Tage)", "lock_attempts": "Sperre nach Fehlversuchen",
    "lock_minutes": "Sperrdauer", "fail_notify": "Fehlversuche melden", "geoip_auto": "Länder-Datenbank automatisch", "geoip_days": "Länder-Datenbank erneuern alle (Tage)", "geoip_mode": "Länder-Datenbank erneuern", "geoip_time": "Länder-Datenbank: Uhrzeit", "geoip_dow": "Länder-Datenbank: Wochentage", "visible_to": "Sichtbar für", "windows": "aktiv nur zu Zeiten", "versions_keep": "Versionen behalten", "versions_days": "Versionen höchstens Tage", "expires": "gültig bis", "ips": "erlaubte IPs", "members": "Mitglieder", "keys": "API-Keys", "bw_unit": "Einheit der Bandbreite",
    "hash": "Passwort", "pass": "Passwort", "token": "Token", "smtp_pass": "SMTP-Passwort", "telegram_token": "Telegram-Token",
    "notify_telegram_token": "Telegram-Token", "smtp_user": "SMTP-Benutzer", "host": "Server", "user": "Benutzer", "totp_secret": "2FA-Schlüssel", "backup_codes": "Backup-Codes",
    "paused": "pausiert", "paused_until": "pausiert bis", "paused_by": "pausiert von", "pause_chain": "pausiert in Kette",
    "apprise_urls": "Apprise-URLs", "notify_apprise_urls": "Apprise-URLs", "apprise_enabled": "Apprise aktiv",
    "apprise_mode": "Apprise-Art", "apprise_api_url": "Apprise-API-Server", "apprise_api_key": "Apprise-Key",
    "apprise_tag": "Apprise-Tag", "notify_apprise": "Apprise", "notify_apprise_tag": "Apprise-Tag",
    "webhook_url": "Webhook", "smtp_host": "SMTP-Server", "smtp_to": "E-Mail an", "when": "benachrichtigen bei",
}
TRIGGERS = {"time": "Uhrzeit", "after": "nach Aufgabe", "manual": "manuell", "live": "Live"}


def _short(v, n=300):
    if isinstance(v, bool):
        return "ja" if v else "nein"
    if v is None or v == "":
        return "–"
    if isinstance(v, list) and v and all(isinstance(x, dict) and "net" in x for x in v):
        v = ", ".join(x["net"] + (f" (bis {x['until'].replace('T', ' ')})" if x.get("until") else "") for x in v)
    elif isinstance(v, list) and all(isinstance(x, str) for x in v):
        v = ", ".join(v)
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    v = str(v)
    return v if len(v) <= n else v[:n] + "…"


FULL_MAX = 4000      # so viel vom vollstaendigen Wert wird fuer die Detailansicht gespeichert
ITEMS_MAX = 200


def _items(v):
    """Listen und mehrzeilige Texte als Einzelpunkte (fuer 'hinzugefuegt/entfernt')."""
    if isinstance(v, list):
        out = []
        for x in v:
            if isinstance(x, dict) and "net" in x:
                out.append(x["net"])
            elif isinstance(x, (str, int, float)):
                out.append(str(x))
            else:
                return None
        return out
    if isinstance(v, str) and "\n" in v:
        return [x.strip() for x in v.splitlines() if x.strip()]
    if isinstance(v, dict) and all(isinstance(x, (str, int, float, bool)) or x is None for x in v.values()):
        return [f"{k}: {_short(x, 200)}" for k, x in v.items()]
    return None


def _full(v):
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False, indent=1)
    v = "" if v is None else str(v)
    return v[:FULL_MAX] + ("…" if len(v) > FULL_MAX else "")


def diff(before, after, kind=""):
    """Liste von Aenderungen [{"f": Feld, "label", "old", "new"}] zwischen zwei flachen Objekten."""
    before, after = before or {}, after or {}
    out = []
    noise = NOISE.get(kind, set())
    for k in sorted(set(before) | set(after)):
        if k in noise:
            continue
        a, b = before.get(k), after.get(k)
        if a == b or (a in (None, "", [], {}, False) and b in (None, "", [], {}, False)):
            continue
        label = LABELS.get(k, k)
        if SECRET_RE.search(k):
            out.append({"f": k, "label": label, "old": "•••" if a else "–", "new": "•••" if b else "–", "secret": True})
            continue
        if k == "trigger":
            a, b = TRIGGERS.get(a, a), TRIGGERS.get(b, b)
        c = {"f": k, "label": label, "old": _short(a), "new": _short(b)}
        ia, ib = _items(a) if a not in (None, "") else [], _items(b) if b not in (None, "") else []
        if ia is not None and ib is not None and (ia or ib) and (isinstance(a, (list, dict)) or isinstance(b, (list, dict))
                                                             or "\n" in str(a or "") or "\n" in str(b or "")):
            sa, sb = set(ia), set(ib)
            c["added"] = [x for x in ib if x not in sa][:ITEMS_MAX]
            c["removed"] = [x for x in ia if x not in sb][:ITEMS_MAX]
        if c["old"].endswith("…") or c["new"].endswith("…") or isinstance(a, (dict, list)) or isinstance(b, (dict, list)) \
                or "\n" in str(a or "") or "\n" in str(b or ""):
            c["old_full"], c["new_full"] = _full(a), _full(b)
        out.append(c)
    return out


def redact(obj):
    """Fuer 'angelegt'/'geloescht': Objekt ohne Geheimnisse und Betriebsfelder."""
    return {k: v for k, v in (obj or {}).items() if not SECRET_RE.search(k)}


class AuditLog:
    """Audit-Log in der Datenbank (Tabelle audit)."""
    def __init__(self, db):
        self.db = db
        self._writes = 0
        self.keep_days = 365
        self.keep_max = 20000

    def add(self, user, cat, action, target="", changes=None, detail="", ip="", flag="", country="", info=None):
        e = {"id": f"{time.time():.6f}", "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "user": user or "System",
             "ip": ip, "flag": flag, "country": country, "cat": cat, "action": action, "target": str(target)[:200],
             "detail": str(detail)[:500], "changes": changes or []}
        if info:
            e["info"] = {str(k)[:60]: ("•••" if SECRET_RE.search(str(k)) else _short(v, 2000)) for k, v in info.items()
                         if v not in (None, "", [], {})}
        with _lock:
            self.db.audit_add(e)
            self._writes += 1
            if self._writes % 200 == 0:
                self.prune()
        return e

    def all(self):
        """Neueste zuerst."""
        return self.db.audit_all()

    def prune(self, keep_days=None, keep_max=None):
        days = self.keep_days if keep_days is None else keep_days
        mx = self.keep_max if keep_max is None else keep_max
        limit = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(days) * 86400)) if days else None
        with _lock:
            return self.db.audit_prune(limit, int(mx) if mx else None)

    def query(self, cat="", user="", q="", day_from="", day_to=""):
        q = (q or "").strip().lower()
        res = []
        for e in self.all():
            if cat and e.get("cat") != cat:
                continue
            if user and e.get("user", "").lower() != user.lower():
                continue
            d = e.get("ts", "")[:10]
            if day_from and d < day_from or day_to and d > day_to:
                continue
            if q:
                hay = " ".join([e.get("user", ""), e.get("ip", ""), e.get("action", ""), e.get("target", ""),
                                e.get("detail", ""), CATEGORIES.get(e.get("cat"), "")] +
                               [f"{c.get('label')} {c.get('old')} {c.get('new')}" for c in e.get("changes", [])]).lower()
                if q not in hay:
                    continue
            res.append(e)
        return res

    def users(self):
        return sorted({e.get("user", "") for e in self.all()}, key=str.lower)


def to_csv(entries):
    buf = io.StringIO()
    buf.write("﻿")   # damit Excel Umlaute richtig zeigt
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Zeit", "Benutzer", "IP", "Land", "Bereich", "Aktion", "Objekt", "Details", "Änderungen"])
    for e in entries:
        ch = " | ".join(f"{c['label']}: geändert" if c.get("secret") else f"{c['label']}: {c['old']} → {c['new']}"
                        for c in e.get("changes", []))
        w.writerow([e.get("ts"), e.get("user"), e.get("ip"), e.get("country"), CATEGORIES.get(e.get("cat"), e.get("cat")),
                    e.get("action"), e.get("target"), e.get("detail"), ch])
    return buf.getvalue()
