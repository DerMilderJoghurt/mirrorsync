"""SQLite-Datenspeicher (config/mirrorsync.db).

Aufgaben, Einstellungen, Benutzer, Rollen und IP-Regeln liegen als Dokumente (JSON) in der Tabelle docs,
je Objekt eine Zeile (ns = Bereich, key = ID). Anmeldeverlauf und Audit-Log haben eigene Tabellen.
Alle Schreibvorgaenge laufen in Transaktionen: entweder alles oder nichts."""
import json
import os
import sqlite3
import threading
import time

SCHEMA_VERSION = 1
DB_NAME = "mirrorsync.db"
# Bereiche in docs
NS = ("job", "user", "role", "settings", "ipguard", "apikey", "group", "remote_meta")
# JSON-Dateien bis 1.17 -> Bereich ('*' = ganze Datei ist ein Objekt mit Feldern)
LEGACY = {"jobs.json": "job", "users.json": "user", "roles.json": "role", "settings.json": "settings",
          "ipguard.json": "ipguard"}
LEGACY_LOGS = ("login_log.json", "audit.jsonl")

_lock = threading.RLock()


def _dumps(v):
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


class DB:
    def __init__(self, path):
        self.path = path
        self._local = threading.local()
        new = not os.path.exists(path)
        with _lock:
            c = self.conn()
            c.executescript("""
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS docs (ns TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,
                                             PRIMARY KEY (ns, key));
            CREATE TABLE IF NOT EXISTS login_log (seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, cat TEXT, user TEXT,
                                              data TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS audit_ts ON audit (ts);
            """)
            c.execute("INSERT OR IGNORE INTO meta VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),))
        for p in (path, path + "-wal", path + "-shm"):   # enthaelt Geheimnisse: nur fuer root lesbar
            try:
                os.chmod(p, 0o600)
            except OSError:
                pass

    # ------------------------------------------------------------ Verbindung
    def conn(self):
        c = getattr(self._local, "c", None)
        if c is None:
            c = sqlite3.connect(self.path, timeout=30, isolation_level=None, check_same_thread=False)
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=NORMAL")
            c.execute("PRAGMA foreign_keys=ON")
            self._local.c = c
        return c

    class _Tx:
        def __init__(self, db):
            self.db = db

        def __enter__(self):
            _lock.acquire()
            self.c = self.db.conn()
            self.nested = self.c.in_transaction
            if not self.nested:
                self.c.execute("BEGIN IMMEDIATE")
            return self.c

        def __exit__(self, et, ev, tb):
            try:
                if not self.nested:
                    self.c.execute("ROLLBACK" if et else "COMMIT")
            finally:
                _lock.release()
            return False

    def tx(self):
        """with db.tx() as c: ... -> eine Transaktion (verschachtelt = Teil der aeusseren)."""
        return DB._Tx(self)

    # ------------------------------------------------------------ Meta
    def meta(self, key, default=None):
        r = self.conn().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else default

    def set_meta(self, key, value, c=None):
        (c or self.conn()).execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, str(value)))

    # ------------------------------------------------------------ Dokumente
    def get_map(self, ns):
        with _lock:
            rows = self.conn().execute("SELECT key, value FROM docs WHERE ns=? ORDER BY rowid", (ns,)).fetchall()
        return {k: json.loads(v) for k, v in rows}

    def get(self, ns, key, default=None):
        r = self.conn().execute("SELECT value FROM docs WHERE ns=? AND key=?", (ns, key)).fetchone()
        return json.loads(r[0]) if r else default

    def put_map(self, ns, data):
        """Bereich komplett ersetzen: geaenderte Zeilen schreiben, fehlende loeschen."""
        with self.tx() as c:
            old = dict(c.execute("SELECT key, value FROM docs WHERE ns=?", (ns,)).fetchall())
            for k, v in data.items():
                s = _dumps(v)
                if old.get(str(k)) != s:
                    c.execute("INSERT OR REPLACE INTO docs VALUES (?, ?, ?)", (ns, str(k), s))
            gone = [k for k in old if k not in {str(x) for x in data}]
            c.executemany("DELETE FROM docs WHERE ns=? AND key=?", [(ns, k) for k in gone])

    def put(self, ns, key, value):
        with self.tx() as c:
            c.execute("INSERT OR REPLACE INTO docs VALUES (?, ?, ?)", (ns, str(key), _dumps(value)))

    # ------------------------------------------------------------ Anmeldeverlauf (neueste zuerst)
    def login_all(self, limit=None):
        sql = "SELECT data FROM login_log ORDER BY seq DESC" + (f" LIMIT {int(limit)}" if limit else "")
        with _lock:
            return [json.loads(r[0]) for r in self.conn().execute(sql).fetchall()]

    def login_add(self, entry, keep):
        with self.tx() as c:
            c.execute("INSERT INTO login_log (id, data) VALUES (?, ?)", (entry.get("id"), _dumps(entry)))
            c.execute("DELETE FROM login_log WHERE seq NOT IN (SELECT seq FROM login_log ORDER BY seq DESC LIMIT ?)",
                      (int(keep),))

    def login_replace(self, entries, keep):
        """Liste (neueste zuerst) komplett ersetzen."""
        with self.tx() as c:
            c.execute("DELETE FROM login_log")
            c.executemany("INSERT INTO login_log (id, data) VALUES (?, ?)",
                          [(e.get("id"), _dumps(e)) for e in reversed(entries[:keep])])

    # ------------------------------------------------------------ Audit-Log
    def audit_add(self, e):
        with self.tx() as c:
            c.execute("INSERT INTO audit (ts, cat, user, data) VALUES (?, ?, ?, ?)",
                      (e.get("ts"), e.get("cat"), e.get("user"), _dumps(e)))

    def audit_all(self):
        with _lock:
            return [json.loads(r[0]) for r in self.conn().execute("SELECT data FROM audit ORDER BY seq DESC").fetchall()]

    def audit_prune(self, before_ts=None, keep_max=None):
        with self.tx() as c:
            n0 = c.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
            if before_ts:
                c.execute("DELETE FROM audit WHERE ts < ?", (before_ts,))
            if keep_max:
                c.execute("DELETE FROM audit WHERE seq NOT IN (SELECT seq FROM audit ORDER BY seq DESC LIMIT ?)",
                          (int(keep_max),))
            return n0 - c.execute("SELECT COUNT(*) FROM audit").fetchone()[0]

    # ------------------------------------------------------------ Export / Import des ganzen Inhalts
    def dump(self):
        out = {ns: self.get_map(ns) for ns in NS}
        out["login_log"] = self.login_all()
        out["audit"] = list(reversed(self.audit_all()))   # aelteste zuerst
        return out

    def counts(self):
        c = self.conn()
        res = {ns: c.execute("SELECT COUNT(*) FROM docs WHERE ns=?", (ns,)).fetchone()[0] for ns in NS}
        res["login_log"] = c.execute("SELECT COUNT(*) FROM login_log").fetchone()[0]
        res["audit"] = c.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
        return res

    def restore(self, data, c=None):
        """Gesamten Inhalt ersetzen (innerhalb einer Transaktion)."""
        with self.tx() as c:
            c.execute("DELETE FROM docs")
            c.execute("DELETE FROM login_log")
            c.execute("DELETE FROM audit")
            for ns in NS:
                src = data.get(ns) or {}
                if not isinstance(src, dict):
                    raise ValueError(f"Bereich {ns} ist kein Objekt.")
                c.executemany("INSERT INTO docs VALUES (?, ?, ?)", [(ns, str(k), _dumps(v)) for k, v in src.items()])
            logs = data.get("login_log") or []
            c.executemany("INSERT INTO login_log (id, data) VALUES (?, ?)",
                          [(e.get("id"), _dumps(e)) for e in reversed(logs) if isinstance(e, dict)])
            c.executemany("INSERT INTO audit (ts, cat, user, data) VALUES (?, ?, ?, ?)",
                          [(e.get("ts"), e.get("cat"), e.get("user"), _dumps(e)) for e in data.get("audit") or []
                           if isinstance(e, dict)])

    def backup_file(self, dest):
        """Konsistente Kopie der Datenbank (sqlite backup API)."""
        with _lock:
            target = sqlite3.connect(dest)
            try:
                self.conn().backup(target)
            finally:
                target.close()
        os.chmod(dest, 0o600)


