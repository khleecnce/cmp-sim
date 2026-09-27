"""docs/limits.md must stay a complete, accurate index of what the model refuses.

Three separate findings this project has made were closed by naming a structural
limit rather than by refitting a constant: the unresolvable velocity exponent, the
pressure-coupled oxidiser sign, and ceria's non-unimodal pH response. Several more
decided refusals sit alongside them.

Before docs/limits.md existed, each lived only in its own test file and pack
comment, so a reader had no single place saying what the model CANNOT do — and,
worse, nothing stopped a later session from quietly "fixing" one of them.

These tests keep that page honest in both directions:

  - every test that enforces a limit must be CITED by the page, so a new
    structural limit cannot be added without documenting it;
  - every test the page cites must EXIST, so the page cannot rot into claims
    about files that were renamed or deleted;
  - each entry must carry the three things that make a limit reviewable rather
    than an excuse: the measurement, the rejected refit, and the experiment that
    would resolve it.

The last point is the one that matters most. 'We cannot model this' is only
acceptable when accompanied by what was measured, what was tried, and what would
change the answer. Without those, a documented limit is indistinguishable from an
undocumented failure.
"""
from __future__ import annotations

import re
from pathlib import Path

import cmp_sim

DOCS = Path(cmp_sim.__file__).parent.parent / "docs"
TESTS = Path(cmp_sim.__file__).parent.parent / "tests"
LIMITS = DOCS / "limits.md"

#: Tests that enforce a decided refusal to predict. A test added here MUST be
#: cited by docs/limits.md — that is the point of the registry.
LIMIT_ENFORCING_TESTS = {
    # limit 25: the load-sharing axis (chi) is closed on identifiability —
    # its only input is analytically pinned at 1, it reaches almost no rate,
    # and the grade it was blamed for is really a discarded MEASURED alpha
    "test_chi_axis_closed_on_identifiability.py",
    # limit 24: the supply axis (p, q) was never decided — closed from the
    # lubrication regime with zero constants, and the naive gap wiring
    # rejected because the MEAN fluid film is measured in the wrong place
    "test_supply_axis_decided_from_lubrication.py",
    "test_velocity_exponent_unresolvable.py",
    "test_lubrication_gate_is_wrong_not_premature.py",
    "test_contact_metrics_do_not_separate_the_inversion.py",
    "test_oxidizer_sign_tracks_pressure.py",
    "test_two_ceria_datasets_demand_opposite_ph_terms.py",
    "test_no_universal_second_ph_channel.py",
    "test_ph_validity_range_is_declared.py",
    "test_out_of_range_ph_is_a_warning_not_a_gate.py",
    "test_replicate_noise_floor.py",
    # the same limit, extended: a floor can exist and still be unmeasurable,
    # and the column that reports it must not become a scoring change
    "test_noise_floor_can_exist_unmeasured.py",
    "test_replicate_column_is_reporting_only.py",
    "test_pack_axis_blindness_audit.py",
    "test_titanium_is_unsupported.py",
    "test_silica_variant_packs_earn_their_split.py",
    "test_parameter_evidence_inventory.py",
    "test_scale_column_is_reporting_only.py",
    "test_readme_numbers_are_computed.py",
    "test_inherited_kp_is_not_the_problem.py",
    "test_calibration_recovers_a_known_factor.py",
    # limit 13: the P-V interaction is real and both candidate mechanisms are
    # rejected with zero fitted constants; the axis is thin and priced
    "test_pv_interaction_closed.py",
    # limit 14: the improvable error is DISTRIBUTED across axes; tightening the
    # bound from a per-dataset oracle to a shared exponent collapses four of
    # six axes because their exponents disagree in sign
    "test_axis_error_is_distributed.py",
    # limit 14, amended twice: the second amendment withdraws its own
    # predecessor's "derivation target with a definite sign" on
    # abrasive_wt_pct, because withdrawing abrasive_conc_half_wt_pct shrank
    # the shared gain back below the bar. The constant's replacement is a
    # CONDITION for restoring it, not an absence, and that is what this file
    # pins.
    "test_predictive_accuracy.py",
    # limit 15: the oxidiser half order is refuted (two admissible blocks
    # measure a NEGATIVE order) and the census gain that motivated it is
    # inadmissible (one calibration set, one promoter-confounded body)
    "test_oxidizer_order_is_not_half.py",
    # limit 16: <= 10 % is above the ceiling of any shared-constant model here
    # (free per-dataset exponents reach only 11.9 %), and the unowned block is
    # the part the model gets right rather than the hard part
    "test_ten_percent_is_out_of_reach.py",
    # limit 17: 15 % is NOT a measurement floor — the sources that state their own
    # reproducibility span 1.5-37 %, so a corpus-wide floor cannot be claimed in
    # either direction, and a within-wafer SD is not reproducibility at all
    "test_stated_reproducibility.py",
    # limit 18: two swept axes (chelator_M, promoter_M) were INERT — sourced
    # inherited terms that this wrapper never called. The chelator term is now
    # wired; the promoter term is held off because its pack reference is 0 M,
    # so the shape gain would cost a 13x absolute-scale error
    "test_chelator_promoter_axes_are_wired.py",
    # limit 19: the EXHAUSTIVE inert-axis scan (91 swept axes / 46 datasets).
    # Every inhibitor sweep in the corpus was dead on a unit mismatch, and
    # connecting it exposed that the only reachable BTA constant is an
    # EQUILIBRIUM one, refuted 18.4x vs a measured 1.21x. Refused below the
    # reference, where the error fabricates a rate, and left above it, where
    # it is bounded and merely quiet
    "test_every_swept_axis_is_connected.py",
    # limit 20: the last four SILENT axes now declare themselves. Three
    # different causes (wrong path, correct-by-design, sourced null result),
    # zero constants added, and the known-silent allowlist is now empty
    "test_silent_axes_now_declare_themselves.py",
    # limit 21: the ceria Ce3+ axis is closed on IDENTIFIABILITY — the
    # published theta(D) relation holds out of sample, but theta is reachable
    # only through D50, which the size term already reads, so no block varies
    # Ce3+ at fixed size and the three that vary it disagree in sign
    "test_ce3_axis_is_closed.py",
    # limit 22: the absolute-rate failure is NOT a mis-anchored constant. The
    # miss population is centred (no global missing factor) and four of five
    # failing packs disagree with themselves by 8-222x under one shared Kp
    "test_absolute_scale_is_not_one_constant.py",
    # limit 23: nine of the eleven absolute-scale failures were ALREADY
    # identified in dataset prose the scorer cannot read, and sti_ceria's own
    # excluded composite Kp predicts the scale of the two blocks it excluded
    "test_kp_provenance_is_identified.py",
}


