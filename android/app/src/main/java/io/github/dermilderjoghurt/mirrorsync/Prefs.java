package io.github.dermilderjoghurt.mirrorsync;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/** Settings of the app and a few small helpers shared by the activities and the background check. */
final class Prefs {
    static final String KEY_SERVER = "server_url";
    static final String KEY_NOTIFY = "notify_enabled";
    static final String KEY_NOTIFY_SUCCESS = "notify_success";
    static final String KEY_INTERVAL = "notify_interval_min";
    static final String KEY_API_KEY = "api_key";
    static final String KEY_SEEN = "seen_runs";
    static final String KEY_AUTH_WARNED = "auth_warned";
    static final String KEY_ASKED_PERMISSION = "asked_notification_permission";

    static final int[] INTERVALS = {15, 30, 60, 180, 360};

    private Prefs() {
    }

    static SharedPreferences get(Context c) {
        return c.getSharedPreferences("mirrorsync", Context.MODE_PRIVATE);
    }

    static String server(Context c) {
        return get(c).getString(KEY_SERVER, "");
    }

    static boolean notifyEnabled(Context c) {
        return get(c).getBoolean(KEY_NOTIFY, true);
    }

    static int interval(Context c) {
        return get(c).getInt(KEY_INTERVAL, 15);
    }

    /** "sync.example.com" → "https://sync.example.com"; removes a trailing slash. Returns "" if unusable. */
    static String normalize(String raw) {
        String s = raw == null ? "" : raw.trim();
        if (s.isEmpty()) return "";
        if (!s.matches("(?i)^https?://.*")) s = "https://" + s;
        while (s.endsWith("/")) s = s.substring(0, s.length() - 1);
        Uri u = Uri.parse(s);
        if (u.getHost() == null || u.getHost().isEmpty()) return "";
        return s;
    }

    static boolean sameServer(Context c, Uri url) {
        Uri base = Uri.parse(server(c));
        if (url == null || url.getHost() == null || base.getHost() == null) return false;
        return url.getHost().equalsIgnoreCase(base.getHost()) && port(url) == port(base);
    }

    private static int port(Uri u) {
        if (u.getPort() != -1) return u.getPort();
        return "http".equalsIgnoreCase(u.getScheme()) ? 80 : 443;
    }

    static String lang() {
        String l = Locale.getDefault().getLanguage();
        return l.matches("de|en|fr|es|it") ? l : "en";
    }

    /** Small HTTP GET returning {status code, body}. Body is "" on network errors (code -1, message in body). */
    static Object[] httpGet(String url, String cookie, String apiKey, int timeoutMs) {
        HttpURLConnection con = null;
        try {
            con = (HttpURLConnection) new URL(url).openConnection();
            con.setConnectTimeout(timeoutMs);
            con.setReadTimeout(timeoutMs);
            con.setInstanceFollowRedirects(false);
            con.setRequestProperty("Accept", "application/json");
            con.setRequestProperty("Accept-Language", lang());
            con.setRequestProperty("User-Agent", "MirrorSyncApp/" + BuildConfig.VERSION_NAME);
            if (apiKey != null && !apiKey.isEmpty()) {
                con.setRequestProperty("Authorization", "Bearer " + apiKey);
            } else if (cookie != null && !cookie.isEmpty()) {
                con.setRequestProperty("Cookie", cookie);
            }
            int code = con.getResponseCode();
            InputStream in = code >= 400 ? con.getErrorStream() : con.getInputStream();
            return new Object[]{code, in == null ? "" : readAll(in)};
        } catch (Exception e) {
            String msg = e.getMessage();
            return new Object[]{-1, e.getClass().getSimpleName() + (msg == null ? "" : ": " + msg)};
        } finally {
            if (con != null) con.disconnect();
        }
    }

    static String readAll(InputStream in) throws IOException {
        try (InputStream is = in) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = is.read(buf)) > 0) {
                out.write(buf, 0, n);
                if (out.size() > 8 * 1024 * 1024) break;
            }
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }
}
