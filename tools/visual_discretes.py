"""Standalone (discrete) questions that come with a figure, table or structure.
Each generator draws the figure from the same numbers it uses to compute the answer.
Run from the repo root: python3 tools/visual_discretes.py  (inserts/replaces ids starting with 'vq-' in practice.html's Q)."""
import json, math, re, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from passage_kit import line, bar, table
from chem_kit import energy_diagram, phase_diagram
from physics_kit import fbd, circuit, rays
from orgo_kit import structures, choice
from bio_kit import pedigree

R = random.Random(11)
V = []


def inner(fig):
    """Strip the outer <figure class="qfig"> so the app's own figure wrapper isn't doubled."""
    return re.sub(r'^<figure class="qfig">|</figure>$', "", fig.strip())


def add(subj, unit, lv, q, right, wrong, e, k, fig="", t=""):
    plain = lambda o: re.sub("<[^>]+>", "", o)
    keep, seen = [], {plain(right)}
    for w in wrong:  # drop any distractor that happens to equal the answer or another distractor
        if plain(w[0]) not in seen:
            keep.append(w); seen.add(plain(w[0]))
    assert len(keep) >= 3, (q, right, wrong)
    wrong = keep[:3]
    opts = [right] + [w[0] for w in wrong]
    item = {"id": f"vq-{subj}-{len([v for v in V if v['subj'] == subj]) + 1:03d}", "subj": subj, "unit": unit, "lv": lv,
            "q": q, "o": opts, "a": 0, "e": e, "k": k, "w": [""] + [w[1] for w in wrong]}
    if fig: item["fig"] = inner(fig)
    if t: item["t"] = t
    V.append(item)


def fmt(x, nd=2):
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return s.replace("-", "−")


# ================================================================== GENERAL CHEMISTRY
# --- energy diagrams: Ea forward / reverse / ΔH (units 5 and 7)
for i, (r, ts, p) in enumerate([(10, 80, -40), (20, 110, 60), (0, 55, -120), (10, 90, 30), (-20, 70, -90), (0, 130, 50), (30, 95, -10), (0, 60, 20)]):
    lo = min(r, p, 0) - 20; hi = max(ts, 0) + 20
    lo, hi = 20 * math.floor(lo / 20), 20 * math.ceil(hi / 20)
    fig = energy_diagram("Energy profile (values in kJ mol⁻¹)", [("", [r, ts, p])], lo, hi, ystep=20 if hi - lo <= 140 else 40,
                         labels=[(0, r, fmt(r)), (1, ts, fmt(ts)), (2, p, fmt(p))])
    kind = ["fwd", "rev", "dH"][i % 3]
    ea_f, ea_r, dH = ts - r, ts - p, p - r
    if kind == "fwd":
        add("gc", 5, "C", "Based on the energy profile shown, what is the activation energy of the forward reaction?",
            f"{ea_f} kJ mol⁻¹", [(f"{ea_r} kJ mol⁻¹", "This is the barrier for the reverse reaction, measured from the products."),
                                 (f"{ts} kJ mol⁻¹", "This reads the peak's height from zero. Measure from the reactants' energy."),
                                 (f"{abs(dH)} kJ mol⁻¹", "This is the size of ΔH, the gap between reactants and products."),
                                 (f"{ea_f + abs(dH)} kJ mol⁻¹", "This adds ΔH to the barrier. The barrier is measured from the reactants to the peak only.")],
            [f"<i>E</i><sub>a</sub> = peak − reactants = {fmt(ts)} − ({fmt(r)}) = {ea_f} kJ mol⁻¹."], 4, fig)
    elif kind == "rev":
        add("gc", 5, "A", "Based on the energy profile shown, what is the activation energy of the reverse reaction?",
            f"{ea_r} kJ mol⁻¹", [(f"{ea_f} kJ mol⁻¹", "This is the forward barrier. The reverse reaction starts from the products."),
                                 (f"{abs(dH)} kJ mol⁻¹", "This is the size of ΔH, not a barrier."),
                                 (f"{ea_f + ea_r} kJ mol⁻¹", "This adds the two barriers. The reverse barrier alone is peak − products."),
                                 (f"{ts} kJ mol⁻¹", "This reads the peak's height from zero. Measure from the products' energy.")],
            [f"<i>E</i><sub>a,reverse</sub> = peak − products = {fmt(ts)} − ({fmt(p)}) = {ea_r} kJ mol⁻¹."], 4, fig)
    else:
        sign = "exothermic" if dH < 0 else "endothermic"
        other = "endothermic" if dH < 0 else "exothermic"
        add("gc", 7, "C", "What are ΔH and the type of reaction shown in the energy profile?",
            f"ΔH = {fmt(dH)} kJ mol⁻¹; {sign}", [(f"ΔH = {fmt(-dH)} kJ mol⁻¹; {other}", "This takes reactants − products. ΔH = products − reactants."),
                                                 (f"ΔH = {fmt(ea_f)} kJ mol⁻¹; endothermic", "This is the activation energy, not ΔH."),
                                                 (f"ΔH = {fmt(dH)} kJ mol⁻¹; {other}", f"A {'negative' if dH < 0 else 'positive'} ΔH means the reaction is {sign}."),
                                                 (f"ΔH = {fmt(ts)} kJ mol⁻¹; endothermic", "This reads the height of the peak, not the difference between products and reactants.")],
            [f"ΔH = products − reactants = {fmt(p)} − ({fmt(r)}) = {fmt(dH)} kJ mol⁻¹.", f"{'Products are lower: heat is released.' if dH < 0 else 'Products are higher: heat is absorbed.'}"], 4, fig)

