// cdp-shot.mjs — 确保有一个 discord 标签页（没有就把最新标签导航过去），截图 + 上下文/存储 API 诊断
import { writeFileSync } from 'node:fs';
const BASE = 'http://127.0.0.1:9222';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const list = await (await fetch(BASE + '/json/list')).json();
const pages = list.filter(x => x.type === 'page');
let dt = pages.find(x => /discord\.com/.test(x.url));
if (!dt) dt = pages[pages.length - 1]; // 最新的标签（通常是刚开的 about:blank）
if (!dt) { console.log('NO_PAGE_TARGET'); process.exit(1); }
console.log('TARGET_BEFORE:', dt.url.slice(0, 70));

const ws = new WebSocket(dt.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params })); });
const fire = (method, params = {}) => { const mid = ++id; ws.send(JSON.stringify({ id: mid, method, params })); };

await send('Page.enable');
await send('Runtime.enable');
if (!/discord\.com/.test(dt.url)) {
  console.log('navigating newest tab -> https://discord.com/app ...');
  fire('Page.navigate', { url: 'https://discord.com/app' });
  await sleep(10000);
}
const expr = '(function(){try{return JSON.stringify({href:location.href.slice(0,60), ls:typeof localStorage, ss:typeof sessionStorage, idb:typeof indexedDB, cache:typeof caches})}catch(e){return "ERR:"+e.message}})()';
for (let i = 0; i < 5; i++) {
  try {
    const r = await Promise.race([
      send('Runtime.evaluate', { expression: expr, returnByValue: true }),
      sleep(6000).then(() => null)
    ]);
    if (r && r.result) { console.log('CONTEXT:', r.result.value); break; }
  } catch (e) { console.log('eval retry', i, e.message); await sleep(2000); }
}
try {
  const shot = await Promise.race([
    send('Page.captureScreenshot', { format: 'png' }),
    sleep(8000).then(() => null)
  ]);
  if (shot && shot.data) { writeFileSync('discord-tab.png', Buffer.from(shot.data, 'base64')); console.log('SCREENSHOT_SAVED'); }
  else console.log('SCREENSHOT_TIMEOUT');
} catch (e) { console.log('SHOT_FAIL:', e.message); }
ws.close();
