"""Batch 3 of standalone questions with figures: ECG strips, dose–response curves, Hardy–Weinberg tables,
cell-cycle DNA content and Behavioral Sciences study figures.
Run from the repo root: python3 tools/visual_discretes_3.py --write  (replaces ids starting with 'vq3-')."""
import json, math, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from passage_kit import line, bar, table
from bio_kit import ecg

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
    item = {"id": f"vq3-{subj}-{len([v for v in V if v['subj'] == subj]) + 1:03d}", "subj": subj, "unit": unit, "lv": lv,
            "q": q, "o": [right] + [w[0] for w in wrong], "a": 0, "e": e, "k": k, "w": [""] + [w[1] for w in wrong]}
    if fig: item["fig"] = inner(fig)
    if t: item["t"] = t
    V.append(item)


# ================================================================== ECG strips (Biology unit 7, cardiovascular)
for rr, name in [(0.8, "normal"), (0.5, "fast"), (1.2, "slow")]:
    beats = [0.3 + rr * i for i in range(int((4.0 - 0.3) / rr) + 1)]
    fig = ecg("ECG, lead II", beats)
    hr = round(60 / rr)
    add("bio", 7, "A", "Based on the ECG strip, what is the patient's heart rate?", f"{hr} beats per minute",
        [(f"{round(60 / (rr * 2))} beats per minute", "This uses two R–R intervals as one. Measure from one R peak to the very next."),
         (f"{round(60 / (rr / 2))} beats per minute", "This counts both the R wave and the T wave as beats. Only the tall QRS spikes are beats."),
         (f"{round(rr / 0.04)} beats per minute", f"This is the number of small boxes between R peaks ({round(rr / 0.04)}), not the rate."),
         (f"{round(60 * rr)} beats per minute", "This multiplies by the interval. Rate = 60 ÷ (R–R interval in seconds).")],
        [f"R–R interval = {round(rr / 0.2)} large boxes × 0.20 s = {rr} s.", f"Heart rate = 60 ÷ {rr} = {hr} beats per minute" + (" (tachycardia, above 100)." if hr > 100 else " (bradycardia, below 60)." if hr < 60 else " (normal range).")],
        2, fig, t="Rate ≈ 300 ÷ number of large boxes between R peaks.")
fig = ecg("ECG, lead II", [0.4 + 0.8 * i for i in range(5)], labels={"A": (0.24, 0.24), "B": (0.4, 1.45), "C": (0.68, 0.38)})
for wave, event, wr in [("B", "Ventricular depolarization", [("Atrial depolarization", "Atrial depolarization is the small P wave (A) before the QRS."), ("Ventricular repolarization", "Ventricular repolarization is the T wave (C)."), ("Atrial repolarization", "Atrial repolarization is hidden inside the QRS complex and has no separate wave.")]),
                        ("C", "Ventricular repolarization", [("Ventricular depolarization", "That is the QRS complex (B), the tall spike."), ("Atrial depolarization", "That is the P wave (A)."), ("Closure of the aortic valve", "Valves make sounds, not ECG waves. The ECG records electrical activity only.")])]:
    add("bio", 7, "F", f"On the labeled ECG strip, which event does wave {wave} represent?", event, wr,
        ["P wave (A): atria depolarize. QRS complex (B): ventricles depolarize. T wave (C): ventricles repolarize."], 1, fig)
fig = ecg("ECG, lead II", [0.45 + 0.9 * i for i in range(5)], pr=0.32)
add("bio", 7, "R", "On this strip, every P wave is followed by a QRS complex, but the P-to-R interval is 0.32 s (normal: 0.12–0.20 s). What does this most likely indicate?",
    "Slowed conduction through the AV node", [("A faster-than-normal heart rate", "The R–R interval is 0.9 s, about 67 beats per minute, which is normal."),
                                               ("Ventricles beating independently of the atria", "Every P wave still leads to a QRS. In complete block, P waves and QRS complexes lose their link."),
                                               ("Damage to the ventricular muscle", "The QRS (ventricular depolarization) is normal in width. Only the delay before it is long.")],
    ["The PR interval measures the time from atrial depolarization to ventricular depolarization, mostly delay in the AV node.", "A PR above 0.20 s with every beat conducted is first-degree AV block."], 4, fig)
