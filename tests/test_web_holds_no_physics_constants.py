"""The simulator's SHELL must hold no physics.

The owner's instruction (2026-09-26) is explicit: the 3D view, the panels and the
routes are one thing, and the physical model is another. Physics — equations and
constants — lives in ``cmp_sim/models/`` and ``cmp_sim/data/*.yaml``; the web
layer reads it and never carries its own copy. Fixing the model must not require
touching the UI, and vice versa.

A convention alone will not hold that. The 3D view already had, before this test,
a hard-coded groove pitch of 2.0 mm and width of 0.5 mm in ``tool.html`` — real
pad geometry, sitting in a presentation file, disagreeing with the 3.05 mm /
0.6 mm the catalogue publishes with sources. Nothing failed when they diverged,
because nothing was watching. These tests watch.

WHAT COUNTS AS A VIOLATION

Not "any number". A CSS pixel, a colour, a poll interval and a camera position
are properties of the picture, and forbidding those would make the test useless
noise. A violation is a number the ENGINE also owns:

  * a physics constant key from any parameter pack appearing in the web layer
    next to a literal number,
  * a pad or disk property from the consumables catalogue hard-coded, and
  * the removal-rate scale itself: Preston coefficients, Angstrom-per-minute
    conversions, activation energies.

The check is therefore keyed on the PACK's own vocabulary, which means it grows
automatically: adding a constant to a pack immediately makes hard-coding that
constant in the UI a failure, with no test edit needed.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "cmp_sim" / "web"

#: Every file the browser loads. tool3d.js is a scene builder, so its geometry
#: literals are legitimate; it is still checked for PACK keys.
WEB_FILES = sorted(list(WEB.glob("*.html")) + list(WEB.glob("vendor/tool3d.js")))


def _web_text() -> dict:
    return {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
            for p in WEB_FILES}


def _pack_constant_keys() -> set:
    """Physics constant names declared by any parameter pack.

    Operating conditions are EXCLUDED even though some share a name with a pack
    key (``pressure_psi``, ``rpm_platen``): those are what the machine is set to,
    the UI is the thing that sets them, and a default of 3 psi in the recipe
    object is a starting operating point rather than a claim about physics. What
    is forbidden is the UI carrying a value the MODEL owns.
    """
    from cmp_sim.core.params import available_packs, load_pack
    from cmp_sim.core.state import (Abrasive, Additive, Disk, Pad, Slurry, Tool,
                                    Wafer)

    operating = set()
    for cls in (Abrasive, Additive, Disk, Pad, Slurry, Tool, Wafer):
        operating.update(getattr(cls, "__dataclass_fields__", {}))

    keys = set()
    for name in available_packs():
        try:
            pack = load_pack(name)
        except Exception:                                 # pragma: no cover
            continue
        for key, param in pack.params.items():
            if isinstance(param.value, (int, float)) and key not in operating:
                keys.add(key)
    return keys


def test_the_web_layer_exists_and_is_being_checked():
    """A rename that empties the glob must fail loudly, not pass vacuously."""
    assert WEB_FILES, f"no web files found under {WEB}"
    names = {p.name for p in WEB_FILES}
    assert {"tool.html", "index.html", "tool3d.js"} <= names, sorted(names)


def test_no_pack_constant_is_assigned_a_literal_in_the_web_layer():
    """`kp_m_per_pa: 1e-13` in a .html is a second source of truth.

    Reading a constant is fine and is the point — the UI displays
    `/api/model`'s output. ASSIGNING one a number is not.
    """
    keys = _pack_constant_keys()
    assert len(keys) > 50, f"only {len(keys)} pack constants found; loader broken?"

    offenders = []
    for path, text in _web_text().items():
        for key in keys:
            # `key: 123`, `key = 123`, `key":123` — an assignment of a literal
            for m in re.finditer(
                    rf"""["']?{re.escape(key)}["']?\s*[:=]\s*(-?\d[\d.eE+_-]*)""",
                    text):
                offenders.append(f"{path}: {key} = {m.group(1)}")
    assert not offenders, (
        "a physics constant is hard-coded in the web layer, so the model now has "
        "two sources of truth and a model fix would silently disagree with the "
        "UI:\n  " + "\n  ".join(sorted(offenders)) +
        "\nRead it from /api/model instead.")


def test_no_catalogued_pad_or_disk_property_is_hard_coded_in_the_web_layer():
    """The exact bug this test was written for.

    tool.html carried `groove_pitch_mm: 2.0` and `groove_width_mm: 0.5` while
    consumables.yaml publishes 3.05 mm / 0.6 mm for IC1000 with sources (Mu 2016,
    the inherited base pack). The picture was drawing a pad nobody measured.
    """
    from cmp_sim.pad.catalog import DISK_FIELD_MAP, PAD_FIELD_MAP

    props = set(PAD_FIELD_MAP.values()) | set(DISK_FIELD_MAP.values())
    offenders = []
    for path, text in _web_text().items():
        for prop in props:
            for m in re.finditer(
                    rf"""["']?{re.escape(prop)}["']?\s*[:=]\s*(-?\d[\d.eE+_-]*)""",
                    text):
                offenders.append(f"{path}: {prop} = {m.group(1)}")
    assert not offenders, (
        "a pad/disk property is hard-coded in the web layer instead of coming "
        "from the consumables catalogue via /api/meta:\n  "
        + "\n  ".join(sorted(offenders)))


