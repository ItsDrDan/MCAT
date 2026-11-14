"""Batch 2 of standalone questions with figures: Lineweaver–Burk plots, gels, IR and ¹H NMR spectra,
Punnett squares, action-potential traces and Behavioral Sciences graphs.
Run from the repo root: python3 tools/visual_discretes_2.py --write  (replaces ids starting with 'vq2-')."""
import json, math, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from passage_kit import line, bar, table
from chem_kit import ir_spectrum, nmr_spectrum
from bio_kit import gel, punnett

V = []


def inner(fig):
    return re.sub(r'^<figure class="qfig">|</figure>$', "", fig.strip())


def add(subj, unit, lv, q, right, wrong, e, k, fig="", t=""):
    plain = lambda o: re.sub("<[^>]+>", "", o)
    keep, seen = [], {plain(right)}
    for w in wrong:
        if plain(w[0]) not in seen:
            keep.append(w); seen.add(plain(w[0]))
    assert len(keep) >= 3, (q, right, wrong)
    wrong = keep[:3]
    item = {"id": f"vq2-{subj}-{len([v for v in V if v['subj'] == subj]) + 1:03d}", "subj": subj, "unit": unit, "lv": lv,
            "q": q, "o": [right] + [w[0] for w in wrong], "a": 0, "e": e, "k": k, "w": [""] + [w[1] for w in wrong]}
    if fig: item["fig"] = inner(fig)
    if t: item["t"] = t
    V.append(item)


def fmt(x, nd=2):
    return f"{x:.{nd}f}".rstrip("0").rstrip(".").replace("-", "−")


# ================================================================== BIOCHEM: Lineweaver–Burk (unit 2)
def lb_line(Vm, Km, xs):
    return [(round(x, 3), round(Km / Vm * x + 1 / Vm, 4)) for x in xs]
xs = [-1.25, -1.0, -0.75, -0.5, -0.25, 0, 0.5, 1.0]
for Vm, Km, kind in [(50, 2, "competitive"), (40, 2, "noncompetitive"), (50, 4, "uncompetitive"), (25, 1, "competitive"), (20, 4, "noncompetitive")]:
    if kind == "competitive": Vm2, Km2 = Vm, Km * 2
    elif kind == "noncompetitive": Vm2, Km2 = Vm / 2, Km
    else: Vm2, Km2 = Vm / 2, Km / 2
    s1, s2 = lb_line(Vm, Km, xs), lb_line(Vm2, Km2, xs)
    lo_, hi_ = min(p[1] for p in s1 + s2), max(p[1] for p in s1 + s2)
    # pick the smallest "nice" step that keeps the y-axis to about 8 labels (0.04 alone gave 29 crowded labels)
    ystep = next(s for s in (0.02, 0.04, 0.05, 0.1, 0.2, 0.25, 0.5, 1.0) if (hi_ * 1.05 - lo_) / s <= 8)
    ymin, ymax = ystep * math.floor(lo_ / ystep), ystep * math.ceil(hi_ * 1.05 / ystep)
    fig = line("Lineweaver–Burk plot", "1/[S] (mM⁻¹)", "1/<i>V</i><sub>0</sub> (min µM⁻¹)",
               [("No inhibitor", s1), ("+ Inhibitor", s2)], 1.0, round(ymax, 3), xmin=-1.25, xstep=0.25, ymin=round(ymin, 3), ystep=ystep, w=440, h=290, points=False, yfmt=lambda y: f"{y:.2f}")
    expl = {"competitive": "lines meet on the y-axis (same <i>V</i><sub>max</sub>), and the inhibitor's line is steeper (higher apparent <i>K</i><sub>m</sub>)",
            "noncompetitive": "lines meet on the x-axis (same <i>K</i><sub>m</sub>), and the inhibitor raises the y-intercept (lower <i>V</i><sub>max</sub>)",
            "uncompetitive": "lines are parallel: both <i>V</i><sub>max</sub> and <i>K</i><sub>m</sub> fall by the same factor"}
    others = [x for x in ["competitive", "noncompetitive", "uncompetitive", "mixed (both <i>K</i><sub>m</sub> and <i>V</i><sub>max</sub> change)"] if x != kind]
    add("bc", 2, "A", "Based on the Lineweaver–Burk plot, which type of inhibition is shown?", kind.capitalize(),
        [(o[0].upper() + o[1:], ("In " + o + " inhibition, the " + expl[o] + ".") if o in expl else "In mixed inhibition, the lines cross to the left of the y-axis but off the x-axis.") for o in others],
        [f"Here the {expl[kind]}."], 4, fig, t="On a double-reciprocal plot, the y-intercept is 1/<i>V</i><sub>max</sub> and the x-intercept is −1/<i>K</i><sub>m</sub>.")
    if kind != "uncompetitive":
        add("bc", 2, "R", "From the line with no inhibitor, what is the enzyme's <i>K</i><sub>m</sub>?", f"{Km} mM",
            [(f"{fmt(1 / Km)} mM", "This is the magnitude of the x-intercept, −1/<i>K</i><sub>m</sub>. Take its reciprocal."),
             (f"{Vm} mM", "This is <i>V</i><sub>max</sub> (from the y-intercept), a rate, not a concentration."),
             (f"{fmt(Km / Vm, 3)} mM", "This is the slope (<i>K</i><sub>m</sub>/<i>V</i><sub>max</sub>), not <i>K</i><sub>m</sub>."),
             (f"{Km * 2} mM", "Read the x-intercept of the no-inhibitor line: −1/<i>K</i><sub>m</sub>.")],
            [f"x-intercept = −1/<i>K</i><sub>m</sub> = {fmt(-1 / Km)} mM⁻¹.", f"<i>K</i><sub>m</sub> = {Km} mM."], 4, fig)

