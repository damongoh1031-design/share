// 登录态采集 Facebook 公共主页：正文文本 + 手机/电邮 + 帖子大图
//
// 用法:
//   node fb_harvest.js urls.txt outdir [scrollTimes=8] [maxImgs=26] [cookies.json]
//
// 产出:
//   <outdir>/pages.jsonl      一行一个页面（body_excerpt / phones / emails / img_count / saved_images）
//   <outdir>/<slug>/<id>.jpg  帖子图片，<id> 为 FB 图片 ID，便于回溯
//
// 关键点:
//   - 必须带登录 cookie。登出态只有 590px 缩略图，改写 CDN 的 stp/ctp 参数会返回
//     "URL signature mismatch"（22 字节），所以别试图改 URL，要拿登录态下 DOM 里的 naturalWidth。
//   - 同名图片会以多种尺寸出现，按图片 ID 归并后取面积最大的一张。
//   - 图片用页面内 fetch 下载，带上 cookie 与 referer，比外部请求稳。
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const listFile = process.argv[2];
const outDir = process.argv[3] || '_raw/fb_out';
const scrolls = parseInt(process.argv[4] || '8', 10);
const maxImgs = parseInt(process.argv[5] || '26', 10);
const cookieFile = process.argv[6] || path.join(process.cwd(), '..', '_raw', 'fb_cookies.json');

const COOKIES = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const PHONE = /(?:\+?60|0)\s?\d{1,2}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}/g;
const MAIL = /[\w\.\-\+]+@[\w\-]+\.[\w\.\-]{2,}/g;

function fmtMy(raw) {
  let d = String(raw).replace(/[^\d+]/g, '');
  if (d.startsWith('+60')) { } else if (d.startsWith('60')) d = '+' + d;
  else if (d.startsWith('0')) d = '+6' + d; else return null;
  const n = d.replace(/\D/g, '').length;
  if (n < 9 || n > 12) return null;
  const s = d.replace(/\D/g, '').slice(2);
  let area, rest;
  if (s.startsWith('1')) { area = s.slice(0, 2); rest = s.slice(2); }
  else if (s[0] === '8' && s.length >= 8) { area = s.slice(0, 2); rest = s.slice(2); }
  else { area = s[0]; rest = s.slice(1); }
  const body = rest.length === 8 ? rest.slice(0, 4) + ' ' + rest.slice(4)
    : rest.length >= 6 ? rest.slice(0, 3) + ' ' + rest.slice(3) : rest;
  return `+60 ${area}-${body}`;
}
const uniq = a => [...new Set(a)];

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const urls = fs.readFileSync(listFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
  });
  const ctx = await browser.newContext({ viewport: { width: 1500, height: 1100 }, locale: 'zh-CN', userAgent: UA });
  await ctx.addCookies(COOKIES.map(c => ({ ...c, sameSite: c.sameSite === 'None' ? 'None' : 'Lax' })));
  const out = fs.createWriteStream(path.join(outDir, 'pages.jsonl'), { flags: 'a' });

  const probe = await ctx.newPage();
  await probe.goto('https://www.facebook.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await probe.waitForTimeout(4000);
  const loggedIn = await probe.evaluate(() => !!document.cookie.match(/c_user=/));
  console.log('LOGIN', loggedIn, '|', await probe.title());
  if (!loggedIn) { console.log('!! cookie 失效'); await browser.close(); process.exit(2); }
  await probe.close();

  for (const url of urls) {
    const slug = (url.match(/facebook\.com\/(?:p\/)?([^\/\?]+)/) || [, 'unknown'])[1]
      .replace(/[^\w\-]/g, '_').slice(0, 60);
    const page = await ctx.newPage();
    const rec = { url, slug, ts: new Date().toISOString(), login: loggedIn };
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(6000);
      for (const sel of ['div[aria-label="关闭"]', 'div[aria-label="Close"]', 'div[aria-label="關閉"]']) {
        const b = await page.$(sel); if (b) { await b.click().catch(() => { }); break; }
      }
      rec.title = await page.title();
      for (let i = 0; i < scrolls; i++) {
        await page.mouse.wheel(0, 2800);
        await page.waitForTimeout(1600);
      }
      const body = await page.innerText('body').catch(() => '');
      rec.body_len = body.length;
      rec.body_excerpt = body.slice(0, 8000);
      rec.phones = uniq((body.match(PHONE) || []).map(fmtMy).filter(Boolean));
      rec.emails = uniq(body.match(MAIL) || []);

      const raw = await page.$$eval('img', els => els
        .filter(e => e.src.startsWith('https://scontent'))
        .map(e => ({ src: e.src, w: e.naturalWidth, h: e.naturalHeight })));
      const byId = new Map();
      for (const o of raw) {
        const m = o.src.match(/\/(\d{6,})_(\d+)_(\d+)_[a-z]\.(jpg|png|webp)/i);
        const id = m ? m[1] : o.src.slice(-70);
        const cur = byId.get(id);
        if (!cur || o.w * o.h > cur.w * cur.h) byId.set(id, { ...o, id });
      }
      const cand = [...byId.values()].filter(o => o.w >= 480 && o.h >= 300)
        .sort((a, b) => b.w * b.h - a.w * a.h);
      rec.img_count = cand.length;
      rec.max_w = cand.length ? cand[0].w : 0;

      const dir = path.join(outDir, slug);
      fs.mkdirSync(dir, { recursive: true });
      let saved = 0;
      for (const o of cand.slice(0, maxImgs)) {
        const fn = path.join(dir, `${o.id}.jpg`);
        if (fs.existsSync(fn)) { saved++; continue; }
        try {
          const buf = await page.evaluate(async (u) => {
            const r = await fetch(u); const b = await r.arrayBuffer();
            return Array.from(new Uint8Array(b));
          }, o.src);
          fs.writeFileSync(fn, Buffer.from(buf));
          saved++;
        } catch (e) { }
      }
      rec.saved_images = saved;
      console.log('OK  ', slug, '|', (rec.title || '').slice(0, 26), '| maxW', rec.max_w,
        '| big', cand.length, '| saved', saved, '| ph', rec.phones.length);
    } catch (e) {
      rec.err = e.message.slice(0, 160);
      console.log('ERR ', slug, rec.err);
    }
    out.write(JSON.stringify(rec) + '\n');
    await page.close();
  }
  out.end();
  await browser.close();
})();
