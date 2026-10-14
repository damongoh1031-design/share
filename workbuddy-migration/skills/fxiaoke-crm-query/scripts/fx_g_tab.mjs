// fx_g_tab.mjs — 对授权标签本身开 Network 监听，捕获 127.0.0.1 回调请求
// 必须在点最后一次「继续」之前挂上，且标签必须保持打开。
const CDP = 'http://127.0.0.1:9222';
import fs from 'fs';
import { CdpSession } from './fx_lib.mjs';

const TMPD = process.env.TEMP || 'C:/Users/Admin/AppData/Local/Temp';
const REDIRECT_OUT = TMPD + '/gog_redirect_url.txt';
const EMAIL = process.argv[2] || 'jsng0819@gmail.com';

const findTab = async () => {
  const l = await (await fetch(CDP + '/json/list')).json();
  return l.filter(t => t.type === 'page' && /accounts\.google\.com|chrome-error/.test(t.url || '')).pop();
};

// 1) 找到当前授权标签
let tgt = await findTab();
if (!tgt) { console.log('NO_AUTH_TAB'); process.exit(1); }
console.log('目标标签:', tgt.id, '|', (tgt.url || '').slice(0, 80));

// 2) 在标签上开 Network 监听（记录所有请求 URL）
const rec = [];
const ws = new WebSocket(tgt.webSocketDebuggerUrl);
ws.onmessage = (ev) => {
  try {
    const m = JSON.parse(ev.data);
    if (m.method === 'Network.requestWillBeSent') {
      const u = m.params?.request?.url || '';
      rec.push(u);
      if (/127\.0\.0\.1:\d+\/oauth2\/callback/.test(u) && u.includes('code=')) {
        fs.writeFileSync(REDIRECT_OUT, u, 'utf8');
        console.log('🎯 捕获: ' + u.slice(0, 120));
      }
    }
    if (m.method === 'Page.frameRequestedNavigation') {
      const u = m.params?.url || '';
      if (/127\.0\.0\.1:\d+\/oauth2\/callback/.test(u) && u.includes('code=')) {
        fs.writeFileSync(REDIRECT_OUT, u, 'utf8');
        console.log('🎯 frameRequested: ' + u.slice(0, 120));
      }
    }
  } catch {}
};
await new Promise((res) => {
  ws.onopen = () => {
    ws.send(JSON.stringify({ id: 1, method: 'Network.enable' }));
    ws.send(JSON.stringify({ id: 2, method: 'Page.enable' }));
    setTimeout(res, 700);
  };
  ws.onerror = () => res();
  setTimeout(res, 3000);
}, 0);
console.log('网络监听已挂载');

// 3) 驱动页面（每步用新会话，WS 事件流保持在 ws 上）
const s0 = await CdpSession.connect(tgt);
for (let i = 1; i <= 18; i++) {
  await new Promise(r => setTimeout(r, 2200));
  if (fs.existsSync(REDIRECT_OUT)) break;

  let url = '';
  try { url = String(await s0.evaluate('location.href')); } catch { /* 导航中会短暂失败 */ }
  console.log('[' + i + '] ' + url.slice(0, 95));
  if (/chrome-error|127\.0\.0\.1/.test(url)) continue;

  try {
    if (/accountchooser/.test(url)) {
      const r = await s0.evaluate(`(() => {
        const all=[...document.querySelectorAll('div[data-identifier],li,div[role=link],div[role=button]')];
        const hit=all.find(e=>(e.getAttribute('data-identifier')||'').toLowerCase()===${JSON.stringify(EMAIL.toLowerCase())})
               || all.find(e=>(e.innerText||'').includes(${JSON.stringify(EMAIL)}));
        if(!hit) return 'NOT_FOUND'; hit.click(); return 'PICKED';
      })()`);
      console.log('   → 选账号 ' + r);
    } else if (/consent|signin\/oauth/.test(url)) {
      const r = await s0.evaluate(`(() => {
        const want=['继续','允许','同意','Allow','Continue'];
        const all=[...document.querySelectorAll('button,div[role=button],span[role=button]')].filter(e=>e.offsetHeight>0&&!e.disabled);
        for(const w of want){
          const hit=all.find(e=>{const t=(e.innerText||e.textContent||'').trim();return t===w||t.startsWith(w);});
          if(hit){hit.click();return 'CLICKED:'+((hit.innerText||'').trim().slice(0,18));}
        }
        return 'NO_BTN';
      })()`);
      console.log('   → ' + r);
    }
  } catch (e) { console.log('   → ERR ' + String(e.message).slice(0, 60)); }
}

// 4) 若仍未捕获，尝试从记录的 URL 里找
if (!fs.existsSync(REDIRECT_OUT)) {
  const hit = rec.find(u => /127\.0\.0\.1:\d+\/oauth2\/callback/.test(u));
  if (hit) { fs.writeFileSync(REDIRECT_OUT, hit, 'utf8'); console.log('🎯 从记录中找到: ' + hit.slice(0, 120)); }
}

console.log('\n捕获的 127.0.0.1 请求: ' + rec.filter(u => /127\.0\.0\.1/.test(u)).length);
rec.filter(u => /127\.0\.0\.1/.test(u)).slice(0, 3).forEach(u => console.log('  ' + u.slice(0, 150)));

try { ws.close(); } catch {}
s0.close();

console.log(fs.existsSync(REDIRECT_OUT) ? '\n✅ 回调 URL 已保存' : '\n⚠️ 未捕获');
process.exit(0);
