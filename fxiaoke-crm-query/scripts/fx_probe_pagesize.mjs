// fx_probe_pagesize.mjs — 对照实验：同一号码用不同 page_size 查询，验证结果是否一致
// 用法: node fx_probe_pagesize.mjs 0192000008 0127690001 ...
import { findCrmTarget, CdpSession, preflight } from './fx_lib.mjs';

const tels = process.argv.slice(2);
if (!tels.length) { console.error('用法: node fx_probe_pagesize.mjs <号码...>'); process.exit(2); }

const target = await findCrmTarget({ create: true });
const s = await CdpSession.connect(target);
const pf = await preflight(s);
if (!pf.ok) { console.error('登录态失效:', pf.code); process.exit(3); }

async function q(tel, pageSize, incDescribe) {
  const raw = await s.evaluate(`(async () => {
    try {
      const fsToken = (document.cookie.match(/(?:^|;\\s*)fs_token=([^;]+)/) || [])[1];
      if (!fsToken) return JSON.stringify({ __err: 'E_NO_FS_TOKEN' });
      const url = 'https://www.fxiaoke.com/FHH/EM1HNCRM/API/v1/object/AccountObj/controller/DuplicateSearch?_fs_token=' + fsToken;
      const body = {
        describe_api_name: 'AccountObj', type: 'TOOL',
        object_data: { object_describe_api_name: 'AccountObj', tel: ${JSON.stringify(tel)}, duplicate_rule_api_name: 'rule_rnhS3__c' },
        include_object_describes: ${incDescribe}, is_need_duplicate: true,
        page_size: ${pageSize}, page_number: 1,
        duplicate_rule_api_name: 'rule_rnhS3__c',
        describeVersionMap: { AccountObj: 150 }
      };
      const r = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include', body: JSON.stringify(body) });
      const j = await r.json();
      if (j?.Result?.FailureCode) return JSON.stringify({ __err: 'API_' + j.Result.FailureCode });
      const dl = j?.Value?.data_list || [];
      return JSON.stringify({ n: dl.length, items: dl.map(x => ({ name: x.name, type: x.account_type })) });
    } catch (e) { return JSON.stringify({ __err: String(e) }); }
  })()`, 60000);
  try { return JSON.parse(raw); } catch { return { __err: 'PARSE' }; }
}

const TYPE = { '1': 'PJ1', 'V0QhX94z4': 'PJ2', 'z8qM9c51e': 'FB PJ1', 'DQx161x0t': 'FB PJ2', 'Q3ZFSjTtd': 'JOHOR' };

console.log('号码 | page_size=1(incDescribe) | page_size=50(noDescribe) | page_size=50(incDescribe)');
for (const tel of tels) {
  const a = await q(tel, 1, true);
  await new Promise(r => setTimeout(r, 200));
  const b = await q(tel, 50, false);
  await new Promise(r => setTimeout(r, 200));
  const c = await q(tel, 50, true);
  const fmt = (x) => x.__err ? 'ERR:' + x.__err : `${x.n}条[${x.items.map(i => (TYPE[i.type] || i.type) + ':' + i.name).join(' / ')}]`;
  console.log(`\n${tel}`);
  console.log(`  ps=1  inc=true : ${fmt(a)}`);
  console.log(`  ps=50 inc=false: ${fmt(b)}`);
  console.log(`  ps=50 inc=true : ${fmt(c)}`);
  await new Promise(r => setTimeout(r, 150));
}
process.exit(0);
