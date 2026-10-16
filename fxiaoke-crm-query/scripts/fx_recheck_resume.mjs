// fx_recheck_resume.mjs — 对号码取「全量匹配」，按客户级别（PJ1/PJ2）分类
// 【增强版】支持断点续跑 + CDP 断线自动重连
//
// 用法:
//   node fx_recheck_resume.mjs --file tel.txt --out levels.csv [--delay 150] [--chunk 20]
//   中断后重跑同一条命令即可自动续跑（进度落盘在同目录 <out>.progress.json）
//
// 相对 fx_recheck.mjs 的改进：
//   1. 每处理 --chunk 条就把已完成的号码落盘 → 崩溃后可续跑，不丢进度
//   2. 捕获 E_WS_CLOSED / E_CTX_DESTROYED / E_WS_TIMEOUT → 退避后重连并重试当前号码
//   3. 输出实时追加写入（--out 始终有可用内容）
import fs from 'fs';
import path from 'path';
import { findCrmTarget, CdpSession, preflight, probeCdp, mkErr, sleep } from './fx_lib.mjs';

const LEVEL = { '1': 'PJ 1', 'V0QhX94z4': 'PJ 2', 'z8qM9c51e': 'FB PJ 1', 'DQx161x0t': 'FB PJ 2', 'Q3ZFSjTtd': 'JOHOR', other: '其他' };

const argv = process.argv.slice(2);
const getArg = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const FILE = getArg('--file');
const OUT = getArg('--out', 'recheck.csv');
const DELAY = parseInt(getArg('--delay', '150'), 10);
const CHUNK = parseInt(getArg('--chunk', '20'), 10);
if (!FILE) { console.error('缺 --file'); process.exit(2); }

const PROG = OUT + '.progress.json';
const HEAD = ['号码', '记录数', '级别列表', 'PJ2名称', 'PJ1名称', '其他级别名称', '全部名称'];

const tels = fs.readFileSync(FILE, 'utf8').split(/\r?\n/).map(x => x.trim()).filter(Boolean);
console.log('待重查: %d 个', tels.length);

// ---- 载入进度 ----
let doneMap = {};                       // tel -> row(array)
if (fs.existsSync(PROG)) {
  try {
    doneMap = JSON.parse(fs.readFileSync(PROG, 'utf8'));
    console.log('续跑: 已完成 %d 个，剩余 %d 个', Object.keys(doneMap).length, tels.filter(t => !(t in doneMap)).length);
  } catch { doneMap = {}; }
}

