"""Versionshinweise aus CHANGELOG.md lesen und als HTML anzeigen (Seite /changelog und „Neu in dieser Version“)."""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = re.compile(r"^## (\d+\.\d+\.\d+)\s*[–-]\s*(.*)$")
_cache = {}


def _files(lang):
    names = (["CHANGELOG.de.md", "CHANGELOG.md"] if lang == "de" else ["CHANGELOG.en.md", "CHANGELOG.md", "CHANGELOG.de.md"])
    for d in (HERE, os.path.dirname(HERE)):
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return p
    return None


def vtuple(v):
    try:
        return tuple(int(x) for x in str(v).split(".")[:3])
    except ValueError:
        return (0, 0, 0)


def entries(lang="de"):
    """[{version, date, md}] neueste zuerst."""
    path = _files(lang)
    if not path:
        return []
    mt = os.path.getmtime(path)
    hit = _cache.get(path)
    if hit and hit[0] == mt:
        return hit[1]
    out, cur = [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HEAD.match(line.rstrip("\n"))
            if m:
                cur = {"version": m.group(1), "date": m.group(2).strip(), "lines": []}
                out.append(cur)
            elif cur is not None:
                cur["lines"].append(line.rstrip("\n"))
    for e in out:
        e["md"] = "\n".join(e.pop("lines")).strip()
    _cache[path] = (mt, out)
    return out


def between(lang, after, upto):
    """Eintraege mit after < Version <= upto (after leer = nur upto)."""
    a, u = vtuple(after) if after else None, vtuple(upto)
    res = []
    for e in entries(lang):
        v = vtuple(e["version"])
        if v > u:
            continue
        if a is None:
            if v == u:
                res.append(e)
        elif v > a:
            res.append(e)
    return res


def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def to_html(md):
    """Kleines Markdown: Absaetze, **fett**, `code`, Links, Listen mit -, eingerueckte Fortsetzungszeilen."""
    out, in_list, para = [], False, []

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para.clear()
    items = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith(("- ", "* ")):
            flush_para()
            items.append(s[2:])
            in_list = True
        elif s and in_list and line.startswith(" "):
            items[-1] += " " + s
        else:
            if items:
                out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
                items = []
            in_list = False
            if not s:
                flush_para()
            elif s.startswith("### "):
                flush_para()
                out.append(f"<h4>{_inline(s[4:])}</h4>")
            else:
                para.append(s)
    if items:
        out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
    flush_para()
    return "\n".join(out)
