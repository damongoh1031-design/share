// cdp-cookie-check.mjs — 只读检查：用 CDP Network.getCookies 取 9222 浏览器的 discord.com 完整 cookie 罐
// 不导航、不读写页面，纯旁路读取；用于确认「导出 cookie 的浏览器」与「9222 浏览器」是否同一配置文件
const BASE = 'http://127.0.0.1:9222';
const list = await (await fetch(BASE + '/json/list')).json();
const t = list.find(x => x.type === 'page');
if (!t) { console.log('NO_PAGE'); process.exit(1); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const p = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && p.has(m.id)) { p.get(m.id)(m); p.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; p.set(mid, m => m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });
await send('Network.enable');
const r = await send('Network.getCookies', { urls: ['https://discord.com', 'https://discord.com/'] });
const names = (r.cookies || []).map(c => c.name);
const ga = (r.cookies || []).find(c => c.name === '_ga');
console.log(JSON.stringify({
  totalDiscordCookies: names.length,
  names,
  gaValue: ga ? ga.value : null,
  sameProfileAsPastedExport: !!ga && ga.value.includes('830215638')
}));
ws.close();
