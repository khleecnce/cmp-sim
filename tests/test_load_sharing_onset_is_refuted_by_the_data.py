"""The load-sharing ONSET is the right sign and is still refuted — by the data, not by the median.

Enforces `docs/limits.md` §29.

Session 32 derived a monolayer-occupancy saturation, priced it and was refused
(§28 amendment).  This session asked *where* that derivation had been applied
rather than whether theta was the right variable, found a placement whose sign
matches the measurements, priced it -- and then refuted it on a statement about
the DATA that does not pass through the corpus median at all.

Everything here is re-measured at test time from the solver and the datasets.
No number is copied from the documentation.
"""

from __future__ import annotations

import math
import statistics

import pytest

from tools.load_sharing_onset_counterfactual import correction, rescore
from tools.load_sharing_slope_probe import slope_pairs


@pytest.fixture(scope="module")
def priced():
    return rescore()


@pytest.fixture(scope="module")
def pairs():
    return slope_pairs()


# ── the derivation's structural invariants ──────────────────────────────────
# These hold by construction and are asserted so that a future session cannot
# reintroduce the term in a form that breaks them.

def test_the_correction_is_exactly_one_at_the_pack_reference():
    """Every factor in this model must be 1.0 at its pack's reference.

    A factor that is not is an absolute term, and an absolute term counts the
    physics already baked into the back-calculated Kp a second time.
    """
    for theta in (0.02, 0.5, 1.0, 4.9, 60.0):
        for n_eff in (0.1, 0.33, 0.67, 0.9):
            assert correction(theta, theta, n_eff) == pytest.approx(1.0)


def test_the_correction_bends_the_response_the_way_the_data_do():
    """Dilute predictions must go DOWN, not up.

    This is the whole reason a second look at theta was warranted. Session 32
    applied it to the particle COUNT, which makes N sub-linear in C; raised to
    a sub-unity load-sharing exponent that RAISES the dilute prediction, while
    the binding dataset's measured slope is steeper at dilute than the model's
    (+0.532 measured vs +0.226 modelled from 1->5 wt%). The sign was wrong
    before a single number was computed. Applied to the load-shared FRACTION
    instead, chi = 1 - exp(-theta) is concave, so below the reference the
    correction is < 1 and above it is > 1.
    """
    theta_ref, n_eff = 2.74, 0.24  # liang2026's own resolved values
    assert correction(0.2 * theta_ref, theta_ref, n_eff) < 1.0
    assert correction(5.0 * theta_ref, theta_ref, n_eff) > 1.0


def test_the_derivation_introduces_no_free_constant():
    """theta, alpha and chi are all read from quantities the model computes.

    `correction` takes only (theta, theta_ref, n_eff): the occupancy, the same
    occupancy at the reference composition, and the exponent measured off the
    shipping model by perturbation. There is no fitted argument to tune, which
    is why this could be priced honestly at all.
    """
    import inspect
    sig = inspect.signature(correction)
    assert list(sig.parameters) == ["theta", "theta_ref", "n_eff"]
    assert all(p.default is inspect.Parameter.empty
               for p in sig.parameters.values()), (
        "a default argument is a free constant with a hiding place")


# ── the median verdict (weak evidence, recorded as such) ────────────────────

def test_the_median_verdict_alone_would_not_have_settled_it(priced):
    """The counterfactual FIXES the binding dataset and still loses on median.

    That combination is exactly why the median could not settle this: the
    headline is a counting statistic, so a term can repair the dataset the
    whole completion criterion hangs on and still be scored down by other
    blocks crossing the middle. Recorded so nobody re-runs the counterfactual,
    sees liang2026 collapse to single digits, and wires the term on that.
    """
    rows, summary = priced
    by_name = {r["dataset"]: r for r in rows}
    binding = by_name.get("liang2026_4hsic_ceria_composite_h2o2_conc")
    assert binding is not None, (
        "the binding dataset dropped out of the pricing set; §29 must be "
        "re-measured rather than inherited")
    assert binding["shape_after"] < binding["shape_before"] / 3.0, (
        "§29 records that the load-sharing onset repairs the binding dataset "
        f"(got {binding['shape_before']:.1f}% -> {binding['shape_after']:.1f}%)")
    assert summary["median_in_premise"] > summary["median_before"], (
        "§29 records the corpus median moving the WRONG way despite that "
        "repair; if this now improves, the refutation must be re-measured")


