package io.github.dermilderjoghurt.mirrorsync;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.webkit.CookieManager;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Background check for notifications: asks MirrorSync for the tasks (GET /api/v1/jobs) and reports every run
 * that finished since the last check. Uses the API key from the settings or else the login cookie of the app.
 */
public class PollService extends JobService {
    private static final int JOB_ID = 4711;
    private static final String CH_FAILED = "runs_failed";
    private static final String CH_DONE = "runs_done";
    private static final String CH_ACCOUNT = "account";
    private static final int ID_AUTH = 1;

    static void schedule(Context c) {
        JobScheduler js = (JobScheduler) c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        if (js == null) return;
        if (!Prefs.notifyEnabled(c) || Prefs.server(c).isEmpty()) {
            js.cancel(JOB_ID);
            return;
        }
        long period = Prefs.interval(c) * 60_000L;
        JobInfo existing = js.getPendingJob(JOB_ID);
        if (existing != null && existing.getIntervalMillis() == period) return;
        js.schedule(new JobInfo.Builder(JOB_ID, new ComponentName(c, PollService.class))
                .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
                .setPeriodic(period)
                .setPersisted(true)
                .build());
    }

    @Override
    public boolean onStartJob(JobParameters params) {
        String server = Prefs.server(this);
        String apiKey = Prefs.get(this).getString(Prefs.KEY_API_KEY, "");
        String cookie = null;
        try {
            cookie = CookieManager.getInstance().getCookie(server);
        } catch (Exception ignored) {
            // WebView not available (being updated): try again next time
        }
        String ck = cookie;
        new Thread(() -> {
            try {
                check(this, server, apiKey, ck);
            } catch (Exception ignored) {
                // never crash in the background; the next check tries again
            }
            jobFinished(params, false);
        }).start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters params) {
        return true;
    }

    static void check(Context c, String server, String apiKey, String cookie) throws Exception {
        if (server.isEmpty() || !Prefs.notifyEnabled(c)) return;
        SharedPreferences p = Prefs.get(c);
        Object[] r = Prefs.httpGet(server + "/api/v1/jobs?lang=" + Prefs.lang(), cookie, apiKey, 20000);
        int code = (int) r[0];
        if (code == 401 || code == 403 || (code >= 300 && code < 400)) {
            if (!p.getBoolean(Prefs.KEY_AUTH_WARNED, false)) {
                p.edit().putBoolean(Prefs.KEY_AUTH_WARNED, true).apply();
                notify(c, ID_AUTH, CH_ACCOUNT, c.getString(R.string.n_login_title),
                        c.getString(code == 403 ? R.string.n_perm_text : R.string.n_login_text), null, false);
            }
            return;
        }
        if (code != 200) return;   // server not reachable right now: stay quiet
        if (p.getBoolean(Prefs.KEY_AUTH_WARNED, false)) {
            p.edit().putBoolean(Prefs.KEY_AUTH_WARNED, false).apply();
            cancel(c, ID_AUTH);
        }

        JSONArray jobs = new JSONArray((String) r[1]);
        JSONObject seen = new JSONObject(p.getString(Prefs.KEY_SEEN, "{}"));
        boolean first = !p.contains(Prefs.KEY_SEEN);
        boolean all = p.getBoolean(Prefs.KEY_NOTIFY_SUCCESS, false);
        JSONObject now = new JSONObject();
        for (int i = 0; i < jobs.length(); i++) {
            JSONObject j = jobs.getJSONObject(i);
            String id = j.optString("id");
            String last = j.optString("last_run", "");
            String status = j.optString("last_status", "");
            if (id.isEmpty()) continue;
            if ("laeuft".equals(status)) {   // still running: remember the previous run, report when it is done
                now.put(id, seen.optString(id, last));
                continue;
            }
            now.put(id, last);
            if (first || last.isEmpty() || !seen.has(id) || last.equals(seen.optString(id))) continue;
            boolean failed = "fehler".equals(status);
            if (!failed && !all) continue;
            report(c, server, apiKey, cookie, id, j.optString("name", id), status);
        }
        // tasks that were deleted simply drop out of the map
        p.edit().putString(Prefs.KEY_SEEN, now.toString()).apply();
    }

    private static void report(Context c, String server, String apiKey, String cookie, String id, String name, String status) {
        int title;
        switch (status) {
            case "fehler":
                title = R.string.n_failed;
                break;
            case "ok":
                title = R.string.n_ok;
                break;
            case "abgebrochen":
                title = R.string.n_cancelled;
                break;
            default:
                title = 0;
        }
        String head = title != 0 ? c.getString(title, name) : c.getString(R.string.n_other, name, status);
        String text = "";
        boolean dry = false;
        try {   // details of the newest run: when, copied, deleted, errors
            Object[] h = Prefs.httpGet(server + "/api/v1/jobs/" + Uri.encode(id) + "/history?limit=1", cookie, apiKey, 15000);
            if ((int) h[0] == 200) {
                JSONArray arr = new JSONArray((String) h[1]);
                if (arr.length() > 0) {
                    JSONObject e = arr.getJSONObject(0);
                    String start = e.optString("start", "");
                    String when = start.length() >= 16 ? start.substring(11, 16) : start;
                    dry = e.optBoolean("dry_run", false);
                    text = c.getString(R.string.n_details, when, e.optString("copied", "0"), e.optString("deleted", "0"),
                            e.optString("errors", "0"));
                }
            }
        } catch (Exception ignored) {
            // details are optional
        }
        if (dry) head = head + " (" + c.getString(R.string.n_dry) + ")";
        notify(c, 100 + Math.abs(id.hashCode() % 100000), "fehler".equals(status) ? CH_FAILED : CH_DONE, head, text,
                "/job/" + Uri.encode(id) + "/log", true);
    }

    private static void channels(NotificationManager nm, Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        nm.createNotificationChannel(new NotificationChannel(CH_FAILED, c.getString(R.string.ch_failed), NotificationManager.IMPORTANCE_HIGH));
        nm.createNotificationChannel(new NotificationChannel(CH_DONE, c.getString(R.string.ch_done), NotificationManager.IMPORTANCE_DEFAULT));
        nm.createNotificationChannel(new NotificationChannel(CH_ACCOUNT, c.getString(R.string.ch_account), NotificationManager.IMPORTANCE_DEFAULT));
    }

    @SuppressWarnings("deprecation")
    private static void notify(Context c, int id, String channel, String title, String text, String path, boolean autoCancel) {
        if (Build.VERSION.SDK_INT >= 33 && c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return;
        }
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        channels(nm, c);
        Intent open = new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (path != null) open.putExtra(MainActivity.EXTRA_PATH, path);
        PendingIntent pi = PendingIntent.getActivity(c, id, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, channel) : new Notification.Builder(c);
        b.setSmallIcon(R.drawable.ic_notification)
                .setColor(c.getColor(R.color.brand))
                .setContentTitle(title)
                .setContentText(text)
                .setStyle(new Notification.BigTextStyle().bigText(text))
                .setContentIntent(pi)
                .setAutoCancel(autoCancel)
                .setWhen(System.currentTimeMillis())
                .setShowWhen(true);
        if (Build.VERSION.SDK_INT < 26 && CH_FAILED.equals(channel)) b.setPriority(Notification.PRIORITY_HIGH);
        nm.notify(id, b.build());
    }

    private static void cancel(Context c, int id) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.cancel(id);
    }
}
