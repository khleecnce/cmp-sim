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


def test_the_axis_still_rests_on_a_single_publication(rep):
    """EXIT CONDITION.

    This fails the moment a second applicant reports a PSD width, which is
    the event that makes the axis testable.  Read a failure here as an
    instruction to RE-MEASURE the sign question on the enlarged evidence --
    never as a test to relax.  The unit is the publication, not the file:
    two files from the same four polishing runs are one experiment (§33).
    """
    assert len(rep["sources"]) == 1, (
        "a second source now reports a PSD width -- re-run "
        "tools/psd_width_identifiability_probe.py and rewrite limits §38 from "
        f"its output: {rep['sources']}")


def test_the_two_films_disagree_in_sign(rep):
    """The killing fact, and the one that no amount of data from this source fixes.

    Same abrasives, same runs, two oxide films.  A particle-count mechanism
    cannot know how the oxide was deposited, so opposite residual slopes mean
    no shared width constant is even the right DIRECTION.
    """
    teos = rep["blocks"][TEOS]["slope"]
    hdp = rep["blocks"][HDP]["slope"]
    assert teos < 0 < hdp or hdp < 0 < teos, (teos, hdp)
    # And the disagreement must be substantive, not a sign flip on noise: the
    # films must differ by more than the smaller slope's own magnitude.
    assert abs(teos - hdp) > 0.3, (teos, hdp)


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
