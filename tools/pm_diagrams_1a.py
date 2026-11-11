"""Physics passages with diagrams, batch 1 (part A): Motion & forces, Work & energy, Electrostatics."""
from passage_kit import passage, table, line, bar, eq
from physics_kit import fbd, svg_figure, _arrow, _line, _txt, COL, INK, MUTED

P = []

# ---------------------------------------------------------------- Unit 1 · Motion & forces
P.append(passage("pms-01", "cp", "pm", 1, "Keeping Patients From Sliding Down the Bed", [
    "Hospital beds are often tilted so that a patient's head is raised (to help breathing) or lowered (to help blood return to the heart). On a tilted bed, a patient tends to slide toward the foot. Nurses then have to pull the patient back up, which can injure both the nurse and the patient's skin.",
    "The forces on a patient lying on a tilted surface are shown in Figure 1. Gravity (<i>F</i><sub>g</sub> = <i>mg</i>) acts straight down. The normal force <i>F</i><sub>N</sub> acts perpendicular to the surface, and static friction <i>f</i> acts up the slope, parallel to the surface. If the patient does not move, the forces balance:",
    "<span class=\"eq\"><i>F</i><sub>N</sub> = <i>mg</i> cos θ&emsp;&emsp;and   <i>f</i> = <i>mg</i> sin θ</span>",
    fbd("Figure 1 Forces on a patient on a bed tilted at angle θ", [("<i>F</i><sub>g</sub>", -90, 1.0, "pink"), ("<i>F</i><sub>N</sub>", 60, 0.87, "blue"), ("<i>f</i>", 150, 0.5, "green")], incline=30),
    "Static friction can be no larger than μ<sub>s</sub><i>F</i><sub>N</sub>, where μ<sub>s</sub> is the coefficient of static friction. Sliding begins at the angle where the friction needed equals this maximum, so at that angle tan θ = μ<sub>s</sub>.",
    "To choose a sheet material, engineers placed a 70 kg test dummy on a bed covered with each material and slowly raised the head of the bed until the dummy began to slide. Each material was tested five times; the mean angle is reported (Table 1; hypothetical data). Use g = 10 m s⁻².",
    table("Table 1 Angle at which sliding began", ["Sheet material", "Mean angle (°)", "tan θ"],
          [["Cotton", "31", "0.60"], ["Polyester blend", "22", "0.40"], ["Silicone-grip fabric", "45", "1.00"], ["Low-friction slide sheet", "8", "0.14"]]),
], [
    dict(q="For the 70 kg dummy on a bed tilted at 30° that is not sliding, what is the friction force? (sin 30° = 0.50, cos 30° = 0.87)",
         right="350 N", wrong=[("610 N", "This uses cos 30°. The friction force balances the component of gravity along the slope, mg sin θ."),
                               ("700 N", "This is the full weight. Only part of the weight acts along the slope."),
                               ("35 N", "This forgets g. Multiply the mass by 10 m s⁻² to get the weight.")],
         e=["Weight = 70 kg × 10 m s⁻² = 700 N.", "<i>f</i> = <i>mg</i> sin 30° = 700 × 0.50 = 350 N."], k=2),
    dict(q="As the head of the bed is raised from 10° to 30°, what happens to the normal force on the dummy?",
         right="It decreases", wrong=[("It increases", "<i>F</i><sub>N</sub> = <i>mg</i> cos θ, and cos θ gets smaller as θ grows."),
                                      ("It stays equal to <i>mg</i>", "The normal force equals <i>mg</i> only on a flat (θ = 0) surface."),
                                      ("It becomes zero", "It would be zero only at 90°, when the bed is vertical.")],
         e=["<i>F</i><sub>N</sub> = <i>mg</i> cos θ.", "cos 10° ≈ 0.98 and cos 30° ≈ 0.87, so the normal force falls."], k=1),
    dict(q="What is the coefficient of static friction between the dummy and cotton?", right="0.60",
         wrong=[("0.52", "This is sin 31°. At the slipping angle, μ<sub>s</sub> = tan θ."),
                ("31", "31 is the angle in degrees. μ<sub>s</sub> has no units and equals tan θ."),
                ("0.86", "This is cos 31°. Use tan θ.")],
         e=["At the slipping angle, <i>mg</i> sin θ = μ<sub>s</sub><i>mg</i> cos θ.", "So μ<sub>s</sub> = tan 31° ≈ 0.60. The mass cancels."], k=2),
    dict(q="A hospital wants the head of the bed raised to 30° without patients sliding, while still letting staff move patients easily when needed. Which plan best fits the data in Table 1?",
         right="Cotton sheets, with slide sheets only for moves",
         wrong=[("Slide sheets left under the patient all the time", "With μ<sub>s</sub> = 0.14, slipping starts at 8°, far below 30°."),
                ("Polyester-blend sheets for every patient at all times", "Polyester slips at 22°, below the 30° needed."),
                ("Any material, since mass cancels in tan θ = μ<sub>s</sub>", "Mass cancels, but μ<sub>s</sub> differs between materials. That's what Table 1 shows.")],
         e=["Cotton holds until 31°, just above 30° (silicone-grip, at 45°, would also hold).",
            "A slide sheet (8°) makes moving easy but must be removed afterward."], k=4),
    dict(q="Why does the conclusion tan θ = μ<sub>s</sub> not depend on the dummy's mass being 70 kg?",
         right="Both forces are proportional to <i>mg</i>",
         wrong=[("Heavier objects have larger μ<sub>s</sub>", "μ<sub>s</sub> depends on the two surfaces, not on the object's mass."),
                ("The test was repeated five times for each material", "Repeating a test reduces random error. It doesn't explain why mass cancels."),
                ("Friction does not depend on the normal force", "Maximum static friction is μ<sub>s</sub><i>F</i><sub>N</sub>, so it does depend on the normal force.")],
         e=["Gravity's component along the slope is <i>mg</i> sin θ; maximum friction is μ<sub>s</sub><i>mg</i> cos θ.",
            "Setting them equal, <i>mg</i> cancels, leaving tan θ = μ<sub>s</sub>."], k=3),
]))

