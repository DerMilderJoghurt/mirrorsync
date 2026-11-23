"""Dateimanager (ab 1.27.0): in einem oder zwei Speicherorten browsen, Groessen und Berechtigungen ansehen,
Dateien bearbeiten, hochladen, herunterladen, umbenennen, loeschen, kopieren und verschieben.

Alles laeuft ueber rclone, damit jeder Speichertyp funktioniert. Die GUI ruft /files/op/<op> (JSON) auf,
REST-API und MCP gehen ueber apigui.gui() durch dieselben Routen: gleiche Rechte, Sichtbarkeit und Audit-Log.
Kopieren und Verschieben laufen im Hintergrund als Auftrag mit Fortschritt (auch zwischen zwei Speicherorten)."""
import base64
import difflib
import json
import os
import posixpath
import re
import secrets
import subprocess
import threading
import time

from flask import Response, g, jsonify, request, stream_with_context

core = None
LOCAL = "/data"
TEXT_MAX = 1024 * 1024          # Bearbeiten im Editor
READ_MAX = 5 * 1024 * 1024      # Lesen per API (base64)
LIST_MAX = 5000
TASKS_KEEP = 50

OP_PERMS = {"locations": "files.view", "list": "files.view", "size": "files.view", "info": "files.view",
            "read": "files.view", "tasks": "files.view",
            "mkdir": "files.edit", "write": "files.edit", "rename": "files.edit", "copy": "files.edit",
            "move": "files.edit", "cancel": "files.edit", "remove_tasks": "files.edit", "delete": "files.delete"}

_tasks = {}
_tlock = threading.Lock()


class FileError(Exception):
    def __init__(self, status, msg, **extra):
        super().__init__(msg)
        self.status, self.msg, self.extra = status, msg, extra


# ---------------------------------------------------------------- Pfade und Rechte
def locations():
    """Speicherorte, die der Benutzer sehen darf, plus /data mit Recht local.paths."""
    out = [{"id": r["name"], "label": r["name"], "type": r["type"]}
           for r in core.list_remotes() if g.access.remote_ok(r["name"])]
    if g.access.has("local.paths") and os.path.isdir(LOCAL):
        out.append({"id": LOCAL, "label": LOCAL, "type": "local"})
    return out


def _clean(rel):
    rel = str(rel or "").replace("\\", "/")
    if "\x00" in rel:
        raise FileError(400, "Ungültiger Pfad.")
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise FileError(400, "Ungültiger Pfad.")
    return "/".join(parts)


def resolve(loc, rel=""):
    """(rclone-Pfad, bereinigter relativer Pfad, Anzeige) oder FileError."""
    loc = str(loc or "").strip()
    rel = _clean(rel)
    if loc in (LOCAL, LOCAL + "/"):
        if not g.access.has("local.paths"):
            raise FileError(403, "Deine Rolle darf lokale Ordner (/data) nicht verwenden.")
        full = LOCAL + ("/" + rel if rel else "")
        return full, rel, full
    name = loc.rstrip(":")
    r = next((x for x in core.list_remotes() if x["name"] == name), None)
    if not r or not g.access.remote_ok(name):
        raise FileError(404, "Speicherort nicht gefunden.")
    base = name + (":/" if r["type"] in core.ABS_ROOT_TYPES else ":")
    return base + rel, rel, f"{name}:/{rel}"


def _rc(*args, timeout=120, data=None):
    cmd = ["rclone", "--config", core.RCLONE_CONF, *args]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, input=data)
    except subprocess.TimeoutExpired:
        raise FileError(504, "Zeitüberschreitung bei rclone.")
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


def _err(stderr, path):
    msg, detail = core.friendly_error(stderr, path)
    return FileError(502, msg, detail=detail)


