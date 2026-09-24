/* CMP tool scene — a clickable polisher, built in geometry rather than painted.
 *
 * Why geometry and not an AI-rendered image
 * ----------------------------------------
 * The owner asked for a photoreal 3D tool whose parts you click to enter data.
 * A generated bitmap can only be clicked by guessing pixel boxes, and it drifts
 * from the model: if the platen is at 60 rpm the picture cannot show it. Every
 * part here is a real mesh, so a click is a raycast hit on the actual object,
 * the platen and head really rotate at the recipe's rpm, the slurry arm really
 * delivers at the recipe's flow, and the wafer's colour map is the SIMULATED
 * radial removal profile rather than decoration.
 *
 * Parts that carry data (click to open that section of the form):
 *   wafer / carrier head   -> wafer + film stack
 *   platen + pad           -> pad properties and grooving
 *   conditioner disk       -> diamond disk and conditioning
 *   slurry supply unit     -> slurry formulation (the tank, not the nozzle:
 *                             the formulator's mental model is the supply drum)
 *   tool frame             -> pressure, speeds, flow, time
 */
import * as THREE from './three.module.min.js';
import { OrbitControls } from './OrbitControls.js';

const PARTS = {
  wafer:      { label: 'Wafer / film stack',   section: 'wafer'  },
  head:       { label: 'Carrier head',         section: 'tool'   },
  pad:        { label: 'Pad',                  section: 'pad'    },
  platen:     { label: 'Platen',               section: 'tool'   },
  disk:       { label: 'Conditioner disk',     section: 'disk'   },
  slurry:     { label: 'Slurry supply unit',   section: 'slurry' },
  nozzle:     { label: 'Slurry delivery arm',  section: 'slurry' },
  frame:      { label: 'Tool / process setup', section: 'tool'   },
};

