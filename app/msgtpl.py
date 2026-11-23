"""Vorlagen fuer Benachrichtigungstexte: Betreff und Text je Ereignis, mit {variablen}."""
import json
import re

import i18n

# Ereignis -> Bezeichnung, Standard-Betreff, Standard-Text, Variablen (Name, Beschreibung, Beispiel)
COMMON = [("datum", "Datum", "22.11.2026"), ("zeit", "Uhrzeit", "03:00:42"), ("version", "MirrorSync-Version", "1.13.0"),
          ("titel", "fertiger Betreff (nur im Text)", "")]
RUN_VARS = [
    ("job", "Name der Aufgabe", "NAS → Docker"), ("status", "OK, FEHLER oder GESTOPPT", "OK"),
    ("status_icon", "✅ oder ❌", "✅"), ("testlauf", "„ (Testlauf)“ oder leer", ""),
    ("quelle", "Quelle", "NAS:Daten"), ("ziel", "Ziel", "Server:/backup/Daten"),
    ("start", "Startzeit", "22.11.2026 03:00:00"), ("ende", "Endzeit", "22.11.2026 03:00:42"),
    ("dauer", "Dauer lesbar", "42 s"), ("dauer_s", "Dauer in Sekunden", "42"),
    ("kopiert", "kopierte/aktualisierte Dateien", "17"), ("geloescht", "gelöschte Dateien", "3"),
    ("fehler", "Anzahl Fehler", "0"), ("fehler_liste", "letzte Fehler, je Zeile „• …“", ""),
    ("fehler_block", "„Letzte Fehler:“ + Liste, oder leer", ""), ("gestartet_von", "Zeitplan, Live, Benutzername …", "Zeitplan"),
    ("art", "„Live“ bei Live-Läufen, sonst „Spiegel“", "Spiegel"),
]
RUN_FAIL_SAMPLE = {"status": "FEHLER", "status_icon": "❌", "fehler": "2", "kopiert": "15",
                   "fehler_liste": "• Daten/bild.jpg: permission denied\n• Daten/x.tmp: file changed",
                   "fehler_block": "\nLetzte Fehler:\n• Daten/bild.jpg: permission denied\n• Daten/x.tmp: file changed"}
