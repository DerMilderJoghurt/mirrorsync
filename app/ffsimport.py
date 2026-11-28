"""FreeFileSync-Import (seit 1.58.0): .ffs_batch und .ffs_gui lesen und daraus Vorschlaege fuer Aufgaben machen.

Uebernommen werden: Ordnerpaare (links = Quelle, rechts = Ziel), Art (Spiegeln, Aktualisieren = ohne Loeschen,
Zwei-Wege), Vergleich (Zeit und Groesse, Inhalt, Groesse), verschobene Dateien erkennen, Papierkorb/Versionierung
(mit Anzahl und Alter), Ausschluesse und Groessenfilter. Windows-Pfade (C:\\..., \\\\NAS\\freigabe) kann MirrorSync
nicht direkt lesen: Sie werden ueber Pfad-Ersetzungen auf Speicherorte umgestellt (z. B. \\\\NAS\\daten = NAS:daten).
"""
import re
import xml.etree.ElementTree as ET

MAX_BYTES = 2 * 1024 * 1024
VARIANTS = {"mirror": ("mirror", False), "update": ("mirror", True), "twoway": ("bisync", False)}
COMPARE = {"timeandsize": "standard", "content": "checksum", "size": "size"}
UNITS = {"byte": "B", "kb": "K", "mb": "M", "gb": "G", "tb": "T"}


class ImportError_(Exception):
    pass


def _find(el, *names):
    for n in names:
        x = el.find(n) if el is not None else None
        if x is not None:
            return x
    return None


def _txt(el, default=""):
    return (el.text or "").strip() if el is not None and el.text else default


def _variant(sync):
    v = _txt(_find(sync, "Variant", "Differences")).lower()
    if not v:
        d = _find(sync, "Differences")
        if d is not None:
            v = "custom"
    return v


def _filters(flt, warn):
    out = {"excludes": [], "min_size": "", "max_size": ""}
    if flt is None:
        return out
    inc = [_txt(i) for i in flt.findall("Include/Item")]
    if not inc:   # aeltere Formate: ein Text mit Zeilen/Semikolons
        inc = [x for x in re.split(r"[\n;|]+", _txt(flt.find("Include"))) if x.strip()]
    if [x for x in inc if x.strip() not in ("*", "")]:
        warn.append("Include-Filter (nur bestimmte Dateien) werden nicht übernommen: " + ", ".join(inc[:5]))
    exc = [_txt(i) for i in flt.findall("Exclude/Item")]
    if not exc:
        exc = [x for x in re.split(r"[\n;|]+", _txt(flt.find("Exclude"))) if x.strip()]
    for e in exc:
        e = e.strip().replace("\\", "/")
        if not e:
            continue
        if e.startswith("*/") and "*" not in e[2:]:
            e = e[2:]                     # jeder Ordner bzw. jede Datei mit diesem Namen
        out["excludes"].append(e)
    for key, tag in (("min_size", "SizeMin"), ("max_size", "SizeMax")):
        el = flt.find(tag)
        if el is None:
            continue
        unit = (el.get("Unit") or "").lower()
        val = _txt(el, "0")
        if unit in UNITS and val.isdigit() and int(val) > 0:
            out[key] = val + (" " + UNITS[unit] + "B" if UNITS[unit] != "B" else " B")
    tm = flt.find("TimeSpan")
    if tm is not None and (tm.get("Type") or "None").lower() != "none":
        warn.append("Zeitfilter (nur Dateien der letzten Tage) wird nicht übernommen.")
    return out