def _stat(full):
    """Eintrag zu einem Pfad oder None, wenn es ihn nicht gibt."""
    rc, out, err = _rc("lsjson", "--stat", "-M", "--no-mimetype", full, timeout=60)
    if rc != 0:
        if "not found" in err.lower() or "doesn't exist" in err.lower() or "no such" in err.lower() or rc == 3:
            return None
        raise _err(err, full)
    try:
        return json.loads(out or b"null")
    except ValueError:
        return None


def mode_text(meta):
    """'mode' aus den rclone-Metadaten (z. B. 100644) als rwxr-xr-x."""
    m = (meta or {}).get("mode")
    if not m:
        return ""
    try:
        v = int(str(m), 8)
    except ValueError:
        return str(m)
    s = "d" if v & 0o040000 else ("l" if (v & 0o170000) == 0o120000 else "-")
    for shift in (6, 3, 0):
        b = (v >> shift) & 7
        s += ("r" if b & 4 else "-") + ("w" if b & 2 else "-") + ("x" if b & 1 else "-")
    return s


def _entry(it):
    mod = (it.get("ModTime") or "")[:19]
    meta = it.get("Metadata") or {}
    return {"name": it.get("Name", ""), "dir": bool(it.get("IsDir")),
            "size": None if it.get("IsDir") or it.get("Size", -1) < 0 else it.get("Size"),
            "mod": mod.replace("T", " ") if mod and not mod.startswith("2000-01-01") else "",
            "mode": mode_text(meta), "owner": ":".join(x for x in (meta.get("uid", ""), meta.get("gid", "")) if x)}


def _child(rel, name):
    name = str(name or "").strip()
    if not name or "/" in name or "\\" in name or name in (".", "..") or "\x00" in name:
        raise FileError(400, "Ungültiger Name.")
    return (rel + "/" if rel else "") + name


def _audit(action, target, detail="", info=None):
    core.audit_add("files", action, target, detail=detail, info=info)


_SECRET_LINE = re.compile(r"((?:pass\w*|secret\w*|token\w*|\w*key\w*|auth\w*|bearer)\s*[:=]\s*).+", re.I)


def _dir_listing(full, limit=200):
    """Dateien in einem Ordner (fuer das Audit-Log vor dem Loeschen): (Anzahl, erste `limit` Pfade)."""
    try:
        rc, out, _ = _rc("lsf", "-R", "--files-only", full, timeout=60)
    except Exception:   # noqa: BLE001
        return None, []
    if rc != 0:
        return None, []
    if isinstance(out, bytes):
        out = out.decode("utf-8", "replace")
    names = [x for x in out.splitlines() if x.strip()]
    return len(names), names[:limit]


# ---------------------------------------------------------------- Operationen
def op_locations(a):
    return {"ok": True, "locations": locations()}


def op_list(a):
    full, rel, disp = resolve(a.get("loc"), a.get("path"))
    rc, out, err = _rc("lsjson", "--max-depth", "1", "-M", "--no-mimetype", full, timeout=90)
    if rc != 0:
        raise _err(err, full)
    try:
        items = json.loads(out or b"[]")
    except ValueError:
        raise FileError(502, "Antwort von rclone nicht lesbar.")
    items.sort(key=lambda it: (not it.get("IsDir"), (it.get("Name") or "").lower()))
    return {"ok": True, "loc": a.get("loc"), "path": rel, "display": disp, "entries": [_entry(it) for it in items[:LIST_MAX]],
            "total": len(items), "truncated": len(items) > LIST_MAX}


def op_size(a):
    """Groesse, Anzahl Dateien und Unterordner (rekursiv) in einem Durchlauf, zeilenweise gelesen."""
    full, rel, disp = resolve(a.get("loc"), a.get("path"))
    cmd = ["rclone", "--config", core.RCLONE_CONF, "lsf", "-R", "--format", "sp", "--separator", "\t", full]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    files = dirs = total = 0
    t0 = time.time()
    for line in p.stdout:
        sz, _, path = line.rstrip("\n").partition("\t")
        if path.endswith("/"):
            dirs += 1
        else:
            files += 1
            try:
                total += max(int(sz), 0)
            except ValueError:
                pass
        if time.time() - t0 > 1800:
            p.kill()
            raise FileError(504, "Zeitüberschreitung bei rclone.")
    err = p.stderr.read()
    if p.wait() != 0:
        raise _err(err, full)
    return {"ok": True, "path": rel, "count": files, "files": files, "dirs": dirs, "bytes": total}


