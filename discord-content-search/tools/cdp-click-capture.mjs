// cdp-click-capture.mjs — 不 reload：模拟点击 Discord 侧边栏触发真实 API 流量 → 捕获 Authorization → 执行搜索
// 用法: node cdp-click-capture.mjs "关键词" [服务器序号]
// 安全承诺: token 仅存在脚本内存，不打印、不写盘；所有请求以用户本人会话发出
const BASE = 'http://127.0.0.1:9222';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const list = await (await fetch(BASE + '/json/list')).json();
const dt = list.find(x => x.type === 'page' && /discord\.com/.test(x.url));
if (!dt) { console.log('NO_DISCORD_TAB'); process.exit(1); }
console.log('TARGET:', dt.url.slice(0, 70));

const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pending = new Map();
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });

await send('Network.enable');
await send('Page.enable');

let token = null;
const grab = h => { const a = (h || {}).authorization || (h || {}).Authorization; if (a) token = a; };
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.method === 'Network.requestWillBeSent') grab(m.params.request && m.params.request.headers);
  if (m.method === 'Network.requestWillBeSentExtraInfo') grab(m.params.headers);
});

// 模拟点击侧边栏触发客户端真实流量（商店/任务/首页等）
const clickPoints = [[150, 96], [150, 132], [150, 178], [62, 44], [350, 32], [430, 918]];
for (const [x, y] of clickPoints) {
  if (token) break;
  console.log('click at', x, y);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  for (let i = 0; i < 8 && !token; i++) await sleep(500);
}
if (!token) { console.log('NO_TOKEN_CAPTURED after clicks — 侧边栏点击未触发带 Authorization 的 API 请求'); process.exit(2); }
console.log('Authorization captured (length ' + token.length + ', content not shown)');

// 带 12s 超时 + 自动重试的页面内求值（防店铺页/导航中 fetch 挂起）
const ev = async (expr) => {
  for (let i = 0; i < 4; i++) {
    try {
      const wrapped = `(async()=>{try{const r=await Promise.race([(${expr}),new Promise((_,j)=>setTimeout(()=>j(new Error('FETCH_TIMEOUT')),12000))]);return JSON.stringify(r)}catch(e){return 'ERR:'+e.message}})()`;
      const r = await send('Runtime.evaluate', { expression: wrapped, awaitPromise: true, returnByValue: true });
      if (r && r.result && typeof r.result.value === 'string') {
        try { return JSON.parse(r.result.value); } catch { return r.result.value; }
      }
    } catch (e) { /* CDP 层错误，重试 */ }
    await sleep(2000);
  }
  return undefined;
};

const me = await ev(`fetch('/api/v9/users/@me',{headers:{authorization: ${JSON.stringify(token)}, accept:'*/*'}}).then(async r=>({status:r.status, body: r.status===200? await r.json(): await r.text()}))`);
if (me?.status !== 200) { console.log('LOGIN_CHECK_FAILED:', JSON.stringify(me).slice(0, 200)); process.exit(3); }
console.log('LOGIN_OK as:', me.body.username, '| id:', me.body.id);

const guilds = await ev(`fetch('/api/v9/users/@me/guilds',{headers:{authorization: ${JSON.stringify(token)}, accept:'*/*'}}).then(r=>r.json())`);
console.log('GUILDS:', Array.isArray(guilds) ? guilds.length : 'N/A');
if (Array.isArray(guilds)) guilds.slice(0, 10).forEach((g, i) => console.log('  [' + i + ']', g.name, '(' + g.id + ')'));

if (Array.isArray(guilds) && guilds.length) {
  const g = guilds[Number(process.argv[3] || 0)] || guilds[0];
  // 4) 官方搜索端点 —— 实测正确姿势：GET + query 参数（POST 会 405，messages-search 连字符版 404）
  const q = process.argv[2] || 'a';
  const url = `/api/v9/guilds/${g.id}/messages/search?content=${encodeURIComponent(q)}&include_nsfw=true&sort_by=timestamp&sort_order=desc&offset=0&limit=25`;
  const search = await ev(`fetch('${url}',{headers:{authorization: ${JSON.stringify(token)}, accept:'*/*'}}).then(async r=>({s:r.status, b: r.status===200? await r.json(): (await r.text()).slice(0,200)}))`);
  if (search && search.s === 200) {
    const groups = search.b.messages || [];
    console.log('SEARCH ' + JSON.stringify(q) + ' in "' + g.name + '" -> total_results:', search.b.total_results, '| groups returned:', groups.length);
    groups.slice(0, 5).forEach((grp, i) => {
      const hit = Array.isArray(grp) ? grp[0] : grp;
      if (hit) console.log('  [' + (i + 1) + ']', (hit.author && hit.author.username) || '?', ':', String(hit.content || '(embed/attachment)').slice(0, 80));
    });
  } else {
    console.log('SEARCH_FAILED:', JSON.stringify(search).slice(0, 250));
  }
} else {
  console.log('NO_GUILDS: 该账号未加入任何服务器');
}
ws.close();