# --- phase diagrams (unit 8)
water = dict(triple=(0.01, 0.006), critical=(374, 218), fusion_slope="negative", Tr=(-60, 420), Pr=(0.00001, 1000),
             ticksT=(0.01, 100, 374), ticksP=(0.006, 1, 218), extraT=[(100, .55)], extraP=[(1, .55)])
co2 = dict(triple=(-56.6, 5.1), critical=(31, 73), fusion_slope="positive", Tr=(-100, 60), Pr=(0.1, 400),
           ticksT=(-78.5, -56.6, 31), ticksP=(1, 5.1, 73), extraT=[(-78.5, .14)], extraP=[(1, .14)])
phase_q = [(water, "water", (-20, 1), "solid"), (water, "water", (50, 1), "liquid"), (water, "water", (150, 0.5), "gas"), (water, "water", (400, 300), "supercritical fluid"),
           (co2, "carbon dioxide", (-78.5, 0.5), "gas"), (co2, "carbon dioxide", (0, 60), "liquid"), (co2, "carbon dioxide", (-80, 20), "solid"), (co2, "carbon dioxide", (45, 150), "supercritical fluid")]
for d, name, (T, Pp), ans in phase_q:
    fig = phase_diagram(f"Phase diagram of {name} (not to scale)", d["triple"], d["critical"], d["fusion_slope"], d["Tr"], d["Pr"],
                        points=[(T, Pp, "X")], ticksT=d["ticksT"], ticksP=d["ticksP"], extraT=d["extraT"], extraP=d["extraP"])
    phases = ["solid", "liquid", "gas", "supercritical fluid"]
    why = {"solid": "Point X is to the left of the melting line and above the sublimation curve, which is the solid region.",
           "liquid": "Point X is between the melting line and the boiling curve, which is the liquid region.",
           "gas": "Point X is below the boiling and sublimation curves, which is the gas region.",
           "supercritical fluid": "Point X is beyond both the critical temperature and the critical pressure."}
    add("gc", 8, "F", f"In what phase is {name} at point X ({fmt(T, 1)} °C, {fmt(Pp, 3)} atm)?", ans,
        [(ph, f"X isn't in the {ph} region. " + why[ans]) for ph in phases if ph != ans],
        [why[ans], f"Compare X with the triple point ({fmt(d['triple'][0], 2)} °C, {fmt(d['triple'][1], 3)} atm) and the critical point ({fmt(d['critical'][0])} °C, {fmt(d['critical'][1])} atm)."], 4, fig)

# --- titration curves (unit 10)
def titr_curve(pKa, Ca=0.100, Va=25.0, Cb=0.100):
    Ka = 10 ** -pKa; pts = []; Veq = Ca * Va / Cb
    for Vb in [0, 2, 4, 6, 8, 10, 12.5, 15, 17.5, 20, 22, 24, 24.5, 25, 25.5, 26, 28, 30, 35, 40]:
        na, nb = Ca * Va / 1000, Cb * Vb / 1000; Vt = (Va + Vb) / 1000
        if Vb == 0:
            h = math.sqrt(Ka * Ca); ph = -math.log10(h)
        elif nb < na - 1e-9:
            ph = pKa + math.log10(nb / (na - nb))
        elif abs(nb - na) < 1e-9:
            Cconj = na / Vt; Kb = 1e-14 / Ka; ph = 14 + math.log10(math.sqrt(Kb * Cconj))
        else:
            ph = 14 + math.log10((nb - na) / Vt)
        pts.append((Vb, round(ph, 2)))
    return pts, Veq
