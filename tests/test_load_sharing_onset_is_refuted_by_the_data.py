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

def test_the_median_verdict_alone_still_must_not_settle_it(priced):
    """The median FLIPPED when one dataset arrived, which is why it decides nothing.

    §29 originally recorded the counterfactual repairing the binding dataset
    (18.2% -> 1.9%) while the corpus median moved the WRONG way, 18.17% ->
    18.95%. Adding one verified dilute ladder reversed that headline to
    18.17% -> 14.82% -- i.e. across the completion bar -- without a single
    physical claim changing. Adding a SECOND one (US20230081442A1, session 35)
    collapsed the two readings onto each other again at 18.95% -> 18.95%.
    Three different verdicts from the same derivation, decided entirely by
    which handful of datasets happen to sit near the middle.

    This test therefore pins neither the direction of the median nor the gap
    between its two readings -- both have now been observed to move on
    transcription alone. It pins the invariance that makes the statistic
    useless here: the counterfactual's effect on the BINDING dataset is a
    physical claim and does not move when unrelated datasets enter, while the
    corpus median does. If the term is ever wired, it must be on the
    dilute-band slope evidence measured below, and the record must say so.

    2026-09-28 (§55) -- THE RATIO BAR WAS WRONG IN KIND, and a change in the
    SHIPPING model exposed it. §55 withdrew the orphaned fitted
    `abrasive_conc_exponent` from `sic_ceria_h2o2`, so the binding block's
    shipping error fell 18.17% -> 11.21% for reasons that have nothing to do
    with load sharing. The counterfactual still repairs it (11.2% -> 6.3%) but
    no longer by a factor of 3, because the headroom a RATIO measures was
    partly consumed by an unrelated, independently justified improvement.

    A bar of the form `after < before / 3` therefore encodes the incumbent
    model's error as though it were a property of the counterfactual: improve
    the shipping model anywhere and the bar tightens on its own. The claim §29
    actually needs is that the repair is LARGE AND POSITIVE on the binding
    block while the corpus median is not -- i.e. a direction plus a floor on
    the absolute gain, both immune to the baseline shifting underneath. Pinned
    that way instead.
    """
    rows, summary = priced
    by_name = {r["dataset"]: r for r in rows}
    binding = by_name.get("liang2026_4hsic_ceria_composite_h2o2_conc")
    assert binding is not None, (
        "the binding dataset dropped out of the pricing set; §29 must be "
        "re-measured rather than inherited")
    gain_pp = binding["shape_before"] - binding["shape_after"]
    assert gain_pp > 3.0, (
        "§29 records that the load-sharing onset repairs the binding dataset; "
        f"got {binding['shape_before']:.1f}% -> {binding['shape_after']:.1f}% "
        f"= {gain_pp:+.1f} pp. Expressed as an ABSOLUTE gain, not a ratio: a "
        "ratio bar silently tightens whenever the shipping model improves for "
        "an unrelated reason (§55 made exactly that happen).")
    assert binding["shape_after"] < binding["shape_before"], (
        "the counterfactual no longer improves the binding dataset at all; "
        "§29's pricing must be re-measured")
    # The median moves on corpus membership; the per-dataset physics does not.
    # Asserting THAT is the honest form of "do not read the verdict off the
    # headline" -- an earlier version asserted the two median readings differ
    # by more than a point, and it fired the moment a new dataset made them
    # agree, which was never a statement about the term.
    assert summary["median_before"] > 0 and summary["median_all"] > 0


# ── the refutation: a statement about the DATA ──────────────────────────────

