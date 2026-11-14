/* MCAT Study Hub + Pre-Med Pulse offline support.
   Pages: network first (so updates show up right away), falling back to the saved copy when offline or when the
   network is very slow. Question-bank files carry a version stamp in their URL, so a saved copy is always the
   right one: saved copy first. Images: saved copy first. CACHE, DATA and ART are written by
   python3 tools/build_hub_data.py, so the worker updates itself whenever the bank changes. */
const CACHE = "mcat-3e646946f4";
const ART_CACHE = "mcat-art-1"; // kept across updates so pictures download once
const CORE = ["./", "index.html", "practice.html"];
const DATA = ["data/bank/q-gc.js?v=3e646946f4", "data/bank/q-oc.js?v=3e646946f4", "data/bank/q-pm.js?v=3e646946f4", "data/bank/q-bc.js?v=3e646946f4", "data/bank/q-bio.js?v=3e646946f4", "data/bank/q-beh.js?v=3e646946f4", "data/bank/q-cars.js?v=3e646946f4", "data/bank/p-cp.js?v=3e646946f4", "data/bank/p-cars.js?v=3e646946f4", "data/bank/p-bb.js?v=3e646946f4", "data/bank/p-ps.js?v=3e646946f4", "data/daily.json", "data/search.json", "data/learn.json"];
const ART = ["assets/b_bb10.webp", "assets/b_cars10.webp", "assets/b_century.webp", "assets/b_clock.webp", "assets/b_cp10.webp", "assets/b_first.webp", "assets/b_full.webp", "assets/b_pass.webp", "assets/b_ps10.webp", "assets/b_round.webp", "assets/b_s10.webp", "assets/b_s5.webp", "assets/dg/learn_dgA_brain.webp", "assets/dg/learn_dgA_gi.webp", "assets/dg/learn_dgA_heart.webp", "assets/dg/learn_dgA_neuron.webp", "assets/dg/learn_dgA_resp.webp", "assets/dg/learn_dgB_endocrine.webp", "assets/dg/learn_dgB_nephron.webp", "assets/dg/learn_dgB_sarcomere.webp", "assets/dg/learn_dgB_skin.webp", "assets/dg/learn_dgC_cell.webp", "assets/dg/learn_dgC_express.webp", "assets/dg/learn_dgC_microbes.webp", "assets/dg/learn_dgC_mitosis.webp", "assets/dg/ox_eye.jpg", "assets/dg/ox_juxtaglomerular.jpg", "assets/dg/ox_muscle_fibers.jpg", "assets/dg/ox_nephron_blood_flow.jpg", "assets/dg/ox_thick_thin_filaments.jpg", "assets/hero.webp", "assets/icon_hub_180.png", "assets/icon_hub_32.png", "assets/icon_pulse_180.png", "assets/icon_pulse_32.png", "assets/logo_hub.webp", "assets/logo_pulse.webp", "assets/m_daily5.webp", "assets/m_full_length.webp", "assets/m_must_know.webp", "assets/m_passage_sets.webp", "assets/m_progress.webp", "assets/m_quick_drill.webp", "assets/m_real_exam.webp", "assets/m_search.webp", "assets/m_skill_gym.webp", "assets/m_study_plan.webp", "assets/m_timed.webp", "assets/og.png", "assets/pulse_correct.webp", "assets/pulse_idle.webp", "assets/pulse_oops.webp", "assets/pulse_reading.webp", "assets/pulse_thinking.webp", "assets/pulse_victory.webp", "assets/sec_bb.webp", "assets/sec_cars.webp", "assets/sec_cp.webp", "assets/sec_ps.webp"];
const SLOW_MS = 4000;

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    // pages: skip the browser's HTTP cache so a new version never saves an old page
    await c.addAll(CORE.map(u => new Request(u, {cache: "reload"})));
    // bank files are versioned, so the copy the page just downloaded (HTTP cache) is the right one: no second download
    for (const u of DATA) { try { const r = await fetch(u); if (r.ok) await c.put(u, r); } catch (err) { /* saved later when used */ } }
    await self.skipWaiting();
  })());
});
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const ks = await caches.keys();
    await Promise.all(ks.filter(k => k.startsWith("mcat-") && k !== CACHE && k !== ART_CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
    const art = await caches.open(ART_CACHE), have = new Set((await art.keys()).map(r => r.url));
    for (const u of ART) {
      const url = new URL(u, self.registration.scope).href;
      if (have.has(url)) continue;
      try { const r = await fetch(url); if (r.ok) await art.put(url, r); } catch (err) { /* saved the first time it is shown */ }
    }
  })());
});

const offlineReply = () => new Response("Offline, and this file is not saved on this device yet.", {status: 503, statusText: "Offline", headers: {"Content-Type": "text/plain; charset=utf-8"}});
const keep = (name, key, res) => { if (res && res.ok && (res.type === "basic" || res.type === "default")) { const cp = res.clone(); caches.open(name).then(c => c.put(key, cp)).catch(() => {}); } return res; };

async function savedFirst(req, name) {
  const hit = await caches.match(req, name === ART_CACHE ? {ignoreSearch: true} : undefined);
  if (hit) return hit;
  try { return keep(name, req, await fetch(req)); } catch (err) { return offlineReply(); }
}
async function networkFirst(req, fallbackPage) {
  const cache = await caches.open(CACHE);
  const saved = async () => (await cache.match(req, {ignoreSearch: true})) || (fallbackPage ? await cache.match(fallbackPage) : undefined);
  const net = fetch(req.url, {cache: "no-cache", credentials: "same-origin"}).then(res => keep(CACHE, new URL(req.url).pathname.endsWith("/") ? "./" : req, res));
  const slow = new Promise(r => setTimeout(r, SLOW_MS)).then(saved);
  try { const first = await Promise.race([net, slow]); return first || await net; }
  catch (err) { return (await saved()) || offlineReply(); }
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;               // answer stats and reports always go to the network
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;     // fonts and outside links go straight to the network
  const inScope = url.href.startsWith(self.registration.scope);
  if (inScope && url.pathname.includes("/data/bank/")) { e.respondWith(savedFirst(req, CACHE)); return; }
  if (inScope && url.pathname.includes("/assets/")) { e.respondWith(savedFirst(req, ART_CACHE)); return; }
  if (req.mode === "navigate") { e.respondWith(networkFirst(req, url.pathname.endsWith("practice.html") ? "practice.html" : "index.html")); return; }
  // daily.json, search.json and the shared ItsDrDan brand scripts (same site): fresh when online, saved copy when not
  e.respondWith(networkFirst(req, null));
});