for name, pKa in [("acetic acid", 4.76), ("formic acid", 3.75), ("lactic acid", 3.86), ("benzoic acid", 4.20), ("hypochlorous acid", 7.53), ("an unknown weak acid", 5.5)]:
    pts, Veq = titr_curve(pKa)
    fig = line(f"Titration of 25.0 mL of 0.100 M {name} with 0.100 M NaOH", "Volume of NaOH added (mL)", "pH", [("pH", pts)], 40, 14, xstep=5, ystep=2, w=440, h=280, points=False)
    add("gc", 10, "A", "Based on the titration curve, what is the p<i>K</i><sub>a</sub> of the acid?", fmt(pKa, 1),
        [(fmt([p for v, p in pts if v == 25.0][0], 1), "This is the pH at the equivalence point. The p<i>K</i><sub>a</sub> is read at the half-equivalence point."),
         (fmt(pts[0][1], 1), "This is the starting pH of the acid alone."),
         ("7.0", "pH 7 is neutral. For a weak acid titrated with strong base, the equivalence pH is above 7 and the p<i>K</i><sub>a</sub> is read halfway there.")],
        [f"Equivalence point: {Veq:.1f} mL (steep rise). Half of it: {Veq / 2:.1f} mL.", f"At half-equivalence, [HA] = [A⁻], so pH = p<i>K</i><sub>a</sub> ≈ {fmt(pKa, 1)}."], 4, fig,
        t="On any weak acid–strong base curve, find the steep jump first, then read the pH at half that volume.")
    if name == "an unknown weak acid" and False:
        pass

# --- successive ionization energies (unit 2): real third-row data
ies = {"sodium": ([496, 4562, 6910, 9543, 13354], 1), "magnesium": ([738, 1451, 7733, 10543, 13630], 2), "aluminum": ([578, 1817, 2745, 11577, 14842], 3),
       "silicon": ([787, 1577, 3232, 4356, 16091], 4), "phosphorus": ([1012, 1907, 2914, 4964, 6274], 5)}
names = list(ies)
for el, (vals, nval) in ies.items():
    fig = table("Successive ionization energies of element X (kJ mol⁻¹)", [f"IE<sub>{i + 1}</sub>" for i in range(5)], [[f"{v:,}" for v in vals]])
    others = [n for n in names if n != el]
    R.shuffle(others)
    wrong = []
    for o in others[:3]:
        wrong.append((o.capitalize(), f"{o.capitalize()} has {ies[o][1]} valence electron{'s' if ies[o][1] > 1 else ''}, so its large jump would come after IE<sub>{ies[o][1]}</sub>."))
    jump = f"after IE<sub>{nval}</sub>" if nval < 5 else "only after IE<sub>5</sub> (beyond the table)"
    add("gc", 2, "A", "Element X is in the third period. Based on its successive ionization energies, element X is most likely", el.capitalize(), wrong,
        [f"Look for the largest jump between neighboring values. It comes {jump}.", f"So X has {nval} valence electron{'s' if nval > 1 else ''}: {el}."], 4, fig)

# --- first-order kinetics from a graph (unit 5)
for i, (k_, c0, unit_) in enumerate([(0.0347, 0.80, "min"), (0.0231, 1.00, "min"), (0.1386, 0.40, "s"), (0.0693, 2.0, "h")]):
    t12 = math.log(2) / k_
    tmax = round(4 * t12)
    pts = [(round(t, 2), round(c0 * math.exp(-k_ * t), 3)) for t in [tmax * j / 8 for j in range(9)]]
    fig = line("Concentration of reactant over time", f"Time ({unit_})", "[A] (M)", [("[A]", pts)], tmax, c0 * 1.1, xstep=tmax / 4, ystep=round(c0 * 1.1 / 5, 2), w=440, h=270)
    add("gc", 5, "A", "The decay of reactant A shown in the graph is first order. What is its half-life?", f"{t12:.0f} {unit_}",
        [(f"{2 * t12:.0f} {unit_}", f"At {2 * t12:.0f} {unit_}, [A] has fallen to one-fourth of its starting value, which is two half-lives."),
         (f"{t12 / 2:.0f} {unit_}", f"At {t12 / 2:.0f} {unit_}, [A] has fallen only to about 71% of its starting value."),
         (f"{tmax:.0f} {unit_}", "This is the whole time shown, about four half-lives.")],
        [f"Start: {c0} M. Half: {c0 / 2:g} M.", f"[A] reaches {c0 / 2:g} M at about {t12:.0f} {unit_}. For first order, every half-life is the same length."], 4, fig)