fig = ecg("ECG, lead II", [0.5, 2.0, 3.5], p_times=[0.2 + 0.8 * i for i in range(5)])
add("bio", 7, "R", "In this strip, the P waves occur every 0.8 s and the QRS complexes every 1.5 s, with no fixed link between them. Which conclusion fits best?",
    "Atria and ventricles beat independently", [("The SA node has stopped firing completely", "Regular P waves show the SA node is still firing every 0.8 s."),
                                                     ("The ventricles beat faster than the atria", "The ventricles beat every 1.5 s (40 per minute), slower than the atria (75 per minute)."),
                                                     ("Conduction is normal but slow", "If conduction were only slow, every P would still be followed by a QRS at a fixed delay.")],
    ["No P wave reliably leads to a QRS: signals aren't crossing the AV node.", "A slower pacemaker in the ventricles takes over (third-degree, or complete, heart block)."], 4, fig)

# ================================================================== Dose–response (Biochem unit 3)
logd = [-9 + 0.25 * i for i in range(17)]  # 10⁻⁹ to 10⁻⁵ M
def resp(logc, ec50, emax=100, n=1): return emax / (1 + 10 ** (n * (ec50 - logc)))
curves = [("Drug A", -8, 100), ("Drug B", -6, 100), ("Drug C", -7, 50)]
fig = line("Dose–response curves", "log [drug] (M)", "Response (% of maximum)", [(n, [(round(x, 2), round(resp(x, e, m), 1)) for x in logd]) for n, e, m in curves],
           -5, 110, xmin=-9, xstep=1, ystep=20, w=460, h=290, points=False)
add("bc", 3, "A", "Based on the graph, which drug is the most potent?", "Drug A",
    [("Drug B", "Drug B reaches a full response but needs about 100 times more drug (EC<sub>50</sub> ≈ 10⁻⁶ M)."),
     ("Drug C", "Drug C has a lower maximum response. That's lower efficacy, and its EC<sub>50</sub> (10⁻⁷ M) is higher than A's."),
     ("Drugs A and B equally", "They have the same efficacy (100%), but A reaches half its maximum at a much lower dose.")],
    ["Potency is judged by EC<sub>50</sub>, the dose giving half the maximal response.", "Drug A: about 10⁻⁸ M, the lowest, so it is the most potent."], 4, fig)
add("bc", 3, "A", "How does drug C differ from drugs A and B?", "Lower efficacy (partial agonist)",
    [("Higher potency than drug A", "Drug C's EC<sub>50</sub> (10⁻⁷ M) is higher than A's (10⁻⁸ M), so it is less potent."),
     ("A full agonist like A and B", "Even at high doses, drug C reaches only 50% of the maximum response."),
     ("An antagonist with no effect", "Drug C does produce a response, up to 50%.")],
    ["Efficacy = the maximum response a drug can produce.", "Drug C plateaus at 50%, so it is a partial agonist."], 4, fig)
fig = line("Agonist alone and with two antagonists", "log [agonist] (M)", "Response (% of maximum)",
           [("Agonist alone", [(round(x, 2), round(resp(x, -8), 1)) for x in logd]), ("+ Antagonist X", [(round(x, 2), round(resp(x, -7), 1)) for x in logd]),
            ("+ Antagonist Y", [(round(x, 2), round(resp(x, -8, 55), 1)) for x in logd])], -5, 110, xmin=-9, xstep=1, ystep=20, w=460, h=290, points=False)
add("bc", 3, "R", "Based on the graph, antagonist X is most likely", "a competitive antagonist",
    [("a noncompetitive antagonist", "A noncompetitive antagonist lowers the maximum response, like antagonist Y."),
     ("a partial agonist", "Antagonist X doesn't produce a response on its own. It shifts the agonist's curve."),
     ("an inverse agonist", "Nothing in the graph shows activity below baseline.")],
    ["X shifts the curve to the right (EC<sub>50</sub> 10⁻⁸ → 10⁻⁷ M) without lowering the maximum.", "Enough agonist can outcompete it for the binding site: competitive antagonism."], 4, fig)
