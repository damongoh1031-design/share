const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const ROOT = __dirname;
const OUT = path.join(ROOT, 'aestheticclinic_profiles.jsonl');
const STATE = path.join(ROOT, 'aestheticclinic_state.json');
const DELAY = 1200;

const loadDone = () => fs.existsSync(STATE) ? new Set(JSON.parse(fs.readFileSync(STATE, 'utf8')).done || []) : new Set();
const saveDone = (d) => fs.writeFileSync(STATE, JSON.stringify({ done: [...d], updated: new Date().toISOString() }, null, 1));
const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();

function normPhones(value) {
  const out = [];
  for (const token of value.split(/[\/,;]|\bor\b/i)) {
    const digits = token.replace(/[^\d+]/g, '');
    if (!digits) continue;
    let d = digits.replace(/^\+/, '');
    if (d.startsWith('60')) out.push('+' + d);
    else if (d.startsWith('0')) out.push('+6' + d);
    else if (d.startsWith('6') && d.length >= 10) out.push('+' + d);
  }
  return [...new Set(out.filter(p => /^\+60\d{8,10}$/.test(p)))];
}

function parsePage(text, url) {
  const body = text.replace(/\u00a0/g, ' ');
  const lines = body.split('\n');
  const kv = {};
  for (const line of lines) {
    const idx = line.indexOf('\t');
    if (idx > 0) {
      const label = clean(line.slice(0, idx));
      const value = clean(line.slice(idx + 1));
      if (label && value && !kv[label]) kv[label] = value;
    }
  }

  // completeness: value on the line right after the label
  let completeness = '';
  for (let i = 0; i < lines.length; i++) {
    if (/^Profile completeness$/i.test(clean(lines[i]))) {
      completeness = clean(lines[i + 1] || '');
      break;
    }
  }

  const name = (() => {
    const m = body.match(/\n([^\n]{3,120})\n\nCLINIC ·/);
    if (m) return clean(m[1]);
    const h = body.match(/Home\s*\n\s*\/\s*\n([^\n]+)/);
    return h ? clean(h[1]) : '';
  })();

  const phoneField = kv['Phone or contact route'] || '';
  const phones = normPhones(phoneField);

  return {
    url,
    name,
    registered_premises: kv['Registered premises'] || '',
    address: kv['Address'] || '',
    area: kv['Area'] || '',
    phone_field: phoneField,
    phones,
    hours: kv['Opening hours'] || '',
    matched_doctor: kv['Matched doctor'] || '',
    completeness,
    verification: kv['Verification'] || '',
    last_checked: kv['Last checked'] || '',
    has_quickfacts: Object.keys(kv).length > 0,
    text_len: body.length,
  };
}

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
  });
  const ctx = await browser.newContext({
    locale: 'en-US', userAgent: UA, viewport: { width: 1366, height: 900 },
    extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' },
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(60000);

  await page.goto('https://www.aestheticclinic.my/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(8000);
  console.log('warm:', await page.title());

  const xml = await page.evaluate(async (u) => (await fetch(u)).text(),
    'https://www.aestheticclinic.my/wp-sitemap-posts-ac_clinic-1.xml');
  const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].trim());
  fs.writeFileSync(path.join(ROOT, 'aestheticclinic_urls.txt'), urls.join('\n') + '\n');
  console.log('urls:', urls.length);

  const done = loadDone();
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    if (done.has(url)) continue;
    let parsed = null, err = '';
    for (let attempt = 1; attempt <= 3 && !parsed; attempt++) {
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000);
        let text = await page.evaluate(() => document.body.innerText);
        if (!/Quick facts/i.test(text)) {
          await page.waitForTimeout(5000);
          text = await page.evaluate(() => document.body.innerText);
        }
        if (/performing security verification|one moment, please/i.test(text.slice(0, 300))) throw new Error('challenge');
        parsed = parsePage(text, url);
      } catch (e) {
        err = e.message;
        if (attempt < 3) await page.waitForTimeout(3000);
      }
    }
    if (!parsed) parsed = { url, name: '', phones: [], error: err };
    fs.appendFileSync(OUT, JSON.stringify(parsed) + '\n');
    done.add(url);
    saveDone(done);
    const tag = parsed.error ? 'ERR' : (parsed.phones.length ? parsed.phones.join(',') : 'NO_PHONE');
    console.log(`${String(i + 1).padStart(3)}/${urls.length} ${tag.padEnd(26)} ${(parsed.name || '').slice(0, 46)}`);
    await page.waitForTimeout(DELAY);
  }
  console.log('ALL DONE');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
