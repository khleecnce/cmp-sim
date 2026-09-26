"""The ceria Ce3+ axis is CLOSED, and the reason is identifiability, not effort.

Pre-registered in STATUS.md (19th run) as the next physics question: five ceria
blocks sit in the corpus's worst tail, the pH route was closed for them in §5
and §14, and the mechanism their own authors name is Cook's chemical tooth —
removal through Si-O-Ce condensation at surface **Ce3+ sites**. Ce3+ fraction
(theta) is an XPS-measurable MATERIAL PROPERTY, so if the residual ordered by
it, a free constant would have been replaced by a property rather than a fit.

It does not, and the decisive finding is structural rather than statistical:

  * The published theta(D) relation is REAL and holds out of sample (Q2), so
    this is not a case of bad input data.
  * But theta is reachable ONLY through D, and D already drives the rate
    through the size term. Inside a block theta is a strictly monotone
    function of D50, so no block in the corpus varies theta at fixed D50 —
    zero of nine admissible blocks. Any gain credited to Ce3+ here would be
    the size term fitted a second time under a new name.
  * Where theta does vary, the three blocks' residual slopes DISAGREE IN SIGN
    (-0.302 / +0.039 / +0.276), which is the §14 signature of dispersion
    rather than a missing law, and the mechanism pre-registers a positive sign.

These tests pin the closure and — more importantly — pin the EXIT: a future
dataset that prints its own XPS Ce3+ makes `blocks_with_own_xps_theta` non-zero
and fails `test_the_axis_stays_closed_only_while_theta_is_unidentifiable`, so
the refusal cannot become permanent by accident.
"""
from __future__ import annotations

import pytest

from tools.ce3_residual_probe import (
    HWANG_2026_HELD_OUT, NETZBAND_2019_TABLE_I, NON_CERIA_ABRASIVE,
    Q2_TOLERANCE_PCT, collect, fit_theta_of_d, identifiability, q2_holdout,
    q3_between_blocks, q3_within_block, theta_of_d,
)


@pytest.fixture(scope="module")
def blocks():
    return collect()


# ---------------------------------------------------------------- Q2: the input
def test_the_published_theta_of_size_relation_is_a_power_law_that_fits():
    """theta = A*D^m on Netzband 2019 Table I — the input is not the problem.

    Recorded so the closure below cannot be read as "the Ce3+ data were bad".
    """
    _, m, r2 = fit_theta_of_d()
    assert r2 > 0.9, f"theta(D) is not a power law here (R^2={r2:.3f})"
    assert -1.0 < m < 0.0, (
        f"m={m:.3f}: Ce3+ must RISE as particles shrink (more under-coordinated "
        "surface cerium), and shallower than the fixed-shell limit m=-1")


def test_theta_of_size_survives_an_independent_laboratory():
    """Hwang 2026 never informed the fit and lands inside the +-30 % bar.

    A relation fitted to three points from one lab is worthless without this;
    with it, the closure below rests on a relation that demonstrably transfers.
    """
    held = q2_holdout()
    assert len(held) == len(HWANG_2026_HELD_OUT)
    outside = [h for h in held if not h["within_bar"]]
    assert not outside, (
        f"held-out theta misses the +-{Q2_TOLERANCE_PCT:.0f} % bar: {outside}")


def test_the_two_theta_sources_are_independent():
    """Guard against the fit and its hold-out quietly becoming the same data."""
    fitted_sizes = {d for d, _ in NETZBAND_2019_TABLE_I}
    held_sizes = {d for d, _ in HWANG_2026_HELD_OUT}
    assert not (fitted_sizes & held_sizes), (
        "a hold-out point shares a particle size with the fit; it is no longer "
        "independent evidence")


