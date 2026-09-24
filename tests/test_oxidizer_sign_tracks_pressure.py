"""The oxidiser term's sign flips with PRESSURE, inside a single experiment.

jani2025_cu_rsm_composition_heldout was the corpus's worst undiagnosed dataset at
51.2% shape error, inside its pack's pH range and with no replicates to excuse it.
The diagnosis is specific and it is not a scale problem.

WHICH TERM IS DEAD. Correlating each swept axis against measurement and against
prediction over the 13 rows:

    axis        corr(measured)   corr(predicted)
    oxidiser        +0.76            +0.04
    abrasive        +0.34            +0.92
    chelator        -0.11            -0.05
    promoter        +0.66            +0.31

The oxidiser is the dataset's strongest driver and the model is blind to it. The
predicted rates span only 2.5x (4257-10596) against a measured 4.8x
(3470-16750), and the ratio measured/predicted runs 0.41 to 1.69 — a 4.1x spread,
so this is a shape failure, not a constant offset that a Kp refit could absorb.

WHY THE TERM IS DEAD. `cu_h2o2_bta` places `oxidizer_peak_wt_pct` at 3.0, so
across jani2025's 3-7 wt% range the response only ever falls: 1.000, 0.979,
0.933, 0.905, 0.815. The dataset rises strongly over the same range. The term is
not mis-scaled, it points the wrong way.

AND THE CORPUS CANNOT SIMPLY BE REFITTED, because its Cu oxidiser sweeps disagree
with each other:

    ihnfeldt2008   pH 10.0   0.0/0.1/2.0 wt%   150 -> 3500 -> 1660   peak ~0.1
    jani2025 acid  pH  3.0   3.0/4.0/6.0       22820 -> 25780        rising at 6
    us8501625b2    pH  3.6   3.0/9.0/15.0      two groups, BOTH SIGNS

The first hypothesis — that the sign tracks inhibitor presence, BTA-passivated
slurries falling and BTA-free ones rising — is FALSIFIED by us8501625b2, which
contains both signs at the same 0.08 mM BTA.

WHAT ACTUALLY SEPARATES THEM. Those two us8501625b2 groups are identical in every
slurry variable — same abrasive 0.17 wt%, citric acid 0.0078 M, BTA 0.08 mM,
oxalic acid 0, flow 200 ml/min, pH 3.6, same 93 rpm. They differ in ONE thing:

    2 psi:  3.0 -> 8200,  9.0 -> 7200,  15.0 -> 6300   monotone FALLING
    1 psi:  3.0 -> 1900,  9.0 -> 3900,  15.0 -> 3300   RISING, peak near 9

The oxidiser sign is a function of down force, within one experiment, one slurry
and one lab. That is mechanistically sensible — H2O2 builds a passivating film,
and whether more film helps or hurts depends on whether the mechanics can clear
it — but the model has no pressure-oxidiser coupling, and two pressures from one
patent are not enough to fit one.

So this is recorded as a diagnosis, not a fix. `oxidizer_peak_wt_pct` stays at
3.0 with its alumina/glycine citation (GT07, peak 2-3.6 wt%), and jani2025's
51.2% stays on the board as an honest miss with a named cause, in the same way
the velocity exponent was left unfitted when the corpus could not resolve it.

⚠ NOTE the pack's citation is for an ALUMINA slurry, while jani2025 is silica —
so abrasive type is a second candidate explanation that this corpus also cannot
separate from pressure, because the two vary together across these datasets.
"""
from __future__ import annotations

import statistics
from collections import defaultdict

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _recipe_for, score_dataset
from cmp_sim.core.validation import dataset_paths
from cmp_sim.models.chemical_rate import peaked_oxidizer_response

HELDOUT = "jani2025_cu_rsm_composition_heldout"
BOTH_SIGNS = "us8501625b2_cu_h2o2_pressure_series"


def _doc(stem):
    return yaml.safe_load(next(p for p in dataset_paths() if p.stem == stem)
                          .read_text(encoding="utf-8"))


def _correlation(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs)
           * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den if den else 0.0


def _measured_and_predicted(stem):
    doc = _doc(stem)
    rows = []
    for row in doc["conditions"]:
        rows.append((row["overrides"], _measured(row),
                     run_recipe(_recipe_for(doc, row))["removal_rate_A_per_min"]))
    return rows


