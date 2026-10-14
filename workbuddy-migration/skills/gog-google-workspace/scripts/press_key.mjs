// 发送真实按键（CDP 原生）
// 用法: node press_key.mjs <urlSubstring> <Enter|Tab|Escape|ArrowDown|Space>
const CDP = 'http://127.0.0.1:9222';
const urlMatch = process.argv[2];
const keyName = process.argv[3] || 'Enter';

const KEYS = {
  Enter: { key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 },
  Tab: { key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 },
  Escape: { key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 },
  ArrowDown: { key: 'ArrowDown', code: 'ArrowDown', windowsVirtualKeyCode: 40 },
  Space: { key: ' ', code: 'Space', windowsVirtualKeyCode: 32 },
};
const k = KEYS[keyName];
if (!k) {
  console.error('unsupported key:', keyName, '| supported:', Object.keys(KEYS).join(', '));
  process.exit(1);
}

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
await send('Page.bringToFront');
await send('Emulation.setFocusEmulationEnabled', { enabled: true });

await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', ...k });
await new Promise((r) => setTimeout(r, 60));
await send('Input.dispatchKeyEvent', { type: 'keyUp', ...k });
console.log('PRESSED', keyName);
ws.close();
process.exit(0);