const csvCell = (c) => { const s = String(c ?? ''); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
function flush() {
  fs.writeFileSync(PROG, JSON.stringify(doneMap), 'utf8');
  const rows = [HEAD, ...tels.map(t => doneMap[t]).filter(Boolean)];
  fs.writeFileSync(OUT, '\uFEFF' + rows.map(r => r.map(csvCell).join(',')).join('\n'), 'utf8');
}

// ---- 建连（带重试）----
let target = null, session = null;
async function connect(retries = 5) {
  for (let i = 1; i <= retries; i++) {
    try {
      const p = await probeCdp();
      if (!p.ok) throw mkErr('E_CDP_UNREACHABLE');
      target = await findCrmTarget({ create: true });
      session = await CdpSession.connect(target);
      const pf = await preflight(session);
      if (!pf.ok) { console.error('登录态失效:', pf.code); process.exit(3); }
      console.log('CDP 已连接（第 %d 次尝试）', i);
      return;
    } catch (e) {
      console.warn('连接失败(%d/%d): %s', i, retries, e.message);
      await sleep(2000 * i);
    }
  }
  throw new Error('CDP 连接彻底失败');
}

await connect();

// ---- 单条查询 ----
async function queryOne(tel) {
  const raw = await session.evaluate(`(async () => {
    try {
      const fsToken = (document.cookie.match(/(?:^|;\\s*)fs_token=([^;]+)/) || [])[1];
      if (!fsToken) return JSON.stringify({ __err: 'E_NO_FS_TOKEN' });
      const url = 'https://www.fxiaoke.com/FHH/EM1HNCRM/API/v1/object/AccountObj/controller/DuplicateSearch?_fs_token=' + fsToken;
      const body = {
        describe_api_name: 'AccountObj', type: 'TOOL',
        object_data: { object_describe_api_name: 'AccountObj', tel: ${JSON.stringify(tel)}, duplicate_rule_api_name: 'rule_rnhS3__c' },
        include_object_describes: false, is_need_duplicate: true,
        page_size: 50, page_number: 1,
        duplicate_rule_api_name: 'rule_rnhS3__c',
        describeVersionMap: { AccountObj: 150 }
      };
      const r = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include', body: JSON.stringify(body) });
      const j = await r.json();
      if (j?.Result?.FailureCode) return JSON.stringify({ __err: 'API_' + j.Result.FailureCode });
      const dl = j?.Value?.data_list || [];
      return JSON.stringify(dl.map(x => ({ n: x.name, t: x.account_type, no: x.account_no })));
    } catch (e) { return JSON.stringify({ __err: String(e) }); }
  })()`, 60000);

  let list;
  try { list = JSON.parse(raw); } catch { list = { __err: 'PARSE' }; }
  if (list && list.__err) {
    if (list.__err === 'E_NO_FS_TOKEN') throw mkErr('E_NO_FS_TOKEN');
    return { row: [tel, 'ERROR', '', '', '', '', list.__err], err: list.__err };
  }
  const names = list.map(x => x.n || '');
  const pj2 = list.filter(x => x.t === 'V0QhX94z4').map(x => x.n).filter(Boolean);
  const pj1 = list.filter(x => x.t === '1').map(x => x.n).filter(Boolean);
  const other = list.filter(x => !['V0QhX94z4', '1'].includes(x.t)).map(x => (LEVEL[x.t] || x.t) + ':' + (x.n || '')).filter(Boolean);
  const levels = list.map(x => LEVEL[x.t] || x.t).join('|');
  return { row: [tel, String(list.length), levels, pj2.join(';'), pj1.join(';'), other.join(';'), names.join(';')], err: null };
}

// ---- 主循环（含重连）----
let pending = tels.filter(t => !(t in doneMap));
console.log('本轮需处理: %d 个', pending.length);

let processed = 0, errs = 0, reconnects = 0;
for (let i = 0; i < pending.length; i++) {
  const tel = pending[i];
  let ok = false;
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const { row, err } = await queryOne(tel);
      doneMap[tel] = row;
      if (err) errs++;
      processed++; ok = true;
      break;
    } catch (e) {
      const kind = e.kind || 'unknown';
      if (kind === 'auth') { console.error('登录态失效，停止:', e.message); flush(); process.exit(3); }
      if (['env', 'net', 'unknown'].includes(kind) && attempt < 4) {
        console.warn('  [%s] 第%d次失败(%s)，重连后重试…', tel, attempt, e.code || e.message);
        reconnects++;
        try { session && session.close(); } catch {}
        await sleep(1500 * attempt);
        await connect(3);
        continue;
      }
      console.warn('  [%s] 放弃: %s', tel, e.message);
    }
  }
  if (!ok) { doneMap[tel] = [tel, 'ERROR', '', '', '', '', 'GIVEUP']; errs++; }

  if ((i + 1) % CHUNK === 0 || i === pending.length - 1) {
    flush();
    const totalDone = Object.keys(doneMap).length;
    console.log('  [%d/%d] 累计完成 %d/%d  错误 %d  重连 %d', i + 1, pending.length, totalDone, tels.length, errs, reconnects);
  }
  await sleep(DELAY);
}

flush();
const body = tels.map(t => doneMap[t]).filter(Boolean);
const hasPj2 = body.filter(r => r[3]);
const noPj2HasPj1 = body.filter(r => !r[3] && r[4]);
const noPj2NoPj1 = body.filter(r => !r[3] && !r[4] && r[2] !== 'ERROR');
console.log('\n===== 分类结果 =====');
console.log('总重查      : %d', body.length);
console.log('有 PJ2      : %d  <== 用户要的', hasPj2.length);
console.log('无PJ2 有PJ1 : %d', noPj2HasPj1.length);
console.log('无PJ2 无PJ1 : %d', noPj2NoPj1.length);
console.log('错误        : %d', errs);
console.log('重连次数    : %d', reconnects);
console.log('明细: %s', OUT);
process.exit(0);
