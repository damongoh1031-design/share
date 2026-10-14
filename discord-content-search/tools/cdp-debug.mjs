// cdp-debug.mjs — 一次性诊断：9222 Chrome 的 discord 标签页 localStorage 键名与 token 长度
const BASE = 'http://127.0.0.1:9222';
const list = await (await fetch(BASE + '/json/list')).json();
const dt = list.find(x => x.type === 'page' && /discord\.com/.test(x.url));
console.log('TARGET:', dt ? dt.url.slice(0, 60) : 'NONE');
if (!dt) { console.log('PAGES:', list.filter(x => x.type === 'page').map(x => x.url.slice(0, 60))); process.exit(0); }
const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const p = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && p.has(m.id)) { p.get(m.id)(m); p.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; p.set(mid, m => m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });
await send('Runtime.enable');
const expr = [
  '(function(){',
  '  try {',
  '    var keys = Object.keys(localStorage);',
  '    var t = localStorage.getItem("token") || "";',
  '    return JSON.stringify({ href: location.href.slice(0,50), keyCount: keys.length, keys: keys, tokenLen: t.length });',
  '  } catch(e) { return "ERR:" + e.message; }',
  '})()'
].join('\n');
const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
console.log('EVAL_RESULT:', JSON.stringify(r).slice(0, 800));
ws.close();
