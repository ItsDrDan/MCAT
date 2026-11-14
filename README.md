# MCAT Study Hub + Pre-Med Pulse, by ItsDrDan

Free MCAT prep covering all four sections: Chem/Phys, CARS, Bio/Biochem and Psych/Soc.

- **index.html: MCAT Study Hub.** Section pages with every unit, a Daily 5, a week-by-week study plan builder, topic search and progress tracking.
- **practice.html: Pre-Med Pulse.** Quick Drill, Passage Sets, Timed Mini-Section and a Mini Full-Length in real test order. Deep links: `practice.html?subj=gc&unit=5`, `?section=cars&mode=passage`, `?mode=eqs`. Modes: `drill`, `review`, `passage`, `timed`, `full`, `real`, `gym`, `eqs`.
- **data/:** the question bank (`bank-q.js`, `bank-p.js`), the Daily 5 question pool and the search index used by the hub.

Every question is original and written from the public AAMC content outline, with background from free OpenStax textbooks.

## Maintaining the bank

The questions live in two data files that `practice.html` loads: `data/bank-q.js` (`const Q`, single questions) and `data/bank-p.js` (`const P`, passages). Each question or passage is on its own line, so a git diff shows exactly which ones changed. Other tools should read and write them through `tools/bank.py` (`load()`, `save()`). After any edit:

1. `python3 tools/build_hub_data.py` rebuilds the hub's counts, the topic search index (`data/search.json`) and the Daily 5 pool (`data/daily.json`) from the bank. It also stamps the data-file links in `practice.html` with a hash of the bank, so a browser never pairs a new page with an old cached bank.
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

Rules the progress screens follow: a number is always shown with how many answers it rests on, fewer than 5 answers in a unit is "limited evidence", and no scaled score is estimated from a short set.

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
