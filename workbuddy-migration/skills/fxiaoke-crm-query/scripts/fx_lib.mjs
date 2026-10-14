/**
 * fx_lib.mjs — 纷享销客 CRM CDP 查询共享库
 *
 * 职责：CDP 连接管理、登录态探测、接口调用、号码归一化、错误分类、退避重试。
 * 被 fx_doctor.mjs / fx_phone_query.mjs 复用。
 */
import fs from 'fs';

// ============ 租户常量（本企业固定，勿改）============
export const CDP_BASE = process.env.CDP_URL || 'http://127.0.0.1:9222';
export const OBJECT = 'AccountObj';
export const RULE = 'rule_rnhS3__c';
export const DESCRIBE_VERSION = 150;
export const API_PATH = `/FHH/EM1HNCRM/API/v1/object/${OBJECT}/controller/DuplicateSearch`;
export const CRM_HOST = 'https://www.fxiaoke.com';
export const CRM_TARGET_HINT = '/XV/UI/Home';

// ============ 错误码字典 ============
/**
 * kind:
 *   env    — 环境问题（浏览器/端口/标签页），需人工或自动修复后重试
 *   auth   — 登录态失效，必须人工重新登录，重试无意义
 *   risk   — 触发风控，必须暂停并人工介入
 *   net    — 网络/瞬时故障，可自动重试
 *   data   — 数据问题（号码格式等），跳过该条
 *   ok     — 正常
 */
export const ERR = {
  E_CDP_UNREACHABLE: { kind: 'env', msg: '连不上 CDP 端口 9222', fix: 'Chrome 未启动或未开调试端口 → 用启动命令重启（见 fx_errors.md §1）' },
  E_NO_TARGET: { kind: 'env', msg: '找不到 CRM 标签页', fix: 'CRM 标签页被关了 → 脚本会自动新建；若失败请手动打开 CRM 页面' },
  E_TARGET_NAVIGATING: { kind: 'env', msg: '标签页正在导航', fix: '等页面加载完重试' },
  E_WS_CLOSED: { kind: 'env', msg: 'CDP WebSocket 已断开', fix: '标签页关闭或 Chrome 崩溃 → 脚本会自动重连' },
  E_WS_TIMEOUT: { kind: 'net', msg: 'CDP 命令超时', fix: '页面卡住 → 自动重试' },
  E_CTX_DESTROYED: { kind: 'net', msg: '页面执行上下文失效', fix: '页面导航导致 → 自动重试' },

  E_NO_FS_TOKEN: { kind: 'auth', msg: 'cookie 里没有 fs_token', fix: '登录态失效 → 回到 Chrome 窗口重新扫码登录' },
  E_REDIRECTED: { kind: 'auth', msg: '请求被重定向到登录页', fix: '登录态失效 → 重新扫码登录' },
  E_HTTP_401: { kind: 'auth', msg: 'HTTP 401 未授权', fix: '会话过期 → 重新扫码登录' },
  E_HTTP_403: { kind: 'auth', msg: 'HTTP 403 无权限', fix: '账号权限变更或会话失效 → 联系管理员/重新登录' },
  E_HTTP_429: { kind: 'net', msg: 'HTTP 429 请求过频', fix: '触发限流 → 脚本自动指数退避，可调大 --delay' },
  E_HTTP_5XX: { kind: 'net', msg: '服务端 5xx', fix: '纷享服务端瞬时故障 → 自动重试' },
  E_RISK_HTML: { kind: 'risk', msg: '返回 HTML 而非 JSON（疑似风控验证页）', fix: '停止批量，回浏览器窗口手动通过验证后再跑' },
  E_BAD_JSON: { kind: 'net', msg: '响应不是合法 JSON', fix: '页面导航中或网关异常 → 自动重试' },
  E_FETCH: { kind: 'net', msg: '页面内 fetch 抛错', fix: '网络抖动 → 自动重试' },
  E_API_ERROR: { kind: 'env', msg: '接口返回业务错误码', fix: '看 errorCode/errorMessage 明细' },
  E_UNKNOWN: { kind: 'net', msg: '未知错误', fix: '重试；持续失败请看 fx_errors.md' },
};

