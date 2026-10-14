// cdp-session-search.mjs — 附着已登录 Chrome：从真实流量捕获 Authorization 头 → 执行官方搜索
// 用法: node cdp-session-search.mjs "关键词" [服务器序号]
// 安全承诺: token 仅存在于本脚本内存，不打印、不写盘；所有请求都以用户本人会话发出
const BASE = 'http://127.0.0.1:9222';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const list = await (await fetch(BASE + '/json/list')).json();
const dt = list.find(x => x.type === 'page' && /discord\.com/.test(x.url));
if (!dt) { console.log('NO_DISCORD_TAB: 先在 9222 Chrome 打开 https://discord.com/app 并登录'); process.exit(1); }
console.log('TARGET:', dt.url.slice(0, 70));

const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pending = new Map();
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });
// 发后不管（Page.reload 的 CDP 响应可能永不到达，会话已挂起等待）
const fire = (method, params = {}) => { const mid = ++id; ws.send(JSON.stringify({ id: mid, method, params })); };

await send('Network.enable');
await send('Page.enable');

// 1) 从客户端真实 API 调用的请求头里捕获 Authorization
let token = null;
const onMsg = ev => {
  const m = JSON.parse(ev.data);
  if (m.method === 'Network.requestWillBeSent') {
    const h = (m.params.request && m.params.request.headers) || {};
    const a = h.authorization || h.Authorization;
    if (a && /discord\.com/.test(m.params.request.url || '')) token = a;
  }
  if (m.method === 'Network.requestWillBeSentExtraInfo') {
    const h = m.params.headers || {};
    const a = h.authorization || h.Authorization;
    if (a) token = a;
  }
};
ws.addEventListener('message', onMsg);
console.log('reloading discord tab to capture live Authorization header ...');
fire('Page.reload', { ignoreCache: false });
for (let i = 0; i < 50 && !token; i++) await sleep(500);
ws.removeEventListener('message', onMsg);
if (!token) { console.log('NO_TOKEN_CAPTURED: 页面 reload 后未见带 Authorization 的 API 请求（可能未登录或页面异常）'); process.exit(2); }
console.log('Authorization captured from live traffic (length ' + token.length + ', content not shown)');

await sleep(6000); // 等 app 启动完成
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.value;

// 2) 登录态校验 + 用户名
const me = await ev(`fetch('/api/v9/users/@me',{headers:{authorization: ${JSON.stringify(token)}, accept:'*/*'}}).then(async r=>({status:r.status, body: r.status===200? await r.json(): await r.text()}))`);
if (me?.status !== 200) { console.log('LOGIN_CHECK_FAILED:', JSON.stringify(me).slice(0, 200)); process.exit(3); }
console.log('LOGIN_OK as:', me.body.username, '| id:', me.body.id);

// 3) 服务器列表
const guilds = await ev(`fetch('/api/v9/users/@me/guilds',{headers:{authorization: ${JSON.stringify(token)}, accept:'*/*'}}).then(r=>r.json())`);
if (!Array.isArray(guilds) || !guilds.length) { console.log('NO_GUILDS'); process.exit(4); }
console.log('GUILDS(' + guilds.length + '):');
guilds.slice(0, 10).forEach((g, i) => console.log('  [' + i + ']', g.name, '(' + g.id + ')'));

// 4) 官方搜索端点（与客户端 Ctrl+F 同后端）
const q = process.argv[2] || 'a';
const gi = Number(process.argv[3] || 0);
const g = guilds[gi] || guilds[0];
const search = await ev(`fetch('/api/v9/guilds/${g.id}/messages/search',{method:'POST',headers:{authorization: ${JSON.stringify(token)}, accept:'*/*','content-type':'application/json'},body:JSON.stringify({content:${JSON.stringify(q)},include_nsfw:true,sort_by:'timestamp',sort_order:'desc',offset:0,limit:25})}).then(async r=>({status:r.status, body: r.status===200? await r.json(): await r.text()}))`);
if (search.status === 200) {
  const raw = search.body.messages || [];
  const flat = raw.flat ? raw.flat().filter(Boolean) : raw;
  console.log('SEARCH ' + JSON.stringify(q) + ' in "' + g.name + '" -> total_results:', search.body.total_results, '| returned:', flat.length);
  flat.slice(0, 5).forEach(m => console.log('  -', (m.author && m.author.username) || '?', ':', String(m.content || '(embed/attachment)').slice(0, 70), '| ch:' + (m.channel_id || '?')));
} else {
  console.log('SEARCH_FAILED status:', search.status, '| body:', String(search.body).slice(0, 300));
}
ws.close();
