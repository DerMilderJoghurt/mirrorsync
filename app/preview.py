"""Vorschau: wie sieht das Ziel nach dem naechsten Lauf aus?

Aus den Listen von Quelle und Ziel (rclone lsjson -R, mit denselben Filtern wie beim echten Lauf) wird ein
Ordnerbaum des Ziels gebaut. Jeder Eintrag bekommt einen Status:
  new     wird neu angelegt bzw. kopiert
  update  wird aktualisiert (Groesse oder Aenderungszeit unterschiedlich)
  same    bleibt, wie es ist
  delete  wird im Ziel geloescht (Spiegeln: gibt es in der Quelle nicht)
  to_a    nur Zwei-Wege: liegt nur auf Seite B und wird nach A kopiert
Ordner bekommen zusaetzlich Zaehler fuer ihren gesamten Inhalt.
"""
import datetime

STATUSES = ("new", "update", "same", "delete", "to_a")
MAX_FILES = 3000      # so viele Dateien stehen hoechstens einzeln im Baum, Ordner und Zaehler immer vollstaendig
MAX_TEXT_LINES = 1500


def _ts(s):
    if not s:
        return None
    try:
        s = s.replace("Z", "+00:00")
        if "." in s:
            head, rest = s.split(".", 1)
            frac = "".join(ch for ch in rest if ch.isdigit())
            tz = rest[len(frac):]
            s = f"{head}.{frac[:6].ljust(6, '0')}{tz}"
        return datetime.datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def _differs(a, b, window=1.0):
    if a.get("Size", -1) != b.get("Size", -1):
        return True
    ta, tb = _ts(a.get("ModTime")), _ts(b.get("ModTime"))
    return ta is not None and tb is not None and abs(ta - tb) > window


def _index(items):
    out = {}
    for it in items or []:
        p = (it.get("Path") or "").strip("/")
        if p:
            out[p] = it
    return out


def _parents(path):
    parts = path.split("/")
    return ["/".join(parts[:i]) for i in range(1, len(parts))]


def compute(src_items, dst_items, mode="mirror", delete_extra=True):
    """Statusliste je Pfad -> (ist_ordner, status, groesse). mode: mirror | bisync."""
    src, dst = _index(src_items), _index(dst_items)
    out = {}
    for p, it in src.items():
        d = dst.get(p)
        is_dir = bool(it.get("IsDir"))
        if d is None:
            st = "new"
        elif is_dir or not _differs(it, d):
            st = "same"
        else:
            st = "update"
        out[p] = (is_dir, st, 0 if is_dir else int(it.get("Size") or 0))
    for p, it in dst.items():
        if p in out:
            continue
        is_dir = bool(it.get("IsDir"))
        if mode == "bisync":
            st = "to_a"
        else:
            st = "delete" if delete_extra else "same"
        out[p] = (is_dir, st, 0 if is_dir else int(it.get("Size") or 0))
    # Ordner, die nur implizit vorkommen (z. B. bei Speichern ohne echte Ordner wie S3)
    for p in list(out):
        for q in _parents(p):
            if q not in out:
                kids_state = out[p][1]
                out[q] = (True, "new" if kids_state == "new" else ("delete" if kids_state == "delete" else "same"), 0)
    return out


def build_tree(entries, max_files=MAX_FILES):
    """Verschachtelter Baum mit Zaehlern. Liefert (wurzel, abgeschnitten)."""
    root = {"n": "", "d": True, "s": "same", "c": {k: 0 for k in STATUSES}, "b": {k: 0 for k in STATUSES}, "ch": {}}
    files_shown = 0
    truncated = False
    for path in sorted(entries, key=lambda x: (x.count("/"), x.lower())):
        is_dir, st, size = entries[path]
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            node = node["ch"].setdefault(part, {"n": part, "d": True, "s": "same", "c": {k: 0 for k in STATUSES},
                                                 "b": {k: 0 for k in STATUSES}, "ch": {}})
        name = parts[-1]
        if is_dir:
            child = node["ch"].setdefault(name, {"n": name, "d": True, "s": st, "c": {k: 0 for k in STATUSES},
                                                  "b": {k: 0 for k in STATUSES}, "ch": {}})
            child["s"] = st
        else:
            if files_shown < max_files:
                node["ch"][name] = {"n": name, "d": False, "s": st, "size": size}
                files_shown += 1
            else:
                truncated = True
            # Zaehler in allen Ordnern darueber
            n = root
            n["c"][st] += 1
            n["b"][st] += size
            for part in parts[:-1]:
                n = n["ch"][part]
                n["c"][st] += 1
                n["b"][st] += size

    def finish(node):
        kids = list(node.get("ch", {}).values())
        kids.sort(key=lambda k: (not k["d"], k["n"].lower()))
        for k in kids:
            if k["d"]:
                finish(k)
        node["ch"] = kids
        return node
    return finish(root), truncated


def summary(entries):
    s = {"files": {k: 0 for k in STATUSES}, "bytes": {k: 0 for k in STATUSES}, "dirs": {k: 0 for k in STATUSES}}
    for is_dir, st, size in entries.values():
        if is_dir:
            s["dirs"][st] += 1
        else:
            s["files"][st] += 1
            s["bytes"][st] += size
    return s


MARK = {"new": "+", "update": "~", "same": " ", "delete": "-", "to_a": "<"}


def as_text(root, max_lines=MAX_TEXT_LINES):
    """Einfacher Textbaum (fuer API und MCP). + neu, ~ aktualisiert, - geloescht, < nach Seite A."""
    lines = []

    def walk(node, depth):
        for k in node["ch"]:
            if len(lines) >= max_lines:
                return
            lines.append(f"{MARK.get(k['s'], ' ')} {'  ' * depth}{k['n']}{'/' if k['d'] else ''}")
            if k["d"]:
                walk(k, depth + 1)
    walk(root, 0)
    if len(lines) >= max_lines:
        lines.append("…")
    return "\n".join(lines)
