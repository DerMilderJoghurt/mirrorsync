# Changelog

Versionsnummern nach [SemVer](https://semver.org/lang/de/): MAJOR.MINOR.PATCH
(MAJOR = inkompatible Änderung, MINOR = neue Funktion, PATCH = Fehlerbehebung).

## 1.57.0 – 2026-11-26
**Wiederherstellungs-Test**
- Neu unter **Aufgabe → Prüfen & schützen**: Nach einem erfolgreichen Lauf holt MirrorSync ein paar zufällige Dateien
  aus dem Ziel zurück (bei verschlüsseltem Ziel entschlüsselt) und vergleicht sie Byte für Byte mit der Quelle. So
  ist sicher, dass sich das Backup im Ernstfall wirklich zurückspielen lässt. Einstellbar: aus, nach jedem Lauf,
  höchstens einmal in der Woche oder im Monat, Anzahl Dateien (Standard 5) und größte Datei (Standard 100 MB).
- Schlägt der Test fehl, wird der Lauf zum Fehler und die Benachrichtigung geht raus. Das Ergebnis steht im Verlauf
  (♻), in Health (`restore_test`), in den Metriken (`mirrorsync_job_restore_test_ok`) und im Wochenbericht.
- Im Log startet **♻ Wiederherstellung testen** den Test jederzeit von Hand (Recht `jobs.run`, API/MCP
  `restore_test_job`).

**Sicherung: jeden Bereich einzeln anhaken**
- Beim **Exportieren**, bei der **automatischen Sicherung** und beim **Importieren/Wiederherstellen** hat jeder Bereich
  einen eigenen Haken: Aufgaben, Speicherorte (rclone.conf), Sichtbarkeit der Speicherorte, SSH-Schlüssel und weitere
  Dateien, Benutzer, Gruppen, Rollen, API-Keys, IP- und Länderregeln, Dashboards, die Einstellungs-Gruppen
  (Benachrichtigungen, Wochenbericht, Anmeldung und Sicherheit, Updates und Neustart, automatische Sicherung,
  Bandbreite und Datenvolumen, Aufbewahrung der Logs, Monitoring, Allgemein), Statistik, Anmeldeverlauf, Audit-Log und
  Lauf-Logs. So lassen sich z. B. nur Aufgaben und Speicherorte auf eine zweite Instanz übernehmen.
- Beim Import zeigt die Vorschau je Bereich die Anzahl in der Datei und jetzt. **Ersetzen** tauscht nur die
  angehakten Bereiche aus, **Ergänzen** fügt nur Neues hinzu (gleiche ID bzw. gleicher Name bleibt, rclone.conf wird
  um neue Speicherorte erweitert). Vorher wird wie bisher automatisch gesichert.
- Dashboards und Statistik sind jetzt Teil der Sicherung; ein Import löscht sie nicht mehr mit.
- API/MCP: `export_backup`, `import_backup`, `restore_backup` und `update_autobackup` kennen `parts`, Import und
  Wiederherstellung zusätzlich `mode` (replace oder merge); `backup_overview` listet die Bereiche.

**Speicherorte**
- **🔍 Nur testen, nicht speichern** beim Anlegen und Bearbeiten: prüft die Verbindung mit den eingegebenen Daten,
  bevor etwas gespeichert wird (Recht `remotes.test`, API/MCP `probe_remote`).

**Updates**
- **Jetzt aktualisieren** ist ausgegraut, bis **Jetzt prüfen** eine neue Version findet. „Jetzt prüfen“ darf auch,
  wer nur `system.update` hat.

**Repo**
- Vorlagen für Fehlermeldungen und Funktionswünsche auf GitHub (mit Version, Installationsart und Logs).

## 1.56.0 – 2026-11-26
**Einstellungen neu sortiert**
- Neue Gruppen in der Leiste: **Wartung** (Updates, Neustart, Logs), **Monitoring** (Überwachung) und **Netzwerk**
  (Bandbreite). **Anmeldung und Sicherheit** ist eine eigene Seite und steht oben unter **Sicherheit**. Unter
  **System → Allgemein** bleiben Sprache und Dateimanager. Jede Seite hat eine eigene Adresse (z. B.
  `/settings/updates`), alte Links wie `/settings/general#bw` springen automatisch an die neue Stelle; das Suchfeld
  findet alles an der neuen Stelle.
- **Updates** aufgeräumt: oben installierte und neueste Version mit **Jetzt prüfen** und **Jetzt aktualisieren** und
  dem Ablauf eines Updates, darunter „Nach Updates suchen“ und „Automatisch aktualisieren“ nebeneinander, dann
  **Container** (Name, Image, Compose-Projekt, Docker-Socket), **Verlauf** der letzten Updates und alte Images.
- Wer nur `system.update` bzw. `system.restart` hat, sieht die Seiten Updates bzw. Neustart und kann dort
  aktualisieren bzw. neu starten, aber nichts an den Einstellungen ändern.

**Aufgaben**
- **Nur diese Aufgabe**: Hat eine Aufgabe Folgeaufgaben, gibt es neben „Start“ den Knopf **▶ Nur diese**. Er startet
  nur diese Aufgabe, die Kette läuft danach nicht weiter (auch nicht bei einem neuen Versuch nach einem Fehler).
- **Mehrfachauswahl**: **☑ Auswahl** blendet links Kästchen ein (Umschalt-Klick wählt einen Bereich). Für alle
  markierten Aufgaben: Starten, Nur diese, Testlauf, Prüfen, Pausieren, Fortsetzen, Duplizieren, Logs öffnen,
  Entfernen. Bei **Speicherorten**: Testen, Duplizieren (als `<name>-kopie`), Entfernen. Jede Aktion braucht dasselbe
  Recht wie einzeln.

**Audit-Log**
- Kompakter: pro Eintrag eine Zeile mit Zeit, Benutzer, Bereich, Aktion und Kurzfassung (z. B. die geänderten Felder).
  Ein Klick klappt alle Details direkt darunter auf, dazu „Alle aufklappen“ und „Alle zuklappen“.

**Fehler behoben**
- Die Vorlage-Rollen **Operator** und **Nur lesen** ließen sich nicht löschen, sie kamen sofort wieder. Jetzt bleiben
  sie gelöscht und lassen sich unter **Rollen → Gelöschte Vorlagen** wiederherstellen. Admin bleibt unlöschbar. Eine
  Rolle, die ein API-Key noch verwendet, lässt sich nicht mehr löschen.

**API und MCP**
- `run_job` bzw. `POST /api/v1/jobs/<id>/run` mit `only_this` (ohne Folgeaufgaben).
- Neu `bulk_jobs` (`POST /api/v1/jobs/bulk`) und `bulk_remotes` (`POST /api/v1/remotes/bulk`) für die
  Mehrfachauswahl, `restore_role` und `list_deleted_role_templates` für gelöschte Vorlagen.
- Hilfe und alle Texte in fünf Sprachen.

## 1.55.0 – 2026-11-26
**Übersichtliche Einstellungen**
- **Einstellungen** mit einer Leiste links statt zehn Tabs nebeneinander, in vier Gruppen: **Benutzer & Rechte**
  (Benutzer, Rollen, Gruppen), **Sicherheit** (Zugriff, API), **System** (Allgemein, Benachrichtigungen, Sicherung)
  und **Persönlich** (Mein Konto, Hilfe). Sichtbar sind wie bisher nur Seiten, für die man das Recht hat. Am Handy
  stehen die Seiten als Knöpfe zum Wischen über dem Inhalt.
- **Suchfeld** für die Einstellungen: springt direkt zur passenden Einstellung (z. B. „2FA“, „Bandbreite“, „Passkeys“),
  klappt den Bereich auf und hebt ihn kurz hervor; `/` springt ins Suchfeld. Ohne Treffer geht es in die Hilfe.
- **Allgemein** in Bereiche zum Aufklappen aufgeteilt: Oberfläche, Updates und Neustart, Überwachung, Logs, Anmeldung
  und Sicherheit, Leistung. „Alle aufklappen“ und „Alle zuklappen“; offene Bereiche merkt sich der Browser.

**Aufgabe bearbeiten**
- **Reiter** statt einer langen Seite: Grundlagen, Filter, Verhalten, Prüfen & schützen, Benachrichtigungen, Erweitert.
  Abzeichen zeigen, wo etwas eingestellt ist („3 Regeln“, „2 aktiv“), „Alle anzeigen“ zeigt alles untereinander.
  Fehlt ein Pflichtfeld in einem anderen Reiter, springt das Formular dorthin.
- **Zusammenfassung** oben: Quelle → Ziel, Start, Papierkorb, Prüflauf, Löschwarnung, Verschlüsselung, Zeitfenster.
- **Speichern-Leiste** bleibt beim Scrollen unten. Neu: **Speichern und testen** speichert und startet gleich einen
  Testlauf (braucht `jobs.run`).

**Speicherort bearbeiten**
- Aufgeteilt in **Verbindung**, **Anmeldedaten**, **Erweiterte Optionen** und **Sichtbar für**, Felder zweispaltig.
- **Alles bearbeitbar**: Der **Name lässt sich ändern**, Aufgaben (Quelle, Ziel, SSH-Host) und Speicherorte, die darauf
  aufbauen (z. B. Verschlüsselung), werden mit umgestellt. Geleerte Felder werden entfernt (dann gilt der Standard),
  ein gespeichertes Passwort lässt sich **entfernen**.
- **Alle Einträge (rclone.conf)**: alle gespeicherten Einträge als Text, auch solche ohne eigenes Feld; Passwörter
  stehen als `••••••` da und bleiben erhalten, neue werden verschleiert gespeichert.
- Erweiterte Optionen mit **Suche** und „nur gesetzte anzeigen“; **Speichern und Verbindung testen**.

**Weiteres**
- **Meldungen** oben auf der Seite (z. B. „Aufgabe „rr“ entfernt.“) lassen sich mit **×** wegklicken.
- API und MCP: neu `GET /api/v1/settings/search` bzw. `find_setting` (Einstellung finden, mit Link); `update_remote`
  mit `new_name`, `clear` und `raw`; `get_remote` liefert `raw`. Hilfe und alle Texte in fünf Sprachen.

## 1.54.0 – 2026-11-26
**Hilfe**
- Neue **Hilfe** (Tab „❓ Hilfe“ in den Einstellungen, Knopf „❓ Hilfe“ in jeder Aufgabe): erklärt alles, was man in
  MirrorSync einstellen kann, in 20 Abschnitten von der Aufgabe (Art, Quelle und Ziel, Start und Zeitfenster,
  Optionen, Prüfen und schützen, Verschlüsselung, Skripte) über Speicherorte, Dateimanager, Dashboard,
  Benachrichtigungen, Allgemein, Zugriff, Benutzer, Rollen und Gruppen, Mein Konto und Sicherung bis zur Oberfläche.
- **Suche** über alle Einträge mit Hervorhebung der Treffer; der Link `/help?q=…` merkt sich die Suche. Aus jeder
  Einstellungsseite springt der Tab direkt zum passenden Abschnitt.
- **Schritt-für-Schritt-Anleitungen** mit Beispielen zum Kopieren (mit der eigenen Adresse ausgefüllt): API anbinden
  (Key, curl, Swagger, n8n, Home Assistant `rest_command`), MCP einrichten (Claude Desktop, Claude Code, Cursor und
  VS Code, `mcp-remote`, n8n „MCP Client Tool“) und Überwachung mit Uptime Kuma, Home Assistant (RESTful-Sensor) und
  Prometheus über `/health/jobs` und `/metrics`.
- API und MCP: `GET /api/v1/help` bzw. Tool `get_help` mit `q` (Suche) und `section`, damit auch Assistenten die
  Hilfe nutzen können. Alle Texte in fünf Sprachen.

## 1.53.0 – 2026-11-26
**Ziel verschlüsseln**
- Pro Aufgabe lässt sich das **Ziel verschlüsseln** (Karte „🔒 Ziel verschlüsseln“): MirrorSync legt dafür selbst einen
  verschlüsselten Speicherort (rclone crypt) über das Ziel. Dateiinhalte sind immer verschlüsselt, Datei- und
  Ordnernamen wahlweise verschlüsselt, nur verschleiert oder lesbar; optional mit zweitem Passwort (Salt). Wer Zugriff
  auf Server B hat, sieht nur Zeichensalat.
- Im verschlüsselten Speicherort liegen die Daten im Ordner `data`, der Papierkorb in `data.versions`; im Ziel selbst
  sind Namen und Inhalte nur verschlüsselt zu sehen.
  Papierkorb, Wiederherstellen, Vorschau und Platzbedarf arbeiten entschlüsselt wie gewohnt.
- **Prüflauf** über die Verschlüsselung hinweg: Kann der Speicher Prüfsummen, vergleicht MirrorSync per
  `rclone cryptcheck` echte Prüfsummen, sonst Größe und Anzahl.
- Deutliche Warnung beim Einschalten: Ohne Passwort sind die Daten verloren. Das Passwort muss zweimal eingegeben und
  die Aufbewahrung bestätigt werden. Es wird nie angezeigt oder per API ausgegeben und lässt sich danach nicht ändern
  (beim Speichern kann es optional geprüft werden).
- Ausschalten lässt den verschlüsselten Speicherort bestehen (er erscheint dann unter Speicherorte), sodass die Daten
  lesbar bleiben. Duplizieren übernimmt den Schlüssel. Nicht kombinierbar mit dem Zwei-Wege-Sync.
- In der Übersicht zeigt „🔒 verschlüsselt“ betroffene Aufgaben.
- Neues Recht `jobs.encrypt` („Verschlüsselung des Ziels einrichten oder ausschalten“), nur für Admin vorgegeben.
- API und MCP: Felder `encrypt`, `encrypt_password`, `encrypt_password_confirm`, `encrypt_ack`, `encrypt_names`,
  `encrypt_dirnames`, `encrypt_password2` (Passwörter nur schreibbar), Anzeige `encrypted`. Alle Texte in fünf Sprachen.

## 1.52.0 – 2026-11-25
**Sicher spiegeln**
- **Prüflauf nach dem Sync** (pro Aufgabe: aus, nach jedem Lauf, täglich oder wöchentlich): `rclone check` vergleicht
  Quelle und Ziel und zeigt schwarz auf weiß, ob beide 1:1 gleich sind (Größe, Prüfsumme oder automatisch). Abweichungen
  machen den Lauf zum Fehler, mit Liste im Log. Knopf „🔎 Jetzt prüfen“ im Log prüft, ohne zu spiegeln.
- **Löschwarnung:** Würde ein Lauf mehr als X % der Dateien im Ziel löschen (z. B. 20 %, ab einer Mindestanzahl),
  pausiert er und fragt nach („Freigabe nötig“). Schutz vor Ransomware oder einer versehentlich leeren Quelle. Freigeben
  oder Verwerfen in der Übersicht und im Log, per API/MCP und mit Benachrichtigung.
- **Papierkorb durchsuchen und wiederherstellen:** Gelöschte und überschriebene Dateien aus der Versionierung nach Name
  oder Stand suchen, herunterladen und mit einem Klick in Quelle oder Ziel zurückholen.
- **Speicher am Ziel prüfen:** vor dem Lauf, ob genug Platz frei ist (benötigte Menge laut Testlauf oder fester
  Mindestwert); warnen oder gar nicht erst starten, statt mittendrin abzubrechen.
- **Automatisch neu versuchen:** Scheitert ein Lauf (nur bei Netzproblemen oder bei jedem Fehler), versucht MirrorSync
  es nach z. B. 5, 15 und 60 Minuten erneut und meldet erst danach. Übersteht einen Neustart.
- **Ordner mit `.nosync` überspringen** (bei neuen Aufgaben an): Der Ordner bleibt im Ziel unberührt, statt gelöscht
  zu werden.
- **Snapshot am Ziel** nach jedem erfolgreichen Lauf: ZFS, Btrfs oder eigener Befehl, mit „nur die letzten N behalten“.
- **Skripte vor und nach dem Lauf** (z. B. Datenbank anhalten), im Container oder per SSH auf einem SFTP-Speicherort,
  mit Zeitlimit und Umgebungsvariablen. Neues Recht „Skripte, Snapshots und Wake-on-LAN“.
- **Wake-on-LAN:** Server B vor dem Lauf aufwecken, warten bis er erreichbar ist, und danach per SSH wieder schlafen
  legen.

**Überwachung**
- **Health-Check** `/health/jobs` (und `/health/jobs/<Aufgabe>`) für Uptime Kuma oder Home Assistant: HTTP 200 bzw.
  503, z. B. „1 Aufgaben ok, letzter Sync vor 5 Minuten“. Meldet Fehler, Überfälligkeit, offene Löschwarnung und
  Abweichungen beim Prüflauf. Mit `?format=text` als Klartext.
- **Prometheus-Metriken** `/metrics`: Läufe, Datenmengen, Dauer, Status, Alter des letzten Laufs, Prüfläufe, Volumen.
  Zugriff mit API-Key (Recht „Überwachung“) oder in den Einstellungen ohne Anmeldung freigeben.
- **Statistik pro Monat** (neuer Menüpunkt): Läufe, übertragene Daten, Fehler, Laufzeit je Monat und Aufgabe.
  **Datenvolumen-Limit** pro Monat mit Warnung ab X % und auf Wunsch Anhalten automatischer Läufe.
- **Größte Ordner und Dateien** einer Aufgabe (Quelle oder Ziel) zum Durchklicken, dazu die am häufigsten übertragenen
  Ordner und Dateien laut Logs.

**Benachrichtigungen**
- **Wochenbericht** per Mail, Webhook, Telegram oder Apprise: Läufe, übertragene Daten, Fehler. Tage und Uhrzeit
  einstellbar, „Bericht jetzt senden“.
- **Ruhezeiten:** z. B. nachts nur Fehler oder gar nichts melden, mit Wochentagen.
- **Probe an alle Kanäle** mit einem Klick.
- Neue Ereignisse: Löschwarnung, Speicher knapp, Datenvolumen; Prüfergebnis in den Nachrichten (`{pruefung}`).

**Oberfläche**
- **Als App installierbar (PWA)** auf Handy und PC, mit Offline-Seite.
- **„Neu in dieser Version“:** Beim ersten Anmelden nach einem Update erscheinen die Änderungen.
- Die **Versionsnummer** unten links führt zu allen Versionshinweisen direkt in MirrorSync.
- Die **API-Seite** (Swagger) folgt dem Hell-/Dunkelmodus und hat einen eigenen Umschalter.
- Alles auch per REST-API und MCP (u. a. `verify_job`, `approve_job`, `list_versions`, `restore_versions`, `get_health`,
  `get_stats`, `get_changelog`, `send_report`, `test_notify_all`), neue Rechte, alle Sprachen.

## 1.51.0 – 2026-11-24
**Dashboard**
- **Dashboard** ganz oben in der Seitenleiste, aktualisiert sich alle 5 Sekunden. **Tabs** wie im Browser (anlegen,
  umbenennen, verschieben, löschen), jeder Tab mit eigenen Kacheln; pro Benutzer bzw. API-Key gespeichert.
- **Kacheln frei anordnen:** ziehen oder mit Pfeilen verschieben, an der Ecke unten rechts in Breite (1–12 Spalten)
  und Höhe (1–24 Zeilen) ändern. Kleinere Kacheln rücken automatisch in freie Lücken.
- **Baukasten:** jede Kachel aus Datenquelle (Überblick, laufende Aufträge, Aufgaben, Läufe, nächste Starts,
  Anmeldungen, Audit-Log, Speicherplatz, System), Darstellung und Filter (Aufgaben, Status, Testläufe, Zeitraum bis
  365 Tage, Messwert, Anzahl). Editor mit Live-Vorschau; die Standardkacheln sind Vorlagen und lassen sich umbauen.
- **Darstellungen:** Zahl, Zahl mit Verlauf (Sparkline), Liste, Balken, gestapelte Balken pro Tag, Tortendiagramm,
  Tacho, Liniendiagramm über die Zeit (Anzahl, übertragene Datenmenge, Laufdauer …), Kalender-Heatmap, Zeitleiste der
  Läufe mit Überschneidungen und Statusampel. Angeboten wird nur, was zur Datenquelle passt.
- Die übertragene Datenmenge wird je Lauf gespeichert (Spalte „Übertragen“), ältere Läufe aus dem Log.

**Aufgaben und Speicherorte**
- **Zeitfenster pro Aufgabe:** Beginn, Ende (auch über Mitternacht) und Wochentage. Automatische Starts außerhalb
  werden aufgeschoben, Live-Runden entfallen. Am Fensterende: durchlaufen lassen, anhalten und im nächsten Fenster
  weitermachen, oder anhalten bis zum nächsten regulären Start.
- **Aufgaben und Speicherorte duplizieren** („⧉“); die Kopie einer Aufgabe ist ausgeschaltet, ohne Verlauf.
- **Protokoll eines Speicherorts nachträglich ändern** (z. B. SMB → SFTP); schlägt es fehl, gilt der alte Stand.
- **Spiegeln ohne Löschen:** Option „Im Ziel nichts löschen“ (`rclone copy` statt `sync`), auch in der Vorschau.

**System**
- **Container neu starten:** von Hand oder nach Zeitplan (Uhrzeit, Wochentage; wartet auf laufende Aufgaben). Mit
  Docker-Socket über Docker, sonst beendet sich MirrorSync und Docker startet es über `restart: unless-stopped` neu.
- **Alte Images:** nach einem Selbst-Update wird das alte Image gelöscht (abschaltbar), dazu „Alte Images entfernen“.
- **Oberfläche:** Start-Knopf so hoch wie die übrigen Knöpfe, Pfeil der Seitenleiste mittig am Rand, Fenster wie die
  Audit-Details sind modal. Größenangaben auch in GB/TB.

**Rechte, API/MCP, Sprachen**
- Neues Recht `system.restart`; Dashboard-Kacheln brauchen das Recht ihrer Datenquelle (`jobs.view`, `users.view`,
  `system.audit`, `system.settings`). Zeitfenster wie die übrigen Aufgaben-Einstellungen (`jobs.edit`).
- API/MCP: `get_dashboard`, `update_dashboard`, `duplicate_job`, `duplicate_remote`, `update_remote` mit `type`,
  `no_delete`, `window`, `get_restart`, `restart_container`, `update_restart_settings`, `list_old_images`,
  `prune_images`, `selfupdate_prune`. Alles im Audit-Log, alle 5 Sprachen.

## 1.50.0 – 2026-11-23
- **Aufträge-Fenster bleibt offen.** Läuft eine Aufgabe, lud sich die Übersicht (und die Seiten einer Aufgabe und ihr
  Live-Log) alle 3 Sekunden neu und schloss dabei das Fenster „Aufträge“ oben rechts. Jetzt pausiert das Neuladen,
  solange das Fenster, ein Menü oder ein Dialog offen ist oder Text markiert wird. Das Fenster bleibt auch beim
  Wechsel auf eine andere Seite offen, bis man es schließt (✕, Klick daneben oder Esc).
- **Woran eine Änderung erkannt wird, pro Aufgabe wählbar:** Größe und Änderungszeit (Standard), nur Größe, Prüfsumme
  oder Änderungszeit mit Toleranz in Sekunden (z. B. 2 für FAT/exFAT, 3600 nach der Zeitumstellung). Ersetzt das
  Häkchen „Vergleich per Prüfsumme“ (wird übernommen). Die Vorschau rechnet mit derselben Einstellung.
- **Tempo pro Aufgabe:** Schonend (2 parallel), Normal (4), Schnell (8, mit `--fast-list`), Sehr schnell (16). Für
  den Dateimanager unter Einstellungen → Allgemein → Dateimanager. Eine eigene Index-Datenbank gibt es bewusst
  nicht, weil sie nur den Vergleich beschleunigt und veraltet Änderungen übersehen könnte.
- API/MCP: `compare`, `compare_window`, `speed` bei Aufgaben (`checksum` bleibt als veralteter Schalter), `compare`
  bei `preview_job`, neu `update_files_settings` und `files.speed` in `get_settings`. Rechte: wie die übrigen
  Optionen (`jobs.edit`), Dateimanager-Tempo mit `system.settings`. Audit-Log nennt die neuen Felder. Alle 5
  Sprachen.

## 1.49.0 – 2026-11-23
- **Dateien: Gesamtfortschritt beim Kopieren und Verschieben.** Über den Listen erscheint während eines Auftrags
  eine Karte mit dem Fortschritt über alle Einträge: Prozent und Balken, Bytes „x von y“, Dateien „x von y“,
  Geschwindigkeit, Restzeit und aktueller Eintrag („Eintrag 2 von 5“). Vorher wird die Gesamtgröße ermittelt,
  bis dahin steht „Gesamtgröße wird ermittelt …“. Bei mehreren Aufträgen gibt es zusätzlich eine Zeile „Gesamt“.
  Das Aufträge-Fenster zeigt dieselben Angaben. Vorher zählte der Prozentwert nur pro Eintrag.
- API/MCP `list_file_tasks` liefert neu `bytes_done`, `bytes_total`, `files_done`, `files_total`, `speed`, `eta`,
  `item`, `items` und `current`; `progress` ist jetzt der Gesamtwert. Rechte unverändert (`files.view` zum
  Ansehen, `files.edit` bzw. `files.delete` für die Aufträge). Alle 5 Sprachen.

## 1.48.0 – 2026-11-23
- **Speicherort testen: SFTP und FTP zeigen das Stammverzeichnis.** „Testen“ listet bei SFTP und FTP jetzt die
  Ordner in `/` statt im Home-Ordner des Benutzers (bei `root` standen dort nur `.local` und `.ssh`). Die Meldung
  nennt den gelisteten Pfad. Pfade in Aufgaben bleiben unverändert. API/MCP `test_remote` liefert dasselbe. Recht
  `remotes.test` wie bisher. Alle 5 Sprachen.

## 1.47.0 – 2026-11-23
- **Vorschau: „Nach oben“ bis zum Stammverzeichnis.** In allen Vorschau-Browsern (Fenster „Ergebnis“ und
  „Änderungen“ sowie die Seite „Ergebnis im Browser“) geht „Nach oben“ bzw. „⬆ ..“ jetzt über das Ziel hinaus bis
  zum Stammverzeichnis des Speicherorts. Dort stehen die echten Ordner, wie sie jetzt sind; der Weg zum Ziel ist
  markiert („→ zum Ziel“, „🎯 Ziel der Aufgabe“, noch fehlende Ordner „wird angelegt“), ein Klick führt zurück in
  die Vorschau. Braucht zusätzlich das Recht `remotes.browse`. API/MCP: `path` mit `../` bei `preview_job` und
  `preview_paths` (`status: outside`, `target: way/dest`).
- **Updates: „Speichern“ und „Jetzt prüfen“ getrennt.** „Speichern und jetzt prüfen“ entfällt, „Jetzt prüfen“ prüft
  sofort, ohne Eingaben zu speichern, und verschickt bei einer neuen Version die Benachrichtigung (falls
  eingeschaltet). API/MCP `check_update` macht dasselbe und liefert zusätzlich `message`. Recht `system.settings`.
  Alle 5 Sprachen.

## 1.46.0 – 2026-11-23
- **Ergebnis im Browser öffnen:** Neuer Knopf neben „Vorschau der Ordnerstruktur“ (und im Vorschau-Fenster). Er
  öffnet in einem neuen Tab eine Seite, die aussieht wie **Dateien** (Pfadzeile, „Nach oben“, Name, Größe mit Anzahl
  Dateien, Geändert, Rechte), aber das Ziel nach dem Lauf zeigt, schreibgeschützt. Was gelöscht wird, fehlt.
  „Änderungen markieren“ zeigt zusätzlich neu, wird aktualisiert und wird gelöscht. Recht `jobs.preview`.
- **Benachrichtigung bei neuer Version:** Unter Einstellungen → Allgemein → Updates lässt sich einschalten, dass eine
  Nachricht kommt, sobald eine neue MirrorSync-Version verfügbar ist, je Version genau einmal, optional nur über
  bestimmte Kanäle. Eigener Text unter „Texte der Benachrichtigungen“ (Ereignis „Neue MirrorSync-Version
  verfügbar“). API/MCP: `update_notify`, `update_notify_channels` bei `update_update_settings`, `get_update` liefert
  `notify`, `notify_channels`, `notified`. Recht `system.settings`, Audit-Log und alle 5 Sprachen angepasst.

## 1.45.0 – 2026-11-23
- **Vorschau „✅ Ergebnis“:** zeigt das Ziel genau so, wie es nach dem Lauf aussieht, fast wie der Datei-Browser
  (Ordner zum Durchklicken, Name, Größe, Geändert). Was gelöscht wird, ist dort nicht mehr zu sehen. Das ist jetzt
  die Standardansicht. Die Ansicht mit allen Markierungen heißt „📂 Änderungen“, der Baum bleibt. API/MCP:
  `preview_job` und `preview_paths` mit `result: true` (Text, Einträge und Baum ohne Gelöschtes). Recht
  `jobs.preview` wie bisher. Alle 5 Sprachen.

## 1.44.0 – 2026-11-23
- **Vorschau zum Durchklicken wie im Datei-Browser.** Die Vorschau der Ordnerstruktur öffnet jetzt eine Ansicht wie
  der Datei-Browser: Ordner anklicken, Pfadleiste und „⬆ ..“ zum Zurückgehen, Spalten Name, Änderung (neu, wird
  aktualisiert, wird gelöscht, kommt nach A, mit Zählern an Ordnern), Größe und Geändert, Suche im Ordner und
  „Nur Änderungen zeigen“. Die bisherige Baumansicht gibt es weiter über „🌳 Baum“. API/MCP: `preview_job` und
  `preview_paths` können mit `path` einen Ordner öffnen (`entries`) und mit `only_changes` nur Änderungen liefern.
  Recht `jobs.preview` heißt jetzt „… ansehen und durchklicken“. Alle 5 Sprachen.

## 1.43.0 – 2026-11-23
- **Vorschau der Ordnerstruktur.** In einer Aufgabe zeigt der neue Knopf „🗂 Vorschau der Ordnerstruktur“, wie das
  Ziel nach dem nächsten Lauf aussieht: aufklappbarer Ordnerbaum, jeder Eintrag markiert als neu, wird
  aktualisiert, wird gelöscht oder unverändert, mit Zählern an den Ordnern. Nimmt die Werte aus dem Formular (auch
  ungespeichert) und dieselben Regeln wie der echte Lauf (Auswahl, Ausschlüsse, Quellordner mitkopieren,
  Zwei-Wege). Kopiert und löscht nichts. Neues Recht `jobs.preview` (Admins und Operator), API/MCP `preview_job`
  und `preview_paths`, alle 5 Sprachen.

## 1.42.0 – 2026-11-23
- **Selbst-Update über den Docker-Socket (optional).** Ist `/var/run/docker.sock` eingebunden, gibt es unten links
  beim Update-Hinweis und unter Einstellungen → Allgemein → Selbst aktualisieren den Knopf **„Jetzt aktualisieren“**,
  wahlweise auch **automatisch einmal am Tag** ab einer Uhrzeit. Ein kurzlebiger Hilfs-Container tauscht den
  Container gegen einen neuen mit **identischen Einstellungen** aus (Name, Ports, Volumes, Umgebungsvariablen,
  Netzwerke mit fester IP/MAC, Neustart-Regel, Labels inkl. Docker Compose, sodass Compose, Dockhand und Portainer
  ihn weiter erkennen). Startet die neue Version nicht, läuft automatisch wieder die alte (Rollback). Ohne Socket
  ist alles ausgeschaltet. Neues Recht `system.update`, Audit-Einträge „Update gestartet / abgeschlossen /
  fehlgeschlagen“, API/MCP `get_self_update`, `self_update`, `selfupdate_auto`/`selfupdate_time` in
  `update_update_settings`, alle 5 Sprachen. Sicherheitshinweis in README und Compose-Datei.
- `docker stop` beendet MirrorSync jetzt sofort sauber, statt nach 10 Sekunden hart abgebrochen zu werden.

## 1.41.0 – 2026-11-23
- **2FA erzwingen**, global und pro Benutzer. Unter Einstellungen → Allgemein → Anmeldung und Sicherheit:
  *Aus (nur pro Benutzer)*, *Für neue Benutzer* oder *Für alle Benutzer*. Unter Benutzer → Bearbeiten das Häkchen
  „2FA erzwingen“. Betroffene Benutzer landen nach der Anmeldung bei „Mein Konto“ mit dem QR-Code und können
  nichts anderes tun, bis die 2FA eingerichtet ist; ausschalten kann sie danach nur ein Admin. Die Benutzerliste
  zeigt „Pflicht, noch nicht eingerichtet“. API/MCP: `require_2fa_mode` bei `update_security_settings`,
  `require_2fa` bei `create_user`/`update_user`, `get_user` liefert `require_2fa`, `must_2fa`, `totp_setup_pending`.
  Rechte: `system.settings` bzw. `users.manage`. Audit-Log und alle 5 Sprachen angepasst.
- **Benachrichtigungen per API und MCP anlegen:** neue Aktionen `setup_notification_channel`
  (`POST /api/v1/settings/notifications/channels/{channel}`, Kanäle webhook, smtp, telegram, apprise mit
  verständlichen Feldern, Apprise-URLs auch anhängen mit `add_urls`, optional gleich `test: true`) und
  `remove_notification_channel` (ausschalten, mit `forget: true` auch Zugangsdaten löschen). Recht `notify.edit`.
- Die Versionsnummer unten links ist jetzt ein Link zu den Versionshinweisen auf GitHub.
- Behoben: Neben den Reitern in den Einstellungen stand rechts ein kleiner Scrollbalken. Die Reiter lassen sich
  auf schmalen Bildschirmen weiter wischen, aber ohne sichtbaren Balken.
- Audit-Log: verständliche Namen für weitere Benachrichtigungs-Felder (z. B. Telegram-Chat-ID, Webhook aktiv).

## 1.40.1 – 2026-11-23
- **Behoben: Update-Prüfer (z. B. Dockhand) meldeten ständig ein ausstehendes Update.** Bisher wurde das Image
  bei jedem Push auf GitHub neu gebaut und als `:latest` veröffentlicht, auch bei Änderungen, die das Image gar
  nicht betreffen (Anleitung, Workflows, Android-App, Dependabot). Jeder Build hatte außerdem eine neue Bauzeit und
  zusätzliche Nachweis-Daten, dadurch änderte sich jedes Mal die Prüfsumme (Digest). Dockhand vergleicht genau
  diese und meldete deshalb „Update ausstehend“, obwohl die Version gleich blieb. Jetzt wird das Image nur noch
  veröffentlicht, wenn sich die Versionsnummer ändert, und gleiche Quellen ergeben das gleiche Image.
- Basis-Image ist jetzt `python:3.15-alpine` (Dependabot-Update).

## 1.40.0 – 2026-11-23
- **Android-App** (neu, Ordner `android/` im GitHub-Repo): MirrorSync als App auf dem Handy. Eine schlanke Hülle
  um die Weboberfläche ohne Browserleiste, jede neue Funktion ist also sofort in der App. Die APK hängt an jedem
  GitHub-Release (`mirrorsync-1.40.0.apk`).
  - Beim ersten Start die Server-Adresse eingeben (wird über `/health` geprüft), später ändern über die
    Zurück-Taste, den Fehlerbildschirm oder langes Drücken auf das App-Symbol.
  - Anmelden, 2FA und „Angemeldet bleiben“ wie im Browser; **Passkeys** gehen auch in der App (siehe unten).
  - **Benachrichtigungen** bei fehlgeschlagenen Läufen (wahlweise auch erfolgreiche/abgebrochene) mit
    kopiert/gelöscht/Fehler; Tippen öffnet das Log. Die App prüft im Hintergrund alle 15 Minuten bis 6 Stunden,
    mit ihrer Anmeldung oder einem optionalen API-Key.
  - Downloads (Logs, Audit-CSV, Backup-Export) landen im Download-Ordner, Datei-Upload für den Backup-Import geht.
  - Hell/Dunkel folgt der Weboberfläche, HTTP im Heimnetz und selbst signierte Zertifikate (nach Rückfrage) gehen.
- Server: neuer öffentlicher Endpunkt `/.well-known/assetlinks.json` (Digital Asset Links), damit Android der App
  die Passkeys deiner Domain erlaubt. Die Passkey-Anmeldung akzeptiert zusätzlich zur HTTPS-Adresse die Herkunft
  der App. Selbst gebaute APK mit eigenem Schlüssel: dessen SHA-256-Fingerabdruck über `MIRRORSYNC_ANDROID_CERTS`.

## 1.39.0 – 2026-11-23
- **Alte Logs löschen** als eigener Punkt unter Einstellungen → Allgemein: Datum wählen, „Anzahl anzeigen“ zeigt,
  wie viele Läufe in wie vielen Aufgaben vor diesem Datum gestartet sind, „Jetzt endgültig löschen“ (mit
  Rückfrage) löscht sie einmalig samt Log. Laufende Aufgaben bleiben unberührt, Eintrag im Audit-Log.
  API/MCP: `POST /logs/purge` (`purge_logs`) mit `before` (JJJJ-MM-TT) und `dry_run`, Recht „allgemeine Einstellungen“.
- Die dauerhafte Regel „Nur Logs ab diesem Datum behalten“ aus 1.38.0 entfällt dafür (auch `log_keep_from` in
  der API). Läufe pro Aufgabe (0 = unbegrenzt) und Alter in Tagen, Wochen oder Monaten bleiben.

## 1.38.0 – 2026-11-23
- **Log-Aufbewahrung flexibler** (Einstellungen → Allgemein → Logs aufbewahren):
  - „Läufe pro Aufgabe behalten“ erlaubt jetzt 0 = unbegrenzt.
  - Das Alter gibst du als Zahl in Tagen, Wochen oder Monaten an (ein Monat = 30 Tage, 0 = unbegrenzt).
  - Neu: „Nur Logs ab diesem Datum behalten“. Ältere Läufe werden gelöscht, leer = kein Datum.
  - Sind mehrere Grenzen gesetzt, gilt die, die zuerst greift. Der neueste Lauf bleibt immer erhalten.
- API/MCP: `PATCH /settings/logs` (`update_log_settings`) mit `log_keep_runs` 0–1000 und neu `log_keep_from`
  (`JJJJ-MM-TT`). Änderungen stehen im Audit-Log, alle Texte in 5 Sprachen.

## 1.37.3 – 2026-11-23
- Der stündliche Sicherheits-Scan läuft jetzt immer zur vollen Stunde.

## 1.37.2 – 2026-11-23
- Der Sicherheits-Scan des veröffentlichten Images (`:latest`) auf GitHub läuft jetzt einmal pro Stunde statt
  einmal pro Woche. Neue Schwachstellen erscheinen so spätestens nach einer Stunde unter „Security“. An der App
  selbst ändert sich nichts.

## 1.37.1 – 2026-11-23
- Erster Trivy-Scan: 5 Funde (Stufe „hoch“), alle in alten Kopien von urllib3, msgpack und setuptools, die pip
  selbst mitbringt. MirrorSync nutzt sie nicht, pip wird nur zum Bauen gebraucht. pip und setuptools werden jetzt
  nach der Installation aus dem Image entfernt, damit sind diese Funde weg. Betriebssystem und rclone: keine Funde.

## 1.37.0 – 2026-11-23
- **Abhängigkeiten aktualisiert:** rclone 1.68 → 1.76, Python 3.12 → 3.14 (Alpine), Flask 3.0.3 → 3.1.3,
  APScheduler 3.10.4 → 3.11.3, tzdata 2024.2 → 2026.6, segno 1.6.1 → 1.6.6. Waitress, Apprise, webauthn und
  swagger-ui-bundle waren schon aktuell. Spiegeln, Zwei-Wege-Sync, GUI, API, MCP, 2FA-QR-Code und Passkeys getestet.
- **Automatische Prüfungen auf GitHub:** Dependabot meldet jede Woche neue Versionen der Python-Pakete, der
  Basis-Images und der GitHub Actions als Pull Request. Trivy scannt jedes neu gebaute Image und einmal pro Woche
  das aktuelle Image auf bekannte Schwachstellen, die Ergebnisse stehen im Repo unter „Security“.

## 1.36.0 – 2026-11-23
- **Ersteinrichtung ohne Einmal-Code:** Solange noch kein Benutzer existiert, legt der erste Aufruf im Browser
  direkt den Admin an (Benutzername und Passwort genügen). Der Einrichtungs-Code aus dem Container-Log entfällt.
- Wer den Code weiter möchte (z. B. wenn der Container schon vor der Einrichtung aus dem Internet erreichbar ist),
  setzt `SETUP_TOKEN=true`. Dann verhält sich die Einrichtung wie bisher. Hinweis zum Risiko in der Anleitung.
- Bestehende Installationen mit Benutzern betrifft das nicht.

## 1.35.0 – 2026-11-23
- **Zwei-Wege-Sync legt fehlende Ordner an:** Gibt es beim ersten Lauf den Ordner von Seite A oder Seite B noch
  nicht, wird er angelegt (bisher brach der Lauf mit „directory not found“ ab, außer bei „Quellordner selbst
  mitkopieren“). Das Log nennt jeden angelegten Ordner, ein Testlauf zeigt, was angelegt würde.
- Schutz bei späteren Läufen: Fehlt eine Seite, die schon einmal da war, oder ist sie leer (z. B. Laufwerk nicht
  eingehängt), wird weiterhin nichts angelegt oder verteilt. Der Lauf bricht ab und das Log erklärt den Grund und
  den nächsten Schritt („Neu zusammenführen“). Auch „Neu zusammenführen“ legt dann keinen Ordner an.
- Ein Testlauf mit fehlendem Ordner verlangt danach kein „Neu zusammenführen“ mehr.
- **Abstand der Update-Prüfung einstellbar:** Unter Einstellungen → Allgemein → Updates gibst du eine Zahl ein und
  wählst Minuten oder Stunden (5 Minuten bis 720 Stunden). Standard ist jetzt 1 Stunde (bisher fest 6 Stunden).
  API/MCP: `update_interval` (in Minuten) in `PATCH /settings/update` (`update_update_settings`), `interval_minutes`
  in `GET /update`. Recht wie bisher „allgemeine Einstellungen“, Änderungen stehen im Audit-Log.
- Neue Log-Hinweise in allen 5 Sprachen.

## 1.34.0 – 2026-11-23
- **Hinweis auf neue Versionen:** MirrorSync fragt alle 6 Stunden bei GitHub nach, ob es eine neuere Version gibt.
  Wenn ja, steht unten links unter der Versionsnummer „⬆ vX.Y.Z verfügbar“ mit Link zum Release. Abschaltbar unter
  Einstellungen → Allgemein → Updates, dort auch „Speichern und jetzt prüfen“ und der Stand der letzten Prüfung.
  Übertragen wird nur die eigene Versionsnummer. Änderung der Einstellung steht im Audit-Log. API/MCP:
  `GET /update` (`get_update`), `POST /update/check` (`check_update`, Recht „allgemeine Einstellungen“),
  `PATCH /settings/update` mit `update_check` (`update_update_settings`), außerdem `update` in `/status` und
  `get_settings`. Anderes Repo per Umgebungsvariable `UPDATE_REPO`. Alle Texte in 5 Sprachen.
- Behoben: Einige Texte erschienen in anderen Sprachen noch auf Deutsch: „aktiv“, „immer“, „aus“ und „manuell“ auf
  der Seite Zeitpläne, „sonst“/„immer“ in der Vorschau der Bandbreite sowie die Namen der Speicherarten „S3 und
  S3-kompatibel“ und „Verschlüsselung (crypt)“ in der Auswahl beim Anlegen eines Speicherorts.
- MirrorSync gibt es jetzt auch auf GitHub: https://github.com/DerMilderJoghurt/mirrorsync, mit fertigem Image
  `ghcr.io/dermilderjoghurt/mirrorsync`. Die Versionen 1.33.1 und 1.33.2 betrafen nur das GitHub-Repo.

## 1.33.0 – 2026-11-23
- **Nächster Lauf in der Aufgaben-Übersicht:** Unter dem Status steht bei jeder Aufgabe, wann sie das nächste Mal
  startet („heute, 14:30“, „morgen, 03:00“ oder Datum), auch auf dem Handy. Live-Aufgaben zeigen die nächste Runde,
  Folgeaufgaben eine Schätzung über den Vorgänger („ca. …“, bzw. „wenn „…“ fertig ist“, solange er läuft), sonst
  „nur manuell“, „pausiert“ oder „keiner geplant“. API/MCP: `next_start` (ISO-Zeit) und `next_start_kind` in
  `list_jobs` und `get_job`.
- **Zwei-Wege-Sync mit Ordnerauswahl und „Quellordner selbst mitkopieren“:** wie beim Spiegeln, auch per Häkchen
  im Durchsuchen-Fenster. Die Auswahl gilt für beide Seiten, alles andere bleibt auf beiden Seiten unberührt. Mit
  dem Häkchen wird `<Seite B>/<Ordnername>` beim ersten Lauf angelegt und abgeglichen. Das Formular zeigt das
  Ergebnis an. Eine Änderung daran führt beim nächsten Lauf neu zusammen (ohne Löschen).
- **Seitenleiste einklappbar:** Pfeil oben neben „MirrorSync“ klappt auf nur Symbole ein (mit Namen beim
  Überfahren), der Inhalt nutzt die frei werdende Breite. Gespeichert je Benutzer im Konto, gilt also auf allen
  Geräten. Kein neues Recht nötig. API/MCP: Feld `sidebar` (`full`/`mini`) bei `get_user`, `list_users` und
  `update_user` (Recht „Benutzer verwalten“), Änderung steht im Audit-Log.
- Alle neuen Texte in 5 Sprachen.

## 1.32.0 – 2026-11-23
- **Audit-Log mit Details:** Klick auf einen Eintrag öffnet ein Fenster mit allen Infos: Herkunft (Weboberfläche mit
  Browser, REST-API oder MCP, Anfrage), vollständige alte und neue Werte, bei Listen „+ hinzugefügt / − entfernt“,
  beim Löschen der ganze Inhalt. Dateimanager: Pfad, Größe, Dateien in gelöschten Ordnern, geänderte Zeilen beim
  Bearbeiten (Geheimnisse maskiert), Von/Nach bei Kopieren und Verschieben. Starts mit Quelle, Ziel und Lauf.
- **Hostnamen (FQDN) in Erlaubt- und Sperrliste**, z. B. `buero.example.de` oder `facebook.com`. Aufgelöst wird bei
  der Anfrage per DNS (5 Minuten Cache), die Seite zeigt die aktuellen Adressen.
- **Länder-Datenbank nach Zeitplan:** wahlweise wie bisher nach Intervall oder zu einer Uhrzeit an gewählten
  Wochentagen. API: `geoip_mode`, `geoip_time`, `geoip_dow`.
- Die Sperrseite „Zugriff gesperrt“ nennt den Notfall-Schalter `IPGUARD_RESET` nicht mehr (nur noch im README).
- API/MCP, Audit-Bezeichnungen und alle 5 Sprachen angepasst.

## 1.31.0 – 2026-11-23
- **Zwei-Wege-Sync** (rclone bisync): In der Aufgabe wählt man zuerst die Art („Spiegeln (Einweg)“ oder
  „Zwei-Wege-Sync“), danach Seite A und Seite B. Änderungen und Löschungen auf beiden Seiten werden übertragen.
  Erster Lauf führt beide Seiten ohne Löschen zusammen. Konfliktregel (neuere gewinnt, beide behalten, A oder B
  gewinnt; Verlierer bleibt als `.konflikt1` erhalten), Löschschutz in Prozent, „Neu zusammenführen“ nach einem
  Abbruch. Funktioniert auch live. Übersicht, Zeitpläne und Log zeigen ⇄.
- Neues Recht **„Zwei-Wege-Sync einrichten“** (Operator hat es, Admin sowieso).
- **Aufträge-Fenster** zeigt jetzt auch gerade laufende Aufgaben mit Prozent, Balken, Log-Link und Stopp; sie
  zählen in der Zahl am Knopf mit und verschwinden nach dem Ende. Der Knopf erscheint auch mit Recht „Aufgaben ansehen“.
- API/MCP: Felder `direction`, `bisync_conflict`, `bisync_max_delete`, Endpunkte `POST /jobs/{id}/resync` und
  `GET /jobs/running` (Tools `resync_job`, `list_running_jobs`). Audit-Log mit „Art“, „Konfliktregel“,
  „Löschschutz (%)“ und „neu zusammengeführt“. Alles in 5 Sprachen.
- Live-Log: Hinweiszeilen werden jetzt in der gewählten Sprache angezeigt.

## 1.30.0 – 2026-11-23
- **Live wie Spiegeln:** Jede Live-Runde gleicht jetzt standardmäßig wie ein normaler Spiegel-Lauf ab
  (`rclone sync`), Löschungen und Umbenennungen in der Quelle kommen also sofort im Ziel an. „Max. Löschungen“,
  Versionierung und Ausschlüsse gelten in jeder Runde. Runden ohne Änderung bleiben still. Bestehende
  Live-Aufgaben nutzen ab jetzt diesen Modus.
- Alternativ **„Schnell“**: wie bisher nur neue und geänderte Dateien kopieren (`--max-age`), nichts löschen,
  für sehr große Quellen.
- Voller Abgleich im Modus „Schnell“ jetzt auch **nach Intervall** (alle X Minuten oder Stunden), neben Uhrzeit
  und Cron. Auch auf der Seite Zeitpläne einstellbar.
- API/MCP: Feld `live_mode` (mirror|fast), `live_full` akzeptiert `@every 6h` / `@every 90m`,
  `set_job_trigger` hat `mode`. Audit-Log zeigt „Live-Modus“. Alles in 5 Sprachen.

## 1.29.0 – 2026-11-23
- Dateimanager: **Rechtsklick-Kontextmenü** mit allen Aktionen (Öffnen, Bearbeiten, Herunterladen,
  Eigenschaften, Größe berechnen, Umbenennen, Kopieren/Verschieben nach …, auf die andere Seite, Löschen), auch
  für mehrere markierte Einträge. Auf freier Fläche: Neuer Ordner, Neue Datei, Hochladen, Neu laden,
  Ordnergrößen, Alle auswählen.
- **Aufträge-Knopf oben rechts** auf allen Seiten (mit Recht „Dateien ansehen“). Die Zahl zeigt, wie viele
  Aufträge gerade laufen. Ein Klick öffnet ein schwebendes Fenster mit allen Aufträgen, dort kann man sie
  abbrechen und entfernen. Der Kasten über den Listen ist weg.

## 1.28.0 – 2026-11-23
- Dateimanager: **Drag & Drop**. Dateien und ganze Ordner vom Computer hineinziehen lädt sie hoch. Zeilen auf
  die andere Seite ziehen kopiert sie (mit Umschalttaste: verschieben), auf einen Ordner ziehen legt sie hinein.
  Vorher kommt eine Rückfrage, bei Konflikten einmal „alle überschreiben / überspringen“.
- Dateimanager: Die Ansicht passt sich an. Ein Speicherort nimmt die ganze Breite ein, zwei je die Hälfte. Die
  Listen reichen bis zum unteren Rand und scrollen für sich.
- Dateimanager: „berechnen“ und „Ordnergrößen“ zeigen jetzt auch die Anzahl der Unterordner und Dateien (API
  `file_size`: `dirs`, `files`).
- Dateimanager: Die Aufträge zeigen Status und Prozent, der Balken ist farbig (blau läuft, grün fertig, rot
  Fehler). Fertige Aufträge lassen sich einzeln oder alle auf einmal entfernen, auch per API/MCP
  (`delete_file_task`, `clear_file_tasks`, Recht „Dateien bearbeiten“).
- Dateimanager: Fehlende Änderungszeit oder Berechtigungen (z. B. bei SMB) erscheinen als „–“ statt als leeres
  Kästchen.

## 1.27.0 – 2026-11-23
- Neu: **Dateimanager** (Seitenleiste „Dateien“). Man wählt einen Speicherort, mit „Zwei Speicherorte
  nebeneinander“ auch zwei. Darin kann man browsen, Ordnergrößen und Berechtigungen (rwx, Besitzer) ansehen,
  Textdateien bearbeiten, hoch- und herunterladen, Ordner und Dateien anlegen, umbenennen und löschen sowie
  kopieren und verschieben, innerhalb oder zwischen beiden Seiten. Kopieren und Verschieben laufen im
  Hintergrund mit Fortschritt und lassen sich abbrechen. Vor dem Löschen und dem Überschreiben kommt eine
  Rückfrage.
- Neue Rechte „Dateimanager: Dateien ansehen / bearbeiten / löschen“ (Admins haben sie, andere Rollen nicht
  automatisch). Es gelten die Beschränkung der Rolle und „Sichtbar für“. Audit-Log-Kategorie „Dateien“.
- API/MCP: 15 neue Endpunkte bzw. Tools (`list_files`, `read_file`, `write_file`, `upload_file`,
  `download_file`, `copy_files`, `move_files`, `delete_files` …).
- Geändert: Bei gesetzter Auswahl („Nur diese Dateien und Ordner“) ist „Quellordner selbst mitkopieren“
  automatisch aus, im Formular ausgegraut, und wird auch bei bestehenden Aufgaben ignoriert. Die gewählten
  Ordner landen dann direkt im Ziel (vorher z. B. `ziel/share/10-Temp` statt `ziel/10-Temp`).

## 1.26.0 – 2026-11-23
- Neu: Beim Anlegen eines Speicherorts steht der **Standard-Port** des Typs schon im Feld (SMB 445, SFTP 22,
  FTP 21) und wechselt mit dem Typ. Bei FTP mit „tls“ = ja springt er auf 990 und zurück, solange man keinen
  eigenen Port eingetragen hat. Per API/MCP gilt ohne `port` wie bisher der Standard von rclone.

## 1.25.0 – 2026-11-23
- Neu: **Sprache der API-Antworten pro Key** (Einstellungen → API, beim Anlegen und Bearbeiten). Standard
  „Wie der Benutzer“: Meldungen, Swagger-Beschreibungen und MCP-Tool-Texte kommen in der Sprache des
  Benutzers, der den Key angelegt hat. Ohne bekannten Benutzer und vor der Anmeldung (z. B. „API-Key fehlt“)
  Englisch statt bisher der Systemsprache. `?lang=` und `Accept-Language` überschreiben weiterhin.
  API/MCP: Feld `lang` bei `create_api_key`/`update_api_key`, `effective_lang` in der Key-Ansicht; Audit-Log.
- Behoben: Einige Fehlermeldungen der API (Key ungültig, deaktiviert, falsche IP, zu viele Anfragen) und der
  MCP-Begrüßungstext waren nicht übersetzt.

## 1.24.0 – 2026-11-23
- Neu: **API-Key später nochmal anzeigen** (Einstellungen → API → „Anzeigen“) nach Bestätigung mit Passwort
  (+ 2FA-Code, falls eingerichtet) oder Passkey. Nur in der Web-GUI, nicht per API/MCP. Audit-Log
  „API-Key angezeigt“ bzw. „… abgelehnt“, Fehlversuche zählen wie falsche Passwörter. Neue Keys werden dazu
  verschlüsselt gespeichert. **Keys von vor 1.24.0 sind nicht anzeigbar** (nur Hash vorhanden).
- Neu: **API-Key bearbeiten**: Name, Rolle/Rechte, Ablauf, IPs, Gruppen, **deaktivieren/aktivieren**,
  **Pause von–bis** und **wöchentliche Zeitfenster**. Status in der Liste. API `PATCH /api-keys/{id}`,
  MCP `update_api_key`, Audit mit Vorher/Nachher.
- Neu: Versionierung mit **„Versionen behalten“** (Anzahl) und **„höchstens Tage“**; ältere Versionsordner
  werden nach jedem erfolgreichen Lauf entfernt (steht im Lauf-Log). Auch per API/MCP (`versions_keep`,
  `versions_days`).
- Geändert: Löschknöpfe heißen überall „Entfernen“ (API-Keys, Benutzer, Rollen, Gruppen, Sicherungen).
- Geändert: Swagger-Dokumentation und openapi.json öffnen in einem neuen Tab.
- Geändert: Mehr Abstand zwischen Sprachauswahl und „Deine letzten Anmeldungen“ (Mein Konto).

## 1.23.0 – 2026-11-23
- Neu: **API-Keys löschen** (Einstellungen → API, Knopf „Löschen“ mit Rückfrage): entfernt den Key ganz,
  auch aus Gruppen. Audit-Log-Eintrag „API-Key gelöscht“; frühere Einträge des Keys bleiben. Den gerade
  benutzten Key kann man nicht löschen. API `DELETE /api-keys/{id}`, MCP `delete_api_key`.
- **Geändert (REST):** Widerrufen ist jetzt `POST /api-keys/{id}/revoke` (vorher `DELETE /api-keys/{id}`,
  das jetzt endgültig löscht). Das MCP-Tool `revoke_api_key` heißt gleich und widerruft weiterhin.
- Geändert: In der Aufgabenübersicht und auf der Aufgabenseite heißt der Knopf „Entfernen“ (EN Remove,
  ES Quitar, IT Rimuovi, FR Retirer).

## 1.22.0 – 2026-11-23
- Neu: **Gruppen** (Einstellungen → Gruppen, neues Recht „Gruppen verwalten“): Benutzer und API-Keys als
  Mitglieder, optional zusätzliche Rechte (Rolle + Rechte aller Gruppen; nur Rechte, die man selbst hat).
  Mitgliedschaft auch beim Benutzer einstellbar, Gruppen in der Benutzerliste sichtbar.
- Neu: **„Sichtbar für“** bei jeder Aufgabe und jedem Speicherort: alle mit Recht (Standard) oder nur
  ausgewählte Benutzer und Gruppen. Gilt überall (Übersicht, Zeitpläne, Ketten, Quelle/Ziel, API, MCP).
  Admins und der Ersteller einer Aufgabe sehen sie immer; sich selbst ausblenden geht nicht.
- API/MCP: `list_groups`, `get_group`, `create_group`, `update_group`, `delete_group`; `visible_to` bei
  Aufgaben und Speicherorten, `groups` bei Benutzern und API-Keys. Gleiche Prüfungen und Audit wie in der GUI.
- Audit-Log: Gruppen, Mitglieder und „Sichtbar für“ mit Vorher/Nachher. Sicherung/Export enthält beides.
- Geändert: In der Übersicht heißt der Knopf jetzt „Löschen“ statt ✕.
- Behoben: Speicherorte vom Typ local/alias ließen sich nicht bearbeiten („Unbekannter Typ“).

## 1.21.0 – 2026-11-22
- Neu: **Alles aus der GUI auch per REST-API und MCP** (sehen, bearbeiten, löschen): Zeitpläne und Ketten,
  Speicherorte (inkl. Assistent-Fragen, Test, neu anmelden), Benachrichtigungen und Vorlagen, allgemeine
  Einstellungen, Zugriff nach IP/Land, Benutzer, Anmeldeverlauf, Rollen, API-Keys, Sicherung/Export/Import/
  Wiederherstellen, Vorlagen und Benachrichtigung pro Aufgabe. Jede Aktion läuft durch dieselbe Funktion wie
  in der GUI: gleiche Prüfungen, Rechte, Schutzregeln und Audit-Einträge (`API:<Name>`). Geheimnisse nur
  schreibbar. Sicherung/Import/Wiederherstellen nur für Admin-Rollen. Swagger und MCP-Tools übersetzt.
- Neu: **Länder-Datenbank** wahlweise täglich, wöchentlich, alle 2 Wochen, monatlich (Standard), alle 2 oder
  3 Monate erneuern (Einstellungen → Allgemein, API `geoip_days`).
- Neu: **Bandbreite in MB/s oder Mbit/s** (Einstellungen → Allgemein → Bandbreite). Gilt für alle Anzeigen
  und Eingaben, Werte werden beim Wechsel umgerechnet, gespeichert wird weiter in MB/s. API: `unit` und
  `input_unit`.
- Neu: **Aufgaben direkt in der Übersicht löschen** (✕, mit Rückfrage; nur mit Recht „Aufgaben: löschen“).
- Verbessert: Pause-Menü in Übersicht und Zeitplänen schließt bei einem Klick daneben oder mit Esc.
- Behoben: Beschreibung der Bandbreite war in anderen Sprachen teilweise deutsch.

## 1.20.0 – 2026-11-22
- Neu: **Automatische Sicherung** (Einstellungen → Sicherung) nach Cron-Zeitplan. Neue Datei nur, wenn sich
  der Stand seit der letzten Sicherung geändert hat (Prüfsumme; Verlauf, Anmeldungen und Zähler zählen nicht).
  Eigener Zielordner, Aufbewahrung nach Anzahl und Tagen, optional verschlüsselt, optional mit Lauf-Logs,
  „Jetzt sichern“ (auch erzwungen), Liste aller Sicherungen mit Herunterladen, Wiederherstellen und Löschen.
- Neu: Benachrichtigung für die Sicherung (nie / bei Fehler / immer, optional auch „nichts geändert“) mit
  wählbaren Kanälen und drei neuen Vorlagen-Ereignissen.
- Neu: **Mehrsprachig**: Englisch (Standard), Deutsch, Spanisch, Italienisch, Französisch. Sprache bei der
  Einrichtung und auf der Anmeldeseite wählbar, Systemsprache unter Einstellungen → Allgemein, eigene Sprache
  pro Benutzer unter Mein Konto. Übersetzt sind GUI, Meldungen, Standard-Vorlagen, Swagger/OpenAPI und
  MCP-Tool-Beschreibungen (API: `?lang=` oder `Accept-Language`). Weitere Sprachen per JSON-Datei in
  `app/i18n/`.
- Bestehende Installationen behalten Deutsch als Systemsprache.

## 1.19.1 – 2026-11-22
- Behoben: Build bricht bei langsamer oder kurz gestörter Verbindung zu PyPI ab („Read timed out“, danach
  „No matching distribution found“). `pip` wartet jetzt 60 s statt 15 s, wiederholt 10-mal und der ganze
  Schritt wird bis zu 3-mal neu versucht, mit klarer Meldung, falls PyPI gar nicht erreichbar ist.
- waitress 3.0.0 → 3.0.2 (Sicherheitskorrekturen).

## 1.19.0 – 2026-11-22
- Neu: **API-Keys** (Einstellungen → API, neues Recht `system.api`): Name, Rolle (Rechte und Beschränkungen wie
  bei Benutzern), optional Ablaufdatum und erlaubte IPs. Key nur einmal sichtbar, gespeichert als SHA-256-Hash,
  „zuletzt benutzt“ mit IP, Widerruf, Audit-Log als `API:<Name>`.
- Neu: **REST-API** unter `/api/v1` (Aufgaben anlegen/ändern/löschen/starten/stoppen/pausieren, Verlauf, Logs,
  Speicherorte ohne Geheimnisse, Durchsuchen, Zeitpläne, Audit-Log, Benutzer). Dieselben Rechte, IP-Sperren und
  Fehlversuch-Bremse wie in der GUI, 300 Anfragen pro Minute und Key. OpenAPI unter `/api/v1/openapi.json`,
  **Swagger-UI** unter `/api/docs` (im Image enthalten, neue Abhängigkeit `swagger-ui-bundle`).
- Neu: **MCP-Server** unter `/mcp` (Streamable HTTP, JSON-RPC) mit 17 Tools, sichtbar nur mit passendem Recht.
- Aufgaben-Prüfung aus dem Formular in eine gemeinsame Funktion verschoben (GUI und API prüfen gleich).
- Export/Import enthält die API-Keys.

## 1.18.0 – 2026-11-22
- Geändert: Datenspeicher ist jetzt **SQLite** (`config/mirrorsync.db`) statt einzelner JSON-Dateien: Aufgaben
  mit Verlauf, Einstellungen und Vorlagen, Benutzer mit 2FA und Passkeys, Rollen, IP-Regeln, Anmeldeverlauf,
  Audit-Log. Alle Änderungen laufen in Transaktionen. `rclone.conf` bleibt eine eigene Datei.
- **Automatische Übernahme** beim ersten Start: alle JSON-Dateien in einer Transaktion (ganz oder gar nicht,
  idempotent), danach als Sicherung nach `config/json-backup/`. Kaputte Datei → Container startet nicht und
  nennt sie, statt leer zu starten.
- Neu: Einstellungen → **Sicherung** (nur Admins): **Exportieren** des gesamten Stands als ZIP (Datenbank-Inhalt,
  rclone.conf, SSH-Schlüssel, optional Lauf-Logs), optional mit Passwort verschlüsselt (AES-256-GCM/scrypt),
  deutliche Warnung wegen enthaltener Geheimnisse. **Importieren** mit Prüfung (Version, Kompatibilität,
  Inhalt im Vergleich), Ersetzen erst nach Bestätigung, vorher automatische Sicherung in `config/backups/`.
  Export, Import und Downloads im Audit-Log.

## 1.17.0 – 2026-11-22
- Geändert: Benutzer und Passwort stehen nicht mehr in der Compose-Datei. Beim ersten Start legt ein
  **Einrichtungsassistent** im Browser den ersten Admin an. Schutz durch einen **Einrichtungs-Code** im
  Container-Log (`docker logs mirrorsync`, auch in `config/setup_token`), Fehlversuche gebremst und geloggt.
  Schritt 2 (optional): 2FA und Passkey einrichten.
- Neu: **Passkeys** (WebAuthn) als Anmeldung pro Benutzer, ohne Benutzername und Passwort, mehrere pro Benutzer,
  umbenennen/entfernen in „Mein Konto“, Admin kann sie unter „Bearbeiten“ entfernen. Braucht HTTPS und einen
  Domainnamen; über IP oder http:// erklärt MirrorSync, warum es keine Passkeys gibt. Optionale Einstellung
  „Öffentliche Adresse“ (bzw. `PUBLIC_URL`). Neue Abhängigkeit `webauthn==3.0.1`.
- Bestehende Installationen laufen unverändert weiter. `WEB_USER`/`WEB_PASS` bleiben optional (abwärtskompatibel),
  im Compose-Beispiel nur noch auskommentiert für den Notfall `ADMIN_RESET`.

## 1.16.0 – 2026-11-22
- Neu: **Nur ausgewählte Dateien und Ordner synchronisieren.** Im Quell-Browser setzt du Häkchen an Ordner und
  Dateien (auch in Unterordnern), „Übernehmen“ trägt den Basisordner als Quelle und die Auswahl ins neue Feld
  „Nur diese Dateien und Ordner“ ein. Leer = wie bisher der ganze Ordner.
- Mit Auswahl prüft, kopiert und löscht rclone nur innerhalb der Auswahl (Filterregeln, Ausschlüsse gelten weiter).
  Alles andere im Ziel bleibt unberührt; „Ausgeschlossenes auch im Ziel löschen“ wirkt dann nicht.
- Eine einzelne Datei als Quelle wird beim Speichern automatisch zu Elternordner + Auswahl.
- Live-Sync, Testlauf, Versionierung und „Quellordner mitkopieren“ funktionieren mit der Auswahl. Eine geänderte
  Auswahl löst beim Live-Sync wieder einen vollen Abgleich aus. Übersicht zeigt „☑ nur N Einträge“, Audit-Log „Auswahl“.

## 1.15.0 – 2026-11-22
- Geändert: Der Datei-Browser sitzt jetzt im **Aufgabenformular**. „Durchsuchen“ bei Quelle und Ziel öffnet rechts
  ein Panel: Speicherort wählen, Ordner mit Größe/Datum, Pfadleiste, Sortierung, Suche, „Übernehmen“.
- Ausschlüsse werden im selben Browser gewählt, jetzt auch einzelne Dateien (⛔ zum An- und Abwählen).
- Seite Speicherorte wieder als schlanke Liste ohne Browser.
- Alle Seiten nutzen die volle Fensterbreite.
- Neuer Endpunkt `/browse/list` (ersetzt `/remotes/<name>/files`).

## 1.14.0 – 2026-11-22
- Neu: **Datei-Browser** auf der Seite Speicherorte (rechts bzw. auf dem Handy darunter): Ordner und Dateien mit
  Größe und Datum, Pfadleiste, Sortierung, Suche, SFTP/FTP ab `/`, „Als Quelle/Ziel für neue Aufgabe“,
  „Pfad kopieren“. Nur lesen, Recht `remotes.browse` und Beschränkung pro Speicherort gelten.
- Neu: Aufgaben **pausieren** (unbefristet, 1 h, 24 h, 1 Woche oder bis Datum) direkt in der Übersicht oder in
  der Aufgabe; keine Starts per Zeitplan, Live oder Kette, automatisches Ende der Pause, manueller Start bleibt möglich.
  Verhalten in Ketten wählbar: überspringen (Folgeaufgaben laufen weiter) oder Kette anhalten. Markierung in
  Übersicht und Zeitplänen, Einträge im Audit-Log.
- `/job/new?source=…&dest=…` füllt Quelle und Ziel vor.

## 1.13.0 – 2026-11-22
- Neu: **eigene Benachrichtigungstexte** (Vorlagen) für Betreff und Text je Ereignis (Lauf erfolgreich,
  Lauf fehlgeschlagen/gestoppt, fehlgeschlagene Anmeldungen, Konto gesperrt, IP gesperrt, Test), für alle Kanäle.
  Variablen zum Anklicken, Live-Vorschau mit Beispieldaten, „Auf Standard zurücksetzen“; ohne Änderung gilt
  weiter der eingebaute Text.
- Neu: eigene Texte pro Aufgabe für erfolgreiche und fehlgeschlagene Läufe.
- Neu: Webhook-JSON-Body als Vorlage mit Beispielen (Discord, Slack, Gotify, Home Assistant/n8n) und
  JSON-Prüfung; neue Webhook-Felder `event` und `title` im Standard-JSON.
- Neue Variablen u. a. `{start}`, `{ende}`, `{dauer}` (lesbar), `{gestartet_von}`, `{art}` (Live/Spiegel).

## 1.12.0 – 2026-11-22
- Neu: Benachrichtigungskanal **Apprise**, global und pro Aufgabe, mit Test-Knopf.
  - Direkt: Apprise-URLs (eine pro Zeile) über die Apprise-Bibliothek im Container (`apprise==2.3.0`).
  - Über einen Apprise-API-Server: mit Konfigurations-Key und optionalem Tag (`/notify/<key>`) oder
    zustandslos mit den eingetragenen URLs (`/notify`).
  - Gilt auch für Meldungen zu fehlgeschlagenen Anmeldungen und IP-Sperren.
  - URLs und Key werden maskiert angezeigt und nicht ins Audit-Log geschrieben.

## 1.11.0 – 2026-11-22
- Neu: Startart **„Fortlaufend (Live)“** in der Aufgabe und als eigener Bereich auf der Seite Zeitpläne.
  - Alle N Minuten (Standard 1) ein schneller Lauf mit `rclone copy --max-age`, der nur seit dem letzten
    erfolgreichen Lauf geänderte Dateien kopiert und nichts löscht.
  - Zusätzlicher voller Spiegel-Lauf zu einer wählbaren Zeit (Standard täglich 03:00), damit Löschungen ankommen.
  - Erster Lauf und Lauf nach Änderung von Quelle, Ziel oder Ausschlüssen ist ein voller Abgleich.
  - Keine Überlappung; Läufe ohne Änderung erscheinen nicht im Verlauf und erzeugen kein Log; Fehlerserien werden
    nur einmal gemeldet und protokolliert. Bandbreitenregeln gelten.
  - Übersicht zeigt „Live, alle N Minuten“, den nächsten vollen Abgleich und „zuletzt geprüft“.
- Neu: **Audit-Log** als eigener Menüpunkt (`config/audit.jsonl`): Änderungen an Aufgaben, Zeitplänen,
  Speicherorten, Benutzern, Rollen, Einstellungen und Zugriffsregeln mit Vorher/Nachher, Starts/Stopps,
  An- und Abmeldungen, automatische Sperren; Benutzer, IP und Land je Eintrag; Geheimnisse werden nie gespeichert.
  Filter, Suche, CSV-Export, Aufbewahrung (Standard 365 Tage), neues Recht `system.audit`.

## 1.10.0 – 2026-11-22
- Neu: Einstellungen → Zugriff mit Schutz nach IP-Adresse und Land (`config/ipguard.json`):
  - Sperrliste für einzelne IPs und Netze (IPv4/IPv6, CIDR), dauerhaft oder befristet, mit Notiz und Zähler.
  - Erlaubt-Liste, z. B. nur das lokale Netz (Knopf trägt die privaten Bereiche ein).
  - Länderregel „nur diese Länder erlauben“ oder „diese Länder sperren“ über die lokale Länder-Datenbank;
    das lokale Netz ist immer ausgenommen.
  - Automatische Sperre nach X Fehlversuchen derselben IP innerhalb von Y Minuten, befristet oder dauerhaft,
    lokales Netz optional ausgenommen, mit Benachrichtigung.
  - Knopf „IP sperren“ im Anmeldeverlauf.
- Gesperrte Adressen bekommen eine Hinweisseite (403); Anmeldeversuche von dort erscheinen im Anmeldeverlauf.
- Schutz vor dem Aussperren: Regeln, die die eigene Adresse treffen würden, werden abgelehnt; 127.0.0.1 (Healthcheck)
  ist nie gesperrt. Notfall-Reset per `IPGUARD_RESET=true`, Abschalten per `IPGUARD=off`.
- Hinweis in der GUI, wenn ein Reverse-Proxy erkannt wird, aber „Reverse-Proxy“ nicht eingeschaltet ist.
- Neues Recht „System: Zugriff nach IP-Adresse und Land verwalten“ (Admin hat es automatisch).

## 1.9.0 – 2026-11-22
- Geändert: Benutzernamen unterscheiden bei der Anmeldung nicht mehr zwischen Groß- und Kleinschreibung.
  Neue Namen, die sich nur in der Schreibweise von einem bestehenden unterscheiden, werden abgelehnt.
  Bestehende Konflikte (z. B. `Max` und `max`) werden in der Benutzerliste und im Container-Log gemeldet;
  für sie gilt bis zur Bereinigung die exakte Schreibweise.
- Neu: Benachrichtigung über fehlgeschlagene Anmeldungen über Webhook, E-Mail und Telegram: bei jedem Fehlversuch
  (gedrosselt, Fehlversuche werden gesammelt und gebündelt nachgeschickt), nur bei Sperre oder nie.
- Neu: Fehlversuche im Anmeldeverlauf bestätigen und löschen, einzeln, ausgewählt oder alle. Filter „Unbestätigt“,
  unbestätigte Einträge sind rot markiert, eine rote Zahl bei „Einstellungen“ und „Benutzer“ zeigt sie an.
  Einträge aus älteren Versionen gelten als bestätigt.

## 1.8.0 – 2026-11-22
- Neu: Menüpunkt „Zeitpläne“ in der Seitenleiste mit den Bereichen „Nach Uhrzeit“, „Nach einer anderen Aufgabe“
  und „Nur manuell“.
- Nach Uhrzeit: Uhrzeit, Wochentage und aktiv direkt in der Liste ändern (Cron-Ausdrücke als Textfeld).
- Nach Aufgabe: Ketten untereinander, beginnend mit ihrer Startaufgabe. Reihenfolge per Drag & Drop oder mit ↑ ↓,
  Aufgaben lassen sich zwischen Ketten und aus „Nur manuell“ ziehen; „Neue Kette beginnen mit …“.
  Bedingung (nur bei Erfolg / immer) und aktiv je Aufgabe. Alles wird sofort gespeichert.
- Startart je Eintrag umstellen (Uhrzeit / nach Aufgabe / manuell): Die Aufgabe wird angepasst und rutscht sofort
  in den richtigen Bereich. Beim Einreihen nach einer Aufgabe laufen deren bisherige Nachfolger danach weiter.
- Die Seite nutzt dieselben Daten wie das Aufgabenformular, Änderungen gelten in beide Richtungen.

## 1.7.0 – 2026-11-22
- Neu: Abschnitt „Start“ mit drei Arten: zu einer Uhrzeit, nach einer anderen Aufgabe, nur manuell.
- Neu: „Nach einer anderen Aufgabe“ mit Auswahlliste und Bedingung (nur bei Erfolg / immer). Ketten über
  mehrere Aufgaben sind möglich, Schleifen werden erkannt und abgelehnt. Nach Testlauf oder Stopp startet nichts.
  Das Log der vorherigen Aufgabe vermerkt, welche Folgeaufgaben gestartet wurden.
- Neu: Uhrzeit einfach einstellbar (Uhrzeit + Wochentage), Cron-Ausdruck weiterhin unter „Erweitert“.
- Übersicht: Ketten werden eingerückt unter ihrer Startaufgabe angezeigt („nach …“, „danach: …“),
  einfache Zeitpläne in Klartext (z. B. „Mo–Fr 03:00“).
- Beim Löschen einer Aufgabe werden ihre Folgeaufgaben auf „Nur manuell“ gestellt.
- Bestehende Aufgaben behalten ihren Zeitplan.
- Neu: Letzte Anmeldung pro Benutzer mit Zeit, IP-Adresse und Land (mit Flagge). Private Adressen erscheinen als
  „Lokales Netz“.
- Neu: Anmeldeverlauf (Einstellungen → Benutzer → Anmeldeverlauf) mit erfolgreichen und fehlgeschlagenen
  Versuchen, Grund, IP, Land und Browser, filterbar nach Ergebnis und Benutzer. „Mein Konto“ zeigt die eigenen
  letzten Anmeldungen.
- Neu: Länder kommen aus einer lokalen Datenbank (DB-IP Lite, CC BY 4.0), die der Container selbst lädt und
  monatlich erneuert. Es werden keine IP-Adressen an fremde Dienste geschickt. Eigene `GeoLite2-Country.mmdb`
  in `config/geoip/` wird bevorzugt. Abschaltbar, dann nur IP-Adressen.
- Neu: Einstellung „Reverse-Proxy“: Nur wenn sie an ist, wird `X-Forwarded-For` ausgewertet.
  Sicherheitskorrektur: Bisher wurde der Header immer übernommen, damit ließ sich die Sperre nach Fehlversuchen umgehen.
- Neu: Konten deaktivieren und wieder aktivieren, dazu ein planbarer Sperrzeitraum („gesperrt ab“, „wieder aktiv ab“,
  beide optional). Offene Sitzungen enden sofort, danach wird das Konto automatisch wieder aktiv.
- Neu: Sperre nach Fehlversuchen einstellbar (Anzahl, Dauer in Minuten oder dauerhaft bis ein Admin freigibt),
  optional mit Benachrichtigung. „Entsperren“-Knopf in der Benutzerliste.
- Schutz: Es bleibt immer ein aktiver Admin ohne geplante Sperre. Der letzte Admin wird nach Fehlversuchen
  höchstens 15 Minuten gesperrt, nie dauerhaft. Das eigene Konto lässt sich nicht deaktivieren.

## 1.6.0 – 2026-11-22
- Neu: Bandbreitenbegrenzung mit Zeitplan. Zeitfenster mit Wochentagen, Uhrzeit von–bis und getrennten Werten
  für Upload und Download in MB/s, plus eine Grenze für die Zeit außerhalb der Fenster. Fenster über Mitternacht
  sind möglich. Vorlagen „werktags 8–18 Uhr 10 MB/s“ und „tagsüber 5 MB/s“, Vorschau in Klartext.
- Standard unter Einstellungen → Allgemein, pro Aufgabe überschreibbar (Standard, eigene Grenzen, immer unbegrenzt).
- Umsetzung als rclone-Zeittabelle (`--bwlimit`), die auch während eines laufenden Spiegelns umschaltet.
  Ein `--bwlimit` in den zusätzlichen Optionen hat weiterhin Vorrang. Bestehende Aufgaben bleiben unbegrenzt,
  solange kein Standard eingestellt ist.

## 1.5.1 – 2026-11-22
- Geändert: „Durchsuchen“ beginnt bei SFTP/SSH- und FTP-Speicherorten im Wurzelverzeichnis `/` statt im
  Home-Ordner des Benutzers. Gewählte Pfade werden absolut übernommen (z. B. `Server:/opt/daten`).
  „⬆ ..“ führt bis `/` und von dort zur Auswahl der Speicherorte. Wer bewusst im Home-Ordner arbeiten will,
  trägt `Name:` bzw. `Name:ordner` von Hand ein, bestehende Aufgaben ändern sich nicht.
- Neu: MirrorSync-Logo als Favicon im Browser-Tab (`favicon.ico`, SVG und Symbol für den Startbildschirm).

## 1.5.0 – 2026-11-22
- Neu: Jeder Lauf hat ein eigenes Log (`logs/<aufgabe>/<lauf>.log`) statt einer Datei, die beim nächsten Lauf
  überschrieben wird.
- Neu: Der Verlauf zeigt pro Lauf kopiert, gelöscht und Fehler. Jede Zeile ist anklickbar und öffnet das ganze Log.
- Neu: Log-Ansicht mit Filtern (Alle, Fehler, Kopiert, Gelöscht, Hinweise) samt Anzahl, Suche und Download.
  Fehler sind rot, Kopiertes grün, Gelöschtes orange markiert. Laufende Läufe aktualisieren sich live.
- Neu: Einstellungen → Allgemein mit Log-Aufbewahrung (Anzahl Läufe pro Aufgabe, maximales Alter in Tagen) und
  Anzeige des belegten Platzes. Neues Recht „System: allgemeine Einstellungen ändern" (Admin hat es automatisch).
- Das bisherige Log wird beim ersten Start übernommen. Beim Löschen einer Aufgabe werden ihre Logs mitgelöscht.

## 1.4.0 – 2026-11-22
- Neu: Häkchen „Quellordner selbst mitkopieren“ in der Aufgabe. Ohne Häkchen wird wie bisher der Inhalt der
  Quelle gespiegelt, mit Häkchen landet er im Ziel in einem Ordner mit dem Namen der Quelle
  (`Ziel/OPNsense/…`). Gelöscht wird dann nur innerhalb dieses Ordners, andere Ordner im Ziel bleiben unberührt.
- Das Formular zeigt beim Eintippen, wo die Daten landen und in welchem Ordner gelöscht wird.
- Versionierung, Log, Übersicht und Benachrichtigungen verwenden das tatsächliche Ziel.
- Bestehende Aufgaben ändern sich nicht (Häkchen ist aus).

## 1.3.1 – 2026-11-22
- Fehler behoben: „Durchsuchen“ bei leerem Feld suchte in `/data` und zeigte „directory not found“, wenn kein
  lokaler Ordner eingebunden ist. Jetzt erscheint zuerst die Liste der Speicherorte (und `/data`, falls vorhanden).
- Bei SMB-Speicherorten zeigt die oberste Ebene die Freigaben, darunter die Ordner. „⬆ ..“ führt bis zurück
  zur Auswahl der Speicherorte.
- Verständliche Fehlermeldungen beim Durchsuchen (Ordner nicht gefunden, Anmeldung abgelehnt, keine Verbindung,
  Passwort/Schlüssel fehlt, Anmeldung abgelaufen); die rclone-Meldung steht klein darunter.
- Ordnerauswahl für Ausschlüsse funktioniert jetzt auch, wenn die Quelle direkt ein Speicherort ist (z. B. `nas:`).

## 1.3.0 – 2026-11-22
- Neu: Eigene Rollen unter Einstellungen → Rollen, zusammengesetzt aus 21 Einzelrechten für Aufgaben,
  Speicherorte, Benachrichtigungen, Benutzer und Rollen.
- Neu: Rollen lassen sich auf ausgewählte Aufgaben und ausgewählte Speicherorte beschränken. Selbst angelegte
  Aufgaben bleiben für ihren Ersteller sichtbar. Quelle und Ziel müssen in erlaubten Speicherorten liegen.
- Neu: Admin, Operator und Nur lesen sind Vorlagen („Als Vorlage“ kopiert eine Rolle). Admin ist fest.
- Neu: Schutz gegen Rechteausweitung: Rollen und Benutzer können nur mit höchstens den eigenen Rechten
  angelegt, geändert oder vergeben werden.
- Rechteänderungen an einer Rolle gelten sofort für alle ihre Benutzer.
- Update: Bestehende Benutzer behalten ihre Rolle (Admin, Operator, Nur lesen) mit denselben Rechten wie in 1.2.0.

## 1.2.0 – 2026-11-22
- Neu: Mehrere Benutzer unter Einstellungen → Benutzer, mit Rollen Admin, Operator und Nur lesen.
  Rechte werden auf jeder Seite und bei jeder Aktion geprüft; Knöpfe ohne Recht werden ausgeblendet.
- Neu: 2FA per Authenticator-App (TOTP) mit QR-Code und 10 Backup-Codes, unter Einstellungen → Mein Konto.
  Admins können die 2FA eines Benutzers zurücksetzen.
- Neu: Passwort selbst ändern; dabei werden andere Anmeldungen beendet. Passwörter werden gehasht gespeichert.
- Neu: Einstellungen mit Reitern Benutzer, Benachrichtigungen, Mein Konto. Benutzername und Rolle unten in der Seitenleiste.
- Neu: Im Verlauf einer Aufgabe steht, wer sie gestartet hat (Benutzer oder Zeitplan).
- Neu: Ersteinrichtung in der GUI, falls kein `WEB_PASS` gesetzt ist; Notfall-Reset per `ADMIN_RESET=true`.
- Update: Bestehende Installationen übernehmen `WEB_USER`/`WEB_PASS` automatisch als ersten Admin.

## 1.1.1 – 2026-11-22
- Compose-Beispiel nutzt Port 80 (`PORT=80`), GUI damit direkt unter `http://192.168.1.132`.
- Fehler behoben: Die Statusprüfung (Healthcheck) des Containers fragte fest Port 8080 ab und meldete
  bei geändertem `PORT` „unhealthy“. Sie nutzt jetzt den eingestellten Port.

## 1.1.0 – 2026-11-22
- Neu: Eigene Login-Seite mit „Angemeldet bleiben“ und Abmelden, statt Browser-Anmeldedialog.
  Schutz gegen Passwort-Raten (5 Fehlversuche = 5 Minuten Sperre).
- Neu: Modernes Design mit Seitenleiste, Übersichtskarten, hellem und dunklem Theme (umschaltbar),
  besser auf dem Handy.
- Neu: Benachrichtigungen direkt in der Aufgabe anlegen und bearbeiten: Standard verwenden, eigene
  oder keine; eigene Webhook-URL, E-Mail-Empfänger, Telegram-Chat-ID und -Bot pro Aufgabe; Testknopf.
- Übersicht zeigt pro Aufgabe, wann und wohin benachrichtigt wird.
- Compose-Beispiel mit macvlan, Umgebungsvariablen als Liste und deutlichem Hinweis auf `build: .`.
- Aufgaben aus 1.0.0 werden automatisch übernommen.

## 1.0.0 – 2026-11-22
Erste Version.
- Einweg-Spiegelung 1:1 (wie FreeFileSync „Spiegeln“) mit rclone als Sync-Motor
- Web-GUI mit Passwortschutz: Aufgaben anlegen, starten, stoppen, Testlauf, Live-Log, Verlauf
- Aufgabenplanung pro Aufgabe per Cron-Zeitplan mit Vorlagen
- Speicherorte für alle rclone-Typen (SMB, WebDAV, SFTP, FTP, S3, B2, Azure, Google Drive,
  OneDrive, Dropbox, pCloud, MEGA, crypt …) in der GUI anlegen, bearbeiten, testen
- Browser-Anmeldung (OAuth) über `rclone authorize` mit Anleitung in der GUI
- Ausschlüsse (Ordner, Dateien, Muster) mit Ordnerauswahl, optional auch im Ziel löschen
- Versionierung gelöschter/überschriebener Dateien, Lösch-Schutz (max. Löschungen)
- Benachrichtigungen per Webhook, E-Mail (SMTP) und Telegram, global und pro Aufgabe
- Betrieb als Vermittler zwischen zwei entfernten Servern (A → B) ohne lokale Ordner