# ================================================================== ORGANIC CHEMISTRY
# --- count stereocenters (RDKit-checked) (unit 2)
from rdkit import Chem
mols = [("Ibuprofen", "CC(C)Cc1ccc(cc1)C(C)C(=O)O"), ("Ephedrine", "CNC(C)C(O)c1ccccc1"), ("Threonine", "CC(O)C(N)C(=O)O"),
        ("Menthol", "CC(C)C1CCC(C)CC1O"), ("Glucose (open chain)", "OCC(O)C(O)C(O)C(O)C=O"), ("Lactic acid", "CC(O)C(=O)O"),
        ("Glycerol", "OCC(O)CO"), ("Isoleucine", "CCC(C)C(N)C(=O)O"), ("Pseudoephedrine", "CNC(C)C(O)c1ccccc1"), ("Citric acid", "OC(=O)CC(O)(CC(=O)O)C(=O)O")]
seen = set()
for name, smi in mols:
    if smi in seen: continue
    seen.add(smi)
    m = Chem.MolFromSmiles(smi)
    n = len(Chem.FindMolChiralCenters(m, includeUnassigned=True, useLegacyImplementation=False))
    fig = structures(f"Structure of {name.lower() if name[0].islower() else name}", [(smi, name)])
    opts = [n] + [x for x in [n + 1, n + 2, n - 1, 0, 3, 4] if x != n and x >= 0][:3]
    wrongs = []
    for x in opts[1:]:
        if x > n: why = "This counts a carbon that has two identical groups (such as two H atoms, two CH<sub>3</sub> groups or two identical chains)."
        else: why = "This misses a carbon bonded to four different groups."
        wrongs.append((str(x), why))
    add("oc", 2, "C", f"How many chiral centers does {name.lower() if name not in ('Ibuprofen', 'Menthol') else name} have?", str(n), wrongs,
        [f"A chiral center is an sp<sup>3</sup> carbon with four different groups.", f"{name} has {n}." + (" Citric acid's central carbon carries two identical –CH<sub>2</sub>COOH arms, so it is not chiral." if name == "Citric acid" else "")], 1, fig)

# --- functional groups from a drawn structure (unit 1 naming / 4)
fg = [("Acetaminophen", "CC(=O)Nc1ccc(O)cc1", "amide and phenol", ["ester and phenol", "amine and alcohol", "amide and carboxylic acid"]),
      ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O", "ester and carboxylic acid", ["ketone and carboxylic acid", "amide and ester", "ether and aldehyde"]),
      ("Procaine", "CCN(CC)CCOC(=O)c1ccc(N)cc1", "ester and amines", ["amide and amines", "ketone and ether", "carboxylic acid and amine"]),
      ("Testosterone", "CC12CCC3C(CCC4=CC(=O)CCC34C)C1CCC2O", "ketone, alkene and alcohol", ["aldehyde, alkene and alcohol", "ketone, alkyne and ether", "ester, alkene and alcohol"]),
      ("Vanillin", "COc1cc(C=O)ccc1O", "aldehyde, ether and phenol", ["ketone, ether and alcohol", "carboxylic acid, ether and phenol", "aldehyde, ester and phenol"]),
      ("Lidocaine", "CCN(CC)CC(=O)Nc1c(C)cccc1C", "amide and amine", ["ester and amine", "imine and amide", "nitrile and amine"])]
for name, smi, right, wr in fg:
    fig = structures(f"Structure of {name}", [(smi, name)])
    expl = {"ester": "an ester has C(=O)–O–C", "amide": "an amide has C(=O)–N", "ketone": "a ketone has C=O between two carbons",
            "aldehyde": "an aldehyde has C(=O)–H at the end of a chain", "carboxylic acid": "a carboxylic acid has C(=O)–OH",
            "phenol": "a phenol has –OH directly on a benzene ring", "alcohol": "an alcohol has –OH on an sp<sup>3</sup> carbon"}
    add("oc", 1, "F", f"Which functional groups are present in {name}?", right,
        [(w, f"{name} has no " + " or ".join(g for g in re.split(r", | and ", w) if g not in re.split(r", | and ", right)) + ". Look at what is bonded to each C=O, O and N.") for w in wr],
        [f"{name} contains: {right}.", "Look at what is attached to each C=O and each heteroatom."], 1, fig)