// ============ 号码归一化 ============
export function normalize(tel, noNorm = false) {
  let t = String(tel ?? '').replace(/\D/g, '');
  if (noNorm) return t;
  if (!t) return t;
  if (/^6\d+$/.test(t)) t = t.slice(1);                       // ① 以 6 开头（国家码 60）→ 删掉最前面的 6
  if (!t.startsWith('0') && /^\d{9}$/.test(t)) t = '0' + t;   // ② 9 位且非 0 开头 → 补前导 0
  if (!t.startsWith('0')) t = '0' + t;                        // ③ 兜底：必须以 0 开头
  return t;
}

/** 号码体检：返回 {ok, reason} */
export function checkNumber(raw, norm) {
  if (!String(raw ?? '').trim()) return { ok: false, reason: '空值' };
  if (!norm) return { ok: false, reason: '无有效数字' };
  if (norm.length < 9) return { ok: false, reason: `过短(${norm.length}位)` };
  if (norm.length > 12) return { ok: false, reason: `过长(${norm.length}位)` };
  if (!norm.startsWith('01')) return { ok: false, reason: '非 01 开头' };
  return { ok: true };
}

export const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// ============ CDP 连接 ============
async function fetchJson(url, timeoutMs = 5000) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    const r = await fetch(url, { signal: ac.signal });
    return await r.json();
  } finally {
    clearTimeout(t);
  }
}

/** 探测 CDP 端口是否活着 */
export async function probeCdp() {
  try {
    const v = await fetchJson(CDP_BASE + '/json/version', 4000);
    return { ok: true, browser: v.Browser || 'unknown', ws: v.webSocketDebuggerUrl || '' };
  } catch (e) {
    return { ok: false, error: String(e?.message || e) };
  }
}

/** 找到（或新建）CRM 标签页 */
export async function findCrmTarget({ create = true } = {}) {
  let list;
  try {
    list = await fetchJson(CDP_BASE + '/json/list', 5000);
  } catch (e) {
    throw mkErr('E_CDP_UNREACHABLE', String(e?.message || e));
  }
  const pages = list.filter(t => t.type === 'page');
  let target = pages.find(p => p.url && p.url.includes(CRM_TARGET_HINT))
    || pages.find(p => p.url && p.url.includes('fxiaoke.com'));

  if (!target && create) {
    // 新建标签页并导航到 CRM（登录态在 cookie 里，通常无需重登）
    try {
      const r = await fetch(`${CDP_BASE}/json/new?${encodeURIComponent(CRM_HOST + '/XV/UI/Home')}`, { method: 'PUT' });
      target = await r.json();
      await sleep(3500); // 等 SPA 起来
    } catch (e) {
      throw mkErr('E_NO_TARGET', String(e?.message || e));
    }
  }
  if (!target) throw mkErr('E_NO_TARGET');
  return target;
}

export function mkErr(code, detail = '') {
  const meta = ERR[code] || ERR.E_UNKNOWN;
  const e = new Error(`${code}: ${meta.msg}${detail ? ' | ' + detail : ''}`);
  e.code = code;
  e.kind = meta.kind;
  e.fix = meta.fix;
  return e;
}

// ============ CDP 会话 ============
export class CdpSession {
  constructor(target) {
    this.target = target;
    this.ws = null;
    this._id = 0;
    this._pending = new Map();
    this._closed = false;
    this.onClose = null;
  }

  static async connect(target) {
    const s = new CdpSession(target);
    await s._open();
    return s;
  }