EVENTS = {
    "run_ok": {
        "label": "Lauf erfolgreich", "vars": RUN_VARS,
        "title": "{status_icon} MirrorSync: {job} – {status}{testlauf}",
        "body": "{titel}\n{quelle} → {ziel}\nDauer: {dauer_s} s, kopiert/aktualisiert: {kopiert}, gelöscht: {geloescht}, Fehler: {fehler}{fehler_block}",
    },
    "run_fail": {
        "label": "Lauf fehlgeschlagen oder gestoppt", "vars": RUN_VARS, "sample": RUN_FAIL_SAMPLE,
        "title": "{status_icon} MirrorSync: {job} – {status}{testlauf}",
        "body": "{titel}\n{quelle} → {ziel}\nDauer: {dauer_s} s, kopiert/aktualisiert: {kopiert}, gelöscht: {geloescht}, Fehler: {fehler}{fehler_block}",
    },
    "login_fail": {
        "label": "Fehlgeschlagene Anmeldungen",
        "vars": [("anzahl", "Anzahl gesammelter Fehlversuche", "2"), ("anmeldungen", "„Anmeldung“ oder „Anmeldungen“", "Anmeldungen"),
                 ("liste", "alle Fehlversuche, je Zeile", "03:12:01 admin von 203.0.113.7 🇺🇸 Vereinigte Staaten: Passwort falsch\n03:12:09 root von 203.0.113.7 🇺🇸 Vereinigte Staaten: unbekannter Benutzer"),
                 ("benutzer", "zuletzt versuchter Benutzer", "root"), ("ip", "zuletzt benutzte IP", "203.0.113.7"),
                 ("pause", "Minuten bis zur nächsten Meldung", "15")],
        "title": "⚠️ MirrorSync: {anzahl} fehlgeschlagene {anmeldungen}",
        "body": "{titel}\n{liste}\nNächste Meldung frühestens in {pause} Minuten.",
    },
    "account_lock": {
        "label": "Konto gesperrt",
        "vars": [("benutzer", "Benutzername", "olaf"), ("sperre", "wie lange gesperrt", "für 15 Minuten gesperrt (bis 22.11.2026 03:27)"),
                 ("versuche", "Anzahl Fehlversuche", "5"), ("ip", "letzte IP", "203.0.113.7"),
                 ("land", "Land der IP", "Vereinigte Staaten"), ("flagge", "Flagge der IP", "🇺🇸")],
        "title": "🔒 MirrorSync: Konto „{benutzer}“ gesperrt",
        "body": "🔒 MirrorSync: Konto „{benutzer}“ {sperre}.\n{versuche} fehlgeschlagene Anmeldungen, zuletzt von {ip}.",
    },
    "ip_block": {
        "label": "IP-Adresse gesperrt",
        "vars": [("ip", "gesperrte IP", "203.0.113.7"), ("land", "Land", "Vereinigte Staaten"), ("flagge", "Flagge", "🇺🇸"),
                 ("wie_lange", "„dauerhaft“ oder „bis …“", "bis 22.11.2026 04:12"), ("benutzer", "zuletzt versuchter Benutzer", "admin")],
        "title": "🚫 MirrorSync: IP gesperrt",
        "body": "🚫 MirrorSync: IP {ip} {flagge} {land} wurde nach zu vielen Fehlversuchen {wie_lange} gesperrt (zuletzt Benutzer „{benutzer}“).",
    },
    "backup_ok": {
        "label": "Automatische Sicherung erstellt", "vars": None,
        "title": "💾 MirrorSync: Sicherung erstellt",
        "body": "{titel}\n{datei} ({groesse}, verschlüsselt: {verschluesselt}) in {ordner}.\nAlte Sicherungen gelöscht: {geloescht}.",
    },
    "backup_skip": {
        "label": "Automatische Sicherung: nichts geändert", "vars": None,
        "title": "💾 MirrorSync: keine Änderung, keine neue Sicherung",
        "body": "{titel}\nLetzte Sicherung: {datei} vom {letzte}.",
    },
    "backup_fail": {
        "label": "Automatische Sicherung fehlgeschlagen", "vars": None, "sample": {"fehler_text": "PermissionError: [Errno 13] Permission denied: '/backups'", "datei": ""},
        "title": "❌ MirrorSync: Sicherung fehlgeschlagen",
        "body": "{titel}\nZiel: {ordner}\nFehler: {fehler_text}",
    },
    "test": {
        "label": "Testnachricht",
        "vars": [("job", "Aufgabe (beim Test aus einer Aufgabe) oder „Test“", "Test")],
        "title": "🔔 MirrorSync: Testnachricht",
        "body": "{titel}\nWenn du das liest, funktioniert der Kanal.",
    },
}
BACKUP_VARS = [("datei", "Dateiname der Sicherung", "mirrorsync-auto-20261122-030000.zip.enc"),
               ("ordner", "Zielordner", "/config/backups"), ("groesse", "Größe", "84 KB"),
               ("verschluesselt", "„ja“ oder „nein“", "ja"), ("geloescht", "gelöschte alte Sicherungen", "1"),
               ("fehler_text", "Fehlermeldung (nur bei Fehler)", ""), ("letzte", "Zeit der letzten Sicherung", "21.11.2026 03:00"),
               ("gestartet_von", "Zeitplan oder Benutzername", "Zeitplan")]
for _e in ("backup_ok", "backup_skip", "backup_fail"):
    EVENTS[_e]["vars"] = BACKUP_VARS
JOB_EVENTS = ("run_ok", "run_fail")
VAR_RE = re.compile(r"\{\{|\}\}|\{([a-z_]+)\}")


def default(event, k, lang=None):
    """Eingebauter Betreff/Text in der Systemsprache (Benachrichtigungen gehen immer in dieser Sprache raus)."""
    return i18n.translate(EVENTS[event][k], lang=lang or i18n.default_lang)


