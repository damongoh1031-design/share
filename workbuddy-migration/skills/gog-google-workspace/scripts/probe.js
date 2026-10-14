// 页面诊断：列出所有可见输入框/按钮及真实坐标（含 shadow DOM）
// 用法: node cdp.mjs "<urlSubstring>" probe.js
(() => {
  const out = [];
  const walk = (root, path) => {
    root.querySelectorAll('input, textarea').forEach((el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      out.push({
        path,
        kind: 'input',
        type: el.type,
        name: el.name,
        id: el.id,
        aria: el.getAttribute('aria-label'),
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        valLen: (el.value || '').length,
        display: cs.display,
        opacity: cs.opacity,
        inView: r.width > 0 && r.height > 0,
      });
    });
    root.querySelectorAll('button, a, [role=button], [role=menuitem], [role=tab]').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return;
      out.push({
        path,
        kind: el.tagName === 'A' ? 'link' : 'button',
        text: (el.innerText || el.value || '').replace(/\s+/g, ' ').trim().slice(0, 40),
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        inView: r.width > 0 && r.height > 0,
      });
    });
    root.querySelectorAll('*').forEach((el) => {
      if (el.shadowRoot) walk(el.shadowRoot, path + '>' + el.tagName.toLowerCase());
    });
  };
  walk(document, 'doc');

  return JSON.stringify(
    {
      url: location.href,
      title: document.title,
      viewport: [innerWidth, innerHeight, devicePixelRatio],
      hasFocus: document.hasFocus(),
      webdriver: navigator.webdriver,
      activeEl: document.activeElement
        ? document.activeElement.tagName + ':' + (document.activeElement.name || document.activeElement.id || '')
        : null,
      iframes: [...document.querySelectorAll('iframe')].map((f) => (f.src || '').slice(0, 80)),
      inViewItems: out.filter((o) => o.inView),
      hiddenCount: out.filter((o) => !o.inView).length,
    },
    null,
    2
  );
})()