# ================================================================== BIOCHEM: gels (units 3 and 6)
ladder = [10000, 6000, 4000, 3000, 2000, 1500, 1000, 500, 250]
# restriction digest of a 6000 bp circular plasmid
cases = [("EcoRI", [1000], "6,000 bp (one band)", [6000]), ("BamHI", [1000, 3000], "2,000 and 4,000 bp", [4000, 2000]),
         ("HindIII", [500, 2000, 4500], "1,500, 2,000 and 2,500 bp", [2500, 2000, 1500])]
lanes = [("1", [4000, 2000]), ("2", [6000]), ("3", [2500, 2000, 1500]), ("4", [5000, 1000])]
fig = gel("Restriction digests of a 6,000 bp circular plasmid", lanes, ladder=ladder)
for enz, sites, sizes, bands in cases:
    lane = [l for l, b in lanes if sorted(b) == sorted(bands)][0]
    pos = ", ".join(str(s) for s in sites)
    others = [l for l, _ in lanes if l != lane]
    add("bc", 6, "A", f"A 6,000 bp circular plasmid has {len(sites)} {enz} site{'s' if len(sites) > 1 else ''} (at position{'s' if len(sites) > 1 else ''} {pos}). Which lane shows the complete {enz} digest?",
        f"Lane {lane}", [(f"Lane {o}", f"Lane {o} shows {', '.join(f'{x:,}' for x in dict(lanes)[o])} bp. Cutting a circle at {len(sites)} site{'s' if len(sites) > 1 else ''} gives {len(sites)} fragment{'s' if len(sites) > 1 else ''}: {sizes}.") for o in others],
        [f"A circular molecule cut at <i>n</i> sites gives <i>n</i> fragments.", f"Fragments: {sizes}, which matches lane {lane}."], 2, fig,
        t="Fragments from a circular plasmid must add up to the plasmid's full length.")
# paternity / STR style
fig = gel("DNA fingerprints at one STR locus", [("Mother", [320, 260]), ("Child", [320, 300]), ("Man A", [300, 240]), ("Man B", [280, 220]), ("Man C", [340, 260])], ladder=[400, 350, 300, 250, 200], unit="bp", h=260)
add("bio", 12, "A", "The gel shows one STR (short tandem repeat) locus for a mother, her child and three men. Based on this locus, which man could be the biological father?", "Man A",
    [("Man B", "Man B has neither 300 nor 320 bp. The child's 300 bp band, which didn't come from the mother, must come from the father."),
     ("Man C", "Man C shares 260 bp with the mother, but the child didn't inherit a 260 bp band."),
     ("Men A and C", "Only man A carries the 300 bp allele that the child must have received from the father.")],
    ["The child has 320 bp (shared with the mother) and 300 bp.", "The 300 bp allele must come from the father. Only man A has it. (One locus can exclude men but can't prove fatherhood.)"], 4, fig)
