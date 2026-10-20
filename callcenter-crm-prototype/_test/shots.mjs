// 生成截图：按场景设置状态后逐张抓取
import { writeFileSync } from 'node:fs';

const shot = async (api, file, w = 1600, h = 1100) => {
  await api.evalJS(`document.querySelectorAll('.toast').forEach(t=>t.remove())`);
  await api.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
  await api.sleep(260);
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

  // 0 登录页
  await shot(api, '00-登录.png');

  // 1 主管工作台
  await login('zhaomin', '123456');
  await evalJS(`DB.settings.theme='dark';DB.settings.fs='md';DB.settings.lang='zh';applyPrefs();state.view='dashboard';render()`);
  await shot(api, '01-工作台-主管.png');

  // 2 客户列表（脱敏）
  await evalJS(`state.view='customers';state.page=1;render()`);
  await shot(api, '02-客户列表-脱敏.png');

  // 3 按数量分配弹窗
  await evalJS(`A['assign-plan']()`);
  await sleep(200);
  await shot(api, '03-按数量分配.png');
  await evalJS(`closeModal()`);

  // 4 上传 XLSX
  await evalJS(`A['import']()`);
  await sleep(200);
  await shot(api, '04-上传XLSX.png');
  await evalJS(`closeModal()`);

  // 5 客户体检（重复）
  await evalJS(`state.view='datahealth';state.dhTab='dup';render()`);
  await shot(api, '05-客户体检-重复.png');

  // 6 呼叫台（员工视角）
  await evalJS(`A['logout']()`); await sleep(120);
  await login('wangxm', '123456');
  await evalJS(`state.view='call';state.callResult='';state.callNote='';state.callStatus='';render()`);
  await shot(api, '06-呼叫台.png');

  // 7 日志（主管看组员登录）
  await evalJS(`A['logout']()`); await sleep(120);
  await login('zhaomin', '123456');
  await evalJS(`state.view='logs';state.logTab='login';render()`);
  await shot(api, '07-登录日志-主管.png');

  // 8 用户管理（密码与小组）
  await evalJS(`state.view='users';render()`);
  await shot(api, '08-用户管理-密码.png');

  // 9 权限管理 + 小组管理（管理员）
  await evalJS(`A['logout']()`); await sleep(120);
  await login('admin', 'admin123');
  await evalJS(`state.view='perms';render()`);
  await shot(api, '09-权限管理-小组.png');

  // 10 主题与字号面板（浅色 + 大字号）
  await evalJS(`DB.settings.theme='light';DB.settings.fs='lg';applyPrefs();state.view='dashboard';state.prefs=true;render()`);
  await shot(api, '10-主题与字号-浅色.png');

  // 11 英文界面（护眼主题）
  await evalJS(`DB.settings.lang='en';DB.settings.theme='eye';DB.settings.fs='md';applyPrefs();state.view='customers';state.prefs=false;render()`);
  await sleep(200);
  await shot(api, '11-英文界面-护眼.png');

  // 12 高对比主题
  await evalJS(`DB.settings.lang='zh';DB.settings.theme='contrast';applyPrefs();state.view='board';render()`);
  await sleep(150);
  await shot(api, '12-高对比-主管看板.png');

  // 13 查看完整号码留痕（回到深色）
  await evalJS(`DB.settings.theme='dark';applyPrefs();state.view='customers';state.page=1;render()`);
  await sleep(120);
  await evalJS(`(()=>{const b=document.querySelector('[data-act="reveal"]');if(b)b.click();})()`);
  await sleep(200);
  await shot(api, '13-查看完整号码留痕.png');
}
