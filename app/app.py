"""MirrorSync: 1:1-Spiegelung (wie FreeFileSync "Spiegeln") mit Web-GUI und Zeitplänen.

Sync-Motor ist rclone (SMB, WebDAV, SFTP/SSH, FTP, S3, lokale Ordner, ...).
"""
import datetime
import hmac
import ipaddress
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import threading
import time
import uuid

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import flask
from flask import Flask, abort, g, has_request_context, redirect, request, send_file, session, url_for
from jinja2 import BaseLoader, TemplateNotFound

import api
import apigui
import audit
import backup
import bwlimit
import configparser
import db as dbmod
import files as filemgr
import geoip
import i18n
import update
import ipguard
import msgtpl
import notify
import passkeys
import roles
import users
from markupsafe import Markup

from templates import ICONS, TEMPLATES

CONFIG_DIR = os.environ.get("CONFIG_DIR", "/config")
LOG_DIR = os.environ.get("LOG_DIR", "/logs")
RCLONE_CONF = os.path.join(CONFIG_DIR, "rclone.conf")
JOBS_FILE = os.path.join(CONFIG_DIR, "jobs.json")
TZ = os.environ.get("TZ", "Europe/Berlin")
WEB_USER = os.environ.get("WEB_USER", "admin")
WEB_PASS = os.environ.get("WEB_PASS", "")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION"), encoding="utf-8") as _f:
    VERSION = _f.read().strip()

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.exists(RCLONE_CONF):
    open(RCLONE_CONF, "a").close()

app = Flask(__name__)
import re  # noqa: E402

TPL_REF = re.compile(r"""(\{%-?\s*(?:extends|include|import|from)\s+)(["'])([^"']+)\2""")


class I18nLoader(BaseLoader):
    """Templates je Sprache: "en::index.html" ist index.html mit englischen Texten."""
    def get_source(self, environment, name):
        lang, sep, base = name.partition("::")
        if not sep:
            lang, base = i18n.SOURCE, name
        if base not in TEMPLATES or not (i18n.valid(lang)):
            raise TemplateNotFound(name)
        src = TEMPLATES[base]
        if lang != i18n.SOURCE:
            src = i18n.translate_source(src, i18n.catalog_for(lang))
        src = TPL_REF.sub(lambda m: f"{m.group(1)}{m.group(2)}{lang}::{m.group(3)}{m.group(2)}", src)
        return src, None, lambda: True


BRIDGE_CTX = ("err", "msg", "preview", "new", "q", "error")


def render_template(template_name, /, **ctx):
    br = g.get("bridge") if has_request_context() else None
    if br is not None:   # Aufruf ueber die API: Ergebnis der Seite festhalten statt HTML auszuwerten
        br["out"].setdefault("pages", []).append(template_name)
        for k in BRIDGE_CTX:
            if ctx.get(k) is not None and k not in br["out"]:
                br["out"][k] = ctx[k]
    return flask.render_template(f"{i18n.current()}::{template_name}", **ctx)


def _flash_err(text):
    """Fehlermeldung fuer die naechste Seite (GUI) bzw. als Fehler fuer die API."""
    session["flash"] = text
    br = g.get("bridge")
    if br is not None:
        br["out"]["err"] = text


def _req_lang():
    """Sprache der aktuellen Anfrage: Benutzerkonto > Auswahl auf der Anmeldeseite > Systemsprache."""
    if not has_request_context():
        return None
    for v in (g.get("user_lang"), session.get("lang") if not g.get("user") else None):
        if v and i18n.valid(v):
            return v
    return None


i18n.resolver = _req_lang
app.jinja_loader = I18nLoader()
app.jinja_env.finalize = lambda v: i18n.translate(v) if type(v) is str else v
app.jinja_env.globals.update(_=i18n.t, lang_code=i18n.current, LANGS=i18n.languages,
                             bw_unit=lambda: load_settings().get("bw_unit") or "MB/s")
app.jinja_env.filters["regex_cmd"] = lambda h: (re.search(r'rclone authorize "[^\n]*', h or "") or [None])[0]
app.jinja_env.globals["VERSION"] = VERSION
app.jinja_env.globals["UPDATE"] = lambda: update_status() if g.get("user") else None
notify.VERSION = VERSION
app.jinja_env.globals["ICON"] = {k: Markup(v) for k, v in ICONS.items()}
app.jinja_env.globals["STATUS"] = {"ok": "OK", "fehler": "Fehler", "laeuft": "läuft",
                                    "gestoppt": "gestoppt", "abgebrochen": "abgebrochen"}

_lock = threading.RLock()
_running = {}  # job_id -> subprocess.Popen
_current_run = {}  # job_id -> run_id des laufenden Laufs
scheduler = BackgroundScheduler(timezone=TZ)


# ---------------------------------------------------------------- Speicher
DB = dbmod.DB(os.path.join(CONFIG_DIR, dbmod.DB_NAME))
update.init(DB, VERSION)
try:
    dbmod.migrate(DB, CONFIG_DIR, log=lambda m: print(m, flush=True))
except Exception as _e:   # nichts uebernommen, JSON-Dateien unveraendert -> lieber nicht starten als leer starten
    print(f"FEHLER: Übernahme der alten Daten nach SQLite fehlgeschlagen: {_e}\n"
          "Es wurde nichts verändert. Bitte die genannte Datei in config/ prüfen oder reparieren und neu starten.",
          flush=True)
    raise SystemExit(1)


def load_jobs():
    with _lock:
        return DB.get_map("job")


def save_jobs(jobs):
    with _lock:
        DB.put_map("job", jobs)


def update_job(job_id, **fields):
    with _lock:
        jobs = load_jobs()
        if job_id in jobs:
            jobs[job_id].update(fields)
            save_jobs(jobs)


