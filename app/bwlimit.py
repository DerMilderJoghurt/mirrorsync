"""Bandbreitenbegrenzung mit Zeitfenstern -> rclone --bwlimit Zeittabelle."""
import re


def _t(text, *a):
    try:
        import i18n
        return i18n.t(text, *a)
    except Exception:   # ausserhalb einer Anfrage oder ohne i18n
        return text.format(*a) if a else text

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
WEEK = 7 * 1440
EMPTY = {"up": "", "down": "", "rules": []}
TIME_RE = re.compile(r"^([01]?\d|2[0-4]):([0-5]\d)$")


def _mb(v):
    """'10' / '2,5' -> float MB/s, '' -> None (unbegrenzt). ValueError bei Unsinn."""
    v = str(v or "").strip().replace(",", ".")
    if not v:
        return None
    f = float(v)
    if f <= 0 or f > 100000:
        raise ValueError(v)
    return f


def _minutes(t):
    m = TIME_RE.match(str(t or "").strip())
    if not m:
        raise ValueError(t)
    h, mi = int(m.group(1)), int(m.group(2))
    if h == 24 and mi:
        raise ValueError(t)
    return h * 60 + mi


def _fmt(f):
    return "off" if f is None else f"{f:g}M"


def _value(up, down):
    u, d = _fmt(up), _fmt(down)
    return u if u == d else f"{u}:{d}"


def clean(cfg):
    """Prueft und normalisiert eine Konfiguration. Liefert (cfg, fehler)."""
    cfg = cfg if isinstance(cfg, dict) else {}
    out = {"up": "", "down": "", "rules": []}
    try:
        for k in ("up", "down"):
            f = _mb(cfg.get(k))
            out[k] = "" if f is None else f"{f:g}"
    except ValueError:
        return out, "Bandbreite außerhalb der Zeitfenster: bitte eine Zahl in MB/s eintragen oder leer lassen."
    for i, r in enumerate(cfg.get("rules") or [], 1):
        try:
            days = sorted({int(d) for d in r.get("days", []) if 0 <= int(d) <= 6})
            s, e = _minutes(r.get("start")), _minutes(r.get("end"))
            up, down = _mb(r.get("up")), _mb(r.get("down"))
        except (ValueError, TypeError, AttributeError):
            return out, f"Zeitfenster {i}: Uhrzeit (HH:MM) oder Bandbreite (Zahl in MB/s) ungültig."
        if not days:
            return out, f"Zeitfenster {i}: bitte mindestens einen Wochentag wählen."
        if s == e:
            return out, f"Zeitfenster {i}: Beginn und Ende sind gleich."
        out["rules"].append({"days": days, "start": f"{s // 60:02d}:{s % 60:02d}", "end": f"{e // 60:02d}:{e % 60:02d}",
                             "up": "" if up is None else f"{up:g}", "down": "" if down is None else f"{down:g}"})
    return out, None


def timetable(cfg):
    """rclone --bwlimit-Wert oder None, wenn nie begrenzt wird.
    Spaetere Zeitfenster gewinnen bei Ueberschneidung. Fenster mit Ende <= Beginn gehen ueber Mitternacht."""
    cfg, err = clean(cfg)
    if err:
        return None
    default = _value(_mb(cfg["up"]), _mb(cfg["down"]))
    if not cfg["rules"]:
        return None if default == "off" else default
    slots = [default] * WEEK
    for r in cfg["rules"]:
        val = _value(_mb(r["up"]), _mb(r["down"]))
        s, e = _minutes(r["start"]), _minutes(r["end"])
        length = (e - s) % 1440 or 1440
        for d in r["days"]:
            start = d * 1440 + s
            for m in range(start, start + length):
                slots[m % WEEK] = val
    if all(v == "off" for v in slots):
        return None
    if len(set(slots)) == 1:
        return slots[0]
    entries = []
    for m in range(WEEK):
        if slots[m] != slots[m - 1]:
            entries.append(f"{DAYS[m // 1440]}-{(m % 1440) // 60:02d}:{m % 60:02d},{slots[m]}")
    return " ".join(entries)


def _days_text(days):
    if days == list(range(7)):
        return _t("täglich")
    if days == list(range(5)):
        return _t("Mo–Fr")
    if days == [5, 6]:
        return _t("Sa–So")
    return ", ".join(_t(DAYS_DE[d]) for d in days)


UNITS = {"MB/s": 1, "Mbit/s": 8}   # gespeichert wird immer MB/s, angezeigt in der gewaehlten Einheit


def _show(v, unit):
    f = UNITS.get(unit, 1)
    return f"{round(float(v) * f, 3):g} {unit if unit in UNITS else 'MB/s'}"


def _rate(up, down, unit="MB/s"):
    u = _show(up, unit) if up else _t("unbegrenzt")
    d = _show(down, unit) if down else _t("unbegrenzt")
    return u if u == d else f"↑ {u} / ↓ {d}"


def describe(cfg, unit="MB/s"):
    cfg, err = clean(cfg)
    if err or timetable(cfg) is None:
        return _t("unbegrenzt")
    parts = [f"{_days_text(r['days'])} {r['start']}–{r['end']} {_rate(r['up'], r['down'], unit)}" for r in cfg["rules"]]
    rest = _rate(cfg["up"], cfg["down"], unit)
    if parts:
        parts.append(_t("sonst {0}", rest))
    else:
        parts.append(_t("immer {0}", rest))
    return ", ".join(parts)


def for_job(settings, job):
    """Effektive Konfiguration fuer eine Aufgabe."""
    mode = job.get("bw_mode", "global")
    if mode == "off":
        return dict(EMPTY)
    if mode == "custom":
        return job.get("bw") or dict(EMPTY)
    return settings.get("bw") or dict(EMPTY)


def convert(cfg, factor):
    """Alle Werte einer Konfiguration mit factor multiplizieren (z. B. Mbit/s -> MB/s = 1/8). Unsinn bleibt stehen, clean() meldet ihn."""
    def f(v):
        try:
            return "" if str(v or "").strip() == "" else f"{round(float(str(v).replace(',', '.')) * factor, 4):g}"
        except ValueError:
            return v
    cfg = dict(cfg or {})
    for k in ("up", "down"):
        cfg[k] = f(cfg.get(k))
    cfg["rules"] = [dict(r, up=f(r.get("up")), down=f(r.get("down"))) if isinstance(r, dict) else r for r in cfg.get("rules") or []]
    return cfg