# ================================================================== PHYSICS
# --- free-body: net force and acceleration (unit 1)
for i, (m, F1, F2, fr) in enumerate([(4.0, 30, 10, 6), (2.0, 18, 0, 4), (5.0, 40, 15, 5), (10.0, 60, 20, 10), (3.0, 24, 6, 3), (8.0, 50, 10, 8)]):
    forces = [("<i>F</i><sub>1</sub> = %d N" % F1, 0, 0.9, "blue", (28, 0))]
    if F2: forces.append(("<i>F</i><sub>2</sub> = %d N" % F2, 180, 0.9 * F2 / F1 + .15, "pink", (-28, -12)))
    forces.append(("<i>f</i> = %d N" % fr, 180, 0.9 * fr / F1 + .15, "green", (-28, 14)))
    forces += [("<i>F</i><sub>N</sub>", 90, .6, "ink", (0, -22)), ("<i>mg</i>", -90, .6, "ink", (0, 22))]
    fig = fbd(f"Forces on a {m:g} kg block on a level floor", forces, h=260, w=440)
    net = F1 - F2 - fr; a = net / m
    add("pm", 1, "A", f"A {m:g} kg block slides to the right on a level floor under the horizontal forces shown (kinetic friction <i>f</i> acts to the left). What is the block's acceleration?",
        f"{fmt(a)} m s⁻² to the right",
        [(f"{fmt((F1 - F2) / m)} m s⁻² to the right", "This leaves out friction, which also opposes the motion."),
         (f"{fmt((F1 + F2 + fr) / m)} m s⁻² to the right", "This adds every force. Forces to the left must be subtracted."),
         (f"{fmt(net)} m s⁻² to the right", f"This is the net force in newtons. Divide by the mass ({m:g} kg).")],
        [f"Net horizontal force = {F1} − {F2} − {fr} = {net} N.", f"<i>a</i> = <i>F</i><sub>net</sub>/<i>m</i> = {net}/{m:g} = {fmt(a)} m s⁻². Vertical forces cancel."], 2, fig)

# --- circuits: equivalent resistance and current (unit 6)
cir = [((60, 6, 12, 4), "series-parallel"), ((12, 2, 6, 3), "series-parallel"), ((24, 8, 12, 12), "series-parallel"), ((18, 1, 3, 6), "series-parallel"), ((9, 1, 4, 4), "series-parallel"), ((30, 3, 6, 3), "series-parallel")]
for (V_, R1, R2, R3), _ in cir:
    fig = circuit("Circuit", [("battery", (50, 190), (50, 50), f"{V_} V"), ("wire", (50, 50), (80, 50)), ("R", (80, 50), (200, 50), f"<i>R</i><sub>1</sub> = {R1} Ω"),
                              ("wire", (200, 50), (250, 50)), ("wire", (250, 50), (350, 50)), ("R", (250, 50), (250, 190), f"<i>R</i><sub>2</sub> = {R2} Ω"),
                              ("R", (350, 50), (350, 190), f"<i>R</i><sub>3</sub> = {R3} Ω"), ("wire", (350, 190), (250, 190)), ("wire", (250, 190), (50, 190))],
                  w=440, h=230, nodes=[(250, 50), (250, 190)])
    Rp = R2 * R3 / (R2 + R3); Req = R1 + Rp; I = V_ / Req
    add("pm", 6, "A", "In the circuit shown, what current flows through the battery?", f"{fmt(I)} A",
        [(f"{fmt(V_ / (R1 + R2 + R3))} A", "This puts all three resistors in series. <i>R</i><sub>2</sub> and <i>R</i><sub>3</sub> are in parallel."),
         (f"{fmt(V_ / R1)} A", "This uses only <i>R</i><sub>1</sub>. The parallel pair adds resistance too."),
         (f"{fmt(V_ / Rp)} A", "This leaves out <i>R</i><sub>1</sub>, which is in series with the parallel pair."),
         (f"{fmt(V_ / (R1 + R2))} A", "This ignores <i>R</i><sub>3</sub>. Current splits between <i>R</i><sub>2</sub> and <i>R</i><sub>3</sub>, which lowers the total resistance."),
         (f"{fmt(V_ / (R1 + R2 + R3) * 3)} A", "This averages the resistors instead of combining them by the series and parallel rules.")],
        [f"Parallel: <i>R</i><sub>23</sub> = ({R2} × {R3})/({R2} + {R3}) = {fmt(Rp)} Ω.", f"Total: {R1} + {fmt(Rp)} = {fmt(Req)} Ω. <i>I</i> = {V_}/{fmt(Req)} = {fmt(I)} A."], 2, fig)