# ---------------------------------------------------------------- rclone
def rclone(*args, timeout=60):
    cmd = ["rclone", "--config", RCLONE_CONF, *args]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        # Bei Erfolg nur stdout (Hinweise auf stderr wuerden sonst Listen verfaelschen)
        return p.returncode, (p.stdout if p.returncode == 0 else p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, f"Zeitüberschreitung nach {timeout}s"


def exclude_list(job):
    """Ausschluesse (eine Zeile pro Eintrag) in rclone-Filtermuster umwandeln.

    - "/Ordner/" oder "Ordner/"   -> ganzer Ordner (inkl. Inhalt)
    - voller Quellpfad            -> wird relativ zur Quelle gemacht
    - sonst unveraendert (rclone-Muster wie *.tmp, **/.cache/**)
    """
    src = job.get("source", "").rstrip("/")
    out = []
    for line in (job.get("excludes") or "").splitlines():
        p = line.strip()
        if not p or p.startswith("#"):
            continue
        if src and p.startswith(src + "/"):
            p = p[len(src):]
        if p.endswith("/"):
            p += "**"
        out.append(p)
    return out


GLOB_SPECIAL = re.compile(r"([\\*?\[\]{}])")


def selection_list(job):
    """Auswahl einzelner Dateien/Ordner relativ zur Quelle. Ordner enden mit '/'. Leer = ganze Quelle."""
    out = []
    for line in (job.get("selection") or "").splitlines():
        p = line.strip()
        while p.startswith("./"):
            p = p[2:]
        p = re.sub(r"/{2,}", "/", p).lstrip("/")
        if not p or p.startswith("#") or p == "/" or any(x in ("..", ".") for x in p.rstrip("/").split("/")):
            continue
        if p not in out:
            out.append(p)
    return out


def selection_filters(job):
    """rclone --filter-Regeln: erst Ausschluesse, dann die Auswahl, alles andere ausgeschlossen.
    Damit prueft, kopiert und loescht rclone nur innerhalb der Auswahl."""
    rules = [f"- {p}" for p in exclude_list(job)]
    for p in selection_list(job):
        e = "/" + GLOB_SPECIAL.sub(r"\\\1", p.rstrip("/"))
        rules.append(f"+ {e}/**" if p.endswith("/") else f"+ {e}")
    rules.append("- **")
    return rules


def split_file_source(source):
    """Zeigt die Quelle auf eine Datei, liefert (Elternordner, Dateiname), sonst None."""
    src = source.strip().rstrip("/")
    if not src or src.endswith(":"):
        return None
    rc, out = rclone("lsjson", "--stat", "--no-mimetype", src, timeout=20)
    if rc != 0:
        return None
    try:
        info = json.loads(out or "{}")
    except ValueError:
        return None
    if info.get("IsDir", True):
        return None
    i = src.rfind("/")
    c = src.find(":") if not src.startswith("/") else -1
    if i > c:
        parent = src[:i] or "/"
        if parent.endswith(":"):
            parent += "/"
        return parent, src[i + 1:]
    return src[:c + 1], src[c + 1:]


def source_basename(source):
    """Letzter Ordnername der Quelle, z. B. 'OPNsense' bei 'NAS:backup/OPNsense'. Leer bei Wurzeln."""
    path = source.strip().rstrip("/")
    if ":" in path and not path.startswith("/"):
        path = path.split(":", 1)[1]
    return path.rsplit("/", 1)[-1] if path.strip("/") else ""


def has_selection(job):
    return any(x.strip() and not x.strip().startswith("#") for x in (job.get("selection") or "").splitlines())


def effective_dest(job):
    """Tatsaechliches Ziel. Mit 'Quellordner selbst mitkopieren' wird der Ordnername der Quelle angehaengt
    (wie rsync ohne Schraegstrich am Ende): Ziel/OPNsense/..."""
    dest = job["dest"].strip()
    if not job.get("include_source_dir") or has_selection(job):   # mit Auswahl landen die gewaehlten Eintraege direkt im Ziel
        return dest
    name = source_basename(job["source"])
    if not name:
        return dest
    return dest + name if dest.endswith((":", "/")) else dest + "/" + name


BISYNC_DIR = os.path.join(CONFIG_DIR, "bisync")
BISYNC_CONFLICTS = ("newer", "path1", "path2", "none")
BISYNC_RESET_KEYS = ("source", "dest", "excludes", "direction", "checksum", "selection", "include_source_dir")


def is_bisync(job):
    return (job or {}).get("direction") == "bisync"


def bisync_workdir(job_id):
    return os.path.join(BISYNC_DIR, re.sub(r"[^A-Za-z0-9_-]", "_", job_id or "x"))


def bisync_max_delete(job):
    try:
        return max(1, min(100, int(job.get("bisync_max_delete") or 50)))
    except (TypeError, ValueError):
        return 50


def bisync_missing_sides(job):
    """Seiten eines Zwei-Wege-Syncs, deren Ordner es (noch) nicht gibt. Der Wurzelordner eines Speicherorts gilt als vorhanden."""
    missing = []
    for side in (job["source"], effective_dest(job)):
        side = side.strip()
        if not side or side.endswith(":"):
            continue
        rc, out = rclone("lsjson", side, "--stat", timeout=30)
        if rc != 0 and any(w in out.lower() for w in ("not found", "doesn't exist", "no such")):
            missing.append(side)
    return missing


def build_bisync_cmd(job, job_id, dry_run, resync=False):
    """Zwei-Wege-Sync: rclone bisync zwischen Seite A (source) und Seite B (dest)."""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    conflict = job.get("bisync_conflict") if job.get("bisync_conflict") in BISYNC_CONFLICTS else "newer"
    side_b = effective_dest(job)   # mit "Quellordner selbst mitkopieren": Seite B/<Ordnername>
    cmd = [
        "rclone", "bisync", job["source"], side_b,
        "--config", RCLONE_CONF, "--workdir", bisync_workdir(job_id),
        "--create-empty-src-dirs", "--resilient", "--recover", "--color", "NEVER",
        "--conflict-resolve", conflict, "--conflict-loser", "num", "--conflict-suffix", "konflikt",
        "--max-delete", str(bisync_max_delete(job)),
        "--log-level", "INFO",
        "--stats", "15s", "--stats-one-line", "--stats-log-level", "NOTICE",
    ]
    if resync:
        cmd += ["--resync", "--resync-mode", "newer"]
    if dry_run or job.get("dry_run"):
        cmd.append("--dry-run")
    if job.get("versioning"):
        cmd += ["--backup-dir1", job["source"].rstrip("/") + ".versions/" + stamp,
                "--backup-dir2", side_b.rstrip("/") + ".versions/" + stamp]
    if job.get("checksum"):
        cmd += ["--compare", "size,modtime,checksum"]
    if selection_list(job):   # nur die Auswahl wird abgeglichen, auf beiden Seiten bleibt alles andere unberuehrt
        for rule in selection_filters(job):
            cmd += ["--filter", rule]
    else:
        for pattern in exclude_list(job):
            cmd += ["--exclude", pattern]
    return _cmd_tail(job, cmd)


def _cmd_tail(job, cmd):
    extra = shlex.split(job.get("extra_flags", "") or "")
    if not any(a == "--bwlimit" or a.startswith("--bwlimit=") for a in extra):   # eigene Option hat Vorrang
        tt = bwlimit.timetable(bwlimit.for_job(load_settings(), job))
        if tt:
            cmd += ["--bwlimit", tt]
    return cmd + extra


def build_sync_cmd(job, dry_run, mode="full", max_age=None):
    """mode=full: rclone sync (Spiegel). mode=delta: rclone copy nur kuerzlich geaenderter Dateien, ohne Loeschen."""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    delta = mode == "delta"
    cmd = [
        "rclone", "copy" if delta else "sync", job["source"], effective_dest(job),
        "--config", RCLONE_CONF,
        "--create-empty-src-dirs",
        "--log-level", "INFO",
        "--stats", "15s", "--stats-one-line", "--stats-log-level", "NOTICE",
    ]
    if dry_run or job.get("dry_run"):
        cmd.append("--dry-run")
    if delta:
        cmd += ["--max-age", f"{int(max_age or 3600)}s"]
    if str(job.get("max_delete", "")).strip() and not delta:
        cmd += ["--max-delete", str(job["max_delete"]).strip()]
    if job.get("versioning"):
        cmd += ["--backup-dir", effective_dest(job).rstrip("/") + ".versions/" + stamp]
    if job.get("checksum"):
        cmd.append("--checksum")
    if selection_list(job):   # nur ausgewaehlte Dateien/Ordner; im Ziel bleibt alles andere unberuehrt
        for rule in selection_filters(job):
            cmd += ["--filter", rule]
    else:
        for pattern in exclude_list(job):
            cmd += ["--exclude", pattern]
    if job.get("delete_excluded") and not delta and not selection_list(job):
        cmd.append("--delete-excluded")
    return _cmd_tail(job, cmd)


SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


LOG_DEFAULTS = {"log_keep_runs": "50", "log_keep_days": "30", "trust_proxy": False, "geoip_auto": True, "geoip_days": "30",
                "geoip_mode": "interval", "geoip_time": "03:00", "geoip_dow": "mon",
                "lock_attempts": "5", "lock_minutes": "15", "lock_notify": True,
                "fail_notify": "", "fail_notify_minutes": "15", "audit_keep_days": "365", "update_check": True, "update_interval": "60"}
RUN_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


def load_settings():
    data = dict(notify.DEFAULTS, **LOG_DEFAULTS)
    data.update(json.loads(json.dumps(backup.AUTO_DEFAULTS)))
    data.update(DB.get_map("settings"))
    return data


def save_settings(data):
    DB.put_map("settings", data)


def update_status():
    """Ergebnis der Pruefung auf eine neuere Version (siehe update.py)."""
    s = load_settings()
    return update.status(s.get("update_check", True), s.get("update_interval", "60"))


def _update_loop():
    """Beim Start (nach kurzer Pause) und danach regelmaessig bei GitHub nach einer neueren Version fragen."""
    time.sleep(30)
    while True:
        try:
            s = load_settings()
            if s.get("update_check", True) and update.due(s.get("update_interval", "60")):
                st = update.check()
                if st.get("error"):
                    print(f"Update-Prüfung: {st['error']}", flush=True)
                elif update.newer(st.get("latest"), VERSION):
                    print(f"Neue MirrorSync-Version {st['latest']} verfügbar: {st.get('url')}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"Update-Prüfung: {e}", flush=True)
        time.sleep(60)   # der eingestellte Abstand kann bis 5 Minuten herunter gehen


def keep_limits():
    st = load_settings()
    try:
        runs = max(1, min(1000, int(st.get("log_keep_runs") or 50)))
    except ValueError:
        runs = 50
    try:
        days = max(0, min(3650, int(st.get("log_keep_days") or 0)))
    except ValueError:
        days = 30
    return runs, days


def run_log_path(job_id, run_id):
    return os.path.join(LOG_DIR, job_id, f"{run_id}.log")


def cleanup_logs(job_id):
    """Alte Lauf-Logs nach Anzahl und Alter loeschen. Der neueste Lauf bleibt immer erhalten."""
    runs, days = keep_limits()
    with _lock:
        jobs = load_jobs()
        job = jobs.get(job_id)
        if not job:
            return
        hist = job.get("history", [])
        cutoff = time.time() - days * 86400 if days else None
        keep = []
        for i, h in enumerate(hist):
            too_old = False
            if cutoff and i > 0:
                try:
                    too_old = time.mktime(time.strptime(h["start"], "%Y-%m-%d %H:%M:%S")) < cutoff
                except (KeyError, ValueError):
                    pass
            if i < runs and not too_old:
                keep.append(h)
        kept_runs = {h.get("run") for h in keep}
        job["history"] = keep
        save_jobs(jobs)
    d = os.path.join(LOG_DIR, job_id)
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.endswith(".log") and fn[:-4] not in kept_runs and fn[:-4] != _current_run.get(job_id):
                try:
                    os.remove(os.path.join(d, fn))
                except OSError:
                    pass


def migrate_logs():
    """Logs aus Version <= 1.4 (eine Datei pro Aufgabe) als Lauf uebernehmen."""
    jobs = load_jobs()
    changed = False
    for job_id, job in jobs.items():
        old = os.path.join(LOG_DIR, f"{job_id}.log")
        if not os.path.isfile(old):
            continue
        run_id = "alt-" + time.strftime("%Y%m%d-%H%M%S", time.localtime(os.path.getmtime(old)))
        os.makedirs(os.path.join(LOG_DIR, job_id), exist_ok=True)
        os.replace(old, run_log_path(job_id, run_id))
        hist = job.get("history", [])
        if hist and not hist[0].get("run"):
            c, d, e = notify.summarize_log(run_log_path(job_id, run_id))
            hist[0].update(run=run_id, copied=c, deleted=d, errors=len(e))
            changed = True
    if changed:
        save_jobs(jobs)


def send_notifications(job_id, job, status, duration, dry, log_path, by="", mode="full"):
    settings = load_settings()
    when, eff = notify.effective(settings, job)
    if not notify.should_send(when, status == "ok"):
        return
    ev = notify.build_event(dict(job, dest=effective_dest(job)), status, duration, dry, log_path, settings, by, mode)
    results = notify.send(eff, ev)
    if results:
        with open(log_path, "a", encoding="utf-8") as f:
            for ch, err in results.items():
                f.write(f"Benachrichtigung {ch}: {'gesendet' if err is None else 'FEHLER ' + err}\n")


VERSION_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{6}$")


def prune_versions(job):
    """Alte Versionen unter <ziel>.versions/ aufraeumen: hoechstens versions_keep Staende, keine aelter als versions_days.
    Liefert Log-Zeilen."""
    keep = int(job.get("versions_keep") or 0)
    days = int(job.get("versions_days") or 0)
    if not job.get("versioning") or (not keep and not days):
        return []
    base = effective_dest(job).rstrip("/") + ".versions"
    rc, out = rclone("lsjson", base, "--dirs-only", timeout=120)
    if rc != 0:
        return [] if "not found" in out.lower() or "doesn't exist" in out.lower() else [i18n.t("Versionen aufräumen: {0} nicht lesbar: {1}", base, out[-300:])]
    try:
        names = sorted(d["Name"] for d in json.loads(out or "[]") if VERSION_DIR_RE.match(d.get("Name", "")))
    except ValueError:
        return []
    drop = set()
    if keep and len(names) > keep:
        drop.update(names[:len(names) - keep])
    if days:
        limit = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d_%H%M%S")
        drop.update(n for n in names if n < limit)
    lines = []
    for n in sorted(drop):
        rc, out = rclone("purge", f"{base}/{n}", timeout=600)
        lines.append(i18n.t("Alte Version entfernt: {0}", n) if rc == 0 else i18n.t("Version {0} konnte nicht entfernt werden: {1}", n, out[-300:]))
    if lines:
        lines.append(i18n.t("Versionen: {0} behalten, {1} entfernt.", len(names) - len(drop), len(drop)))
    return lines


def _watch(job_id, job, proc, logf, started, dry, by, run_id, log_path, mode="full"):
    rc = proc.wait()
    if rc == 0 and not dry and not job.get("dry_run"):
        try:
            for line in prune_versions(job):
                logf.write(line + "\n")
        except Exception as e:   # Aufraeumen darf den Lauf nicht scheitern lassen
            logf.write(f"Versionen aufräumen: {e}\n")
    if is_bisync(job) and job.get("bisync_ready") and rc not in (0, -15, 143):
        try:
            with open(log_path, encoding="utf-8", errors="replace") as lf:
                gone = re.search(r"directory not found|Empty current Path[12] listing", lf.read())
        except OSError:
            gone = None
        if gone:
            logf.write("\n=== Eine Seite fehlt oder ist leer, z. B. weil ein Laufwerk nicht eingehängt ist. Zum Schutz wurde "
                       "abgebrochen, angelegt oder gelöscht wurde nichts. Prüfe beide Seiten und klicke dann auf "
                       "„Neu zusammenführen“. ===\n")
    duration = int(time.time() - started)
    logf.write(f"\n=== Ende: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}, Code {rc}, Dauer {duration}s ===\n")
    logf.close()
    copied, deleted, errors = notify.summarize_log(log_path)
    bisync = is_bisync(job)
    need_resync = False
    if bisync:
        if rc == 0:
            errors = []   # bisync meldet bei Konflikt-Pruefungen "ERROR : ... differ", obwohl alles klappt
        else:
            try:
                with open(log_path, encoding="utf-8", errors="replace") as lf:
                    need_resync = "Must run --resync" in lf.read()
            except OSError:
                pass
    delta = mode in ("delta", "livesync")   # beides sind Live-Runden
    quiet = repeat = False
    notify_now = True
    with _lock:
        _running.pop(job_id, None)
        _current_run.pop(job_id, None)
        status = "ok" if rc == 0 else ("gestoppt" if rc in (-15, 143) else "fehler")
        jobs = load_jobs()
        if job_id in jobs:
            j = jobs[job_id]
            if status == "ok" and not dry and trigger_of(j) == "live":
                j["live_last"] = started            # naechster Live-Lauf holt alles ab diesem Zeitpunkt
            if bisync and not dry and status == "ok":
                j["bisync_ready"] = True
                j.pop("bisync_need_resync", None)
            elif bisync and need_resync and not dry:   # ein Testlauf ohne angelegten Ordner muss nicht neu abgleichen
                j["bisync_need_resync"] = True
            if delta:
                j["live_checked"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                repeat = status == "fehler" and j.get("live_failing")
                notify_now = status == "fehler" and not repeat      # nur der erste Fehler einer Serie
                j["live_failing"] = status == "fehler"
                j["live_fail_count"] = (j.get("live_fail_count", 0) + 1) if status == "fehler" else 0
                # nichts geaendert oder derselbe Fehler noch einmal: kein Verlauf, kein Log
                quiet = (status == "ok" and copied == 0 and deleted == 0 and not errors) or bool(repeat)
            if not quiet:
                entry = {
                    "start": datetime.datetime.fromtimestamp(started).strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": duration, "status": status, "code": rc, "dry_run": dry, "by": by,
                    "run": run_id, "copied": copied, "deleted": deleted, "errors": len(errors),
                }
                if delta:
                    entry["mode"] = "live"
                j.update(last_status=status, last_run=entry["start"], history=[entry] + j.get("history", []))
            elif j.get("last_status") == "laeuft":
                j["last_status"] = "fehler" if repeat else (j.get("history") or [{}])[0].get("status", "ok")
            save_jobs(jobs)
    if quiet:
        try:
            os.remove(log_path)
        except OSError:
            pass
        return
    if not delta or notify_now and status == "fehler":
        send_notifications(job_id, job, status, duration, dry, log_path, by, mode)
    if not delta or mode == "livesync":    # Live wie Spiegeln: Folgeaufgaben nach jeder Runde mit Aenderungen
        start_followers(job_id, status, dry, log_path)
    cleanup_logs(job_id)


def start_job(job_id, dry_run=False, by="Zeitplan", mode="full", manual=False, resync=False):
    """Startet einen Job im Hintergrund. False, wenn er schon laeuft (Laeufe ueberlappen nie).
    mode=delta: Live-Lauf, kopiert nur seit dem letzten erfolgreichen Lauf geaenderte Dateien."""
    with _lock:
        if job_id in _running:
            return False
        job = load_jobs().get(job_id)
        if not job:
            return False
        if is_paused(job) and not manual:
            return False   # pausiert: kein Start per Zeitplan, Live oder Kette
        max_age = None
        if mode == "delta" and job.get("dry_run"):
            return False   # "nur Testlauf": Live-Runden auslassen, nur der volle Abgleich laeuft als Test
        bisync = is_bisync(job)
        if mode == "delta" and (bisync or live_mode(job) == "mirror"):
            mode = "livesync"   # jede Runde wie Spiegeln (bzw. Zwei-Wege-Abgleich), inklusive Loeschen
        if bisync and job.get("bisync_need_resync") and not resync:
            if mode == "livesync":
                return False   # erst nach "Neu abgleichen" weiter, sonst kommt jede Minute derselbe Fehler
        first = bisync and (resync or not job.get("bisync_ready"))
        if mode == "delta":
            last = job.get("live_last")
            if not last:
                mode, by = "full", by + " (erster voller Abgleich)"
            else:
                max_age = min(int(time.time() - float(last)) + 120, 30 * 86400)   # 2 Minuten Puffer
        if bisync:
            cmd = build_bisync_cmd(job, job_id, dry_run, resync=first)
            os.makedirs(bisync_workdir(job_id), exist_ok=True)
            for fn in os.listdir(bisync_workdir(job_id)):   # Laeufe ueberlappen nie: alte Sperren sind verwaist
                if fn.endswith(".lck"):
                    try:
                        os.remove(os.path.join(bisync_workdir(job_id), fn))
                    except OSError:
                        pass
            if first:
                by += " (erster Zwei-Wege-Abgleich)"
            # bisync braucht beide Seiten. Fehlende Ordner nur beim allerersten Abgleich anlegen; fehlt spaeter eine Seite,
            # die schon einmal da war (z. B. Laufwerk nicht eingehaengt), bricht rclone ab, statt alles neu zu verteilen.
            bisync_missing = bisync_missing_sides(job) if first and not job.get("bisync_ready") else []
            if bisync_missing and not (dry_run or job.get("dry_run")):
                for side in bisync_missing:
                    rclone("mkdir", side, timeout=30)
        else:
            cmd = build_sync_cmd(job, dry_run, mode, max_age)
        os.makedirs(os.path.join(LOG_DIR, job_id), exist_ok=True)
        run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        n = 2
        while os.path.exists(run_log_path(job_id, run_id)):
            run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{n}"
            n += 1
        log_path = run_log_path(job_id, run_id)
        logf = open(log_path, "w", encoding="utf-8", buffering=1)
        dry = dry_run or bool(job.get("dry_run"))
        logf.write(f"=== Start: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}, gestartet von {by}"
                   f"{'  (TESTLAUF, nichts wird verändert)' if dry else ''} ===\n")
        for side in (bisync_missing if bisync else []):
            logf.write(f"=== Ordner fehlte und wird angelegt: {side} ===\n" if not dry
                       else f"=== Ordner fehlt und würde angelegt: {side} ===\n")
        if bisync and bisync_missing and dry:
            logf.write("=== Testlauf: Ohne den Ordner kann rclone den Abgleich nicht durchspielen. Beim echten Lauf wird er "
                       "angelegt. ===\n")
        if bisync and first:
            logf.write("=== Zwei-Wege-Sync, erster Abgleich (--resync): Beide Seiten werden zusammengeführt, gelöscht wird "
                       "dabei nichts. Gibt es eine Datei auf beiden Seiten unterschiedlich, gewinnt die neuere. ===\n")
        elif bisync:
            logf.write("=== Zwei-Wege-Sync: Änderungen und Löschungen auf beiden Seiten werden übernommen ===\n")
        elif mode == "livesync":
            logf.write("=== Live-Lauf: Abgleich wie beim Spiegeln, inklusive Löschen ===\n")
        if mode == "delta":
            logf.write(f"=== Live-Lauf: nur Dateien, die sich in den letzten {max_age // 60} Minuten geändert haben, "
                       f"ohne Löschen ===\n")
        logf.write("$ " + " ".join(shlex.quote(c) for c in cmd) + "\n\n")
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT)
        _running[job_id] = proc
        _current_run[job_id] = run_id
        update_job(job_id, last_status="laeuft")
    threading.Thread(target=_watch, args=(job_id, job, proc, logf, time.time(), dry, by, run_id, log_path, mode),
                     daemon=True).start()
    return True


def stop_job(job_id):
    with _lock:
        proc = _running.get(job_id)
        if proc:
            proc.terminate()


# ---------------------------------------------------------------- Pausieren
def is_paused(job):
    """Pausiert und (falls befristet) die Zeit noch nicht abgelaufen."""
    if not job.get("paused"):
        return False
    until = (job.get("paused_until") or "").strip()
    return not until or until > datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")


def pause_text(job):
    until = (job.get("paused_until") or "").strip()
    return "pausiert bis " + _dt(until) if until else "pausiert"


def resume_expired():
    """Abgelaufene Pausen aufheben (vom Planer jede Minute und beim Start aufgerufen)."""
    changed = []
    with _lock:
        jobs = load_jobs()
        for jid, j in jobs.items():
            if j.get("paused") and not is_paused(j):
                j.update(paused=False, paused_until="", paused_by="")
                changed.append(j["name"])
        if changed:
            save_jobs(jobs)
    for name in changed:
        audit_log.add("System", "job", "fortgesetzt (Pause abgelaufen)", name)
    if changed:
        schedule_all()


# ---------------------------------------------------------------- Zeitplaene
def trigger_of(job):
    """time = Zeitplan, after = nach einer anderen Aufgabe, manual = nur von Hand (alte Aufgaben ohne Feld)."""
    t = job.get("trigger")
    if t in ("time", "after", "manual", "live"):
        return t
    return "time" if job.get("schedule", "").strip() else "manual"


def chain_problem(jobs, job_id, parent_id):
    """Fehlertext, wenn die Kette einen Kreis bilden wuerde, sonst None."""
    if not parent_id or parent_id not in jobs:
        return "Bitte die Aufgabe wählen, nach der gestartet werden soll."
    if parent_id == job_id:
        return "Eine Aufgabe kann nicht nach sich selbst starten."
    seen, cur = [], parent_id
    while cur and cur in jobs and cur not in seen:
        seen.append(cur)
        pj = jobs[cur]
        if trigger_of(pj) != "after":
            return None
        cur = pj.get("after_job")
        if job_id and cur == job_id:
            names = " → ".join(jobs[x]["name"] for x in reversed([job_id] + seen) if x in jobs)
            return f"Das ergäbe eine Endlosschleife ({names} → …). Bitte eine andere Aufgabe wählen."
    return None


def start_followers(job_id, status, dry, log_path, _seen=None, _notes=None):
    """Aufgaben starten, die nach dieser Aufgabe laufen sollen.
    Pausierte Folgeaufgabe: "skip" = ueberspringen, ihre Folgeaufgaben laufen weiter; "stop" = Kette endet dort."""
    if dry or status == "gestoppt":
        return
    seen = _seen or {job_id}
    jobs = load_jobs()
    parent = jobs.get(job_id, {}).get("name", job_id)
    notes = [] if _notes is None else _notes
    for cid, cj in sorted(jobs.items(), key=lambda kv: kv[1]["name"].lower()):
        if trigger_of(cj) != "after" or cj.get("after_job") != job_id or not cj.get("enabled"):
            continue
        if status != "ok" and cj.get("after_when", "ok") != "always":
            notes.append(f"Folgeaufgabe „{cj['name']}“ nicht gestartet (nur bei Erfolg).")
            continue
        if is_paused(cj):
            if cj.get("pause_chain", "skip") == "stop":
                notes.append(f"Folgeaufgabe „{cj['name']}“ ist {pause_text(cj)}, die Kette endet hier.")
            elif cid not in seen:
                notes.append(f"Folgeaufgabe „{cj['name']}“ ist {pause_text(cj)} und wird übersprungen, ihre Folgeaufgaben laufen weiter.")
                seen.add(cid)
                start_followers(cid, status, dry, log_path, seen, notes)
            continue
        ok = start_job(cid, by=f"nach „{parent}“")
        notes.append(f"Folgeaufgabe „{cj['name']}“ " + ("gestartet." if ok else "läuft schon, nicht erneut gestartet."))
    if notes and _notes is None:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n".join(notes) + "\n")
        except OSError:
            pass


def schedule_all():
    for j in scheduler.get_jobs():
        j.remove()
    scheduler.add_job(resume_expired, IntervalTrigger(minutes=1, timezone=TZ), id="_resume", coalesce=True, max_instances=1)
    st = load_settings()
    if geoip_scheduled(st):
        h, m = (st.get("geoip_time") or "03:00").split(":")
        scheduler.add_job(_geoip_run, CronTrigger(day_of_week=st.get("geoip_dow") or "mon", hour=int(h), minute=int(m), timezone=TZ),
                          id="_geoip", misfire_grace_time=3600, coalesce=True, max_instances=1)
    if st.get("autobackup_enabled"):
        try:
            scheduler.add_job(run_autobackup, CronTrigger.from_crontab(st.get("autobackup_schedule") or "0 3 * * *", timezone=TZ),
                              id="_autobackup", misfire_grace_time=3600, coalesce=True, max_instances=1)
        except ValueError:
            pass
    for job_id, job in load_jobs().items():
        if is_paused(job):
            continue
        if job.get("enabled") and trigger_of(job) == "live":
            iv = live_interval(job)
            scheduler.add_job(start_job, IntervalTrigger(minutes=iv, timezone=TZ), args=[job_id],
                              kwargs={"by": "Live", "mode": "delta"}, id=job_id + ":live",
                              misfire_grace_time=60, coalesce=True, max_instances=1)
            full = (job.get("live_full") or "").strip() if live_mode(job) == "fast" else ""
            if full:
                try:
                    every = live_full_every(full)
                    trig = (IntervalTrigger(minutes=every, timezone=TZ) if every
                            else CronTrigger.from_crontab(full, timezone=TZ))
                    scheduler.add_job(start_job, trig, args=[job_id],
                                      kwargs={"by": "Live (voller Abgleich)"}, id=job_id,
                                      misfire_grace_time=3600, coalesce=True, max_instances=1)
                except ValueError:
                    pass
            continue
        if job.get("enabled") and trigger_of(job) == "time" and job.get("schedule", "").strip():
            try:
                trigger = CronTrigger.from_crontab(job["schedule"], timezone=TZ)
            except ValueError:
                continue
            scheduler.add_job(start_job, trigger, args=[job_id], id=job_id,
                              misfire_grace_time=3600, coalesce=True, max_instances=1)


def next_run(job_id):
    j = scheduler.get_job(job_id)
    return j.next_run_time.strftime("%d.%m.%Y %H:%M") if j and j.next_run_time else None


def _next_time(sched_id):
    j = scheduler.get_job(sched_id)
    return j.next_run_time if j and j.next_run_time else None


def next_start(jobs, job_id, _seen=None):
    """Naechster voraussichtlicher Start einer Aufgabe: (datetime oder None, Art).
    Art: time, live, after (geschaetzt ueber den Vorgaenger, rekursiv), parent_running, manual, off, paused, ''."""
    j = jobs.get(job_id)
    if not j:
        return None, ""
    trig = trigger_of(j)
    if trig == "manual":
        return None, "manual"
    if is_paused(j):
        return None, "paused"
    if not j.get("enabled"):
        return None, "off"
    if trig == "time":
        t = _next_time(job_id)
        return (t, "time") if t else (None, "off")
    if trig == "live":
        c = [t for t in (_next_time(job_id + ":live"), _next_time(job_id)) if t]
        return (min(c), "live") if c else (None, "off")
    seen = set(_seen or ()) | {job_id}
    parent = j.get("after_job")
    if parent not in jobs or parent in seen:
        return None, ""
    if parent in _running:
        return None, "parent_running"
    t, kind = next_start(jobs, parent, seen)
    if t:
        return t, "after"
    return None, "parent_running" if kind == "parent_running" else ""


def next_start_view(jobs, job_id):
    """Fuer Uebersicht und API: Zeitpunkt, Art, Tagesabstand (0 = heute, 1 = morgen), Uhrzeit, Datum."""
    t, kind = next_start(jobs, job_id)
    if not t:
        return dict(next_at=None, next_kind=kind, next_day=None, next_hm="", next_full="")
    days = (t.date() - datetime.datetime.now(t.tzinfo).date()).days
    return dict(next_at=t, next_kind=kind, next_day=days, next_hm=t.strftime("%H:%M"), next_full=t.strftime("%d.%m.%Y %H:%M"))


LIVE_FULL_DEFAULT = "0 3 * * *"


def live_interval(job):
    try:
        return max(1, min(1440, int(job.get("live_interval") or 1)))
    except (TypeError, ValueError):
        return 1


def live_mode(job):
    """mirror (Standard): jede Runde wie Spiegeln inkl. Loeschen. fast: nur neue/geaenderte Dateien kopieren."""
    return "fast" if job.get("live_mode") == "fast" and not is_bisync(job) else "mirror"


def live_full_every(full):
    """'@every 6h' / '@every 90m' -> Minuten, sonst None (dann ist es ein Cron-Ausdruck)."""
    m = re.match(r"^@every\s+(\d+)\s*([mh])$", (full or "").strip())
    if not m:
        return None
    return int(m.group(1)) * (60 if m.group(2) == "h" else 1)


def every_text(n):
    if n % 60 == 0:
        h = n // 60
        return "jede Stunde" if h == 1 else f"alle {h} Stunden"
    return "jede Minute" if n == 1 else f"alle {n} Minuten"


def live_text(job):
    n = live_interval(job)
    if is_bisync(job):
        return "Live Zwei-Wege, jede Minute" if n == 1 else f"Live Zwei-Wege, alle {n} Minuten"
    if live_mode(job) == "fast":
        return "Live, jede Minute" if n == 1 else f"Live, alle {n} Minuten"
    return "Live wie Spiegeln, jede Minute" if n == 1 else f"Live wie Spiegeln, alle {n} Minuten"


def live_full_text(job):
    if is_bisync(job):
        return "jede Runde gleicht beide Seiten ab, inklusive Löschen"
    if live_mode(job) == "mirror":
        return "jede Runde gleicht voll ab, inklusive Löschen"
    full = (job.get("live_full") or "").strip()
    if not full:
        return "kein voller Abgleich"
    every = live_full_every(full)
    if every:
        return "voller Abgleich " + every_text(every)
    return "voller Abgleich " + (cron_text(full) or full)


def live_check(f_interval, f_full):
    """Formularwerte pruefen. Liefert (interval, full, fehler)."""
    try:
        iv = int(str(f_interval or "1").strip())
        if not 1 <= iv <= 1440:
            raise ValueError
    except ValueError:
        return 1, f_full, "Live-Intervall: bitte 1 bis 1440 Minuten angeben."
    full = (f_full or "").strip()
    if full.startswith("@every"):
        every = live_full_every(full)
        if not every or not 5 <= every <= 43200:
            return iv, full, "Voller Abgleich: Intervall bitte als @every 6h oder @every 90m angeben (5 Minuten bis 30 Tage)."
        return iv, full, None
    if full:
        try:
            CronTrigger.from_crontab(full, timezone=TZ)
        except ValueError as e:
            return iv, full, f"Zeitplan für den vollen Abgleich ungültig: {e}"
    return iv, full, None


LIVE_RESET_KEYS = ("source", "dest", "excludes", "selection", "include_source_dir", "delete_excluded", "trigger", "live_mode")


def live_reset_if_changed(old, new):
    """Quelle/Ziel/Filter geaendert -> naechster Live-Lauf ist wieder ein voller Abgleich."""
    if any(old.get(k) != new.get(k) for k in LIVE_RESET_KEYS):
        new.pop("live_last", None)
    if is_bisync(new) and any(old.get(k) != new.get(k) for k in BISYNC_RESET_KEYS):
        new.pop("bisync_ready", None)   # Zwei-Wege: neu zusammenfuehren (--resync)
        new.pop("bisync_need_resync", None)


# ---------------------------------------------------------------- Web
def _secret_key():
    path = os.path.join(CONFIG_DIR, "secret_key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
        os.chmod(path, 0o600)
    with open(path) as f:
        return f.read().strip()


app.secret_key = _secret_key()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_NAME="mirrorsync_session",
                  PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=30))
_failed = {}  # ip -> (anzahl, zeitpunkt) fuer Schutz gegen Passwort-Raten
PUBLIC = {"/health", "/login", "/login/2fa", "/setup", "/login/passkey", "/login/passkey/options"}
store = users.Store(DB)
role_store = roles.RoleStore(DB)


def load_groups():
    return DB.get_map("group")


def save_groups(data):
    DB.put_map("group", data)


def remote_vis_map():
    return {k: (v or {}).get("visible_to", "all") for k, v in DB.get_map("remote_meta").items()}


def make_access(name, role_id, key_id=None):
    """Rechte = Rolle + Gruppen (Benutzer bzw. API-Key), dazu Sichtbarkeit der Speicherorte."""
    all_g = load_groups()
    mine = {gid: all_g[gid] for gid in roles.groups_of(all_g, None if key_id else name, key_id)}
    return roles.Access(name, role_store.get(role_id), mine, remote_vis_map(), key_id)


def vis_options():
    """Auswahl fuer "Sichtbar für": Benutzer und Gruppen."""
    return {"users": [("user:" + n.lower(), n) for n in sorted(store.load(), key=str.lower)],
            "groups": [("group:" + gid, x.get("name", gid)) for gid, x in
                       sorted(load_groups().items(), key=lambda kv: kv[1].get("name", "").lower())]}


def vis_from_form(f):
    """Formular (vis_mode=all|some, vis=[kennungen]) bzw. API -> ("all" | [kennungen], fehler)."""
    if f.get("vis_mode") != "some":
        return "all", None
    raw = f.getlist("vis") if hasattr(f, "getlist") else str(f.get("vis") or "").split("\n")
    o = vis_options()
    valid = {k for k, _ in o["users"]} | {k for k, _ in o["groups"]}
    out = []
    for x in raw:
        x = x.strip()
        if not x:
            continue
        if x.startswith("user:"):
            x = x.lower()
        if x not in valid:
            return "all", i18n.t("„Sichtbar für“: {0} gibt es nicht (Form user:<Name> oder group:<ID>).", x)
        if x not in out:
            out.append(x)
    return out, None


def vis_text(vis):
    """Lesbare Liste fuer Anzeige und Audit."""
    if vis is None or vis == "all":
        return i18n.t("alle mit Recht")
    o = vis_options()
    names = dict(o["users"] + o["groups"])
    return ", ".join(names.get(x, x) for x in vis) or i18n.t("nur Admins und Besitzer")


def drop_principal(pid):
    """Benutzer oder Gruppe wurde geloescht: aus allen "Sichtbar für"-Listen entfernen."""
    with _lock:
        jobs = load_jobs()
        hit = False
        for j in jobs.values():
            if isinstance(j.get("visible_to"), list) and pid in j["visible_to"]:
                j["visible_to"].remove(pid)
                hit = True
        if hit:
            save_jobs(jobs)
    meta = DB.get_map("remote_meta")
    changed = False
    for m in meta.values():
        if isinstance(m.get("visible_to"), list) and pid in m["visible_to"]:
            m["visible_to"].remove(pid)
            changed = True
    if changed:
        DB.put_map("remote_meta", meta)
login_log = users.LoginLog(DB)
audit_log = audit.AuditLog(DB)
geoip.init(CONFIG_DIR)
guard = ipguard.Guard(DB)
IPGUARD_OFF = os.environ.get("IPGUARD", "").lower() in ("0", "off", "false", "nein")


SETUP_TOKEN_FILE = os.path.join(CONFIG_DIR, "setup_token")
SETUP_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # ohne 0/O und 1/I
# Einmal-Code bei der Ersteinrichtung nur auf Wunsch (SETUP_TOKEN=true), z. B. wenn der Container vor dem ersten
# Admin schon aus dem Internet erreichbar ist. Standard: der erste Aufruf im Browser legt direkt den Admin an.
SETUP_TOKEN_ON = os.environ.get("SETUP_TOKEN", "").strip().lower() in ("1", "true", "yes", "on", "ja")


def setup_token(show=False):
    """Einmal-Code fuer die Ersteinrichtung (nur mit SETUP_TOKEN=true). Existiert nur, solange es keinen Benutzer gibt,
    und steht im Container-Log."""
    if store.load() or not SETUP_TOKEN_ON:
        try:
            os.remove(SETUP_TOKEN_FILE)
        except OSError:
            pass
        return None
    tok = ""
    try:
        with open(SETUP_TOKEN_FILE, encoding="utf-8") as f:
            tok = f.read().strip()
    except OSError:
        pass
    new = not tok
    if new:
        raw = "".join(secrets.choice(SETUP_ALPHABET) for _ in range(12))
        tok = "-".join(raw[i:i + 4] for i in range(0, 12, 4))
        with open(SETUP_TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(tok)
        os.chmod(SETUP_TOKEN_FILE, 0o600)
    if show or new:
        line = "=" * 62
        print(f"\n{line}\n  " + i18n.t("MirrorSync: Ersteinrichtung") + "\n  " +
              i18n.t("Web-GUI öffnen und diesen Einrichtungs-Code eingeben:") + f"\n\n      {tok}\n\n  " +
              i18n.t("(steht auch in config/setup_token, gilt bis der erste Admin angelegt ist)") + f"\n{line}\n", flush=True)
    return tok


def bootstrap_users():
    """Erster Start / Update von 1.1.x: Admin aus WEB_USER/WEB_PASS anlegen.
    ADMIN_RESET=true setzt Passwort und 2FA dieses Admins auf WEB_PASS zurueck (Notfall)."""
    all_users = store.load()
    if not all_users and WEB_PASS:
        all_users[WEB_USER] = users.new_user(WEB_PASS, "admin")
        store.save(all_users)
        print(f"Admin-Benutzer '{WEB_USER}' aus WEB_USER/WEB_PASS angelegt.", flush=True)
    elif os.environ.get("ADMIN_RESET", "").lower() in ("1", "true", "yes", "ja") and WEB_PASS:
        u = all_users.get(WEB_USER) or users.new_user(WEB_PASS, "admin")
        u.update(hash=users.hash_password(WEB_PASS), role="admin", totp_enabled=False, totp_secret="", disabled=False, disabled_by="", lock_from="", lock_until="", auto_lock_until="", fail_count=0,
                 backup_codes=[], sv=u.get("sv", 1) + 1)
        all_users[WEB_USER] = u
        store.save(all_users)
        audit_log.add("System", "user", "zurückgesetzt (ADMIN_RESET)", WEB_USER, detail="Passwort und 2FA")
        print(f"ADMIN_RESET: Passwort und 2FA von '{WEB_USER}' zurueckgesetzt. "
              "ADMIN_RESET jetzt wieder entfernen!", flush=True)


# Endpunkt -> benoetigtes Recht. None = nur angemeldet. Fehlende Endpunkte = nur angemeldet.
ENDPOINT_PERMS = {
    "index": "jobs.view", "jobs_running": "jobs.view", "schedules": "jobs.view", "schedules_json": "jobs.view", "schedule_job": "jobs.edit", "schedule_chains": "jobs.edit", "show_log": "jobs.logs", "show_run": "jobs.logs", "download_run": "jobs.logs", "delete_job": "jobs.delete", "stop": "jobs.run",
    "job_notify_test": "jobs.notify", "job_pause": "jobs.edit",
    "remotes": "remotes.view", "test_remote": "remotes.test", "delete_remote": "remotes.delete",
    "auth_remote": "remotes.edit", "browse": "remotes.browse", "browse_list": "remotes.browse",
    "users_page": "users.view", "login_history": "users.view", "login_log_action": "users.manage", "user_unlock": "users.manage", "user_edit": "users.manage", "user_delete": "users.manage",
    "roles_page": "roles.manage", "role_edit": "roles.manage", "role_delete": "roles.manage",
    "groups_page": "groups.manage", "group_edit": "groups.manage", "group_delete": "groups.manage",
    "general_settings": "system.settings", "audit_page": "system.audit", "audit_export": "system.audit",
    "access_settings": "system.access", "access_block": "system.access", "access_unblock": "system.access",
}


def endpoint_perm():
    ep, va, post = request.endpoint, request.view_args or {}, request.method == "POST"
    if ep == "edit_job":
        return ("jobs.edit" if post else "jobs.view") if va.get("job_id") else "jobs.create"
    if ep in ("run_job", "resync_job"):
        return "jobs.dryrun" if request.form.get("dry") == "1" else "jobs.run"
    if ep == "edit_remote":
        return "remotes.edit" if va.get("name") else "remotes.create"
    if ep == "remote_wizard":
        return "remotes.edit" if g.access.has("remotes.edit") else "remotes.create"
    if ep == "settings_page":
        return "notify.edit" if post else "notify.view"
    if ep == "files_op":
        return filemgr.OP_PERMS.get(va.get("op"), "files.edit")
    return ENDPOINT_PERMS.get(ep)


def scope_ok():
    """Beschraenkung der Rolle auf einzelne Aufgaben/Speicherorte pruefen."""
    va = request.view_args or {}
    acc = g.access
    if "job_id" in va and va["job_id"]:
        return acc.job_ok(va["job_id"], load_jobs().get(va["job_id"]))
    if request.endpoint in ("edit_remote", "remote_wizard", "test_remote", "delete_remote", "auth_remote") and va.get("name"):
        return acc.remote_ok(va["name"])
    if request.endpoint == "browse":
        path = request.args.get("path", "").strip()
        return True if not path else acc.path_ok(path)
    return True


def current_user():
    name = session.get("user")
    u = store.get(name) if name else None
    if u and session.get("sv") == u.get("sv", 1) and not users.inactive_reason(u):
        return name, u
    return None, None


def can(perm):
    acc = g.get("access")
    return bool(acc and acc.has(perm))


def role_name(rid):
    r = role_store.get(rid)
    return r["name"] if r else rid


app.jinja_env.globals.update(can=can, role_name=role_name)


@app.context_processor
def _badges():
    try:
        n = login_log.unacked() if can("users.view") else 0
    except Exception:   # noqa: BLE001
        n = 0
    try:
        mini = bool(g.get("user")) and (store.get(g.user) or {}).get("sidebar") == "mini"
    except Exception:   # noqa: BLE001
        mini = False
    return {"fail_badge": n, "side_mini": mini}


def _dt(v):
    """'2026-11-22T17:30' -> '22.11.2026 17:30'"""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}:\d{2})", v or "")
    return f"{m.group(3)}.{m.group(2)}.{m.group(1)} {m.group(4)}" if m else (v or "")


