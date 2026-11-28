"""Export und Import des gesamten MirrorSync-Stands als ZIP (optional mit Passwort verschluesselt).

Inhalt: manifest.json (Version, Datum, Anzahl), data.json (Datenbank-Inhalt), files/ (rclone.conf, SSH-Schluessel
und andere eigene Dateien aus config/), optional logs/ (Lauf-Logs)."""
import hashlib
import io
import json
import os
import secrets
import time
import zipfile

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    CRYPTO = True
except Exception:
    CRYPTO = False

import db as dbmod

MAGIC = b"MIRRORSYNC-ENC1\n"
FORMAT = 1
MAX_TOTAL = 1024 * 1024 * 1024   # 1 GB entpackt
# Nicht exportieren: Datenbank selbst (steckt in data.json), Laufzeitdateien, Sicherungen, Laenderdatenbank
SKIP_TOP = {dbmod.DB_NAME, dbmod.DB_NAME + "-wal", dbmod.DB_NAME + "-shm", dbmod.DB_NAME + "-journal",
            "geoip", "json-backup", "backups", "import-pending", "secret_key", "setup_token"}


class BackupError(Exception):
    pass


# ---------------------------------------------------------------- Bereiche zum Anhaken (seit 1.57.0)
# (Schluessel, Beschriftung, Art, Inhalt). Art: ns = Datenbank-Bereich, settings = Einstellungen mit diesen Praefixen,
# file = rclone.conf, files = alle anderen Dateien aus config/, table = Anmeldeverlauf/Audit, logs = Lauf-Logs
RCLONE_CONF = "rclone.conf"
PARTS = [
    ("jobs", "Aufgaben (mit Zeitplänen und Verlauf)", "ns", "job"),
    ("remotes", "Speicherorte (rclone.conf mit Zugangsdaten)", "file", RCLONE_CONF),
    ("remote_meta", "Sichtbarkeit und Besitzer der Speicherorte", "ns", "remote_meta"),
    ("files", "SSH-Schlüssel und weitere Dateien aus config", "files", None),
    ("users", "Benutzer (mit Passwort-Hash, 2FA und Passkeys)", "ns", "user"),
    ("groups", "Gruppen", "ns", "group"),
    ("roles", "Rollen", "ns", "role"),
    ("apikeys", "API-Keys", "ns", "apikey"),
    ("ipguard", "IP- und Länderregeln", "ns", "ipguard"),
    ("dashboard", "Dashboards", "ns", "dashboard"),
    ("shares", "Freigabelinks", "ns", "share"),
    ("s_notify", "Benachrichtigungen (Kanäle, Ruhezeiten, Vorlagen)", "settings",
     ("when", "webhook_", "smtp_", "telegram_", "apprise_", "quiet_", "msg_templates", "notify")),
    ("s_report", "Wochenbericht", "settings", ("report_",)),
    ("s_security", "Anmeldung und Sicherheit", "settings",
     ("lock_", "require_2fa", "fail_notify", "geoip_", "trust_proxy", "session_", "passkey", "password_", "login_")),
    ("s_update", "Updates und Neustart", "settings", ("update_", "selfupdate_", "restart_")),
    ("s_autobackup", "Automatische Sicherung", "settings", ("autobackup_",)),
    ("s_network", "Bandbreite und Datenvolumen", "settings", ("bw", "volume_")),
    ("s_logs", "Aufbewahrung der Logs", "settings", ("log_keep_", "audit_keep")),
    ("s_monitor", "Monitoring", "settings", ("monitor_", "health_", "metrics_")),
    ("s_mqtt", "MQTT (Home Assistant)", "settings", ("mqtt_",)),
    ("s_files", "Dateimanager (Tempo, Bildvorschau, Freigabelinks)", "settings", ("files_", "thumbs", "share_")),
    ("s_general", "Allgemeine Einstellungen (Sprache, Adresse, übrige)", "settings", ()),
    ("stats", "Statistik", "ns", "stats"),
    ("login_log", "Anmeldeverlauf", "table", "login_log"),
    ("audit", "Audit-Log", "table", "audit"),
    ("logs", "Lauf-Logs", "logs", None),
]
PART_KEYS = [p[0] for p in PARTS]
PART_INFO = {p[0]: p for p in PARTS}
DEFAULT_OFF = {"logs"}   # wird nicht vorausgewaehlt (kann gross werden)
EXTRA_NS = ("dashboard", "stats", "share")   # stehen nicht in db.NS, gehoeren aber zum Stand


