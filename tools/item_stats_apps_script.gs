/**
 * ItsDrDan study games: per-question stats (add-on for the existing stats Apps Script).
 *
 * What this adds
 *   - Each answer that carries an `item` (question ID) is also written to a separate "Items" sheet,
 *     with: time, game, item, ver (wording fingerprint), key (correct choice 0-3), pick (chosen 0-3),
 *     correct (true/false), mode, session. No names, emails or student IDs.
 *   - A summary view: <your /exec URL>?items=1&game=mcat&days=365 returns one row per question
 *     version with how many students answered, how many got it right, and how often each choice was picked.
 *   - Your existing sheet, columns and stats page are not changed.
 *
 * How to install (about 5 minutes)
 *   1. Open the Apps Script project behind the stats URL in games/track.js
 *      (script.google.com → the project → Editor).
 *   2. Paste this whole file into a new script file (File → New → Script), e.g. "items.gs".
 *   3. In your existing doPost(e), right after the line that parses the posted events, add:
 *          ddLogItems_(events);      // use whatever your variable for the parsed array is called
 *   4. At the very top of your existing doGet(e), add:
 *          if (e && e.parameter && e.parameter.items) return ddItemsResponse_(e);
 *   5. If the project is NOT bound to the stats spreadsheet (i.e., it uses SpreadsheetApp.openById),
 *      set DD_SHEET_ID below to that spreadsheet's ID. If it is bound, leave it empty.
 *   6. Deploy → Manage deployments → pencil icon on the current web-app deployment → Version: New version
 *      → Deploy. Editing the existing deployment keeps the same /exec URL, so no game needs changing.
 *   7. Check: open <your /exec URL>?items=1&game=mcat — you should see JSON (an empty list until
 *      students answer with the new site).
 */

var DD_SHEET_ID = '';          // leave empty if this script is bound to the stats spreadsheet
var DD_ITEMS_SHEET = 'Items';

function ddItemsBook_() {
  return DD_SHEET_ID ? SpreadsheetApp.openById(DD_SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
}

/** Append one row per event that names a question. Safe to call with any parsed batch. */
function ddLogItems_(events) {
  if (!events || !events.length) return;
  var rows = [];
  for (var i = 0; i < events.length; i++) {
    var e = events[i];
    if (!e || !e.item) continue;
    rows.push([
      new Date(),
      String(e.game || '').slice(0, 40),
      String(e.item).slice(0, 40),
      String(e.ver || '').slice(0, 12),
      (e.key === 0 || e.key > 0) ? Number(e.key) : '',
      (e.pick === 0 || e.pick > 0) ? Number(e.pick) : '',
      e.correct === true || e.correct === 'true',
      String(e.mode || '').slice(0, 60),
      String(e.session || '').slice(0, 16)
    ]);
  }
  if (!rows.length) return;
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var book = ddItemsBook_();
    var sh = book.getSheetByName(DD_ITEMS_SHEET);
    if (!sh) {
      sh = book.insertSheet(DD_ITEMS_SHEET);
      sh.appendRow(['time', 'game', 'item', 'ver', 'key', 'pick', 'correct', 'mode', 'session']);
      sh.setFrozenRows(1);
    }
    sh.getRange(sh.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
  } finally {
    lock.releaseLock();
  }
}

/** Aggregate the Items sheet: one entry per (item, ver). */
function ddItemSummary_(game, days) {
  var sh = ddItemsBook_().getSheetByName(DD_ITEMS_SHEET);
  if (!sh || sh.getLastRow() < 2) return [];
  var data = sh.getRange(2, 1, sh.getLastRow() - 1, 9).getValues();
  var since = new Date(Date.now() - days * 864e5);
  var agg = {};
  for (var i = 0; i < data.length; i++) {
    var r = data[i];
    if (r[0] < since || (game && r[1] !== game)) continue;
    var k = r[2] + '|' + r[3];
    var a = agg[k] || (agg[k] = {item: r[2], ver: r[3], key: r[4], n: 0, correct: 0, picks: [0, 0, 0, 0], sessions: {}});
    a.n++;
    if (r[6] === true || r[6] === 'TRUE') a.correct++;
    if (r[5] !== '' && r[5] >= 0 && r[5] <= 3) a.picks[r[5]]++;
    a.sessions[r[8]] = 1;
  }
  var out = [];
  for (var key in agg) {
    var a = agg[key];
    out.push({item: a.item, ver: a.ver, key: a.key, n: a.n, correct: a.correct, picks: a.picks, sessions: Object.keys(a.sessions).length});
  }
  return out;
}

function ddItemsResponse_(e) {
  var game = e.parameter.game || 'mcat';
  var days = Math.max(1, Math.min(3650, Number(e.parameter.days) || 365));
  var body = {generated: new Date().toISOString(), game: game, days: days, items: ddItemSummary_(game, days)};
  return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);
}
