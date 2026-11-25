"""Befehle ausfuehren: im Container (sh -c) oder per SSH auf dem Server eines SFTP-Speicherorts.

Fuer Skripte vor/nach dem Lauf, Snapshots am Ziel und das Schlafenlegen nach Wake-on-LAN. Die Zugangsdaten kommen
aus dem SFTP-Speicherort in rclone.conf (Host, Port, Benutzer, Passwort oder Schluessel), es muss nichts doppelt
eingetragen werden."""
import configparser
import os
import shlex
import subprocess

RCLONE_CONF = None      # von app.py gesetzt
OUT_MAX = 20000


def _conf():
    cp = configparser.RawConfigParser(strict=False)
    try:
        cp.read(RCLONE_CONF, encoding="utf-8")
    except (OSError, configparser.Error):
        pass
    return cp


def ssh_remotes():
    """Namen aller SFTP-Speicherorte (nur diese koennen Befehle per SSH ausfuehren)."""
    cp = _conf()
    return sorted(s for s in cp.sections() if cp.get(s, "type", fallback="") == "sftp")


def remote_of(path):
    """'NAS:/daten' -> 'NAS', lokale Pfade -> ''."""
    path = (path or "").strip()
    if not path or path.startswith("/") or ":" not in path:
        return ""
    return path.split(":", 1)[0]


def remote_info(name):
    """Host/Port/Typ eines Speicherorts (fuer Wake-on-LAN-Pruefung). None, wenn unbekannt."""
    cp = _conf()
    if not name or not cp.has_section(name):
        return None
    sec = dict(cp.items(name))
    typ = sec.get("type", "")
    host, port = sec.get("host", ""), sec.get("port", "")
    if typ == "webdav" and sec.get("url"):
        from urllib.parse import urlparse
        u = urlparse(sec["url"])
        host, port = u.hostname or "", str(u.port or (443 if u.scheme == "https" else 80))
    default_port = {"sftp": "22", "smb": "445", "ftp": "21"}.get(typ, "")
    return {"type": typ, "host": host, "port": int(port or default_port or 0) or None}


def _reveal(obscured):
    try:
        p = subprocess.run(["rclone", "reveal", obscured], capture_output=True, text=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _env_prefix(env):
    return "".join(f"export {k}={shlex.quote(str(v))}; " for k, v in (env or {}).items())


def run(target, command, timeout=600, env=None):
    """Fuehrt command aus. target = '' (im Container) oder Name eines SFTP-Speicherorts.
    Liefert (exitcode, ausgabe). Exitcode 124 = Zeitueberschreitung, 127 = nicht ausfuehrbar."""
    command = (command or "").strip()
    if not command:
        return 0, ""
    if not target:
        try:
            p = subprocess.run(["sh", "-c", command], capture_output=True, text=True, timeout=timeout,
                               env=dict(os.environ, **{k: str(v) for k, v in (env or {}).items()}))
            return p.returncode, (p.stdout + p.stderr)[-OUT_MAX:]
        except subprocess.TimeoutExpired:
            return 124, f"Zeitüberschreitung nach {timeout} s"
        except OSError as e:
            return 127, str(e)
    return _ssh(target, _env_prefix(env) + command, timeout)


def _ssh(name, command, timeout):
    cp = _conf()
    if not cp.has_section(name):
        return 127, f"Speicherort {name} gibt es nicht."
    sec = dict(cp.items(name))
    if sec.get("type") != "sftp":
        return 127, f"Speicherort {name} ist kein SFTP-Speicherort, per SSH geht nur SFTP."
    try:
        import io
        import paramiko
    except ImportError:
        return 127, "SSH-Bibliothek (paramiko) fehlt im Container. Bitte Image neu bauen."
    host = sec.get("host", "")
    if not host:
        return 127, f"Speicherort {name} hat keinen Host."
    kw = {"hostname": host, "port": int(sec.get("port") or 22), "username": sec.get("user") or "root",
          "timeout": 20, "banner_timeout": 20, "auth_timeout": 20, "allow_agent": False, "look_for_keys": False}
    key_pass = _reveal(sec["key_file_pass"]) if sec.get("key_file_pass") else None
    pkey = None
    try:
        if sec.get("key_pem"):
            pem = sec["key_pem"].replace("\\n", "\n")
            pkey = _load_key(paramiko, io.StringIO(pem), key_pass)
        elif sec.get("key_file"):
            path = os.path.expanduser(sec["key_file"])
            with open(path, encoding="utf-8") as fh:
                pkey = _load_key(paramiko, io.StringIO(fh.read()), key_pass)
    except Exception as e:  # noqa: BLE001
        return 127, f"SSH-Schlüssel von {name} nicht lesbar: {e}"
    if pkey:
        kw["pkey"] = pkey
    if sec.get("pass"):
        kw["password"] = _reveal(sec["pass"])
    client = paramiko.SSHClient()
    kh = sec.get("known_hosts_file")
    if kh and os.path.exists(os.path.expanduser(kh)):
        client.load_host_keys(os.path.expanduser(kh))
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    else:   # wie rclone ohne known_hosts_file: Hostschluessel nicht pruefen
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(**kw)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        stdin.close()
        chan = stdout.channel
        chan.settimeout(timeout)
        out = stdout.read().decode("utf-8", "replace") + stderr.read().decode("utf-8", "replace")
        return chan.recv_exit_status(), out[-OUT_MAX:]
    except TimeoutError:
        return 124, f"Zeitüberschreitung nach {timeout} s"
    except Exception as e:  # noqa: BLE001
        return 127, f"SSH zu {host}: {type(e).__name__}: {e}"
    finally:
        client.close()


def _load_key(paramiko, fh, password):
    import io
    text = fh.getvalue()
    last = None
    for cls in [getattr(paramiko, n) for n in ("Ed25519Key", "ECDSAKey", "RSAKey", "DSSKey") if hasattr(paramiko, n)]:
        try:
            return cls.from_private_key(io.StringIO(text), password=password)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last or ValueError("unbekanntes Schlüsselformat")
