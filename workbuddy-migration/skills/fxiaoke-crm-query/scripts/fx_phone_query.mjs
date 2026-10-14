/**
 * fx_phone_query.mjs — 纷享销客 CRM 手机号批量查重（生产级）
 *
 * 特性：
 *   · 断点续跑    —— 中断后加 --resume 从上次位置继续
 *   · 自适应限流  —— 成功则提速，遇 429/5xx 指数退避
 *   · 错误隔离    —— 单号失败不中断整批；鉴权/风控类错误立即停并给出修复指引
 *   · 自动重连    —— WebSocket 断开自动重连
 *   · 优雅中断    —— Ctrl+C 保存进度后退出
 *   · 登录预检    —— 开跑前先验登录态，避免整批白跑
 *
 * 用法：
 *   node fx_phone_query.mjs 0122139000 0123159997
 *   node fx_phone_query.mjs --file numbers.txt --out result.csv
 *   node fx_phone_query.mjs --file numbers.txt --out result.csv --resume
 *   node fx_phone_query.mjs --file numbers.txt --delay 500 --retries 5
 *   node fx_phone_query.mjs --no-normalize 122891188
 *   node fx_phone_query.mjs --file numbers.txt --dry-run      # 只体检号码，不发请求
 *
 * 输出 CSV：输入号码,查询号码,匹配数,客户名称,客户编号
 */
import fs from 'fs';
import {
  findCrmTarget, CdpSession, preflight, queryWithRetry,
  normalize, checkNumber, sleep, ERR,
  writeCsv, loadProgress, saveProgress, clearProgress,
} from './fx_lib.mjs';

// ============ 参数解析 ============
const argv = process.argv.slice(2);
function flag(name, def = null) {
  const i = argv.indexOf(name);
  if (i === -1) return def;
  const v = argv[i + 1];
  return (v && !v.startsWith('--')) ? v : true;
}
const FILE = flag('--file');
const OUT = flag('--out') || 'fx_result.csv';
const DELAY = Number(flag('--delay', 300));
const MAX_DELAY = Number(flag('--max-delay', 8000));
const RETRIES = Number(flag('--retries', 3));
const RESUME = argv.includes('--resume');
const NO_NORM = argv.includes('--no-normalize');
const DRY = argv.includes('--dry-run');
const QUIET = argv.includes('--quiet');

function log(...a) { if (!QUIET) console.log(...a); }
function elog(...a) { console.error(...a); }

// ============ 读号码 ============
const VALUE_FLAGS = ['--file', '--out', '--delay', '--max-delay', '--retries'];
function readNumbers() {
  if (FILE) {
    if (!fs.existsSync(FILE)) { elog(`❌ 文件不存在: ${FILE}`); process.exit(1); }
    return fs.readFileSync(FILE, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  }
  const out = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (VALUE_FLAGS.includes(a)) { i++; continue; }   // 跳过 flag 及其取值
    if (a.startsWith('--')) continue;                 // 跳过布尔 flag
    if (/^[+\d][\d\s\-+()]*$/.test(a)) out.push(a);   // 只收看起来像号码的
  }
  return out;
}

let numbers = readNumbers();
if (!numbers.length) {
  elog('用法: node fx_phone_query.mjs <号码...>');
  elog('      node fx_phone_query.mjs --file numbers.txt --out result.csv [--resume] [--delay 300]');
  process.exit(1);
}

// ============ 号码体检 ============
const prepared = numbers.map((raw, idx) => {
  const norm = normalize(raw, NO_NORM);
  const chk = checkNumber(raw, norm);
  return { idx, raw, norm, ok: chk.ok, reason: chk.reason };
});
const badOnes = prepared.filter(p => !p.ok);
if (badOnes.length) {
  log(`⚠️  ${badOnes.length} 个号码格式可疑（会被跳过并记录原因）：`);
  badOnes.slice(0, 8).forEach(b => log(`     #${b.idx + 1} ${JSON.stringify(b.raw)} → ${b.norm || '(空)'} [${b.reason}]`));
  if (badOnes.length > 8) log(`     ... 另有 ${badOnes.length - 8} 个`);
  log('');
}

if (DRY) {
  log('--dry-run 模式：仅体检，不发起请求。');
  log(`共 ${numbers.length} 个号码，可查询 ${prepared.filter(p => p.ok).length} 个，异常 ${badOnes.length} 个。`);
  process.exit(0);
}

// ============ 进度恢复 ============
let done = {};      // idx -> 结果对象
let startIdx = 0;
if (RESUME) {
  const p = loadProgress(OUT);
  if (p && p.done) {
    done = p.done;
    startIdx = p.next || 0;
    log(`↻ 断点续跑：已完成 ${Object.keys(done).length} 条，从第 ${startIdx + 1} 条继续。`);
  } else {
    log('↻ 未找到进度文件，从头开始。');
  }
}

// ============ 连接 + 预检 ============
let session = null;
let target = null;
async function ensureSession({ force = false } = {}) {
  if (session && session.alive && !force) return session;
  if (session) session.close();
  target = await findCrmTarget({ create: true });
  session = await CdpSession.connect(target);
  session.onClose = () => { log('   ⚠️ CDP 连接断开，将在下次查询前自动重连'); };
  return session;
}

log('═'.repeat(64));
log(' 纷享销客 CRM · 批量查重');
log('═'.repeat(64));
log(` 号码总数 : ${numbers.length}`);
log(` 输出文件 : ${OUT}`);
log(` 间隔     : ${DELAY}ms（自适应上限 ${MAX_DELAY}ms）  重试: ${RETRIES}`);
log('─'.repeat(64));

