"""§38 — the PSD-width axis is unidentifiable, and this keeps that honest.

The second-cheapest crosser (`us20190127607a1_teos_ceriasilica_size_sweep`)
is non-monotonic in D50, and the dip is the one broad-PSD abrasive.  The
mechanism (a broader distribution loads a smaller FRACTION of the abrasive at
the same D50) is real and its sign is predicted, but the corpus can neither
identify nor even sign it:

  * exactly ONE publication in the corpus reports a PSD width at all, and its
    two files are the same four polishing runs on two films -- so the holdout
    unit is one (§33);
  * within that one experiment the two oxide films give residual width slopes
    of OPPOSITE sign, and a mechanical particle-count term cannot depend on
    the deposition method of the oxide (§14).

Every number below is re-measured from the shipping solver and the dataset
files at test time; none is copied from docs/limits.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.psd_width_identifiability_probe import report  # noqa: E402

TEOS = "us20190127607a1_teos_ceriasilica_size_sweep"
HDP = "us20190127607a1_hdpoxide_ceriasilica_size_sweep"


@pytest.fixture(scope="module")
def rep():
    return report()


def test_the_probe_finds_rows_at_all(rep):
    """Non-vacuity: a probe that collects nothing passes every other test here."""
    assert rep["rows"] >= 8, rep["rows"]
    assert len(rep["blocks"]) >= 2, sorted(rep["blocks"])


def test_the_width_driver_is_present_on_the_rows(rep):
    """The refusal is about IDENTIFIABILITY, not about a missing key.

    If D99 were simply absent the honest entry would be "transcribe it".  It
    is transcribed, on every row of both files, which is why §38 has to make
    the harder argument.
    """
    for stem in (TEOS, HDP):
        assert stem in rep["blocks"], sorted(rep["blocks"])
        assert rep["blocks"][stem] is not None, stem
        assert rep["blocks"][stem]["n"] >= 4, rep["blocks"][stem]


def test_the_axis_still_rests_on_a_single_SCORED_publication(rep):
    """The corpus-internal half of §38's identifiability argument.

    This still holds and is still the reason no width CONSTANT can be fitted:
    the two files are the same four polishing runs on two films, so the
    holdout unit is one publication (§33).

    ⚠ This is no longer §38's exit condition. §40 retired that role: the exit
    condition was written as "a second applicant appears IN THE CORPUS", and
    that was the wrong place to look — a publication can settle the SIGN of an
    axis while being unscorable for reasons unrelated to it. The live exit
    condition is now `test_a_second_independent_source_reports_the_sign`.
    """
    assert len(rep["sources"]) == 1, (
        "a second SCORED source now reports a PSD width -- re-run "
        "tools/psd_width_identifiability_probe.py and rewrite limits §38/§40 "
        f"from its output: {rep['sources']}")


def test_neither_film_actually_measures_a_width_slope(rep):
    """§40 — the retraction, kept as a live measurement.

    §38 rested its refusal on "the two oxide films disagree in SIGN", which
    would be a genuine refutation of a mechanical term: a particle-count
    mechanism cannot know how the oxide underneath was deposited. The claim
    was read off two point estimates with no uncertainty attached. With the
    standard error computed (n=4, so 2 residual dof) NEITHER slope is
    distinguishable from zero, so the two signs are two draws from noise
    rather than a contradiction.

    The refusal to wire a width term SURVIVES this — one publication still
    cannot supply a magnitude — but it now rests on identifiability alone,
    and this test exists so the retracted reason cannot creep back in.
    """
    ts = [rep["blocks"][s]["t"] for s in (TEOS, HDP)]
    assert all(t is not None for t in ts), ts
    assert all(abs(t) < 2.0 for t in ts), (
        "a film now measures a width slope significantly different from zero "
        f"(t = {ts}). §40 retracted the sign-disagreement claim BECAUSE both "
        "were consistent with noise; if that has changed, re-measure the sign "
        "question and rewrite §40 rather than relaxing this bound.")


def test_the_width_axis_is_confounded_with_the_size_axis_here(rep):
    """Why the corpus block is the WRONG experiment for this axis.

    Width and D50 move together across the patent's four abrasives, so any
    slope read here is partly a relabelled size exponent -- the model already
    reads D50. This is the measured reason the external source (which varies
    width at essentially fixed D50) is the better evidence, and it is asserted
    rather than asserted-in-prose so the comparison stays honest.
    """
    for stem in (TEOS, HDP):
        corr = rep["blocks"][stem]["width_size_corr"]
        assert corr is not None, stem
        assert abs(corr) > 0.2, (
            f"{stem}: width and D50 are now nearly orthogonal (r = {corr:+.3f}), "
            "so this block has become a clean width experiment -- re-measure "
            "the axis instead of inheriting §38/§40's refusal")


def test_a_second_independent_source_reports_the_sign(rep):
    """EXIT CONDITION (live), and the fact §38 was missing.

    §38 asked for "a second, independent applicant" reporting a PSD width
    against removal rate, and looked only among SCORED datasets. Basim 2000
    is that source: a different applicant, abrasive, film, tool and decade,
    varying width at fixed D50 more cleanly than anything in the corpus.

    It is deliberately NOT a scored dataset -- it prints the same six removal
    rates three times with mutually inconsistent absolute values, so only its
    DIRECTION is transcribable. That is exactly why it settles the sign and
    still supplies no constant.
    """
    ext = rep.get("external") or []
    assert ext, (
        "the independent sign evidence for the width axis has disappeared; "
        "research/psd_width_sign_evidence.yaml is the file §40 rests on")
    assert any(e["direction"] == "negative" for e in ext), ext
    for e in ext:
        assert e["magnitude"] is None, (
            "the external source now claims a MAGNITUDE. A sign is not a "
            "constant, and this source cannot supply one -- its own absolute "
            "rates disagree by 2x between text and table. If a magnitude has "
            f"genuinely arrived, it needs its own entry, not this one: {e}")
        assert e["evidence_lines"] >= 3, (
            "the direction must rest on several independently cited readings "
            f"(text, table, figure), not one: {e}")


def test_the_width_span_is_wide_enough_that_the_axis_could_have_been_read(rep):
    """A flat axis is not evidence of unidentifiability -- it is no experiment.

    Guards against the refusal being quietly weakened into "width barely
    varies here", which would be a different (and much weaker) claim.
    """
    for stem in (TEOS, HDP):
        assert rep["blocks"][stem]["width_span"] > 0.4, rep["blocks"][stem]


def test_the_rate_does_not_read_psd_width_but_the_defect_proxy_does():
    """MUTATION GUARD plus §18's "it goes somewhere else" obligation.

    Both halves are asserted, because either alone is an excuse: the rate must
    be provably insensitive to D99 at fixed D50 (so a future width term fails
    loudly here instead of silently inheriting this refusal), AND D99 must
    actually MOVE the defect proxy, so the claim that the key is consumed
    elsewhere is a measurement rather than a deflection.
    """
    from cmp_sim.api import run_recipe

    def _run(d99):
        return run_recipe({
            "model": "auto",
            "wafer": {"film": "oxide", "n_radial": 11},
            "slurry": {"pack": "sti_ceria",
                       "abrasive": {"kind": "ceria", "d50_nm": 117.2,
                                    "d99_nm": d99, "conc_wt_pct": 0.185},
                       "ph": 5.45},
            "tool": {"pressure_psi": 3.7, "rpm_platen": 87.0,
                     "rpm_head": 93.0, "time_s": 60.0},
        })

    narrow, broad = _run(182.7), _run(302.6)
    r_n = narrow.get("removal_rate_A_per_min")
    r_b = broad.get("removal_rate_A_per_min")
    assert r_n and r_b, (r_n, r_b)
    assert abs(r_b - r_n) / r_n < 1e-6, (
        "the removal rate now responds to PSD width -- limits §38 refuses that "
        f"term, so re-measure the refusal rather than inheriting it: {r_n} vs {r_b}")

    d_n = (narrow.get("defect_risk") or {}).get("delta_risk_index")
    d_b = (broad.get("defect_risk") or {}).get("delta_risk_index")
    if d_n is None or d_b is None:  # pragma: no cover - shape guard
        pytest.fail(
            "the defect proxy reported no risk index, so this run cannot show "
            "that D99 is consumed anywhere: "
            f"{narrow.get('defect_risk')}")
    assert d_b > d_n, (
        "D99 must MOVE the defect proxy, otherwise 'the width goes somewhere "
        f"else' is an excuse rather than a destination: {d_n} vs {d_b}")
