"""MQTT fuer Home Assistant (seit 1.58.0): Status und Fortschritt aller Aufgaben live, mit automatischer Erkennung
(MQTT-Discovery) und auf Wunsch Befehlen (Start, Testlauf, Stopp, Wartungsmodus).

Themen (Basis = Einstellung mqtt_topic, Standard "mirrorsync"):
  <basis>/status                 online / offline (Last Will, behalten)
  <basis>/state                  JSON: laufende, wartende, fehlgeschlagene Aufgaben, Wartungsmodus
  <basis>/job/<id>/state         JSON: Status, Fortschritt, letzter Lauf, naechster Start
  <basis>/job/<id>/set           Befehle run | dry | verify | stop (nur mit mqtt_commands)
  <basis>/maintenance/set        ON | OFF (nur mit mqtt_commands)
Discovery-Konfiguration unter <praefix>/<komponente>/mirrorsync_<id>/<objekt>/config (behalten).
"""
import json
import re
import threading
import time

core = None
DEFAULTS = {"mqtt_enabled": False, "mqtt_host": "", "mqtt_port": "1883", "mqtt_tls": False, "mqtt_tls_insecure": False,
            "mqtt_user": "", "mqtt_password": "", "mqtt_topic": "mirrorsync", "mqtt_discovery": True,
            "mqtt_discovery_prefix": "homeassistant", "mqtt_interval": "10", "mqtt_commands": False, "mqtt_client_id": ""}
SECRET = ("mqtt_password",)
TOPIC_RE = re.compile(r"^[A-Za-z0-9_\-/]{1,80}$")
_lock = threading.RLock()
_state = {"client": None, "cfg": None, "connected": False, "error": "", "since": "", "sent": 0, "last": 0.0, "known": set()}
_wake = threading.Event()
_thread = None


def settings(s=None):
    s = s or core.load_settings()
    return {k: s.get(k, v) for k, v in DEFAULTS.items()}


def _cfg_key(c):
    return json.dumps({k: c[k] for k in c if k not in ("mqtt_interval",)}, sort_keys=True)


def status():
    """Verbindungsstatus fuer GUI/API (ohne Passwort)."""
    with _lock:
        return {"enabled": bool((_state["cfg"] or {}).get("mqtt_enabled")), "connected": _state["connected"],
                "error": _state["error"], "since": _state["since"], "messages": _state["sent"]}


def base():
    return ((_state["cfg"] or {}).get("mqtt_topic") or "mirrorsync").strip("/")


def _slug(v):
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(v))


# ---------------------------------------------------------------- Daten
STATUS_TEXT = {"ok": "OK", "fehler": "Fehler", "laeuft": "läuft", "gestoppt": "gestoppt", "abgebrochen": "abgebrochen",
               "freigabe": "Freigabe nötig", "wartet": "wartet", "pausiert": "pausiert", "noch_nie": "noch nie"}


def iso_time(v):
    """'2026-11-28 09:08:01', '28.11.2026 09:08' oder datetime -> ISO mit Zeitzone (fuer device_class timestamp)."""
    import datetime
    if not v:
        return None
    if isinstance(v, datetime.datetime):
        d = v
    else:
        d = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M"):
            try:
                d = datetime.datetime.strptime(str(v), fmt)
                break
            except ValueError:
                pass
        if d is None:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=core.TZINFO)
    return d.isoformat(timespec="seconds")


def job_state(jid, j, jobs=None):
    running = jid in core._running
    queued = core.queue_pos(jid)
    pct, stats = (0, "")
    if running and core._current_run.get(jid):
        pct, stats = core.run_progress(core.run_log_path(jid, core._current_run[jid]))
    h = (j.get("history") or [{}])[0]
    status = "laeuft" if running else ("wartet" if queued else (j.get("last_status") or "noch_nie"))
    if not running and not queued and core.is_paused(j):
        status = "pausiert"
    return {"name": j.get("name", jid), "status": status, "status_text": core.i18n.t(STATUS_TEXT.get(status, status), lang=core.i18n.default_lang),
            "running": running, "progress": pct if running else (100 if h.get("status") == "ok" else 0), "stats": stats,
            "queued": queued, "enabled": bool(j.get("enabled")), "paused": bool(core.is_paused(j)),
            "last_run": iso_time(j.get("last_run")), "last_status": j.get("last_status") or "",
            "last_duration": h.get("duration"), "last_copied": h.get("copied"), "last_deleted": h.get("deleted"),
            "last_errors": h.get("errors"), "last_bytes": h.get("bytes"), "next_run": iso_time(core.next_start(jobs or core.load_jobs(), jid)[0]),
            "source": j.get("source", ""), "dest": core.effective_dest(j), "tags": core.job_tags(j), "priority": j.get("priority") or "normal"}


