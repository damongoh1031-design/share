// 登录态批量搜索 Facebook 公共主页：多查询 -> 去重 -> 按规则过滤 -> CSV
//
// 用法:
//   node fb_search.js queries.txt out.csv [rules.json] [cookies.json]
//
// rules.json（可选，缺省用内置保守规则）:
//   { "keep": "命中才保留的正则", "drop": "命中即剔除的正则", "exclude": "硬排除正则" }
//
// cookies.json 默认读 <cwd>/../_raw/fb_cookies.json，需含 c_user / xs / datr 等。
// 拿 cookie：Chrome 登录 facebook.com -> F12 -> Application -> Cookies -> 复制为 JSON 数组，
//   每条至少要有 {name, value, domain: ".facebook.com", path: "/"}。
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const qFile = process.argv[2];
const outCsv = process.argv[3] || 'fb_found.csv';
const rulesFile = process.argv[4];
const cookieFile = process.argv[5] || path.join(process.cwd(), '..', '_raw', 'fb_cookies.json');

const DEFAULT_RULES = {
  keep: '青年|协会|学会|社团|团契|中心|公会|联合会|总会|youth|association|society|club|fellowship|ministry',
  drop: '补习|診所|诊所|clinic|美容|旅游|保險|保险|地产|汽车|手机|电脑|餐厅|美食|咖啡|直播|网店|代购|按摩|美甲|招聘|课程|学院|大学|中学|小学|幼儿园|安亲|殡葬|风水|命理|塔罗|alumni|校友',
  exclude: ''
};

const rules = fs.existsSync(rulesFile || '')
  ? Object.assign({}, DEFAULT_RULES, JSON.parse(fs.readFileSync(rulesFile, 'utf8')))
  : DEFAULT_RULES;
const KEEP = new RegExp(rules.keep, 'i');
const DROP = new RegExp(rules.drop, 'i');
const EXCL = rules.exclude ? new RegExp(rules.exclude, 'i') : null;

const COOKIES = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));

(async () => {
  const qs = fs.readFileSync(qFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const b = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
  });
  const ctx = await b.newContext({
    viewport: { width: 1500, height: 1100 }, locale: 'zh-CN',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
  });
  await ctx.addCookies(COOKIES);

  // 登录态校验：没有 c_user 就是没登上，搜出来全是登录墙
  const probe = await ctx.newPage();
  await probe.goto('https://www.facebook.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await probe.waitForTimeout(3000);
  const loggedIn = await probe.evaluate(() => !!document.cookie.match(/c_user=/));
  console.log('LOGIN', loggedIn);
  if (!loggedIn) { console.log('!! cookie 无效，先更新 fb_cookies.json'); await b.close(); process.exit(2); }

  const page = await ctx.newPage();
  const found = new Map();

  for (const q of qs) {
    try {
      await page.goto('https://www.facebook.com/search/pages/?q=' + encodeURIComponent(q),
        { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(5000);
      for (let i = 0; i < 3; i++) { await page.mouse.wheel(0, 2400); await page.waitForTimeout(1400); }

      const pairs = await page.$$eval('a', as => as.map(a => ({ t: (a.innerText || '').trim(), h: a.href })));
      let n = 0;
      for (const { t, h } of pairs) {
        if (!t || t.length > 60) continue;
        // 只要「主页」链接，排除帖子/视频/群组
        if (!/facebook\.com\/(p\/[^\/?]+|[A-Za-z0-9_.\-]+)\/?$/.test(h)) continue;
        if (/search|login|help|policies|photo|reel|watch|group|event|notification|messages/.test(h)) continue;
        if (EXCL && EXCL.test(t)) continue;
        if (DROP.test(t)) continue;
        if (!KEEP.test(t)) continue;
        const u = h.replace(/\?.*$/, '');
        if (!found.has(u)) { found.set(u, { name: t, url: u, query: q }); n++; }
      }
      console.log('Q', q.slice(0, 24), '| new', n, '| total', found.size);
    } catch (e) {
      console.log('ERR', q.slice(0, 20), e.message.slice(0, 60));
    }
  }

  const esc = s => '"' + String(s).replace(/"/g, '""') + '"';
  const lines = ['name,url,query'];
  for (const v of found.values()) lines.push([esc(v.name), esc(v.url), esc(v.query)].join(','));
  fs.writeFileSync(outCsv, '\ufeff' + lines.join('\n'), 'utf8');
  console.log('TOTAL', found.size, '->', outCsv);
  await b.close();
})();