# --- lenses and mirrors (unit 8)
for kind, f_, d_, h_ in [("converging lens", 10, 30, 3), ("converging lens", 20, 30, 2), ("converging lens", 15, 10, 2), ("diverging lens", 10, 15, 3),
                         ("concave mirror", 10, 15, 2), ("concave mirror", 20, 12, 2), ("convex mirror", 15, 30, 3), ("converging lens", 12, 36, 3)]:
    fs = f_ if kind in ("converging lens", "concave mirror") else -f_
    di = 1 / (1 / fs - 1 / d_); m = -di / d_
    real = di > 0
    desc = f"{'real' if real else 'virtual'}, {'inverted' if m < 0 else 'upright'}, {'enlarged' if abs(m) > 1 else 'reduced'}"
    fig = rays(f"Ray diagram: {kind}", kind, f_, d_, h_)
    alts = ["real, inverted, enlarged", "real, inverted, reduced", "virtual, upright, enlarged", "virtual, upright, reduced", "real, upright, reduced"]
    wrong = [a for a in alts if a != desc][:3]
    side = "on the far side of the lens" if ("lens" in kind and real) else ("in front of the mirror" if real else ("on the same side as the object" if "lens" in kind else "behind the mirror"))
    add("pm", 8, "C", f"An object is placed {d_} cm from a {kind} with a focal length of magnitude {f_} cm, as shown. The image is",
        desc, [(w, "Check the sign of the image distance (real if positive) and the size of |<i>m</i>| = |<i>i</i>/<i>o</i>|.") for w in wrong],
        [f"1/<i>i</i> = 1/({fmt(fs)}) − 1/{d_} → <i>i</i> = {fmt(di, 1)} cm ({side}).", f"<i>m</i> = −<i>i</i>/<i>o</i> = {fmt(m, 2)}: {desc}."], 2, fig)

# --- velocity-time graphs (unit 1)
for vt in [[(0, 0), (4, 12), (10, 12), (12, 0)], [(0, 5), (5, 15), (10, 15)], [(0, 20), (8, 0)], [(0, 0), (6, 18), (9, 18)]]:
    fig = line("Velocity of a cart", "Time (s)", "Velocity (m s⁻¹)", [("v", vt)], vt[-1][0], max(v for t, v in vt) * 1.25, xstep=2 if vt[-1][0] <= 12 else 4, w=420, h=260)
    area = sum((t2 - t1) * (v1 + v2) / 2 for (t1, v1), (t2, v2) in zip(vt, vt[1:]))
    slope0 = (vt[1][1] - vt[0][1]) / (vt[1][0] - vt[0][0])
    add("pm", 1, "C", f"How far does the cart travel during the {vt[-1][0]} s shown in the graph?", f"{fmt(area)} m",
        [(f"{fmt(max(v for _, v in vt) * vt[-1][0])} m", "This multiplies the top speed by the total time, as if the cart moved at its top speed the whole time."),
         (f"{fmt(abs(slope0))} m", "This is the slope of the first segment (an acceleration), not a distance."),
         (f"{fmt(area / 2)} m", "This halves the area. Only the triangle-shaped parts are halved.")],
        ["Displacement = area under a velocity–time graph.", f"Adding the triangles and rectangles: {fmt(area)} m."], 4, fig)