# traction figure: leg pulled by a rope over a pulley
tr = []
tr.append('<rect x="40" y="170" width="380" height="14" rx="4" fill="#f4f1fa" stroke="' + INK + '" stroke-width="1.5"/>')
tr.append(_txt(70, 200, "bed", 11, fill=MUTED))
tr.append('<rect x="90" y="132" width="170" height="30" rx="14" fill="#ffe6cc" stroke="' + INK + '" stroke-width="1.5"/>')
tr.append(_txt(170, 152, "leg", 12))
tr.append('<circle cx="400" cy="70" r="14" fill="#fff" stroke="' + INK + '" stroke-width="2"/>')
tr.append(_line(400, 70, 400, 30, INK, 2) + _line(370, 30, 430, 30, INK, 3))
tr.append(_line(262, 147, 389, 79, INK, 2))
tr.append(_line(414, 70, 414, 210, INK, 2))
tr.append('<rect x="398" y="210" width="32" height="34" rx="4" fill="#e7defc" stroke="' + INK + '" stroke-width="1.5"/>')
tr.append(_txt(414, 231, "<i>m</i>", 12))
tr.append(_arrow(262, 147, 330, 111, COL["blue"], 3, 11) + _txt(300, 108, "<i>T</i>", 13, fill=COL["blue"]))
tr.append(f'<path d="M300,147 A38,38 0 0 0 296,129" fill="none" stroke="{MUTED}" stroke-width="1.5"/>' + _txt(310, 140, "θ", 12, fill=MUTED))
tr.append(_line(262, 147, 330, 147, MUTED, 1.2, "4 3"))
P.append(passage("pms-02", "cp", "pm", 1, "Traction on a Broken Thigh Bone", [
    "When the femur (thigh bone) breaks, the large thigh muscles contract and pull the broken ends past each other. Traction counteracts this by applying a steady pull along the leg. In a simple setup (Figure 1), a rope attached to the leg runs over a pulley at the foot of the bed to a hanging mass <i>m</i>.",
    svg_figure("Figure 1 A simple traction setup (side view)", "".join(tr), 460, 260),
    "If the pulley is frictionless and the rope's mass is negligible, the tension <i>T</i> is the same everywhere in the rope and equals the weight of the hanging mass, <i>mg</i>. The rope pulls on the leg at angle θ above the horizontal. The horizontal component of the pull, <i>T</i> cos θ, stretches the leg along its length. The vertical component, <i>T</i> sin θ, lifts the leg slightly off the bed.",
    "A physical therapist measured the pull on a leg-shaped dummy with a force sensor while changing the hanging mass and the height of the pulley (Table 1). The sensor reads the force along the leg's length. Use g = 10 m s⁻².",
    table("Table 1 Force along the leg", ["Hanging mass (kg)", "Rope angle θ", "Measured force along leg (N)"],
          [["4.0", "0°", "39"], ["4.0", "30°", "34"], ["4.0", "60°", "20"], ["8.0", "30°", "68"]]),
    "Clinicians usually aim for a pull along the leg of about 1/7 to 1/10 of the patient's body weight. In more complex setups, a rope passes back and forth over several pulleys so that the same hanging mass produces a larger total pull on the leg.",
], [
    dict(q="With a 4.0 kg mass and the rope at 30°, what is the tension in the rope?", right="40 N",
         wrong=[("35 N", "This is the horizontal component, <i>T</i> cos 30°. The tension itself equals the hanging weight."),
                ("20 N", "This is the vertical component, <i>T</i> sin 30°."),
                ("4.0 N", "This leaves out g. Tension is a force: <i>mg</i> = 4.0 × 10.")],
         e=["The hanging mass is in equilibrium, so <i>T</i> = <i>mg</i>.", "<i>T</i> = 4.0 kg × 10 m s⁻² = 40 N, whatever the angle."], k=2),
    dict(q="Do the measured values in Table 1 match the model <i>T</i> cos θ?", right="Yes, within a few percent",
         wrong=[("No; the force should not depend on the angle", "Only the horizontal component acts along the leg, and that depends on cos θ."),
                ("No; at 60° the model predicts 35 N", "At 60°, 40 cos 60° = 20 N, which matches the measured 20 N."),
                ("No; doubling the mass should not double the force", "<i>T</i> = <i>mg</i>, so doubling <i>m</i> doubles every component.")],
         e=["Predicted: 40 cos 0° = 40 N, 40 cos 30° ≈ 35 N, 40 cos 60° = 20 N, 80 cos 30° ≈ 69 N.",
            "Measured: 39, 34, 20, 68 N. All are within about 3% of the model."], k=4),
    dict(q="For a 70 kg patient, about what hanging mass at θ = 0° gives a pull of 1/10 of body weight?",
         right="7 kg", wrong=[("70 kg", "That would pull with the patient's whole weight, ten times too much."),
                              ("0.7 kg", "1/10 of 700 N is 70 N, which needs a 7 kg mass, not 0.7 kg."),
                              ("10 kg", "That gives 100 N, which is 1/7 of the weight, the upper end of the range.")],
         e=["Body weight = 70 × 10 = 700 N; 1/10 of it = 70 N.", "At θ = 0°, pull = <i>mg</i>, so <i>m</i> = 70 N ÷ 10 = 7 kg."], k=2),
    dict(q="Raising the pulley increases θ. What happens to the two components of the pull on the leg?",
         right="Along the leg decreases; upward lift increases",
         wrong=[("Both components increase", "The tension stays <i>mg</i>. If one component grows, the other must shrink."),
                ("Along the leg increases; upward lift decreases", "This is reversed. cos θ falls and sin θ rises as θ grows."),
                ("Neither changes, since the tension is constant", "The tension is constant, but how it divides between the components depends on θ.")],
         e=["Along the leg: <i>T</i> cos θ, which falls as θ rises.", "Lift: <i>T</i> sin θ, which rises as θ rises."], k=1),
    dict(q="A new setup passes the rope over the pulleys so that two segments of the same rope pull along the leg, both at 0°. With the same 4.0 kg mass, the predicted pull along the leg is",
         right="80 N", wrong=[("40 N", "Each rope segment pulls with 40 N. Two segments pulling the same way add."),
                              ("20 N", "Splitting into two segments doesn't halve the tension. A frictionless rope has one tension throughout."),
                              ("160 N", "This counts four segments. Only two pull on the leg.")],
         e=["The tension in a single continuous rope is <i>mg</i> = 40 N everywhere.", "Two segments pulling along the leg: 2 × 40 = 80 N."], k=2),
]))

