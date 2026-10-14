const { chromium } = require('playwright');
const dir = __dirname;
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const view of ['frente', 'tras', 'lado']) {
    const p = await b.newPage({ viewport: { width: 1800, height: 1100 } });
    p.on('console', m => console.log(view, m.text()));
    p.on('pageerror', e => console.log(view, 'ERR', e.message));
    await p.setContent('<html><body style="margin:0;overflow:hidden"></body></html>');
    await p.addScriptTag({ path: dir + '/three/package/build/three.min.js' });
    await p.addScriptTag({ path: dir + '/scene.js' });
    await p.evaluate(v => window.buildScene(v), view);
    await p.evaluate(v => {
      const d = document.createElement('div');
      d.style = 'position:fixed;left:24px;bottom:20px;font:600 22px DejaVu Sans,Arial;color:#123;background:rgba(255,255,255,.75);padding:8px 14px;border-radius:6px';
      d.textContent = 'Carreta porta-caiaques · rev. 3 · ilustração com medidas da planta de fabricação (pessoa 1,75 m p/ escala)';
      document.body.appendChild(d);
    }, view);
    await p.screenshot({ path: `${dir}/ilustracao-${view}.png` });
    await p.close();
  }
  await b.close();
})();
