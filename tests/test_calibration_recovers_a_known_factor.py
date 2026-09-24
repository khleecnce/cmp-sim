"""The calibration limit 11 prescribes is already implemented: `cmp-sim fit`.

Limit 11 tells a user that one calibration wafer re-anchors `Kp` for their tool
and turns the model's ranking claim into a rate claim. STATUS then asked for a
new `cmp-sim calibrate` command to make that possible. It is not needed:
`cmp-sim fit` has done exactly this all along, and the useful work is proving it
recovers a known answer and wiring it to the limit that asks for it.

WHAT WAS VERIFIED

Take `examples/oxide_baseline.yaml`, simulate three conditions, multiply every
predicted rate by a known 2.5x to fake a faster tool, and feed those three
numbers back through `cmp-sim fit`:

    run-2.0-60   2416.3 A/min
    run-4.0-60   4832.6 A/min
    run-3.0-90   5459.2 A/min
    -> Kp  2.3289e-13 m/Pa,  +/-0.3% leave-one-out

A NEAR-MISS WORTH RECORDING

2.3289e-13 against a pack `Kp` of 1.0e-13 looks like it recovered 2.33x, not the
2.5x that was injected — a 7% shortfall that would suggest a biased fit. It is
not a bias. `fit` regresses a *bare Preston* scale (Kp x P x V), while
`simulate()` multiplies that by the chemistry, contact and uniformity factors.
For this recipe those factors net to 0.929, so the honest target is
0.929 x 2.5 x 1e-13 = 2.322e-13, and the fit lands within 0.3% of it — exactly
the leave-one-out error it reports.

The lesson is the assertion below: a fitted `Kp` is an EFFECTIVE Preston
constant for the user's tool, not the pack constant times a tool factor. Testing
it against the pack constant would have manufactured a 7% bug that does not
exist.

WHY CALIBRATION MUST STAY OUT OF THE CORPUS

If a user factor could reach dataset scoring, the validation would be measuring
itself. The last test pins that: fitting does not move the corpus medians.
"""
from __future__ import annotations

import csv
import math
import subprocess
import sys
from pathlib import Path

from cmp_sim.api import simulate
from cmp_sim.cli import load_config
from cmp_sim.core.params import load_pack

CONFIG = "examples/oxide_baseline.yaml"
INJECTED = 2.5
CONDITIONS = ((2.0, 60), (4.0, 60), (3.0, 90))


def _measurements():
    rows = []
    for pressure, rpm in CONDITIONS:
        recipe = load_config(CONFIG)
        recipe.tool.pressure_psi = pressure
        recipe.tool.rpm_platen = rpm
        rate = simulate(recipe).mean_rr_angstrom_per_min * INJECTED
        rows.append((f"run-{pressure}-{rpm}", pressure, rpm, rate))
    return rows


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["label", "pressure_psi", "rpm_platen",
                         "rate_A_per_min"])
        for label, pressure, rpm, rate in rows:
            writer.writerow([label, pressure, rpm, f"{rate:.1f}"])


def _effective_preston_kp():
    """The model's bare-Preston scale, which is what `fit` regresses."""
    recipe = load_config(CONFIG)
    result = simulate(recipe)
    pressure_pa = recipe.tool.pressure_psi * 6894.757
    velocity = 2 * math.pi * (recipe.tool.rpm_platen / 60.0) * 0.20
    kp_a_per_min = result.mean_rr_angstrom_per_min / (pressure_pa * velocity)
    return kp_a_per_min * 1e-10 / 60.0


def test_fit_recovers_an_injected_tool_factor(tmp_path):
    csv_path = tmp_path / "calibration.csv"
    _write_csv(csv_path, _measurements())

    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "fit", CONFIG, str(csv_path)],
        capture_output=True, text=True, check=True).stdout

    line = next(ln for ln in out.split("\n") if ln.strip().startswith("Kp"))
    fitted = float(line.split()[1])

    expected = _effective_preston_kp() * INJECTED
    assert abs(fitted - expected) / expected < 0.02, (
        f"fit returned {fitted:.4e}, expected ~{expected:.4e} "
        f"(the model's effective Preston Kp times the injected {INJECTED}x)")


def test_the_fitted_kp_is_effective_not_the_pack_constant_times_the_factor():
    """The near-miss this file exists to record.

    Comparing a fitted Kp with `pack Kp x tool factor` invents a ~7% bug: the
    chemistry and contact factors sit between them.
    """
    pack_kp = load_pack("oxide_silica").param("kp_m_per_pa").value
    effective = _effective_preston_kp()
    ratio = effective / pack_kp
    assert abs(ratio - 1.0) > 0.02, (
        "the model's effective Preston scale now equals the pack constant, so "
        "this warning no longer applies — but check why the chemistry factors "
        "became unity before deleting it")
    assert 0.5 < ratio < 2.0, (
        f"effective/pack Kp is {ratio:.3f}; a factor that far from 1 means the "
        "non-Preston factors are doing something unexpected on this recipe")


def test_fit_reports_what_it_cannot_identify(tmp_path):
    """Calibration must refuse to fit factors the data cannot support."""
    csv_path = tmp_path / "calibration.csv"
    _write_csv(csv_path, _measurements())
    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "fit", CONFIG, str(csv_path)],
        capture_output=True, text=True, check=True).stdout

    assert "locked" in out, (
        "three rows varying only pressure and speed cannot identify the "
        "chemistry factors; fit must say so rather than fitting them")
    assert "next experiment" in out, (
        "fit should name the measurement that would unlock more")


def test_calibration_never_reaches_the_corpus(tmp_path):
    """Scoring must not see a user's tool factor, or validation is circular."""
    from cmp_sim.core.predictive_score import score_all

    before = [s.shape_mape for s in score_all() if s.shape_mape is not None]
    csv_path = tmp_path / "calibration.csv"
    _write_csv(csv_path, _measurements())
    subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "fit", CONFIG, str(csv_path)],
        capture_output=True, text=True, check=True)
    after = [s.shape_mape for s in score_all() if s.shape_mape is not None]

    assert before == after, (
        "running a calibration changed dataset scores — a user's tool factor "
        "has leaked into the validation corpus")


def test_limit_11_points_at_the_command_that_implements_it():
    root = Path(__file__).resolve().parent.parent
    limits = (root / "docs" / "limits.md").read_text(encoding="utf-8")
    section = limits.split("## 11.")[1]
    assert "cmp-sim fit" in section, (
        "limit 11 tells the reader a calibration wafer fixes this but does not "
        "name the command that does it")
