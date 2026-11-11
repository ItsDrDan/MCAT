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