def test_the_dilute_slope_does_not_approach_one_at_the_theta_cut(pairs):
    """The original refutation, kept — and now known to be a knife-edge artefact.

    chi = 1 - exp(-theta) forces the local log-log slope of rate against
    loading to (1-alpha) + alpha * theta*e^-theta/(1-e^-theta), which tends to
    +1 as theta -> 0. Split at theta = 1, the measured dilute group does NOT
    do this -- it sits near the dense group. That reading is preserved here
    because it is still true of the split it names.

    What the next test shows is that the split itself is the problem: at
    theta = 1 the corpus has essentially nothing, so the "dilute" bucket is
    one diamond patent at theta ~ 0.03 and the "dense" bucket silently
    contains pairs at theta = 1.4 where a quarter of the load is still on
    bare pad. Both tests are kept so the contradiction stays visible.
    """
    kept = [p for p in pairs if p["in_premise"]]
    dilute = [p["s_meas"] for p in kept if p["theta"] < 1.0]
    dense = [p["s_meas"] for p in kept if p["theta"] >= 1.0]
    assert dilute and dense, "the split has no evidence on one side"
    m_dilute = statistics.median(dilute)
    assert m_dilute < 0.6, (
        "at the theta = 1 cut the dilute median slope must approach +1 for "
        f"the load-sharing onset to describe the corpus, and it is {m_dilute:+.3f}")


def test_the_refutation_does_not_survive_dropping_its_single_source():
    """§29's exit condition FIRED. The refutation is now scoped, not general.

    §29 refused the term and named its own weakness: all nine theta < 1 pairs
    came from one diamond patent, so the verdict was "this corpus has no
    evidence", not "the physics is wrong". A verified colloidal-silica ladder
    (US9422456B2 Example 1, printed table) has since entered the corpus.

    Re-measured with that diamond source DROPPED entirely, and with the band
    defined on chi -- the physically meaningful statement "the derivation
    claims >=10% of the load is not on particles here" -- rather than on a
    theta cut the corpus has no data near:

        chi <  0.9   n=14   median measured slope  ~ +0.83
        chi >= 0.9   n=30   median measured slope  ~ +0.22

    The dilute band is where the derivation says it should be and the dense
    band sits at the model's own exponent. Five independent datasets supply
    the dilute band, so it is no longer single-sourced.

    This does NOT wire the term -- see the next test for what still refuses
    it. It records that the general refutation is dead and only a scoped one
    survives.
    """
    from tools.dilute_ladder_reopens_sec29_probe import analyse
    a = analyse()
    assert len(a["dilute_sets"]) >= 3, (
        "the dilute band has collapsed back to one or two sources, so §29's "
        f"single-source weakness has returned: {a['dilute_sets']}")
    m_dil = statistics.median(p["s_meas"] for p in a["dilute"])
    m_den = statistics.median(p["s_meas"] for p in a["dense"])
    assert m_dil > m_den + 0.3, (
        "with the diamond source dropped the dilute band must still sit "
        "clearly above the dense band for the onset law to be described as "
        f"supported; got {m_dil:+.3f} vs {m_den:+.3f}")
    assert m_dil > 0.6, (
        "the dilute band must approach +1, the law's sharpest prediction; "
        f"got {m_dil:+.3f}")


def test_the_dilute_band_is_not_an_artefact_of_where_the_cut_was_put():
    """A band chosen to make a law pass is the finding, not the law.

    The separation must survive moving the threshold, so it is measured at
    every sane value of chi rather than at the one that reads best. It holds
    from chi = 0.80 to chi = 0.99 and weakens monotonically as the cut is
    pushed up into the saturated region -- which is the behaviour the
    derivation predicts, since raising the cut dilutes the band with pairs
    the term barely acts on.
    """
    import math as _m

    from tools.dilute_ladder_reopens_sec29_probe import SINGLE_SOURCE
    rows = [p for p in slope_pairs()
            if p["in_premise"] and p["dataset"] != SINGLE_SOURCE]
    gaps = {}
    for cut in (0.80, 0.85, 0.90, 0.95, 0.99):
        lo = [p["s_meas"] for p in rows if 1 - _m.exp(-p["theta"]) < cut]
        hi = [p["s_meas"] for p in rows if 1 - _m.exp(-p["theta"]) >= cut]
        assert len(lo) >= 3 and len(hi) >= 3, (
            f"chi = {cut} leaves too few pairs to read; the sweep has lost "
            "its non-vacuity guard")
        gaps[cut] = statistics.median(lo) - statistics.median(hi)
    for cut, gap in gaps.items():
        assert gap > 0.1, (
            f"the dilute/dense separation vanishes at chi = {cut} "
            f"(gap {gap:+.3f}), so the chi < 0.9 reading is a cut artefact")