td = [-6 + 0.25 * i for i in range(17)]
fig = line("Therapeutic and toxic effects of a drug", "log [dose] (mg kg⁻¹)", "Patients responding (%)",
           [("Therapeutic effect", [(round(x, 2), round(resp(x, -5, 100, 2), 1)) for x in td]), ("Toxic effect", [(round(x, 2), round(resp(x, -3, 100, 2), 1)) for x in td])],
           -2, 110, xmin=-6, xstep=1, ystep=20, w=460, h=290, points=False)
add("bc", 3, "R", "What is the therapeutic index (TD<sub>50</sub>/ED<sub>50</sub>) of this drug?", "100",
    [("2", "This subtracts the log values (−3 − (−5)). The index is a ratio of doses: 10⁻³/10⁻⁵."),
     ("0.01", "This divides ED<sub>50</sub> by TD<sub>50</sub>. The index is TD<sub>50</sub>/ED<sub>50</sub>."),
     ("1000", "The curves are two log units apart, which is a factor of 100, not 1000.")],
    ["ED<sub>50</sub> = 10⁻⁵ mg kg⁻¹ and TD<sub>50</sub> = 10⁻³ mg kg⁻¹.", "TI = 10⁻³ ÷ 10⁻⁵ = 100: a wide safety margin."], 2, fig)

# ================================================================== Hardy–Weinberg (Biology unit 12)
hw1 = table("Genotypes in a population of 1,000 people", ["Genotype", "AA", "Aa", "aa"], [["Number", "360", "480", "160"]])
add("bio", 12, "A", "Based on the table, what is the frequency of allele A?", "0.6",
    [("0.36", "0.36 is the frequency of the AA genotype, not of the A allele."),
     ("0.84", "This adds AA and Aa as if both were all A. Each Aa person carries only one A."),
     ("0.4", "0.4 is the frequency of allele a.")],
    ["A alleles = 2(360) + 480 = 1200 out of 2000 alleles.", "<i>p</i> = 1200/2000 = 0.6."], 2, hw1)
add("bio", 12, "R", "Is the population in the table in Hardy–Weinberg equilibrium for this gene?", "Yes; observed counts match <i>p</i>², 2<i>pq</i>, <i>q</i>²",
    [("No; there are more heterozygotes than expected", "Expected Aa = 2(0.6)(0.4)(1000) = 480, which is exactly what was observed."),
     ("No; allele frequencies must be 0.5", "Hardy–Weinberg allows any allele frequencies. It predicts genotype ratios from them."),
     ("It can't be tested without the parents", "One generation's genotype counts are enough to compare with Hardy–Weinberg expectations.")],
    ["<i>p</i> = 0.6, <i>q</i> = 0.4. Expected: 360 AA, 480 Aa, 160 aa.", "Observed counts match exactly."], 4, hw1)
hw2 = table("Genotypes in an isolated village of 1,000 people", ["Genotype", "AA", "Aa", "aa"], [["Number", "500", "200", "300"]])
add("bio", 12, "R", "In the village shown, there are far fewer heterozygotes than Hardy–Weinberg predicts. Which explanation is most likely?", "Inbreeding",
    [("A new mutation creating allele a", "A new mutation would be rare and wouldn't specifically reduce heterozygotes."),
     ("Random mating", "Random mating produces Hardy–Weinberg proportions, which these counts don't match."),
     ("A very large population", "Large population size supports equilibrium. It doesn't explain a heterozygote shortage.")],
    ["<i>p</i> = (1000 + 200)/2000 = 0.6, so expected Aa = 2(0.6)(0.4) × 1000 = 480, but only 200 are observed.",
     "Mating between relatives increases homozygotes and lowers heterozygotes."], 4, hw2)
