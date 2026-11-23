"""Uebersetzungen. Quelltexte sind Deutsch, jede Sprache ist eine JSON-Datei in app/i18n/<code>.json:

    {"_meta": {"name": "English", "code": "en"}, "Deutscher Text": "Translated text", ...}

Neue Sprache: en.json kopieren, z. B. als nl.json, _meta anpassen und die Werte uebersetzen. Fehlt ein Eintrag,
wird Englisch und danach Deutsch angezeigt. Platzhalter {0}, {1} … und {name} sowie HTML-Tags und {{ … }} muessen
unveraendert bleiben.

Wie uebersetzt wird:
* Templates: Beim Laden wird jeder Text zwischen Tags (mit Inline-Tags wie <b> und {{ … }} als eine Einheit),
  title/placeholder/aria-label und Texte in JavaScript-Strings ersetzt, wenn sie im Katalog stehen. Pro Sprache
  entsteht eine eigene Template-Fassung ("en::index.html").
* Ausgaben {{ … }} laufen durch t(): ein genauer Treffer im Katalog oder ein Muster mit {0} (z. B. Meldungen
  aus dem Programm wie "Sicherung {0} gelöscht.") wird uebersetzt, alles andere bleibt unveraendert.
* Im Python-Code: t("Text") oder t("Text {0}", wert) mit der Sprache der aktuellen Anfrage."""
import json
import os
import re
import threading

SOURCE = "de"
DEFAULT = "en"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")
_cat = {}          # code -> {quelltext: uebersetzung}
_pat = {}          # code -> [(regex, schluessel, laengster Textteil)]
_names = {SOURCE: "Deutsch"}
_lock = threading.Lock()
_local = threading.local()
default_lang = DEFAULT     # Systemsprache (Einstellung "language"), von app.py gesetzt
resolver = None            # Funktion: Sprache der aktuellen Anfrage oder None
PH = re.compile(r"\{(\d+)\}")


def load():
    global _cat, _pat
    cats, pats = {}, {}
    if os.path.isdir(DIR):
        for f in sorted(os.listdir(DIR)):
            if not f.endswith(".json"):
                continue
            code = f[:-5]
            try:
                with open(os.path.join(DIR, f), encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, ValueError) as e:
                print(f"Sprachdatei {f} nicht lesbar: {e}", flush=True)
                continue
            meta = data.pop("_meta", {}) if isinstance(data.get("_meta"), dict) else {}
            _names[code] = meta.get("name") or code
            cats[code] = {k: v for k, v in data.items() if isinstance(v, str) and v}
    for code, cat in cats.items():
        lst = []
        for k in cat:
            if PH.search(k):
                parts = PH.split(k)
                lit = [p for i, p in enumerate(parts) if i % 2 == 0]
                longest = max(lit, key=len)
                if len("".join(lit).strip()) < 4:
                    continue
                rx = "".join(re.escape(p) if i % 2 == 0 else f"(?P<g{p}_{i}>.+?)" for i, p in enumerate(parts))
                lst.append((re.compile("^" + rx + "$", re.S), k, longest))
        lst.sort(key=lambda x: -len(x[2]))
        pats[code] = lst
    with _lock:
        _cat, _pat = cats, pats


def languages():
    """[(code, Name)] fuer Auswahllisten, Englisch zuerst."""
    codes = sorted(set(_cat) | {SOURCE}, key=lambda c: (c != DEFAULT, _names.get(c, c).lower()))
    return [(c, _names.get(c, c)) for c in codes]


def valid(code):
    return code == SOURCE or code in _cat


def current():
    if resolver:
        try:
            v = resolver()
            if v:
                return v
        except Exception:
            pass
    return getattr(_local, "lang", None) or default_lang


def set_current(code):
    _local.lang = code if valid(code or "") else None


