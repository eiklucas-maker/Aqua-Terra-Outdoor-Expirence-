// Renderiza folha1..N.svg em PNG (prévia) e num PDF A3 multipágina.
// Uso: node render_folhas.js <pasta> <saida.pdf>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const dir = process.argv[2], out = process.argv[3];
  const files = fs.readdirSync(dir).filter(f => /^folha\d+\.svg$/.test(f)).sort();
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8').replace('width="420mm" height="297mm"', 'width="1587" height="1123"');
    await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await p.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
  }
  const pages = files.map(f => `<div class="pg">${fs.readFileSync(path.join(dir, f), 'utf8')}</div>`).join('');
  await p.setContent(`<html><head><style>@page{size:420mm 297mm;margin:0}body{margin:0}.pg{width:420mm;height:297mm;page-break-after:always;overflow:hidden}.pg:last-child{page-break-after:auto}</style></head><body>${pages}</body></html>`);
  await p.pdf({ path: out, width: '420mm', height: '297mm', printBackground: true });
  await b.close();
})();
