"""Selbst-Update ueber den Docker-Socket (optional).

Nur aktiv, wenn /var/run/docker.sock in den Container eingebunden ist. Ablauf:
1. MirrorSync holt das Image neu (gleicher Name und Tag wie der laufende Container, z. B. :latest).
2. Ist es neuer, startet MirrorSync einen kurzlebigen Hilfs-Container aus dem NEUEN Image
   (python selfupdate.py --helper <alter-container>), denn ein Container kann sich nicht selbst ersetzen.
3. Der Helfer stoppt den alten Container, benennt ihn um, legt einen neuen mit identischer Konfiguration an
   (Name, Ports, Volumes, Umgebungsvariablen, Netzwerke mit fester IP/MAC, Labels inkl. Docker-Compose,
   Neustart-Regel …) und startet ihn.
4. Antwortet der neue Container auf /health, wird der alte geloescht. Sonst wird der neue entfernt und der alte
   wieder gestartet (Rollback).
Der Stand steht in <CONFIG_DIR>/selfupdate.json und erscheint in der GUI und im Audit-Log.
"""
import http.client
import json
import os
import re
import socket
import sys
import time
import urllib.parse

SOCK = os.environ.get("DOCKER_SOCK", "/var/run/docker.sock")
CONFIG_DIR = os.environ.get("CONFIG_DIR", "/config")
STATE_FILE = os.path.join(CONFIG_DIR, "selfupdate.json")
HELPER_LABEL = "mirrorsync.selfupdate"
HEALTH_WAIT = 120   # Sekunden, die der neue Container fuer /health bekommt


class DockerError(Exception):
    pass


class _UnixConn(http.client.HTTPConnection):
    def __init__(self, path, timeout=60):
        super().__init__("localhost", timeout=timeout)
        self._path = path

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self._path)
        self.sock = s


class Docker:
    """Sehr kleiner Client fuer die Docker Engine API ueber den Unix-Socket (ohne Zusatzpakete)."""

    def __init__(self, path=SOCK):
        self.path = path
        self.api = None

    def _raw(self, method, url, body=None, timeout=60, stream=False):
        conn = _UnixConn(self.path, timeout=timeout)
        headers = {"Host": "docker"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        conn.request(method, url, body=data, headers=headers)
        r = conn.getresponse()
        raw = r.read()
        conn.close()
        return r.status, raw

    def req(self, method, path, body=None, params=None, timeout=60, ok=(200, 201, 204, 304)):
        if self.api is None:
            st, raw = self._raw("GET", "/version", timeout=10)
            if st != 200:
                raise DockerError(f"Docker antwortet nicht ({st}).")
            v = json.loads(raw)
            self.api = v.get("ApiVersion") or "1.41"
        q = ("?" + urllib.parse.urlencode(params)) if params else ""
        st, raw = self._raw(method, f"/v{self.api}{path}{q}", body, timeout)
        if st not in ok:
            try:
                msg = json.loads(raw).get("message") or raw.decode(errors="replace")
            except ValueError:
                msg = raw.decode(errors="replace")
            raise DockerError(f"{method} {path}: {st} {msg.strip()}")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return raw.decode(errors="replace")

    def api_at_least(self, ver):
        if self.api is None:
            self.req("GET", "/_ping")
        a = tuple(int(x) for x in str(self.api).split("."))
        return a >= tuple(int(x) for x in ver.split("."))

    def pull(self, ref):
        """Image holen. Docker meldet Fehler im Datenstrom, nicht im Status."""
        name, tag = split_ref(ref)
        out = self.req("POST", "/images/create", params={"fromImage": name, "tag": tag}, timeout=900)
        text = out if isinstance(out, str) else json.dumps(out or "")
        for line in text.splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if isinstance(d, dict) and d.get("error"):
                raise DockerError(d.get("error"))

    def exec_ok(self, cid, cmd, timeout=15):
        e = self.req("POST", f"/containers/{cid}/exec", {"Cmd": cmd, "AttachStdout": True, "AttachStderr": True})
        self.req("POST", f"/exec/{e['Id']}/start", {"Detach": False, "Tty": False}, timeout=timeout)
        return (self.req("GET", f"/exec/{e['Id']}/json") or {}).get("ExitCode") == 0


def split_ref(ref):
    """'ghcr.io/a/b:latest' -> ('ghcr.io/a/b', 'latest'); Digest-Angaben bleiben vollstaendig."""
    if "@" in ref:
        return ref, ""
    last = ref.rsplit("/", 1)[-1]
    if ":" in last:
        name, tag = ref.rsplit(":", 1)
        return name, tag
    return ref, "latest"


def available():
    """(ok, grund). ok nur, wenn der Socket da ist und Docker antwortet."""
    if not os.path.exists(SOCK):
        return False, "socket"
    try:
        Docker().req("GET", "/_ping")
        return True, ""
    except (OSError, DockerError) as e:
        return False, str(e)


def own_id():
    """ID des eigenen Containers: aus mountinfo (/etc/hostname usw.), sonst aus dem Hostnamen."""
    try:
        with open("/proc/self/mountinfo", encoding="utf-8") as f:
            m = re.search(r"/containers/([0-9a-f]{64})/", f.read())
            if m:
                return m.group(1)
    except OSError:
        pass
    try:
        with open("/proc/self/cgroup", encoding="utf-8") as f:
            m = re.search(r"([0-9a-f]{64})", f.read())
            if m:
                return m.group(1)
    except OSError:
        pass
    return socket.gethostname()


def info():
    """Was weiss Docker ueber diesen Container? Fuer GUI und API."""
    ok, why = available()
    out = {"available": ok, "reason": why, "state": read_state()}
    if not ok:
        return out
    try:
        d = Docker()
        c = d.req("GET", f"/containers/{own_id()}/json")
        ref = c["Config"]["Image"]
        out.update(container=c["Name"].lstrip("/"), image=ref, image_id=c["Image"],
                   compose_project=(c["Config"].get("Labels") or {}).get("com.docker.compose.project", ""))
        name, tag = split_ref(ref)
        out["pinned"] = bool(re.fullmatch(r"v?\d+(\.\d+){1,2}", tag or ""))
        out["local_only"] = "/" not in name and "." not in name.split("/")[0]
    except (OSError, DockerError, KeyError) as e:
        out.update(available=False, reason=str(e))
    return out


def read_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_state(st):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE_FILE)


