"""The chelator and promoter axes: WIRED, and one of them DECLARED INERT.

Why these tests exist
---------------------
`tools/jani_residual_probe.py` set out to explain the corpus's single most
indefensible miss: jani2025's held-out RSM block at 51.2%, against the
authors' OWN published reproducibility of 1.5-9.5% (docs/limits.md §17).
Uniquely in this corpus, "the data are noisy" has been excluded by the source.

What it found was not a missing law. It was SILENCE. Two of the four axes that
dataset sweeps — `chelator_M` and `promoter_M` — moved the predicted rate by
exactly 0.00% when doubled, while the inherited layer had contained a sourced,
species-gated, unit-tested term for each all along. `cmp_sim`'s wrapper simply
never called them, so the engine accepted the inputs, stored them, and ignored
them. That is the failure this repo rates as worse than a missing feature: the
output still looks like a prediction about those axes.

Wiring them raised a SECOND question that the naive fix gets wrong, and these
tests pin both halves of the answer:

1. `chelator_suppression` transfers and is now live. Its reference is a real
   composition (0.1332 M glycine), so the normalisation is well posed.
2. `carboxylate_promoter` does NOT transfer at this pack's reference, and the
   evidence cuts both ways at once — which is why it must be a declaration
   rather than a quiet omission:
       SHAPE transfers.     Residual log-slope on promoter_M measured over
                            the held-out block is +0.58; the term fitted on a
                            DIFFERENT document (US6309560B1) has local slope
                            +0.675 there, and switching it on flattens the
                            residual to +0.01 and the shape error to 29.9%.
       MAGNITUDE does not.  The same switch drives absolute scale from 0.91x
                            to 0.075x — a 13x over-prediction — because the
                            pack's promoter reference is 0 M, so the factor
                            divides by the pure-mechanical floor phi and
                            multiplies everything by 1/phi = 12.8x. phi was
                            measured in a system whose only chemistry was the
                            complexant; this pack's reference already carries
                            H2O2 and glycine.
   Taking the shape gain would mean publishing a rate 13x wrong. Fitting a
   per-pack phi to keep it would add a free constant to a pack with one
   promoter level — interpolation, not physics. So the axis is declared inert
   and the unblocking measurement is named.

These tests fail if anyone deletes the gate to chase the shape number, if the
chelator term goes silent again, or if the degenerate-reference reasoning is
quietly generalised to a pack where the reference is a real composition.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cmp_sim.core.predictive_score import _predict, _recipe_for
from cmp_sim.api import run_recipe

DATASET = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
           / "validation" / "datasets"
           / "jani2025_cu_rsm_composition_heldout.yaml")


@pytest.fixture(scope="module")
def doc():
    return yaml.safe_load(DATASET.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def row(doc):
    # E9: glycine 0.26 M and oxalic 0.08 M, both well away from the pack
    # reference, so both terms have something to say here.
    return next(r for r in doc["conditions"] if r["label"].startswith("E9 "))


def _perturbed(row, axis, factor):
    out = dict(row)
    ov = dict(row["overrides"])
    ov[axis] = float(ov[axis]) * factor
    out["overrides"] = ov
    return out


def test_chelator_concentration_changes_the_predicted_rate(doc, row):
    """The bug in one line: this axis used to move the rate 0.00%.

    Asserted as a RESPONSE, not as a number, so the test survives a refit of
    `chelator_suppression_a` but still fails if the term stops being called.
    """
    base = _predict(doc, row)
    doubled = _predict(doc, _perturbed(row, "chelator_M", 2.0))
    assert base and doubled
    assert abs(doubled / base - 1.0) > 0.05, (
        "chelator_M is inert again: the engine accepts the input and ignores "
        "it, so the result looks like a prediction about glycine and is not")


def test_more_glycine_removes_LESS_copper(doc, row):
    """Direction, which is the counter-intuitive part and the citable claim.

    A chelator is expected to speed dissolution; Jani 2025's own conclusion is
    the opposite ("glycine effectively functions as an inhibitor rather than a
    dissolution promoter", regression coefficient -440.91, p=4.1e-7). If a
    future refactor flips the sign the model will contradict the paper the
    constant came from.
    """
    base = _predict(doc, row)
    more = _predict(doc, _perturbed(row, "chelator_M", 2.0))
    assert more < base


def test_the_chelator_term_is_exactly_one_at_the_pack_reference():
    """No double counting: Kp was back-calculated at the reference glycine.

    This is the rule that holds the whole factor stack together, so it is
    asserted on the term itself rather than inferred from a rate.
    """
    from cmp_sim.core.solver import resolve
    from cmp_sim.cli import recipe_from_dict
    from cmp_sim.models.chemical_rate import chemical_factor

    rr = resolve(recipe_from_dict({
        "model": "auto",
        "wafer": {"film": "cu"},
        "slurry": {"pack": "cu_h2o2_bta"},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 90, "rpm_head": 90,
                 "time_s": 60.0},
    }))
    eff = chemical_factor(rr)
    assert "chelator_suppression" in eff.terms, (
        "the chelator term is not being assembled at all")
    assert eff.terms["chelator_suppression"] == pytest.approx(1.0, abs=1e-9)


def test_the_promoter_axis_is_inert_BY_DECLARATION_not_by_oversight(doc, row):
    """Inert is acceptable; SILENTLY inert is not.

    The distinction is the whole point of this run: the same 0.00% response
    that was a bug for `chelator_M` is the correct behaviour for `promoter_M`
    at a zero reference — but only if the model says so. A reader must be able
    to tell "no coefficient here" from "this factor does not matter".
    """
    base = _predict(doc, row)
    doubled = _predict(doc, _perturbed(row, "promoter_M", 2.0))
    assert doubled == pytest.approx(base, rel=1e-9)

    result = run_recipe(_recipe_for(doc, row))
    text = " ".join(result.get("warnings") or [])
    assert "promoter" in text.lower(), (
        "the promoter axis is inert and NOTHING says so — that is the "
        "accept-store-ignore failure this test exists to prevent")
    for needle in ("0 M", "12.8", "0.075", "29.9"):
        assert needle in text, (
            f"the declaration must carry its evidence; {needle!r} is missing, "
            "so a future reader cannot check the ruling or overturn it")


def test_the_gate_names_the_measurement_that_would_unblock_it(doc, row):
    """A refusal without an exit condition becomes permanent by accident."""
    result = run_recipe(_recipe_for(doc, row))
    text = " ".join(result.get("warnings") or []).lower()
    assert "zero-oxalate" in text and "reference composition" in text


def test_the_gate_is_about_a_ZERO_reference_not_about_promoters(doc, row):
    """Scope check, so the ruling cannot spread to well-posed packs.

    The objection is arithmetic — dividing by g(0) = phi — not chemical. Give
    the same recipe a non-zero promoter reference and the term must come back,
    or the gate has quietly become "we do not model promoters".
    """
    recipe = _recipe_for(doc, row)
    params = dict(recipe.get("params") or {})
    params["promoter_ref_M"] = 0.02          # a real composition, not 0 M
    recipe["params"] = params
    result = run_recipe(recipe)
    assert "carboxylate_promoter" in (result.get("chemistry_terms") or {}), (
        "with a non-degenerate reference the sourced promoter term must be "
        "applied; the gate is about the zero denominator, not about the axis")


def test_wiring_these_terms_did_not_move_the_corpus_median():
    """Guard against the gain being paid for elsewhere.

    Two terms went live across every Cu pack at once. The corpus median is
    pinned at its long-standing value because nothing was fitted: if this
    fails, a term is firing on datasets whose reference composition it does
    not describe.
    """
    from cmp_sim.core.predictive_score import score_all

    shape = sorted(s.shape_mape for s in score_all()
                   if s.shape_mape is not None)
    # 18.9 since 2026-09-27 (DLC ladder entered the corpus, limits.md §31)
    assert shape[len(shape) // 2] == pytest.approx(18.9, abs=0.35)