def op_info(a):
    full, rel, disp = resolve(a.get("loc"), a.get("path"))
    it = _stat(full) if rel else {"Name": "", "IsDir": True}
    if it is None:
        raise FileError(404, "Datei oder Ordner nicht gefunden.")
    e = _entry(it)
    meta = {k: v for k, v in (it.get("Metadata") or {}).items() if k in ("mode", "uid", "gid", "atime", "mtime", "btime")}
    return {"ok": True, "path": rel, "display": disp, **e, "metadata": meta,
            "hint": None if e["mode"] else "Dieser Speichertyp liefert keine Berechtigungen (z. B. SMB, WebDAV, Clouds)."}


def op_read(a):
    full, rel, disp = resolve(a.get("loc"), a.get("path"))
    it = _stat(full)
    if it is None or it.get("IsDir"):
        raise FileError(404, "Datei nicht gefunden.")
    binary = str(a.get("binary", "")).lower() in ("1", "true", "yes", "on")
    limit = READ_MAX if binary else TEXT_MAX
    if (it.get("Size") or 0) > limit:
        raise FileError(413, "Die Datei ist zu groß zum Anzeigen (höchstens {0} MB).".format(limit // 1048576))
    rc, out, err = _rc("cat", full, timeout=120)
    if rc != 0:
        raise _err(err, full)
    if binary:
        return {"ok": True, "path": rel, "size": len(out), "content_base64": base64.b64encode(out).decode()}
    try:
        text = out.decode("utf-8")
    except UnicodeDecodeError:
        raise FileError(415, "Keine Textdatei (nicht UTF-8). Herunterladen geht trotzdem.")
    return {"ok": True, "path": rel, "size": len(out), "mod": _entry(it)["mod"], "content": text}


def _write(full, data):
    rc, out, err = _rc("rcat", full, timeout=600, data=data)
    if rc != 0:
        raise _err(err, full)


def op_write(a):
    """Textdatei speichern. Neue Datei: name + path (Ordner). Bestehende ueberschreiben nur mit overwrite."""
    if a.get("name"):
        full, rel, disp = resolve(a.get("loc"), _child(_clean(a.get("path")), a.get("name")))
    else:
        full, rel, disp = resolve(a.get("loc"), a.get("path"))
    if not rel:
        raise FileError(400, "Ungültiger Name.")
    if "content_base64" in a:
        try:
            data = base64.b64decode(a.get("content_base64") or "", validate=True)
        except Exception:
            raise FileError(400, "content_base64 ist kein gültiges Base64.")
    else:
        data = str(a.get("content") or "").encode("utf-8")
    old = _stat(full)
    if old and old.get("IsDir"):
        raise FileError(409, "Dort gibt es schon einen Ordner mit diesem Namen.")
    if old and not _yes(a.get("overwrite")):
        raise FileError(409, "„{0}“ gibt es schon. Überschreiben?", exists=True, name=rel.rsplit("/", 1)[-1])
    info = {"Pfad": disp, "Größe neu": f"{len(data)} Bytes"}
    if old:
        info["Größe vorher"] = f"{old.get('Size', 0)} Bytes"
        if 0 <= int(old.get("Size") or 0) <= 512 * 1024 and len(data) <= 512 * 1024:
            try:
                prev = subprocess.run(["rclone", "--config", core.RCLONE_CONF, "cat", full], capture_output=True, timeout=60).stdout
                a_l, b_l = prev.decode("utf-8", "replace").splitlines(), data.decode("utf-8", "replace").splitlines()
                sm = difflib.SequenceMatcher(None, a_l, b_l, autojunk=False)
                plus = sum(j2 - j1 for op, i1, i2, j1, j2 in sm.get_opcodes() if op in ("insert", "replace"))
                minus = sum(i2 - i1 for op, i1, i2, j1, j2 in sm.get_opcodes() if op in ("delete", "replace"))
                info["Zeilen"] = f"+{plus} / −{minus}"
                lines = [_SECRET_LINE.sub(r"\1•••", ln[:300]) for ln in difflib.unified_diff(a_l, b_l, lineterm="", n=1)][2:80]
                if lines:
                    info["Änderung (Auszug)"] = "\n".join(lines)
            except Exception:   # noqa: BLE001 - Audit darf das Speichern nicht verhindern
                pass
    _write(full, data)
    _audit("Datei bearbeitet" if old else "Datei angelegt", disp, f"{len(data)} Bytes", info)
    return {"ok": True, "path": rel, "message": "Gespeichert."}


def upload(loc, path, fname, stream, overwrite):
    full, rel, disp = resolve(loc, _child(_clean(path), os.path.basename(fname or "")))
    old = _stat(full)
    if old and old.get("IsDir"):
        raise FileError(409, "Dort gibt es schon einen Ordner mit diesem Namen.")
    if old and not overwrite:
        raise FileError(409, "„{0}“ gibt es schon. Überschreiben?", exists=True, name=rel.rsplit("/", 1)[-1])
    cmd = ["rclone", "--config", core.RCLONE_CONF, "rcat", full]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    n = 0
    try:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            n += len(chunk)
            p.stdin.write(chunk)
        p.stdin.close()
        err = p.stderr.read().decode("utf-8", "replace")
        rc = p.wait(timeout=600)
    except Exception:
        p.kill()
        raise FileError(502, "Hochladen abgebrochen.")
    if rc != 0:
        raise _err(err, full)
    _audit("Datei hochgeladen (überschrieben)" if old else "Datei hochgeladen", disp, f"{n} Bytes")
    return {"ok": True, "path": rel, "size": n}


def op_mkdir(a):
    full, rel, disp = resolve(a.get("loc"), _child(_clean(a.get("path")), a.get("name")))
    if _stat(full):
        raise FileError(409, "„{0}“ gibt es schon.", name=a.get("name"))
    rc, out, err = _rc("mkdir", full, timeout=60)
    if rc != 0:
        raise _err(err, full)
    _audit("Ordner angelegt", disp, info={"Pfad": disp})
    return {"ok": True, "path": rel, "message": "Ordner angelegt."}


def _yes(v):
    return v is True or str(v).strip().lower() in ("1", "true", "yes", "ja", "on")


def op_delete(a):
    if not _yes(a.get("confirm")):
        raise FileError(400, "Zum Löschen confirm=true mitschicken.")
    paths = a.get("paths") if isinstance(a.get("paths"), list) else [a.get("path")]
    done = []
    for p in paths:
        full, rel, disp = resolve(a.get("loc"), p)
        if not rel:
            raise FileError(400, "Den obersten Ordner eines Speicherorts kann man nicht löschen.")
        it = _stat(full)
        if it is None:
            raise FileError(404, "„{0}“ nicht gefunden.", name=rel)
        info = {"Pfad": disp, "Geändert": (it.get("ModTime") or "")[:19].replace("T", " ")}
        if it.get("IsDir"):
            n, names = _dir_listing(full)
            if n is not None:
                info["Enthaltene Dateien"] = n
                info["Dateien"] = "\n".join(names) + ("\n…" if n > len(names) else "")
            rc, out, err = _rc("purge", full, timeout=3600)
        else:
            info["Größe"] = f"{it.get('Size', 0)} Bytes"
            rc, out, err = _rc("deletefile", full, timeout=300)
        if rc != 0:
            raise _err(err, full)
        _audit("Ordner gelöscht" if it.get("IsDir") else "Datei gelöscht", disp,
               "" if it.get("IsDir") else f"{it.get('Size', 0)} Bytes", info)
        done.append(rel)
    return {"ok": True, "deleted": done, "message": "Gelöscht."}


def op_rename(a):
    full, rel, disp = resolve(a.get("loc"), a.get("path"))
    if not rel:
        raise FileError(400, "Ungültiger Pfad.")
    parent = rel.rsplit("/", 1)[0] if "/" in rel else ""
    nfull, nrel, ndisp = resolve(a.get("loc"), _child(parent, a.get("new_name")))
    it = _stat(full)
    if it is None:
        raise FileError(404, "„{0}“ nicht gefunden.", name=rel)
    if nrel == rel:
        return {"ok": True, "path": rel}
    if _stat(nfull) and nrel.lower() != rel.lower():
        raise FileError(409, "„{0}“ gibt es schon.", name=a.get("new_name"))
    rc, out, err = _rc("moveto", full, nfull, timeout=3600)
    if rc != 0:
        raise _err(err, full)
    if it.get("IsDir"):
        _rc("rmdirs", full, timeout=300)
    _audit("Umbenannt", disp, f"→ {ndisp}", {"Vorher": disp, "Nachher": ndisp})
    return {"ok": True, "path": nrel, "message": "Umbenannt."}


# ---------------------------------------------------------------- Kopieren/Verschieben im Hintergrund
def _transfer(a, move):
    if move and not g.access.has("files.delete"):
        raise FileError(403, "Verschieben braucht zusätzlich das Recht „Dateien löschen“.")
    src_loc = a.get("loc") or a.get("src_loc")
    dst_loc = a.get("dst_loc") or src_loc
    paths = a.get("paths") if isinstance(a.get("paths"), list) else [a.get("path")]
    dst_dir = _clean(a.get("dst_path"))
    resolve(dst_loc, dst_dir)
    jobs, conflicts = [], []
    for p in paths:
        sfull, srel, sdisp = resolve(src_loc, p)
        if not srel:
            raise FileError(400, "Den obersten Ordner eines Speicherorts kann man nicht verschieben oder kopieren.")
        it = _stat(sfull)
        if it is None:
            raise FileError(404, "„{0}“ nicht gefunden.", name=srel)
        name = a.get("new_name") if len(paths) == 1 and a.get("new_name") else srel.rsplit("/", 1)[-1]
        dfull, drel, ddisp = resolve(dst_loc, _child(dst_dir, name))
        if sfull == dfull:
            raise FileError(400, "Quelle und Ziel sind gleich.")
        if it.get("IsDir") and (dfull + "/").startswith(sfull.rstrip("/") + "/"):
            raise FileError(400, "Ein Ordner kann nicht in sich selbst kopiert oder verschoben werden.")
        if _stat(dfull):
            conflicts.append(name)
        jobs.append((sfull, sdisp, dfull, ddisp, bool(it.get("IsDir")), int(it.get("Size") or 0)))
    if conflicts and not _yes(a.get("overwrite")):
        raise FileError(409, "Im Ziel gibt es schon: {0}. Überschreiben?", exists=True, name=", ".join(conflicts))
    tid = secrets.token_hex(4)
    t = {"id": tid, "op": "move" if move else "copy", "user": g.user, "items": [(j[1], j[3]) for j in jobs],
         "label": (jobs[0][1] if len(jobs) == 1 else f"{len(jobs)} Einträge") + " → " + resolve(dst_loc, dst_dir)[2],
         "state": "läuft", "progress": 0, "stats": "", "error": "", "started": time.strftime("%Y-%m-%d %H:%M:%S"),
         "ended": "", "detail": "", "proc": None, "cancel": False, "overwrite": bool(conflicts),
         # Gesamtfortschritt ueber alle Eintraege (Bytes und Dateien), Tempo in Bytes/s, Restzeit in Sekunden
         "phase": "", "bytes_done": 0, "bytes_total": None, "files_done": 0, "files_total": None,
         "speed": 0, "eta": None, "item": 0, "items": len(jobs), "current": ""}
    with _tlock:
        _tasks[tid] = t
        for old in sorted(_tasks, key=lambda k: _tasks[k]["started"])[:-TASKS_KEEP]:
            if _tasks[old]["state"] != "läuft":
                _tasks.pop(old, None)
    ip = core._client_ip()
    threading.Thread(target=_run_task, args=(t, jobs, move, ip), daemon=True).start()
    return {"ok": True, "task": _task_view(t), "message": "Verschieben gestartet." if move else "Kopieren gestartet."}


STATS_RE = re.compile(r"(\d+)%")


def _count(jobs, t):
    """Im Hintergrund zaehlen: Groesse und Anzahl Dateien je Eintrag (Ordner per rclone size), danach die Summe.
    Das Kopieren startet sofort, die Summe kommt dazu, sobald sie feststeht."""
    sizes = []
    for sfull, _sd, _df, _dd, is_dir, size in jobs:
        if t["cancel"] or t["state"] != "läuft":
            return
        if not is_dir:
            sizes.append((size, 1))
        else:
            try:
                rc, out, _e = _rc("size", "--json", sfull, timeout=900)
                d = json.loads(out) if rc == 0 else None
            except (FileError, ValueError):
                d = None
            sizes.append((int(d.get("bytes") or 0), int(d.get("count") or 0)) if d else (None, None))
        t["_sizes"] = list(sizes)
    if all(b is not None for b, _ in sizes):
        t["bytes_total"] = sum(b for b, _ in sizes)
        t["files_total"] = sum(n for _, n in sizes)


def _update(t, base_b, base_f, item_b, item_f, st):
    """Stand eines rclone-Laufs (stats aus --use-json-log) in den Gesamtfortschritt umrechnen."""
    b = int(st.get("bytes") or 0)
    f = int(st.get("transfers") or 0) + int(st.get("checks") or 0)
    if item_b is not None:
        b = min(b, item_b)
    if item_f is not None:
        f = min(f, item_f)
    t["bytes_done"], t["files_done"] = base_b + b, base_f + f
    t["speed"] = int(st.get("speed") or 0)
    if t["bytes_total"]:
        t["progress"] = min(99, int(t["bytes_done"] * 100 / t["bytes_total"]))
        left = t["bytes_total"] - t["bytes_done"]
        t["eta"] = int(left / t["speed"]) if t["speed"] > 0 else None
    elif st.get("totalBytes"):
        t["progress"] = min(99, int(int(st.get("bytes") or 0) * 100 / int(st["totalBytes"])))
        t["eta"] = st.get("eta")


def _run_task(t, jobs, move, ip):
    threading.Thread(target=_count, args=(jobs, t), daemon=True).start()
    t["phase"] = "move" if move else "copy"
    base_b = base_f = 0
    for idx, (sfull, sdisp, dfull, ddisp, is_dir, _size) in enumerate(jobs):
        if t["cancel"]:
            break
        sizes = t.get("_sizes") or []
        item_b, item_f = sizes[idx] if idx < len(sizes) else ((_size, 1) if not is_dir else (None, None))
        last = {}
        t["item"], t["current"] = idx + 1, sdisp
        verb = ("move" if move else "copy") if is_dir else ("moveto" if move else "copyto")
        cmd = ["rclone", "--config", core.RCLONE_CONF, verb, sfull, dfull, "--use-json-log",
               "--stats", "1s", "--stats-one-line", "--stats-log-level", "NOTICE"]
        if move and is_dir:
            cmd.append("--delete-empty-src-dirs")
        if is_dir:
            cmd += core.SPEED_FLAGS[core.speed_of(core.load_settings(), "files_speed")]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        t["proc"] = p
        tail = []
        for line in p.stderr:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                ev = {"msg": re.sub(r"^\d{4}/\d\d/\d\d \d\d:\d\d:\d\d\s+", "", line)}
            msg = str(ev.get("msg") or "").strip()
            if isinstance(ev.get("stats"), dict):
                t["stats"] = msg
                last = ev["stats"]
                _update(t, base_b, base_f, item_b, item_f, last)
            elif msg:
                tail = (tail + [msg])[-5:]
        rc = p.wait()
        if rc == 0 and move and is_dir:
            subprocess.run(["rclone", "--config", core.RCLONE_CONF, "rmdirs", sfull], capture_output=True, timeout=300)
        if rc == 0:   # Eintrag fertig: ganz zaehlen (auch uebersprungene, schon gleiche Dateien)
            sizes = t.get("_sizes") or []
            item_b, item_f = sizes[idx] if idx < len(sizes) else (item_b, item_f)
            base_b += item_b if item_b is not None else int(last.get("bytes") or 0)
            base_f += item_f if item_f is not None else int(last.get("transfers") or 0) + int(last.get("checks") or 0)
            t["bytes_done"], t["files_done"] = max(t["bytes_done"], base_b), max(t["files_done"], base_f)
            if t["bytes_total"]:
                t["progress"] = min(99, int(t["bytes_done"] * 100 / t["bytes_total"])) if idx + 1 < len(jobs) else t["progress"]
        if t["cancel"]:
            t["state"], t["error"] = "abgebrochen", ""
        elif rc != 0:
            t["state"] = "fehler"
            t["error"], t["detail"] = core.friendly_error("\n".join(tail), sfull)
        try:
            with core.app.test_request_context(environ_base={"REMOTE_ADDR": ip}):
                act = {(False, "ok"): "Kopiert", (True, "ok"): "Verschoben", (False, "ow"): "Kopiert (überschrieben)",
                       (True, "ow"): "Verschoben (überschrieben)", (False, "err"): "Kopieren fehlgeschlagen",
                       (True, "err"): "Verschieben fehlgeschlagen", (False, "stop"): "Kopieren abgebrochen",
                       (True, "stop"): "Verschieben abgebrochen"}[(move, "stop" if t["cancel"] else ("err" if rc != 0 else
                                                                                         ("ow" if t["overwrite"] else "ok")))]
                core.audit_add("files", act, sdisp, detail=f"→ {ddisp}", user=t["user"],
                               info={"Von": sdisp, "Nach": ddisp, "Fortschritt": f"{t.get('progress', 0)} %",
                                     "Statistik": t.get("stats", ""), "Fehler": t.get("error", ""),
                                     "Gestartet": t.get("started", ""), "Über": "Dateimanager"})
        except Exception as e:   # Audit darf den Auftrag nicht abbrechen
            print(f"Audit Dateimanager: {e}", flush=True)
        if t["state"] != "läuft":
            break
    if t["state"] == "läuft":
        t["state"], t["progress"], t["eta"], t["speed"] = "ok", 100, 0, 0
        if t["bytes_total"] is not None:
            t["bytes_done"], t["files_done"] = t["bytes_total"], t["files_total"]
    t["phase"] = ""
    t["ended"] = time.strftime("%Y-%m-%d %H:%M:%S")
    t["proc"] = None


def _task_view(t):
    return {k: v for k, v in t.items() if k not in ("proc", "cancel") and not k.startswith("_")}


def _mine(t):
    return g.access.admin or (t["user"] or "").lower() == (g.user or "").lower()


def op_copy(a):
    return _transfer(a, False)


def op_move(a):
    return _transfer(a, True)


def op_tasks(a):
    with _tlock:
        ts = [_task_view(t) for t in _tasks.values() if _mine(t)]
    return {"ok": True, "tasks": sorted(ts, key=lambda x: x["started"], reverse=True)}


def op_cancel(a):
    t = _tasks.get(str(a.get("task_id") or ""))
    if not t or not _mine(t):
        raise FileError(404, "Auftrag nicht gefunden.")
    if t["state"] == "läuft":
        t["cancel"] = True
        p = t.get("proc")
        if p:
            p.terminate()
    return {"ok": True, "task": _task_view(t), "message": "Abgebrochen."}


def op_remove_tasks(a):
    """Fertige Auftraege aus der Liste entfernen: task_id (einer) oder finished=true (alle fertigen)."""
    tid = str(a.get("task_id") or "")
    with _tlock:
        if tid:
            t = _tasks.get(tid)
            if not t or not _mine(t):
                raise FileError(404, "Auftrag nicht gefunden.")
            if t["state"] == "läuft":
                raise FileError(409, "Der Auftrag läuft noch. Erst abbrechen, dann entfernen.")
            ids = [tid]
        elif _yes(a.get("finished")):
            ids = [k for k, t in _tasks.items() if _mine(t) and t["state"] != "läuft"]
        else:
            raise FileError(400, "task_id oder finished=true angeben.")
        for k in ids:
            _tasks.pop(k, None)
    return {"ok": True, "removed": len(ids), "message": "Entfernt."}


OPS = {"locations": op_locations, "list": op_list, "size": op_size, "info": op_info, "read": op_read, "write": op_write,
       "mkdir": op_mkdir, "delete": op_delete, "rename": op_rename, "copy": op_copy, "move": op_move,
       "tasks": op_tasks, "cancel": op_cancel, "remove_tasks": op_remove_tasks}


def _fail(e):
    body = {"ok": False, "error": core.i18n.t(e.msg, e.extra.get("name", "")) if "{0}" in e.msg else e.msg}
    body.update({k: v for k, v in e.extra.items()})
    return jsonify(body), e.status


# ---------------------------------------------------------------- Routen
def register(app, core_module):
    global core
    core = core_module
    core.ENDPOINT_PERMS.update({"files_page": "files.view", "files_download": "files.view", "files_upload": "files.edit"})

    @app.get("/files")
    def files_page():
        return core.render_template("files.html", locations=locations(), can_local=g.access.has("local.paths"))

    @app.post("/files/op/<op>")
    def files_op(op):
        fn = OPS.get(op)
        if not fn:
            return jsonify({"ok": False, "error": "Unbekannte Aktion."}), 404
        a = request.get_json(silent=True)
        if not isinstance(a, dict):
            a = request.form.to_dict()
        try:
            return jsonify(fn(a))
        except FileError as e:
            return _fail(e)

    @app.post("/files/upload")
    def files_upload():
        f = request.files.get("file")
        if not f or not f.filename:
            return jsonify({"ok": False, "error": "Keine Datei."}), 400
        try:
            return jsonify(upload(request.form.get("loc"), request.form.get("path"), f.filename, f.stream,
                                  _yes(request.form.get("overwrite"))))
        except FileError as e:
            return _fail(e)

    @app.get("/files/download")
    def files_download():
        try:
            full, rel, disp = resolve(request.args.get("loc"), request.args.get("path"))
            it = _stat(full) if rel else None
            if not it or it.get("IsDir"):
                raise FileError(404, "Datei nicht gefunden.")
        except FileError as e:
            return _fail(e)
        p = subprocess.Popen(["rclone", "--config", core.RCLONE_CONF, "cat", full], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)

        def gen():
            try:
                while True:
                    chunk = p.stdout.read(256 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                p.kill()
        name = rel.rsplit("/", 1)[-1]
        from urllib.parse import quote
        _audit("Datei heruntergeladen", disp, f"{it.get('Size', 0)} Bytes")
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"}
        if (it.get("Size") or -1) >= 0:
            headers["Content-Length"] = str(it["Size"])
        return Response(stream_with_context(gen()), mimetype="application/octet-stream", headers=headers,
                        direct_passthrough=True)
