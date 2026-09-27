"""The LOAD-SHARING axis (chi) is closed on IDENTIFIABILITY, not on a fit.

STATUS.md named chi "the only remaining undecided axis" of the Luo-Dornfeld
decomposition after the supply axis was closed, because every scored run
reports `abrasive_regime.confidence == 'unverified'`. The 29th run measured it
with `tools/chi_reachability_probe.py` and the verdict is that chi is not an
axis at all on this corpus:

  * `m` (the pressure exponent of real contact area, chi's ONLY input) is
    1.0000 on all 49 runnable datasets, spread 1.3e-10. That is the analytic
    signature of the exponential GW summit-height distribution, not an
    observation: A_r is linear in load for that distribution at any pad,
    pressure or film. Grading chi "decided from data" would dress a structural
    constant as a measurement — the same trap as lambda = V/p and
    summit_saturation = P (BLOCKED #1).
  * Forcing chi to 0.5 and to 0.0 and re-running the shipping solver moves the
    rate on 5 of 49 datasets; 44 are inert, because each pack's own MEASURED
    concentration/size exponent overrides the derived one inside
    `mechanical_factor`.

The probe then found the thing that is NOT closed, and it is not chi: on 33 of
49 runs the pad-limited contact criterion decides alpha (plastic or
transition) and `resolve_regime` DISCARDS that measured verdict because
alpha*chi > 1 breaks the structural bound. The remaining 16 never decide alpha
at all. So `unverified` is a report about ALPHA in every single run, and the
"chi is the last open axis" reading in STATUS.md was wrong.

These tests pin the measurement and the refusal, not the code shape.
"""
from __future__ import annotations

import numpy as np
import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths
from cmp_sim.models import luo_dornfeld as ld

#: chi's sole input is m in A_r ~ P^m. For the exponential summit-height
#: distribution GW uses here, m = 1 exactly, independent of every input.
EXPECTED_AREA_EXPONENT = 1.0


def _first_rows():
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conditions = doc.get("conditions") or []
        if not conditions:
            continue
        try:
            result = run_recipe(_recipe_for(doc, conditions[0]))
        except Exception:
            continue
        out.append((path.stem, result))
    return out


def test_the_area_pressure_exponent_is_analytically_pinned_not_measured():
    """m = 1 for every pad, pressure and film -- so chi carries no data.

    This is the identifiability claim. If a future pad model used a non-
    exponential summit distribution, m would vary and chi would become a real
    axis; this test would then fail and the closure would have to be revisited,
    which is the intended exit condition.
    """
    from cmp_sim.core.solver import resolve as resolve_recipe
    from cmp_sim.api import recipe_from_dict
    from cmp_sim.pad.material import pad_state

    exponents = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conditions = doc.get("conditions") or []
        if not conditions:
            continue
        try:
            rr = resolve_recipe(recipe_from_dict(_recipe_for(doc, conditions[0])))
            state, _n, _w = pad_state(rr.recipe.pad, rr)
            p_lo, p_hi = 0.5 * rr.pressure_pa, 2.0 * rr.pressure_pa
            a_lo = state.real_area_fraction(p_lo)
            a_hi = state.real_area_fraction(p_hi)
            exponents.append(float(np.log(a_hi / a_lo) / np.log(p_hi / p_lo)))
        except Exception:
            continue

    assert len(exponents) >= 40, (
        f"only {len(exponents)} datasets produced an area-pressure exponent; "
        "the claim is about the corpus and cannot rest on a handful")
    spread = max(exponents) - min(exponents)
    assert spread < 1e-6, (
        f"the area-pressure exponent now VARIES across the corpus "
        f"(spread {spread:.2e}, range {min(exponents):.4f}..{max(exponents):.4f}). "
        "chi is then a real axis carrying information from the pad model, and "
        "the identifiability closure in docs/limits.md section 25 must be "
        "reopened rather than assumed.")
    assert abs(exponents[0] - EXPECTED_AREA_EXPONENT) < 1e-6, (
        f"the exponent settled on {exponents[0]:.6f}, not the {EXPECTED_AREA_EXPONENT} "
        "the exponential GW summit distribution requires analytically")