# ---------------------------------------------------------------- Unit 2 · Work & energy
P.append(passage("pms-03", "cp", "pm", 2, "How a Bike Helmet Protects the Brain", [
    "A bike helmet does not stop a head from hitting the ground. It makes the head stop more gradually. A layer of expanded polystyrene foam crushes during impact, so the head stops over a longer distance and time. The work done by the foam on the head equals the head's loss of kinetic energy:",
    "<span class=\"eq\"><i>F</i><sub>avg</sub> × <i>d</i> = ½<i>mv</i><sup>2</sup></span>",
    "Here <i>d</i> is the stopping distance and <i>F</i><sub>avg</sub> is the average force on the head. In a standard drop test, a 5.0 kg head form falls from a height of 2.0 m onto a steel anvil, reaching 6.3 m s⁻¹ just before impact. A sensor inside the head form records the peak acceleration, given as a multiple of g. Tests have linked peak accelerations above about 300 g to a high risk of severe brain injury.",
    "An engineering class compared foam samples of the same thickness (25 mm) but different densities (Table 1; hypothetical data). Very dense foam barely crushes; very soft foam crushes completely and \"bottoms out\" before the head stops, after which the head is stopped by the hard shell and the anvil.",
    table("Table 1 Drop tests from 2.0 m (5.0 kg head form)", ["Foam density (kg m⁻³)", "Crush distance (mm)", "Peak acceleration (g)"],
          [["40", "25 (bottomed out)", "390"], ["60", "21", "180"], ["90", "14", "240"], ["150", "6", "560"]]),
    bar("Figure 1 Peak acceleration by foam density", "Peak acceleration (g)", ["40", "60", "90", "150"], [("Peak", [390, 180, 240, 560], None)], 600, step=100, w=400, h=260),
    "The same principle is used in car crumple zones, airbags and the padded floors of playgrounds: for a fixed amount of kinetic energy, a longer stopping distance means a smaller average force. Helmets are designed for a single serious impact, because crushed foam does not spring back.",
    "Use g = 10 m s⁻² and ignore air resistance.",
], [
    dict(q="What is the kinetic energy of the head form just before impact?", right="100 J",
         wrong=[("50 J", "This uses ½<i>mg</i>h. The full potential energy, <i>mgh</i> = 5.0 × 10 × 2.0, becomes kinetic energy."),
                ("10 J", "This leaves out the height. <i>mgh</i> = 5.0 × 10 × 2.0."),
                ("200 J", "This doubles the answer. KE = ½<i>mv</i><sup>2</sup> = ½(5.0)(6.3)<sup>2</sup> ≈ 100 J.")],
         e=["All the potential energy converts to kinetic energy: <i>mgh</i> = 5.0 × 10 × 2.0 = 100 J.",
            "Check: ½<i>mv</i><sup>2</sup> = ½ × 5.0 × 6.3<sup>2</sup> ≈ 99 J."], k=2),
    dict(q="With the 60 kg m⁻³ foam, what was the average force on the head form during the crush?",
         right="About 4800 N", wrong=[("About 100 N", "This uses the energy (100 J) as if it were a force. Divide by the distance."),
                                      ("About 2100 N", "This multiplies 100 J by 21. Divide by the distance in meters (0.021 m)."),
                                      ("About 4.8 N", "This divides by 21 m instead of 21 mm. Convert mm to m first.")],
         e=["<i>F</i><sub>avg</sub> = KE ÷ <i>d</i> = 100 J ÷ 0.021 m ≈ 4800 N.",
            "That's an average acceleration of 4800 ÷ 5.0 ≈ 950 m s⁻², about 95 g. The peak is higher than the average."], k=2),
    dict(q="Why did the 40 kg m⁻³ foam give a higher peak acceleration than the 60 kg m⁻³ foam, even though it crushed farther?",
         right="It bottomed out before the head stopped",
         wrong=[("Softer foam always gives a higher acceleration", "The 60 foam is softer than the 90 and 150 foams but gave the lowest peak."),
                ("The 40 foam absorbed more energy than the head had", "Foam can't absorb more energy than the head had (100 J)."),
                ("The head form was heavier in that particular test", "All tests used the same 5.0 kg head form.")],
         e=["Before bottoming out, the soft foam supplies only a small force.",
            "The leftover energy is removed over almost no distance once the foam is fully crushed, giving a sharp spike."], k=4),
    dict(q="Which conclusion is best supported by Table 1 and Figure 1?",
         right="Some intermediate density works best",
         wrong=[("The densest foam protects best", "The densest foam (150) gave the highest peak, 560 g."),
                ("Peak acceleration rises steadily with density", "The lowest value is at 60, between higher values at 40 and 90."),
                ("Crush distance doesn't affect peak acceleration", "Within the foams that didn't bottom out, longer crush gave lower peaks.")],
         e=["Peaks: 390, 180, 240, 560 g. The minimum is at the middle density.",
            "The best foam crushes nearly its full thickness without bottoming out."], k=4),
    dict(q="A student wants to test whether thicker foam lowers the peak acceleration. Which experiment is best?",
         right="Test 60 kg m⁻³ foam at several thicknesses",
         wrong=[("Test all four densities at a 4.0 m drop height", "This changes height, not thickness, so it can't test the effect of thickness."),
                ("Test 25 mm foam samples of new densities", "This keeps thickness at 25 mm, so thickness isn't varied."),
                ("Repeat the 60 kg m⁻³ test with a heavier head form", "This changes the mass, not the thickness.")],
         e=["Vary only the variable being tested (thickness).", "Keep density, drop height and head-form mass the same."], k=3),
]))

