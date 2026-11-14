#!/usr/bin/env python3
"""Helpers for writing MCAT passages with original data figures.

A passage source file calls passage(...) with paragraphs, figures and questions,
then add_to_practice() writes the passages into practice.html's P array.

Figures use the same look as the existing passages (white card, lavender grid,
Nunito labels), so new and old passages match.
"""
from pathlib import Path
import json, math, re, html

FONT = 'font-family="Nunito,Arial,sans-serif"'
INK, MUTED, GRID = "#2d2a3e", "#6b6785", "#ece8f4"
COLORS = ["#e0577f", "#3a7fc4", "#2f9e77", "#f0a23b", "#7a5cc4"]
DASH = ["", "6 4", "2 3", "8 3 2 3", ""]


def _svgtxt(s):
    s = re.sub(r"<i>(.*?)</i>", r'<tspan font-style="italic">\1</tspan>', s)
    s = re.sub(r"<sub>(.*?)</sub>", r"<tspan dy='3' font-size='8'>\1</tspan><tspan dy='-3'> </tspan>", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"<tspan dy='-5' font-size='8'>\1</tspan><tspan dy='5'> </tspan>", s)
    return s


def _t(x, y, s, size=11, anchor="middle", fill=MUTED, weight=600, extra=""):
    s = _svgtxt(s)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
            f'font-weight="{weight}" {FONT}{extra}>{s}</text>')


