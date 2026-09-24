"""Can the lubrication regime be GATED? Not yet — and this records why.

STATUS asked: the velocity axis fails because of a regime the Preston form has
no channel for (US 6,918,821 B2 loses copper rate as speed rises at 1.5 psi).
`core/regime.py` already classifies lubrication, so does an existing flag fire
on those rows, and if not, is there a published criterion that separates them
from the 4 psi rows? If the criterion needs numbers the corpus lacks, name the
missing quantity in BLOCKED rather than inventing a threshold.

THE ANSWER IS NO, AND THE REASON IS QUANTITATIVE.

`classify_lubrication` splits on lambda = film thickness / pad roughness at
LAMBDA_BOUNDARY = 1.0 and LAMBDA_FULL_FILM = 3.0. Every row in both velocity
datasets sits between lambda = 0.0135 and 0.187 — one to two orders of magnitude
BELOW the first threshold. All fifteen classify as "boundary", including the
three rows whose rate falls with speed. The flag is not mis-tuned; a Stribeck
criterion genuinely places all of these in boundary contact, which is where CMP
is supposed to operate. Moving the threshold down to catch the 1.5 psi rows
would relabel most of the corpus as mixed-film and is exactly the invented
threshold the instruction forbids.

WHAT THE CORPUS DOES SHOW. The ORDERING of lambda carries real signal. Ranking
each dataset's rows by lambda against how badly the model over-predicts them:

    us6918821b2    Spearman rho = -0.714   (n=6,  lambda 0.021-0.187)
    mariscal2020   Spearman rho = -0.517   (n=9,  lambda 0.014-0.063)

Both negative, independently, in different films and different labs: the
thicker the modelled slurry film relative to pad roughness, the more the model
over-predicts. That is the lubrication effect showing up exactly where physics
says it should. But a monotone trend is not a threshold, and two datasets
cannot calibrate one.

WHAT IS MISSING, NAMED. lambda here is computed, not measured: it divides a
modelled film thickness (itself a function of assumed slurry viscosity and
sliding speed) by an assumed pad roughness. Neither patent reports slurry
viscosity, pad roughness, nor a measured film thickness, so the absolute
lambda scale is uncalibrated and only its ordering is trustworthy. To gate this
regime honestly the corpus needs one dataset that reports measured film
thickness (or viscosity AND pad roughness) alongside a rate-versus-speed sweep.
That requirement is written into STATUS.md BLOCKED.

These tests pin both halves of the finding: the flag genuinely cannot fire, and
the ordering evidence is real enough that it must not be quietly discarded.
"""
from __future__ import annotations

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.regime import (LAMBDA_BOUNDARY, LAMBDA_FULL_FILM,
                                 classify_lubrication)
from cmp_sim.core.predictive_score import _measured, _recipe_for
from cmp_sim.core.validation import dataset_paths

PRESTON = "us6918821b2_cu_ic1000_pressure_speed_2x3"
MARISCAL = "mariscal2020_peteos_ceria_pressure_velocity_3x3"


def _rows(stem: str):
    """(pressure, rpm, measured, predicted, lambda) for every row."""
    path = next(p for p in dataset_paths() if p.stem == stem)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = []
    for row in doc["conditions"]:
        if _measured(row) is None:
            continue
        result = run_recipe(_recipe_for(doc, row))
        out.append((row["pressure_psi"], row["rpm_platen"], _measured(row),
                    result["removal_rate_A_per_min"],
                    result["situation"]["metrics"]["lambda_ratio"]))
    return out


def _spearman(xs, ys) -> float:
    def rank(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0] * len(values)
        for position, index in enumerate(order):
            ranks[index] = position
        return ranks

    rx, ry = rank(xs), rank(ys)
    n = len(rx)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1))


# ---------------------------------------------------------------------------
# the flag cannot fire
# ---------------------------------------------------------------------------

def test_every_velocity_row_is_far_below_the_boundary_threshold():
    lambdas = [lam for stem in (PRESTON, MARISCAL) for *_, lam in _rows(stem)]
    assert max(lambdas) < 0.25, max(lambdas)
    assert max(lambdas) < LAMBDA_BOUNDARY / 4, (
        "a velocity row has approached the boundary/mixed threshold; the "
        "lubrication gate may now be justified — re-run the diagnosis")


def test_the_falling_rate_rows_classify_as_boundary_like_all_the_others():
    """The rows that break Preston are NOT distinguishable by the flag."""
    falling = [r for r in _rows(PRESTON) if r[0] == 1.5]
    rising = [r for r in _rows(PRESTON) if r[0] == 4.0]

    # the measurement: rate falls with speed at 1.5 psi, rises at 4.0 psi
    assert falling[-1][2] < falling[0][2], falling
    assert rising[-1][2] > rising[0][2], rising

    # yet every row gets the same lubrication label
    labels = {classify_lubrication(lam) for *_, lam in falling + rising}
    assert labels == {"boundary"}, labels


def test_the_thresholds_were_not_moved_to_manufacture_a_gate():
    assert LAMBDA_BOUNDARY == 1.0
    assert LAMBDA_FULL_FILM == 3.0


# ---------------------------------------------------------------------------
# but the ordering is real
# ---------------------------------------------------------------------------

def test_higher_lambda_means_more_over_prediction_in_both_datasets():
    """Independent confirmation in two films, two labs, two abrasives."""
    for stem, weakest in ((PRESTON, -0.5), (MARISCAL, -0.3)):
        rows = _rows(stem)
        rho = _spearman([lam for *_, lam in rows],
                        [m / p for _, _, m, p, _ in rows])
        assert rho < weakest, f"{stem}: rho={rho:.3f}"


def test_the_lambda_signal_spans_the_regime_where_preston_inverts():
    """The largest lambda in the corpus is the row with the worst miss."""
    rows = _rows(PRESTON)
    worst = min(rows, key=lambda r: r[2] / r[3])
    assert worst[4] == max(lam for *_, lam in rows), (
        "the worst-predicted row is no longer the highest-lambda row")
    assert worst[0] == 1.5 and worst[1] == 200, worst
