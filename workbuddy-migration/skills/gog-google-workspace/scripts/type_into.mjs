// 向输入框真实输入文本（CDP 原生键盘事件，自动滚动）
// 用法: node type_into.mjs <urlSubstring> <target> <text>
//   target = css:<选择器>  或  idx:N（第 N 个可见的非 search 输入框，从 0 开始）
const CDP = 'http://127.0.0.1:9222';
const urlMatch = process.argv[2];
const target = process.argv[3];
const text = process.argv[4] ?? '';

const list = await (await fetch(`${CDP}/json/list`)).json();
const tab = list.filter((t) => t.type === 'page').find((p) => p.url.includes(urlMatch));
if (!tab) {
  console.error('no tab matching:', urlMatch);
  process.exit(2);
}

const ws = new WebSocket(tab.webSocketDebuggerUrl);
let seq = 0;
const pending = new Map();
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { resolve, reject } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
  }
});
const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
await new Promise((r) => ws.addEventListener('open', r));
await send('Runtime.enable');
await send('Page.enable');
await send('Page.bringToFront');
await send('Emulation.setFocusEmulationEnabled', { enabled: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const evalJs = async (expression, timeout = 12000) => {
  try {
    const r = await Promise.race([
      send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
      new Promise((_, rej) => setTimeout(() => rej(new Error('TIMEOUT')), timeout)),
    ]);
    return r.result?.value;
  } catch (e) {
    return '__ERR__' + e.message;
  }
};

const pick = target.startsWith('css:')
  ? `document.querySelector(${JSON.stringify(target.slice(4))})`
  : `Array.from(document.querySelectorAll('input, textarea')).filter(function (e) {
       var r = e.getBoundingClientRect();
       return r.width > 4 && r.height > 4 && e.type !== 'search' && e.type !== 'hidden';
     })[${Number(target.replace('idx:', '')) || 0}]`;

const raw = await evalJs(`(() => {
  var el = ${pick};
  if (!el) return JSON.stringify({ found: false });
  window.__ti = el;
  try { el.scrollIntoView({ block: 'center', inline: 'center' }); } catch (e) {}
  var r = el.getBoundingClientRect();
  return JSON.stringify({ found: true, tag: el.tagName, type: el.type, id: el.id, before: el.value, rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)] });
})()`);
if (typeof raw !== 'string' || raw.startsWith('__ERR__')) {
  console.error('eval failed:', raw);
  process.exit(3);
}
const info = JSON.parse(raw);
console.log('TARGET:', JSON.stringify(info));
if (!info.found) process.exit(4);

await sleep(700);

const rectRaw = await evalJs(`(() => { var el = window.__ti; if (!el) return 'null'; var r = el.getBoundingClientRect(); return JSON.stringify({ x: r.x + r.width/2, y: r.y + r.height/2 }); })()`);
const rect = JSON.parse(rectRaw);

// 真实点击聚焦
await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: rect.x, y: rect.y });
await sleep(80);
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
await sleep(60);
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
await sleep(300);

// 清空
await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', modifiers: 2, key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', modifiers: 2, key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65 });
await sleep(120);
await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8 });
await sleep(200);

// 逐字符真实输入
for (const ch of text) {
  await send('Input.dispatchKeyEvent', { type: 'keyDown', text: ch, unmodifiedText: ch, key: ch });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: ch });
  await sleep(35);
}
await sleep(500);

const after = await evalJs(`(() => { var el = window.__ti; return el ? el.value : '__GONE__'; })()`);
console.log('AFTER:', JSON.stringify(after));
console.log(after === text ? '✅ 输入成功' : '⚠️ 值不匹配（可能被框架改写）');
ws.close();
process.exit(0);
