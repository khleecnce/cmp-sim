"""An inert constant that looks active is worse than no constant.

`sic_ceria_h2o2` declared `ph_response_width: null` on purpose. The reasoning in
the pack was sound as far as it went: SiC is oxidation-limited rather than
hydrolysis-limited, its reported pH dependence runs opposite to silica's, and
the pack's inheritance chain (SiC -> sti_ceria -> oxide_silica) would otherwise
have handed it the SILICA optimum of pH 4.5 — acid side, wrong film. Nulling the
width switched the term off rather than guessing.

But switching the term off did not remove the inherited peak. The pack was left
declaring `ph_peak: 4.5` with no width, which is a constant that LOOKS like a
SiC optimum and does nothing at all. The engine already warns about precisely
this shape of mistake ("declares an optimum pH but no ph_response_width, so pH
is INERT") — the warning existed and the condition persisted.

THE JUSTIFICATION FOR THE NULL WAS ALSO CHECKABLE, AND IT WAS WRONG. The note
said the DOE50 set "varies pH together with oxidizer and pressure, so it cannot
isolate the pH axis". True of the set as a whole; false of its structure.
Grouping the 50 rows so that only pH moves leaves FIVE isolated groups spanning
pH 9/10/11:

    (9, 26.7)  (10, 31.1)  (11, 62.7)
    (9, 18.1)  (10, 66.1)  (11, 66.9)
    (9, 19.6)  (10, 60.0)  (11, 63.3)
    (9, 40.0)  (10, 29.1)  (11, 24.9)
    (9, 15.2)  (10, 45.1)  (11, 38.7)

Enough to fit a peak, a width and a floor: pH 10.5, width 1.25, floor 0.10, at
27.5% shape error against 57.1% with the term inert. And the fitted optimum is
ALKALINE — which is what the pack's own mechanism argument predicted, and the
opposite of the inherited 4.5 it was protecting against.

THE TRADE IS RECORDED HONESTLY. Activating the term improves the DOE50 set from
39.3% to 34.0%, and slightly worsens three held-out SiC datasets that sweep
other axes at a fixed pH (liang2026 18.1 -> 19.4, su2011_size 4.2 -> 4.4,
wei2026 3.1 -> 3.2), because their Kp normalisation now runs through a pH term
that is no longer identically 1. Net strongly positive, but not free, and a
future re-fit should know it.
"""
from __future__ import annotations

from collections import defaultdict

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, score_dataset
from cmp_sim.core.validation import dataset_paths
from cmp_sim.models.chemical_rate import ph_response

DOE = "sic2026_ceria_h2o2_ph_DOE50"


def _value(pack_name, key):
    param = load_pack(pack_name).param(key)
    return param.value if hasattr(param, "value") else param


def _isolated_ph_groups():
    """Groups of rows in which ONLY pH differs."""
    doc = yaml.safe_load(
        next(p for p in dataset_paths() if p.stem == DOE)
        .read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for row in doc["conditions"]:
        overrides = dict(row.get("overrides") or {})
        ph = overrides.pop("slurry_ph", None)
        if ph is None:
            continue
        key = (row.get("pressure_psi"), row.get("rpm_platen"),
               tuple(sorted((k, str(v)) for k, v in overrides.items())))
        groups[key].append((ph, _measured(row)))
    return [sorted(v) for v in groups.values() if len({x[0] for x in v}) >= 3]


# ---------------------------------------------------------------------------
# the isolation the pack said was impossible
# ---------------------------------------------------------------------------

def test_the_doe_set_does_isolate_the_ph_axis():
    groups = _isolated_ph_groups()
    assert len(groups) >= 5, f"only {len(groups)} isolated pH groups"
    for group in groups:
        phs = {ph for ph, _ in group}
        assert phs >= {9, 10, 11} or len(phs) >= 3, group


# ---------------------------------------------------------------------------
# the term is active, and it is SiC's own optimum rather than silica's
# ---------------------------------------------------------------------------

def test_the_ph_term_is_no_longer_inert():
    assert _value("sic_ceria_h2o2", "ph_response_width") is not None, (
        "a pack that declares ph_peak with no width has a constant that looks "
        "active and does nothing")


def test_the_optimum_is_alkaline_not_the_inherited_silica_value():
    """The inherited 4.5 comes from sti_ceria, the DIRECT parent.

    Note oxide_silica's own peak is 11.0, which happens to sit near SiC's
    fitted 10.5 — so the meaningful comparison is against the value SiC would
    actually have received, not against the grandparent.
    """
    peak = _value("sic_ceria_h2o2", "ph_peak")
    assert peak > 8.0, (
        f"ph_peak={peak}; the inherited value is 4.5 and SiC is "
        "oxidation-limited, so an acid optimum here means the inheritance "
        "leaked back in")
    inherited = _value("sti_ceria", "ph_peak")
    assert abs(inherited - 4.5) < 0.01, (
        f"sti_ceria's peak moved to {inherited}; this test's premise was that "
        "4.5 is what SiC would inherit")
    assert peak - inherited > 4.0, (peak, inherited)


def test_the_optimum_is_interior_to_the_measured_range_unlike_the_bound_packs():
    """SiC's peak is a real optimum: the data bracket it on both sides."""
    peak = _value("sic_ceria_h2o2", "ph_peak")
    low, high = _value("sic_ceria_h2o2", "ph_valid_range")
    assert low < peak < high, (low, peak, high)


def test_the_narrow_range_is_declared():
    low, high = _value("sic_ceria_h2o2", "ph_valid_range")
    phs = {ph for group in _isolated_ph_groups() for ph, _ in group}
    assert (low, high) == (float(min(phs)), float(max(phs))), (low, high, phs)


def test_the_floor_is_not_zero():
    """SiC still removes away from the optimum: the ceria is under load."""
    assert _value("sic_ceria_h2o2", "ph_mechanical_floor") > 0.0


# ---------------------------------------------------------------------------
# and it beats the inert configuration on the data that justified it
# ---------------------------------------------------------------------------

def test_the_active_term_beats_the_inert_one_on_the_isolated_groups():
    peak = _value("sic_ceria_h2o2", "ph_peak")
    width = _value("sic_ceria_h2o2", "ph_response_width")
    floor = _value("sic_ceria_h2o2", "ph_mechanical_floor")

    def shape_error(response):
        errors = []
        for group in _isolated_ph_groups():
            phs = [ph for ph, _ in group]
            rates = [rate for _, rate in group]
            predicted = [response(ph) for ph in phs]
            scale = (sum(r * p for r, p in zip(rates, predicted))
                     / sum(p * p for p in predicted))
            errors += [abs(scale * p - r) / r for r, p in zip(rates, predicted)]
        return 100 * sum(errors) / len(errors)

    active = shape_error(lambda ph: ph_response(ph, peak, width, floor))
    inert = shape_error(lambda ph: 1.0)
    assert active < inert - 10.0, (
        f"active {active:.1f}% vs inert {inert:.1f}%; the fitted pH term must "
        "earn its place on the groups that justified it")


def test_the_doe_dataset_still_beats_predicting_its_own_mean():
    score = score_dataset(next(p for p in dataset_paths() if p.stem == DOE))
    assert score.beats_flat, (score.shape_mape, score.flat_mape)
    assert score.shape_mape < 36.0, score.shape_mape
