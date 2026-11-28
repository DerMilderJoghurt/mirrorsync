"""Laufbericht als PDF (seit 1.58.0), ohne Zusatzpakete.

Kleiner PDF-Schreiber mit den Standardschriften Helvetica und Courier (WinAnsi/cp1252: deckt Deutsch, Englisch,
Franzoesisch, Spanisch und Italienisch ab). Zeichen ausserhalb von cp1252 (z. B. Emojis) werden weggelassen."""
import datetime
import zlib

W, H = 595.28, 841.89          # A4 in Punkt
M = 48                          # Rand
_HELV = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556, 556, 556,
         556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
         667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556,
         556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]
FONTS = {"R": "Helvetica", "B": "Helvetica-Bold", "M": "Courier"}
COLORS = {"": (0.1, 0.1, 0.12), "mut": (0.42, 0.45, 0.5), "ok": (0.09, 0.5, 0.24), "err": (0.75, 0.13, 0.13),
          "warn": (0.7, 0.42, 0.0), "acc": (0.31, 0.27, 0.9)}


def _clean(text):
    out = []
    for ch in str(text):
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append({"→": "->", "⇄": "<->", "–": "-", "…": "...", "✔": "", "✖": "", "≥": ">=", "≤": "<="}.get(ch, ""))
    return "".join(out).replace("\t", "    ")


def _width(text, font, size):
    if font == "M":
        return len(text) * 0.6 * size
    f = 1.06 if font == "B" else 1.0
    w = 0
    for ch in text:
        o = ord(ch)
        w += _HELV[o - 32] if 32 <= o <= 126 else 556
    return w * f * size / 1000


def _esc(text):
    raw = _clean(text).encode("cp1252", "replace")
    return raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


class Doc:
    def __init__(self, footer=""):
        self.pages, self.cur, self.y = [], None, 0
        self.footer = footer
        self.new_page()

    def new_page(self):
        self.cur = []
        self.pages.append(self.cur)
        self.y = H - M

    def _need(self, h):
        if self.y - h < M + 20:
            self.new_page()

    def _put(self, x, y, text, font, size, color):
        r, g, b = COLORS.get(color, COLORS[""])
        self.cur.append(b"BT %.3f %.3f %.3f rg /F%s %.1f Tf %.2f %.2f Td (" % (r, g, b, font.encode(), size, x, y) + _esc(text) + b") Tj ET")

    def wrap(self, text, font="R", size=10, width=None):
        width = width or (W - 2 * M)
        lines = []
        for para in _clean(text).split("\n"):
            words, line = para.split(" "), ""
            for wd in words:
                cand = (line + " " + wd) if line else wd
                if _width(cand, font, size) <= width:
                    line = cand
                    continue
                if line:
                    lines.append(line)
                while _width(wd, font, size) > width:   # sehr lange Woerter (Pfade) hart umbrechen
                    n = max(1, int(len(wd) * width / max(1, _width(wd, font, size))))
                    lines.append(wd[:n])
                    wd = wd[n:]
                line = wd
            lines.append(line)
        return lines

    def text(self, text, font="R", size=10, color="", indent=0, gap=0.3):
        lh = size * 1.32
        for ln in self.wrap(text, font, size, W - 2 * M - indent):
            self._need(lh)
            self.y -= lh
            self._put(M + indent, self.y, ln, font, size, color)
        self.y -= size * gap

    def title(self, text, size=18):
        self.text(text, "B", size, "acc", gap=0.5)

    def heading(self, text, count=None):
        self._need(40)
        self.y -= 8
        self.text(text + (f"  ({count})" if count is not None else ""), "B", 12.5, gap=0.2)
        self.rule()

    def rule(self):
        self.cur.append(b"0.85 0.86 0.88 RG 0.6 w %.2f %.2f m %.2f %.2f l S" % (M, self.y, W - M, self.y))
        self.y -= 6

    def rows(self, pairs, key_w=150):
        """Tabelle aus (Bezeichnung, Wert[, Farbe])."""
        for p in pairs:
            label, value = p[0], p[1]
            color = p[2] if len(p) > 2 else ""
            vl = self.wrap(str(value), "R", 10, W - 2 * M - key_w)
            self._need(13.2 * len(vl))
            self.y -= 13.2
            self._put(M, self.y, label, "B", 10, "mut")
            for i, ln in enumerate(vl):
                if i:
                    self.y -= 13.2
                self._put(M + key_w, self.y, ln, "R", 10, color)
            self.y -= 2

    def lines(self, items, color="", size=8.5):
        for it in items:
            self.text(it, "M", size, color, indent=6, gap=0.05)

    def build(self):
        objs = []

        def add(b):
            objs.append(b)
            return len(objs)
        cat = add(None)
        pages_id = add(None)
        fonts = {}
        for key, name in FONTS.items():
            fonts[key] = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>" % name.encode())
        res = b"<< /Font << " + b" ".join(b"/F%s %d 0 R" % (k.encode(), v) for k, v in fonts.items()) + b" >> >>"
        kids = []
        n = len(self.pages)
        for i, content in enumerate(self.pages, 1):
            foot = []
            r, g, b = COLORS["mut"]
            ft = f"{self.footer}  ·  {i}/{n}" if self.footer else f"{i}/{n}"
            foot.append(b"BT %.3f %.3f %.3f rg /FR 8 Tf %.2f %.2f Td (" % (r, g, b, M, M - 18) + _esc(ft) + b") Tj ET")
            stream = zlib.compress(b"\n".join(content + foot))
            cid = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(stream) + stream + b"\nendstream")
            kids.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] /Resources %s /Contents %d 0 R >>"
                            % (pages_id, W, H, res, cid)))
        objs[cat - 1] = b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id
        objs[pages_id - 1] = b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % k for k in kids) + b"] /Count %d >>" % len(kids)
        info = add(b"<< /Producer (MirrorSync) /CreationDate (D:" + datetime.datetime.now().strftime("%Y%m%d%H%M%S").encode() + b") >>")
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offs = []
        for i, o in enumerate(objs, 1):
            offs.append(len(out))
            out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
        for o in offs:
            out += b"%010d 00000 n \n" % o
        out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, cat, info, xref)
        return bytes(out)
