/**
 * fx_doctor.mjs — 纷享销客 CDP 方案环境诊断
 *
 * 一条命令查清「为什么跑不起来」，并给出可执行的修复建议。
 *
 * 用法：
 *   node fx_doctor.mjs            # 完整体检
 *   node fx_doctor.mjs --quick    # 只查 CDP + 登录态
 */
import {
  probeCdp, findCrmTarget, CdpSession, inspectPage, queryOne,
  normalize, checkNumber, CDP_BASE, API_PATH, ERR,
} from './fx_lib.mjs';

const QUICK = process.argv.includes('--quick');
const results = [];
function rec(name, ok, detail = '', fix = '') {
  results.push({ name, ok, detail, fix });
  const icon = ok === true ? '✅' : ok === false ? '❌' : '⚠️ ';
  console.log(`${icon} ${name}${detail ? ' — ' + detail : ''}`);
  if (!ok && fix) console.log(`     ↳ 修复：${fix}`);
}
console.log('═'.repeat(66));
console.log(' 纷享销客 CRM · CDP 环境诊断');
console.log('═'.repeat(66));
console.log('');

// ---- 1. Node 版本 ----
const major = Number(process.versions.node.split('.')[0]);
rec('Node 版本', major >= 20, `v${process.versions.node}（需 ≥20 才有内置 WebSocket）`,
  major < 20 ? '升级 Node 到 20+，或用托管 Node：C:\\Users\\Admin\\.workbuddy-ai\\binaries\\node\\versions\\22.22.2-3\\node.exe' : '');

// ---- 2. CDP 端口 ----
const cdp = await probeCdp();
if (!cdp.ok) {
  rec('CDP 端口 9222', false, cdp.error,
    'Chrome 未启动或未开调试端口。执行（后台常驻）：\n' +
    '       "C:/Program Files/Google/Chrome/Application/chrome.exe" \\\n' +
    '         --user-data-dir="C:/Users/Admin/.workbuddy-ai/browser-profiles/manual" \\\n' +
    '         --remote-debugging-port=9222 --no-first-run --no-default-browser-check \\\n' +
    '         "https://www.fxiaoke.com/XV/UI/Home"');
  console.log('');
  console.log('诊断中止：CDP 不通，后续检查无法进行。');
  process.exit(2);
}
rec('CDP 端口 9222', true, cdp.browser);

// ---- 3. CRM 标签页 ----
let target;
try {
  target = await findCrmTarget({ create: !QUICK });
  rec('CRM 标签页', true, target.url.slice(0, 80));
} catch (e) {
  rec('CRM 标签页', false, e.message, '手动在 Chrome 里打开 https://www.fxiaoke.com/XV/UI/Home 后重跑');
  process.exit(2);
}

// ---- 4. WebSocket 连接 ----
let session;
try {
  session = await CdpSession.connect(target);
  rec('CDP WebSocket', true);
} catch (e) {
  rec('CDP WebSocket', false, e.message, '关掉该标签页重开，或重启 Chrome');
  process.exit(2);
}

// ---- 5. 页面状态 ----
let pageInfo;
try {
  pageInfo = await inspectPage(session);
  const loggedIn = pageInfo.hasFsToken && !pageInfo.isLogin;
  rec('登录态', loggedIn,
    `fs_token=${pageInfo.hasFsToken ? '有' : '无'} | url=${pageInfo.url.slice(0, 60)}`,
    loggedIn ? '' : '登录已失效 → 切到 Chrome 窗口，用微信/账号扫码重新登录（登录期间不要动浏览器）');
  const visible = pageInfo.visibility === 'visible' && pageInfo.w > 0;
  rec('窗口可见性', visible ? true : null,
    `visibility=${pageInfo.visibility} outerWidth=${pageInfo.w}`,
    visible ? '' : '窗口被最小化/隐藏。**不影响接口调用**（见下方连通性检查）；如需窗口可见可执行 window.focus()');
  if (!loggedIn) {
    console.log('');
    console.log('诊断中止：未登录，无法验证接口。');
    session.close();
    process.exit(3);
  }
} catch (e) {
  rec('页面状态', false, e.message, '页面可能在导航，稍后重试');
}

if (QUICK) {
  session.close();
  summarize();
  process.exit(results.some(r => r.ok === false) ? 1 : 0);
}

// ---- 6. 接口连通性（探针）----
// 用已知存在的号码做探针：0122139000 → 应返回 1 条
const PROBE = '0122139000';
try {
  const r = await queryOne(session, PROBE);
  if (r.ok) {
    rec('接口连通性', true, `探针 ${PROBE} → 匹配 ${r.count} 条${r.name ? '（' + r.name + '）' : ''}`);
    if (r.count === 0) {
      rec('探针预期', false, '探针号码应有 1 条记录，但返回 0',
        '接口通了但数据异常。可能：该客户已被删除/改名，或查重规则变更');
    }
  } else {
    const meta = ERR[r.code] || ERR.E_UNKNOWN;
    rec('接口连通性', false, `${r.code} ${meta.msg}${r.detail ? ' | ' + r.detail : ''}`, meta.fix);
  }
} catch (e) {
  const meta = ERR[e.code] || ERR.E_UNKNOWN;
  rec('接口连通性', false, `${e.code} ${e.message}`, meta.fix || '');
}

// ---- 7. 号码归一化自检 ----
const cases = [
  ['0122339159', '0122339159'],
  ['122339159', '0122339159'],
  ['60122339159', '0122339159'],
  ['+60 12-233 9159', '0122339159'],
  ['', ''],
];
let normOk = true;
const normDetail = [];
for (const [inp, exp] of cases) {
  const got = normalize(inp);
  if (got !== exp) { normOk = false; normDetail.push(`${JSON.stringify(inp)}→${got}(期望${exp})`); }
}
rec('号码归一化自检', normOk, normOk ? `${cases.length} 个用例全部通过` : normDetail.join(', '),
  normOk ? '' : '归一化逻辑被改动过，检查 fx_lib.mjs 的 normalize()');

// ---- 8. 号码体检器自检 ----
const numChecks = [
  ['123159997', true], ['0123159997', true], ['', false], ['abc', false], ['12345', false],
];
let chkOk = true;
for (const [inp, exp] of numChecks) {
  const r = checkNumber(inp, normalize(inp));
  if (r.ok !== exp) { chkOk = false; console.log(`     号码体检异常: ${JSON.stringify(inp)} → ${r.ok} (期望 ${exp})`); }
}
rec('号码体检器自检', chkOk, chkOk ? `${numChecks.length} 个用例通过` : '见上方异常');

session.close();
summarize();
process.exit(results.some(r => r.ok === false) ? 1 : 0);

function summarize() {
  console.log('');
  console.log('─'.repeat(66));
  const bad = results.filter(r => r.ok === false);
  const warn = results.filter(r => r.ok === null);
  if (bad.length === 0) {
    console.log('✅ 全部通过，可以开始批量查询：');
    console.log('   node fx_phone_query.mjs --file numbers.txt --out result.csv');
  } else {
    console.log(`❌ ${bad.length} 项未通过：`);
    bad.forEach(b => console.log(`   · ${b.name}: ${b.detail}`));
    console.log('');
    console.log('   按上面的「修复」提示处理，或查阅 fx_errors.md 的故障对照表。');
  }
  if (warn.length) {
    console.log('');
    console.log(`⚠️  ${warn.length} 项警告（不影响功能）：`);
    warn.forEach(w => console.log(`   · ${w.name}: ${w.detail}`));
  }
  console.log('─'.repeat(66));
}
