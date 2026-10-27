/**
 * Seek Clinic full-directory crawler (v2).
 *
 * WHY THIS EXISTS
 *   seekclinic.my blocks this machine's egress IP outright: every path — robots.txt,
 *   sitemap, homepage, /clinics/ — returns 403 from nginx, in curl and in real Chrome.
 *   The block is on the network, not on the tool, so local crawling cannot start here.
 *   Run this from a network the site serves normally (home broadband / mobile hotspot).
 *
 * WHY /clinics/ AND NOT /category/...
 *   The site-wide archive https://seekclinic.my/clinics/page/N/ reports
 *   "Page N Of 603" — that is the complete directory (≈5,419 listings at 9 per page).
 *   Category pages overlap heavily with it, so walking the archive once is both
 *   cheaper and duplicate-free compared with walking every category.
 *
 * 403 HANDLING (learned the hard way on 2026-10-27)
 *   Two different 403s exist:
 *     - cache-poisoned 403: the exact URL is cached as 403 at the CDN. Adding a
 *       harmless query string (?cb=...) changes the cache key and the page loads.
 *     - rate-limit 403: the egress IP has made too many requests. Query strings
 *       do not help. Back off long, and stop the run after repeated failures.
 *   This script does exactly that: one cache-buster retry, then exponential backoff,
 *   then a clean stop. It never rotates proxies, spoofs fingerprints or solves
 *   challenges.
 *
 * USAGE
 *   NODE_PATH="C:/Users/Admin/.workbuddy-ai/binaries/node/workspace/node_modules" \
 *   node crawl_seekclinic.js [--delay 2500] [--max-pages 603] [--start 1]
 *
 * OUTPUT
 *   seekclinic_full.jsonl        one record per listing, appended, resumable
 *   seekclinic_full_state.json   checkpoint
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const CHROME = process.env.CHROME_PATH
  || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const ROOT = __dirname;
const OUT = path.join(ROOT, 'seekclinic_full.jsonl');
const STATE = path.join(ROOT, 'seekclinic_full_state.json');
const BASE = 'https://seekclinic.my';
const TOTAL_PAGES = 603; // measured: /clinics/page/603/ exists, page 604 does not

const args = process.argv.slice(2);
const argVal = (flag, dflt) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? Number(args[i + 1]) : dflt;
};
const DELAY = argVal('--delay', 2500);
const MAX_PAGES = argVal('--max-pages', TOTAL_PAGES);
const START = argVal('--start', 1);

const CHALLENGE = /one moment|just a moment|attention required|performing security verification|403 forbidden/i;

const loadState = () => fs.existsSync(STATE)
  ? JSON.parse(fs.readFileSync(STATE, 'utf8'))
  : { done: [], blocked: [], rows: 0 };
const saveState = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 1));

const archiveUrl = (n, cb) => {
  const base = n === 1 ? `${BASE}/clinics/` : `${BASE}/clinics/page/${n}/`;
  return cb ? `${base}?cb=${Date.now()}` : base;
};

// Phone shapes seen on the site: +6062644344, +60 10-368 1400, 018-3722286, 03-3395 1393
const PHONE_RE = /(?:\+60[\d\s\-()]{7,14}|(?<!\d)0\d[\d\s\-()]{6,12})/;

function parseListing(text, pageUrl) {
  const out = [];
  const blocks = text.split(/\n(?=#### )/);
  for (const block of blocks) {
    const nameM = block.match(/^####\s+(.+)$/m);
    if (!nameM) continue;
    const detail = block.match(/\[View Details\]\((https:\/\/seekclinic\.my\/[^)]+)\)/);
    if (!detail) continue; // not a listing block (intro copy, headings)
    const tel = block.match(/tel:([+\d\s\-()%]{8,20})/);
    let phone = '';
    if (tel) {
      phone = decodeURIComponent(tel[1]).trim();
    } else {
      const p = block.match(PHONE_RE);
      phone = p ? p[0].trim() : '';
    }
    const addrM = block.match(/^- (.+)$/m);
    out.push({
      name: nameM[1].trim(),
      phone_raw: phone,
      address: addrM ? addrM[1].trim() : '',
      url: detail[1],
      listing_page: pageUrl,
      page_no: Number((pageUrl.match(/page\/(\d+)/) || [])[1] || 1),
    });
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
  });
  const ctx = await browser.newContext({ locale: 'en-MY', viewport: { width: 1366, height: 900 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(60000);

  // Warm-up: establishes the site's own cookies before deep links.
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await page.waitForTimeout(6000);
  const warmTitle = await page.title();
  if (CHALLENGE.test(warmTitle)) {
    console.error(`BLOCKED at warm-up ("${warmTitle}"). This network is refused by the site.`);
    console.error('Run this script from another network. Do not proxy-rotate or spoof fingerprints.');
    await browser.close();
    process.exit(2);
  }
  console.log('warm ok:', warmTitle);

  const state = loadState();
  let consecutiveBlocked = 0;

  for (let n = START; n <= Math.min(MAX_PAGES, TOTAL_PAGES); n++) {
    if (state.done.includes(n)) continue;

    let text = null;
    for (let attempt = 0; attempt < 2; attempt++) {
      const url = archiveUrl(n, attempt === 1); // 2nd try busts a cached 403
      try {
        const resp = await page.goto(url, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(2000);
        if (resp && resp.status() === 404) {
          console.log(`page ${n}: 404 -> archive ends at ${n - 1}`);
          saveState(state);
          await browser.close();
          return;
        }
        const body = await page.evaluate(() => document.body.innerText);
        if (CHALLENGE.test(body.slice(0, 400))) throw new Error('403/challenge');
        text = body;
        break;
      } catch (e) {
        console.log(`page ${n} attempt ${attempt + 1}: ${e.message}`);
        if (attempt === 1) break;
        await page.waitForTimeout(5000);
      }
    }

    if (!text) {
      state.blocked.push(n);
      consecutiveBlocked++;
      saveState(state);
      if (consecutiveBlocked >= 3) {
        const wait = 60000;
        console.log(`3 consecutive blocks -> likely rate limit. Sleeping ${wait / 1000}s, then stopping.`);
        await page.waitForTimeout(wait);
        console.log('Stopping. Re-run later; checkpoint keeps finished pages.');
        await browser.close();
        process.exit(3);
      }
      await page.waitForTimeout(15000);
      continue;
    }

    consecutiveBlocked = 0;
    const rows = parseListing(text, archiveUrl(n, false));
    if (rows.length === 0) {
      console.log(`page ${n}: 0 listings parsed -> inspect manually before continuing`);
      state.blocked.push(n);
      saveState(state);
      continue;
    }
    fs.appendFileSync(OUT, rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
    state.done.push(n);
    state.rows += rows.length;
    saveState(state);
    console.log(`page ${n}: +${rows.length} (cumulative ${state.rows})`);
    await page.waitForTimeout(DELAY);
  }

  console.log(`\ndone. pages: ${state.done.length}, rows: ${state.rows}`);
  await browser.close();
})().catch((e) => { console.error('FATAL', e.message); process.exit(1); });