def _isolated_oxidiser_groups(stem):
    """Groups of rows in which ONLY the oxidiser concentration differs."""
    doc = _doc(stem)
    groups = defaultdict(list)
    for row in doc["conditions"]:
        overrides = dict(row.get("overrides") or {})
        conc = overrides.pop("oxidizer_wt_pct", None)
        if conc is None:
            continue
        key = (tuple(sorted((k, str(v)) for k, v in overrides.items())),
               row.get("pressure_psi"), row.get("rpm_platen"))
        groups[key].append((conc, _measured(row)))
    return {key: sorted(v) for key, v in groups.items()
            if len({c for c, _ in v}) >= 3}


# ---------------------------------------------------------------------------
# the failure is in the oxidiser term, and it is a shape failure
# ---------------------------------------------------------------------------

def test_the_oxidiser_drives_the_data_and_the_model_is_blind_to_it():
    rows = _measured_and_predicted(HELDOUT)
    concs = [o["oxidizer_wt_pct"] for o, _, _ in rows]
    measured = [m for _, m, _ in rows]
    predicted = [p for _, _, p in rows]

    assert _correlation(concs, measured) > 0.6, "the data should rise with H2O2"
    assert abs(_correlation(concs, predicted)) < 0.25, (
        "the model's rate barely responds to the oxidiser here; if that has "
        "changed, this diagnosis needs revisiting")


def test_it_is_not_a_constant_scale_offset():
    rows = _measured_and_predicted(HELDOUT)
    ratios = [m / p for _, m, p in rows]
    assert max(ratios) / min(ratios) > 3.0, (
        f"ratio spread {max(ratios) / min(ratios):.1f}x — a tight spread would "
        "mean a Kp/normalisation problem instead of a shape failure")


def test_the_packs_peak_makes_the_response_fall_across_this_datasets_range():
    pack = load_pack("cu_h2o2_bta")

    def value(key):
        param = pack.param(key)
        return param.value if hasattr(param, "value") else param

    peak = value("oxidizer_peak_wt_pct")
    k = value("oxidizer_passivation_K")
    assert peak <= 3.0, peak

    response = [peaked_oxidizer_response(c, peak, k) for c in (3.0, 5.0, 7.0)]
    assert response == sorted(response, reverse=True), response
    assert response[-1] < response[0], (
        "the term falls from 3 to 7 wt% while jani2025 rises — it points the "
        "wrong way, rather than being mis-scaled")


# ---------------------------------------------------------------------------
# and the corpus cannot be refitted, because its sweeps disagree
# ---------------------------------------------------------------------------

def test_the_inhibitor_hypothesis_for_the_sign_is_falsified():
    """One dataset contains BOTH signs at the same BTA concentration."""
    groups = _isolated_oxidiser_groups(BOTH_SIGNS)
    assert len(groups) >= 2, groups

    inhibitor_levels = {dict(key[0])["inhibitor_mM"] for key in groups}
    assert len(inhibitor_levels) == 1, (
        f"the groups differ in BTA ({inhibitor_levels}), so they cannot refute "
        "the inhibitor hypothesis")

    trends = set()
    for rows in groups.values():
        trends.add("rises" if rows[-1][1] > rows[0][1] else "falls")
    assert trends == {"rises", "falls"}, trends


def test_the_sign_tracks_pressure_and_nothing_else():
    """The decisive observation: identical slurry, different down force."""
    groups = _isolated_oxidiser_groups(BOTH_SIGNS)

    slurries = {key[0] for key in groups}
    assert len(slurries) == 1, (
        "the two groups must be identical in every slurry variable for pressure "
        "to be the only explanation")

    by_pressure = {key[1]: rows for key, rows in groups.items()}
    assert set(by_pressure) == {1.0, 2.0}, sorted(by_pressure)

    rising = by_pressure[1.0]
    falling = by_pressure[2.0]
    assert rising[-1][1] > rising[0][1], rising
    assert falling[-1][1] < falling[0][1], falling
    # and the falling group is the higher-rate one, as the passivation picture
    # predicts: more mechanical clearing, so extra film only hinders
    assert falling[0][1] > rising[0][1] * 2, (falling[0], rising[0])


def test_the_conflict_is_left_unfitted_and_the_dataset_stays_an_honest_miss():
    """No pressure-oxidiser coupling is invented from two pressures."""
    score = score_dataset(next(p for p in dataset_paths() if p.stem == HELDOUT))
    assert score.shape_mape > 40.0, (
        "if this dataset has improved, a coupling was added — document what "
        "data justified it")
    assert score.error is None, "it must still be scored, not declined"