def _versioning(sync, warn):
    pol = _txt(_find(sync, "DeletionPolicy", "Deletion")).lower()
    out = {"versioning": False, "versions_keep": "", "versions_days": ""}
    if pol in ("versioning", "recyclebin"):
        out["versioning"] = True
        vf = sync.find("VersioningFolder")
        if vf is not None:
            if (vf.get("MaxAge") or "").isdigit() and int(vf.get("MaxAge")) > 0:
                out["versions_days"] = vf.get("MaxAge")
            if (vf.get("MaxCount") or "").isdigit() and int(vf.get("MaxCount")) > 0:
                out["versions_keep"] = vf.get("MaxCount")
            if _txt(vf):
                warn.append("Eigener Versionen-Ordner wird nicht übernommen, MirrorSync legt sie neben dem Ziel unter <ziel>.versions ab.")
        if pol == "recyclebin":
            warn.append("Papierkorb von Windows wird zum Papierkorb von MirrorSync (Versionierung).")
    return out


def _sync_cfg(sync, warn):
    v = _variant(sync)
    direction, no_delete = VARIANTS.get(v, ("mirror", False))
    if v and v not in VARIANTS:
        warn.append("Eigene Sync-Regeln (Custom) werden als Spiegeln übernommen, bitte prüfen.")
    moved = _txt(_find(sync, "DetectMovedFiles")).lower() == "true"
    return dict({"direction": direction, "no_delete": no_delete, "track_renames": "modtime" if moved and direction == "mirror" and not no_delete else "off"},
                **_versioning(sync, warn))


def is_windows_path(p):
    return bool(re.match(r"^[A-Za-z]:[\\/]", p) or p.startswith("\\\\") or "%" in p or p.startswith("\\"))


def parse_mappings(text):
    """'\\\\NAS\\daten = NAS:daten' je Zeile -> [(von, nach)] (laengste zuerst)."""
    out = []
    for ln in str(text or "").splitlines():
        if "=" not in ln or ln.strip().startswith("#"):
            continue
        a, b = ln.split("=", 1)
        a, b = a.strip(), b.strip()
        if a and b:
            out.append((a, b))
    return sorted(out, key=lambda x: -len(x[0]))


def map_path(p, mappings, remotes=()):
    """Windows-/FFS-Pfad in einen MirrorSync-Pfad umwandeln. Liefert (pfad, ok)."""
    raw = (p or "").strip()
    for a, b in mappings:
        if raw.lower().replace("/", "\\").startswith(a.lower().replace("/", "\\")):
            rest = raw[len(a):].replace("\\", "/").strip("/")
            base = b.rstrip("/")
            return (base + ("/" if rest and not base.endswith(":") else "") + rest) if rest else b, True
    m = re.match(r"^\\\\([^\\]+)\\([^\\]+)(.*)$", raw)
    if m:   # \\HOST\freigabe\pfad -> HOST:freigabe/pfad, wenn es einen Speicherort mit diesem Namen gibt
        host, share, rest = m.groups()
        hit = next((r for r in remotes if r.lower() == host.lower()), None)
        if hit:
            rest = rest.replace("\\", "/").strip("/")
            return f"{hit}:{share}" + (f"/{rest}" if rest else ""), True
    if raw.startswith("sftp://") or raw.startswith("ftp://") or raw.lower().startswith(("gdrive:", "mtp:")):
        return raw, False
    if raw.startswith("/") and not raw.startswith("//"):
        return raw, True   # schon ein Pfad im Container
    return raw.replace("\\", "/") if not is_windows_path(raw) else raw, not is_windows_path(raw)


