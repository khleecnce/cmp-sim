/* CMP tool scene — an AMAT Reflexion-style polisher you click to enter data.
 *
 * Why geometry and not an AI-rendered image
 * ----------------------------------------
 * The owner asked for a photoreal 3D tool whose parts you click to enter data.
 * A generated bitmap can only be clicked by guessing pixel boxes, and it drifts
 * from the model: if the platen is at 60 rpm the picture cannot show it. Every
 * part here is a real mesh, so a click is a raycast hit on the actual object,
 * the platens and heads really rotate at the recipe's rpm, the slurry arm
 * really delivers at the recipe's flow, and the wafer's colour map is the
 * SIMULATED radial removal profile rather than decoration.
 *
 * Why THIS layout — the Reflexion platform
 * ----------------------------------------
 * Modelled on the Applied Materials Reflexion / Reflexion LK 300 mm platform,
 * the tool the owner's customers actually run:
 *
 *   - THREE polishing platens, not one. A Cu flow is bulk -> barrier -> buff
 *     across three platens, so a single-platen picture cannot represent the
 *     process the user is designing.
 *   - FOUR carrier heads on a rotating CAROUSEL, which indexes wafers platen to
 *     platen. This is the defining feature of the platform's silhouette.
 *   - A LOAD CUP at the fourth carousel station for wafer transfer, which is
 *     why there are four heads for three platens.
 *   - A conditioner sweep arm per platen, and a slurry delivery arm per platen.
 *
 * Source for the architecture: Applied Materials Reflexion / Reflexion LK
 * product literature and Entrepix's Reflexion refurbishment documentation
 * (three platens, four carriers on a carousel transfer mechanism, multi-zone
 * heads in the Titan 3-zone .. Horizon 12-zone families).
 *
 * Source for the SHELL (what the machine looks like from across the bay) is an
 * asset listing of a real Reflexion LK, which spells the configuration out as
 * plain text rather than as a photo we would have to guess from --
 * Macquarie / wotol, "AMAT Reflexion LK Copper, 13759" (300 mm, 2006):
 *
 *     "Reflexion LK: 4 head, 3 platen polishing system. Dry in Dry out.
 *      Polisher Skins : Dark ... Load Cup Wafer Exchanger ...
 *      Monitor 2 Location : Ergo Arm type
 *      Light Tower: Factory Interface and Polisher Sides"
 *
 * Four concrete, checkable claims come out of that, and each is built here:
 *   - the polisher skins are DARK. The first build painted them light grey and
 *     the tool read as a white plastic toy; the real machine is a dark cabinet
 *     with a bright factory interface bolted to it.
 *   - DRY IN / DRY OUT means the platform is not just a polisher: wafers come
 *     back wet and leave dry, so a cleaner/dryer module sits between the
 *     factory interface and the polish bay. Leaving it out is why the tool
 *     looked like a turntable with a box next to it.
 *   - TWO light towers, one on the factory-interface side and one on the
 *     polisher side, not one.
 *   - the operator monitor hangs on an ERGO ARM, not on a plinth.
 * These are cosmetic-only: no part of the shell touches the physics, and the
 * clickable parts are unchanged.
 *
 * The SIMULATION is still single-platen: the solver predicts one polish step.
 * Platen 1 is therefore the "active" platen — it is the one carrying the wafer
 * whose profile is painted, and the one whose pad the recipe describes. The
 * other two are shown because the tool has them, and are labelled as inactive
 * rather than pretending to be simulated.
 *
 * Parts that carry data (click to open that section of the form):
 *   wafer / carrier head   -> wafer + film stack
 *   platen + pad           -> pad properties and grooving
 *   conditioner disk       -> diamond disk and conditioning
 *   slurry supply unit     -> slurry formulation (the tank, not the nozzle:
 *                             the formulator's mental model is the supply drum)
 *   carousel / frame       -> pressure, speeds, flow, time
 */
import * as THREE from './three.module.min.js';
import { OrbitControls } from './OrbitControls.js';

const PARTS = {
  wafer:      { label: 'Wafer / film stack',      section: 'wafer'  },
  head:       { label: 'Carrier head',            section: 'tool'   },
  pad:        { label: 'Pad (platen 1)',          section: 'pad'    },
  platen:     { label: 'Operation / platen',      section: 'tool'   },
  disk:       { label: 'Conditioner disk',        section: 'disk'   },
  slurry:     { label: 'Slurry supply unit',      section: 'slurry' },
  nozzle:     { label: 'Slurry delivery arm',     section: 'slurry' },
  carousel:   { label: 'Carousel / operation',    section: 'tool'   },
  loadcup:    { label: 'Wafer cart / loading',    section: 'wafer'  },
  frame:      { label: 'Tool / operation',        section: 'tool'   },
};