def test_the_unverified_grade_is_about_alpha_in_every_run():
    """Corrects STATUS.md: chi is not what floors the confidence.

    Two disjoint populations produce the same `unverified` string, and NEITHER
    is chi: runs whose alpha is undetermined, and runs whose MEASURED alpha is
    discarded because alpha*chi breaks the structural bound.
    """
    rows = _first_rows()
    assert len(rows) >= 40, f"only {len(rows)} datasets ran"

    undetermined, vetoed, other = [], [], []
    for name, result in rows:
        regime = result.get("abrasive_regime") or {}
        if regime.get("confidence") != "unverified":
            continue
        notes = " | ".join(regime.get("notes") or [])
        if "breaks the structural bound" in notes:
            vetoed.append(name)
        elif "alpha undetermined" in notes:
            undetermined.append(name)
        else:
            other.append(name)

    assert not other, (
        f"{len(other)} runs are graded 'unverified' for a reason that is "
        f"neither an undetermined alpha nor the alpha-chi veto: {other[:5]}. "
        "A third cause would mean this limit's accounting is incomplete.")
    assert vetoed, (
        "no run hits the alpha-chi structural veto any more. If the conflict "
        "has been resolved, docs/limits.md section 25 must say how; if the "
        "criterion simply stopped deciding alpha, that is a regression.")
    assert len(vetoed) > len(undetermined), (
        f"the veto population ({len(vetoed)}) is no longer the majority cause "
        f"of the unverified grade ({len(undetermined)} undetermined). The "
        "limit's claim that a MEASURED alpha is being discarded corpus-wide "
        "rests on that majority.")


def test_resolving_the_alpha_chi_conflict_the_other_way_buys_nothing():
    """The obvious alternative is measured and REJECTED on its own evidence.

    When alpha*chi > 1 the code keeps chi (structural, information-free) and
    discards alpha (measured). The symmetric choice -- clamp chi to 1/alpha and
    keep the measured alpha -- looks strictly better on provenance. It is
    refused because chi's value is not adjustable evidence: with m pinned at 1,
    chi = 1 is what the contact model says, and clamping it to 2/3 to rescue
    alpha would be fitting the one quantity that carries no data. This test
    pins the measurement that makes the refusal cost nothing, so a future
    session does not adopt it expecting a gain.
    """
    import dataclasses

    base = ld.resolve_regime

    def alt(**kwargs):
        reg = base(**kwargs)
        branch = str(kwargs.get("contact_branch") or "").lower()
        if branch not in ("plastic", "transition"):
            return reg
        alpha = (ld.ALPHA_PLASTIC if branch == "plastic"
                 else 0.5 * (ld.ALPHA_ELASTIC + ld.ALPHA_PLASTIC))
        if alpha * reg.chi <= 1.0 + 1e-9:
            return reg
        beta = ld.beta_for_alpha(alpha) if alpha in ld.BETA_FOR_ALPHA else reg.beta
        chi = 1.0 / alpha
        return dataclasses.replace(
            reg, chi=chi, alpha=alpha, beta=beta,
            n_conc=reg.p * (1.0 - alpha * chi),
            n_size=-reg.q * (1.0 - alpha * chi) + beta)

    def medians():
        from cmp_sim.core import predictive_score as ps
        errs = sorted(r.shape_mape for r in ps.score_all()
                      if r.shape_mape is not None and not r.gated)
        return errs[len(errs) // 2]

    before = medians()
    ld.resolve_regime = alt
    try:
        after = medians()
    finally:
        ld.resolve_regime = base

    assert abs(after - before) < 0.05, (
        f"clamping chi instead of alpha now moves the median {before:.2f}% -> "
        f"{after:.2f}%. The refusal in docs/limits.md section 25 was priced at "
        "zero; if it has a price the decision must be re-argued, not inherited.")


def test_chi_barely_reaches_the_rate_because_measured_exponents_override_it():
    """Why no chi work can move the corpus: the derived exponents are shadowed.

    `mechanical_factor` prefers a pack's own measured concentration/size
    exponent over the derived one, so on most datasets chi could take any value
    in [0,1] and the prediction would not change. That is the real ceiling on
    this axis, and it is a DATA fact about the packs, not a code defect.
    """
    import dataclasses

    base = ld.resolve_regime

    def forced(**kwargs):
        reg = base(**kwargs)
        chi = 0.0
        return dataclasses.replace(
            reg, chi=chi,
            n_conc=reg.p * (1.0 - reg.alpha * chi),
            n_size=-reg.q * (1.0 - reg.alpha * chi) + reg.beta)

    moved = 0
    total = 0
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conditions = doc.get("conditions") or []
        if not conditions:
            continue
        recipe = _recipe_for(doc, conditions[0])
        try:
            rate = run_recipe(recipe).get("removal_rate_A_per_min")
        except Exception:
            continue
        ld.resolve_regime = forced
        try:
            other = run_recipe(recipe).get("removal_rate_A_per_min")
        except Exception:
            other = None
        finally:
            ld.resolve_regime = base
        if not rate or not other:
            continue
        total += 1
        if abs(other / rate - 1.0) * 100.0 >= 0.5:
            moved += 1

    assert total >= 40, f"only {total} datasets compared"
    assert moved <= total // 4, (
        f"a full chi swing (1.0 -> 0.0) now moves {moved} of {total} datasets. "
        "chi has become reachable, so the identifiability closure in "
        "docs/limits.md section 25 no longer holds and the axis is worth "
        "re-opening.")
    assert moved >= 1, (
        "a full chi swing moves NOTHING at all. Either the perturbation is not "
        "reaching the solver (a broken test) or the abrasive mechanics have "
        "been disconnected entirely (a real regression) — both need looking at.")
