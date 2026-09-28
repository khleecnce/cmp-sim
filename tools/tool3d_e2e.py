"""Real-browser proof that /tool renders the 3D polisher and its four input
stations drive the physics.

Why a real browser: the viewport is WebGL. A synthetic click dispatched from a
harness may never reach the raycast handler, and an HTTP 200 on /tool says
nothing about whether the canvas has lit pixels. The only evidence that counts
is (a) a non-black canvas, (b) clicking each mesh opening the matching drawer,
(c) an input change moving the predicted rate.

Run:  .venv/bin/python tools/tool3d_e2e.py [--port 8799] [--shot out.png]
Exit 0 only when every check passes; prints one line per check.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request

# The four input stations the owner asked for, and the mesh that opens each.
# The value is the drawer title the mesh MUST open: clicking the pad and
# landing in the operation drawer is a mis-wire, and a test that only asks
# "did a drawer open" scores that as a pass.
STATIONS = {
    "wafer cart / loading": {"loadcup": "Wafer / film stack",
                             "wafer": "Wafer / film stack"},
    "operation": {"carousel": "Operation", "head": "Operation",
                  "platen": "Operation"},
    "slurry supply": {"slurry": "Slurry supply unit",
                      "nozzle": "Slurry supply unit"},
    "polishing unit": {"pad": "Polishing pad", "disk": "Conditioner disk"},
}

# Framing is checked at several window shapes, not one. The machine is a wide
# floor tool; a camera distance that frames it on a 16:10 desktop crops it on a
# portrait phone, because a perspective camera's horizontal fov shrinks with the
# aspect ratio. Both extremes must show it.
VIEWPORTS = [
    ("desktop", 1440, 900),
    ("laptop", 1280, 720),
    ("phone-portrait", 390, 844),
]

# Where can a REAL mouse click this mesh? Two constraints that a raycast alone
# does not know about, both learned from failures that looked like wiring bugs:
#
#  - INTEGER coordinates. The probe answers happily at x = 1119.75, but a mouse
#    click is rounded to a pixel, and on a target as small as a 300 mm wafer in
#    a whole-machine view that rounding lands on the background instead. The
#    click then opened nothing at all.
#  - ON THE CANVAS. Panels float over it, so a point can be on the pad in 3D
#    and under the TOOL PARTS list on screen, where a click never reaches the
#    canvas.
#
# Named rather than inlined because it is needed twice: once to find the spot,
# and again to re-find it if the camera moved in between.
PROBE_JS = """(want) => {
  const c = document.getElementById('scene');
  const r = c.getBoundingClientRect();
  for (let gy = 0.10; gy < 0.96; gy += 0.01)
    for (let gx = 0.04; gx < 0.96; gx += 0.01) {
      const x = Math.round(r.left + r.width * gx);
      const y = Math.round(r.top + r.height * gy);
      if (window.__probe(x, y) !== want) continue;
      if (document.elementFromPoint(x, y) !== c) continue;
      return {x, y};
    }
  return null;
}"""


def _wait_http(url: str, timeout: float = 20.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8799)
    ap.add_argument("--shot", default="/tmp/cmpsim-tool3d.png")
    ap.add_argument("--serve", action="store_true",
                    help="start our own server on --port and stop it after")
    ap.add_argument("--base", default=None,
                    help="test an already-running instance at this URL "
                         "(e.g. a public tunnel) instead of 127.0.0.1:PORT")
    ap.add_argument("--token", default=None,
                    help="CMPSIM_TOKEN of a link-protected instance; appended "
                         "as ?t= on the first request, after which the server's "
                         "cookie authenticates the module imports")
    args = ap.parse_args()

    base = args.base or f"http://127.0.0.1:{args.port}"
    base = base.rstrip("/")
    tool_url = base + "/tool" + (f"?t={args.token}" if args.token else "")
    proc = None
    if args.serve:
        proc = subprocess.Popen(
            [sys.executable, "-m", "cmp_sim.api", "--host", "127.0.0.1",
             "--port", str(args.port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={"CMPSIM_QUIET": "1", "PATH": "/usr/bin:/bin"},
        )
    try:
        if not _wait_http(tool_url):
            print(f"FAIL  server did not answer on {tool_url}")
            return 1
        return _drive(tool_url, args.shot)
    finally:
        if proc is not None:
            proc.terminate()


def _drive(tool_url: str, shot: str) -> int:
    from playwright.sync_api import sync_playwright

    failures: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            # SwiftShader: a CI/headless box has no GPU, and without this the
            # WebGL context creation fails and the page shows its no-WebGL
            # banner -- which would look like a bug in the scene.
            "--use-gl=angle", "--use-angle=swiftshader",
            "--enable-unsafe-swiftshader",
        ])
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console",
                lambda m: errs.append("console: " + m.text)
                if m.type == "error" else None)

        page.goto(tool_url, wait_until="networkidle")
        # boot ends by running one simulation; the readout leaves its em-dash
        page.wait_for_function(
            "() => !/\\u2014/.test(document.getElementById('lrate').textContent)",
            timeout=40000)
        rate0 = page.text_content("#lrate").strip()
        print(f"OK    boot rate = {rate0}")
        if not any(c.isdigit() for c in rate0):
            failures.append("boot produced no numeric rate")

        # (a) is the canvas actually lit, or a black rectangle?
        lit = page.evaluate("""() => {
          const c = document.getElementById('scene');
          const gl = c.getContext('webgl2') || c.getContext('webgl');
          if (!gl) return null;
          const px = new Uint8Array(4 * c.width * c.height);
          gl.readPixels(0, 0, c.width, c.height, gl.RGBA, gl.UNSIGNED_BYTE, px);
          let bright = 0;
          for (let i = 0; i < px.length; i += 4)
            if (px[i] + px[i+1] + px[i+2] > 150) bright++;
          return {pixels: c.width * c.height, bright};
        }""")
        if not lit:
            failures.append("no WebGL context on #scene")
            print("FAIL  no WebGL context")
        else:
            frac = lit["bright"] / max(1, lit["pixels"])
            print(f"OK    canvas lit {lit['bright']}/{lit['pixels']} "
                  f"= {frac:.1%}")
            # The UI is deliberately a dark fab console: most of the frame is
            # background by design, so a high lit-fraction is the wrong bar.
            # This check exists only to separate "a machine is drawn" from "the
            # context died and the canvas is black" -- the framing checks below
            # are what actually judge how much of the view the tool occupies.
            if frac < 0.005:
                failures.append(f"canvas effectively black ({frac:.2%} lit)")
        if page.locator(".nowebgl").count():
            failures.append("no-WebGL fallback banner is visible")

        # (b) click every mesh; a station passes when ANY of its meshes opens
        # the RIGHT drawer. Freeze the machine first: platens, heads and the
        # conditioner arm all turn, so the answer to "where is the pad" expires
        # within a frame and the click lands on whatever rotated into the spot.
        page.evaluate("() => window.__freeze && window.__freeze(true)")
        page.wait_for_timeout(120)
        hits: dict[str, bool] = {}
        for station, meshes in STATIONS.items():
            ok = False
            for mesh, want_title in meshes.items():
                spot = page.evaluate(PROBE_JS, mesh)
                if not spot:
                    print(f"      {mesh:9s}: not on screen")
                    continue
                # Blank the title BEFORE clicking. Otherwise "which drawer is
                # open" is answered by a string that is already correct-looking
                # from the previous mesh, and a click that never reached the
                # canvas scores as the previous station's pass -- that is
                # exactly how a remote run reported the slurry cabinet as
                # opening the operation form while the identical local run
                # passed. A stale reading must be unmistakable, not plausible.
                page.evaluate("() => { document.getElementById('dtitle')"
                              ".textContent = '<<stale>>'; }")
                # RE-CONFIRM the spot in the same breath as the click. Opening
                # and closing the previous drawer resizes the stage, which
                # re-fits the camera on a timer -- so a spot found a moment ago
                # can be off the mesh by the time the mouse gets there even
                # with the machine frozen. On a big part that slop is
                # invisible; on the wafer, which is ~16 clickable pixels in a
                # whole-machine view, it is the difference between opening the
                # form and clicking the background. Cheap check, and it names
                # the cause instead of reporting "unclickable".
                still = page.evaluate("(s) => window.__probe(s.x, s.y)", spot)
                if still != mesh:
                    page.wait_for_timeout(500)
                    spot = page.evaluate(PROBE_JS, mesh)
                    if not spot:
                        print(f"      {mesh:9s}: moved off-screen before the click")
                        continue
                page.mouse.click(spot["x"], spot["y"])
                # Wait for the ANSWER to arrive rather than for a fixed 250 ms:
                # over a public tunnel the drawer's contents can take longer
                # than any sleep tuned on localhost.
                try:
                    page.wait_for_function(
                        "() => document.getElementById('dtitle').textContent"
                        " !== '<<stale>>'", timeout=5_000)
                except Exception:
                    pass
                opened = page.evaluate(
                    "() => document.getElementById('drawer')"
                    ".classList.contains('open')")
                title = (page.text_content("#dtitle") or "").strip()
                fields = page.evaluate(
                    "() => document.querySelectorAll('#dbody [data-path]').length")
                right = want_title.lower() in title.lower()
                verdict = "OK  " if (opened and fields and right) else "FAIL"
                print(f"{verdict}  {mesh:9s} -> drawer={opened} "
                      f"title={title!r} fields={fields} "
                      f"expected~{want_title!r}")
                if opened and fields > 0 and right:
                    ok = True
                elif title == "<<stale>>":
                    failures.append(
                        f"{mesh}: the click never reached the page (the drawer "
                        f"did not re-render within 5 s)")
                elif opened and not right:
                    failures.append(
                        f"{mesh} opened {title!r}, expected {want_title!r}")
                page.evaluate(
                    "() => document.getElementById('drawerclose')?.click()")
                # Wait for the drawer to actually BE closed, then settle:
                # closing it widens the stage, which fires a resize and
                # re-frames the camera on a 240 ms timer. Probing before that
                # lands makes the next click hit a stale pixel and open the
                # wrong drawer -- which looked like a wiring bug and was not
                # one. The close is confirmed rather than assumed, because a
                # fixed sleep that is generous on localhost is not generous
                # over a tunnel.
                try:
                    page.wait_for_function(
                        "() => !document.getElementById('drawer')"
                        ".classList.contains('open')", timeout=5_000)
                except Exception:
                    pass
                page.wait_for_timeout(700)
            hits[station] = ok
            if not ok:
                failures.append(f"station {station!r} has no working input")
        print("      stations: " + json.dumps(hits))
        page.evaluate("() => window.__freeze && window.__freeze(false)")

        # (b2) framing: the machine must actually fill the frame at every window
        # shape, and must not be cut off by the edges. Measured with the scene's
        # own raycast over a grid -- a screenshot looked "fine" on the one
        # desktop size it was tuned at while the tool was a small dark blob on a
        # phone. Coverage answers "is it big enough"; edge contact answers "is it
        # cropped"; both are needed (a huge, half-off-screen tool covers a lot).
        # The deck and cabinets ('frame') COUNT -- they are the machine's body,
        # and excluding them measures only the small parts sitting on top, which
        # scores a perfectly framed tool as too small.
        for name, w, h in VIEWPORTS:
            page.set_viewport_size({"width": w, "height": h})
            page.wait_for_timeout(500)
            page.evaluate("() => window.__freeze && window.__freeze(true)")
            g = page.evaluate("""() => {
              const c = document.getElementById('scene');
              const r = c.getBoundingClientRect();
              let hit = 0, n = 0, x0 = 1, x1 = 0, y0 = 1, y1 = 0, edge = 0;
              for (let gy = 0.02; gy < 0.99; gy += 0.02)
                for (let gx = 0.02; gx < 0.99; gx += 0.02) {
                  n++;
                  const p = window.__probe(r.left + r.width*gx, r.top + r.height*gy);
                  if (!p) continue;
                  hit++;
                  x0 = Math.min(x0, gx); x1 = Math.max(x1, gx);
                  y0 = Math.min(y0, gy); y1 = Math.max(y1, gy);
                  if (gx < 0.04 || gx > 0.97 || gy < 0.04 || gy > 0.97) edge++;
                }
              return {cover: hit / n, w: x1 - x0, h: y1 - y0, edge};
            }""")
            page.evaluate("() => window.__freeze && window.__freeze(false)")
            # Thresholds, mirroring tests/test_tool_ui_3d.py. Judge the LARGER
            # span, not both dimensions: the machine is wide and flat, so on a
            # tall phone it can never fill the height and on a wide desktop it
            # cannot fill the width. And judge silhouette DENSITY, not share of
            # the whole frame -- a frame-share floor punishes the aspect ratio
            # rather than the framing. Calibrated against the bug: the previous
            # bounding-sphere fit scored span 0.38-0.40 everywhere.
            span = max(g["w"], g["h"])
            density = g["cover"] / max(1e-6, g["w"] * g["h"])
            ok = span >= 0.60 and density >= 0.30 and g["edge"] == 0
            print(f"{'OK  ' if ok else 'FAIL'}  framing {name:15s} "
                  f"{w}x{h}: cover={g['cover']:.1%} density={density:.0%} "
                  f"span={g['w']:.2f}x{g['h']:.2f} edge_hits={g['edge']}")
            if g["edge"]:
                failures.append(f"framing {name}: machine touches the viewport "
                                f"edge ({g['edge']} grid hits) -- cropped")
            elif not ok:
                failures.append(f"framing {name}: span {span:.2f}, "
                                f"density {density:.0%}")
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(400)

        # (c) a process-condition change must move the number
        page.evaluate("""() => {
          const el = document.querySelector('[data-part=carousel]')
                  || [...document.querySelectorAll('#legendbtns button')]
                       .find(b => /arousel|laten/.test(b.textContent));
          el && el.click();
        }""")
        page.wait_for_timeout(300)
        moved = None
        if page.locator('input[data-path="tool.pressure_psi"]').count():
            page.fill('input[data-path="tool.pressure_psi"]', "6")
            page.dispatch_event('input[data-path="tool.pressure_psi"]', "change")
            page.click("#dgo")
            page.wait_for_timeout(3000)
            moved = page.text_content("#lrate").strip()
            print(f"OK    6 psi rate = {moved} (was {rate0})")
            if moved == rate0:
                failures.append("pressure change did not move the rate")
        else:
            failures.append("tool.pressure_psi input not reachable")

        # (d) the model must be VIEWABLE and EDITABLE from the UI, and an edit
        # must re-predict. This is the owner's structural requirement in its
        # observable form: the physics lives in the packs, the browser only
        # reads it, and an owner-supplied edit travels the ordinary override
        # path (so it is reported as owner-supplied and can never pass for a
        # sourced value). Checking that the sheet merely OPENS would be the
        # §"conversion is not reach" error -- grade it by whether the rate
        # moves.
        #
        # Use kp_m_per_pa as the control, because it has an ANALYTIC answer:
        # the Preston coefficient multiplies every rate, so doubling it must
        # exactly double the predicted rate. A threshold ("the number changed")
        # would pass on any wiring that merely perturbs something; an exact
        # factor cannot. Anything else moving means the edit reached more than
        # the constant it named.
        if page.locator("#showmodel").count():
            page.click("#showmodel")
            page.wait_for_selector("#sheetbody [data-param]", timeout=15_000)
            nconst = page.evaluate(
                "() => document.querySelectorAll('#sheetbody table tr').length - 1")
            nsrc = page.evaluate(
                "() => document.querySelectorAll('#sheetbody details').length")
            print(f"OK    model sheet: {nconst} constants, {nsrc} with sources")
            if nconst < 10:
                failures.append(f"model sheet lists only {nconst} constants")
            if nsrc < 1:
                failures.append("model sheet shows no sources -- a constant "
                                "without provenance is indistinguishable "
                                "from an invented one")
            kp = page.locator('#sheetbody input[data-param="kp_m_per_pa"]')
            if kp.count():
                base = float((page.text_content("#lrate") or "")
                             .replace("\u00c5/min", "").strip() or "nan")
                kp0 = float(kp.input_value())
                kp.fill(repr(kp0 * 2))
                kp.dispatch_event("change")
                page.click("#reapply")
                page.wait_for_selector("#sheetbody [data-param]", timeout=20_000)
                page.wait_for_timeout(1500)
                after = float((page.text_content("#lrate") or "")
                              .replace("\u00c5/min", "").strip() or "nan")
                ratio = after / base if base else float("nan")
                edited = page.evaluate(
                    "() => !!document.querySelector('#sheetbody .badge.rank')")
                print(f"OK    Kp x2 -> rate {base:.1f} -> {after:.1f} "
                      f"= {ratio:.4f}x (expected 2.0000), "
                      f"marked edited={edited}")
                # 0.5% tolerance: the readout is rounded to 0.1 A/min, which on
                # a slow film is a real fraction of the number.
                if not (1.99 <= ratio <= 2.01):
                    failures.append(
                        f"editing kp_m_per_pa x2 moved the rate {ratio:.4f}x, "
                        f"not 2x -- Preston is multiplicative, so any other "
                        f"factor means the edit did not reach the solver "
                        f"cleanly")
                if not edited:
                    failures.append(
                        "an owner-edited constant is not marked 'edited' in "
                        "the sheet -- it would read as a sourced value")
                page.click("#clearedits")
                page.wait_for_selector("#sheetbody [data-param]", timeout=15_000)
                page.click("#reapply")
                page.wait_for_timeout(1500)
                back = float((page.text_content("#lrate") or "")
                             .replace("\u00c5/min", "").strip() or "nan")
                print(f"OK    clear edits -> rate back to {back:.1f} "
                      f"(was {base:.1f})")
                if abs(back - base) > max(0.2, 0.005 * base):
                    failures.append(
                        f"clearing edits left the rate at {back}, not {base}")
            else:
                failures.append("kp_m_per_pa is not editable in the model sheet")
            page.evaluate("() => document.getElementById('sheetclose')?.click()")
            page.wait_for_timeout(300)
        else:
            failures.append("no 'model parameters & sources' button in the "
                            "operation drawer -- the model is not inspectable "
                            "from the UI")

        page.evaluate("() => document.getElementById('drawerclose')?.click()")
        page.wait_for_timeout(400)
        page.screenshot(path=shot)
        print(f"OK    screenshot {shot}")

        hard = [e for e in errs if "favicon" not in e]
        if hard:
            print("WARN  page errors: " + json.dumps(hard[:5]))
        browser.close()

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  - " + f)
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