def global_state(jobs):
    m = core.maintenance_state()
    return {"version": core.VERSION, "running": [jobs[x]["name"] for x in core._running if x in jobs], "running_count": len(core._running),
            "queued_count": len(core._queue), "failed_count": sum(1 for j in jobs.values() if j.get("last_status") == "fehler"),
            "jobs": len(jobs), "maintenance": bool(m), "maintenance_until": (m or {}).get("until") or "",
            "time": time.strftime("%Y-%m-%dT%H:%M:%S")}


# ---------------------------------------------------------------- Home Assistant Discovery
def _device():
    return {"identifiers": ["mirrorsync"], "name": "MirrorSync", "manufacturer": "MirrorSync", "model": "rclone mirror",
            "sw_version": core.VERSION, "configuration_url": (core.load_settings().get("public_url") or "").strip() or None}


def _disc(cl, comp, obj_id, cfg):
    pre = ((_state["cfg"] or {}).get("mqtt_discovery_prefix") or "homeassistant").strip("/")
    cfg = dict(cfg, availability_topic=base() + "/status", device=_device())
    cfg["device"] = {k: v for k, v in cfg["device"].items() if v}
    cl.publish(f"{pre}/{comp}/mirrorsync/{obj_id}/config", json.dumps(cfg, ensure_ascii=False), qos=1, retain=True)


def _undisc(cl, obj_ids):
    pre = ((_state["cfg"] or {}).get("mqtt_discovery_prefix") or "homeassistant").strip("/")
    for comp, oid in obj_ids:
        cl.publish(f"{pre}/{comp}/mirrorsync/{oid}/config", "", qos=1, retain=True)


def _job_objects(jid):
    s = _slug(jid)
    return [("sensor", f"{s}_status"), ("sensor", f"{s}_progress"), ("binary_sensor", f"{s}_running"),
            ("sensor", f"{s}_last_run"), ("sensor", f"{s}_next_run"), ("button", f"{s}_run"), ("button", f"{s}_dry"),
            ("button", f"{s}_stop")]


def discovery(cl, jobs):
    c = _state["cfg"] or {}
    b = base()
    t = lambda x: core.i18n.t(x, lang=core.i18n.default_lang)
    cmd = bool(c.get("mqtt_commands"))
    _disc(cl, "sensor", "running", {"name": t("Laufende Aufgaben"), "unique_id": "mirrorsync_running", "state_topic": b + "/state",
                                    "value_template": "{{ value_json.running_count }}", "icon": "mdi:sync",
                                    "json_attributes_topic": b + "/state"})
    _disc(cl, "sensor", "queued", {"name": t("Wartende Aufgaben"), "unique_id": "mirrorsync_queued", "state_topic": b + "/state",
                                   "value_template": "{{ value_json.queued_count }}", "icon": "mdi:timer-sand"})
    _disc(cl, "sensor", "failed", {"name": t("Fehlgeschlagene Aufgaben"), "unique_id": "mirrorsync_failed", "state_topic": b + "/state",
                                   "value_template": "{{ value_json.failed_count }}", "icon": "mdi:alert-circle"})
    if cmd:
        _disc(cl, "switch", "maintenance", {"name": t("Wartungsmodus"), "unique_id": "mirrorsync_maintenance", "state_topic": b + "/state",
                                            "value_template": "{{ 'ON' if value_json.maintenance else 'OFF' }}",
                                            "command_topic": b + "/maintenance/set", "icon": "mdi:wrench"})
        _undisc(cl, [("binary_sensor", "maintenance")])
    else:
        _disc(cl, "binary_sensor", "maintenance", {"name": t("Wartungsmodus"), "unique_id": "mirrorsync_maintenance_state",
                                                   "state_topic": b + "/state", "icon": "mdi:wrench",
                                                   "value_template": "{{ 'ON' if value_json.maintenance else 'OFF' }}"})
        _undisc(cl, [("switch", "maintenance")])
    now = set()
    for jid, j in jobs.items():
        s = _slug(jid)
        st = f"{b}/job/{s}/state"
        name = j.get("name", jid)
        now.add(jid)
        _disc(cl, "sensor", f"{s}_status", {"name": f"{name} " + t("Status"), "unique_id": f"mirrorsync_{s}_status", "state_topic": st,
                                             "value_template": "{{ value_json.status_text }}", "json_attributes_topic": st, "icon": "mdi:folder-sync"})
        _disc(cl, "sensor", f"{s}_progress", {"name": f"{name} " + t("Fortschritt"), "unique_id": f"mirrorsync_{s}_progress",
                                               "state_topic": st, "value_template": "{{ value_json.progress }}", "unit_of_measurement": "%",
                                               "icon": "mdi:progress-upload"})
        _disc(cl, "binary_sensor", f"{s}_running", {"name": f"{name} " + t("läuft"), "unique_id": f"mirrorsync_{s}_running",
                                                     "state_topic": st, "value_template": "{{ 'ON' if value_json.running else 'OFF' }}",
                                                     "device_class": "running"})
        _disc(cl, "sensor", f"{s}_last_run", {"name": f"{name} " + t("Letzter Lauf"), "unique_id": f"mirrorsync_{s}_last_run",
                                               "state_topic": st, "value_template": "{{ value_json.last_run or None }}",
                                               "device_class": "timestamp"})
        _disc(cl, "sensor", f"{s}_next_run", {"name": f"{name} " + t("Nächster Lauf"), "unique_id": f"mirrorsync_{s}_next_run",
                                               "state_topic": st, "value_template": "{{ value_json.next_run or None }}",
                                               "device_class": "timestamp"})
        btn = [("run", t("Starten"), "mdi:play"), ("dry", t("Testlauf"), "mdi:test-tube"), ("stop", t("Stopp"), "mdi:stop")]
        if cmd:
            for key, label, icon in btn:
                _disc(cl, "button", f"{s}_{key}", {"name": f"{name} {label}", "unique_id": f"mirrorsync_{s}_{key}",
                                                   "command_topic": f"{b}/job/{s}/set", "payload_press": key, "icon": icon})
        else:
            _undisc(cl, [("button", f"{s}_{k}") for k, _, _ in btn])
    gone = _state["known"] - now
    for jid in gone:
        _undisc(cl, _job_objects(jid))
        cl.publish(f"{b}/job/{_slug(jid)}/state", "", qos=1, retain=True)
    _state["known"] = now


