"""Rollen mit Einzelrechten und optionaler Beschraenkung auf einzelne Aufgaben und Speicherorte."""
import json
import os
import re
import threading

# Bereich -> [(Recht, Bezeichnung)]. Die Reihenfolge bestimmt die Anzeige im Rollen-Editor.
PERM_GROUPS = [
    ("Aufgaben", [
        ("jobs.view", "ansehen"),
        ("jobs.create", "anlegen"),
        ("jobs.edit", "bearbeiten"),
        ("jobs.delete", "löschen"),
        ("jobs.run", "starten und stoppen"),
        ("jobs.dryrun", "Testlauf starten"),
        ("jobs.preview", "Vorschau der Ordnerstruktur im Ziel ansehen (listet Dateien in Quelle und Ziel)"),
        ("jobs.logs", "Logs und Verlauf ansehen"),
        ("jobs.notify", "Benachrichtigungen der Aufgabe ändern"),
        ("jobs.advanced", "zusätzliche rclone-Optionen ändern"),
        ("jobs.twoway", "Zwei-Wege-Sync einrichten (schreibt auch in die Quelle)"),
    ]),
    ("Speicherorte", [
        ("remotes.view", "ansehen"),
        ("remotes.test", "Verbindung testen"),
        ("remotes.browse", "Ordner durchsuchen"),
        ("remotes.create", "anlegen"),
        ("remotes.edit", "bearbeiten und neu anmelden"),
        ("remotes.delete", "entfernen"),
        ("local.paths", "lokale Ordner (/data) in Aufgaben verwenden"),
    ]),
    ("Dateimanager", [
        ("files.view", "Dateien ansehen (durchsuchen, Größen, Berechtigungen, herunterladen)"),
        ("files.edit", "Dateien hochladen, bearbeiten, umbenennen, Ordner anlegen, kopieren"),
        ("files.delete", "Dateien und Ordner löschen (auch nötig zum Verschieben)"),
    ]),
    ("Benachrichtigungen (Standard)", [
        ("notify.view", "ansehen"),
        ("notify.edit", "ändern und testen"),
    ]),
    ("Benutzer und Rollen", [
        ("users.view", "Benutzer ansehen"),
        ("users.manage", "Benutzer anlegen, bearbeiten, löschen"),
        ("roles.manage", "Rollen verwalten"),
        ("groups.manage", "Gruppen verwalten (Mitglieder und Rechte, nur mit Rechten, die man selbst hat)"),
    ]),
    ("System", [
        ("system.settings", "allgemeine Einstellungen (z. B. Log-Aufbewahrung) ändern"),
        ("system.access", "Zugriff nach IP-Adresse und Land verwalten (Sperr- und Erlaubt-Listen)"),
        ("system.audit", "Audit-Log ansehen und exportieren"),
        ("system.api", "API-Keys verwalten (nur mit Rechten, die man selbst hat)"),
        ("system.update", "MirrorSync aktualisieren (Selbst-Update über den Docker-Socket)"),
    ]),
]
ALL_PERMS = [p for _, perms in PERM_GROUPS for p, _ in perms]
PERM_LABELS = {p: f"{g}: {label}" for g, perms in PERM_GROUPS for p, label in perms}
# Wer etwas aendern darf, darf es auch sehen
IMPLIES = {
    "jobs.create": ["jobs.view"], "jobs.edit": ["jobs.view"], "jobs.delete": ["jobs.view"],
    "jobs.run": ["jobs.view"], "jobs.dryrun": ["jobs.view"], "jobs.logs": ["jobs.view"],
    "jobs.notify": ["jobs.view"], "jobs.preview": ["jobs.view"], "jobs.advanced": ["jobs.view"], "jobs.twoway": ["jobs.view"],
    "remotes.test": ["remotes.view"], "remotes.browse": ["remotes.view"], "remotes.create": ["remotes.view"],
    "remotes.edit": ["remotes.view"], "remotes.delete": ["remotes.view"],
    "files.edit": ["files.view"], "files.delete": ["files.view"],
    "notify.edit": ["notify.view"], "users.manage": ["users.view"], "roles.manage": ["users.view"], "groups.manage": ["users.view"],
}

