"""Zugriffsschutz nach IP-Adresse: Sperrliste, Erlaubt-Liste, Laender, automatische Sperre nach Fehlversuchen."""
import datetime
import ipaddress
import json
import os
import re
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

PRIVATE_NETS = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7", "fe80::/10"]
DEFAULTS = {
    "allow": [],                 # leer = alle Adressen erlaubt; sonst nur diese (IP oder Netz, "# Kommentar" erlaubt)
    "block": [],                 # [{"net", "note", "added", "until" (leer = dauerhaft), "by"}]
    "country_mode": "off",       # off / allow (nur diese Laender) / block (diese Laender sperren)
    "countries": [],
    "auto_attempts": "10",       # 0 = aus
    "auto_minutes": "60",        # 0 = dauerhaft
    "auto_window": "60",         # Fehlversuche innerhalb von so vielen Minuten zaehlen
    "auto_exempt_lan": True,
    "notify": True,
}
_lock = threading.RLock()


HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,61}[a-z0-9]\.?$")
DNS_TTL = 300        # Sekunden: so lange gilt eine Aufloesung
DNS_TTL_FAIL = 60    # nicht aufloesbar: nach so vielen Sekunden neu versuchen
DNS_TIMEOUT = 3
_dns = {}            # host -> (gueltig bis, frozenset(ip_address), fehler)
_dns_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="dns")


def entry_text(text):
    return (text or "").split("#", 1)[0].strip()


def parse_host(text):
    """Hostname (FQDN) wie 'von.google.de' -> klein geschrieben ohne Punkt am Ende, sonst None."""
    t = entry_text(text).lower().rstrip(".")
    if not t or "/" in t or ":" in t:
        return None
    try:
        ipaddress.ip_address(t)
        return None
    except ValueError:
        pass
    return t if HOST_RE.match(t) else None


def parse_net(text):
    """'1.2.3.4' / '10.0.0.0/8' / '2001:db8::/32' -> ip_network oder ValueError."""
    t = entry_text(text)
    if not t:
        raise ValueError("leer")
    return ipaddress.ip_network(t, strict=False)


def parse_entry(text):
    """Eintrag fuer Sperr-/Erlaubt-Liste: Netz/IP (ip_network) oder Hostname (str). Sonst ValueError."""
    host = parse_host(text)
    if host:
        return host
    return parse_net(text)


def _lookup(host):
    out = set()
    for fam, _, _, _, sa in socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP):
        try:
            a = ipaddress.ip_address(sa[0].split("%", 1)[0])
            out.add(a.ipv4_mapped if a.version == 6 and a.ipv4_mapped else a)
        except ValueError:
            continue
    return frozenset(out)


def resolve(host, force=False):
    """Adressen eines Hostnamens (mit kurzem Cache). Liefert (frozenset, fehlertext)."""
    now = time.time()
    hit = _dns.get(host)
    if hit and hit[0] > now and not force:
        return hit[1], hit[2]
    try:
        ips = _dns_pool.submit(_lookup, host).result(timeout=DNS_TIMEOUT)
        err = "" if ips else "keine Adresse"
    except Exception as e:   # Timeout, NXDOMAIN, kein DNS
        ips, err = (hit[1] if hit else frozenset()), (str(e) or e.__class__.__name__)
    _dns[host] = (now + (DNS_TTL if ips and not err else DNS_TTL_FAIL), ips, err)
    if len(_dns) > 2000:
        _dns.clear()
    return ips, err


def entry_matches(a, text):
    """Passt die Adresse a auf einen Listeneintrag (IP, Netz oder Hostname)?"""
    host = parse_host(text)
    if host:
        return a in resolve(host)[0]
    return a in parse_net(text)


def _addr(ip):
    a = ipaddress.ip_address((ip or "").strip())
    if a.version == 6 and a.ipv4_mapped:
        a = a.ipv4_mapped
    return a


def is_lan(ip):
    try:
        a = _addr(ip)
    except ValueError:
        return False
    return a.is_private or a.is_loopback or a.is_link_local


def now_str():
    return time.strftime("%Y-%m-%dT%H:%M")


def active_block(entry, now=None):
    until = (entry.get("until") or "").strip()
    return not until or until > (now or now_str())