# SDS-PAGE with and without reducing agent
fig = gel("SDS-PAGE of a purified protein", [("−BME", [150000]), ("+BME", [50000, 25000])], ladder=[250000, 150000, 100000, 75000, 50000, 37000, 25000, 15000], unit="Da", h=280)
add("bc", 3, "R", "A purified protein was run on SDS-PAGE with and without β-mercaptoethanol (BME), which breaks disulfide bonds. What is the most likely structure of the protein?",
    "Two 50 kDa + two 25 kDa chains",
    [("One single 150 kDa chain with no subunits", "With BME, the 150 kDa band splits into 50 and 25 kDa bands, so the protein has several chains."),
     ("One 50 kDa and one 25 kDa chain", "That adds up to only 75 kDa, but the intact protein is 150 kDa."),
     ("Six identical 25 kDa chains held by disulfides", "BME reveals two different chain sizes (50 and 25 kDa), not one.")],
    ["Without BME: one 150 kDa band, so the chains are held together by disulfides.", "With BME: 50 and 25 kDa chains. 2 × 50 + 2 × 25 = 150 kDa, like an antibody (two heavy and two light chains)."], 4, fig)

# ================================================================== ORGANIC: IR spectra (unit 11)
irs = [("1-butanol", [(3350, .8, 170), (2950, .5, 35), (1050, .6, 30)], "broad O–H stretch near 3300 cm⁻¹ and no C=O"),
       ("butanone", [(2970, .4, 35), (1715, .9, 22)], "strong C=O near 1715 cm⁻¹ and no O–H"),
       ("butanoic acid", [(3000, .7, 380), (1710, .9, 25)], "very broad O–H from about 3300 to 2500 cm⁻¹ plus C=O near 1710 cm⁻¹"),
       ("ethyl acetate", [(2980, .35, 35), (1740, .9, 22), (1240, .8, 35)], "C=O near 1740 cm⁻¹ and a strong C–O stretch near 1240 cm⁻¹, with no O–H"),
       ("butanenitrile", [(2960, .4, 35), (2250, .7, 18)], "sharp C≡N stretch near 2250 cm⁻¹"),
       ("butylamine", [(3370, .45, 40), (3290, .45, 40), (2950, .5, 35), (1600, .3, 30)], "two sharp N–H peaks near 3300–3400 cm⁻¹ (a primary amine) and no C=O")]
names = [n for n, _, _ in irs]
for i, (name, pk, why) in enumerate(irs):
    fig = ir_spectrum("IR spectrum of an unknown", pk)
    others = [names[(i + d) % len(names)] for d in (1, 2, 3)]
    if max(len(o) for o in others) <= len(name):
        others[-1] = max((n for n in names if n != name and n not in others[:2]), key=len)
    reason = {"1-butanol": "An alcohol shows a broad O–H band near 3300 cm⁻¹ with no C=O.", "butanone": "A ketone shows a strong C=O near 1715 cm⁻¹ with no O–H.",
              "butanoic acid": "A carboxylic acid shows a very broad O–H band (3300–2500 cm⁻¹) plus C=O.", "ethyl acetate": "An ester shows C=O near 1740 cm⁻¹ and a strong C–O band, with no O–H.",
              "butanenitrile": "A nitrile shows a sharp C≡N band near 2250 cm⁻¹.", "butylamine": "A primary amine shows two sharp N–H peaks near 3300–3400 cm⁻¹."}
    add("oc", 11, "C", "Which compound best matches the IR spectrum shown?", name.capitalize(), [(o.capitalize(), reason[o] + " That isn't what this spectrum shows.") for o in others],
        [f"Key feature: {why}."], 4, fig)

