"""The velocity exponent cannot be resolved by this corpus — so it is not fitted.

STATUS.md set the rule before any code: fit an exponent to every isolated
velocity group, report the spread, and if they scatter across 1.0 say the axis
cannot resolve it and STOP. Do not fit a global exponent to pooled points.

They scatter, and not randomly — they contradict each other in a structured
way. Every in-scope isolated group, exponent from log-log regression of rate
against platen speed at fixed pressure:

    us6918821b2   1.5 psi   -0.42     425 -> 419 -> 250     (rate FALLS)
    mariscal2020  4.0 psi   +0.62    2064 -> 3079 -> 3463
    mariscal2020  3.0 psi   +0.86    1404 -> 2529 -> 2838
    us6918821b2   4.0 psi   +0.86     594 -> 1384 -> 1636
    mariscal2020  2.0 psi   +1.10     698 -> 1558 -> 1718

Preston's law says every one of these should be +1.0.

The decisive observation is that the two datasets disagree about the SIGN of
the pressure dependence of the exponent:

    mariscal2020    exponent FALLS as pressure rises   1.10 -> 0.86 -> 0.62
    us6918821b2     exponent RISES as pressure rises  -0.42 -> 0.86

So "the velocity exponent is a function of pressure" cannot be written down
either — the two available datasets require opposite functions. A single fitted
constant would sit near 0.86 and would be wrong at both ends of both datasets,
while looking like an improvement in a pooled median.

The -0.42 group is not noise to be trimmed. US 6,918,821 B2 exists to make
precisely that measurement: a conventional IC1000 pad LOSES copper rate as
speed rises at low down force, which is the patent's argument for fixed-abrasive
pads. It is the strongest single piece of evidence in the corpus that the
Preston velocity term is incomplete, and it is the first point a global fit
would discard.

These tests pin the scatter so that a future "improvement" to the velocity term
has to explain the sign reversal rather than average over it.
"""
from __future__ import annotations

import math
from collections import defaultdict

import yaml

from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

PRESTON = "us6918821b2_cu_ic1000_pressure_speed_2x3"
MARISCAL = "mariscal2020_peteos_ceria_pressure_velocity_3x3"


def _doc(stem: str) -> dict:
    for path in dataset_paths():
        if path.stem == stem:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise AssertionError(f"dataset {stem} not found")


def _exponents_by_pressure(stem: str) -> dict[float, float]:
    """log-log slope of rate against platen rpm, at each fixed pressure."""
    groups: dict[float, list] = defaultdict(list)
    for row in _doc(stem)["conditions"]:
        if _measured(row) is not None and row.get("rpm_platen"):
            groups[row["pressure_psi"]].append(row)

    out = {}
    for pressure, rows in groups.items():
        if len({r["rpm_platen"] for r in rows}) < 3:
            continue
        xs = [math.log(r["rpm_platen"]) for r in rows]
        ys = [math.log(_measured(r)) for r in rows]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        out[pressure] = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                         / sum((x - mx) ** 2 for x in xs))
    return out


def test_the_low_pressure_group_has_a_NEGATIVE_velocity_exponent():
    """Rate falls as speed rises — Preston cannot express this at all."""
    exponents = _exponents_by_pressure(PRESTON)
    assert exponents[1.5] < -0.2, exponents
    assert exponents[4.0] > 0.5, exponents


def test_the_two_datasets_require_opposite_pressure_dependences():
    """This is the falsification: no single exponent(P) serves both."""
    preston = _exponents_by_pressure(PRESTON)
    mariscal = _exponents_by_pressure(MARISCAL)

    preston_slope = preston[4.0] - preston[1.5]
    mariscal_slope = mariscal[4.0] - mariscal[2.0]

    assert preston_slope > 0.5, preston      # exponent RISES with pressure
    assert mariscal_slope < -0.3, mariscal   # exponent FALLS with pressure
    assert preston_slope * mariscal_slope < 0, (
        "the datasets now agree on the sign; if one was re-read or corrected, "
        "revisit whether a velocity-exponent model is justified")


def test_mariscal_exponents_decrease_monotonically_with_pressure():
    exponents = _exponents_by_pressure(MARISCAL)
    ordered = [exponents[p] for p in sorted(exponents)]
    assert ordered == sorted(ordered, reverse=True), exponents


def test_the_isolated_exponents_straddle_prestons_value():
    """If they all clustered below 1.0 this would be a pack parameter."""
    values = list(_exponents_by_pressure(PRESTON).values()) + \
        list(_exponents_by_pressure(MARISCAL).values())
    assert min(values) < 1.0 < max(values) + 0.15, values
    assert max(values) - min(values) > 1.0, (
        f"spread {max(values) - min(values):.2f} is too tight to justify the "
        "'cannot resolve' conclusion; re-run the diagnosis")


def test_no_velocity_exponent_parameter_was_introduced():
    """Guard against the fix this investigation rejected."""
    from pathlib import Path

    import cmp_sim

    params = Path(cmp_sim.__file__).parent / "data" / "params"
    offenders = [p.name for p in params.glob("*.yaml")
                 if "velocity_exponent" in p.read_text(encoding="utf-8")]
    assert not offenders, (
        f"{offenders} declare a velocity exponent. The corpus cannot resolve "
        "one: two datasets require opposite pressure dependences. If new data "
        "settled it, delete this test and cite the dataset.")
