// CDP 接管脚本：连接本机 Chrome(9222)，在指定标签页执行 JS 表达式
// usage: node cdp.mjs <urlSubstring> <exprFile> [--nav <url>]
import fs from 'node:fs';

const args = process.argv.slice(2);
const urlMatch = args[0];
const exprFile = args[1];
const navIdx = args.indexOf('--nav');
const navUrl = navIdx >= 0 ? args[navIdx + 1] : null;

const CDP = 'http://127.0.0.1:9222';

const list = await (await fetch(`${CDP}/json/list`)).json();
const pages = list.filter((t) => t.type === 'page');
const target = pages.find((p) => p.url.includes(urlMatch));

if (!target) {
  console.error('NO_TARGET_FOUND');
  pages.forEach((p) => console.error('  page:', p.url.slice(0, 140)));
  process.exit(2);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
let seq = 0;
const pending = new Map();

ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result);
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

const shotIdx = args.indexOf('--shot');
const shotFile = shotIdx >= 0 ? args[shotIdx + 1] : null;

if (navUrl || shotFile || args.includes('--front')) {
  await send('Page.enable');
}
if (args.includes('--front')) {
  try {
    await send('Page.bringToFront');
    await send('Emulation.setFocusEmulationEnabled', { enabled: true });
    console.log('BROUGHT_TO_FRONT');
  } catch (e) {
    console.error('front failed:', e.message);
  }
}
if (navUrl) {
  await send('Page.navigate', { url: navUrl });
  console.log('NAVIGATED ->', navUrl);
}
if (shotFile) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  fs.writeFileSync(shotFile, Buffer.from(r.data, 'base64'));
  console.log('SHOT ->', shotFile);
}

if (exprFile && exprFile !== '-') {
  let expression = fs.readFileSync(exprFile, 'utf8');
  // 占位符注入，避免明文密码落盘
  expression = expression.replace(/__GPWD__/g, JSON.stringify(process.env.GPWD || ''));
  expression = expression.replace(/__GMAIL__/g, JSON.stringify(process.env.GMAIL || ''));
  const timeoutMs = Number(process.env.CDP_TIMEOUT || 25000);
  try {
    const r = await Promise.race([
      send('Runtime.evaluate', {
        expression,
        returnByValue: true,
        awaitPromise: true,
        userGesture: true,
      }),
      new Promise((_, rej) => setTimeout(() => rej(new Error('CDP_EVAL_TIMEOUT')), timeoutMs)),
    ]);
    if (r.exceptionDetails) {
      console.error(
        'EXCEPTION:',
        JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails, null, 2)
      );
      process.exitCode = 3;
    } else {
      const v = r.result.value;
      console.log(typeof v === 'string' ? v : JSON.stringify(v, null, 2));
    }
  } catch (e) {
    console.error('ERROR:', e.message);
    process.exitCode = 4;
  }
}

ws.close();
process.exit(0);
