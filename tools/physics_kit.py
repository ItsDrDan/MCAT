"""Physics figures for MCAT passages: free-body diagrams, ray diagrams and circuit schematics.
Same look as passage_kit (white card, Nunito labels, the site's pink/blue/green/orange/purple palette)."""
import math, re, html

INK, MUTED, GRID = "#2d2a3e", "#6b6785", "#ece8f4"
COL = {"pink": "#e0577f", "blue": "#3a7fc4", "green": "#2f9e77", "orange": "#f0a23b", "purple": "#7a5cc4", "ink": INK}
FONT = 'font-family="Nunito,Arial,sans-serif"'
_n = [0]


def _txt(x, y, s, size=12, anchor="middle", fill=INK, weight=700, italic=False):
    s = re.sub(r"<sub>(.*?)</sub>", r"<tspan dy='3' font-size='9'>\1</tspan><tspan dy='-3'>​</tspan>", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"<tspan dy='-5' font-size='9'>\1</tspan><tspan dy='5'>​</tspan>", s)
    s = re.sub(r"<i>(.*?)</i>", r"<tspan font-style='italic'>\1</tspan>", s)
    it = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
            f'font-weight="{weight}"{it} {FONT} stroke="#fff" stroke-width="3" paint-order="stroke">{s}</text>')


