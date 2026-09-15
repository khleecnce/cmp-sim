"""Absolute-rate plausibility — the guard against confidently wrong numbers.

Each of these encodes a bug that actually shipped and was caught by comparing
the prediction with published rates for that film.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from cmp_sim.cli import load_config
from cmp_sim.core import sanity
from cmp_sim.core.params import load_pack
from cmp_sim.core.solver import simulate

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((ROOT / "examples").glob("*.yaml"))


# ── the checker itself ───────────────────────────────────────────────
def test_checker_flags_a_rate_far_above_the_published_range():
    w = sanity.check_rate("sic", 6000.0)
    assert w and "IMPLAUSIBLE" in w[0]


def test_checker_flags_a_rate_far_below_the_published_range():
    w = sanity.check_rate("cu", 5.0)
    assert w and "IMPLAUSIBLE" in w[0]


def test_checker_passes_a_reasonable_rate():
    assert sanity.check_rate("oxide", 1500.0) == []
    assert sanity.check_rate("sic", 50.0) == []


def test_unknown_film_says_it_could_not_check_rather_than_passing_silently():
    w = sanity.check_rate("unobtainium", 1234.0)
    assert w and "could not be sanity-checked" in w[0]


# ── the Kp corrections ───────────────────────────────────────────────
def test_sic_does_not_inherit_the_oxide_preston_coefficient():
    """The inherited SiC pack declared `base: sti_ceria` and never overrode Kp,
    so it silently used the OXIDE coefficient and over-predicted SiC by ~128x.
    4H-SiC removes about two orders of magnitude slower than oxide."""
    sic = load_pack("sic_ceria_h2o2").get("kp_m_per_pa")
    oxide = load_pack("sti_ceria").get("kp_m_per_pa")
    assert sic < oxide / 50.0, (sic, oxide)


def test_sic_reproduces_its_own_measured_rate():
    """5.5 psi / 60 rpm is a condition in the source DOE, which reports
    2.7-6.7 nm/min there."""
    r = simulate(load_config(str(ROOT / "examples" / "sic_substrate.yaml")))
    assert 1.0 < r.mean_rr_nm_per_min < 20.0, r.mean_rr_nm_per_min


def test_tungsten_kp_comes_from_data_not_from_a_quoted_range():
    """The inherited W Kp was back-calculated from a quoted 300-600 nm/min
    range and over-predicted by ~4x; two printed patent tables agree on ~7e-14."""
    kp = load_pack("w_fe_oxidizer").get("kp_m_per_pa")
    assert 4.0e-14 < kp < 1.2e-13, kp
    assert load_pack("w_fe_oxidizer").params["kp_m_per_pa"].confidence != "estimated"


def test_contact_factor_cannot_silently_inflate_every_rate():
    """kappa is only applied when the pack's reference pad has a real source.
    Against an `estimated` reference it was inflating rates 2-3x."""
    from cmp_sim.core.solver import resolve
    from cmp_sim.core.state import Recipe, Slurry, Wafer
    from cmp_sim.pad.material import reference_pad_is_trustworthy
    rr = resolve(Recipe(wafer=Wafer(film="oxide"), slurry=Slurry(pack="oxide_silica")))
    assert not reference_pad_is_trustworthy(rr)
    rr2 = resolve(Recipe(wafer=Wafer(film="oxide"),
                         slurry=Slurry(pack="oxide_silica_calibrated_pad")))
    assert reference_pad_is_trustworthy(rr2)


# Examples that are SUPPOSED to refuse, because the literature has no value to
# run them with. They are shipped so the refusal itself is demonstrable and
# tested, not to be quietly skipped.
EXPECTED_TO_REFUSE = {"snag_solder"}

RUNNABLE = [p for p in EXAMPLES if p.stem not in EXPECTED_TO_REFUSE]


# ── every shipped example must be plausible ──────────────────────────
@pytest.mark.parametrize("path", RUNNABLE, ids=lambda p: p.stem)
def test_every_example_runs_and_is_plausible(path):
    result = simulate(load_config(str(path)))
    implausible = [w for w in result.warnings if "IMPLAUSIBLE" in w]
    assert not implausible, implausible
    assert result.mean_rr_angstrom_per_min > 0


@pytest.mark.parametrize("path", RUNNABLE, ids=lambda p: p.stem)
def test_every_example_runs_through_the_cli(path):
    proc = subprocess.run([sys.executable, "-m", "cmp_sim.cli", "run", str(path)],
                          capture_output=True, text=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["removal_rate_A_per_min"] > 0
    assert payload["radial_profile"]["radius_mm"]


@pytest.mark.parametrize("stem", sorted(EXPECTED_TO_REFUSE))
def test_an_example_with_no_published_value_refuses_and_explains_why(stem):
    """It must fail for the documented reason, with a non-zero exit code and a
    message naming the missing parameter — not crash, and not invent a number."""
    path = ROOT / "examples" / f"{stem}.yaml"
    assert path.exists(), f"{stem} is listed as expected-to-refuse but is missing"
    proc = subprocess.run([sys.executable, "-m", "cmp_sim.cli", "run", str(path)],
                          capture_output=True, text=True, cwd=str(ROOT))
    assert proc.returncode != 0, "it ran; the refusal is stale"
    combined = proc.stderr + proc.stdout
    # Either gate is a correct refusal: the maturity gate fires when the film is
    # graded unestablished, the missing-Kp gate when nothing can set the scale.
    assert ("not an established CMP target" in combined
            or "not been sourced" in combined)
    assert "measurements" in combined, "the refusal does not say how to proceed"


@pytest.mark.parametrize("stem", sorted(EXPECTED_TO_REFUSE))
def test_such_an_example_runs_once_the_owner_supplies_the_value(stem):
    """The refusal must be a gap in the data, not a broken model."""
    recipe = load_config(str(ROOT / "examples" / f"{stem}.yaml"))
    recipe.slurry.ph = 6.5
    recipe.measurements = [
        {"rate_A_per_min": 3200, "pressure_psi": 1.0, "rpm_platen": 60},
        {"rate_A_per_min": 6500, "pressure_psi": 2.0, "rpm_platen": 60},
    ]
    result = simulate(recipe)
    assert result.mean_rr_angstrom_per_min > 0
    assert result.extras["calibration"]["kp_m_per_pa"] > 0
    # A real measurement must retire the hardness estimate entirely.
    assert "kp_estimate" not in result.extras
