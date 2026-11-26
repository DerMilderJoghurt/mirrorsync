"""Hilfe: Erklaerung aller Einstellungen in MirrorSync, durchsuchbar (Seite /help, API/MCP get_help).

Texte sind deutsch (Quellsprache) und werden ueber die i18n-Kataloge uebersetzt. Markierung im Text:
`code` und **fett**. Beispiel-Code (Feld "code") wird nicht uebersetzt; {base} wird durch die Adresse ersetzt.
"""
import html
import re

# (id, Symbol, Titel, Seite, [(Titel, Text[, Code]), ...])
SECTIONS = [
    ("start", "🚀", "Erste Schritte", "/", [
        ("So funktioniert MirrorSync",
         "MirrorSync spiegelt Ordner mit rclone von einer Quelle in ein Ziel, z. B. von Server A auf Server B. Zuerst "
         "legst du unter **Speicherorte** die Server oder Clouds an, dann unter **Aufgaben** eine Aufgabe mit Quelle, "
         "Ziel und Startzeit. Ein **Testlauf** zeigt, was passieren würde, ohne etwas zu ändern."),
        ("Seitenleiste",
         "Dashboard, Aufgaben, Zeitpläne, Speicherorte, Dateien, Statistik, Audit-Log und Einstellungen. Was du siehst, "
         "hängt von den Rechten deiner Rolle ab. Die Seitenleiste lässt sich mit dem Pfeil einklappen; das merkt sich "
         "MirrorSync pro Benutzer."),
        ("Rechte",
         "Jede Aktion hat ein eigenes Recht (z. B. `jobs.run` zum Starten). Fehlt ein Recht, ist das Feld ausgegraut "
         "oder der Knopf fehlt. Rechte vergibst du unter Einstellungen → Rollen."),
        ("Hilfe durchsuchen",
         "Gib oben einen Begriff ein, z. B. „Löschwarnung“, „Cron“ oder „Uptime Kuma“. Die Hilfe zeigt alle passenden "
         "Einträge. Über **❓ Hilfe** in den Einstellungen und in der Aufgabe kommst du jederzeit hierher."),
    ]),
    ("job", "📋", "Aufgabe: Art, Quelle und Ziel", "/job/new", [
        ("Name", "Frei wählbarer Name der Aufgabe. Er erscheint in der Übersicht, in Benachrichtigungen und im Health-Check."),
        ("Spiegeln (Einweg)",
         "Das Ziel wird an die Quelle angeglichen: Neues und Geändertes wird kopiert, was in der Quelle fehlt, wird im "
         "Ziel gelöscht (rclone sync). Die Quelle wird nie verändert."),
        ("Zwei-Wege-Sync",
         "Änderungen und Löschungen auf beiden Seiten werden übertragen (rclone bisync). Braucht das Recht `jobs.twoway`. "
         "Der erste Lauf führt beide Seiten zusammen, ohne zu löschen. Bricht er ab, hilft **Neu zusammenführen**."),
        ("Wenn eine Datei auf beiden Seiten geändert wurde",
         "Nur beim Zwei-Wege-Sync: die neuere Datei gewinnt, Seite A oder Seite B gewinnt, oder beide bleiben erhalten "
         "(die andere bekommt einen Zusatz im Namen)."),
        ("Löschschutz (Zwei-Wege)",
         "Würde ein Zwei-Wege-Lauf mehr als diesen Prozentsatz der Dateien löschen, bricht er ab. Schutz vor einer "
         "versehentlich geleerten Seite."),
        ("Quelle",
         "Ordner, der gespiegelt wird: ein Speicherort mit Pfad (`NAS:fotos`) oder ein Ordner im Container (`/data`). "
         "**Durchsuchen** öffnet den Datei-Browser. Ist die Quelle eine einzelne Datei, wird daraus automatisch der "
         "Elternordner mit dieser Datei als Auswahl."),
        ("Nur diese Dateien und Ordner",
         "Leer = der ganze Quellordner. Sonst werden nur die gewählten Einträge gespiegelt (eine Zeile pro Eintrag, "
         "relativ zur Quelle). Alles andere im Ziel bleibt unberührt."),
        ("Ziel",
         "Ordner, der an die Quelle angeglichen wird. Achtung: Was im Ziel liegt und nicht in der Quelle, wird beim "
         "Spiegeln gelöscht. Fehlt der Ordner, wird er angelegt."),
        ("Quellordner selbst mitkopieren",
         "Im Ziel entsteht ein Ordner mit dem Namen der Quelle (z. B. `/backup/fotos` statt der Inhalte direkt in "
         "`/backup`). Geht nicht, wenn die Quelle die oberste Ebene eines Speicherorts ist."),
        ("Vorschau der Ordnerstruktur",
         "Zeigt vor dem Speichern, wie das Ziel nach dem nächsten Lauf aussieht: neu, geändert, gelöscht, gleich. "
         "**Ergebnis im Browser öffnen** zeigt dasselbe als eigene Seite. Es wird nichts kopiert. Recht `jobs.preview`."),
        ("Sichtbar für",
         "Wer die Aufgabe sehen darf: alle oder nur bestimmte Benutzer, Gruppen und API-Keys. Admins sehen immer alles."),
    ]),
    ("trigger", "🕒", "Start, Zeitplan und Zeitfenster", "/schedules", [
        ("Zu einer Uhrzeit",
         "Startet nach Zeitplan: Uhrzeit mit Wochentagen, Intervall oder ein Cron-Ausdruck (`Minute Stunde Tag Monat "
         "Wochentag`, z. B. `0 3 * * *` = täglich 03:00). Vorlagen füllen den Ausdruck aus. Zeitzone siehe Anzeige."),
        ("Nach einer anderen Aufgabe",
         "Startet, sobald eine andere Aufgabe fertig ist, wahlweise **nur bei Erfolg** oder **immer**. So entstehen "
         "Ketten. Schleifen verhindert MirrorSync."),
        ("Fortlaufend (Live)",
         "Prüft alle paar Minuten, ob sich in der Quelle etwas geändert hat, und gleicht dann ab. **Wie Spiegeln** "
         "übernimmt auch Löschungen, **Schnell** kopiert nur Neues und Geändertes. Dazu optional regelmäßig ein voller "
         "Abgleich (Uhrzeit, Intervall oder Cron), damit auch Löschungen ankommen."),
        ("Nur manuell", "Die Aufgabe startet nur per Knopf, API oder MCP."),
        ("Automatischen Start aktivieren",
         "Ausgeschaltet startet die Aufgabe weder per Zeitplan noch per Kette oder Live, nur noch von Hand."),
        ("Aufgabe pausieren",
         "Pausiert bis zu einem Zeitpunkt oder unbefristet. In einer Kette wird eine pausierte Aufgabe entweder "
         "übersprungen (die Kette läuft weiter) oder die Kette stoppt hier. Schnell pausieren geht auch in der Übersicht."),
        ("Zeitfenster",
         "Die Aufgabe läuft nur zwischen zwei Uhrzeiten an den gewählten Tagen (auch über Mitternacht). Ein Start "
         "außerhalb wartet, bis das Fenster aufgeht. Endet das Fenster während eines Laufs: bis zum Ende durchlaufen "
         "lassen, anhalten und im nächsten Fenster weitermachen oder anhalten bis zum nächsten regulären Start."),
        ("Seite Zeitpläne",
         "Zeigt alle Aufgaben nach Art des Starts mit Wochenplan, nächsten Starts und Ketten. Von dort aus lassen sich "
         "Zeiten direkt ändern."),
    ]),
    ("options", "⚙️", "Aufgabe: Ausschlüsse und Optionen", "/job/new", [
        ("Ausschlüsse",
         "Ordner, Dateien oder Muster, die nicht gespiegelt werden, eine Zeile pro Eintrag: `/Temp/` (Ordner), "
         "`*.tmp` (Muster), `Thumbs.db`. Mit dem Knopf wählst du Ordner direkt aus der Quelle."),
        ("Im Ziel nichts löschen",
         "Kopiert nur Neues und Geändertes (rclone copy). Was in der Quelle gelöscht wird, bleibt im Ziel."),
        ("Ausgeschlossenes auch im Ziel löschen",
         "Ausgeschlossene Dateien, die schon im Ziel liegen, werden dort entfernt. Sonst bleiben sie unberührt."),
        ("Papierkorb/Versionierung",
         "Gelöschte und überschriebene Dateien werden nach `<ziel>.versions/<datum>` verschoben statt gelöscht. "
         "**Versionen behalten** begrenzt die Anzahl der Stände, **Höchstens so alt** das Alter in Tagen (leer = "
         "unbegrenzt). Ältere Stände werden nach jedem Lauf entfernt."),
        ("Änderung erkennen an",
         "**Standard**: Größe und Änderungszeit. **Nur Größe**: schnell, für Speicher ohne verlässliche Zeiten. "
         "**Prüfsumme**: am genauesten, liest aber alle Dateien. **Tolerant**: wie Standard, Zeitabweichungen bis zur "
         "Toleranz (Sekunden) zählen nicht (z. B. FAT, SMB)."),
        ("Tempo",
         "Wie viele Dateien gleichzeitig übertragen werden: schonend, normal, schnell oder maximal. Schonend belastet "
         "Netz und Server am wenigsten."),
        ("Immer nur Testlauf", "Jeder Lauf ist ein Testlauf: Das Log zeigt, was passieren würde, verändert wird nichts."),
        ("Max. Löschungen pro Lauf",
         "Würden mehr Dateien gelöscht, bricht der Lauf ab, bevor etwas gelöscht wird. Leer = keine Grenze."),
        ("Zusätzliche rclone-Optionen",
         "Weitere Schalter für rclone, z. B. `--transfers 8`. Nur mit dem Recht `jobs.advanced`."),
        ("Bandbreite der Aufgabe",
         "Standard (aus den Einstellungen), eigenes Limit oder unbegrenzt. Ein Limit kann nach Uhrzeit und Wochentag "
         "unterschiedlich sein, z. B. tagsüber 5 MB/s, nachts frei."),
        ("Benachrichtigungen der Aufgabe",
         "Standard übernimmt die Einstellungen. **Eigene** legt fest, wann (immer, nur bei Fehler, nie) und über welche "
         "Kanäle diese Aufgabe meldet, mit eigenen Empfängern, eigenem Telegram-Bot oder eigenen Apprise-URLs. Recht "
         "`jobs.notify`."),
        ("Eigene Texte für diese Aufgabe",
         "Überschreibt die Texte der Benachrichtigungen nur für diese Aufgabe, mit Platzhaltern wie `{job}` oder "
         "`{status}`."),
    ]),
    ("protect", "🛡", "Aufgabe: Prüfen und schützen", "/job/new", [
        ("Prüflauf nach dem Sync",
         "Vergleicht Quelle und Ziel Datei für Datei (aus, nach jedem Lauf, täglich, wöchentlich). Abweichungen machen "
         "den Lauf zum Fehler und stehen im Log. **Vergleich**: automatisch (Prüfsumme, wenn beide Seiten sie können), "
         "nur Größe oder Herunterladen (liest alles, sehr gründlich). Im Log startet **🔎 Jetzt prüfen** einen Prüflauf."),
        ("Löschwarnung",
         "Würde ein Lauf mehr als X % der Dateien im Ziel löschen (ab einer Mindestanzahl), hält er an und wartet auf "
         "**Freigabe** (Recht `jobs.approve`). Schutz vor Ransomware oder einer leeren Quelle. Leer = aus."),
        ("Speicher am Ziel prüfen",
         "Vor dem Lauf prüfen, ob genug Platz frei ist (laut Testlauf benötigte Menge plus Mindestwert in GB). "
         "**Warnen** meldet und läuft trotzdem, **Lauf nicht starten** bricht vorher ab."),
        ("Bei Fehler neu versuchen",
         "Minuten bis zum nächsten Versuch, z. B. `5, 15, 60` (höchstens 10). Nur bei Netzwerkfehlern oder bei jedem "
         "Fehler. Gemeldet wird erst, wenn auch der letzte Versuch scheitert."),
        ("Ordner mit .nosync überspringen",
         "Liegt in einem Ordner der Quelle eine Datei `.nosync`, wird er samt Unterordnern ausgelassen. Was davon schon "
         "im Ziel liegt, bleibt dort."),
        ("Überfällig nach (Stunden)",
         "Für den Health-Check: Ist der letzte Lauf älter, gilt die Aufgabe als überfällig. Leer = aus dem Zeitplan "
         "berechnet."),
    ]),
    ("encrypt", "🔒", "Aufgabe: Ziel verschlüsseln", "/job/new", [
        ("Ziel verschlüsseln",
         "MirrorSync legt einen verschlüsselten Speicherort (rclone crypt) über das Ziel. Darin liegen die Dateien im "
         "Ordner `data`, der Papierkorb in `data.versions`; im Ziel selbst sieht man nur verschlüsselte Namen und "
         "Inhalte. Recht `jobs.encrypt`. Nicht mit dem Zwei-Wege-Sync."),
        ("Passwort",
         "Mindestens 8 Zeichen, zweimal eingeben und bestätigen, dass es sicher aufbewahrt ist. **Ohne Passwort sind die "
         "Daten verloren.** Es lässt sich später nicht ändern und wird nie angezeigt. Ein eingegebenes Passwort prüft "
         "MirrorSync beim Speichern."),
        ("Dateinamen und Ordnernamen",
         "Dateinamen verschlüsseln (empfohlen), nur verschleiern oder lesbar lassen; Ordnernamen optional. Ein zweites "
         "Passwort (Salt) erhöht die Sicherheit. Alles nur beim ersten Einschalten wählbar."),
        ("Ausschalten",
         "Der nächste Lauf spiegelt wieder unverschlüsselt. Der verschlüsselte Speicherort `msenc_…` bleibt unter "
         "Speicherorte erhalten, die Daten bleiben damit lesbar."),
    ]),
    ("scripts", "🧰", "Aufgabe: Skripte, Snapshot und Wake-on-LAN", "/job/new", [
        ("Skripte vor und nach dem Lauf",
         "Shell-Befehle im Container oder per SSH auf einem SFTP-Speicherort, mit Zeitlimit. Variablen `MS_JOB_NAME`, "
         "`MS_SOURCE`, `MS_DEST`, `MS_RUN_ID`, danach `MS_STATUS`. Scheitert das Skript davor: Lauf abbrechen oder "
         "trotzdem spiegeln. Das Skript danach läuft immer, nur bei Erfolg oder nur bei Fehler. Recht `jobs.scripts`."),
        ("Snapshot am Ziel",
         "Nach jedem erfolgreichen Lauf ein Snapshot: ZFS (Dataset), Btrfs (Subvolume und Ordner für Snapshots) oder "
         "eigener Befehl mit `{name}`, `{date}`, `{job}`, `{dest}`. Optional mit `sudo -n` und „nur die letzten N "
         "behalten“."),
        ("Wake-on-LAN",
         "Weckt den Zielserver vor dem Lauf (MAC-Adresse, Broadcast, Port) und wartet, bis er erreichbar ist (Host:Port "
         "oder der Speicherort). Danach kann ihn ein Befehl per SSH wieder schlafen legen."),
    ]),
    ("runs", "▶️", "Läufe, Logs, Papierkorb und Statistik", "/", [
        ("Start, Test, Stopp",
         "**Start** spiegelt sofort, **Test** zeigt nur, was passieren würde, **Stopp** bricht ab. Laufende Aufgaben "
         "und Kopieraufträge zeigt der Knopf **Aufträge** oben rechts."),
        ("Log",
         "Jeder Lauf hat ein eigenes Log mit Filter (Fehler, kopiert, gelöscht, Hinweise), Suche und Download. Läuft "
         "die Aufgabe, aktualisiert es sich laufend."),
        ("Papierkorb durchsuchen",
         "Mit Versionierung: gelöschte und überschriebene Dateien nach Name suchen, herunterladen oder in Quelle oder "
         "Ziel zurückholen. Recht `jobs.restore`."),
        ("Platzbedarf",
         "Größte Ordner und Dateien in Quelle oder Ziel zum Durchklicken, dazu die am häufigsten übertragenen Ordner."),
        ("Statistik",
         "Übertragene Daten, Läufe, Fehler und Laufzeit pro Monat und Aufgabe, mit Datenvolumen-Limit (Einstellungen → "
         "Allgemein)."),
        ("Duplizieren und Entfernen",
         "⧉ legt eine ausgeschaltete Kopie der Aufgabe an. Entfernen löscht nur die Aufgabe, Dateien in Quelle und Ziel "
         "bleiben."),
    ]),
    ("remotes", "🗄", "Speicherorte und Dateien", "/remotes", [
        ("Speicherort anlegen",
         "Rund 55 Speicherarten: SMB, SFTP, WebDAV, FTP, S3, B2, Google Drive, OneDrive, Dropbox u. v. m. Der Assistent "
         "fragt die nötigen Angaben ab; bei Clouds mit Browser-Anmeldung (OAuth) führt er Schritt für Schritt durch. "
         "Der Name darf nur Buchstaben, Ziffern, - und _ enthalten."),
        ("Testen", "Prüft die Verbindung und listet die oberste Ebene."),
        ("Bearbeiten und neu anmelden",
         "Zugangsdaten ändern oder bei abgelaufener Cloud-Anmeldung neu anmelden. Passwörter werden nie angezeigt."),
        ("Duplizieren", "Kopie mit denselben Zugangsdaten unter neuem Namen, z. B. für ein anderes Protokoll."),
        ("Sichtbar für",
         "Wer den Speicherort sehen und in Aufgaben verwenden darf. Rollen können zusätzlich auf einzelne Speicherorte "
         "beschränkt sein."),
        ("Dateimanager (Dateien)",
         "Ein oder zwei Speicherorte nebeneinander: browsen, hoch- und herunterladen, umbenennen, löschen, kopieren und "
         "verschieben, Textdateien bearbeiten, Eigenschaften ansehen. Rechte `files.view`, `files.edit`, "
         "`files.delete`. Das Tempo stellst du unter Einstellungen → Allgemein ein."),
    ]),
    ("dashboard", "📊", "Dashboard", "/dashboard", [
        ("Kacheln",
         "Jeder Benutzer gestaltet sein Dashboard selbst: Kacheln hinzufügen, verschieben, in Breite (1–12 Spalten) "
         "und Höhe ändern. Es zeigt nur, wofür du Rechte hast."),
        ("Eigene Kacheln",
         "Datenquelle (z. B. Läufe, Datenmenge, Fehler), Darstellung (Zahl, Liste, Torte, Linie, Balken, Tacho, "
         "Kalender, Zeitleiste) und Zeitraum frei kombinieren."),
        ("Tabs", "Mehrere Dashboard-Seiten als Tabs, z. B. „Übersicht“ und „Server B“."),
    ]),
    ("notify", "🔔", "Einstellungen: Benachrichtigungen", "/settings", [
        ("Wann benachrichtigen",
         "Standard für alle Aufgaben: immer, nur bei Fehler oder nie. Jede Aufgabe kann eigene Regeln haben."),
        ("Ruhezeiten",
         "In diesem Zeitraum (z. B. 22:00–07:00, an den gewählten Tagen) meldet MirrorSync nur Fehler und Warnungen "
         "oder gar nichts. Erfolgsmeldungen entfallen."),
        ("Wochenbericht",
         "Regelmäßig ein Bericht über die letzten Tage: Läufe, Fehler, Datenmenge, Hinweise. Tage, Uhrzeit, Zeitraum "
         "und Kanäle wählbar, mit Knopf zum sofortigen Senden."),
        ("Texte der Benachrichtigungen",
         "Titel und Text pro Ereignis (Erfolg, Fehler, Löschwarnung …) mit Platzhaltern, mit Vorschau."),
        ("Webhook",
         "Sendet JSON an eine URL (ntfy, Discord, Slack, Home Assistant, n8n …), Methode wählbar."),
        ("E-Mail (SMTP)",
         "SMTP-Server, Port, Verschlüsselung (z. B. STARTTLS), Benutzer, Passwort, Absender und Empfänger (mehrere "
         "mit Komma)."),
        ("Telegram", "Bot-Token von @BotFather und Chat-ID. Der Token wird nie angezeigt."),
        ("Apprise",
         "Über 100 Dienste mit einer URL pro Zeile, direkt aus MirrorSync oder über einen Apprise-API-Server (Adresse, "
         "optional Konfigurations-Key und Tag)."),
        ("Test und Probe an alle", "Jeder Kanal hat einen Test-Knopf; **Probe an alle Kanäle** prüft alle auf einmal."),
    ]),
    ("general", "🧩", "Einstellungen: Allgemein", "/settings/general", [
        ("Sprache",
         "Standardsprache für neue Benutzer, die Anmeldeseite, Berichte und die API. Jeder Benutzer stellt seine eigene "
         "unter Mein Konto ein."),
        ("Dateimanager: Tempo", "Wie schnell Kopieren und Verschieben im Dateimanager laufen."),
        ("Updates",
         "Regelmäßig nach neuen Versionen suchen und optional benachrichtigen. Der Hinweis erscheint unten in der "
         "Seitenleiste."),
        ("Selbst aktualisieren",
         "Mit Docker-Socket: Knopf „Jetzt aktualisieren“ oder automatisch einmal am Tag ab einer Uhrzeit, optional das "
         "alte Image danach löschen. **Alte MirrorSync-Images** listet und löscht übrige Images."),
        ("Neustart", "Container sofort oder nach Zeitplan (Uhrzeit, Wochentage) neu starten, auf Wunsch auch während Aufgaben laufen."),
        ("Überwachung",
         "`/health/jobs` und `/metrics` ohne Anmeldung abrufbar machen. Sonst brauchen sie einen API-Key mit dem Recht "
         "`system.monitor`."),
        ("Datenvolumen pro Monat",
         "Limit in GB, Warnschwelle in %, Benachrichtigung und auf Wunsch automatische Läufe bis Monatsende anhalten."),
        ("Logs aufbewahren",
         "Läufe pro Aufgabe (Standard 50) und höchstens so lange (Standard 30 Tage, 0 = unbegrenzt). Dazu die "
         "Aufbewahrung des Audit-Logs in Tagen."),
        ("Alte Logs löschen", "Einmalig alle Läufe vor einem Datum löschen; vorher zeigt MirrorSync die Anzahl."),
        ("Anmeldung und Sicherheit",
         "Konto nach so vielen Fehlversuchen für X Minuten sperren, 2FA erzwingen (aus, für neue oder alle Benutzer) und "
         "über fehlgeschlagene Anmeldungen benachrichtigen."),
        ("IP-Adresse und Land",
         "Hinter einem Reverse-Proxy (z. B. Nginx Proxy Manager) den Haken setzen, damit die echte IP erkannt wird. Die "
         "Länder-Datenbank (DB-IP Lite) wird automatisch geladen und nach Intervall oder Zeitplan erneuert."),
        ("Passkeys", "Öffentliche Adresse von MirrorSync (z. B. `https://sync.example.de`), nötig für Passkeys."),
        ("Bandbreite (Standard)",
         "Limit für alle Aufgaben, die „Standard“ verwenden, wahlweise nach Uhrzeit und Wochentag gestaffelt."),
    ]),
    ("access", "🌐", "Einstellungen: Zugriff", "/settings/access", [
        ("Deine Verbindung", "Zeigt deine IP-Adresse und dein Land, damit du dich nicht aussperrst."),
        ("Erlaubt-Liste",
         "Nur diese IP-Adressen oder Netze (z. B. `192.168.1.0/24`) dürfen zugreifen. Leer = alle."),
        ("Länder", "Nur bestimmte Länder erlauben oder sperren (ISO-Codes mit Komma, z. B. `DE, AT, CH`)."),
        ("Automatisch sperren",
         "Eine IP nach so vielen Fehlversuchen innerhalb von X Minuten für eine Dauer sperren. Lokale Adressen auf Wunsch "
         "nie sperren, optional mit Benachrichtigung."),
        ("Sperrliste", "IPs, Netze oder Hostnamen von Hand sperren, mit Notiz und Dauer; Sperren wieder aufheben."),
    ]),
    ("users", "👥", "Benutzer, Rollen und Gruppen", "/users", [
        ("Benutzer anlegen",
         "Benutzername, Rolle und Passwort. Groß- und Kleinschreibung zählen nicht doppelt (`Max` und `max` sind "
         "derselbe Name)."),
        ("Aktiv, deaktiviert, Sperrzeitraum",
         "Ein Konto abschalten, einen Sperrzeitraum planen (gesperrt ab, wieder aktiv ab) oder eine Zeitsperre nach "
         "Fehlversuchen aufheben."),
        ("2FA und Passkeys zurücksetzen", "Bei verlorenem Handy oder Gerät; der Benutzer richtet sie danach neu ein."),
        ("Rollen",
         "Eine Rolle ist eine Sammlung von Rechten, optional beschränkt auf ausgewählte Aufgaben und Speicherorte. "
         "Vorlagen wie Admin, Operator oder Nur lesen helfen beim Start. Vergeben kann man nur Rechte, die man selbst hat."),
        ("Gruppen",
         "Fassen Benutzer und API-Keys zusammen, geben zusätzliche Rechte und bestimmen, welche Aufgaben und "
         "Speicherorte die Mitglieder sehen."),
        ("Anmeldeverlauf", "Wer sich wann von wo angemeldet hat, mit Fehlversuchen und Entsperren."),
        ("Audit-Log", "Wer hat wann was geändert, mit Vorher/Nachher, Filter, Suche und CSV-Export. Recht `system.audit`."),
    ]),
    ("account", "👤", "Mein Konto", "/account", [
        ("Sprache", "Deine Sprache für die Oberfläche."),
        ("Passwort ändern", "Aktuelles Passwort und zweimal das neue."),
        ("Zwei-Faktor-Anmeldung (2FA)",
         "Mit einer Authenticator-App (QR-Code). Dazu gibt es Backup-Codes für den Notfall; neue Codes ersetzen die alten."),
        ("Passkeys", "Anmeldung mit Fingerabdruck, Gesicht oder Sicherheitsschlüssel statt Passwort. Pro Gerät ein Passkey."),
        ("Deine letzten Anmeldungen", "Zeigt Zeit, IP, Land und Gerät deiner Anmeldungen."),
    ]),
    ("backup", "💾", "Einstellungen: Sicherung", "/settings/backup", [
        ("Exportieren",
         "Alle Einstellungen, Aufgaben, Benutzer und Speicherorte als ZIP, mit Passwort verschlüsselt (empfohlen), "
         "optional mit Lauf-Logs."),
        ("Importieren",
         "Zeigt zuerst, was die Datei enthält. Danach Teile übernehmen oder den Stand komplett ersetzen. Verschlüsselte "
         "Dateien brauchen das Passwort."),
        ("Automatische Sicherung",
         "Nach Zeitplan (Cron) in einen Ordner im Container, nur wenn sich etwas geändert hat. Anzahl und Alter "
         "begrenzen, Passwort, Benachrichtigung."),
        ("Gespeicherte Sicherungen", "Herunterladen, wiederherstellen oder löschen. Nur für Admins."),
    ]),
    ("misc", "✨", "Oberfläche, App und Versionen", "/changelog", [
        ("Helles und dunkles Design", "Umschalten unten in der Seitenleiste; ohne Wahl folgt MirrorSync dem Gerät."),
        ("Als App installieren",
         "Im Browser „Zum Startbildschirm hinzufügen“ bzw. „Installieren“ wählen. MirrorSync öffnet sich dann wie eine "
         "App. Für Android gibt es zusätzlich eine eigene App (APK) mit Anmeldung per Server-Adresse."),
        ("Versionshinweise",
         "Ein Klick auf die Versionsnummer unten in der Seitenleiste zeigt, was sich in jeder Version geändert hat. Nach "
         "einem Update erscheint einmal „Neu in dieser Version“."),
        ("Datei-Browser im Formular",
         "**Durchsuchen** bei Quelle, Ziel und Ausschlüssen öffnet ein Seitenpanel mit Größe, Datum, Sortierung und "
         "Suche. Recht `remotes.browse`."),
    ]),
    ("api", "🔌", "API anbinden", "/settings/api", [
        ("1. API-Key anlegen",
         "Einstellungen → API → Neuen API-Key erstellen: Name (z. B. n8n), Rolle (genau deren Rechte), optional Ablauf, "
         "erlaubte IPs und Sprache der Antworten. Der Key `msk_…` wird angezeigt; später nur mit Passwort oder Passkey "
         "erneut. Für wenige Rechte vorher eine eigene Rolle anlegen."),
        ("2. Anfragen senden",
         "Basis-Adresse `/api/v1`, Anmeldung mit dem Header `Authorization: Bearer msk_…`. Antworten sind JSON, Fehler "
         "kommen als `{\"error\": …}` mit Status 400 bis 429. Höchstens 300 Anfragen pro Minute und Key.",
         "curl -H \"Authorization: Bearer msk_…\" {base}/api/v1/status\n"
         "curl -H \"Authorization: Bearer msk_…\" {base}/api/v1/jobs\n"
         "curl -X POST -H \"Authorization: Bearer msk_…\" \"{base}/api/v1/jobs/<id>/run?dry_run=true\""),
        ("Swagger-Dokumentation",
         "Unter `/api/docs` alle Endpunkte zum Ausprobieren (mit GUI-Anmeldung oder „Authorize“ mit Key), die "
         "Spezifikation unter `/api/v1/openapi.json`. Alles aus der GUI geht auch per API, mit denselben Prüfungen."),
        ("n8n (HTTP Request)",
         "Node **HTTP Request**, Authentication „Generic Credential Type“ → **Header Auth**: Name `Authorization`, Wert "
         "`Bearer msk_…`. URL z. B. `{base}/api/v1/jobs/<id>/run`, Methode POST."),
        ("Home Assistant (rest_command)",
         "Aufgabe aus Home Assistant starten, z. B. per Automation oder Knopf. In `configuration.yaml` eintragen, "
         "neu starten, dann als Aktion `rest_command.mirrorsync_run` verwenden.",
         "rest_command:\n  mirrorsync_run:\n    url: \"{base}/api/v1/jobs/<id>/run\"\n    method: post\n"
         "    headers:\n      Authorization: \"Bearer msk_…\""),
        ("Sprache und Sicherheit",
         "Sprache der Antworten mit `?lang=de|en|es|fr|it` oder am Key. Geheimnisse (Passwörter, Tokens) lassen sich nur "
         "schreiben, nie lesen. Alles steht im Audit-Log als `API:<Name>`."),
    ]),
    ("mcp", "🤖", "MCP einrichten (Claude, n8n und andere)", "/settings/api", [
        ("MCP-Server",
         "Adresse `{base}/mcp` (Streamable HTTP), Anmeldung mit demselben Header wie die API. Der Client sieht nur Tools, "
         "für die der Key das Recht hat; ein Key mit „Nur lesen“ bekommt keine schreibenden Tools."),
        ("Claude Desktop, Cursor, VS Code",
         "In der MCP-Konfiguration des Programms eintragen (der Schlüssel heißt je nach Programm `mcpServers` oder "
         "`servers`) und das Programm neu starten.",
         "{\n  \"mcpServers\": {\n    \"mirrorsync\": {\n      \"type\": \"http\",\n      \"url\": \"{base}/mcp\",\n"
         "      \"headers\": { \"Authorization\": \"Bearer msk_…\" }\n    }\n  }\n}"),
        ("Claude Code", "Einmal im Terminal ausführen:",
         "claude mcp add --transport http mirrorsync {base}/mcp --header \"Authorization: Bearer msk_…\""),
        ("Programme nur mit lokalen Servern",
         "Kann ein Programm nur lokale (stdio) MCP-Server, verbindet `mcp-remote` es mit MirrorSync:",
         "npx mcp-remote {base}/mcp --header \"Authorization: Bearer msk_…\""),
        ("n8n (KI-Agent)",
         "Im **AI Agent** als Tool den Node **MCP Client Tool** hinzufügen: Endpoint `{base}/mcp`, Server Transport "
         "**HTTP Streamable**, Authentication **Header Auth** mit Name `Authorization` und Wert `Bearer msk_…`. Unter "
         "Tools „All“ oder nur ausgewählte freigeben."),
        ("Tipp: eigener Key pro Assistent",
         "Lege für jeden Assistenten einen eigenen Key mit passender Rolle an (z. B. nur ansehen und starten). So lässt "
         "er sich einzeln sperren, und das Audit-Log zeigt, was er getan hat."),
    ]),
    ("monitor", "📈", "Überwachung mit Uptime Kuma und Home Assistant", "/settings/general", [
        ("Health-Check /health/jobs",
         "Antwortet mit HTTP 200, wenn alle Aufgaben in Ordnung sind, sonst 503 (Fehler, überfällig, Löschwarnung, "
         "Abweichung beim Prüflauf), z. B. `{\"status\": \"ok\", \"summary\": \"3 Aufgaben ok, letzter Sync vor 5 "
         "Minuten\"}`. Eine Aufgabe: `/health/jobs/<ID oder Name>`, als Text `?format=text`, immer HTTP 200 mit "
         "`?always200=1`. Prometheus-Werte unter `/metrics`."),
        ("Schritt 1: Zugang",
         "Rolle „Überwachung“ mit nur dem Recht `system.monitor` anlegen (Einstellungen → Rollen), dann einen API-Key "
         "mit dieser Rolle (Einstellungen → API). Alternativ unter Einstellungen → Allgemein → Überwachung ohne "
         "Anmeldung freigeben (zeigt dann Namen und Zustand aller Aufgaben)."),
        ("Uptime Kuma",
         "1. **Neuen Monitor hinzufügen**, Typ **HTTP(s)**. 2. URL `{base}/health/jobs` (oder `/health/jobs/<Name>` für "
         "eine Aufgabe). 3. Intervall z. B. 300 Sekunden. 4. Unter **Header** das JSON unten eintragen. 5. Speichern: "
         "bei 503 meldet Uptime Kuma „Down“. Ohne Header geht auch die URL mit `?key=msk_…`. Mit Typ **HTTP(s) - "
         "Keyword**, der URL `{base}/health/jobs?format=text` und dem Keyword `OK:` prüfst du zusätzlich den Inhalt.",
         "{\n  \"Authorization\": \"Bearer msk_…\"\n}"),
        ("Home Assistant",
         "RESTful-Sensor in `configuration.yaml`, danach Home Assistant neu starten. Der Binärsensor wird „Problem“, "
         "sobald etwas nicht stimmt, und eignet sich für Automationen und Benachrichtigungen. `always200=1` sorgt dafür, "
         "dass Home Assistant die Antwort auch bei Problemen liest.",
         "rest:\n  - resource: \"{base}/health/jobs?always200=1\"\n    headers:\n      Authorization: \"Bearer msk_…\"\n"
         "    scan_interval: 300\n    sensor:\n      - name: \"MirrorSync\"\n        value_template: \"{{ value_json.summary }}\"\n"
         "    binary_sensor:\n      - name: \"MirrorSync Problem\"\n        device_class: problem\n"
         "        value_template: \"{{ not value_json.ok }}\""),
        ("Grafana und Prometheus",
         "Prometheus holt `{base}/metrics` mit demselben Key (`authorization: credentials: msk_…`). Werte: Läufe, Bytes, "
         "Dauer, Status, Alter des letzten Laufs, Prüfläufe, Datenvolumen.",
         "scrape_configs:\n  - job_name: mirrorsync\n    scheme: https\n    metrics_path: /metrics\n"
         "    authorization:\n      credentials: msk_…\n    static_configs:\n      - targets: [\"{host}\"]"),
    ]),
]