def _lookup(text, lang):
    if lang == SOURCE:
        return None
    hit = _cat.get(lang, {}).get(text)
    if hit is None and lang != DEFAULT:
        hit = _cat.get(DEFAULT, {}).get(text)
    return hit


def _match(text, lang, depth):
    for code in ([lang, DEFAULT] if lang != DEFAULT else [lang]):
        for rx, key, longest in _pat.get(code, ()):
            if longest and longest not in text:
                continue
            m = rx.match(text)
            if not m:
                continue
            tr = _cat[code][key]
            vals = {}
            for name, v in m.groupdict().items():
                idx = name[1:].split("_")[0]
                vals[idx] = translate(v, lang, depth + 1) if depth < 3 else v
            return PH.sub(lambda mm: vals.get(mm.group(1), mm.group(0)), tr)
    return None


def translate(text, lang=None, depth=0):
    """Text uebersetzen, wenn er im Katalog steht oder auf ein Muster passt; sonst unveraendert."""
    lang = lang or current()
    if lang == SOURCE or not isinstance(text, str) or not text or len(text) > 3000:
        return text
    s = text.strip()
    if not s:
        return text
    hit = _lookup(s, lang)
    if hit is None:
        hit = _match(s, lang, depth)
    if hit is None:
        if _MISS and depth == 0 and LETTER.search(s):
            _miss(s)
        return text
    if s != text:   # Leerzeichen am Rand erhalten
        lead = text[:len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        return lead + hit + trail
    return hit


_MISS = os.environ.get("I18N_MISSES")   # Entwicklerhilfe: nicht gefundene Texte in diese Datei schreiben


def _miss(s):
    try:
        with open(_MISS, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    except OSError:
        pass


def t(text, *args, lang=None, **kw):
    """Uebersetzen und Platzhalter fuellen: t("Sicherung {0} gelöscht.", name)."""
    lang = lang or current()
    out = _lookup(text, lang) if lang != SOURCE else None
    out = text if out is None else out
    if args:
        out = PH.sub(lambda m: str(args[int(m.group(1))]) if int(m.group(1)) < len(args) else m.group(0), out)
    if kw:
        for k, v in kw.items():
            out = out.replace("{" + k + "}", str(v))
    return out


def translate_deep(obj, keys=("description", "summary", "instructions", "title"), lists=("tags",), lang=None):
    """Texte in verschachtelten Daten (OpenAPI, MCP-Tools) uebersetzen: nur Werte unter den genannten Schluesseln."""
    lang = lang or current()
    if lang == SOURCE:
        return obj
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, str) and k in keys:
                out[k] = translate(v, lang)
            elif isinstance(v, list) and k in lists:
                out[k] = [translate(x, lang) if isinstance(x, str) else x for x in v]
            else:
                out[k] = translate_deep(v, keys, lists, lang)
        return out
    if isinstance(obj, list):
        return [translate_deep(x, keys, lists, lang) for x in obj]
    return obj


def from_header(value):
    """Erste passende Sprache aus Accept-Language ('es-ES,es;q=0.9,en;q=0.8') oder None."""
    for part in (value or "").split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code and valid(code):
            return code
    return None


# ---------------------------------------------------------------- Templates
INLINE = {"b", "i", "strong", "em", "code", "a", "small", "br", "kbd", "u", "sup", "sub"}
TOKEN = re.compile(r"(\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}|<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>"
                   r"|<[a-zA-Z/!](?:\"[^\"]*\"|'[^']*'|[^>{\"']|\{\{.*?\}\}|\{%.*?%\}|\{(?![{%]))*>)", re.S)
ATTR = re.compile(r"""(\s)(placeholder|title|aria-label|alt|label|data-confirm|data-title|data-t|data-l|onclick|onsubmit|onchange|oninput|value)=(["'])(.*?)\3""", re.S)
JS_STR = re.compile(r"""'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\]|\\.)*)`""", re.S)
LETTER = re.compile(r"[A-Za-zÄÖÜäöüß]{2,}")


def _tag_name(tok):
    m = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
    return m.group(1).lower() if m else ""


def _plain(unit):
    return re.sub(r"\{\{.*?\}\}|<[^>]*>", " ", unit, flags=re.S)


def _units(src):
    """Liefert Tokens [(art, text)] und Einheiten [(start_idx, end_idx)] (Index in Tokens, inklusive)."""
    toks, pos = [], 0
    for m in TOKEN.finditer(src):
        if m.start() > pos:
            toks.append(("text", src[pos:m.start()]))
        tok = m.group(0)
        if tok.startswith("{{"):
            kind = "expr"
        elif tok.startswith("{%") or tok.startswith("{#") or tok.startswith("<!--"):
            kind = "ctl"
        elif tok.lower().startswith("<script") or tok.lower().startswith("<style"):
            kind = "script" if tok.lower().startswith("<script") else "ctl"
        else:
            # Inline-Tags gehoeren zum Satz, ausser sie tragen selbst Template-Logik (z. B. Navigation)
            kind = "inline" if _tag_name(tok) in INLINE and "{{" not in tok and "{%" not in tok else "tag"
        toks.append((kind, tok))
        pos = m.end()
    if pos < len(src):
        toks.append(("text", src[pos:]))
    units, run = [], []

    def flush():
        if run:
            a, b = run[0], run[-1]
            # Rand: Leerzeichen-Text und nicht geoeffnete/geschlossene Tags vorn/hinten abschneiden
            def edge(i):   # Leerraum und Symbole ({{ ICON.x }}) am Rand gehoeren nicht zum Text
                k, v = toks[i]
                return (k == "text" and not v.strip()) or (k == "expr" and v.replace(" ", "").startswith("{{ICON.")) \
                    or (k == "inline" and _tag_name(v) == "br")
            def opening(i):
                return toks[i][0] == "inline" and not toks[i][1].startswith("</") and _tag_name(toks[i][1]) != "br"

            def closing(i):
                return toks[i][0] == "inline" and toks[i][1].startswith("</")

            def count(name, lo, hi, close):
                return sum(1 for j in range(lo, hi + 1) if toks[j][0] == "inline" and _tag_name(toks[j][1]) == name
                           and toks[j][1].startswith("</") == close)
            changed = True
            while changed and a <= b:   # Leerraum, Symbole und nicht passende Tags am Rand abschneiden
                changed = False
                if edge(a) or closing(a) or (opening(a) and count(_tag_name(toks[a][1]), a, b, True) == 0):
                    a += 1
                    changed = True
                elif edge(b) or (opening(b)) or (closing(b) and count(_tag_name(toks[b][1]), a, b, False) == 0):
                    b -= 1
                    changed = True
                elif a < b and opening(a) and closing(b) and _tag_name(toks[a][1]) == _tag_name(toks[b][1]) \
                        and count(_tag_name(toks[a][1]), a, b, False) == 1:
                    a, b = a + 1, b - 1   # umschliessendes <a>…</a> oder <b>…</b> gehoert nicht zum Text
                    changed = True
            if a <= b:
                unit = "".join(t for _, t in toks[a:b + 1]).strip()
                if LETTER.search(_plain(unit)):
                    units.append((a, b))
        run.clear()
    for i, (kind, _) in enumerate(toks):
        if kind in ("text", "expr", "inline"):
            run.append(i)
        else:
            flush()
    flush()
    return toks, units


def _js_strings(code):
    for m in JS_STR.finditer(code):
        q = m.group(0)[0]
        body = m.group(1) if q == "'" else m.group(2) if q == '"' else m.group(3)
        yield m.start(), m.end(), q, body


def _js_escape(text, q):
    return text.replace("\\", "\\\\").replace(q, "\\" + q) if q != "`" else text.replace("`", "\\`")


def _tr_js(code, cat):
    out, pos = [], 0
    for a, b, q, body in _js_strings(code):
        tr = cat.get(body)
        if tr is not None:
            out.append(code[pos:a] + q + _js_escape(tr, q) + q)
            pos = b
    out.append(code[pos:])
    return "".join(out)


def _tr_tag(tok, cat):
    def sub(m):
        sp, name, q, val = m.groups()
        if name.startswith("on"):
            new = _tr_js(val.replace("&quot;", '"'), cat)
            if new == val.replace("&quot;", '"'):
                return m.group(0)
            new = new.replace('"', "&quot;") if q == '"' else new
            return f"{sp}{name}={q}{new}{q}"
        if name == "value" and not re.search(r"type=[\"']?(submit|button)", tok):
            return m.group(0)
        tr = cat.get(val.strip())
        if tr is None:
            return m.group(0)
        tr = tr.replace(q, "&quot;" if q == '"' else "&#39;")
        return f"{sp}{name}={q}{tr}{q}"
    return ATTR.sub(sub, tok)


def translate_source(src, cat):
    """Template-Quelltext in eine Sprache uebersetzen (cat: Katalog dieser Sprache, mit Englisch aufgefuellt)."""
    toks, units = _units(src)
    out = [t for _, t in toks]
    done = set()
    for a, b in units:
        raw = "".join(t for _, t in toks[a:b + 1])
        key = raw.strip()
        tr = cat.get(key)
        if tr is not None:
            lead = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            out[a] = lead + tr + trail
            for i in range(a + 1, b + 1):
                out[i] = ""
            done.update(range(a, b + 1))
    for i, (kind, tok) in enumerate(toks):
        if i in done:
            continue
        if kind in ("tag", "inline"):
            out[i] = _tr_tag(tok, cat)
        elif kind == "script":
            m = re.match(r"(<script\b[^>]*>)(.*)(</script\s*>)$", tok, re.S)
            if m:
                out[i] = m.group(1) + _tr_js(m.group(2), cat) + m.group(3)
    res = "".join(out)
    # Verweise auf andere Templates auf dieselbe Sprache umbiegen
    return res


def catalog_for(lang):
    if lang == SOURCE:
        return {}
    cat = dict(_cat.get(DEFAULT, {}))
    cat.update(_cat.get(lang, {}))
    return cat


# ---------------------------------------------------------------- Werkzeug: Texte sammeln (python -m i18n)
def extract_templates(templates):
    """Alle uebersetzbaren Einheiten aus den Templates (fuer die Pflege der Kataloge)."""
    found = {}
    for name, src in templates.items():
        toks, units = _units(src)
        for a, b in units:
            found.setdefault("".join(t for _, t in toks[a:b + 1]).strip(), name)
        for kind, tok in toks:
            if kind in ("tag", "inline"):
                for m in ATTR.finditer(tok):
                    _, an, _, val = m.groups()
                    if an.startswith("on"):
                        for _, _, _, body in _js_strings(val.replace("&quot;", '"')):
                            if LETTER.search(body) and " " in body:
                                found.setdefault(body, name + " (js)")
                    elif an != "value" and LETTER.search(_plain(val)):
                        found.setdefault(val.strip(), name + " (attr)")
            elif kind in ("expr", "ctl") and not tok.startswith("{#"):
                for _, _, _, body in _js_strings(tok):
                    if re.search(r"[A-Za-zäöüß]{2}", body) and (re.search(r"[äöüßÄÖÜ ]", body) or body[:1].isupper()):
                        found.setdefault(body, name + " (expr)")
            elif kind == "script":
                for _, _, _, body in _js_strings(tok):
                    if LETTER.search(body) and re.search(r"[A-ZÄÖÜ][a-zäöüß]|[äöüßÄÖÜ…]|[a-z]{3,} [a-z]", body) \
                            and not re.match(r"^[#.\[/]|^[a-z-]+$|^\w+/\w+", body):
                        found.setdefault(body, name + " (js)")
    return found


load()
