"""Structure drawings for MCAT passages, in the look of Dr. Dan's organic games
(Bond Voyage / Final Boss palette: dark-slate bonds, red O, blue N, green halogens).
RDKit does the 2D layout so rings, fused rings and wedge/dash stereo come out right."""
import re, html
from rdkit import Chem
from rdkit.Chem import AllChem, rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D
rdDepictor.SetPreferCoordGen(True)

INK, MUTED = "#2d2a3e", "#6b6785"
PAL = {6: (0.176, 0.247, 0.294), 8: (0.753, 0.224, 0.169), 7: (0.184, 0.373, 0.769),
       17: (0.180, 0.545, 0.341), 9: (0.180, 0.545, 0.341), 35: (0.541, 0.353, 0.110),
       16: (0.722, 0.525, 0.043), 15: (0.769, 0.416, 0.071), 1: (0.176, 0.247, 0.294),
       53: (0.45, 0.2, 0.6), 11: (0.42, 0.31, 0.79), -1: (0.176, 0.247, 0.294)}
FONT = 'font-family="Nunito,Arial,sans-serif"'
_uid = [0]

def _crowding(m):
    """Smallest distance between atoms that are not bonded (bigger = cleaner drawing)."""
    c = m.GetConformer(); n = m.GetNumAtoms(); best = 9e9
    for i in range(n):
        pi = c.GetAtomPosition(i)
        for j in range(i + 1, n):
            if m.GetBondBetweenAtoms(i, j): continue
            pj = c.GetAtomPosition(j); d = ((pi.x - pj.x) ** 2 + (pi.y - pj.y) ** 2) ** .5
            best = min(best, d)
    return best

def _mol(smi, explicit_h=None):
    m = Chem.MolFromSmiles(smi)
    assert m is not None, smi
    heavy = m.GetNumAtoms()
    if explicit_h or (explicit_h is None and heavy <= 2 and all(a.GetSymbol() == "C" for a in m.GetAtoms())):
        m = Chem.AddHs(m)
    best, bc = None, -1
    for cg in (True, False):  # try both RDKit layout engines, keep the less crowded one
        rdDepictor.SetPreferCoordGen(cg)
        mm = Chem.Mol(m); rdDepictor.Compute2DCoords(mm)
        c = _crowding(mm) if mm.GetNumAtoms() > 2 else 9
        if c > bc + 0.05: best, bc = mm, c
    rdDepictor.SetPreferCoordGen(True)
    return best

def mol_svg(smi, bl=32, notes=None):
    """Return (inner_svg, w, h) for one molecule. notes = {atom_idx: 'label'} draws a small tag."""
    m = _mol(smi)
    d = rdMolDraw2D.MolDraw2DSVG(-1, -1)  # canvas sized to the molecule at a fixed bond length
    o = d.drawOptions()
    o.setAtomPalette(PAL); o.clearBackground = False
    o.bondLineWidth = 2; o.fixedBondLength = bl; o.padding = 0.08
    o.minFontSize = 16; o.maxFontSize = 18; o.additionalAtomLabelPadding = 0.12
    o.multipleBondOffset = 0.18
    if notes:
        for i, t in notes.items():
            m.GetAtomWithIdx(i).SetProp("atomNote", t)
        o.annotationFontScale = 0.7
    d.DrawMolecule(m); d.FinishDrawing()
    s = d.GetDrawingText()
    mm = re.search(r"width='([\d.]+)px' height='([\d.]+)px'", s)
    w, h = int(float(mm.group(1))), int(float(mm.group(2)))
    s = re.sub(r"<\?xml.*?\?>", "", s, flags=re.S)
    s = re.sub(r"<!-- END OF HEADER -->", "", s)
    s = re.sub(r"^.*?<svg[^>]*>", "", s, flags=re.S).replace("</svg>", "")
    s = re.sub(r"<rect[^>]*/>", "", s, count=1) if "style='opacity:1.0;fill:#FFFFFF" in s[:300] else s
    _uid[0] += 1  # RDKit reuses ids; keep them unique when several drawings share a page
    s = re.sub(r"(class|id)='(bond|atom)-", lambda mm: f"{mm.group(1)}='m{_uid[0]}-{mm.group(2)}-", s)
    return s, w, h