def _text() -> str:
    return LIMITS.read_text(encoding="utf-8")


def _entries() -> list[str]:
    """The numbered limit sections."""
    parts = re.split(r"\n## \d+\. ", _text())
    return parts[1:]


def test_the_limits_page_exists_and_is_substantial():
    assert LIMITS.exists(), "docs/limits.md is missing"
    assert len(_text()) > 5000, len(_text())


def test_it_distinguishes_itself_from_open_questions():
    """Undecided items belong in open-questions.md; decided refusals here."""
    text = _text()
    assert "open-questions.md" in text
    assert "settled" in text.lower() or "decided" in text.lower()
    assert "None of these is a TODO" in text


def test_every_limit_enforcing_test_is_cited():
    text = _text()
    missing = sorted(name for name in LIMIT_ENFORCING_TESTS
                     if name not in text)
    assert not missing, (
        f"{missing} enforce a structural limit but are not cited in "
        "docs/limits.md. A limit that is not written down is a limit the next "
        "session will 'fix'.")


def test_every_cited_test_actually_exists():
    cited = set(re.findall(r"tests/(test_[a-z0-9_]+\.py)", _text()))
    assert cited, "no test files cited"
    missing = sorted(name for name in cited if not (TESTS / name).exists())
    assert not missing, f"docs/limits.md cites non-existent tests: {missing}"


def test_the_registry_matches_the_citations():
    """Catches a limit test added to the page but not to the registry."""
    cited = set(re.findall(r"tests/(test_[a-z0-9_]+\.py)", _text()))
    unregistered = cited - LIMIT_ENFORCING_TESTS
    assert not unregistered, (
        f"{sorted(unregistered)} are cited as enforcing a limit but are not in "
        "LIMIT_ENFORCING_TESTS; add them deliberately")


def test_there_are_enough_entries_to_cover_the_named_limits():
    assert len(_entries()) >= 8, len(_entries())


def test_each_entry_names_the_measurement_behind_it():
    for entry in _entries():
        title = entry.splitlines()[0]
        assert "measurement" in entry.lower() or "measured" in entry.lower(), (
            f"'{title}' does not say what was measured")


def test_each_entry_names_the_refit_that_was_rejected_or_the_decision_taken():
    for entry in _entries():
        title = entry.splitlines()[0]
        lowered = entry.lower()
        assert ("rejected" in lowered or "the decision" in lowered), (
            f"'{title}' does not say what was tried and refused; without that "
            "the limit is indistinguishable from an untried one")


def test_each_entry_says_what_would_resolve_it():
    for entry in _entries():
        title = entry.splitlines()[0]
        lowered = entry.lower()
        assert ("would resolve it" in lowered
                or "deliberately *not* a gate" in lowered
                or "unknown" in lowered), (
            f"'{title}' does not name the experiment that would lift the limit")


def test_each_entry_points_at_its_enforcing_test():
    for entry in _entries():
        title = entry.splitlines()[0]
        assert "Enforced by" in entry, (
            f"'{title}' is not tied to a test, so nothing stops it being undone")


def test_the_quantitative_claims_carry_numbers():
    """A limit stated without figures cannot be checked by a reviewer.

    Note the page is prose and uses a Unicode minus sign, so each figure is
    checked in both forms rather than assuming ASCII.
    """
    text = _text().replace("\u2212", "-")
    for figure in ("-0.42", "1.10",      # velocity exponent spread
                   "0.00739",             # summit_saturation = k*P
                   "492.6%",              # cost of the netzband refit
                   "z = -0.15",           # the no-gate measurement
                   "13.0%",               # hong2007 replicate scatter
                   "0.958"):              # the W pH null result
        assert figure in text, f"{figure} missing from docs/limits.md"
