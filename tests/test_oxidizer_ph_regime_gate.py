"""The oxidizer term's SIGN is a property of the pH branch, not of the film.

Miranda 2004 ran a 2x2 factorial on electroplated copper — same Cabot 5001
base, same EPAD-A100 pad, same 4 psi / 60 rpm / 200 mL/min, 3 replicates per
cell — and moved only pH and H2O2:

    pH 4:  H2O2 1.5 -> 3.5 wt%   1953 -> 2908 A/min   (+49 %)
    pH 8:  H2O2 1.5 -> 3.5 wt%   1743 ->  243 A/min   (-86 %)

ANOVA: pH main effect p=0.0021, pH x H2O2 interaction p=0.0207, H2O2 alone
p=0.588. The mechanism is Pourbaix — acidic H2O2 gives soluble Cu2+, alkaline
H2O2 above ~2.5 % grows hard CuO that the abrasive cannot cut.

The model carries ONE oxidizer constant per pack, so its term is monotonic in
that constant for every value of it. No refit reaches both legs; this is a
functional-form limit. Rather than let the acidic constant extrapolate into
the alkaline branch with a sign the measurement contradicts, the pack declares
the pH window its constants were measured in and the term is GATED outside it.

These tests pin the three things that make a gate honest:

1. it is narrow, and fires only where the pack says it has no data;
2. the silence is loud — the caller is told, in the warning and in the score,
   which regime is unmeasured and what experiment would close it;
3. it cannot be used to duck a bad score, so a gate on an axis the dataset
   holds CONSTANT must not silence that dataset.
"""
from __future__ import annotations

import pytest
import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import (_predict_with_gate, _recipe_for,
                                           score_all, score_dataset)
from cmp_sim.core.validation import dataset_paths

WINDOW = (2.0, 6.25)


def _run(ph: float, ox: float) -> dict:
    return run_recipe({
        "model": "auto",
        "wafer": {"film": "cu", "n_radial": 11},
        "slurry": {"pack": "cu_h2o2_bta", "ph": ph,
                   "additives": [{"name": "hydrogen_peroxide",
                                  "role": "oxidizer", "conc_wt_pct": ox}]},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60},
    })


def _path(stem: str):
    for path in dataset_paths():
        if path.stem == stem:
            return path
    raise AssertionError(f"dataset {stem} not found")


# ---------------------------------------------------------------------------
# the measurement the gate is derived from
# ---------------------------------------------------------------------------

def test_the_two_legs_really_do_move_in_opposite_directions():
    """If this ever stops holding, the gate has lost its justification."""
    doc = yaml.safe_load(_path("miranda2004_cu_ph_h2o2_2x2")
                         .read_text(encoding="utf-8"))
    cell = {(r["overrides"]["slurry_ph"], r["overrides"]["oxidizer_wt_pct"]):
            r["mrr_nm_per_min"] for r in doc["conditions"]}

    acidic = cell[(4.0, 3.5)] / cell[(4.0, 1.5)]
    alkaline = cell[(8.0, 3.5)] / cell[(8.0, 1.5)]
    assert acidic > 1.4, acidic        # +49 %
    assert alkaline < 0.2, alkaline    # -86 %
    assert (acidic - 1.0) * (alkaline - 1.0) < 0, "the sign flip is the point"


def test_no_single_signed_constant_can_fit_both_legs():
    """The reason this is a gate and not a refit.

    The oxidizer term multiplies the rate by a factor that depends only on
    concentration, so within one pack the ratio between two concentrations is
    the SAME at every pH. The measurement says that ratio is 1.49 on one leg
    and 0.14 on the other. One number cannot be both.
    """
    at_ph4 = [_run(4.0, c)["chemistry_terms"] for c in (1.5, 3.5)]
    ratio_4 = at_ph4[1].get("oxidizer_peaked", 1.0) / at_ph4[0].get("oxidizer_peaked", 1.0)
    # measured ratios, for contrast
    assert 1.4 < 2908 / 1953 < 1.6
    assert 0.1 < 243 / 1743 < 0.2
    # the model's single-signed term cannot straddle them
    assert not (0.14 * 0.9 < ratio_4 < 0.14 * 1.1 or ratio_4 > 1.4), (
        "if the term reproduced one leg exactly it would still miss the other")


# ---------------------------------------------------------------------------
# the gate fires exactly where the pack says it has no data
# ---------------------------------------------------------------------------