st = [["A", "60", "3.0", "4.0"], ["B", "80", "3.0", "4.0"], ["C", "60", "3.0", "2.0"], ["D", "80", "3.0", "6.0"]]
P.append(passage("pms-04", "cp", "pm", 2, "Measuring Power on the Stairs", [
    "Mechanical power is the rate of doing work. When a person climbs stairs at a steady speed, the useful work done against gravity is <i>mgh</i>, where <i>h</i> is the vertical height climbed, so the mechanical power is",
    "<span class=\"eq\"><i>P</i> = <i>mgh</i> / <i>t</i></span>",
    "The body is not very efficient at turning chemical energy into mechanical work. During stair climbing, about 25% of the metabolic energy used goes into lifting the body; the rest becomes heat. Metabolic power is therefore about four times the mechanical power.",
    "In an exercise physiology lab, four students climbed the same flight of stairs, 3.0 m high, and timed themselves (Table 1). Use g = 10 m s⁻².",
    table("Table 1 Stair-climbing trials", ["Student", "Mass (kg)", "Height (m)", "Time (s)"], st),
    "The unit of power, the watt, equals one joule per second. A well-trained cyclist can sustain about 300 W of mechanical power for an hour, while a sprinter can briefly produce more than 1000 W.",
    "A clinical version of this idea, the stair-climb power test, is used to track leg strength in older adults and in patients recovering from knee surgery. Patients who cannot generate enough power have a higher risk of falls.",
    "One student pointed out that the measurement ignores the kinetic energy gained at the start of the climb and the work done swinging the arms and legs. Another noted that a stopwatch started and stopped by hand has a reaction-time error of about 0.2 s on each end.",
], [
    dict(q="What mechanical power did student A develop?", right="450 W",
         wrong=[("1800 W", "This is the approximate metabolic power, 4 × 450 W. The question asks for mechanical power."),
                ("45 W", "This leaves out g = 10 m s⁻²."),
                ("720 W", "This multiplies by time instead of dividing: power is work ÷ time.")],
         e=["Work = <i>mgh</i> = 60 × 10 × 3.0 = 1800 J.", "<i>P</i> = 1800 J ÷ 4.0 s = 450 W."], k=2),
    dict(q="Which student developed the most mechanical power?", right="Student C",
         wrong=[("Student B", "B did 2400 J in 4.0 s = 600 W. C did 1800 J in 2.0 s = 900 W."),
                ("Student D", "D did the most work (2400 J) but took 6.0 s, only 400 W."),
                ("Students B and D equally", "They did the same work but in different times, so their power differs.")],
         e=["A: 450 W. B: 2400/4.0 = 600 W. C: 1800/2.0 = 900 W. D: 2400/6.0 = 400 W.",
            "C has the largest power even though B and D are heavier."], k=4),
    dict(q="About how much metabolic energy did student B use to climb the stairs?", right="9600 J",
         wrong=[("2400 J", "This is the mechanical work. Only about 25% of the metabolic energy becomes mechanical work."),
                ("600 J", "This is 25% of the mechanical work. The metabolic energy is larger, not smaller."),
                ("3000 J", "This adds 25% to the mechanical work. Divide by 0.25 instead.")],
         e=["Mechanical work = 80 × 10 × 3.0 = 2400 J.", "Metabolic energy ≈ 2400 ÷ 0.25 = 9600 J."], k=2),
    dict(q="How does the 0.2 s reaction-time error affect the measurement most?",
         right="It matters most for the fastest climber, C",
         wrong=[("It matters most for the slowest climber, D", "0.2 s out of 6.0 s is 3%; out of 2.0 s it is 10%. Shorter times are hurt more."),
                ("It affects every student by the same percentage", "The same absolute error is a bigger fraction of a shorter time."),
                ("It doesn't matter, because it is the same for everyone", "A constant time error changes short times by a larger percentage.")],
         e=["Percentage error = 0.2 ÷ time.", "C: 10%; A and B: 5%; D: about 3%."], k=3),
    dict(q="Ignoring the kinetic energy gained and the work of swinging the limbs makes the calculated mechanical power",
         right="smaller than the true total power",
         wrong=[("larger than the true total power", "Leaving out work that was really done makes the estimate too low, not too high."),
                ("equal to the true total power", "Those extra forms of work are real, so leaving them out changes the estimate."),
                ("negative for the heavier students", "Power from lifting is always positive. Ignoring other work only lowers the estimate.")],
         e=["The body does work against gravity, plus extra work for KE and limb motion.", "Counting only <i>mgh</i> underestimates the total mechanical power."], k=3),
]))

