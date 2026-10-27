const fs = require('fs');
const { chromium } = require('playwright');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
  });
  const ctx = await browser.newContext({ locale: 'en-US', userAgent: UA, viewport: { width: 1366, height: 900 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(60000);

  // warm up: hit homepage so the WAF sets its cookie
  for (const home of ['https://seekclinic.my/', 'https://www.aestheticclinic.my/']) {
    await page.goto(home, { waitUntil: 'domcontentloaded' }).catch(e => console.log('warm err', home, e.message));
    await page.waitForTimeout(6000);
    console.log('warm', home, '->', await page.title().catch(() => '?'));
  }

  const fetchXml = async (url) => {
    try {
      return await page.evaluate(async (u) => {
        const r = await fetch(u, { credentials: 'include' });
        return r.status + '\u0000' + (await r.text());
      }, url);
    } catch (e) {
      return 'ERR\u0000' + e.message;
    }
  };

  const out = {};

  // ---- Seek Clinic sitemap index ----
  console.log('\n=== seekclinic sitemap_index.xml ===');
  const [st, body] = (await fetchXml('https://seekclinic.my/sitemap_index.xml')).split('\u0000');
  console.log('status', st, 'len', (body || '').length);
  const children = [...(body || '').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].trim());
  console.log('child sitemaps:', children.length);
  fs.writeFileSync('seekclinic_sitemap_children.txt', children.join('\n') + '\n');
  out.seek_children = children.length;

  // ---- AestheticClinic sitemap index ----
  console.log('\n=== aestheticclinic wp-sitemap.xml ===');
  const [st2, body2] = (await fetchXml('https://www.aestheticclinic.my/wp-sitemap.xml')).split('\u0000');
  console.log('status', st2, 'len', (body2 || '').length);
  const acChildren = [...(body2 || '').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].trim());
  console.log('child sitemaps:', acChildren.length);
  for (const c of acChildren) console.log('  ', c);
  fs.writeFileSync('aestheticclinic_sitemap_children.txt', acChildren.join('\n') + '\n');

  fs.writeFileSync('sitemap_probe.json', JSON.stringify(out, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
