"""Gen chem and biochem figures for MCAT passages: reaction energy diagrams, phase diagrams,
metabolic cycles/pathways and an electron transport chain sketch. Same look as passage_kit."""
import math, re
from physics_kit import _txt, _line, _arrow, _frame, COL, INK, MUTED, GRID

PAL = [COL["pink"], COL["blue"], COL["green"], COL["orange"], COL["purple"]]
DASH = ["", "7 4", "2 3", "8 3 2 3"]


def _smooth(pts):
    """Path through the given points with flat tangents at each point (good for energy profiles)."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx = (x1 - x0) * .5
        d += f" C{x0 + dx:.1f},{y0:.1f} {x1 - dx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    return d


def energy_diagram(title, profiles, ymin, ymax, note="", ylab="Energy (kJ mol⁻¹)", w=460, h=300, labels=(), marks=(), xlab="Reaction progress", ystep=None):
    """profiles = [(name, [E0, E1, ...])], energies at evenly spaced stations (reactant, TS, intermediate, TS, product...).
    labels = [(station_index, energy, text)] text placed near a point; marks = [(station, E_low, E_high, text)] vertical double arrows."""
    x0, x1, y0, y1 = 70, w - 20, h - 40, 24 + 18 * (len(profiles) > 1)
    n = max(len(p[1]) for p in profiles)
    X = lambda i: x0 + 30 + i * (x1 - x0 - 60) / (n - 1)
    Y = lambda e: y0 - (e - ymin) / (ymax - ymin) * (y0 - y1)
    b = [_line(x0, y1 - 6, x0, y0, INK, 1.6), _line(x0, y0, x1, y0, INK, 1.6),
         f'<text x="16" y="{(y0 + y1) / 2:.1f}" font-size="12" text-anchor="middle" fill="{INK}" font-weight="700" font-family="Nunito,Arial,sans-serif" transform="rotate(-90 16 {(y0 + y1) / 2:.1f})">{ylab}</text>',
         _txt((x0 + x1) / 2, h - 12, xlab, 12)]
    step = ystep or (ymax - ymin) / 5
    for k in range(int(round((ymax - ymin) / step)) + 1):
        e = ymin + k * step
        b.append(_line(x0 - 4, Y(e), x0, Y(e), INK, 1.2))
        b.append(_txt(x0 - 7, Y(e) + 4, f"{e:g}", 10, "end", MUTED, 600))
    for i, (name, es) in enumerate(profiles):
        pts = [(X(k), Y(e)) for k, e in enumerate(es)]
        dash = f' stroke-dasharray="{DASH[i]}"' if DASH[i] else ""
        b.append(f'<path d="{_smooth(pts)}" fill="none" stroke="{PAL[i]}" stroke-width="3"{dash}/>')
    if len(profiles) > 1:
        x = x0 + 10
        for i, (name, _) in enumerate(profiles):
            dash = f' stroke-dasharray="{DASH[i]}"' if DASH[i] else ""
            b.append(f'<line x1="{x}" y1="14" x2="{x + 20}" y2="14" stroke="{PAL[i]}" stroke-width="3"{dash}/>')
            b.append(_txt(x + 25, 18, name, 11, "start"))
            x += 34 + 6.4 * len(re.sub("<[^>]+>", "", name))
    for st, e, text in labels:
        b.append(_txt(X(st), Y(e) - 9, text, 11, fill=INK))
    for st, lo, hi, text in marks:
        xx = X(st)
        b.append(_line(xx - 18, Y(lo), xx + 18, Y(lo), MUTED, 1, "3 3"))
        b.append(_arrow(xx, Y(lo), xx, Y(hi) + 2, MUTED, 1.6, 7) + _arrow(xx, Y(hi), xx, Y(lo) - 2, MUTED, 1.6, 7))
        b.append(_txt(xx + 6, (Y(lo) + Y(hi)) / 2 + 4, text, 11, "start", MUTED))
    return _frame(title, note, "".join(b), w, h)


def _pw(anchors):
    """Piecewise-linear map through sorted (value, pixel) anchors."""
    anchors = sorted(anchors)
    def f(v):
        for (a, pa), (b, pb) in zip(anchors, anchors[1:]):
            if v <= b or (b, pb) == anchors[-1]:
                return pa + (v - a) / (b - a) * (pb - pa)
    return f


def phase_diagram(title, triple, critical, fusion_slope, Tr, Pr, note="", points=(), w=460, h=320, Tlab="Temperature (°C)", Plab="Pressure (atm)",
                  path=None, ticksT=(), ticksP=(), extraT=(), extraP=()):
    """Schematic phase diagram (not to scale): the triple and critical points sit at fixed spots and the axes are
    stretched piecewise between labeled values. triple/critical = (T, P); Tr, Pr = (min, max) ranges.
    fusion_slope = 'negative' (water) or 'positive'. points = [(T, P, 'A')]; path = [(T, P), ...] drawn as arrows.
    extraT / extraP = additional (value, fraction-of-axis) anchors, e.g. 1 atm."""
    x0, x1, y0, y1 = 64, w - 20, h - 44, 20
    X = _pw([(Tr[0], x0), (triple[0], x0 + .32 * (x1 - x0)), (critical[0], x0 + .80 * (x1 - x0)), (Tr[1], x1)] +
            [(v, x0 + fr * (x1 - x0)) for v, fr in extraT])
    lg = math.log10
    Yl = _pw([(lg(Pr[0]), y0), (lg(triple[1]), y0 - .30 * (y0 - y1)), (lg(critical[1]), y0 - .82 * (y0 - y1)), (lg(Pr[1]), y1)] +
             [(lg(v), y0 - fr * (y0 - y1)) for v, fr in extraP])
    Y = lambda P: Yl(lg(P))
    b = [_line(x0, y1, x0, y0, INK, 1.6), _line(x0, y0, x1, y0, INK, 1.6), _txt((x0 + x1) / 2, h - 10, Tlab + " (not to scale)", 12),
         f'<text x="16" y="{(y0 + y1) / 2:.1f}" font-size="12" text-anchor="middle" fill="{INK}" font-weight="700" font-family="Nunito,Arial,sans-serif" transform="rotate(-90 16 {(y0 + y1) / 2:.1f})">{Plab} (not to scale)</text>']
    for t in ticksT:
        b.append(_line(X(t), y0, X(t), y0 + 4, INK, 1.2) + _txt(X(t), y0 + 16, f"{t:g}", 10, fill=MUTED, weight=600))
    for p in ticksP:
        b.append(_line(x0 - 4, Y(p), x0, Y(p), INK, 1.2) + _txt(x0 - 7, Y(p) + 4, f"{p:g}", 10, "end", MUTED, 600))
        b.append(_line(x0, Y(p), x1, Y(p), GRID, 1, "3 4"))
    tx, ty = X(triple[0]), Y(triple[1]); cx, cy = X(critical[0]), Y(critical[1])
    sx, sy = x0 + 8, y0 - 6
    b.append(f'<path d="M{sx:.1f},{sy:.1f} Q{tx - 20:.1f},{sy - 4:.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    b.append(f'<path d="M{tx:.1f},{ty:.1f} Q{(tx + cx) / 2 + 40:.1f},{ty - 10:.1f} {cx:.1f},{cy:.1f}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{COL["purple"]}"/>' + _txt(cx - 6, cy - 9, "critical point", 10, "end", COL["purple"]))
    dx = -22 if fusion_slope == "negative" else 22
    b.append(_line(tx, ty, tx + dx, y1 + 4, INK, 2.4))
    b.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="4.5" fill="{COL["pink"]}"/>' + _txt(tx + 8, ty + 16, "triple point", 10, "start", COL["pink"]))
    b.append(_txt((x0 + tx) / 2 - 6, (ty + y1) / 2, "SOLID", 13, fill=COL["blue"]))
    b.append(_txt((tx + cx) / 2 + 6, y1 + 30, "LIQUID", 13, fill=COL["green"]))
    b.append(_txt((tx + x1) / 2 + 30, y0 - 22, "GAS", 13, fill=COL["orange"]))
    if path:
        for (Ta, Pa), (Tb, Pb) in zip(path, path[1:]):
            b.append(_arrow(X(Ta), Y(Pa), X(Tb), Y(Pb), COL["pink"], 2.4, 10, "6 3"))
    for T, P, lab in points:
        b.append(f'<circle cx="{X(T):.1f}" cy="{Y(P):.1f}" r="4" fill="{INK}"/>' + _txt(X(T) + 7, Y(P) - 6, lab, 12, "start"))
    return _frame(title, note, "".join(b), w, h)


def cycle(title, nodes, outs, note="", w=520, h=440, center=""):
    """Circular pathway. nodes = ['citrate', ...] clockwise from the top. outs = {i: ('text', side)}, placed on the arrow
    from node i to node i+1; side = 'out' (pointing away from the circle) or 'in'."""
    cx, cy, R = w / 2, h / 2 + 4, min(w, h) * .30
    n = len(nodes)
    pos = [(cx + R * math.sin(2 * math.pi * k / n), cy - R * math.cos(2 * math.pi * k / n)) for k in range(n)]
    b = []
    if center:
        b.append(_txt(cx, cy + 5, center, 16, fill=COL["purple"]))
    for k in range(n):
        a1, a2 = 2 * math.pi * (k + .22) / n, 2 * math.pi * (k + .78) / n
        p1 = (cx + R * math.sin(a1), cy - R * math.cos(a1)); p2 = (cx + R * math.sin(a2), cy - R * math.cos(a2))
        b.append(_arrow(*p1, *p2, MUTED, 2.2, 9))
        if k in outs:
            text, side = outs[k]
            am = 2 * math.pi * (k + .5) / n
            mx, my = cx + R * math.sin(am), cy - R * math.cos(am)
            ox, oy = math.sin(am), -math.cos(am)
            if side == "out":
                b.append(_arrow(mx, my, mx + ox * 30, my + oy * 30, COL["orange"], 2, 8))
                tx, ty = mx + ox * 46, my + oy * 46 + 4
            else:
                b.append(_arrow(mx + ox * 30, my + oy * 30, mx, my, COL["blue"], 2, 8))
                tx, ty = mx + ox * 46, my + oy * 46 + 4
            anchor = "start" if ox > .35 else "end" if ox < -.35 else "middle"
            b.append(_txt(tx, ty, text, 13, anchor, COL["orange"] if side == "out" else COL["blue"]))
    for (x, y), name in zip(pos, nodes):
        wbox = 14 + 7.6 * len(re.sub("<[^>]+>", "", name))
        b.append(f'<rect x="{x - wbox / 2:.1f}" y="{y - 13:.1f}" width="{wbox:.1f}" height="28" rx="14" fill="#e7defc" stroke="{COL["purple"]}" stroke-width="1.5"/>')
        b.append(_txt(x, y + 5, name, 13))
    return _frame(title, note, "".join(b), w, h)


def chain(title, nodes, steps, note="", w=420):
    """Vertical linear pathway. nodes = names top to bottom; steps[i] = (enzyme, side_in, side_out) for the arrow below node i."""
    gap = 70
    h = 30 + gap * (len(nodes) - 1) + 30
    x = w * .42
    b = []
    for i, name in enumerate(nodes):
        y = 26 + i * gap
        wbox = 16 + 6.8 * len(re.sub("<[^>]+>", "", name))
        b.append(f'<rect x="{x - wbox / 2:.1f}" y="{y - 13:.1f}" width="{wbox:.1f}" height="26" rx="13" fill="#e7defc" stroke="{COL["purple"]}" stroke-width="1.5"/>')
        b.append(_txt(x, y + 4, name, 12))
        if i < len(steps):
            enz, sin, sout = steps[i]
            b.append(_arrow(x, y + 15, x, y + gap - 15, MUTED, 2.2, 9))
            ym = y + gap / 2
            if enz:
                b.append(_txt(x - 12, ym + 4, enz, 11, "end", COL["purple"], 700, True))
            if sin or sout:
                b.append(f'<path d="M{x + 40:.1f},{ym - 16:.1f} Q{x + 6:.1f},{ym:.1f} {x + 40:.1f},{ym + 16:.1f}" fill="none" stroke="{COL["orange"]}" stroke-width="2"/>')
                b.append(f'<path d="M{x + 40:.1f},{ym + 16:.1f} l-9,-1 l5,-7 z" fill="{COL["orange"]}"/>')
                if sin: b.append(_txt(x + 46, ym - 12, sin, 11, "start", COL["blue"]))
                if sout: b.append(_txt(x + 46, ym + 22, sout, 11, "start", COL["orange"]))
    return _frame(title, note, "".join(b), w, h)


def etc_diagram(title, note="", blocked=None, w=520, h=300):
    """Inner mitochondrial membrane with complexes I–IV and ATP synthase. blocked = {'I': 'rotenone', ...} marks a red X."""
    b = []
    top, bot = 110, 170
    b.append(f'<rect x="10" y="{top}" width="{w - 20}" height="{bot - top}" fill="#fff3d6" stroke="#e7c97a"/>')
    b.append(_txt(16, 18, "intermembrane space (high [H⁺])", 11, "start", MUTED))
    b.append(_txt(16, bot + 76, "matrix", 11, "start", MUTED))
    comps = [("I", 60, 64), ("II", 140, 40), ("III", 230, 64), ("IV", 330, 64), ("ATP synthase", 450, 60)]
    for name, x, wd in comps:
        hh = 96 if name != "II" else 60
        y = top - 18 if name != "II" else top + 18
        col = "#d6ecff" if name != "ATP synthase" else "#d4f5e6"
        b.append(f'<rect x="{x - wd / 2}" y="{y}" width="{wd}" height="{hh}" rx="14" fill="{col}" stroke="{INK}" stroke-width="1.6"/>')
        b.append(_txt(x, y + hh / 2 + 4, name, 12 if len(name) < 4 else 10))
        if blocked and name in blocked:
            b.append(_line(x - 18, y + 10, x + 18, y + hh - 10, COL["pink"], 4) + _line(x + 18, y + 10, x - 18, y + hh - 10, COL["pink"], 4))
            b.append(_txt(x, y - 8, blocked[name], 11, fill=COL["pink"]))
    for x in (60 + 42, 230 + 42, 330 + 42):
        b.append(_arrow(x, bot + 24, x, top - 30, COL["pink"], 2, 8) + _txt(x, top - 36, "H⁺", 11, "middle", COL["pink"]))
    b.append(_arrow(450 - 40, top - 30, 450 - 40, bot + 24, COL["green"], 2, 8) + _txt(450 - 40, top - 36, "H⁺", 11, "middle", COL["green"]))
    b.append(_txt(450, bot + 56, "ADP + Pᵢ → ATP", 10, "middle", COL["green"]))
    b.append(_txt(60, bot + 56, "NADH → NAD⁺", 10, fill=COL["blue"]))
    b.append(_txt(140, bot + 40, "FADH₂", 10, fill=COL["blue"]))
    b.append(_txt(330, bot + 56, "½O₂ → H₂O", 10, fill=COL["blue"]))
    b.append(_txt(185, top + 34, "Q", 12, fill=COL["purple"]))
    b.append(_txt(280, top - 4, "cyt c", 10, fill=COL["purple"]))
    b.append(_arrow(92, top + 40, 120, top + 40, COL["purple"], 1.6, 7) + _arrow(160, top + 40, 198, top + 40, COL["purple"], 1.6, 7))
    b.append(_arrow(262, top + 6, 298, top + 6, COL["purple"], 1.6, 7))
    return _frame(title, note, "".join(b), w, h)


def levels_spectrum(title, levels, transitions, lines, note="energy levels not to scale", w=480, h=380, emin=-13.6, emax=0):
    """Energy-level diagram (top) with emission arrows, plus a visible line spectrum strip (bottom).
    levels = [(n, E_eV)]; transitions = [(n_hi, n_lo, color_key)]; lines = [(wavelength_nm, color_key, label)]."""
    x0, x1, top, bot = 70, w - 56, 16, h - 120
    def Y(e):  # schematic spacing so the upper levels don't pile up (not to scale)
        fr = 1.0 if e >= 0 else 1 - (-e / -emin) ** 0.4
        return bot - fr * (bot - top)
    b = [_txt(x0, h - 6 - 100 + 100, "", 1)]
    for n, e in levels:
        b.append(_line(x0, Y(e), x1, Y(e), INK, 1.6))
        b.append(_txt(x0 - 8, Y(e) + 4, f"n = {n}" if n != "∞" else "n = ∞", 11, "end"))
        b.append(_txt(x1 + 4, Y(e) + 4, f"{e:g} eV", 10, "start", MUTED, 600))
    lev = dict(levels)
    for k, (hi, lo, c) in enumerate(transitions):
        xx = x0 + 40 + k * 46
        b.append(_arrow(xx, Y(lev[hi]), xx, Y(lev[lo]), COL.get(c, c), 2.6, 9))
    # spectrum strip 400-700 nm
    sx0, sx1, sy = x0, x1, h - 70
    b.append(f'<rect x="{sx0}" y="{sy}" width="{sx1 - sx0}" height="34" fill="#1d1b2b" rx="4"/>')
    X = lambda nm: sx0 + (nm - 400) / 300 * (sx1 - sx0)
    for nm in (400, 500, 600, 700):
        b.append(_txt(X(nm), sy + 50, f"{nm}", 10, fill=MUTED, weight=600))
    b.append(_txt((sx0 + sx1) / 2, sy + 64, "Wavelength (nm)", 11))
    for nm, c, lab in lines:
        b.append(f'<rect x="{X(nm) - 2:.1f}" y="{sy + 2}" width="4" height="30" fill="{COL.get(c, c)}"/>')
        b.append(_txt(X(nm), sy - 6, lab, 10, fill=INK))
    return _frame(title, note, "".join(b), w, h)


def ir_spectrum(title, peaks, note="", w=480, h=270):
    """Schematic IR spectrum (% transmittance vs wavenumber, 4000 → 500 cm⁻¹).
    peaks = [(center_cm1, depth 0-1, half-width_cm1)]; broad O–H bands use a large half-width."""
    x0, x1, y0, y1 = 56, w - 16, h - 40, 20
    X = lambda k: x0 + (4000 - k) / 3500 * (x1 - x0)
    pts = []
    for k in range(4000, 499, -10):
        t = 1.0
        for c, d, hw in peaks:
            t *= 1 - d * math.exp(-((k - c) / hw) ** 2)
        pts.append((X(k), y1 + (1 - t) * (y0 - y1) * .92 + 4))
    b = [_line(x0, y0, x1, y0, INK, 1.4), _line(x0, y1, x0, y0, INK, 1.4)]
    for k in (4000, 3000, 2000, 1500, 1000, 500):
        b.append(_line(X(k), y0, X(k), y0 + 4, INK, 1.2) + _txt(X(k), y0 + 16, f"{k}", 10, fill=MUTED, weight=600))
    b.append(_txt((x0 + x1) / 2, h - 8, "Wavenumber (cm⁻¹)", 11))
    b.append(f'<text x="16" y="{(y0 + y1) / 2:.1f}" font-size="11" text-anchor="middle" fill="{INK}" font-weight="700" font-family="Nunito,Arial,sans-serif" transform="rotate(-90 16 {(y0 + y1) / 2:.1f})">% Transmittance</text>')
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    b.append(f'<path d="{d}" fill="none" stroke="{COL["purple"]}" stroke-width="1.8"/>')
    return _frame(title, note, "".join(b), w, h)


def nmr_spectrum(title, signals, note="", w=480, h=250, xmax=12):
    """Stick ¹H NMR spectrum. signals = [(ppm, n_peaks, integration_H, label)]; peaks use Pascal-triangle heights."""
    x0, x1, y0, y1 = 30, w - 20, h - 42, 34
    X = lambda p: x1 - p / xmax * (x1 - x0)
    b = [_line(x0, y0, x1, y0, INK, 1.4)]
    for p in range(0, xmax + 1):
        b.append(_line(X(p), y0, X(p), y0 + 4, INK, 1.1))
        if p % 2 == 0 or xmax <= 8:
            b.append(_txt(X(p), y0 + 16, str(p), 10, fill=MUTED, weight=600))
    b.append(_txt((x0 + x1) / 2, h - 8, "Chemical shift δ (ppm)", 11))
    for ppm, n, H, lab in signals:
        coeffs = [math.comb(n - 1, i) for i in range(n)]
        top = max(coeffs)
        tall = (y0 - y1 - 18) * min(1, .35 + .13 * H)
        sp = 4.5
        for i, cf in enumerate(coeffs):
            xx = X(ppm) + (i - (n - 1) / 2) * sp
            b.append(_line(xx, y0, xx, y0 - tall * cf / top, COL["blue"], 1.8))
        b.append(_txt(X(ppm), y0 - tall - 8, lab or f"{H}H", 10, fill=INK))
    return _frame(title, note, "".join(b), w, h)
