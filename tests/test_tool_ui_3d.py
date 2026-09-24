"""The 3D tool UI, driven by a real browser.

The owner's brief asked for a simulator you operate by clicking parts of a CMP
polisher, not a form. Until now nothing tested that: the engine had 834 tests and
the UI had none, so a broken canvas, a dead raycast or a film selector wired to
nothing would all have shipped silently while every test stayed green.

These tests drive the real page in headless Chromium (SwiftShader, so no GPU is
required) and assert the chain the brief actually asked for:

    the scene renders  ->  parts are clickable  ->  a click opens that part's
    form  ->  changing an input changes the predicted rate

WHAT WAS VERIFIED WHEN THIS WAS WRITTEN

    canvas 1280x808, 1,027,557 lit pixels, zero console errors
    10 clickable parts found by scanning the canvas with the scene's raycaster:
      frame 375 · pad 137 · head 118 · carousel 102 · slurry 96 · nozzle 64
      disk 40 · platen 32 · loadcup 8 · wafer 5
    click slurry -> "Slurry supply unit"   click pad   -> "Polishing pad"
    click disk   -> "Conditioner disk"     click wafer -> "Wafer / film stack"
    film:     cu 5458.5 · w 1091.7 · poly_si 1668.7 · oxide 1559.6 A/min
    abrasive: ceria 4678.7 · alumina 1559.6 · zirconia 1559.6 A/min

Two of those numbers look like a bug and are not. `alumina` and `zirconia`
return the same rate as the pack's own abrasive because no published same-recipe
rate ratio exists for them, and `abrasive_effects.py` refuses to invent one — it
returns no scale factor and warns that the run is a RANKING. The test asserts the
warning is present rather than asserting the rates differ, because demanding a
difference would be demanding a fabricated number.

Why a pixel scan rather than hard-coded coordinates: the parts' screen positions
depend on the camera, so a fixed click point breaks the moment the view changes.
`tool3d.js` exposes `probeAt` (and the page re-exports it as `window.__probe`)
precisely so a test can find a part the way a user's eye does.
"""
from __future__ import annotations

import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
pytest.importorskip("playwright.sync_api",
                    reason="pip install playwright && playwright install chromium")
from playwright.sync_api import sync_playwright  # noqa: E402

CHROMIUM_ARGS = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "cmp_sim.api", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**__import__("os").environ, "CMPSIM_TOKEN": "", "CMPSIM_QUIET": "1"})
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("the API server never came up")
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="module")
def page(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(args=CHROMIUM_ARGS)
        pg = browser.new_page(viewport={"width": 1280, "height": 860})
        errors: list[str] = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f"{server}/tool", wait_until="networkidle")
        pg.wait_for_function("() => !!window.__probe", timeout=30_000)
        pg.wait_for_timeout(3000)
        pg.__dict__["_errors"] = errors
        yield pg
        browser.close()


def _rate(pg) -> float:
    text = pg.evaluate(
        r"""(() => {const m = document.body.innerText.match(
                /([\d,]+\.?\d*)\s*Å\/min/); return m ? m[1] : null;})()""")
    assert text, "no removal rate is displayed on the page"
    return float(text.replace(",", ""))


def _find(pg, part):
    """Screen point that actually hits `part`, via the scene's own raycaster."""
    return pg.evaluate(
        """(part) => {
             const c = document.querySelector('canvas');
             const r = c.getBoundingClientRect();
             for (let y = 0; y < r.height; y += 6)
               for (let x = 0; x < r.width; x += 6)
                 if (window.__probe(r.left + x, r.top + y) === part)
                   return {x: r.left + x, y: r.top + y};
             return null;}""", part)


def _click(pg, part):
    point = _find(pg, part)
    assert point, f"'{part}' is not visible anywhere on the canvas"
    pg.mouse.click(point["x"], point["y"])
    pg.wait_for_timeout(600)


def _simulate(pg):
    pg.evaluate("""(() => {const b = [...document.querySelectorAll('button')]
                     .find(b => /simulate/i.test(b.textContent)); if (b) b.click();})()""")
    pg.wait_for_timeout(2500)


