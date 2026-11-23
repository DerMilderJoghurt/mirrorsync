"""Land zu einer IP-Adresse aus einer lokalen MMDB-Datei (DB-IP Lite oder MaxMind GeoLite2 Country).

Kleiner eigener MMDB-Leser, damit keine zusaetzliche Bibliothek noetig ist. Es werden keine
externen Dienste abgefragt; die Datenbank liegt in /config/geoip/.
"""
import datetime
import gzip
import ipaddress
import os
import shutil
import struct
import threading
import time
import urllib.request

import i18n

MARKER = b"\xab\xcd\xefMaxMind.com"
DB_NAME = "dbip-country-lite.mmdb"
DB_URL = "https://download.db-ip.com/free/dbip-country-lite-{ym}.mmdb.gz"
MAX_AGE = 35 * 86400
ATTRIBUTION = 'IP-Geolocation von <a href="https://db-ip.com" target="_blank" rel="noopener">DB-IP</a> (CC BY 4.0)'


class Reader:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.buf = f.read()
        pos = self.buf.rfind(MARKER, max(0, len(self.buf) - 128 * 1024))
        if pos < 0:
            raise ValueError("keine MMDB-Datei")
        self.meta, _ = self._decode(pos + len(MARKER), pos + len(MARKER))
        self.nodes = self.meta["node_count"]
        self.rsize = self.meta["record_size"]
        if self.rsize not in (24, 28, 32):
            raise ValueError("unbekannte record_size")
        self.tree_size = self.rsize * 2 // 8 * self.nodes
        self.data_start = self.tree_size + 16
        self.v4_start = 0
        if self.meta.get("ip_version") == 6:
            node = 0
            for _ in range(96):
                if node >= self.nodes:
                    break
                node = self._record(node, 0)
            self.v4_start = node

    # ------------------------------------------------------------ Suchbaum
    def _record(self, node, bit):
        b = self.buf
        if self.rsize == 24:
            o = node * 6 + bit * 3
            return int.from_bytes(b[o:o + 3], "big")
        if self.rsize == 28:
            o = node * 7
            if bit == 0:
                return ((b[o + 3] & 0xF0) << 20) | int.from_bytes(b[o:o + 3], "big")
            return ((b[o + 3] & 0x0F) << 24) | int.from_bytes(b[o + 4:o + 7], "big")
        o = node * 8 + bit * 4
        return int.from_bytes(b[o:o + 4], "big")

    def lookup(self, ip):
        addr = ipaddress.ip_address(ip)
        if addr.version == 6 and addr.ipv4_mapped:
            addr = addr.ipv4_mapped
        if addr.version == 6 and self.meta.get("ip_version") != 6:
            return None
        packed, bits = addr.packed, addr.max_prefixlen
        node = self.v4_start if addr.version == 4 else 0
        for i in range(bits):
            if node >= self.nodes:
                break
            node = self._record(node, (packed[i >> 3] >> (7 - (i & 7))) & 1)
        if node <= self.nodes:   # == nodes: nicht gefunden
            return None
        off = node - self.nodes - 16 + self.data_start
        return self._decode(off, self.data_start)[0]

    # ------------------------------------------------------------ Datenbereich
    def _decode(self, off, base):
        b = self.buf
        ctrl = b[off]
        off += 1
        typ = ctrl >> 5
        if typ == 1:   # Zeiger
            ss, v = (ctrl >> 3) & 3, ctrl & 7
            if ss == 0:
                p = (v << 8) | b[off]
            elif ss == 1:
                p = ((v << 16) | int.from_bytes(b[off:off + 2], "big")) + 2048
            elif ss == 2:
                p = ((v << 24) | int.from_bytes(b[off:off + 3], "big")) + 526336
            else:
                p = int.from_bytes(b[off:off + 4], "big")
            val, _ = self._decode(base + p, base)
            return val, off + ss + 1
        if typ == 0:
            typ = 7 + b[off]
            off += 1
        size = ctrl & 0x1F
        if size >= 29:
            n = size - 28
            ext = int.from_bytes(b[off:off + n], "big")
            off += n
            size = {29: 29, 30: 285, 31: 65821}[size] + ext
        if typ == 2:
            return b[off:off + size].decode("utf-8", "replace"), off + size
        if typ == 3:
            return struct.unpack(">d", b[off:off + 8])[0], off + 8
        if typ == 4:
            return bytes(b[off:off + size]), off + size
        if typ in (5, 6, 9, 10):
            return int.from_bytes(b[off:off + size], "big"), off + size
        if typ == 7:
            out = {}
            for _ in range(size):
                k, off = self._decode(off, base)
                out[k], off = self._decode(off, base)
            return out, off
        if typ == 8:
            return int.from_bytes(b[off:off + size].rjust(4, b"\0"), "big", signed=True), off + size
        if typ == 11:
            arr = []
            for _ in range(size):
                v, off = self._decode(off, base)
                arr.append(v)
            return arr, off
        if typ == 14:
            return bool(size), off
        if typ == 15:
            return struct.unpack(">f", b[off:off + 4])[0], off + 4
        return None, off


