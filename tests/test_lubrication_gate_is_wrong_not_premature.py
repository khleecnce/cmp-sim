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

AND NO CALIBRATION WOULD HELP — this is the decisive part.

It is tempting to say lambda is merely uncalibrated (it divides a modelled film
thickness, itself a function of an assumed viscosity, by an assumed pad
roughness) and that a dataset reporting measured film thickness would unblock
the gate. The arithmetic says otherwise. In this model

    lambda = 0.001401 * (rpm / pressure)

to five digits on every row, i.e. lambda IS the pseudo-Sommerfeld number V/p of
the CMP lubrication literature (Wu & Liao, "Lubrication in Chemical and
Mechanical Planarization", Advances in Tribology, 2016, doi:10.5772/64484,
which also records the standard convention that the effective slurry film
thickness is taken as the pad's arithmetic average roughness) up to a single
multiplicative constant. Measuring viscosity and roughness would fix that
constant. A constant cannot reorder anything, so it cannot create a separation
that is not already there.

And the separation is not there:

    rows where rate FALLS with speed (1.5 psi)   lambda 0.056, 0.112, 0.187
    rows where rate RISES with speed (4.0 psi)   lambda 0.021, 0.042, 0.070

These OVERLAP. A threshold would have to be simultaneously below 0.056 and
above 0.070. Worse, mariscal2020 — nine rows that never invert, in any
combination — spans lambda 0.0135-0.0628, sitting inside the inverting range.

So the velocity inversion is not a Sommerfeld/Stribeck phenomenon in the data
available. Both datasets are boundary-lubricated by every published criterion,
and they still behave oppositely, which means the discriminating variable is
something else (down force enters the two datasets with opposite effect, which
points at pad contact rather than fluid film). Gating on lubrication would be
wrong, not merely premature.

These tests pin all three parts: the flag genuinely cannot fire, no calibration
could make it fire, and the lambda ORDERING evidence that remains real must not
be quietly discarded either.
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


# ---------------------------------------------------------------------------
# and no calibration could rescue the gate
# ---------------------------------------------------------------------------

def test_lambda_is_the_pseudo_sommerfeld_number_up_to_one_constant():
    """lambda = k * (rpm / pressure), so calibrating it only sets k."""
    ratios = [lam / (rpm / pressure) for pressure, rpm, _, _, lam in _rows(PRESTON)]
    spread = (max(ratios) - min(ratios)) / max(ratios)
    assert spread < 0.01, (
        f"lambda is no longer proportional to V/p (spread {spread:.3%}); the "
        "argument that calibration cannot help must be re-derived")


def test_no_threshold_can_separate_inverting_from_non_inverting_rows():
    """The falsification. A scale factor cannot reorder overlapping sets."""
    rows = _rows(PRESTON)
    falling = sorted(lam for pressure, _, _, _, lam in rows if pressure == 1.5)
    rising = sorted(lam for pressure, _, _, _, lam in rows if pressure == 4.0)

    assert max(rising) > min(falling), (
        "the two groups have separated; a lubrication gate may now be "
        "justified — re-run the diagnosis before trusting this test")

    # and the dataset that NEVER inverts sits inside the inverting range
    mariscal = [lam for *_, lam in _rows(MARISCAL)]
    assert min(mariscal) < max(falling) and max(mariscal) > min(falling), (
        "mariscal2020 no longer overlaps the inverting rows")
