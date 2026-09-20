"""The lubrication limit of Preston's law, against US 6,918,821 B2 Table 1.

This is the strongest validation result in the project, because the model is
not being fitted here — it is predicting where it will fail.

The patent polished copper on an IC1000 pad at two pressures and three speeds.
At 4.0 psi the rate rises with speed as Preston requires. At 1.5 psi it FALLS:
425 -> 419 -> 250 A/min as the platen goes 60 -> 120 -> 200 rpm. No single Kp
can describe both branches.

The regime detector sees only pressure, speed, pad and flow — never a measured
rate — and flags exactly the point where the collapse happens.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

#: US 6,918,821 B2 TABLE 1, IC1000 rows. Verified against the official PDF.
MEASURED = {
    (1.5, 60): 425.0, (1.5, 120): 419.0, (1.5, 200): 250.0,
    (4.0, 60): 594.0, (4.0, 120): 1384.0, (4.0, 200): 1636.0,
}


def _situation(psi, rpm):
    return simulate(Recipe(
        model="auto",
        wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta"),
        pad=Pad(name="IC1000", groove_width_mm=0.5, groove_pitch_mm=2.0,
                groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=psi, rpm_platen=rpm, rpm_head=rpm,
                  time_s=60.0, flow_ml_min=150.0),
    )).extras["situation"]


def test_the_measured_rate_inverts_at_low_pressure():
    """Guards the transcription: the anomaly must survive in the data."""
    assert MEASURED[(1.5, 200)] < MEASURED[(1.5, 60)], "the inversion is gone"
    assert MEASURED[(4.0, 200)] > MEASURED[(4.0, 60)], "the normal branch is gone"


def test_preston_cannot_describe_both_branches():
    """Ratio over 60 -> 200 rpm: Preston demands 3.33x at both pressures."""
    low = MEASURED[(1.5, 200)] / MEASURED[(1.5, 60)]
    high = MEASURED[(4.0, 200)] / MEASURED[(4.0, 60)]
    assert low < 1.0, "low-pressure branch no longer contradicts Preston"
    assert high > 2.0
    assert low < high


@pytest.mark.parametrize("psi,rpm", sorted(MEASURED))
def test_only_the_collapse_point_leaves_the_boundary_regime(psi, rpm):
    """The detector never sees a rate; it works from lambda = h/roughness."""
    lubrication = _situation(psi, rpm)["lubrication"]
    if (psi, rpm) == (1.5, 200):
        assert lubrication != "boundary", (
            "the one condition where the measured rate collapses was not "
            "flagged as leaving boundary lubrication")
    else:
        assert lubrication == "boundary", (
            f"{psi} psi / {rpm} rpm was flagged as {lubrication}, but its "
            "measured rate follows Preston")


def test_lambda_rises_with_speed_and_falls_with_load():
    """The physical ordering behind the flag."""
    lam = {k: _situation(*k)["metrics"]["lambda_ratio"] for k in MEASURED}
    assert lam[(1.5, 200)] > lam[(1.5, 60)], "film does not thicken with speed"
    assert lam[(1.5, 200)] > lam[(4.0, 200)], "load does not thin the film"


def test_lambda_ranks_the_collapse_point_first_without_seeing_a_rate():
    """The part of the claim that survives sourcing the pad roughness.

    The absolute threshold does not: no sourced roughness in the corpus puts
    this point above lambda = 1 (see docs/open-questions.md), because lambda
    scales as 1/sigma and the old 0.3 um was below a NEW pad's measured Rq.

    A pure rescale cannot change an ordering, so this statement is independent
    of which roughness constant is right - and it is still the useful one:
    the condition where the measured rate collapses is the one with the
    thickest fluid film in the whole window, picked out without a rate.
    """
    lam = {k: _situation(*k)["metrics"]["lambda_ratio"] for k in MEASURED}
    worst = max(lam, key=lambda k: lam[k])
    assert worst == (1.5, 200), (
        f"the thickest-film condition is {worst}, but the rate collapses at "
        "(1.5 psi, 200 rpm)")
    assert lam[worst] == max(lam.values())
    runner_up = max(v for k, v in lam.items() if k != worst)
    assert lam[worst] / runner_up > 1.5, (
        "the collapse point is no longer a clear outlier in lambda, so the "
        "ranking argument is as weak as the threshold one")


def test_this_dataset_is_kept_as_a_documented_failure():
    """It must not be quietly converted into a passing fit by splitting it."""
    from pathlib import Path

    from cmp_sim.core.validation import fit_dataset
    path = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data" /
            "validation" / "datasets" /
            "us6918821b2_cu_ic1000_pressure_speed_2x3.yaml")
    fits = fit_dataset(path)
    assert fits, "the dataset stopped producing a fit"
    full = max(fits, key=lambda f: f.n)
    assert full.n == 6, "the six conditions were split into subsets"
    assert full.mape_pct > 15.0, (
        "this dataset is expected to FAIL the Preston gate; if it now passes, "
        "either the data or the fit changed and the documented limit is stale")
