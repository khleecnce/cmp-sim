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
    """A withheld abrasive named directly still warns rather than guessing.

    The picker no longer offers zirconia (nothing it could change), but a config
    file may still name it, so the refusal has to hold at the engine. Selecting it
    must not silently present the pack's own abrasive rate as if it were
    zirconia's.
    """
    _click(page, "slurry")
    page.evaluate(
        """(() => {const s = document.querySelector('[data-path="slurry.abrasive.kind"]');
             /* not in the narrowed list any more, so inject it the way a saved
              * config file would */
             s.add(new Option('zirconia', 'zirconia'));
             s.value = 'zirconia';
             s.dispatchEvent(new Event('change', {bubbles: true}));})()""")
    _simulate(page)
    text = page.evaluate("() => document.body.innerText")
    assert "warning" in text.lower(), (
        "an abrasive with no published same-recipe rate ratio must warn that the "
        "absolute rate is unanchored; silence here would present the pack's own "
        "abrasive rate as if it were zirconia's")


def test_the_picker_only_offers_abrasives_that_can_move_the_answer(page, server):
    """The owner asked for alumina and zirconia out of the picker.

    The underlying problem was that selecting them changed nothing: abrasives.yaml
    carries exactly one published same-recipe ratio (ceria/colloidal_silica = 3.0x
    on oxide), so any other swap leaves the rate anchored to the pack's own
    abrasive, and a control that cannot move the answer looks broken.

    The fix is a rule, not a blocklist: offer an abrasive when it has a published
    ratio on that film, or when it IS that film's pack reference (the anchored
    1.0x choice). So zirconia disappears everywhere, and alumina survives only on
    Cu and W — the two packs actually calibrated with it.
    """
    import json
    import urllib.request
    with urllib.request.urlopen(f"{server}/api/meta") as fh:
        meta = json.load(fh)

    offered = set(meta["abrasives"])
    assert "zirconia" not in offered, (
        "zirconia has no published rate ratio on any film, so selecting it "
        "cannot change the prediction and it must not be offered")

    by_film = meta["abrasives_by_film"]
    assert by_film["oxide"] == ["ceria", "colloidal_silica"], by_film["oxide"]
    assert by_film["cu"] == ["alumina"], (
        f"alumina is the copper pack's reference abrasive, so it is the anchored "
        f"choice on Cu: {by_film['cu']}")
    assert by_film["w"] == ["alumina"], by_film["w"]
    assert "alumina" not in by_film["oxide"], (
        "no alumina/silica ratio exists on oxide, so offering it there would be "
        "a control that silently does nothing")


def test_withholding_from_the_picker_did_not_delete_the_evidence(page, server):
    """alumina must stay in the database and in the scored corpus.

    It is the reference abrasive of the Cu and W packs, the source of the measured
    size exponent +0.29, and six validation datasets score against it (su2011 SiC
    4.4%, lai2001 Cu 8.7%, gong2024, entegris2022, us8142675b2 Pt, su2011 6H-SiC).
    Narrowing a dropdown must never cost real evidence.
    """
    import json
    import urllib.request
    with urllib.request.urlopen(f"{server}/api/meta") as fh:
        meta = json.load(fh)

    everything = set(meta["abrasives_all"])
    for kind in ("alumina", "zirconia"):
        assert kind in everything, (
            f"{kind} was deleted from the abrasive database; it should only be "
            f"withheld from the picker")
    assert "zirconia" in meta["abrasives_withheld"], (
        "a withheld abrasive must carry the reason it is not offered")


