"""Locks the Sorooshian 2005 decision on the velocity axis.

WHAT WAS DECIDED
----------------
The 8th run found a large velocity residual (b_V = -0.549, b_P = -0.036) and
one surviving zero-constant candidate, reactant starvation:

    MRR ~ P * V**(2/3) * Q**(1/3)

Sorooshian 2005 (Univ. of Arizona PhD, Philipossian group) is a full factorial
in exactly those three variables -- flow 40/120 cc/min, velocity 0.32/0.64/0.96
m/s, pressure 2/4/6 psi, on thermal oxide -- so it can decide all three legs at
once. Measured (``tools/sorooshian_flow_probe.py``):

    b_P = +1.165   over 30 ladders   Preston requires +1.000   PASSES the audit
    b_V = +0.655   over 29 ladders   starvation predicts +0.667
    b_Q = -0.010   over 47 MATCHED pairs   starvation predicts +0.333

Two legs land almost exactly on the derivation and the third is flatly absent:
tripling the flow moves the rate by -1.1 % where the law needs +44.2 %.

THE RULE THIS ENCODES
---------------------
b_V and b_Q come from the SAME mass balance -- Q/V is one quantity, not two.
A derivation cannot be adopted one half at a time. Keeping V**(2/3) because it
matches while discarding Q**(1/3) because it does not would convert a derived
law into a fitted exponent that merely happens to be written as a fraction.
So the exponent stays OUT of the model even though it is now corroborated by
four independent sources (Sorooshian +0.655 here; Tseng & Wang 1997 derive and
report +0.5 for thermal oxide; Park/Lee/Jeong 2005 fit +0.74 for copper; the
corpus residual implies ~+0.45). What is missing is not evidence that the
velocity response is sub-linear -- that is now well established -- but a
mechanism that predicts sub-linearity WITHOUT predicting a flow dependence
that measurement says is not there.

These tests exist so that (a) the corroborated-but-underived exponent cannot
drift into a pack as a fitted constant, and (b) if the digitised data are ever
corrected in a way that changes the verdict, the suite says so loudly instead
of leaving a stale conclusion in a docstring.
"""
from __future__ import annotations

import math

import pytest

from tools.sorooshian_flow_probe import (
    PREDICTED_BQ,
    flow_exponent,
    load,
    pressure_exponent,
    velocity_exponent,
)


@pytest.fixture(scope="module")
def rows():
    data = load()
    assert len(data) > 100, "digitised Sorooshian table looks truncated"
    return data


def test_dataset_passes_the_preston_audit(rows):
    """Only a P-linear dataset may arbitrate the subtler velocity axis.

    This is the check ``yang2023_quartz_ceria_L25`` failed (its own b_P is
    -1.276), which is why that dataset was refused as an arbiter. Sorooshian
    has to pass the same bar before its flow verdict counts for anything.
    """
    b_p, n, _ = pressure_exponent(rows)
    assert n >= 10, f"only {n} pressure ladders; too few to audit"
    assert 0.65 < b_p < 1.35, (
        f"b_P = {b_p:+.3f} is no longer close to Preston's +1. This dataset's "
        "authority to decide the flow question rested on reproducing "
        "P-linearity; if that has changed, the verdict below is void."
    )


def test_velocity_response_is_sublinear(rows):
    """The measured exponent is well below Preston's 1 — the effect is real."""
    b_v, n, _ = velocity_exponent(rows)
    assert n >= 10, f"only {n} velocity ladders"
    assert b_v < 0.85, (
        f"b_V = {b_v:+.3f} is no longer clearly sub-linear. The whole velocity "
        "investigation rests on the rate growing more slowly than V."
    )
    assert b_v > 0.35, (
        f"b_V = {b_v:+.3f}: the response has collapsed further than any "
        "published report (the literature range is ~0.45 to ~0.74). Re-check "
        "the digitisation before trusting this."
    )


def test_starvation_flow_leg_is_falsified(rows):
    """b_Q is ZERO, not +1/3 — tripling the flow does nothing.

    This is the measurement that forbids adopting MRR ~ P*V^(2/3)*Q^(1/3).
    """
    b_q, n, per = flow_exponent(rows)
    assert n >= 30, f"only {n} matched flow pairs; expected ~47"

    # The effect is absent, not merely smaller than predicted.
    assert abs(b_q) < 0.12, (
        f"b_Q = {b_q:+.3f} is no longer ~0. If flow has acquired a real "
        "effect, the starvation law must be re-examined."
    )
    assert b_q < PREDICTED_BQ / 2.0, (
        f"b_Q = {b_q:+.3f} has moved toward the derived {PREDICTED_BQ:+.3f}; "
        "re-open MRR ~ P*V^(2/3)*Q^(1/3)."
    )
    # A coin-flip sign is the signature of no effect at all.
    positive = sum(1 for e in per if e > 0)
    assert 0.25 < positive / len(per) < 0.75, (
        f"{positive}/{len(per)} matched pairs are positive; that is no longer "
        "a coin flip, so flow may carry a real signal."
    )
    # Size of the miss, stated as the physical quantity.
    observed = math.exp(b_q * math.log(3.0)) - 1.0
    required = 3.0 ** PREDICTED_BQ - 1.0
    assert abs(observed) < required / 4.0, (
        f"a 3x flow change moves MRR by {observed * 100:+.1f}%, which is no "
        f"longer negligible against the {required * 100:+.1f}% the law needs."
    )


def test_no_pack_has_adopted_the_uncorroborated_velocity_exponent():
    """The exponent matches, but its derivation failed — it stays out.

    Guards the rule in this module's docstring: half a falsified derivation is
    a fitted constant, not a law.
    """
    import pathlib

    import yaml

    forbidden = ("velocity_exponent", "v_exponent", "flow_exponent",
                 "starvation_exponent", "slurry_flow_exponent")
    root = pathlib.Path(__file__).resolve().parents[1]
    offenders = []
    for path in sorted((root / "cmp_sim" / "data" / "params").glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

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
        f"{offenders} declare a velocity or flow exponent. Sorooshian 2005 "
        "measures b_V = +0.655 (matching the 2/3 derivation) but b_Q = -0.010 "
        "(refuting the SAME derivation's flow leg). Adopting the velocity half "
        "alone would be a fitted constant wearing a fraction's clothing. If a "
        "NEW mechanism is found that predicts sub-linear V with NO flow "
        "dependence, derive it, cite it, and then change this test."
    )