gens = [(g, round(0.5 / (1 + 0.5 * g * 0.05 * 2), 3)) for g in range(0, 41, 4)]
gens = [(0, .50), (4, .44), (8, .39), (12, .34), (16, .30), (20, .27), (24, .24), (28, .22), (32, .20), (36, .18), (40, .17)]
fig = line("Frequency of allele b in a laboratory fly population", "Generation", "Frequency of b", [("b", gens)], 40, 0.6, xstep=8, ystep=0.1, w=440, h=270)
add("bio", 12, "A", "In this population, recessive allele b causes small wings. What does the graph most likely show?", "Natural selection against bb flies",
    [("Genetic drift in a large population", "Drift is random and weak in large populations. A steady one-way decline points to selection."),
     ("Hardy–Weinberg equilibrium", "In equilibrium, allele frequencies stay constant over generations."),
     ("Selection favoring allele b", "Allele b is becoming less common, not more.")],
    ["The frequency of b falls steadily from 0.50 to 0.17.", "The decline slows as b becomes rare, because most b alleles then hide in heterozygotes, where selection can't act on them."], 4, fig)

# ================================================================== Cell cycle DNA content (Biology unit 2)
def hist(g1, s, g2):
    xs = [round(1.4 + 0.1 * i, 1) for i in range(30)]
    v = lambda x: g1 * math.exp(-((x - 2) / 0.12) ** 2) + g2 * math.exp(-((x - 4) / 0.18) ** 2) + (s if 2.2 < x < 3.8 else 0)
    return [(x, round(v(x), 1)) for x in xs]
for title, g1, s, g2, q, right, wr, e in [
    ("Untreated, dividing cells", 100, 14, 30, "In the untreated sample, the cells in the peak at 4 units of DNA are in which phase(s)?", "G2 or M",
     [("G1 or G0", "G1 and G0 cells haven't copied their DNA yet: they form the peak at 2 units."), ("S (DNA synthesis)", "S-phase cells are partway through copying: they fall between 2 and 4 units."), ("Early S", "Early S cells have only begun copying their DNA, so they sit just above 2 units.")],
     ["After S phase, each cell has twice its G1 amount of DNA.", "Cells with 4 units are in G2 or mitosis (before the cell splits)."]),
    ("Cells treated with nocodazole (blocks spindle formation)", 18, 8, 110, "After treatment with nocodazole, which stops the mitotic spindle from forming, the cells mostly", "arrest in mitosis with doubled DNA",
     [("arrest in G1 before replicating", "The large peak is at 4 units, so most cells have already replicated their DNA."),
      ("die during S phase", "The S-phase region isn't enlarged, and nothing in the histogram shows death."),
      ("divide faster than untreated cells", "Faster division would not pile cells up at 4 units.")],
     ["Without a spindle, chromosomes can't separate.", "Cells finish S and G2 but stall in mitosis, so the 4-unit peak grows."]),
    ("Cells treated with hydroxyurea (blocks DNA synthesis)", 140, 4, 6, "Hydroxyurea blocks the production of DNA building blocks. Based on the histogram, the treated cells", "stall at the G1/S boundary",
     [("arrest in G2", "G2 cells have 4 units of DNA. The treated cells nearly all have 2."),
      ("arrest in mitosis", "Mitotic cells have 4 units. The 4-unit peak almost disappeared."),
      ("lose half of their DNA content", "The main peak is at 2 units, the normal G1 amount, not 1.")],
     ["Without new nucleotides, cells can't replicate DNA.", "They stall at the G1/S boundary with 2 units, and the S and 4-unit populations drain away."])]:
    fig = line(f"Flow cytometry: {title}", "DNA content per cell (arbitrary units)", "Number of cells", [("cells", hist(g1, s, g2))], 4.3, 150, xmin=1.4, xstep=0.5, ystep=30, w=440, h=270, points=False)
    add("bio", 2, "A", q, right, wr, e, 4, fig)
mei = [(0, 2), (1, 2), (1.01, 2), (2, 4), (3, 4), (3.01, 2), (4, 2), (4.01, 1), (5, 1)]
fig = line("DNA content per cell during meiosis", "Stage", "DNA content (C)", [("DNA", mei)], 5, 5, xstep=1, ystep=1, w=440, h=270,
           vlines=[(1, "S"), (3, "MI"), (4, "MII")], points=False)
