"""Einstellungen: Leiste links mit Gruppen und Suchindex fuer das Suchfeld (seit 1.55.0).

Quelltexte sind Deutsch, uebersetzt wird ueber die i18n-Kataloge (t()).
Rechte: Jede Seite hat ein Recht (None = jeder angemeldete Benutzer, "admin" = nur Admins). Eine Seite und ihre
Suchtreffer erscheinen nur, wenn der Benutzer das Recht hat, genau wie frueher die Tabs. Ein Tupel als Recht
heisst: eines der Rechte genuegt.
Seit 1.56.0 sind die Bereiche von "Allgemein" eigene Seiten unter Sicherheit, Wartung, Monitoring und Netzwerk.
"""
import i18n

# Seiten: id -> (Bezeichnung, Adresse, Recht, Symbol)
PAGES = {
    "users": ("Benutzer", "/users", "users.view", "👤"),
    "roles": ("Rollen", "/roles", "roles.manage", "🏷"),
    "groups": ("Gruppen", "/groups", "groups.manage", "👥"),
    "security": ("Anmeldung und Sicherheit", "/settings/security", "system.settings", "🔐"),
    "access": ("Zugriff", "/settings/access", "system.access", "🛡"),
    "api": ("API", "/settings/api", "system.api", "🔑"),
    "general": ("Allgemein", "/settings/general", "system.settings", "⚙"),
    "notify": ("Benachrichtigungen", "/settings", "notify.view", "🔔"),
    "backup": ("Sicherung", "/settings/backup", "admin", "💾"),
    "updates": ("Updates", "/settings/updates", ("system.settings", "system.update"), "⬆"),
    "restart": ("Neustart", "/settings/restart", ("system.settings", "system.restart"), "🔄"),
    "logs": ("Logs", "/settings/logs", "system.settings", "📜"),
    "monitoring": ("Überwachung", "/settings/monitoring", "system.settings", "📈"),
    "network": ("Bandbreite", "/settings/network", "system.settings", "🚀"),
    "account": ("Mein Konto", "/account", None, "🪪"),
    "help": ("Hilfe", "/help", None, "❓"),
}

GROUPS = [
    ("Benutzer & Rechte", ["users", "roles", "groups"]),
    ("Sicherheit", ["security", "access", "api"]),
    ("System", ["general", "notify", "backup"]),
    ("Wartung", ["updates", "restart", "logs"]),
    ("Monitoring", ["monitoring"]),
    ("Netzwerk", ["network"]),
    ("Persönlich", ["account", "help"]),
]

# Suchindex: (Bezeichnung, Seite, Anker, Stichwoerter). Der Anker ist die id des Bereichs auf der Seite.
INDEX = [
    # Allgemein
    ("Sprache", "general", "lang", "Standardsprache language Deutsch English Oberfläche"),
    ("Dateimanager: Tempo", "general", "files", "parallel kopieren verschieben schnell"),
    ("Nach Updates suchen", "updates", "update", "neue Version prüfen Intervall GitHub Benachrichtigung"),
    ("Selbst aktualisieren", "updates", "selfupdate", "Docker-Socket automatisch Update Image"),
    ("Update-Verlauf", "updates", "history", "Updates früher Versionen Ergebnis"),
    ("Alte Images löschen", "updates", "images", "prune Speicherplatz Docker"),
    ("Neustart des Containers", "restart", "restart", "neu starten Zeitplan Docker"),
    ("Überwachung (Health, Prometheus)", "monitoring", "monitor", "Uptime Kuma Home Assistant Grafana metrics health"),
    ("Datenvolumen pro Monat", "monitoring", "volume", "Limit GB Traffic Warnschwelle"),
    ("Logs aufbewahren", "logs", "logs", "Läufe behalten Audit-Log Tage Wochen Monate"),
    ("Alte Logs löschen", "logs", "purge", "Datum aufräumen Speicher"),
    ("Konto sperren nach Fehlversuchen", "security", "security", "Sperre Passwort falsch Anmeldung Sperrdauer"),
    ("Zwei-Faktor-Anmeldung erzwingen", "security", "security", "2FA Authenticator TOTP"),
    ("Meldung bei fehlgeschlagener Anmeldung", "security", "security", "Login Fehlversuch Benachrichtigung"),
    ("Reverse-Proxy und IP-Adresse", "security", "proxy", "X-Forwarded-For Nginx Traefik Caddy"),
    ("Passkeys: öffentliche Adresse", "security", "passkeys", "Domain HTTPS public url WebAuthn"),
    ("Länder-Datenbank (GeoIP)", "security", "geoip", "DB-IP Land Flagge"),
    ("Bandbreite (Standard)", "network", "bw", "bwlimit Geschwindigkeit Zeittabelle drosseln"),
    # Benachrichtigungen
    ("Standard-Benachrichtigungen", "notify", "std", "Webhook E-Mail Telegram Apprise ntfy Discord Gotify Kanäle"),
    ("Ruhezeiten", "notify", "quiet", "Nacht nicht stören leise"),
    ("Wochenbericht", "notify", "report", "Zusammenfassung wöchentlich Bericht"),
    ("Texte der Benachrichtigungen", "notify", "texts", "Vorlagen Text anpassen Nachricht"),
    # Sicherung
    ("Einstellungen exportieren", "backup", "export", "Sicherung Backup herunterladen"),
    ("Einstellungen importieren", "backup", "import", "Wiederherstellen Datei hochladen"),
    ("Automatische Sicherung", "backup", "auto", "Backup Zeitplan behalten"),
    ("Gespeicherte Sicherungen", "backup", "saved", "Backup Liste"),
    ("Datenbank", "backup", "db", "SQLite Größe aufräumen"),
    # API
    ("API und MCP", "api", "apimcp", "Swagger Claude n8n Home Assistant Schnittstelle"),
    ("API-Keys", "api", "keys", "Schlüssel Token"),
    ("Neuen API-Key erstellen", "api", "newkey", "Schlüssel Token anlegen"),
    # Zugriff
    ("Deine Verbindung", "access", "conn", "IP-Adresse Land"),
    ("Erlaubt-Liste", "access", "allow", "IP erlauben Whitelist Netz"),
    ("Länder sperren oder erlauben", "access", "countries", "Land GeoIP Geoblocking"),
    ("Automatisch sperren", "access", "autoban", "Fail2ban Fehlversuche IP sperren"),
    ("Sperrliste", "access", "blocklist", "IP gesperrt entsperren Blacklist"),
    # Benutzer, Rollen, Gruppen
    ("Benutzer anlegen und bearbeiten", "users", "", "Konto neu Passwort zurücksetzen"),
    ("Anmeldeverlauf", "users", "", "Login Protokoll fehlgeschlagen"),
    ("Rollen und Rechte", "roles", "", "Berechtigungen Admin Recht"),
    ("Gruppen", "groups", "", "Team Mitglieder"),
    # Mein Konto
    ("Mein Konto: Name, Sprache und Design", "account", "konto", "Anzeigename Sprache dunkel hell Theme"),
    ("Passkeys", "account", "passkeys", "WebAuthn Fingerabdruck Face ID Sicherheitsschlüssel"),
    ("Zwei-Faktor-Anmeldung (2FA)", "account", "twofa", "Authenticator Backup-Codes TOTP"),
    ("Passwort ändern", "account", "password", "Kennwort neu"),
]