def settings_part(key):
    """Zu welchem Bereich gehoert eine Einstellung?"""
    for k, _, kind, pre in PARTS:
        if kind == "settings" and pre and any(key == x or key.startswith(x) for x in pre):
            return k
    return "s_general"


def parse_parts(values):
    """Liste aus der GUI/API pruefen. None oder leer = alles."""
    vals = [v for v in (values or []) if v in PART_INFO]
    return vals or None


def _file_part(rel):
    return "remotes" if rel == RCLONE_CONF else "files"


def part_counts(data, files=(), logs=0):
    """Anzahl je Bereich (fuer Vorschau und Anzeige)."""
    out = {k: 0 for k in PART_KEYS}
    for k, _, kind, what in PARTS:
        if kind == "ns":
            out[k] = len(data.get(what) or {})
        elif kind == "table":
            out[k] = len(data.get(what) or [])
    for key in (data.get("settings") or {}):
        out[settings_part(key)] += 1
    for f in files:
        out[_file_part(f)] += 1
    if isinstance(data.get("_remotes"), int):
        out["remotes"] = data["_remotes"]
    out["logs"] = logs
    return out


def count_remotes(conf_bytes):
    import configparser
    cp = configparser.RawConfigParser()
    try:
        cp.read_string(conf_bytes.decode("utf-8", "replace"))
    except Exception:
        return 0
    return len(cp.sections())


# Felder, die sich bei jedem Lauf oder jeder Anmeldung aendern: zaehlen nicht als Aenderung
VOLATILE = {"job": {"history", "last_status", "last_run", "live_last", "live_checked", "live_failing", "live_fail_count",
                    "delete_hold", "retry_pending", "last_verify", "dest_space", "nosync_dirs"},
            "user": {"last_login", "last_ip", "last_country", "fail_count", "totp_last", "auto_lock_until"},
            "apikey": {"last_used", "last_ip", "uses"}}
AUTO_PREFIX = "mirrorsync-auto-"
_extra_skip = set()   # absolute Ordner, die nie mitgesichert werden (eigenes Sicherungsziel unter config/)


