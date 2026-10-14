(() => {
  const t = document.body.innerText || '';
  const id = (t.match(/(\d{12}-[a-z0-9]+\.apps\.googleusercontent\.com)/) || [])[1] || null;
  const secret = (t.match(/(GOCSPX-[A-Za-z0-9_\-]+)/) || [])[1] || null;
  return JSON.stringify({ client_id: id, client_secret: secret });
})()
