// v3 截图：角色化首页 / 公海 / 待回收 / 审批 / 可调闸门
import { writeFileSync } from 'node:fs';

const shot = async (api, file, w = 1600, h = 1100) => {
  await api.evalJS(`document.querySelectorAll('.toast').forEach(t=>t.remove())`);
  await api.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
  await api.sleep(240);
  const r = await api.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync('screenshots/' + file, Buffer.from(r.result.data, 'base64'));
  console.log('shot', file);
};

export default async function (api) {
  const { evalJS, sleep } = api;
  const login = async (u, p) => {
    await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
      if(!f) return;
      f.querySelector('[name=username]').value='${u}';
      f.querySelector('[name=password]').value='${p}';
      f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
    await sleep(200);
  };
  const reset = async () => {
    await evalJS(`DB.settings.theme='dark';DB.settings.fs='md';DB.settings.lang='zh';
      DB.settings.gateOn=true;DB.settings.gateMax=2;DB.settings.gateStart=9;DB.settings.gateEnd=20;
      DB.settings.claimLimit=200;DB.settings.protectDays=15;DB.settings.autoRecycle=true;DB.settings.crossApprove=true;
      applyPrefs()`);
  };

  await shot(api, '00-登录.png');

  // 主管 KPI 看板
  await login('zhaomin', '123456');
  await reset();
  await evalJS(`state.view='dashboard';render()`);
  await shot(api, '01-KPI看板-主管.png');

  // 员工「我的日程」
  await evalJS(`A['logout']()`); await sleep(120);
  await login('wangxm', '123456');
  await evalJS(`state.view='calendar';state.calMode='month';render()`);
  await shot(api, '02-我的日程-员工.png');

  // 客户列表（含页签）
  await evalJS(`A['logout']()`); await sleep(120);
  await login('zhaomin', '123456');
  await evalJS(`state.poolTab='mine';state.view='customers';state.page=1;render()`);
  await shot(api, '03-客户列表-页签.png');

  // 公海
  await evalJS(`state.poolTab='pool';state.page=1;render()`);
  await shot(api, '04-公海领取.png');

  // 待回收
  await evalJS(`state.poolTab='recycle';state.page=1;render()`);
  await shot(api, '05-待回收.png');

  // 客户详情（频次提示 + 申请转组）
  const cid = await evalJS(`(()=>{const c=visibleCustomers().find(x=>x.pool!=='public');return c?c.id:1})()`);
  await evalJS(`state.poolTab='mine';A['open-customer'](${cid})`); await sleep(150);
  await shot(api, '06-客户详情-频次.png');

  // 呼叫台
  await evalJS(`state.view='call';state.callResult='';state.callNote='';state.callStatus='';render()`);
  await shot(api, '07-呼叫台.png');

  // 设置：频次闸门 + 客户池
  await evalJS(`A['logout']()`); await sleep(120);
  await login('admin', 'admin123');
  await evalJS(`state.view='settings';render()`);
  await shot(api, '08-设置-闸门与客户池.png');

  // 审批页（先造两条记录）
  await evalJS(`(()=>{
    const c = DB.customers.find(x=>x.pool!=='public' && x.ownerId!==1) || DB.customers[0];
    DB.requests.unshift({ id: nextId('request'), type:'cross', custId: c.id, fromId: c.ownerId||2,
      toId: 6, reason:'客户在华南区域，跟进不便，申请转给华南二组', status:'pending',
      createdAt: iso(now()), decidedAt:null, decidedBy:null });
    DB.requests.unshift({ id: nextId('request'), type:'cross', custId: DB.customers[1].id, fromId: 3,
      toId: 2, reason:'原负责人休假，临时转组跟进', status:'approved',
      createdAt: iso(dAt(-1,15,20)), decidedAt: iso(dAt(-1,16,0)), decidedBy: 2 });
    saveDB(); state.view='approvals'; render();
  })()`);
  await sleep(200);
  await shot(api, '09-审批-跨组流转.png');

  // 权限管理（小组）
  await evalJS(`state.view='perms';render()`);
  await shot(api, '10-权限管理-小组.png');

  // 浅色 + 大字号
  await evalJS(`DB.settings.theme='light';DB.settings.fs='lg';applyPrefs();state.view='dashboard';state.prefs=true;render()`);
  await shot(api, '11-浅色主题-大字.png');

  // 英文 + 护眼
  await evalJS(`DB.settings.lang='en';DB.settings.theme='eye';DB.settings.fs='md';applyPrefs();state.view='customers';state.poolTab='pool';state.prefs=false;render()`);
  await sleep(200);
  await shot(api, '12-英文-公海.png');

  // 高对比
  await evalJS(`DB.settings.lang='zh';DB.settings.theme='contrast';applyPrefs();state.view='board';render()`);
  await sleep(150);
  await shot(api, '13-高对比-主管看板.png');
}