# ================================================================== ORGANIC: ¹H NMR (unit 11)
nmrs = [("ethyl acetate", [(4.1, 4, 2, "2H"), (2.0, 1, 3, "3H"), (1.2, 3, 3, "3H")], "a 3H singlet at 2.0 (CH<sub>3</sub> next to C=O) and a 2H quartet at 4.1 (CH<sub>2</sub> on O, next to CH<sub>3</sub>)"),
        ("methyl propanoate", [(3.7, 1, 3, "3H"), (2.3, 4, 2, "2H"), (1.1, 3, 3, "3H")], "a 3H singlet at 3.7 (CH<sub>3</sub> on O) and a 2H quartet at 2.3 (CH<sub>2</sub> next to C=O)"),
        ("propanoic acid", [(11.5, 1, 1, "1H"), (2.4, 4, 2, "2H"), (1.1, 3, 3, "3H")], "a 1H singlet near 11.5 ppm (COOH)"),
        ("2-butanone", [(2.4, 4, 2, "2H"), (2.1, 1, 3, "3H"), (1.0, 3, 3, "3H")], "a 3H singlet at 2.1 and a 2H quartet at 2.4, both next to C=O, with no signal above 3 ppm"),
        ("2-propanol", [(4.0, 7, 1, "1H"), (2.2, 1, 1, "1H"), (1.2, 2, 6, "6H")], "a 6H doublet (two equivalent CH<sub>3</sub>) and a 1H septet at 4.0 (CH on O)"),
        ("toluene", [(7.2, 1, 5, "5H"), (2.3, 1, 3, "3H")], "a 5H signal near 7.2 ppm (benzene ring) and a 3H singlet at 2.3")]
nnames = [n for n, _, _ in nmrs]
fmls = {"ethyl acetate": "C<sub>4</sub>H<sub>8</sub>O<sub>2</sub>", "methyl propanoate": "C<sub>4</sub>H<sub>8</sub>O<sub>2</sub>", "propanoic acid": "C<sub>3</sub>H<sub>6</sub>O<sub>2</sub>",
        "2-butanone": "C<sub>4</sub>H<sub>8</sub>O", "2-propanol": "C<sub>3</sub>H<sub>8</sub>O", "toluene": "C<sub>7</sub>H<sub>8</sub>"}
for i, (name, sig, why) in enumerate(nmrs):
    fig = nmr_spectrum("¹H NMR spectrum of an unknown", sig, xmax=12 if name == "propanoic acid" else 10)
    others = [nnames[(i + d) % len(nnames)] for d in (1, 2, 3)]
    if name in ("ethyl acetate", "methyl propanoate"):  # put the isomer in as a distractor
        iso = "methyl propanoate" if name == "ethyl acetate" else "ethyl acetate"
        others = [iso] + [o for o in others if o != iso][:2]
    if max(len(o) for o in others) <= len(name):
        others[-1] = max((n for n in nnames if n != name and n not in others[:2]), key=len)
    add("oc", 11, "A", "Which compound best matches the ¹H NMR spectrum shown? (Peak labels give the number of H.)", f"{name.capitalize()}",
        [(o.capitalize(), f"{o.capitalize()} ({fmls[o]}) would show a different pattern: compare the shifts, the splitting (n + 1 rule) and the H counts.") for o in others],
        [f"Key features: {why}.", "Splitting follows the n + 1 rule: a quartet means 3 neighboring H, a triplet 2, a doublet 1."], 4, fig)

# ================================================================== BIOLOGY: Punnett squares (unit 12)
fig = punnett("Punnett square for the cross", ["RY", "Ry", "rY", "ry"], ["RY", "Ry", "rY", "ry"])
add("bio", 12, "C", "In pea plants, round seeds (R) are dominant to wrinkled (r) and yellow (Y) is dominant to green (y). Two RrYy plants are crossed, as set up in the Punnett square. What fraction of offspring will have wrinkled, yellow seeds?",
    "3/16", [("9/16", "9/16 have both dominant traits (round and yellow)."), ("1/16", "1/16 have both recessive traits (wrinkled and green)."), ("1/4", "1/4 is the chance of wrinkled alone. It must be multiplied by 3/4 for yellow.")],
    ["P(rr) = 1/4; P(Y_) = 3/4.", "Independent genes: 1/4 × 3/4 = 3/16."], 2, fig)