# ---------------------------------------------------------------- Migration aus JSON (bis 1.17)
def read_legacy(config_dir):
    """Alle alten JSON-Dateien lesen. Liefert (daten, gefundene Dateien). Fehlerhafte Datei -> Exception."""
    data, found = {}, []
    for fn, ns in LEGACY.items():
        p = os.path.join(config_dir, fn)
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    v = json.load(f)
            except ValueError as e:
                raise ValueError(f"{fn} ist kein gültiges JSON ({e})") from None
            if not isinstance(v, dict):
                raise ValueError(f"{fn}: unerwartetes Format")
            data[ns] = v
            found.append(fn)
    p = os.path.join(config_dir, "login_log.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                v = json.load(f)
        except ValueError:
            v = []   # Anmeldeverlauf ist verzichtbar
        data["login_log"] = v if isinstance(v, list) else []
        found.append("login_log.json")
    p = os.path.join(config_dir, "audit.jsonl")
    if os.path.exists(p):
        rows = []
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue   # einzelne kaputte Zeile (z. B. Abbruch beim Schreiben) ueberspringen
        data["audit"] = rows
        found.append("audit.jsonl")
    return data, found


def migrate(db, config_dir, log=print):
    """Einmalig: JSON-Dateien in die Datenbank uebernehmen. In einer Transaktion (bei Abbruch bleibt die DB leer
    und der naechste Start versucht es erneut). Danach werden die Dateien nach config/json-backup/ verschoben."""
    if db.meta("migrated_at"):
        _move_legacy(config_dir, log)   # falls der Start nach dem Commit abbrach
        return False
    data, found = read_legacy(config_dir)
    with db.tx() as c:
        if found:
            db.restore(data, c)
        db.set_meta("migrated_at", time.strftime("%Y-%m-%d %H:%M:%S"), c)
        db.set_meta("migrated_from", ", ".join(found) or "-", c)
    if found:
        n = db.counts()
        log(f"Daten nach SQLite übernommen ({', '.join(found)}): {n['job']} Aufgaben, {n['user']} Benutzer, "
            f"{n['role']} Rollen, {n['login_log']} Anmeldungen, {n['audit']} Audit-Einträge.")
        _move_legacy(config_dir, log)
    return bool(found)


def _move_legacy(config_dir, log=print):
    files = [fn for fn in list(LEGACY) + list(LEGACY_LOGS) if os.path.exists(os.path.join(config_dir, fn))]
    if not files:
        return
    dest = os.path.join(config_dir, "json-backup")
    os.makedirs(dest, exist_ok=True)
    os.chmod(dest, 0o700)
    for fn in files:
        target = os.path.join(dest, fn)
        if os.path.exists(target):
            target = os.path.join(dest, time.strftime("%Y%m%d-%H%M%S-") + fn)
        os.replace(os.path.join(config_dir, fn), target)
    log(f"Alte JSON-Dateien liegen als Sicherung in config/json-backup/ ({', '.join(files)}).")