def _l(x1, y1, x2, y2, stroke=INK, w=1.5, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{w}" stroke-linecap="round"{d}/>')


def _fmt(v):
    if abs(v) >= 1000 or v == int(v):
        return f"{int(v):,}".replace(",", ",") if abs(v) < 1e5 else f"{v:g}"
    return f"{v:g}"


def _frame(title, note, body, w, h):
    cap = f"<b>{title}</b>" + (f" · {note}" if note else "")
    return (f'<figure class="qfig"><figcaption class="fcap">{cap}</figcaption>'
            f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" '
            f'aria-label="{html.escape(re.sub("<[^>]+>", "", title))}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fff" rx="10"/>{body}</svg></figure>')


def _legend(names, x, y, colors, dashes=None, kind="line"):
    if not names or len(names) < 2:
        return ""
    wid = 30 + 7 * max(len(re.sub("<[^>]+>", "", n)) for n in names)
    out = [f'<rect x="{x - wid:.1f}" y="{y}" width="{wid}" height="{14 + 18 * len(names)}" fill="#fff" stroke="#e6e0f2" rx="6"/>']
    for i, n in enumerate(names):
        yy = y + 14 + 18 * i
        if kind == "bar":
            out.append(f'<rect x="{x - wid + 8:.1f}" y="{yy - 5}" width="14" height="10" fill="{colors[i]}" rx="2"/>')
        else:
            out.append(_l(x - wid + 8, yy, x - wid + 24, yy, colors[i], 3, (dashes or [""] * 9)[i]))
        out.append(_t(x - wid + 30, yy + 4, n, anchor="start", fill=INK))
    return "".join(out)


def _legend_rows(names, avail):
    rows, cur, w = [], [], 0
    for i, n in enumerate(names):
        wid = 34 + 6.6 * len(re.sub("<[^>]+>", "", n))
        if cur and w + wid > avail:
            rows.append(cur); cur, w = [], 0
        cur.append((i, n, wid)); w += wid
    if cur:
        rows.append(cur)
    return rows


def _top(series, x0, x1):
    """Top of the plot area: leaves room for one or more legend rows."""
    if len(series) < 2:
        return 16
    return 16 + 20 * len(_legend_rows([s[0] for s in series], x1 - x0))


def _hlegend(names, x0, x1, kind="line"):
    """Legend rows centered above the plot area (never overlaps data)."""
    if not names or len(names) < 2:
        return ""
    out = []
    for r, row in enumerate(_legend_rows(names, x1 - x0)):
        x = (x0 + x1) / 2 - sum(w for _, _, w in row) / 2
        y = 14 + 20 * r
        for i, n, wid in row:
            if kind == "bar":
                out.append(f'<rect x="{x:.1f}" y="{y - 5}" width="14" height="10" fill="{COLORS[i]}" rx="2"/>')
            else:
                out.append(_l(x, y, x + 18, y, COLORS[i], 3, DASH[i]))
            out.append(_t(x + 22, y + 4, n, anchor="start", fill=INK))
            x += wid
    return "".join(out)


def _yaxis(x0, x1, y0, y1, ymin, ymax, ticks, ylab, log=False, fmt=_fmt):
    out = []
    for v in ticks:
        f = (math.log10(v) - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) if log else (v - ymin) / (ymax - ymin)
        y = y0 - f * (y0 - y1)
        out.append(_l(x0, y, x1, y, GRID, 1))
        lab = (f"10<tspan dy='-5' font-size='8'>{int(round(math.log10(v)))}</tspan>" if log else fmt(v))
        out.append(_t(x0 - 6, y + 4, lab, anchor="end"))
    out.append(_l(x0, y1, x0, y0))
    out.append(_l(x0, y0, x1, y0))
    mid = (y0 + y1) / 2
    out.append(_t(16, mid, ylab, 12, fill=INK, extra=f' transform="rotate(-90 16 {mid:.1f})"'))
    return out


def bar(title, ylab, groups, series, ymax, step=None, note="", ymin=0, stars=None, w=460, h=300):
    """Grouped bar chart. series = [(name, [values], [errors or None])].
    stars = {group_index: "*"} puts a mark above the tallest bar of that group."""
    x0, x1, y0, y1 = 64, w - 14, h - 52, _top(series, 64, w - 14)
    step = step or (ymax - ymin) / 5
    ticks = [ymin + i * step for i in range(int(round((ymax - ymin) / step)) + 1)]
    out = _yaxis(x0, x1, y0, y1, ymin, ymax, ticks, ylab)
    if ymin < 0:
        out.append(_l(x0, Y0 := y0 - (0 - ymin) / (ymax - ymin) * (y0 - y1), x1, Y0, INK, 1.2))
    gw = (x1 - x0) / len(groups)
    bw = min(54, (gw - 24) / len(series))
    Y = lambda v: y0 - (v - ymin) / (ymax - ymin) * (y0 - y1)
    for gi, g in enumerate(groups):
        cx = x0 + gw * (gi + 0.5)
        lines = g.split("|")
        for li, s in enumerate(lines):
            out.append(_t(cx, y0 + 16 + 13 * li, s))
        top = y0
        for si, (name, vals, errs) in enumerate(series):
            v = vals[gi]
            if v is None:
                continue
            bx = cx - bw * len(series) / 2 + bw * si + 1
            base = Y(max(ymin, 0))
            out.append(f'<rect x="{bx:.1f}" y="{min(Y(v), base):.1f}" width="{bw - 2:.1f}" height="{abs(base - Y(v)):.1f}" fill="{COLORS[si]}" rx="3"/>')
            top = min(top, Y(v))
            if errs and errs[gi]:
                e = errs[gi]; mx = bx + (bw - 2) / 2
                out += [_l(mx, Y(v + e), mx, Y(max(ymin, v - e)), INK, 1.4), _l(mx - 6, Y(v + e), mx + 6, Y(v + e), INK, 1.4),
                        _l(mx - 6, Y(max(ymin, v - e)), mx + 6, Y(max(ymin, v - e)), INK, 1.4)]
                top = min(top, Y(v + e))
        if stars and gi in stars:
            out.append(_t(cx, top - 6, stars[gi], 16, fill=INK, weight=800))
    out.append(_hlegend([s[0] for s in series], x0, x1, "bar"))
    return _frame(title, note, "".join(out), w, h)


def line(title, xlab, ylab, series, xmax, ymax, xstep=None, ystep=None, xmin=0, ymin=0, note="",
         logy=False, points=True, w=460, h=300, legend_at="right", vlines=None, xfmt=_fmt, yfmt=_fmt):
    """Line chart. series = [(name, [(x, y), ...])]. vlines = [(x, label)]."""
    x0, x1, y0, y1 = 64, w - 14, h - 52, _top(series, 64, w - 14)
    if logy:
        ticks = [10 ** k for k in range(int(round(math.log10(ymin))), int(round(math.log10(ymax))) + 1)]
    else:
        ystep = ystep or (ymax - ymin) / 5
        ticks = [ymin + i * ystep for i in range(int(round((ymax - ymin) / ystep)) + 1)]
    out = _yaxis(x0, x1, y0, y1, ymin, ymax, ticks, ylab, logy, yfmt)
    if logy and len(ticks) <= 4:  # few decades: add labeled minor gridlines at 2x and 5x so values can be read
        for d in ticks:
            for m in (2, 5):
                v = d * m
                if ymin < v < ymax:
                    yy = y0 - (math.log10(v) - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) * (y0 - y1)
                    out.append(_l(x0, yy, x1, yy, "#f4f1fa", 1))
                    out.append(_t(x0 - 6, yy + 3, f"{v:,.0f}" if v >= 1 else f"{v:g}", 8, anchor="end", fill="#9a96b0"))
    X = lambda x: x0 + (x - xmin) / (xmax - xmin) * (x1 - x0)
    Y = (lambda v: y0 - (math.log10(v) - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) * (y0 - y1)) if logy \
        else (lambda v: y0 - (v - ymin) / (ymax - ymin) * (y0 - y1))
    xstep = xstep or (xmax - xmin) / 5
    i = 0
    while xmin + i * xstep <= xmax + 1e-9:
        v = xmin + i * xstep
        out.append(_l(X(v), y0, X(v), y0 + 4, INK, 1.2))
        out.append(_t(X(v), y0 + 17, xfmt(round(v, 6))))
        i += 1
    out.append(_t((x0 + x1) / 2, h - 10, xlab, 12, fill=INK))
    for vx, lab in (vlines or []):
        out.append(_l(X(vx), y1, X(vx), y0, MUTED, 1.2, "4 4"))
        right_room = x1 - X(vx) > 7 * len(re.sub("<[^>]+>", "", lab)) + 8
        out.append(_t(X(vx) + 4 if right_room else X(vx) - 4, y1 + 12, lab, 10, anchor="start" if right_room else "end"))
    for si, ser in enumerate(series):
        name, pts = ser[0], ser[1]
        c = COLORS[si]
        if len(ser) > 2 and ser[2] == "scatter":  # points only, e.g. individual participants
            for (x, y) in pts:
                out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="{c}" fill-opacity="0.55"/>')
            continue
        d = " ".join(f"{'M' if k == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for k, (x, y) in enumerate(pts))
        dash = f' stroke-dasharray="{DASH[si]}"' if DASH[si] else ""
        out.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.5" stroke-linejoin="round"{dash}/>')
        if points:
            for (x, y) in pts:
                out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.5" fill="{c}"/>')
    out.append(_hlegend([s[0] for s in series], x0, x1))
    return _frame(title, note, "".join(out), w, h)


def table(title, header, rows, note=""):
    cap = f"<b>{title}</b>" + (f" · {note}" if note else "")
    th = "".join(f"<th>{c}</th>" for c in header)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<figure class="qfig"><figcaption class="fcap">{cap}</figcaption><table class="data"><tr>{th}</tr>{tr}</table></figure>'


def eq(s):
    return f'<span class="eq">{s}</span>'


def passage(pid, s, subj, unit, title, parts, qs):
    """parts: list of strings; plain strings become <p> paragraphs, figure/table/eq HTML is kept as is.
    qs: list of dicts with keys q, right, wrong=[(choice, why_wrong) x3], e=[steps], k (1-4), t (optional tip).
    The right answer is stored first (a=0); the app shuffles choices when shown."""
    body = []
    for x in parts:
        body.append(x if x.lstrip().startswith("<") else f"<p>{x}</p>")
    out = []
    for q in qs:
        assert len(q["wrong"]) == 3, (pid, q["q"])
        item = {"q": q["q"], "o": [q["right"]] + [w[0] for w in q["wrong"]], "a": 0, "e": q["e"],
                "w": [""] + [w[1] for w in q["wrong"]], "k": q["k"]}
        if q.get("t"):
            item["t"] = q["t"]
        out.append(item)
    return {"id": pid, "s": s, "subj": subj, "unit": unit, "title": title, "text": "\n".join(body), "qs": out}


def add_to_practice(new):
    """Insert or replace passages (matched by id) in the bank (data/bank/p-*.js)."""
    import sys as _s; _s.path.insert(0, str(Path(__file__).resolve().parent)); import bank
    Q, P = bank.load()
    ids = {p["id"]: i for i, p in enumerate(P)}
    for p in new:
        words = len(re.sub(r"<svg.*?</svg>|<table.*?</table>|<[^>]+>", " ", p["text"], flags=re.S).split())
        if not 220 <= words <= 560: print("LENGTH WARNING", p["id"], words)
        assert len(p["qs"]) in (4, 5, 6, 7), p["id"]
        if p["id"] in ids:
            P[ids[p["id"]]] = p
        else:
            P.append(p)
    bank.save("P", P)
    return len(new)