def parse(blob, filename="", remotes=(), mappings=None):
    """Datei lesen. Liefert {"name", "pairs": [Vorschlag], "warnings": [...]} oder wirft ImportError_."""
    if len(blob) > MAX_BYTES:
        raise ImportError_("Datei zu groß.")
    try:
        root = ET.fromstring(blob)
    except ET.ParseError as e:
        raise ImportError_(f"Keine gültige FreeFileSync-Datei (XML-Fehler: {e}).")
    if root.tag != "FreeFileSync":
        raise ImportError_("Keine FreeFileSync-Datei (.ffs_batch oder .ffs_gui).")
    warn = []
    base = re.sub(r"\.ffs_(batch|gui)$", "", (filename or "FreeFileSync").rsplit("/", 1)[-1].rsplit("\\", 1)[-1], flags=re.I) or "FreeFileSync"
    comp = _find(root, "Compare", "MainConfig/Comparison")
    sync = _find(root, "Synchronize", "MainConfig/SyncConfig")
    flt = _find(root, "Filter", "MainConfig/GlobalFilter")
    compare = COMPARE.get(_txt(_find(comp, "Variant")).lower(), "standard")
    g_sync = _sync_cfg(sync, warn) if sync is not None else {"direction": "mirror", "no_delete": False, "track_renames": "off",
                                                              "versioning": False, "versions_keep": "", "versions_days": ""}
    g_flt = _filters(flt, warn)
    pairs_el = root.findall("FolderPairs/Pair") or root.findall("MainConfig/FolderPairs/Pair")
    if not pairs_el:
        raise ImportError_("In der Datei stehen keine Ordnerpaare.")
    maps = parse_mappings(mappings) if isinstance(mappings, str) else (mappings or [])
    pairs = []
    for i, p in enumerate(pairs_el, 1):
        left, right = _txt(_find(p, "Left")), _txt(_find(p, "Right"))
        pw = []
        cfg = dict(g_sync)
        ls = _find(p, "Synchronize", "SyncConfig")
        if ls is not None and _variant(ls):
            loc = _sync_cfg(ls, pw)
            cfg.update(direction=loc["direction"], no_delete=loc["no_delete"], track_renames=loc["track_renames"])
            if _find(ls, "DeletionPolicy", "Deletion") is not None:
                cfg.update({k: loc[k] for k in ("versioning", "versions_keep", "versions_days")})
            if cfg["no_delete"] or cfg["direction"] != "mirror":
                cfg["track_renames"] = "off"
        lc = _find(p, "Compare", "CompConfig")
        cmp_ = COMPARE.get(_txt(_find(lc, "Variant")).lower(), compare) if lc is not None else compare
        f = dict(g_flt)
        lf = _find(p, "Filter", "LocalFilter")
        if lf is not None:
            more = _filters(lf, pw)
            f["excludes"] = g_flt["excludes"] + more["excludes"]
            f["min_size"] = more["min_size"] or g_flt["min_size"]
            f["max_size"] = more["max_size"] or g_flt["max_size"]
        src, ok_s = map_path(left, maps, remotes)
        dst, ok_d = map_path(right, maps, remotes)
        if not ok_s or not ok_d:
            pw.append("Windows-Pfad: bitte durch einen Speicherort ersetzen (Pfad-Ersetzungen oder direkt im Feld).")
        name = base if len(pairs_el) == 1 else f"{base} ({i})"
        pairs.append({"name": name, "left": left, "right": right, "source": src, "dest": dst, "ok": ok_s and ok_d,
                      "compare": cmp_, "excludes": "\n".join(f["excludes"]), "min_size": f["min_size"], "max_size": f["max_size"],
                      "warnings": pw, **cfg})
    return {"name": base, "pairs": pairs, "warnings": warn}


def job_fields(pair, trigger="manual", schedule="", enabled=False):
    """Vorschlag -> Felder fuer create_job (API) bzw. apply_job_form."""
    out = {k: pair[k] for k in ("name", "source", "dest", "direction", "no_delete", "track_renames", "versioning", "versions_keep",
                                "versions_days", "compare", "excludes", "min_size", "max_size") if k in pair}
    out.update(trigger=trigger if trigger in ("manual", "time") else "manual", enabled=bool(enabled),
               note="Importiert aus FreeFileSync: " + (pair.get("left") or "") + " → " + (pair.get("right") or ""))
    if out["trigger"] == "time":
        out["schedule"] = schedule or "0 3 * * *"
    if out.get("direction") == "bisync":
        out["no_delete"] = False
    out["max_delete"] = ""
    return out
