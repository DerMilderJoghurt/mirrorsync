"""Benutzer, Rollen und Zwei-Faktor-Anmeldung (TOTP, RFC 6238)."""
import base64
import hashlib
import hmac
import io
import json
import os
import secrets
import struct
import threading
import time
import urllib.parse

from werkzeug.security import check_password_hash, generate_password_hash

_lock = threading.RLock()


class Store:
    """Benutzer in der SQLite-Datenbank (Bereich 'user', ein Eintrag pro Benutzer)."""
    def __init__(self, db):
        self.db = db

    def load(self):
        with _lock:
            return self.db.get_map("user")

    def save(self, users):
        with _lock:
            self.db.put_map("user", users)

    def get(self, name):
        return self.load().get(name)

    def find(self, name):
        """Benutzername ohne Unterscheidung von Gross-/Kleinschreibung. Exakte Schreibweise hat Vorrang.
        Liefert den gespeicherten Namen oder None (auch, wenn mehrere Konten nur in der Schreibweise abweichen)."""
        name = (name or "").strip()
        all_users = self.load()
        if name in all_users:
            return name
        hits = [n for n in all_users if n.casefold() == name.casefold()]
        return hits[0] if len(hits) == 1 else None

    def taken(self, name):
        return any(n.casefold() == (name or "").strip().casefold() for n in self.load())

    def case_conflicts(self):
        groups = {}
        for n in self.load():
            groups.setdefault(n.casefold(), []).append(n)
        return [sorted(v) for v in groups.values() if len(v) > 1]

    def update(self, name, **fields):
        with _lock:
            users = self.load()
            if name in users:
                users[name].update(fields)
                self.save(users)

    def admins(self):
        return [n for n, u in self.load().items() if u.get("role") == "admin"]


def new_user(password, role):
    return {"hash": hash_password(password), "role": role, "totp_secret": "", "totp_enabled": False,
            "backup_codes": [], "sv": 1, "created": time.strftime("%Y-%m-%d %H:%M"), "last_login": ""}


def hash_password(pw):
    return generate_password_hash(pw)


def check_password(user, pw):
    return bool(user) and check_password_hash(user.get("hash", ""), pw)


def password_problem(pw):
    if len(pw) < 8:
        return "Das Passwort muss mindestens 8 Zeichen lang sein."
    return None


def valid_name(name):
    return 1 <= len(name) <= 32 and all(c.isalnum() or c in "-_.@" for c in name)


# ---------------------------------------------------------------- TOTP
def new_totp_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _totp(secret, counter):
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[off:off + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code:06d}"