def _t(x, y, s, size=12, anchor="middle", fill=INK, weight=700, italic=False):
    st = ' font-style="italic"' if italic else ""
    s = re.sub(r"<sub>(.*?)</sub>", r"<tspan dy='3' font-size='9'>\1</tspan><tspan dy='-3'> </tspan>", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"<tspan dy='-5' font-size='9'>\1</tspan><tspan dy='5'> </tspan>", s)
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{st} {FONT}>{s}</text>'

def _svg(body, w, h, label):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{html.escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="{w}" height="{h}" fill="#fff" rx="10"/>{body}</svg>')

def _frame(title, note, svg):
    cap = f"<b>{title}</b>" + (f" · {note}" if note else "")
    return f'<figure class="qfig"><figcaption class="fcap">{cap}</figcaption>{svg}</figure>'

def structures(title, items, note="", cols=None, bl=28, maxw=450):
    """Grid of labeled structures. items = [(smiles, label, sublabel?)]."""
    cells = []
    for it in items:
        inner, w, h = mol_svg(it[0], bl)
        lab, sub = it[1], (it[2] if len(it) > 2 else "")
        need = int(max(7.6 * len(re.sub("<[^>]+>", "", lab)), 6.6 * len(re.sub("<[^>]+>", "", sub)))) + 10
        if need > w:  # widen the cell so labels never collide; keep the drawing centered
            inner = f'<g transform="translate({(need - w) / 2:.1f},0)">{inner}</g>'; w = need
        cells.append((inner, w, h, lab, sub))
    if cols:
        rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    else:  # fill rows up to about 620 px so drawings are never shrunk much
        rows, cur, cw = [], [], 0
        for c in cells:
            if cur and cw + c[1] + 18 > maxw - 24:
                rows.append(cur); cur, cw = [], 0
            cur.append(c); cw += c[1] + 18
        rows.append(cur)
    gap, body, y, W = 18, [], 8, 0
    for r in rows:
        rw = sum(c[1] for c in r) + gap * (len(r) - 1)
        W = max(W, rw)
    W = max(W + 24, 200)
    for r in rows:
        rh = max(c[2] for c in r)
        rw = sum(c[1] for c in r) + gap * (len(r) - 1)
        x = (W - rw) / 2
        for (inner, w, h, lab, sub) in r:
            body.append(f'<g transform="translate({x:.1f},{y + (rh - h) / 2:.1f})">{inner}</g>')
            body.append(_t(x + w / 2, y + rh + 14, lab, 13))
            if sub:
                body.append(_t(x + w / 2, y + rh + 29, sub, 11, fill=MUTED, weight=600))
            x += w + gap
        y += rh + (36 if any(c[4] for c in r) else 24)
    return _frame(title, note, _svg("".join(body), int(W), int(y + 4), re.sub("<[^>]+>", "", title)))

def _arrow(x, y, L, top="", bot="", kind="→"):
    if kind == "↔":
        a = (f'<line x1="{x + 8:.1f}" y1="{y:.1f}" x2="{x + L - 8:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{x + L:.1f},{y:.1f} l-10,-5 l0,10 z M{x:.1f},{y:.1f} l10,-5 l0,10 z" fill="{INK}"/>')
    elif kind == "⇌":
        a = (f'<line x1="{x:.1f}" y1="{y - 3:.1f}" x2="{x + L - 2:.1f}" y2="{y - 3:.1f}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{x + L:.1f},{y - 3:.1f} l-9,-6" stroke="{INK}" stroke-width="2" fill="none"/>'
             f'<line x1="{x:.1f}" y1="{y + 3:.1f}" x2="{x + L - 2:.1f}" y2="{y + 3:.1f}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{x:.1f},{y + 3:.1f} l9,6" stroke="{INK}" stroke-width="2" fill="none"/>')
    else:
      a = (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + L - 8:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="2"/>'
         f'<path d="M{x + L:.1f},{y:.1f} l-10,-5 l0,10 z" fill="{INK}"/>')
    if top: a += _t(x + L / 2, y - 10, top, 11)
    if bot: a += _t(x + L / 2, y + 17, bot, 11, fill=MUTED, weight=600)
    return a

def scheme(title, parts, note="", bl=26, labels=None, maxw=450):
    """Reaction scheme. parts: smiles strings, '+', ('→'|'⇌'|'↔', top, bottom), or '\n' to start a new row.
    Rows also wrap on their own so drawings are never shrunk much.
    labels = captions under each molecule, in order ('' to skip)."""
    items = []
    for p in parts:
        if isinstance(p, tuple):
            L = max(54 if p[0] == "↔" else 70, 7.2 * max(len(re.sub("<[^>]+>", "", p[1])), len(re.sub("<[^>]+>", "", p[2] if len(p) > 2 else ""))) + 20)
            items.append(("arr", L, p))
        elif p == "+":
            items.append(("plus", 22, None))
        elif p == "\n":
            items.append(("br", 0, None))
        else:
            inner, w, h = mol_svg(p, bl)
            k = sum(1 for it in items if it[0] == "mol")
            lab = labels[k] if labels and k < len(labels) else ""
            need = int(6.9 * len(re.sub("<[^>]+>", "", lab))) + 8
            if need > w:  # keep the caption inside the cell
                inner = f'<g transform="translate({(need - w) / 2:.1f},0)">{inner}</g>'; w = need
            items.append(("mol", w, (inner, h)))
    rows, cur, cw = [], [], 0
    for it in items:
        if it[0] == "br":
            rows.append(cur); cur, cw = [], 0; continue
        if cur and cw + it[1] + 8 > maxw - 20 and it[0] != "plus":
            # never end a row on an arrow: carry a trailing arrow to the next row
            carry = [cur.pop()] if cur[-1][0] in ("arr", "plus") else []
            rows.append(cur); cur = carry; cw = sum(c[1] + 8 for c in cur)
        cur.append(it); cw += it[1] + 8
    rows.append(cur)
    W = max(sum(it[1] for it in r) + 8 * (len(r) - 1) for r in rows) + 20
    body, y, k = [], 8, 0
    for r in rows:
        H = max([it[2][1] for it in r if it[0] == "mol"] or [40])
        rw = sum(it[1] for it in r) + 8 * (len(r) - 1)
        x, mid = (W - rw) / 2, y + H / 2
        has_lab = False
        for kind, w, d in r:
            if kind == "mol":
                inner, h = d
                body.append(f'<g transform="translate({x:.1f},{mid - h / 2:.1f})">{inner}</g>')
                if labels and k < len(labels) and labels[k]:
                    body.append(_t(x + w / 2, y + H + 14, labels[k], 12)); has_lab = True
                k += 1
            elif kind == "plus":
                body.append(_t(x + w / 2, mid + 6, "+", 20))
            else:
                body.append(_arrow(x + 2, mid, w - 4, d[1], d[2] if len(d) > 2 else "", d[0]))
            x += w + 8
        y += H + (26 if has_lab else 8)
    return _frame(title, note, _svg("".join(body), int(W), int(y + 4), re.sub("<[^>]+>", "", title)))

def choice(smi, bl=24):
    """Small inline structure for an answer choice."""
    inner, w, h = mol_svg(smi, bl)
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" style="max-width:100%;height:auto;vertical-align:middle" role="img" '
            f'aria-label="structure" xmlns="http://www.w3.org/2000/svg">{inner}</svg>')