def test_every_pad_and_disk_property_the_ui_can_show_comes_from_the_catalogue():
    """The catalogue is reachable from the API the UI actually calls."""
    from cmp_sim.api import _meta

    meta = _meta()
    assert meta["pads"], "the UI has no pads to offer"
    assert meta["disks"], "the UI has no conditioner disks to offer"
    for name, entry in meta["pads"].items():
        for prop, value in entry["published"].items():
            assert prop in entry["sources"], (
                f"pad {name}.{prop} = {value} is offered to the UI with no "
                f"source; every number shown must carry one")
            assert entry["sources"][prop]["source"], (
                f"pad {name}.{prop} has an empty source string")


def test_a_pad_with_no_published_property_cannot_move_the_rate_and_says_so():
    """Politex has no published Shore D anywhere in the sources held here.

    The honest behaviour is the one `abrasive_effects` already established for
    unanchored abrasives: change nothing, and warn. Inventing a Shore D from a
    Shore A conversion table (non-linear, approximate) to make the control feel
    responsive would be a fabricated number reaching the rate.
    """
    from cmp_sim.api import run_recipe

    base = {"model": "full", "wafer": {"film": "oxide"},
            "slurry": {"pack": "oxide_silica_calibrated_pad"},
            "tool": {"pressure_psi": 3.0}}
    plain = run_recipe(base)
    soft = run_recipe({**base, "pad": {"name": "Politex"}})

    assert soft["removal_rate_A_per_min"] == pytest.approx(
        plain["removal_rate_A_per_min"], rel=1e-9), (
        "selecting Politex changed the rate, which means a Shore D was "
        "manufactured for it somewhere — no source held here publishes one")
    assert any("Politex" in w and "not published" in w.lower()
               for w in soft["warnings"]), (
        "the run must SAY that the selection could not reach the rate; silence "
        "presents the pack's own pad as if it were the chosen one")


def test_choosing_the_packs_own_calibration_pad_does_not_rescale_the_rate():
    """kappa must be exactly 1.0 for the pad the Kp was calibrated on.

    Measured when this was wired: selecting IC1000 on
    `oxide_silica_calibrated_pad` rescaled the rate 1.9x, because the
    catalogue's published Shore D 60 goes through the Qi correlation to
    E* = 2.5e8 Pa while the pack's reference pad is the 1.0e9 Pa Jeong 2024
    measured on that same physical pad. kappa was reporting the disagreement
    between two descriptions of one pad as a physical pad difference — a fitted
    constant arriving through a dropdown.
    """
    from cmp_sim.api import run_recipe

    base = {"model": "full", "wafer": {"film": "oxide"},
            "slurry": {"pack": "oxide_silica_calibrated_pad"},
            "tool": {"pressure_psi": 3.0}}
    plain = run_recipe(base)
    named = run_recipe({**base, "pad": {"name": "IC1000"}})

    assert named["factors"]["kappa_contact"] == pytest.approx(1.0), (
        "kappa is not 1.0 for the pack's own calibration pad: "
        f"{named['factors']['kappa_contact']}")
    assert named["removal_rate_A_per_min"] == pytest.approx(
        plain["removal_rate_A_per_min"], rel=1e-9)
    # and the pad's published properties DID arrive — this is not a no-op path
    assert named["consumables"]["filled"]["shore_d"] == 60.0


def test_a_harder_pad_than_the_reference_lowers_the_rate():
    """A pad selection that IS anchored must still move the answer.

    Otherwise the two tests above would be satisfiable by a picker that does
    nothing at all. D100 (72 Shore D, US10562149 Table 1B) is stiffer than the
    IC1000 reference, so GW contact area falls and so does the rate.
    """
    from cmp_sim.api import run_recipe

    base = {"model": "full", "wafer": {"film": "oxide"},
            "slurry": {"pack": "oxide_silica_calibrated_pad"},
            "tool": {"pressure_psi": 3.0}}
    ref = run_recipe({**base, "pad": {"name": "IC1000"}})
    hard = run_recipe({**base, "pad": {"name": "D100"}})

    assert hard["removal_rate_A_per_min"] < ref["removal_rate_A_per_min"], (
        f"a 72 Shore D pad did not reduce the rate against a 60 Shore D "
        f"reference: {hard['removal_rate_A_per_min']} vs "
        f"{ref['removal_rate_A_per_min']}")