def test_the_scene_renders_and_is_lit(page):
    size = page.evaluate(
        """(() => {const c = document.querySelector('canvas');
             return c ? {w: c.width, h: c.height} : null;})()""")
    assert size and size["w"] > 400, "no canvas on the tool page"

    lit = page.evaluate(
        """(() => {const c = document.querySelector('canvas');
             const gl = c.getContext('webgl2') || c.getContext('webgl');
             if (!gl) return -1;
             const px = new Uint8Array(c.width * c.height * 4);
             gl.readPixels(0, 0, c.width, c.height, gl.RGBA, gl.UNSIGNED_BYTE, px);
             let n = 0;
             for (let i = 0; i < px.length; i += 4)
               if (px[i] + px[i+1] + px[i+2] > 30) n++;
             return n;})()""")
    assert lit > 100_000, (
        f"only {lit} lit pixels — the scene is a black rectangle, which is what "
        "a silently failing WebGL build looks like")


def test_the_page_loads_without_javascript_errors(page):
    assert not page.__dict__["_errors"], page.__dict__["_errors"][:3]


def test_every_data_carrying_part_is_clickable(page):
    hits = page.evaluate(
        """(() => {const c = document.querySelector('canvas');
             const r = c.getBoundingClientRect(), found = {};
             for (let y = 0; y < r.height; y += 10)
               for (let x = 0; x < r.width; x += 10) {
                 const k = window.__probe(r.left + x, r.top + y);
                 if (k) found[k] = (found[k] || 0) + 1;}
             return found;})()""")
    # the parts the brief named: wafer, pad, conditioner disk, slurry supply,
    # and the operation/setup body of the tool
    for part in ("wafer", "pad", "disk", "slurry", "head", "platen",
                 "carousel"):
        assert hits.get(part), (
            f"'{part}' cannot be hit anywhere on screen; the brief asks for it "
            f"to be clickable. Found: {sorted(hits)}")


@pytest.mark.parametrize("part,heading", [
    ("wafer", "Wafer / film stack"),
    ("pad", "Polishing pad"),
    ("disk", "Conditioner disk"),
    ("slurry", "Slurry supply unit"),
])
def test_clicking_a_part_opens_its_own_form(page, part, heading):
    _click(page, part)
    shown = page.evaluate(
        """(() => {const h = document.querySelector('#drawer h2, #drawer h3');
             return h ? h.textContent.trim() : '';})()""")
    assert shown == heading, f"clicking {part} opened '{shown}'"


def test_each_film_is_predicted_separately(page):
    """The brief: films differ by orders of magnitude, never pool them."""
    _click(page, "wafer")
    rates = {}
    for film in ("cu", "w", "poly_si", "oxide"):
        changed = page.evaluate(
            """(f) => {const s = document.querySelector('[data-path="wafer.film"]');
                 if (!s || ![...s.options].some(o => o.value === f)) return false;
                 s.value = f; s.dispatchEvent(new Event('change', {bubbles: true}));
                 return true;}""", film)
        assert changed, f"the film selector offers no '{film}'"
        _simulate(page)
        rates[film] = _rate(page)

    assert len(set(rates.values())) == len(rates), (
        f"two films predict an identical rate, so the selector is not reaching "
        f"the model: {rates}")
    assert rates["cu"] > rates["w"], rates


def test_an_abrasive_without_a_published_ratio_warns_instead_of_guessing(page):
    """alumina returning the pack rate is a refusal, not a bug."""
    _click(page, "slurry")
    page.evaluate(
        """(() => {const s = document.querySelector('[data-path="slurry.abrasive.kind"]');
             s.value = 'alumina';
             s.dispatchEvent(new Event('change', {bubbles: true}));})()""")
    _simulate(page)
    text = page.evaluate("() => document.body.innerText")
    assert "warning" in text.lower(), (
        "swapping in an abrasive with no published same-recipe rate ratio must "
        "warn that the absolute rate is unanchored; silence here would present "
        "the pack's own abrasive rate as if it were alumina's")


def test_the_abrasive_selector_offers_the_families_the_owner_named(page, server):
    import json
    import urllib.request
    with urllib.request.urlopen(f"{server}/api/meta") as fh:
        meta = json.load(fh)
    offered = set(meta["abrasives"])
    for family in ("ceria", "alumina", "zirconia"):
        assert family in offered, f"{family} missing from {sorted(offered)}"
    assert any("silica" in a for a in offered), (
        "no silica variant offered; the corpus splits it into colloidal_silica "
        "and fumed_silica, and at least one must be selectable")
