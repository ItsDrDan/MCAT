# MCAT Study Hub + Pre-Med Pulse, by ItsDrDan

Free MCAT prep covering all four sections: Chem/Phys, CARS, Bio/Biochem and Psych/Soc.

- **index.html: MCAT Study Hub.** Section pages with every unit, a Daily 5, a week-by-week study plan builder, topic search and progress tracking.
- **practice.html: Pre-Med Pulse.** Quick Drill, Passage Sets, Timed Mini-Section and a Mini Full-Length in real test order. Deep links: `practice.html?subj=gc&unit=5`, `?section=cars&mode=passage`, `?mode=eqs`. Modes: `drill`, `review`, `passage`, `timed`, `full`, `real`, `gym`, `eqs`.
- **data/:** the question bank (`bank/`), the 3-minute lessons (`learn.json`), the Daily 5 question pool and the search index used by the hub.
- **sw.js:** offline support. After one full visit the hub, the practice app, every question and every lesson work without internet. Pages are network-first (updates show up right away); bank files are versioned, so saved copies are used first.

Every question is original and written from the public AAMC content outline, with background from free OpenStax textbooks.

## Maintaining the bank

The questions live in `data/bank/`, split so the practice app can load one section at a time: `q-<subject>.js` (single questions for gc, oc, pm, bc, bio, beh, cars) and `p-<section>.js` (passages for cp, cars, bb, ps). Each question or passage is on its own line, so a git diff shows exactly which ones changed. Always read and write them through `tools/bank.py` (`load()`, `save()`). After any edit:

1. `python3 tools/build_hub_data.py` rebuilds the hub's counts, the topic search index (`data/search.json`) and the Daily 5 pool (`data/daily.json`) from the bank. It also writes a hash of the bank into `practice.html` (`BANKV`) and into the offline worker `sw.js` (its cache name and file list), so a browser never pairs a new page with an old saved bank.
2. `python3 tools/validate_bank.py` must show `ERRORS: 0`. It catches:
   - broken items
   - duplicate IDs or passage titles
   - option letters or "Question N" that break when choices are shuffled
   - bad paragraph references
   - stale hub counts
   - a Daily 5 pool that no longer matches the bank
   - a question ID that used to exist and is gone (`tools/id_manifest.json`). After adding questions, or a deliberate removal, run `python3 tools/validate_bank.py --accept-ids`.

   Add `--all` to list every warning.
3. `python3 tools/check_answer_lengths.py` guards against "the longest answer is right."

GitHub runs steps 2 and 3 on every push and pull request (`.github/workflows/validate.yml`).

Rules that keep student progress safe:
- **Don't renumber or reorder.** Question IDs (`id`, and `<passage id>-q<n>` for passage questions) are what saved progress, review queues and stats point to. Never renumber them or reorder a passage's questions; add new passage questions at the end.
- **Shuffle-proof answers.** Options are shuffled in the app. Put the key first with `"a": 0`, and never refer to option letters.

## How the practice app loads

`practice.html` asks for only the files the current mode needs (for example `q-beh.js` for a Psych/Soc drill), shows a question as soon as they arrive, then downloads the rest in the background. Modes that need everything (Review My Misses, timed sets, full-length exams) wait with a short message. If a file can't be downloaded, the page says so and offers a retry.

## 3-minute lessons and figure descriptions

- `data/learn.json` has one lesson per unit (`s`, `u`, `why`, `big`, `ex`, `trap`, `memory`, `pre`), shown on the hub at `#/learn/<subject>/<unit>`. Only `<b>` is allowed in lesson text; the validator checks every unit has one and every prerequisite is a real unit.
- Every figure's `aria-label` holds its title plus a text description written for screen-reader users: the same information a sighted student reads off the figure, with no conclusions the questions ask for. Keep this true when you edit a figure.

## Guided CARS review

Each CARS passage can carry a `map`: `main` (the central argument), `paras` (what each body paragraph does, one entry per paragraph), `turn` (where the reasoning shifts) and `tip` (a reading habit). Pre-Med Pulse shows it only after the passage is finished or in the review after a timed set, never while the clock is running. The validator checks that `paras` matches the paragraph count.

## What is saved in the student's browser

Progress never leaves the device (the anonymous stats described below are separate). Keys in `localStorage`:

| Key | Holds |
|---|---|
| `premedpulse_v2` | Totals, per-subject and per-unit counts, badges, skills, the review queue and the fields below |
| `premedpulse_exam` | A Full-Length Exam in progress |
| `mcathub_daily_v1` | Daily 5 history and streak |
| `mcathub_plan_v1` | The study plan and its checkmarks |

Fields added to `premedpulse_v2` in November 2026. All are optional, so older saved progress loads unchanged:
- `units["gc:10"].r`: the last 12 results in that unit as a string of 1s and 0s. Drives "strong recent performance" and "more practice recommended".
- `srs`: now also holds passage-question IDs (`<passage id>-q<n>`). IDs that no longer exist are dropped on load.
- `log`: the last 300 answers as `[id, right, pick]`, for "My recent answers".
- `why`: the student's own reason for a miss, by question ID.
- `tn`: timed sets finished.

"Back up or move my progress" in Pre-Med Pulse saves these four keys to a file and restores them. The file has `app: "itsdrdan-mcat"` and `v: 1`.

Rules the progress screens follow: a number is always shown with how many answers it rests on, fewer than 5 answers in a unit is "limited evidence", and no 118–132 or 472–528 score is shown anywhere. The Full-Length Exam reports accuracy, pacing and the weakest units instead, and points students to the free official AAMC exam and the Fee Assistance Program for a real scaled score. Students who have taken an official exam can share both results anonymously; an estimate should only be added if that data shows this exam predicts real scores reliably.

## Finding problem questions from real answers

Each answer sends the question ID, the choice picked, the correct choice and a wording fingerprint. These go to the anonymous stats Apps Script ("ItsDrDan Game Stats Receiver"), which saves them to the "items" tab of the stats sheet. No names or student IDs are sent.

`python3 tools/item_analysis.py` writes `item-analysis.md`, which flags:
- **Possible mis-keys:** a wrong choice is picked more often than the key.
- **Too hard:** under 30% correct.
- **Too easy:** 97% or more correct.
- **Unused distractors:** wrong choices almost nobody picks.

It only uses answers to each question's current wording. `tools/item_stats_apps_script.gs` is a reference copy of that Apps Script add-on.
MCAT® is a registered trademark of the AAMC. This project is not affiliated with or endorsed by the AAMC.

© ItsDrDan. All rights reserved.