def _strings():
    """Alle uebersetzbaren Texte (fuer die Kataloge)."""
    out = []
    for sid, icon, title, link, items in SECTIONS:
        out.append(title)
        for it in items:
            out.extend(it[:2])
    return out


def _fmt(text):
    s = html.escape(text, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def _plain(text):
    return text.replace("**", "").replace("`", "")


def sections(t, base="", can=lambda p: True, fmt=True):
    """Uebersetzte Hilfe. t = Uebersetzungsfunktion, base = Adresse von MirrorSync fuer Beispiele."""
    base = (base or "https://sync.example.de").rstrip("/")
    res = []
    for sid, icon, title, link, items in SECTIONS:
        entries = []
        for i, it in enumerate(items):
            tx = t(it[1]).replace("{base}", base)
            e = {"id": f"{sid}-{i + 1}", "title": t(it[0]), "text": _fmt(tx) if fmt else _plain(tx)}
            if len(it) > 2:
                e["code"] = it[2].replace("{base}", base).replace("{host}", base.split("://", 1)[-1])
            entries.append(e)
        res.append({"id": sid, "icon": icon, "title": t(title), "link": link, "entries": entries})
    return res


def search(t, q="", base="", section=None):
    """Fuer API/MCP: Eintraege, die alle Suchwoerter enthalten (ohne Suche: alle), als reiner Text."""
    words = [w for w in (q or "").lower().split() if w]
    out = []
    for s in sections(t, base, fmt=False):
        if section and s["id"] != section:
            continue
        for e in s["entries"]:
            hay = " ".join([s["title"], e["title"], e["text"], e.get("code", "")]).lower()
            if all(w in hay for w in words):
                out.append(dict(e, section=s["title"], section_id=s["id"], page=s["link"]))
    return out