def _ua(v):
    """Kurzform des User-Agents: 'Firefox · Windows'."""
    v = v or ""
    browser = next((n for k, n in (("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
                                   ("Safari/", "Safari"), ("curl/", "curl")) if k in v), "")
    system = next((n for k, n in (("Windows", "Windows"), ("Android", "Android"), ("iPhone", "iPhone"), ("iPad", "iPad"),
                                  ("Mac OS", "macOS"), ("Linux", "Linux")) if k in v), "")
    return " · ".join(x for x in (browser, system) if x) or v[:40]


app.jinja_env.filters.update(dt=_dt, ua=_ua)


@app.before_request
def auth():
    g.user, g.role, g.access = None, None, roles.Access()
    br = request.environ.get("mirrorsync.bridge")
    if br:
        # Interner Aufruf aus der REST-API/MCP (api.gui): dieselbe Seite wie in der GUI, mit den Rechten des Keys.
        # Der Schluessel steht nur im WSGI-Environ und kann nicht per HTTP gesetzt werden.
        g.user, g.role, g.access, g.user_lang, g.api_key = br["user"], br["role"], br["access"], br["lang"], br["key"]
        g.bridge = br
        perm = endpoint_perm()
        if (perm and not g.access.has(perm)) or not scope_ok():
            br["out"]["denied"] = perm or "scope"
            return {"ok": False, "error": "Keine Berechtigung"}, 403
        return None
    blocked = _ip_blocked()
    if blocked:
        return blocked
    if request.path.startswith("/static") or request.path in ("/health", "/favicon.ico"):
        return None
    if request.path.startswith(("/api/v1", "/mcp")):   # REST-API und MCP: API-Key (Bearer)
        if not store.load():
            return {"error": "MirrorSync ist noch nicht eingerichtet."}, 503
        return api.authenticate()
    lang_q = request.args.get("lang")
    if lang_q and i18n.valid(lang_q):
        session["lang"] = lang_q   # Auswahl auf der Anmelde-/Einrichtungsseite
    if not store.load():
        # Noch kein Benutzer: Ersteinrichtung erzwingen
        return None if request.path == "/setup" else redirect(url_for("setup"))
    name, u = current_user()
    if name:
        g.user, g.role = name, u["role"]
        g.user_lang = u.get("lang") or ""
        g.access = make_access(name, u["role"])
    if request.path in PUBLIC:
        return None
    wants_json = request.path == "/browse" or request.headers.get("Accept", "").startswith("application/json")
    if not name:
        if wants_json:
            return {"ok": False, "error": "Nicht angemeldet"}, 401
        nxt = request.full_path.rstrip("?") if request.method == "GET" else "/"
        return redirect(url_for("login", next=nxt) if nxt != "/" else url_for("login"))
    perm = endpoint_perm()
    if (perm and not g.access.has(perm)) or not scope_ok():
        if wants_json:
            return {"ok": False, "error": "Keine Berechtigung"}, 403
        return render_template("denied.html", perm=roles.PERM_LABELS.get(perm)), 403
    return None


def _client_ip():
    """Adresse des Browsers. X-Forwarded-For nur, wenn ein Reverse-Proxy eingestellt ist (sonst faelschbar).
    Genommen wird der letzte Eintrag, den der eigene Proxy angehaengt hat."""
    ip = request.remote_addr or ""
    if load_settings().get("trust_proxy"):
        fwd = [x.strip() for x in request.headers.get("X-Forwarded-For", "").split(",") if x.strip()]
        ip = fwd[-1] if fwd else (request.headers.get("X-Real-IP", "").strip() or ip)
    return ip


def _country_iso(ip):
    return geoip.locate(ip).get("iso", "")


def _ip_blocked():
    """Zugriffsschutz nach IP. Liefert eine 403-Antwort oder None."""
    if IPGUARD_OFF or request.path == "/health":
        return None
    ip = _client_ip()
    verdict = guard.check(ip, _country_iso)
    if not verdict:
        return None
    reason, rule = verdict
    guard.hit(rule)
    if request.method == "POST" and request.path in ("/login", "/login/2fa"):
        _record_login(request.form.get("user", "").strip() or session.get("pending", ""), False, f"IP gesperrt ({reason})",
                      count=False)
    html = (f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>Gesperrt</title>"
            f"<body style='font:15px system-ui;display:grid;place-items:center;min-height:90vh;margin:0;background:#f6f7f9;color:#0f172a'>"
            f"<div style='max-width:420px;padding:24px;background:#fff;border:1px solid #e5e7eb;border-radius:12px'>"
            f"<h2 style='margin-top:0'>🚫 Zugriff gesperrt</h2><p>Von deiner Adresse <code>{Markup.escape(ip)}</code> ist kein Zugriff "
            f"auf MirrorSync erlaubt ({Markup.escape(reason)}).</p></div>")
    return html, 403


# ---------------------------------------------------------------- Audit-Log
def _remotes_snapshot():
    cp = configparser.RawConfigParser(strict=False)
    try:
        cp.read(RCLONE_CONF, encoding="utf-8")
    except (configparser.Error, OSError):
        return {}
    return {sec: dict(cp.items(sec)) for sec in cp.sections()}


def _remotes_audit():
    snap = _remotes_snapshot()
    for name, vis in remote_vis_map().items():
        if name in snap and vis != "all":
            snap[name]["visible_to"] = vis_text(vis)
    return snap


def _groups_audit():
    out = {}
    for gid, x in load_groups().items():
        out[gid] = dict(x, members=", ".join(x.get("members") or []),
                        keys=", ".join((DB.get("apikey", k) or {}).get("name", k) for k in x.get("keys") or []))
    return out


def _keys_audit():
    keep = ("name", "role", "expires", "ips", "disabled", "lock_from", "lock_until", "windows", "lang")
    out = {kid: {x: k.get(x) for x in keep} for kid, k in DB.get_map("apikey").items()}
    for v in out.values():
        v["windows"] = api.windows_text(v.get("windows")) if v.get("windows") else ""
    return out


AUDIT_SNAP = {
    "apikey": _keys_audit,
    "group": _groups_audit,
    "job": lambda: {k: (dict(v, visible_to=vis_text(v["visible_to"])) if "visible_to" in v else v) for k, v in load_jobs().items()},
    "remote": _remotes_audit, "user": lambda: store.load(), "role": lambda: role_store.load(),
    "settings": lambda: {"Einstellungen": load_settings()}, "access": lambda: {"Zugriff": guard.load()},
}
WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")
# Endpunkt -> Datenbereiche, deren Vorher/Nachher verglichen werden
AUDIT_EP = {
    "edit_job": ["job"], "delete_job": ["job"], "job_pause": ["job"], "schedule_job": ["job"], "schedule_chains": ["job"],
    "edit_remote": ["remote"], "remote_wizard": ["remote"], "auth_remote": ["remote"], "delete_remote": ["remote"],
    "settings_page": ["settings"], "general_settings": ["settings"],
    "access_settings": ["access"], "access_block": ["access"], "access_unblock": ["access"],
    "role_edit": ["role"], "role_delete": ["role", "user"], "user_edit": ["user", "group"], "user_delete": ["user", "group"],
    "group_edit": ["group"], "group_delete": ["group"], "api_key_edit": ["apikey", "group"],
    "user_unlock": ["user"], "account": ["user"], "setup": ["user"], "backup_settings": ["settings"],
}
# Aktionen, die ohne Datenaenderung protokolliert werden
AUDIT_ACTIONS = {
    "run_job": ("run", "gestartet"), "resync_job": ("run", "neu zusammengeführt (Zwei-Wege)"), "stop": ("run", "gestoppt"), "test_remote": ("remote", "Verbindung getestet"),
    "user_unlock": ("user", "entsperrt"), "login_log_action": ("login", "Anmeldeverlauf bearbeitet"),
}
SECTION_NAMES = {"settings_page": "Benachrichtigungen", "general_settings": "Allgemein"}


def _browser(ua):
    ua = ua or ""
    for name, key in (("Edge", "Edg/"), ("Firefox", "Firefox/"), ("Chrome", "Chrome/"), ("Safari", "Safari/")):
        if key in ua:
            os_ = next((o for o, k in (("Windows", "Windows"), ("Android", "Android"), ("iOS", "iPhone"), ("iPadOS", "iPad"),
                                       ("macOS", "Mac OS"), ("Linux", "Linux")) if k in ua), "")
            return f"{name}{' · ' + os_ if os_ else ''}"
    return ua[:80]


def _request_info():
    """Woher kam die Aktion? Fuer die Detailansicht im Audit-Log."""
    try:
        if not request:
            return {}
        path = request.path
    except RuntimeError:
        return {}
    br = g.get("bridge")
    if br is not None:
        via = br.get("via") or "REST-API"
    elif g.get("api_key") or path.startswith(("/api/", "/mcp")):
        via = "MCP" if path.startswith("/mcp") else "REST-API"
    else:
        via = "Weboberfläche"
    info = {"Über": via, "Anfrage": f"{request.method} {path}"}
    if via == "Weboberfläche":
        info["Browser"] = _browser(request.headers.get("User-Agent"))
    return info


def audit_add(cat, action, target="", changes=None, detail="", user=None, info=None):
    try:
        ip = _client_ip() if request else ""
    except RuntimeError:
        ip = ""
    loc = geoip.locate(ip) if ip else {"flag": "", "name": ""}
    if user is None:
        user = g.get("user") if request else None
    try:
        audit_log.add(user or "System", cat, action, target, changes, detail, ip, loc.get("flag", ""), loc.get("name", ""),
                      info=dict(_request_info(), **(info or {})))
    except Exception as e:   # Audit darf nie eine Aktion verhindern
        print(f"Audit-Log nicht schreibbar: {e}", flush=True)


@app.before_request
def _audit_before():
    if request.method in WRITE_METHODS and request.endpoint in AUDIT_EP:
        g.audit_snap = {c: json.loads(json.dumps(AUDIT_SNAP[c]())) for c in AUDIT_EP[request.endpoint]}


def _audit_target(kind, key, obj):
    if kind in ("job", "role", "group", "apikey"):
        return (obj or {}).get("name") or key
    return key


@app.after_request
def _audit_after(resp):
    ep = request.endpoint
    if request.method not in WRITE_METHODS or resp.status_code >= 400:
        return resp
    try:
        logged = False
        for kind, before in (g.get("audit_snap") or {}).items():
            after = AUDIT_SNAP[kind]()
            cat = "schedule" if ep and ep.startswith("schedule") else ("api" if kind == "apikey" else kind)
            for key in sorted(set(before) | set(after)):
                a, b = before.get(key), after.get(key)
                if a == b:
                    continue
                if kind in ("settings", "access"):
                    ch = audit.diff(a, b, kind)
                    if ch:
                        audit_add(cat, "geändert", SECTION_NAMES.get(ep, key), ch)
                        logged = True
                elif a is None:
                    audit_add(cat, "angelegt", _audit_target(kind, key, b), audit.diff({}, b, kind),
                              user=key if ep == "setup" else None)
                    logged = True
                elif b is None:
                    det = f"{a.get('source', '')} → {a.get('dest', '')}" if kind == "job" else \
                        (f"Typ {a.get('type', '')}" if kind == "remote" else (f"Rolle {a.get('role', '')}" if kind == "user" else ""))
                    audit_add(cat, "gelöscht", _audit_target(kind, key, a), audit.diff(a, {}, kind), detail=det)
                    logged = True
                else:
                    ch = audit.diff(a, b, kind)
                    if ch:
                        who = "eigenes Konto" if ep == "account" else ""
                        audit_add(cat, "geändert", _audit_target(kind, key, b), ch, detail=who)
                        logged = True
        if not logged and ep in AUDIT_ACTIONS:
            cat, action = AUDIT_ACTIONS[ep]
            va = request.view_args or {}
            target, detail, info = va.get("job_id") or va.get("name") or "", "", {}
            if "job_id" in va:
                jj = load_jobs().get(va["job_id"], {})
                target = jj.get("name", target)
                if jj:
                    info = {"Aufgabe-ID": va["job_id"], "Art": "Zwei-Wege-Sync" if is_bisync(jj) else "Spiegeln",
                            "Quelle" if not is_bisync(jj) else "Seite A": jj.get("source", ""),
                            "Ziel" if not is_bisync(jj) else "Seite B": effective_dest(jj),
                            "Lauf": _current_run.get(va["job_id"], "")}
            if ep == "run_job" and request.form.get("dry") == "1":
                action = "Testlauf gestartet"
            if ep == "login_log_action":
                detail = {"ack": "bestätigt", "delete": "gelöscht"}.get(request.form.get("action"), request.form.get("action", ""))
            audit_add(cat, action, target, detail=detail, info=info)
    except Exception as e:   # noqa: BLE001 - Audit darf nie eine Aktion verhindern
        print(f"Audit-Fehler: {e}", flush=True)
    return resp


def _record_login(name, ok, reason="", count=True):
    ip = _client_ip()
    loc = geoip.locate(ip)
    ua = request.headers.get("User-Agent", "")[:160]
    login_log.add(user=name[:64], ok=ok, reason=reason, ip=ip, iso=loc["iso"], country=loc["name"],
                  flag=loc["flag"], ua=ua)
    audit_add("login", "angemeldet" if ok else "Anmeldung fehlgeschlagen", name[:64], detail=reason, user=name[:64] or "?")
    if not ok and not reason.startswith("Konto für") and not reason.startswith("Konto deaktiviert, bis"):
        _notify_fail(name[:64], reason, ip, loc)
    if not ok and count and not IPGUARD_OFF:
        hit = guard.register_fail(ip)
        if hit:
            net, until = hit
            how = f"bis {_dt(until)}" if until else "dauerhaft"
            login_log.add(user=name[:64], ok=False, reason=f"IP {net} automatisch gesperrt ({how})", ip=ip, iso=loc["iso"],
                          country=loc["name"], flag=loc["flag"], ua=ua)
            audit_add("access", "IP automatisch gesperrt", net, detail=f"{how}, zuletzt Benutzer „{name[:64]}“", user="System")
            if guard.load().get("notify"):
                st = load_settings()
                ev = notify.event(st, "ip_block", {"ip": net, "land": loc["name"], "flagge": loc["flag"],
                                                   "wie_lange": how, "benutzer": name},
                                  status="ipblock", job="Anmeldung", source=ip, dest=name)
                ev["errors"] = [ev["message"]]
                threading.Thread(target=notify.send, args=(st, ev), daemon=True).start()
    return ip, loc


INACTIVE_TEXT = {"deaktiviert": "Dieses Konto ist deaktiviert.", "gesperrt": "Dieses Konto ist zurzeit gesperrt."}


def lock_limits():
    st = load_settings()
    try:
        attempts = max(0, min(100, int(st.get("lock_attempts") or 0)))
    except ValueError:
        attempts = 5
    try:
        minutes = max(0, min(525600, int(st.get("lock_minutes") or 0)))
    except ValueError:
        minutes = 15
    return attempts, minutes, fail_notify_mode(st) != "off"


def fail_notify_mode(st=None):
    """off / lock (nur bei Sperre) / every (jeder Fehlversuch, gedrosselt). Alte Einstellung lock_notify uebernehmen."""
    st = st or load_settings()
    mode = st.get("fail_notify") or ("lock" if st.get("lock_notify") else "off")
    return mode if mode in ("off", "lock", "every") else "lock"


_fail_note = {"last": 0, "pending": []}


def _notify_fail(name, reason, ip, loc):
    """Fehlversuch melden, hoechstens einmal pro Drosselzeit; dazwischen Gesammeltes kommt mit der naechsten Meldung."""
    st = load_settings()
    if fail_notify_mode(st) != "every":
        return
    try:
        gap = max(1, int(st.get("fail_notify_minutes") or 15)) * 60
    except ValueError:
        gap = 900
    line = f"{time.strftime('%H:%M:%S')} {name or '?'} von {ip} {loc.get('flag', '')} {loc.get('name', '')}: {reason}".strip()
    with _lock:
        _fail_note["pending"].append(line)
        wait = gap - (time.time() - _fail_note["last"])
        if wait > 0:
            if not _fail_note.get("timer"):   # Gesammeltes nach Ablauf der Drosselzeit nachschicken
                t = threading.Timer(wait + 1, _flush_fail_notes)
                t.daemon = True
                _fail_note["timer"] = t
                t.start()
            return
    _send_fail_notes(st, gap)


def _flush_fail_notes():
    _fail_note["timer"] = None
    st = load_settings()
    if _fail_note["pending"] and fail_notify_mode(st) == "every":
        try:
            gap = max(1, int(st.get("fail_notify_minutes") or 15)) * 60
        except ValueError:
            gap = 900
        _send_fail_notes(st, gap)


def _send_fail_notes(st, gap):
    with _lock:
        lines, _fail_note["pending"], _fail_note["last"] = _fail_note["pending"], [], time.time()
    if not lines:
        return
    ip = lines[-1].split(" von ", 1)[-1].split(" ", 1)[0]
    name = lines[-1].split(" ", 2)[1] if len(lines[-1].split(" ")) > 1 else ""
    liste = "\n".join(lines[-20:]) + (f"\n… und {len(lines) - 20} weitere" if len(lines) > 20 else "")
    ev = notify.event(st, "login_fail", {"anzahl": str(len(lines)), "anmeldungen": "Anmeldung" if len(lines) == 1 else "Anmeldungen",
                                         "liste": liste, "benutzer": name, "ip": ip, "pause": str(gap // 60)},
                      status="login", job="Anmeldung", source=ip, dest=name, errors=lines[-5:])
    threading.Thread(target=notify.send, args=(st, ev), daemon=True).start()


def _locked():
    """Bremse pro IP-Adresse (zusaetzlich zur Sperre pro Konto)."""
    attempts = lock_limits()[0] or 5
    count, since = _failed.get(_client_ip(), (0, 0))
    return count >= max(attempts, 3) and time.time() - since < 300


def _account_fail(name):
    """Fehlversuch fuer ein bestehendes Konto zaehlen und es ggf. sperren."""
    attempts, minutes, notify_admin = lock_limits()
    with users._lock:
        all_users = store.load()
        u = all_users.get(name)
        if not u:
            return
        u["fail_count"] = u.get("fail_count", 0) + 1
        locked = None
        if attempts and u["fail_count"] >= attempts:
            last_admin = name in users.permanent_admins(all_users) and not users.permanent_admins(all_users, except_name=name)
            if minutes or last_admin:
                until = datetime.datetime.now() + datetime.timedelta(minutes=minutes or 15)
                u["auto_lock_until"] = until.strftime("%Y-%m-%dT%H:%M")
                locked = f"für {minutes or 15} Minuten gesperrt (bis {until:%d.%m.%Y %H:%M})"
                if not minutes:
                    locked += ", nicht dauerhaft, weil es der letzte Admin ist"
            else:
                u.update(disabled=True, disabled_by="Fehlversuche")
                locked = "deaktiviert, bis ein Admin es wieder aktiviert"
            u["fail_count"] = 0
            u["sv"] = u.get("sv", 1) + 1
        store.save(all_users)
    if locked:
        ip, loc = _record_login(name, False, f"Konto {locked}", count=False)
        if notify_admin:
            st = load_settings()
            ev = notify.event(st, "account_lock", {"benutzer": name, "sperre": locked, "versuche": str(attempts), "ip": ip,
                                                   "land": loc.get("name", ""), "flagge": loc.get("flag", "")},
                              status="lock", job="Anmeldung", source=ip, dest=name)
            ev["errors"] = [ev["message"]]
            threading.Thread(target=notify.send, args=(st, ev), daemon=True).start()


def _fail():
    ip = _client_ip()
    count, since = _failed.get(ip, (0, 0))
    time.sleep(1)
    _failed[ip] = (count + 1 if time.time() - since < 300 else 1, time.time())


def _finish_login(name, u, remember, method="Passwort"):
    _failed.pop(_client_ip(), None)
    ip, loc = _record_login(name, True, method)
    nxt = session.get("next") or "/"
    session.clear()
    session["user"], session["sv"] = name, u.get("sv", 1)
    session.permanent = bool(remember)
    store.update(name, fail_count=0, last_login=time.strftime("%Y-%m-%d %H:%M"), last_ip=ip, last_country=loc["name"],
                 last_flag=loc["flag"])
    return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else "/")


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if store.load():
        return redirect(url_for("login"))
    err = None
    token = setup_token()
    if request.method == "POST" and _locked():
        err = "Zu viele Fehlversuche. Bitte 5 Minuten warten."
    elif request.method == "POST":
        name, pw = request.form.get("user", "").strip(), request.form.get("password", "")
        typed = re.sub(r"[^A-Z0-9]", "", request.form.get("token", "").upper())
        if SETUP_TOKEN_ON and (not token or not hmac.compare_digest(typed, token.replace("-", ""))):
            _fail()
            print(f"Ersteinrichtung: falscher Einrichtungs-Code von {_client_ip()}", flush=True)
            err = "Einrichtungs-Code falsch. Er steht im Container-Log (docker logs mirrorsync)."
        elif not users.valid_name(name):
            err = "Benutzername: 1-32 Zeichen, Buchstaben, Ziffern, - _ . @"
        elif pw != request.form.get("password2", ""):
            err = "Die Passwörter stimmen nicht überein."
        else:
            err = users.password_problem(pw)
        if not err:
            with users._lock:
                if store.load():   # jemand war schneller
                    return redirect(url_for("login"))
                lang = request.form.get("language") if i18n.valid(request.form.get("language") or "") else i18n.current()
                st = load_settings()
                st["language"] = lang
                save_settings(st)
                i18n.default_lang = lang
                store.save({name: dict(users.new_user(pw, "admin"), lang=lang)})
            setup_token()   # Code ist verbraucht
            resp = _finish_login(name, store.get(name), True, "Ersteinrichtung")
            session["welcome"] = True
            return redirect(url_for("account"))
    return render_template("login.html", mode="setup", err=err, user=request.form.get("user", ""),
                           token_typed=request.form.get("token", ""), need_token=SETUP_TOKEN_ON)


@app.route("/login", methods=["GET", "POST"])
def login():
    err = None
    if request.method == "GET" and request.args.get("next"):
        session["next"] = request.args["next"]
    if _locked():
        err = "Zu viele Fehlversuche. Bitte 5 Minuten warten."
        if request.method == "POST":
            _record_login(request.form.get("user", "").strip(), False, "gesperrt (zu viele Fehlversuche)", count=False)
    elif request.method == "POST":
        typed, pw = request.form.get("user", "").strip(), request.form.get("password", "")
        name = store.find(typed) or typed   # Gross-/Kleinschreibung egal
        u = store.get(name)
        why = users.inactive_reason(u) if u else None
        if users.check_password(u, pw) and why:
            _record_login(name, False, f"Konto {why}")
            err = INACTIVE_TEXT[why]
        elif users.check_password(u, pw):
            if u.get("totp_enabled"):
                nxt = session.get("next")
                session.clear()
                session.update(pending=name, pending_at=time.time(), remember=bool(request.form.get("remember")))
                if nxt:
                    session["next"] = nxt
                return redirect(url_for("login_2fa"))
            return _finish_login(name, u, request.form.get("remember"))
        else:
            if not u:
                users.check_password({"hash": _DUMMY_HASH}, pw)  # gleiche Laufzeit fuer unbekannte Namen
            _record_login(name, False, "Passwort falsch" if u else "unbekannter Benutzer")
            if u:
                _account_fail(name)
            _fail()
            err = "Benutzername oder Passwort falsch."
    return render_template("login.html", mode="login", err=err, user=request.form.get("user", ""), pk_off=bool(_pk_rp()[2]))


_DUMMY_HASH = users.hash_password(secrets.token_hex(8))


@app.route("/login/2fa", methods=["GET", "POST"])
def login_2fa():
    name = session.get("pending")
    if not name or time.time() - session.get("pending_at", 0) > 300:
        session.pop("pending", None)
        return redirect(url_for("login"))
    u = store.get(name)
    if not u or not u.get("totp_enabled") or users.inactive_reason(u):
        return redirect(url_for("login"))
    err = None
    if _locked():
        err = "Zu viele Fehlversuche. Bitte 5 Minuten warten."
    elif request.method == "POST":
        code = request.form.get("code", "").strip()
        counter = users.verify_totp(u["totp_secret"], code, u.get("totp_last", 0))
        if counter:
            store.update(name, totp_last=counter)
            return _finish_login(name, u, session.get("remember"), "Passwort + 2FA")
        rest = users.use_backup_code(u, code)
        if rest is not None:
            store.update(name, backup_codes=rest)
            session["backup_left"] = len(rest)
            resp = _finish_login(name, u, session.get("remember"), "Passwort + Backup-Code")
            session["flash"] = f"Backup-Code verwendet. Noch {len(rest)} übrig." + (
                " Bitte unter „Mein Konto“ neue erzeugen." if len(rest) < 3 else "")
            return resp
        _record_login(name, False, "2FA-Code falsch")
        _account_fail(name)
        _fail()
        err = "Code ungültig."
    return render_template("login.html", mode="2fa", err=err, user=name)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if g.get("user"):
        audit_add("login", "abgemeldet", g.user)
    session.clear()
    return redirect(url_for("login"))


AUDIT_PAGE = 200


def _audit_filters():
    a = request.args
    day = lambda v: v if re.match(r"^\d{4}-\d{2}-\d{2}$", v or "") else ""
    return {"cat": a.get("cat", "") if a.get("cat", "") in audit.CATEGORIES else "", "user": a.get("user", "").strip()[:64],
            "q": a.get("q", "").strip()[:200], "day_from": day(a.get("from", "")), "day_to": day(a.get("to", ""))}


@app.get("/audit")
def audit_page():
    f = _audit_filters()
    entries = audit_log.query(**f)
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    pages = max(1, (len(entries) + AUDIT_PAGE - 1) // AUDIT_PAGE)
    page = min(page, pages)
    args = {k: v for k, v in request.args.items() if k != "page" and v}
    return render_template("audit.html", entries=entries[(page - 1) * AUDIT_PAGE:page * AUDIT_PAGE], total=len(entries),
                           page=page, pages=pages, f=f, args=args, cats=audit.CATEGORIES, users=audit_log.users(),
                           keep=load_settings().get("audit_keep_days", "365"))


@app.get("/audit/export.csv")
def audit_export():
    f = _audit_filters()
    entries = audit_log.query(**f)
    audit_add("system", "Audit-Log exportiert", "CSV", detail=f"{len(entries)} Einträge")
    from flask import Response
    return Response(audit.to_csv(entries), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename=mirrorsync-audit-{time.strftime('%Y%m%d-%H%M')}.csv"})


@app.get("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.get("/")
def index():
    jobs = load_jobs()
    settings = load_settings()
    visible = {jid: j for jid, j in jobs.items() if g.access.job_ok(jid, j)}
    children = {}
    for jid, j in visible.items():
        if trigger_of(j) == "after" and j.get("after_job") in visible and j.get("after_job") != jid:
            children.setdefault(j["after_job"], []).append(jid)
    by_name = lambda jid: visible[jid]["name"].lower()
    roots = sorted((jid for jid in visible if not any(jid in c for c in children.values())), key=by_name)
    order, seen = [], set()

    def walk(jid, depth):
        if jid in seen:
            return
        seen.add(jid)
        order.append((jid, depth))
        for c in sorted(children.get(jid, []), key=by_name):
            walk(c, depth + 1)
    for r in roots:
        walk(r, 0)
    for jid in sorted(visible, key=by_name):   # Reste (z. B. Kreis aus alten Daten)
        walk(jid, 0)
    rows = []
    for job_id, depth in order:
        job = visible[job_id]
        trig = trigger_of(job)
        parent = jobs.get(job.get("after_job")) if trig == "after" else None
        rows.append(dict(job, id=job_id, eff_dest=effective_dest(job), running=job_id in _running, next_run=next_run(job_id),
                         n_excludes=len(exclude_list(job)), n_select=len(selection_list(job)), notify_summary=notify.describe(settings, job),
                         trig=trig, depth=min(depth, 4), parent_name=parent["name"] if parent else None,
                         followers=[visible[c]["name"] for c in sorted(children.get(job_id, []), key=by_name)],
                         schedule_text=cron_text(job.get("schedule", "")),
                         live_text=live_text(job) if trig == "live" else "", is_paused=is_paused(job),
                         pause_text=pause_text(job),
                         live_full_text=live_full_text(job) if trig == "live" else "",
                         direction="bisync" if is_bisync(job) else "mirror", **next_start_view(jobs, job_id)))
    return render_template("index.html", jobs=rows, auto_refresh=bool(_running))


# ---------------------------------------------------------------- Zeitplaene (Uebersicht aller Ausloeser)
def chain_layout(jobs, visible_ids):
    """Ketten als lineare Listen: [(root_id, [follower_ids in Reihenfolge])], Pool, verzweigt?"""
    vis = {j: jobs[j] for j in visible_ids}
    children = {}
    for jid, j in vis.items():
        if trigger_of(j) == "after" and j.get("after_job") in vis and j.get("after_job") != jid:
            children.setdefault(j["after_job"], []).append(jid)
    by_name = lambda jid: vis[jid]["name"].lower()
    chains, used, branched = [], set(), False
    for root in sorted((j for j in vis if trigger_of(vis[j]) != "after" and j in children), key=by_name):
        order, stack = [], sorted(children[root], key=by_name, reverse=True)
        if len(children[root]) > 1:
            branched = True
        while stack:
            c = stack.pop()
            if c in used or c == root:
                continue
            used.add(c)
            order.append(c)
            kids = sorted(children.get(c, []), key=by_name, reverse=True)
            branched |= len(kids) > 1
            stack.extend(kids)
        used.add(root)
        chains.append((root, order))
    pool = sorted((j for j in vis if j not in used), key=by_name)
    return chains, pool, branched


def schedules_data():
    jobs = load_jobs()
    visible = [jid for jid, j in jobs.items() if g.access.job_ok(jid, j)]
    chains, _, branched = chain_layout(jobs, visible)

    def info(jid):
        j = jobs[jid]
        return {"id": jid, "name": j["name"], "trigger": trigger_of(j), "schedule": j.get("schedule", ""),
                "enabled": bool(j.get("enabled")), "when": j.get("after_when", "ok"), "next_run": next_run(jid),
                "text": i18n.translate(cron_text(j.get("schedule", ""))), "running": jid in _running,
                "after_job": j.get("after_job", "") if trigger_of(j) == "after" else "",
                "parent_missing": trigger_of(j) == "after" and j.get("after_job") not in jobs,
                "status": j.get("last_status"), "path": f"{j['source']} ⇄ {effective_dest(j)}" if is_bisync(j) else f"{j['source']} → {effective_dest(j)}",
                "interval": live_interval(j), "full": j.get("live_full", LIVE_FULL_DEFAULT), "live_mode": live_mode(j), "direction": "bisync" if is_bisync(j) else "mirror",
                "live_text": i18n.translate(live_text(j)),
                "full_text": i18n.translate(live_full_text(j)) if trigger_of(j) == "live" else "",
                "live_checked": j.get("live_checked"), "next_live": next_run(jid + ":live"),
                "paused": is_paused(j), "pause_text": i18n.translate(pause_text(j)) if is_paused(j) else "", "pause_chain": j.get("pause_chain", "skip")}
    return {"jobs": {jid: info(jid) for jid in visible},
            "order": sorted(visible, key=lambda x: jobs[x]["name"].lower()),
            "chains": [{"root": r, "items": items} for r, items in chains],
            "branched": branched, "edit": g.access.has("jobs.edit"), "tz": TZ}


@app.get("/schedules")
def schedules():
    return render_template("schedules.html", data=schedules_data(), tz=TZ)


@app.get("/schedules/data")
def schedules_json():
    return schedules_data()


@app.post("/schedules/job/<job_id>")
def schedule_job(job_id):
    """Startart einer Aufgabe aendern (Uhrzeit / nach Aufgabe / manuell) – dieselben Daten wie im Aufgabenformular."""
    d = request.get_json(silent=True) or {}
    trig = d.get("trigger")
    if trig not in ("time", "after", "manual", "live"):
        return {"ok": False, "error": "Unbekannte Startart."}, 400
    with _lock:
        jobs = load_jobs()
        job = jobs.get(job_id) or abort(404)
        enabled = bool(d.get("enabled", True))
        if trig == "time":
            sched = (d.get("schedule") or job.get("schedule") or "0 3 * * *").strip()
            try:
                CronTrigger.from_crontab(sched, timezone=TZ)
            except ValueError as e:
                return {"ok": False, "error": f"Zeitplan ungültig: {e}"}, 400
            job.update(trigger="time", schedule=sched, after_job="", enabled=enabled)
        elif trig == "manual":
            job.update(trigger="manual", after_job="")
        elif trig == "live":
            iv, full, err = live_check(d.get("interval", job.get("live_interval") or 1),
                                       d.get("full", job.get("live_full", LIVE_FULL_DEFAULT)))
            if err:
                return {"ok": False, "error": err}, 400
            if trigger_of(job) != "live":
                job.pop("live_last", None)
            mode = d.get("mode", job.get("live_mode") or "mirror")
            if mode not in ("mirror", "fast"):
                return {"ok": False, "error": "Live-Modus: mirror oder fast."}, 400
            job.update(trigger="live", live_interval=iv, live_full=full, live_mode=mode, after_job="", enabled=enabled)
        else:
            parent = d.get("after_job", "")
            prob = chain_problem(jobs, job_id, parent)
            if not prob and not g.access.job_ok(parent, jobs.get(parent)):
                prob = "Diese Aufgabe darfst du nicht als Auslöser wählen."
            if prob:
                return {"ok": False, "error": prob}, 400
            if job.get("after_job") != parent or trigger_of(job) != "after":
                # direkt hinter "parent" einreihen: bisherige Nachfolger von parent laufen danach
                for cid, cj in jobs.items():
                    if cid != job_id and trigger_of(cj) == "after" and cj.get("after_job") == parent:
                        tail = job_id
                        while True:   # ans Ende der eigenen Kette haengen, damit nichts verloren geht
                            nxt = next((x for x, y in jobs.items() if trigger_of(y) == "after" and y.get("after_job") == tail
                                        and x != cid), None)
                            if not nxt:
                                break
                            tail = nxt
                        cj["after_job"] = tail
            job.update(trigger="after", after_job=parent, enabled=enabled,
                       after_when="always" if d.get("when") == "always" else job.get("after_when", "ok"))
        save_jobs(jobs)
    schedule_all()
    return {"ok": True}


@app.post("/schedules/chains")
def schedule_chains():
    data = request.get_json(silent=True) or {}
    with _lock:
        jobs = load_jobs()
        visible = {jid for jid, j in jobs.items() if g.access.job_ok(jid, j)}
        seen, plan = set(), {}
        for ch in data.get("chains", []):
            root = ch.get("root")
            items = [it for it in ch.get("items", []) if isinstance(it, dict)]
            if not items:
                continue
            ids = [root] + [it.get("id") for it in items]
            if any(i not in visible for i in ids):
                return {"ok": False, "error": "Unbekannte Aufgabe oder keine Berechtigung."}, 400
            if seen & set(ids) or len(set(ids)) != len(ids):
                return {"ok": False, "error": "Eine Aufgabe darf nur einmal vorkommen."}, 400
            if trigger_of(jobs[root]) == "after":
                return {"ok": False, "error": f"„{jobs[root]['name']}“ startet selbst nach einer Aufgabe und kann keine Kette beginnen."}, 400
            seen |= set(ids)
            prev = root
            for it in items:
                plan[it["id"]] = dict(trigger="after", after_job=prev, enabled=bool(it.get("enabled", True)),
                                      after_when="always" if it.get("when") == "always" else "ok")
                prev = it["id"]
        changed = []
        for jid in visible:
            j = jobs[jid]
            if jid in plan:
                new = plan[jid]
                if any(j.get(k) != v for k, v in new.items()) or trigger_of(j) != "after":
                    j.update(new)
                    changed.append(j["name"])
            elif trigger_of(j) == "after" and j.get("after_job") in visible:
                j.update(trigger="manual", after_job="")   # aus der Kette genommen
                changed.append(j["name"])
        save_jobs(jobs)
    schedule_all()
    return {"ok": True, "changed": changed}


DOW = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def cron_text(expr):
    """Einfache Cron-Ausdruecke in Klartext ('Mo–Fr 22:00'), sonst None."""
    m = re.match(r"^(\d{1,2}) (\d{1,2}) \* \* (\*|[0-7](?:[-,][0-7])*)$", (expr or "").strip())
    if not m:
        return None
    t = f"{int(m.group(2)):02d}:{int(m.group(1)):02d}"
    d = m.group(3)
    if d == "*":
        return f"täglich {t}"
    if d == "1-5":
        return f"Mo–Fr {t}"
    if d in ("0,6", "6,0", "6-7"):
        return f"Sa–So {t}"
    parts = []
    for p in d.split(","):
        a, _, b = p.partition("-")
        parts.append(i18n.translate(DOW[int(a)]) + (f"–{i18n.translate(DOW[int(b)])}" if b else ""))
    return ", ".join(parts) + f" {t}"


EMPTY_JOB = dict(name="", source="", dest="", schedule="0 3 * * *", enabled=True,
                 dry_run=False, versioning=False, versions_keep="", versions_days="", checksum=False, max_delete="500", extra_flags="",
                 excludes="", delete_excluded=False, notify_mode="global", notify_when="fail",
                 notify_webhook=False, notify_webhook_url="", notify_smtp=False, notify_smtp_to="",
                 notify_telegram=False, notify_telegram_chat_id="", notify_telegram_token="")


def job_notify_from_form(f, old=None):
    old = old or {}
    mode = f.get("notify_mode") if f.get("notify_mode") in ("global", "custom", "off") else "global"
    token = f.get("notify_telegram_token", "").strip() or old.get("notify_telegram_token", "")
    if f.get("notify_telegram_token_clear"):
        token = ""
    ap_urls = f.get("notify_apprise_urls", "").strip() or old.get("notify_apprise_urls", "")
    if f.get("notify_apprise_urls_clear"):
        ap_urls = ""
    return dict(
        notify_mode=mode, notify_when="always" if f.get("notify_when") == "always" else "fail",
        notify_webhook="notify_webhook" in f, notify_webhook_url=f.get("notify_webhook_url", "").strip(),
        notify_smtp="notify_smtp" in f, notify_smtp_to=f.get("notify_smtp_to", "").strip(),
        notify_telegram="notify_telegram" in f, notify_telegram_chat_id=f.get("notify_telegram_chat_id", "").strip(),
        notify_telegram_token=token,
        notify_apprise="notify_apprise" in f, notify_apprise_urls=ap_urls,
        notify_apprise_tag=f.get("notify_apprise_tag", "").strip(),
    )


def apply_job_form(f, job, old, job_id, jobs, api=False):
    """Formularfelder (GUI) bzw. API-Felder pruefen und in job uebernehmen. Liefert Fehlertext oder None."""
    error = None
    job.update(
        name=f.get("name", "").strip(), source=f.get("source", "").strip(),
        dest=f.get("dest", "").strip(), schedule=f.get("schedule", "").strip(),
        enabled="enabled" in f, dry_run="dry_run" in f, versioning="versioning" in f,
        versions_keep=str(f.get("versions_keep", "") or "").strip(), versions_days=str(f.get("versions_days", "") or "").strip(),
        checksum="checksum" in f, max_delete=f.get("max_delete", "").strip(),
        extra_flags=f.get("extra_flags", "").strip(),
        excludes=f.get("excludes", "").replace("\r\n", "\n").strip(),
        selection=f.get("selection", "").replace("\r\n", "\n").strip()[:20000],
        delete_excluded="delete_excluded" in f,
        include_source_dir="include_source_dir" in f and not has_selection({"selection": f.get("selection", "")}),
        trigger=f.get("trigger") if f.get("trigger") in ("time", "after", "manual", "live") else "time",
        direction="bisync" if f.get("direction") == "bisync" else "mirror",
        after_job=f.get("after_job", "").strip(), after_when="always" if f.get("after_when") == "always" else "ok",
    )
    if job["trigger"] != "time":
        job["schedule"] = old.get("schedule", "") if job_id else ""
    if job["trigger"] != "after":
        job["after_job"] = ""
    job["paused"] = "paused" in f
    pu = f.get("paused_until", "").strip()[:16]
    job["paused_until"] = pu if job["paused"] and re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", pu) else ""
    if job["paused"] and not old.get("paused"):
        job["paused_by"] = g.user or ""
    if not job["paused"]:
        job["paused_by"] = ""
    job["pause_chain"] = "stop" if f.get("pause_chain") == "stop" else "skip"
    twoway_err = None
    if job["direction"] == "bisync":
        job["delete_excluded"] = False
        job["bisync_conflict"] = f.get("bisync_conflict") if f.get("bisync_conflict") in BISYNC_CONFLICTS else "newer"
        md = str(f.get("bisync_max_delete", "") or "50").strip()
        if not md.isdigit() or not 1 <= int(md) <= 100:
            twoway_err = "Löschschutz: bitte 1 bis 100 Prozent angeben."
        job["bisync_max_delete"] = md
    if (job["direction"] == "bisync" or is_bisync(old)) and job["direction"] != old.get("direction", "mirror") \
            and not g.access.has("jobs.twoway"):
        twoway_err = "Dir fehlt das Recht „Zwei-Wege-Sync einrichten“."
    live_err = None
    if job["trigger"] == "live":
        job["live_interval"], job["live_full"], live_err = live_check(f.get("live_interval"), f.get("live_full"))
        job["live_mode"] = "fast" if f.get("live_mode") == "fast" else "mirror"
    live_reset_if_changed(old, job)
    bw_mode = f.get("bw_mode", "global")
    job["bw_mode"] = bw_mode if bw_mode in ("global", "custom", "off") else "global"
    bw_err = None
    if job["bw_mode"] == "custom":
        job["bw"], bw_err = bwlimit.clean(parse_bw(f.get("bw_json")))
    if g.access.has("jobs.notify") and (not api or "notify_mode" in f):
        job.update(job_notify_from_form(f, jobs.get(job_id)))
        if not api or "tpl_api" in f:
            job["msg_tpl_on"] = "msg_tpl_on" in f
            job["msg_tpl"] = msgtpl.form_templates(f, "jtpl_", msgtpl.JOB_EVENTS, load_settings().get("msg_templates"))
        job.pop("notify", None)
    vis_err = None
    if not api or "vis_mode" in f:
        vis, vis_err = vis_from_form(f)
        if vis == "all":
            job.pop("visible_to", None)
        else:
            job["visible_to"] = vis
    if not g.access.has("jobs.advanced"):
        job["extra_flags"] = old.get("extra_flags", "")
    if not job_id:
        job["owner"] = g.user
    if job["source"] and not job["selection"] and job["source"] != old.get("source") and g.access.path_ok(job["source"]):
        fs = split_file_source(job["source"])   # Quelle ist eine einzelne Datei -> Elternordner + Auswahl
        if fs:
            job["source"], job["selection"] = fs[0], fs[1]
    if job["selection"]:
        job["selection"] = "\n".join(selection_list(job))
    if not job["name"] or not job["source"] or not job["dest"]:
        error = "Name, Quelle und Ziel sind Pflichtfelder."
    elif bw_err:
        error = bw_err
    elif vis_err:
        error = vis_err
    elif any(job[x] and (not job[x].isdigit() or int(job[x]) > 100000) for x in ("versions_keep", "versions_days")):
        error = "Versionen behalten: Anzahl bzw. Tage als Zahl (leer = unbegrenzt)."
    elif not g.access.job_ok(job_id or "", job):
        error = "Mit dieser Auswahl unter „Sichtbar für“ würdest du die Aufgabe selbst nicht mehr sehen."
    elif live_err:
        error = live_err
    elif twoway_err:
        error = twoway_err
    elif not g.access.path_ok(job["source"]) or not g.access.path_ok(job["dest"]):
        error = "Deine Rolle darf diesen Speicherort bzw. lokale Ordner nicht verwenden."
    elif any(".." in x.strip().split("/") for x in f.get("selection", "").splitlines()):
        error = "Die Auswahl darf kein „..“ enthalten."
    elif job["include_source_dir"] and not source_basename(job["source"]):
        error = "„Quellordner selbst mitkopieren“ geht nicht, wenn die Quelle die oberste Ebene eines Speicherorts ist."
    elif job["source"].rstrip("/") == effective_dest(job).rstrip("/") or job["source"].rstrip("/") == job["dest"].rstrip("/"):
        error = "Quelle und Ziel dürfen nicht gleich sein."
    elif is_bisync(job) and (effective_dest(job).rstrip("/").startswith(job["source"].rstrip("/") + "/")
                             or job["source"].rstrip("/").startswith(effective_dest(job).rstrip("/") + "/")):
        error = "Beim Zwei-Wege-Sync darf eine Seite nicht in der anderen liegen."
    elif job["max_delete"] and not job["max_delete"].isdigit():
        error = "Max. Löschungen muss eine Zahl sein (oder leer)."
    elif job["trigger"] == "after" and (chain_problem(jobs, job_id, job["after_job"])
                                        or not g.access.job_ok(job["after_job"], jobs.get(job["after_job"]))):
        error = chain_problem(jobs, job_id, job["after_job"]) or "Diese Aufgabe darfst du nicht als Auslöser wählen."
    elif job["trigger"] == "time" and not job["schedule"]:
        error = "Bitte eine Uhrzeit bzw. einen Zeitplan angeben oder „Nur manuell“ wählen."
    elif job["trigger"] == "time":
        try:
            CronTrigger.from_crontab(job["schedule"], timezone=TZ)
        except ValueError as e:
            error = f"Zeitplan ungültig: {e}"
    if not error:
        try:
            shlex.split(job["extra_flags"])
        except ValueError as e:
            error = f"Zusätzliche Optionen ungültig: {e}"
    return error


@app.route("/job/new", methods=["GET", "POST"])
@app.route("/job/<job_id>", methods=["GET", "POST"])
def edit_job(job_id=None):
    jobs = load_jobs()
    if job_id and job_id not in jobs:
        abort(404)
    job = dict(jobs.get(job_id, EMPTY_JOB))
    if not job_id and request.method == "GET":   # aus dem Datei-Browser: "Als Quelle/Ziel verwenden"
        for k in ("source", "dest"):
            if request.args.get(k):
                job[k] = request.args[k][:500]
    old = dict(job)
    error = None
    if request.method == "POST":
        error = apply_job_form(request.form, job, old, job_id, jobs)
        if not error:
            with _lock:
                jobs = load_jobs()
                job_id = job_id or uuid.uuid4().hex[:8]
                jobs[job_id] = job
                save_jobs(jobs)
            schedule_all()
            return redirect(url_for("index"))
    remotes = [r for r in list_remotes() if g.access.remote_ok(r["name"])]
    settings = load_settings()
    job.update(notify.job_config(settings, job))
    has_token = bool(job.get("notify_telegram_token"))
    job["notify_telegram_token"] = ""   # Token nie ins Formular schreiben
    job_ap = notify.apprise_list(job.get("notify_apprise_urls"))
    job["notify_apprise_urls"] = ""
    job["apprise_saved"] = ", ".join(notify.mask_url(u) for u in job_ap)
    glob = {"when": settings.get("when"), "webhook": bool(settings.get("webhook_url")),
            "smtp": bool(settings.get("smtp_host")), "telegram": bool(settings.get("telegram_token")),
            "webhook_url": settings.get("webhook_url"), "smtp_to": settings.get("smtp_to"),
            "telegram_chat_id": settings.get("telegram_chat_id"),
            "apprise": bool(settings.get("apprise_enabled")), "apprise_tag": settings.get("apprise_tag", ""),
            "apprise_ready": bool(notify.apprise_list(settings.get("apprise_urls")) or (settings.get("apprise_mode") == "api" and settings.get("apprise_api_key"))),
            "summary": notify.describe(settings, {"notify_mode": "global"})}
    glob["bw"] = bwlimit.describe(settings.get("bw"), settings.get("bw_unit") or "MB/s")
    job["trigger"] = trigger_of(job) if job_id or request.method == "POST" else "time"
    job.setdefault("live_interval", 1)
    job["live_mode"] = live_mode(job)
    job["direction"] = "bisync" if is_bisync(job) else "mirror"
    if "live_full" not in job:
        job["live_full"] = LIVE_FULL_DEFAULT
    others = [{"id": jid, "name": j["name"], "trig": trigger_of(j),
               "loop": bool(job_id) and chain_problem(jobs, job_id, jid) is not None}
              for jid, j in sorted(jobs.items(), key=lambda kv: kv[1]["name"].lower())
              if jid != job_id and g.access.job_ok(jid, j)]
    followers = [j["name"] for jid, j in jobs.items() if job_id and trigger_of(j) == "after" and j.get("after_job") == job_id]
    jtpl = msgtpl.editor_data(msgtpl.JOB_EVENTS, job.get("msg_tpl"), settings.get("msg_templates"))
    return render_template("job.html", job=job, job_id=job_id, error=error, remotes=remotes, tz=TZ, jtpl=jtpl, vis_opts=vis_options(),
                           glob=glob, has_token=has_token, others=others, followers=followers, bw_cfg=job.get("bw") or settings.get("bw") or bwlimit.EMPTY)


def parse_bw(raw):
    try:
        data = json.loads(raw or "{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


@app.post("/job/notify-test")
@app.post("/job/<job_id>/notify-test")
def job_notify_test(job_id=None):
    """Testnachricht mit den (noch nicht gespeicherten) Einstellungen aus dem Formular."""
    old = load_jobs().get(job_id, {}) if job_id else {}
    cfg = job_notify_from_form(request.form, old)
    cfg["name"] = request.form.get("name") or "Test"
    when, eff = notify.effective(load_settings(), cfg)
    if when == "never":
        return {"ok": False, "results": {}, "error": "Benachrichtigungen sind für diese Aufgabe aus."}
    tj = {"msg_tpl_on": "msg_tpl_on" in request.form,
          "msg_tpl": msgtpl.form_templates(request.form, "jtpl_", msgtpl.JOB_EVENTS, load_settings().get("msg_templates"))}
    vals = {k: v for k, v in msgtpl.sample("run_ok").items() if k not in ("datum", "zeit", "version", "titel")}
    vals.update(job=cfg["name"], quelle=request.form.get("source", "-"), ziel=request.form.get("dest", "-"),
                testlauf=" (Test der Benachrichtigung)", gestartet_von=g.user or "")
    ev = notify.event(eff, "run_ok", vals, tj, status="test", ok=True, job=cfg["name"],
                      source=vals["quelle"], dest=vals["ziel"])
    results = notify.send(eff, ev)
    if not results:
        return {"ok": False, "results": {}, "error": "Kein Kanal aktiv."}
    return {"ok": all(v is None for v in results.values()), "results": results}


@app.post("/job/<job_id>/delete")
def delete_job(job_id):
    stop_job(job_id)
    with _lock:
        jobs = load_jobs()
        name = (jobs.pop(job_id, None) or {}).get("name")
        for j in jobs.values():   # Folgeaufgaben verlieren ihren Ausloeser
            if trigger_of(j) == "after" and j.get("after_job") == job_id:
                j.update(trigger="manual", after_job="")
        save_jobs(jobs)
    shutil.rmtree(os.path.join(LOG_DIR, job_id), ignore_errors=True)
    schedule_all()
    if name is not None and not getattr(g, "bridge", None):
        session["flash"] = i18n.t("Aufgabe „{0}“ entfernt.", name)
    return redirect(url_for("index"))


@app.post("/job/<job_id>/run")
def run_job(job_id):
    start_job(job_id, dry_run=request.form.get("dry") == "1", by=g.user or "Web", manual=True)
    return redirect(url_for("show_log", job_id=job_id))


_PCT_RE = re.compile(r"(\d{1,3})%")


def run_progress(log_path):
    """Letzte rclone-Statuszeile eines laufenden Logs: (Prozent, Kurztext)."""
    try:
        with open(log_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8192))
            tail = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return 0, ""
    for line in reversed(tail):
        if "ETA" in line and "%" in line:
            m = _PCT_RE.search(line)
            text = line.split("NOTICE:", 1)[-1].strip() if "NOTICE:" in line else line.strip()
            return (min(100, int(m.group(1))) if m else 0), text[:160]
    return 0, ""


def running_jobs_data():
    jobs = load_jobs()
    out = []
    for jid, run_id in list(_current_run.items()):
        j = jobs.get(jid)
        if not j or jid not in _running or not g.access.job_ok(jid, j):
            continue
        pc, stats = run_progress(run_log_path(jid, run_id))
        try:
            started = datetime.datetime.strptime(run_id[:15], "%Y%m%d-%H%M%S").strftime("%d.%m.%Y %H:%M:%S")
        except ValueError:
            started = run_id
        out.append({"id": jid, "name": j["name"], "run": run_id, "started": started, "progress": pc, "stats": stats,
                    "path": f"{j['source']} ⇄ {effective_dest(j)}" if is_bisync(j) else f"{j['source']} → {effective_dest(j)}",
                    "direction": "bisync" if is_bisync(j) else "mirror", "live": trigger_of(j) == "live"})
    return sorted(out, key=lambda x: x["name"].lower())


@app.get("/jobs/running")
def jobs_running():
    return {"ok": True, "jobs": running_jobs_data()}


@app.post("/job/<job_id>/resync")
def resync_job(job_id):
    """Zwei-Wege-Sync neu zusammenfuehren (--resync), z. B. nach einem Abbruch."""
    job = load_jobs().get(job_id) or abort(404)
    if not is_bisync(job):
        abort(400)
    ok = start_job(job_id, dry_run=request.form.get("dry") == "1", by=g.user or "Web", manual=True, resync=True)
    if ok:
        update_job(job_id, bisync_need_resync=False)
    return redirect(url_for("show_log", job_id=job_id))


@app.post("/job/<job_id>/pause")
def job_pause(job_id):
    """Pausieren (dauerhaft, fuer X Stunden oder bis Datum) oder fortsetzen."""
    f = request.form
    with _lock:
        jobs = load_jobs()
        job = jobs.get(job_id) or abort(404)
        if f.get("action") == "resume":
            job.update(paused=False, paused_until="", paused_by="")
        else:
            until = ""
            if f.get("hours", "").strip().isdigit() and int(f["hours"]) > 0:
                until = (datetime.datetime.now() + datetime.timedelta(hours=int(f["hours"]))).strftime("%Y-%m-%dT%H:%M")
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", f.get("until", "")):
                until = f["until"]
            if until and until <= datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"):
                until = ""
            job.update(paused=True, paused_until=until, paused_by=g.user or "")
        save_jobs(jobs)
    schedule_all()
    back = f.get("back", "")
    return redirect(back if back.startswith("/") and not back.startswith("//") else url_for("index"))


@app.post("/job/<job_id>/stop")
def stop(job_id):
    stop_job(job_id)
    return redirect(url_for("show_log", job_id=job_id))


@app.get("/job/<job_id>/log")
def show_log(job_id):
    """Uebersicht aller gespeicherten Laeufe einer Aufgabe; zeigt den neuesten bzw. laufenden Lauf."""
    job = load_jobs().get(job_id) or abort(404)
    running = job_id in _running
    hist = job.get("history", [])
    current = _current_run.get(job_id) or (hist[0].get("run") if hist else None)
    text = "Noch kein Lauf."
    if current and os.path.exists(run_log_path(job_id, current)):
        path = run_log_path(job_id, current)
        with open(path, encoding="utf-8", errors="replace") as f:
            f.seek(max(0, os.path.getsize(path) - 100_000))
            text = f.read()
        # Hinweiszeilen einzeln uebersetzen (der ganze Text passt auf kein Muster)
        text = "".join(i18n.translate(ln) if ln.startswith("===") else ln for ln in text.splitlines(True))
    runs, days = keep_limits()
    job = dict(job, dest=effective_dest(job))
    return render_template("log.html", job=job, job_id=job_id, log=text, current=current,
                           running=running, auto_refresh=running, keep_runs=runs, keep_days=days,
                           has_file={h.get("run"): bool(h.get("run")) and os.path.exists(run_log_path(job_id, h["run"]))
                                     for h in hist})


LOG_FILTERS = {"all": "Alle", "error": "Fehler", "copied": "Kopiert", "deleted": "Gelöscht", "notice": "Hinweise"}
MAX_LINES = 5000


@app.get("/job/<job_id>/run/<run_id>")
def show_run(job_id, run_id):
    job = load_jobs().get(job_id) or abort(404)
    if not RUN_ID_RE.match(run_id) or not os.path.exists(run_log_path(job_id, run_id)):
        abort(404)
    flt = request.args.get("f", "all") if request.args.get("f") in LOG_FILTERS else "all"
    q = request.args.get("q", "").strip()
    counts = {k: 0 for k in LOG_FILTERS}
    lines, total = [], 0
    with open(run_log_path(job_id, run_id), encoding="utf-8", errors="replace") as f:
        for line in f:
            kind = notify.classify(line)
            counts["all"] += 1
            if kind in counts:
                counts[kind] += 1
            if (flt == "all" or kind == flt) and (not q or q.lower() in line.lower()):
                total += 1
                lines.append((kind, line.rstrip("\n")))
                if len(lines) > MAX_LINES:
                    lines.pop(0)
    entry = next((h for h in job.get("history", []) if h.get("run") == run_id), None)
    live = _current_run.get(job_id) == run_id
    return render_template("run.html", job=dict(job, dest=effective_dest(job)), job_id=job_id, run_id=run_id,
                           entry=entry, lines=lines, total=total, counts=counts, flt=flt, q=q, filters=LOG_FILTERS,
                           live=live, auto_refresh=live and not q, max_lines=MAX_LINES)


@app.get("/job/<job_id>/run/<run_id>/download")
def download_run(job_id, run_id):
    job = load_jobs().get(job_id) or abort(404)
    if not RUN_ID_RE.match(run_id) or not os.path.exists(run_log_path(job_id, run_id)):
        abort(404)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", job["name"]) or job_id
    return send_file(run_log_path(job_id, run_id), mimetype="text/plain", as_attachment=True,
                     download_name=f"mirrorsync_{safe}_{run_id}.log")


# ---------------------------------------------------------------- Remotes
# Haeufige Speicherarten zuerst, mit deutschem Namen. Alle anderen rclone-Typen folgen danach.
COMMON_TYPES = [
    ("smb", "SMB / Windows-Freigabe / NAS"), ("webdav", "WebDAV (Nextcloud, ownCloud, …)"),
    ("sftp", "SFTP / SSH"), ("ftp", "FTP / FTPS"), ("s3", "S3 und S3-kompatibel (AWS, MinIO, Wasabi, …)"),
    ("b2", "Backblaze B2"), ("azureblob", "Azure Blob Storage"), ("drive", "Google Drive"),
    ("onedrive", "Microsoft OneDrive / SharePoint"), ("dropbox", "Dropbox"), ("pcloud", "pCloud"),
    ("mega", "MEGA"), ("crypt", "Verschlüsselung (crypt, legt sich über einen anderen Speicherort)"),
]
SKIP_TYPES = {"memory", "local", "cache", "tardigrade", "uptobox"}
_providers = None


def providers():
    """Alle rclone-Speicherarten mit ihren Optionen (aus 'rclone config providers')."""
    global _providers
    if _providers is None:
        rc, out = rclone("config", "providers", timeout=30)
        data = json.loads(out) if rc == 0 else []
        labels = dict(COMMON_TYPES)
        order = {t: i for i, (t, _) in enumerate(COMMON_TYPES)}
        res = []
        for p in data:
            if p.get("Hide") or p["Name"] in SKIP_TYPES:
                continue
            opts = [{k: o.get(k) for k in ("Name", "Help", "Provider", "DefaultStr", "Examples", "Required",
                                           "IsPassword", "Sensitive", "Advanced", "Exclusive", "Type")}
                    for o in p.get("Options", []) if not o.get("Hide") and o["Name"] != "token"]
            res.append({"name": p["Name"], "label": labels.get(p["Name"], p["Description"]),
                        "common": p["Name"] in order, "oauth": any(o["Name"] == "token" for o in p.get("Options", [])),
                        "options": opts})
        res.sort(key=lambda p: (order.get(p["name"], 999), p["name"]))
        _providers = res
    return _providers


def providers_tr():
    """providers() mit Bezeichnungen in der Sprache der Anfrage (fuer die GUI)."""
    return [dict(p, label=i18n.t(p["label"])) for p in providers()]


def list_remotes():
    rc, out = rclone("listremotes", "--long", timeout=15)
    if rc != 0:
        return []
    res = []
    for line in out.splitlines():
        if ":" in line:
            name, typ = line.split(":", 1)
            res.append({"name": name.strip(), "type": typ.strip()})
    return res


def remote_config(name):
    rc, out = rclone("config", "dump", timeout=15)
    try:
        return json.loads(out).get(name) if rc == 0 else None
    except ValueError:
        return None


def _config_step(args):
    """Ein Schritt im Einrichtungs-Dialog von rclone. Liefert (frage|None, fehler|None)."""
    rc, out = rclone(*args, "--non-interactive", timeout=60)
    if rc != 0:
        return None, out
    try:
        res = json.loads(out[out.index("{"):]) if "{" in out else {}
    except ValueError:
        return None, None
    if res.get("Error"):
        # rclone stellt die Frage nach einem Fehler erneut, Fehler mit anzeigen
        return (res if res.get("State") else None), res["Error"]
    return (res if res.get("State") else None), None


_pending = {}  # remote-name -> offene Frage aus dem Einrichtungs-Dialog


def _after_step(name, question, err, done_msg):
    if question:
        # Browser-Anmeldung im Container ist nicht moeglich -> automatisch "nein" (Token einfuegen)
        if question["Option"]["Name"] == "config_is_local":
            q2, err2 = _config_step(["config", "update", name, "--continue",
                                     "--state", question["State"], "--result", "false"])
            return _after_step(name, q2, err2, done_msg)
        _pending[name] = question
        return redirect(url_for("remote_wizard", name=name, err=err or ""))
    _pending.pop(name, None)
    if err:
        return render_remotes(err=err)
    return render_remotes(msg=done_msg)


def _safe(conf):
    """Gespeicherte Werte fuers Formular, ohne Passwoerter und Tokens."""
    if not conf:
        return None
    prov = next((p for p in providers() if p["name"] == conf.get("type")), {"options": []})
    secret = {o["Name"] for o in prov["options"] if o["IsPassword"]} | {"token"}
    return {k: v for k, v in conf.items() if k not in secret}


def render_remotes(msg=None, err=None):
    oauth = {p["name"] for p in providers() if p["oauth"]}
    rc, out = rclone("config", "dump", timeout=15)
    try:
        dump = json.loads(out) if rc == 0 else {}
    except ValueError:
        dump = {}
    rows = [dict(r, oauth=r["type"] in oauth, no_token=r["type"] in oauth and not dump.get(r["name"], {}).get("token"))
            for r in list_remotes() if g.access.remote_ok(r["name"])]
    return render_template("remotes.html", remotes=rows, msg=msg, err=err)


@app.post("/remotes/<name>/auth")
def auth_remote(name):
    """Browser-Anmeldung (OAuth) neu starten, z. B. wenn abgebrochen oder abgelaufen."""
    q, err = _config_step(["config", "update", name])
    return _after_step(name, q, err, f"Anmeldung für '{name}' abgeschlossen.")


@app.get("/remotes")
def remotes():
    return render_remotes()


@app.route("/remotes/new", methods=["GET", "POST"])
@app.route("/remotes/<name>/edit", methods=["GET", "POST"])
def edit_remote(name=None):
    existing = remote_config(name) if name else None
    if name and existing is None:
        abort(404)
    if request.method == "POST":
        f = request.form
        new_name = name or f.get("name", "").strip()
        typ = existing["type"] if existing else f.get("type", "")
        err = None
        if not new_name or not new_name.replace("-", "").replace("_", "").isalnum():
            err = "Name nur aus Buchstaben, Ziffern, - und _."
        elif not name and any(r["name"] == new_name for r in list_remotes()):
            err = f"Ein Speicherort '{new_name}' existiert schon."
        elif not name and typ not in {p["name"] for p in providers()}:
            err = "Unbekannter Typ."
        vis, vis_err = vis_from_form(f) if (g.access.has("remotes.edit") or not name) else (remote_vis_map().get(name, "all"), None)
        if not err and vis_err:
            err = vis_err
        if not err and not g.access.admin and not roles.visible(None if vis == "all" else vis, g.access.principals):
            err = "Mit dieser Auswahl unter „Sichtbar für“ würdest du den Speicherort selbst nicht mehr sehen."
        if err:
            return render_template("remote_edit.html", name=name, existing=_safe(existing), err=err,
                                   providers=providers_tr(), form=f, vis=vis, vis_opts=vis_options())
        meta = DB.get_map("remote_meta")
        if vis == "all":
            meta.pop(new_name, None)
        else:
            meta[new_name] = dict(meta.get(new_name) or {}, visible_to=vis)
        DB.put_map("remote_meta", meta)
        params = []
        for key, val in f.items():
            if key.startswith("opt_") and val.strip() != "":
                params.append(f"{key[4:]}={val.strip()}")
        if name:
            q, err = _config_step(["config", "update", name, *params, "--obscure"])
        else:
            q, err = _config_step(["config", "create", new_name, typ, *params, "--obscure"])
        return _after_step(new_name, q, err, f"Speicherort '{new_name}' gespeichert. Jetzt mit „Testen“ prüfen.")
    return render_template("remote_edit.html", name=name, existing=_safe(existing), err=None,
                           providers=providers_tr(), form={}, vis=remote_vis_map().get(name, "all") if name else "all",
                           vis_opts=vis_options())


@app.route("/remotes/<name>/wizard", methods=["GET", "POST"])
def remote_wizard(name):
    q = _pending.get(name)
    if not q:
        return redirect(url_for("remotes"))
    if request.method == "POST":
        q2, err = _config_step(["config", "update", name, "--continue", "--state", q["State"],
                                "--result", request.form.get("result", "").strip()])
        return _after_step(name, q2, err, f"Speicherort '{name}' fertig eingerichtet. Jetzt mit „Testen“ prüfen.")
    typ = (remote_config(name) or {}).get("type", "")
    return render_template("remote_wizard.html", name=name, q=q["Option"], typ=typ, err=request.args.get("err"))


@app.post("/remotes/<name>/test")
def test_remote(name):
    rc, out = rclone("lsf", f"{name}:", "--max-depth", "1", "--dirs-only", timeout=30)
    if rc == 0:
        return render_remotes(msg=f"Verbindung zu '{name}' OK. Ordner:\n{out or '(leer)'}")
    return render_remotes(err=f"Verbindung zu '{name}' fehlgeschlagen:\n{out}")


@app.post("/remotes/<name>/delete")
def delete_remote(name):
    rclone("config", "delete", name)
    _pending.pop(name, None)
    meta = DB.get_map("remote_meta")
    if meta.pop(name, None) is not None:
        DB.put_map("remote_meta", meta)
    return redirect(url_for("remotes"))


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    s = load_settings()
    msg = err = None
    if request.method == "POST":
        f = request.form
        for key, default in notify.DEFAULTS.items():
            if isinstance(default, bool):
                s[key] = key in f
            elif key in notify.SECRET_FIELDS:
                if f.get(key, "").strip():   # leer = unveraendert
                    s[key] = f[key].strip()
                if f.get(key + "_clear"):
                    s[key] = ""
            elif key in f:
                s[key] = f.get(key, "").strip()
        if s["when"] not in ("always", "fail", "never"):
            s["when"] = "fail"
        if s.get("apprise_mode") not in ("lib", "api"):
            s["apprise_mode"] = "lib"
        if "tpl_present" in f:
            s["msg_templates"] = msgtpl.form_templates(f, "tpl_", list(msgtpl.EVENTS))
            s["webhook_body"] = f.get("webhook_body", "").replace("\r\n", "\n").strip()[:8000]
        err = msgtpl.check_webhook_body(s.get("webhook_body"))
        if err:
            old_s = load_settings()
            s["webhook_body"] = old_s.get("webhook_body", "")   # Rest speichern, ungueltige Vorlage nicht
        save_settings(s)
        test = f.get("test")
        if err:
            pass
        elif test in notify.CHANNELS:
            ev = notify.event(s, "test", {"job": "Test"}, status="test", ok=True, job="Test", source="-", dest="-")
            res = notify.send(s, ev, only=test)[test]
            msg, err = (f"Testnachricht über {test} gesendet.", None) if res is None else (None, f"{test}: {res}")
        else:
            msg = "Einstellungen gespeichert."
    view = {k: ("" if k in notify.SECRET_FIELDS else v) for k, v in s.items()}
    has_secret = {k: bool(s.get(k)) for k in notify.SECRET_FIELDS}
    ap_saved = [notify.mask_url(u) for u in notify.apprise_list(s.get("apprise_urls"))]
    try:
        import apprise as _ap   # noqa: F401
        ap_lib = True
    except ImportError:
        ap_lib = False
    tpl_data = msgtpl.editor_data(list(msgtpl.EVENTS), s.get("msg_templates"))
    if err and request.method == "POST":   # Eingaben nicht verlieren
        view["webhook_body"] = request.form.get("webhook_body", "")
    wh_sample = dict(msgtpl.sample("run_fail"), titel="❌ MirrorSync: NAS → Docker – FEHLER", ereignis="run_fail", ok="false")
    wh_sample["nachricht"] = msgtpl.make({}, "run_fail", wh_sample)[1]
    return render_template("settings.html", s=view, has_secret=has_secret, msg=msg, err=err, ap_saved=ap_saved, ap_lib=ap_lib,
                           tpl_data=tpl_data, wh_sample=wh_sample)


@app.route("/settings/general", methods=["GET", "POST"])
def general_settings():
    s = load_settings()
    msg = err = None
    if request.method == "POST" and request.form.get("section") == "security":
        f = request.form
        a, m = f.get("lock_attempts", "").strip(), f.get("lock_minutes", "").strip()
        if not a.isdigit() or int(a) > 100 or not m.isdigit() or int(m) > 525600:
            err = "Sperre: Anzahl 0 bis 100, Dauer 0 bis 525600 Minuten."
        else:
            s.update(lock_attempts=str(int(a)), lock_minutes=str(int(m)), lock_notify=f.get("fail_notify") in ("lock", "every"),
                     fail_notify=f.get("fail_notify") if f.get("fail_notify") in ("off", "lock", "every") else "lock",
                     fail_notify_minutes=str(max(1, min(1440, int(f.get("fail_notify_minutes") or 15)))) if (f.get("fail_notify_minutes") or "15").isdigit() else "15",
                     trust_proxy="trust_proxy" in f, geoip_auto="geoip_auto" in f,
                     geoip_days=f.get("geoip_days") if f.get("geoip_days", "").isdigit() and int(f["geoip_days"]) in geoip.INTERVALS else (s.get("geoip_days") or "30"),
                     public_url=f.get("public_url", "").strip().rstrip("/")[:200])
            s["geoip_mode"] = "schedule" if f.get("geoip_mode") == "schedule" else "interval"
            if s["geoip_mode"] == "schedule" or f.get("geoip_time") or f.getlist("geoip_dow"):
                dows = [x for v in f.getlist("geoip_dow") for x in v.split(",")]
                s["geoip_time"], s["geoip_dow"], gerr = geoip_clean_schedule(f.get("geoip_time") or s.get("geoip_time"), dows or (s.get("geoip_dow") or "mon").split(","))
                if gerr and s["geoip_mode"] == "schedule":
                    err = gerr
        if not err:
            save_settings(s)
            schedule_all()
            msg = "Sicherheitseinstellungen gespeichert."
            if f.get("geoip_now"):
                e = geoip.update(force=True)
                msg, err = (msg + " GeoIP-Datenbank aktualisiert.", None) if not e else (msg, "GeoIP-Download fehlgeschlagen: " + e)
    elif request.method == "POST" and request.form.get("section") == "lang":
        lang = request.form.get("language", "")
        if not i18n.valid(lang):
            err = "Unbekannte Sprache."
        else:
            s["language"] = lang
            save_settings(s)
            i18n.default_lang = lang
            msg = "Standardsprache gespeichert."
    elif request.method == "POST" and request.form.get("section") == "update":
        s["update_check"] = "update_check" in request.form
        iv = (request.form.get("update_interval_value") or "").strip()
        if iv:
            try:
                mins = int(iv) * (60 if request.form.get("update_interval_unit") == "h" else 1)
            except ValueError:
                mins = -1
            if not update.MIN_MINUTES <= mins <= update.MAX_MINUTES:
                err = "Abstand: 5 Minuten bis 720 Stunden (30 Tage)."
            else:
                s["update_interval"] = str(mins)
        if not err:
            save_settings(s)
            msg = "Gespeichert."
        if not err and request.form.get("check_now"):
            st = update.check()
            msg = (i18n.t("Prüfung fehlgeschlagen: {0}", st["error"]) if st.get("error") else
                   i18n.t("Neue Version {0} verfügbar.", st["latest"]) if update.newer(st.get("latest"), VERSION) else
                   i18n.t("MirrorSync ist aktuell ({0}).", VERSION))
    elif request.method == "POST" and request.form.get("section") == "bw":
        cfg, err = bwlimit.clean(parse_bw(request.form.get("bw_json")))
        if not err:
            s["bw"] = cfg
            if request.form.get("bw_unit") in bwlimit.UNITS:
                s["bw_unit"] = request.form["bw_unit"]
            save_settings(s)
            msg = "Bandbreite gespeichert. Gilt ab dem nächsten Lauf."
    elif request.method == "POST":
        vals = {}
        for key, lo, hi in (("log_keep_runs", 1, 1000), ("log_keep_days", 0, 3650), ("audit_keep_days", 0, 3650)):
            v = request.form.get(key, "").strip()
            if not v.isdigit() or not lo <= int(v) <= hi:
                err = f"Bitte eine Zahl von {lo} bis {hi} eintragen."
                break
            vals[key] = str(int(v))
        if not err:
            s.update(vals)
            save_settings(s)
            with _lock:
                for jid in load_jobs():
                    cleanup_logs(jid)
            audit_log.keep_days = int(vals["audit_keep_days"])
            audit_log.prune()
            msg = "Gespeichert. Ältere Logs wurden aufgeräumt."
    usage = 0
    for root, _, files in os.walk(LOG_DIR):
        usage += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    bw = s.get("bw") or bwlimit.EMPTY
    pk_rp_id, _, _pk_prob = _pk_rp()
    return render_template("general.html", s=s, msg=msg, err=err, usage=usage, bw_cfg=bw, geo=geoip.status(), pk_now=pk_rp_id,
                           attribution=Markup(geoip.ATTRIBUTION), my_ip=_client_ip(), my_loc=geoip.locate(_client_ip()),
                           next_geoip=next_run("_geoip"), tz=TZ, upd=update_status(),
                           fwd=request.headers.get("X-Forwarded-For", ""),
                           bw_desc=bwlimit.describe(bw, s.get("bw_unit") or "MB/s"), bw_tt=bwlimit.timetable(bw))


COUNTRY_CHOICES = [("DE", "Deutschland"), ("AT", "Österreich"), ("CH", "Schweiz"), ("NL", "Niederlande"), ("BE", "Belgien"),
                   ("LU", "Luxemburg"), ("FR", "Frankreich"), ("IT", "Italien"), ("ES", "Spanien"), ("PL", "Polen"),
                   ("CZ", "Tschechien"), ("DK", "Dänemark"), ("SE", "Schweden"), ("NO", "Norwegen"), ("FI", "Finnland"),
                   ("GB", "Vereinigtes Königreich"), ("IE", "Irland"), ("PT", "Portugal"), ("US", "USA"), ("CA", "Kanada"),
                   ("RU", "Russland"), ("CN", "China"), ("IN", "Indien"), ("BR", "Brasilien"), ("KP", "Nordkorea"), ("IR", "Iran")]


def _access_page(cfg, msg=None, err=None, form_cfg=None):
    guard.prune()
    ip = _client_ip()
    view = form_cfg or cfg
    rows = []
    for e in cfg.get("block", []):
        n, last = guard.hits.get(e["net"], (0, ""))
        host = ipguard.parse_host(e.get("net", ""))
        rows.append(dict(e, hits=n, last=last, active=ipguard.active_block(e), is_host=bool(host),
                         ips=sorted(str(x) for x in ipguard.resolve(host)[0]) if host else []))
    hosts = []
    for x in view.get("allow", []):
        host = ipguard.parse_host(x)
        if host:
            ips, herr = ipguard.resolve(host)
            hosts.append({"host": host, "ips": sorted(str(i) for i in ips), "err": herr})
    return render_template("access.html", cfg=view, rows=rows, hosts=hosts, msg=msg, err=err, my_ip=ip, my_loc=geoip.locate(ip),
                           my_verdict=guard.check(ip, _country_iso, view), geo=geoip.status(), off=IPGUARD_OFF,
                           trust_proxy=load_settings().get("trust_proxy"), fwd=request.headers.get("X-Forwarded-For", ""),
                           countries=COUNTRY_CHOICES, rule_hits={k: v for k, v in guard.hits.items()})


# ---------------------------------------------------------------- Sicherung: Export / Import
IMPORT_DIR = os.path.join(CONFIG_DIR, "import-pending")
BACKUP_LABELS = {"job": "Aufgaben", "user": "Benutzer", "role": "Rollen", "settings": "Einstellungen",
                 "ipguard": "IP- und Länderregeln", "apikey": "API-Keys", "group": "Gruppen", "remote_meta": "Sichtbarkeit der Speicherorte", "login_log": "Anmeldeverlauf", "audit": "Audit-Log"}
UPLOAD_MAX = 1024 * 1024 * 1024


def _admin_only():
    if g.role != "admin":
        return render_template("denied.html", perm="nur Admins: Export und Import"), 403
    return None


def _pending_cleanup():
    if not os.path.isdir(IMPORT_DIR):
        return
    for f in os.listdir(IMPORT_DIR):
        p = os.path.join(IMPORT_DIR, f)
        try:
            if time.time() - os.path.getmtime(p) > 3600:
                os.remove(p)
        except OSError:
            pass


def _pending_path():
    tok = (session.get("import") or {}).get("t", "")
    if not re.match(r"^[a-f0-9]{32}$", tok):
        return None
    p = os.path.join(IMPORT_DIR, tok + ".zip")
    return p if os.path.exists(p) else None


@app.route("/settings/backup")
def backup_page(preview=None, err=None):
    deny = _admin_only()
    if deny:
        return deny
    _pending_cleanup()
    return render_template("backup.html", msg=session.pop("flash", None), err=err, preview=preview,
                           counts=DB.counts(), labels=BACKUP_LABELS, backups=_backups(),
                           ab=_autobackup_view(), cron_presets=AB_PRESETS,
                           crypto=backup.CRYPTO, files=backup._config_files(CONFIG_DIR),
                           db_info={"path": DB.path, "size": os.path.getsize(DB.path), "migrated": DB.meta("migrated_at"),
                                    "from": DB.meta("migrated_from")})


@app.post("/settings/backup/export")
def backup_export():
    deny = _admin_only()
    if deny:
        return deny
    f = request.form
    pw, pw2 = f.get("password", ""), f.get("password2", "")
    if pw != pw2:
        return backup_page(err="Die Passwörter stimmen nicht überein.")
    if pw and len(pw) < 8:
        return backup_page(err="Das Passwort für den Export braucht mindestens 8 Zeichen.")
    if pw and not backup.CRYPTO:
        return backup_page(err="Verschlüsselung ist in diesem Image nicht verfügbar.")
    raw, man = backup.build(DB, CONFIG_DIR, VERSION, LOG_DIR, include_logs=bool(f.get("logs")))
    name = f"mirrorsync-export-{VERSION}-{time.strftime('%Y%m%d-%H%M')}.zip"
    if pw:
        raw, name = backup.encrypt(raw, pw), name + ".enc"
    audit_add("system", "exportiert", "Gesamter Stand",
              detail=("verschlüsselt" if pw else "UNVERSCHLÜSSELT") + (f", mit {man['logs']} Log-Dateien" if man["logs"] else ""))
    import io as _io
    return send_file(_io.BytesIO(raw), as_attachment=True, download_name=name,
                     mimetype="application/octet-stream" if pw else "application/zip")


@app.post("/settings/backup/import")
def backup_import():
    deny = _admin_only()
    if deny:
        return deny
    if (request.content_length or 0) > UPLOAD_MAX:
        return backup_page(err="Die Datei ist größer als 1 GB.")
    up = request.files.get("file")
    if not up or not up.filename:
        return backup_page(err="Bitte eine Exportdatei auswählen.")
    return _stage_import(up.read(UPLOAD_MAX + 1), up.filename)


def _stage_import(blob, filename, password=None):
    """Importdatei pruefen, zwischenspeichern und die Vorschau zeigen."""
    if password is None:
        password = request.form.get("password", "")
    try:
        raw = backup.decrypt(blob, password) if backup.is_encrypted(blob) else blob
        parsed = backup.read(raw)
    except backup.BackupError as e:
        return backup_page(err=str(e))
    os.makedirs(IMPORT_DIR, exist_ok=True)
    os.chmod(IMPORT_DIR, 0o700)
    tok = secrets.token_hex(16)
    path = os.path.join(IMPORT_DIR, tok + ".zip")
    with open(path, "wb") as fh:
        fh.write(raw)
    os.chmod(path, 0o600)
    old = _pending_path()
    if old:
        try:
            os.remove(old)
        except OSError:
            pass
    session["import"] = {"t": tok, "name": filename[:120], "enc": backup.is_encrypted(blob)}
    ok, notes = backup.check(parsed, VERSION)
    return backup_page(preview={"m": parsed["manifest"], "counts": {k: len(v) for k, v in parsed["data"].items()
                                                                     if k in BACKUP_LABELS},
                                "files": sorted(parsed["files"]), "logs": len(parsed["logs"]), "ok": ok,
                                "notes": notes, "name": filename, "enc": backup.is_encrypted(blob)})


@app.post("/settings/backup/apply")
def backup_apply():
    deny = _admin_only()
    if deny:
        return deny
    path = _pending_path()
    if request.form.get("cancel") or not path:
        if path:
            os.remove(path)
        session.pop("import", None)
        if request.form.get("cancel"):
            session["flash"] = "Import abgebrochen."
        else:
            _flash_err("Keine Importdatei mehr vorhanden, bitte erneut hochladen.")
        return redirect(url_for("backup_page"))
    if not request.form.get("confirm"):
        return backup_page(err="Bitte bestätigen, dass der aktuelle Stand ersetzt werden soll.")
    with open(path, "rb") as fh:
        parsed = backup.read(fh.read())
    ok, notes = backup.check(parsed, VERSION)
    if not ok:
        return backup_page(err=" ".join(notes))
    me, imp = g.user, session.get("import") or {}
    if _running:
        return backup_page(err="Während Aufgaben laufen, ist kein Import möglich. Bitte warten oder stoppen.")
    try:
        bk = backup.auto_backup(DB, CONFIG_DIR, VERSION)
        with _lock:
            n_files = backup.apply(DB, CONFIG_DIR, LOG_DIR, parsed, with_files=bool(request.form.get("files")),
                                   with_logs=bool(request.form.get("logs")))
    except Exception as e:
        return backup_page(err=f"Import fehlgeschlagen, der bisherige Stand ist unverändert: {e}")
    os.remove(path)
    session.pop("import", None)
    m = parsed["manifest"]
    audit_add("system", "importiert", imp.get("name", "Exportdatei"), user=me,
              detail=f"aus Version {m.get('version')} vom {m.get('created')}, {n_files} Dateien, "
                     f"vorher gesichert: config/backups/{os.path.basename(bk)}")
    schedule_all()
    session["flash"] = (f"Import abgeschlossen. Der vorherige Stand liegt als Sicherung in config/backups/{os.path.basename(bk)}. "
                        "Falls du jetzt abgemeldet wirst: mit einem Benutzer aus der importierten Datei anmelden.")
    return redirect(url_for("backup_page"))


def _backups():
    return backup.list_backups(CONFIG_DIR, backup.auto_dir(CONFIG_DIR, load_settings()))


def _backup_by_name(name):
    return next((b for b in _backups() if b["name"] == name), None)


@app.get("/settings/backup/file/<name>")
def backup_download(name):
    deny = _admin_only()
    if deny:
        return deny
    b = _backup_by_name(name)
    if not b:
        abort(404)
    audit_add("system", "Sicherung heruntergeladen", name)
    return send_file(b["path"], as_attachment=True, download_name=name)


@app.post("/settings/backup/file/<name>/delete")
def backup_delete(name):
    deny = _admin_only()
    if deny:
        return deny
    b = _backup_by_name(name)
    if b:
        os.remove(b["path"])
        audit_add("system", "Sicherung gelöscht", name)
        session["flash"] = f"Sicherung {name} gelöscht."
    return redirect(url_for("backup_page"))


@app.post("/settings/backup/file/<name>/restore")
def backup_restore(name):
    """Gespeicherte Sicherung pruefen und wie eine hochgeladene Datei in die Import-Vorschau legen."""
    deny = _admin_only()
    if deny:
        return deny
    b = _backup_by_name(name)
    if not b:
        abort(404)
    with open(b["path"], "rb") as fh:
        blob = fh.read(UPLOAD_MAX + 1)
    pw = request.form.get("password", "") or (load_settings().get("autobackup_password") or "")
    return _stage_import(blob, name, password=pw)


# ---------------------------------------------------------------- automatische Sicherung
AB_PRESETS = [("0 3 * * *", "täglich um 3:00"), ("0 */6 * * *", "alle 6 Stunden"), ("0 * * * *", "stündlich"),
              ("0 3 * * 0", "sonntags um 3:00"), ("0 3 1 * *", "am 1. jedes Monats um 3:00")]
_ab_lock = threading.Lock()


def _size(n):
    n = int(n or 0)
    return f"{n} B" if n < 1024 else f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def _autobackup_view():
    st = load_settings()
    try:
        status = json.loads(DB.meta("autobackup_status") or "{}")
    except ValueError:
        status = {}
    job = scheduler.get_job("_autobackup") if scheduler.running else None
    nxt = job.next_run_time.strftime("%d.%m.%Y %H:%M") if job and job.next_run_time else ""
    view = {k: st.get(k) for k in backup.AUTO_DEFAULTS}
    view["autobackup_password"] = ""
    view.update(has_password=bool(st.get("autobackup_password")), status=status, next=nxt,
                dir=backup.auto_dir(CONFIG_DIR, st), default_dir=os.path.join(CONFIG_DIR, "backups"),
                channels=[(c, n, bool(st.get(f"{c}_enabled"))) for c, n in
                          (("webhook", "Webhook"), ("smtp", "E-Mail"), ("telegram", "Telegram"), ("apprise", "Apprise"))])
    return view


def run_autobackup(by="Zeitplan", force=False, user=None):
    """Automatische Sicherung ausfuehren (Zeitplan oder Knopf). Benachrichtigt je nach Einstellung."""
    if not _ab_lock.acquire(blocking=False):
        return {"result": "fail", "error": "Es läuft bereits eine Sicherung."}
    try:
        st = load_settings()
        res = backup.run_auto(DB, CONFIG_DIR, VERSION, st, LOG_DIR, force=force)
        res["by"] = by
        DB.set_meta("autobackup_status", json.dumps({k: res.get(k) for k in
                                                     ("result", "file", "size", "error", "time", "removed", "by", "last_time")}))
        fname = os.path.basename(res.get("file") or "")
        if res["result"] == "ok":
            audit_add("system", "automatisch gesichert", fname, user=user or "System",
                      detail=f"{_size(res['size'])}, {'verschlüsselt' if res.get('encrypted') else 'unverschlüsselt'}, "
                             f"{by}" + (f", {len(res['removed'])} alte gelöscht" if res["removed"] else ""))
        elif res["result"] == "fail":
            audit_add("system", "automatische Sicherung fehlgeschlagen", res["dir"], detail=res["error"], user=user or "System")
        print(f"Automatische Sicherung ({by}): {res['result']} {fname or res['error']}", flush=True)
        when = st.get("autobackup_notify") or "fail"
        send = (res["result"] == "fail" and when in ("fail", "always")) or (res["result"] == "ok" and when == "always") \
            or (res["result"] == "skip" and when == "always" and st.get("autobackup_notify_skip"))
        if send:
            eff = dict(st)
            chans = st.get("autobackup_channels") or []
            if chans:
                for c in notify.CHANNELS:
                    eff[f"{c}_enabled"] = c in chans
            kind = {"ok": "backup_ok", "skip": "backup_skip"}.get(res["result"], "backup_fail")
            vals = {"datei": fname, "ordner": res["dir"], "groesse": _size(res.get("size")),
                    "verschluesselt": "ja" if res.get("encrypted") else "nein", "geloescht": str(len(res["removed"])),
                    "fehler_text": res.get("error", ""), "letzte": res.get("last_time", ""), "gestartet_von": by}
            ev = notify.event(eff, kind, vals, status=kind, ok=res["result"] != "fail", job="Sicherung",
                              source=CONFIG_DIR, dest=res["dir"])
            if res["result"] == "fail":
                ev["errors"] = [res["error"]]
            res["notify"] = notify.send(eff, ev)
        return res
    finally:
        _ab_lock.release()


@app.post("/settings/backup/auto")
def backup_settings():
    deny = _admin_only()
    if deny:
        return deny
    f = request.form
    st = load_settings()
    if f.get("run"):
        res = run_autobackup(by=g.user or "GUI", force=bool(f.get("force")), user=g.user)
        if res["result"] == "ok":
            session["flash"] = f"Sicherung erstellt: {os.path.basename(res['file'])} ({_size(res['size'])})."
        elif res["result"] == "skip":
            session["flash"] = "Seit der letzten Sicherung hat sich nichts geändert, deshalb wurde keine neue angelegt."
        else:
            return backup_page(err=f"Sicherung fehlgeschlagen: {res['error']}")
        return redirect(url_for("backup_page"))
    sched = " ".join((f.get("autobackup_schedule") or "").split())
    try:
        CronTrigger.from_crontab(sched or "x", timezone=TZ)
    except ValueError:
        return backup_page(err=f"Der Zeitplan „{sched}“ ist kein gültiger Cron-Ausdruck (Beispiel: 0 3 * * *).")
    d = (f.get("autobackup_dir") or "").strip().rstrip("/") if (f.get("autobackup_dir") or "").strip() != "/" else "/"
    if d and not os.path.isabs(d):
        return backup_page(err="Der Zielordner muss ein absoluter Pfad im Container sein, z. B. /backups.")
    if d and os.path.realpath(d) in (os.path.realpath(LOG_DIR), "/"):
        return backup_page(err="Dieser Ordner ist als Ziel nicht erlaubt.")
    if d:
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, ".mirrorsync-write-test")
            with open(probe, "w") as fh:
                fh.write("ok")
            os.remove(probe)
        except OSError as e:
            return backup_page(err=f"In den Zielordner {d} kann nicht geschrieben werden: {e.strerror or e}")
    pw, pw2 = f.get("autobackup_password", ""), f.get("autobackup_password2", "")
    if pw or pw2:
        if pw != pw2:
            return backup_page(err="Die Passwörter stimmen nicht überein.")
        if len(pw) < 8:
            return backup_page(err="Das Passwort für die Verschlüsselung braucht mindestens 8 Zeichen.")
        if not backup.CRYPTO:
            return backup_page(err="Verschlüsselung ist in diesem Image nicht verfügbar.")
        st["autobackup_password"] = pw
    elif f.get("autobackup_password_clear"):
        st["autobackup_password"] = ""
    st.update(autobackup_enabled=bool(f.get("autobackup_enabled")), autobackup_schedule=sched, autobackup_dir=d,
              autobackup_keep=str(backup._int(f.get("autobackup_keep"), 14)),
              autobackup_days=str(backup._int(f.get("autobackup_days"), 0)),
              autobackup_logs=bool(f.get("autobackup_logs")),
              autobackup_notify=f.get("autobackup_notify") if f.get("autobackup_notify") in ("never", "fail", "always") else "fail",
              autobackup_notify_skip=bool(f.get("autobackup_notify_skip")),
              autobackup_channels=[c for c in notify.CHANNELS if f.get(f"autobackup_ch_{c}")])
    if st["autobackup_keep"] == "0" and st["autobackup_days"] == "0":
        st["autobackup_keep"] = "14"
    save_settings(st)
    schedule_all()
    session["flash"] = "Automatische Sicherung gespeichert." + ("" if st["autobackup_enabled"] else " Sie ist ausgeschaltet.")
    return redirect(url_for("backup_page"))


@app.route("/settings/access", methods=["GET", "POST"])
def access_settings():
    cfg = guard.load()
    if request.method == "GET":
        kind, text = session.pop("flash_access", (None, None))
        return _access_page(cfg, msg=text if kind == "ok" else None, err=text if kind == "err" else None)
    f = request.form
    new = dict(cfg)
    allow, bad = [], []
    for line in f.get("allow", "").replace("\r", "").split("\n"):
        if not line.split("#", 1)[0].strip():
            continue
        try:
            ipguard.parse_entry(line)
            allow.append(line.strip())
        except ValueError:
            bad.append(line.strip())
    codes = sorted({c.strip().upper() for c in f.get("countries", "").replace(";", ",").replace(" ", ",").split(",")
                    if len(c.strip()) == 2 and c.strip().isalpha()} | {c.upper() for c in f.getlist("cc")})
    new.update(allow=allow, countries=codes,
               country_mode=f.get("country_mode") if f.get("country_mode") in ("off", "allow", "block") else "off",
               auto_exempt_lan="auto_exempt_lan" in f, notify="notify" in f)
    err = None
    for key, lo, hi in (("auto_attempts", 0, 1000), ("auto_minutes", 0, 5256000), ("auto_window", 1, 10080)):
        v = f.get(key, "").strip()
        if not v.isdigit() or not lo <= int(v) <= hi:
            err = "Automatische Sperre: bitte ganze Zahlen eintragen."
            break
        new[key] = str(int(v))
    if bad:
        err = "Ungültige Einträge in der Erlaubt-Liste: " + ", ".join(bad[:5])
    elif not err and new["country_mode"] != "off" and not codes:
        err = "Bitte mindestens ein Land auswählen oder die Ländersperre ausschalten."
    if not err:
        verdict = guard.check(_client_ip(), _country_iso, new)
        if verdict:
            err = (f"Nicht gespeichert: Damit würdest du dich selbst aussperren ({verdict[0]}, deine Adresse "
                   f"{_client_ip()}). Nimm deine Adresse oder dein Netz in die Erlaubt-Liste auf.")
    if err:
        return _access_page(cfg, err=err, form_cfg=new)
    guard.save(new)
    return _access_page(guard.load(), msg="Zugriffsregeln gespeichert.")


@app.post("/settings/access/block")
def access_block():
    f = request.form
    back = f.get("back") or "/settings/access"
    back = back if back.startswith("/") and not back.startswith("//") else "/settings/access"
    try:
        net = ipguard.parse_entry(f.get("net", ""))
    except ValueError:
        session["flash_access"] = ("err", "Ungültige IP-Adresse, ungültiges Netz oder ungültiger Hostname.")
        return redirect(back)
    try:
        me = ipaddress.ip_address(_client_ip())
        if me.version == 6 and me.ipv4_mapped:
            me = me.ipv4_mapped
        if ipguard.entry_matches(me, str(net)):
            session["flash_access"] = ("err", f"{net} enthält deine eigene Adresse {me}. Nicht gesperrt.")
            return redirect(back)
    except ValueError:
        pass
    try:
        minutes = int(f.get("minutes") or 0)
    except ValueError:
        minutes = 0
    n, until = guard.add_block(str(net), note=f.get("note", "").strip(), minutes=max(0, minutes), by=g.user)
    session["flash_access"] = ("ok", f"{n} gesperrt" + (f" bis {_dt(until)}." if until else " (dauerhaft)."))
    return redirect(back)


@app.post("/settings/access/unblock")
def access_unblock():
    guard.remove_block(request.form.get("net", ""))
    session["flash_access"] = ("ok", f"Sperre für {request.form.get('net', '')} aufgehoben.")
    return redirect(url_for("access_settings"))


# ---------------------------------------------------------------- Benutzer und Rollen
def within(role):
    """Darf der angemeldete Benutzer diese Rolle vergeben/bearbeiten? Niemand kann mehr Rechte
    weitergeben, als er selbst hat."""
    if not role:
        return False
    mine = g.access.role
    if not set(role.get("perms", [])) <= g.access.perms:
        return False
    for key in ("jobs", "remotes"):
        if mine.get(key, "all") != "all" and (role.get(key, "all") == "all" or not set(role[key]) <= set(mine[key])):
            return False
    return True


@app.get("/roles")
def roles_page():
    all_roles = role_store.load()
    counts = {}
    for u in store.load().values():
        counts[u.get("role")] = counts.get(u.get("role"), 0) + 1
    summary = {rid: [(gname.split(" ")[0], sum(p in r.get("perms", []) for p, _ in perms), len(perms))
                     for gname, perms in roles.PERM_GROUPS if any(p in r.get("perms", []) for p, _ in perms)]
               for rid, r in all_roles.items()}
    return render_template("roles.html", roles=all_roles, counts=counts, summary=summary,
                           msg=session.pop("flash", None))


@app.route("/roles/new", methods=["GET", "POST"])
@app.route("/roles/<rid>/edit", methods=["GET", "POST"])
def role_edit(rid=None):
    all_roles = role_store.load()
    if rid and rid not in all_roles:
        abort(404)
    src = all_roles.get(rid) or all_roles.get(request.args.get("from", ""), {}) or {}
    role = {"name": "" if not rid else src.get("name", ""), "description": src.get("description", ""),
            "perms": list(src.get("perms", [])), "jobs": src.get("jobs", "all"), "remotes": src.get("remotes", "all")}
    if not rid and request.args.get("from"):
        role["name"] = f"{src.get('name', '')} (Kopie)"
    locked = bool(rid and all_roles[rid].get("locked"))
    err = None
    if request.method == "POST" and not locked:
        f = request.form
        role.update(name=f.get("name", "").strip()[:40], description=f.get("description", "").strip()[:200],
                    perms=roles.normalize(f.getlist("perm")),
                    jobs="all" if f.get("jobs_scope") != "some" else f.getlist("job"),
                    remotes="all" if f.get("remotes_scope") != "some" else f.getlist("remote"))
        if not role["name"]:
            err = "Bitte einen Namen eingeben."
        elif any(r["name"].lower() == role["name"].lower() and k != rid for k, r in all_roles.items()):
            err = "Eine Rolle mit diesem Namen gibt es schon."
        elif not within(role) or (rid and not within(all_roles[rid])):
            err = "Du kannst keine Rolle mit mehr Rechten anlegen oder ändern, als du selbst hast."
        if not err:
            with roles._lock:
                all_roles = role_store.load()
                new_rid = rid or roles.new_id(role["name"], all_roles)
                entry = all_roles.get(new_rid, {})
                entry.update(role)
                entry.setdefault("builtin", False)
                all_roles[new_rid] = entry
                role_store.save(all_roles)
            session["flash"] = f"Rolle „{role['name']}“ gespeichert."
            return redirect(url_for("roles_page"))
    jobs = sorted(((k, v["name"]) for k, v in load_jobs().items()), key=lambda kv: kv[1].lower())
    return render_template("role_edit.html", rid=rid, role=role, locked=locked, err=err, groups=roles.PERM_GROUPS,
                           jobs=jobs, remotes=list_remotes(), templates=all_roles)


@app.post("/roles/<rid>/delete")
def role_delete(rid):
    all_roles = role_store.load()
    in_use = [n for n, u in store.load().items() if u.get("role") == rid]
    if rid not in all_roles:
        abort(404)
    if all_roles[rid].get("locked"):
        _flash_err("Die Rolle Admin kann nicht gelöscht werden.")
    elif in_use:
        _flash_err(f"Rolle wird noch benutzt von: {', '.join(in_use)}.")
    elif not within(all_roles[rid]):
        _flash_err("Keine Berechtigung für diese Rolle.")
    else:
        with roles._lock:
            all_roles = role_store.load()
            all_roles.pop(rid, None)
            role_store.save(all_roles)
        session["flash"] = "Rolle gelöscht."
    return redirect(url_for("roles_page"))


# ---------------------------------------------------------------- Gruppen
def group_within(grp):
    """Gruppen geben ihren Mitgliedern Rechte. Bearbeiten darf sie nur, wer diese Rechte selbst hat."""
    return set((grp or {}).get("perms") or []) <= g.access.perms


def group_views(gid):
    """Eingeschraenkte Aufgaben und Speicherorte, die diese Gruppe sieht."""
    pid = "group:" + gid
    jobs = sorted((j["name"], jid) for jid, j in load_jobs().items()
                  if isinstance(j.get("visible_to"), list) and pid in j["visible_to"])
    rem = sorted(n for n, v in remote_vis_map().items() if isinstance(v, list) and pid in v)
    return jobs, rem


@app.get("/groups")
def groups_page():
    grs = load_groups()
    keys = DB.get_map("apikey")
    rows = []
    for gid, x in sorted(grs.items(), key=lambda kv: kv[1].get("name", "").lower()):
        jobs, rem = group_views(gid)
        rows.append(dict(x, id=gid, n_perms=len(x.get("perms") or []), view_jobs=jobs, view_remotes=rem,
                         key_names=[keys.get(k, {}).get("name", k) for k in x.get("keys") or []],
                         editable=group_within(x)))
    return render_template("groups.html", rows=rows, msg=session.pop("flash", None))


@app.route("/groups/new", methods=["GET", "POST"])
@app.route("/groups/<gid>/edit", methods=["GET", "POST"])
def group_edit(gid=None):
    grs = load_groups()
    if gid and gid not in grs:
        abort(404)
    grp = dict(grs.get(gid) or {"name": "", "description": "", "members": [], "keys": [], "perms": []})
    err = None
    if request.method == "POST":
        f = request.form
        all_users = store.load()
        keys = DB.get_map("apikey")
        grp.update(name=f.get("name", "").strip()[:40], description=f.get("description", "").strip()[:200],
                   perms=roles.normalize(f.getlist("perm")),
                   members=[n for n in sorted(all_users, key=str.lower) if n in f.getlist("member")],
                   keys=[k for k in keys if k in f.getlist("key")])
        unknown = [m for m in f.getlist("member") if m not in all_users] + [k for k in f.getlist("key") if k not in keys]
        if not grp["name"]:
            err = "Bitte einen Namen eingeben."
        elif unknown:
            err = i18n.t("Unbekanntes Mitglied: {0}", unknown[0])
        elif any(x.get("name", "").lower() == grp["name"].lower() and k != gid for k, x in grs.items()):
            err = "Eine Gruppe mit diesem Namen gibt es schon."
        elif not group_within(grp) or (gid and not group_within(grs[gid])):
            err = "Du kannst einer Gruppe keine Rechte geben, die du selbst nicht hast."
        if not err:
            grs = load_groups()
            new_gid = gid or roles.new_id(grp["name"], grs)
            grs[new_gid] = grp
            save_groups(grs)
            session["flash"] = i18n.t("Gruppe „{0}“ gespeichert.", grp["name"])
            return redirect(url_for("groups_page"))
    keys = [(k, v.get("name", k), api.key_status(v)) for k, v in sorted(DB.get_map("apikey").items(), key=lambda kv: kv[1].get("name", "").lower())]
    jobs, rem = group_views(gid) if gid else ([], [])
    return render_template("group_edit.html", gid=gid, grp=grp, err=err, groups=roles.PERM_GROUPS,
                           all_users=sorted(store.load(), key=str.lower), keys=keys, view_jobs=jobs, view_remotes=rem)


@app.post("/groups/<gid>/delete")
def group_delete(gid):
    grs = load_groups()
    if gid not in grs:
        abort(404)
    if not group_within(grs[gid]):
        _flash_err("Keine Berechtigung für diese Gruppe.")
    else:
        name = grs.pop(gid).get("name", gid)
        save_groups(grs)
        drop_principal("group:" + gid)
        session["flash"] = i18n.t("Gruppe „{0}“ gelöscht.", name)
    return redirect(url_for("groups_page"))


def _admin_guard(name, new_role=None, deleting=False, override=None):
    """Verhindert, dass der letzte Admin entfernt, herabgestuft, deaktiviert oder befristet wird.
    Es muss immer ein aktiver Admin ohne Ablaufdatum bleiben."""
    all_users = store.load()
    if name not in users.permanent_admins(all_users):
        return None
    change = dict(override or {})
    if new_role:
        change["role"] = new_role
    rest = users.permanent_admins(all_users, except_name=name, override=None if deleting else change)
    if not rest:
        return "Es muss mindestens ein aktiver Admin ohne geplante Sperre bleiben."
    return None


@app.get("/users")
def users_page():
    all_users = store.load()
    grs = load_groups()
    rows = [dict(u, name=n, backup_left=len(u.get("backup_codes") or []), n_passkeys=len(u.get("passkeys") or []), why=users.inactive_reason(u),
                 group_names=[grs[x]["name"] for x in roles.groups_of(grs, n)],
                 planned=users.lock_pending(u) and not users.inactive_reason(u))
            for n, u in sorted(all_users.items())]
    fails = login_log.unacked()
    return render_template("users.html", rows=rows, msg=session.pop("flash", None), err=None,
                           roles=role_store.load(), fails=fails, conflicts=store.case_conflicts())


@app.post("/users/log/action")
def login_log_action():
    f = request.form
    ids = f.getlist("id") or None
    scope_all = f.get("all") == "1"
    if not scope_all and not ids:
        _flash_err("Keine Einträge ausgewählt.")
    elif f.get("action") == "ack":
        n = login_log.ack(None if scope_all else ids, by=g.user)
        session["flash"] = f"Fehlversuche bestätigt: {n}."
    elif f.get("action") == "delete":
        n = login_log.delete(None if scope_all else ids, failed_only=f.get("only_failed", "1") == "1")
        session["flash"] = f"Einträge gelöscht: {n}."
    back = f.get("back", "/users/log")
    return redirect(back if back.startswith("/users/log") else "/users/log")


@app.post("/users/<name>/unlock")
def user_unlock(name):
    target = store.get(name) or abort(404)
    if not within(role_store.get(target.get("role"))):
        _flash_err("Keine Berechtigung für diesen Benutzer.")
    else:
        store.update(name, disabled=False, disabled_by="", auto_lock_until="", fail_count=0)
        session["flash"] = f"Benutzer '{name}' entsperrt."
    return redirect(url_for("users_page"))


@app.get("/users/log")
def login_history():
    flt = request.args.get("f", "all")
    who = request.args.get("u", "").strip()
    entries = login_log.load()
    if flt == "ok":
        entries = [e for e in entries if e.get("ok")]
    elif flt == "fail":
        entries = [e for e in entries if not e.get("ok")]
    if who:
        entries = [e for e in entries if e.get("user") == who]
    if flt == "new":
        entries = [e for e in login_log.load() if not e.get("ok") and not e.get("ack") and (not who or e.get("user") == who)]
    return render_template("login_log.html", entries=entries[:500], flt=flt, who=who, geo=geoip.status(),
                           msg=session.pop("flash", None) or (session.pop("flash_access", (None, None))[1]), unacked=login_log.unacked(),
                           blocked_nets=[e["net"] for e in guard.load().get("block", []) if ipguard.active_block(e)],
                           attribution=Markup(geoip.ATTRIBUTION))


@app.route("/users/new", methods=["GET", "POST"])
@app.route("/users/<name>/edit", methods=["GET", "POST"])
def user_edit(name=None):
    all_users = store.load()
    if name and name not in all_users:
        abort(404)
    u = all_users.get(name, {"role": "operator"})
    err = None
    if request.method == "POST":
        f = request.form
        all_roles = role_store.load()
        role = f.get("role") if f.get("role") in all_roles else "viewer"
        pw = f.get("password", "")
        new_name = name or f.get("name", "").strip()
        if not name and not users.valid_name(new_name):
            err = "Benutzername: 1-32 Zeichen, Buchstaben, Ziffern, - _ . @"
        elif not name and store.taken(new_name):
            err = f"Benutzer '{store.find(new_name) or new_name}' existiert schon (Groß-/Kleinschreibung zählt nicht)."
        elif (pw or not name) and users.password_problem(pw):
            err = users.password_problem(pw)
        elif pw and pw != f.get("password2", ""):
            err = "Die Passwörter stimmen nicht überein."
        elif not within(all_roles.get(role)) or (name and not within(all_roles.get(u.get("role")))):
            err = "Du kannst keine Rolle mit mehr Rechten vergeben, als du selbst hast."
        disabled = f.get("active") == "0"
        lock_from = f.get("lock_from", "").strip()[:16] if f.get("lock") else ""
        lock_until = f.get("lock_until", "").strip()[:16] if f.get("lock") else ""
        dt_ok = lambda v: not v or re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", v)
        if not err and (not dt_ok(lock_from) or not dt_ok(lock_until)):
            err = "Sperrzeitraum: bitte Datum und Uhrzeit angeben."
        elif not err and f.get("lock") and not (lock_from or lock_until):
            err = "Sperrzeitraum: bitte mindestens „gesperrt ab“ oder „wieder aktiv ab“ angeben."
        elif not err and lock_from and lock_until and lock_until <= lock_from:
            err = "Sperrzeitraum: „wieder aktiv ab“ muss nach „gesperrt ab“ liegen."
        elif not err and lock_until and not lock_from and lock_until <= users._now():
            err = "Sperrzeitraum: „wieder aktiv ab“ liegt in der Vergangenheit."
        elif not err and name and name == g.user and (disabled or lock_from or lock_until):
            err = "Du kannst dein eigenes Konto nicht deaktivieren oder sperren."
        elif not err and name:
            err = _admin_guard(name, new_role=role,
                               override={"disabled": disabled, "lock_from": lock_from, "lock_until": lock_until})
        if not err:
            with users._lock:
                all_users = store.load()
                if name:
                    entry = all_users[name]
                    changed = entry.get("role") != role or bool(pw) or (disabled and not entry.get("disabled"))
                    entry.update(role=role, disabled=disabled, lock_from=lock_from, lock_until=lock_until)
                    if not disabled:
                        entry.update(disabled_by="", fail_count=0)
                    if f.get("unlock"):
                        entry.update(auto_lock_until="", fail_count=0)
                    entry.pop("valid_until", None)
                    if pw:
                        entry["hash"] = users.hash_password(pw)
                    if f.get("reset_2fa"):
                        entry.update(totp_enabled=False, totp_secret="", backup_codes=[])
                        changed = True
                    if f.get("reset_passkeys") and entry.get("passkeys"):
                        audit_add("user", "Passkeys entfernt", name, detail=f"{len(entry['passkeys'])} Stück, durch Admin")
                        entry["passkeys"] = []
                        changed = True
                    if changed:
                        entry["sv"] = entry.get("sv", 1) + 1   # bestehende Anmeldungen beenden
                else:
                    all_users[new_name] = dict(users.new_user(pw, role), disabled=disabled, lock_from=lock_from, lock_until=lock_until)
                store.save(all_users)
            if g.access.has("groups.manage") and f.get("grp_form"):
                grs = load_groups()
                want = set(f.getlist("grp"))
                for gid, x in grs.items():
                    if not group_within(x):
                        continue   # fremde Gruppen mit mehr Rechten bleiben unberuehrt
                    mem = [m for m in x.get("members") or [] if m.lower() != new_name.lower()]
                    if gid in want:
                        mem.append(new_name)
                    x["members"] = sorted(mem, key=str.lower)
                save_groups(grs)
            if name == g.user and store.get(name):
                session["sv"] = store.get(name)["sv"]
            session["flash"] = f"Benutzer '{new_name}' gespeichert."
            return redirect(url_for("users_page"))
    grs = load_groups()
    mine = roles.groups_of(grs, name) if name else []
    return render_template("user_edit.html", name=name, u=u, err=err, roles=role_store.load(), form=request.form,
                           all_groups=[(gid, dict(x, editable=group_within(x))) for gid, x in sorted(grs.items(), key=lambda kv: kv[1].get("name", "").lower())],
                           my_groups=mine, my_group_names=[grs[x]["name"] for x in mine])


@app.post("/users/<name>/delete")
def user_delete(name):
    target = store.get(name) or {}
    err = (_admin_guard(name, deleting=True) or ("Du kannst dich nicht selbst löschen." if name == g.user else None)
           or (None if within(role_store.get(target.get("role"))) else "Keine Berechtigung für diesen Benutzer."))
    if not err:
        with users._lock:
            all_users = store.load()
            all_users.pop(name, None)
            store.save(all_users)
        grs = load_groups()
        for x in grs.values():
            x["members"] = [m for m in x.get("members") or [] if m.lower() != name.lower()]
        save_groups(grs)
        drop_principal("user:" + name.lower())
        session["flash"] = f"Benutzer '{name}' gelöscht."
    else:
        _flash_err(err)
    return redirect(url_for("users_page"))


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.args.get("done"):
        session.pop("welcome", None)
        return redirect(url_for("index"))
    u = store.get(g.user)
    msg = session.pop("flash", None)
    err = None
    codes = None
    if request.method == "POST":
        action = request.form.get("action")
        if action in ("passkey_delete", "passkey_rename"):
            pid = request.form.get("id", "")
            keys = list(u.get("passkeys") or [])
            entry = next((p for p in keys if p.get("id") == pid), None)
            if not entry:
                err = "Passkey nicht gefunden."
            elif action == "passkey_rename":
                entry["name"] = request.form.get("name", "").strip()[:60] or "Passkey"
                store.update(g.user, passkeys=keys)
                msg = "Passkey umbenannt."
            elif not users.check_password(u, request.form.get("password", "")):
                err = "Passwort falsch."
            else:
                store.update(g.user, passkeys=[p for p in keys if p.get("id") != pid])
                audit_add("user", "Passkey entfernt", g.user, detail=entry.get("name", ""))
                msg = f"Passkey „{entry.get('name')}“ entfernt."
        if action == "language":
            lang = request.form.get("language", "")
            if lang and not i18n.valid(lang):
                err = "Unbekannte Sprache."
            else:
                store.update(g.user, lang=lang)
                g.user_lang = lang
                session["flash"] = "Sprache gespeichert."
                return redirect(url_for("account"))
        if action == "password":
            old, pw, pw2 = (request.form.get(k, "") for k in ("old", "password", "password2"))
            if not users.check_password(u, old):
                err = "Aktuelles Passwort falsch."
            elif pw != pw2:
                err = "Die neuen Passwörter stimmen nicht überein."
            else:
                err = users.password_problem(pw)
            if not err:
                sv = u.get("sv", 1) + 1
                store.update(g.user, hash=users.hash_password(pw), sv=sv)
                session["sv"] = sv
                msg = "Passwort geändert. Andere Anmeldungen wurden beendet."
        elif action == "2fa_start":
            session["totp_setup"] = users.new_totp_secret()
        elif action == "2fa_confirm":
            secret = session.get("totp_setup")
            counter = users.verify_totp(secret, request.form.get("code", "")) if secret else None
            if not counter:
                err = "Code falsch. Prüfe die Uhrzeit von Handy und Server und versuche es erneut."
            else:
                codes, hashes = users.new_backup_codes()
                store.update(g.user, totp_secret=secret, totp_enabled=True, totp_last=counter, backup_codes=hashes)
                session.pop("totp_setup", None)
                msg = "Zwei-Faktor-Anmeldung ist aktiv."
        elif action == "2fa_disable":
            if not users.check_password(u, request.form.get("password", "")):
                err = "Passwort falsch."
            else:
                store.update(g.user, totp_enabled=False, totp_secret="", backup_codes=[])
                msg = "Zwei-Faktor-Anmeldung ist ausgeschaltet."
        elif action == "codes":
            if not users.check_password(u, request.form.get("password", "")):
                err = "Passwort falsch."
            else:
                codes, hashes = users.new_backup_codes()
                store.update(g.user, backup_codes=hashes)
                msg = "Neue Backup-Codes erzeugt. Die alten gelten nicht mehr."
        u = store.get(g.user)
    setup_secret = session.get("totp_setup") if not u.get("totp_enabled") else None
    qr = users.qr_svg(users.otpauth_uri(setup_secret, g.user)) if setup_secret else None
    rp_id, _, pk_problem = _pk_rp()
    return render_template("account.html", u=u, msg=msg, err=err, codes=codes, setup_secret=setup_secret, qr=qr,
                           welcome=session.get("welcome"), passkeys_list=u.get("passkeys") or [], pk_problem=pk_problem,
                           pk_rp=rp_id,
                           backup_left=len(u.get("backup_codes") or []),
                           my_logins=[e for e in login_log.load() if e.get("user") == g.user][:10])


# ---------------------------------------------------------------- Passkeys
def _pk_rp():
    """RP-ID und Origins fuer Passkeys aus Einstellung 'Oeffentliche Adresse' bzw. der aufgerufenen Adresse."""
    st = load_settings()
    host = request.host
    if st.get("trust_proxy") and request.headers.get("X-Forwarded-Host"):
        host = request.headers["X-Forwarded-Host"].split(",")[0].strip()
    public = (st.get("public_url") or os.environ.get("PUBLIC_URL", "")).strip()
    rp_id, origins, problem = passkeys.rp_for(host, public)
    if public and not problem and passkeys._host_only(host) != rp_id:
        problem = (f"Passkeys sind für {origins[0]} eingerichtet (Einstellungen → Allgemein). Du hast MirrorSync gerade "
                   f"über {host} geöffnet. Bitte über {origins[0]} aufrufen.")
    return rp_id, origins, problem


def _pk_json():
    data = request.get_json(silent=True) or {}
    return data if isinstance(data, dict) else {}


@app.post("/account/sidebar")
def account_sidebar():
    """Seitenleiste eingeklappt (nur Symbole) oder ausgeklappt, gespeichert je Benutzer."""
    state = request.form.get("state") or (request.get_json(silent=True) or {}).get("state", "")
    if state not in ("mini", "full"):
        return {"ok": False, "error": i18n.t("Ungültiger Wert für die Seitenleiste (mini oder full).")}, 400
    if not g.get("user") or not store.get(g.user):
        return {"ok": False, "error": i18n.t("Nur für angemeldete Benutzer.")}, 400
    store.update(g.user, sidebar=state if state == "mini" else "")
    return {"ok": True, "sidebar": state}


@app.post("/account/passkey/options")
def passkey_reg_options():
    rp_id, _, problem = _pk_rp()
    if problem:
        return {"ok": False, "error": problem}, 400
    u = store.get(g.user)
    handle = u.get("webauthn_id")
    if not handle:
        handle = passkeys.new_user_handle()
        store.update(g.user, webauthn_id=handle)
    opts, chal = passkeys.registration_options(rp_id, g.user, handle, u.get("passkeys"))
    session["pk_reg"] = {"c": chal, "t": time.time(), "rp": rp_id}
    return app.response_class(opts, mimetype="application/json")


@app.post("/account/passkey/register")
def passkey_register():
    st = session.pop("pk_reg", None)
    rp_id, origins, problem = _pk_rp()
    if problem:
        return {"ok": False, "error": problem}, 400
    if not st or time.time() - st.get("t", 0) > passkeys.TIMEOUT_S or st.get("rp") != rp_id:
        return {"ok": False, "error": "Die Anfrage ist abgelaufen. Bitte noch einmal versuchen."}, 400
    data = _pk_json()
    try:
        entry = passkeys.verify_registration(data.get("credential") or {}, st["c"], rp_id, origins, data.get("name"))
    except Exception as e:
        return {"ok": False, "error": f"Passkey konnte nicht geprüft werden: {e}"}, 400
    with users._lock:
        u = store.get(g.user)
        keys = [p for p in (u.get("passkeys") or []) if p.get("id") != entry["id"]]
        if len(keys) >= 20:
            return {"ok": False, "error": "Höchstens 20 Passkeys pro Benutzer."}, 400
        store.update(g.user, passkeys=keys + [entry])
    audit_add("user", "Passkey hinzugefügt", g.user, detail=f"{entry['name']} ({rp_id})")
    session["flash"] = f"Passkey „{entry['name']}“ ist eingerichtet. Du kannst dich jetzt damit anmelden."
    return {"ok": True}


@app.post("/login/passkey/options")
def passkey_login_options():
    rp_id, _, problem = _pk_rp()
    if problem:
        return {"ok": False, "error": problem}, 400
    if _locked():
        return {"ok": False, "error": "Zu viele Fehlversuche. Bitte 5 Minuten warten."}, 429
    opts, chal = passkeys.authentication_options(rp_id)
    session["pk_auth"] = {"c": chal, "t": time.time(), "rp": rp_id}
    return app.response_class(opts, mimetype="application/json")


@app.post("/login/passkey")
def passkey_login():
    st = session.pop("pk_auth", None)
    rp_id, origins, problem = _pk_rp()
    if problem:
        return {"ok": False, "error": problem}, 400
    if _locked():
        return {"ok": False, "error": "Zu viele Fehlversuche. Bitte 5 Minuten warten."}, 429
    if not st or time.time() - st.get("t", 0) > passkeys.TIMEOUT_S or st.get("rp") != rp_id:
        return {"ok": False, "error": "Die Anfrage ist abgelaufen. Bitte noch einmal versuchen."}, 400
    data = _pk_json()
    cred = data.get("credential") or {}
    try:
        cid = passkeys.credential_id(cred)
    except Exception:
        cid = ""
    name, entry = passkeys.find(store.load(), cid) if cid else (None, None)
    if not entry:
        _record_login("?", False, "unbekannter Passkey")
        _fail()
        return {"ok": False, "error": "Dieser Passkey ist hier nicht (mehr) hinterlegt. Bitte mit Passwort anmelden."}, 400
    try:
        count = passkeys.verify_authentication(cred, st["c"], rp_id, origins, entry)
    except Exception as e:
        _record_login(name, False, "Passkey ungültig")
        _account_fail(name)
        _fail()
        return {"ok": False, "error": f"Passkey-Anmeldung abgelehnt: {e}"}, 400
    u = store.get(name)
    why = users.inactive_reason(u) if u else "deaktiviert"
    if why:
        _record_login(name, False, f"Konto {why}")
        return {"ok": False, "error": INACTIVE_TEXT.get(why, "Konto nicht aktiv.")}, 403
    with users._lock:
        keys = list(store.get(name).get("passkeys") or [])
        for p in keys:
            if p.get("id") == entry["id"]:
                p.update(count=count, last_used=time.strftime("%Y-%m-%d %H:%M"))
        store.update(name, passkeys=keys)
    nxt = session.get("next")
    resp = _finish_login(name, u, data.get("remember"), f"Passkey ({entry.get('name', '')})")
    return {"ok": True, "next": resp.location or nxt or "/"}


def friendly_error(out, path=""):
    """rclone-Meldung in einen verstaendlichen Satz uebersetzen (Original bleibt als Detail erhalten)."""
    text = out or ""
    low = text.lower()
    rules = [
        (("directory not found", "not found", "no such file", "object_name_not_found", "bad network name", "bad_network_name"),
         f"Ordner „{path}“ wurde nicht gefunden."),
        (("logon failure", "access denied", "permission denied", "401", "403", "authentication", "unable to authenticate",
          "login incorrect", "status_logon_failure", "invalid credentials"),
         "Anmeldung abgelehnt. Bitte Benutzer und Passwort des Speicherorts prüfen."),
        (("no such host", "name resolution", "i/o timeout", "connection refused", "network is unreachable",
          "no route to host", "deadline exceeded", "zeitüberschreitung", "connection reset", "dial tcp"),
         "Keine Verbindung zum Server. Bitte Adresse, Port und Netzwerk prüfen."),
        (("ssh-agent", "ssh_auth_sock", "no key", "need a password or key"),
         "Für diesen Speicherort fehlt ein Passwort oder SSH-Schlüssel. Bitte unter Speicherorte bearbeiten."),
        (("didn't find section in config file", "not found in config"),
         "Diesen Speicherort gibt es nicht. Bitte unter Speicherorte anlegen."),
        (("token", "oauth", "invalid_grant"), "Die Anmeldung beim Dienst ist abgelaufen. Unter Speicherorte „Anmelden“ klicken."),
    ]
    msg = next((m for keys, m in rules if any(k in low for k in keys)), "Ordner konnte nicht gelesen werden.")
    lines = [re.sub(r"^\d{4}/\d\d/\d\d \d\d:\d\d:\d\d\s+", "", l).strip() for l in text.splitlines() if l.strip()]
    return msg, "\n".join(lines[-3:])


# Bei diesen Typen beginnt "name:" im Home-Ordner des Benutzers; Durchsuchen startet deshalb bei "name:/"
ABS_ROOT_TYPES = {"sftp", "ftp"}


@app.get("/browse")
def browse():
    """Ordner eines Pfades auflisten (fuer die Pfadauswahl im Job-Formular).
    Leerer Pfad = oberste Ebene: alle erlaubten Speicherorte und, falls erlaubt, lokale Ordner."""
    path = request.args.get("path", "").strip()
    if not path:
        entries = [{"name": r["name"] + ":", "path": r["name"] + (":/" if r["type"] in ABS_ROOT_TYPES else ":"),
                    "kind": "remote", "type": r["type"]}
                   for r in list_remotes() if g.access.remote_ok(r["name"])]
        if g.access.has("local.paths"):
            if os.path.isdir("/data"):
                entries.append({"name": "/data", "path": "/data", "kind": "local", "type": "lokale Ordner"})
        return {"ok": True, "path": "", "root": True, "entries": entries, "dirs": [],
                "hint": None if entries else "Noch keine Speicherorte angelegt."}
    m = re.match(r"^([^/:]+):$", path)
    if m and request.args.get("abs") == "1":   # SFTP/FTP: oberste Ebene = Wurzel / statt Home-Ordner
        typ = next((r["type"] for r in list_remotes() if r["name"] == m.group(1)), "")
        if typ in ABS_ROOT_TYPES:
            path += "/"
    rc, out = rclone("lsf", path, "--dirs-only", "--max-depth", "1", timeout=30)
    if rc != 0:
        msg, detail = friendly_error(out, path)
        return {"ok": False, "path": path, "dirs": [], "error": msg, "detail": detail}
    dirs = [d.rstrip("/") for d in out.splitlines() if d.strip()]
    return {"ok": True, "path": path, "root": False, "dirs": dirs, "error": None}


FILES_MAX = 5000


@app.get("/browse/list")
def browse_list():
    """Datei-Browser im Aufgabenformular: Ordner und Dateien eines Pfades mit Groesse und Datum (nur lesen)."""
    return browse_entries(request.args.get("path", "").strip())


def browse_entries(path):
    if not path:
        return {"ok": False, "error": "Kein Pfad."}, 400
    if not g.access.path_ok(path):
        return {"ok": False, "error": "Deine Rolle darf diesen Speicherort nicht verwenden."}, 403
    if any(part == ".." for part in re.split(r"[/:]", path)):
        return {"ok": False, "error": "Ungültiger Pfad."}, 400
    m = re.match(r"^([^/:]+):$", path)
    if m:   # SFTP/FTP: oberste Ebene = Wurzel /
        typ = next((r["type"] for r in list_remotes() if r["name"] == m.group(1)), "")
        if typ in ABS_ROOT_TYPES:
            path += "/"
    rc, out = rclone("lsjson", path, "--max-depth", "1", "--no-mimetype", timeout=60)
    if rc != 0:
        msg, detail = friendly_error(out, path)
        return {"ok": False, "path": path, "error": msg, "detail": detail}
    try:
        items = json.loads(out or "[]")
    except ValueError:
        return {"ok": False, "path": path, "error": "Antwort von rclone nicht lesbar."}
    entries = []
    for it in items[:FILES_MAX]:
        mod = (it.get("ModTime") or "")[:19]
        entries.append({"name": it.get("Name", ""), "dir": bool(it.get("IsDir")),
                        "size": None if it.get("IsDir") or it.get("Size", -1) < 0 else it.get("Size"),
                        "mod": mod.replace("T", " ") if mod and not mod.startswith("2000-01-01") else ""})
    return {"ok": True, "path": path, "entries": entries, "truncated": len(items) > FILES_MAX, "total": len(items)}


GEOIP_DOW = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def geoip_enabled(st):
    return bool(st.get("geoip_auto")) and os.environ.get("GEOIP", "").lower() not in ("0", "off", "false", "nein")


def geoip_scheduled(st):
    return geoip_enabled(st) and st.get("geoip_mode") == "schedule"


def geoip_clean_schedule(t, dows):
    """('03:00', ['mon','thu']) pruefen -> (zeit, 'mon,thu', fehler)."""
    t = (t or "").strip()
    if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", t):
        return "03:00", "mon", "Länder-Datenbank: Uhrzeit bitte als HH:MM angeben."
    d = [x for x in GEOIP_DOW if x in {str(y).strip().lower()[:3] for y in dows}]
    if not d:
        return t, "mon", "Länder-Datenbank: bitte mindestens einen Wochentag wählen."
    return t, ",".join(d), None


def _geoip_run():
    """Geplanter Download der Laender-Datenbank (Zeitplan mit Uhrzeit und Wochentagen)."""
    if not geoip_scheduled(load_settings()):
        return
    err = geoip.update(force=True)
    print(f"GeoIP: {err}" if err else "GeoIP: Länder-Datenbank nach Zeitplan aktualisiert.", flush=True)
    if not err:
        audit_add("settings", "Länder-Datenbank aktualisiert", "GeoIP", detail="Zeitplan", user="System")


def _geoip_loop():
    """GeoIP-Datenbank (DB-IP Lite) beim Start und dann taeglich pruefen, im eingestellten Abstand erneuern."""
    while True:
        st = load_settings()
        if geoip_enabled(st):
            # Mit Zeitplan nur nachladen, wenn sie fehlt oder sehr alt ist; sonst im gewaehlten Abstand
            err = geoip.update() if geoip_scheduled(st) else geoip.update(days=st.get("geoip_days") or 30)
            if err:
                print(f"GeoIP: {err}", flush=True)
        time.sleep(86400)


api.register(app, sys.modules[__name__])
filemgr.register(app, sys.modules[__name__])
apigui.register(app, sys.modules[__name__])


JSON_TEXT_KEYS = {"error", "msg", "message", "hint", "warning", "note"}


def _tr_json(obj, depth=0):
    if depth > 6:
        return obj
    if isinstance(obj, dict):
        return {k: (i18n.translate(v) if k in JSON_TEXT_KEYS and isinstance(v, str) else _tr_json(v, depth + 1))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [_tr_json(v, depth + 1) for v in obj]
    return obj


@app.after_request
def _bridge_after(resp):
    br = g.get("bridge")
    if br is not None:
        for k in ("flash", "flash_access"):
            if session.get(k) is not None:
                br["out"][k] = session.get(k)
        if session.get("import"):
            br["out"]["import"] = session.get("import")
    return resp


@app.after_request
def _translate_json(resp):
    """Meldungen in JSON-Antworten (GUI-Aufrufe, REST-API) in die Sprache der Anfrage uebersetzen."""
    if i18n.current() == i18n.SOURCE or resp.mimetype != "application/json" or resp.direct_passthrough:
        return resp
    try:
        data = json.loads(resp.get_data())
    except ValueError:
        return resp
    new = _tr_json(data)
    if new != data:
        resp.set_data(json.dumps(new, ensure_ascii=False))
    return resp


def main():
    # Nach einem Neustart haengengebliebene "laeuft"-Status bereinigen
    jobs = load_jobs()
    for job in jobs.values():
        if job.get("last_status") == "laeuft":
            job["last_status"] = "abgebrochen"
    if jobs:
        save_jobs(jobs)
    migrate_logs()
    if "language" not in DB.get_map("settings") and store.load():
        st = load_settings()
        st["language"] = i18n.SOURCE   # bestehende Installation (bis 1.19): bisher alles Deutsch
        save_settings(st)
    i18n.default_lang = load_settings().get("language") if i18n.valid(load_settings().get("language") or "") else i18n.DEFAULT
    login_log.ensure_ids()
    try:
        audit_log.keep_days = int(load_settings().get("audit_keep_days") or 365)
    except ValueError:
        pass
    audit_log.prune()
    if os.environ.get("IPGUARD_RESET", "").lower() in ("1", "true", "yes", "ja"):
        guard.reset()
        print("IPGUARD_RESET: Alle IP- und Ländersperren entfernt. IPGUARD_RESET jetzt wieder entfernen!", flush=True)
        audit_log.add("System", "access", "zurückgesetzt (IPGUARD_RESET)", "Zugriff")
    guard.prune()
    for grp in store.case_conflicts():
        print(f"Hinweis: Benutzer {', '.join(grp)} unterscheiden sich nur in Groß-/Kleinschreibung. "
              "Anmeldung klappt nur mit exakter Schreibweise, bitte einen umbenennen oder löschen.", flush=True)
    threading.Thread(target=_geoip_loop, daemon=True).start()
    threading.Thread(target=_update_loop, daemon=True).start()
    scheduler.start()
    schedule_all()
    from waitress import serve
    port = int(os.environ.get("PORT", "8080"))
    print(f"MirrorSync {VERSION} laeuft auf Port {port} (Zeitzone {TZ})", flush=True)
    bootstrap_users()
    if not store.load():
        print("Noch kein Benutzer angelegt: Beim ersten Aufruf der Web-GUI wird ein Admin eingerichtet.", flush=True)
        setup_token(show=True)
    # Proxy-Header durchreichen; ob sie gelten, entscheidet die Einstellung "Reverse-Proxy" (_client_ip)
    serve(app, host="0.0.0.0", port=port, threads=8, clear_untrusted_proxy_headers=False)


if __name__ == "__main__":
    main()
