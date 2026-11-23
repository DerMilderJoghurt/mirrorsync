# Changelog

Versionsnummern nach [SemVer](https://semver.org/lang/de/): MAJOR.MINOR.PATCH
(MAJOR = inkompatible Änderung, MINOR = neue Funktion, PATCH = Fehlerbehebung).

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
- Compose-Beispiel nutzt Port 80 (`PORT=80`), GUI damit direkt unter `http://192.168.1.50`.
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