  _open() {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.target.webSocketDebuggerUrl);
      this.ws = ws;
      const timer = setTimeout(() => { try { ws.close(); } catch {} reject(mkErr('E_WS_TIMEOUT', '连接超时')); }, 8000);
      ws.addEventListener('open', () => { clearTimeout(timer); resolve(); });
      ws.addEventListener('error', (e) => { clearTimeout(timer); reject(mkErr('E_WS_CLOSED', String(e?.message || 'ws error'))); });
      ws.addEventListener('message', (ev) => {
        let d; try { d = JSON.parse(ev.data); } catch { return; }
        if (d.id && this._pending.has(d.id)) {
          const { resolve, reject, timer } = this._pending.get(d.id);
          this._pending.delete(d.id);
          clearTimeout(timer);
          if (d.error) reject(mkErr('E_WS_CLOSED', JSON.stringify(d.error)));
          else resolve(d.result);
        }
      });
      ws.addEventListener('close', () => {
        this._closed = true;
        for (const [, p] of this._pending) { clearTimeout(p.timer); p.reject(mkErr('E_WS_CLOSED')); }
        this._pending.clear();
        if (this.onClose) this.onClose();
      });
    });
  }

  get alive() { return this.ws && this.ws.readyState === 1 && !this._closed; }

  send(method, params = {}, timeoutMs = 30000) {
    if (!this.alive) return Promise.reject(mkErr('E_WS_CLOSED'));
    return new Promise((resolve, reject) => {
      const id = ++this._id;
      const timer = setTimeout(() => {
        this._pending.delete(id);
        reject(mkErr('E_WS_TIMEOUT', method));
      }, timeoutMs);
      this._pending.set(id, { resolve, reject, timer });
      try { this.ws.send(JSON.stringify({ id, method, params })); }
      catch (e) { clearTimeout(timer); this._pending.delete(id); reject(mkErr('E_WS_CLOSED', String(e))); }
    });
  }

  /** 在页面上下文求值，自动识别常见错误 */
  async evaluate(expression, timeoutMs = 30000) {
    let res;
    try {
      res = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, timeoutMs);
    } catch (e) {
      if (/context|Execution context/i.test(String(e.message))) throw mkErr('E_CTX_DESTROYED');
      throw e;
    }
    if (res?.exceptionDetails) {
      const txt = res.exceptionDetails.exception?.description || res.exceptionDetails.text || 'eval error';
      if (/context|destroyed|navigat/i.test(txt)) throw mkErr('E_CTX_DESTROYED', txt);
      throw mkErr('E_UNKNOWN', txt);
    }
    return res?.result?.value;
  }

  close() { try { this.ws && this.ws.close(); } catch {} }
}

// ============ 登录态 / 页面状态探测 ============
export async function inspectPage(session) {
  return session.evaluate(`(() => {
    const hasFsToken = /(^|;\\s*)fs_token=/.test(document.cookie);
    const url = location.href;
    const isLogin = /login/i.test(url);
    const title = document.title;
    return { url, title, hasFsToken, isLogin, visibility: document.visibilityState,
             w: window.outerWidth, innerW: window.innerWidth };
  })()`);
}

/** 登录态预检：返回 {ok, reason, detail} */
export async function preflight(session) {
  const info = await inspectPage(session);
  if (info.isLogin) return { ok: false, code: 'E_REDIRECTED', info };
  if (!info.hasFsToken) return { ok: false, code: 'E_NO_FS_TOKEN', info };
  return { ok: true, info };
}

// ============ 单号查询 ============
/**
 * 在页面上下文调用 DuplicateSearch。
 * 返回 {ok, count, name, account_no, tel} 或 {ok:false, code, detail}
 */
