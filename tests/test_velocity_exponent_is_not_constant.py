"""Locks the 9th-run verdict: the velocity exponent is NOT a single number.

WHAT WAS ASKED
--------------
Three runs of work on the velocity axis all assumed the object of the search is
one constant b_V with MRR ~ P * V**b_V:

  * ``tools/velocity_thermal_probe.py`` measured a one-sided velocity residual
    and rejected frictional heating, Stribeck lubrication and P*V series
    resistance;
  * ``tools/sorooshian_flow_probe.py`` corroborated sub-linearity as an
    experimental fact (b_V = +0.655 on a Preston-passing full factorial) but
    falsified its only zero-constant derivation on the flow leg.

Borucki & Philipossian (ECS J. Solid State Sci. Technol. 12 (2023) 043003,
DOI 10.1149/2162-8777/accaa6) report Cu velocity exponents that CHANGE SIGN
with pressure (-0.81 / -0.62 / +0.33 at 1 / 1.5 / 2 psi). Before proposing a
fourth functional form, this run measured the SHAPE of the thing being
explained, using data already in the repo.

WHAT WAS MEASURED (``tools/velocity_pressure_interaction_probe.py``)
-------------------------------------------------------------------
At fixed pressure the raw log-log slope of measured rate against speed IS the
velocity exponent, with no model in the loop and no fitted scale -- the least
model-dependent estimator available, chosen so the probe cannot inherit an
artefact from the simulator it audits.

    Sorooshian 2005 (thermal oxide, 29 ladders)
        2 psi  b_V = +0.370  (n=11, SE 0.081)
        4 psi  b_V = +0.687  (n=9,  SE 0.079)
        6 psi  b_V = +0.764  (n=9,  SE 0.034)
        -> monotone INCREASING, and 2 psi vs 6 psi are ~4 SE apart

    mariscal2020 (PETEOS/ceria, genuine 3x3)
        2 / 3 / 4 psi  b_V = +1.105 / +0.857 / +0.625
        -> monotone DECREASING

    us6918821b2 (Cu/IC1000, genuine 2x3)
        1.5 psi  b_V = -0.416      4 psi  b_V = +0.863
        -> SIGN CHANGE, reproducing Borucki's published Cu behaviour

THE CONCLUSION, AND WHY IT MATTERS MORE THAN A NUMBER
-----------------------------------------------------
1. b_V is NOT a constant. One dataset changes its sign with pressure, so no
   global exponent -- derived or fitted -- can be right, and the three-run
   programme of hunting for one was aimed at the wrong object.
2. The interaction's DIRECTION is not universal either: oxide/silica rises with
   pressure while PETEOS/ceria falls. So this is not one master curve b_V(P)
   waiting to be parameterised; it is a P-V coupling whose sign depends on the
   film/slurry pair. Any law of the form V**f(P) with a single f is already
   excluded by these two datasets together.
3. Therefore the "find the velocity exponent" line is CLOSED, the same way the
   pH axis was closed, and the open question is restated: what couples pressure
   and velocity such that the coupling can invert between consumable sets?
   (Contact-area evolution and pad-asperity flash heating both do this in
   principle; neither has a zero-constant form here yet.)

These tests exist so that (a) nobody re-opens the search for a single velocity
exponent without first contradicting this measurement, (b) no pack can smuggle
one in, and (c) if the digitised or corpus data change in a way that overturns
the verdict, the suite fails loudly instead of leaving a stale docstring.
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

from tools.velocity_pressure_interaction_probe import (
    BORUCKI_CU_EXPONENTS,
    INTERACTION_BAR,
    REVIEWED_CORPUS,
    Verdict,
    admissible_corpus,
    corpus_ladders,
    median_stderr,
    monotone_trend,
    sorooshian_ladders,
    unreviewed_sources,
)


@pytest.fixture(scope="module")
def sorooshian() -> Verdict:
    return Verdict("sorooshian", sorooshian_ladders())


@pytest.fixture(scope="module")
def corpus():
    return corpus_ladders()


def test_sorooshian_velocity_exponent_rises_with_pressure(sorooshian):
    """The exponent is not one number even inside a single oxide dataset.

    The pre-registered ratio rule does NOT fire here (0.99x), and that is
    reported honestly by the probe: with ~10 ladders per pressure it compares
    the spread of MEDIANS against the spread of SINGLE ladders and is therefore
    structurally insensitive. What the data do show is a monotone rise whose
    endpoints are separated by several standard errors of the medians -- a
    weaker claim than the ratio rule makes, and the one asserted here.
    """
    meds = sorooshian.medians()
    assert sorted(meds) == [2.0, 4.0, 6.0]
    assert monotone_trend(sorooshian) == "up", (
        f"Sorooshian per-pressure medians {meds} are no longer monotone in "
        "pressure; the 9th-run verdict rests on this."
    )
    errs = median_stderr(sorooshian)
    lo, hi = meds[2.0], meds[6.0]
    se = (errs[2.0] or 0.0) + (errs[6.0] or 0.0)
    assert hi - lo > 2.0 * se, (
        f"b_V rises only {hi - lo:+.3f} from 2 to 6 psi against a combined "
        f"median standard error of {se:.3f}; that is no longer a separation."
    )


def test_ratio_rule_does_not_fire_on_sorooshian_and_that_is_disclosed(sorooshian):
    """Do not let the pre-registered rule be quietly replaced after the fact.

    The rule was calibrated on the size and concentration probes, where each
    group held a handful of sweeps. Here it fails to fire, the monotone trend
    is flagged as POST-HOC, and this test pins that honesty: if someone later
    rewrites the probe so the ratio does fire on this body, they have changed
    the statistic, and must say so.
    """
    ratio = sorooshian.ratio()
    assert ratio is not None
    assert ratio < INTERACTION_BAR, (
        f"ratio is now {ratio:.2f}x, at or above the pre-registered "
        f"{INTERACTION_BAR:.1f}x bar. If the estimator changed, update the "
        "docstrings that call this body 'suggestive but under-powered'."
    )


def test_copper_exponent_changes_sign_with_pressure(corpus):
    """The decisive, purely qualitative result: b_V < 0 at low P, > 0 at high P.

    us6918821b2 is a genuine 2x3 pressure x speed factorial on one pad and one
    slurry, and it independently reproduces Borucki's published Cu sign change.
    A sign change cannot be absorbed by any single exponent.
    """
    per_dataset = admissible_corpus(corpus)
    cu = per_dataset.get("us6918821b2_cu_ic1000_pressure_speed_2x3")
    assert cu, "the Cu pressure x speed factorial produced no ladders"
    body = Verdict("cu", cu)
    meds = body.medians()
    assert len(meds) >= 2, f"only one pressure level survived: {meds}"
    assert body.sign_change(), (
        f"Cu per-pressure exponents {meds} no longer change sign. The 9th-run "
        "verdict that no global velocity exponent can exist rests on this "
        "measurement plus Borucki 2023."
    )
    assert meds[min(meds)] < 0 < meds[max(meds)], (
        f"the sign change has reversed direction: {meds}. Borucki reports "
        "negative at low pressure turning positive at high pressure."
    )


def test_published_copper_observation_agrees_in_direction():
    """Our corpus and Borucki 2023 are not merely both 'variable' — they agree.

    Kept as an explicit assertion so that if the transcribed literature values
    are ever corrected, the agreement claim in the docstrings is re-checked
    rather than assumed.
    """
    pressures = sorted(BORUCKI_CU_EXPONENTS)
    assert BORUCKI_CU_EXPONENTS[pressures[0]] < 0
    assert BORUCKI_CU_EXPONENTS[pressures[-1]] > 0


def test_interaction_direction_is_not_universal(corpus):
    """The coupling's SIGN differs between consumable sets, so no b_V(P) either.

    Sorooshian (oxide / fumed silica) rises with pressure; mariscal2020
    (PETEOS / ceria) falls. Both are monotone and both are genuine factorials,
    so a single master function V**f(P) is excluded by the pair -- which is
    what forbids replacing the constant exponent with one pressure-dependent
    exponent and calling the axis solved.
    """
    oxide = Verdict("sorooshian", sorooshian_ladders())
    mari = admissible_corpus(corpus).get(
        "mariscal2020_peteos_ceria_pressure_velocity_3x3")
    assert mari, "the PETEOS 3x3 factorial produced no ladders"
    assert monotone_trend(oxide) == "up"
    assert monotone_trend(Verdict("mariscal", mari)) == "down", (
        "mariscal2020's exponent no longer falls with pressure; if both bodies "
        "now trend the same way, a single b_V(P) becomes admissible again and "
        "this module's conclusion must be revisited."
    )


def test_confounded_designs_are_excluded_with_a_recorded_reason(corpus):
    """An L9 array is not a velocity ladder, and the reason must be written down.

    sic2023_shear_rheological_L9 changes abrasive size and loading from row to
    row, recording them only in the row LABEL where the grouping key cannot see
    them, which produced a nonsensical b_V = +6.76 at one pressure. Excluding
    it is a statement about its DESIGN, not about its answer, so the reason is
    stored in the probe and pinned here.
    """
    ok, why = REVIEWED_CORPUS["sic2023_shear_rheological_L9"]
    assert ok is False
    assert "L9" in why and "label" in why.lower()
    assert "sic2023_shear_rheological_L9" not in admissible_corpus(corpus)


def test_every_ladder_producing_dataset_has_been_reviewed(corpus):
    """A newly added dataset must be looked at, not silently averaged in.

    This is the guard that the first cut of this probe needed and lacked: it
    pooled one ladder from each of several unrelated datasets and reported a
    spurious 22x interaction, because the across-pressure spread was really the
    spread between films, slurries and tools.
    """
    missing = unreviewed_sources(corpus)
    assert not missing, (
        f"{missing} now produce per-pressure velocity ladders but have not "
        "been reviewed for design confounds. Add each to REVIEWED_CORPUS with "
        "an explicit admit/exclude reason before any verdict is trusted."
    )


def test_no_pack_declares_a_velocity_exponent_or_a_pv_interaction_constant():
    """Nothing may be adopted from this run: it is a negative shape result.

    The temptation after measuring a pressure-dependent exponent is to fit
    b_V(P) per pack. That is a fitted function replacing a fitted constant,
    with no derivation, and test_interaction_direction_is_not_universal shows a
    single such function cannot cover even the two clean datasets here.
    """
    forbidden = {"velocity_exponent", "v_exponent", "pv_interaction",
                 "pv_interaction_exponent", "velocity_exponent_at_pressure",
                 "velocity_pressure_coupling", "b_v"}
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
        f"{offenders} declare a velocity exponent or a P-V coupling constant. "
        "The 9th run measured that b_V moves with pressure AND that the "
        "direction of that movement differs between film/slurry pairs, so no "
        "single exponent and no single b_V(P) is admissible. A mechanism that "
        "predicts an invertible P-V coupling would be; derive it, cite it, "
        "then change this test."
    )
