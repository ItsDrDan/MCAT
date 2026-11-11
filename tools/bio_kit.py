"""Biology figures for MCAT passages: pedigrees (standard symbols)."""
import re
from physics_kit import _txt, _line, _frame, COL, INK, MUTED

ROMAN = ["I", "II", "III", "IV", "V"]


def pedigree(title, people, couples=(), families=(), note="", w=460, slot=52, gen_h=92, legend=True):
    """people = {id: (generation 1-based, x_slot, 'M'|'F', status)}; status 'U' unaffected, 'A' affected,
    'C' carrier (dot), 'P' presymptomatic/unknown (shown with '?' beside).
    couples = [(id1, id2)]; families = [((id1, id2), [child ids])]. Each person is labeled like II-3,
    numbered left to right within a generation."""
    s = 13  # half-size of a symbol
    x0 = 56
    X = lambda slot_x: x0 + slot_x * slot
    Y = lambda g: 30 + (g - 1) * gen_h
    gens = max(p[0] for p in people.values())
    h = Y(gens) + 46 + (30 if legend else 0)
    b = []
    for g in range(1, gens + 1):
        b.append(_txt(18, Y(g) + 5, ROMAN[g - 1], 13, fill=MUTED))
    # number people left to right in each generation
    label = {}
    for g in range(1, gens + 1):
        row = sorted([k for k, p in people.items() if p[0] == g], key=lambda k: people[k][1])
        for i, k in enumerate(row):
            label[k] = f"{ROMAN[g - 1]}-{i + 1}"
    for a, c in couples:
        ga, xa = people[a][0], X(people[a][1]); xc = X(people[c][1])
        lo, hi = sorted((xa, xc))
        b.append(_line(lo + s, Y(ga), hi - s, Y(ga), INK, 1.8))
    for (a, c), kids in families:
        g = people[a][0]
        mx = (X(people[a][1]) + X(people[c][1])) / 2
        ys = Y(g) + gen_h / 2
        b.append(_line(mx, Y(g), mx, ys, INK, 1.8))
        xs = [X(people[k][1]) for k in kids]
        b.append(_line(min(xs + [mx]), ys, max(xs + [mx]), ys, INK, 1.8))
        for xk in xs:
            b.append(_line(xk, ys, xk, Y(g + 1) - s, INK, 1.8))
    for k, (g, sx, sex, st) in people.items():
        x, y = X(sx), Y(g)
        fill = INK if st == "A" else "#fff"
        if sex == "M":
            b.append(f'<rect x="{x - s}" y="{y - s}" width="{2 * s}" height="{2 * s}" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="{s}" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
        if st == "C":
            b.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')
        if st == "P":
            b.append(_txt(x + s + 7, y + 5, "?", 13, "start", COL["pink"]))
        b.append(_txt(x, y + s + 15, label[k], 10, fill=MUTED, weight=600))
    if legend:
        ly = h - 14
        items = [("M", "U", "unaffected male"), ("F", "U", "unaffected female"), ("M", "A", "affected")]
        if any(p[3] == "C" for p in people.values()):
            items.append(("F", "C", "carrier"))
        x = 30
        for sex, st, text in items:
            fill = INK if st == "A" else "#fff"
            if sex == "M":
                b.append(f'<rect x="{x - 7}" y="{ly - 7}" width="14" height="14" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>')
            else:
                b.append(f'<circle cx="{x}" cy="{ly}" r="7" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>')
            if st == "C":
                b.append(f'<circle cx="{x}" cy="{ly}" r="2.5" fill="{INK}"/>')
            b.append(_txt(x + 12, ly + 4, text, 10, "start", MUTED, 600))
            x += 30 + 6.2 * len(text)
    return _frame(title, note, "".join(b), w, h)


def gel(title, lanes, ladder=None, note="", w=None, h=300, top_label="wells", unit="bp"):
    """Agarose/SDS gel. lanes = [(label, [sizes])]; ladder = [sizes] drawn as lane 'M'. Bands are placed on a log scale."""
    import math
    allv = [s for _, ss in lanes for s in ss] + (ladder or [])
    lo, hi = min(allv) * 0.7, max(allv) * 1.3
    L = ([("M", ladder)] if ladder else []) + lanes
    lw = 64; w = w or (60 + lw * len(L) + 70)
    y0, y1 = 46, h - 24
    Y = lambda s: y0 + (math.log10(hi) - math.log10(s)) / (math.log10(hi) - math.log10(lo)) * (y1 - y0)
    b = [f'<rect x="40" y="30" width="{lw * len(L) + 20}" height="{h - 44}" rx="8" fill="#eef1f8" stroke="#c9cfe0"/>']
    for i, (lab, sizes) in enumerate(L):
        x = 50 + i * lw
        b.append(f'<rect x="{x + 8}" y="34" width="{lw - 16}" height="7" fill="#9aa3bb"/>')
        b.append(_txt(x + lw / 2, 22, lab, 12))
        for s in sizes:
            col = "#7a5cc4" if lab != "M" else "#9aa3bb"
            b.append(f'<rect x="{x + 8}" y="{Y(s) - 3:.1f}" width="{lw - 16}" height="6" rx="2" fill="{col}"/>')
    if ladder:
        for s in ladder:
            b.append(_txt(50 + lw * len(L) + 16, Y(s) + 4, f"{s:,}", 10, "start", MUTED, 600))
        b.append(_txt(50 + lw * len(L) + 16, y0 - 14, unit, 10, "start", MUTED, 600))
    b.append(_txt(26, y0 + 4, "−", 14, fill=COL["blue"]) + _txt(26, y1, "+", 14, fill=COL["pink"]))
    return _frame(title, note, "".join(b), w, h)


def punnett(title, top, side, cells=None, note=""):
    """Punnett square grid with gametes on the top and side. cells = 2-D list of strings (or None to leave blank)."""
    n, m = len(top), len(side)
    c = 62; x0, y0 = 70, 40
    w, h = x0 + c * n + 20, y0 + c * m + 20
    b = []
    for j, g in enumerate(top):
        b.append(_txt(x0 + c * j + c / 2, y0 - 12, g, 14, fill=COL["blue"]))
    for i, g in enumerate(side):
        b.append(_txt(x0 - 12, y0 + c * i + c / 2 + 5, g, 14, "end", COL["pink"]))
    for i in range(m):
        for j in range(n):
            b.append(f'<rect x="{x0 + c * j}" y="{y0 + c * i}" width="{c}" height="{c}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
            if cells and cells[i][j]:
                b.append(_txt(x0 + c * j + c / 2, y0 + c * i + c / 2 + 5, cells[i][j], 13))
    return _frame(title, note, "".join(b), w, h)


def ecg(title, qrs_times, p_times=None, pr=0.16, seconds=4.0, note="", labels=None, pxs=120):
    """ECG strip on standard paper (small box 0.04 s, large box 0.20 s; 0.1 mV per small box).
    qrs_times = times (s) of each R peak; p_times = times of P-wave peaks (default: R − pr).
    labels = {letter: (t, mV)} to place letters on waves."""
    import math
    w = int(seconds * pxs) + 30; h = 200
    x0, base = 15, 120
    X = lambda t: x0 + t * pxs
    Ym = lambda mv: base - mv * 60
    b = []
    # paper grid
    t = 0.0
    k = 0
    while t <= seconds + 1e-9:
        major = k % 5 == 0
        b.append(f'<line x1="{X(t):.1f}" y1="10" x2="{X(t):.1f}" y2="{h - 26}" stroke="{"#f2a7b8" if major else "#fbe0e6"}" stroke-width="{1.2 if major else .6}"/>')
        t += 0.04; k += 1
    for j in range(0, 40):
        y = 10 + j * 0.1 * 60
        if y > h - 26: break
        b.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{X(seconds):.1f}" y2="{y:.1f}" stroke="{"#f2a7b8" if j % 5 == 0 else "#fbe0e6"}" stroke-width="{1.2 if j % 5 == 0 else .6}"/>')
    p_times = p_times if p_times is not None else [r - pr for r in qrs_times]
    g = lambda t, c, s, a: a * math.exp(-((t - c) / s) ** 2)
    pts = []
    for i in range(int(seconds * 500) + 1):
        tt = i / 500
        v = 0
        for r in qrs_times:
            v += g(tt, r - 0.025, 0.008, -0.12) + g(tt, r, 0.011, 1.4) + g(tt, r + 0.03, 0.01, -0.3) + g(tt, r + 0.28, 0.045, 0.3)
        for p in p_times:
            v += g(tt, p, 0.025, 0.16)
        pts.append((X(tt), Ym(v)))
    b.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    for s in range(int(seconds) + 1):
        b.append(_txt(X(s), h - 10, f"{s} s", 10, fill=MUTED, weight=600))
    for lab, (tt, mv) in (labels or {}).items():
        b.append(_txt(X(tt), Ym(mv) - 6, lab, 13, fill=COL["purple"]))
    return _frame(title, note or "paper speed 25 mm s⁻¹: small box = 0.04 s, large box = 0.20 s", "".join(b), w, h)
