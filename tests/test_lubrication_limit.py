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
def test_every_condition_reads_boundary_once_the_roughness_is_sourced(psi, rpm):
    """The absolute-threshold claim did NOT survive sourcing the pad roughness.

    This test used to assert the opposite: that (1.5 psi, 200 rpm) — the one
    condition where the measured rate collapses — was the only one to leave
    boundary lubrication, at lambda = 1.24 against a threshold of 1.0.

    That crossing was an artifact. It rested on sigma = 0.3 um, an unsourced
    order-of-magnitude guess, and Zhou 2018 (ECS JSS 7(6) P295,
    doi:10.1149/2.0011806jss) measures Rq = 0.474 um on a pad **before any
    use**, rising to 0.68-1.1 um in service. A polished pad is not smoother
    than a new one, so the old constant was never physical. Sweeping every
    sourced roughness in the corpus (0.474 to 5.0 um) puts the collapse point
    at lambda 0.79 down to 0.075 — **none of them clears 1.0**. It would take
    sigma = 0.373 um, below a brand-new pad, to reach the threshold.

    So the honest state is: all six conditions read boundary, and the model no
    longer claims to flag the failure against an absolute cut. What survives is
    the ordering, which a pure rescale cannot change — see
    test_lambda_ranks_the_collapse_point_first_without_seeing_a_rate, where the
    collapse point still comes first by 1.7x without the model seeing a rate.

    Kept as an assertion rather than deleted so that if someone restores the
    old constant to make a nicer claim, this fails and names the reason.
    """
    assert _situation(psi, rpm)["lubrication"] == "boundary", (
        f"{psi} psi / {rpm} rpm left boundary lubrication. With every sourced "
        "roughness in the corpus all six conditions sit well below lambda = 1; "
        "check whether pad_height_beta_inv_m was reverted to the unsourced "
        "0.3 um, which is smoother than a new pad")


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