add("bio", 12, "A", "For the same RrYy × RrYy cross, what fraction of offspring will be true-breeding (homozygous) for both genes?", "1/4",
    [("1/16", "1/16 is one specific homozygous genotype, such as RRYY. There are four: RRYY, RRyy, rrYY and rryy."),
     ("9/16", "9/16 is the fraction showing both dominant traits, not the fraction that is homozygous."),
     ("1/2", "P(homozygous) for one gene is 1/2, but both genes must be homozygous: 1/2 × 1/2.")],
    ["P(homozygous at R) = 1/2 (RR or rr); same for Y.", "1/2 × 1/2 = 1/4."], 2, fig)
fig = punnett("Cross between a carrier mother and an affected father", ["X<sup>h</sup>", "Y"], ["X<sup>H</sup>", "X<sup>h</sup>"])
add("bio", 12, "A", "Hemophilia A is X-linked recessive. A carrier woman (X<sup>H</sup>X<sup>h</sup>) has children with an affected man (X<sup>h</sup>Y). What fraction of their DAUGHTERS will be affected?", "1/2",
    [("0", "Every daughter gets X<sup>h</sup> from her father, so a daughter is affected whenever she also gets X<sup>h</sup> from her mother (1/2)."),
     ("1/4", "1/4 is the fraction of ALL children who are affected daughters. Among daughters only, it's 1/2."),
     ("1", "Half of the daughters get X<sup>H</sup> from their mother and are carriers, not affected.")],
    ["Daughters: X<sup>h</sup> from father + X<sup>H</sup> or X<sup>h</sup> from mother.", "So 1/2 are X<sup>h</sup>X<sup>h</sup> (affected) and 1/2 are carriers."], 2, fig)
fig = table("Results of a test cross: AaBb × aabb", ["Offspring phenotype", "Number"], [["A_B_ (parental)", "412"], ["aabb (parental)", "398"], ["A_bb (recombinant)", "96"], ["aaB_ (recombinant)", "94"]])
add("bio", 12, "R", "A dihybrid AaBb was test-crossed to aabb, giving the offspring in the table. What is the distance between genes A and B?", "19 map units",
    [("50 map units", "50% recombinants would mean the genes assort independently. Here the parental classes are far more common."),
     ("81 map units", "81% is the parental fraction. Map distance comes from the recombinant fraction."),
     ("9.5 map units", "This counts only one recombinant class. Add both: 96 + 94.")],
    ["Recombinants = 96 + 94 = 190 out of 1000.", "Recombination frequency = 19% = 19 map units (cM)."], 4, fig)

# ================================================================== BIOLOGY: action potentials (unit 4)
ap = [(0, -70), (1, -70), (1.5, -55), (2, 30), (2.5, 10), (3, -40), (3.5, -80), (4.5, -75), (6, -70)]
fig = line("Membrane potential of a neuron during an action potential", "Time (ms)", "Membrane potential (mV)", [("Vm", ap)], 6, 40, ymin=-90, xstep=1, ystep=20, w=440, h=280,
           vlines=[(1.5, "threshold"), (3.5, "undershoot")])
for q, right, wr, e in [
    ("During the rising phase (1.5–2 ms), the change in membrane potential is mainly caused by", "Na⁺ flowing into the cell",
     [("K⁺ flowing into the cell", "K⁺ mostly flows out, and K⁺ efflux causes repolarization, not depolarization."),
      ("K⁺ flowing out of the cell", "K⁺ efflux makes the inside more negative, which is repolarization (2–3.5 ms)."),
      ("The Na⁺/K⁺ pump moving ions", "The pump is far too slow to cause a millisecond spike. It maintains gradients over the long term.")],
     ["At threshold, voltage-gated Na⁺ channels open.", "Na⁺ rushes in down its electrochemical gradient, driving the potential toward +30 mV."]),
    ("Why does the membrane potential dip below −70 mV at about 3.5 ms?", "K⁺ channels stay open",
     [("Na⁺ channels reopen briefly", "Na⁺ influx would make the inside more positive, not more negative."),
      ("The Na⁺/K⁺ pump stops", "Stopping the pump wouldn't make the potential suddenly more negative."),
      ("Cl⁻ flows out of the cell", "Cl⁻ leaving would make the inside more positive.")],
     ["Voltage-gated K⁺ channels close slowly.", "Extra K⁺ leaves the cell, so the potential briefly overshoots past rest toward the K⁺ equilibrium potential (about −90 mV)."]),
    ("Tetrodotoxin (TTX), a pufferfish toxin, blocks voltage-gated Na⁺ channels. If TTX were applied before the stimulus, the trace would most likely", "show no spike",
     [("reach a higher peak", "Blocking Na⁺ channels removes the inward current that creates the peak."),
      ("repolarize more slowly", "Repolarization depends on K⁺ channels, but without Na⁺ entry there is no spike to repolarize."),
      ("start from a more positive resting potential", "The resting potential depends mostly on K⁺ leak channels, which TTX doesn't block.")],
     ["Without voltage-gated Na⁺ channels, depolarization can't become self-reinforcing.", "The membrane may depolarize slightly from the stimulus, but no action potential fires."]),
]:
    add("bio", 4, "C", q, right, wr, e, 4, fig)