# ---------------------------------------------------------------- Unit 5 · Electrostatics & magnetism
mb = []
mb.append('<rect x="60" y="40" width="360" height="14" fill="#ffd6e4" stroke="' + INK + '" stroke-width="1.5"/>')
mb.append('<rect x="60" y="186" width="360" height="14" fill="#d6ecff" stroke="' + INK + '" stroke-width="1.5"/>')
for i in range(8):
    x = 80 + i * 46
    mb.append(_txt(x, 51, "+", 14, fill=COL["pink"]))
    mb.append(_txt(x, 198, "−", 14, fill=COL["blue"]))
    mb.append(_arrow(x, 62, x, 178, MUTED, 1.6, 8))
mb.append(_txt(440, 51, "outside (0 mV)", 11, "start", INK))
mb.append(_txt(440, 198, "inside (−70 mV)", 11, "start", INK))
mb.append(_txt(440, 124, "membrane", 11, "start", MUTED))
mb.append(_txt(440, 140, "<i>d</i> = 7.0 nm", 11, "start", MUTED))
mb.append(_txt(240, 128, "<i>E</i>", 15, fill=COL["purple"]))
mb.append(f'<circle cx="300" cy="120" r="9" fill="#fff8e1" stroke="{INK}" stroke-width="1.5"/>' + _txt(300, 124, "Na⁺", 9))
P.append(passage("pms-05", "cp", "pm", 5, "The Membrane as a Capacitor", [
    "A nerve cell membrane separates two salt solutions. At rest, a thin layer of extra positive charge lines the outside surface and an equal layer of negative charge lines the inside, so the inside is about 70 mV negative relative to the outside. Because the lipid bilayer is a poor conductor sandwiched between two conducting solutions, it behaves like a parallel-plate capacitor (Figure 1).",
    svg_figure("Figure 1 The resting membrane modeled as a parallel-plate capacitor", "".join(mb), 560, 230),
    "For parallel plates, the electric field between them is uniform and points from the positive plate to the negative plate. Its magnitude is <i>E</i> = <i>V</i>/<i>d</i>, where <i>V</i> is the potential difference and <i>d</i> is the separation. The charge stored is <i>Q</i> = <i>CV</i>. Biological membranes have a capacitance of about 1 µF per cm<sup>2</sup> of membrane area.",
    "During an action potential, sodium channels open and Na⁺ ions flow inward until the inside is about 30 mV positive. A student estimated how many ions must cross to make this change (Table 1). Use e = 1.6 × 10⁻¹⁹ C.",
    table("Table 1 Values for a small spherical neuron", ["Quantity", "Value"],
          [["Membrane area", "1.0 × 10⁻⁵ cm<sup>2</sup>"], ["Capacitance", "1.0 × 10⁻¹¹ F"], ["Voltage change during the spike", "100 mV"],
           ["Na⁺ ions inside the cell", "about 2 × 10<sup>10</sup>"]]),
    "Because the membrane is so thin, even a small voltage produces an enormous field, larger than the field needed to make air conduct a spark.",
    "The membrane field acts on charged parts of the channel proteins themselves. Voltage-gated channels contain charged \"sensor\" segments that move within the membrane when the field changes, which opens or closes the pore.",
], [
    dict(q="What is the magnitude of the electric field across the resting membrane?", right="1.0 × 10<sup>7</sup> V m⁻¹",
         wrong=[("1.0 × 10<sup>−2</sup> V m⁻¹", "This forgets that nm is 10⁻⁹ m. 0.070 V ÷ 7.0 × 10⁻⁹ m is a very large field."),
                ("4.9 × 10<sup>−10</sup> V m⁻¹", "This multiplies <i>V</i> by <i>d</i>. The field is <i>V</i> divided by <i>d</i>."),
                ("1.0 × 10<sup>4</sup> V m⁻¹", "This uses 7.0 µm instead of 7.0 nm. Recheck the power of ten.")],
         e=["<i>E</i> = <i>V</i>/<i>d</i> = 0.070 V ÷ 7.0 × 10⁻⁹ m.", "<i>E</i> = 1.0 × 10<sup>7</sup> V m⁻¹."], k=2),
    dict(q="In which direction does the resting field push a Na⁺ ion inside the membrane?", right="Inward, toward the cytoplasm",
         wrong=[("Outward, toward the extracellular fluid", "The field points from + (outside) to − (inside). A positive ion is pushed along the field, inward."),
                ("Parallel to the membrane surface", "Between parallel plates, the field is perpendicular to the plates."),
                ("No direction; the field is zero inside the membrane", "The field is zero inside a conductor, but the membrane is an insulator with a strong field.")],
         e=["The field points from the positive outside to the negative inside.", "Force on a positive charge is along <i>E</i>: inward."], k=1),
    dict(q="About how many Na⁺ ions must enter to change the membrane voltage by 100 mV?", right="About 6 × 10<sup>6</sup>",
         wrong=[("About 2 × 10<sup>10</sup>", "This is the total Na⁺ already inside, not the number that must cross."),
                ("About 1 × 10<sup>−12</sup>", "This is the charge in coulombs. Divide by e to get the number of ions."),
                ("About 6 × 10<sup>9</sup>", "Check the exponent: 1.0 × 10⁻¹² C ÷ 1.6 × 10⁻¹⁹ C ≈ 6 × 10<sup>6</sup>.")],
         e=["<i>Q</i> = <i>C</i>Δ<i>V</i> = 1.0 × 10⁻¹¹ F × 0.100 V = 1.0 × 10⁻¹² C.", "Number = <i>Q</i>/e = 1.0 × 10⁻¹² ÷ 1.6 × 10⁻¹⁹ ≈ 6 × 10<sup>6</sup>."], k=2),
    dict(q="Based on Table 1, which conclusion follows?",
         right="One spike barely changes the Na⁺ inside",
         wrong=[("Each spike doubles the Na⁺ inside", "6 × 10<sup>6</sup> out of 2 × 10<sup>10</sup> is about 0.03%, far from doubling."),
                ("The cell must pump out all its Na⁺ after each spike", "Only a tiny fraction enters, so pumps have little to remove per spike."),
                ("The voltage change requires a large flow of ions", "Because the membrane's capacitance is small, few ions are needed.")],
         e=["Fraction = 6 × 10<sup>6</sup> ÷ 2 × 10<sup>10</sup> ≈ 3 × 10⁻⁴, about 0.03%.", "Concentrations stay almost constant, so the cell can fire many spikes."], k=4),
    dict(q="How much work does the resting field do on one Na⁺ ion that crosses the whole membrane inward?",
         right="1.1 × 10<sup>−20</sup> J", wrong=[("1.6 × 10<sup>−19</sup> J", "This is the charge of one ion in coulombs, not the work."),
                                                    ("7.0 × 10<sup>−2</sup> J", "This is the voltage. Multiply by the charge of one ion."),
                                                    ("1.1 × 10<sup>−27</sup> J", "This multiplies by the thickness. Work = <i>qV</i>, with no distance needed.")],
         e=["<i>W</i> = <i>qV</i> = 1.6 × 10⁻¹⁹ C × 0.070 V.", "<i>W</i> ≈ 1.1 × 10⁻²⁰ J (0.070 eV)."], k=2),
]))

