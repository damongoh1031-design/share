// 读取单个 Google 工作表为 CSV（在页面上下文 fetch，复用登录 cookie）
// 用法:
//   SHEET_ID=<表格ID> SHEET_NAME=<工作表名> node read_sheet.mjs
// 或直接改下面的常量。
//
// 注意: gviz 只读。写入见 SKILL.md「写入表格」一节。

const CDP = 'http://127.0.0.1:9222';
const ID = process.env.SHEET_ID || '1WdlrWe2vY8cVCzyowfZJUF1F6H4oEhwz9iLIVH4lAPU';
const NAME = process.env.SHEET_NAME || '';
const GID = process.env.SHEET_GID || '';

const list = await (await fetch(`${CDP}/json/list`)).json();
const tab = list.filter((t) => t.type === 'page').find((p) => p.url.includes('docs.google.com/spreadsheets'));
if (!tab) {
  console.error('没有打开的 Google 表格标签页');
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

// 列出工作表名（若未指定）
const names = JSON.parse(
  await (async () => {
    const r = await send('Runtime.evaluate', {
      expression: `JSON.stringify([...document.querySelectorAll('[id^="sheet-button-"]')].map(el => (el.innerText||'').trim()).filter(Boolean))`,
      returnByValue: true,
    });
    return r.result.value;
  })()
);
console.log('工作表:', names.join(' | '));

const selector = GID
  ? `gid=${GID}`
  : `sheet=${encodeURIComponent(NAME || names[0])}`;

const r = await Promise.race([
  send('Runtime.evaluate', {
    expression: `(async () => {
      const res = await fetch('https://docs.google.com/spreadsheets/d/${ID}/gviz/tq?tqx=out:csv&${selector}', { credentials: 'include' });
      return await res.text();
    })()`,
    returnByValue: true,
    awaitPromise: true,
  }),
  new Promise((_, rej) => setTimeout(() => rej(new Error('TIMEOUT')), 45000)),
]);

const csv = r.result.value;
const lines = csv.split('\n').filter((l) => l.trim()).length;
console.log(`OK  rows=${lines}  bytes=${csv.length}`);
console.log('--- preview ---');
console.log(csv.slice(0, 1200));

ws.close();
process.exit(0);