# ---------------------------------------------------------------- oeffentliche Funktionen
_reader = None
_reader_mtime = 0
_lock = threading.Lock()
_dir = "/config/geoip"


def init(config_dir):
    global _dir
    _dir = os.path.join(config_dir, "geoip")
    os.makedirs(_dir, exist_ok=True)


def db_path():
    """Eigene Datei des Benutzers hat Vorrang (GeoLite2-Country.mmdb oder *.mmdb), sonst DB-IP Lite."""
    try:
        files = sorted(f for f in os.listdir(_dir) if f.endswith(".mmdb"))
    except OSError:
        return None
    for pref in ("GeoLite2-Country.mmdb", DB_NAME):
        if pref in files:
            return os.path.join(_dir, pref)
    return os.path.join(_dir, files[0]) if files else None


def _get_reader():
    global _reader, _reader_mtime
    path = db_path()
    if not path:
        return None
    with _lock:
        m = os.path.getmtime(path)
        if _reader is None or m != _reader_mtime:
            try:
                _reader, _reader_mtime = Reader(path), m
            except (OSError, ValueError, KeyError, IndexError):
                _reader = None
        return _reader


def flag(iso):
    if not iso or len(iso) != 2 or not iso.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso.upper())


def locate(ip):
    """Liefert {"iso": "DE", "name": "Deutschland", "flag": "🇩🇪"} bzw. Lokales Netz / unbekannt."""
    try:
        addr = ipaddress.ip_address((ip or "").strip())
    except ValueError:
        return {"iso": "", "name": "unbekannt", "flag": ""}
    if addr.version == 6 and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
        return {"iso": "LAN", "name": "Lokales Netz", "flag": "🏠"}
    r = _get_reader()
    if not r:
        return {"iso": "", "name": "", "flag": ""}
    try:
        rec = r.lookup(str(addr)) or {}
    except (ValueError, IndexError, KeyError):
        rec = {}
    c = rec.get("country") or rec.get("registered_country") or {}
    iso = c.get("iso_code", "")
    names = c.get("names", {})
    lang = i18n.current()
    return {"iso": iso, "name": names.get(lang) or names.get("en") or names.get("de") or iso or i18n.t("unbekannt"), "flag": flag(iso)}


def status():
    path = db_path()
    if not path:
        return {"ok": False, "file": None, "date": None, "own": False}
    r = _get_reader()
    built = None
    if r and r.meta.get("build_epoch"):
        built = time.strftime("%d.%m.%Y", time.localtime(r.meta["build_epoch"]))
    return {"ok": bool(r), "file": os.path.basename(path), "date": built,
            "own": os.path.basename(path) != DB_NAME, "type": r.meta.get("database_type") if r else None}


INTERVALS = (1, 7, 14, 30, 60, 90)   # waehlbare Erneuerung in Tagen


def update(force=False, days=None):
    """DB-IP Lite herunterladen, wenn sie fehlt oder aelter als `days` Tage (Standard 35) ist. Liefert Fehlertext oder None."""
    path = os.path.join(_dir, DB_NAME)
    max_age = int(days) * 86400 - 3600 if days else MAX_AGE   # 1 h Spielraum, damit die taegliche Pruefung nicht knapp verpasst
    if not force and os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
        return None
    today = datetime.date.today()
    prev = (today.replace(day=1) - datetime.timedelta(days=1))
    last = None
    for d in (today, prev):
        url = DB_URL.format(ym=d.strftime("%Y-%m"))
        tmp = path + ".download"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MirrorSync"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(tmp + ".gz", "wb") as f:
                shutil.copyfileobj(resp, f)
            with gzip.open(tmp + ".gz") as g, open(tmp, "wb") as f:
                shutil.copyfileobj(g, f)
            Reader(tmp)   # pruefen, bevor die alte Datei ersetzt wird
            os.replace(tmp, path)
            return None
        except Exception as e:   # noqa: BLE001 - Netzfehler, 404 im neuen Monat usw.
            last = f"{url}: {e}"
        finally:
            for t in (tmp, tmp + ".gz"):
                try:
                    os.remove(t)
                except OSError:
                    pass
    return last