# ================================================================== BEHAVIORAL SCIENCES
serial = [(p, v) for p, v in zip(range(1, 16), [78, 66, 58, 48, 42, 38, 36, 35, 36, 38, 44, 52, 64, 76, 84])]
delayed = [(p, v) for p, v in zip(range(1, 16), [74, 62, 54, 45, 40, 36, 34, 33, 33, 34, 35, 34, 35, 36, 35])]
fig = line("Free recall of a 15-word list", "Position of word in the list", "Recalled (%)", [("Immediate recall", serial), ("Recall after 30 s of counting backward", delayed)],
           15, 100, xmin=1, xstep=2, ystep=20, w=460, h=290)
add("beh", 3, "A", "In the graph, words at the end of the list are recalled well immediately but poorly after a 30-second distraction. What does this best show?", "The recency effect depends on short-term memory",
    [("The primacy effect depends on short-term memory", "The early-list advantage (primacy) stays after the delay, so it reflects long-term memory."),
     ("Distraction erases long-term memory", "Early words, held in long-term memory, are recalled about as well after the delay."),
     ("Words in the middle are encoded best", "Middle words are recalled worst under both conditions.")],
    ["The last few words are still in short-term memory at immediate recall.", "Counting backward displaces them, so the recency effect disappears while primacy (long-term memory) stays."], 4, fig)
add("beh", 3, "C", "Why are the first few words recalled better than the middle words, even after the delay?", "They were rehearsed more",
    [("They are still in short-term memory", "If so, the delay would erase their advantage, as it did for the last words."),
     ("They are shorter words", "Nothing in the graph concerns word length; the effect depends on position."),
     ("They were presented more loudly", "All words were presented the same way. Position alone changes recall.")],
    ["Early words get more rehearsal before new words arrive.", "Rehearsal transfers them into long-term memory (primacy effect), which survives the distraction."], 4, fig)

cond = [(0, 0), (1, 20), (2, 45), (3, 65), (4, 78), (5, 85), (6, 87), (7, 70), (8, 45), (9, 22), (10, 10), (11, 5), (12, 40), (13, 18), (14, 6)]
fig = line("Salivation in a classical conditioning experiment", "Trial block", "Saliva to the tone (drops)", [("Response", cond)], 14, 100, xstep=2, ystep=20, w=460, h=290,
           vlines=[(6.5, "tone alone"), (11.5, "after 24 h rest")])
add("beh", 3, "A", "In the graph, the response to the tone returns briefly after a 24-hour rest (block 12). This is called", "spontaneous recovery",
    [("extinction", "Extinction is the decline in blocks 7–11, when the tone was no longer paired with food."),
     ("acquisition", "Acquisition is the rise in blocks 0–6 while the tone was paired with food."),
     ("stimulus generalization", "Generalization is responding to a similar stimulus. The same tone is used throughout.")],
    ["After extinction and a rest, the conditioned response reappears at a reduced level.", "This shows extinction suppresses, rather than erases, the original learning."], 4, fig)