def start(by, from_version):
    """Image holen und, wenn es neuer ist, den Hilfs-Container starten.
    Liefert (status, text): status = started | current | error."""
    d = Docker()
    me = d.req("GET", f"/containers/{own_id()}/json")
    for h in d.req("GET", "/containers/json", params={"filters": json.dumps({"label": [HELPER_LABEL]})}) or []:
        if h.get("State") == "running":
            return "error", "Es läuft schon ein Update."
    ref = me["Config"]["Image"]
    # Konfiguration des bisherigen Images merken, bevor das Pull es ueberschreibt: Damit erkennt der Helfer spaeter,
    # welche Umgebungsvariablen und Labels aus dem Image stammen und welche du gesetzt hast.
    try:
        old_cfg = (d.req("GET", f"/images/{me['Image']}/json") or {}).get("Config") or {}
    except DockerError:
        old_cfg = None
    if ref.startswith("sha256:"):
        return "error", "Der Container wurde mit einer Image-ID statt einem Image-Namen gestartet, so kann MirrorSync kein neues Image holen."
    try:
        d.pull(ref)
    except DockerError as e:
        return "error", f"Image {ref} konnte nicht geladen werden: {e}"
    new = d.req("GET", f"/images/{urllib.parse.quote(ref, safe='')}/json")
    if new["Id"] == me["Image"]:
        return "current", ref
    cfg_src = next((m for m in me.get("Mounts") or [] if m.get("Destination") == CONFIG_DIR), None)
    if not cfg_src:
        return "error", f"{CONFIG_DIR} ist kein Volume, der Stand des Updates könnte nicht gespeichert werden."
    cfg_bind = (cfg_src["Source"] if cfg_src.get("Type") == "bind" else cfg_src["Name"]) + ":" + CONFIG_DIR
    sock_src = next((m["Source"] for m in me.get("Mounts") or [] if m.get("Destination") == SOCK), SOCK)
    write_state({"state": "running", "by": by, "from_version": from_version, "image": ref, "old_image_config": old_cfg,
                 "started": time.strftime("%Y-%m-%d %H:%M:%S"), "log": ["Neues Image geladen, Update startet."]})
    helper = d.req("POST", "/containers/create", {
        "Image": new["Id"], "Entrypoint": ["python", "/app/selfupdate.py", "--helper", me["Id"]], "Cmd": [],
        "Labels": {HELPER_LABEL: me["Id"][:12]}, "Env": [f"CONFIG_DIR={CONFIG_DIR}", f"DOCKER_SOCK={SOCK}"],
        "Healthcheck": {"Test": ["NONE"]},
        "HostConfig": {"AutoRemove": True, "NetworkMode": "none", "Binds": [f"{sock_src}:{SOCK}", cfg_bind]},
    }, params={"name": f"{me['Name'].lstrip('/')}-updater-{int(time.time())}"})
    d.req("POST", f"/containers/{helper['Id']}/start")
    return "started", ref