class Guard:
    def __init__(self, db):
        self.db = db
        self.hits = {}           # net -> (Anzahl, letzte Zeit), nur im Speicher
        self.fails = {}          # ip -> [Zeitstempel]

    def load(self):
        with _lock:
            data = json.loads(json.dumps(DEFAULTS))
            data.update(self.db.get_map("ipguard"))
            return data

    def save(self, data):
        with _lock:
            self.db.put_map("ipguard", data)

    def reset(self):
        self.save(json.loads(json.dumps(DEFAULTS)))

    # ------------------------------------------------------------ Entscheidung
    def check(self, ip, country_iso=None, cfg=None):
        """Liefert None (erlaubt) oder (Grund, Regel). country_iso: Funktion ip -> ISO-Code oder ''."""
        cfg = cfg or self.load()
        try:
            a = _addr(ip)
        except ValueError:
            return None
        if a.is_loopback:   # Healthcheck im Container
            return None
        now = now_str()
        for e in cfg.get("block", []):
            try:
                if active_block(e, now) and entry_matches(a, e["net"]):
                    return ("Sperrliste", e["net"])
            except (ValueError, KeyError):
                continue
        allow = [x for x in cfg.get("allow", []) if x.split("#", 1)[0].strip()]
        if allow:
            ok = False
            for x in allow:
                try:
                    if entry_matches(a, x):
                        ok = True
                        break
                except ValueError:
                    continue
            if not ok:
                return ("nicht in der Erlaubt-Liste", "Erlaubt-Liste")
        mode = cfg.get("country_mode", "off")
        codes = {c.upper() for c in cfg.get("countries", [])}
        if mode in ("allow", "block") and codes and not is_lan(ip) and country_iso:
            iso = (country_iso(ip) or "").upper()
            if iso:   # ohne Datenbank oder unbekanntes Land: nicht sperren
                if mode == "allow" and iso not in codes:
                    return (f"Land {iso} nicht erlaubt", "Länder")
                if mode == "block" and iso in codes:
                    return (f"Land {iso} gesperrt", "Länder")
        return None

    def hit(self, rule):
        n, _ = self.hits.get(rule, (0, ""))
        self.hits[rule] = (n + 1, time.strftime("%d.%m. %H:%M"))

    # ------------------------------------------------------------ Sperrliste bearbeiten
    def add_block(self, net, note="", minutes=0, by=""):
        n = str(parse_entry(net))
        if n.endswith("/32") or n.endswith("/128"):
            n = n.rsplit("/", 1)[0]
        until = ""
        if minutes:
            until = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M")
        with _lock:
            cfg = self.load()
            cfg["block"] = [e for e in cfg.get("block", []) if e.get("net") != n]
            cfg["block"].insert(0, {"net": n, "note": note[:120], "added": time.strftime("%Y-%m-%d %H:%M"),
                                    "until": until, "by": by})
            self.save(cfg)
        return n, until

    def remove_block(self, net):
        with _lock:
            cfg = self.load()
            cfg["block"] = [e for e in cfg.get("block", []) if e.get("net") != net]
            self.save(cfg)

    def prune(self):
        """Abgelaufene Zeitsperren entfernen."""
        with _lock:
            cfg = self.load()
            keep = [e for e in cfg.get("block", []) if active_block(e)]
            if len(keep) != len(cfg.get("block", [])):
                cfg["block"] = keep
                self.save(cfg)

    # ------------------------------------------------------------ automatische Sperre
    def register_fail(self, ip):
        """Fehlversuch zaehlen. Liefert (net, until) wenn die IP jetzt gesperrt wurde, sonst None."""
        cfg = self.load()
        try:
            attempts = int(cfg.get("auto_attempts") or 0)
            minutes = int(cfg.get("auto_minutes") or 0)
            window = max(1, int(cfg.get("auto_window") or 60)) * 60
        except ValueError:
            return None
        if attempts <= 0 or not ip:
            return None
        try:
            if _addr(ip).is_loopback:
                return None
        except ValueError:
            return None
        if cfg.get("auto_exempt_lan") and is_lan(ip):
            return None
        t = time.time()
        with _lock:
            lst = [x for x in self.fails.get(ip, []) if t - x < window] + [t]
            self.fails[ip] = lst
            if len(lst) < attempts:
                return None
            self.fails.pop(ip, None)
        mins = f"{minutes} Minuten" if minutes else "dauerhaft"
        return self.add_block(ip, note=f"automatisch: {attempts} Fehlversuche ({mins})", minutes=minutes, by="automatisch")