easy = [(x, round(95 * math.exp(-((x - 7) / 3.5) ** 2) + 5, 1)) for x in range(0, 11)]
hard = [(x, round(95 * math.exp(-((x - 4) / 3.0) ** 2) + 5, 1)) for x in range(0, 11)]
fig = line("Performance and arousal", "Arousal (0 = very low, 10 = very high)", "Performance (%)", [("Simple task", easy), ("Complex task", hard)], 10, 110, xstep=2, ystep=20, w=440, h=280, points=False)
add("beh", 5, "C", "Which conclusion is best supported by the graph?", "Complex tasks peak at lower arousal",
    [("Higher arousal always improves performance", "Both curves fall at high arousal, so more arousal eventually hurts."),
     ("Arousal has no effect on complex tasks", "Performance on the complex task changes a lot with arousal."),
     ("Simple tasks peak at lower arousal", "The simple-task curve peaks to the right (about 7), later than the complex task (about 4).")],
    ["Both curves are inverted U's (the Yerkes–Dodson law).", "The complex-task curve peaks at a lower arousal level than the simple-task curve."], 4, fig)

weber = table("Smallest noticeable difference in weight", ["Standard weight (g)", "Just-noticeable difference (g)"], [["100", "2"], ["200", "4"], ["500", "10"], ["1000", "?"]])
add("beh", 2, "A", "Based on the table, what is the just-noticeable difference for a 1000 g standard, if Weber's law holds?", "20 g",
    [("2 g", "This assumes the JND is constant. Weber's law says it's a constant fraction of the standard."),
     ("12 g", "This adds 2 g per step. The JND grows in proportion to the standard (2%)."),
     ("200 g", "This uses 20%. The table shows a constant 2% (2/100, 4/200, 10/500).")],
    ["Weber fraction = ΔI/I = 2/100 = 0.02 for every row.", "For 1000 g: 0.02 × 1000 = 20 g."], 2, "<figure class=\"qfig\">" + inner(weber) + "</figure>")

ages = ["0–14", "15–29", "30–44", "45–59", "60–74", "75+"]
fig = bar("Population by age group in two countries (% of population)", "% of population", ages, [("Country A", [40, 27, 17, 10, 5, 1], None), ("Country B", [14, 17, 19, 21, 18, 11], None)], 45, step=10, w=460, h=280)
add("beh", 11, "A", "Which statement about the two countries in the graph is best supported?", "Country A is at an earlier transition stage",
    [("Country B has the higher birth rate of the two", "Country B has a small share of children, which points to a lower birth rate."),
     ("Country A has a higher life expectancy", "Country A has few people over 60, which suggests lower life expectancy."),
     ("Both countries have similar age structures", "Country A is dominated by young people; country B is much older.")],
    ["Country A: many children, few elderly → high birth and death rates (early stage).", "Country B: fewer children, more older adults → low birth and death rates (late stage)."], 4, fig)

hours = [("0–1", 12), ("1–2", 18), ("2–3", 26), ("3–4", 34), ("4+", 43)]
fig = bar("Adolescents reporting depressive symptoms by daily social media use (survey of 6,000 students)", "% reporting symptoms", [h[0] for h in hours], [("%", [h[1] for h in hours], None)], 50, step=10, w=440, h=270)
add("beh", 7, "A", "A researcher concludes from this survey that social media use causes depression. What is the main problem with this conclusion?", "Correlation can't show cause",
    [("The sample size of 6,000 is too small", "6,000 students is a large sample."),
     ("There is no relationship in the data", "Symptoms rise steadily with use, so there is a relationship."),
     ("The y-axis should show raw numbers", "Percentages are appropriate when group sizes differ.")],
    ["The data show an association, not a cause.", "Depressed teens might use social media more (reverse causation), or a third factor such as poor sleep might affect both."], 3, fig)

print(len(V), "visual discrete questions (batch 2)")


def insert():
    """Insert or replace this script's questions (ids starting with "vq2-") in the bank (data/bank/q-*.js)."""
    import sys as _s; from pathlib import Path as _P; _s.path.insert(0, str(_P(__file__).resolve().parent)); import bank
    Q, P = bank.load()
    Q = [q for q in Q if not q["id"].startswith("vq2-")] + V
    bank.save("Q", Q)


if __name__ == "__main__" and "--write" in sys.argv:
    insert(); print("written")
