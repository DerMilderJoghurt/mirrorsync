package io.github.dermilderjoghurt.mirrorsync;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Insets;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.text.InputType;
import android.util.Base64;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.CookieManager;
import android.webkit.HttpAuthHandler;
import android.webkit.JavascriptInterface;
import android.webkit.SslErrorHandler;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.webkit.WebSettingsCompat;
import androidx.webkit.WebViewFeature;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.HashSet;
import java.util.Set;

/** The MirrorSync web interface in a full-screen WebView. */
public class MainActivity extends Activity {
    static final String EXTRA_PATH = "path";
    static final String EXTRA_RELOAD = "reload";
    private static final int REQ_FILE = 10;
    private static final int REQ_NOTIFY = 11;

    private WebView web;
    private View root;
    private View error;
    private TextView errorText;
    private ProgressBar progress;
    private ValueCallback<Uri[]> fileCallback;
    private boolean loadFailed;
    private final Set<String> trustedCerts = new HashSet<>();   // hosts whose invalid certificate the user accepted (this session)

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (Prefs.server(this).isEmpty()) {
            startActivity(new Intent(this, SettingsActivity.class));
            finish();
            return;
        }
        setContentView(R.layout.activity_main);
        root = findViewById(R.id.root);
        applyInsets(this, root);
        web = findViewById(R.id.web);
        error = findViewById(R.id.error);
        errorText = findViewById(R.id.error_text);
        progress = findViewById(R.id.progress);
        findViewById(R.id.retry).setOnClickListener(v -> {
            error.setVisibility(View.GONE);
            if (web.getUrl() == null || web.getUrl().startsWith("about:")) web.loadUrl(Prefs.server(this));
            else web.reload();
        });
        findViewById(R.id.change_server).setOnClickListener(v -> startActivity(new Intent(this, SettingsActivity.class)));

        setupWebView();
        if (savedInstanceState != null) web.restoreState(savedInstanceState);
        if (web.getUrl() == null) web.loadUrl(startUrl(getIntent()));