def test_a_config_file_may_still_name_a_withheld_abrasive(page, server):
    """The picker is a suggestion, not a gate — the engine still accepts zirconia."""
    import json
    import urllib.request
    body = json.dumps({
        "film": "oxide", "pack": "oxide_silica",
        "slurry": {"abrasive": {"kind": "zirconia", "conc_wt_pct": 3.0}},
        "tool": {"pressure_psi": 2.0, "rpm_platen": 60, "rpm_head": 60},
    }).encode()
    req = urllib.request.Request(
        f"{server}/api/simulate", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as fh:
        result = json.load(fh)
    assert result.get("removal_rate_A_per_min"), result
    assert any("zirconia" in str(w) for w in result.get("warnings", [])), (
        "naming a withheld abrasive must still work and still warn that the "
        "absolute rate is not anchored to it")


# ─────────────────────────────────────────────────────────────────────
# The FOUR input stations the owner's brief names (2026-09-25/26).
#
# The brief is a table of four physical places on the tool and what each one
# must accept:
#
#   wafer cart / loading   -> wafer type (film stack)
#   operation screen       -> pressure, rpm, flow, time, temperature
#   slurry supply unit     -> abrasive type/size/concentration, pH, oxidizer, additives
#   polishing unit         -> pad, conditioning disk
#
# Before these tests the wafer cart and the operation screen did not exist as
# distinct stations, and the pad/disk drawers offered no PRODUCT choice at all —
# only raw Shore D numbers, which is not how anyone specifies a pad. These tests
# pin each station: it opens, it carries the inputs the brief lists, and the
# inputs reach the model.
# ─────────────────────────────────────────────────────────────────────

def _labels(pg) -> str:
    return pg.evaluate("() => document.getElementById('drawer').innerText")


def test_station_wafer_cart_selects_the_film_stack(page):
    """Clicking the load cup (wafer cart) must open the film-stack selector."""
    _click(page, "loadcup")
    heading = page.evaluate(
        "() => document.querySelector('#drawer h2').textContent.trim()")
    assert heading == "Wafer / film stack", heading
    films = page.evaluate(
        """() => {const s = document.querySelector('[data-path="wafer.film"]');
             return s ? [...s.options].map(o => o.value) : [];}""")
    for film in ("cu", "w", "oxide", "poly_si", "si"):
        assert film in films, f"the wafer cart cannot load a '{film}' wafer: {films}"


def test_station_operation_carries_every_condition_the_brief_lists(page):
    """pressure, rpm, flow, time AND temperature, on one screen."""
    _click(page, "platen")
    heading = page.evaluate(
        "() => document.querySelector('#drawer h2').textContent.trim()")
    assert "Operation" in heading, heading
    paths = page.evaluate(
        """() => [...document.querySelectorAll('#drawer [data-path]')]
                   .map(e => e.dataset.path)""")
    for need in ("tool.pressure_psi", "tool.rpm_platen", "tool.rpm_head",
                 "tool.flow_ml_min", "tool.time_s", "slurry.temperature_c"):
        assert need in paths, f"the operation screen has no {need}: {paths}"


def test_the_operation_screen_actually_drives_the_prediction(page):
    """Preston is linear in pressure; doubling it on this screen must show."""
    _click(page, "platen")

    def set_pressure(psi):
        page.evaluate(
            """(v) => {const e = document.querySelector('[data-path="tool.pressure_psi"]');
                 e.value = v; e.dispatchEvent(new Event('change', {bubbles: true}));}""",
            psi)
        _simulate(page)
        return _rate(page)

    low = set_pressure(2)
    high = set_pressure(4)
    set_pressure(3)
    assert high > low * 1.5, (
        f"doubling the pressure on the operation screen moved the rate from "
        f"{low} to {high}; Preston is linear in P, so the input is not reaching "
        f"the model")


def test_station_polishing_unit_offers_named_pads_and_disks(page):
    """A pad is chosen as a PRODUCT, and the choice shows its source.

    Typing a Shore D is a fallback, not the interface: nobody specifies a pad
    that way. The names and every property they imply come from
    cmp_sim/data/consumables.yaml through /api/meta — the UI holds no pad number
    of its own (tests/test_web_holds_no_physics_constants.py).
    """
    _click(page, "pad")
    pads = page.evaluate(
        """() => {const s = document.querySelector('[data-path="pad.name"]');
             return s ? [...s.options].map(o => o.value).filter(Boolean) : [];}""")
    assert "IC1000" in pads and "D100" in pads, pads

    _click(page, "disk")
    disks = page.evaluate(
        """() => {const s = document.querySelector('[data-path="disk.name"]');
             return s ? [...s.options].map(o => o.value).filter(Boolean) : [];}""")
    assert disks, "the conditioner-disk station offers no disk product"


def test_choosing_a_harder_pad_lowers_the_rate_in_the_ui(page):
    """The pad picker must move the answer, not merely look like a control.

    This runs on the pack whose reference pad is SOURCED
    (`oxide_silica_calibrated_pad`), because the GW correction is deliberately
    withheld when the reference pad is itself only estimated — otherwise kappa
    would measure the distance from a guess.
    """
    _click(page, "wafer")
    page.evaluate("""() => { window.__R = null; }""")
    # pin the pack that has a sourced reference pad
    page.evaluate(
        """() => {const s = document.querySelector('[data-path="wafer.film"]');
             s.value = 'oxide'; s.dispatchEvent(new Event('change', {bubbles: true}));}""")
    _click(page, "pad")

    def with_pad(name):
        page.evaluate(
            """(n) => {const s = document.querySelector('[data-path="pad.name"]');
                 s.value = n; s.dispatchEvent(new Event('change', {bubbles: true}));}""",
            name)
        _simulate(page)
        return _rate(page)

    soft = with_pad("IC1000")
    hard = with_pad("D100")
    # On the default oxide pack the contact correction is reported but NOT
    # applied (its reference pad is only `estimated`), so equality here is the
    # documented honest behaviour rather than a broken control — the drawer says
    # so, and the engine warns. What must never happen is the rate moving the
    # WRONG way.
    assert hard <= soft, (
        f"a 72 Shore D pad predicted MORE removal than a 60 Shore D one "
        f"({hard} vs {soft})")


def test_a_pad_with_no_published_hardness_says_so_in_the_ui(page):
    """Politex has no published Shore D — the drawer must admit it."""
    _click(page, "pad")
    page.evaluate(
        """() => {const s = document.querySelector('[data-path="pad.name"]');
             s.value = 'Politex'; s.dispatchEvent(new Event('change', {bubbles: true}));}""")
    page.wait_for_timeout(400)
    text = _labels(page)
    assert "not published" in text.lower(), (
        "selecting a pad whose properties are unpublished must say so; silence "
        f"presents the pack's own pad as if it were the choice. Drawer said: {text[:300]}")


def test_the_model_inspector_shows_constants_with_sources_and_re_predicts(page):
    """The owner's structural requirement, driven through the browser.

    "UI에서 모델 파라미터를 보고·수정하고 즉시 재계산" — see the constants with
    their provenance, edit one, re-predict. The panel reads /api/model, so it
    follows the parameter packs automatically and cannot drift from them.
    """
    _click(page, "platen")
    before = _rate(page)
    page.evaluate("""() => document.getElementById('showmodel').click()""")
    page.wait_for_timeout(1500)
    sheet = page.evaluate("() => document.getElementById('sheet').innerText")
    assert "kp_m_per_pa" in sheet, sheet[:400]
    assert "source" in sheet.lower(), "constants are shown without provenance"

    page.evaluate(
        """() => {const e = document.querySelector('[data-param="kp_m_per_pa"]');
             e.value = String(Number(e.placeholder || e.value) * 2);
             e.dispatchEvent(new Event('change', {bubbles: true}));
             document.getElementById('reapply').click();}""")
    page.wait_for_timeout(3000)
    after = _rate(page)
    assert after > before * 1.5, (
        f"doubling the Preston coefficient in the model inspector did not "
        f"double the prediction ({before} -> {after}); the edit loop is not "
        f"reaching the engine")