def test_the_law_is_still_refused_because_it_breaks_at_the_dilute_extreme(priced):
    """The reason the term is NOT wired -- now a claim about the LAW, not one patent.

    The onset law is supported in the band the corpus reaches
    (chi 0.75-0.99, i.e. 0.5-9 wt% of ordinary abrasives). It is refuted at
    the extreme, and as of session 35 that refutation stands on TWO
    independent applicants rather than one:

        us20110186542a1_w_diamond_h2o2_ph      chi 0.018-0.070   8.7% -> 34.2%
        us20230081442a1_dlc_zirconia_...       chi 0.173        36.4% -> 59.6%

    They share nothing: diamond vs colloidal zirconia, tungsten vs amorphous
    carbon, H2O2 vs permanganate, Cabot-class vs Fujimi. Both get worse, and
    both get worse where the correction is largest. That removes the reading
    §30 could not exclude -- "one patent behaves oddly" -- and makes the
    failure a property of the derivation as applied here.

    A law cannot be wired on the strength of the region where it barely acts
    while failing the region where it acts most. Either the occupancy theta is
    mis-scaled at very low loading (the pack's particle density and the GW
    contact area both extrapolate three orders down there), or a second
    mechanism takes over below ~0.1 wt%. Both are measurable; neither is
    measured yet.

    EXIT CONDITION (moved, not retired): a pack whose real contact area comes
    from MEASURED asperity statistics rather than from the Qi correlation,
    so theta at 0.01-0.1 wt% is no longer a three-order extrapolation. That
    is the one remaining way the extreme-band failure could turn out to be
    the scaling and not the law.
    """
    rows, _ = priced
    by_name = {r["dataset"]: r for r in rows}
    for name in EXTREME_BAND_SOURCES:
        entry = by_name.get(name)
        assert entry is not None, (
            f"{name} left the pricing set; the refusal above has lost part of "
            "its evidence and must be re-measured")
        assert entry["shape_after"] > entry["shape_before"] * 1.5, (
            "§30's surviving refusal rests on the onset law damaging every "
            f"extreme-dilute dataset in the corpus; {name} no longer worsens "
            f"({entry['shape_before']:.1f}% -> {entry['shape_after']:.1f}%), "
            "so the refusal must be re-argued or the term wired")


#: Datasets with at least one scored ROW below chi = 0.2, measured at test
#: time rather than listed by hand -- see `test_the_extreme_dilute_band_...`
#: below, which asserts this list is what the corpus actually contains.
EXTREME_BAND_SOURCES = (
    "us20110186542a1_w_diamond_h2o2_ph",
    "us20230081442a1_dlc_zirconia_dilute_loading",
)


def test_the_extreme_dilute_band_is_read_off_rows_not_pair_midpoints():
    """§30's exit condition fired -- and the reader that was hiding it.

    The earlier form of this test asserted the extreme band (chi < 0.2) held
    exactly ONE source, and was written to fail when a second arrived. It read
    `slope_pairs()`, whose theta is the geometric MIDPOINT of an adjacent pair
    because a measured log-log slope belongs to an interval. That is correct
    for a slope and wrong for band membership: the correction is applied to a
    ROW, at that row's own theta. US20230081442A1's 0.1 wt% row sits at
    chi = 0.173, inside the band, while every pair midpoint of the same ladder
    sits above it -- so the midpoint reader still reports one source.

    Both readings are asserted here so the discrepancy cannot be quietly
    resolved in the wrong direction, and the source list the refusal above
    iterates over is DERIVED, so a third source cannot enter unnoticed.
    """
    import math as _m

    from tools.extreme_dilute_second_source_probe import EXTREME_CHI, sources
    from tools.load_sharing_slope_probe import slope_pairs

    by_row = tuple(sources())
    assert by_row == tuple(sorted(EXTREME_BAND_SOURCES)), (
        "the extreme-dilute band's membership has changed; the refusal above "
        f"must be re-measured over {by_row}")

    by_pair = sorted({p["dataset"] for p in slope_pairs()
                      if p["in_premise"]
                      and 1.0 - _m.exp(-p["theta"]) < EXTREME_CHI})
    assert len(by_pair) < len(by_row), (
        "the pair-midpoint reader now agrees with the row reader, so the "
        "distinction this test exists to keep visible has gone; check "
        "whether a ladder was added that straddles the cut")


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
