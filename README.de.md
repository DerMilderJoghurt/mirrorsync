<p align="center">
  <img src="docs/logo.png" alt="MirrorSync" width="480">
</p>

# MirrorSync – 1:1-Spiegelung mit Web-GUI und Zeitplänen

Version **1.50.0** · Änderungen siehe [CHANGELOG.md](CHANGELOG.md) (englisch) · [English version](README.md)

Ein Docker-Container, der Ordner **einweg 1:1 spiegelt** (wie FreeFileSync „Spiegeln"):
Das Ziel wird exakt wie die Quelle, inklusive Löschungen. Als Sync-Motor dient
[rclone](https://rclone.org), damit gehen **SMB, WebDAV (Nextcloud …), SFTP/SSH, FTP/FTPS,
S3, lokale Ordner** und viele mehr, in jeder Kombination (z. B. SMB → WebDAV).

![Aufgaben-Übersicht](docs/screenshots/jobs.png)

<details><summary>Weitere Screenshots</summary>

| | |
|---|---|
| ![Dunkles Design](docs/screenshots/jobs-dark.png) | ![Aufgabe bearbeiten](docs/screenshots/edit-job.png) |
| Dunkles Design | Aufgabe bearbeiten |
| ![Zeitpläne](docs/screenshots/schedules.png) | ![Speicherorte](docs/screenshots/remotes.png) |
| Zeitpläne | Speicherorte |
| ![Dateimanager](docs/screenshots/files.png) | |
| Dateimanager | |

</details>

## Schnellstart
```bash
docker run -d --name mirrorsync --restart unless-stopped \
  -p 8080:8080 -e PORT=8080 -e TZ=Europe/Berlin \
  -v ./config:/config -v ./logs:/logs \
  ghcr.io/dermilderjoghurt/mirrorsync:latest
```
Dann `http://<docker-host>:8080` öffnen und den ersten Admin anlegen.

## Funktionen
- **Mehrere Benutzer** mit **eigenen Rollen** (Einzelrechte pro Aktion, beschränkbar auf einzelne Aufgaben und Speicherorte), **2FA** per Authenticator-App inkl. Backup-Codes und **Passkeys**
- **REST-API mit Swagger** und **MCP-Server** für n8n, Home Assistant, Skripte und KI-Assistenten, mit **API-Keys** und Rechten wie bei Benutzern
- **Fünf Sprachen**: Englisch (Standard), Deutsch, Spanisch, Italienisch, Französisch. Sprache bei der Einrichtung wählen, jeder Benutzer stellt seine eigene ein
- **Automatische Sicherung** nach Zeitplan, nur wenn sich etwas geändert hat, optional verschlüsselt und mit Benachrichtigung
- **Ersteinrichtung im Browser** mit Einmal-Code aus dem Container-Log, kein Passwort in der Compose-Datei
- Moderne Web-GUI (Seitenleiste, helles und dunkles Design) mit eigener Login-Seite: Aufgaben anlegen, bearbeiten, starten, stoppen
- **Aufgabenplanung** pro Aufgabe per Cron-Zeitplan, mit Vorlagen (stündlich, täglich 03:00 …), als Kette nach einer anderen Aufgabe oder **fortlaufend (Live)** alle paar Minuten
- **Zwei-Wege-Sync** (rclone bisync): Änderungen und Löschungen auf beiden Seiten werden übertragen, mit Konfliktregel und Löschschutz
- **Audit-Log**: wer hat wann was gemacht, mit Vorher/Nachher, Filter, Suche und CSV-Export
- **Speicherorte für alle rclone-Speicherarten** (rund 55) direkt in der GUI anlegen, bearbeiten und per Klick testen: SMB, WebDAV, SFTP, FTP, S3 (AWS, MinIO, Wasabi …), B2, Azure, Google Drive, OneDrive, Dropbox, pCloud, MEGA, crypt usw.
- Browser-Anmeldung (OAuth) für Google Drive, OneDrive, Dropbox, pCloud … mit Schritt-für-Schritt-Anleitung in der GUI
- **Dateimanager** (Seitenleiste „Dateien“): in einem oder zwei Speicherorten nebeneinander browsen, Ordnergrößen
  und Berechtigungen ansehen, Textdateien bearbeiten, hoch- und herunterladen, umbenennen, löschen, kopieren und
  verschieben, auch von einem Speicherort in den anderen
- **Datei-Browser** im Aufgabenformular für Quelle, Ziel und Ausschlüsse (Seitenpanel mit Größe, Datum, Sortierung, Suche)
- Aufgaben **pausieren**, unbefristet oder bis zu einem Zeitpunkt
- **Ausschlüsse**: Ordner, Dateien oder Muster (z. B. `/Temp/`, `*.tmp`) pro Aufgabe ausschließen, Ordner per Klick aus der Quelle wählbar
- **Testlauf** (zeigt nur, was passieren würde), Live-Log und ein eigenes Log für jeden Lauf (Filter, Suche, Download)
- **Versionierung**: gelöschte/überschriebene Dateien landen in `<ziel>.versions/<datum>`, optional nur die
  letzten N Versionen bzw. höchstens X Tage behalten (Ältere werden nach jedem Lauf entfernt)
- **Lösch-Schutz**: Lauf bricht ab, wenn mehr als N Dateien gelöscht würden
- **Benachrichtigungen** per Webhook (ntfy, Discord, Slack, Home Assistant, n8n …), E-Mail (SMTP), Telegram und **Apprise** (über 100 Dienste, direkt oder über einen Apprise-API-Server), mit Test-Knopf; wann (immer / nur bei Fehler / nie) als Standard für alle Aufgaben, oder direkt in der Aufgabe mit eigenen Kanälen, Empfängern, Chat-ID und Test-Knopf

## Betrieb als Vermittler (Server A → Server B)
Der Container muss nicht auf A oder B laufen. Er verbindet sich zu beiden und reicht die Daten durch:
Speicherort `server-a` (z. B. SFTP) und `server-b` (z. B. SMB) anlegen, dann eine Aufgabe
`server-a:/pfad` → `server-b:freigabe/pfad`. Lokale Ordner müssen dafür nicht eingebunden werden.
Beachte: Alle Daten fließen durch den Docker-Host, seine Verbindung zu A und B bestimmt das Tempo.
Geänderte Dateien werden komplett neu übertragen (kein Delta wie bei rsync).

## Installation
Das fertige Image liegt in der GitHub Container Registry: `ghcr.io/dermilderjoghurt/mirrorsync`
(für amd64 und arm64, z. B. Raspberry Pi). Tags: `latest` (neueste Version), `1.50.0` (feste Version),
`1.40` (neuester Patch dieser Version). Das Image wird nur veröffentlicht, wenn sich die Versionsnummer ändert.
Update-Prüfer wie Dockhand oder Watchtower melden deshalb nur dann ein Update, wenn es wirklich eine neue Version gibt.

### Mit Docker Compose (empfohlen)
1. Ordner anlegen und die [`docker-compose.yml`](docker-compose.yml) hineinlegen, z. B. nach `/opt/mirrorsync/`.
2. Bei Bedarf anpassen:
   - Port: `ports: - "8080:8080"` (linke Zahl = Port auf dem Docker-Host, frei wählbar).
   - Benutzer und Passwort gehören **nicht** in die Compose-Datei. Den ersten Admin legst du beim ersten Aufruf
     der Web-GUI an (siehe „Ersteinrichtung“).
   - optional lokale Ordner unter `volumes` (erscheinen in der GUI als `/data/...`)
3. Starten:
   ```bash
   cd /opt/mirrorsync
   docker compose up -d
   ```
4. Im Browser `http://<docker-host>:8080` öffnen.

**Portainer:** Die `docker-compose.yml` einfach in den Stack-Editor kopieren, es muss nichts gebaut werden.

### Mit docker run
```bash
docker run -d \
  --name mirrorsync \
  --restart unless-stopped \
  -p 8080:8080 \
  -e PORT=8080 \
  -e TZ=Europe/Berlin \
  -v /opt/mirrorsync/config:/config \
  -v /opt/mirrorsync/logs:/logs \
  ghcr.io/dermilderjoghurt/mirrorsync:latest
```
Lokale Ordner zusätzlich mit z. B. `-v /srv/daten:/data/daten:ro` einbinden.

### Selbst bauen
Repo klonen und in der `docker-compose.yml` die Zeile `image:` durch `build: .` ersetzen (oder
`docker build -t mirrorsync .`), dann `docker compose up -d --build`.

## Benutzer, Rechte und 2FA
Unter **Einstellungen → Benutzer** werden Benutzer angelegt, unter **Einstellungen → Rollen** die Rollen.
Mitgeliefert sind drei Vorlagen:

| Rolle | darf |
|---|---|
| Admin | alles (fest, nicht änderbar, damit sich niemand aussperrt) |
| Operator | Aufgaben anlegen, bearbeiten, löschen, starten; Speicherorte ansehen, testen, durchsuchen |
| Nur lesen | Aufgaben, Status und Logs ansehen |

**Eigene Rollen** („Neue Rolle“ oder „Als Vorlage“ bei einer bestehenden) setzen sich aus Einzelrechten zusammen:

- *Aufgaben:* ansehen, anlegen, bearbeiten, löschen, starten/stoppen, Testlauf, Logs, Benachrichtigungen der
  Aufgabe ändern, zusätzliche rclone-Optionen ändern, Zwei-Wege-Sync einrichten (schreibt auch in die Quelle;
  ohne dieses Recht kann man eine Zwei-Wege-Aufgabe bearbeiten, aber nicht ein- oder ausschalten)
- *Speicherorte:* ansehen, testen, Ordner durchsuchen, anlegen, bearbeiten/neu anmelden, entfernen,
  lokale Ordner (`/data`) verwenden
- *Dateimanager:* Dateien ansehen (durchsuchen, Größen, Berechtigungen, herunterladen), bearbeiten (hochladen,
  bearbeiten, umbenennen, Ordner anlegen, kopieren), löschen (auch nötig zum Verschieben)
- *Benachrichtigungen (Standard):* ansehen, ändern
- *Benutzer und Rollen:* Benutzer ansehen, Benutzer verwalten, Rollen verwalten, Gruppen verwalten
- *System:* allgemeine Einstellungen (Log-Aufbewahrung, Standard-Bandbreite) ändern

Zusätzlich lässt sich jede Rolle auf **ausgewählte Aufgaben** und **ausgewählte Speicherorte** beschränken.
Benutzer sehen dann nur diese; selbst angelegte Aufgaben sehen sie immer. Beim Anlegen und Bearbeiten von
Aufgaben sind als Quelle und Ziel nur erlaubte Speicherorte möglich. Niemand kann eine Rolle mit mehr
Rechten anlegen oder vergeben, als er selbst hat.

### Gruppen und „Sichtbar für“ (seit 1.22.0)
Unter **Einstellungen → Gruppen** (Recht „Gruppen verwalten“) fasst du Benutzer und API-Keys zu Gruppen
zusammen, z. B. „Buchhaltung“ oder „Home Assistant“.

- **Zusätzliche Rechte:** Eine Gruppe kann Rechte geben. Ein Mitglied hat die Rechte seiner Rolle plus die
  Rechte aller seiner Gruppen. Beispiel: Rolle „Nur lesen“ plus Gruppe mit „starten und stoppen“. Vergeben kann
  man nur Rechte, die man selbst hat.
- **Sichtbar für:** Bei jeder Aufgabe und jedem Speicherort stellst du ein, wer ihn sieht: „alle mit dem
  passenden Recht“ (Standard, wie bisher) oder nur ausgewählte Benutzer und Gruppen. Wer etwas nicht sieht,
  kann es auch nicht starten, ändern, als Auslöser einer Kette oder als Quelle/Ziel wählen.
- Admins sehen immer alles, wer eine Aufgabe angelegt hat, sieht sie auch. Man kann sich nicht selbst
  ausblenden. Eine Beschränkung der Rolle auf einzelne Aufgaben/Speicherorte gilt zusätzlich.
- Mitgliedschaften lassen sich auch beim Benutzer unter „Gruppen“ setzen. Die Gruppenseite zeigt, welche
  eingeschränkten Aufgaben und Speicherorte eine Gruppe sieht.
- Wird ein Benutzer oder eine Gruppe gelöscht, verschwindet er bzw. sie aus allen „Sichtbar für“-Listen.
- Änderungen stehen im Audit-Log, Gruppen und Sichtbarkeit sind in Sicherung und Export enthalten.

Unter **Einstellungen → Mein Konto** richtet jeder Benutzer selbst 2FA ein (QR-Code mit Google/Microsoft
Authenticator, Aegis, 2FAS, Bitwarden … scannen) und bekommt 10 Backup-Codes, die nur einmal angezeigt werden.
Passwörter werden gehasht in der Datenbank `config/mirrorsync.db` gespeichert.

**2FA erzwingen** (seit 1.41.0): Unter **Einstellungen → Allgemein → Anmeldung und Sicherheit** wählst du global
*Aus (nur pro Benutzer)*, *Für neue Benutzer* oder *Für alle Benutzer*. Pro Benutzer gibt es unter
**Benutzer → Bearbeiten** das Häkchen **„2FA erzwingen“** (bei „Für neue Benutzer“ ist es beim Anlegen schon
gesetzt). Wer 2FA einrichten muss, landet nach der Anmeldung direkt bei „Mein Konto“ mit dem QR-Code und kann
nichts anderes tun, bis die Authenticator-App eingerichtet ist. Ausschalten kann die 2FA dann nur ein Admin
(„2FA zurücksetzen“, danach muss der Benutzer sie beim nächsten Anmelden neu einrichten). Die Benutzerliste zeigt
„Pflicht, noch nicht eingerichtet“. API-Keys (REST, MCP) sind davon nicht betroffen. Rechte: global
`system.settings`, pro Benutzer `users.manage`; per API `require_2fa_mode` (`update_security_settings`) und
`require_2fa` (`create_user`, `update_user`).

- **Bestehende Installation:** Sind schon Benutzer angelegt, ändert sich nichts. `WEB_USER`/`WEB_PASS` kannst du
  aus der Compose-Datei löschen, sie werden nur noch für den Notfall (`ADMIN_RESET`) gebraucht.

### Ersteinrichtung
Solange noch kein Benutzer angelegt ist, führt der erste Aufruf im Browser direkt zur Ersteinrichtung:
1. Web-GUI öffnen, Benutzername und Passwort eingeben → der erste Admin ist angelegt.
2. Optional gleich 2FA (Authenticator-App) und/oder einen Passkey einrichten, oder „Fertig“.

> **Achtung:** Bis der Admin angelegt ist, kann jeder, der die Web-GUI erreicht, diesen Admin anlegen. Lege ihn
> deshalb gleich nach dem ersten Start an. Ist der Container schon vorher aus dem Internet erreichbar (z. B. über
> eine Portfreigabe), setze `SETUP_TOKEN=true`: Dann schreibt der Container beim ersten Start einen
> **Einrichtungs-Code** ins Log (`docker logs mirrorsync`, auch in `config/setup_token`), ohne den sich der Admin
> nicht anlegen lässt. Fehlversuche werden gebremst und geloggt, nach der Einrichtung wird der Code gelöscht.

Wer weiter `WEB_USER`/`WEB_PASS` setzt, bekommt wie früher den Admin automatisch angelegt.

### Passkeys
Statt Passwort (+ 2FA) kann sich jeder Benutzer mit einem **Passkey** anmelden: Fingerabdruck, Gesicht,
Geräte-PIN, Passwort-Manager oder Sicherheitsschlüssel (YubiKey). Einrichten unter **Einstellungen → Mein
Konto → Passkeys**, mehrere pro Benutzer möglich (umbenennen, entfernen). Auf der Anmeldeseite dann
„Mit Passkey anmelden“, ein Benutzername ist nicht nötig.

- Passkeys brauchen **HTTPS und einen Domainnamen**, z. B. `https://sync.example.de` über einen Reverse-Proxy. Über
  `http://192.168.1.50` bietet MirrorSync keine Passkeys an und erklärt, warum: Browser erlauben Passkeys nur
  auf sicheren HTTPS-Seiten, und ein Passkey ist immer an einen Domainnamen gebunden, nie an eine IP.
- MirrorSync nimmt die aufgerufene Adresse. Leitet der Proxy den Host nicht durch, unter **Einstellungen →
  Allgemein → Passkeys** die öffentliche Adresse eintragen (oder `PUBLIC_URL=` in der Compose-Datei).
  Eine spätere Änderung der Adresse macht bestehende Passkeys unbrauchbar.
- Gerät verloren: Ein Admin entfernt die Passkeys des Benutzers unter „Bearbeiten“. Anmelden mit Passwort
  geht immer weiter. Hinzufügen und Entfernen steht im Audit-Log.
- **Handy verloren:** Ein anderer Admin setzt die 2FA unter „Bearbeiten“ zurück, oder du meldest dich mit
  einem Backup-Code an.
- **Admin-Passwort vergessen:** In der Compose-Datei `ADMIN_RESET=true` setzen, Container neu starten
  (`docker compose up -d`). Passwort und 2FA von `WEB_USER` sind dann wieder `WEB_PASS`. Danach
  `ADMIN_RESET` wieder auskommentieren und neu starten.

## Erste Schritte
1. **Speicherorte** → z. B. SMB-Freigabe anlegen (Name `nas`, Server, Benutzer, Passwort) → **Testen**.
2. **Neue Aufgabe**: Quelle `/data/daten/fotos`, Ziel `nas:backup/fotos`, Zeitplan wählen.
3. Zuerst **Test** klicken und im Log prüfen, was kopiert/gelöscht würde.
4. Passt alles → **▶** oder auf den Zeitplan warten.

Pfadschreibweise: lokal `/data/…`, entfernt `name:pfad` (bei SMB: `name:freigabe/ordner`).

**Ordner oder nur Inhalt?** Standard ist wie bei rsync mit Schrägstrich am Ende: der *Inhalt* der Quelle
landet direkt im Ziel. Mit dem Häkchen „Quellordner selbst mitkopieren“ wird im Ziel ein Ordner mit dem
Namen der Quelle angelegt. Beispiel Quelle `NAS:backup/OPNsense`, Ziel `backup-server:sicherung`:

| Häkchen | Ergebnis im Ziel | gelöscht wird nur in |
|---|---|---|
| aus | `sicherung/config.xml …` | `sicherung` |
| an | `sicherung/OPNsense/config.xml …` | `sicherung/OPNsense` |

Mit Häkchen bleiben andere Ordner im Ziel (z. B. `sicherung/Anderes`) unberührt. Ausschlüsse gelten immer
relativ zur Quelle, die Versionierung landet in `sicherung/OPNsense.versions/…`. Das Formular zeigt das
Ergebnis vor dem Speichern an.

## Vorschau der Ordnerstruktur (seit 1.43.0)
In einer Aufgabe zeigt der Knopf **„🗂 Vorschau der Ordnerstruktur“** (unter dem Ziel), wie das Ziel nach dem
nächsten Lauf aussieht. Es werden nur Quelle und Ziel gelesen, nichts wird kopiert oder gelöscht. Die Vorschau
nimmt die Werte, die gerade im Formular stehen, du musst also nicht erst speichern.

- **„✅ Ergebnis“** (seit 1.45.0, Standard): das Ziel genau so, wie es nach dem Lauf aussieht, fast wie der
  Datei-Browser (Name, Größe, Geändert). Was gelöscht wird, ist hier nicht mehr zu sehen.
- **„📂 Änderungen“** (seit 1.44.0): dieselbe Ansicht zum Durchklicken, aber mit Spalte Änderung, auch mit dem, was
  gelöscht wird, und **„Nur Änderungen zeigen“**.
- **„📂 Ergebnis im Browser öffnen“** (seit 1.46.0, neben dem Vorschau-Knopf und im Vorschau-Fenster): öffnet in
  einem neuen Tab eine eigene Seite, die aussieht wie **Dateien** (Pfadzeile, „Nach oben“, Name, Größe mit Anzahl
  Dateien, Geändert, Rechte), aber das Ziel **nach dem Lauf** zeigt und nur zum Ansehen ist. Gelöschtes fehlt dort;
  mit „Änderungen markieren“ siehst du zusätzlich, was neu ist, aktualisiert oder gelöscht wird.
- **„Nach oben“ bis zum Stammverzeichnis** (seit 1.47.0, in allen Vorschau-Browsern): Oberhalb des Ziels siehst
  du die echten Ordner des Speicherorts, so wie sie jetzt sind (die Aufgabe ändert dort nichts). Der Weg zum Ziel ist
  mit „→ zum Ziel“ und „🎯 Ziel der Aufgabe“ markiert, Ordner, die es noch nicht gibt, mit „wird angelegt“. Ein Klick
  darauf führt zurück in die Vorschau. Dafür braucht es zusätzlich das Recht `remotes.browse` („Ordner
  durchsuchen“), ohne das Recht ist am Ziel Schluss. API/MCP: `path` mit `../` (z. B. `../..`) liefert die echten
  Einträge mit `status: outside`, der Weg zum Ziel hat `target: way` bzw. `dest`.
- In beiden Ansichten Ordner anklicken, über die Pfadleiste oder „⬆ ..“ zurück und im Ordner suchen. Mit
  **„🌳 Baum“** wechselst du zur aufklappbaren Baumansicht, die Wahl merkt sich der Browser.
- Jeder Eintrag ist markiert: **neu**, **wird aktualisiert**
  (Größe oder Änderungszeit anders), **wird gelöscht** (gibt es in der Quelle nicht mehr) oder unverändert. Ordner
  zeigen, wie viele Dateien darin neu sind, aktualisiert oder gelöscht werden.
- Es gelten dieselben Regeln wie beim echten Lauf: „Nur diese Dateien und Ordner“, Ausschlüsse, „Quellordner
  mitkopieren“ und „Ausgeschlossenes auch im Ziel löschen“.
- Bei **Zwei-Wege** zeigt die Vorschau, wie beide Seiten danach aussehen. Was nur auf Seite B liegt, ist mit
  „kommt nach A“ markiert. Löschungen seit dem letzten Lauf sind dabei nicht berücksichtigt.
- Gibt es das Ziel noch nicht, steht das oben, und alles ist „neu“. Bei sehr vielen Dateien (über 3000) werden
  nur die ersten einzeln gezeigt, die Zähler stimmen trotzdem.
- **Recht:** `jobs.preview` („Vorschau der Ordnerstruktur im Ziel ansehen und durchklicken“). Admins und die Standardrolle
  Operator haben es. Eigene Rollen, die schon in der Datenbank stehen, bekommen es nicht automatisch.
- **API/MCP:** `POST /api/v1/jobs/{job_id}/preview` (`preview_job`, gespeicherte Aufgabe, Felder optional
  überschreibbar) und `POST /api/v1/jobs/preview` (`preview_paths`, nur `source` und `dest`). Antwort mit
  `summary` (Zähler) und `text` (Baum mit `+` neu, `~` aktualisiert, `-` gelöscht, `<` nach Seite A), mit
  `tree: true` auch als JSON. Mit `path` (z. B. `Fotos/2024`) wird ein Ordner wie im Datei-Browser geöffnet
  (`entries` mit `name`, `dir`, `status`, `size`, `modified`, bei Ordnern `counts`), mit `only_changes: true` nur
  Einträge, die sich ändern, mit `result: true` das Ergebnis ohne Gelöschtes (für `text`, `entries` und `tree`).

## Nur einzelne Dateien und Ordner
Im Feld **Nur diese Dateien und Ordner** stehen Einträge relativ zur Quelle, einer pro Zeile, Ordner mit `/` am
Ende (z. B. `Projekte/` und `bericht.docx`). Am einfachsten setzt du im Quell-Browser Häkchen an Ordner und
Dateien, auch über mehrere Unterordner verteilt, und klickst „Übernehmen“. Liegt alles in der bisherigen Quelle,
bleibt sie Basisordner, sonst wird der gemeinsame Elternordner zur Quelle.

- Nur die Auswahl wird geprüft und gespiegelt. Im Ziel wird nur innerhalb der Auswahl gelöscht (z. B. eine
  ausgewählte Datei, die in der Quelle verschwindet), alles andere im Ziel bleibt unberührt.
- Ausschlüsse gelten zusätzlich (z. B. `*.tmp` in einem ausgewählten Ordner). „Ausgeschlossenes auch im Ziel
  löschen“ ist bei einer Auswahl wirkungslos, damit nichts außerhalb gelöscht wird.
- Trägst du als Quelle direkt eine Datei ein (`NAS:data/f3.txt`), wird beim Speichern daraus Quelle
  `NAS:data` mit Auswahl `f3.txt`.
- Live-Sync, Testlauf und Versionierung funktionieren wie gewohnt. **„Quellordner mitkopieren“ ist bei einer
  Auswahl aus** (seit 1.27.0): Die gewählten Ordner und Dateien landen direkt im Ziel, z. B. Quelle
  `NAS:share` mit Auswahl `10-Temp/` und Ziel `Familie-NAS:share` ergibt `Familie-NAS:share/10-Temp`.
- Leeres Feld = der ganze Quellordner wie bisher.

## Änderungen erkennen und Tempo (seit 1.50.0)
Unter **Optionen** jeder Aufgabe:

- **Änderung erkennen an:** woran MirrorSync merkt, dass eine Datei neu übertragen werden muss.
  - *Größe und Änderungszeit* (Standard): schnell und für die meisten Fälle richtig.
  - *Nur Größe:* am schnellsten, übersieht aber Änderungen bei gleicher Größe.
  - *Prüfsumme:* vergleicht den Inhalt, am sichersten, liest dafür jede Datei. Haben beide Seiten keine
    gemeinsame Prüfsumme, gilt Größe und Änderungszeit.
  - *Größe und Änderungszeit mit Toleranz:* Zeiten dürfen um die angegebenen Sekunden abweichen (2 für FAT/exFAT
    und manche SMB-Freigaben, 3600 gegen Kopien nach der Zeitumstellung).
  Die Vorschau der Ordnerstruktur rechnet mit derselben Einstellung. Die frühere Option „Vergleich per Prüfsumme“
  wird übernommen.
- **Tempo:** wie viele Dateien gleichzeitig übertragen und geprüft werden. *Schonend* 2, *Normal* 4
  (rclone-Standard), *Schnell* 8 mit schnellem Auflisten (`--fast-list`), *Sehr schnell* 16. Mehr parallel hilft
  vor allem bei vielen kleinen Dateien und bei Clouds. Eigene `--transfers`/`--checkers` unter „Zusätzliche
  rclone-Optionen“ haben Vorrang.
- Das Tempo des Dateimanagers steht unter **Einstellungen → Allgemein → Dateimanager**.
- Eine eigene Index-Datenbank gibt es bewusst nicht: Sie würde nur den Vergleich beschleunigen, nicht die Kopie, und
  eine veraltete Datenbank könnte Änderungen übersehen.
- API/MCP: Felder `compare` (`standard`, `size`, `checksum`, `tolerant`), `compare_window` (Sekunden) und `speed`
  (`gentle`, `normal`, `fast`, `max`) bei `create_job`/`update_job`; `compare` auch bei `preview_job`.
  Dateimanager: `update_files_settings` (`PATCH /api/v1/settings/files`, Recht „Einstellungen“).

## Ausschlüsse
Ein Eintrag pro Zeile, relativ zur Quelle:

| Eintrag | schließt aus |
|---|---|
| `/Temp/` | Ordner `Temp` direkt in der Quelle |
| `Temp/` | jeden Ordner namens `Temp`, egal wie tief |
| `/Projekte/alt/bericht.docx` | genau diese Datei |
| `*.tmp` | alle `.tmp`-Dateien |
| `**/node_modules/**` | alle `node_modules`-Ordner |

Volle Pfade (z. B. `/data/daten/Temp/`) werden automatisch umgerechnet. Ausgeschlossenes bleibt
im Ziel standardmäßig liegen; mit „Ausgeschlossenes auch im Ziel löschen" wird es dort entfernt.

## Anmeldungen, Sperren und Länder
- **Einstellungen → Benutzer** zeigt pro Konto die letzte Anmeldung mit IP und Land, den Status (aktiv,
  deaktiviert, gesperrt bis …) und Fehlversuche. „Anmeldeverlauf“ listet die letzten 1000 Versuche.
- **Konto bearbeiten:** Aktiv oder Deaktiviert, dazu optional ein Sperrzeitraum mit „gesperrt ab“ und
  „wieder aktiv ab“ (z. B. Urlaub eines Mitarbeiters). Das Konto wird zur Uhrzeit automatisch gesperrt bzw. wieder frei.
- **Einstellungen → Allgemein → Anmeldung und Sicherheit:** nach wie vielen Fehlversuchen ein Konto gesperrt
  wird, für wie lange (0 = bis ein Admin es freigibt) und ob du benachrichtigt wirst. Zusätzlich bremst MirrorSync
  pro IP-Adresse für 5 Minuten.
- **Land:** Der Container lädt die freie Länder-Datenbank von DB-IP (ca. 8 MB) nach `config/geoip/` und erneuert
  sie entweder **nach Intervall** (täglich, wöchentlich, alle 2 Wochen, monatlich = Standard, alle 2 oder 3 Monate)
  oder **nach Zeitplan** mit Uhrzeit und einem oder mehreren Wochentagen (seit 1.32.0, z. B. Mo und Do um 04:30;
  dann wird zur gewählten Zeit immer neu geladen; DB-IP erscheint monatlich). Dafür braucht er Internetzugang zu `download.db-ip.com`. Abgefragt wird nur lokal. Alternativ eine eigene
  `GeoLite2-Country.mmdb` dorthin legen, oder `GEOIP=off` setzen.
- **Hinter einem Reverse-Proxy** (Nginx Proxy Manager, Traefik …) das Häkchen „Reverse-Proxy“ setzen, sonst
  steht überall die IP des Proxys. Ohne Proxy das Häkchen aus lassen.
- **Benutzernamen** sind bei der Anmeldung unabhängig von Groß-/Kleinschreibung (`Max` = `max`).
- **Fehlversuche melden:** Unter „Anmeldung und Sicherheit“ wählst du „bei jedem Fehlversuch“, „nur bei Sperre“
  oder „nie“, dazu eine Drosselzeit (Standard 15 Minuten). Gesammelte Fehlversuche kommen gebündelt in einer Nachricht.
- **Fehlversuche bestätigen oder löschen:** Unbestätigte zeigt eine rote Zahl bei „Einstellungen“ und „Benutzer“.
  Im Anmeldeverlauf („Unbestätigt“) einzeln oder alle bestätigen bzw. löschen.
- Ausgesperrt? `ADMIN_RESET=true` setzt den Admin aus `WEB_USER` zurück und hebt Sperren auf.

## Zugriff nach IP-Adresse und Land
Unter Einstellungen → Zugriff (Recht „Zugriff nach IP-Adresse und Land verwalten“):

- **Erlaubt-Liste:** Nur diese Adressen/Netze/Hostnamen dürfen zugreifen, z. B. nur das lokale Netz (Knopf „Nur
  lokales Netz erlauben“). Leer = alle.
- **Sperrliste:** einzelne IPs, Netze (`1.2.3.4`, `10.0.0.0/8`, IPv6) oder Hostnamen, dauerhaft oder für 1 Stunde bis 30 Tage.
- **Hostnamen (FQDN, seit 1.32.0)** wie `buero.example.de` oder `facebook.com` gehen in beiden Listen. Bei einer
  Anfrage löst MirrorSync den Namen per DNS auf (IPv4 und IPv6, 5 Minuten Cache, höchstens 3 Sekunden) und prüft,
  ob die Adresse dazu gehört. So lassen sich z. B. DynDNS-Adressen erlauben. Ist ein Name gerade nicht auflösbar,
  gilt der letzte bekannte Stand. Die Seite zeigt zu jedem Namen die aktuell aufgelösten Adressen. Platzhalter
  (`*.example.de`) gehen nicht.
  Im Anmeldeverlauf sperrt „IP sperren“ eine Adresse mit einem Klick.
- **Länder:** „nur diese Länder erlauben“ (z. B. DE) oder „diese Länder sperren“. Das lokale Netz ist immer
  ausgenommen, Adressen mit unbekanntem Land werden nicht gesperrt. Braucht die Länder-Datenbank.
- **Automatisch sperren:** IP nach X Fehlversuchen in Y Minuten für Z Minuten oder dauerhaft sperren, optional mit
  Benachrichtigung. Das lokale Netz kann ausgenommen werden (Standard).
- **Kein Aussperren:** Regeln, die deine aktuelle Adresse treffen würden, werden nicht gespeichert.
- **Notfall:** `IPGUARD_RESET=true` in der Compose-Datei setzen, neu starten, wieder entfernen (löscht alle IP- und
  Länderregeln). `IPGUARD=off` schaltet den Schutz ab. Die Sperrseite selbst nennt diese Möglichkeit nicht (seit 1.32.0).
- **Hinter einem Reverse-Proxy** (OPNsense/HAProxy, Nginx Proxy Manager …) unbedingt unter Allgemein „Reverse-Proxy“
  einschalten, sonst sieht MirrorSync nur die IP des Proxys.

## Zwei-Wege-Sync (seit 1.31.0)
Ganz oben in der Aufgabe wählst du die **Art**: „Spiegeln (Einweg): Quelle → Ziel“ oder „Zwei-Wege-Sync:
Seite A ⇄ Seite B“. Beim Zwei-Wege-Sync (`rclone bisync`) wird alles, was sich auf einer Seite ändert, auf die
andere übertragen: neue und geänderte Dateien, Umbenennungen und Löschungen. Beide Seiten werden also beschrieben.
Dafür gibt es ein eigenes Recht „Zwei-Wege-Sync einrichten“.

- **Erster Lauf** (und nach einer Änderung von Seite A, Seite B, Ausschlüssen oder Prüfsumme): Beide Seiten
  werden zusammengeführt (`--resync`). Was nur auf einer Seite liegt, wird auf die andere kopiert, gelöscht wird
  nichts. Ist eine Datei auf beiden Seiten verschieden, gewinnt die neuere. Löschungen werden erst ab dem zweiten
  Lauf übertragen. Tipp: Den ersten Lauf als Testlauf starten.
- **Fehlender Ordner** (seit 1.35.0): Gibt es den Ordner von Seite A oder Seite B beim ersten Lauf noch nicht,
  legt MirrorSync ihn an, wie beim Spiegeln. Fehlt dagegen bei einem späteren Lauf eine Seite, die schon einmal
  da war, oder ist sie plötzlich leer (z. B. Laufwerk nicht eingehängt), bricht der Lauf zum Schutz ab, ohne etwas
  anzulegen oder zu löschen. Das Log sagt dann, was los ist. Ist die Seite wieder da, „Neu zusammenführen“ klicken.
- **Konflikt** (Datei auf beiden Seiten geändert): wählbar „die neuere gewinnt“ (Standard), „beide behalten“,
  „Seite A gewinnt“ oder „Seite B gewinnt“. Die unterlegene Fassung bleibt immer umbenannt erhalten
  (`datei.txt.konflikt1`) und liegt auf beiden Seiten.
- **Löschschutz** in Prozent (Standard 50): Würden auf einer Seite mehr Dateien gelöscht, bricht der Lauf ohne
  Änderung ab und meldet einen Fehler (z. B. wenn ein Laufwerk nicht eingehängt ist). Ist die Löschung gewollt,
  vorübergehend den Wert erhöhen. Mit „Neu zusammenführen“ (Übersicht oder Aufgabe) werden die Seiten stattdessen
  wieder vereint, die fehlenden Dateien kommen dann zurück.
- **Abbruch:** Verlangt rclone nach einem schweren Fehler einen neuen Abgleich, zeigt die Übersicht einen Hinweis
  und den Knopf **„Neu zusammenführen“**. Live-Runden sind bis dahin ausgesetzt.
- Ausschlüsse gelten für beide Seiten. „Ausgeschlossenes löschen“ und „Max. Löschungen“ gibt es beim Zwei-Wege-Sync
  nicht. Versionierung legt Stände in `<seite>.versions/` auf beiden Seiten an. Eine Seite darf nicht in der anderen liegen.
- **Ordnerauswahl und „Quellordner selbst mitkopieren“** (seit 1.33.0) gehen wie beim Spiegeln, auch per Häkchen im
  Durchsuchen-Fenster. Die Auswahl gilt für beide Seiten: Nur die gewählten Ordner und Dateien werden in beide
  Richtungen abgeglichen, alles andere bleibt auf beiden Seiten unberührt. Mit dem Häkchen „Quellordner selbst
  mitkopieren“ ist Seite B der Ordner `<Seite B>/<Name von Seite A>`, er wird beim ersten Lauf angelegt. Eine
  Änderung von Auswahl oder Häkchen führt beim nächsten Lauf neu zusammen (ohne Löschen).
- Live: Jede Runde ist ein Zwei-Wege-Abgleich, Runden ohne Änderung bleiben still.
- Der Zustand (Listen der letzten Runde) liegt in `/config/bisync/<Aufgabe>`.
- API/MCP: Felder `direction` (`mirror`|`bisync`), `bisync_conflict` (`newer`|`none`|`path1`|`path2`),
  `bisync_max_delete`; neu zusammenführen per `POST /api/v1/jobs/{id}/resync` bzw. Tool `resync_job`. Laufende
  Aufgaben: `GET /api/v1/jobs/running` bzw. Tool `list_running_jobs`.

## Start: Uhrzeit, Kette, Live oder manuell
Im Abschnitt „Start“ jeder Aufgabe wählst du:

- **Zu einer Uhrzeit:** Uhrzeit und Wochentage anklicken (z. B. Mo–Fr 03:00). Unter „Erweitert“ geht weiter ein
  Cron-Ausdruck für „alle 15 Minuten“, „stündlich“ usw.
- **Nach einer anderen Aufgabe:** Aufgabe aus der Liste wählen und die Bedingung „nur wenn sie erfolgreich war“
  oder „immer, auch nach einem Fehler“. So entstehen Ketten wie A → B → C. Nach einem Testlauf oder einem Stopp
  startet keine Folgeaufgabe. Schleifen (A nach C, C nach A) werden beim Speichern abgelehnt.
- **Fortlaufend (Live):** siehe unten.
- **Nur manuell:** Start nur über die Übersicht.

Alle Startzeiten an einem Ort zeigt der Menüpunkt **Zeitpläne** mit vier Bereichen: „Nach Uhrzeit“ (Uhrzeit,
Tage, aktiv direkt bearbeiten), „Fortlaufend (Live)“ (Intervall, voller Abgleich, aktiv), „Nach einer anderen Aufgabe“ (Ketten untereinander, Reihenfolge per Drag & Drop
oder ↑ ↓, Bedingung je Aufgabe) und „Nur manuell“. Über die Auswahl „Startart“ wechselt eine Aufgabe sofort in den
passenden Bereich. Alles ist dieselbe Einstellung wie in der Aufgabe selbst.

**Nächster Lauf** (seit 1.33.0): In der Übersicht steht bei jeder Aufgabe unter dem Status, wann sie das nächste
Mal startet, z. B. „heute, 14:30“, „morgen, 03:00“ oder ein Datum. Bei Live-Aufgaben ist es die nächste Runde. Bei
Folgeaufgaben wird die Zeit über den Vorgänger geschätzt („ca. morgen, 03:00“, Tooltip nennt den Vorgänger), läuft
der Vorgänger gerade, steht dort „wenn „…“ fertig ist“. Sonst „nur manuell“, „pausiert“ oder „keiner geplant“
(z. B. Zeitplan aus). REST-API und MCP (`list_jobs`, `get_job`) liefern dazu `next_start` (ISO-Zeit) und
`next_start_kind` (`time`, `live`, `after`, `parent_running`, `manual`, `paused`, `off`).

Die Übersicht zeigt Ketten eingerückt unter ihrer Startaufgabe, mit „nach …“ und „danach: …“. Im Log der vorherigen
Aufgabe steht, welche Folgeaufgaben gestartet wurden. Wird eine Aufgabe gelöscht, stehen ihre Folgeaufgaben auf
„Nur manuell“.

### Fortlaufend (Live)
Echtes Live-Spiegeln per Dateisystem-Ereignis geht nicht, weil Quelle und Ziel entfernte Server sind. MirrorSync
kommt dem mit Runden alle N Minuten nahe (Standard 1, bis 1440). Pro Aufgabe wählst du, was eine Runde tut:

**Wie Spiegeln (Standard, seit 1.30.0):** Jede Runde ist ein normaler Spiegel-Lauf (`rclone sync`). Neue und
geänderte Dateien werden kopiert, was in der Quelle gelöscht oder umbenannt wurde, wird auch im Ziel entfernt.
Übertragen wird nur, was sich wirklich geändert hat, aber beide Seiten werden in jeder Runde aufgelistet. Bei
sehr großen Quellen (mehrere 100.000 Dateien) lieber ein größeres Intervall oder „Schnell“ wählen. „Max.
Löschungen pro Lauf“, Versionierung und Ausschlüsse gelten in jeder Runde. Folgeaufgaben starten nach jeder
Runde, die etwas geändert hat. Ein extra voller Abgleich ist hier nicht nötig.

**Schnell:** zwei Arten von Läufen:

- **Schnelle Live-Läufe** alle N Minuten (Standard 1, bis 1440): `rclone copy --max-age` kopiert nur, was sich
  seit dem letzten erfolgreichen Lauf geändert hat (plus 2 Minuten Puffer), und löscht nichts. Bei wenig
  Änderungen dauert so ein Lauf nur Sekunden, die Quelle wird trotzdem einmal aufgelistet.
- **Voller Abgleich** zu einer Uhrzeit (Standard täglich 03:00), **nach Intervall** (z. B. alle 6 Stunden,
  in der API `@every 6h` oder `@every 90m`, 5 Minuten bis 30 Tage) oder per Cron, abschaltbar: ein normaler Spiegel-Lauf, damit
  Löschungen und Umbenennungen im Ziel ankommen. Der erste Lauf und der nach einer Änderung von Quelle, Ziel
  oder Ausschlüssen ist immer ein voller Abgleich.

Läufe überlappen nie: Läuft der vorige noch, wird die Runde ausgelassen. Live-Läufe ohne Änderung erscheinen
nicht im Verlauf, ihr Log wird sofort gelöscht, die Übersicht zeigt nur „zuletzt geprüft“. Läufe mit kopierten
Dateien stehen mit Kennzeichen „Live“ im Verlauf. Ein Fehler wird einmal gemeldet und einmal protokolliert,
weitere Fehler in Folge zählt die Übersicht nur mit; nach dem nächsten erfolgreichen Lauf meldet sich ein neuer
Fehler wieder. Bandbreite, Ausschlüsse und Versionierung gelten wie sonst. Im Modus „Schnell“ starten
Folgeaufgaben nur nach dem vollen Abgleich. Ist „nur Testlauf“ an, fallen die Live-Läufe aus.

API/MCP: Feld `live_mode` (`mirror` oder `fast`) an der Aufgabe, bei `set_job_trigger` heißt es `mode`.

Grenze: Dateien, die mit altem Änderungsdatum in die Quelle kommen (z. B. verschoben oder aus einem Archiv
entpackt), erkennt erst der volle Abgleich.

## Apprise
Unter Einstellungen → Benachrichtigungen gibt es den Kanal **Apprise**, damit gehen Meldungen an alles, was
[Apprise](https://github.com/caronc/apprise/wiki) kennt (Discord, ntfy, Pushover, Gotify, Signal, Matrix, Teams …).

- **Direkt aus MirrorSync:** Apprise-URLs eintragen, eine pro Zeile, z. B. `ntfy://ntfy.sh/mein-thema` oder
  `discord://webhook_id/webhook_token`. Die Apprise-Bibliothek ist im Image enthalten.
- **Über einen Apprise-API-Server** (z. B. Container `caronc/apprise`): Adresse eintragen, etwa
  `http://192.168.1.20:8000`. Mit Konfigurations-Key nutzt MirrorSync die dort gespeicherten Ziele
  (`/notify/<key>`, optional mit Tag), ohne Key schickt es die eingetragenen URLs mit (`/notify`).

In jeder Aufgabe lässt sich Apprise unter „Eigene Benachrichtigung“ an- und abwählen, mit eigenen URLs oder
eigenem Tag. Apprise gilt auch für die Meldungen zu fehlgeschlagenen Anmeldungen und IP-Sperren. URLs und Key
werden nach dem Speichern nur maskiert angezeigt (`discord://•••`) und nie ins Audit-Log geschrieben.

## Eigene Benachrichtigungstexte
Unter Einstellungen → Benachrichtigungen, Karte „Texte der Benachrichtigungen“, lassen sich Betreff und Text für
jedes Ereignis anpassen: Lauf erfolgreich, Lauf fehlgeschlagen oder gestoppt, fehlgeschlagene Anmeldungen, Konto
gesperrt, IP gesperrt und Testnachricht. Der Text gilt für alle Kanäle (E-Mail-Betreff und -Text, Telegram,
Apprise, Webhook-Feld `message`).

- Variablen wie `{job}`, `{status}`, `{status_icon}`, `{quelle}`, `{ziel}`, `{start}`, `{ende}`, `{dauer}`,
  `{kopiert}`, `{geloescht}`, `{fehler}`, `{fehler_liste}`, `{gestartet_von}`, `{art}`, bei Anmeldungen `{benutzer}`,
  `{ip}`, `{land}`, `{flagge}`, `{anzahl}`, `{liste}` sowie überall `{datum}`, `{zeit}`, `{version}` und im Text
  `{titel}`. Jede Variable lässt sich anklicken und wird an der Cursor-Position eingefügt.
- Die Vorschau zeigt den Text sofort mit Beispieldaten.
- „Auf Standard zurücksetzen“ stellt den eingebauten Text wieder her. Unveränderte Texte werden nicht gespeichert,
  so kommen Verbesserungen am Standardtext bei Updates automatisch an.
- Unbekannte Variablen bleiben stehen, `{{` und `}}` ergeben geschweifte Klammern.

In jeder Aufgabe kann unter Benachrichtigungen „Eigene Texte für diese Aufgabe“ eigene Texte für „Lauf
erfolgreich“ und „Lauf fehlgeschlagen“ festlegen. Der Test-Knopf der Aufgabe schickt den Erfolgstext mit Beispielzahlen.

Beim **Webhook** lässt sich zusätzlich der ganze JSON-Body als Vorlage festlegen, mit Vorlagen für Discord,
Slack/Mattermost, Gotify und Home Assistant/n8n. Werte werden JSON-sicher eingesetzt, Texte gehören in
Anführungszeichen (`"text": "{nachricht}"`), Zahlen dürfen ohne (`"copied": {kopiert}`). Die Vorschau prüft, ob
gültiges JSON entsteht. Ungültige Vorlagen werden nicht gespeichert. Passt eine Vorlage nicht zu einem Ereignis,
kommt das Standard-JSON.

## Seitenleiste einklappen (seit 1.33.0)
Der Pfeil oben in der Seitenleiste (neben „MirrorSync“) klappt sie auf eine schmale Leiste mit nur den Symbolen ein,
der Inhalt nutzt dann die ganze Breite. Beim Überfahren zeigt jedes Symbol seinen Namen. Ein Klick auf den Pfeil
klappt wieder aus. Die Einstellung gilt je Benutzer und wird im Konto gespeichert, also auf allen Geräten und nach
dem Neuladen. Dafür braucht es kein eigenes Recht. Admins mit „Benutzer verwalten“ können sie per REST-API oder MCP
setzen: `PATCH /api/v1/users/{name}` bzw. `update_user` mit `"sidebar": "mini"` oder `"full"`; `get_user` und
`list_users` zeigen sie als `sidebar`. Auf dem Handy gibt es weiter die Leiste oben.

## Datei-Browser
In der Aufgabe öffnet **Durchsuchen** neben Quelle oder Ziel rechts ein Browser-Panel. Auf breiten Bildschirmen
steht es neben dem Formular, sonst darüber, auf dem Handy über die ganze Breite.

- Zuerst den Speicherort wählen (oder `/data`), dann durch die Ordner klicken. SFTP und FTP beginnen bei `/`.
  Auch **„Testen“** bei Speicherorte listet bei SFTP und FTP das Stammverzeichnis `/` (seit 1.48.0, vorher den
  Home-Ordner des Benutzers). Pfade in Aufgaben ändern sich dadurch nicht.
- Ordner und Dateien mit Größe und Änderungsdatum, klickbare Pfadleiste, „..“ für eine Ebene höher, Sortierung
  per Klick auf die Spaltenköpfe, Suche im aktuellen Ordner.
- **Übernehmen** trägt den aktuellen Ordner ins Feld ein. Bei der Quelle markieren ☑ einzelne Dateien oder Ordner,
  dann übernimmt der Knopf die Auswahl (siehe „Nur einzelne Dateien und Ordner“). Esc oder ✕ schließt das Panel.
- **Ausschlüsse:** „Ordner oder Dateien aus der Quelle ausschließen“ öffnet denselben Browser in der Quelle. ⛔
  neben einem Ordner oder einer Datei trägt sie als Ausschluss ein (`/Ordner/` bzw. `/Ordner/datei.txt`), ein
  zweiter Klick nimmt sie wieder heraus. Ausgeschlossenes ist durchgestrichen.

Der Browser liest nur. Er braucht das Recht „Speicherorte: Ordner durchsuchen“, Rollen mit Beschränkung sehen
nur ihre Speicherorte. Alle Seiten nutzen jetzt die volle Fensterbreite.

## Dateimanager
Unter **Dateien** in der Seitenleiste (Recht „Dateimanager: Dateien ansehen“) wählst du oben links einen
Speicherort (oder `/data`). Mit **„Zwei Speicherorte nebeneinander“** kommt rechts ein zweiter dazu.

- **Browsen:** Ordner anklicken, Pfadleiste oben, „Nach oben“. SFTP und FTP beginnen bei `/`. Die Spalten zeigen
  Größe, Änderungszeit und **Berechtigungen** (`rwxr-xr-x`, wenn der Speichertyp sie liefert: lokal und SFTP ja,
  SMB, WebDAV und Clouds nein, dann steht dort „–“). **Ordnergrößen** berechnet Größe sowie Anzahl Unterordner
  und Dateien für alle Ordner der Ansicht, „berechnen“ für einen.
- **Ansicht:** Mit einem Speicherort nimmt er die ganze Breite ein, mit zwei jeweils die Hälfte. Die Listen reichen
  bis zum unteren Fensterrand und scrollen für sich.
- **Rechtsklick** auf einen Eintrag öffnet ein Kontextmenü mit allen Aktionen, bei mehreren markierten für alle.
  Rechtsklick auf die freie Fläche bietet Neuer Ordner, Neue Datei, Hochladen, Neu laden, Ordnergrößen und
  Alle auswählen.
- **⋯ an jeder Zeile:** Eigenschaften (Größe, Zeit, Rechte, Besitzer uid:gid), Bearbeiten (Textdateien bis 1 MB im
  Editor), Herunterladen, Umbenennen, Kopieren nach …, Verschieben nach …, Löschen.
- **Oben:** neuer Ordner, neue Datei, Hochladen (mehrere Dateien). Mit ☑ mehrere Einträge markieren, dann
  Kopieren, Verschieben oder Löschen für alle.
- **Drag & Drop:** Dateien und ganze Ordner vom Computer in eine Liste ziehen lädt sie hoch (auf einen Ordner
  gezogen: in diesen Ordner). Zeilen auf die andere Seite ziehen kopiert sie, mit gedrückter Umschalttaste
  werden sie verschoben. Auf einen Ordner derselben Seite gezogen werden sie dorthin verschoben. Vorher kommt
  eine Rückfrage, bei vorhandenen Dateien einmal „alle überschreiben oder überspringen“.
- **Zwischen zwei Speicherorten:** „Nach rechts kopieren →“ bzw. „← Nach links verschieben“ nimmt den gerade
  geöffneten Ordner der anderen Seite als Ziel. Kopieren und Verschieben laufen als **Auftrag im Hintergrund** mit
  Fortschritt. Der Knopf **„Aufträge“** oben rechts (auf jeder Seite) zeigt als Zahl, wie viele gerade laufen. Ein
  Klick öffnet ein schwebendes Fenster. Oben stehen die **gerade laufenden Aufgaben** (Spiegeln, Zwei-Wege, Live)
  mit Prozent, Balken, Link zum Log und Stopp-Knopf; sie zählen in der Zahl mit und verschwinden, sobald sie fertig
  sind (seit 1.31.0, Recht „Aufgaben ansehen“). Darunter alle Aufträge des Dateimanagers: Status, Prozent und Balken (blau = läuft, grün = fertig,
  rot = Fehler). Laufende lassen sich abbrechen, fertige einzeln oder mit „Alle fertigen entfernen“ entfernen.
  Klick daneben oder Esc schließt es. Man kann die Seite währenddessen verlassen.
- **Gesamtfortschritt auf der Seite Dateien (seit 1.49.0):** Während kopiert oder verschoben wird, steht über den
  Listen eine Karte mit dem Fortschritt über alle Einträge des Auftrags: Prozent und Balken, Bytes „x von y“,
  Dateien „x von y“, Geschwindigkeit, Restzeit und welcher Eintrag gerade dran ist. Zu Beginn wird kurz die
  Gesamtgröße ermittelt. Laufen mehrere Aufträge, kommt eine Zeile „Gesamt“ dazu. Abbrechen geht direkt dort.
- **Rückfragen:** Löschen fragt immer nach. Gibt es im Ziel schon eine Datei oder einen Ordner mit dem Namen,
  fragt MirrorSync vor dem Überschreiben (beim Hochladen, Anlegen, Kopieren, Verschieben).
- **Rechte:** „ansehen“ (durchsuchen, Größen, Berechtigungen, herunterladen), „bearbeiten“ (hochladen,
  bearbeiten, umbenennen, Ordner anlegen, kopieren), „löschen“ (auch nötig zum Verschieben). Es gelten die
  Beschränkung der Rolle und „Sichtbar für“ der Speicherorte, `/data` nur mit „lokale Ordner verwenden“.
- Alles Ändernde und jeder Download steht im Audit-Log (Kategorie „Dateien“).
- API/MCP: `list_file_locations`, `list_files`, `file_size`, `file_info`, `read_file`, `write_file`,
  `upload_file`, `download_file`, `create_folder`, `rename_file`, `delete_files` (mit `confirm=true`),
  `copy_files`, `move_files` (mit `overwrite=true` bei Konflikt), `list_file_tasks`, `cancel_file_task`,
  `delete_file_task`, `clear_file_tasks`.

## Aufgaben pausieren
In der Übersicht hat jede Aufgabe einen Knopf **Pause** (das Menü schließt bei einem Klick daneben oder mit Esc): bis ich fortsetze, 1 Stunde, 24 Stunden, 1 Woche oder
bis zu Datum und Uhrzeit. Eine pausierte Aufgabe ist in Übersicht und Zeitplänen markiert („pausiert bis …“),
startet weder nach Zeitplan noch live noch in einer Kette und läuft nach Ablauf der Zeit von selbst wieder normal
(geprüft jede Minute). Von Hand starten geht weiterhin. „Fortsetzen“ beendet die Pause sofort.

In der Aufgabe unter „Start“ lässt sich dasselbe einstellen, dazu was in einer **Kette** passiert, wenn die
pausierte Aufgabe an der Reihe ist:
- **überspringen** (Standard): Die Aufgabe läuft nicht, ihre Folgeaufgaben starten trotzdem.
- **Kette anhalten:** Die Aufgabe und alles danach läuft nicht.

Das Log der vorherigen Aufgabe vermerkt, was passiert ist. Pausieren, Fortsetzen und das automatische Ende einer
Pause stehen im Audit-Log. Das Recht dafür ist „Aufgaben: bearbeiten“.

## Audit-Log
Der Menüpunkt **Audit-Log** (Recht „System: Audit-Log ansehen und exportieren“, Admins haben es immer) zeigt, wer
wann was gemacht hat:

- Anlegen, Ändern und Löschen von Aufgaben, Zeitplänen, Speicherorten, Benutzern, Rollen, Einstellungen und
  Zugriffsregeln, jeweils mit Vorher/Nachher der geänderten Felder
- manuelle Starts, Testläufe und Stopps, Verbindungstests, Entsperren
- Anmeldungen (auch fehlgeschlagene), Abmeldungen, automatische IP-Sperren, `ADMIN_RESET` und `IPGUARD_RESET`
- zu jedem Eintrag Benutzer, IP-Adresse und Land

**Details (seit 1.32.0):** Ein Klick auf einen Eintrag öffnet ein Fenster mit allem, was dazu bekannt ist: wer, wann,
von welcher IP und welchem Land, über welchen Weg (Weboberfläche mit Browser, REST-API oder MCP, mit Anfrage),
jedes geänderte Feld mit vollständigem altem und neuem Wert, bei Listen und mehrzeiligen Feldern (Ausschlüsse,
Auswahl, Erlaubt-/Sperrliste, Rechte, Mitglieder …) einzeln „+ hinzugefügt“ und „− entfernt“. Beim Anlegen und
Löschen steht der ganze Inhalt da. Im Dateimanager: Pfad, Größe, Änderungsdatum, bei Ordnern die enthaltenen
Dateien (bis 200), beim Bearbeiten einer Textdatei die geänderten Zeilen (Auszug, Werte von Zeilen wie
`password=` oder `token:` werden maskiert), bei Kopieren/Verschieben Von, Nach und Statistik. Bei Starts die Quelle,
das Ziel und die Lauf-Nummer. Alte Einträge zeigen, was damals gespeichert wurde. Die API liefert dieselben Felder
(`changes[].added/removed/old_full/new_full`, `info`).

Passwörter, Tokens, 2FA-Schlüssel und andere Geheimnisse landen nie im Log, nur der Hinweis „geändert“. Filter
nach Bereich, Benutzer und Zeitraum, Freitextsuche (auch in alten und neuen Werten), Export als CSV (für Excel,
mit `;` getrennt) mit denselben Filtern. Gespeichert in `config/audit.jsonl`, Aufbewahrung unter
Einstellungen → Allgemein (Standard 365 Tage, höchstens 20 000 Einträge).

## Bandbreite
Unter Einstellungen → Allgemein legst du die Standard-Bandbreite fest, in jeder Aufgabe unter „Bandbreite“
lässt sie sich überschreiben („Standard verwenden“, „Eigene Grenzen“, „Immer unbegrenzt“).

- **Außerhalb der Zeitfenster:** Grenze, die gilt, wenn kein Zeitfenster passt (leer = unbegrenzt).
- **Einheit:** MB/s (Megabyte pro Sekunde, Standard) oder Mbit/s (Megabit pro Sekunde, wie bei Internetanschlüssen),
  wählbar bei der Standard-Bandbreite; gilt für alle Anzeigen. 1 MB/s = 8 Mbit/s. Gespeichert wird immer in MB/s,
  ein Wechsel rechnet die Felder um.
- **Zeitfenster:** Wochentage, von–bis, Upload und Download. Beispiel: Mo–Fr 08:00–18:00 10 MB/s,
  sonst unbegrenzt. Fenster wie 22:00–06:00 gehen über Mitternacht; bei Überschneidung gilt das untere.
- Upload = zum Ziel, Download = von der Quelle. Als Vermittler (A → B) reicht meist ein Wert, weil alles von A
  direkt nach B weitergereicht wird.
- Die Grenzen wechseln auch während eines laufenden Spiegelns zur eingestellten Uhrzeit (Zeitzone aus `TZ`).
- Intern wird daraus eine rclone-Zeittabelle (`--bwlimit "Mon-08:00,10M Mon-18:00,off …"`), sichtbar im Log.
  Ein eigenes `--bwlimit` in den zusätzlichen rclone-Optionen hat Vorrang.

## Logs
Jeder Lauf bekommt ein eigenes Log unter `logs/<aufgabe>/<datum-uhrzeit>.log`. Über „Log" bei einer Aufgabe
siehst du den letzten Lauf und den Verlauf mit Anzahl kopierter, gelöschter und fehlerhafter Dateien. Ein Klick
auf einen Lauf öffnet sein ganzes Log:

- Filter: Alle, Fehler, Kopiert, Gelöscht (auch „in Versionierung verschoben"), Hinweise
- Suche nach Dateinamen oder Ordnern, kombinierbar mit dem Filter
- „Herunterladen" speichert das vollständige Log als Textdatei
- Ein laufender Lauf aktualisiert sich alle 3 Sekunden

Aufbewahrung unter Einstellungen → Allgemein → Logs aufbewahren:
- **Läufe pro Aufgabe** (Standard 50, 0 = unbegrenzt).
- **Höchstens so lange** als Zahl in Tagen, Wochen oder Monaten (Standard 30 Tage, 0 = unbegrenzt, ein Monat = 30 Tage).

Sind beide Grenzen gesetzt, gilt die, die zuerst greift. Der neueste Lauf bleibt immer erhalten. API/MCP:
`PATCH /api/v1/settings/logs` (`update_log_settings`) mit `log_keep_runs` und `log_keep_days` (in Tagen).

**Alte Logs löschen** (seit 1.39.0, gleiche Seite): Datum wählen, „Anzahl anzeigen“ klicken, dann „Jetzt
endgültig löschen“ bestätigen. Einmalig werden alle Läufe samt Log gelöscht, die vor diesem Datum gestartet sind.
Laufende Aufgaben bleiben unberührt, die Aufbewahrung ändert sich nicht, das Audit-Log vermerkt die Löschung.
API/MCP: `POST /api/v1/logs/purge` (`purge_logs`) mit `before` (`JJJJ-MM-TT`), `dry_run: true` zählt nur. Das Log aus Version 1.4 und älter wird beim
ersten Start als Lauf „alt-…" übernommen.

## API-Keys, REST-API und MCP
Unter **Einstellungen → API** legst du API-Keys an (Recht „API-Keys verwalten“, Admins haben es):

- **Name** (z. B. n8n, Home Assistant, Claude) und **Rolle**. Der Key hat genau die Rechte und
  Beschränkungen dieser Rolle (Aufgaben, Speicherorte), wie ein Benutzer. Für einen Key mit wenigen Rechten
  unter Rollen eine eigene Rolle anlegen, z. B. nur „Aufgaben ansehen“ und „starten“. Vergeben kann man nur
  Rollen, deren Rechte man selbst hat.
- Optional **Ablaufdatum** und **erlaubte IP-Adressen** (einzelne IPs oder Netze wie `192.168.1.0/24`).
- Der Key (`msk_…`) wird nach dem Anlegen angezeigt. Seit 1.24.0 kann man ihn später mit **„Anzeigen“**
  nochmal sehen, nach Eingabe des eigenen Passworts (plus 2FA-Code, falls eingerichtet) oder mit einem
  Passkey. Das geht nur in der Web-GUI, nicht per API oder MCP, und steht im Audit-Log („API-Key angezeigt“).
  Gespeichert ist er dafür verschlüsselt (Schlüssel aus `config/secret_key`). **Keys von vor 1.24.0 lassen sich
  nicht nachträglich anzeigen**, von ihnen existiert nur der SHA-256-Hash; bei Bedarf neu anlegen. Nach
  einem Import ohne den alten `secret_key` gilt das ebenso. Die Liste zeigt „zuletzt benutzt“ mit IP.
- **Bearbeiten**: Name, Rolle (Rechte), Ablaufdatum, IPs, Gruppen sowie **Aktiv/Deaktiviert**, eine
  **Pause** von–bis und **Zeitfenster** pro Wochentag (z. B. Mo–Fr 08:00–18:00, über Mitternacht geht auch).
  Außerhalb wird der Key abgelehnt, die Liste zeigt den Status. Den gerade benutzten Key kann man nicht
  deaktivieren oder seine Rolle ändern. API `PATCH /api-keys/{id}`, MCP `update_api_key`.
- **Widerrufen** sperrt ihn endgültig, er bleibt aber in der Liste.
  **Entfernen** entfernt ihn ganz (auch aus Gruppen), Einträge im Audit-Log bleiben. Den Key, mit dem man
  gerade über die API zugreift, kann man nicht löschen. API: `POST /api-keys/{id}/revoke` bzw.
  `DELETE /api-keys/{id}`, MCP: `revoke_api_key` bzw. `delete_api_key`.
- Alles, was ein Key tut, steht im Audit-Log als Benutzer `API:<Name>` (Knopf „Audit“ in der Liste).
  Fehlversuche zählen wie falsche Passwörter (IP-Bremse, Anmeldeverlauf), IP- und Länderregeln gelten
  auch für die API, höchstens 300 Anfragen pro Minute und Key.

### REST-API
Basis `https://sync.example.de/api/v1`, Anmeldung mit `Authorization: Bearer <Key>`. Die Dokumentation zum
Ausprobieren liegt unter **`/api/docs`** (Swagger-UI, mit GUI-Anmeldung oder über „Authorize“ mit Key), die
Spezifikation unter `/api/v1/openapi.json`. Die Links unter Einstellungen → API öffnen einen neuen Tab.

| Methode und Pfad | Zweck | Recht |
|---|---|---|
| `GET /status` | Version, laufende, fehlgeschlagene, pausierte Aufgaben, Rechte des Keys | – |
| `GET /jobs`, `GET /jobs/{id}` | Aufgaben mit Status und nächstem Start | jobs.view |
| `POST /jobs`, `PATCH /jobs/{id}`, `DELETE /jobs/{id}` | anlegen, ändern (nur angegebene Felder), löschen | jobs.create / edit / delete |
| `POST /jobs/{id}/run` (`?dry_run=true`), `/stop` | starten, Testlauf, stoppen | jobs.run / jobs.dryrun |
| `POST /jobs/{id}/pause` (`?hours=2` oder `?until=…`), `/resume` | pausieren, fortsetzen | jobs.edit |
| `GET /jobs/{id}/history`, `GET /jobs/{id}/log` (`?filter=error&q=…`) | Verlauf, Log eines Laufs | jobs.logs |
| `GET /remotes`, `GET /browse?path=NAS:daten` | Speicherorte (ohne Zugangsdaten), Ordner | remotes.view / browse |
| `GET /schedules`, `GET /audit`, `GET /users` | Zeitpläne, Audit-Log, Benutzer | jobs.view / system.audit / users.view |

```bash
KEY=msk_xxxxxxxx_xxxxxxxxxxxxxxxxxxxx
curl -H "Authorization: Bearer $KEY" https://sync.example.de/api/v1/status
curl -H "Authorization: Bearer $KEY" https://sync.example.de/api/v1/jobs
curl -X POST -H "Authorization: Bearer $KEY" "https://sync.example.de/api/v1/jobs/<id>/run?dry_run=true"
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
     -d '{"name":"Fotos","source":"NAS:fotos","dest":"Server:/backup/fotos","trigger":"time","schedule":"0 3 * * *"}' \
     https://sync.example.de/api/v1/jobs
curl -X PATCH -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
     -d '{"versioning":true,"excludes":["*.tmp"]}' https://sync.example.de/api/v1/jobs/<id>
```
Fehler kommen als `{"error": "…"}` mit passendem Status (400, 401, 403, 404, 409, 429).

**Alles aus der GUI geht auch per API und MCP** (seit 1.21.0): Zusätzlich zu den Aufgaben gibt es Endpunkte für
Zeitpläne und Ketten, Speicherorte (anlegen mit Assistent-Fragen, ändern, testen, neu anmelden, löschen),
Benachrichtigungen und Vorlagen (seit 1.41.0 auch Kanäle anlegen: `setup_notification_channel` bzw.
`POST /settings/notifications/channels/{webhook|smtp|telegram|apprise}` mit Feldern wie `url`, `host`, `token`,
`chat_id`, `add_urls` und optional `test: true`; ausschalten mit `remove_notification_channel`, Recht `notify.edit`),
allgemeine Einstellungen (Logs, Sicherheit, Länder-Datenbank, Sprache,
Bandbreite mit Einheit), Zugriff nach IP und Land, Gruppen, Sichtbarkeit (`visible_to` bei Aufgaben und
Speicherorten, `groups` bei Benutzern), Benutzer (anlegen, ändern, sperren, entsperren, 2FA und
Passkeys zurücksetzen, löschen), Anmeldeverlauf, Rollen, API-Keys sowie Sicherung, Export, Import und
Wiederherstellen. Die vollständige Liste steht in `/api/docs`.
- Jede Aktion läuft intern durch dieselbe Funktion wie in der GUI: gleiche Prüfungen, gleiche Rechte (Rolle des
  Keys), gleiche Schutzregeln (z. B. bleibt immer ein aktiver Admin, man kann sich nicht selbst aussperren) und
  ein Eintrag im Audit-Log als `API:<Name>`.
- Passwörter, Tokens und andere Geheimnisse lassen sich nur schreiben, nie lesen (Antwort z. B. `"token_set": true`).
- Sicherung, Export, Import und Wiederherstellen nur mit Admin-Rolle. Import zeigt zuerst eine Vorschau und
  übernimmt erst mit `confirm=true`.
- Nicht per Key: eigenes Passwort, eigene 2FA und Passkeys (das bleibt beim Konto unter „Mein Konto“).
- Sprache der Antworten (Meldungen, Swagger-Texte, MCP-Tool-Beschreibungen): `?lang=en|de|es|it|fr`, sonst
  `Accept-Language`, sonst die Einstellung **„Sprache der API-Antworten“** am Key. Standard dort ist „Wie der
  Benutzer“: die Sprache des Benutzers, der den Key angelegt hat (Mein Konto → Sprache). Ist kein Benutzer
  bekannt (z. B. gelöscht oder noch nicht angemeldet), antwortet die API auf Englisch. Per API/MCP: Feld
  `lang` bei `create_api_key`/`update_api_key`.
**n8n:** HTTP-Request-Node mit „Header Auth“ (`Authorization` = `Bearer msk_…`). **Home Assistant:**
`rest_command` bzw. `rest`-Sensor mit demselben Header, z. B. `POST …/jobs/<id>/run`.

### MCP-Server
`https://sync.example.de/mcp` (Streamable HTTP, Antworten als JSON, ohne Sitzung), Anmeldung mit demselben
Header. Tools: `status`, `list_jobs`, `get_job`, `job_history`, `job_log`, `run_job`, `stop_job`, `pause_job`,
`resume_job`, `create_job`, `update_job`, `delete_job`, `list_remotes`, `browse`, `list_schedules`,
`audit_log`, `list_users` und dazu alle Tools für die übrigen Bereiche (siehe oben, gleiche Namen wie in
`/api/docs`, z. B. `create_remote`, `update_user`, `set_bandwidth`, `update_security_settings`). Der Client sieht nur die Tools, für die der Key das Recht hat; ein Key mit „Nur
lesen“ bekommt also keine schreibenden Tools.

Beispiel für Clients mit JSON-Konfiguration (Claude Desktop, Cursor, VS Code u. a.; der Schlüssel heißt je nach
Client `mcpServers` oder `servers`):
```json
{
  "mcpServers": {
    "mirrorsync": {
      "type": "http",
      "url": "https://sync.example.de/mcp",
      "headers": { "Authorization": "Bearer msk_xxxxxxxx_xxxxxxxxxxxxxxxxxxxx" }
    }
  }
}
```
Claude Code: `claude mcp add --transport http mirrorsync https://sync.example.de/mcp --header "Authorization: Bearer msk_…"`.
Clients, die nur lokale (stdio) Server können, binden ihn über `npx mcp-remote https://sync.example.de/mcp --header "Authorization: Bearer msk_…"` an.

## Datenbank, Export und Import
Seit 1.18.0 liegen Aufgaben, Verlauf, Einstellungen, Vorlagen, Benutzer (mit 2FA und Passkeys), Rollen,
IP-Regeln, Anmeldeverlauf und Audit-Log in einer SQLite-Datei `config/mirrorsync.db`. `rclone.conf` bleibt
eine eigene Datei.

- **Umstellung:** Beim ersten Start von 1.18.0 übernimmt MirrorSync alle alten JSON-Dateien automatisch in
  einem Schritt (ganz oder gar nicht). Danach liegen sie unverändert in `config/json-backup/`. Bricht die
  Übernahme ab, bleibt alles wie es war, und der nächste Start versucht es erneut. Ist eine Datei kaputt,
  startet der Container nicht und nennt die Datei im Log, statt mit leeren Daten zu starten.
- **Exportieren** (Einstellungen → Sicherung, nur Admins): lädt alles als ZIP herunter, also Datenbank-Inhalt,
  `rclone.conf`, SSH-Schlüssel und andere eigene Dateien aus `config/`, optional die Lauf-Logs. Die Datei
  enthält Geheimnisse, deshalb optional mit Passwort verschlüsseln (AES-256-GCM, Datei `.zip.enc`).
- **Importieren:** Datei hochladen, MirrorSync prüft sie und zeigt Version, Datum und Inhalt im Vergleich zum
  aktuellen Stand. Dateien aus einer neueren Version werden abgelehnt. Erst nach Bestätigung wird ersetzt,
  vorher legt MirrorSync automatisch eine Sicherung in `config/backups/` an (die letzten 10 bleiben, dort auch
  herunterladbar). Während Aufgaben laufen, ist kein Import möglich.
- Export, Import und Download von Sicherungen stehen im Audit-Log.

### Automatische Sicherung
Einstellungen → Sicherung → **Automatische Sicherung**:

- **Zeitplan** als Cron-Ausdruck mit Vorlagen (täglich 3:00, alle 6 Stunden, stündlich, sonntags, monatlich).
- **Nur bei Änderung:** Vor jeder Sicherung bildet MirrorSync eine Prüfsumme über Aufgaben, Speicherorte,
  Benutzer, Rollen, Einstellungen, Vorlagen, IP-Regeln, API-Keys und die Dateien in `config/`. Ist sie gleich
  wie bei der letzten Sicherung (und die Datei existiert noch), entsteht **keine neue Datei**. Verlauf, letzte
  Anmeldung, Fehlversuch-Zähler, Anmeldeverlauf und Audit-Log zählen nicht als Änderung.
- **Ziel:** Standard `config/backups/`. Für eine Kopie außerhalb des Config-Ordners einen eigenen Ordner
  einbinden, z. B. `- /mnt/nas/mirrorsync-backup:/backups` und als Ziel `/backups` eintragen.
- **Aufbewahrung:** Anzahl und/oder höchstens N Tage, die neueste bleibt immer.
- **Passwort** (optional, mindestens 8 Zeichen): die Dateien werden wie beim Export verschlüsselt (`.zip.enc`).
  Das Passwort wird gespeichert, damit „Wiederherstellen…“ diese Dateien direkt öffnen kann.
- **Benachrichtigung:** nie, nur bei Fehler oder bei Erfolg und Fehler, optional auch „nichts geändert“; Kanäle
  frei wählbar (leer = alle aktiven). Betreff und Text unter Benachrichtigungen → Vorlagen
  (Ereignisse „Automatische Sicherung erstellt / nichts geändert / fehlgeschlagen“).
- **Jetzt sichern** (optional „auch ohne Änderung“), Liste aller gespeicherten Sicherungen mit Herunterladen,
  Wiederherstellen (zeigt erst die Prüfung wie beim Import) und Löschen. Alles steht im Audit-Log.

## Sprachen
Die Oberfläche, Fehlermeldungen, API- und MCP-Texte und die Standard-Vorlagen der Benachrichtigungen gibt es
auf **Englisch, Deutsch, Spanisch, Italienisch und Französisch**.

- **Bei der Einrichtung** wird die Systemsprache gewählt (vorausgewählt: Englisch). Bestehende Installationen
  behalten nach dem Update Deutsch.
- **Systemsprache** ändern: Einstellungen → Allgemein → Sprache. Sie gilt für die Anmeldeseite,
  Benachrichtigungen und alle Benutzer ohne eigene Auswahl.
- **Eigene Sprache:** jeder Benutzer unter **Mein Konto** → Sprache.
- **API und MCP** antworten in der Sprache aus `?lang=xx` oder dem Header `Accept-Language`, sonst in der
  Sprache des Keys (Standard: wie der Benutzer, dem er gehört), sonst auf Englisch.
- Selbst geschriebene Texte (Namen, eigene Vorlagen) und die Lauf-Logs bleiben, wie sie sind.

**Weitere Sprache hinzufügen:** `app/i18n/en.json` kopieren, z. B. als `app/i18n/nl.json`, oben
`"_meta": {"name": "Nederlands", "code": "nl"}` eintragen und die Werte übersetzen (die Schlüssel links sind der
deutsche Originaltext und bleiben unverändert). Platzhalter wie `{0}`, `{job}`, HTML-Tags und `{{ … }}` müssen
erhalten bleiben. Fehlt ein Eintrag, erscheint Englisch. Danach Image neu bauen, die Sprache erscheint
automatisch in allen Auswahllisten.
- Zurück auf eine Version vor 1.18.0: die Dateien aus `config/json-backup/` zurück nach `config/` legen.

## Hinweis auf neue Versionen (seit 1.34.0)
MirrorSync fragt regelmäßig (Standard: einmal pro Stunde) bei GitHub (`api.github.com`, Repo `DerMilderJoghurt/mirrorsync`) nach, ob es eine
neuere Version gibt. Wenn ja, steht unten links unter der Versionsnummer „⬆ vX.Y.Z verfügbar“, ein Klick öffnet das
Release mit allen Änderungen. Übertragen wird dabei nur die eigene Versionsnummer.

- Ein- und ausschalten unter **Einstellungen → Allgemein → Updates**, dort auch „Jetzt prüfen“ (prüft sofort, ohne Eingaben zu speichern; seit 1.47.0 getrennt von „Speichern“) und
  wann zuletzt geprüft wurde. Den **Abstand** stellst du dort ebenfalls ein: Zahl eingeben, Minuten oder Stunden
  wählen (5 Minuten bis 720 Stunden, Standard 1 Stunde). Aktualisiert wird nur, wenn du das Selbst-Update nutzt (siehe unten), sonst bleibt das bei dir.
- API/MCP: `GET /api/v1/update` (`get_update`), `POST /api/v1/update/check` (`check_update`),
  `PATCH /api/v1/settings/update` mit `{"update_check": false}` und/oder `{"update_interval": 120}` (Minuten)
  (`update_update_settings`); `/status` enthält `update` mit `interval_minutes`.
- **Benachrichtigung bei neuer Version** (seit 1.46.0): unter Einstellungen → Allgemein → Updates „Benachrichtigung
  schicken, wenn eine neue Version verfügbar ist“ anhaken und optional die Kanäle wählen (keiner = alle
  eingeschalteten). Je neue Version kommt genau eine Nachricht. Den Text änderst du unter Benachrichtigungen →
  Texte der Benachrichtigungen („Neue MirrorSync-Version verfügbar“, Variablen `{neu}`, `{url}`,
  `{veroeffentlicht}`). API/MCP: `update_notify` und `update_notify_channels` bei `update_update_settings`.
- Ein anderes Repo (z. B. ein eigener Fork) lässt sich per `UPDATE_REPO=besitzer/repo` einstellen.

## Selbst-Update über den Docker-Socket (seit 1.42.0, optional)
MirrorSync kann sich selbst aktualisieren, wenn du den Docker-Socket in den Container einbindest:

```yaml
    volumes:
      - ./config:/config
      - ./logs:/logs
      - /var/run/docker.sock:/var/run/docker.sock   # optional: Selbst-Update
```

> **Sicherheit:** Wer den Docker-Socket hat, hat volle Kontrolle über alle Container auf dem Host (praktisch
> Root-Rechte). Binde ihn nur ein, wenn du das willst, und gib das Recht „MirrorSync aktualisieren“ nur Admins.
> Ohne Socket ist die Funktion ausgeschaltet und du aktualisierst wie bisher (Dockhand, Portainer,
> `docker compose pull && docker compose up -d`).

- **Jetzt aktualisieren:** unten links beim Hinweis „⬆ vX.Y.Z verfügbar“ und unter **Einstellungen → Allgemein →
  Selbst aktualisieren**. Optional **automatisch einmal am Tag** ab einer Uhrzeit. Läuft gerade eine Aufgabe, wartet
  das Update, bis sie fertig ist.
- **So läuft es ab:** MirrorSync holt das Image neu (derselbe Name und Tag wie beim laufenden Container, z. B.
  `:latest`). Ist es neuer, startet ein kurzlebiger Hilfs-Container aus dem neuen Image. Er stoppt den alten
  Container, legt einen neuen mit **genau denselben Einstellungen** an (Name, Ports, Volumes, Umgebungsvariablen,
  Netzwerke mit fester IP und MAC-Adresse, Neustart-Regel, Labels) und startet ihn. Die Labels von Docker Compose
  bleiben erhalten und werden angepasst, daher erkennen `docker compose`, Dockhand und Portainer den Container
  weiter als ihren und legen ihn nicht noch einmal neu an. Umgebungsvariablen, die aus dem Image stammen (z. B.
  die Python-Version), kommen aus dem neuen Image, alles aus deiner Compose-Datei bleibt.
- **Rollback:** Antwortet die neue Version nicht innerhalb von 2 Minuten auf `/health` oder beendet sie sich, wird
  sie entfernt und die bisherige läuft wieder. Ergebnis und Ablauf stehen in der GUI, im Audit-Log
  („Update gestartet / abgeschlossen / fehlgeschlagen“) und in `config/selfupdate.json`.
- **Voraussetzungen:** Das Image muss aus einem Registry kommen (`image: ghcr.io/dermilderjoghurt/mirrorsync:latest`).
  Mit `build: .` gebaute Images kann MirrorSync nicht neu holen. Mit festem Versions-Tag (`:1.50.0`) wird nur dieser
  Tag neu geholt. `/config` muss als Volume oder Ordner eingebunden sein (ist es in der Beispiel-Compose).
- **Recht:** `system.update` („MirrorSync aktualisieren“, Admins haben es automatisch). Automatik und Uhrzeit
  ändern braucht `system.settings`.
- **API/MCP:** `GET /api/v1/update/self` (`get_self_update`), `POST /api/v1/update/apply` (`self_update`),
  `PATCH /api/v1/settings/update` mit `selfupdate_auto` und `selfupdate_time` (`update_update_settings`).

## Android-App (seit 1.40.0)
Im GitHub-Repo liegt unter `android/` eine kleine Android-App (ab Android 7): die MirrorSync-Weboberfläche ohne
Browserleiste, mit eigenem Symbol und Benachrichtigungen. Weil sie die normale Weboberfläche zeigt, ist jede neue
MirrorSync-Funktion sofort in der App.

- **Installieren:** `mirrorsync-<version>.apk` aus dem [neuesten Release](https://github.com/DerMilderJoghurt/mirrorsync/releases/latest)
  auf dem Handy laden und öffnen (einmalig „Unbekannte Apps installieren“ für Browser oder Dateimanager erlauben).
  Updates: neuere APK einfach drüber installieren, Einstellungen und Anmeldung bleiben.
- **Erster Start:** die Adresse eingeben, die du auch im Browser nutzt, z. B. `https://sync.example.com` oder
  `http://192.168.1.50:8080`. Später ändern über die Zurück-Taste auf der Startseite, den Fehlerbildschirm oder
  langes Drücken auf das App-Symbol → „Server & Benachrichtigungen“.
- **Passkeys** in der App brauchen wie im Browser HTTPS mit Domainnamen, eine aktuelle „Android System WebView“
  und Google-Play-Dienste. Android prüft `https://<deine Domain>/.well-known/assetlinks.json`, das MirrorSync selbst
  ausliefert. Google holt diese Datei aus dem Internet, sie muss also von außen erreichbar sein (Reverse-Proxy,
  kein Geo-Blocking für diesen Pfad). Im Browser angelegte Passkeys gehen auch in der App und umgekehrt.
  Klappt es nicht, geht Passwort + 2FA immer.
- **Benachrichtigungen:** standardmäßig an für fehlgeschlagene Läufe, wahlweise auch für erfolgreiche und
  abgebrochene. Die App fragt im Hintergrund `GET /api/v1/jobs` ab (alle 15 Min. bis 6 Std., Android verschiebt
  das evtl. etwas). Sie nutzt die Anmeldung der App, beim Anmelden „Angemeldet bleiben“ ankreuzen. Robuster: einen
  API-Key mit einer Rolle eintragen, die Aufgaben sehen darf.
- **Selbst bauen:** `cd android && ./gradlew assembleRelease` (JDK 17, Android SDK). Mit eigenem Schlüssel
  signiert: dessen SHA-256-Fingerabdruck am Server über `MIRRORSYNC_ANDROID_CERTS=AB:CD:…` eintragen, damit
  Passkeys weiter gehen.

## Update auf eine neue Version
```bash
docker compose pull && docker compose up -d
```
Mit `docker run`: `docker pull ghcr.io/dermilderjoghurt/mirrorsync:latest`, Container entfernen und mit
demselben Befehl neu starten. `config/` und `logs/` bleiben erhalten. Die laufende Version steht unten in der
GUI und unter `/health`.

## Hinweise
- **Spiegeln löscht im Ziel.** Ziel nie auf einen Ordner mit anderen wichtigen Daten zeigen lassen.
- Der Lösch-Schutz (Standard 500) bricht nach N Löschungen ab. Bis dahin Gelöschtes ist weg,
  außer die Versionierung ist an. Für wichtige Daten Versionierung einschalten.
- SSH-Schlüssel statt Passwort: Schlüssel nach `./config/` legen und im SFTP-Speicherort
  `/config/id_ed25519` eintragen.
- Dienste mit Browser-Login (OneDrive, Google Drive, Dropbox, pCloud …): Nach dem Anlegen zeigt die GUI
  den Befehl `rclone authorize "<dienst>"`. Den einmal auf einem PC mit Browser ausführen (rclone von
  rclone.org/downloads entpacken), anmelden und das ausgegebene Token in die GUI einfügen. Abgebrochene
  oder abgelaufene Anmeldungen per Knopf „Anmelden“ neu starten.
- crypt: Erst den eigentlichen Speicherort anlegen (z. B. `nas`), dann einen crypt-Speicherort mit
  `remote = nas:verschluesselt` und Passwort. Im Job dann den crypt-Namen als Ziel verwenden.
- Beim Bearbeiten Passwortfelder leer lassen, dann bleibt das gespeicherte Passwort erhalten.
- Daten liegen in `./config` (Datenbank `mirrorsync.db`, Speicherorte `rclone.conf`) und `./logs` (Lauf-Logs).
- Die GUI nur im Heimnetz betreiben oder hinter einen Reverse-Proxy mit HTTPS stellen.
- Enthalten sind nur Alpine Linux mit Python 3.15, rclone 1.76 und wenige Python-Pakete (`app/requirements.txt`),
  kein PHP und kein Node.js. Auf GitHub prüft Dependabot jede Woche auf neue Versionen, und Trivy scannt jedes
  Image auf bekannte Schwachstellen (Ergebnisse unter „Security“ im Repo).
