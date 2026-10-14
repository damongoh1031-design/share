// cdp-discord-search.mjs — 通过本机 Chrome CDP(9222) 驱动「已登录的 Discord 会话」执行官方搜索
// 用法: node cdp-discord-search.mjs "关键词" [guild序号]
// 原理: 附着到你正在运行的 Chrome（不提取 token、不开新会话），在 discord.com 页面上下文里
//       调用与官方客户端完全相同的内部搜索端点 POST /api/v9/guilds/{id}/messages/search
// 前提: Chrome 以 --remote-debugging-port=9222 启动，且该浏览器已登录 discord.com
const BASE = 'http://127.0.0.1:9222';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const list = await (await fetch(BASE + '/json/list')).json();
const pages = list.filter(t => t.type === 'page');
let target = pages.find(t => /discord\.com/.test(t.url));
const reused = !!target;
if (!target) target = pages[0];
if (!target) { console.error('NO_PAGE_TARGET: 9222 可达但没有普通标签页'); process.exit(1); }
console.log(reused ? 'REUSE_DISCORD_TAB: ' + target.url.slice(0, 80) : 'USING_TAB: ' + target.url.slice(0, 80));

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('WS_FAIL')); });
let id = 0; const pending = new Map();
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => {
  const mid = ++id;
  pending.set(mid, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result));
  ws.send(JSON.stringify({ id: mid, method, params }));
});

await send('Runtime.enable');
if (!/discord\.com/.test(target.url)) {
  console.log('navigating tab -> https://discord.com/app ...');
  await send('Page.enable').catch(() => {});
  await send('Page.navigate', { url: 'https://discord.com/app' });
  await sleep(8000);
}
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.value;

// 1) 登录态校验
const me = await ev(`fetch('/api/v9/users/@me',{headers:{accept:'*/*'}}).then(async r=>({status:r.status, body: r.status===200? await r.json(): await r.text()}))`);
if (me?.status !== 200) { console.log('LOGIN_CHECK_FAILED:', JSON.stringify(me).slice(0, 200), '\n=> 该 9222 浏览器未登录 Discord。需用你常用的 Chrome 配置文件重启（见交付说明）。'); process.exit(2); }
console.log('LOGIN_OK as:', me.body.username, '| id:', me.body.id);

// 2) 拉取服务器列表
const guilds = await ev(`fetch('/api/v9/users/@me/guilds',{headers:{accept:'*/*'}}).then(r=>r.json())`);
if (!Array.isArray(guilds) || !guilds.length) { console.log('NO_GUILDS'); process.exit(3); }
console.log('GUILDS(' + guilds.length + '):');
guilds.slice(0, 10).forEach((g, i) => console.log('  [' + i + ']', g.name, '(' + g.id + ')'));

// 3) 官方搜索端点（与客户端 Ctrl+F 后端同一个）
const q = process.argv[2] || 'a';
const gi = Number(process.argv[3] || 0);
const g = guilds[gi] || guilds[0];
const search = await ev(`fetch('/api/v9/guilds/${g.id}/messages/search',{method:'POST',headers:{accept:'*/*','content-type':'application/json'},body:JSON.stringify({content:${JSON.stringify(q)},include_nsfw:true,sort_by:'timestamp',sort_order:'desc',offset:0,limit:25})}).then(async r=>({status:r.status, body: r.status===200? await r.json(): await r.text()}))`);
if (search.status === 200) {
  const raw = search.body.messages || [];
  const flat = raw.flat ? raw.flat().filter(Boolean) : raw;
  console.log('SEARCH ' + JSON.stringify(q) + ' in "' + g.name + '" -> total_results:', search.body.total_results, '| returned:', flat.length);
  flat.slice(0, 3).forEach(m => console.log('  -', (m.author && m.author.username) || '?', ':', String(m.content || '(embed/attachment)').slice(0, 60), '| ch:' + (m.channel_id || '?')));
} else {
  console.log('SEARCH_FAILED status:', search.status, '| body:', String(search.body).slice(0, 300));
}
ws.close();