def _config_files(config_dir):
    out = []
    for root, dirs, files in os.walk(config_dir):
        rel_root = os.path.relpath(root, config_dir)
        dirs[:] = [d for d in dirs if os.path.realpath(os.path.join(root, d)) not in _extra_skip]
        if rel_root == ".":
            dirs[:] = [d for d in dirs if d not in SKIP_TOP]
            files = [f for f in files if f not in SKIP_TOP]
        for f in files:
            if f.endswith(".tmp"):
                continue
            p = os.path.join(root, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out.append(os.path.normpath(os.path.join(rel_root, f)) if rel_root != "." else f)
    return sorted(out)


def full_dump(db):
    data = db.dump()
    for ns in EXTRA_NS:
        data[ns] = db.get_map(ns)
    return data


def filter_data(data, parts):
    """Nur die angehakten Bereiche behalten."""
    out = {}
    for k in parts:
        kind, what = PART_INFO[k][2], PART_INFO[k][3]
        if kind in ("ns", "table") and what in data:
            out[what] = data[what]
    if any(PART_INFO[k][2] == "settings" for k in parts):
        out["settings"] = {key: v for key, v in (data.get("settings") or {}).items() if settings_part(key) in parts}
    return out


def build(db, config_dir, version, log_dir=None, include_logs=False, note="", parts=None):
    """Sicherung bauen. parts = Liste von Bereichen (PART_KEYS); None = alles (Lauf-Logs nur mit include_logs)."""
    data = full_dump(db)
    files = _config_files(config_dir)
    if parts is not None:
        include_logs = "logs" in parts
        data = filter_data(data, parts)
        files = [f for f in files if _file_part(f) in parts]
    logs = []
    if include_logs and log_dir and os.path.isdir(log_dir):
        for root, _, fs in os.walk(log_dir):
            for f in fs:
                p = os.path.join(root, f)
                if os.path.isfile(p) and not os.path.islink(p):
                    logs.append(os.path.relpath(p, log_dir))
    manifest = {"app": "MirrorSync", "format": FORMAT, "version": version, "schema": dbmod.SCHEMA_VERSION,
                "created": time.strftime("%Y-%m-%d %H:%M:%S"), "note": note,
                "counts": {k: len(v) for k, v in data.items()}, "files": files, "logs": len(logs),
                "parts": [k for k in PART_KEYS if parts is None and (k != "logs" or logs) or parts and k in parts]}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("data.json", json.dumps(data, ensure_ascii=False))
        for f in files:
            z.write(os.path.join(config_dir, f), "files/" + f)
        for f in logs:
            z.write(os.path.join(log_dir, f), "logs/" + f)
    return buf.getvalue(), manifest


def _key(password, salt):
    return Scrypt(salt=salt, length=32, n=2 ** 15, r=8, p=1).derive(password.encode("utf-8"))


def encrypt(raw, password):
    if not CRYPTO:
        raise BackupError("Verschlüsselung nicht verfügbar (Bibliothek cryptography fehlt).")
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    return MAGIC + salt + nonce + AESGCM(_key(password, salt)).encrypt(nonce, raw, MAGIC)


def is_encrypted(blob):
    return blob.startswith(MAGIC)


def decrypt(blob, password):
    if not CRYPTO:
        raise BackupError("Die Datei ist verschlüsselt, aber die Bibliothek cryptography fehlt.")
    if not password:
        raise BackupError("Die Datei ist verschlüsselt. Bitte das Passwort des Exports eingeben.")
    m = len(MAGIC)
    salt, nonce, ct = blob[m:m + 16], blob[m + 16:m + 28], blob[m + 28:]
    try:
        return AESGCM(_key(password, salt)).decrypt(nonce, ct, MAGIC)
    except Exception:
        raise BackupError("Passwort falsch oder Datei beschädigt.") from None


def _safe(name):
    parts = name.replace("\\", "/").split("/")
    return name and not name.startswith("/") and ".." not in parts and ":" not in parts[0]


def read(blob, password=""):
    """Datei pruefen und lesen. Liefert dict(manifest, data, files{pfad: bytes}, logs{pfad: bytes}, encrypted)."""
    enc = is_encrypted(blob)
    raw = decrypt(blob, password) if enc else blob
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise BackupError("Das ist keine MirrorSync-Exportdatei (kein ZIP).") from None
    with z:
        names = z.namelist()
        if "manifest.json" not in names or "data.json" not in names:
            raise BackupError("Das ist keine MirrorSync-Exportdatei (manifest.json oder data.json fehlt).")
        if sum(i.file_size for i in z.infolist()) > MAX_TOTAL:
            raise BackupError("Die Datei ist entpackt größer als 1 GB.")
        try:
            manifest = json.loads(z.read("manifest.json"))
            data = json.loads(z.read("data.json"))
        except ValueError:
            raise BackupError("manifest.json oder data.json ist beschädigt.") from None
        if manifest.get("app") != "MirrorSync" or not isinstance(data, dict):
            raise BackupError("Das ist keine MirrorSync-Exportdatei.")
        files, logs = {}, {}
        for n in names:
            if n.endswith("/"):
                continue
            if not _safe(n):
                raise BackupError(f"Unzulässiger Pfad in der Datei: {n}")
            if n.startswith("files/"):
                files[n[6:]] = z.read(n)
            elif n.startswith("logs/"):
                logs[n[5:]] = z.read(n)
    return {"manifest": manifest, "data": data, "files": files, "logs": logs, "encrypted": enc}


def file_parts(parsed):
    """Welche Bereiche stecken in der Datei? Aeltere Dateien (ohne parts) enthalten alles, was darin vorkommt."""
    m = parsed["manifest"]
    if isinstance(m.get("parts"), list):
        have = [k for k in m["parts"] if k in PART_INFO]
    else:
        d = parsed["data"]
        have = [k for k, _, kind, what in PARTS if kind in ("ns", "table") and what in d]
        if "settings" in d:
            have += [k for k, _, kind, _ in PARTS if kind == "settings"]
        if RCLONE_CONF in parsed["files"]:
            have.append("remotes")
        if any(f != RCLONE_CONF for f in parsed["files"]):
            have.append("files")
        if parsed["logs"]:
            have.append("logs")
    return [k for k in PART_KEYS if k in have]


def check(parsed, my_version, parts=None):
    """(ok, Liste von Hinweisen) zur Kompatibilitaet. parts: nur diese Bereiche sollen uebernommen werden."""
    m = parsed["manifest"]
    notes, ok = [], True
    if int(m.get("format") or 0) > FORMAT or int(m.get("schema") or 0) > dbmod.SCHEMA_VERSION:
        ok = False
        notes.append(f"Die Datei stammt aus einer neueren MirrorSync-Version ({m.get('version')}). "
                     f"Bitte zuerst MirrorSync auf mindestens diese Version aktualisieren.")
    elif _ver(m.get("version")) < _ver(my_version):
        notes.append(f"Die Datei stammt aus Version {m.get('version')}, hier läuft {my_version}. "
                     "Das ist in Ordnung: fehlende neue Einstellungen bekommen ihre Standardwerte.")
    else:
        notes.append(f"Version {m.get('version')} passt zu dieser Installation ({my_version}).")
    for ns in dbmod.NS:
        if ns in parsed["data"] and not isinstance(parsed["data"][ns], dict):
            ok = False
            notes.append(f"Bereich „{ns}“ hat ein ungültiges Format.")
    if parts is not None and "users" not in parts or parts is None and "users" not in file_parts(parsed):
        return ok, notes   # Benutzer bleiben, wie sie sind
    if not (parsed["data"].get("user") or {}):
        ok = False
        notes.append("Die Datei enthält keinen Benutzer. Nach dem Import könnte sich niemand anmelden.")
    elif not any(u.get("role") == "admin" for u in parsed["data"]["user"].values() if isinstance(u, dict)):
        ok = False
        notes.append("Die Datei enthält keinen Admin-Benutzer.")
    return ok, notes


def _ver(v):
    try:
        return tuple(int(x) for x in str(v).split(".")[:3])
    except ValueError:
        return (0, 0, 0)


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".import-tmp"
    with open(tmp, "wb") as f:
        f.write(content)
    os.chmod(tmp, 0o600)
    return tmp


def _merge_conf(cur_path, new_bytes):
    """rclone.conf ergaenzen: Speicherorte aus der Datei hinzufuegen, vorhandene gleichen Namens behalten."""
    import configparser
    cur = configparser.RawConfigParser()
    cur.optionxform = str
    try:
        cur.read(cur_path, encoding="utf-8")
    except Exception:
        pass
    new = configparser.RawConfigParser()
    new.optionxform = str
    new.read_string(new_bytes.decode("utf-8", "replace"))
    added = [sec for sec in new.sections() if not cur.has_section(sec)]
    for sec in added:
        cur.add_section(sec)
        for k, v in new.items(sec):
            cur.set(sec, k, v)
    buf = io.StringIO()
    cur.write(buf)
    return buf.getvalue().encode("utf-8"), added


def apply(db, config_dir, log_dir, parsed, with_files=True, with_logs=False, parts=None, merge=False):
    """Stand uebernehmen. parts = Bereiche (None = alle in der Datei; with_files/with_logs wie bisher).
    merge = False: angehakte Bereiche ersetzen. merge = True: nur Neues hinzufuegen, Vorhandenes (gleiche ID/Name) bleibt.
    Dateien werden erst als .import-tmp geschrieben, dann die Datenbank in einer Transaktion geaendert und erst danach
    die Dateien an ihren Platz gelegt. Liefert die Anzahl uebernommener Dateien."""
    have = file_parts(parsed)
    if parts is None:
        parts = [k for k in have if (k not in ("remotes", "files") or with_files) and (k != "logs" or with_logs)]
    parts = [k for k in parts if k in have]
    staged = []
    data = parsed["data"]
    try:
        for rel, content in parsed["files"].items():
            if _file_part(rel) not in parts:
                continue
            dest = os.path.join(config_dir, rel)
            if merge and rel == RCLONE_CONF and os.path.exists(dest):
                content, _ = _merge_conf(dest, content)
            elif merge and os.path.exists(dest):
                continue
            staged.append((_write(dest, content), dest))
        if "logs" in parts:
            for rel, content in parsed["logs"].items():
                dest = os.path.join(log_dir, rel)
                if merge and os.path.exists(dest):
                    continue
                staged.append((_write(dest, content), dest))
        with db.tx() as c:
            for k in parts:
                kind, what = PART_INFO[k][2], PART_INFO[k][3]
                if kind == "ns":
                    src = data.get(what) or {}
                    if not isinstance(src, dict):
                        raise ValueError(f"Bereich {what} ist kein Objekt.")
                    if not merge:
                        c.execute("DELETE FROM docs WHERE ns=?", (what,))
                    c.executemany("INSERT OR IGNORE INTO docs VALUES (?, ?, ?)" if merge else "INSERT INTO docs VALUES (?, ?, ?)",
                                  [(what, str(key), dbmod._dumps(v)) for key, v in src.items()])
                elif kind == "table" and not merge:
                    rows = data.get(what) or []
                    c.execute(f"DELETE FROM {what}")
                    if what == "login_log":
                        c.executemany("INSERT INTO login_log (id, data) VALUES (?, ?)",
                                      [(e.get("id"), dbmod._dumps(e)) for e in reversed(rows) if isinstance(e, dict)])
                    else:
                        c.executemany("INSERT INTO audit (ts, cat, user, data) VALUES (?, ?, ?, ?)",
                                      [(e.get("ts"), e.get("cat"), e.get("user"), dbmod._dumps(e)) for e in rows if isinstance(e, dict)])
            sparts = [k for k in parts if PART_INFO[k][2] == "settings"]
            if sparts:
                cur = dict(c.execute("SELECT key, value FROM docs WHERE ns='settings'").fetchall())
                for key in cur:
                    if settings_part(key) in sparts and not merge:
                        c.execute("DELETE FROM docs WHERE ns='settings' AND key=?", (key,))
                for key, v in (data.get("settings") or {}).items():
                    if settings_part(key) in sparts and not (merge and key in cur):
                        c.execute("INSERT OR REPLACE INTO docs VALUES ('settings', ?, ?)", (key, dbmod._dumps(v)))
    except Exception:
        for tmp, _ in staged:
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise
    for tmp, final in staged:
        os.replace(tmp, final)
    return len(staged)


def auto_backup(db, config_dir, version, log_dir=None, keep=10, reason="vor-import"):
    """Unverschluesselte Sicherung nach config/backups/ (nur fuer root lesbar). Behaelt die letzten 'keep'."""
    raw, _ = build(db, config_dir, version, log_dir, include_logs=False, note=f"automatische Sicherung {reason}")
    d = os.path.join(config_dir, "backups")
    os.makedirs(d, exist_ok=True)
    os.chmod(d, 0o700)
    path = os.path.join(d, f"mirrorsync-{reason}-{time.strftime('%Y%m%d-%H%M%S')}.zip")
    with open(path, "wb") as f:
        f.write(raw)
    os.chmod(path, 0o600)
    for old in [b for b in list_backups(config_dir) if not b["auto"] and b["dir"] == d][keep:]:
        try:
            os.remove(old["path"])
        except OSError:
            pass
    return path


def list_backups(config_dir, extra_dir=None):
    """Sicherungen aus config/backups und (falls anders) dem Ziel der automatischen Sicherung, neueste zuerst."""
    dirs = [os.path.join(config_dir, "backups")]
    if extra_dir and os.path.realpath(extra_dir) != os.path.realpath(dirs[0]):
        dirs.append(extra_dir)
    out, seen = [], set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if (f.endswith(".zip") or f.endswith(".zip.enc")) and f.startswith("mirrorsync-") and os.path.isfile(p) \
                    and f not in seen:
                seen.add(f)
                st = os.stat(p)
                out.append({"name": f, "size": st.st_size, "path": p, "dir": d, "auto": f.startswith(AUTO_PREFIX),
                            "enc": f.endswith(".enc"), "mtime": st.st_mtime,
                            "time": time.strftime("%d.%m.%Y %H:%M", time.localtime(st.st_mtime))})
    return sorted(out, key=lambda x: -x["mtime"])


# ---------------------------------------------------------------- automatische Sicherung nach Zeitplan
AUTO_DEFAULTS = {"autobackup_enabled": False, "autobackup_schedule": "0 3 * * *", "autobackup_dir": "",
                 "autobackup_keep": "14", "autobackup_days": "0", "autobackup_logs": False, "autobackup_password": "",
                 "autobackup_notify": "fail", "autobackup_notify_skip": False, "autobackup_channels": [],
                 "autobackup_parts": []}   # leer = alle Bereiche


def auto_dir(config_dir, settings):
    d = (settings.get("autobackup_dir") or "").strip()
    return d if d else os.path.join(config_dir, "backups")


def state_hash(db, config_dir):
    """Pruefsumme ueber alles, was eine Sicherung ausmacht, ohne Verlauf, Zeitstempel und Zaehler.
    Gleiche Pruefsumme = nichts geaendert."""
    data = full_dump(db)
    data.pop("login_log", None)
    data.pop("audit", None)
    data.pop("stats", None)   # Monatsstatistik aendert sich mit jedem Lauf
    for ns, keys in VOLATILE.items():
        for v in (data.get(ns) or {}).values():
            if isinstance(v, dict):
                for k in keys:
                    v.pop(k, None)
                if ns == "user":
                    v["passkeys"] = [{k: x for k, x in p.items() if k not in ("count", "last_used")}
                                     for p in v.get("passkeys") or [] if isinstance(p, dict)]
    h = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for f in _config_files(config_dir):
        h.update(b"\0" + f.encode("utf-8") + b"\0")
        try:
            with open(os.path.join(config_dir, f), "rb") as fh:
                h.update(hashlib.sha256(fh.read()).digest())
        except OSError:
            pass
    return h.hexdigest()


def _int(v, default):
    try:
        return max(0, int(str(v).strip()))
    except (TypeError, ValueError):
        return default


def prune_auto(target, keep, days, protect=None):
    """Alte automatische Sicherungen loeschen. Die neueste bleibt immer. Liefert die geloeschten Namen."""
    files = [b for b in list_backups(target, target) if b["auto"] and b["dir"] == target]
    removed, now = [], time.time()
    for i, b in enumerate(files):
        if i == 0 or b["path"] == protect:
            continue
        if (keep and i >= keep) or (days and now - b["mtime"] > days * 86400):
            try:
                os.remove(b["path"])
                removed.append(b["name"])
            except OSError:
                pass
    return removed


def run_auto(db, config_dir, version, settings, log_dir=None, force=False):
    """Eine automatische Sicherung. Liefert dict(result=ok|skip|fail, file, size, removed, error, hash).
    Ohne Aenderung seit der letzten Sicherung (und deren Datei noch da) wird nichts geschrieben."""
    cfg = dict(AUTO_DEFAULTS, **{k: v for k, v in settings.items() if k.startswith("autobackup_")})
    target = auto_dir(config_dir, cfg)
    res = {"result": "fail", "file": "", "size": 0, "removed": [], "error": "", "hash": "", "dir": target,
           "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        if not os.path.isabs(target):
            raise BackupError(f"Das Sicherungsziel muss ein absoluter Pfad sein: {target}")
        _extra_skip.add(os.path.realpath(target))
        h = state_hash(db, config_dir)
        res["hash"] = h
        try:
            last = json.loads(db.meta("autobackup_last") or "{}")
        except ValueError:
            last = {}
        if not force and last.get("hash") == h and last.get("file") and os.path.exists(last["file"]):
            res.update(result="skip", file=last["file"], last_time=last.get("time", ""))
            res["removed"] = prune_auto(target, _int(cfg["autobackup_keep"], 14), _int(cfg["autobackup_days"], 0))
            return res
        parts = [k for k in (cfg.get("autobackup_parts") or []) if k in PART_INFO and k != "logs"]
        if parts and cfg["autobackup_logs"]:
            parts.append("logs")
        raw, man = build(db, config_dir, version, log_dir, include_logs=bool(cfg["autobackup_logs"]),
                         note="automatische Sicherung (Zeitplan)", parts=parts or None)
        name = f"{AUTO_PREFIX}{time.strftime('%Y%m%d-%H%M%S')}.zip"
        pw = cfg.get("autobackup_password") or ""
        if pw:
            raw, name = encrypt(raw, pw), name + ".enc"
        os.makedirs(target, exist_ok=True)
        if os.path.realpath(target) == os.path.realpath(os.path.join(config_dir, "backups")):
            os.chmod(target, 0o700)
        path, n = os.path.join(target, name), 1
        while os.path.exists(path):   # zwei Sicherungen in derselben Sekunde
            n += 1
            path = os.path.join(target, name.replace(".zip", f"-{n}.zip", 1))
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(raw)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        db.set_meta("autobackup_last", json.dumps({"hash": h, "file": path, "time": res["time"]}))
        res.update(result="ok", file=path, size=len(raw), encrypted=bool(pw), logs=man["logs"])
        res["removed"] = prune_auto(target, _int(cfg["autobackup_keep"], 14), _int(cfg["autobackup_days"], 0), protect=path)
    except Exception as e:   # Sicherung darf den Dienst nie stoeren
        res.update(result="fail", error=f"{e}" if isinstance(e, BackupError) else f"{type(e).__name__}: {e}")
    return res
