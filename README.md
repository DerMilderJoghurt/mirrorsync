<p align="center">
  <img src="docs/logo.png" alt="MirrorSync" width="480">
</p>

# MirrorSync – 1:1 mirroring with a web GUI and schedules

Version **1.46.0** · Changes: [CHANGELOG.md](CHANGELOG.md) · [Deutsche Version](README.de.md)

A Docker container that **mirrors folders one-way, 1:1** (like FreeFileSync "Mirror"):
the destination becomes an exact copy of the source, including deletions. The sync engine is
[rclone](https://rclone.org), so **SMB, WebDAV (Nextcloud …), SFTP/SSH, FTP/FTPS, S3, local folders**
and many more work, in any combination (e.g. SMB → WebDAV). Two-way sync is available too.

![Jobs overview](docs/screenshots/jobs.png)

<details><summary>More screenshots</summary>

| | |
|---|---|
| ![Dark theme](docs/screenshots/jobs-dark.png) | ![Edit job](docs/screenshots/edit-job.png) |
| Dark theme | Edit job |
| ![Schedules](docs/screenshots/schedules.png) | ![Storage](docs/screenshots/remotes.png) |
| Schedules | Storage |
| ![File manager](docs/screenshots/files.png) | |
| File manager | |

</details>

## Quick start
```bash
docker run -d --name mirrorsync --restart unless-stopped \
  -p 8080:8080 -e PORT=8080 -e TZ=Europe/Berlin \
  -v ./config:/config -v ./logs:/logs \
  ghcr.io/dermilderjoghurt/mirrorsync:latest
```
Then open `http://<docker-host>:8080` and create the first admin.

## Features
- **Multiple users** with **custom roles** (individual permissions per action, can be limited to specific jobs and storage locations), **2FA** with an authenticator app incl. backup codes, and **passkeys**
- **REST API with Swagger** and an **MCP server** for n8n, Home Assistant, scripts and AI assistants, with **API keys** and the same permissions as users
- **Five languages**: English (default), German, Spanish, Italian, French. Pick the language during setup, every user can choose their own
- **Automatic backup** of the configuration on a schedule, only when something changed, optionally encrypted and with notification
- **First-time setup in the browser** with a one-time code from the container log, no password in the compose file
- Modern web GUI (sidebar, light and dark theme) with its own login page: create, edit, start and stop jobs
- **Scheduling** per job with cron, with presets (hourly, daily 03:00 …), as a chain after another job, or **continuous (live)** every few minutes
- **Two-way sync** (rclone bisync): changes and deletions on both sides are transferred, with a conflict rule and deletion protection
- **Audit log**: who did what and when, with before/after values, filters, search and CSV export
- **Storage locations for every rclone backend** (about 55), created, edited and tested directly in the GUI: SMB, WebDAV, SFTP, FTP, S3 (AWS, MinIO, Wasabi …), B2, Azure, Google Drive, OneDrive, Dropbox, pCloud, MEGA, crypt and more
- Browser login (OAuth) for Google Drive, OneDrive, Dropbox, pCloud … with step-by-step instructions in the GUI
- **File manager** (sidebar "Files"): browse one storage location or two side by side, see folder sizes and
  permissions, edit text files, upload and download, rename, delete, copy and move, also from one storage location to another
- **File browser** in the job form for source, destination and excludes (side panel with size, date, sorting, search)
- **Pause** jobs indefinitely or until a point in time
- **Excludes**: exclude folders, files or patterns (e.g. `/Temp/`, `*.tmp`) per job, pick folders from the source with a click
- **Dry run** (only shows what would happen), live log and a separate log for every run (filter, search, download)
- **Versioning**: deleted/overwritten files go to `<destination>.versions/<date>`, optionally keep only the
  last N versions or at most X days (older ones are removed after each run)
- **Deletion protection**: the run aborts if more than N files would be deleted
- **Notifications** via webhook (ntfy, Discord, Slack, Home Assistant, n8n …), email (SMTP), Telegram and **Apprise** (over 100 services, directly or via an Apprise API server), with a test button; when (always / only on failure / never) as a default for all jobs, or per job with its own channels, recipients, chat ID and test button

## Running as a relay (server A → server B)
The container does not have to run on A or B. It connects to both and passes the data through:
create storage locations `server-a` (e.g. SFTP) and `server-b` (e.g. SMB), then a job
`server-a:/path` → `server-b:share/path`. No local folders need to be mounted for this.
Note: all data flows through the Docker host, its connection to A and B determines the speed.
Changed files are transferred completely (no delta transfer like rsync).

## Installation
The ready-made image is in the GitHub Container Registry: `ghcr.io/dermilderjoghurt/mirrorsync`
(for amd64 and arm64, e.g. Raspberry Pi). Tags: `latest` (newest version), `1.46.0` (fixed version),
`1.40` (newest patch of this version). The image is only published when the version number changes, so
update checkers such as Dockhand or Watchtower only report an update when there really is a new version.

### With Docker Compose (recommended)
1. Create a folder and put the [`docker-compose.yml`](docker-compose.yml) into it, e.g. `/opt/mirrorsync/`.
2. Adjust if needed:
   - Port: `ports: - "8080:8080"` (left number = port on the Docker host, freely selectable).
   - User and password do **not** belong in the compose file. You create the first admin when you open
     the web GUI for the first time (see "First-time setup").
   - optionally local folders under `volumes` (they appear in the GUI as `/data/...`)
3. Start:
   ```bash
   cd /opt/mirrorsync
   docker compose up -d
   ```
4. Open `http://<docker-host>:8080` in your browser.

**Portainer:** simply paste the `docker-compose.yml` into the stack editor, nothing needs to be built.

### With docker run
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
Mount local folders additionally with e.g. `-v /srv/data:/data/data:ro`.

### Build it yourself
Clone the repo and replace the `image:` line in `docker-compose.yml` with `build: .` (or
`docker build -t mirrorsync .`), then run `docker compose up -d --build`.

## Users, permissions and 2FA
Users are created under **Settings → Users**, roles under **Settings → Roles**.
Three templates are included:

| Role | may |
|---|---|
| Admin | everything (fixed, cannot be changed, so nobody locks themselves out) |
| Operator | create, edit, delete and start jobs; view, test and browse storage locations |
| Read only | view jobs, status and logs |

**Custom roles** ("New role", or "Use as template" on an existing one) are made of individual permissions:

- *Jobs:* view, create, edit, delete, start/stop, dry run, logs, change the job's notifications, change
  additional rclone options, set up two-way sync (also writes to the source; without this permission you
  can edit a two-way job but not switch it on or off)
- *Storage:* view, test, browse folders, create, edit/re-authorize, remove, use local folders (`/data`)
- *File manager:* view files (browse, sizes, permissions, download), edit (upload, edit, rename, create
  folders, copy), delete (also required for moving)
- *Notifications (defaults):* view, change
- *Users and roles:* view users, manage users, manage roles, manage groups
- *System:* change general settings (log retention, default bandwidth)

In addition, every role can be limited to **selected jobs** and **selected storage locations**.
Users then only see those; jobs they created themselves are always visible to them. When creating or
editing jobs, only allowed storage locations can be used as source and destination. Nobody can create
or assign a role with more permissions than they have themselves.

### Groups and "Visible to" (since 1.22.0)
Under **Settings → Groups** (permission "Manage groups") you combine users and API keys into groups,
e.g. "Accounting" or "Home Assistant".

- **Additional permissions:** a group can grant permissions. A member has the permissions of their role plus
  those of all their groups. Example: role "Read only" plus a group with "start and stop". You can only grant
  permissions you have yourself.
- **Visible to:** for each job and storage location you set who can see it: "everyone with the matching
  permission" (default) or only selected users and groups. Whoever cannot see something cannot start or
  change it either, or pick it as the trigger of a chain or as source/destination.
- Admins always see everything, and whoever created a job sees it too. You cannot hide something from
  yourself. A role limited to specific jobs/storage locations applies in addition.
- Memberships can also be set on the user under "Groups". The group page shows which restricted jobs and
  storage locations a group can see.
- When a user or group is deleted, it disappears from all "Visible to" lists.
- Changes are recorded in the audit log, groups and visibility are part of backup and export.

Under **Settings → My account** every user sets up 2FA themselves (scan the QR code with Google/Microsoft
Authenticator, Aegis, 2FAS, Bitwarden …) and receives 10 backup codes that are shown only once.
Passwords are stored hashed in the database `config/mirrorsync.db`.

**Require 2FA** (since 1.41.0): Under **Settings → General → Sign-in and security** choose globally
*Off (per user only)*, *For new users* or *For all users*. Per user there is the **“Require 2FA”** checkbox under
**Users → Edit** (with “For new users” it is already ticked when you create a user). A user who has to set up 2FA
lands on “My account” with the QR code right after signing in and can do nothing else until the authenticator app
is set up. Afterwards only an admin can turn it off (“Reset 2FA”; the user then has to set it up again at the next
sign-in). The user list shows “Required, not set up yet”. API keys (REST, MCP) are not affected. Permissions:
`system.settings` globally, `users.manage` per user; via the API `require_2fa_mode` (`update_security_settings`)
and `require_2fa` (`create_user`, `update_user`).

- **Existing installation:** if users already exist, nothing changes. You can remove `WEB_USER`/`WEB_PASS`
  from the compose file, they are only needed for emergencies (`ADMIN_RESET`).

### First-time setup
As long as no user exists, the first visit in the browser leads straight to the first-time setup:
1. Open the web GUI, enter a user name and password → the first admin is created.
2. Optionally set up 2FA (authenticator app) and/or a passkey right away, or click "Done".

> **Caution:** until the admin has been created, anyone who can reach the web GUI can create that admin. So create
> it right after the first start. If the container is reachable from the internet before that (e.g. through a port
> forward), set `SETUP_TOKEN=true`: the container then writes a **setup code** to the log on the first start
> (`docker logs mirrorsync`, also in `config/setup_token`), and the admin cannot be created without it. Failed
> attempts are throttled and logged, the code is deleted after the setup.

If you keep setting `WEB_USER`/`WEB_PASS`, the admin is created automatically as before.

### Passkeys
Instead of a password (+ 2FA) every user can sign in with a **passkey**: fingerprint, face, device PIN,
password manager or security key (YubiKey). Set it up under **Settings → My account → Passkeys**, several
per user are possible (rename, remove). On the login page, click "Sign in with passkey", no user name needed.

- Passkeys require **HTTPS and a domain name**, e.g. `https://sync.example.com` via your reverse proxy.
  Via `http://192.168.1.50` MirrorSync does not offer passkeys and explains why: browsers only allow passkeys
  on secure HTTPS pages, and a passkey is always bound to a domain name, never to an IP.
- MirrorSync uses the address it is called with. If the proxy does not pass the host through, enter the public
  address under **Settings → General → Passkeys** (or `PUBLIC_URL=` in the compose file).
  Changing the address later makes existing passkeys unusable.
- Device lost: an admin removes the user's passkeys under "Edit". Signing in with the password always keeps
  working. Adding and removing is recorded in the audit log.
- **Phone lost:** another admin resets the 2FA under "Edit", or you sign in with a backup code.
- **Admin password forgotten:** set `ADMIN_RESET=true` in the compose file and restart the container
  (`docker compose up -d`). Password and 2FA of `WEB_USER` are then reset to `WEB_PASS`. Afterwards
  comment out `ADMIN_RESET` again and restart.

## Getting started
1. **Storage** → e.g. create an SMB share (name `nas`, server, user, password) → **Test**.
2. **New job**: source `/data/data/photos`, destination `nas:backup/photos`, pick a schedule.
3. Click **Test** first and check in the log what would be copied/deleted.
4. If everything looks right → **▶ Start** or wait for the schedule.

Path notation: local `/data/…`, remote `name:path` (for SMB: `name:share/folder`).

**Folder or only its contents?** By default it works like rsync with a trailing slash: the *contents* of the
source end up directly in the destination. With the checkbox "Copy the source folder itself" a folder with the
source's name is created in the destination. Example source `NAS:backup/OPNsense`, destination `backup-server:backups`:

| Checkbox | Result in the destination | deletions only within |
|---|---|---|
| off | `backups/config.xml …` | `backups` |
| on | `backups/OPNsense/config.xml …` | `backups/OPNsense` |

With the checkbox, other folders in the destination (e.g. `backups/Other`) stay untouched. Excludes are always
relative to the source, versions go to `backups/OPNsense.versions/…`. The form shows the result before saving.

## Folder structure preview (since 1.43.0)
In a job, the **"🗂 Preview folder structure"** button (below the destination) shows what the destination will look
like after the next run. Source and destination are only read, nothing is copied or deleted. The preview uses the
values currently in the form, so you don't have to save first.

- **"✅ Result"** (since 1.45.0, default): the destination exactly as it will look after the run, almost like the
  file browser (name, size, modified). Anything that gets deleted is no longer shown here.
- **"📂 Changes"** (since 1.44.0): the same browsable view, but with a change column, including what gets deleted,
  and **"Show changes only"**.
- **"📂 Open result in browser"** (since 1.46.0, next to the preview button and in the preview window): opens a
  page of its own in a new tab that looks like **Files** (path bar, "Up", name, size with file count, modified,
  permissions) but shows the destination **after the run** and is view-only. Deleted items are missing there; with
  "Mark changes" you also see what is new, updated or deleted.
- In both views click folders, go back via the path bar or "⬆ .." and search in the folder. **"🌳 Tree"** switches
  to the collapsible tree view, the browser remembers your choice.
- Every entry is marked: **new**, **will be updated** (different
  size or modification time), **will be deleted** (no longer in the source) or unchanged. Folders show how many
  files inside are new, updated or deleted.
- The same rules as in the real run apply: "Only these files and folders", excludes, "Copy the source folder itself"
  and "Also delete excluded items in the destination".
- For **two-way** jobs the preview shows what both sides will look like afterwards. Anything only on side B is
  marked "goes to A". Deletions since the last run are not taken into account.
- If the destination does not exist yet, this is shown at the top and everything is "new". With very many files
  (over 3000) only the first ones are listed individually, the counters are still correct.
- **Permission:** `jobs.preview` ("View and browse the folder structure preview of the destination"). Admins and the default
  Operator role have it. Custom roles already stored in the database don't get it automatically.
- **API/MCP:** `POST /api/v1/jobs/{job_id}/preview` (`preview_job`, saved job, fields can be overridden) and
  `POST /api/v1/jobs/preview` (`preview_paths`, just `source` and `dest`). The response contains `summary`
  (counters) and `text` (tree with `+` new, `~` updated, `-` deleted, `<` to side A), with `tree: true` also as JSON.
  With `path` (e.g. `Photos/2024`) a folder is opened like in the file browser (`entries` with `name`, `dir`,
  `status`, `size`, `modified`, `counts` for folders), with `only_changes: true` only entries that change, with `result: true` the outcome without deleted
  items (for `text`, `entries` and `tree`).

## Only specific files and folders
The field **Only these files and folders** holds entries relative to the source, one per line, folders ending
with `/` (e.g. `Projects/` and `report.docx`). The easiest way is to tick folders and files in the source
browser, even across several subfolders, and click "Apply". If everything is inside the current source, it stays
the base folder, otherwise the common parent folder becomes the source.

- Only the selection is checked and mirrored. In the destination, deletions happen only within the selection
  (e.g. a selected file that disappears from the source), everything else in the destination stays untouched.
- Excludes apply in addition (e.g. `*.tmp` inside a selected folder). "Also delete excluded files in the
  destination" has no effect with a selection, so nothing outside of it is deleted.
- If you enter a file directly as source (`NAS:data/f3.txt`), saving turns it into source `NAS:data` with
  selection `f3.txt`.
- Live sync, dry run and versioning work as usual. **"Copy the source folder itself" is off with a selection**
  (since 1.27.0): the selected folders and files go directly into the destination, e.g. source `NAS:share`
  with selection `10-Temp/` and destination `Family-NAS:share` gives `Family-NAS:share/10-Temp`.
- Empty field = the whole source folder.

## Excludes
One entry per line, relative to the source:

| Entry | excludes |
|---|---|
| `/Temp/` | folder `Temp` directly in the source |
| `Temp/` | every folder named `Temp`, at any depth |
| `/Projects/old/report.docx` | exactly this file |
| `*.tmp` | all `.tmp` files |
| `**/node_modules/**` | all `node_modules` folders |

Full paths (e.g. `/data/data/Temp/`) are converted automatically. By default excluded files stay in the
destination; with "Also delete excluded files in the destination" they are removed there.

## Sign-ins, lockouts and countries
- **Settings → Users** shows the last sign-in per account with IP and country, the status (active,
  disabled, locked until …) and failed attempts. "Sign-in history" lists the last 1000 attempts.
- **Edit account:** active or disabled, plus an optional lock period with "locked from" and "active again from"
  (e.g. an employee's vacation). The account is locked and unlocked automatically at that time.
- **Settings → General → Sign-in and security:** after how many failed attempts an account is locked, for how
  long (0 = until an admin unlocks it) and whether you are notified. In addition MirrorSync throttles each IP
  address for 5 minutes.
- **Country:** the container downloads the free country database from DB-IP (about 8 MB) to `config/geoip/` and
  refreshes it either **by interval** (daily, weekly, every 2 weeks, monthly = default, every 2 or 3 months)
  or **on a schedule** with a time and one or more weekdays (since 1.32.0, e.g. Mon and Thu at 04:30; DB-IP
  publishes monthly). This requires internet access to `download.db-ip.com`. Lookups are local only.
  Alternatively put your own `GeoLite2-Country.mmdb` there, or set `GEOIP=off`.
- **Behind a reverse proxy** (Nginx Proxy Manager, Traefik …) tick "Reverse proxy", otherwise the proxy's IP is
  shown everywhere. Without a proxy leave it off.
- **User names** are case-insensitive when signing in (`Max` = `max`).
- **Report failed attempts:** under "Sign-in and security" choose "on every failed attempt", "only on lockout" or
  "never", plus a throttle time (default 15 minutes). Collected failed attempts arrive bundled in one message.
- **Acknowledge or delete failed attempts:** unacknowledged ones show a red number at "Settings" and "Users".
  Acknowledge or delete them one by one or all at once in the sign-in history ("Unacknowledged").
- Locked out? `ADMIN_RESET=true` resets the admin from `WEB_USER` and lifts lockouts.

## Access by IP address and country
Under Settings → Access (permission "Manage access by IP address and country"):

- **Allow list:** only these addresses/networks/host names may connect, e.g. only the local network (button
  "Allow local network only"). Empty = everyone.
- **Block list:** single IPs, networks (`1.2.3.4`, `10.0.0.0/8`, IPv6) or host names, permanently or for 1 hour up to 30 days.
- **Host names (FQDN, since 1.32.0)** like `office.example.com` or `facebook.com` work in both lists. On each
  request MirrorSync resolves the name via DNS (IPv4 and IPv6, 5 minute cache, at most 3 seconds) and checks
  whether the address belongs to it. This allows e.g. DynDNS addresses. If a name cannot be resolved right now,
  the last known result is used. The page shows the currently resolved addresses for each name. Wildcards
  (`*.example.com`) are not supported. In the sign-in history, "Block IP" blocks an address with one click.
- **Countries:** "allow only these countries" (e.g. DE) or "block these countries". The local network is always
  exempt, addresses with an unknown country are not blocked. Requires the country database.
- **Block automatically:** block an IP after X failed attempts within Y minutes for Z minutes or permanently,
  optionally with notification. The local network can be exempted (default).
- **No self-lockout:** rules that would match your current address are not saved.
- **Emergency:** set `IPGUARD_RESET=true` in the compose file, restart, remove it again (deletes all IP and
  country rules). `IPGUARD=off` disables the protection. The block page itself does not mention this (since 1.32.0).
- **Behind a reverse proxy** (OPNsense/HAProxy, Nginx Proxy Manager …) make sure to enable "Reverse proxy" under
  General, otherwise MirrorSync only sees the proxy's IP.

## Two-way sync (since 1.31.0)
At the top of the job you choose the **type**: "Mirror (one-way): source → destination" or "Two-way sync:
side A ⇄ side B". With two-way sync (`rclone bisync`) everything that changes on one side is transferred to the
other: new and changed files, renames and deletions. So both sides are written to. There is a separate
permission "Set up two-way sync" for this.

- **First run** (and after changing side A, side B, excludes or checksum): both sides are merged (`--resync`).
  Whatever exists only on one side is copied to the other, nothing is deleted. If a file differs on both
  sides, the newer one wins. Deletions are transferred from the second run on. Tip: start the first run as a dry run.
- **Missing folder** (since 1.35.0): if the folder of side A or side B does not exist yet on the first run,
  MirrorSync creates it, just like mirroring does. If a side that existed before is missing on a later run, or is
  suddenly empty (e.g. a drive is not mounted), the run stops as a precaution without creating or deleting anything.
  The log explains what happened. Once the side is back, click "Merge again".
- **Conflict** (file changed on both sides): choose "newer wins" (default), "keep both", "side A wins" or
  "side B wins". The losing version is always kept, renamed (`file.txt.konflikt1`), on both sides.
- **Deletion protection** in percent (default 50): if more files would be deleted on one side, the run aborts
  without changes and reports an error (e.g. when a drive is not mounted). If the deletion is intended, raise
  the value temporarily. "Re-merge" (overview or job) instead reunites the sides, the missing files come back.
- **Abort:** if rclone requires a new resync after a severe error, the overview shows a notice and the button
  **"Re-merge"**. Live rounds are suspended until then.
- Excludes apply to both sides. "Delete excluded" and "Max. deletions" do not exist for two-way sync.
  Versioning keeps versions in `<side>.versions/` on both sides. One side must not be inside the other.
- **Folder selection and "Copy the source folder itself"** (since 1.33.0) work as with mirroring, also via
  checkboxes in the browse panel. The selection applies to both sides: only the selected folders and files are
  synced in both directions, everything else stays untouched on both sides. With "Copy the source folder itself",
  side B is the folder `<side B>/<name of side A>`, created on the first run. Changing the selection or the
  checkbox triggers a merge on the next run (without deleting).
- Live: every round is a two-way sync, rounds without changes stay silent.
- The state (listings of the last round) is stored in `/config/bisync/<job>`.
- API/MCP: fields `direction` (`mirror`|`bisync`), `bisync_conflict` (`newer`|`none`|`path1`|`path2`),
  `bisync_max_delete`; re-merge via `POST /api/v1/jobs/{id}/resync` or tool `resync_job`. Running jobs:
  `GET /api/v1/jobs/running` or tool `list_running_jobs`.

## Start: time, chain, live or manual
In the "Start" section of each job you choose:

- **At a time:** click the time and weekdays (e.g. Mon–Fri 03:00). Under "Advanced" a cron expression is still
  possible for "every 15 minutes", "hourly" etc.
- **After another job:** pick a job from the list and the condition "only if it succeeded" or "always, even after
  an error". This creates chains like A → B → C. No follow-up job starts after a dry run or a stop. Loops
  (A after C, C after A) are rejected when saving.
- **Continuous (live):** see below.
- **Manual only:** start only from the overview.

The **Schedules** page shows all start times in one place, in four sections: "By time" (edit time, days, active
directly), "Continuous (live)" (interval, full sync, active), "After another job" (chains below each other, order
via drag & drop or ↑ ↓, condition per job) and "Manual only". Changing the "Start type" moves a job to the
matching section immediately. It is the same setting as in the job itself.

**Next run** (since 1.33.0): the overview shows under each job's status when it will start next, e.g.
"today, 14:30", "tomorrow, 03:00" or a date. For live jobs it is the next round. For follow-up jobs the time is
estimated from the predecessor ("approx. tomorrow, 03:00", the tooltip names the predecessor); while the
predecessor is running it says "when "…" has finished". Otherwise "manual only", "paused" or "none scheduled"
(e.g. schedule off). REST API and MCP (`list_jobs`, `get_job`) return `next_start` (ISO time) and
`next_start_kind` (`time`, `live`, `after`, `parent_running`, `manual`, `paused`, `off`).

The overview shows chains indented below their starting job, with "after …" and "then: …". The log of the
previous job lists which follow-up jobs were started. When a job is deleted, its follow-up jobs are set to
"Manual only".

### Continuous (live)
True live mirroring via file system events is not possible because source and destination are remote servers.
MirrorSync comes close with rounds every N minutes (default 1, up to 1440). Per job you choose what a round does:

**Like mirroring (default, since 1.30.0):** every round is a normal mirror run (`rclone sync`). New and changed
files are copied, whatever was deleted or renamed in the source is removed from the destination too. Only what
really changed is transferred, but both sides are listed in every round. For very large sources (several
100,000 files) better choose a larger interval or "Fast". "Max. deletions per run", versioning and excludes apply
in every round. Follow-up jobs start after every round that changed something. An extra full sync is not needed here.

**Fast:** two kinds of runs:

- **Fast live runs** every N minutes (default 1, up to 1440): `rclone copy --max-age` copies only what changed
  since the last successful run (plus a 2 minute buffer) and deletes nothing. With few changes such a run takes
  only seconds, the source is still listed once.
- **Full sync** at a time of day (default daily 03:00), **by interval** (e.g. every 6 hours, in the API
  `@every 6h` or `@every 90m`, 5 minutes to 30 days) or via cron, can be switched off: a normal mirror run so
  that deletions and renames reach the destination. The first run, and the one after changing source,
  destination or excludes, is always a full sync.

Runs never overlap: if the previous one is still running, the round is skipped. Live runs without changes do
not appear in the history, their log is deleted immediately, the overview only shows "last checked". Runs that
copied files appear in the history marked "Live". An error is reported and logged once, further consecutive
errors are only counted in the overview; after the next successful run a new error is reported again.
Bandwidth, excludes and versioning apply as usual. In "Fast" mode follow-up jobs only start after the full sync.
If "dry run only" is on, live runs are skipped.

API/MCP: field `live_mode` (`mirror` or `fast`) on the job, for `set_job_trigger` it is called `mode`.

Limitation: files that arrive in the source with an old modification date (e.g. moved or extracted from an
archive) are only detected by the full sync.

## Apprise
Under Settings → Notifications there is the **Apprise** channel, which sends messages to everything
[Apprise](https://github.com/caronc/apprise/wiki) supports (Discord, ntfy, Pushover, Gotify, Signal, Matrix, Teams …).

- **Directly from MirrorSync:** enter Apprise URLs, one per line, e.g. `ntfy://ntfy.sh/my-topic` or
  `discord://webhook_id/webhook_token`. The Apprise library is included in the image.
- **Via an Apprise API server** (e.g. container `caronc/apprise`): enter its address, e.g.
  `http://192.168.1.20:8000`. With a configuration key MirrorSync uses the targets stored there
  (`/notify/<key>`, optionally with a tag), without a key it sends the entered URLs along (`/notify`).

In every job Apprise can be enabled or disabled under "Custom notification", with its own URLs or tag. Apprise
is also used for messages about failed sign-ins and IP blocks. URLs and key are only shown masked after saving
(`discord://•••`) and are never written to the audit log.

## Custom notification texts
Under Settings → Notifications, card "Notification texts", subject and text can be customized for each event:
run succeeded, run failed or stopped, failed sign-ins, account locked, IP blocked and test message. The text is
used for all channels (email subject and body, Telegram, Apprise, webhook field `message`).

- Variables like `{job}`, `{status}`, `{status_icon}`, `{quelle}` (source), `{ziel}` (destination), `{start}`,
  `{ende}` (end), `{dauer}` (duration), `{kopiert}` (copied), `{geloescht}` (deleted), `{fehler}` (errors),
  `{fehler_liste}` (error list), `{gestartet_von}` (started by), `{art}` (type), for sign-ins `{benutzer}` (user),
  `{ip}`, `{land}` (country), `{flagge}` (flag), `{anzahl}` (count), `{liste}` (list), and everywhere `{datum}`
  (date), `{zeit}` (time), `{version}` and in the body `{titel}` (title). Click a variable to insert it at the cursor.
- The preview shows the text immediately with sample data.
- "Reset to default" restores the built-in text. Unchanged texts are not stored, so improvements to the default
  text arrive automatically with updates.
- Unknown variables are left as they are, `{{` and `}}` produce curly braces.

In every job, "Custom texts for this job" under Notifications can define its own texts for "run succeeded" and
"run failed". The job's test button sends the success text with sample numbers.

For the **webhook** the whole JSON body can also be defined as a template, with presets for Discord,
Slack/Mattermost, Gotify and Home Assistant/n8n. Values are inserted JSON-safe, texts belong in quotes
(`"text": "{nachricht}"`), numbers may go without (`"copied": {kopiert}`). The preview checks whether valid JSON
results. Invalid templates are not saved. If a template does not fit an event, the default JSON is sent.

## Collapsible sidebar (since 1.33.0)
The arrow at the top of the sidebar (next to "MirrorSync") collapses it to a narrow bar with icons only, the
content then uses the full width. Hovering an icon shows its name. Clicking the arrow expands it again. The
setting is per user and stored in the account, so it applies on all devices and after reloading. No extra
permission is needed. Admins with "Manage users" can set it via REST API or MCP:
`PATCH /api/v1/users/{name}` or `update_user` with `"sidebar": "mini"` or `"full"`; `get_user` and `list_users`
show it as `sidebar`. On phones the bar at the top stays as before.

## File browser
In the job form, **Browse** next to source or destination opens a browser panel on the right. On wide screens
it sits next to the form, otherwise above it, on phones across the full width.

- First pick the storage location (or `/data`), then click through the folders. SFTP and FTP start at `/`.
- Folders and files with size and modification date, clickable path bar, ".." for one level up, sorting by
  clicking the column headers, search within the current folder.
- **Apply** puts the current folder into the field. For the source, ☑ marks individual files or folders and the
  button then applies the selection (see "Only specific files and folders"). Esc or ✕ closes the panel.
- **Excludes:** "Exclude folders or files from the source" opens the same browser in the source. ⛔ next to a
  folder or file adds it as an exclude (`/folder/` or `/folder/file.txt`), a second click removes it again.
  Excluded items are struck through.

The browser is read-only. It requires the permission "Storage: browse folders", restricted roles only see
their storage locations.

## File manager
Under **Files** in the sidebar (permission "File manager: view files") you pick a storage location (or `/data`)
at the top left. With **"Two storage locations side by side"** a second one is added on the right.

- **Browse:** click folders, path bar at the top, "Up". SFTP and FTP start at `/`. The columns show size,
  modification time and **permissions** (`rwxr-xr-x`, if the storage type provides them: local and SFTP yes,
  SMB, WebDAV and clouds no, then "–" is shown). **Folder sizes** calculates size and number of subfolders
  and files for all folders in the view, "calculate" for a single one.
- **Layout:** with one storage location it takes the full width, with two each takes half. The lists reach
  down to the bottom of the window and scroll on their own.
- **Right-click** on an entry opens a context menu with all actions, for several marked entries for all of them.
  Right-click on empty space offers New folder, New file, Upload, Reload, Folder sizes and Select all.
- **⋯ on every row:** properties (size, time, permissions, owner uid:gid), edit (text files up to 1 MB in the
  editor), download, rename, copy to …, move to …, delete.
- **Top:** new folder, new file, upload (multiple files). Mark several entries with ☑, then copy, move or
  delete them all.
- **Drag & drop:** dragging files and whole folders from your computer into a list uploads them (dropped on a
  folder: into that folder). Dragging rows to the other side copies them, holding Shift moves them. Dropped on
  a folder of the same side they are moved there. You are asked first, for existing files once "overwrite all
  or skip".
- **Between two storage locations:** "Copy to the right →" or "← Move to the left" uses the folder currently
  open on the other side as destination. Copying and moving run as a **background task** with progress. The
  **"Tasks"** button at the top right (on every page) shows how many are running. Clicking it opens a floating
  window. At the top it shows **currently running jobs** (mirror, two-way, live) with percentage, bar, link to
  the log and stop button; they count towards the number and disappear once finished (since 1.31.0, permission
  "View jobs"). Below are all file manager tasks: status, percentage and bar (blue = running, green = done,
  red = error). Running tasks can be cancelled, finished ones removed individually or with "Remove all
  finished". Clicking outside or Esc closes it. You can leave the page meanwhile.
- **Confirmations:** deleting always asks. If a file or folder with that name already exists in the destination,
  MirrorSync asks before overwriting (when uploading, creating, copying, moving).
- **Permissions:** "view" (browse, sizes, permissions, download), "edit" (upload, edit, rename, create folders,
  copy), "delete" (also required for moving). The role's restrictions and the storage locations' "Visible to"
  apply, `/data` only with "use local folders".
- Every change and every download is recorded in the audit log (category "Files").
- API/MCP: `list_file_locations`, `list_files`, `file_size`, `file_info`, `read_file`, `write_file`,
  `upload_file`, `download_file`, `create_folder`, `rename_file`, `delete_files` (with `confirm=true`),
  `copy_files`, `move_files` (with `overwrite=true` on conflict), `list_file_tasks`, `cancel_file_task`,
  `delete_file_task`, `clear_file_tasks`.

## Pausing jobs
In the overview every job has a **Pause** button (the menu closes when clicking outside or with Esc): until I
resume, 1 hour, 24 hours, 1 week or until a date and time. A paused job is marked in the overview and schedules
("paused until …"), does not start by schedule, live or in a chain, and resumes normally by itself when the time
is up (checked every minute). Starting it manually still works. "Resume" ends the pause immediately.

The same can be set in the job under "Start", plus what happens in a **chain** when the paused job's turn comes:
- **skip** (default): the job does not run, its follow-up jobs still start.
- **stop chain:** the job and everything after it does not run.

The log of the previous job notes what happened. Pausing, resuming and the automatic end of a pause are
recorded in the audit log. The permission for this is "Jobs: edit".

## Audit log
The **Audit log** page (permission "System: view and export audit log", admins always have it) shows who did
what and when:

- creating, changing and deleting jobs, schedules, storage locations, users, roles, settings and access rules,
  each with before/after values of the changed fields
- manual starts, dry runs and stops, connection tests, unlocks
- sign-ins (also failed ones), sign-outs, automatic IP blocks, `ADMIN_RESET` and `IPGUARD_RESET`
- user, IP address and country for every entry

**Details (since 1.32.0):** clicking an entry opens a window with everything known about it: who, when, from
which IP and country, through which channel (web GUI with browser, REST API or MCP, with request), every changed
field with full old and new value, for lists and multi-line fields (excludes, selection, allow/block list,
permissions, members …) individually "+ added" and "− removed". On create and delete the whole content is shown.
In the file manager: path, size, modification date, for folders the contained files (up to 200), when editing a
text file the changed lines (excerpt, values of lines like `password=` or `token:` are masked), for copy/move
from, to and statistics. For starts the source, destination and run number. Old entries show what was stored at
the time. The API returns the same fields (`changes[].added/removed/old_full/new_full`, `info`).

Passwords, tokens, 2FA secrets and other secrets never end up in the log, only the note "changed". Filter by
area, user and time range, full-text search (also in old and new values), export as CSV (for Excel, separated
by `;`) with the same filters. Stored in `config/audit.jsonl`, retention under Settings → General (default
365 days, at most 20,000 entries).

## Bandwidth
Under Settings → General you set the default bandwidth, in every job it can be overridden under "Bandwidth"
("Use default", "Custom limits", "Always unlimited").

- **Outside the time windows:** limit that applies when no time window matches (empty = unlimited).
- **Unit:** MB/s (megabytes per second, default) or Mbit/s (megabits per second, as for internet connections),
  selectable with the default bandwidth; applies to all displays. 1 MB/s = 8 Mbit/s. Values are always stored
  in MB/s, switching converts the fields.
- **Time windows:** weekdays, from–to, upload and download. Example: Mon–Fri 08:00–18:00 10 MB/s, otherwise
  unlimited. Windows like 22:00–06:00 span midnight; if windows overlap, the lower one wins.
- Upload = to the destination, download = from the source. As a relay (A → B) one value is usually enough,
  because everything from A is passed straight to B.
- The limits switch at the configured time even during a running mirror (time zone from `TZ`).
- Internally this becomes an rclone timetable (`--bwlimit "Mon-08:00,10M Mon-18:00,off …"`), visible in the log.
  Your own `--bwlimit` in the additional rclone options takes precedence.

## Logs
Every run gets its own log under `logs/<job>/<date-time>.log`. "Log" on a job shows the last run and the history
with the number of copied, deleted and failed files. Clicking a run opens its full log:

- Filter: all, errors, copied, deleted (also "moved to versioning"), notices
- Search for file or folder names, combinable with the filter
- "Download" saves the complete log as a text file
- A running run refreshes every 3 seconds

Retention under Settings → General → Keep logs:
- **Runs per job** (default 50, 0 = unlimited).
- **At most this long** as a number of days, weeks or months (default 30 days, 0 = unlimited, a month = 30 days).

If both limits are set, whichever applies first wins. The newest run is always kept. API/MCP:
`PATCH /api/v1/settings/logs` (`update_log_settings`) with `log_keep_runs` and `log_keep_days` (in days).

**Delete old logs** (since 1.39.0, same page): pick a date, click "Show count", then confirm "Delete permanently
now". All runs started before that date are deleted once, together with their log. Running jobs are not affected,
the retention settings do not change, and the audit log records the deletion.
API/MCP: `POST /api/v1/logs/purge` (`purge_logs`) with `before` (`YYYY-MM-DD`); `dry_run: true` only counts.

## API keys, REST API and MCP
Under **Settings → API** you create API keys (permission "Manage API keys", admins have it):

- **Name** (e.g. n8n, Home Assistant, Claude) and **role**. The key has exactly the permissions and restrictions
  of that role (jobs, storage locations), like a user. For a key with few permissions, create a custom role
  under Roles, e.g. only "View jobs" and "Start". You can only assign roles whose permissions you have yourself.
- Optional **expiry date** and **allowed IP addresses** (single IPs or networks like `192.168.1.0/24`).
- The key (`msk_…`) is shown after creating it. Since 1.24.0 you can view it again later with **"Show"**, after
  entering your own password (plus 2FA code, if set up) or with a passkey. This only works in the web GUI, not via
  API or MCP, and is recorded in the audit log ("API key shown"). For this it is stored encrypted (key from
  `config/secret_key`). **Keys from before 1.24.0 cannot be shown afterwards**, only their SHA-256 hash exists;
  create a new one if needed. The same applies after an import without the old `secret_key`. The list shows
  "last used" with IP.
- **Edit**: name, role (permissions), expiry date, IPs, groups as well as **active/disabled**, a **pause**
  from–to and **time windows** per weekday (e.g. Mon–Fri 08:00–18:00, spanning midnight works too). Outside of
  them the key is rejected, the list shows the status. The key currently in use cannot be disabled or have its
  role changed. API `PATCH /api-keys/{id}`, MCP `update_api_key`.
- **Revoke** blocks it permanently, but it stays in the list. **Remove** deletes it completely (also from
  groups), audit log entries remain. The key you are currently using via the API cannot be deleted.
  API: `POST /api-keys/{id}/revoke` or `DELETE /api-keys/{id}`, MCP: `revoke_api_key` or `delete_api_key`.
- Everything a key does is recorded in the audit log as user `API:<name>` (button "Audit" in the list).
  Failed attempts count like wrong passwords (IP throttling, sign-in history), IP and country rules apply to
  the API too, at most 300 requests per minute and key.

### REST API
Base `https://sync.example.com/api/v1`, authentication with `Authorization: Bearer <key>`. Interactive
documentation is at **`/api/docs`** (Swagger UI, with GUI sign-in or via "Authorize" with a key), the
specification at `/api/v1/openapi.json`. The links under Settings → API open a new tab.

| Method and path | Purpose | Permission |
|---|---|---|
| `GET /status` | version, running, failed, paused jobs, permissions of the key | – |
| `GET /jobs`, `GET /jobs/{id}` | jobs with status and next start | jobs.view |
| `POST /jobs`, `PATCH /jobs/{id}`, `DELETE /jobs/{id}` | create, change (only given fields), delete | jobs.create / edit / delete |
| `POST /jobs/{id}/run` (`?dry_run=true`), `/stop` | start, dry run, stop | jobs.run / jobs.dryrun |
| `POST /jobs/{id}/pause` (`?hours=2` or `?until=…`), `/resume` | pause, resume | jobs.edit |
| `GET /jobs/{id}/history`, `GET /jobs/{id}/log` (`?filter=error&q=…`) | history, log of a run | jobs.logs |
| `GET /remotes`, `GET /browse?path=NAS:data` | storage locations (without credentials), folders | remotes.view / browse |
| `GET /schedules`, `GET /audit`, `GET /users` | schedules, audit log, users | jobs.view / system.audit / users.view |

```bash
KEY=msk_xxxxxxxx_xxxxxxxxxxxxxxxxxxxx
curl -H "Authorization: Bearer $KEY" https://sync.example.com/api/v1/status
curl -H "Authorization: Bearer $KEY" https://sync.example.com/api/v1/jobs
curl -X POST -H "Authorization: Bearer $KEY" "https://sync.example.com/api/v1/jobs/<id>/run?dry_run=true"
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
     -d '{"name":"Photos","source":"NAS:photos","dest":"Server:/backup/photos","trigger":"time","schedule":"0 3 * * *"}' \
     https://sync.example.com/api/v1/jobs
curl -X PATCH -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
     -d '{"versioning":true,"excludes":["*.tmp"]}' https://sync.example.com/api/v1/jobs/<id>
```
Errors come as `{"error": "…"}` with a matching status (400, 401, 403, 404, 409, 429).

**Everything in the GUI also works via API and MCP** (since 1.21.0): besides jobs there are endpoints for
schedules and chains, storage locations (create with wizard questions, change, test, re-authorize, delete),
notifications and templates (since 1.41.0 also creating channels: `setup_notification_channel` or
`POST /settings/notifications/channels/{webhook|smtp|telegram|apprise}` with fields such as `url`, `host`, `token`,
`chat_id`, `add_urls` and optionally `test: true`; turn one off with `remove_notification_channel`, permission
`notify.edit`), general settings (logs, security, country database, language, bandwidth with
unit), access by IP and country, groups, visibility (`visible_to` on jobs and storage locations, `groups` on
users), users (create, change, lock, unlock, reset 2FA and passkeys, delete), sign-in history, roles, API keys,
as well as backup, export, import and restore. The full list is in `/api/docs`.
- Every action runs internally through the same function as in the GUI: same checks, same permissions (role of
  the key), same safeguards (e.g. there is always one active admin, you cannot lock yourself out) and an audit
  log entry as `API:<name>`.
- Passwords, tokens and other secrets can only be written, never read (response e.g. `"token_set": true`).
- Backup, export, import and restore only with the admin role. Import shows a preview first and only applies
  with `confirm=true`.
- Not via key: your own password, your own 2FA and passkeys (those stay with the account under "My account").
- Language of responses (messages, Swagger texts, MCP tool descriptions): `?lang=en|de|es|it|fr`, otherwise
  `Accept-Language`, otherwise the key's setting **"Language of API responses"**. Its default is "Same as user":
  the language of the user who created the key (My account → Language). If no user is known (e.g. deleted or
  never signed in), the API answers in English. Via API/MCP: field `lang` on `create_api_key`/`update_api_key`.

**n8n:** HTTP Request node with "Header Auth" (`Authorization` = `Bearer msk_…`). **Home Assistant:**
`rest_command` or `rest` sensor with the same header, e.g. `POST …/jobs/<id>/run`.

### MCP server
`https://sync.example.com/mcp` (Streamable HTTP, JSON responses, stateless), authentication with the same header.
Tools: `status`, `list_jobs`, `get_job`, `job_history`, `job_log`, `run_job`, `stop_job`, `pause_job`,
`resume_job`, `create_job`, `update_job`, `delete_job`, `list_remotes`, `browse`, `list_schedules`, `audit_log`,
`list_users`, plus all tools for the other areas (see above, same names as in `/api/docs`, e.g. `create_remote`,
`update_user`, `set_bandwidth`, `update_security_settings`). The client only sees the tools the key has the
permission for; a "Read only" key therefore gets no writing tools.

Example for clients with JSON configuration (Claude Desktop, Cursor, VS Code and others; depending on the client
the key is called `mcpServers` or `servers`):
```json
{
  "mcpServers": {
    "mirrorsync": {
      "type": "http",
      "url": "https://sync.example.com/mcp",
      "headers": { "Authorization": "Bearer msk_xxxxxxxx_xxxxxxxxxxxxxxxxxxxx" }
    }
  }
}
```
Claude Code: `claude mcp add --transport http mirrorsync https://sync.example.com/mcp --header "Authorization: Bearer msk_…"`.
Clients that only support local (stdio) servers can connect via `npx mcp-remote https://sync.example.com/mcp --header "Authorization: Bearer msk_…"`.

## Database, export and import
Since 1.18.0 jobs, history, settings, templates, users (with 2FA and passkeys), roles, IP rules, sign-in
history and audit log are stored in an SQLite file `config/mirrorsync.db`. `rclone.conf` stays a separate file.

- **Migration:** on the first start of 1.18.0 MirrorSync imports all old JSON files automatically in one step
  (all or nothing). Afterwards they remain unchanged in `config/json-backup/`. If the import is aborted,
  everything stays as it was and the next start tries again. If a file is broken, the container does not start
  and names the file in the log instead of starting with empty data. To go back to a version before 1.18.0,
  move the files from `config/json-backup/` back to `config/`.
- **Export** (Settings → Backup, admins only): downloads everything as a ZIP, i.e. database content,
  `rclone.conf`, SSH keys and other own files from `config/`, optionally the run logs. The file contains
  secrets, so optionally encrypt it with a password (AES-256-GCM, file `.zip.enc`).
- **Import:** upload the file, MirrorSync checks it and shows version, date and content compared to the current
  state. Files from a newer version are rejected. Only after confirmation is anything replaced; before that
  MirrorSync automatically creates a backup in `config/backups/` (the last 10 are kept and can be downloaded
  there). No import is possible while jobs are running.
- Export, import and backup downloads are recorded in the audit log.

### Automatic backup
Settings → Backup → **Automatic backup**:

- **Schedule** as a cron expression with presets (daily 3:00, every 6 hours, hourly, Sundays, monthly).
- **Only on change:** before each backup MirrorSync computes a checksum over jobs, storage locations, users,
  roles, settings, templates, IP rules, API keys and the files in `config/`. If it is the same as for the last
  backup (and that file still exists), **no new file** is created. History, last sign-in, failed attempt
  counters, sign-in history and audit log do not count as changes.
- **Destination:** default `config/backups/`. For a copy outside the config folder mount a folder of your own,
  e.g. `- /mnt/nas/mirrorsync-backup:/backups`, and enter `/backups` as destination.
- **Retention:** number and/or at most N days, the newest is always kept.
- **Password** (optional, at least 8 characters): the files are encrypted like an export (`.zip.enc`). The
  password is stored so that "Restore…" can open these files directly.
- **Notification:** never, only on failure, or on success and failure, optionally also "nothing changed";
  channels freely selectable (empty = all active). Subject and text under Notifications → Templates
  (events "Automatic backup created / nothing changed / failed").
- **Back up now** (optionally "even without changes"), list of all stored backups with download, restore (shows
  the same check as an import first) and delete. Everything is recorded in the audit log.

## Languages
The interface, error messages, API and MCP texts and the default notification templates are available in
**English, German, Spanish, Italian and French**.

- **During setup** the system language is chosen (preselected: English). Existing installations keep German
  after the update.
- Change the **system language**: Settings → General → Language. It applies to the login page, notifications
  and all users without their own choice.
- **Own language:** every user under **My account** → Language.
- **API and MCP** respond in the language from `?lang=xx` or the `Accept-Language` header, otherwise in the
  key's language (default: same as the user it belongs to), otherwise in English.
- Self-written texts (names, custom templates) and run logs stay as they are.

**Add another language:** copy `app/i18n/en.json`, e.g. to `app/i18n/nl.json`, add
`"_meta": {"name": "Nederlands", "code": "nl"}` at the top and translate the values (the keys on the left are
the original German text and stay unchanged). Placeholders like `{0}`, `{job}`, HTML tags and `{{ … }}` must be
kept. Missing entries fall back to English. Then rebuild the image, the language appears automatically in all
selection lists. Pull requests with new languages are welcome.

## New version notice (since 1.34.0)
Regularly (by default once an hour) MirrorSync asks GitHub (`api.github.com`, repository `DerMilderJoghurt/mirrorsync`) whether a newer
version exists. If so, the bottom left shows "⬆ vX.Y.Z available" below the version number; clicking it opens the
release with all changes. Only the installed version number is sent.

- Turn it on or off under **Settings → General → Updates**, which also has "Save and check now" and shows when the
  last check happened. You also set the **interval** there: enter a number and pick minutes or hours (5 minutes to
  720 hours, default 1 hour). Nothing is updated automatically unless you use the self-update (see below).
- API/MCP: `GET /api/v1/update` (`get_update`), `POST /api/v1/update/check` (`check_update`),
  `PATCH /api/v1/settings/update` with `{"update_check": false}` and/or `{"update_interval": 120}` (minutes)
  (`update_update_settings`); `/status` contains `update` with `interval_minutes`.
- **Notification for a new version** (since 1.46.0): under Settings → General → Updates tick "Send a notification
  when a new version is available" and optionally pick channels (none = all enabled ones). Exactly one message per
  new version. Change the text under Notifications → Notification texts ("New MirrorSync version available",
  variables `{neu}`, `{url}`, `{veroeffentlicht}`). API/MCP: `update_notify` and `update_notify_channels` in
  `update_update_settings`.
- Another repository (e.g. your own fork) can be set with `UPDATE_REPO=owner/repo`.

## Self-update via the Docker socket (since 1.42.0, optional)
MirrorSync can update itself if you mount the Docker socket into the container:

```yaml
    volumes:
      - ./config:/config
      - ./logs:/logs
      - /var/run/docker.sock:/var/run/docker.sock   # optional: self-update
```

> **Security:** whoever has the Docker socket has full control over all containers on the host (effectively root).
> Only mount it if you want that, and give the permission "Update MirrorSync" to admins only. Without the socket
> the feature is off and you update as before (Dockhand, Portainer, `docker compose pull && docker compose up -d`).

- **Update now:** at the bottom left next to "⬆ vX.Y.Z available" and under **Settings → General → Self-update**.
  Optionally **automatically once a day** from a set time. If a job is running, the update waits until it has
  finished.
- **How it works:** MirrorSync pulls the image again (same name and tag as the running container, e.g. `:latest`).
  If it is newer, a short-lived helper container from the new image stops the old container, creates a new one with
  **exactly the same settings** (name, ports, volumes, environment variables, networks with fixed IP and MAC address,
  restart policy, labels) and starts it. Docker Compose labels are kept and updated, so `docker compose`, Dockhand
  and Portainer still recognise the container as theirs and do not recreate it again. Environment variables that
  come from the image (e.g. the Python version) come from the new image, everything from your compose file stays.
- **Rollback:** if the new version does not answer `/health` within 2 minutes or exits, it is removed and the
  previous one runs again. Result and steps are shown in the GUI, in the audit log ("Update started / completed /
  failed") and in `config/selfupdate.json`.
- **Requirements:** the image has to come from a registry (`image: ghcr.io/dermilderjoghurt/mirrorsync:latest`).
  MirrorSync cannot pull images built with `build: .`. With a fixed version tag (`:1.46.0`) only that tag is pulled
  again. `/config` has to be a volume or bind mount (it is in the example compose file).
- **Permission:** `system.update` ("Update MirrorSync", admins have it automatically). Changing the automatic
  update and its time needs `system.settings`.
- **API/MCP:** `GET /api/v1/update/self` (`get_self_update`), `POST /api/v1/update/apply` (`self_update`),
  `PATCH /api/v1/settings/update` with `selfupdate_auto` and `selfupdate_time` (`update_update_settings`).

## Android app (since 1.40.0)
The folder `android/` contains a small Android app (Android 7 or newer): the MirrorSync web interface without
browser bar, with its own icon and notifications. Because it shows the normal web interface, every new
MirrorSync feature is available in the app immediately.

- **Install:** download `mirrorsync-<version>.apk` from the [latest release](https://github.com/DerMilderJoghurt/mirrorsync/releases/latest)
  on the phone and open it (allow "Install unknown apps" for the browser or file manager once).
  Updates: install the newer APK over the old one, settings and login stay.
- **First start:** enter the address you also use in the browser, e.g. `https://sync.example.com` or
  `http://192.168.1.50:8080`. Change it later via the back button on the start page, the error screen or a long
  press on the app icon → "Server & notifications".
- **Passkeys** in the app need HTTPS with a domain name (as in the browser), a current "Android System WebView"
  and Google Play services. Android checks `https://<your domain>/.well-known/assetlinks.json`, which MirrorSync
  serves by itself. Google fetches this file from the internet, so it has to be reachable from outside (reverse
  proxy, no geo-blocking for this path). Passkeys created in the browser work in the app and vice versa.
  If it does not work, password + 2FA always do.
- **Notifications:** on by default for failed runs, optionally also for successful and cancelled runs. The app
  asks `GET /api/v1/jobs` in the background (every 15 min to 6 h, Android may delay it a bit). It uses the login of
  the app; tick "Stay signed in" when logging in. More robust: enter an API key with a role that may view jobs.
- **Build it yourself:** `cd android && ./gradlew assembleRelease` (JDK 17, Android SDK). The workflow
  `.github/workflows/android.yml` builds it on GitHub. To sign with your own key, set the repository secrets
  `ANDROID_KEYSTORE_B64` (base64 of the `.jks`) and `ANDROID_KEYSTORE_PASSWORD`, and add the key's SHA-256
  fingerprint to the server via `MIRRORSYNC_ANDROID_CERTS=AB:CD:…` so passkeys keep working.

## Updating to a new version
```bash
docker compose pull && docker compose up -d
```
With `docker run`: `docker pull ghcr.io/dermilderjoghurt/mirrorsync:latest`, remove the container and start it
again with the same command. `config/` and `logs/` are kept. The running version is shown at the bottom of the
GUI and under `/health`.

## Notes
- **Mirroring deletes in the destination.** Never point the destination at a folder with other important data.
- The deletion protection (default 500) aborts after N deletions. Whatever was deleted up to then is gone,
  unless versioning is on. Turn on versioning for important data.
- SSH key instead of password: put the key into `./config/` and enter `/config/id_ed25519` in the SFTP storage location.
- Services with browser login (OneDrive, Google Drive, Dropbox, pCloud …): after creating the storage location
  the GUI shows the command `rclone authorize "<service>"`. Run it once on a PC with a browser (extract rclone
  from rclone.org/downloads), sign in and paste the printed token into the GUI. Restart aborted or expired
  sign-ins with the "Sign in" button.
- crypt: first create the actual storage location (e.g. `nas`), then a crypt storage location with
  `remote = nas:encrypted` and a password. Use the crypt name as destination in the job.
- When editing, leave password fields empty to keep the stored password.
- Data lives in `./config` (database `mirrorsync.db`, storage locations `rclone.conf`) and `./logs` (run logs).
- Run the GUI only in your home network or behind a reverse proxy with HTTPS.
- The image contains only Alpine Linux with Python 3.15, rclone 1.76 and a few Python packages
  (`app/requirements.txt`), no PHP and no Node.js. On GitHub, Dependabot checks for new versions every week and
  Trivy scans every image for known vulnerabilities (results under "Security" in the repository).

## License
[MIT](LICENSE)
