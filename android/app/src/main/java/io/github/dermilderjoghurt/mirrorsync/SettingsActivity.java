package io.github.dermilderjoghurt.mirrorsync;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

/** First start: enter the server address. Later: change the address and the notification settings. */
public class SettingsActivity extends Activity {
    private EditText url;
    private EditText apiKey;
    private TextView status;
    private Button connect;
    private Switch notify;
    private Switch notifySuccess;
    private Spinner interval;
    private boolean firstRun;
    private String failedUrl;   // address that failed the check; a second tap saves it anyway

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        MainActivity.applyInsets(this, findViewById(R.id.root));
        SharedPreferences p = Prefs.get(this);
        firstRun = Prefs.server(this).isEmpty();

        url = findViewById(R.id.url);
        apiKey = findViewById(R.id.api_key);
        status = findViewById(R.id.status);
        connect = findViewById(firstRun ? R.id.connect : R.id.save);   // the button that checks and saves
        notify = findViewById(R.id.notify);
        notifySuccess = findViewById(R.id.notify_success);
        interval = findViewById(R.id.interval);

        url.setText(Prefs.server(this));
        apiKey.setText(p.getString(Prefs.KEY_API_KEY, ""));
        notify.setChecked(Prefs.notifyEnabled(this));
        notifySuccess.setChecked(p.getBoolean(Prefs.KEY_NOTIFY_SUCCESS, false));
        notifySuccess.setEnabled(notify.isChecked());
        notify.setOnCheckedChangeListener((b, on) -> notifySuccess.setEnabled(on));

        String[] labels = new String[Prefs.INTERVALS.length];
        int sel = 0;
        for (int i = 0; i < Prefs.INTERVALS.length; i++) {
            int m = Prefs.INTERVALS[i];
            labels[i] = m < 60 ? getString(R.string.minutes, m) : (m == 60 ? getString(R.string.hour) : getString(R.string.hours, m / 60));
            if (m == Prefs.interval(this)) sel = i;
        }
        ArrayAdapter<String> ad = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, labels);
        ad.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        interval.setAdapter(ad);
        interval.setSelection(sel);

        ((TextView) findViewById(R.id.version)).setText(getString(R.string.version_info, BuildConfig.VERSION_NAME));
        if (!firstRun) findViewById(R.id.welcome).setVisibility(View.GONE);
        if (!firstRun) ((TextView) findViewById(R.id.title)).setText(R.string.settings_title);
        findViewById(R.id.connect).setVisibility(firstRun ? View.VISIBLE : View.GONE);
        findViewById(R.id.save).setVisibility(firstRun ? View.GONE : View.VISIBLE);
        connect.setOnClickListener(v -> check());
        url.setOnEditorActionListener((v, id, e) -> {
            if (id == EditorInfo.IME_ACTION_GO) {
                check();
                return true;
            }
            return false;
        });
    }

    /** Checks /health of the entered address, then saves. */
    private void check() {
        String u = Prefs.normalize(url.getText().toString());
        if (u.isEmpty()) {
            showStatus(getString(R.string.url_invalid), false);
            return;
        }
        url.setText(u);
        if (u.equals(failedUrl) || u.equals(Prefs.server(this))) {
            save(u);
            return;
        }
        showStatus(getString(R.string.checking), true);
        connect.setEnabled(false);
        new Thread(() -> {
            Object[] r = Prefs.httpGet(u + "/health", null, null, 10000);
            String version = null;
            String problem;
            int code = (int) r[0];
            if (code == 200) {
                try {
                    JSONObject o = new JSONObject((String) r[1]);
                    if ("ok".equals(o.optString("status"))) version = o.optString("version", "?");
                } catch (Exception ignored) {
                    // not JSON: some other web server
                }
                problem = "HTTP 200, " + getString(R.string.app_name) + "?";
            } else {
                problem = code == -1 ? (String) r[1] : "HTTP " + code;
            }
            String v = version;
            runOnUiThread(() -> {
                connect.setEnabled(true);
                if (v != null) {
                    showStatus(getString(R.string.check_ok, v), true);
                    save(u);
                } else {
                    failedUrl = u;
                    showStatus(getString(R.string.check_fail, problem) + "\n" + getString(R.string.check_fail_hint), false);
                    connect.setText(R.string.save_anyway);
                }
            });
        }).start();
    }

    private void save(String u) {
        boolean changed = !u.equals(Prefs.server(this));
        int min = Prefs.INTERVALS[Math.max(0, interval.getSelectedItemPosition())];
        SharedPreferences.Editor e = Prefs.get(this).edit()
                .putString(Prefs.KEY_SERVER, u)
                .putBoolean(Prefs.KEY_NOTIFY, notify.isChecked())
                .putBoolean(Prefs.KEY_NOTIFY_SUCCESS, notifySuccess.isChecked())
                .putInt(Prefs.KEY_INTERVAL, min)
                .putString(Prefs.KEY_API_KEY, apiKey.getText().toString().trim())
                .putBoolean(Prefs.KEY_AUTH_WARNED, false);
        if (changed) e.remove(Prefs.KEY_SEEN);   // other server: start fresh, no flood of old runs
        e.apply();
        PollService.schedule(this);
        if (notify.isChecked() && Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
            return;   // continue in onRequestPermissionsResult
        }
        done(changed);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        done(true);
    }

    private void done(boolean changed) {
        Toast.makeText(this, R.string.saved, Toast.LENGTH_SHORT).show();
        Intent i = new Intent(this, MainActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        if (changed) i.putExtra(MainActivity.EXTRA_RELOAD, true);
        startActivity(i);
        finish();
    }

    private void showStatus(String text, boolean ok) {
        status.setVisibility(View.VISIBLE);
        status.setText(text);
        status.setTextColor(ok ? getColor(R.color.muted) : 0xFFDC2626);
    }
}