        PollService.schedule(this);
        askNotificationPermission();
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        s.setUserAgentString(s.getUserAgentString() + " MirrorSyncApp/" + BuildConfig.VERSION_NAME);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, false);

        // Passkeys (WebAuthn). Needs a recent Android System WebView and the Digital Asset Links file
        // that MirrorSync serves under /.well-known/assetlinks.json.
        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_AUTHENTICATION)) {
            WebSettingsCompat.setWebAuthenticationSupport(s, WebSettingsCompat.WEB_AUTHENTICATION_SUPPORT_FOR_APP);
        }

        web.addJavascriptInterface(new Bridge(), "MirrorSyncApp");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new Chrome());
        web.setDownloadListener((url, ua, disposition, mime, length) -> download(url, ua, disposition, mime));
    }

    private String startUrl(Intent i) {
        String base = Prefs.server(this);
        String path = i == null ? null : i.getStringExtra(EXTRA_PATH);
        return path != null && path.startsWith("/") ? base + path : base + "/";
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (web == null) return;
        if (intent.getBooleanExtra(EXTRA_RELOAD, false)) {
            web.clearHistory();
            error.setVisibility(View.GONE);
            web.loadUrl(startUrl(intent));
        } else if (intent.getStringExtra(EXTRA_PATH) != null) {
            web.loadUrl(startUrl(intent));
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        if (web != null) web.saveState(out);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    protected void onPause() {
        if (web != null) web.onPause();
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (error.getVisibility() == View.VISIBLE || web == null) {
            super.onBackPressed();
        } else if (web.canGoBack()) {
            web.goBack();
        } else {
            new AlertDialog.Builder(this)
                    .setTitle(R.string.exit_title)
                    .setMessage(R.string.exit_text)
                    .setPositiveButton(R.string.exit, (d, w) -> finish())
                    .setNeutralButton(R.string.change_server, (d, w) -> startActivity(new Intent(this, SettingsActivity.class)))
                    .setNegativeButton(R.string.cancel, null)
                    .show();
        }
    }

    private void askNotificationPermission() {
        if (Build.VERSION.SDK_INT < 33 || !Prefs.notifyEnabled(this)) return;
        if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) return;
        if (Prefs.get(this).getBoolean(Prefs.KEY_ASKED_PERMISSION, false)) return;
        Prefs.get(this).edit().putBoolean(Prefs.KEY_ASKED_PERMISSION, true).apply();
        requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIFY);
    }

    private void showError(String what) {
        loadFailed = true;
        errorText.setText(getString(R.string.error_text, Prefs.server(this), what));
        error.setVisibility(View.VISIBLE);
        progress.setVisibility(View.GONE);
    }

    // ------------------------------------------------------------------ insets and colours

    /** Draws edge to edge on every Android version and keeps the content clear of status bar, navigation bar and keyboard. */
    @SuppressWarnings("deprecation")
    static void applyInsets(Activity a, View v) {
        Window w = a.getWindow();
        w.setStatusBarColor(Color.TRANSPARENT);
        w.setNavigationBarColor(Color.TRANSPARENT);
        if (Build.VERSION.SDK_INT >= 30) {
            w.setDecorFitsSystemWindows(false);
        } else {
            v.setSystemUiVisibility(v.getSystemUiVisibility() | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        }
        v.setOnApplyWindowInsetsListener((view, in) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                Insets i = in.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime() | WindowInsets.Type.displayCutout());
                view.setPadding(i.left, i.top, i.right, i.bottom);
                return WindowInsets.CONSUMED;
            }
            view.setPadding(in.getSystemWindowInsetLeft(), in.getSystemWindowInsetTop(),
                    in.getSystemWindowInsetRight(), in.getSystemWindowInsetBottom());
            return in.consumeSystemWindowInsets();
        });
        v.requestApplyInsets();
    }

    /** Background behind the system bars follows the page (light/dark theme of the web interface). */
    @SuppressWarnings("deprecation")
    private void setBarColor(int color) {
        root.setBackgroundColor(color);
        double lum = (0.299 * Color.red(color) + 0.587 * Color.green(color) + 0.114 * Color.blue(color)) / 255.0;
        boolean light = lum > 0.5;
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                int mask = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(light ? mask : 0, mask);
            }
        } else {
            int f = root.getSystemUiVisibility();
            f = light ? (f | View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR) : (f & ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
            if (Build.VERSION.SDK_INT >= 26) {
                f = light ? (f | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR) : (f & ~View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
            }
            root.setSystemUiVisibility(f);
        }
    }

    // ------------------------------------------------------------------ downloads and uploads

    private void download(String url, String ua, String disposition, String mime) {
        String name = URLUtil.guessFileName(url, disposition, mime);
        if (url.startsWith("blob:")) {
            web.evaluateJavascript("window.__msSaveBlobUrl&&window.__msSaveBlobUrl(" + jsString(url) + "," + jsString(name) + ")", null);
            return;
        }
        if (url.startsWith("data:")) {
            int comma = url.indexOf(',');
            if (comma > 0) {
                String head = url.substring(5, comma);
                byte[] data = head.endsWith(";base64") ? Base64.decode(url.substring(comma + 1), Base64.DEFAULT)
                        : Uri.decode(url.substring(comma + 1)).getBytes();
                saveBytes(name, mime, data);
            }
            return;
        }
        if (Build.VERSION.SDK_INT < 29 && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 12);
            return;
        }
        try {
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(url));
            String cookie = CookieManager.getInstance().getCookie(url);
            if (cookie != null) r.addRequestHeader("Cookie", cookie);
            r.addRequestHeader("User-Agent", ua);
            r.setMimeType(mime);
            r.setTitle(name);
            r.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            r.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, name);
            ((DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE)).enqueue(r);
            Toast.makeText(this, getString(R.string.download_started, name), Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, getString(R.string.download_failed, String.valueOf(e.getMessage())), Toast.LENGTH_LONG).show();
        }
    }

    /** Writes a file to the public Downloads folder. */
    private void saveBytes(String name, String mime, byte[] data) {
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues cv = new ContentValues();
                cv.put(MediaStore.Downloads.DISPLAY_NAME, name);
                cv.put(MediaStore.Downloads.MIME_TYPE, mime == null || mime.isEmpty() ? "application/octet-stream" : mime);
                Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (uri == null) throw new IllegalStateException("MediaStore");
                try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                    if (out == null) throw new IllegalStateException("MediaStore");
                    out.write(data);
                }
            } else {
                if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 12);
                    throw new IllegalStateException("permission");
                }
                @SuppressWarnings("deprecation")
                File dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                //noinspection ResultOfMethodCallIgnored
                dir.mkdirs();
                try (OutputStream out = new FileOutputStream(new File(dir, name))) {
                    out.write(data);
                }
            }
            Toast.makeText(this, getString(R.string.download_saved, name), Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, getString(R.string.download_failed, String.valueOf(e.getMessage())), Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQ_FILE && fileCallback != null) {
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    private static String jsString(String s) {
        return "'" + s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'";
    }

    /**
     * Script injected into every page: reports the page colour, saves files that only exist in the page
     * (blob: links) and turns the POST form of the backup export into a download.
     */
    private static final String PAGE_SCRIPT = "(function(){if(window.__msApp)return;window.__msApp=1;"
            + "function col(){try{MirrorSyncApp.setColor(getComputedStyle(document.body).backgroundColor)}catch(e){}}"
            + "col();new MutationObserver(col).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme','class']});"
            + "try{matchMedia('(prefers-color-scheme: dark)').addEventListener('change',col)}catch(e){}"
            + "function save(blob,name){var r=new FileReader();r.onload=function(){var s=String(r.result);"
            + "MirrorSyncApp.saveFile(name,blob.type||'application/octet-stream',s.substring(s.indexOf(',')+1))};r.readAsDataURL(blob)}"
            + "window.__msSaveBlobUrl=function(u,n){fetch(u).then(function(r){return r.blob()}).then(function(b){save(b,n)})};"
            + "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||!f.action||!/\\/settings\\/backup\\/export$/.test(f.action))return;"
            + "if(ev.defaultPrevented)return;ev.preventDefault();"
            + "fetch(f.action,{method:'POST',body:new FormData(f),credentials:'same-origin'}).then(function(r){"
            + "var cd=r.headers.get('Content-Disposition')||'';if(/attachment/i.test(cd)){"
            + "var m=/filename\\*?=(?:UTF-8'')?\"?([^\";]+)\"?/i.exec(cd);var n=m?decodeURIComponent(m[1]):'mirrorsync-export.zip';"
            + "return r.blob().then(function(b){save(b,n)})}"
            + "return r.text().then(function(t){document.open();document.write(t);document.close()})})},false);"
            + "})();";

    /** Methods the page can call as window.MirrorSyncApp.* */
    private class Bridge {
        @JavascriptInterface
        public String version() {
            return BuildConfig.VERSION_NAME;
        }

        @JavascriptInterface
        public void saveFile(String name, String mime, String base64) {
            byte[] data = Base64.decode(base64, Base64.DEFAULT);
            String safe = name == null || name.isEmpty() ? "download" : name.replaceAll("[\\\\/:*?\"<>|]", "_");
            runOnUiThread(() -> saveBytes(safe, mime, data));
        }

        @JavascriptInterface
        public void setColor(String css) {
            int c = parseCssColor(css);
            if (c != 0) runOnUiThread(() -> setBarColor(c));
        }
    }

    /** "rgb(9, 9, 11)" / "rgba(…)" → colour int, 0 if not parseable or transparent. */
    static int parseCssColor(String css) {
        if (css == null) return 0;
        java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("rgba?\\(\\s*(\\d+)[,\\s]+(\\d+)[,\\s]+(\\d+)(?:[,\\s/]+([\\d.]+))?").matcher(css);
        if (!m.find()) return 0;
        if (m.group(4) != null && Double.parseDouble(m.group(4)) == 0) return 0;
        return Color.rgb(Integer.parseInt(m.group(1)), Integer.parseInt(m.group(2)), Integer.parseInt(m.group(3)));
    }

    // ------------------------------------------------------------------ WebView callbacks

    private class Client extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri u = request.getUrl();
            String scheme = u.getScheme() == null ? "" : u.getScheme().toLowerCase();
            if ((scheme.equals("http") || scheme.equals("https")) && Prefs.sameServer(MainActivity.this, u)) return false;
            try {   // other sites (GitHub, docs), mailto: and so on open outside the app
                startActivity(new Intent(Intent.ACTION_VIEW, u));
            } catch (ActivityNotFoundException ignored) {
                // nothing can open it
            }
            return true;
        }

        @Override
        public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
            loadFailed = false;
            progress.setVisibility(View.VISIBLE);
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            progress.setVisibility(View.GONE);
            if (!loadFailed) error.setVisibility(View.GONE);
            CookieManager.getInstance().flush();
            view.evaluateJavascript(PAGE_SCRIPT, null);
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError err) {
            if (request.isForMainFrame()) showError(String.valueOf(err.getDescription()));
        }

        @Override
        public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError err) {
            String host = Uri.parse(err.getUrl()).getHost();
            String key = host + "|" + err.getCertificate().toString();
            if (trustedCerts.contains(key)) {
                handler.proceed();
                return;
            }
            int why;
            switch (err.getPrimaryError()) {
                case SslError.SSL_EXPIRED:
                case SslError.SSL_NOTYETVALID:
                    why = R.string.ssl_expired;
                    break;
                case SslError.SSL_IDMISMATCH:
                    why = R.string.ssl_mismatch;
                    break;
                case SslError.SSL_UNTRUSTED:
                    why = R.string.ssl_untrusted;
                    break;
                default:
                    why = R.string.ssl_other;
            }
            new AlertDialog.Builder(MainActivity.this)
                    .setTitle(R.string.ssl_title)
                    .setMessage(getString(R.string.ssl_text, host, getString(why)))
                    .setPositiveButton(R.string.ssl_continue, (d, w) -> {
                        trustedCerts.add(key);
                        handler.proceed();
                    })
                    .setNegativeButton(R.string.cancel, (d, w) -> {
                        handler.cancel();
                        showError(getString(R.string.ssl_title));
                    })
                    .setOnCancelListener(d -> {
                        handler.cancel();
                        showError(getString(R.string.ssl_title));
                    })
                    .show();
        }

        @Override
        public void onReceivedHttpAuthRequest(WebView view, HttpAuthHandler handler, String host, String realm) {
            LinearLayout box = new LinearLayout(MainActivity.this);
            box.setOrientation(LinearLayout.VERTICAL);
            int pad = (int) (20 * getResources().getDisplayMetrics().density);
            box.setPadding(pad, pad / 2, pad, 0);
            EditText user = new EditText(MainActivity.this);
            user.setHint(R.string.auth_user);
            user.setSingleLine(true);
            EditText pass = new EditText(MainActivity.this);
            pass.setHint(R.string.auth_pass);
            pass.setSingleLine(true);
            pass.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
            box.addView(user);
            box.addView(pass);
            new AlertDialog.Builder(MainActivity.this)
                    .setTitle(getString(R.string.auth_title, host))
                    .setView(box)
                    .setPositiveButton(R.string.login, (d, w) -> handler.proceed(user.getText().toString(), pass.getText().toString()))
                    .setNegativeButton(R.string.cancel, (d, w) -> handler.cancel())
                    .setOnCancelListener(d -> handler.cancel())
                    .show();
        }
    }

    private class Chrome extends WebChromeClient {
        @Override
        public void onProgressChanged(WebView view, int p) {
            progress.setProgress(p);
            progress.setVisibility(p < 100 ? View.VISIBLE : View.GONE);
        }

        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (fileCallback != null) fileCallback.onReceiveValue(null);
            fileCallback = callback;
            try {
                startActivityForResult(params.createIntent(), REQ_FILE);
            } catch (ActivityNotFoundException e) {
                fileCallback = null;
                return false;
            }
            return true;
        }
    }
}