# Seiten, die zu einem Leisten-Eintrag gehoeren (z. B. /users/log zu Benutzer)
def _active(pid, path):
    url = PAGES[pid][1]
    if pid == "notify":
        return path == "/settings" or path.startswith("/settings/templates")
    return path == url or path.startswith(url + "/")


def _allowed(perm, can, is_admin):
    if perm is None:
        return True
    if perm == "admin":
        return bool(is_admin)
    if isinstance(perm, tuple):
        return any(can(p) for p in perm)
    return bool(can(perm))


def nav(path, can, is_admin):
    """Gruppen fuer die Leiste: [{title, items: [{id, label, url, icon, active}]}], nur erlaubte Seiten."""
    out = []
    for title, ids in GROUPS:
        items = [{"id": p, "label": i18n.t(PAGES[p][0]), "url": PAGES[p][1], "icon": PAGES[p][3],
                  "active": _active(p, path)}
                 for p in ids if _allowed(PAGES[p][2], can, is_admin)]
        if items:
            out.append({"title": i18n.t(title), "items": items})
    return out


def index(can, is_admin):
    """Suchindex fuer die erlaubten Seiten: Seiten selbst und ihre Bereiche."""
    out = []
    for _title, ids in GROUPS:
        for p in ids:
            label, url, perm, icon = PAGES[p]
            if not _allowed(perm, can, is_admin):
                continue
            out.append({"label": i18n.t(label), "page": i18n.t(label), "url": url, "icon": icon,
                        "k": label})
    for label, p, anchor, kw in INDEX:
        plabel, url, perm, icon = PAGES[p]
        if not _allowed(perm, can, is_admin):
            continue
        u = url + ("/log" if label == "Anmeldeverlauf" else "") + ("#" + anchor if anchor else "")
        tr = i18n.t(label)
        out.append({"label": tr, "page": i18n.t(plabel), "url": u, "icon": icon,
                    "k": " ".join(x for x in (label if tr != label else "", kw) if x)})
    return out


def _norm(s):
    s = (s or "").lower()
    for a, b in (("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss"), ("-", " "), ("_", " ")):
        s = s.replace(a, b)
    return s


def search(q, can, is_admin, limit=20):
    """Einstellungen suchen (fuer API/MCP): alle Woerter muessen in Name, Seite oder Stichwoertern vorkommen."""
    words = _norm(q).split()
    res = []
    for e in index(can, is_admin):
        hay = _norm(" ".join((e["label"], e["page"], e["k"])))
        if all(w in hay for w in words):
            score = sum(3 if w in _norm(e["label"]) else 1 for w in words)
            res.append((score, e))
    res.sort(key=lambda x: -x[0])
    return [{"label": e["label"], "page": e["page"], "url": e["url"]} for _, e in res[:limit]]