# ----------------------------------------------------------------- Hilfs-Container
def _same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# Variablen, die man typischerweise selbst setzt: ohne Daten zum alten Image bleiben sie immer erhalten
USER_ENV = {"TZ", "PORT", "CONFIG_DIR", "LOG_DIR", "PUBLIC_URL", "SETUP_TOKEN", "WEB_USER", "WEB_PASS", "ADMIN_RESET",
            "IPGUARD_RESET", "UPDATE_REPO", "MIRRORSYNC_ANDROID_CERTS", "DOCKER_SOCK"}


def build_create(old, old_cfg, new_img):
    """Konfiguration fuer den neuen Container aus dem alten ableiten. Was aus dem alten IMAGE stammte
    (Umgebung, Labels, Befehl …), kommt jetzt aus dem neuen Image; alles, was beim Anlegen gesetzt wurde, bleibt.
    old_cfg = Config des alten Images; fehlt sie (Image schon geloescht), wird am neuen Image abgeschaetzt."""
    c = json.loads(json.dumps(old["Config"]))
    nc = new_img.get("Config") or {}
    if old_cfg is not None:
        ic = old_cfg
        img_env = set(ic.get("Env") or [])
        c["Env"] = [e for e in c.get("Env") or [] if e not in img_env]
        img_lab = ic.get("Labels") or {}
        c["Labels"] = {k: v for k, v in (c.get("Labels") or {}).items() if img_lab.get(k) != v}
    else:
        ic = nc
        new_keys = {e.split("=", 1)[0] for e in nc.get("Env") or []}
        c["Env"] = [e for e in c.get("Env") or [] if e.split("=", 1)[0] not in new_keys or e.split("=", 1)[0] in USER_ENV
                    and e not in (nc.get("Env") or [])]
        img_lab = nc.get("Labels") or {}
        c["Labels"] = {k: v for k, v in (c.get("Labels") or {}).items()
                       if k not in img_lab and not k.startswith("org.opencontainers.image.")}
    for k in ("Cmd", "Entrypoint", "WorkingDir", "User", "Healthcheck", "StopSignal", "OnBuild", "Shell"):
        if k in c and _same(c.get(k), ic.get(k)):
            c.pop(k, None)
    if _same(c.get("Volumes"), ic.get("Volumes")):
        c.pop("Volumes", None)
    if _same(c.get("ExposedPorts"), ic.get("ExposedPorts")):
        c.pop("ExposedPorts", None)
    if c.get("Hostname") == old["Id"][:12]:
        c.pop("Hostname", None)
    c["Image"] = old["Config"]["Image"]
    hc = json.loads(json.dumps(old["HostConfig"]))
    # Anonyme Volumes (z. B. /config ohne eigenen Eintrag in der Compose-Datei) weiterverwenden, sonst waeren die Daten weg
    used = {b.split(":")[1] for b in hc.get("Binds") or [] if ":" in b} | {m.get("Target") for m in hc.get("Mounts") or []}
    for m in old.get("Mounts") or []:
        if m.get("Type") == "volume" and m.get("Destination") not in used and m.get("Name"):
            hc.setdefault("Binds", [])
            hc["Binds"] = (hc["Binds"] or []) + [f"{m['Name']}:{m['Destination']}" + ("" if m.get("RW", True) else ":ro")]
    c["HostConfig"] = hc
    nets = {}
    for name, ep in (old.get("NetworkSettings") or {}).get("Networks", {}).items():
        e = {k: ep.get(k) for k in ("IPAMConfig", "Links", "Aliases", "DriverOpts", "MacAddress", "GwPriority") if ep.get(k)}
        if e.get("Aliases"):
            e["Aliases"] = [a for a in e["Aliases"] if a != old["Id"][:12]] or None
            if not e["Aliases"]:
                e.pop("Aliases")
        nets[name] = e
    return c, nets


def compose_image_id(d, old, new_img):
    """Wert, den Docker Compose fuer das neue Image ins Label schreiben wuerde: die Image-ID, beim containerd-Speicher
    das Manifest der eigenen Plattform."""
    if (old["Config"].get("Labels") or {}).get("com.docker.compose.image") == old["Image"]:
        return new_img["Id"]
    try:
        if d.api_at_least("1.48"):
            v = d.req("GET", "/version")
            full = d.req("GET", f"/images/{urllib.parse.quote(old['Config']['Image'], safe='')}/json", params={"manifests": "1"})
            for m in full.get("Manifests") or []:
                p = (m.get("ImageData") or {}).get("Platform") or {}
                if m.get("Kind") == "image" and p.get("architecture") == v.get("Arch") and p.get("os") == v.get("Os"):
                    return m["ID"]
    except (DockerError, KeyError):
        pass
    return new_img["Id"]


class _Log:
    def __init__(self):
        self.st = read_state()
        self.st.setdefault("log", [])

    def __call__(self, text, **kw):
        print(text, flush=True)
        self.st["log"].append(time.strftime("%H:%M:%S ") + text)
        self.st.update(kw)
        try:
            write_state(self.st)
        except OSError:
            pass