DEFAULT_ROLES = {
    "admin": {"name": "Admin", "description": "darf alles", "perms": list(ALL_PERMS),
              "jobs": "all", "remotes": "all", "builtin": True, "locked": True},
    "operator": {"name": "Operator", "description": "Aufgaben anlegen, bearbeiten, starten; Speicherorte ansehen und testen",
                 "perms": ["jobs.view", "jobs.create", "jobs.edit", "jobs.delete", "jobs.run", "jobs.dryrun", "jobs.preview",
                           "jobs.logs", "jobs.notify", "jobs.advanced", "jobs.twoway", "remotes.view", "remotes.test", "remotes.browse", "local.paths"],
                 "jobs": "all", "remotes": "all", "builtin": True},
    "viewer": {"name": "Nur lesen", "description": "Aufgaben, Status und Logs ansehen",
               "perms": ["jobs.view", "jobs.logs", "remotes.view"], "jobs": "all", "remotes": "all", "builtin": True},
}
_lock = threading.RLock()


def normalize(perms):
    out = set(p for p in perms if p in ALL_PERMS)
    for p in list(out):
        out.update(IMPLIES.get(p, []))
    return [p for p in ALL_PERMS if p in out]


class RoleStore:
    def __init__(self, db):
        self.db = db

    def load(self):
        with _lock:
            data = self.db.get_map("role")
            changed = False
            for rid, role in DEFAULT_ROLES.items():   # Vorlagen immer vorhanden, Admin immer vollstaendig
                if rid not in data:
                    data[rid] = json.loads(json.dumps(role))
                    changed = True
            if data["admin"].get("perms") != ALL_PERMS:
                data["admin"].update(perms=list(ALL_PERMS), jobs="all", remotes="all", locked=True)
                changed = True
            if changed:
                self.save(data)
            return data

    def save(self, data):
        with _lock:
            self.db.put_map("role", data)

    def get(self, rid):
        return self.load().get(rid)


def new_id(name, existing):
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "rolle"
    rid, i = base, 2
    while rid in existing:
        rid, i = f"{base}-{i}", i + 1
    return rid


def principals_of(user=None, key_id=None, groups=None):
    """Kennungen, unter denen jemand in "Sichtbar für" stehen kann: user:<name>, group:<id>."""
    out = set()
    if user and not key_id:
        out.add("user:" + user.lower())
    for gid in groups or []:
        out.add("group:" + gid)
    return out


def groups_of(all_groups, user=None, key_id=None):
    """IDs der Gruppen, in denen ein Benutzer bzw. API-Key Mitglied ist."""
    out = []
    for gid, grp in (all_groups or {}).items():
        if key_id and key_id in (grp.get("keys") or []):
            out.append(gid)
        elif user and not key_id and user.lower() in [m.lower() for m in grp.get("members") or []]:
            out.append(gid)
    return out


def visible(vis, principals, owner_ok=False):
    """vis = "all"/None (Standard) oder Liste von Kennungen. Eine leere Liste heisst: nur Admins und Besitzer."""
    if vis is None or vis == "all" or owner_ok:
        return True
    return bool(principals & set(vis))


class Access:
    """Rechte eines angemeldeten Benutzers bzw. API-Keys: Rolle plus Gruppen, dazu Sichtbarkeit von Aufgaben und Speicherorten."""

    def __init__(self, user_name=None, role=None, groups=None, remote_vis=None, key_id=None):
        self.user = user_name
        self.role = role or {}
        self.groups = groups or {}          # {gid: gruppe} in denen er Mitglied ist
        self.remote_vis = remote_vis or {}  # {remote: "all" | [kennungen]}
        self.admin = bool(self.role.get("locked"))
        perms = set(self.role.get("perms", []))
        for grp in self.groups.values():
            perms.update(grp.get("perms") or [])
        self.perms = set(normalize(perms))
        self.role_perms = set(self.role.get("perms", []))
        self.principals = principals_of(user_name, key_id, self.groups)

    def has(self, perm):
        return perm in self.perms

    def job_ok(self, job_id, job=None):
        if self.admin:
            return True
        owner = bool(job and job.get("owner") and self.user and job.get("owner").lower() == self.user.lower())
        scope = self.role.get("jobs", "all")
        if scope != "all" and job_id not in scope and not owner:
            return False
        return visible((job or {}).get("visible_to"), self.principals, owner)

    def remote_ok(self, name):
        if self.admin:
            return True
        scope = self.role.get("remotes", "all")
        if scope != "all" and name not in scope:
            return False
        return visible(self.remote_vis.get(name), self.principals)

    def path_ok(self, path):
        """Darf dieser Pfad (remote:pfad oder lokaler Pfad) benutzt werden?"""
        path = (path or "").strip()
        m = re.match(r"^([A-Za-z0-9_.\- ]+):", path)
        if m and not path.startswith("/"):
            return self.remote_ok(m.group(1))
        return self.has("local.paths")