# ---------------------------------------------------------------- Senden
def publish_all(cl, disc=False):
    jobs = core.load_jobs()
    b = base()
    if disc and (_state["cfg"] or {}).get("mqtt_discovery"):
        discovery(cl, jobs)
    cl.publish(b + "/state", json.dumps(global_state(jobs), ensure_ascii=False), qos=0, retain=True)
    for jid, j in jobs.items():
        cl.publish(f"{b}/job/{_slug(jid)}/state", json.dumps(job_state(jid, j, jobs), ensure_ascii=False, default=str), qos=0, retain=True)
    with _lock:
        _state["sent"] += 1 + len(jobs)
        _state["last"] = time.time()


def _on_message(cl, userdata, msg):
    """Befehle aus Home Assistant (nur mit mqtt_commands). Laeuft unter dem Namen „MQTT“ und landet im Audit-Log."""
    c = _state["cfg"] or {}
    if not c.get("mqtt_commands"):
        return
    payload = msg.payload.decode("utf-8", "replace").strip().lower()
    b = base()
    try:
        if msg.topic == b + "/maintenance/set":
            on = payload in ("on", "1", "true", "ein")
            core.set_maintenance(on, by="MQTT")
            core.audit_log.add("MQTT", "system", "Wartungsmodus " + ("eingeschaltet" if on else "ausgeschaltet"), "Wartungsmodus")
            return
        m = re.match(re.escape(b) + r"/job/([A-Za-z0-9_-]+)/set$", msg.topic)
        if not m:
            return
        jid = next((x for x in core.load_jobs() if _slug(x) == m.group(1)), None)
        if not jid:
            return
        name = core.load_jobs()[jid].get("name", jid)
        if payload in ("run", "start", "dry", "test", "verify"):
            ok = core.start_job(jid, dry_run=payload in ("dry", "test"), by="MQTT", manual=True,
                                mode="verify" if payload == "verify" else "full")
            core.audit_log.add("MQTT", "run", {"dry": "Testlauf gestartet", "test": "Testlauf gestartet", "verify": "Prüflauf gestartet"}.get(payload, "gestartet")
                               + ("" if ok else " (läuft schon)"), name)
        elif payload == "stop":
            core.stop_job(jid)
            core.audit_log.add("MQTT", "run", "gestoppt", name)
    except Exception as e:  # noqa: BLE001
        print(f"MQTT-Befehl: {e}", flush=True)
    push()