def helper(old_id):
    log = _Log()
    try:
        d = Docker()
        old = d.req("GET", f"/containers/{old_id}/json")
        name = old["Name"].lstrip("/")
        old_cfg = log.st.get("old_image_config")
        if old_cfg is None:
            try:
                old_cfg = (d.req("GET", f"/images/{old['Image']}/json") or {}).get("Config") or {}
            except DockerError:
                old_cfg = None
        new_img = d.req("GET", f"/images/{urllib.parse.quote(old['Config']['Image'], safe='')}/json")
        log.st["to_version"] = (new_img.get("Config", {}).get("Labels") or {}).get("org.opencontainers.image.version", "")
        cfg, nets = build_create(old, old_cfg, new_img)
        labels = cfg.get("Labels") or {}
        if "com.docker.compose.image" in labels:
            # Docker Compose merkt sich das Image im Label; passt es nicht, legt "docker compose up" den Container neu an
            labels["com.docker.compose.image"] = compose_image_id(d, old, new_img)
    except Exception as e:  # noqa: BLE001 - nichts angefasst, alter Container laeuft weiter
        log(f"Fehler vor dem Austausch: {e}. Die bisherige Version läuft unverändert weiter.", state="failed", error=str(e),
            finished=time.strftime("%Y-%m-%d %H:%M:%S"))
        return 1
    backup = f"{name}-alt-{time.strftime('%Y%m%d-%H%M%S')}"
    new_id = None
    log("Alter Container wird gestoppt.")
    d.req("POST", f"/containers/{old_id}/stop", params={"t": 30}, timeout=90)
    try:
        d.req("POST", f"/containers/{old_id}/rename", params={"name": backup})
        names = list(nets)
        first = {names[0]: nets[names[0]]} if names else {}
        cfg["NetworkingConfig"] = {"EndpointsConfig": nets if d.api_at_least("1.44") else first}
        new_id = d.req("POST", "/containers/create", cfg, params={"name": name})["Id"]
        if not d.api_at_least("1.44"):
            for n in names[1:]:
                d.req("POST", f"/networks/{urllib.parse.quote(n, safe='')}/disconnect", {"Container": new_id, "Force": True},
                      ok=(200, 204, 404))
                d.req("POST", f"/networks/{urllib.parse.quote(n, safe='')}/connect", {"Container": new_id, "EndpointConfig": nets[n]})
        log("Neuer Container angelegt, er startet.")
        d.req("POST", f"/containers/{new_id}/start")
        port = next((e.split("=", 1)[1] for e in (cfg.get("Env") or []) + (new_img.get("Config", {}).get("Env") or [])
                     if e.startswith("PORT=")), "8080")
        url = f"http://127.0.0.1:{port}/health"
        until = time.time() + HEALTH_WAIT
        healthy = False
        while time.time() < until:
            time.sleep(3)
            st = (d.req("GET", f"/containers/{new_id}/json") or {}).get("State", {})
            if not st.get("Running") or st.get("Restarting"):
                raise DockerError(f"Der neue Container ist beendet (Exit-Code {st.get('ExitCode')})")
            try:
                if d.exec_ok(new_id, ["wget", "-qO-", url]):
                    healthy = True
                    break
            except DockerError:
                pass
        if not healthy:
            raise DockerError(f"Der neue Container hat in {HEALTH_WAIT} Sekunden nicht auf /health geantwortet")
        d.req("DELETE", f"/containers/{old_id}", params={"v": "false"})
        log("Update abgeschlossen, alter Container entfernt.", state="ok", finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:  # noqa: BLE001 - alles zurueckdrehen
        log(f"Fehler: {str(e).rstrip('.')}. Die bisherige Version wird wieder gestartet.")
        if new_id:
            try:
                logs = d.req("GET", f"/containers/{new_id}/logs", params={"stdout": 1, "stderr": 1, "tail": 20})
                if isinstance(logs, str):
                    log.st["new_logs"] = re.sub(r"[\x00-\x08]", "", logs)[-3000:]
            except DockerError:
                pass
            d.req("DELETE", f"/containers/{new_id}", params={"force": "true"}, ok=(200, 204, 404))
        try:
            d.req("POST", f"/containers/{old_id}/rename", params={"name": name})
            d.req("POST", f"/containers/{old_id}/start", ok=(200, 204, 304))
            log("Bisherige Version läuft wieder.", state="failed", error=str(e), finished=time.strftime("%Y-%m-%d %H:%M:%S"))
        except DockerError as e2:
            log(f"Zurückdrehen fehlgeschlagen: {e2}. Der alte Container heißt jetzt {backup}.", state="failed",
                error=f"{e}; {e2}", finished=time.strftime("%Y-%m-%d %H:%M:%S"))
        return 1
    return 0


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "--helper":
    sys.exit(helper(sys.argv[2]))