# ================================================================== BIOCHEMISTRY
# --- Michaelis–Menten / inhibitors (unit 2)
def mm(Vm, Km, S): return Vm * S / (Km + S)
for Vm, Km, inh in [(100, 2, "competitive"), (80, 5, "noncompetitive"), (120, 4, "competitive"), (60, 1, "noncompetitive"), (90, 3, "uncompetitive")]:
    Ss = [0, 1, 2, 4, 6, 8, 12, 16, 20]
    if inh == "competitive": Vm2, Km2 = Vm, Km * 3
    elif inh == "noncompetitive": Vm2, Km2 = Vm / 2, Km
    else: Vm2, Km2 = Vm / 2, Km / 2
    fig = line("Reaction rate vs substrate concentration", "[S] (mM)", "<i>V</i><sub>0</sub> (µM min⁻¹)",
               [("No inhibitor", [(s, round(mm(Vm, Km, s), 1)) for s in Ss]), ("+ Inhibitor", [(s, round(mm(Vm2, Km2, s), 1)) for s in Ss])],
               20, 20 * math.ceil(Vm * 1.2 / 20), xstep=2, ystep=20, w=440, h=280)
    expl = {"competitive": "the inhibitor raises the apparent <i>K</i><sub>m</sub> but leaves <i>V</i><sub>max</sub> unchanged; at high [S] the curves meet",
            "noncompetitive": "the inhibitor lowers <i>V</i><sub>max</sub> but leaves <i>K</i><sub>m</sub> unchanged; half of each curve's maximum is reached at the same [S]",
            "uncompetitive": "the inhibitor lowers both <i>V</i><sub>max</sub> and <i>K</i><sub>m</sub> by the same factor"}
    others = [x for x in ["competitive", "noncompetitive", "uncompetitive", "irreversible (covalent)"] if x != inh]
    add("bc", 2, "A", "Based on the graph, which type of reversible inhibition is shown?", inh.capitalize(),
        [(o.capitalize(), ("With " + o + " inhibition, " + expl[o] + ".") if o in expl else "Nothing in a single rate curve shows covalent binding. The data fit a reversible pattern.") for o in others],
        [f"No inhibitor: <i>V</i><sub>max</sub> ≈ {Vm}, <i>K</i><sub>m</sub> ≈ {Km} mM. With inhibitor: <i>V</i><sub>max</sub> ≈ {fmt(Vm2)}, <i>K</i><sub>m</sub> ≈ {fmt(Km2)} mM.", f"So {expl[inh]}."], 4, fig)
    add("bc", 2, "C", "Based on the curve with no inhibitor, what is the approximate <i>K</i><sub>m</sub> of the enzyme?", f"{Km} mM",
        [(f"{Vm} mM", "This is the <i>V</i><sub>max</sub> value read off the y-axis, not a substrate concentration."),
         (f"{Km * 2} mM", f"At {Km * 2} mM the rate is about {fmt(mm(Vm, Km, 2 * Km) / Vm * 100, 0)}% of <i>V</i><sub>max</sub>, not half."),
         (f"{fmt(Vm / 2)} mM", "This is half of <i>V</i><sub>max</sub> (a rate). <i>K</i><sub>m</sub> is the [S] where the rate reaches that value.")],
        [f"<i>V</i><sub>max</sub> ≈ {Vm} µM min⁻¹, so half of it is {fmt(Vm / 2)}.", f"The rate reaches {fmt(Vm / 2)} at [S] = {Km} mM = <i>K</i><sub>m</sub>."], 4, fig)

# --- oxygen dissociation curves (unit 3 protein function)
def hb(p, p50, n=2.7): return 100 * p ** n / (p50 ** n + p ** n)
for cond, p50b, ans, wr in [("during intense exercise (lower pH, higher CO<sub>2</sub>, higher temperature)", 33, "Curve B", [("Curve A", "Curve A is shifted left, which means higher O<sub>2</sub> affinity, the opposite of the Bohr effect."), ("Neither; the curve doesn't move", "Lower pH, more CO<sub>2</sub> and heat all lower hemoglobin's affinity for O<sub>2</sub>."), ("Both curves equally", "Only a right shift fits these conditions.")]),
                            ("in fetal blood (fetal hemoglobin binds 2,3-BPG weakly)", 19, "Curve A", [("Curve B", "Curve B is shifted right (lower affinity). Fetal hemoglobin has higher affinity."), ("Neither; the curve doesn't move", "Fetal hemoglobin's weak 2,3-BPG binding raises its O<sub>2</sub> affinity."), ("Both curves equally", "Only a left shift fits higher affinity.")])]:
    pts = [0, 10, 20, 30, 40, 50, 60, 80, 100]
    fig = line("Hemoglobin O<sub>2</sub> saturation", "<i>P</i><sub>O₂</sub> (mmHg)", "Saturation (%)",
               [("Normal adult", [(p, round(hb(p, 26), 1)) for p in pts]), ("Curve A", [(p, round(hb(p, 19), 1)) for p in pts]), ("Curve B", [(p, round(hb(p, 33), 1)) for p in pts])],
               100, 110, xstep=20, ystep=20, w=440, h=290, points=False)
    add("bc", 3, "C", f"Which curve best represents hemoglobin {cond}?", ans, wr,
        ["A left shift (lower <i>P</i><sub>50</sub>) means higher O<sub>2</sub> affinity; a right shift means lower affinity.", f"{ans} has a <i>P</i><sub>50</sub> of about {p50b} mmHg vs 26 mmHg normally."], 4, fig)