export async function queryOne(session, tel, timeoutMs = 30000) {
  const expr = `(async () => {
    try {
      const fsToken = (document.cookie.match(/(?:^|;\\s*)fs_token=([^;]+)/) || [])[1];
      if (!fsToken) return { __err: 'E_NO_FS_TOKEN' };
      const url = ${JSON.stringify(CRM_HOST + API_PATH)} + '?_fs_token=' + fsToken;
      const body = {
        describe_api_name: ${JSON.stringify(OBJECT)},
        type: 'TOOL',
        object_data: { object_describe_api_name: ${JSON.stringify(OBJECT)}, tel: ${JSON.stringify(tel)}, duplicate_rule_api_name: ${JSON.stringify(RULE)} },
        include_object_describes: true,
        is_need_duplicate: true,
        page_size: 1,
        page_number: 1,
        duplicate_rule_api_name: ${JSON.stringify(RULE)},
        describeVersionMap: { ${JSON.stringify(OBJECT)}: ${DESCRIBE_VERSION} }
      };
      const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), credentials: 'include' });
      if (r.status === 401) return { __err: 'E_HTTP_401' };
      if (r.status === 403) return { __err: 'E_HTTP_403' };
      if (r.status === 429) return { __err: 'E_HTTP_429' };
      if (r.status >= 500) return { __err: 'E_HTTP_5XX', __detail: String(r.status) };
      if (r.redirected || /\\/login/i.test(r.url)) return { __err: 'E_REDIRECTED' };
      const text = await r.text();
      const head = text.slice(0, 60).trim().toLowerCase();
      if (head.startsWith('<')) return { __err: 'E_RISK_HTML', __detail: text.slice(0, 120) };
      let j; try { j = JSON.parse(text); } catch (e) { return { __err: 'E_BAD_JSON', __detail: text.slice(0, 120) }; }
      if (j.errorCode && j.errorCode !== 0) return { __err: 'E_API_ERROR', __detail: j.errorCode + ' ' + (j.errorMessage || '') };
      const list = (j.Value && j.Value.data_list) ? j.Value.data_list : [];
      const d = list[0] || {};
      return { count: list.length, name: d.name || '', account_no: d.account_no || '', tel: d.tel || '' };
    } catch (e) {
      return { __err: 'E_FETCH', __detail: String(e && e.message || e) };
    }
  })()`;

  const raw = await session.evaluate(expr, timeoutMs);
  if (raw && raw.__err) return { ok: false, code: raw.__err, detail: raw.__detail || '' };
  if (!raw) return { ok: false, code: 'E_UNKNOWN', detail: '空结果' };
  return { ok: true, count: raw.count || 0, name: raw.name || '', account_no: raw.account_no || '', tel: raw.tel || '' };
}

// ============ 带重试的查询 ============
/**
 * 重试策略：
 *   net 类 → 指数退避重试（默认 3 次）
 *   auth / risk 类 → 不重试，直接抛（必须人工介入）
 *   env 类 → 由调用方决定是否重连后重试
 */
export async function queryWithRetry(session, tel, { retries = 3, baseDelay = 500, onRetry = null, timeoutMs = 30000 } = {}) {
  let last = null;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const r = await queryOne(session, tel, timeoutMs);
      if (r.ok) return r;
      const meta = ERR[r.code] || ERR.E_UNKNOWN;
      last = r;
      if (meta.kind === 'auth' || meta.kind === 'risk') {
        const e = mkErr(r.code, r.detail); throw e;   // 立即中断整批
      }
      if (attempt < retries) {
        const d = baseDelay * Math.pow(2, attempt);
        if (onRetry) onRetry(attempt + 1, r.code, d);
        await sleep(d);
      }
    } catch (e) {
      if (e.kind === 'auth' || e.kind === 'risk') throw e;
      last = { ok: false, code: e.code || 'E_UNKNOWN', detail: e.message };
      if (attempt < retries) {
        const d = baseDelay * Math.pow(2, attempt);
        if (onRetry) onRetry(attempt + 1, e.code, d);
        await sleep(d);
      }
    }
  }
  return last;
}

// ============ CSV 工具 ============
export function csvEscape(v) {
  const s = String(v ?? '');
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

export function writeCsv(path, rows) {
  const body = rows.map(r => r.map(csvEscape).join(',')).join('\n') + '\n';
  fs.writeFileSync(path, body, 'utf8');
}

// ============ 进度文件（断点续跑）============
export function progressPath(outCsv) { return outCsv + '.progress.json'; }

export function loadProgress(outCsv) {
  try {
    const p = progressPath(outCsv);
    if (!fs.existsSync(p)) return null;
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch { return null; }
}

export function saveProgress(outCsv, data) {
  try { fs.writeFileSync(progressPath(outCsv), JSON.stringify(data, null, 2), 'utf8'); } catch {}
}

export function clearProgress(outCsv) {
  try { const p = progressPath(outCsv); if (fs.existsSync(p)) fs.unlinkSync(p); } catch {}
}
