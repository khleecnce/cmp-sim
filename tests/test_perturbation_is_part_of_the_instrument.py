"""The perturbation IS part of the instrument (docs/limits.md §43).

`tools/declared_key_response_census.py` answers "does any rate term read this
declared pack key?" by perturbing the key and watching the rate. §42 fixed
WHERE it stands (displaced off every reference axis). It did not fix HOW it
pushes, and a single large one-sided factor manufactured silence twice on the
same pack -- filing this repository's strongest pH constants under `silent`:

1. `ph_peak` x3 moves the optimum from pH 11.0 to 33.0, 7 widths from the
   query. The model then correctly refuses (mechanical floor, `ph_valid_range`
   clamp, a warning). Measured x3 -> 0.00%, x1.25 -> 54.8%: the probe was
   grading an honest out-of-domain refusal as a forgotten wire.
2. `ph_response_width` was killed by the DISPLACEMENT landing on a symmetry
   point. `oxide_silica` has ph_ref 10.5 and ph_peak 11.0, and the displacement
   was +1.0 -- exactly twice that distance -- so the query sat at pH 11.5,
   mirror-symmetric to the reference about the peak. The factor is
   exp(-(x/w)^2)/exp(-(x_ref/w)^2), which is 1 for EVERY w when |x| == |x_ref|.
   An exact cancellation by derivation, at that one point only.

Both halves are re-measured here at run time; none of the numbers is pinned as
a literal, because pinning would go stale the moment a pack's pH constants are
re-sourced, and a stale literal invites editing the claim rather than the code.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import declared_key_response_census as census_mod  # noqa: E402

from cmp_sim.core.params import load_pack  # noqa: E402

PACK = "oxide_silica"


@pytest.fixture(scope="module")
def rows():
    return census_mod.census([PACK])


@pytest.fixture(scope="module")
def by_key(rows):
    return {r.key: r for r in rows}


def test_the_ph_optimum_is_recovered_as_read(by_key):
    """The headline repair: `ph_peak` is READ, and was reported silent."""
    row = by_key.get("ph_peak")
    assert row is not None, f"{PACK} must declare ph_peak for this limit"
    assert row.kind == "reads", (
        f"ph_peak classified '{row.kind}' at {row.rate_percent}% -- §43 says "
        "this key is read by the peaked pH term and only LOOKED silent because "
        "a x3 perturbation left the term's validity window")


def test_the_ph_width_is_recovered_as_read(by_key):
    """The second repair: the displacement must not sit on the symmetry point."""
    row = by_key.get("ph_response_width")
    assert row is not None, f"{PACK} must declare ph_response_width"
    assert row.kind == "reads", (
        f"ph_response_width classified '{row.kind}' at {row.rate_percent}% -- "
        "the displaced query has landed mirror-symmetric to ph_ref about "
        "ph_peak again, where the normalised Gaussian is exactly 1 for every "
        "width")


def test_a_large_factor_alone_cannot_find_the_ph_optimum():
    """The BUG is reproduced, so the fix cannot be mistaken for a no-op.

    Reproduced at the ORIGINAL probe point (`PH_DISPLACEMENT` with no symmetry
    break), because the §43 fix moves the probe and a bug can only be shown at
    the operating point where it happened. Two claims, both re-measured: at that
    point x3 on `ph_peak` is inert while x1.25 is enormous, and at the CURRENT
    point a small factor still out-reaches the large one -- the ordering, not a
    literal, is what makes a one-sided large perturbation the wrong instrument.
    """
    value = float(load_pack(PACK).params["ph_peak"].value)
    ph_ref = float(load_pack(PACK).params["slurry_ph"].value)
    old_point = dict(census_mod._displaced_overrides(PACK))
    old_point["slurry_ph"] = ph_ref + census_mod.PH_DISPLACEMENT

    def moved(overrides: dict, factor: float) -> float:
        base = census_mod._rate(census_mod._run(PACK, overrides))
        assert base, "base run must produce a rate"
        rate = census_mod._rate(
            census_mod._run(PACK, dict(overrides, ph_peak=value * factor)))
        assert rate is not None
        return 100.0 * abs(rate - base) / base

    big, small = moved(old_point, 3.0), moved(old_point, 1.25)
    assert big < census_mod.INERT_TOLERANCE, (
        f"x3 on ph_peak now moves the rate {big:.2f}% at the original probe "
        f"point (pH {old_point['slurry_ph']:g}), so the artefact §43 corrects "
        "no longer exists; re-derive the limit rather than deleting it")
    assert small > 10.0, (
        f"a small perturbation must reach ph_peak ({small:.2f}%) where the "
        "large one cannot, or this limit has no content")

    current = census_mod._displaced_overrides(PACK)
    assert moved(current, 1.25) > moved(current, 3.0), (
        "at the current probe point a small perturbation must still out-reach "
        "x3: the response is non-monotonic in the perturbation, which is the "
        "whole reason the census sweeps a set instead of picking one factor")


def test_the_ph_width_is_inert_exactly_on_the_symmetry_point():
    """Half two of the bug, derived rather than asserted.

    At |ph - ph_peak| == |ph_ref - ph_peak| the width cancels, and one step off
    it the width is read. Both are measured on the shipping solver.
    """
    params = load_pack(PACK).params
    peak = float(params["ph_peak"].value)
    ref = float(params["ph_ref"].value)
    width = float(params["ph_response_width"].value)
    mirror = peak + abs(peak - ref)  # the reference reflected about the optimum
    displaced = census_mod._displaced_overrides(PACK)

    def response(ph: float) -> float:
        overrides = dict(displaced, slurry_ph=ph)
        base = census_mod._rate(census_mod._run(PACK, overrides))
        alt = census_mod._rate(
            census_mod._run(PACK, dict(overrides, ph_response_width=width * 1.25)))
        assert base and alt is not None
        return 100.0 * abs(alt - base) / base

    on_point = response(mirror)
    off_point = response(mirror + census_mod.PH_SYMMETRY_BREAK)
    assert on_point < census_mod.INERT_TOLERANCE, (
        f"the width moved the rate {on_point:.3f}% at the symmetry point "
        f"(pH {mirror:g}); the normalised Gaussian is supposed to cancel there "
        "exactly, so either ph_ref/ph_peak changed or the term was re-derived")
    assert off_point > on_point, (
        f"off the symmetry point (pH {mirror + census_mod.PH_SYMMETRY_BREAK:g}) "
        f"the width must be read: {off_point:.3f}% vs {on_point:.3f}%")


def test_the_displacement_avoids_every_packs_symmetry_point():
    """Generalised: no pack may be probed on its own pH symmetry point.

    Derived from `available_packs()` at run time, so a new pack is covered with
    no test edit -- a hand-listed set is how this class of bug returns.
    """
    from cmp_sim.core.params import available_packs

    checked = 0
    for name in sorted(available_packs()):
        if name not in census_mod.PACK_FILM:
            continue
        params = load_pack(name).params
        peak, ref = params.get("ph_peak"), params.get("ph_ref")
        if not (peak and ref):
            continue
        if not isinstance(peak.value, (int, float)):
            continue
        if not isinstance(ref.value, (int, float)):
            continue
        query = census_mod._displaced_overrides(name).get("slurry_ph")
        if query is None:
            continue
        checked += 1
        gap = abs(abs(query - float(peak.value))
                  - abs(float(ref.value) - float(peak.value)))
        assert gap >= census_mod.PH_SYMMETRY_TOLERANCE, (
            f"{name} is probed at pH {query:g}, mirror-symmetric to ph_ref "
            f"{ref.value} about ph_peak {peak.value}, where the width cancels "
            "for every value -- the probe would report it inert by artefact")
    assert checked >= 2, (
        "no pack exercised this guard; it passes vacuously and is "
        "indistinguishable from a deleted check")


def test_the_census_publishes_its_perturbations_and_controls(rows):
    """A zero response is only quotable alongside what was tried."""
    assert len(census_mod.PERTURBATION_FACTORS) >= 4
    assert any(f < 1.0 for f in census_mod.PERTURBATION_FACTORS), (
        "a one-sided perturbation set cannot distinguish a validity-window "
        "refusal from a missing wire")
    assert any(abs(f - 1.0) <= 0.3 for f in census_mod.PERTURBATION_FACTORS), (
        "the set needs a SMALL factor: that is what recovered ph_peak")
    for row in rows:
        if row.rate_percent is not None:
            assert row.perturbation is not None, (
                f"{row.key} reports a response with no perturbation recorded")


def test_the_instrument_controls_hold(rows):
    """The census must recover keys known to be read, or say it cannot."""
    assert census_mod.INSTRUMENT_CONTROLS.get(PACK), (
        "the control set must name this pack; without controls a census that "
        "reaches nothing reports a clean bill of health for the repository")
    assert census_mod.instrument_control_failures(rows) == []


def test_the_controls_are_not_vacuous():
    """A control that cannot fail is not a control."""
    original = dict(census_mod.INSTRUMENT_CONTROLS)
    fake = census_mod.KeyResponse(
        pack=PACK, key="ph_peak", value=11.0, rate_percent=0.0,
        perturbation=3.0)
    try:
        failures = census_mod.instrument_control_failures([fake])
    finally:
        census_mod.INSTRUMENT_CONTROLS.clear()
        census_mod.INSTRUMENT_CONTROLS.update(original)
    assert failures, (
        "a silent ph_peak must trip the instrument control; otherwise the "
        "control passes on a broken probe")
    assert "suspect" in failures[0], (
        "the failure must say that the census's own verdicts are unreliable, "
        "not merely that one key did not move")