def render(text, values, esc=None):
    """{name} ersetzen; unbekannte Namen bleiben stehen, {{ und }} ergeben { und }."""
    def sub(m):
        tok = m.group(0)
        if tok == "{{":
            return "{"
        if tok == "}}":
            return "}"
        name = m.group(1)
        if name not in values:
            return tok
        v = "" if values[name] is None else str(values[name])
        return esc(v) if esc else v
    return VAR_RE.sub(sub, text or "")


def sample(event):
    e = EVENTS[event]
    vals = {k: ex for k, _, ex in COMMON + e["vars"]}
    vals.update(e.get("sample", {}))
    return {k: i18n.translate(v, lang=i18n.default_lang) if isinstance(v, str) else v for k, v in vals.items()}


def pick(settings, event, job=None):
    """Effektiver Betreff/Text: Aufgabe > eigene Standardvorlage > eingebauter Standard."""
    out = {"title": default(event, "title"), "body": default(event, "body")}
    for src in ((settings or {}).get("msg_templates") or {}, (job or {}).get("msg_tpl") or {} if job and job.get("msg_tpl_on") else {}):
        t = src.get(event) or {}
        for k in ("title", "body"):
            if (t.get(k) or "").strip():
                out[k] = t[k]
    return out


def make(settings, event, values, job=None):
    """Liefert (Betreff, Text) mit eingesetzten Werten."""
    t = pick(settings, event, job)
    vals = dict(values)
    title = render(t["title"], vals).strip()
    vals["titel"] = title
    return title, render(t["body"], vals).strip()


NUMERIC = {"kopiert", "geloescht", "fehler", "dauer_s", "anzahl", "versuche", "pause"}


def all_blank():
    vals = {"titel": "", "nachricht": "", "ereignis": "", "ok": "false"}
    for e in EVENTS.values():
        for n, _, _ in COMMON + e["vars"]:
            vals[n] = "0" if n in NUMERIC else ""
    return vals


def json_escape(v):
    return json.dumps(v, ensure_ascii=False)[1:-1]


def webhook_body(tpl, values):
    """Eigener JSON-Body: Werte werden JSON-sicher eingesetzt (in Anfuehrungszeichen schreiben: "{job}")."""
    return render(tpl, values, json_escape)


def check_webhook_body(tpl):
    """Fehlertext oder None: Vorlage muss mit Beispielwerten gueltiges JSON ergeben."""
    if not (tpl or "").strip():
        return None
    vals = sample("run_fail")
    vals.update(titel="❌ MirrorSync: Beispiel", nachricht="Zeile 1\nZeile 2", ereignis="run_fail", ok="false")
    try:
        json.loads(webhook_body(tpl, vals))
    except ValueError as e:
        return f"Webhook-Vorlage ergibt kein gültiges JSON ({e}). Texte in Anführungszeichen setzen, z. B. \"text\": \"{{nachricht}}\"."
    return None


def form_templates(form, prefix, events, base=None):
    """Formularfelder <prefix><event>_title/_body lesen; Text gleich Standard (bzw. geerbter Vorlage) = nicht speichern."""
    out = {}
    for ev in events:
        t = {}
        for k in ("title", "body"):
            v = (form.get(f"{prefix}{ev}_{k}") or "").replace("\r\n", "\n").strip()
            inherited = ((base or {}).get(ev) or {}).get(k) or default(ev, k)
            if v and v != inherited.strip():
                t[k] = v[:4000]
        if t:
            out[ev] = t
    return out


def editor_data(events, current=None, base=None):
    """Daten fuer den Editor im Browser: Standard, aktuelle Werte, Variablen, Beispielwerte."""
    data = {}
    for ev in events:
        e = EVENTS[ev]
        cur = (current or {}).get(ev) or {}
        inherited = {"title": default(ev, "title"), "body": default(ev, "body")}
        b = (base or {}).get(ev) or {}
        for k in ("title", "body"):
            if (b.get(k) or "").strip():
                inherited[k] = b[k]
        data[ev] = {"label": i18n.translate(e["label"]), "default": inherited,
                    "title": cur.get("title") or inherited["title"], "body": cur.get("body") or inherited["body"],
                    "custom": bool(cur), "vars": [[n, i18n.translate(d)] for n, d, _ in COMMON + e["vars"]], "sample": sample(ev)}
    return data