def _line(x1, y1, x2, y2, c=INK, w=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{d}/>'


def _arrow(x1, y1, x2, y2, c=INK, w=2.5, head=10, dash=""):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    p1 = (bx + head * .45 * math.sin(a), by - head * .45 * math.cos(a))
    p2 = (bx - head * .45 * math.sin(a), by + head * .45 * math.cos(a))
    return (_line(x1, y1, bx, by, c, w, dash) +
            f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{c}"/>')


def _frame(title, note, body, w, h):
    cap = f"<b>{title}</b>" + (f" · {note}" if note else "")
    lab = html.escape(re.sub("<[^>]+>", "", title))
    return (f'<figure class="qfig"><figcaption class="fcap">{cap}</figcaption>'
            f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{lab}" '
            f'xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="{w}" height="{h}" fill="#fff" rx="10"/>{body}</svg></figure>')


# ------------------------------------------------------------------ free-body diagrams
def fbd(title, forces, note="", incline=None, obj="block", w=420, h=300, obj_label=""):
    """forces = [(label, angle_deg, rel_length, color)], angle measured counterclockwise from +x (screen right).
    incline = angle in degrees (block drawn on a ramp rising to the left), or None for a free object.
    obj = 'block' or 'dot'. Arrows start at the object's center."""
    cx, cy = w / 2, h / 2 + (10 if incline else 0)
    body = []
    if incline:
        t = math.radians(incline)
        L = w * .9
        x0, y0 = w * .05, h - 26
        body.append(f'<path d="M{x0:.1f},{y0:.1f} L{x0 + L:.1f},{y0:.1f} L{x0:.1f},{y0 - L * math.tan(t):.1f} Z" fill="#f4f1fa" stroke="{INK}" stroke-width="1.5"/>')
        body.append(f'<path d="M{x0 + L - 46:.1f},{y0:.1f} A46,46 0 0 0 {x0 + L - 46 * math.cos(t):.1f},{y0 - 46 * math.sin(t):.1f}" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
        body.append(_txt(x0 + L - 62, y0 - 8, f"{incline}°", 12, fill=MUTED))
        # block sits on the slope at its middle
        mx = x0 + L * .5
        my = y0 - (L * .5) * math.tan(t)
        s = 46
        nx, ny = math.sin(t), -math.cos(t)  # outward normal, up and to the right (screen coords)
        cx, cy = mx + nx * s / 2, my + ny * s / 2
        deg = incline
        body.append(f'<rect x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" width="{s}" height="{s}" rx="4" fill="#e7defc" stroke="{INK}" stroke-width="1.8" transform="rotate({deg} {cx:.1f} {cy:.1f})"/>')
    elif obj == "block":
        body.append(f'<rect x="{cx - 28:.1f}" y="{cy - 22:.1f}" width="56" height="44" rx="5" fill="#e7defc" stroke="{INK}" stroke-width="1.8"/>')
    else:
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{INK}"/>')
    if obj_label:
        body.append(_txt(cx, cy + 4, obj_label, 12))
    unit = min(w, h) * .36
    for fo in forces:
        lab, ang, rel, c = fo[:4]
        ox, oy = fo[4] if len(fo) > 4 else (0, 0)  # optional start offset (px) so parallel forces don't overlap
        a = math.radians(ang)
        sx, sy = cx + ox, cy + oy
        x2, y2 = sx + rel * unit * math.cos(a), sy - rel * unit * math.sin(a)
        body.append(_arrow(sx, sy, x2, y2, COL.get(c, c), 3, 12))
        lx, ly = x2 + 16 * math.cos(a), y2 - 16 * math.sin(a) + 4
        anchor = "start" if math.cos(a) > .3 else "end" if math.cos(a) < -.3 else "middle"
        body.append(_txt(lx, ly, lab, 13, anchor, COL.get(c, c)))
    return _frame(title, note, "".join(body), w, h)


# ------------------------------------------------------------------ ray diagrams
def rays(title, kind, f, do, ho, note="", w=480, h=260, scale=None, show_values=True):
    """Thin lens or mirror ray diagram with the image located by calculation.
    kind: 'converging lens', 'diverging lens', 'concave mirror', 'convex mirror'. f > 0 magnitude (cm), do (cm), ho (cm)."""
    lens = "lens" in kind
    fs = f if kind in ("converging lens", "concave mirror") else -f
    di = 1 / (1 / fs - 1 / do) if abs(1 / fs - 1 / do) > 1e-9 else float("inf")
    hi = -di / do * ho
    span = max(do, abs(di) if di != float("inf") else do, 2 * f) * 1.15
    sc = scale or (w * .44) / span
    ax, ay = (w / 2 if lens else (w * .78 if di > 0 else w * .58)), h / 2 + 10
    X = lambda d: ax - d * sc  # object side is to the left
    Xi = (lambda d: ax + d * sc) if lens else (lambda d: ax - d * sc)  # real image side
    hs = (h * .32) / max(ho, abs(hi) if di != float("inf") else ho)
    Y = lambda y: ay - y * hs
    b = [_line(10, ay, w - 10, ay, MUTED, 1.2, "5 4")]
    # optic
    if lens:
        conv = kind == "converging lens"
        top, bot = ay - h * .40, ay + h * .40
        b.append(_line(ax, top, ax, bot, COL["blue"], 3))
        for yy, d in ((top, -1), (bot, 1)):
            if conv:
                b.append(_arrow(ax, yy + (14 if d < 0 else -14), ax, yy, COL["blue"], 3, 9))
            else:
                b.append(_line(ax - 7, yy + (-8 if d < 0 else 8), ax, yy, COL["blue"], 3))
                b.append(_line(ax + 7, yy + (-8 if d < 0 else 8), ax, yy, COL["blue"], 3))
        for s in (-1, 1):
            b.append(f'<circle cx="{ax + s * f * sc:.1f}" cy="{ay:.1f}" r="3.5" fill="{INK}"/>')
            b.append(_txt(ax + s * f * sc, ay + 18, "F", 12, fill=MUTED))
    else:
        conc = kind == "concave mirror"
        R = 2 * f * sc
        top, bot = ay - h * .40, ay + h * .40
        bulge = 14 if conc else -14
        b.append(f'<path d="M{ax - bulge:.1f},{top:.1f} Q{ax + bulge:.1f},{ay:.1f} {ax - bulge:.1f},{bot:.1f}" fill="none" stroke="{COL["blue"]}" stroke-width="3"/>')
        b.append(_txt(ax + 18, top - 4, "mirror", 11, "start", COL["blue"]))
        fx = X(f) if conc else ax + f * sc
        b.append(f'<circle cx="{fx:.1f}" cy="{ay:.1f}" r="3.5" fill="{INK}"/>')
        b.append(_txt(fx, ay + 18, "F", 12, fill=MUTED))
    # object
    ox = X(do)
    b.append(_arrow(ox, ay, ox, Y(ho), COL["pink"], 3.5, 11))
    b.append(_txt(ox, ay + 18, "object", 11, fill=COL["pink"]))
    # image and rays
    if di != float("inf"):
        real = di > 0
        ix = Xi(di)
        iy = Y(hi)
        c = COL["green"]
        b.append(_arrow(ix, ay, ix, iy, c, 3.5, 11, "" if real else "6 4"))
        b.append(_txt(ix, ay - 8 if hi < 0 else ay + 18, "image" if real else "virtual image", 11, fill=c))
        tip = (ox, Y(ho))
        # ray 1: parallel then through/away from focal point; ray 2: through center (lens) / vertex (mirror)
        rc = COL["orange"]
        hit1 = (ax, Y(ho))
        b.append(_line(*tip, *hit1, rc, 1.8))
        b.append(_line(*hit1, ix, iy, rc, 1.8, "" if real else "4 4"))
        if not real:  # continue the real ray past the optic so students see it diverge
            ex = w - 12 if lens else 12
            slope = (iy - hit1[1]) / (ix - hit1[0])
            b.append(_line(*hit1, ex, hit1[1] + slope * (ex - hit1[0]), rc, 1.8))
        rc2 = COL["purple"]
        if lens:
            b.append(_line(*tip, ax, ay, rc2, 1.8))
            b.append(_line(ax, ay, ix, iy, rc2, 1.8, "" if real else "4 4"))
            if not real:
                ex = w - 12
                slope = (ay - tip[1]) / (ax - tip[0])
                b.append(_line(ax, ay, ex, ay + slope * (ex - ax), rc2, 1.8))
        else:
            b.append(_line(*tip, ax, ay, rc2, 1.8))
            b.append(_line(ax, ay, ix, iy, rc2, 1.8, "" if real else "4 4"))
            if not real:
                slope = (ay - tip[1]) / (ax - tip[0])
                ex = 12
                b.append(_line(ax, ay, ex, ay - slope * (ex - ax), rc2, 1.8))
    if show_values:
        b.append(_txt(14, 18, f"f = {f:g} cm   object distance = {do:g} cm", 11, "start", MUTED, 600))
    return _frame(title, note, "".join(b), w, h)


# ------------------------------------------------------------------ circuits
def _resistor(x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    zl = min(44, L * .6); s = (L - zl) / 2
    pts = [(x1, y1), (x1 + ux * s, y1 + uy * s)]
    for k in range(1, 7):
        t = s + zl * k / 7; amp = 7 * (1 if k % 2 else -1)
        pts.append((x1 + ux * t + px * amp, y1 + uy * t + py * amp))
    pts += [(x1 + ux * (L - s), y1 + uy * (L - s)), (x2, y2)]
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'


def _battery(x1, y1, x2, y2, plus_at_end=True):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    m = L / 2; g = 5
    a = (x1 + ux * (m - g), y1 + uy * (m - g)); b = (x1 + ux * (m + g), y1 + uy * (m + g))
    long_, short = (b, a) if plus_at_end else (a, b)
    s = _line(x1, y1, *a) + _line(*b, x2, y2)
    s += _line(long_[0] + px * 14, long_[1] + py * 14, long_[0] - px * 14, long_[1] - py * 14, INK, 2.4)
    s += _line(short[0] + px * 7, short[1] + py * 7, short[0] - px * 7, short[1] - py * 7, INK, 4)
    s += _txt(long_[0] + ux * 9 + px * 18, long_[1] + uy * 9 + py * 18 + 4, "+", 13, fill=COL["pink"])
    return s


def _capacitor(x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    m = L / 2; g = 5
    a = (x1 + ux * (m - g), y1 + uy * (m - g)); b = (x1 + ux * (m + g), y1 + uy * (m + g))
    s = _line(x1, y1, *a) + _line(*b, x2, y2)
    for p in (a, b):
        s += _line(p[0] + px * 13, p[1] + py * 13, p[0] - px * 13, p[1] - py * 13, INK, 2.6)
    return s


def _meter(x1, y1, x2, y2, letter):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return (_line(x1, y1, mx - ux * 13, my - uy * 13) + _line(mx + ux * 13, my + uy * 13, x2, y2) +
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="13" fill="#fff" stroke="{INK}" stroke-width="2"/>' + _txt(mx, my + 5, letter, 13))


def _switch(x1, y1, x2, y2, closed=False):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    a = (x1 + ux * L * .3, y1 + uy * L * .3); b = (x1 + ux * L * .7, y1 + uy * L * .7)
    s = _line(x1, y1, *a) + _line(*b, x2, y2)
    s += f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="3" fill="{INK}"/><circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="3" fill="{INK}"/>'
    end = b if closed else (b[0] + px * -14, b[1] + py * -14)
    return s + _line(*a, *end, INK, 2.2)


def _bulb(x1, y1, x2, y2):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return (_line(x1, y1, mx - ux * 13, my - uy * 13) + _line(mx + ux * 13, my + uy * 13, x2, y2) +
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="13" fill="#fff8e1" stroke="{INK}" stroke-width="2"/>' +
            _line(mx - 9, my - 9, mx + 9, my + 9, INK, 1.6) + _line(mx - 9, my + 9, mx + 9, my - 9, INK, 1.6))


def circuit(title, parts, w=420, h=240, note="", nodes=()):
    """parts = [(kind, (x1,y1), (x2,y2), label)] with kind in wire, R, battery, battery-, C, A, V, switch, switch-closed, bulb.
    Labels sit beside the part. nodes = [(x,y)] for junction dots."""
    b = []
    for kind, p1, p2, *lab in parts:
        lab = lab[0] if lab else ""
        if kind == "wire": b.append(_line(*p1, *p2, INK, 2.2))
        elif kind == "R": b.append(_resistor(*p1, *p2))
        elif kind == "battery": b.append(_battery(*p1, *p2, True))
        elif kind == "battery-": b.append(_battery(*p1, *p2, False))
        elif kind == "C": b.append(_capacitor(*p1, *p2))
        elif kind in ("A", "V"): b.append(_meter(*p1, *p2, kind))
        elif kind == "switch": b.append(_switch(*p1, *p2, False))
        elif kind == "switch-closed": b.append(_switch(*p1, *p2, True))
        elif kind == "bulb": b.append(_bulb(*p1, *p2))
        if lab:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            if abs(p2[0] - p1[0]) > abs(p2[1] - p1[1]):  # horizontal part: label above
                b.append(_txt(mx, my - 18, lab, 12))
            else:
                b.append(_txt(mx + 20, my + 4, lab, 12, "start"))
    for (x, y) in nodes:
        b.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')
    return _frame(title, note, "".join(b), w, h)


# ------------------------------------------------------------------ generic labeled sketch helpers
def svg_figure(title, body, w, h, note=""):
    return _frame(title, note, body, w, h)