// Platen centres on the Reflexion deck. Three platens sit on a circle around
// the carousel axis; the fourth carousel station is the load cup.
const R_DECK = 1.02;                       // carousel arm reach
// Platen radius lives at module scope because the ENCLOSURE is sized from it:
// the roof opening must clear (R_DECK + PLATEN_R) or it crops the platens.
// Declared inside createScene it was in the temporal dead zone at that point
// and the whole scene threw before a single mesh was built.
const PLATEN_R = 0.62;
const STATIONS = [0, 1, 2, 3].map(i => {
  const a = -Math.PI / 2 + i * (Math.PI / 2);    // 4 stations, 90 deg apart
  return { i, a, x: Math.cos(a) * R_DECK, z: Math.sin(a) * R_DECK };
});
const PLATEN_STATIONS = [0, 1, 2];         // stations 0..2 carry platens
const LOADCUP_STATION = 3;                 // station 3 is the load cup

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
  // Filmic tone mapping. Without it the bright metal highlights clip to flat
  // white and everything else crushes to the same dark grey, which is what
  // made the first build read as matte plastic rather than a machine.
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  if ('outputColorSpace' in renderer) renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0d12);
  scene.fog = new THREE.Fog(0x0b0d12, 7.0, 20.0);

  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 120);
  // Viewing DIRECTION only. The distance and the target are computed from the
  // machine's own bounding sphere in fitView() once the geometry exists, so the
  // tool fills the frame at any window shape. A hard-coded camera position was
  // tuned on one 1440x900 desktop screenshot and left the machine a small dark
  // blob off to one side on other viewports (reported from a phone: "the 3D
  // model doesn't display properly"). A number chosen for one aspect ratio is
  // not a framing rule.
  // Elevation ~40 deg, not ~27. With the enclosure in place a low camera
  // shows the drum's flank and hides the platens inside it; the viewer needs
  // to look INTO the bay the way an operator leaning over the tool does.
  camera.position.set(4.6, 5.2, 5.0);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 1.6;
  controls.maxDistance = 16.0;
  controls.maxPolarAngle = Math.PI * 0.49;

  // ── lighting: one key light with shadows, plus fill, plus a rim ──
  scene.add(new THREE.HemisphereLight(0x8fa8c8, 0x14161c, 0.58));
  const key = new THREE.DirectionalLight(0xffffff, 2.0);
  key.position.set(3.4, 5.0, 2.6);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 0.5;
  key.shadow.camera.far = 18;
  key.shadow.camera.left = -3.4;
  key.shadow.camera.right = 3.4;
  key.shadow.camera.top = 3.4;
  key.shadow.camera.bottom = -3.4;
  key.shadow.bias = -0.0008;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x6f9bd1, 0.45);
  fill.position.set(-3.0, 1.6, -2.2);
  scene.add(fill);
  const rim = new THREE.SpotLight(0x4da3ff, 1.6, 12, 0.7, 0.5, 1.4);
  rim.position.set(-1.6, 2.8, -3.0);
  scene.add(rim);

  // ── environment map: what makes metal look like metal ───────────
  // Brushed stainless reads as grey plastic unless it has something to
  // REFLECT. Three point lights give one specular dot each; a real fab bay
  // wraps the tool in a bright ceiling and dim walls. Built procedurally from
  // emissive boxes and baked with PMREMGenerator, because the owner's fab PCs
  // are offline -- loading an HDRI from a CDN is not an option here.
  (function buildEnvironment() {
    const envScene = new THREE.Scene();
    const panel = (w, h, d, colour, intensity, pos) => {
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(w, h, d),
        new THREE.MeshBasicMaterial({ color: new THREE.Color(colour)
                                       .multiplyScalar(intensity) }));
      m.position.set(...pos);
      envScene.add(m);
    };
    panel(30, 0.1, 30, 0x0a0c11, 1.0, [0, -8, 0]);      // dark floor
    panel(30, 0.1, 30, 0xdce6f5, 2.4, [0, 9, 0]);       // bright ceiling
    panel(0.1, 18, 30, 0x5b6b82, 0.55, [-12, 0, 0]);    // walls
    panel(0.1, 18, 30, 0x5b6b82, 0.55, [12, 0, 0]);
    panel(30, 18, 0.1, 0x4a5568, 0.45, [0, 0, -12]);
    // ceiling light banks: the streaked highlights along the deck rim
    for (const z of [-5, 0, 5]) panel(16, 0.1, 1.1, 0xffffff, 6.0, [0, 8.4, z]);
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(envScene, 0.04).texture;
    pmrem.dispose();
  })();

  // ── materials ───────────────────────────────────────────────────
  const M = {
    steel:  new THREE.MeshStandardMaterial({ color: 0x9aa4b2, metalness: 0.92, roughness: 0.34 }),
    dark:   new THREE.MeshStandardMaterial({ color: 0x2b303a, metalness: 0.65, roughness: 0.55 }),
    panel:  new THREE.MeshStandardMaterial({ color: 0x3a4150, metalness: 0.35, roughness: 0.62 }),
    deck:   new THREE.MeshStandardMaterial({ color: 0x323845, metalness: 0.45, roughness: 0.58 }),
    // Fab tools are painted off-white sheet metal, not black. This is the
    // single biggest reason the first build read as a toy: a real CMP bay is
    // bright, and only the machinery inside the enclosure is dark.
    // Mid-grey, not white. Fab panels ARE near-white, but at this exposure a
    // pure white shell out-shouted the machine inside it -- the eye went to
    // the empty sheet metal instead of the platens. Reference photos of the
    // tool look bright because the bay lighting is bright, not because the
    // paint is the brightest thing in frame.
    // POLISHER SKINS ARE DARK. Sourced, not styled: the asset listing for the
    // real tool says "Polisher Skins : Dark" in so many words. The previous
    // light-grey shell is why the machine read as a plastic toy -- a fab bay is
    // bright, but the polisher standing in it is a dark cabinet, and the
    // FACTORY INTERFACE (M.fi below) is the light part. Getting that contrast
    // backwards flattened the whole tool into one grey mass.
    skin:   new THREE.MeshStandardMaterial({ color: 0x353a44, metalness: 0.38, roughness: 0.46 }),
    skinLo: new THREE.MeshStandardMaterial({ color: 0x252932, metalness: 0.42, roughness: 0.50 }),
    // factory interface / EFEM: light painted sheet metal, the bright end of
    // the platform, which is what makes the dark polisher read as dark.
    fi:     new THREE.MeshStandardMaterial({ color: 0xb9c0ca, metalness: 0.24, roughness: 0.50 }),
    fiLo:   new THREE.MeshStandardMaterial({ color: 0x8d949e, metalness: 0.28, roughness: 0.54 }),
    window: new THREE.MeshPhysicalMaterial({ color: 0x9fc4e8, metalness: 0.0, roughness: 0.06,
                                             transmission: 0.82, thickness: 0.03,
                                             transparent: true, opacity: 0.30,
                                             clearcoat: 1.0, side: THREE.DoubleSide }),
    foup:   new THREE.MeshStandardMaterial({ color: 0x9aa7b4, metalness: 0.05, roughness: 0.42 }),
    pad:    new THREE.MeshStandardMaterial({ color: 0xd9dbe0, metalness: 0.02, roughness: 0.95 }),
    padOff: new THREE.MeshStandardMaterial({ color: 0x8e939c, metalness: 0.02, roughness: 0.95 }),
    wafer:  new THREE.MeshStandardMaterial({ color: 0x8899aa, metalness: 0.55, roughness: 0.22,
                                            vertexColors: true }),
    glass:  new THREE.MeshStandardMaterial({ color: 0x9fd8ff, metalness: 0.1, roughness: 0.08,
                                            transparent: true, opacity: 0.32 }),
    fluid:  new THREE.MeshStandardMaterial({ color: 0xbfe6ff, metalness: 0.0, roughness: 0.25,
                                            transparent: true, opacity: 0.75 }),
    diamond:new THREE.MeshStandardMaterial({ color: 0x22262e, metalness: 0.5, roughness: 0.45 }),
    // PPS retaining ring: the head's one large non-metallic part. Pale cream,
    // matte, no metalness -- the contrast against the dark housing is how the
    // ring reads as a separate consumable rather than part of the head casting.
    pps:    new THREE.MeshStandardMaterial({ color: 0xd8d0bc, metalness: 0.0, roughness: 0.62 }),
    ppsOff: new THREE.MeshStandardMaterial({ color: 0x9e9a8c, metalness: 0.0, roughness: 0.66 }),
    accent: new THREE.MeshStandardMaterial({ color: 0x4da3ff, metalness: 0.4, roughness: 0.4,
                                            emissive: 0x11304f, emissiveIntensity: 0.6 }),
  };

  const pickable = [];
  function tag(mesh, part) {
    mesh.userData.part = part;
    pickable.push(mesh);
    return mesh;
  }

  /* ── machined-geometry helpers ──────────────────────────────────────
   *
   * Ported from the owner's earlier LK-class tool model
   * (`~/fab-sim/sim/web/studio3d.html`, chamferCyl / chamferRing /
   * boltCircle), which is the build he asked to use as the base rather than
   * starting a third silhouette from scratch.
   *
   * Why chamfers matter more than they sound: a raw CylinderGeometry has a
   * mathematically sharp 90-degree rim, and a sharp rim catches NO specular
   * highlight -- the normal jumps discontinuously, so the edge renders as a
   * hard colour boundary. Every real machined aluminium or stainless part is
   * broken-edged (a deburring requirement, not a styling choice), and that
   * chamfer is the thin bright line your eye uses to read "metal". Its
   * absence on every cylinder in the scene is a large part of why the tool
   * read as moulded plastic. A lathe profile with the corner cut gives the
   * extra normal for free at ~6 more vertices per part.
   */
  function chamferCyl(r, h, c, seg = 64) {
    c = Math.min(c, r * 0.45, h * 0.45);
    const pts = [new THREE.Vector2(0, -h / 2), new THREE.Vector2(r - c, -h / 2),
                 new THREE.Vector2(r, -h / 2 + c), new THREE.Vector2(r, h / 2 - c),
                 new THREE.Vector2(r - c, h / 2), new THREE.Vector2(0, h / 2)];
    const g = new THREE.LatheGeometry(pts, seg);
    g.computeVertexNormals();
    return g;
  }

  /** A chamfered tube (retaining rings, clamp rings, trays). */
  function chamferRing(ri, ro, h, c, seg = 64) {
    c = Math.min(c, (ro - ri) * 0.45, h * 0.45);
    const pts = [new THREE.Vector2(ri, -h / 2), new THREE.Vector2(ro - c, -h / 2),
                 new THREE.Vector2(ro, -h / 2 + c), new THREE.Vector2(ro, h / 2 - c),
                 new THREE.Vector2(ro - c, h / 2), new THREE.Vector2(ri + c, h / 2),
                 new THREE.Vector2(ri, h / 2 - c), new THREE.Vector2(ri, -h / 2)];
    const g = new THREE.LatheGeometry(pts, seg);
    g.computeVertexNormals();
    return g;
  }

  /* A ring of hex-head bolts. Fasteners are the cheapest possible cue that a
   * surface is a bolted-down machined plate rather than a solid block, and
   * they are the detail a process engineer looks for first on a platen.
   *
   * Tagged and pickable like everything else: an InstancedMesh left untagged
   * still occupies its pixels for the raycaster, so bolts sitting on a platen
   * would silently swallow clicks meant for the platen and report "nothing
   * here". Giving them the parent's part key makes a click on a bolt open the
   * same drawer as a click on the plate it holds down. */
  function boltRing(parent, part, R, y, n, s, mat) {
    const im = new THREE.InstancedMesh(
      new THREE.CylinderGeometry(s, s, s * 0.9, 6), mat || M.steel, n);
    const o = new THREE.Object3D();
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      o.position.set(Math.cos(a) * R, y, Math.sin(a) * R);
      o.rotation.y = a;
      o.updateMatrix();
      im.setMatrixAt(i, o.matrix);
    }
    im.castShadow = true;
    parent.add(tag(im, part));
    return im;
  }

  // ── floor ───────────────────────────────────────────────────────
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(7.0, 64),
    new THREE.MeshStandardMaterial({ color: 0x11141a, roughness: 0.9, metalness: 0.1 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.62;
  floor.receiveShadow = true;
  scene.add(floor);

  // ── tool frame: the deck the platens are set into ───────────────
  const frame = new THREE.Group();
  const deck = new THREE.Mesh(new THREE.CylinderGeometry(1.72, 1.80, 0.36, 72), M.deck);
  deck.position.y = -0.20;
  deck.castShadow = deck.receiveShadow = true;
  frame.add(tag(deck, 'frame'));

  const deckRim = new THREE.Mesh(new THREE.TorusGeometry(1.72, 0.04, 12, 80), M.steel);
  deckRim.rotation.x = Math.PI / 2;
  deckRim.position.y = -0.02;
  frame.add(tag(deckRim, 'frame'));

  // ── enclosure, EFEM, FOUPs, signal tower ────────────────────────
  // A real polisher is a closed cabinet: the polish bay is behind viewing
  // windows, wafers arrive through an EFEM with FOUPs on the load ports, and
  // a stack light shows tool state. Without this the scene is a bare
  // turntable floating in a void, which is what "the UI is rubbish" meant.
  // It is built as ONE group so the machinery underneath is untouched, and
  // every piece is tagged to a part that already exists -- no new form
  // section, no new physics, purely the shell the tool actually has.
  const shell = new THREE.Group();
  // Bay height is set just above the carousel mast, NOT at a round number.
  // A taller drum looked more like a tool in isolation but buried the platens
  // at the bottom of a well -- from any normal viewing angle you saw sheet
  // metal and no machine. The enclosure has to end where the machinery ends.
  const BAY_R = 1.95, BAY_H = 0.96, BAY_Y = -0.62;

  // polish bay: a 12-sided drum, opaque below the belt line, glazed above,
  // so the platens stay visible the way they are through a real window.
  const bayLower = new THREE.Mesh(
    new THREE.CylinderGeometry(BAY_R, BAY_R * 1.02, 0.78, 12, 1, true), M.skin);
  bayLower.position.y = BAY_Y + 0.39;
  bayLower.castShadow = bayLower.receiveShadow = true;
  shell.add(tag(bayLower, 'frame'));

  const bayGlass = new THREE.Mesh(
    new THREE.CylinderGeometry(BAY_R, BAY_R, BAY_H - 0.78, 12, 1, true), M.window);
  bayGlass.position.y = BAY_Y + 0.78 + (BAY_H - 0.78) / 2;
  shell.add(bayGlass);            // not pickable: clicks pass through to parts

  // mullions between the glazed facets, and the belt line / top capping rings
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    const post = new THREE.Mesh(
      new THREE.BoxGeometry(0.055, BAY_H - 0.78, 0.055), M.skinLo);
    post.position.set(Math.cos(a) * BAY_R, BAY_Y + 0.78 + (BAY_H - 0.78) / 2,
                      Math.sin(a) * BAY_R);
    post.rotation.y = -a;
    shell.add(tag(post, 'frame'));
  }
  for (const [y, r, t] of [[BAY_Y + 0.78, BAY_R + 0.012, 0.045],
                           [BAY_Y + BAY_H, BAY_R + 0.012, 0.055]]) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r, t, 10, 72), M.skinLo);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = y;
    shell.add(tag(ring, 'frame'));
  }
  // Roof: an ANNULUS of service panels, not a closed lid. A solid disc is what
  // the real tool has, but it hides every part the user is here to click --
  // the first attempt rendered as a white drum with the machine sealed inside.
  // An open centre keeps the fab silhouette and the top-down view of the
  // platens at the same time, which is the tradeoff a cutaway drawing makes.
  const roof = new THREE.Mesh(
    // Inner radius clears the platens: they sit at R_DECK with radius
    // PLATEN_R, so anything tighter than (R_DECK + PLATEN_R) crops the very
    // parts the user clicks. Derived, not eyeballed -- a hand-picked 0.74
    // looked fine in one screenshot and hid a platen edge in every other.
    new THREE.RingGeometry(R_DECK + PLATEN_R + 0.10, BAY_R + 0.02, 12, 1),
    M.skin);
  roof.rotation.x = -Math.PI / 2;
  roof.position.y = BAY_Y + BAY_H + 0.05;
  roof.castShadow = true;
  shell.add(tag(roof, 'frame'));

  // panel seams on the roof ring, so it reads as bolted sheet metal
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2 + Math.PI / 12;
    const seam = new THREE.Mesh(
      new THREE.BoxGeometry(BAY_R - (R_DECK + PLATEN_R + 0.10), 0.012, 0.030),
      M.skinLo);
    const rMid = ((R_DECK + PLATEN_R + 0.10) + BAY_R) / 2;
    seam.position.set(Math.cos(a) * rMid, BAY_Y + BAY_H + 0.058,
                      Math.sin(a) * rMid);
    seam.rotation.y = -a;
    shell.add(tag(seam, 'frame'));
  }

  // EFEM: the front-end box wafers pass through, with FOUP load ports.
  // Placed on the load-cup side so the wafer path reads correctly:
  // FOUP -> EFEM -> load cup -> carousel -> platen.
  const efemSt = STATIONS[LOADCUP_STATION];
  const outEf = new THREE.Vector3(efemSt.x, 0, efemSt.z).normalize();

  /* The platform is a TRAIN, and its pieces must not occupy the same metres.
   * Laid out as explicit depths along the outward axis rather than as three
   * independently hand-picked radii -- the first attempt put the cleaner at a
   * radius that was still INSIDE the polish bay drum, where it was invisible.
   * A spacing chosen by eye in one screenshot is not a layout. */
  const EFEM_D = 1.05, CLEAN_D = 0.86;
  const CLEAN_MID = BAY_R + CLEAN_D / 2;          // hard against the bay wall
  const EFEM_MID  = BAY_R + CLEAN_D + EFEM_D / 2; // then the factory interface
  const FRONT     = EFEM_MID + EFEM_D / 2;        // the operator's side of it

  const efem = new THREE.Group();
  efem.position.set(outEf.x * EFEM_MID, 0, outEf.z * EFEM_MID);
  efem.rotation.y = -Math.atan2(outEf.z, outEf.x);

  const efemBody = new THREE.Mesh(new THREE.BoxGeometry(EFEM_D, 1.95, 2.05), M.fi);
  efemBody.position.y = BAY_Y + 0.98;
  efemBody.castShadow = efemBody.receiveShadow = true;
  efem.add(tag(efemBody, 'loadcup'));

  /* PANEL SEAMS AND SERVICE DOORS on the factory interface.
   *
   * The EFEM is the brightest large surface in the scene, and it was a single
   * smooth box: a featureless white slab reads as polystyrene packaging no
   * matter how good the machinery beside it is, and at this size it is the
   * first thing the eye lands on. Real fab sheet metal is panelised — the
   * cabinet is made of bolted service panels with visible seams, recessed door
   * frames and handles, because every one of them has to open for maintenance.
   *
   * Seams are drawn as thin darker strips proud of the surface rather than as
   * a texture, so they hold up at any zoom and cast their own micro-shadows,
   * which is what actually separates "panelled cabinet" from "painted lines".
   */
  const seamStrip = (w, h, d, pos) => {
    const s = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), M.fiLo);
    s.position.set(...pos);
    efem.add(tag(s, 'loadcup'));
  };
  for (const z of [-0.98, -0.34, 0.34, 0.98]) {        // vertical panel joins
    seamStrip(EFEM_D + 0.008, 1.90, 0.014, [0, BAY_Y + 0.98, z]);
  }
  for (const y of [BAY_Y + 0.16, BAY_Y + 1.80]) {      // horizontal rails
    seamStrip(EFEM_D + 0.008, 0.030, 2.05, [0, y, 0]);
  }
  // recessed service doors on the operator face, each with a handle
  for (const z of [-0.66, 0.66]) {
    const frame_ = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.86, 0.54), M.fiLo);
    frame_.position.set(-EFEM_D / 2 - 0.004, BAY_Y + 1.10, z);
    efem.add(tag(frame_, 'loadcup'));
    const handle = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.04, 0.16), M.dark);
    handle.position.set(-EFEM_D / 2 - 0.020, BAY_Y + 1.10, z + 0.20);
    efem.add(tag(handle, 'loadcup'));
  }

  const efemWin = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.62, 1.70), M.window);
  efemWin.position.set(0.53, BAY_Y + 1.45, 0);
  efem.add(efemWin);

  // three FOUPs on the load ports -- the clearest "this is a fab tool" cue
  for (const z of [-0.66, 0, 0.66]) {
    const port = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.30, 0.52), M.fiLo);
    port.position.set(0.55, BAY_Y + 0.62, z);
    efem.add(tag(port, 'loadcup'));

    const foup = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.44, 0.48), M.foup);
    foup.position.set(0.80, BAY_Y + 0.96, z);
    foup.castShadow = true;
    efem.add(tag(foup, 'loadcup'));

    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.36, 0.40), M.fiLo);
    lid.position.set(0.58, BAY_Y + 0.96, z);
    efem.add(tag(lid, 'loadcup'));

    const handle = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.05, 0.05), M.dark);
    handle.position.set(0.80, BAY_Y + 1.21, z);
    efem.add(tag(handle, 'loadcup'));
  }
  shell.add(efem);

  /* CLEANER / DRYER MODULE — the "Dry in Dry out" half of the platform.
   *
   * This is the piece whose absence made the tool read as a turntable with a
   * box beside it. On the real platform the wafer comes off the last platen
   * WET and must leave the machine DRY, so a brush/megasonic cleaner and a
   * spin-rinse dryer sit between the polish bay and the factory interface.
   * It is drawn as a low dark housing with lid ports, bridging exactly that
   * gap, so the wafer path reads FOUP -> FI -> cleaner -> bay and back.
   *
   * It carries no data and no physics: the solver models ONE polish step, so
   * tagging this as a clickable input would promise a cleaning model that does
   * not exist. It is tagged 'frame' (operation) like the rest of the body. */
  const clean = new THREE.Group();
  clean.position.set(outEf.x * CLEAN_MID, 0, outEf.z * CLEAN_MID);
  clean.rotation.y = -Math.atan2(outEf.z, outEf.x);
  const cleanBody = new THREE.Mesh(new THREE.BoxGeometry(CLEAN_D, 1.34, 1.86), M.skin);
  cleanBody.position.y = BAY_Y + 0.67;
  cleanBody.castShadow = cleanBody.receiveShadow = true;
  clean.add(tag(cleanBody, 'frame'));
  // service lids over the cleaning stations: brush box, brush box, dryer
  for (const [z, lit] of [[-0.58, false], [0, false], [0.58, true]]) {
    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.05, 0.52), M.skinLo);
    lid.position.set(0, BAY_Y + 1.36, z);
    clean.add(tag(lid, 'frame'));
    const eye = new THREE.Mesh(
      new THREE.CylinderGeometry(0.035, 0.035, 0.02, 16),
      new THREE.MeshStandardMaterial({
        color: lit ? 0x1fdc6a : 0x2b90d9, emissive: lit ? 0x1fdc6a : 0x2b90d9,
        emissiveIntensity: 0.9, roughness: 0.35 }));
    eye.position.set(0.22, BAY_Y + 1.39, z);
    clean.add(tag(eye, 'frame'));
  }
  shell.add(clean);

  /* OPERATOR MONITOR ON AN ERGO ARM. The listing is specific -- "Monitor 2
   * Location : Ergo Arm type" -- and it is a strong silhouette cue: the screen
   * floats out from the factory interface on a jointed arm at standing height,
   * it does not sit on a plinth. Built as post -> upper arm -> forearm ->
   * screen so the joints read at a glance. */
  const console_ = new THREE.Group();
  console_.position.set(outEf.x * (FRONT + 0.05), 0, outEf.z * (FRONT + 0.05));
  console_.rotation.y = -Math.atan2(outEf.z, outEf.x);
  const ergoPost = new THREE.Mesh(
    new THREE.CylinderGeometry(0.032, 0.032, 0.95, 16), M.steel);
  ergoPost.position.set(-0.02, BAY_Y + 1.30, -0.88);
  console_.add(tag(ergoPost, 'carousel'));
  const ergoUpper = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.05, 0.05), M.steel);
  ergoUpper.position.set(0.10, BAY_Y + 1.76, -0.68);
  ergoUpper.rotation.y = -0.85;
  console_.add(tag(ergoUpper, 'carousel'));
  const ergoFore = new THREE.Mesh(new THREE.BoxGeometry(0.40, 0.045, 0.045), M.steel);
  ergoFore.position.set(0.30, BAY_Y + 1.74, -0.36);
  ergoFore.rotation.y = -0.30;
  console_.add(tag(ergoFore, 'carousel'));

  const scr = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.42, 0.66), M.dark);
  scr.position.set(0.42, BAY_Y + 1.66, -0.18);
  scr.rotation.set(0, 0.24, -0.16);
  console_.add(tag(scr, 'carousel'));
  const scrFace = new THREE.Mesh(new THREE.BoxGeometry(0.01, 0.36, 0.60),
    new THREE.MeshStandardMaterial({ color: 0x0e2a45, emissive: 0x1d6fb8,
                                     emissiveIntensity: 0.85, roughness: 0.3 }));
  scrFace.position.set(0.45, BAY_Y + 1.665, -0.175);
  scrFace.rotation.set(0, 0.24, -0.16);
  console_.add(tag(scrFace, 'carousel'));
  // keyboard shelf under the screen -- what makes it read as a workstation
  const shelf = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.025, 0.56), M.fiLo);
  shelf.position.set(0.36, BAY_Y + 1.36, -0.20);
  console_.add(tag(shelf, 'carousel'));
  shell.add(console_);

  /* TWO SIGNAL TOWERS, not one: "Light Tower: Factory Interface and Polisher
   * Sides". A single tower was a guess; the source states both ends carry one,
   * which is also how an operator reads tool state from either aisle. Each is
   * an identical stack (green lit = running, amber and red dark). */
  const buildTower = (pos) => {
    const tower = new THREE.Group();
    tower.position.copy(pos);
    const towerPost = new THREE.Mesh(
      new THREE.CylinderGeometry(0.035, 0.035, 0.22, 16), M.dark);
    towerPost.position.y = 0.11;
    tower.add(tag(towerPost, 'frame'));
    const LAMPS = [[0x1fdc6a, 1.30], [0xffb020, 0.10], [0xff3b30, 0.10]];
    LAMPS.forEach(([c, e], i) => {
      const lamp = new THREE.Mesh(
        new THREE.CylinderGeometry(0.062, 0.062, 0.10, 20),
        new THREE.MeshStandardMaterial({ color: c, emissive: c,
                                         emissiveIntensity: e, roughness: 0.35,
                                         transparent: true, opacity: 0.92 }));
      lamp.position.y = 0.27 + i * 0.105;
      tower.add(tag(lamp, 'frame'));
    });
    const towerCap = new THREE.Mesh(
      new THREE.CylinderGeometry(0.066, 0.066, 0.03, 20), M.dark);
    towerCap.position.y = 0.27 + LAMPS.length * 0.105;
    tower.add(tag(towerCap, 'frame'));
    shell.add(tower);
  };
  // polisher side: on the bay roof, away from the factory interface
  buildTower(new THREE.Vector3(-outEf.x * BAY_R * 0.74, BAY_Y + BAY_H + 0.10,
                              -outEf.z * BAY_R * 0.74));
  // factory-interface side: on the EFEM roof
  buildTower(new THREE.Vector3(outEf.x * EFEM_MID, BAY_Y + 1.96,
                               outEf.z * EFEM_MID));

  scene.add(shell);

  // base cabinets under the deck — the tool is a floor machine, and without a
  // body the platens look like they are floating on a table.
  for (let i = 0; i < 4; i++) {
    const a = i * (Math.PI / 2) + Math.PI / 4;
    const cab = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.46, 0.85), M.panel);
    cab.position.set(Math.cos(a) * 1.12, -0.60, Math.sin(a) * 1.12);
    cab.rotation.y = -a;
    cab.castShadow = cab.receiveShadow = true;
    frame.add(tag(cab, 'frame'));
  }
  scene.add(frame);

  // ── the three platens ───────────────────────────────────────────
  // Platen 1 (station 0) is the ACTIVE one: the solver simulates a single
  // polish step, so exactly one platen may claim to be the simulated one.
  const platens = [];
  let grooveTex = null;
  let bumpTex = null;

  /* GROOVES AS A TEXTURE, NOT AS GEOMETRY. Concentric tori at a 2 mm pitch
   * means ~190 rings on a 30-inch pad; at screen scale they alias into a moiré
   * shimmer that reads as a rendering fault rather than as a grooved pad. A
   * canvas texture with mipmaps and anisotropic filtering resolves cleanly at
   * every zoom AND still moves with the pitch, which is the point — the picture
   * has to be honest about the recipe.
   *
   * A flat fill plus grey rings, which is what this drew before, is a
   * TECHNICAL DRAWING of a pad, not a pad. Two things are added here, both
   * carried over from the owner's earlier LK-class model:
   *
   *  - a noise base with dark specks. Cast polyurethane pad (IC1000 family) is
   *    a closed-cell foam: the polishing surface is visibly porous, and those
   *    pores are where the slurry actually sits. Rendering the pad as a smooth
   *    plastic sheet hid the single most recognisable feature of the consumable
   *    this whole simulator is about.
   *  - a BUMP MAP built from the same rings. Without it the grooves are painted
   *    stripes that stay flat as the platen turns; with it they catch and lose
   *    the key light as they rotate, which is what makes them read as cut
   *    channels with depth rather than as printed lines.
   *
   * Colour stays in the pad's own khaki-grey family rather than the previous
   * near-white: a bright pad was the second-brightest thing in frame after the
   * wafer and pulled the eye off the machine. */
  let padBaseCv = null;
  function padBase(S) {
    // Built once and reused: the pore field is the expensive part (a full
    // getImageData/putImageData pass), and re-rolling it on every groove
    // change would also make the pad's pores JUMP whenever the user edits a
    // pitch, as if the consumable had been swapped.
    if (padBaseCv) return padBaseCv;
    const cv = document.createElement('canvas');
    cv.width = cv.height = S;
    const g = cv.getContext('2d');
    g.fillStyle = '#9a9a72';
    g.fillRect(0, 0, S, S);
    const img = g.getImageData(0, 0, S, S), d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      const n = (Math.random() - 0.5) * 24;
      const pore = Math.random() < 0.06 ? -26 : 0;   // ~6% closed-cell pores
      d[i] = Math.max(0, d[i] + n + pore);
      d[i + 1] = Math.max(0, d[i + 1] + n + pore);
      d[i + 2] = Math.max(0, d[i + 2] + n * 0.8 + pore);
    }
    g.putImageData(img, 0, 0);
    // radial scuffing from previous wafers, the marks conditioning leaves
    g.strokeStyle = 'rgba(255,255,245,0.05)';
    g.lineWidth = 1;
    for (let i = 0; i < 220; i++) {
      const a = Math.random() * Math.PI * 2, r = Math.random() * S / 2;
      g.beginPath();
      g.arc(S / 2, S / 2, r, a, a + 0.02 + Math.random() * 0.15);
      g.stroke();
    }
    padBaseCv = cv;
    return cv;
  }

  function buildGrooves(pitchMm, widthMm) {
    const pitch = Math.max(0.5, Number(pitchMm) || 2.0);       // mm
    const width = Math.max(0.1, Number(widthMm) || 0.5);       // mm
    const PAD_MM = 762;                                        // 30-inch pad
    const S = 1024;
    const cv = document.createElement('canvas');
    cv.width = cv.height = S;
    const g = cv.getContext('2d');
    g.drawImage(padBase(S), 0, 0);
    const bump = document.createElement('canvas');
    bump.width = bump.height = S;
    const b = bump.getContext('2d');
    b.fillStyle = '#808080';                 // mid-grey = the pad's land area
    b.fillRect(0, 0, S, S);

    const pxPerMm = (S / 2) / (PAD_MM / 2);
    const w = Math.max(1.2, width * pxPerMm);
    g.strokeStyle = 'rgba(30,32,22,0.62)';   // groove floor, in shadow
    g.lineWidth = w;
    b.strokeStyle = '#303030';               // darker = lower, i.e. cut away
    b.lineWidth = w;
    for (let rMm = pitch; rMm < PAD_MM / 2; rMm += pitch) {
      const r = rMm * pxPerMm;
      g.beginPath(); g.arc(S / 2, S / 2, r, 0, Math.PI * 2); g.stroke();
      b.beginPath(); b.arc(S / 2, S / 2, r, 0, Math.PI * 2); b.stroke();
    }
    // lit edge on the side of each groove that faces the light
    g.strokeStyle = 'rgba(255,255,240,0.10)';
    g.lineWidth = Math.max(0.6, w * 0.4);
    for (let rMm = pitch; rMm < PAD_MM / 2; rMm += pitch) {
      g.beginPath();
      g.arc(S / 2, S / 2, rMm * pxPerMm + w * 0.9, 0, Math.PI * 2);
      g.stroke();
    }

    if (grooveTex) grooveTex.dispose();
    if (bumpTex) bumpTex.dispose();
    bumpTex = new THREE.CanvasTexture(bump);
    bumpTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    grooveTex = new THREE.CanvasTexture(cv);
    grooveTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    grooveTex.colorSpace = THREE.SRGBColorSpace;
    for (const mat of [M.pad, M.padOff]) {
      mat.bumpMap = bumpTex;
      mat.bumpScale = 0.02;
    }
    M.pad.map = grooveTex;
    M.pad.needsUpdate = true;
    M.padOff.map = grooveTex;
    M.padOff.needsUpdate = true;
  }
  buildGrooves(2.0, 0.5);

  for (const si of PLATEN_STATIONS) {
    const st = STATIONS[si];
    const g = new THREE.Group();
    g.position.set(st.x, 0, st.z);

    /* The platen is a machined aluminium table, and on the real deck you see
     * three separate parts stacked: the platen body, the bolt circle that holds
     * the pad clamp down, and the clamp ring itself trapping the pad's outer
     * edge. Previously this was one sharp-edged cylinder with a torus round it,
     * which is why the largest part of the machine was also its flattest. */
    const body = new THREE.Mesh(chamferCyl(PLATEN_R, 0.16, 0.014, 96), M.steel);
    body.position.y = -0.04;
    body.castShadow = body.receiveShadow = true;
    g.add(tag(body, 'platen'));

    // non-rotating bearing housing under the platen: the part that makes it
    // read as a driven table rather than a disc lying on the deck
    const hub = new THREE.Mesh(chamferCyl(PLATEN_R * 0.62, 0.12, 0.012, 64), M.dark);
    hub.position.y = -0.17;
    hub.receiveShadow = true;
    g.add(tag(hub, 'platen'));

    const pad = new THREE.Mesh(
      new THREE.CylinderGeometry(PLATEN_R - 0.015, PLATEN_R - 0.015, 0.035, 80),
      si === 0 ? M.pad : M.padOff);
    pad.position.y = 0.067;
    pad.castShadow = pad.receiveShadow = true;
    g.add(tag(pad, 'pad'));

    /* NO clamp ring and NO bolt circle over the pad face. A first pass added
     * both because they make a platen look machined, and both are wrong: a
     * polishing pad of this class is pressure-sensitive-adhesive mounted to the
     * platen, so nothing is fastened over the polishing surface. Detail that
     * makes a picture look more convincing while showing hardware the tool does
     * not have is the same error as inventing a parameter value.
     *
     * The bolts that ARE visible on the real machine are on the bearing housing
     * flange below the platen, where they hold the drive down. */
    boltRing(g, 'platen', PLATEN_R * 0.62 - 0.035, -0.110, 12, 0.013, M.steel);

    // retaining ring around the platen, as on the real deck
    const ring = new THREE.Mesh(new THREE.TorusGeometry(PLATEN_R + 0.02, 0.028, 10, 72),
                                si === 0 ? M.accent : M.dark);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = 0.02;
    g.add(tag(ring, 'platen'));

    scene.add(g);
    platens.push({ group: g, station: si, active: si === 0 });
  }

  // ── carousel: four carrier heads, indexing between stations ─────
  const carousel = new THREE.Group();
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.34, 0.20, 40), M.dark);
  hub.position.y = 1.16;
  hub.castShadow = true;
  carousel.add(tag(hub, 'carousel'));

  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.17, 1.30, 32), M.steel);
  mast.position.y = 0.55;
  mast.castShadow = true;
  carousel.add(tag(mast, 'carousel'));

  const heads = [];
  for (const st of STATIONS) {
    // the arm out to this station
    const arm = new THREE.Mesh(new THREE.BoxGeometry(R_DECK, 0.10, 0.17), M.dark);
    arm.position.set(Math.cos(st.a) * R_DECK / 2, 1.16, Math.sin(st.a) * R_DECK / 2);
    arm.rotation.y = -st.a;
    arm.castShadow = true;
    carousel.add(tag(arm, 'carousel'));

    const headGroup = new THREE.Group();
    headGroup.position.set(st.x, 0, st.z);

    const spindle = new THREE.Mesh(chamferCyl(0.052, 0.72, 0.006, 32), M.steel);
    spindle.position.y = 0.80;
    spindle.castShadow = true;
    headGroup.add(tag(spindle, 'head'));

    /* CARRIER HEAD STACK. A multi-zone head is not one cylinder: from the pad
     * upward it is membrane base -> housing -> sealing flange -> upper step ->
     * gimbal housing -> spindle, with the zone-pressure lines running down the
     * outside to the pneumatic ports. Those lines are the visible evidence of
     * the zone pressures the Operation form lets you set, so drawing them is
     * not decoration — it connects an input the user types to a part they can
     * see. Proportions follow the owner's earlier LK-class model, scaled to
     * this deck's 300 mm head. */
    const body = new THREE.Mesh(chamferCyl(0.172, 0.20, 0.020, 64), M.dark);
    body.position.y = 0.40;
    body.castShadow = body.receiveShadow = true;
    headGroup.add(tag(body, 'head'));

    // sealing flange on top of the housing, with the bolts that hold it
    const seal = new THREE.Mesh(chamferRing(0.150, 0.178, 0.014, 0.004, 64), M.steel);
    seal.position.y = 0.505;
    headGroup.add(tag(seal, 'head'));
    boltRing(headGroup, 'head', 0.163, 0.516, 12, 0.008, M.steel);

    // gimbal housing: the joint that lets the head follow the pad
    const gimbal = new THREE.Mesh(chamferCyl(0.085, 0.10, 0.012, 48), M.steel);
    gimbal.position.y = 0.575;
    gimbal.castShadow = true;
    headGroup.add(tag(gimbal, 'head'));

    // three pneumatic ports + the zone-pressure lines climbing to the spindle
    for (let k = 0; k < 3; k++) {
      const a = (k / 3) * Math.PI * 2 + 0.4;
      const port = new THREE.Mesh(
        new THREE.CylinderGeometry(0.011, 0.011, 0.045, 12), M.steel);
      port.position.set(Math.cos(a) * 0.150, 0.520, Math.sin(a) * 0.150);
      headGroup.add(tag(port, 'head'));
      const hose = new THREE.Mesh(new THREE.TubeGeometry(
        new THREE.CatmullRomCurve3([
          new THREE.Vector3(Math.cos(a) * 0.150, 0.540, Math.sin(a) * 0.150),
          new THREE.Vector3(Math.cos(a) * 0.115, 0.760, Math.sin(a) * 0.115),
          new THREE.Vector3(Math.cos(a) * 0.052, 1.010, Math.sin(a) * 0.052)]),
        20, 0.0075, 8, false), M.dark);
      headGroup.add(tag(hose, 'head'));
    }

    /* CUT-AWAY CARRIER on the active head. A real carrier head covers the wafer
     * completely — the wafer faces down and you never see it. Modelling that
     * faithfully made the wafer unclickable and invisible, which defeats the one
     * thing this view is for: the wafer's colour map IS the predicted removal
     * profile. So the active head is drawn as a hub plus three arms reaching to
     * a retaining ring, leaving the wafer face open. The arms make it read as a
     * deliberate section rather than a missing part. The three idle heads are
     * drawn closed, which is what they actually look like. */
    const isActive = st.i === 0;
    if (isActive) {
      for (let k = 0; k < 3; k++) {
        const a = (k / 3) * Math.PI * 2;
        const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.042, 0.052), M.dark);
        spoke.position.set(Math.cos(a) * 0.16, 0.335, Math.sin(a) * 0.16);
        spoke.rotation.y = -a;
        spoke.castShadow = true;
        headGroup.add(tag(spoke, 'head'));
      }
    } else {
      const shell = new THREE.Mesh(new THREE.CylinderGeometry(0.315, 0.315, 0.10, 48), M.dark);
      shell.position.y = 0.27;
      shell.castShadow = true;
      headGroup.add(tag(shell, 'head'));
    }

    /* RETAINING RING in PPS, not metal. It is the one large non-metallic part
     * on the head, and its pale cream colour against the dark housing is how a
     * process engineer picks it out in a photo; drawn in steel it disappeared
     * into the head. It is also a wear consumable, which is why it is drawn as
     * a thick chamfered ring rather than a thin torus. */
    const retainer = new THREE.Mesh(
      chamferRing(0.295, 0.335, 0.062, 0.006, 80), isActive ? M.pps : M.ppsOff);
    retainer.position.y = 0.215;
    retainer.castShadow = true;
    headGroup.add(tag(retainer, 'head'));

    // slurry slots through the ring's base: how slurry reaches the wafer edge
    if (isActive) {
      const slots = new THREE.InstancedMesh(
        new THREE.BoxGeometry(0.044, 0.016, 0.007), M.dark, 36);
      const o = new THREE.Object3D();
      for (let k = 0; k < 36; k++) {
        const a = (k / 36) * Math.PI * 2;
        o.position.set(Math.cos(a) * 0.315, 0.192, Math.sin(a) * 0.315);
        o.rotation.y = -a;
        o.updateMatrix();
        slots.setMatrixAt(k, o.matrix);
      }
      headGroup.add(tag(slots, 'head'));
    }

    carousel.add(headGroup);
    heads.push({ group: headGroup, station: st.i, active: isActive });
  }
  scene.add(carousel);

  // the wafer under the ACTIVE head: a disc whose vertex colours carry the
  // simulated radial profile
  const WAFER_RINGS = 48;
  const rg = new THREE.RingGeometry(0.0001, 0.295, 96, WAFER_RINGS);
  const colors = new Float32Array(rg.attributes.position.count * 3);
  rg.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const wafer = new THREE.Mesh(rg, M.wafer);
  wafer.rotation.x = -Math.PI / 2;
  wafer.position.y = 0.20;
  heads[0].group.add(tag(wafer, 'wafer'));

  /** Paint the wafer with a radial removal-rate profile. */
  function paintWafer(radiusMm, rateArr) {
    const pos = rg.attributes.position;
    const col = rg.attributes.color;
    if (!rateArr || rateArr.length < 2) {
      for (let i = 0; i < pos.count; i++) col.setXYZ(i, 0.55, 0.60, 0.67);
      col.needsUpdate = true;
      return;
    }
    let lo = Infinity, hi = -Infinity;
    for (const v of rateArr) { if (v < lo) lo = v; if (v > hi) hi = v; }
    const span = (hi - lo) || 1;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), y = pos.getY(i);
      const frac = Math.min(1, Math.sqrt(x * x + y * y) / 0.295);
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

  // ── load cup at the fourth station ──────────────────────────────
  // This is WHY there are four heads for three platens: one station is always
  // loading or unloading while the other three polish.
  const cupSt = STATIONS[LOADCUP_STATION];
  const cup = new THREE.Group();
  cup.position.set(cupSt.x, 0, cupSt.z);
  const cupBowl = new THREE.Mesh(
    new THREE.CylinderGeometry(0.34, 0.30, 0.16, 48, 1, true), M.steel);
  cupBowl.position.y = 0.06;
  cupBowl.castShadow = true;
  cup.add(tag(cupBowl, 'loadcup'));
  const cupFloor = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.30, 0.02, 48), M.dark);
  cupFloor.position.y = -0.02;
  cup.add(tag(cupFloor, 'loadcup'));
  const cupRing = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.022, 10, 56), M.accent);
  cupRing.rotation.x = Math.PI / 2;
  cupRing.position.y = 0.14;
  cup.add(tag(cupRing, 'loadcup'));
  scene.add(cup);

  // ── conditioner sweep arm on each platen ────────────────────────
  const conditioners = [];
  for (const p of platens) {
    const st = STATIONS[p.station];
    // pivot sits just outside the platen, arm sweeps the disk across the radius
    const outward = new THREE.Vector3(st.x, 0, st.z).normalize();
    const pivot = new THREE.Group();
    pivot.position.set(st.x + outward.x * (PLATEN_R + 0.20), 0,
                       st.z + outward.z * (PLATEN_R + 0.20));

    const post = new THREE.Mesh(chamferCyl(0.055, 0.62, 0.008, 28), M.steel);
    post.position.y = 0.26;
    post.castShadow = true;
    pivot.add(tag(post, 'disk'));
    // base flange bolting the sweep column to the deck
    const baseFlange = new THREE.Mesh(chamferCyl(0.10, 0.03, 0.005, 32), M.dark);
    baseFlange.position.y = -0.03;
    pivot.add(tag(baseFlange, 'disk'));
    boltRing(pivot, 'disk', 0.078, -0.010, 6, 0.010, M.steel);
    // sweep motor on top of the column: what drives the oscillation
    const sweepMotor = new THREE.Mesh(chamferCyl(0.062, 0.11, 0.010, 32), M.dark);
    sweepMotor.position.y = 0.625;
    sweepMotor.castShadow = true;
    pivot.add(tag(sweepMotor, 'disk'));

    // rotate the arm group so it reaches back over the platen centre
    const armHolder = new THREE.Group();
    armHolder.rotation.y = Math.atan2(outward.z, outward.x);
    const armMesh = new THREE.Mesh(new THREE.BoxGeometry(0.50, 0.048, 0.095), M.dark);
    armMesh.position.set(-0.25, 0.50, 0);
    armMesh.castShadow = true;
    armHolder.add(tag(armMesh, 'disk'));
    // stiffening cap plate along the arm's top, and the rinse line feeding the
    // disk -- a conditioner is rinsed continuously or it loads up with debris
    const armCap = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.014, 0.060), M.steel);
    armCap.position.set(-0.25, 0.528, 0);
    armHolder.add(tag(armCap, 'disk'));
    const rinse = new THREE.Mesh(new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3([new THREE.Vector3(-0.04, 0.545, 0.030),
                                  new THREE.Vector3(-0.26, 0.552, 0.030),
                                  new THREE.Vector3(-0.44, 0.500, 0.030)]),
      18, 0.0075, 8, false), M.steel);
    armHolder.add(tag(rinse, 'disk'));

    const diskGroup = new THREE.Group();
    diskGroup.position.set(-0.46, 0.42, 0);
    // down-force cylinder, then the shaft, then the disk itself: the load on
    // the conditioner is an input, so the actuator that applies it is drawn
    const downForce = new THREE.Mesh(chamferCyl(0.055, 0.10, 0.008, 32), M.dark);
    downForce.position.y = 0.095;
    downForce.castShadow = true;
    diskGroup.add(tag(downForce, 'disk'));
    const diskShaft = new THREE.Mesh(chamferCyl(0.020, 0.075, 0.003, 20), M.steel);
    diskShaft.position.y = 0.030;
    diskGroup.add(tag(diskShaft, 'disk'));
    const diskBody = new THREE.Mesh(chamferCyl(0.115, 0.05, 0.007, 48), M.steel);
    diskBody.castShadow = true;
    diskGroup.add(tag(diskBody, 'disk'));
    boltRing(diskGroup, 'disk', 0.088, 0.028, 6, 0.008, M.steel);
    const diskFace = new THREE.Mesh(
      new THREE.CylinderGeometry(0.112, 0.112, 0.012, 36), M.diamond);
    diskFace.position.y = -0.028;
    diskGroup.add(tag(diskFace, 'disk'));
    // diamond grit specks, so the disk reads as a diamond disk and not a puck
    const grit = new THREE.InstancedMesh(
      new THREE.OctahedronGeometry(0.005, 0),
      new THREE.MeshStandardMaterial({ color: 0xdfe6ef, metalness: 0.3, roughness: 0.15 }),
      200);
    const m4 = new THREE.Matrix4();
    for (let i = 0; i < 200; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = 0.025 + Math.sqrt(Math.random()) * 0.082;
      m4.makeTranslation(Math.cos(a) * r, -0.033, Math.sin(a) * r);
      grit.setMatrixAt(i, m4);
    }
    diskGroup.add(grit);
    armHolder.add(diskGroup);
    pivot.add(armHolder);
    scene.add(pivot);
    conditioners.push({ pivot, diskGroup, active: p.active });
  }

  // ── slurry: one supply cabinet, a delivery arm over each platen ──
  const supply = new THREE.Group();
  supply.position.set(-2.05, 0, 1.55);

  const cabinet = new THREE.Mesh(new THREE.BoxGeometry(0.60, 0.78, 0.52), M.panel);
  cabinet.position.y = -0.18;
  cabinet.castShadow = cabinet.receiveShadow = true;
  supply.add(tag(cabinet, 'slurry'));

  const drum = new THREE.Mesh(new THREE.CylinderGeometry(0.20, 0.20, 0.52, 32), M.glass);
  drum.position.y = 0.48;
  supply.add(tag(drum, 'slurry'));
  // the fill level is a fixed prop; the slurry's FLOW is animated instead,
  // because flow is a recipe input and fill level is not.
  const drumFill = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.30, 32), M.fluid);
  drumFill.position.y = 0.37;
  supply.add(tag(drumFill, 'slurry'));
  const drumCap = new THREE.Mesh(new THREE.CylinderGeometry(0.215, 0.215, 0.04, 32), M.steel);
  drumCap.position.y = 0.76;
  supply.add(tag(drumCap, 'slurry'));

  const readout = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.17, 0.02), M.accent);
  readout.position.set(0, 0.02, 0.27);
  supply.add(tag(readout, 'slurry'));
  scene.add(supply);

  // delivery arm over each platen, fed from the cabinet
  const nozzles = [];
  for (const p of platens) {
    const st = STATIONS[p.station];
    const outward = new THREE.Vector3(st.x, 0, st.z).normalize();
    const armX = st.x + outward.x * (PLATEN_R + 0.10);
    const armZ = st.z + outward.z * (PLATEN_R + 0.10);
    const tipX = st.x - outward.x * 0.10;
    const tipZ = st.z - outward.z * 0.10;

    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.042, 0.70, 16), M.steel);
    post.position.set(armX, 0.30, armZ);
    post.castShadow = true;
    scene.add(tag(post, 'nozzle'));

    const pts = [
      new THREE.Vector3(-2.05, 0.30, 1.55),
      new THREE.Vector3((armX - 2.05) / 2, 0.80, (armZ + 1.55) / 2),
      new THREE.Vector3(armX, 0.66, armZ),
      new THREE.Vector3(tipX, 0.52, tipZ),
    ];
    const line = new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 44, 0.020, 10, false), M.dark);
    line.castShadow = true;
    scene.add(tag(line, 'nozzle'));

    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.032, 0.085, 18), M.steel);
    tip.position.set(tipX, 0.47, tipZ);
    tip.rotation.x = Math.PI;
    scene.add(tag(tip, 'nozzle'));

    nozzles.push({ x: tipX, y: 0.43, z: tipZ, active: p.active });
  }

  // slurry stream on the ACTIVE platen: count and speed follow the flow rate.
  // Only the simulated platen gets a stream — an idle platen showing flow would
  // claim a process that is not being modelled.
  const activeNozzle = nozzles.find(n => n.active) || nozzles[0];
  const STREAM_N = 150;
  const streamGeom = new THREE.BufferGeometry();
  const sPos = new Float32Array(STREAM_N * 3);
  const sLife = new Float32Array(STREAM_N);
  for (let i = 0; i < STREAM_N; i++) sLife[i] = Math.random();
  streamGeom.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
  const stream = new THREE.Points(streamGeom, new THREE.PointsMaterial({
    color: 0xbfe6ff, size: 0.017, transparent: true, opacity: 0.85,
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
          const c = m.userData.origMat.clone();
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

  /* Motion can be stopped without stopping rendering.
   *
   * The tool is always turning: platens, heads and the conditioner arm all
   * move. That makes any "where is this part on screen" answer perishable —
   * an end-to-end test that asks where the pad is and then clicks there hits
   * whatever rotated into that spot in the meantime, and reports a clickable
   * part as broken. It is also what a user wants when they are trying to
   * click a specific mesh on a moving machine.
   * Rendering continues while frozen, so the view still responds to orbiting.
   */
  let frozen = false;
  function freeze(on) { frozen = !!on; }

  // Simulated time, advanced by dt. NOT clock.elapsedTime: the conditioner
  // sweep is an absolute function of time, so reading the wall clock made the
  // arm keep sweeping while "frozen" and a probed disk position still expired
  // between the probe and the click. Anything periodic must be driven from
  // this accumulator, or freeze() is a half-measure.
  let simT = 0;

  function frame_() {
    // getDelta() is called unconditionally: it RESETS the clock's internal
    // mark, so skipping it while frozen would make the first unfrozen frame
    // advance by the whole frozen duration and the machine would jump.
    const raw = Math.min(0.05, clock.getDelta());
    const dt = frozen ? 0 : raw;
    simT += dt;
    const t = simT;

    // Only the ACTIVE platen and head turn at the recipe's rpm. The idle
    // stations turn slowly, so the tool looks alive without implying that
    // three polish steps are being simulated.
    for (const p of platens) {
      const rpm = p.active ? state.rpmPlaten : state.rpmPlaten * 0.18;
      p.group.rotation.y += (rpm / 60) * 2 * Math.PI * dt;
    }
    for (const h of heads) {
      const rpm = h.active ? state.rpmHead : state.rpmHead * 0.18;
      h.group.rotation.y += (rpm / 60) * 2 * Math.PI * dt;
    }

    if (state.conditioning) {
      for (const c of conditioners) {
        c.diskGroup.rotation.y += (c.active ? 2.2 : 0.5) * Math.PI * dt;
        c.pivot.rotation.y = 0.42 * Math.sin((2 * Math.PI / state.sweepPeriodS) * t);
      }
    }

    // slurry stream on the active platen: more flow = faster and denser
    const speed = 0.25 + (state.flow / 200) * 0.9;
    const visible = Math.round(Math.min(STREAM_N, 20 + (state.flow / 400) * STREAM_N));
    for (let i = 0; i < STREAM_N; i++) {
      if (i >= visible) { sPos[i * 3 + 1] = -99; continue; }
      sLife[i] += dt * speed;
      if (sLife[i] > 1) sLife[i] -= 1;
      const u = sLife[i];
      const drop = 0.33 * u;
      const y = activeNozzle.y - drop;
      const spread = u > 0.82 ? (u - 0.82) * 1.7 : 0;
      const a = i * 2.399963;                       // golden angle, even fan
      sPos[i * 3 + 0] = activeNozzle.x + Math.cos(a) * (0.012 + spread);
      sPos[i * 3 + 1] = Math.max(0.10, y);
      sPos[i * 3 + 2] = activeNozzle.z + Math.sin(a) * (0.012 + spread);
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
    fitView();
  }

  /** Frame the whole machine, whatever the window shape.
   *
   * Fitting to a bounding SPHERE, or to the global axis-aligned bounding BOX,
   * is the textbook move and both are badly wrong here. This tool is a round,
   * flat deck: its AABB is a square prism whose corners contain a lot of empty
   * air, and viewed from a diagonal that phantom air is what gets framed —
   * leaving the machine at roughly a third of the frame, which is exactly the
   * "the 3D model doesn't display properly" report.
   *
   * So fit to the real silhouette: a sub-sampled world-space point cloud of the
   * pickable geometry, projected to NDC. Perspective makes the right distance a
   * fixed point rather than a closed form, so iterate; it converges in 2-3
   * passes. Sub-sampling keeps this a few thousand points, cheap enough to run
   * on every resize.
   *
   * Points come from the pickable machine parts only. The floor disc is 7 units
   * across, and including it would push the camera back far enough to shrink
   * the tool to a speck.
   *
   * The user's viewing DIRECTION is preserved and only the distance re-derived,
   * so a window resize never throws away an orbit.
   */
  let fitPoints = null;
  function collectFitPoints() {
    const pts = [];
    const v = new THREE.Vector3();
    for (const m of pickable) {
      const pos = m.geometry && m.geometry.attributes && m.geometry.attributes.position;
      if (!pos) continue;
      // ~24 samples per mesh: enough to catch the extremes of a 72-segment
      // cylinder without turning a resize into a full vertex walk.
      const stride = Math.max(1, Math.floor(pos.count / 24));
      for (let i = 0; i < pos.count; i += stride) {
        v.fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld);
        pts.push(v.clone());
      }
    }
    return pts;
  }

  function fitView() {
    scene.updateMatrixWorld(true);
    if (!fitPoints || !fitPoints.length) fitPoints = collectFitPoints();
    if (!fitPoints.length) return;
    const box = new THREE.Box3().setFromPoints(fitPoints);
    const centre = box.getCenter(new THREE.Vector3());
    const radius = box.getBoundingSphere(new THREE.Sphere()).radius;
    const dir = camera.position.clone().sub(controls.target);
    if (dir.lengthSq() < 1e-6) dir.set(4.6, 5.2, 5.0);
    dir.normalize();

    const FILL = 0.92;            // leave a little air around the tool
    let dist = radius * 2.2;      // a safe starting point; refined below
    const p = new THREE.Vector3();
    for (let pass = 0; pass < 8; pass++) {
      camera.position.copy(centre).addScaledVector(dir, dist);
      camera.near = Math.max(0.05, dist - radius * 2.0);
      camera.far = dist + radius * 4.0;
      camera.lookAt(centre);
      camera.updateMatrixWorld(true);
      camera.updateProjectionMatrix();
      let extent = 0;
      for (const q of fitPoints) {
        p.copy(q).project(camera);
        extent = Math.max(extent, Math.abs(p.x), Math.abs(p.y));
      }
      if (!isFinite(extent) || extent <= 1e-4) break;
      const next = dist * (extent / FILL);
      if (Math.abs(next - dist) < dist * 0.004) { dist = next; break; }
      dist = next;
    }
    controls.target.copy(centre);
    camera.position.copy(centre).addScaledVector(dir, dist);
    camera.near = Math.max(0.05, dist - radius * 2.0);
    camera.far = dist + radius * 4.0;
    controls.minDistance = Math.min(controls.minDistance, dist * 0.25);
    controls.maxDistance = Math.max(controls.maxDistance, dist * 2.5);
    camera.updateProjectionMatrix();
    controls.update();
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
    setState, paintWafer, resize, probeAt, fitView, freeze,
    parts: PARTS,
    dispose() { cancelAnimationFrame(raf); renderer.dispose(); },
  };
}
