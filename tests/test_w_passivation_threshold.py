"""The W passivation threshold: derived form, measured support, honest limits.

Guards `cmp_sim/models/passivation_threshold.py` and the two constants it reads
from `w_fe_oxidizer`. Three things are pinned here, because each has already
been a trap somewhere in this repo:

 1. The law must BEAT a fitted pressure exponent on the dataset that motivated
    it, using a mechanism instead of curvature. If someone later reverts to
    `pressure_exponent`, the numbers here say what was lost.
 2. The threshold must NOT reach films whose pack does not declare it. A
    borrowed threshold would silently suppress every low-pressure rate.
 3. The PARTIAL FALSIFICATION must stay recorded: per-composition thresholds
    are not monotone in inhibitor loading, so P_y is extrapolated. A future run
    that finds this comment gone should find this test failing first.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.models.passivation_threshold import (
    langmuir_coverage, passivation_threshold_factor, threshold_pressure_psi)

DATASET = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data" /
           "validation" / "datasets" /
           "ep3161098b1_w_silica_pressure_sweep.yaml")


def _pack_constants():
    pack = load_pack("w_fe_oxidizer")
    return (float(pack.param("passivation_yield_pressure_psi").value),
            float(pack.param("inhibitor_langmuir_K_per_ppm").value))


def _rows():
    doc = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    out = []
    for cond in doc["conditions"]:
        ov = cond["overrides"]
        out.append((float(cond["pressure_psi"]), float(cond["mrr_nm_per_min"]),
                    float(ov["fe_ppm"]), float(ov["inhibitor_ppm"])))
    return out


# ---------------------------------------------------------------- the form ---

def test_coverage_is_a_bounded_langmuir_isotherm():
    k_l = _pack_constants()[1]
    assert langmuir_coverage(0.0, k_l) == 0.0
    assert 0.0 < langmuir_coverage(50.0, k_l) < 1.0
    # monotone and saturating: the second decade must add less than the first
    a = langmuir_coverage(50.0, k_l)
    b = langmuir_coverage(500.0, k_l)
    c = langmuir_coverage(5000.0, k_l)
    assert a < b < c < 1.0
    assert (c - b) < (b - a)


def test_threshold_vanishes_at_high_pressure_so_preston_is_recovered():
    """RR = K*V*(P - P0) must be indistinguishable from Preston at P >> P0."""
    p_y, k_l = _pack_constants()
    far = passivation_threshold_factor(500.0, 50.0, p_y, k_l)
    assert far.factor > 0.99
    near = passivation_threshold_factor(2.0, 50.0, p_y, k_l)
    assert near.factor < 0.9, "the threshold must matter in the 1.5-3 psi band"


def test_below_threshold_is_loud_not_silent():
    p_y, k_l = _pack_constants()
    p0 = threshold_pressure_psi(60.0, p_y, k_l)
    res = passivation_threshold_factor(p0 * 0.5, 60.0, p_y, k_l)
    assert res.factor < 1e-3
    assert any("threshold" in w and "EXTRAPOLATION" in w
               for w in res.warnings), (
        "predicting near-zero removal below the threshold is a real claim, but "
        "it is extrapolation below the measured 1.5-3.0 psi band and must warn")


# --------------------------------------------------- it beats the fitted n ---

def _shape_mape(rows, pred):
    import statistics as st
    ratios = sorted(m / p for (_, m, _, _), p in zip(rows, pred) if p > 0)
    scale = st.median(ratios)
    return 100.0 * sum(abs(scale * p - m) / m
                       for (_, m, _, _), p in zip(rows, pred)) / len(rows)


def test_the_law_beats_both_preston_and_a_fitted_pressure_exponent():
    """The whole justification: a mechanism with 2 constants beats curvature.

    Re-derived from the dataset on every run rather than quoting the numbers in
    the pack note, so the claim cannot rot.
    """
    rows = _rows()
    p_y, k_l = _pack_constants()

    plain = _shape_mape(rows, [p for p, _, _, _ in rows])

    best_exp = min(
        _shape_mape(rows, [p ** (0.5 + i * 0.01) for p, _, _, _ in rows])
        for i in range(1, 201))

    derived = _shape_mape(
        rows, [max(p - threshold_pressure_psi(inh, p_y, k_l), 1e-9)
               for p, _, _, inh in rows])

    assert plain > 40.0, f"plain Preston was {plain:.1f}% (expected >40%)"
    assert derived < 15.0, f"threshold law was {derived:.1f}% (expected <15%)"
    assert derived < best_exp - 10.0, (
        f"the threshold ({derived:.1f}%) must beat the best single fitted "
        f"pressure exponent ({best_exp:.1f}%) by a wide margin, otherwise it is "
        "just a reparameterisation of curvature and the mechanism claim is "
        "unsupported")


def test_the_inhibitor_axis_is_no_longer_inert():
    """The dataset's two previously-dead axes: inhibitor must now reach the rate.

    Fe must NOT — the pack deliberately declines a Fenton term because the
    reference concentration it would need is unpublished. Asserting silence
    there keeps a future run from quietly inventing that reference.
    """
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

    def rate(inh, fe):
        return simulate(Recipe(
            model="auto",
            wafer=Wafer(film="w", n_radial=11),
            slurry=Slurry(pack="w_fe_oxidizer"),
            pad=Pad(), disk=Disk(),
            tool=Tool(pressure_psi=2.0, rpm_platen=100.0, rpm_head=100.0,
                      time_s=60.0),
            params={"inhibitor_ppm": inh, "fe_ppm": fe,
                    "slurry_ph": 4.0, "oxidizer_wt_pct": 2.0,
                    "abrasive_wt_pct": 2.0, "abrasive_size_nm": 55.0},
        )).mean_rr_angstrom_per_min

    low, high = rate(37.0, 45.0), rate(63.0, 45.0)
    assert high < low * 0.97, (
        f"more inhibitor must lower the W rate ({low:.1f} -> {high:.1f} A/min)")

    fe_low, fe_high = rate(50.0, 45.0), rate(50.0, 60.0)
    assert fe_low == pytest.approx(fe_high, rel=1e-9), (
        "the Fe axis is DELIBERATELY silent: Fenton is first order in the "
        "catalyst, but this pack's Kp is anchored on US2011/0186542A1, which "
        "never states its Fe loading, so the reference concentration the term "
        "needs does not exist in the literature this pack cites")


# ------------------------------------------------- the limits stay recorded ---

def test_the_extrapolation_limit_of_P_y_is_still_declared():
    """P_y is an intercept, not a measured shear strength. Say so, in the pack."""
    doc = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "cmp_sim" / "data" / "params" /
         "w_fe_oxidizer.yaml").read_text(encoding="utf-8"))
    note = doc["params"]["passivation_yield_pressure_psi"]["note"]
    assert "EXTRAPOLATED" in note
    assert "not monotone" in note or "within each other's scatter" in note, (
        "the per-composition thresholds (0.52/1.19/1.08 psi at 37/50/63 ppm) "
        "are NOT monotone in inhibitor loading; that partial falsification is "
        "the reason P_y cannot be quoted as a material property")


def test_the_measured_coverage_range_never_approaches_saturation():
    """Why P_y is extrapolated, re-derived from the data rather than asserted."""
    _p_y, k_l = _pack_constants()
    thetas = [langmuir_coverage(inh, k_l) for _, _, _, inh in _rows()]
    assert max(thetas) < 0.4, (
        f"the patent's 37-63 ppm only reaches theta = {max(thetas):.2f}, so the "
        "saturated-coverage limit P_y is never observed directly")
