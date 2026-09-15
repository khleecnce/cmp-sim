"""Why SiC fails the Preston gate, stated as a measurement rather than an excuse.

The claim "SiC is chemically rate-limited" is easy to assert and easy to abuse:
it could excuse any bad fit. So it is tested numerically against the 50-run DOE.

If removal were mechanically limited, then at IDENTICAL pressure and velocity
Preston would predict a single rate whatever the chemistry. The DOE holds P and
V fixed while varying pH, oxidiser and abrasive loading, so the spread within
such a group is a direct measure of how much of the process Preston cannot see.
"""
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
import yaml

DATASET = (Path(__file__).resolve().parents[1] / "legacy" / "validation" /
           "datasets" / "sic2026_ceria_h2o2_ph_DOE50.yaml")


@pytest.fixture(scope="module")
def rows():
    data = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    return data["conditions"]


def _groups(rows, min_n=3):
    g = defaultdict(list)
    for r in rows:
        g[(r["pressure_psi"], r["rpm_platen"])].append(r["mrr_nm_per_min"])
    return {k: v for k, v in g.items() if len(v) >= min_n}


def test_the_rate_varies_severalfold_at_identical_pressure_and_velocity(rows):
    """Preston predicts a ratio of exactly 1.0 within each group."""
    spreads = [max(v) / min(v) for v in _groups(rows).values()]
    assert spreads, "the DOE no longer holds P and V fixed across runs"
    assert float(np.median(spreads)) > 3.0, (
        "the chemistry spread has collapsed; the claim that this system is "
        "chemically limited would no longer be supported by its own data")


def test_pressure_times_velocity_explains_almost_none_of_the_variance(rows):
    """R^2 of MRR against P*V across the whole DOE."""
    pv = np.array([r["pressure_psi"] * r["rpm_platen"] for r in rows], float)
    mrr = np.array([r["mrr_nm_per_min"] for r in rows], float)
    r2 = float(np.corrcoef(pv, mrr)[0, 1] ** 2)
    assert r2 < 0.25, (
        f"P*V now explains {r2:.0%} of the variance; if it genuinely does, this "
        "system is not chemically limited and the SiC exemption should be "
        "reconsidered rather than kept as a standing excuse")


def test_no_preston_coefficient_can_rescue_this_dataset(rows):
    """Kp is a single scale factor, so it cannot change the shape at all.

    Fit the best possible Kp by least squares and show the residual stays far
    outside the gate: the failure is structural, not a calibration error.
    """
    pv = np.array([r["pressure_psi"] * r["rpm_platen"] for r in rows], float)
    mrr = np.array([r["mrr_nm_per_min"] for r in rows], float)
    kp = float((pv * mrr).sum() / (pv * pv).sum())
    mape = float(np.abs((kp * pv - mrr) / mrr).mean() * 100.0)
    assert mape > 15.0, (
        f"the best possible Kp now fits to {mape:.1f}%; the documented "
        "structural failure is stale and should be re-examined")


def test_the_chemically_limited_profile_is_selected_for_this_system():
    """The simulator must route SiC away from a pure mechanical law."""
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

    r = simulate(Recipe(
        model="auto",
        wafer=Wafer(film="sic", n_radial=11),
        slurry=Slurry(pack="sic_ceria_h2o2"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=5.5, rpm_platen=60, rpm_head=60, time_s=60)))
    assert r.extras["profile"] == "chemically_limited"
    assert r.extras["situation"]["rate_limit"] == "chemical"


def test_the_absolute_rate_stays_inside_the_measured_range(rows):
    """Ranking is trustworthy here; the absolute number must at least be sane."""
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

    lo = min(r["mrr_nm_per_min"] for r in rows)
    hi = max(r["mrr_nm_per_min"] for r in rows)
    r = simulate(Recipe(
        model="auto",
        wafer=Wafer(film="sic", n_radial=11),
        slurry=Slurry(pack="sic_ceria_h2o2"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=5.5, rpm_platen=60, rpm_head=60, time_s=60)))
    predicted = r.mean_rr_angstrom_per_min / 10.0      # A/min -> nm/min
    assert lo <= predicted <= hi, (
        f"predicted {predicted:.2f} nm/min is outside the measured "
        f"{lo:.2f}-{hi:.2f} nm/min range of the DOE")
