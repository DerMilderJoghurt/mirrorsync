"""Passkeys (WebAuthn): Anmelden ohne Passwort mit Fingerabdruck, Gesicht, PIN oder Sicherheitsschluessel.

Die eigentliche Pruefung macht die Bibliothek py_webauthn. Hier nur: Optionen bauen, Antworten pruefen,
gespeicherte Passkeys verwalten. Ein Passkey ist an einen Domainnamen gebunden (RP-ID) und braucht HTTPS
(ausser bei localhost)."""
import ipaddress
import json
import secrets
import time
from urllib.parse import urlparse

try:
    import webauthn
    from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
    from webauthn.helpers.structs import (AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor,
                                          ResidentKeyRequirement, UserVerificationRequirement)
    AVAILABLE = True
except Exception:   # Bibliothek fehlt: Passkeys einfach nicht anbieten
    AVAILABLE = False

RP_NAME = "MirrorSync"
TIMEOUT_S = 300   # so lange gilt eine Anfrage (Challenge)


def _host_only(host):
    host = (host or "").strip().lower()
    if host.startswith("["):   # [IPv6]:port
        return host[1:host.find("]")] if "]" in host else host
    return host.rsplit(":", 1)[0] if host.count(":") == 1 else host


def rp_for(host, public_url=""):
    """(rp_id, erlaubte Origins, Problem oder None) fuer die aktuelle Adresse.
    public_url (Einstellung) hat Vorrang vor dem Host-Header."""
    if not AVAILABLE:
        return None, [], "Die Passkey-Bibliothek ist in diesem Image nicht installiert."
    if public_url:
        u = urlparse(public_url.strip())
        if u.scheme not in ("https", "http") or not u.hostname:
            return None, [], "Die öffentliche Adresse unter Einstellungen → Allgemein ist ungültig (Beispiel: https://sync.example.de)."
        rp_id = u.hostname.lower()
        origins = [f"{u.scheme}://{u.netloc.lower()}"]
        if u.scheme != "https" and rp_id != "localhost":
            return rp_id, origins, "Passkeys brauchen HTTPS. Die öffentliche Adresse beginnt mit http://."
    else:
        rp_id = _host_only(host)
        h = (host or "").strip().lower()
        origins = [f"https://{h}"] + ([f"http://{h}"] if rp_id == "localhost" else [])
    if not rp_id:
        return None, [], "Adresse unbekannt."
    try:
        ipaddress.ip_address(rp_id)
        return rp_id, origins, ("Passkeys funktionieren nicht über eine IP-Adresse. Öffne MirrorSync über seinen "
                                "Domainnamen mit HTTPS, z. B. über deinen Reverse-Proxy.")
    except ValueError:
        pass
    return rp_id, origins, None


def registration_options(rp_id, user_name, user_handle, existing):
    """Optionen fuer navigator.credentials.create(). Liefert (JSON-Text, challenge-b64)."""
    opts = webauthn.generate_registration_options(
        rp_id=rp_id, rp_name=RP_NAME, user_name=user_name, user_display_name=user_name,
        user_id=bytes.fromhex(user_handle), timeout=TIMEOUT_S * 1000,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED, user_verification=UserVerificationRequirement.REQUIRED),
        exclude_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(p["id"])) for p in existing or []])
    return webauthn.options_to_json(opts), bytes_to_base64url(opts.challenge)


def verify_registration(credential, challenge, rp_id, origins, name):
    """Neue Passkey-Antwort pruefen. Liefert den zu speichernden Eintrag (wirft bei Fehler)."""
    v = webauthn.verify_registration_response(
        credential=credential, expected_challenge=base64url_to_bytes(challenge), expected_rp_id=rp_id,
        expected_origin=origins, require_user_verification=True)
    cred = credential if isinstance(credential, dict) else json.loads(credential)
    transports = ((cred.get("response") or {}).get("transports") or [])[:6]
    return {"id": bytes_to_base64url(v.credential_id), "pk": bytes_to_base64url(v.credential_public_key),
            "count": v.sign_count, "name": (name or "Passkey").strip()[:60] or "Passkey", "rp_id": rp_id,
            "created": time.strftime("%Y-%m-%d %H:%M"), "last_used": "", "transports": [str(t) for t in transports],
            "synced": bool(getattr(v, "credential_backed_up", False))}


def authentication_options(rp_id):
    """Optionen fuer navigator.credentials.get() ohne Benutzernamen (Passkey waehlt das Konto)."""
    opts = webauthn.generate_authentication_options(rp_id=rp_id, timeout=TIMEOUT_S * 1000,
                                                    user_verification=UserVerificationRequirement.REQUIRED)
    return webauthn.options_to_json(opts), bytes_to_base64url(opts.challenge)


def credential_id(credential):
    cred = credential if isinstance(credential, dict) else json.loads(credential)
    return str(cred.get("rawId") or cred.get("id") or "")


def find(all_users, cred_id):
    """(Benutzername, Passkey-Eintrag) zum Passkey oder (None, None)."""
    for name, u in all_users.items():
        for p in u.get("passkeys") or []:
            if secrets.compare_digest(p.get("id", ""), cred_id):
                return name, p
    return None, None


def verify_authentication(credential, challenge, rp_id, origins, entry):
    """Anmelde-Antwort pruefen. Liefert den neuen Zaehlerstand (wirft bei Fehler)."""
    v = webauthn.verify_authentication_response(
        credential=credential, expected_challenge=base64url_to_bytes(challenge), expected_rp_id=rp_id,
        expected_origin=origins, credential_public_key=base64url_to_bytes(entry["pk"]),
        credential_current_sign_count=int(entry.get("count") or 0), require_user_verification=True)
    return v.new_sign_count


def new_user_handle():
    return secrets.token_hex(16)
