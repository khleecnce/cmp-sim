"""Locks the 2026-09-26 velocity-axis measurement.

Three laws were tested against the P/V residual and rejected (see the module
docstring of ``tools/velocity_thermal_probe.py`` for the derivations):

1. frictional-heating Arrhenius activation  -> needs a POSITIVE b_V
2. Stribeck / hydrodynamic lubrication      -> needs b_P = -b_V
3. any series resistance in the product P*V -> needs b_P = b_V

All three are contradicted by the same two numbers: b_P is ~0 and b_V is
~-0.55. These tests assert that measurement so that (a) nobody re-proposes a
rejected law without new data, (b) nobody adopts the tempting V**(2/3)
exponent while its supporting starvation law still fails its flow check, and
(c) if a future dataset OVERTURNS the measurement, the suite says so loudly
instead of leaving a stale conclusion in a docstring.

The bars are deliberately loose. They test the SIGN and the ORDER of the
effect, which is what the physics argument turns on, not a fitted digit.
"""
from __future__ import annotations

import pytest

from tools.velocity_thermal_probe import (
    STARVATION_BQ,
    flow_test,
    trends,
    verdict,
)


@pytest.fixture(scope="module")
def rows():
    measured = trends()
    if len(measured) < 3:
        pytest.skip("fewer than 3 velocity ladders in the corpus")
    return measured


def test_frictional_heating_activation_is_falsified(rows):
    """A thermal law needs the model to UNDER-predict at high speed."""
    median_slope, positive, total = verdict(rows)
    assert median_slope < 0.0, (
        f"median d(ln residual)/d(ln V) = {median_slope:+.3f} is no longer "
        "negative. Frictional-heating activation was rejected on the strength "
        "of a negative median; if new data have flipped it, re-run "
        "tools/velocity_thermal_probe.py and revisit the R_th question."
    )
    assert positive <= total / 2, (
        f"{positive}/{total} velocity ladders now have a positive residual "
        "slope; the rejection of thermal activation assumed a minority."
    )


def test_velocity_residual_is_not_symmetric_with_pressure(rows):
    """b_P ~ 0 while b_V < 0 — this is what kills lubrication and 1/(kPV)."""
    joint = [t for t in rows if t.joint_p is not None and t.joint_v is not None]
    if len(joint) < 3:
        pytest.skip("fewer than 3 datasets vary P and V independently")
    import statistics

    b_p = statistics.median(float(t.joint_p) for t in joint)
    b_v = statistics.median(float(t.joint_v) for t in joint)

    # Pressure linearity: Preston's best-supported axis needs no correction.
    assert abs(b_p) < 0.30, (
        f"median b_P = {b_p:+.3f}: the pressure residual is no longer flat, "
        "so the claim that Preston's P-linearity needs no correction has to "
        "be re-examined."
    )
    # Velocity sub-linearity: real, and larger than the pressure effect.
    assert b_v < -0.20, f"median b_V = {b_v:+.3f} is no longer clearly negative"
    assert abs(b_v) > 2.0 * abs(b_p), (
        f"b_V ({b_v:+.3f}) is no longer much larger in magnitude than b_P "
        f"({b_p:+.3f}). The P/V ASYMMETRY is the whole argument: a symmetric "
        "residual would be consistent with a P*V series-resistance law, which "
        "this repo rejected on exactly this evidence."
    )
    # Lubrication would need the two to cancel.
    assert abs(b_p + b_v) > 0.20, (
        f"b_P + b_V = {b_p + b_v:+.3f} is now near zero, which is the "
        "signature of a Sommerfeld-number (eta*V/P) lubrication law. That law "
        "was rejected because the sum was -0.585; re-open it."
    )


def test_starvation_law_flow_leg_still_fails():
    """The 2/3 exponent stays withheld while b_Q has the wrong sign.

    MRR ~ P * V**(2/3) * Q**(1/3) is a zero-constant derivation, so it is
    allowed in only if ALL THREE of its coefficient predictions hold. The flow
    leg is the one the velocity data cannot fake.
    """
    fit = flow_test()
    if fit is None:
        pytest.skip("no corpus dataset both records and varies flow_ml_min")
    assert fit["b_q"] < STARVATION_BQ / 2.0, (
        f"measured b_Q = {fit['b_q']:+.3f} has moved toward the derived "
        f"{STARVATION_BQ:+.3f}. The starvation law may now be admissible, "
        "which would license the V**(2/3) exponent (worth ~2 points of corpus "
        "median). Re-run tools/velocity_thermal_probe.py and decide."
    )


def test_no_pack_declares_a_thermal_resistance_constant():
    """Guard: the rejected law must not reappear as a pack field."""
    import pathlib

    import yaml

    forbidden = ("thermal_resistance", "r_th", "friction_heating",
                 "velocity_exponent")
    root = pathlib.Path(__file__).resolve().parents[1]
    offenders = []
    for path in sorted((root / "cmp_sim" / "data" / "params").glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        # parse to be sure it is a real key, not prose in a note
        doc = yaml.safe_load(text) or {}

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if str(key).lower() in forbidden:
                        offenders.append(f"{path.name}:{key}")
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(doc)
    assert not offenders, (
        "these packs declare a constant for a law this repo measured and "
        f"rejected on 2026-09-26: {offenders}. Frictional-heating activation "
        "(median b_V is NEGATIVE, not positive) and a free velocity exponent "
        "(no surviving derivation) are both out. See "
        "tools/velocity_thermal_probe.py."
    )
