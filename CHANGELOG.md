# Changelog

Version numbers follow [SemVer](https://semver.org/): MAJOR.MINOR.PATCH
(MAJOR = incompatible change, MINOR = new feature, PATCH = bug fix).

## 1.50.0 – 2026-11-23
- **Tasks window stays open.** While a job was running, the overview (and a job's pages and its live log) reloaded
  every 3 seconds and closed the "Tasks" window at the top right. Reloading now pauses while that window, a menu or
  a dialog is open or text is selected. The window also stays open when switching pages until you close it (✕,
  click outside or Esc).
- **How a change is detected, per job:** size and modification time (default), size only, checksum, or modification
  time with a tolerance in seconds (e.g. 2 for FAT/exFAT, 3600 after a daylight saving change). Replaces the
  "compare by checksum" checkbox (carried over). The preview uses the same setting.
- **Speed per job:** Gentle (2 parallel), Normal (4), Fast (8, with `--fast-list`), Very fast (16). For the file
  manager under Settings → General → File manager. There is deliberately no separate index database, because it
  only speeds up the comparison and could miss changes when outdated.
- API/MCP: `compare`, `compare_window`, `speed` on jobs (`checksum` stays as a deprecated switch), `compare` for
  `preview_job`, new `update_files_settings` and `files.speed` in `get_settings`. Permissions: like the other
  options (`jobs.edit`), file manager speed with `system.settings`. The audit log names the new fields. All 5
  languages.

## 1.49.0 – 2026-11-23
- **Files: overall progress for copy and move.** While a transfer runs, a card above the lists shows the progress
  across all entries: percent and bar, bytes "x of y", files "x of y", speed, time left and the current entry
  ("Entry 2 of 5"). The total size is determined first, until then it says "Determining total size …". With
  several transfers there is an extra "Total" row. The tasks window shows the same details. Before, the percentage
  only counted per entry.
- API/MCP `list_file_tasks` now returns `bytes_done`, `bytes_total`, `files_done`, `files_total`, `speed`, `eta`,
  `item`, `items` and `current`; `progress` is now the overall value. Permissions unchanged (`files.view` to view,
  `files.edit` or `files.delete` for transfers). All 5 languages.

## 1.48.0 – 2026-11-23
- **Test storage location: SFTP and FTP show the root folder.** "Test" now lists the folders in `/` for SFTP and FTP
  instead of the user's home folder (for `root` that only showed `.local` and `.ssh`). The message names the listed
  path. Paths in jobs stay unchanged. API/MCP `test_remote` returns the same. Permission `remotes.test` as before.
  All 5 languages.

## 1.47.0 – 2026-11-23
- **Preview: "Up" to the root folder.** In all preview browsers ("Result" and "Changes" window and the "Result in
  browser" page), "Up" or "⬆ .." now goes beyond the destination up to the root folder of the storage location.
  There you see the real folders as they are now; the way to the destination is marked ("→ to destination",
  "🎯 Job destination", folders that don't exist yet "will be created"), clicking leads back into the preview. Also
  needs the permission `remotes.browse`. API/MCP: `path` with `../` in `preview_job` and `preview_paths`
  (`status: outside`, `target: way/dest`).
- **Updates: "Save" and "Check now" separated.** "Save and check now" is gone; "Check now" checks right away without
  saving your input and sends the notification for a new version (if turned on). API/MCP `check_update` does the
  same and also returns `message`. Permission `system.settings`. All 5 languages.

## 1.46.0 – 2026-11-23
- **Open result in browser:** New button next to "Preview folder structure" (and in the preview window). It opens a
  page in a new tab that looks like **Files** (path bar, "Up", name, size with file count, modified, permissions)
  but shows the destination after the run, read-only. Anything that gets deleted is missing. "Mark changes" also
  shows new, will be updated and will be deleted. Permission `jobs.preview`.
- **Notification for a new version:** Under Settings → General → Updates you can turn on a message as soon as a new
  MirrorSync version is available, exactly once per version, optionally only via certain channels. Custom text
  under "Notification texts" (event "New MirrorSync version available"). API/MCP: `update_notify`,
  `update_notify_channels` in `update_update_settings`, `get_update` returns `notify`, `notify_channels`,
  `notified`. Permission `system.settings`, audit log and all 5 languages updated.

## 1.45.0 – 2026-11-23
- **Preview "✅ Result":** shows the destination exactly as it will look after the run, almost like the file
  browser (browsable folders, name, size, modified). Anything that gets deleted is no longer shown there. This is
  now the default view. The view with all markers is called "📂 Changes", the tree stays. API/MCP: `preview_job` and
  `preview_paths` with `result: true` (text, entries and tree without deleted items). Permission `jobs.preview` as
  before. All 5 languages.

## 1.44.0 – 2026-11-23
- **Browse the preview like in the file browser.** The folder structure preview now opens a view like the file
  browser: click folders, path bar and "⬆ .." to go back, columns name, change (new, will be updated, will be
  deleted, goes to A, with counters on folders), size and modified, search in the folder and "Show changes only".
  The previous tree view is still available via "🌳 Tree". API/MCP: `preview_job` and `preview_paths` can open a
  folder with `path` (`entries`) and return only changes with `only_changes`. Permission `jobs.preview` is now
  labelled "… view and browse". All 5 languages.

## 1.43.0 – 2026-11-23
- **Folder structure preview.** In a job, the new "🗂 Preview folder structure" button shows what the destination
  will look like after the next run: collapsible folder tree, every entry marked as new, will be updated, will be
  deleted or unchanged, with counters on folders. Uses the values in the form (even unsaved) and the same rules as
  the real run (selection, excludes, copy source folder itself, two-way). Copies and deletes nothing. New permission
  `jobs.preview` (admins and Operator), API/MCP `preview_job` and `preview_paths`, all 5 languages.

## 1.42.0 – 2026-11-23
- **Self-update via the Docker socket (optional).** If `/var/run/docker.sock` is mounted, there is an **"Update now"**
  button at the bottom left next to the update notice and under Settings → General → Self-update, optionally also
  **automatically once a day** from a set time. A short-lived helper container swaps the container for a new one
  with **identical settings** (name, ports, volumes, environment variables, networks with fixed IP/MAC, restart
  policy, labels incl. Docker Compose, so Compose, Dockhand and Portainer still recognise it). If the new version
  does not start, the old one runs again automatically (rollback). Without the socket everything is off. New
  permission `system.update`, audit entries "Update started / completed / failed", API/MCP `get_self_update`,
  `self_update`, `selfupdate_auto`/`selfupdate_time` in `update_update_settings`, all 5 languages. Security note in
  the README and compose file.
- `docker stop` now ends MirrorSync cleanly right away instead of killing it after 10 seconds.

## 1.41.0 – 2026-11-23
- **Require 2FA**, globally and per user. Under Settings → General → Sign-in and security: *Off (per user only)*,
  *For new users* or *For all users*. Under Users → Edit the “Require 2FA” checkbox. Affected users land on
  “My account” with the QR code after signing in and can do nothing else until 2FA is set up; afterwards only an
  admin can turn it off. The user list shows “Required, not set up yet”. API/MCP: `require_2fa_mode` in
  `update_security_settings`, `require_2fa` in `create_user`/`update_user`; `get_user` returns `require_2fa`,
  `must_2fa`, `totp_setup_pending`. Permissions: `system.settings` and `users.manage`. Audit log and all 5 languages
  updated.
- **Create notifications via the API and MCP:** new actions `setup_notification_channel`
  (`POST /api/v1/settings/notifications/channels/{channel}`, channels webhook, smtp, telegram, apprise with
  readable fields, append Apprise URLs with `add_urls`, optionally `test: true` right away) and
  `remove_notification_channel` (turn off, with `forget: true` also delete credentials). Permission `notify.edit`.
- The version number at the bottom left now links to the release notes on GitHub.
- Fixed: a small scrollbar appeared to the right of the tabs in the settings. The tabs can still be swiped on narrow
  screens, but without a visible bar.
- Audit log: readable names for more notification fields (e.g. Telegram chat ID, Webhook on).

## 1.40.1 – 2026-11-23
- **Fixed: update checkers kept reporting a pending update.** Until now every push to main rebuilt the image and
  pushed it as `:latest`, also for changes that do not affect the image (README, workflows, Android app,
  Dependabot). Each build also had a new build time and extra attestation data, so the image digest changed every
  time. Dockhand and similar tools compare that digest and therefore showed "update pending" although the version
  was the same. Now the image is only pushed when `app/VERSION` contains a version that is not in the registry
  yet, and builds are reproducible (build time = commit time, no provenance/SBOM manifests). A manual run of the
  workflow with "force" still rebuilds the current version.
- Base image is now `python:3.15-alpine` (Dependabot update).

## 1.40.0 – 2026-11-23
- **Android app** (new, folder `android/`): MirrorSync as an app on the phone. A thin wrapper around the web
  interface without browser bar, so every new feature is in the app right away. The APK is attached to each
  GitHub release (`mirrorsync-1.40.0.apk`).
  - On first start enter the server address (checked via `/health`), change it later via the back button,
    the error screen or a long press on the app icon.
  - Login, 2FA and "Stay signed in" work as in the browser; **passkeys** work in the app as well (see below).
  - **Notifications** about failed runs (optionally also successful/cancelled ones) with copied/deleted/errors;
    a tap opens the log. The app checks in the background every 15 minutes to 6 hours, using its login or an
    optional API key.
  - Downloads (logs, audit CSV, backup export) land in the Downloads folder, file upload for backup import works.
  - Light/dark design follows the web interface, plain HTTP in the home network and self-signed certificates
    (after a confirmation) are possible.
- Server: new public endpoint `/.well-known/assetlinks.json` (Digital Asset Links), so Android lets the app use
  the passkeys of your domain. Passkey sign-in accepts the app's origin in addition to the HTTPS address.
  Self-built APKs with an own signing key: add its SHA-256 fingerprint via `MIRRORSYNC_ANDROID_CERTS`.
- GitHub Actions: new workflow `android.yml` builds the APK; "Image and release" attaches it to the release
  (signed when the secrets `ANDROID_KEYSTORE_B64` and `ANDROID_KEYSTORE_PASSWORD` are set).

## 1.39.0 – 2026-11-23
- **Delete old logs** as its own section under Settings → General: pick a date, "Show count" shows how many runs
  in how many jobs started before that date, "Delete permanently now" (with confirmation) deletes them once,
  including their logs. Running jobs are not affected, the deletion is recorded in the audit log.
  API/MCP: `POST /logs/purge` (`purge_logs`) with `before` (YYYY-MM-DD) and `dry_run`, permission "general settings".
- The permanent rule "Only keep logs from this date" from 1.38.0 is removed in favour of this (including
  `log_keep_from` in the API). Runs per job (0 = unlimited) and age in days, weeks or months stay.

## 1.38.0 – 2026-11-23
- **More flexible log retention** (Settings → General → Keep logs):
  - "Runs per job to keep" now allows 0 = unlimited.
  - The age is entered as a number of days, weeks or months (a month = 30 days, 0 = unlimited).
  - New: "Only keep logs from this date". Older runs are deleted, empty = no date.
  - If several limits are set, whichever applies first wins. The newest run is always kept.
- API/MCP: `PATCH /settings/logs` (`update_log_settings`) with `log_keep_runs` 0–1000 and the new `log_keep_from`
  (`YYYY-MM-DD`). Changes are recorded in the audit log, all texts in 5 languages.

## 1.37.3 – 2026-11-23
- The hourly security scan now runs on the full hour.

## 1.37.2 – 2026-11-23
- The security scan of the published image (`:latest`) now runs once an hour instead of once a week, so new
  vulnerabilities show up under "Security" within an hour. The app itself is unchanged.

## 1.37.1 – 2026-11-23
- First Trivy scan: 5 findings (severity high), all in old copies of urllib3, msgpack and setuptools bundled with
  pip itself. MirrorSync does not use them, pip is only needed for the build. pip and setuptools are now removed
  from the image after the installation, which clears these findings. Operating system and rclone: no findings.

## 1.37.0 – 2026-11-23
- **Dependencies updated:** rclone 1.68 → 1.76, Python 3.12 → 3.14 (Alpine), Flask 3.0.3 → 3.1.3,
  APScheduler 3.10.4 → 3.11.3, tzdata 2024.2 → 2026.6, segno 1.6.1 → 1.6.6. Waitress, Apprise, webauthn and
  swagger-ui-bundle were already current. Mirroring, two-way sync, GUI, API, MCP, 2FA QR code and passkeys tested.
- **Automatic checks on GitHub:** Dependabot opens weekly pull requests for new versions of the Python packages,
  the base images and the GitHub Actions. Trivy scans every newly built image and, once a week, the current image
  for known vulnerabilities; results are under "Security" in the repository.

## 1.36.0 – 2026-11-23
- **First-time setup without a one-time code:** as long as no user exists, the first visit in the browser creates
  the admin directly (user name and password are enough). The setup code from the container log is gone.
- If you still want the code (e.g. because the container is reachable from the internet before the setup), set
  `SETUP_TOKEN=true`. The setup then works as before. The README explains the risk.
- Existing installations with users are not affected.

## 1.35.0 – 2026-11-23
- **Two-way sync creates missing folders:** if the folder of side A or side B does not exist yet on the first run,
  it is created (previously the run stopped with "directory not found", except with "Also copy the source folder
  itself"). The log lists every created folder, a dry run shows what would be created.
- Protection on later runs: if a side that existed before is missing or empty (e.g. a drive is not mounted), still
  nothing is created or distributed. The run stops and the log explains why and what to do next ("Merge again").
  "Merge again" does not create the folder in that case either.
- A dry run with a missing folder no longer requires "Merge again" afterwards.
- **Configurable update check interval:** under Settings → General → Updates enter a number and pick minutes or
  hours (5 minutes to 720 hours). The default is now 1 hour (previously a fixed 6 hours). API/MCP:
  `update_interval` (in minutes) in `PATCH /settings/update` (`update_update_settings`), `interval_minutes` in
  `GET /update`. Same permission as before ("general settings"), changes are recorded in the audit log.
- New log hints in all 5 languages.

## 1.34.0 – 2026-11-23
- **New version notice:** every 6 hours MirrorSync asks GitHub whether a newer version exists. If so, the bottom left
  shows "⬆ vX.Y.Z available" below the version number, linking to the release. Can be turned off under
  Settings → General → Updates, which also offers "Save and check now" and shows the last check. Only the installed
  version number is sent. Changing the setting is recorded in the audit log. API/MCP: `GET /update` (`get_update`),
  `POST /update/check` (`check_update`, permission "general settings"), `PATCH /settings/update` with `update_check`
  (`update_update_settings`), plus `update` in `/status` and `get_settings`. Use another repository via the
  environment variable `UPDATE_REPO`. All texts in 5 languages.
- Fixed: some texts still appeared in German in other languages: "aktiv", "immer", "aus" and "manuell" on the
  Schedules page, "sonst"/"immer" in the bandwidth preview, and the storage type names "S3 and S3-compatible" and
  "Encryption (crypt)" in the type selection when creating a storage location.

## 1.33.2 – 2026-11-23
- **GitHub repository in English:** README, CHANGELOG, compose file and workflow comments are now in English.
  The German README is still available as [README.de.md](README.de.md).
- New screenshots with the English interface.
- No changes to the app itself.

## 1.33.1 – 2026-11-23
- **Ready-made image on GitHub:** `ghcr.io/dermilderjoghurt/mirrorsync` (amd64 and arm64) with the tags `latest`,
  `1.33.1` and `1.33`, built automatically by a GitHub Action on every push to `main`.
- **Automatic releases:** when `app/VERSION` contains a new version, the Action creates the tag `vX.Y.Z` and a
  GitHub release with the matching CHANGELOG text and the ZIP.
- `docker-compose.yml` now uses the ready-made image and a normal Docker network with port 8080 instead of macvlan.
  Building it yourself still works with `build: .`.
- README: quick start with `docker run`, installation via Compose/Portainer without building, update via
  `docker compose pull`, screenshots of the interface.
- No changes to the app itself.

## 1.33.0 – 2026-11-23
- **Next run in the jobs overview:** below the status, every job shows when it starts next ("today, 14:30",
  "tomorrow, 03:00" or a date), also on phones. Live jobs show the next round, follow-up jobs an estimate based on
  the predecessor ("approx. …", or "when "…" has finished" while it runs), otherwise "manual only", "paused" or
  "none scheduled". API/MCP: `next_start` (ISO time) and `next_start_kind` in `list_jobs` and `get_job`.
- **Two-way sync with folder selection and "Copy the source folder itself":** works as with mirroring, also via
  checkboxes in the browse panel. The selection applies to both sides, everything else stays untouched on both
  sides. With the checkbox, `<side B>/<folder name>` is created and synced on the first run. The form shows the
  result. Changing it triggers a merge on the next run (without deleting).
- **Collapsible sidebar:** the arrow next to "MirrorSync" collapses it to icons only (names on hover), the content
  uses the freed width. Stored per user in the account, so it applies on all devices. No new permission needed.
  API/MCP: field `sidebar` (`full`/`mini`) on `get_user`, `list_users` and `update_user` (permission "Manage users"),
  changes are recorded in the audit log.
- All new texts in 5 languages.

## 1.32.0 – 2026-11-23
- **Audit log with details:** clicking an entry opens a window with all information: origin (web GUI with browser,
  REST API or MCP, request), full old and new values, "+ added / − removed" for lists, the whole content on delete.
  File manager: path, size, files in deleted folders, changed lines when editing (secrets masked), from/to for copy
  and move. Starts with source, destination and run.
- **Host names (FQDN) in allow and block lists**, e.g. `office.example.com` or `facebook.com`. Resolved via DNS on
  each request (5 minute cache), the page shows the current addresses.
- **Country database on a schedule:** either by interval as before or at a time on selected weekdays.
  API: `geoip_mode`, `geoip_time`, `geoip_dow`.
- The "Access blocked" page no longer mentions the emergency switch `IPGUARD_RESET` (only in the README).
- API/MCP, audit labels and all 5 languages updated.

## 1.31.0 – 2026-11-23
- **Two-way sync** (rclone bisync): in the job you first choose the type ("Mirror (one-way)" or "Two-way sync"),
  then side A and side B. Changes and deletions on both sides are transferred. The first run merges both sides
  without deleting. Conflict rule (newer wins, keep both, A or B wins; the loser is kept as `.konflikt1`),
  deletion protection in percent, "Re-merge" after an abort. Also works live. Overview, schedules and log show ⇄.
- New permission **"Set up two-way sync"** (Operator has it, Admin anyway).
- The **Tasks window** now also shows currently running jobs with percentage, bar, log link and stop; they count
  towards the number on the button and disappear when finished. The button also appears with permission "View jobs".
- API/MCP: fields `direction`, `bisync_conflict`, `bisync_max_delete`, endpoints `POST /jobs/{id}/resync` and
  `GET /jobs/running` (tools `resync_job`, `list_running_jobs`). Audit log with "Type", "Conflict rule",
  "Deletion protection (%)" and "re-merged". Everything in 5 languages.
- Live log: notice lines are now shown in the selected language.

## 1.30.0 – 2026-11-23
- **Live like mirroring:** every live round now syncs like a normal mirror run by default (`rclone sync`), so
  deletions and renames in the source reach the destination right away. "Max. deletions", versioning and excludes
  apply in every round. Rounds without changes stay silent. Existing live jobs use this mode from now on.
- Alternatively **"Fast"**: as before, only copy new and changed files (`--max-age`), delete nothing, for very
  large sources.
- Full sync in "Fast" mode now also **by interval** (every X minutes or hours), besides time of day and cron.
  Also configurable on the Schedules page.
- API/MCP: field `live_mode` (mirror|fast), `live_full` accepts `@every 6h` / `@every 90m`, `set_job_trigger`
  has `mode`. Audit log shows "Live mode". Everything in 5 languages.

## 1.29.0 – 2026-11-23
- File manager: **right-click context menu** with all actions (open, edit, download, properties, calculate size,
  rename, copy/move to …, to the other side, delete), also for several marked entries. On empty space: new folder,
  new file, upload, reload, folder sizes, select all.
- **Tasks button at the top right** on all pages (with permission "View files"). The number shows how many tasks are
  running. Clicking opens a floating window with all tasks, where they can be cancelled and removed. The box above
  the lists is gone.

## 1.28.0 – 2026-11-23
- File manager: **drag & drop**. Dragging files and whole folders from the computer uploads them. Dragging rows to
  the other side copies them (with Shift: moves), dropping on a folder puts them inside. You are asked first, on
  conflicts once "overwrite all / skip".
- File manager: the layout adapts. One storage location takes the full width, two take half each. The lists reach
  to the bottom and scroll on their own.
- File manager: "calculate" and "Folder sizes" now also show the number of subfolders and files (API `file_size`:
  `dirs`, `files`).
- File manager: tasks show status and percentage, the bar is colored (blue running, green done, red error).
  Finished tasks can be removed individually or all at once, also via API/MCP (`delete_file_task`,
  `clear_file_tasks`, permission "Edit files").
- File manager: missing modification time or permissions (e.g. on SMB) appear as "–" instead of an empty box.

## 1.27.0 – 2026-11-23
- New: **file manager** (sidebar "Files"). Pick a storage location, with "Two storage locations side by side" also
  two. Browse, see folder sizes and permissions (rwx, owner), edit text files, upload and download, create, rename
  and delete folders and files, copy and move within or between both sides. Copy and move run in the background
  with progress and can be cancelled. Deleting and overwriting ask for confirmation.
- New permissions "File manager: view / edit / delete files" (admins have them, other roles not automatically).
  The role's restrictions and "Visible to" apply. Audit log category "Files".
- API/MCP: 15 new endpoints/tools (`list_files`, `read_file`, `write_file`, `upload_file`, `download_file`,
  `copy_files`, `move_files`, `delete_files` …).
- Changed: with a selection ("Only these files and folders"), "Copy the source folder itself" is automatically off,
  greyed out in the form and ignored for existing jobs too. The selected folders then go directly into the
  destination (before e.g. `dest/share/10-Temp` instead of `dest/10-Temp`).

## 1.26.0 – 2026-11-23
- New: when creating a storage location, the **default port** of the type is prefilled (SMB 445, SFTP 22, FTP 21)
  and changes with the type. For FTP with "tls" = yes it switches to 990 and back, as long as you have not entered
  your own port. Via API/MCP without `port` the rclone default still applies.

## 1.25.0 – 2026-11-23
- New: **language of API responses per key** (Settings → API, when creating and editing). Default "Same as user":
  messages, Swagger descriptions and MCP tool texts come in the language of the user who created the key. Without
  a known user and before authentication (e.g. "API key missing") English instead of the system language.
  `?lang=` and `Accept-Language` still override. API/MCP: field `lang` on `create_api_key`/`update_api_key`,
  `effective_lang` in the key view; audit log.
- Fixed: some API error messages (key invalid, disabled, wrong IP, too many requests) and the MCP greeting were not
  translated.

## 1.24.0 – 2026-11-23
- New: **show an API key again later** (Settings → API → "Show") after confirming with password (+ 2FA code, if set
  up) or passkey. Web GUI only, not via API/MCP. Audit log "API key shown" or "… rejected", failed attempts count
  like wrong passwords. New keys are stored encrypted for this. **Keys from before 1.24.0 cannot be shown** (only
  the hash exists).
- New: **edit API keys**: name, role/permissions, expiry, IPs, groups, **disable/enable**, **pause from–to** and
  **weekly time windows**. Status in the list. API `PATCH /api-keys/{id}`, MCP `update_api_key`, audit with
  before/after.
- New: versioning with **"Keep versions"** (count) and **"at most days"**; older version folders are removed after
  each successful run (noted in the run log). Also via API/MCP (`versions_keep`, `versions_days`).
- Changed: delete buttons are called "Remove" everywhere (API keys, users, roles, groups, backups).
- Changed: Swagger documentation and openapi.json open in a new tab.
- Changed: more space between language selection and "Your last sign-ins" (My account).

## 1.23.0 – 2026-11-23
- New: **delete API keys** (Settings → API, "Delete" button with confirmation): removes the key completely, also from
  groups. Audit log entry "API key deleted"; earlier entries of the key remain. The key currently in use cannot be
  deleted. API `DELETE /api-keys/{id}`, MCP `delete_api_key`.
- **Changed (REST):** revoking is now `POST /api-keys/{id}/revoke` (before `DELETE /api-keys/{id}`, which now
  deletes permanently). The MCP tool `revoke_api_key` keeps its name and still revokes.
- Changed: in the jobs overview and on the job page the button is called "Remove" (DE Entfernen, ES Quitar,
  IT Rimuovi, FR Retirer).

## 1.22.0 – 2026-11-23
- New: **groups** (Settings → Groups, new permission "Manage groups"): users and API keys as members, optionally
  additional permissions (role + permissions of all groups; only permissions you have yourself). Membership can also
  be set on the user, groups are visible in the user list.
- New: **"Visible to"** on every job and storage location: everyone with permission (default) or only selected users
  and groups. Applies everywhere (overview, schedules, chains, source/destination, API, MCP). Admins and the creator
  of a job always see it; hiding something from yourself is not possible.
- API/MCP: `list_groups`, `get_group`, `create_group`, `update_group`, `delete_group`; `visible_to` on jobs and
  storage locations, `groups` on users and API keys. Same checks and audit as in the GUI.
- Audit log: groups, members and "Visible to" with before/after. Backup/export contains both.
- Changed: in the overview the button is now called "Delete" instead of ✕.
- Fixed: storage locations of type local/alias could not be edited ("Unknown type").

## 1.21.0 – 2026-11-22
- New: **everything in the GUI also via REST API and MCP** (view, edit, delete): schedules and chains, storage
  locations (incl. wizard questions, test, re-authorize), notifications and templates, general settings, access by
  IP/country, users, sign-in history, roles, API keys, backup/export/import/restore, templates and notifications per
  job. Every action runs through the same function as in the GUI: same checks, permissions, safeguards and audit
  entries (`API:<name>`). Secrets are write-only. Backup/import/restore only for admin roles. Swagger and MCP tools
  translated.
- New: refresh the **country database** daily, weekly, every 2 weeks, monthly (default), every 2 or 3 months
  (Settings → General, API `geoip_days`).
- New: **bandwidth in MB/s or Mbit/s** (Settings → General → Bandwidth). Applies to all displays and inputs, values
  are converted when switching, storage stays in MB/s. API: `unit` and `input_unit`.
- New: **delete jobs directly in the overview** (✕, with confirmation; only with permission "Jobs: delete").
- Improved: the pause menu in overview and schedules closes when clicking outside or with Esc.
- Fixed: the bandwidth description was partly German in other languages.

## 1.20.0 – 2026-11-22
- New: **automatic backup** (Settings → Backup) on a cron schedule. A new file only when the state changed since the
  last backup (checksum; history, sign-ins and counters do not count). Own destination folder, retention by count
  and days, optionally encrypted, optionally with run logs, "Back up now" (also forced), list of all backups with
  download, restore and delete.
- New: notification for the backup (never / on failure / always, optionally also "nothing changed") with selectable
  channels and three new template events.
- New: **multilingual**: English (default), German, Spanish, Italian, French. Language selectable during setup and on
  the login page, system language under Settings → General, own language per user under My account. Translated are
  GUI, messages, default templates, Swagger/OpenAPI and MCP tool descriptions (API: `?lang=` or `Accept-Language`).
  More languages via a JSON file in `app/i18n/`.
- Existing installations keep German as system language.

## 1.19.1 – 2026-11-22
- Fixed: the build aborted on a slow or briefly interrupted connection to PyPI ("Read timed out", then "No matching
  distribution found"). `pip` now waits 60 s instead of 15 s, retries 10 times, and the whole step is retried up to
  3 times, with a clear message if PyPI cannot be reached at all.
- waitress 3.0.0 → 3.0.2 (security fixes).

## 1.19.0 – 2026-11-22
- New: **API keys** (Settings → API, new permission `system.api`): name, role (permissions and restrictions as for
  users), optional expiry date and allowed IPs. Key shown only once, stored as SHA-256 hash, "last used" with IP,
  revoke, audit log as `API:<name>`.
- New: **REST API** under `/api/v1` (create/change/delete/start/stop/pause jobs, history, logs, storage locations
  without secrets, browse, schedules, audit log, users). Same permissions, IP blocks and failed attempt throttling as
  in the GUI, 300 requests per minute and key. OpenAPI under `/api/v1/openapi.json`, **Swagger UI** under `/api/docs`
  (included in the image, new dependency `swagger-ui-bundle`).
- New: **MCP server** under `/mcp` (Streamable HTTP, JSON-RPC) with 17 tools, visible only with matching permission.
- Job validation moved from the form into a shared function (GUI and API validate the same way).
- Export/import includes the API keys.

## 1.18.0 – 2026-11-22
- Changed: the data store is now **SQLite** (`config/mirrorsync.db`) instead of separate JSON files: jobs with
  history, settings and templates, users with 2FA and passkeys, roles, IP rules, sign-in history, audit log. All
  changes run in transactions. `rclone.conf` stays a separate file.
- **Automatic migration** on the first start: all JSON files in one transaction (all or nothing, idempotent),
  afterwards kept as backup in `config/json-backup/`. Broken file → the container does not start and names it,
  instead of starting empty.
- New: Settings → **Backup** (admins only): **export** the whole state as ZIP (database content, rclone.conf, SSH
  keys, optionally run logs), optionally encrypted with a password (AES-256-GCM/scrypt), clear warning about the
  included secrets. **Import** with checks (version, compatibility, content comparison), replacing only after
  confirmation, automatic backup in `config/backups/` before. Export, import and downloads in the audit log.

## 1.17.0 – 2026-11-22
- Changed: user and password are no longer in the compose file. On the first start a **setup wizard** in the browser
  creates the first admin. Protected by a **setup code** in the container log (`docker logs mirrorsync`, also in
  `config/setup_token`), failed attempts throttled and logged. Step 2 (optional): set up 2FA and passkey.
- New: **passkeys** (WebAuthn) as sign-in per user, without user name and password, several per user, rename/remove
  in "My account", admins can remove them under "Edit". Requires HTTPS and a domain name; via IP or http://
  MirrorSync explains why there are no passkeys. Optional setting "Public address" (or `PUBLIC_URL`). New dependency
  `webauthn==3.0.1`.
- Existing installations keep running unchanged. `WEB_USER`/`WEB_PASS` remain optional (backwards compatible), in the
  compose example only commented out for the `ADMIN_RESET` emergency.

## 1.16.0 – 2026-11-22
- New: **sync only selected files and folders.** In the source browser you tick folders and files (also in
  subfolders), "Apply" puts the base folder into the source and the selection into the new field "Only these files
  and folders". Empty = the whole folder as before.
- With a selection rclone only checks, copies and deletes within the selection (filter rules, excludes still apply).
  Everything else in the destination stays untouched; "Also delete excluded files in the destination" has no effect then.
- A single file as source is automatically turned into parent folder + selection when saving.
- Live sync, dry run, versioning and "Copy the source folder itself" work with the selection. A changed selection
  triggers a full sync again for live jobs. Overview shows "☑ only N entries", audit log "Selection".

## 1.15.0 – 2026-11-22
- Changed: the file browser now lives in the **job form**. "Browse" next to source and destination opens a panel on
  the right: pick a storage location, folders with size/date, path bar, sorting, search, "Apply".
- Excludes are picked in the same browser, now also single files (⛔ to toggle).
- Storage page is a slim list again without a browser.
- All pages use the full window width.
- New endpoint `/browse/list` (replaces `/remotes/<name>/files`).

## 1.14.0 – 2026-11-22
- New: **file browser** on the Storage page (on the right, below on phones): folders and files with size and date,
  path bar, sorting, search, SFTP/FTP from `/`, "Use as source/destination for a new job", "Copy path". Read-only,
  permission `remotes.browse` and per-storage restrictions apply.
- New: **pause** jobs (indefinitely, 1 h, 24 h, 1 week or until a date) directly in the overview or in the job; no
  starts by schedule, live or chain, automatic end of the pause, manual start still possible. Behavior in chains
  selectable: skip (follow-up jobs keep running) or stop the chain. Marked in overview and schedules, entries in the
  audit log.
- `/job/new?source=…&dest=…` prefills source and destination.

## 1.13.0 – 2026-11-22
- New: **custom notification texts** (templates) for subject and body per event (run succeeded, run failed/stopped,
  failed sign-ins, account locked, IP blocked, test), for all channels. Clickable variables, live preview with sample
  data, "Reset to default"; without changes the built-in text still applies.
- New: custom texts per job for successful and failed runs.
- New: webhook JSON body as a template with examples (Discord, Slack, Gotify, Home Assistant/n8n) and JSON
  validation; new webhook fields `event` and `title` in the default JSON.
- New variables incl. `{start}`, `{ende}`, `{dauer}` (readable), `{gestartet_von}`, `{art}` (live/mirror).

## 1.12.0 – 2026-11-22
- New: notification channel **Apprise**, global and per job, with test button.
  - Directly: Apprise URLs (one per line) via the Apprise library in the container (`apprise==2.3.0`).
  - Via an Apprise API server: with configuration key and optional tag (`/notify/<key>`) or stateless with the
    entered URLs (`/notify`).
  - Also used for messages about failed sign-ins and IP blocks.
  - URLs and key are shown masked and not written to the audit log.

## 1.11.0 – 2026-11-22
- New: start type **"Continuous (live)"** in the job and as a separate section on the Schedules page.
  - Every N minutes (default 1) a fast run with `rclone copy --max-age` that only copies files changed since the last
    successful run and deletes nothing.
  - Additional full mirror run at a selectable time (default daily 03:00) so that deletions arrive.
  - The first run and the run after changing source, destination or excludes is a full sync.
  - No overlap; runs without changes do not appear in the history and create no log; error series are reported and
    logged only once. Bandwidth rules apply.
  - Overview shows "Live, every N minutes", the next full sync and "last checked".
- New: **audit log** as a separate page (`config/audit.jsonl`): changes to jobs, schedules, storage locations, users,
  roles, settings and access rules with before/after, starts/stops, sign-ins and sign-outs, automatic blocks; user, IP
  and country per entry; secrets are never stored. Filter, search, CSV export, retention (default 365 days), new
  permission `system.audit`.

## 1.10.0 – 2026-11-22
- New: Settings → Access with protection by IP address and country (`config/ipguard.json`):
  - Block list for single IPs and networks (IPv4/IPv6, CIDR), permanent or temporary, with note and counter.
  - Allow list, e.g. only the local network (a button enters the private ranges).
  - Country rule "allow only these countries" or "block these countries" via the local country database; the local
    network is always exempt.
  - Automatic block after X failed attempts from the same IP within Y minutes, temporary or permanent, local network
    optionally exempt, with notification.
  - "Block IP" button in the sign-in history.
- Blocked addresses get a notice page (403); sign-in attempts from there appear in the sign-in history.
- Protection against self-lockout: rules that would match your own address are rejected; 127.0.0.1 (health check) is
  never blocked. Emergency reset via `IPGUARD_RESET=true`, disable via `IPGUARD=off`.
- Notice in the GUI when a reverse proxy is detected but "Reverse proxy" is not enabled.
- New permission "System: manage access by IP address and country" (Admin has it automatically).

## 1.9.0 – 2026-11-22
- Changed: user names are no longer case-sensitive when signing in. New names that only differ in case from an
  existing one are rejected. Existing conflicts (e.g. `Max` and `max`) are reported in the user list and the container
  log; until they are resolved the exact spelling applies to them.
- New: notification about failed sign-ins via webhook, email and Telegram: on every failed attempt (throttled, failed
  attempts are collected and sent bundled), only on lockout, or never.
- New: acknowledge and delete failed attempts in the sign-in history, individually, selected or all. Filter
  "Unacknowledged", unacknowledged entries are marked red, a red number at "Settings" and "Users" shows them.
  Entries from older versions count as acknowledged.

## 1.8.0 – 2026-11-22
- New: "Schedules" page in the sidebar with the sections "By time", "After another job" and "Manual only".
- By time: change time, weekdays and active directly in the list (cron expressions as a text field).
- After a job: chains below each other, starting with their starting job. Order via drag & drop or ↑ ↓, jobs can be
  dragged between chains and from "Manual only"; "Start a new chain with …". Condition (only on success / always)
  and active per job. Everything is saved immediately.
- Change the start type per entry (time / after job / manual): the job is updated and moves to the right section
  immediately. When inserting after a job, its previous successors keep running after it.
- The page uses the same data as the job form, changes apply in both directions.

## 1.7.0 – 2026-11-22
- New: "Start" section with three types: at a time, after another job, manual only.
- New: "After another job" with a selection list and condition (only on success / always). Chains over several jobs
  are possible, loops are detected and rejected. Nothing starts after a dry run or stop. The previous job's log notes
  which follow-up jobs were started.
- New: easy time setting (time + weekdays), cron expression still under "Advanced".
- Overview: chains are shown indented below their starting job ("after …", "then: …"), simple schedules in plain
  text (e.g. "Mon–Fri 03:00").
- When a job is deleted, its follow-up jobs are set to "Manual only".
- Existing jobs keep their schedule.
- New: last sign-in per user with time, IP address and country (with flag). Private addresses appear as "Local network".
- New: sign-in history (Settings → Users → Sign-in history) with successful and failed attempts, reason, IP, country
  and browser, filterable by result and user. "My account" shows your own last sign-ins.
- New: countries come from a local database (DB-IP Lite, CC BY 4.0) that the container downloads itself and refreshes
  monthly. No IP addresses are sent to third-party services. Your own `GeoLite2-Country.mmdb` in `config/geoip/` is
  preferred. Can be switched off, then only IP addresses are shown.
- New: setting "Reverse proxy": `X-Forwarded-For` is only evaluated when it is on. Security fix: before, the header
  was always trusted, which allowed bypassing the lockout after failed attempts.
- New: disable and re-enable accounts, plus a plannable lock period ("locked from", "active again from", both
  optional). Open sessions end immediately, afterwards the account becomes active again automatically.
- New: configurable lockout after failed attempts (count, duration in minutes or permanently until an admin unlocks),
  optionally with notification. "Unlock" button in the user list.
- Safeguards: there is always one active admin without a planned lock. The last admin is locked for at most
  15 minutes after failed attempts, never permanently. You cannot disable your own account.

## 1.6.0 – 2026-11-22
- New: bandwidth limit with schedule. Time windows with weekdays, time from–to and separate values for upload and
  download in MB/s, plus a limit for the time outside the windows. Windows across midnight are possible. Presets
  "weekdays 8–18 10 MB/s" and "daytime 5 MB/s", preview in plain text.
- Default under Settings → General, can be overridden per job (default, custom limits, always unlimited).
- Implemented as an rclone timetable (`--bwlimit`) that also switches during a running mirror. A `--bwlimit` in the
  additional options still takes precedence. Existing jobs stay unlimited as long as no default is set.

## 1.5.1 – 2026-11-22
- Changed: "Browse" starts at the root `/` for SFTP/SSH and FTP storage locations instead of the user's home folder.
  Selected paths are taken as absolute (e.g. `Server:/opt/data`). "⬆ .." goes up to `/` and from there to the storage
  location selection. To work in the home folder on purpose, enter `Name:` or `Name:folder` by hand; existing jobs
  do not change.
- New: MirrorSync logo as favicon in the browser tab (`favicon.ico`, SVG and home screen icon).

## 1.5.0 – 2026-11-22
- New: every run has its own log (`logs/<job>/<run>.log`) instead of one file that is overwritten on the next run.
- New: the history shows copied, deleted and errors per run. Every row is clickable and opens the full log.
- New: log view with filters (all, errors, copied, deleted, notices) with counts, search and download. Errors are
  red, copied green, deleted orange. Running runs update live.
- New: Settings → General with log retention (number of runs per job, maximum age in days) and the used space.
  New permission "System: change general settings" (Admin has it automatically).
- The previous log is migrated on the first start. Deleting a job also deletes its logs.

## 1.4.0 – 2026-11-22
- New: checkbox "Copy the source folder itself" in the job. Without it the contents of the source are mirrored as
  before, with it they go into a folder named like the source in the destination (`dest/OPNsense/…`). Deletions then
  only happen inside this folder, other folders in the destination stay untouched.
- The form shows while typing where the data ends up and in which folder deletions happen.
- Versioning, log, overview and notifications use the actual destination.
- Existing jobs do not change (checkbox is off).

## 1.3.1 – 2026-11-22
- Fixed: "Browse" with an empty field searched in `/data` and showed "directory not found" when no local folder was
  mounted. Now the list of storage locations appears first (and `/data`, if present).
- For SMB storage locations the top level shows the shares, below them the folders. "⬆ .." goes back to the storage
  location selection.
- Understandable error messages when browsing (folder not found, sign-in rejected, no connection, password/key
  missing, sign-in expired); the rclone message is shown small below.
- Folder selection for excludes now also works when the source is a storage location itself (e.g. `nas:`).

## 1.3.0 – 2026-11-22
- New: custom roles under Settings → Roles, made of 21 individual permissions for jobs, storage locations,
  notifications, users and roles.
- New: roles can be limited to selected jobs and selected storage locations. Jobs a user created stay visible to
  them. Source and destination must be in allowed storage locations.
- New: Admin, Operator and Read only are templates ("Use as template" copies a role). Admin is fixed.
- New: protection against privilege escalation: roles and users can only be created, changed or assigned with at
  most your own permissions.
- Permission changes on a role apply immediately to all its users.
- Update: existing users keep their role (Admin, Operator, Read only) with the same permissions as in 1.2.0.

## 1.2.0 – 2026-11-22
- New: multiple users under Settings → Users, with the roles Admin, Operator and Read only. Permissions are checked on
  every page and every action; buttons without permission are hidden.
- New: 2FA with an authenticator app (TOTP) with QR code and 10 backup codes, under Settings → My account. Admins can
  reset a user's 2FA.
- New: change your own password; other sessions are ended. Passwords are stored hashed.
- New: settings with tabs Users, Notifications, My account. User name and role at the bottom of the sidebar.
- New: the job history shows who started it (user or schedule).
- New: first-time setup in the GUI if no `WEB_PASS` is set; emergency reset via `ADMIN_RESET=true`.
- Update: existing installations take over `WEB_USER`/`WEB_PASS` automatically as the first admin.

## 1.1.1 – 2026-11-22
- Compose example uses port 80 (`PORT=80`), so the GUI is directly at `http://192.168.1.50`.
- Fixed: the container's health check always queried port 8080 and reported "unhealthy" with a changed `PORT`. It
  now uses the configured port.

## 1.1.0 – 2026-11-22
- New: own login page with "Stay signed in" and sign-out, instead of the browser's sign-in dialog. Protection
  against password guessing (5 failed attempts = 5 minute lockout).
- New: modern design with sidebar, overview cards, light and dark theme (switchable), better on phones.
- New: create and edit notifications directly in the job: use default, custom or none; own webhook URL, email
  recipients, Telegram chat ID and bot per job; test button.
- The overview shows per job when and where notifications are sent.
- Compose example with macvlan, environment variables as a list and a clear note about `build: .`.
- Jobs from 1.0.0 are migrated automatically.

## 1.0.0 – 2026-11-22
First version.
- One-way 1:1 mirroring (like FreeFileSync "Mirror") with rclone as sync engine
- Web GUI with password protection: create, start, stop jobs, dry run, live log, history
- Scheduling per job with cron and presets
- Storage locations for all rclone types (SMB, WebDAV, SFTP, FTP, S3, B2, Azure, Google Drive, OneDrive, Dropbox,
  pCloud, MEGA, crypt …) created, edited and tested in the GUI
- Browser sign-in (OAuth) via `rclone authorize` with instructions in the GUI
- Excludes (folders, files, patterns) with folder picker, optionally also deleted in the destination
- Versioning of deleted/overwritten files, deletion protection (max. deletions)
- Notifications via webhook, email (SMTP) and Telegram, global and per job
- Running as a relay between two remote servers (A → B) without local folders