# ── the refutation: a statement about the DATA ──────────────────────────────

def test_the_dilute_slope_does_not_approach_one(pairs):
    """The derivation's sharpest prediction, and the corpus says no.

    chi = 1 - exp(-theta) forces the local log-log slope of rate against
    loading to (1-alpha) + alpha * theta*e^-theta/(1-e^-theta), which tends to
    +1 as theta -> 0: with the contact nearly empty each particle carries its
    own load independently and removal is linear in count. The measured dilute
    group does not do this -- it sits near the same value as the dense group.
    """
    kept = [p for p in pairs if p["in_premise"]]
    dilute = [p["s_meas"] for p in kept if p["theta"] < 1.0]
    dense = [p["s_meas"] for p in kept if p["theta"] >= 1.0]
    assert dilute and dense, "the split has no evidence on one side"
    m_dilute = statistics.median(dilute)
    assert m_dilute < 0.6, (
        "§29 is refuted BY THIS: the dilute median slope must approach +1 for "
        f"the load-sharing onset to describe the corpus, and it is {m_dilute:+.3f}")


def test_the_dilute_evidence_rests_on_a_single_dataset(pairs):
    """And the refutation's own weakness is stated, not hidden.

    Every theta < 1 pair in the corpus comes from one patent's diamond series
    at 0.01-0.04 wt%. So the refutation is as narrow as the claim it refutes:
    it says this corpus gives no support, NOT that the physics is wrong. That
    distinction is the exit condition -- a second dilute dataset from a
    different abrasive system reopens §29.
    """
    kept = [p for p in pairs if p["in_premise"]]
    sources = {p["dataset"] for p in kept if p["theta"] < 1.0}
    assert len(sources) <= 1, (
        "a second dilute-loading dataset has entered the corpus, so the §29 "
        f"refutation is no longer single-sourced and must be re-measured: {sources}")


def test_the_premise_is_a_scope_claim_and_excludes_datasets_both_ways(pairs):
    """alpha = 1 - n_eff outside (0, 1] means the premise does not apply.

    An indentation-load exponent cannot be negative or exceed 1, so a pack
    whose measured loading exponent is negative (the Entegris alumina series,
    -0.406) is not a load-sharing response at all. Excluding it is a scope
    condition declared from the derivation, not a choice of which datasets
    make the number look good -- and the test asserts the exclusion is real,
    so the refutation above cannot be an artefact of an empty filter.
    """
    excluded = [p for p in pairs if not p["in_premise"]]
    assert excluded, (
        "nothing is out of premise, so the scope condition is inert and the "
        "in-premise reading claims more than it measured")
    for p in excluded:
        assert not (0.0 < p["alpha"] <= 1.0)


def test_the_correction_formula_matches_the_slope_law_being_tested(pairs):
    """The probe and the counterfactual must be testing the SAME derivation.

    Two files implementing one law is how a refutation quietly stops applying
    to the thing it refuted. The slope law is the analytic derivative of the
    correction, so check it numerically at the corpus's own thetas.
    """
    kept = [p for p in pairs if p["in_premise"]]
    assert kept
    for p in kept[:20]:
        theta, alpha = p["theta"], p["alpha"]
        n_eff = 1.0 - alpha
        h = 1e-4
        numeric = (math.log(correction(theta * (1 + h), theta, n_eff)
                            / correction(theta * (1 - h), theta, n_eff))
                   / math.log((1 + h) / (1 - h)))
        analytic = alpha * theta * math.exp(-theta) / (1.0 - math.exp(-theta))
        assert numeric == pytest.approx(analytic, rel=1e-3, abs=1e-6)
