// cdp-cookie-check.mjs — 只读诊断：9222 Chrome 的 discord.com 标签页 localStorage 键名 + cookie 罐 + 登录态
const BASE = 'http://127.0.0.1:9222';
const list = await (await fetch(BASE + '/json/list')).json();
const dt = list.find(x => x.type === 'page' && /discord\.com/.test(x.url));
if (!dt) { console.log(JSON.stringify({ discordTabOpen: false, pages: list.filter(x => x.type === 'page').map(x => x.url.slice(0, 60)) })); process.exit(0); }
const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const p = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && p.has(m.id)) { p.get(m.id)(m); p.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; p.set(mid, m => m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });
await send('Runtime.enable');
const ls = await send('Runtime.evaluate', { expression: `JSON.stringify({url: location.href.slice(0,60), lsKeys: Object.keys(localStorage), hasTokenKey: !!localStorage.getItem('token'), tokenLen: (localStorage.getItem('token')||'').length})`, returnByValue: true });
console.log('LOCALSTORAGE:', ls.result.value);
await send('Network.enable');
const r = await send('Network.getCookies', { urls: ['https://discord.com'] });
const names = (r.cookies || []).map(c => c.name);
console.log('COOKIES(' + names.length + '):', names.join(','));
ws.close();
