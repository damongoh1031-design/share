/**
 * Seek Clinic full-directory crawler.
 *
 * WHY THIS EXISTS
 *   seekclinic.my serves an interstitial ("One moment, please...", HTTP 200, reloads
 *   every 5s) to this machine's network for *every* path, headless and headful alike.
 *   The challenge never resolves, so local crawling cannot start. The site is not
 *   broken — the block is on our egress. Run this script from a network the site
 *   serves normally (home broadband / mobile hotspot), and it will walk the whole
 *   directory.
 *
 * WHAT IT DOES
 *   Category listing pages carry name + address + tel: for 9 clinics each, so the
 *   whole directory is reachable without touching detail pages.
 *
 * USAGE
 *   NODE_PATH="C:/Users/Admin/.workbuddy-ai/binaries/node/workspace/node_modules" \
 *   node crawl_seekclinic.js [--max-pages N] [--delay 2000]
 *
 * OUTPUT
 *   seekclinic_full.jsonl   one record per listing, appended, resumable
 *   seekclinic_full_state.json
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

const args = process.argv.slice(2);
const argVal = (flag, dflt) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? Number(args[i + 1]) : dflt;
};
const DELAY = argVal('--delay', 2000);
const MAX_PAGES = argVal('--max-pages', 200);

// Categories visible on the site nav / homepage. Add more as they are discovered;
// the crawler stops a category on the first 404, so extra entries are harmless.
const CATEGORIES = [
  'aesthetic-clinic-1',
  'skin-clinic',
  'medical-clinic',
  'dental-clinic',
  'women-clinic',
  'eye-clinic',
  'ent-clinic',
  'orthopedic-clinic',
  'health-screening',
  'vaccination',
];

const CHALLENGE = /one moment|just a moment|attention required|performing security verification/i;

const loadState = () => fs.existsSync(STATE)
  ? JSON.parse(fs.readFileSync(STATE, 'utf8'))
  : { done: [], pages: {} };
const saveState = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 1));

function parseListing(text, pageUrl) {
  // Each listing block: "#### Name" then "- address" then "- phone" then links.
  const out = [];
  const blocks = text.split(/\n(?=#### )/);
  for (const block of blocks) {
    const nameM = block.match(/^####\s+(.+)$/m);
    if (!nameM) continue;
    const name = nameM[1].trim();
    const phones = [...block.matchAll(/\+\d{8,13}/g)].map(m => m[0]);
    const tel = [...block.matchAll(/tel:(\+?\d{8,13})/g)].map(m => m[1]);
    const detail = block.match(/\[View Details\]\((https:\/\/seekclinic\.my\/[^)]+)\)/);
    const addrM = block.match(/^- (.+)$/m);
    if (!detail) continue;
    out.push({
      name,
      phone_raw: (tel[0] || phones[0] || ''),
      address: addrM ? addrM[1].trim() : '',
      url: detail[1],
      listing_page: pageUrl,
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
  const ctx = await browser.newContext({ locale: 'en-US', viewport: { width: 1366, height: 900 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(60000);

  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(6000);
  let title = await page.title();
  if (CHALLENGE.test(title)) {
    console.error(`BLOCKED: interstitial still showing after warm-up ("${title}").`);
    console.error('This network is blocked by the site. Run from another network.');
    await browser.close();
    process.exit(2);
  }
  console.log('warm ok:', title);

  const state = loadState();
  let pagesDone = 0;

  for (const cat of CATEGORIES) {
    if (state.pages[cat] === 'closed') continue;
    for (let n = 1; n <= MAX_PAGES; n++) {
      const key = `${cat}/${n}`;
      if (state.done.includes(key)) continue;
      const url = n === 1 ? `${BASE}/category/${cat}/` : `${BASE}/category/${cat}/page/${n}/`;
      let text = '';
      try {
        const resp = await page.goto(url, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(2500);
        if (resp && resp.status() === 404) { state.pages[cat] = 'closed'; console.log(`  ${cat}: 404 at page ${n} -> category done`); break; }
        text = await page.evaluate(() => document.body.innerText);
        if (CHALLENGE.test(text.slice(0, 300))) throw new Error('challenge');
      } catch (e) {
        console.log(`  ${cat} p${n}: ${e.message} -> stop this category`);
        state.pages[cat] = 'blocked';
        break;
      }
      const rows = parseListing(text, url);
      if (rows.length === 0) { state.pages[cat] = 'closed'; console.log(`  ${cat}: no listings at page ${n} -> done`); break; }
      fs.appendFileSync(OUT, rows.map(r => JSON.stringify(r)).join('\n') + '\n');
      state.done.push(key);
      saveState(state);
      pagesDone++;
      console.log(`${cat} p${n}: +${rows.length} (total pages this run ${pagesDone})`);
      await page.waitForTimeout(DELAY);
    }
  }

  const lines = fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').trim().split('\n').filter(Boolean).length : 0;
  console.log(`\nrows in seekclinic_full.jsonl: ${lines}`);
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