r = [round(x * 0.1, 1) for x in range(3, 11)]
P.append(passage("pms-06", "cp", "pm", 5, "Why Salt Dissolves in Water", [
    "In a crystal of sodium chloride, each Na⁺ ion is held to neighboring Cl⁻ ions by electrostatic attraction. Coulomb's law gives the force between two point charges <i>q</i><sub>1</sub> and <i>q</i><sub>2</sub> a distance <i>r</i> apart:",
    "<span class=\"eq\"><i>F</i> = <i>kq</i><sub>1</sub><i>q</i><sub>2</sub> / (κ<i>r</i><sup>2</sup>)</span>",
    "Here <i>k</i> = 9.0 × 10<sup>9</sup> N m<sup>2</sup> C⁻². The dielectric constant κ describes how much the medium between the charges weakens the force. It is 1 in a vacuum and about 2 in a hydrocarbon such as hexane, but about 80 in water at 25 °C. Water molecules are polar: they turn so that their partial negative oxygen ends face cations and their partial positive hydrogen ends face anions. These oriented dipoles partly cancel the field between the ions.",
    "Figure 1 shows the calculated force between one Na⁺ and one Cl⁻ ion as a function of distance in hexane and in water. The ions touch in the crystal at about 0.28 nm.",
    line("Figure 1 Attractive force between Na⁺ and Cl⁻", "Distance <i>r</i> (nm)", "Force (nN)",
         [("Hexane (κ = 2)", [(x, round(9e9 * (1.6e-19) ** 2 / (2 * (x * 1e-9) ** 2) * 1e9, 2)) for x in r]),
          ("Water (κ = 80)", [(x, round(9e9 * (1.6e-19) ** 2 / (80 * (x * 1e-9) ** 2) * 1e9, 3)) for x in r])],
         1.0, 1.4, xmin=0.3, xstep=0.1, ystep=0.2, w=460, h=300),
    "Because the attraction between ions is much weaker in water, the thermal motion of molecules can pull ions out of the crystal, and each ion becomes surrounded by a hydration shell. Hexane cannot form such shells, and table salt is almost insoluble in it. The same idea explains why ion pairs, such as a salt bridge between charged amino acid side chains, are much stronger in the nonpolar interior of a protein than at its water-exposed surface.",
], [
    dict(q="By what factor is the force between two ions at the same distance weaker in water than in hexane?",
         right="40", wrong=[("80", "80 compares water with a vacuum. Hexane's κ is 2, so the ratio is 80/2."),
                            ("2", "This is hexane's dielectric constant, not the ratio."),
                            ("1600", "The force depends on 1/κ, not 1/κ<sup>2</sup>.")],
         e=["<i>F</i> ∝ 1/κ at fixed <i>r</i>.", "<i>F</i><sub>hexane</sub>/<i>F</i><sub>water</sub> = 80/2 = 40."], k=2),
    dict(q="If the distance between two ions in water doubles, the force between them becomes",
         right="one-fourth as large", wrong=[("one-half as large", "Force depends on 1/<i>r</i><sup>2</sup>, not 1/<i>r</i>."),
                                             ("twice as large", "Increasing the distance weakens the attraction."),
                                             ("one-eighth as large", "That would be a 1/<i>r</i><sup>3</sup> dependence. Coulomb's law uses 1/<i>r</i><sup>2</sup>.")],
         e=["<i>F</i> ∝ 1/<i>r</i><sup>2</sup>.", "Doubling <i>r</i>: (1/2)<sup>2</sup> = 1/4."], k=1),
    dict(q="According to Figure 1, the force between the ions in hexane at 0.60 nm is closest to",
         right="0.32 nN", wrong=[("0.64 nN", "This is about the hexane value at 0.42 nm. Read the hexane curve at 0.60 nm."),
                                 ("0.008 nN", "This is the water value at 0.60 nm."),
                                 ("1.28 nN", "This is the hexane value near 0.30 nm.")],
         e=["<i>F</i> = (9.0 × 10<sup>9</sup>)(1.6 × 10⁻¹⁹)<sup>2</sup> ÷ (2 × (0.60 × 10⁻⁹)<sup>2</sup>) ≈ 3.2 × 10⁻¹⁰ N.", "That is 0.32 nN, matching the graph."], k=4),
    dict(q="Why do water molecules lower the force between ions?",
         right="Their dipoles orient to oppose the ions' field",
         wrong=[("They carry a net charge that cancels the ions' charge", "Water molecules are neutral overall. Only their charge distribution is uneven."),
                ("They push the ions farther apart than in the crystal", "κ lowers the force at any fixed distance, separate from the distance effect."),
                ("They form covalent bonds with Na⁺ and Cl⁻", "Hydration involves ion–dipole attractions, not covalent bonds.")],
         e=["Water's O end faces Na⁺ and its H ends face Cl⁻.", "These aligned dipoles create a field opposing the ions' field, so the net force is smaller."], k=1),
    dict(q="A researcher finds that a salt bridge between a lysine and a glutamate side chain contributes much more to a protein's stability when it is buried in the core. Which explanation is best supported by the passage?",
         right="The protein's core has a low dielectric constant",
         wrong=[("The ions are farther apart in the core", "Farther apart would weaken the attraction, not strengthen it."),
                ("Water in the core has a higher dielectric constant", "The core is mostly nonpolar side chains, with little water."),
                ("Buried charges have larger charges than surface charges", "Lysine and glutamate carry the same charges (+1 and −1) wherever they are.")],
         e=["The interior is nonpolar, like hexane (κ ≈ 2–4).", "With little dielectric screening, the attraction between the charges is much stronger."], k=4),
]))