def test_an_unnamed_pad_leaves_every_existing_answer_untouched():
    """The catalogue must not act on a dataclass DEFAULT.

    `Pad.name` defaults to "IC1000" for backward compatibility. If the catalogue
    filled IC1000's published Shore D and grooves into every recipe that never
    mentioned a pad, every stored example and every validation dataset would
    shift on the strength of a default — a guess presented as data. Same
    discipline as `Wafer.film_was_defaulted`.
    """
    from cmp_sim.api import run_recipe

    r = run_recipe({"model": "full", "wafer": {"film": "oxide"},
                    "tool": {"pressure_psi": 3.0}})
    assert "consumables" not in r or not r["consumables"]["filled"], (
        "a recipe that never named a pad had pad properties filled from the "
        f"catalogue: {r.get('consumables')}")


def test_a_pad_built_in_code_is_also_inert_until_the_name_is_chosen():
    """The second, easier-to-miss way to arrive at the default pad name.

    `Pad()` constructed directly — in a test, a script, or a calibration tool —
    also carries name="IC1000" without anyone choosing it. When the flag's
    polarity was the other way round (defaulting to "chosen"), this path filled
    IC1000's Shore D into every such recipe, which made the pad differ from the
    pack's reference pad and silently DELETED the contact factor from three
    existing tests. The conservative default is the correct one.
    """
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Pad, Recipe, Slurry, Tool, Wafer

    rec = Recipe(model="gw_preston",
                 wafer=Wafer(film="oxide", n_radial=21),
                 slurry=Slurry(pack="oxide_silica_calibrated_pad"),
                 pad=Pad(),
                 tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60))
    res = simulate(rec)
    assert res.factors["kappa_contact"] == pytest.approx(1.0, rel=1e-12), (
        "a directly-constructed Pad() picked up catalogue properties and so "
        "stopped matching the pack's reference pad")
    assert not res.extras.get("consumables", {}).get("filled"), (
        res.extras.get("consumables"))


def test_the_model_route_exposes_constants_with_sources_and_is_editable():
    """The edit-and-re-predict loop the owner asked for, end to end."""
    from cmp_sim.api import model_parameters, run_recipe

    j = model_parameters("oxide_silica")
    assert j["parameters"], "no constants exposed"
    kp = next(p for p in j["parameters"] if p["key"] == "kp_m_per_pa")
    assert kp["source"], "the Preston coefficient is exposed with no source"
    assert kp["editable"] is True

    base = {"model": "preston", "wafer": {"film": "oxide"},
            "tool": {"pressure_psi": 3.0}}
    one = run_recipe(base)
    two = run_recipe({**base, "params": {"kp_m_per_pa": kp["value"] * 2.0}})
    # rel=1e-4, not tighter: the API rounds the reported rate to 0.1 A/min, so
    # doubling 1559.8 gives 3119.7 against an exact 3119.6. Asserting exact
    # equality here would be asserting the rounding, not the physics.
    assert two["removal_rate_A_per_min"] == pytest.approx(
        one["removal_rate_A_per_min"] * 2.0, rel=1e-4), (
        "editing the Preston coefficient through the override path did not "
        "change the prediction proportionally, so the UI's edit loop is not "
        "reaching the engine")
    assert any("owner-supplied" in n for n in two["notes"]), (
        "an edited constant must be reported as owner-supplied so it cannot be "
        "mistaken for a sourced value")


def test_a_disk_property_the_engine_ignores_is_declared_unwired():
    """A control that cannot move the answer must announce itself.

    The abrasive picker already had to be fixed for exactly this: offering
    zirconia looked broken because selecting it changed nothing. Conditioner grit
    design is in that state now — legacy/knowledge/performance/disk.yaml records
    the grit -> pad-asperity mapping as `pack_only` with an undetermined
    proportionality constant — so the catalogue marks it `wired: false` and the
    API reports it instead of letting the UI imply otherwise.
    """
    from cmp_sim.api import _meta, run_recipe
    from cmp_sim.pad.catalog import disk_catalog

    unwired_any = False
    for name, entry in disk_catalog().items():
        for prop, spec in entry.items():
            if isinstance(spec, dict) and spec.get("value") is not None:
                assert "wired" in spec, (
                    f"disk {name}.{prop} has a value but does not state whether "
                    f"the engine reads it")
                unwired_any = unwired_any or spec["wired"] is False
    assert unwired_any, (
        "no disk property is marked unwired — if the grit design has since been "
        "wired to the rate with a sourced proportionality constant, delete this "
        "assertion and say so in docs/derivations.md")

    meta = _meta()
    assert meta["disks"]["3M_E187_80mesh"]["unwired"], (
        "the API must publish which disk properties do not reach the rate")

    base = {"model": "full", "wafer": {"film": "oxide"},
            "tool": {"pressure_psi": 3.0}, "disk": {"hours_used": 0}}
    a = run_recipe({**base, "disk": {"name": "3M_E187_80mesh", "hours_used": 0}})
    b = run_recipe({**base, "disk": {"name": "EHWA_CVD_1.3K", "hours_used": 0}})
    assert a["removal_rate_A_per_min"] == pytest.approx(
        b["removal_rate_A_per_min"]), (
        "two different disks changed the rate, so grit design IS wired now — "
        "update the catalogue's `wired` flags and this test together")
    assert any("recorded but" in w or "does NOT reach" in w
               for w in a["warnings"]), a["warnings"]