add("bio", 2, "R", "According to the graph (MI = end of meiosis I, MII = end of meiosis II), between stages 3 and 4 the cells are", "haploid, with sister chromatids still joined",
    [("diploid, with sister chromatids still joined", "Meiosis I separated the homologous pairs, so each cell is already haploid."),
     ("haploid, with single chromatids", "Sister chromatids don't separate until meiosis II, which is why the DNA content is still 2C."),
     ("diploid, with single chromatids", "That describes no stage of meiosis.")],
    ["Meiosis I separates homologs: chromosome number halves, but each chromosome still has two chromatids (2C).", "Meiosis II separates sister chromatids, giving 1C haploid cells."], 4, fig)

# ================================================================== Behavioral Sciences
fig = bar("Participants who helped someone having a seizure (heard over an intercom)", "Helped within 4 min (%)", ["Alone", "1 other present", "4 others present"], [("%", [85, 62, 31], None)], 100, step=20, w=420, h=260)
add("beh", 9, "A", "Which concept best explains the pattern in the graph?", "Diffusion of responsibility",
    [("Social facilitation by observers", "Social facilitation concerns performance improving with an audience, not helping."),
     ("Group polarization in a crowd", "Group polarization is the strengthening of opinions after group discussion."),
     ("Deindividuation", "Deindividuation is losing self-awareness in a crowd, often linked to antisocial acts.")],
    ["Helping fell as the number of bystanders rose (85% → 31%).", "Each person feels less personally responsible when others could help: the bystander effect."], 4, fig)
cum = {"Fixed ratio": [(0, 0), (2, 60), (2.5, 60), (4.5, 120), (5, 120), (7, 180), (7.5, 180), (9.5, 240), (10, 240)],
       "Variable ratio": [(0, 0), (2, 80), (4, 160), (6, 240), (8, 320), (10, 400)],
       "Fixed interval": [(0, 0), (1.5, 5), (2.5, 40), (3, 42), (4.5, 48), (5.5, 85), (6, 87), (7.5, 92), (8.5, 128), (10, 135)]}
fig = line("Cumulative responses under three reinforcement schedules", "Time (min)", "Cumulative responses", [(k, v) for k, v in cum.items()], 10, 450, xstep=2, ystep=100, w=460, h=290, points=False)
add("beh", 3, "A", "Which schedule in the graph produces the highest, steadiest response rate?", "Variable ratio",
    [("Fixed ratio", "Fixed ratio responding is high but pauses after each reinforcer (flat steps)."),
     ("Fixed interval", "Fixed interval responding is low after each reward and speeds up near the end of the interval (scallops)."),
     ("All three are equal", "The variable ratio line is the steepest and has no pauses.")],
    ["The steepest straight line means a high, constant rate.", "Unpredictable reward after a varying number of responses (like a slot machine) keeps responding high and steady."], 4, fig)
add("beh", 3, "C", "The scalloped pattern of the fixed interval line shows that the animal", "responds faster as the reward time nears",
    [("responds at a constant rate", "The line flattens after each reward and steepens later, so the rate changes."),
     ("stops responding after the first reward", "Responses keep accumulating through the whole session."),
     ("is reinforced after a set number of responses", "That describes a fixed ratio schedule. Fixed interval depends on time.")],
    ["After each reward, responding drops (flat part), then speeds up as the next interval ends (steeper part).", "Animals learn the timing of the schedule."], 4, fig)
fig = bar("Performance with and without an audience", "Score (% correct)", ["Simple task", "Complex task"], [("Alone", [70, 62], None), ("Audience", [84, 45], None)], 100, step=20, w=420, h=260)
add("beh", 8, "A", "Which concept best explains the results in the graph?", "Social facilitation",
    [("Social loafing", "Social loafing is reduced effort when individual work is pooled in a group, not an audience effect."),
     ("Groupthink", "Groupthink concerns group decision-making that values harmony over critical thinking."),
     ("The bystander effect", "The bystander effect concerns helping in emergencies.")],
    ["An audience raises arousal.", "Arousal improves well-learned, simple tasks (70 → 84%) but impairs complex ones (62 → 45%)."], 4, fig)
