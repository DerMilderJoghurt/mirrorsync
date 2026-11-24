"""Zeitfenster pro Aufgabe: automatische Starts nur zwischen start und end (an den gewaehlten Wochentagen).

cfg = {"start": "22:00", "end": "06:00", "days": [0, 1, 2, 3, 4, 5, 6], "mode": "finish" | "resume" | "stop"}
- Ein Fenster, dessen Ende vor dem Anfang liegt, geht ueber Mitternacht; der Wochentag zaehlt fuer den Anfang.
- start == end bedeutet: ganzer Tag (24 Stunden ab start).
- mode: finish = laufende Aufgabe darf zu Ende laufen; resume = am Fensterende anhalten und im naechsten Fenster
  weitermachen; stop = am Fensterende anhalten, erst der naechste regulaere Start laeuft wieder.
"""
import datetime
import re

MODES = ("finish", "resume", "stop")
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]
DAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def clean(raw):
    """Eingabe pruefen. Liefert (cfg oder None, fehlertext oder None)."""
    if not raw:
        return None, None
    start, end = str(raw.get("start") or "").strip(), str(raw.get("end") or "").strip()
    if not _TIME.match(start) or not _TIME.match(end):
        return None, "Zeitfenster: Beginn und Ende bitte als HH:MM angeben."
    days = raw.get("days")
    if days in (None, "", "all"):
        days = list(ALL_DAYS)
    if isinstance(days, str):
        days = [d for d in re.split(r"[,\s]+", days) if d]
    try:
        days = sorted({int(d) for d in days})
    except (TypeError, ValueError):
        return None, "Zeitfenster: Wochentage als Zahlen 0 (Montag) bis 6 (Sonntag)."
    if not days or any(d not in ALL_DAYS for d in days):
        return None, "Zeitfenster: mindestens einen Wochentag wählen (0 = Montag bis 6 = Sonntag)."
    mode = raw.get("mode") or "finish"
    if mode not in MODES:
        return None, "Zeitfenster: Verhalten am Ende ist finish, resume oder stop."
    return {"start": start, "end": end, "days": days, "mode": mode}, None


def _hm(s):
    h, m = s.split(":")
    return int(h), int(m)


def _span(cfg, day):
    """(anfang, ende) des Fensters, das am Datum day beginnt."""
    h, m = _hm(cfg["start"])
    a = datetime.datetime.combine(day, datetime.time(h, m))
    h, m = _hm(cfg["end"])
    e = datetime.datetime.combine(day, datetime.time(h, m))
    if e <= a:
        e += datetime.timedelta(days=1)
    return a, e


def current(cfg, now=None):
    """(anfang, ende) des gerade offenen Fensters oder None."""
    if not cfg:
        return None
    now = now or datetime.datetime.now()
    for back in (1, 0):
        day = now.date() - datetime.timedelta(days=back)
        if day.weekday() not in cfg["days"]:
            continue
        a, e = _span(cfg, day)
        if a <= now < e:
            return a, e
    return None


def inside(cfg, now=None):
    return not cfg or current(cfg, now) is not None


def next_open(cfg, now=None):
    """Beginn des naechsten Fensters (jetzt, wenn gerade offen)."""
    if not cfg:
        return None
    now = now or datetime.datetime.now()
    cur = current(cfg, now)
    if cur:
        return now
    for ahead in range(0, 8):
        day = now.date() + datetime.timedelta(days=ahead)
        if day.weekday() not in cfg["days"]:
            continue
        a, _ = _span(cfg, day)
        if a > now:
            return a
    return None


def days_text(days, tr=lambda x: x):
    days = sorted(days or ALL_DAYS)
    if days == ALL_DAYS:
        return tr("täglich")
    if days == [0, 1, 2, 3, 4]:
        return tr("Mo–Fr")
    return ", ".join(tr(DAY_NAMES[d]) for d in days)


def describe(cfg, tr=lambda x: x):
    """Kurzer Text wie „täglich 22:00–06:00“; tr uebersetzt die Wochentage."""
    if not cfg:
        return ""
    return f"{days_text(cfg['days'], tr)} {cfg['start']}–{cfg['end']}"