export function createScene(canvas, onPick) {
  // preserveDrawingBuffer: an end-to-end test must be able to read the rendered
  // pixels back to prove the scene is lit rather than a black rectangle.
  // Without it readPixels returns zeros after the frame is presented, and the
  // check silently "passes" on an empty canvas.
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false,
                                             preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0d12);
  scene.fog = new THREE.Fog(0x0b0d12, 2.4, 7.5);

  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  // Framed to include the slurry supply unit at x = -1.35: an earlier, closer
  // camera cropped it off the left edge, so the part the formulator cares about
  // most was the one part not visible.
  camera.position.set(2.05, 1.70, 2.60);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(-0.16, 0.20, 0.10);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 1.0;
  controls.maxDistance = 6.0;
  controls.maxPolarAngle = Math.PI * 0.49;

  // ── lighting: one key light with shadows, plus fill, plus a rim ──
  scene.add(new THREE.HemisphereLight(0x8fa8c8, 0x14161c, 0.55));
  const key = new THREE.DirectionalLight(0xffffff, 2.1);
  key.position.set(2.2, 3.4, 1.8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 0.5;
  key.shadow.camera.far = 12;
  key.shadow.camera.left = -2.2;
  key.shadow.camera.right = 2.2;
  key.shadow.camera.top = 2.2;
  key.shadow.camera.bottom = -2.2;
  key.shadow.bias = -0.0008;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x6f9bd1, 0.45);
  fill.position.set(-2.4, 1.2, -1.6);
  scene.add(fill);
  const rim = new THREE.SpotLight(0x4da3ff, 1.4, 8, 0.6, 0.5, 1.4);
  rim.position.set(-1.0, 2.0, -2.2);
  scene.add(rim);

  // ── materials ───────────────────────────────────────────────────
  const M = {
    steel:  new THREE.MeshStandardMaterial({ color: 0x9aa4b2, metalness: 0.92, roughness: 0.34 }),
    dark:   new THREE.MeshStandardMaterial({ color: 0x2b303a, metalness: 0.65, roughness: 0.55 }),
    panel:  new THREE.MeshStandardMaterial({ color: 0x3a4150, metalness: 0.35, roughness: 0.62 }),
    pad:    new THREE.MeshStandardMaterial({ color: 0xd9dbe0, metalness: 0.02, roughness: 0.95 }),
    wafer:  new THREE.MeshStandardMaterial({ color: 0x8899aa, metalness: 0.55, roughness: 0.22,
                                            vertexColors: true }),
    glass:  new THREE.MeshStandardMaterial({ color: 0x9fd8ff, metalness: 0.1, roughness: 0.08,
                                            transparent: true, opacity: 0.32 }),
    fluid:  new THREE.MeshStandardMaterial({ color: 0xbfe6ff, metalness: 0.0, roughness: 0.25,
                                            transparent: true, opacity: 0.75 }),
    diamond:new THREE.MeshStandardMaterial({ color: 0x22262e, metalness: 0.5, roughness: 0.45 }),
    accent: new THREE.MeshStandardMaterial({ color: 0x4da3ff, metalness: 0.4, roughness: 0.4,
                                            emissive: 0x11304f, emissiveIntensity: 0.6 }),
  };

  const pickable = [];
  function tag(mesh, part) {
    mesh.userData.part = part;
    mesh.userData.baseEmissive = 0x000000;
    pickable.push(mesh);
    return mesh;
  }

  // ── floor ───────────────────────────────────────────────────────
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(4.2, 64),
    new THREE.MeshStandardMaterial({ color: 0x11141a, roughness: 0.9, metalness: 0.1 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.34;
  floor.receiveShadow = true;
  scene.add(floor);

  // ── tool base / frame ───────────────────────────────────────────
  const frame = new THREE.Group();
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 1.02, 0.30, 64), M.panel);
  base.position.y = -0.18;
  base.castShadow = base.receiveShadow = true;
  frame.add(tag(base, 'frame'));

  const skirt = new THREE.Mesh(new THREE.TorusGeometry(0.93, 0.035, 12, 64), M.steel);
  skirt.rotation.x = Math.PI / 2;
  skirt.position.y = -0.03;
  frame.add(tag(skirt, 'frame'));
  scene.add(frame);

  // ── platen + pad (rotates) ──────────────────────────────────────
  const platenGroup = new THREE.Group();
  const platen = new THREE.Mesh(new THREE.CylinderGeometry(0.88, 0.88, 0.07, 96), M.steel);
  platen.position.y = 0.0;
  platen.castShadow = platen.receiveShadow = true;
  platenGroup.add(tag(platen, 'platen'));

  const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.86, 0.86, 0.035, 96), M.pad);
  pad.position.y = 0.052;
  pad.castShadow = pad.receiveShadow = true;
  platenGroup.add(tag(pad, 'pad'));

  // GROOVES AS A TEXTURE, NOT AS GEOMETRY. Concentric tori at a 2 mm pitch
  // means ~190 rings on a 30-inch pad; at screen scale they alias into a moiré
  // shimmer that reads as a rendering fault rather than as a grooved pad. A
  // canvas texture with mipmaps and anisotropic filtering resolves cleanly at
  // every zoom AND still moves with the pitch, which is the point — the picture
  // has to be honest about the recipe.
  let grooveTex = null;
  function buildGrooves(pitchMm, widthMm) {
    const pitch = Math.max(0.5, Number(pitchMm) || 2.0);       // mm
    const width = Math.max(0.1, Number(widthMm) || 0.5);       // mm
    const PAD_MM = 762;                                        // 30-inch pad
    const S = 1024;
    const cv = document.createElement('canvas');
    cv.width = cv.height = S;
    const g = cv.getContext('2d');
    g.fillStyle = '#d9dbe0';
    g.fillRect(0, 0, S, S);
    const pxPerMm = (S / 2) / (PAD_MM / 2);
    g.strokeStyle = '#a7abb4';
    g.lineWidth = Math.max(1, width * pxPerMm);
    for (let rMm = pitch; rMm < PAD_MM / 2; rMm += pitch) {
      g.beginPath();
      g.arc(S / 2, S / 2, rMm * pxPerMm, 0, Math.PI * 2);
      g.stroke();
    }
    if (grooveTex) grooveTex.dispose();
    grooveTex = new THREE.CanvasTexture(cv);
    grooveTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    grooveTex.colorSpace = THREE.SRGBColorSpace;
    M.pad.map = grooveTex;
    M.pad.needsUpdate = true;
  }
  buildGrooves(2.0, 0.5);
  scene.add(platenGroup);

  // ── carrier head + wafer (rotates, off-centre like a real tool) ──
  const headGroup = new THREE.Group();
  headGroup.position.set(0.40, 0, 0);

  const spindle = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.85, 24), M.steel);
  spindle.position.y = 0.62;
  spindle.castShadow = true;
  headGroup.add(tag(spindle, 'head'));

  const headBody = new THREE.Mesh(new THREE.CylinderGeometry(0.155, 0.17, 0.15, 48), M.dark);
  headBody.position.y = 0.34;
  headBody.castShadow = headBody.receiveShadow = true;
  headGroup.add(tag(headBody, 'head'));

  // CUT-AWAY CARRIER. A real carrier head covers the wafer completely — the
  // wafer faces down and you never see it. Modelling that faithfully made the
  // wafer unclickable and invisible, which defeats the one thing this view is
  // for: the wafer's colour map IS the predicted removal profile. So the head
  // is drawn as a hub plus three arms reaching to a retaining ring, leaving the
  // wafer face open. It is a cut-away, and the arms make that read as a
  // deliberate section rather than a missing part.
  const armMat = M.dark;
  for (let i = 0; i < 3; i++) {
    const arm = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.045, 0.055), armMat);
    const a = (i / 3) * Math.PI * 2;
    arm.position.set(Math.cos(a) * 0.16, 0.285, Math.sin(a) * 0.16);
    arm.rotation.y = -a;
    arm.castShadow = true;
    headGroup.add(tag(arm, 'head'));
  }

  const retainer = new THREE.Mesh(new THREE.TorusGeometry(0.315, 0.020, 10, 64), M.accent);
  retainer.rotation.x = Math.PI / 2;
  retainer.position.y = 0.168;
  headGroup.add(tag(retainer, 'head'));

  // the wafer: a disc whose vertex colours carry the SIMULATED radial profile
  const WAFER_RINGS = 48;
  const waferGeom = new THREE.CircleGeometry(0.30, 96, 0, Math.PI * 2);
  // CircleGeometry gives one ring of vertices; use a radial grid instead so a
  // profile can be painted across the radius.
  const rg = new THREE.RingGeometry(0.0001, 0.30, 96, WAFER_RINGS);
  const colors = new Float32Array(rg.attributes.position.count * 3);
  rg.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const wafer = new THREE.Mesh(rg, M.wafer);
  wafer.rotation.x = -Math.PI / 2;
  wafer.position.y = 0.155;
  wafer.castShadow = false;
  headGroup.add(tag(wafer, 'wafer'));
  scene.add(headGroup);

  /** Paint the wafer with a radial removal-rate profile. */
  function paintWafer(radiusMm, rateArr) {
    const pos = rg.attributes.position;
    const col = rg.attributes.color;
    if (!rateArr || rateArr.length < 2) {
      for (let i = 0; i < pos.count; i++) col.setXYZ(i, 0.55, 0.60, 0.67);
      col.needsUpdate = true;
      return;
    }
    const rMax = radiusMm[radiusMm.length - 1] || 1;
    let lo = Infinity, hi = -Infinity;
    for (const v of rateArr) { if (v < lo) lo = v; if (v > hi) hi = v; }
    const span = (hi - lo) || 1;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), y = pos.getY(i);
      const frac = Math.min(1, Math.sqrt(x * x + y * y) / 0.30);
      // sample the profile at this radius
      const idx = Math.min(rateArr.length - 1, Math.round(frac * (rateArr.length - 1)));
      const t = (rateArr[idx] - lo) / span;
      // blue (slow) -> cyan -> amber (fast): a diverging map reads a droop or
      // an edge fast-zone at a glance, which a single-hue ramp hides.
      const r = 0.15 + 0.85 * Math.pow(t, 0.9);
      const g = 0.35 + 0.50 * Math.sin(Math.PI * t);
      const b = 0.95 - 0.80 * Math.pow(t, 0.8);
      col.setXYZ(i, r, g, b);
    }
    col.needsUpdate = true;
  }
  paintWafer([0, 1], null);

  // ── conditioner disk on its own sweep arm ───────────────────────
  const condPivot = new THREE.Group();
  condPivot.position.set(-0.55, 0, 0.0);
  const condArm = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.05, 0.10), M.dark);
  condArm.position.set(0.20, 0.42, 0);
  condArm.castShadow = true;
  condPivot.add(tag(condArm, 'disk'));
  const condPost = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.55, 20), M.steel);
  condPost.position.y = 0.30;
  condPost.castShadow = true;
  condPivot.add(tag(condPost, 'disk'));

  const diskGroup = new THREE.Group();
  diskGroup.position.set(0.42, 0.33, 0);
  const diskBody = new THREE.Mesh(new THREE.CylinderGeometry(0.135, 0.135, 0.055, 40), M.steel);
  diskBody.castShadow = true;
  diskGroup.add(tag(diskBody, 'disk'));
  const diskFace = new THREE.Mesh(new THREE.CylinderGeometry(0.132, 0.132, 0.012, 40), M.diamond);
  diskFace.position.y = -0.031;
  diskGroup.add(tag(diskFace, 'disk'));
  // diamond grit specks, so the disk reads as a diamond disk and not a puck
  const grit = new THREE.InstancedMesh(
    new THREE.OctahedronGeometry(0.0055, 0),
    new THREE.MeshStandardMaterial({ color: 0xdfe6ef, metalness: 0.3, roughness: 0.15 }),
    260);
  const m4 = new THREE.Matrix4();
  for (let i = 0; i < 260; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = 0.03 + Math.sqrt(Math.random()) * 0.098;
    m4.makeTranslation(Math.cos(a) * r, -0.036, Math.sin(a) * r);
    grit.setMatrixAt(i, m4);
  }
  diskGroup.add(grit);
  condPivot.add(diskGroup);
  scene.add(condPivot);

  // ── slurry supply unit (drum + pump cabinet + arm + nozzle) ─────
  const supply = new THREE.Group();
  supply.position.set(-1.35, 0, 0.85);

  const cabinet = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.60, 0.40), M.panel);
  cabinet.position.y = -0.04;
  cabinet.castShadow = cabinet.receiveShadow = true;
  supply.add(tag(cabinet, 'slurry'));

  const drum = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.44, 32), M.glass);
  drum.position.y = 0.48;
  supply.add(tag(drum, 'slurry'));
  // the fill level is driven by nothing physical, so it is a fixed prop; the
  // slurry's *flow* is animated instead, because flow IS a recipe input.
  const drumFill = new THREE.Mesh(new THREE.CylinderGeometry(0.152, 0.152, 0.26, 32), M.fluid);
  drumFill.position.y = 0.39;
  supply.add(tag(drumFill, 'slurry'));
  const drumCap = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.035, 32), M.steel);
  drumCap.position.y = 0.715;
  supply.add(tag(drumCap, 'slurry'));

  const readout = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.14, 0.02), M.accent);
  readout.position.set(0, 0.10, 0.205);
  supply.add(tag(readout, 'slurry'));
  scene.add(supply);

  // delivery line from the cabinet to over the pad
  const linePts = [
    new THREE.Vector3(-1.35, 0.30, 0.85),
    new THREE.Vector3(-1.05, 0.62, 0.62),
    new THREE.Vector3(-0.55, 0.60, 0.28),
    new THREE.Vector3(-0.12, 0.42, 0.10),
  ];
  const line = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(linePts), 48, 0.022, 10, false),
    M.dark);
  line.castShadow = true;
  scene.add(tag(line, 'nozzle'));
  const nozzle = new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.09, 20), M.steel);
  nozzle.position.set(-0.12, 0.37, 0.10);
  nozzle.rotation.x = Math.PI;
  scene.add(tag(nozzle, 'nozzle'));

  // slurry stream: particle count and speed follow the recipe's flow rate
  const STREAM_N = 140;
  const streamGeom = new THREE.BufferGeometry();
  const sPos = new Float32Array(STREAM_N * 3);
  const sLife = new Float32Array(STREAM_N);
  for (let i = 0; i < STREAM_N; i++) sLife[i] = Math.random();
  streamGeom.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
  const stream = new THREE.Points(streamGeom, new THREE.PointsMaterial({
    color: 0xbfe6ff, size: 0.018, transparent: true, opacity: 0.85,
    sizeAttenuation: true }));
  scene.add(stream);

  // ── hover highlight ─────────────────────────────────────────────
  const ray = new THREE.Raycaster();
  const ptr = new THREE.Vector2();
  let hovered = null;

  function setHover(mesh) {
    if (hovered === mesh) return;
    if (hovered) {
      for (const m of pickable) {
        if (m.userData.part === hovered.userData.part) m.material = m.userData.origMat || m.material;
      }
    }
    hovered = mesh;
    if (hovered) {
      for (const m of pickable) {
        if (m.userData.part !== hovered.userData.part) continue;
        if (!m.userData.origMat) m.userData.origMat = m.material;
        const hi = m.userData.hiMat || (m.userData.hiMat = (() => {
          const c = m.material.clone();
          c.emissive = new THREE.Color(0x2f6ea8);
          c.emissiveIntensity = 0.9;
          return c;
        })());
        m.material = hi;
      }
    }
    canvas.style.cursor = hovered ? 'pointer' : 'grab';
  }

  function pickAt(ev) {
    const r = canvas.getBoundingClientRect();
    ptr.x = ((ev.clientX - r.left) / r.width) * 2 - 1;
    ptr.y = -((ev.clientY - r.top) / r.height) * 2 + 1;
    ray.setFromCamera(ptr, camera);
    const hit = ray.intersectObjects(pickable, false)[0];
    return hit ? hit.object : null;
  }

  canvas.addEventListener('pointermove', (ev) => setHover(pickAt(ev)));
  canvas.addEventListener('pointerleave', () => setHover(null));
  let downAt = null;
  canvas.addEventListener('pointerdown', (ev) => { downAt = [ev.clientX, ev.clientY]; });
  canvas.addEventListener('pointerup', (ev) => {
    // A click, not the end of an orbit drag: otherwise rotating the view keeps
    // popping panels open, which makes the scene feel broken.
    if (!downAt) return;
    const moved = Math.hypot(ev.clientX - downAt[0], ev.clientY - downAt[1]);
    downAt = null;
    if (moved > 5) return;
    const m = pickAt(ev);
    if (m && onPick) onPick(m.userData.part, PARTS[m.userData.part]);
  });

  // ── animation, driven by the CURRENT RECIPE ─────────────────────
  const state = {
    rpmPlaten: 60, rpmHead: 60, flow: 200, conditioning: true,
    sweepPeriodS: 8,
  };

  function setState(next) {
    Object.assign(state, next || {});
    if (next && (next.groovePitchMm !== undefined || next.grooveWidthMm !== undefined)) {
      buildGrooves(next.groovePitchMm ?? 2.0, next.grooveWidthMm ?? 0.5);
    }
  }

  const clock = new THREE.Clock();
  let raf = 0;

  function frame_() {
    const dt = Math.min(0.05, clock.getDelta());
    const t = clock.elapsedTime;

    platenGroup.rotation.y += (state.rpmPlaten / 60) * 2 * Math.PI * dt;
    headGroup.rotation.y   += (state.rpmHead   / 60) * 2 * Math.PI * dt;
    if (state.conditioning) {
      diskGroup.rotation.y += 2.2 * Math.PI * dt;
      // the sweep arm oscillates across the pad radius
      condPivot.rotation.y = 0.55 * Math.sin((2 * Math.PI / state.sweepPeriodS) * t);
    }

    // slurry stream: more flow = faster and denser
    const speed = 0.25 + (state.flow / 200) * 0.9;
    const visible = Math.round(Math.min(STREAM_N, 20 + (state.flow / 400) * STREAM_N));
    for (let i = 0; i < STREAM_N; i++) {
      if (i >= visible) { sPos[i * 3 + 1] = -99; continue; }
      sLife[i] += dt * speed;
      if (sLife[i] > 1) sLife[i] -= 1;
      const u = sLife[i];
      // fall from the nozzle, then spread outward on the pad surface
      const drop = 0.30 * u;
      const y = 0.33 - drop;
      const spread = u > 0.82 ? (u - 0.82) * 1.6 : 0;
      const a = i * 2.399963;                       // golden angle, even fan
      sPos[i * 3 + 0] = -0.12 + Math.cos(a) * (0.012 + spread);
      sPos[i * 3 + 1] = Math.max(0.075, y);
      sPos[i * 3 + 2] = 0.10 + Math.sin(a) * (0.012 + spread);
    }
    streamGeom.attributes.position.needsUpdate = true;
    stream.visible = state.flow > 0;

    controls.update();
    renderer.render(scene, camera);
    raf = requestAnimationFrame(frame_);
  }

  function resize() {
    // Measure the PARENT box, not the canvas. A <canvas> is a replaced element:
    // with position:fixed and left/right/top/bottom set but no explicit size, it
    // does NOT stretch to those offsets — it falls back to its intrinsic
    // 300x150. Reading clientWidth then returns 300 and the whole tool renders
    // into a postage stamp in the corner, which is exactly what happened when
    // the canvas was changed from width:100% to an inset box.
    const host = canvas.parentElement || document.body;
    const w = Math.max(80, host.clientWidth), h = Math.max(80, host.clientHeight);
    // updateStyle = false: the canvas is already sized to 100% of its host by
    // CSS, and writing pixel sizes here would fight the layout transition.
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize);
  resize();
  raf = requestAnimationFrame(frame_);

  /** Which part is under this screen point? Returns a part key or null.
   *
   * Exposed because the only honest way to verify a WebGL scene is clickable is
   * to drive it with a real mouse, and a real mouse needs to be told where the
   * platen actually IS on screen — which depends on the camera. Scanning the
   * canvas with this is how the end-to-end test finds each part without
   * hard-coding pixel boxes that break the moment the camera moves.
   */
  function probeAt(clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    ptr.x = ((clientX - r.left) / r.width) * 2 - 1;
    ptr.y = -((clientY - r.top) / r.height) * 2 + 1;
    ray.setFromCamera(ptr, camera);
    const hit = ray.intersectObjects(pickable, false)[0];
    return hit ? hit.object.userData.part : null;
  }

  return {
    setState, paintWafer, resize, probeAt,
    parts: PARTS,
    dispose() { cancelAnimationFrame(raf); renderer.dispose(); },
  };
}
