// v3 回归：角色化首页 / 公海回收 / 跨组审批 / 频次闸门
const P = (ok, name, extra = '') => ({ ok, name, extra });

export default async function (api) {
  const { evalJS, sleep } = api;
  const R = [];
  const A = (ok, name, extra) => R.push(P(ok, name, extra));

  const login = async (u, p) => {
    await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
      if(!f) return;
      f.querySelector('[name=username]').value='${u}';
      f.querySelector('[name=password]').value='${p}';
      f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
    await sleep(180);
  };
  const logout = async () => { await evalJS(`A['logout']()`); await sleep(120); };

  A(!!(await evalJS(`typeof DB !== 'undefined'`)), '脚本加载');

  // ---------- 1. 员工首页 = 日程 ----------
  await login('wangxm', '123456');
  A((await evalJS(`state.view`)) === 'calendar', '员工登录落在「我的日程」', await evalJS(`state.view`));
  const agentNav = await evalJS(`navItems().map(n=>n.id).join(',')`);
  A(!agentNav.includes('dashboard'), '员工导航无 KPI 看板', agentNav);
  A(agentNav.startsWith('calendar'), '员工第一项是日程', agentNav.split(',')[0]);
  const agentNavLabel = await evalJS(`navItems()[0].label`);
  A(agentNavLabel === '我的日程', '员工首页标签', agentNavLabel);
  const hasKpi = await evalJS(`!!document.querySelector('.kpi .k')`);
  A(hasKpi, '日程页顶部有指标条');
  const hasTodayList = await evalJS(`document.body.innerHTML.includes('今日待回访')`);
  A(hasTodayList, '日程页含今日待回访列表');

  // ---------- 2. 主管首页 = KPI ----------
  await logout();
  await login('zhaomin', '123456');
  A((await evalJS(`state.view`)) === 'dashboard', '主管登录落在 KPI 看板', await evalJS(`state.view`));
  const supNav = await evalJS(`navItems().map(n=>n.id).join(',')`);
  A(supNav.startsWith('dashboard'), '主管第一项是 KPI 看板');
  A(supNav.includes('approvals'), '主管导航有审批', supNav);
  const poolCard = await evalJS(`document.body.innerHTML.includes('客户池')`);
  A(poolCard, 'KPI 看板有客户池卡片');

  // ---------- 3. 公海领取 ----------
  const before = await evalJS(`({pub: poolList().length, priv: privateCount(state.user.id)})`);
  A(before.pub > 0, '存在公海客户', String(before.pub));
  const pid = await evalJS(`poolList()[0].id`);
  await evalJS(`A['pool-claim'](${pid})`); await sleep(120);
  const after = await evalJS(`({pub: poolList().length, priv: privateCount(state.user.id), pool: getCustomer(${pid}).pool, owner: getCustomer(${pid}).ownerId})`);
  A(after.pub === before.pub - 1 && after.pool === 'private' && after.owner === (await evalJS(`state.user.id`)),
    '领取后进私海且归自己', JSON.stringify(after));

  // ---------- 4. 领取上限可调 ----------
  await evalJS(`DB.settings.claimLimit = privateCount(state.user.id)`);
  const pid2 = await evalJS(`poolList()[0] && poolList()[0].id`);
  if (pid2) {
    const c0 = await evalJS(`privateCount(state.user.id)`);
    await evalJS(`A['pool-claim'](${pid2})`); await sleep(100);
    const c1 = await evalJS(`privateCount(state.user.id)`);
    A(c0 === c1, '达到持有上限后拒绝领取', c0 + ' -> ' + c1);
  } else { A(false, '公海已空，无法测上限'); }
  await evalJS(`DB.settings.claimLimit = 200; saveDB()`);

  // ---------- 5. 待回收 + 自动回收 ----------
  const rc = await evalJS(`recycleCandidates().length`);
  A(rc > 0, '存在超保护期客户', String(rc));
  const rcId = await evalJS(`recycleCandidates()[0].id`);
  await evalJS(`A['pool-tab']('recycle')`); await sleep(150);
  const rcAfter = await evalJS(`({pool: getCustomer(${rcId}).pool, owner: getCustomer(${rcId}).ownerId, left: recycleCandidates().length})`);
  A(rcAfter.pool === 'public' && rcAfter.owner === null, '超期客户被回收进公海', JSON.stringify(rcAfter));

  // ---------- 6. 保护期可调 ----------
  await evalJS(`DB.settings.protectDays = 1; DB.settings.autoRecycle = false; saveDB()`);
  const noRecycle = await evalJS(`recycleCandidates().length`);
  A(noRecycle === 0, '关闭自动回收后无候选', String(noRecycle));
  await evalJS(`DB.settings.autoRecycle = true; DB.settings.protectDays = 15; saveDB()`);

  // ---------- 7. 频次闸门 ----------
  await evalJS(`DB.settings.gateOn = true; DB.settings.gateDays = 30; DB.settings.gateMax = 1; saveDB()`);
  const busy = await evalJS(`(()=>{const c = visibleCustomers().find(x=>x.pool!=='public' && DB.notes.some(n=>n.custId===x.id&&!n.voided));
    if(!c) return null; const g=gateCheck(c); return {id:c.id, ok:g.ok, used:gateInfo(c).used, reason:g.reason||''}})()`);
  A(busy && busy.ok === false, '频次达上限时被拦', busy ? busy.reason : 'no customer');
  const inQueue = await evalJS(`callQueue().some(x=>x.c.id === ${busy ? busy.id : 0})`);
  A(inQueue === false, '频次已满的客户不在呼叫队列');
  await evalJS(`DB.settings.gateMax = 99; saveDB()`);
  const freeAgain = await evalJS(`gateCheck(getCustomer(${busy ? busy.id : 0})).ok`);
  A(freeAgain === true, '调高上限后恢复可联系');
  // 时段闸门
  await evalJS(`DB.settings.gateStart = 23; DB.settings.gateEnd = 24; saveDB()`);
  const timeBlocked = await evalJS(`gateCheck(getCustomer(${busy ? busy.id : 0})).ok`);
  A(timeBlocked === false, '不在允许时段时被拦');
  await evalJS(`DB.settings.gateStart = 0; DB.settings.gateEnd = 24; DB.settings.gateMax = 2; saveDB()`);

  // ---------- 8. 跨组流转审批 ----------
  const cid = await evalJS(`(()=>{const c = visibleCustomers().find(x=>x.pool!=='public' && x.ownerId!==state.user.id); return c?c.id:null})()`);
  A(!!cid, '找到可申请转组的客户', String(cid));
  await evalJS(`A['req-cross'](${cid})`); await sleep(120);
  const modalOk = await evalJS(`!!document.querySelector('form[data-form="cross"]')`);
  A(modalOk, '申请转组弹窗打开');
  const reqBefore = await evalJS(`(DB.requests||[]).length`);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="cross"]');
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(150);
  const reqAfter = await evalJS(`(DB.requests||[]).length`);
  A(reqAfter === reqBefore + 1, '提交后生成待审批申请', reqBefore + ' -> ' + reqAfter);
  const req = await evalJS(`(()=>{const r=(DB.requests||[]).find(x=>x.status==='pending'); return r?{id:r.id,custId:r.custId,toId:r.toId}:null})()`);
  A(!!req, '存在待审批记录');
  await evalJS(`A['nav']('approvals')`); await sleep(120);
  const apprRows = await evalJS(`document.querySelectorAll('tbody tr').length`);
  A(apprRows > 0, '审批页有列表', String(apprRows));
  await evalJS(`A['req-approve'](${req.id})`); await sleep(150);
  const moved = await evalJS(`({owner: getCustomer(${req.custId}).ownerId, status: (DB.requests||[]).find(x=>x.id===${req.id}).status})`);
  A(moved.owner === req.toId && moved.status === 'approved', '同意后客户转到目标组', JSON.stringify(moved));

  // ---------- 9. 审批可关闭 ----------
  await evalJS(`DB.settings.crossApprove = false; saveDB()`);
  const cid2 = await evalJS(`(()=>{const c = visibleCustomers().find(x=>x.pool!=='public' && x.ownerId!==state.user.id); return c?c.id:null})()`);
  await evalJS(`A['req-cross'](${cid2})`); await sleep(100);
  const reqB2 = await evalJS(`(DB.requests||[]).length`);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="cross"]');
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(150);
  const direct = await evalJS(`({n: (DB.requests||[]).length, owner: getCustomer(${cid2}).ownerId})`);
  A(direct.n === reqB2, '关闭审批后不生成申请', String(direct.n));
  A(direct.owner !== null, '关闭审批后直接生效', String(direct.owner));

  // ---------- 10. 设置项可调并持久 ----------
  await evalJS(`DB.settings.protectDays = 21; saveDB()`);
  const persisted = await evalJS(`JSON.parse(localStorage.getItem('crm_proto_v3')).settings.protectDays`);
  A(persisted === 21, '设置写入 localStorage', String(persisted));

  // 报告
  const bad = R.filter(r => !r.ok);
  console.log('\n=== 断言 ' + R.length + ' 条，失败 ' + bad.length + ' 条 ===');
  R.forEach(r => console.log((r.ok ? 'PASS ' : 'FAIL ') + r.name + (r.extra ? '  [' + r.extra + ']' : '')));
  if (api.errors.length) { console.log('\n--- 页面异常 ---'); api.errors.slice(0, 8).forEach(e => console.log(e)); }
}
