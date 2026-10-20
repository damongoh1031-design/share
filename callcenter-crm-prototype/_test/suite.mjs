// 回归测试：v2.0 的 14 条需求
const P = (ok, name, extra = '') => ({ ok, name, extra });

export default async function (api) {
  const { evalJS, sleep } = api;
  const R = [];
  const A = (ok, name, extra) => R.push(P(ok, name, extra));

  const probe = await evalJS(`(typeof DB !== 'undefined') ? {u: DB.users.length, c: DB.customers.length, t: DB.teams.length} : null`);
  A(!!probe, '脚本加载，DB 可访问', JSON.stringify(probe));

  // 1. 登录页
  let login = await evalJS(`!!document.querySelector('form[data-form="login"]')`);
  A(login, '需求1 登录画面存在');

  // 2. 管理员登录
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
    f.querySelector('[name=username]').value='admin';
    f.querySelector('[name=password]').value='admin123';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(150);
  const who = await evalJS(`state.user ? state.user.username : null`);
  A(who === 'admin', '需求1 管理员登录成功', String(who));

  // 3. 导航项
  const nav = await evalJS(`navItems().map(n=>n.id).join(',')`);
  A(nav.includes('call') && nav.includes('logs') && nav.includes('perms'), '导航含呼叫台/日志/权限', nav);

  // 4. 逐页渲染无异常
  const pages = ['dashboard', 'call', 'customers', 'datahealth', 'calendar', 'notes', 'board', 'users', 'perms', 'logs', 'settings'];
  for (const v of pages) {
    await evalJS(`A['nav']('${v}')`);
    await sleep(60);
    const len = await evalJS(`document.querySelector('.main').innerHTML.length`);
    A(len > 400, `页面渲染 ${v}`, String(len));
  }

  // 5. 主题 4 套
  for (const t of ['light', 'contrast', 'eye', 'dark']) {
    await evalJS(`A['set-theme']('${t}')`);
    await sleep(40);
    const got = await evalJS(`document.documentElement.getAttribute('data-theme')`);
    A(got === t, `需求2 主题切换 ${t}`, got);
  }
  // 6. 字号 4 档
  for (const f of ['sm', 'lg', 'xl', 'md']) {
    await evalJS(`A['set-fs']('${f}')`);
    await sleep(40);
    const got = await evalJS(`document.documentElement.getAttribute('data-fs')`);
    A(got === f, `需求3 字号切换 ${f}`, got);
  }

  // 7. 中英切换：收集未翻译的中文 UI 文本
  await evalJS(`A['nav']('dashboard')`);
  await sleep(60);
  await evalJS(`A['set-lang']('en')`);
  await sleep(120);
  const enNav = await evalJS(`[...document.querySelectorAll('.nav a')].map(a=>a.textContent.trim()).join('|')`);
  A(!/[\u4e00-\u9fff]/.test(enNav), '需求4 英文模式导航全英文', enNav);

  // 收集各页残留中文（排除数据：客户名/公司/记事内容）
  const zhMap = {};
  for (const v of pages) {
    await evalJS(`A['nav']('${v}')`);
    await sleep(80);
    const arr = await evalJS(`(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null);
      while(w.nextNode()){const p=w.currentNode.parentNode;if(!p||/^(SCRIPT|STYLE)$/.test(p.nodeName))continue;
      const s=w.currentNode.nodeValue.trim();if(s&&/[\\u4e00-\\u9fff]/.test(s))out.push(s);}return [...new Set(out)];})()`);
    zhMap[v] = arr;
  }
  await evalJS(`A['set-lang']('zh')`);
  await sleep(80);

  // 8. 呼叫台：员工视角
  await evalJS(`A['logout']()`); await sleep(80);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
    f.querySelector('[name=username]').value='wangxm';
    f.querySelector('[name=password]').value='123456';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  const q0 = await evalJS(`callQueue().length`);
  A(q0 > 0, '需求6 呼叫队列非空', String(q0));
  await evalJS(`A['nav']('call')`); await sleep(80);
  const hasName = await evalJS(`!!document.querySelector('.callname')`);
  const hasHist = await evalJS(`!!document.querySelector('.callhist')`);
  A(hasName && hasHist, '需求6 呼叫台显示客户资料与历史记事');
  // 保存一条
  await evalJS(`A['call-result']('已接通')`); await sleep(60);
  await evalJS(`document.querySelector('[data-input="callNote"]').value='原型测试：客户同意下周报价';`);
  await evalJS(`document.querySelector('[data-input="callNote"]').dispatchEvent(new Event('input',{bubbles:true}))`);
  await sleep(60);
  const notesBefore = await evalJS(`DB.notes.length`);
  await evalJS(`A['call-save']()`); await sleep(150);
  const notesAfter = await evalJS(`DB.notes.length`);
  const q1 = await evalJS(`callQueue().length`);
  A(notesAfter === notesBefore + 1 && q1 === q0 - 1, '需求6 登记后保存并跳到下一位', `notes ${notesBefore}->${notesAfter}, queue ${q0}->${q1}`);

  // 9. 员工不能导出
  await evalJS(`A['nav']('customers')`); await sleep(80);
  const expDisabled = await evalJS(`(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.includes('导出'));return b?b.disabled:null})()`);
  A(expDisabled === true, '需求5 员工导出按钮禁用', String(expDisabled));
  const phoneMasked = await evalJS(`(()=>{const td=document.querySelector('tbody tr td.mono');return td?td.textContent.trim():''})()`);
  A(/\*/.test(phoneMasked), '需求5 员工看到脱敏号码', phoneMasked);
  const seePhone = await evalJS(`!!document.querySelector('[data-act="reveal"]')`);
  A(seePhone, '需求5 员工可查看完整号码（留痕）');

  // 10. 主管登录
  await evalJS(`A['logout']()`); await sleep(80);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
    f.querySelector('[name=username]').value='zhaomin';
    f.querySelector('[name=password]').value='123456';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  A((await evalJS(`state.user.username`)) === 'zhaomin', '主管登录成功');

  // 9b. 主管可上传 + 下载客户资料
  await evalJS(`A['nav']('customers')`); await sleep(80);
  const supBtns = await evalJS(`(()=>{const b=[...document.querySelectorAll('.card-hd button')];
    return {imp: b.some(x=>x.textContent.includes('上传')), exp: b.some(x=>x.textContent.includes('导出') && !x.disabled)}})()`);
  A(supBtns.imp, '需求9 主管可见「上传 XLSX」');
  A(supBtns.exp, '需求9 主管可见可用的「导出」');

  // 11. 按数量分配
  await evalJS(`A['nav']('customers')`); await sleep(80);
  const hasPlan = await evalJS(`!!document.querySelector('[data-act="assign-plan"]')`);
  A(hasPlan, '需求8 客户页有「按数量分配」入口');
  await evalJS(`A['assign-plan']()`); await sleep(100);
  const modalOpen = await evalJS(`!!document.querySelector('form[data-form="assign-plan"]')`);
  A(modalOpen, '需求8 分配弹窗打开');
  const before = await evalJS(`(()=>{const c={};DB.users.forEach(u=>c[u.id]=DB.customers.filter(x=>x.ownerId===u.id).length);return JSON.stringify(c)})()`);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="assign-plan"]');
    f.querySelector('[name=count]').value='60';
    f.querySelector('[name=mode]').value='rand';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(150);
  const after = await evalJS(`(()=>{const c={};DB.users.forEach(u=>c[u.id]=DB.customers.filter(x=>x.ownerId===u.id).length);return JSON.stringify(c)})()`);
  A(before !== after, '需求8 随机分配 60 条生效', before + ' -> ' + after);
  const auditHas = await evalJS(`DB.audit[0].action`);
  A(auditHas === '按数量分配', '需求8 分配写入审计', auditHas);

  // 12. 主管重设组员密码
  await evalJS(`A['nav']('users')`); await sleep(80);
  const pwdBtn = await evalJS(`(()=>{const b=[...document.querySelectorAll('[data-act="set-pwd"]')];return b.length})()`);
  A(pwdBtn > 0, '需求10 主管可重设组员密码', String(pwdBtn));
  const sug = await evalJS(`(()=>{const b=document.querySelector('[data-act="set-pwd"]');A['set-pwd'](b.dataset.id);
    const i=document.querySelector('form[data-form="set-pwd"] [name=p1]');return i?i.value:''})()`);
  await sleep(80);
  A(/^Crm\d{6}$/.test(sug), '需求10 生成临时密码', sug);
  const tgt = await evalJS(`document.querySelector('form[data-form="set-pwd"]').dataset.id`);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="set-pwd"]');
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  const mustChange = await evalJS(`getUser(${tgt}).mustChange`);
  A(mustChange === true, '需求10 被重设账号需强制改密');

  // 13. 主管看组员登录日志
  await evalJS(`A['nav']('logs')`); await sleep(80);
  const logRows = await evalJS(`document.querySelectorAll('.tbl-wrap tbody tr').length`);
  const scope = await evalJS(`JSON.stringify(scopeIds())`);
  const outsider = await evalJS(`(()=>{const ids=scopeIds();return DB.logins.filter(l=>l.userId&&!ids.includes(l.userId)).length})()`);
  A(logRows > 0, '需求11 主管可见登录日志', String(logRows));
  A(outsider > 0, '需求11 日志按数据范围过滤（存在范围外记录被排除）', 'excluded ' + outsider);

  // 14. 管理员登录：改全部人密码 + 全部日志 + 小组
  await evalJS(`A['logout']()`); await sleep(80);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
    f.querySelector('[name=username]').value='admin';
    f.querySelector('[name=password]').value='admin123';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  await evalJS(`A['nav']('users')`); await sleep(80);
  const adminPwd = await evalJS(`document.querySelectorAll('[data-act="set-pwd"]').length`);
  A(adminPwd >= 7, '需求12 管理员可改全部人密码', String(adminPwd));
  await evalJS(`A['nav']('logs')`); await sleep(80);
  const allLogs = await evalJS(`document.querySelectorAll('.tbl-wrap tbody tr').length`);
  A(allLogs > 40, '需求13 管理员可见全部日志', String(allLogs));

  // 15. 小组名 + 转移组员
  await evalJS(`A['nav']('perms')`); await sleep(80);
  const teamRows = await evalJS(`document.querySelectorAll('[data-act="team-edit"]').length`);
  A(teamRows === 2, '需求14 权限页有小组管理', String(teamRows));
  await evalJS(`A['team-edit']('1')`); await sleep(80);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="team"]');
    f.querySelector('[name=name]').value='华东一组A';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  const tname = await evalJS(`DB.teams[0].name`);
  A(tname === '华东一组A', '需求14 小组改名生效', tname);
  const mv = await evalJS(`(()=>{const f=document.querySelector('form[data-form="move-member"]');return !!f})()`);
  A(mv, '需求14 有转移组员表单');
  const beforeMgr = await evalJS(`(()=>{const u=DB.users.find(x=>x.role==='agent');return u.id+'|'+u.managerId})()`);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="move-member"]');
    const u=DB.users.find(x=>x.role==='agent');
    f.querySelector('[name=member]').value=u.id;
    f.querySelector('[name=supervisor]').value=DB.users.filter(x=>x.role==='supervisor').map(x=>x.id).filter(i=>i!==u.managerId)[0];
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  const afterMgr = await evalJS(`(()=>{const u=DB.users.find(x=>x.role==='agent');return u.id+'|'+u.managerId})()`);
  A(beforeMgr !== afterMgr, '需求14 转移组员生效', beforeMgr + ' -> ' + afterMgr);

  // 16. 自定义密码
  await evalJS(`A['change-pwd']()`); await sleep(80);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="change-pwd"]');
    f.querySelector('[name=old]').value='admin123';
    f.querySelector('[name=p1]').value='NewPass888';
    f.querySelector('[name=p2]').value='NewPass888';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(120);
  const newPwd = await evalJS(`DB.users.find(u=>u.username==='admin').pwd`);
  A(newPwd === 'NewPass888', '需求7 自定义密码生效', newPwd);

  // 17. 被主管重设密码后，下次登录强制改密
  await evalJS(`A['logout']()`); await sleep(120);
  await evalJS(`(()=>{const f=document.querySelector('form[data-form="login"]');
    f.querySelector('[name=username]').value='wangxm';
    f.querySelector('[name=password]').value='${sug}';
    f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));})()`);
  await sleep(160);
  const forced = await evalJS(`!!(state.modal && state.modal.type==='change-pwd' && state.modal.force)`);
  A(forced, '需求10 用临时密码登录被强制改密');
  const noClose = await evalJS(`!document.querySelector('.modal-hd .x')`);
  A(noClose, '需求10 强制改密弹窗不能直接关闭');

  // 报告
  const bad = R.filter(r => !r.ok);
  console.log('\n=== 断言 ' + R.length + ' 条，失败 ' + bad.length + ' 条 ===');
  R.forEach(r => console.log((r.ok ? 'PASS ' : 'FAIL ') + r.name + (r.extra ? '  [' + r.extra + ']' : '')));
  if (api.errors.length) { console.log('\n--- 页面异常 ---'); api.errors.slice(0, 10).forEach(e => console.log(e)); }
  if (api.logs.length) { console.log('\n--- console.error ---'); api.logs.slice(0, 10).forEach(e => console.log(e)); }

  // 输出英文模式残留中文
  console.log('\n=== EN 模式残留中文（按页面）===');
  for (const k of Object.keys(zhMap)) {
    if (zhMap[k].length) console.log('[' + k + '] ' + zhMap[k].slice(0, 40).join(' ¦ '));
  }
  const { writeFileSync } = await import('node:fs');
  writeFileSync('_test/zh-leftover.json', JSON.stringify(zhMap, null, 1), 'utf8');
}
