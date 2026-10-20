// 极简 CDP 驱动：启动 headless Chrome，加载原型，执行脚本，收集错误
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9333;
const FILE = process.argv[2] || 'crm-prototype.html';
const URL = 'file:///' + FILE.replace(/\\/g, '/').replace(/^\/+/, '');
const PROFILE = 'C:/Users/Admin/AppData/Local/Temp/cdpprof-' + Date.now();

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE,
  '--allow-file-access-from-files', '--window-size=1600,1100', 'about:blank'
], { stdio: 'ignore' });

let ws, id = 0;
const pending = new Map();
const errors = [];
const logs = [];

async function connect() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      const j = await r.json();
      ws = new WebSocket(j.webSocketDebuggerUrl);
      await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
      ws.onmessage = ev => {
        const m = JSON.parse(ev.data);
        if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
        if (m.method === 'Runtime.exceptionThrown') {
          errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
        }
        if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
          logs.push(m.params.args.map(a => a.value ?? a.description).join(' '));
        }
      };
      return;
    } catch { await sleep(250); }
  }
  throw new Error('chrome 未就绪');
}
function send(method, params = {}, sessionId) {
  const mid = ++id;
  return new Promise(res => {
    pending.set(mid, res);
    ws.send(JSON.stringify({ id: mid, method, params, sessionId }));
  });
}

let sessionId;
async function evalJS(expr, awaitPromise = true) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise }, sessionId);
  if (r.result?.exceptionDetails) {
    const d = r.result.exceptionDetails;
    throw new Error((d.exception?.description || d.text) + ' :: ' + expr.slice(0, 120));
  }
  return r.result?.result?.value;
}

async function main() {
  await connect();
  const t = await send('Target.createTarget', { url: 'about:blank' });
  const targetId = t.result.targetId;
  const at = await send('Target.attachToTarget', { targetId, flatten: true });
  sessionId = at.result.sessionId;
  await send('Runtime.enable', {}, sessionId);
  await send('Page.enable', {}, sessionId);
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 1100, deviceScaleFactor: 1, mobile: false }, sessionId);
  await send('Page.navigate', { url: URL }, sessionId);
  await sleep(900);

  const api = { send: (m, p) => send(m, p, sessionId), evalJS, sleep, errors, logs, sessionId };
  const mod = await import(process.argv[3] || './suite.mjs');
  await mod.default(api);
}

main()
  .catch(e => { console.error('FATAL', e.message); process.exitCode = 1; })
  .finally(async () => {
    try { ws && ws.close(); } catch { }
    try { chrome.kill(); } catch { }
    await sleep(300);
    process.exit(process.exitCode || 0);
  });
