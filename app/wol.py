"""Wake-on-LAN: Server vor dem Lauf aufwecken und warten, bis er erreichbar ist."""
import re
import socket
import time

MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]?){5}[0-9A-Fa-f]{2}$")


def clean_mac(mac):
    mac = (mac or "").strip()
    if not MAC_RE.match(mac):
        return None
    return ":".join(re.findall(r"[0-9A-Fa-f]{2}", mac)).upper()


def magic_packet(mac):
    raw = bytes.fromhex(clean_mac(mac).replace(":", ""))
    return b"\xff" * 6 + raw * 16


def send(mac, broadcast="255.255.255.255", port=9):
    """Magic Packet dreimal senden. Wirft OSError, wenn das Netz es nicht zulaesst."""
    pkt = magic_packet(mac)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for _ in range(3):
            s.sendto(pkt, (broadcast or "255.255.255.255", int(port or 9)))
            time.sleep(0.2)


def tcp_ok(host, port, timeout=3):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def wait(probe, max_wait, stop=lambda: False, every=5):
    """probe() so lange aufrufen, bis sie True liefert oder max_wait Sekunden vorbei sind. Liefert Sekunden oder None."""
    t0 = time.time()
    while time.time() - t0 < max_wait:
        if stop():
            return None
        if probe():
            return int(time.time() - t0)
        time.sleep(every)
    return None
