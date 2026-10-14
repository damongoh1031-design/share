// cdp-discord-weekly.mjs — Discord 服务器「最近一周」热门讨论 digest
// 用法: node cdp-discord-weekly.mjs [天数=7] [guild关键词=RimWorld] [频道逗号列表=auto]
// 方法: CDP捕获Authorization → 频道表 → 对活跃频道 × 近N天做「时间锚点采样」
//       (GET /channels/{id}/messages?limit=50&around=<snowflake>，消息对象含 reactions)
//       → 合并去重 → 按 reactions 总数排名，原始数据落盘 discord-week-raw.json
// 安全承诺: token 仅存在脚本内存，不打印、不写盘
import { writeFileSync } from 'node:fs';
const BASE = 'http://127.0.0.1:9222';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const list = await (await fetch(BASE + '/json/list')).json();
const dt = list.find(x => x.type === 'page' && /discord\.com/.test(x.url));
if (!dt) { console.log('NO_DISCORD_TAB: 先在 9222 Chrome 打开 https://discord.com/app'); process.exit(1); }

const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pending = new Map();
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });

await send('Network.enable');
await send('Page.enable');

// ---- 1) 点击侧边栏捕获 Authorization ----
let token = null;
const grab = h => { const a = (h || {}).authorization || (h || {}).Authorization; if (a) token = a; };
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.method === 'Network.requestWillBeSent') grab(m.params.request && m.params.request.headers);
  if (m.method === 'Network.requestWillBeSentExtraInfo') grab(m.params.headers);
});
for (const [x, y] of [[150, 96], [150, 132], [150, 178], [62, 44]]) {
  if (token) break;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  for (let i = 0; i < 8 && !token; i++) await sleep(500);
}
if (!token) { console.log('NO_TOKEN_CAPTURED — Discord 标签页无响应或未登录'); process.exit(2); }
console.log('token captured (len ' + token.length + ')');

// ---- 2) 带超时重试的页面内求值 ----
const ev = async (expr) => {
  for (let i = 0; i < 3; i++) {
    try {
      const wrapped = `(async()=>{try{const r=await Promise.race([(${expr}),new Promise((_,j)=>setTimeout(()=>j(new Error('T')),15000))]);return JSON.stringify(r)}catch(e){return 'ERR:'+e.message}})()`;
      const r = await send('Runtime.evaluate', { expression: wrapped, awaitPromise: true, returnByValue: true });
      if (r && r.result && typeof r.result.value === 'string') { try { return JSON.parse(r.result.value); } catch { return r.result.value; } }
    } catch (e) { }
    await sleep(2000);
  }
  return undefined;
};
const H = JSON.stringify(token);
const apiGet = async p => {
  for (let a = 0; a < 3; a++) {
    const r = await ev(`fetch('${p}',{headers:{authorization: ${H}, accept:'*/*'}}).then(async r=>({s:r.status, b: r.status===200? await r.json(): (await r.text()).slice(0,120)}))`);
    if (r && r.s === 429) { await sleep(5000); continue; }   // 限流退避
    return r;
  }
  return null;
};

// ---- 3) 服务器 + 频道表 ----
const me = await apiGet('/api/v9/users/@me');
console.log('LOGIN:', me && me.s === 200 ? me.b.username : 'FAILED');
const gRes = await apiGet('/api/v9/users/@me/guilds');
if (!gRes || gRes.s !== 200 || !Array.isArray(gRes.b)) { console.log('GUILDS_FAILED:', JSON.stringify(gRes).slice(0, 300)); process.exit(3); }
const kw = (process.argv[3] || 'RimWorld').toLowerCase();
const g = gRes.b.find(x => x.name.toLowerCase().includes(kw)) || gRes.b[0];
console.log('GUILD:', g.name, '(' + g.id + ')');

const chRes = await apiGet(`/api/v9/guilds/${g.id}/channels`);
const allCh = (chRes && chRes.s === 200 && Array.isArray(chRes.b)) ? chRes.b.filter(c => c.type === 0) : [];
const chMap = {}; allCh.forEach(c => { chMap[c.id] = c.name; });
// 默认频道集：经验活跃 + 名称含 mod/vanilla/general/art 的
const autoNames = ['rimworld', 'mod-development', 'mod-general', 'vanilla', 'general', 'mod-art', 'art', 'colony-sharing'];
let want = (process.argv[4] || '').split(',').filter(Boolean);
if (!want.length) {
  want = allCh.filter(c => autoNames.some(n => c.name === n) || /^(mod|help|vanilla)/.test(c.name)).map(c => c.name).slice(0, 12);
}
let targets = allCh.filter(c => want.includes(c.name));
console.log('SAMPLING_CHANNELS(' + targets.length + '):', targets.map(c => c.name).join(', '));