# ================================================================== BIOLOGY
# --- pedigree mode-of-inheritance (unit 12)
peds = [
    ("Autosomal dominant", {"a": (1, 1, "M", "A"), "b": (1, 2.5, "F", "U"), "c": (2, 0.5, "M", "A"), "d": (2, 1.5, "F", "U"), "e": (2, 2.5, "M", "U"), "f": (2, 3.5, "F", "A"), "g": (3, 0.5, "M", "A"), "h": (3, 1.5, "F", "A")},
     [("a", "b"), ("c", "d")], [(("a", "b"), ["c", "e", "f"]), (("c", "d"), ["g", "h"])],
     "It appears in every generation, every affected child has an affected parent, and affected fathers pass it to sons (I-1 → II-1, II-1 → III-1).",
     [("X-linked dominant", "Fathers pass their Y, not their X, to sons. Father-to-son transmission (I-1 → II-1) rules out X-linkage."),
      ("Autosomal recessive", "This would require both spouses who married into the family (I-2, II-2) to be carriers, and the trait appears in every generation."),
      ("Mitochondrial", "Mitochondrial traits pass only through mothers, but here affected fathers have affected children.")]),
    ("Autosomal recessive", {"a": (1, 1, "M", "U"), "b": (1, 2.5, "F", "U"), "c": (2, 0.5, "F", "A"), "d": (2, 1.5, "M", "U"), "e": (2, 2.5, "F", "U"), "f": (2, 3.5, "M", "A")},
     [("a", "b")], [(("a", "b"), ["c", "d", "e", "f"])],
     "Two unaffected parents have affected children of both sexes. An affected daughter (II-1) with an unaffected father rules out X-linked recessive.",
     [("Autosomal dominant", "Two unaffected parents can't have an affected child with a dominant allele (barring a new mutation)."),
      ("X-linked recessive", "An affected daughter (II-1) would need an affected father, but I-1 is unaffected."),
      ("Mitochondrial", "Mitochondrial disease passes from an affected mother, but the mother here (I-2) is unaffected.")]),
    ("X-linked recessive", {"a": (1, 1, "M", "U"), "b": (1, 2.5, "F", "U"), "c": (2, 0.5, "M", "A"), "e": (2, 1.5, "M", "U"), "d": (2, 2.5, "F", "U"), "f": (2, 3.5, "M", "U"),
                            "g": (3, 2.5, "M", "A"), "h": (3, 3.5, "F", "U")},
     [("a", "b"), ("d", "f")], [(("a", "b"), ["c", "d", "e"]), (("d", "f"), ["g", "h"])],
     "Only males are affected, and each affected male's mother (I-2, II-3) is unaffected: a carrier passing the allele on her X.",
     [("Autosomal dominant", "Affected sons (II-1, III-1) have two unaffected parents, which doesn't fit a dominant trait."),
      ("Mitochondrial", "Mitochondrial disease passes from affected mothers to all their children. These mothers are unaffected."),
      ("X-linked dominant", "With an X-linked dominant trait, the mothers of affected sons would themselves be affected.")]),
    ("X-linked dominant", {"a": (1, 1, "M", "A"), "b": (1, 2.5, "F", "U"), "c": (2, 0.5, "F", "A"), "d": (2, 1.5, "M", "U"), "e": (2, 2.5, "F", "A"), "f": (2, 3.5, "M", "U"),
                           "g": (3, 2, "M", "A"), "h": (3, 3, "F", "U")},
     [("a", "b"), ("e", "f")], [(("a", "b"), ["c", "d", "e"]), (("e", "f"), ["g", "h"])],
     "The affected father (I-1) passes it to both daughters and not to his son, and his affected daughter (II-3) passes it to a son.",
     [("X-linked recessive", "Daughters II-1 and II-3 are affected even though their mother is unaffected, which doesn't fit a recessive X-linked trait."),
      ("Mitochondrial", "An affected father (I-1) has affected children, but fathers don't transmit mitochondria."),
      ("Autosomal recessive", "Affected people appear in every generation with only one affected parent, which fits a dominant trait better.")]),
]
for ans, ppl, cps, fams, why, wr in peds:
    fig = pedigree("Pedigree", ppl, couples=cps, families=fams, w=380, slot=60)
    add("bio", 12, "A", "Which mode of inheritance is most consistent with the pedigree shown? (Filled symbols are affected.)", ans, wr, [why], 4, fig)

print(len(V), "visual discrete questions")


def insert():
    """Insert or replace this script's questions (ids starting with "vq-") in the bank (data/bank/q-*.js)."""
    import sys as _s; from pathlib import Path as _P; _s.path.insert(0, str(_P(__file__).resolve().parent)); import bank
    Q, P = bank.load()
    Q = [q for q in Q if not q["id"].startswith("vq-")] + V
    bank.save("Q", Q)


if __name__ == "__main__" and "--write" in sys.argv:
    insert()
    print("written")