def totp_now(secret, t=None):
    return _totp(secret, int((t or time.time()) // 30))


def verify_totp(secret, code, last_counter=0):
    """Prueft den Code (+-1 Zeitfenster). Liefert den Zaehler bei Erfolg, sonst None.
    Ein bereits benutzter Code (Zaehler <= last_counter) wird abgelehnt."""
    code = "".join(c for c in (code or "") if c.isdigit())
    if len(code) != 6 or not secret:
        return None
    now = int(time.time() // 30)
    for c in (now - 1, now, now + 1):
        if c > (last_counter or 0) and hmac.compare_digest(_totp(secret, c), code):
            return c
    return None


def otpauth_uri(secret, name, issuer="MirrorSync"):
    label = urllib.parse.quote(f"{issuer}:{name}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={urllib.parse.quote(issuer)}&digits=6&period=30"


def qr_svg(data):
    import segno
    buf = io.BytesIO()
    segno.make(data, error="m").save(buf, kind="svg", scale=5, border=2, dark="#000", light="#fff",
                                      xmldecl=False, svgns=True)
    return buf.getvalue().decode()


# ---------------------------------------------------------------- Backup-Codes
def new_backup_codes(n=10):
    """Liefert (Klartext-Codes fuer die einmalige Anzeige, Hashes zum Speichern)."""
    codes = ["-".join(secrets.token_hex(2) for _ in range(2)) + "-" + secrets.token_hex(2) for _ in range(n)]
    return codes, [_code_hash(c) for c in codes]


def _code_hash(code):
    return hashlib.sha256(code.replace("-", "").replace(" ", "").lower().encode()).hexdigest()


def use_backup_code(user, code):
    """Entfernt den Code, wenn er passt. Liefert die neue Liste oder None."""
    h = _code_hash(code or "")
    codes = list(user.get("backup_codes") or [])
    for i, stored in enumerate(codes):
        if hmac.compare_digest(stored, h):
            del codes[i]
            return codes
    return None


# ---------------------------------------------------------------- Konto aktiv / gesperrt
def _now():
    return time.strftime("%Y-%m-%dT%H:%M")


def inactive_reason(user, now=None):
    """None, wenn das Konto benutzt werden darf, sonst ein kurzer Grund.
    lock_from/lock_until ('YYYY-MM-DDTHH:MM', beide optional) bilden ein Sperr-Zeitfenster."""
    if not user:
        return "unbekannt"
    if user.get("disabled"):
        return "deaktiviert"
    now = now or _now()
    if (user.get("auto_lock_until") or "") > now:
        return "gesperrt"
    f, u = (user.get("lock_from") or "").strip(), (user.get("lock_until") or "").strip()
    if (f or u) and (not f or now >= f) and (not u or now < u):
        return "gesperrt"
    return None


def lock_pending(user, now=None):
    """Sperre liegt in der Zukunft oder laeuft gerade (Fenster noch nicht vorbei)."""
    now = now or _now()
    f, u = (user.get("lock_from") or "").strip(), (user.get("lock_until") or "").strip()
    return bool(f or u) and (not u or now < u)


def permanent_admins(all_users, except_name=None, override=None):
    """Admins, die aktiv sind und keine aktuelle oder geplante Sperre haben."""
    out = []
    for n, u in all_users.items():
        if n == except_name:
            if override is None:
                continue
            u = dict(u, **override)
        if u.get("role") == "admin" and not u.get("disabled") and not lock_pending(u):
            out.append(n)
    return out


# ---------------------------------------------------------------- Anmeldeverlauf
class LoginLog:
    """Anmeldeverlauf in der Datenbank (Tabelle login_log), neueste Eintraege zuerst, hoechstens KEEP."""
    KEEP = 1000

    def __init__(self, db):
        self.db = db

    def load(self):
        with _lock:
            return self.db.login_all(self.KEEP)

    def _save(self, data):
        self.db.login_replace(data, self.KEEP)

    def add(self, **entry):
        entry.setdefault("time", time.strftime("%Y-%m-%d %H:%M:%S"))
        entry.setdefault("id", secrets.token_hex(6))
        if not entry.get("ok"):
            entry.setdefault("ack", False)
        with _lock:
            self.db.login_add(entry, self.KEEP)

    def ensure_ids(self):
        """Eintraege aus aelteren Versionen bekommen eine ID; alte Fehlversuche gelten als bestaetigt."""
        with _lock:
            data = self.load()
            changed = False
            for e in data:
                if "id" not in e:
                    e["id"] = secrets.token_hex(6)
                    if not e.get("ok"):
                        e["ack"] = True
                    changed = True
            if changed:
                self._save(data)

    def unacked(self):
        return sum(1 for e in self.load() if not e.get("ok") and not e.get("ack"))

    def ack(self, ids=None, by=""):
        """ids=None: alle Fehlversuche bestaetigen."""
        with _lock:
            data = self.load()
            n = 0
            for e in data:
                if not e.get("ok") and not e.get("ack") and (ids is None or e.get("id") in ids):
                    e.update(ack=True, ack_by=by, ack_time=time.strftime("%Y-%m-%d %H:%M"))
                    n += 1
            self._save(data)
            return n

    def delete(self, ids=None, failed_only=True):
        """ids=None: alle (Fehlversuche bzw. alle Eintraege) loeschen."""
        with _lock:
            data = self.load()
            keep = [e for e in data if not ((ids is None or e.get("id") in ids) and (not failed_only or not e.get("ok")))]
            self._save(keep)
            return len(data) - len(keep)
