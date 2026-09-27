"""The alpha-chi veto is a SCOPE statement, and the corpus says so.

`models/luo_dornfeld.resolve_regime` measures a contact branch for most corpus
runs and then refuses it when `alpha*chi > 1` breaks the structural bound
`0 <= 1 - alpha*chi <= 1`, substituting the inherited elastic pair. Until the
30th run that refusal was reported as "the elastic/plastic branch was not
determined from data" -- false in 33 of 49 runs, where alpha WAS determined
and then declared out of scope.

The substitution is not neutral: it asserts

    n_C = p * (1 - alpha*chi) = 1 * (1 - 2/3) = +1/3

on every vetoed run, against the -0.5 the plastic branch would give if the
bound were simply lifted. `tools/plastic_branch_exponent_probe.py` fitted the
measurements -- every iso-condition abrasive-loading series on a vetoed branch
-- and they land on the substituted value, not on the literal plastic one.

These tests pin BOTH halves, because a scope claim with no exit condition
becomes permanent by accident:
  * the refusal is reported as scope, not as ignorance, and it says what would
    reopen it;
  * the measurement that justifies it is re-derived from the dataset files
    here, so the claim fails the moment the corpus contradicts it.

No constant and no exponent changed in the 30th run, so the corpus median must
be UNMOVED. That invariance is asserted too -- if it moved, honesty work
touched the physics and that is a bug.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from cmp_sim.api import run_recipe
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

# What the substitution asserts (elastic Hertz alpha = 2/3, chi = 1, p = 1),
# and what the literal plastic branch would assert if the bound were lifted.
ELASTIC_FALLBACK_N_C = 1.0 / 3.0
PLASTIC_LITERAL_N_C = -0.5


def _vetoed_runs():
    """(dataset stem, result) for every dataset whose branch is refused."""
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conds = doc.get("conditions") or []
        if not conds:
            continue
        try:
            result = run_recipe(_recipe_for(doc, conds[0]))
        except Exception:
            continue
        regime = result.get("abrasive_regime") or {}
        if regime.get("branch_outside_scope"):
            out.append((path.stem, result, regime))
    return out


@pytest.fixture(scope="module")
def vetoed():
    runs = _vetoed_runs()
    assert runs, (
        "no corpus run reports branch_outside_scope. Either the veto no "
        "longer fires -- in which case this whole limit is obsolete and "
        "should be retired deliberately, not left passing vacuously -- or "
        "the flag is not being published.")
    return runs


def test_the_veto_is_reported_as_scope_not_as_an_undetermined_axis(vetoed):
    """The old wording claimed alpha was unknown. It was measured."""
    for name, result, _regime in vetoed:
        blob = " ".join(result.get("warnings") or [])
        assert "OUTSIDE this decomposition's validity" in blob, (
            f"{name}: the run does not say the branch is out of SCOPE")
        assert "was not determined from data" not in blob, (
            f"{name}: the run still claims an axis is undetermined while the "
            "contact branch was in fact measured and then refused")


def test_the_scope_claim_names_what_would_reopen_it(vetoed):
    """A refusal with no exit condition becomes permanent by accident."""
    for name, result, _regime in vetoed:
        blob = " ".join(result.get("notes") or []) + " " + " ".join(
            result.get("warnings") or [])
        assert "plastic_branch_exponent_probe" in blob, (
            f"{name}: the refusal does not point at the measurement "
            "that justifies it")
        assert "at or below zero" in blob, (
            f"{name}: the refusal does not state the observation that "
            "would reopen the axis")
        assert "ONE dataset" in blob, (
            f"{name}: the refusal quotes four ladders without saying they all "
            "come from a single dataset. Four ladders from one patent is not "
            "corpus-wide evidence, and a claim that hides that reads as "
            "stronger than it is.")
        assert "TRANSITION branch" in blob, (
            f"{name}: the refusal quotes evidence without stating that the "
            "evidence covers only the transition branch. The plastic runs "
            "inherit the verdict, they do not measure it, and a claim that "
            "hides its own scope is how a caveat gets lost.")


def test_the_single_dataset_caveat_is_a_fact(vetoed):
    """If a second dataset ever supplies a vetoed ladder, rewrite the claim."""
    from plastic_branch_exponent_probe import dataset_branches, loading_groups

    branches = dataset_branches()
    sources = sorted({g["dataset"] for g in loading_groups()
                      if branches.get(g["dataset"]) in ("plastic",
                                                        "transition")})
    assert sources, "no vetoed-branch ladder exists at all"
    assert len(sources) == 1, (
        f"the vetoed-branch evidence now spans {sources}, so the 'ONE "
        "dataset' caveat in models/luo_dornfeld.py understates it. Widen the "
        "claim deliberately rather than leaving it stale.")


def test_the_evidence_really_is_transition_only(vetoed):
    """The scope caveat must be a fact, not boilerplate.

    If a plastic-branch dataset ever yields an iso-condition loading ladder,
    the caveat becomes false and must be rewritten -- so this fails then.
    """
    from plastic_branch_exponent_probe import dataset_branches, loading_groups

    branches = dataset_branches()
    plastic_ladders = [g["dataset"] for g in loading_groups()
                       if branches.get(g["dataset"]) == "plastic"]
    assert not plastic_ladders, (
        f"{sorted(set(plastic_ladders))} now provide a plastic-branch loading "
        "ladder, so the 'transition branch only' caveat in "
        "models/luo_dornfeld.py is out of date: score them and state the "
        "plastic result directly instead of inheriting it.")


def test_the_substituted_exponent_is_the_one_the_measurements_support():
    """Re-derive the justification from the dataset files, not from a memo.

    Every iso-condition abrasive-loading series that sits on a vetoed branch
    is fitted here. If a future dataset lands a zero or negative slope on such
    a branch, this fails and the veto's justification must be re-argued.
    """
    from plastic_branch_exponent_probe import (dataset_branches,
                                               loading_groups, slope_with_se)

    branches = dataset_branches()
    slopes = []
    for g in loading_groups():
        if branches.get(g["dataset"]) not in ("plastic", "transition"):
            continue
        m, se, _r2 = slope_with_se(g["points"])
        slopes.append((g["dataset"], m, se))

    assert slopes, (
        "no loading sweep sits on a vetoed branch, so the scope claim has no "
        "evidence in this corpus and must be downgraded to an assumption")

    negative = [(n, m) for n, m, _ in slopes if m <= 0.0]
    assert not negative, (
        f"{negative} have a non-positive concentration slope on a vetoed "
        "branch. That is the observation the literal plastic exponent "
        "(-0.5) predicts and the elastic substitution (+1/3) forbids, so the "
        "veto can no longer be called a scope statement backed by the data.")

    closer_to_elastic = [
        n for n, m, _ in slopes
        if abs(m - ELASTIC_FALLBACK_N_C) <= abs(m - PLASTIC_LITERAL_N_C)]
    assert len(closer_to_elastic) == len(slopes), (
        "not every vetoed-branch slope is closer to the substituted +1/3 "
        f"than to the literal -0.5: {slopes}")

    ms = sorted(m for _, m, _ in slopes)
    median = ms[len(ms) // 2]
    assert abs(median - ELASTIC_FALLBACK_N_C) < abs(
        median - PLASTIC_LITERAL_N_C), (
        f"median vetoed-branch slope {median:+.3f}")


def test_the_two_unverified_populations_are_distinguishable(vetoed):
    """`unverified` covers two different states; they must not read alike.

    One is "alpha could not be decided" (a genuine data gap). The other is
    "alpha was decided and is out of scope". They produced the SAME string
    before the 30th run, which is why the false warning survived 33 runs.
    """
    for name, _result, regime in vetoed:
        assert regime.get("confidence") == "unverified", name
        assert regime["branch_outside_scope"] is True, name

    # And the other population must still exist and still say the honest
    # thing, or this change simply relabelled every run.
    undetermined = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conds = doc.get("conditions") or []
        if not conds:
            continue
        try:
            result = run_recipe(_recipe_for(doc, conds[0]))
        except Exception:
            continue
        regime = result.get("abrasive_regime") or {}
        if (regime.get("confidence") == "unverified"
                and not regime.get("branch_outside_scope")):
            undetermined.append(path.stem)
    assert undetermined, (
        "every unverified run is now labelled out-of-scope; the genuine "
        "'alpha was never decided' population has vanished, which means the "
        "flag is being set too widely")


def test_the_exponents_did_not_change(vetoed):
    """An honesty fix that moves a number is not an honesty fix."""
    for name, _result, regime in vetoed:
        # as_dict() rounds to 4 d.p., so compare at that resolution.
        assert math.isclose(regime["alpha"], 2.0 / 3.0, abs_tol=1e-3), (
            f"{name}: alpha {regime['alpha']} is no longer the substituted "
            "elastic value, so this run changed the physics")
        assert math.isclose(regime["n_conc"], ELASTIC_FALLBACK_N_C,
                            abs_tol=1e-3), (
            f"{name}: n_C {regime['n_conc']} is not the +1/3 the scope claim "
            "is argued from")
