// Cena 3D da carreta porta-caiaques (rev. 2) — medidas da planta, em metros.
// Eixos: X = comprimento (0 = traseira do chassi, + para a lança), Y = altura, Z = largura.
window.buildScene = function (view) {
  const W = 1800, H = 1100;
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe0f2);
  scene.fog = new THREE.Fog(0xbfe0f2, 18, 60);

  scene.add(new THREE.HemisphereLight(0xffffff, 0xc9b48a, 0.9));
  const sun = new THREE.DirectionalLight(0xfff3dd, 2.2);
  sun.position.set(4, 9, 6);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 30 });
  sun.shadow.bias = -0.0005;
  scene.add(sun);

  // areia
  const sandC = document.createElement('canvas'); sandC.width = sandC.height = 512;
  const sc = sandC.getContext('2d'); sc.fillStyle = '#e2d1a4'; sc.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 9000; i++) {
    const v = 190 + Math.random() * 50 | 0;
    sc.fillStyle = `rgba(${v},${v - 18},${v - 60},0.35)`;
    sc.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
  }
  const sandT = new THREE.CanvasTexture(sandC); sandT.wrapS = sandT.wrapT = THREE.RepeatWrapping; sandT.repeat.set(20, 20);
  sandT.colorSpace = THREE.SRGBColorSpace;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.MeshStandardMaterial({ map: sandT, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(200, 80), new THREE.MeshStandardMaterial({ color: 0x2f9fb5, roughness: 0.25, metalness: 0.1 }));
  sea.rotation.x = -Math.PI / 2; sea.position.set(0, 0.01, -50); scene.add(sea);
  // morro ao fundo
  const hill = new THREE.Mesh(new THREE.SphereGeometry(14, 32, 16), new THREE.MeshStandardMaterial({ color: 0x4d7a3c, roughness: 1 }));
  hill.scale.set(1.6, 0.45, 0.6); hill.position.set(-22, -1, -38); scene.add(hill);

  const alu = new THREE.MeshStandardMaterial({ color: 0xd5dbe0, metalness: 0.25, roughness: 0.45 });
  const rubber = new THREE.MeshStandardMaterial({ color: 0x1f1f1f, roughness: 0.95 });
  const eva = new THREE.MeshStandardMaterial({ color: 0x2b2b2b, roughness: 0.9 });
  const black = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.6 });

  function box(x1, x2, y1, y2, z1, z2, mat) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x2 - x1, y2 - y1, z2 - z1), mat);
    m.position.set((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2);
    m.castShadow = m.receiveShadow = true; scene.add(m); return m;
  }
  function rod(a, b, r, mat) {
    const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b);
    const len = va.distanceTo(vb);
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 20), mat);
    m.position.copy(va).add(vb).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), vb.clone().sub(va).normalize());
    m.castShadow = true; scene.add(m); return m;
  }

  // rodas balão Ø400 × 150
  for (const x of [0.2, 1.4]) for (const s of [-1, 1]) {
    const tire = new THREE.Mesh(new THREE.TorusGeometry(0.135, 0.068, 20, 40), rubber);
    tire.position.set(x, 0.2, s * 0.55); tire.scale.set(1, 1, 1.1); tire.castShadow = true; scene.add(tire);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.12, 24), alu);
    hub.rotation.x = Math.PI / 2; hub.position.set(x, 0.2, s * 0.55); scene.add(hub);
  }
  rod([0.2, 0.2, -0.5], [0.2, 0.2, 0.5], 0.0125, alu);
  rod([1.4, 0.2, -0.5], [1.4, 0.2, 0.5], 0.0125, alu);
  // suportes de eixo e prato giratório
  for (const s of [-1, 1]) box(0.18, 0.22, 0.2, 0.275, s * 0.2 - 0.02, s * 0.2 + 0.02, alu);
  const turn = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.03, 32), alu);
  turn.position.set(1.4, 0.26, 0); scene.add(turn);
  box(1.38, 1.42, 0.2, 0.245, -0.45, 0.45, alu);

  // chassi espinha 400
  for (const s of [-1, 1]) box(0, 1.6, 0.275, 0.325, s * 0.175 - 0.025, s * 0.175 + 0.025, alu);
  for (const x of [0.025, 0.8, 1.575]) box(x - 0.025, x + 0.025, 0.275, 0.325, -0.15, 0.15, alu);

  // mastros duplos + viga superior
  for (const x of [0.1, 1.5]) for (const s of [-1, 1]) box(x - 0.02, x + 0.02, 0.325, 1.46, s * 0.06 - 0.02, s * 0.06 + 0.02, alu);
  box(0.12, 1.48, 1.42, 1.46, -0.02, 0.02, alu);
  // travessas, berços
  const TIERS = [0.44, 0.92, 1.40];
  for (const c of TIERS) for (const x of [0.1, 1.5]) {
    box(x - 0.02, x + 0.02, c - 0.02, c + 0.02, -0.75, 0.75, alu);
    for (const s of [-1, 1]) {
      box(x - 0.075, x + 0.075, c + 0.02, c + 0.07, s * 0.4 - 0.2, s * 0.4 + 0.2, eva);
      box(x - 0.022, x + 0.022, c - 0.022, c + 0.022, s * 0.75, s * 0.758, black);
    }
  }

  // viga porta-caixa + tirante + caixa traseira
  box(-1.65, 0.08, 0.43, 0.48, -0.025, 0.025, alu);
  rod([0.08, 0.86, 0], [-0.95, 0.48, 0], 0.015, alu);
  const perfC = document.createElement('canvas'); perfC.width = 256; perfC.height = 128;
  const pc = perfC.getContext('2d'); pc.fillStyle = '#c8cfd5'; pc.fillRect(0, 0, 256, 128);
  pc.fillStyle = '#454b50';
  for (let x = 8; x < 256; x += 16) for (let y = 8; y < 128; y += 16) { pc.beginPath(); pc.arc(x, y, 4, 0, 7); pc.fill(); }
  const perfT = new THREE.CanvasTexture(perfC); perfT.colorSpace = THREE.SRGBColorSpace;
  const perfM = new THREE.MeshStandardMaterial({ map: perfT, metalness: 0.2, roughness: 0.5 });
  box(-1.6, -1.0, 0.48, 0.78, -0.175, 0.175, perfM);
  box(-1.61, -0.99, 0.78, 0.795, -0.18, 0.18, alu);      // tampa
  box(-1.62, -1.6, 0.74, 0.79, -0.04, 0.04, black);       // dobradiça/trinco

  // caiaques 4,8 m
  function kayak(color, cx, yBottom, z) {
    const g = new THREE.SphereGeometry(1, 96, 32);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      let x = p.getX(i), y = p.getY(i), zz = p.getZ(i);
      const base = Math.sqrt(Math.max(1 - x * x, 1e-6));
      const prof = Math.pow(Math.max(1 - Math.pow(Math.abs(x), 1.9), 0), 0.8);
      const k = prof / base;
      y *= k; zz *= k;
      if (y > 0) y *= 0.75;               // convés mais baixo que o casco
      y += 0.55 * Math.pow(Math.abs(x), 6); // rocker nas pontas
      p.setXYZ(i, x * 2.4, y * 0.19, zz * 0.28);
    }
    g.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.05 });
    const m = new THREE.Mesh(g, mat);
    m.position.set(cx, yBottom + 0.19, z); m.castShadow = m.receiveShadow = true; scene.add(m);
    // cockpit
    const ck = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 0.03, 40), black);
    ck.scale.set(0.42, 1, 0.22); ck.position.set(cx + 0.5, yBottom + 0.19 + 0.14, z); scene.add(ck);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(1, 0.06, 8, 40), mat);
    rim.rotation.x = Math.PI / 2; rim.scale.set(0.42, 0.22, 0.4); rim.position.set(cx + 0.5, yBottom + 0.19 + 0.155, z); scene.add(rim);
    // cintas nos dois apoios
    for (const xs of [0.1, 1.5]) {
      const st = new THREE.Mesh(new THREE.TorusGeometry(1, 0.012, 6, 40), black);
      st.scale.set(0.3, 0.2, 1); st.rotation.y = Math.PI / 2;
      st.position.set(xs, yBottom + 0.17, z); scene.add(st);
    }
  }
  const colors = [[0xd8262b, 0xf2c014], [0xf07a1a, 0x1f6fd1], [0xe8eef2, 0x2aa35a]];
  TIERS.forEach((c, i) => {
    kayak(colors[i][0], 0.3, c + 0.055, -0.4);
    kayak(colors[i][1], 0.3, c + 0.055, 0.4);
  });

  // lança reta + manopla T
  rod([1.5, 0.23, 0], [1.65, 0.23, 0], 0.02, alu);
  rod([1.65, 0.23, 0], [3.0, 0.9, 0], 0.019, alu);
  rod([3.0, 0.9, -0.25], [3.0, 0.9, 0.25], 0.019, alu);
  for (const s of [-1, 1]) rod([3.0, 0.9, s * 0.12], [3.0, 0.9, s * 0.25], 0.024, black);

  // pessoa 1,75 m (escala)
  const skin = new THREE.MeshStandardMaterial({ color: 0xc58c64, roughness: 0.8 });
  const shirt = new THREE.MeshStandardMaterial({ color: 0x4a5462, roughness: 0.9 });
  const shorts = new THREE.MeshStandardMaterial({ color: 0x1f7f86, roughness: 0.9 });
  const P = { x: 3.25, z: 0.0 };
  for (const s of [-1, 1]) {
    rod([P.x, 0.05, P.z + s * 0.1], [P.x + 0.02, 0.5, P.z + s * 0.1], 0.055, skin);
    rod([P.x + 0.02, 0.48, P.z + s * 0.1], [P.x, 0.9, P.z + s * 0.1], 0.075, shorts);
    rod([P.x - 0.02, 1.45, P.z + s * 0.2], [P.x - 0.12, 1.1, P.z + s * 0.24], 0.045, shirt);
    rod([P.x - 0.12, 1.1, P.z + s * 0.24], [3.0, 0.92, s * 0.2], 0.04, skin);
  }
  const torso = rod([P.x, 0.88, P.z], [P.x - 0.02, 1.48, P.z], 0.17, shirt); torso.scale.set(1, 1, 1.25);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 24, 16), skin); head.position.set(P.x - 0.02, 1.64, P.z); head.castShadow = true; scene.add(head);
  const hat = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.02, 24), new THREE.MeshStandardMaterial({ color: 0x8a8a7a }));
  hat.position.set(P.x - 0.02, 1.71, P.z); scene.add(hat);

  const cam = new THREE.PerspectiveCamera(35, W / H, 0.1, 200);
  const views = {
    frente: { pos: [4.3, 2.1, 4.9], at: [0.6, 0.75, 0] },
    tras: { pos: [-4.2, 1.9, 4.0], at: [-0.3, 0.75, 0] },
    lado: { pos: [0.6, 1.0, 7.6], at: [0.6, 0.9, 0] },
  };
  const v = views[view] || views.frente;
  cam.position.set(...v.pos); cam.lookAt(...v.at);
  renderer.render(scene, cam);
};
