"""limits.md §40 (amended) — the zero-constant lognormal width factor is
PRICED and deliberately NOT WIRED.

The form is

    f(sigma) = exp(-4.5 sigma^2),   sigma = ln(D99/D50) / 2.32635

and it has no fitted constant anywhere in it: both diameters are published,
z99 is a standard-normal quantile and 4.5 = 3^2/2 is the lognormal moment
coefficient.  Its sign is structurally negative, matching the independent
sign evidence in research/psd_width_sign_evidence.yaml.

It is still refused, because a derivation with zero free constants is not
self-justifying: it answers "is this constant earned?" and not "does the data
confirm it?".  On this corpus the answer to the second question is no --
neither residual slope is distinguishable from zero, and the term pays for one
oxide film with the other inside a single experiment.

Every number here is re-measured from the shipping solver at test time.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.lognormal_width_price_probe import (  # noqa: E402
    Z99, sigma_from, width_factor, report,
)

TEOS = "us20190127607a1_teos_ceriasilica_size_sweep"
HDP = "us20190127607a1_hdpoxide_ceriasilica_size_sweep"


@pytest.fixture(scope="module")
def priced():
    return report()


def test_the_probe_prices_both_films(priced):
    """Non-vacuity: an empty report would pass every assertion below."""
    for stem in (TEOS, HDP):
        assert stem in priced, sorted(priced)
        assert priced[stem]["n"] >= 4, priced[stem]


def test_the_derivation_is_a_computation_not_an_assertion():
    """sigma must reproduce the published D99 from D50 -- the zero-constant claim.

    If this inverts correctly the form carries no fitted freedom: the only
    inputs are two printed diameters and a standard-normal quantile.
    """
    d50, d99 = 156.1, 302.6
    sigma = sigma_from(d50, d99)
    assert sigma is not None
    assert d50 * math.exp(Z99 * sigma) == pytest.approx(d99, rel=1e-9), (
        "sigma no longer inverts to the published D99, so the 'no free "
        "constant' claim has stopped being a computation")
    # And the factor's sign is structural: broader is always fewer particles.
    assert width_factor(sigma) < 1.0
    assert width_factor(0.0) == pytest.approx(1.0)


def test_the_term_pays_for_one_film_with_the_other(priced):
    """The load-bearing fact of the refusal.

    One experiment, four polishing runs, two oxide films. A mass-dosed
    particle-count term cannot know the deposition method, so improving one
    while degrading the other is a block swap rather than physics.
    """
    d_teos = priced[TEOS]["after"] - priced[TEOS]["before"]
    d_hdp = priced[HDP]["after"] - priced[HDP]["before"]
    assert d_teos < 0 < d_hdp or d_hdp < 0 < d_teos, (
        "the two films now move the same way under the width factor "
        f"({d_teos:+.1f} / {d_hdp:+.1f} pp). That removes the central reason "
        "§40's amendment refuses the term -- re-measure and rewrite it rather "
        "than wiring on a stale refusal")


def test_neither_film_measures_the_predicted_slope(priced):
    """EXIT CONDITION.

    (W) predicts a residual slope of +1.00 against ln f. Measured: +1.95+/-1.04
    and -0.04+/-0.78 on 2 dof -- consistent with the prediction AND with zero,
    which is what "unconfirmed" means. A failure here means a block has
    acquired a real slope: re-price the term, do not relax this.
    """
    for stem in (TEOS, HDP):
        r = priced[stem]
        assert r["slope"] is not None and r["stderr"] is not None, r
        if r["stderr"] == 0:
            pytest.fail(f"{stem}: zero residual scatter, slope is not a fit: {r}")
        t = r["slope"] / r["stderr"]
        assert abs(t) < 2.0, (
            f"{stem}: the width residual slope is now significant (t={t:+.2f}). "
            "The data may now confirm f(sigma) -- re-run "
            "tools/lognormal_width_price_probe.py and rewrite §40's amendment")


def test_the_solver_does_not_apply_the_width_factor():
    """MUTATION GUARD -- the refusal must stay true of the shipping model.

    Two abrasives with the same D50 and loading but different D99 (hence
    different sigma, hence different f) must still predict the same rate. If a
    later session wires (W), this fails loudly instead of the refusal being
    silently inherited as documentation.
    """
    from cmp_sim.api import run_recipe

    def _run(d99):
        return run_recipe({
            "model": "auto",
            "wafer": {"film": "oxide", "n_radial": 11},
            "slurry": {"pack": "sti_ceria",
                       "abrasive": {"kind": "ceria", "d50_nm": 156.1,
                                    "d99_nm": d99, "conc_wt_pct": 0.185},
                       "ph": 5.45},
            "tool": {"pressure_psi": 3.7, "rpm_platen": 87.0,
                     "rpm_head": 93.0, "time_s": 60.0},
        })

    narrow = _run(182.7)["removal_rate_A_per_min"]
    broad = _run(302.6)["removal_rate_A_per_min"]
    assert narrow and broad
    # The factor these two would differ by, if (W) were wired.
    s_n = sigma_from(156.1, 182.7)
    s_b = sigma_from(156.1, 302.6)
    assert s_n is not None and s_b is not None
    expected = width_factor(s_b) / width_factor(s_n)
    assert expected < 0.95, (
        "the two probe points no longer differ enough for this guard to "
        f"detect a wired width factor (ratio {expected:.3f})")
    assert abs(broad - narrow) / narrow < 1e-6, (
        "the rate now responds to PSD width. §40's amendment PRICED and "
        f"REFUSED that term: {narrow} vs {broad}")