night = [(0, 0), (0.1, 0), (0.1, 1), (0.3, 1), (0.3, 2), (0.5, 2), (0.5, 3), (0.6, 3), (0.6, 4), (1.1, 4), (1.1, 3), (1.2, 3), (1.2, 2), (1.35, 2), (1.35, 5), (1.5, 5), (1.5, 2), (1.7, 2), (1.7, 3), (1.9, 3), (1.9, 4), (2.3, 4), (2.3, 3), (2.4, 3), (2.4, 2), (2.6, 2), (2.6, 5), (2.9, 5), (2.9, 2), (3.3, 2), (3.3, 3), (3.6, 3), (3.6, 2), (4.0, 2), (4.0, 5), (4.45, 5), (4.45, 2), (5.2, 2), (5.2, 5), (5.85, 5), (5.85, 1), (6.1, 1), (6.1, 2), (6.6, 2), (6.6, 5), (7.5, 5), (7.5, 1), (7.8, 1), (7.8, 0), (8.0, 0)]
fig = line("Sleep stages across one night (5 = REM, 1–4 = deeper non-REM, 0 = awake)", "Hours after falling asleep", "Stage", [("stage", night)], 8, 5.5, xstep=1, ystep=1, w=460, h=270, points=False)
add("beh", 4, "C", "Which pattern does the graph show?", "REM periods grow longer later in the night",
    [("Deep sleep (stage 4) increases late in the night", "Stage 4 appears mainly in the first part of the night and disappears later."),
     ("REM sleep occurs only at the start of the night", "The first REM period is short; REM returns about every 90 minutes and lengthens."),
     ("The sleeper stays in one stage all night", "The sleeper cycles through stages about every 90 minutes.")],
    ["Early cycles contain the most deep (slow-wave) sleep.", "Later cycles contain longer REM periods, which is why dreams are common near morning."], 4, fig)
fig = bar("Recall of 20 words after a night of sleep or sleep deprivation", "Words recalled", ["Slept 8 h", "Awake all night"], [("words", [14.2, 9.6], None)], 20, step=4, w=380, h=260)
add("beh", 4, "A", "In this study, 40 students were randomly assigned to sleep or stay awake after learning a word list. What is the independent variable?", "Sleep or no sleep",
    [("The number of words recalled", "Recall is what was measured: the dependent variable."),
     ("The 20-word list", "The list was the same for everyone, so it's held constant."),
     ("The students' ages", "Age wasn't manipulated. Random assignment spreads such differences across groups.")],
    ["The independent variable is what the researcher changes: sleep vs. no sleep.", "The dependent variable is what's measured: words recalled."], 3, fig)
exp = [(0, 3.1), (1, 3.4), (2, 3.7), (5, 4.1), (10, 4.4), (25, 4.6)]
fig = line("Liking of unfamiliar faces by number of prior exposures", "Times the face was seen", "Liking rating (1–7)", [("liking", exp)], 25, 7, xstep=5, ystep=1, w=420, h=260)
add("beh", 8, "C", "Which phenomenon does the graph illustrate?", "The mere exposure effect",
    [("The halo effect", "The halo effect is judging one trait from another (e.g., attractive = kind)."),
     ("Cognitive dissonance", "Cognitive dissonance is discomfort from holding conflicting beliefs or acting against them."),
     ("The foot-in-the-door technique", "Foot-in-the-door is a compliance technique using a small first request.")],
    ["Liking rose simply with repeated exposure (3.1 → 4.6).", "People tend to prefer things they've encountered more often."], 4, fig)

print(len(V), "visual discrete questions (batch 3)")


def insert(path="practice.html"):
    src = open(path, encoding="utf-8").read()
    m = re.search(r"\nconst Q = (\[.*?\]);\n", src, re.S)
    Q = [q for q in json.loads(m.group(1)) if not q["id"].startswith("vq3-")] + V
    src = src[:m.start(1)] + json.dumps(Q, ensure_ascii=False, separators=(", ", ": ")) + src[m.end(1):]
    open(path, "w", encoding="utf-8").write(src)


if __name__ == "__main__" and "--write" in sys.argv:
    insert(); print("written")
