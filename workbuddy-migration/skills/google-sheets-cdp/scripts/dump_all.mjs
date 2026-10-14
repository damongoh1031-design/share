// 按工作表名导出全部 CSV 到本地
import fs from 'node:fs';
import path from 'node:path';

const CDP = 'http://127.0.0.1:9222';
const ID = '1WdlrWe2vY8cVCzyowfZJUF1F6H4oEhwz9iLIVH4lAPU';
const OUT = process.env.OUT_DIR || '.';

const list = await (await fetch(`${CDP}/json/list`)).json();
const target = list.filter((t) => t.type === 'page').find((p) => p.url.includes('docs.google.com/spreadsheets'));
if (!target) {
  console.error('no sheets tab');
  process.exit(2);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
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

const evalJs = async (expression, timeoutMs = 60000) => {
  const r = await Promise.race([
    send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
    new Promise((_, rej) => setTimeout(() => rej(new Error('TIMEOUT')), timeoutMs)),
  ]);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'eval error');
  return r.result.value;
};

const namesRaw = await evalJs(`(() => {
  const out = [];
  document.querySelectorAll('[id^="sheet-button-"]').forEach(el => {
    const n = (el.innerText || '').trim();
    if (n) out.push(n);
  });
  if (!out.length) document.querySelectorAll('.docs-sheet-tab').forEach(el => {
    const n = (el.innerText || '').trim();
    if (n) out.push(n);
  });
  return JSON.stringify(out);
})()`);
const names = JSON.parse(namesRaw);
console.log('SHEETS:', names.join(' | '));

const index = [];
for (const name of names) {
  const csv = await evalJs(
    `(async () => {
      const r = await fetch('https://docs.google.com/spreadsheets/d/${ID}/gviz/tq?tqx=out:csv&sheet=${encodeURIComponent(name)}', {credentials:'include'});
      return await r.text();
    })()`
  );
  const safe = name.replace(/[\\/:*?"<>|]/g, '_').slice(0, 60);
  const file = path.join(OUT, `${safe}.csv`);
  fs.writeFileSync(file, csv, 'utf8');
  const rows = csv.split('\n').filter((l) => l.trim()).length;
  index.push({ name, rows, bytes: csv.length, file });
  console.log(`SAVED ${safe}.csv  rows=${rows}  bytes=${csv.length}`);
}

fs.writeFileSync(path.join(OUT, '_index.json'), JSON.stringify(index, null, 2), 'utf8');
console.log('DONE');
ws.close();
process.exit(0);
