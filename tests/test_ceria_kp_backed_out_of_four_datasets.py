"""BLOCKED #2 diagnosed: the ceria Kp was a representative guess, not a fit.

`sti_ceria` predicted 7,235 A/min for a standard STI recipe against a published
200-6,000 A/min envelope. The pack and the envelope both cite sources, so one of
them was wrong FOR THIS RECIPE and it had never been diagnosed.

The answer is the Kp. The inherited legacy pack carries kp_m_per_pa = 2.2e-13
m/Pa with `confidence: estimated` and a note that says, in its own words, that
the value lumps a composition-dependent effect into one constant and is
unreproduced. It was never back-calculated from a measured run.

METHOD — the same back-out that FALSIFIED the inherited-Kp hypothesis for the
silica packs (tests/test_inherited_kp_is_not_the_problem.py). The predicted rate
is linear in Kp, so a dataset whose median measured/predicted ratio is `s`
implies Kp_implied = Kp_declared * s. Four of this pack's datasets are
absolute-comparable (the other four carry the scorer's 'absolute values
incomparable' flag, or are a different abrasive).

WHAT THIS TEST GUARDS, precisely:
  1. The four implied values agree within a small factor and all lie BELOW the
     old constant — a one-sided disagreement is what a wrong scale looks like,
     as opposed to scatter, and is the evidence for changing it at all.
  2. The declared constant equals their geometric mean, recomputed here from the
     scorer rather than copied from the YAML.
  3. Leave-one-out: no single dataset carries the number.
  4. NO SHAPE SCORE MOVED. Kp is one multiplicative scale; if a shape error had
     changed, something other than the intended constant moved with it.
  5. The two ceria-COATED-silica composite datasets are EXCLUDED and stay
     excluded — they imply a ~5x lower Kp, but a ceria shell on a silica core is
     a different abrasive, and averaging them in would hide that disagreement
     inside one constant.

HONESTY: after this change those four datasets' `scale` column is a fit
residual, not an independent test. Their SHAPE errors (12.9 / 25.5 / 42.8 /
49.2%) are untouched and remain the real test of the physics.
"""
from __future__ import annotations

import math
import statistics

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import dataset_paths, score_all

#: The datasets whose absolute rate this pack may legitimately be scaled against.
ANCHORS = (
    "kenchappa2021_softpad_hdp_oxide",
    "mariscal2020_peteos_ceria_pressure_velocity_3x3",
    "netzband2020_thermal_oxide_ceria_ph",
    "son2021_oxide_ceria_size_sweep",
)
#: Ceria-COATED silica. Absolute-comparable, deliberately NOT used.
COMPOSITE = (
    "us20190127607a1_hdpoxide_ceriasilica_size_sweep",
    "us20190127607a1_teos_ceriasilica_size_sweep",
)
#: What the pack declared before the diagnosis.
OLD_KP = 2.20e-13
#: Shape errors that must be unaffected by a pure scale change.
SHAPE_BEFORE = {
    "kenchappa2021_softpad_hdp_oxide": 42.8,
    "mariscal2020_peteos_ceria_pressure_velocity_3x3": 12.9,
    "netzband2020_thermal_oxide_ceria_ph": 49.2,
    "son2021_oxide_ceria_size_sweep": 25.5,
    "us20190127607a1_teos_ceriasilica_size_sweep": 18.9,
    "us20190127607a1_hdpoxide_ceriasilica_size_sweep": 8.4,
}


def _scores():
    return {s.dataset: s for s in score_all()}


def _implied_kp(scores, stem, declared):
    """Kp the dataset implies, given the Kp the prediction was made with."""
    return declared * scores[stem].scale_ratio


def test_the_four_anchors_disagree_with_the_old_constant_in_one_direction():
    """Scatter would straddle the old value. A wrong scale does not."""
    kp = load_pack("sti_ceria").param("kp_m_per_pa").value
    scores = _scores()
    # Re-express each anchor's residual as the Kp it would have implied against
    # the OLD constant, so the comparison is with the pre-change state.
    implied_old = [_implied_kp(scores, s, kp) for s in ANCHORS]
    assert len(implied_old) == 4
    assert all(v < OLD_KP for v in implied_old), (
        f"the finding is a ONE-SIDED disagreement; got {implied_old}")
    spread = max(implied_old) / min(implied_old)
    assert spread < 3.0, (
        f"the four anchors must agree well enough to define one constant; "
        f"end-to-end spread {spread:.2f}x")


def test_the_declared_kp_is_their_geometric_mean_recomputed_here():
    kp = load_pack("sti_ceria").param("kp_m_per_pa").value
    scores = _scores()
    implied = [_implied_kp(scores, s, kp) for s in ANCHORS]
    geo = math.exp(statistics.fmean(math.log(v) for v in implied))
    # The pack's Kp IS the fit, so the residual scales must themselves centre on
    # 1.0 — a self-consistency check, not a restatement of the YAML.
    assert abs(math.log(geo / kp)) < math.log(1.15), (
        f"declared {kp:.3e} vs geometric mean of what its own anchors now "
        f"imply {geo:.3e}: the fit is not self-consistent")


def test_no_single_dataset_carries_the_constant():
    kp = load_pack("sti_ceria").param("kp_m_per_pa").value
    scores = _scores()
    implied = {s: _implied_kp(scores, s, kp) for s in ANCHORS}
    for dropped in ANCHORS:
        rest = [v for s, v in implied.items() if s != dropped]
        loo = kp * math.exp(statistics.fmean(math.log(v / kp) for v in rest))
        assert 0.75 < loo / kp < 1.35, (
            f"dropping {dropped} moves Kp to {loo:.3e} ({loo / kp:.2f}x): one "
            "dataset is carrying the constant")


def test_the_scale_change_moved_no_shape_score():
    """Kp is a pure multiplicative scale. The shape metric divides it out."""
    scores = _scores()
    for stem, before in SHAPE_BEFORE.items():
        now = scores[stem].shape_mape
        assert now is not None and abs(now - before) < 0.5, (
            f"{stem}: shape moved {before} -> {now}. A Kp change cannot do "
            "that; something else moved with it")


def test_the_ceria_coated_composites_stay_excluded_and_still_disagree():
    """Not a silent averaging-in: the disagreement is kept visible."""
    kp = load_pack("sti_ceria").param("kp_m_per_pa").value
    scores = _scores()
    composite = [_implied_kp(scores, s, kp) for s in COMPOSITE]
    assert all(v < kp / 2.5 for v in composite), (
        f"the composite datasets imply {composite}; if they ever agree with "
        "the bare-ceria Kp this exclusion needs revisiting")
    text = (load_pack("sti_ceria").param("kp_m_per_pa").note or "")
    assert "coated" in text.lower(), (
        "the pack must state that its Kp is bare ceria and that the composite "
        "datasets were excluded")


def test_every_anchor_is_a_real_registered_dataset():
    stems = {p.stem for p in dataset_paths()}
    for s in ANCHORS + COMPOSITE:
        assert s in stems, s
