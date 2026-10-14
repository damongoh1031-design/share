// 按文本查找可见按钮/链接并真实点击（CDP 原生鼠标事件，自动滚动到视口内）
// 用法: node click_text.mjs <urlSubstring> "<文本正则>" [第几个，默认0] [--dry]
const CDP = 'http://127.0.0.1:9222';
const urlMatch = process.argv[2];
const textRe = process.argv[3];
const nth = Number(process.argv[4] || 0);
const dry = process.argv.includes('--dry');

const list = await (await fetch(`${CDP}/json/list`)).json();
const tab = list.filter((t) => t.type === 'page').find((p) => p.url.includes(urlMatch));
if (!tab) {
  console.error('no tab matching:', urlMatch);
  list.filter((t) => t.type === 'page').forEach((p) => console.error('  ', p.url.slice(0, 120)));
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

// 第一步：匹配 + 滚动到视口中央
const findExpr = `(() => {
  var re = new RegExp(${JSON.stringify(textRe)});
  var norm = function (el) { return (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim(); };
  var all = Array.from(document.querySelectorAll('button, a, [role=button], [role=menuitem], [role=tab], input[type=submit], span, div'));
  var cands = all.filter(function (el) {
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    var r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return false;
    if (!re.test(norm(el))) return false;
    return !Array.from(el.children).some(function (c) { return re.test(norm(c)); });
  });
  if (!cands.length) return JSON.stringify({ found: false, count: 0 });
  var el = cands[${nth}] || cands[0];
  window.__ct = el;
  try { el.scrollIntoView({ block: 'center', inline: 'center' }); } catch (e) {}
  return JSON.stringify({ found: true, count: cands.length, text: norm(el).slice(0, 60), tag: el.tagName });
})()`;

const raw = await evalJs(findExpr);
if (typeof raw !== 'string' || raw.startsWith('__ERR__')) {
  console.error('eval failed:', raw);
  process.exit(3);
}
const info = JSON.parse(raw);
console.log('MATCH:', JSON.stringify(info));
if (!info.found) process.exit(4);

if (dry) {
  console.log('(dry run, not clicking)');
  process.exit(0);
}

await sleep(700); // 等滚动稳定

const rectRaw = await evalJs(`(() => {
  var el = window.__ct;
  if (!el) return 'null';
  var r = el.getBoundingClientRect();
  return JSON.stringify({ x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height, inView: r.y >= 0 && r.y + r.height <= innerHeight });
})()`);
if (!rectRaw || rectRaw === 'null') {
  console.error('lost element reference');
  process.exit(5);
}
const rect = JSON.parse(rectRaw);
console.log('RECT:', JSON.stringify(rect));
if (!rect.inView) console.error('WARN: still out of viewport, click may miss');

await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: rect.x, y: rect.y });
await sleep(120);
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
await sleep(80);
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
console.log('CLICKED', info.tag, '@', Math.round(rect.x), Math.round(rect.y));

await sleep(3000);
console.log('URL_NOW:', await evalJs('location.href'));
ws.close();
process.exit(0);