def test_the_window_comes_from_the_gated_constants_own_provenance():
    """Not chosen to make a dataset score well.

    The upper bound is the acidic/alkaline branch split the pH term already
    used; the lower bound is the lowest pH in the same fitting set.
    """
    window = load_pack("cu_h2o2_bta").param("oxidizer_ph_window")
    assert tuple(window.value) == WINDOW
    assert window.confidence == "literature"
    assert "10.1109/WMED.2004.1297359" in window.source


def test_inside_the_window_the_oxidizer_term_is_alive():
    terms = [_run(4.0, c)["chemistry_terms"] for c in (1.5, 3.5)]
    assert all("oxidizer_gated" not in t for t in terms)
    assert terms[0]["oxidizer_peaked"] != terms[1]["oxidizer_peaked"]


def test_outside_the_window_the_rate_stops_responding_to_oxidizer():
    low, high = _run(8.0, 1.5), _run(8.0, 3.5)
    assert low["chemistry_terms"]["oxidizer_gated"] == 1.0
    assert low["removal_rate_A_per_min"] == pytest.approx(
        high["removal_rate_A_per_min"]), (
        "a gated term must be inert, not merely weakened")


def test_the_gate_removes_the_inherited_term_too():
    """Gating only the peaked branch would leave the wrong-signed Langmuir
    penalty applied, which is the exact failure the gate exists to stop."""
    terms = _run(8.0, 3.5)["chemistry_terms"]
    assert "oxidizer" not in terms
    assert "oxidizer_peaked" not in terms


def test_ph_itself_still_predicts_across_the_boundary():
    """The gate is on ONE term, not on the run. pH 8 still differs from pH 4."""
    acid, alk = _run(4.0, 3.5), _run(8.0, 3.5)
    assert alk["chemistry_terms"]["ph_peaked"] < acid["chemistry_terms"]["ph_peaked"]
    assert alk["removal_rate_A_per_min"] < acid["removal_rate_A_per_min"]


# ---------------------------------------------------------------------------
# the silence is loud, and cannot be used to duck a score
# ---------------------------------------------------------------------------

def test_the_warning_names_the_regime_and_the_evidence():
    warnings = _run(8.0, 3.5)["warnings"]
    gate = next(w for w in warnings if "GATED" in w)
    assert "pH 2 and 6.25" in gate
    assert "Miranda 2004" in gate
    assert "p=0.0207" in gate
    assert "not a claim that oxidizer is unimportant" in gate


def test_a_dataset_that_varies_the_gated_axis_is_declined_not_scored():
    score = score_dataset(_path("miranda2004_cu_ph_h2o2_2x2"))
    assert score.shape_mape is None, "a declined dataset must not carry a score"
    assert score.gated == 2
    assert "GATED" in score.gated_reason
    assert "declining to predict" in score.error


def test_a_dataset_that_holds_the_gated_axis_constant_is_still_scored():
    """The anti-laundering rule.

    lai2001 runs at pH 7 — outside the window — but never varies H2O2, so the
    switched-off term is a constant that cancels out of a shape comparison.
    Declining it would silence a good size-sweep to say nothing about an axis
    it never probes, and would let any future gate quietly remove datasets.
    """
    score = score_dataset(_path("lai2001_cu_alumina_size_sweep"))
    assert score.gated == score.n, "the gate does fire on every row"
    assert score.shape_mape is not None, "but the dataset is still scored"
    assert "oxidizer_wt_pct" not in score.axes


def test_the_gate_stays_narrow():
    """A gate that silenced much of the corpus would be an excuse, not a fact."""
    scores = list(score_all())
    declined = [s for s in scores if s.error and s.gated_reason]
    assert len(declined) <= 3, [s.dataset for s in declined]
    assert {s.dataset for s in declined} == {
        "miranda2004_cu_ph_h2o2_2x2",
        "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator"}


def test_the_gated_rows_are_counted_in_the_scored_datasets_too():
    """Counted even when they do not change the score, so the gate is visible
    wherever it acts rather than only where it bites."""
    doc = yaml.safe_load(_path("lai2001_cu_alumina_size_sweep")
                         .read_text(encoding="utf-8"))
    for row in doc["conditions"]:
        value, gate, _declined = _predict_with_gate(doc, row)
        assert value is not None
        assert gate and "GATED" in gate
        _ = _recipe_for(doc, row)