// ---- 4) 时间锚点采样：每频道 × 近N天各取 around 50 条 ----
const DAYS = Number(process.argv[2] || 7);
const EPOCH = 1420070400000n;
const snowOf = ms => ((BigInt(ms) - EPOCH) << 22n).toString();
const now = Date.now();
const seen = new Map();
let reqCount = 0;
for (const ch of targets) {
  for (let d = DAYS - 1; d >= 0; d--) {
    const sampleAt = now - d * 86400 * 1000 - 5 * 3600 * 1000; // 每天 GMT+8 的 ~07:00
    const around = snowOf(sampleAt);
    await sleep(1200); // 温和速率
    const r = await apiGet(`/api/v9/channels/${ch.id}/messages?limit=50&around=${around}`);
    reqCount++;
    if (!r || r.s !== 200 || !Array.isArray(r.b)) { console.log(`  skip #${ch.name} d-${d}: ${r ? r.s : 'null'}`); continue; }
    let added = 0;
    for (const m of r.b) {
      if (!m.id || seen.has(m.id)) continue;
      seen.set(m.id, m); added++;
    }
    if (d % 2 === 0 || d === 0) console.log(`  #${ch.name} day-${d}: +${added} (total ${seen.size})`);
  }
}
console.log(`\nsampling done: ${reqCount} requests, ${seen.size} unique messages`);

// ---- 5) 过滤 + 热度排名 ----
const cutoff = now - DAYS * 86400 * 1000;
const msgs = [...seen.values()].filter(m => new Date(m.timestamp).getTime() >= cutoff && !(m.author && m.author.bot));
const reactSum = m => (m.reactions || []).reduce((s, r) => s + (r.count || 0), 0);
const fmt = ts => new Date(new Date(ts).getTime() + 8 * 3600 * 1000).toISOString().slice(5, 16).replace('T', ' ');
const chCount = {};
msgs.forEach(m => { const c = chMap[m.channel_id] || m.channel_id; chCount[c] = (chCount[c] || 0) + 1; });

console.log('\n===== 周度样本 =====');
console.log('messages in window:', msgs.length, '| channels:', Object.keys(chCount).length);
console.log('with >=1 reaction:', msgs.filter(m => reactSum(m) > 0).length);
console.log('\n-- 频道活跃度（样本消息数）--');
Object.entries(chCount).sort((a, b) => b[1] - a[1]).forEach(([c, n]) => console.log(`  #${c}: ${n}`));

console.log('\n-- 热门消息 Top 20（reactions 总数）--');
const top = msgs.map(m => ({ m, r: reactSum(m) })).sort((a, b) => b.r - a.r).slice(0, 20);
top.forEach(({ m, r }, i) => {
  const emojis = (m.reactions || []).map(x => (x.emoji && x.emoji.name ? x.emoji.name : '?') + '×' + x.count).join(' ');
  console.log(`[${i + 1}] ${r} | ${chMap[m.channel_id] || '?'} | ${fmt(m.timestamp)} | ${(m.author && m.author.username) || '?'}`);
  console.log(`    ${String(m.content || '(embed/attachment)').slice(0, 140).replace(/\n/g, ' ')}`);
  console.log(`    ${emojis}`);
  console.log(`    https://discord.com/channels/${g.id}/${m.channel_id}/${m.id}`);
});

// ---- 6) 原始数据落盘（供挖掘话题） ----
writeFileSync('discord-week-raw.json', JSON.stringify({
  guild: { id: g.id, name: g.name }, window_days: DAYS, sampled_at: new Date().toISOString(),
  messages: msgs.map(m => ({ id: m.id, channel: chMap[m.channel_id] || m.channel_id, author: m.author && m.author.username, ts: m.timestamp, reactions: reactSum(m), content: m.content || '', type: m.type }))
}, null, 1));
console.log('\nRAW_SAVED: discord-week-raw.json');
ws.close();