def _connect(c):
    import paho.mqtt.client as mqtt
    cid = (c.get("mqtt_client_id") or "").strip() or "mirrorsync-" + core.secrets.token_hex(3)
    cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=cid)
    if c.get("mqtt_user"):
        cl.username_pw_set(c["mqtt_user"], c.get("mqtt_password") or None)
    if c.get("mqtt_tls"):
        import ssl
        cl.tls_set(cert_reqs=ssl.CERT_NONE if c.get("mqtt_tls_insecure") else ssl.CERT_REQUIRED)
        if c.get("mqtt_tls_insecure"):
            cl.tls_insecure_set(True)
    cl.will_set(base() + "/status", "offline", qos=1, retain=True)

    def on_connect(client, userdata, flags, reason, props=None):
        ok = not getattr(reason, "is_failure", False) and str(reason) in ("Success", "0") or reason == 0
        with _lock:
            _state["connected"] = bool(ok)
            _state["error"] = "" if ok else str(reason)
            if ok:
                _state["since"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if ok:
            client.publish(base() + "/status", "online", qos=1, retain=True)
            if c.get("mqtt_commands"):
                client.subscribe(base() + "/job/+/set")
                client.subscribe(base() + "/maintenance/set")
            _wake.set()
            _state["disc"] = True

    def on_disconnect(client, userdata, flags, reason, props=None):
        with _lock:
            _state["connected"] = False
            if reason and str(reason) not in ("Success", "0", "Normal disconnection"):
                _state["error"] = str(reason)
    cl.on_connect, cl.on_disconnect, cl.on_message = on_connect, on_disconnect, _on_message
    cl.reconnect_delay_set(2, 120)
    cl.connect_async(c["mqtt_host"].strip(), int(c.get("mqtt_port") or 1883), keepalive=60)
    cl.loop_start()
    return cl


def _stop_client():
    cl = _state.get("client")
    if cl:
        try:
            cl.publish(base() + "/status", "offline", qos=1, retain=True).wait_for_publish(2)
        except Exception:  # noqa: BLE001
            pass
        try:
            cl.disconnect()
            cl.loop_stop()
        except Exception:  # noqa: BLE001
            pass
    _state.update(client=None, connected=False)


def _loop():
    while True:
        _wake.wait(timeout=5)
        _wake.clear()
        try:
            c = settings()
            if not c.get("mqtt_enabled") or not (c.get("mqtt_host") or "").strip():
                if _state.get("client"):
                    _stop_client()
                _state["cfg"] = c
                _state["error"] = ""
                continue
            if _state.get("client") is None or _cfg_key(c) != _cfg_key(_state["cfg"] or DEFAULTS):
                _stop_client()
                _state["cfg"] = c
                _state["error"] = ""
                _state["client"] = _connect(c)
                continue
            _state["cfg"] = c
            if not _state["connected"]:
                continue
            try:
                every = max(2, min(3600, int(c.get("mqtt_interval") or 10)))
            except ValueError:
                every = 10
            idle = 300   # ohne laufende Aufgabe nur alle 5 Minuten (und bei jeder Aenderung)
            due = _state.pop("dirty", False) or time.time() - _state["last"] >= (every if core._running else idle)
            if due or _state.get("disc"):
                publish_all(_state["client"], disc=_state.pop("disc", False))
        except Exception as e:  # noqa: BLE001
            with _lock:
                _state["error"] = f"{type(e).__name__}: {e}"


def push():
    """Etwas hat sich geaendert (Start, Ende, Wartungsmodus, Einstellungen): sofort senden."""
    _state["dirty"] = True
    _wake.set()


def reconfigure():
    _state["disc"] = True
    push()


def start(core_module):
    global core, _thread
    core = core_module
    if _thread is None:
        _thread = threading.Thread(target=_loop, daemon=True, name="mqtt")
        _thread.start()


def test(c):
    """Verbindung mit den angegebenen Einstellungen pruefen (ohne zu speichern). Liefert (ok, text)."""
    import paho.mqtt.client as mqtt
    res = {"rc": None}
    ev = threading.Event()
    cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mirrorsync-test-" + core.secrets.token_hex(3))
    if c.get("mqtt_user"):
        cl.username_pw_set(c["mqtt_user"], c.get("mqtt_password") or None)
    if c.get("mqtt_tls"):
        import ssl
        cl.tls_set(cert_reqs=ssl.CERT_NONE if c.get("mqtt_tls_insecure") else ssl.CERT_REQUIRED)
        if c.get("mqtt_tls_insecure"):
            cl.tls_insecure_set(True)

    def on_connect(client, userdata, flags, reason, props=None):
        res["rc"] = reason
        ev.set()
    cl.on_connect = on_connect
    try:
        cl.connect(c["mqtt_host"].strip(), int(c.get("mqtt_port") or 1883), keepalive=10)
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"
    cl.loop_start()
    ev.wait(8)
    cl.disconnect()
    cl.loop_stop()
    rc = res["rc"]
    if rc is None:
        return False, core.i18n.t("Keine Antwort vom Broker.")
    if getattr(rc, "is_failure", False):
        return False, str(rc)
    return True, core.i18n.t("Verbindung zum Broker klappt.")