# ------------------------------------------------- Q1/Q4: who is allowed to speak
def test_a_ceria_pack_does_not_make_the_abrasive_ceria(blocks):
    """Three blocks borrow a ceria pack as a declared placeholder.

    Alumina and silica have no Ce 3d spectrum, so scoring them against a Ce3+
    property would be measuring a quantity the material does not possess — and
    they are size sweeps, so they would inject exactly the theta-vs-D artefact
    this probe exists to detect.
    """
    names = {b.dataset for b in blocks}
    for dataset in NON_CERIA_ABRASIVE:
        assert dataset in names, (
            f"{dataset} is on the exclusion list but is no longer collected; "
            "the list has gone stale")
    for b in blocks:
        if b.dataset in NON_CERIA_ABRASIVE:
            assert not b.can_testify


def test_the_calibration_block_cannot_testify(blocks):
    """13th-run rule: a block the pack was fitted on recognises itself."""
    calibrated = [b for b in blocks if b.used_for_calibration]
    assert calibrated, "expected at least one ceria calibration block"
    for b in calibrated:
        assert not b.can_testify


# --------------------------------------------------------- Q4: the real finding
def test_theta_is_not_identifiable_apart_from_particle_size(blocks):
    """THE CLOSURE. Zero blocks vary theta while holding D50 fixed.

    This is a property of the corpus AND of the route to theta, not of the
    fitting. Adopting a Ce3+ term on this evidence would double-count the size
    term, which is the §18 promoter mistake in a different costume.
    """
    ident = identifiability(blocks)
    assert ident["admissible"] >= 5, ident
    assert ident["theta_varies_at_fixed_d50"] == 0, (
        "a block now varies Ce3+ at fixed D50 — the axis is identifiable and "
        "this closure must be re-examined, not extended")


def test_the_axis_stays_closed_only_while_theta_is_unidentifiable(blocks):
    """The EXIT CONDITION, asserted rather than described.

    A refusal with no way out becomes permanent by accident. The moment a
    dataset carries its own XPS Ce3+ (rather than one derived from size), this
    test fails and the axis is reopened deliberately.
    """
    ident = identifiability(blocks)
    assert ident["blocks_with_own_xps_theta"] == 0, (
        "a block now reports its own measured Ce3+ fraction; theta no longer "
        "has to come through D50, so re-run the probe and re-decide the axis")


# ------------------------------------------------- Q3: and the sign disagrees too
def test_where_theta_does_vary_the_residual_slopes_disagree_in_sign(blocks):
    """Second, independent reason to close: no shared law can serve all three.

    Cook's tooth pre-registers a POSITIVE slope (more Ce3+ sites, faster
    removal). One of the three measured slopes is negative, which is the §14
    dispersion signature rather than a law waiting to be written.
    """
    rows = [r for r in q3_within_block(blocks) if r["slope"] is not None]
    assert len(rows) >= 3, rows
    signs = {r["slope"] > 0 for r in rows}
    assert signs == {True, False}, (
        f"slopes no longer disagree in sign: {[(r['dataset'], round(r['slope'], 3)) for r in rows]}; "
        "the second closure argument has changed and must be re-stated")


def test_the_between_block_correlation_is_not_evidence(blocks):
    """A large between-block slope with no explanatory power is scatter.

    Pinned because it is the number a later run would be tempted to quote: the
    slope is steep, but it is fitted across laboratories, films and polishers,
    and §14 already attributed that variance to between-dataset dispersion.
    """
    between = q3_between_blocks(blocks)
    assert between is not None
    assert between["r2"] < 0.5, (
        f"between-block R^2 rose to {between['r2']:.3f}; if that survives a "
        "within-block test it is worth revisiting, but it is still confounded "
        "with every other difference between the papers")


def test_the_probe_changes_no_pack(blocks):
    """It measures. The sti_ceria Ce3+ constants must be exactly as shipped."""
    from cmp_sim.core.params import load_pack
    pack = load_pack("sti_ceria")
    assert pack.params["ce3_fraction"].value == 0.15
    assert pack.params["ce3_fraction_ref"].value == 0.15
    assert pack.params["ceria_tooth_gain"].value == 1.0
