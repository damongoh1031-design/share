// Google 登录（CDP 接管本机已登录/待登录的 Chrome）
//
// 用法:
//   GMAIL='you@gmail.com' GPWD='yourpassword' \
//     node google_login.mjs [目标URL]
//
// 前提: Chrome 已以 --remote-debugging-port=9222 启动
// 密码通过环境变量传入，不落盘。脚本会先判断是否已登录，已登录则直接导航。

const CDP = process.env.CDP_ENDPOINT || 'http://127.0.0.1:9222';
const EMAIL = process.env.GMAIL;
const PWD = process.env.GPWD;
const TARGET = process.argv[2] || 'https://drive.google.com/drive/home';

if (!EMAIL || !PWD) {
  console.error('缺少 GMAIL / GPWD 环境变量');
  process.exit(1);
}

// ---- 选标签页 ----
const list = await (await fetch(`${CDP}/json/list`)).json();
const pages = list.filter((t) => t.type === 'page' && !t.url.startsWith('chrome://'));
const tab = pages.find((p) => p.url.includes('accounts.google.com')) || pages[0];
if (!tab) {
  console.error('没有可用标签页。请先用 --remote-debugging-port=9222 启动 Chrome 并打开任意页面。');
  process.exit(2);
}

// ---- CDP 连接 ----
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

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const evalJs = async (expression, timeout = 15000) => {
  try {
    const r = await Promise.race([
      send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
      new Promise((_, rej) => setTimeout(() => rej(new Error('EVAL_TIMEOUT')), timeout)),
    ]);
    if (r.exceptionDetails) return null;
    return r.result.value;
  } catch {
    return null;
  }
};

// ---- 输入原语（全部走 CDP 原生事件，最接近真人）----
const mouseClick = async (x, y) => {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  await sleep(80);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
};

const pressKey = async (key, code, vk, modifiers = 0) => {
  await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key, code, windowsVirtualKeyCode: vk, modifiers });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode: vk, modifiers });
};

// 取元素几何信息（用 getBoundingClientRect，不要用 offsetParent）
const geoOf = async (selector) => {
  const raw = await evalJs(`(() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) return 'null';
    const r = el.getBoundingClientRect();
    return JSON.stringify({ x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height, len: (el.value || '').length });
  })()`);
  return !raw || raw === 'null' ? null : JSON.parse(raw);
};

// 找可见按钮（按文本正则），返回中心坐标
const buttonCenter = async (reSource) => {
  const raw = await evalJs(`(() => {
    const re = new RegExp(${JSON.stringify(reSource)});
    const btn = [...document.querySelectorAll('button, [role=button], input[type=submit]')].find((b) => {
      const r = b.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && re.test((b.innerText || b.value || '').trim());
    });
    if (!btn) return 'null';
    const r = btn.getBoundingClientRect();
    return JSON.stringify({ x: r.x + r.width/2, y: r.y + r.height/2, text: (btn.innerText || '').trim() });
  })()`);
  return !raw || raw === 'null' ? null : JSON.parse(raw);
};

// 坐标点击 → 全选清空 → 输入
const clickAndType = async (selector, text) => {
  const g = await geoOf(selector);
  if (!g || g.w === 0) return false;
  await mouseClick(g.x, g.y);
  await sleep(300);
  await pressKey('a', 'KeyA', 65, 2);
  await sleep(120);
  await pressKey('Backspace', 'Backspace', 8);
  await sleep(200);
  await send('Input.insertText', { text });
  await sleep(400);
  const after = await geoOf(selector);
  return !!after && after.len === text.length;
};

// ---- 关键：激活窗口，否则所有交互静默失效 ----
await send('Page.bringToFront');
await send('Emulation.setFocusEmulationEnabled', { enabled: true });
console.log('窗口已激活, hasFocus =', await evalJs('document.hasFocus()'));

// ---- 先导航到目标，看是否已登录 ----
await send('Page.navigate', { url: TARGET });
await sleep(6000);
let url = (await evalJs('location.href')) || '';
console.log('STEP0 url =', url);

// ---- 邮箱步骤 ----
const emailVisible = await evalJs(
  `(() => { const el = document.querySelector('#identifierId'); return !!el && el.getBoundingClientRect().width > 0; })()`
);
if (emailVisible) {
  console.log('→ 填写邮箱');
  console.log('  写入成功:', await clickAndType('#identifierId', EMAIL));
  const btn = await buttonCenter('^(下一步|Next)$');
  if (btn) {
    await mouseClick(btn.x, btn.y);
    console.log('  点击「' + btn.text + '」');
  } else {
    console.log('  ⚠ 未找到「下一步」按钮');
  }
  await sleep(7000);
}

// ---- 密码步骤 ----
url = (await evalJs('location.href')) || '';
const pwdStep = url.includes('challenge/pwd') || (await evalJs(`!!document.querySelector('input[name=Passwd]')`));
if (pwdStep) {
  console.log('→ 填写密码');
  await sleep(1500); // 等密码页渲染完成
  console.log('  写入成功:', await clickAndType('input[name=Passwd]', PWD));
  await sleep(600);
  const btn = await buttonCenter('^(下一步|Next)$');
  if (btn) {
    await mouseClick(btn.x, btn.y);
    console.log('  点击「' + btn.text + '」');
  } else {
    console.log('  ⚠ 未找到提交按钮，改用 Enter');
    await pressKey('Enter', 'Enter', 13);
  }
  await sleep(9000);
}

// ---- 结果 ----
url = (await evalJs('location.href')) || '';
const title = await evalJs('document.title');
const ok = !url.includes('accounts.google.com');
console.log(ok ? '✅ 登录成功' : '❌ 仍在登录页（可能需要 2FA 或人机验证）');
console.log('FINAL url =', url);
console.log('FINAL title =', title);

ws.close();
process.exit(ok ? 0 : 5);