try {
  await ensureSession();
  const pf = await preflight(session);
  if (!pf.ok) {
    const meta = ERR[pf.code] || ERR.E_UNKNOWN;
    elog(`❌ 登录预检失败：${pf.code} — ${meta.msg}`);
    elog(`   修复：${meta.fix}`);
    elog('   提示：可先跑 `node fx_doctor.mjs` 做完整诊断。');
    process.exit(3);
  }
  log(`✅ 登录态正常（${pf.info.url.slice(0, 60)}）`);
} catch (e) {
  elog(`❌ 无法建立连接：${e.message}`);
  elog(`   修复：${e.fix || '先跑 node fx_doctor.mjs 诊断'}`);
  process.exit(2);
}

// ============ 主循环 ============
let delay = DELAY;
let okCount = 0, missCount = 0, errCount = 0, skipCount = 0;
const t0 = Date.now();
let interrupted = false;

process.on('SIGINT', () => {
  interrupted = true;
  elog('\n⏸  收到中断信号，正在保存进度…');
});

function flush() {
  const rows = [['输入号码', '查询号码', '匹配数', '客户名称', '客户编号']];
  for (const p of prepared) {
    const d = done[p.idx];
    if (!d) continue;
    if (d.skip) rows.push([p.raw, p.norm, 'SKIP', '', d.reason || '']);
    else if (d.err) rows.push([p.raw, p.norm, 'ERROR', '', `${d.code} ${d.detail || ''}`.trim()]);
    else rows.push([p.raw, p.norm, d.count > 0 ? d.count : '无数据', d.name || '', d.account_no || '']);
  }
  writeCsv(OUT, rows);
  return rows.length - 1;
}

for (let i = startIdx; i < prepared.length; i++) {
  if (interrupted) break;
  const p = prepared[i];

  // 格式可疑 → 跳过
  if (!p.ok) {
    done[p.idx] = { skip: true, reason: p.reason };
    skipCount++;
    continue;
  }

  let r;
  try {
    r = await queryWithRetry(session, p.norm, {
      retries: RETRIES,
      baseDelay: 500,
      onRetry: (n, code, d) => log(`   ↻ 重试 #${n}（${code}），等待 ${d}ms…`),
    });
  } catch (e) {
    // auth / risk 类：立即停止整批
    if (e.kind === 'auth' || e.kind === 'risk') {
      done[p.idx] = { err: true, code: e.code, detail: e.detail || '' };
      flush(); saveProgress(OUT, { done, next: i });
      elog('');
      elog(`🛑 遇到 ${e.kind === 'auth' ? '登录失效' : '风控拦截'}：${e.code}`);
      elog(`   ${(ERR[e.code] || {}).msg || e.message}`);
      elog(`   修复：${(ERR[e.code] || {}).fix || ''}`);
      elog(`   进度已保存（${Object.keys(done).length}/${prepared.length}），处理后可加 --resume 继续。`);
      process.exit(4);
    }
    // 环境类：尝试重连一次
    log(`   ⚠️ ${e.code}，尝试重连…`);
    try {
      await ensureSession({ force: true });
      r = await queryWithRetry(session, p.norm, { retries: 1, baseDelay: 800 });
    } catch (e2) {
      r = { ok: false, code: e2.code || 'E_UNKNOWN', detail: e2.message };
    }
  }

  if (!r || r.ok === false) {
    const code = r?.code || 'E_UNKNOWN';
    done[p.idx] = { err: true, code, detail: r?.detail || '' };
    errCount++;
    delay = Math.min(Math.round(delay * 1.5), MAX_DELAY);   // 出错后退避
    log(`   ⚠️ #${i + 1} ${p.norm} → ${code}${r?.detail ? ' (' + r.detail + ')' : ''}`);
  } else if (r.count > 0) {
    done[p.idx] = { count: r.count, name: r.name, account_no: r.account_no };
    okCount++;
    delay = Math.max(DELAY, Math.round(delay * 0.8));        // 成功则提速
  } else {
    done[p.idx] = { count: 0 };
    missCount++;
    delay = Math.max(DELAY, Math.round(delay * 0.9));
  }

  // 进度输出
  const total = i + 1;
  if (total % 20 === 0 || total === prepared.length) {
    const el = ((Date.now() - t0) / 1000).toFixed(0);
    const rate = total > startIdx ? ((total - startIdx) / Math.max(el, 1)).toFixed(1) : '0';
    log(`   [${total}/${prepared.length}] 命中 ${okCount} · 无数据 ${missCount} · 错误 ${errCount} · 跳过 ${skipCount} | ${el}s (${rate}/s, 间隔 ${delay}ms)`);
    flush();
    saveProgress(OUT, { done, next: total });
  }

  if (i < prepared.length - 1) await sleep(delay);
}

// ============ 收尾 ============
const written = flush();
if (interrupted) {
  saveProgress(OUT, { done, next: Object.keys(done).length });
  log('');
  log(`⏸  已中断。进度已保存：${written} 条写入 ${OUT}`);
  log(`   继续：node fx_phone_query.mjs --file ${FILE || '<号码>'} --out ${OUT} --resume`);
} else {
  clearProgress(OUT);
  log('');
  log('─'.repeat(64));
  log(`✅ 完成  命中 ${okCount} · 无数据 ${missCount} · 错误 ${errCount} · 跳过 ${skipCount}`);
  log(`   共 ${written} 条 → ${OUT}   耗时 ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  log('─'.repeat(64));
}
if (session) session.close();
process.exit(errCount > 0 ? 1 : 0);
