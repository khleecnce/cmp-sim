"""How much of the model rests on data, and how much on inheritance.

Every previous audit in this project asked about one pack or one axis. This one
asks the whole question at once: for each parameter a pack carries, does any
dataset scored with that pack actually VARY the quantity it controls?

A parameter is counted EXERCISED when a dataset using its pack sweeps the axis it
governs — `ph_peak` is exercised only if some dataset varies `slurry_ph`, and so
on. Anything else is asserted on inheritance and literature alone. That is not a
defect by itself: a Preston coefficient or a pad modulus can be perfectly sound
without a sweep in this corpus. It IS a defect to let a reader assume otherwise,
which is what an unqualified "19.5% median" invites.

The mapping below is deliberately coarse and conservative: a parameter counts as
exercised if ANY axis in its group is swept. That biases the result OPTIMISTIC —
the true evidenced fraction is lower than the number this test reports, never
higher. Stated plainly so nobody quotes it as a floor.

Parameters that describe consumables or the tool rather than the slurry response
(pad geometry, grooves, conditioner schedule, platen temperatures) are grouped
separately, because "unexercised" means something different for them: they are
inputs a user supplies, not constants fitted to a curve.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Set

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

#: parameter prefix -> the dataset axes that would exercise it
EXERCISED_BY: Dict[str, Set[str]] = {
    "ph": {"slurry_ph"},
    "oxidizer": {"oxidizer_wt_pct", "h2o2_vol_pct"},
    "sic": {"slurry_ph", "oxidizer_wt_pct"},
    "cu": {"slurry_ph"},
    "w": {"slurry_ph"},
    "abrasive": {"abrasive_wt_pct", "abrasive_size_nm", "abrasive_d50_nm",
                 "abrasive_d99_nm"},
    "active": {"abrasive_wt_pct", "abrasive_size_nm"},
    "inhibitor": {"inhibitor_mM", "inhibitor_ppm"},
    "shield": {"dispersant_wt_pct", "inhibitor_mM", "inhibitor_ppm"},
    "chelator": {"chelator_M"},
    "promoter": {"promoter_M"},
    "fe": {"fe_ppm"},
    "kp": {"pressure_psi", "rpm_platen"},
    "tr": {"pressure_psi"},
    "relative": {"rpm_platen", "rpm_head"},
    "cond": {"cond_disk_usage_hours"},
    "stab": {"cond_disk_usage_hours"},
    "pad": {"pad_hardness_shore_d"},
}

#: prefixes that are user-supplied inputs or tool state, not fitted constants
INPUT_LIKE = {"groove", "platen", "retaining", "wafer", "edge", "n", "center",
              "pad", "cond", "stab", "lambda", "slurry", "pressure", "rpm",
              "sfr", "film", "reference", "dishing", "initial"}


def _packs_and_axes() -> Dict[str, Set[str]]:
    """Which axes each pack's own datasets actually vary."""
    varied: Dict[str, Set[str]] = defaultdict(set)
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pack = doc.get("pack")
        if not pack:
            continue
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if len(rows) < 3:
            continue
        seen: Dict[str, Set[str]] = defaultdict(set)
        for row in rows:
            for key, value in (row.get("overrides") or {}).items():
                seen[key].add(str(value))
            for key in ("pressure_psi", "rpm_platen", "rpm_head"):
                if row.get(key) is not None:
                    seen[key].add(str(row[key]))
        varied[pack] |= {k for k, v in seen.items() if len(v) > 1}
    return varied


def _inventory():
    """(pack, exercised, unexercised, input_like) per pack."""
    out = {}
    for pack_name, axes in _packs_and_axes().items():
        pack = load_pack(pack_name)
        names = sorted(getattr(pack, "params", {}).keys())
        exercised, unexercised, inputs = [], [], []
        for name in names:
            prefix = name.split("_")[0]
            if prefix in INPUT_LIKE and prefix not in ("pad", "cond", "stab"):
                inputs.append(name)
                continue
            triggers = EXERCISED_BY.get(prefix)
            if triggers and (triggers & axes):
                exercised.append(name)
            elif prefix in INPUT_LIKE:
                inputs.append(name)
            else:
                unexercised.append(name)
        out[pack_name] = (exercised, unexercised, inputs)
    return out


def test_the_inventory_covers_every_pack_with_data():
    inventory = _inventory()
    assert len(inventory) >= 9, sorted(inventory)
    for pack, (exercised, unexercised, inputs) in inventory.items():
        assert exercised or unexercised, pack


def test_most_parameters_are_not_exercised_by_any_dataset():
    """The headline number, and it is deliberately uncomfortable."""
    inventory = _inventory()
    total_ex = sum(len(e) for e, _, _ in inventory.values())
    total_un = sum(len(u) for _, u, _ in inventory.values())
    fraction = total_ex / (total_ex + total_un)
    assert fraction < 0.5, (
        f"{100 * fraction:.0f}% of fitted parameters are exercised — if this "
        "has genuinely risen above half, the README claim derived from it must "
        "be updated rather than this test relaxed")
    assert fraction > 0.05, (
        "an exercised fraction this low suggests the axis mapping broke, not "
        "that the model got worse")


def test_the_mapping_is_optimistic_by_construction():
    """A parameter counts as exercised if ANY axis in its group is swept.

    ph_peak, ph_response_width, ph_mechanical_floor and ph_acid_mechanical_floor
    all count as exercised the moment a single dataset varies slurry_ph, even
    though one sweep cannot separate four constants. The reported fraction is
    therefore an UPPER bound.
    """
    inventory = _inventory()
    exercised, _, _ = inventory["oxide_silica"]
    ph_params = [p for p in exercised if p.startswith("ph_")]
    assert len(ph_params) > 2, (
        "several pH constants are credited to one pH sweep — that is the "
        "optimism this test documents")


def test_no_pack_claims_full_coverage():
    for pack, (exercised, unexercised, _) in _inventory().items():
        assert unexercised, (
            f"{pack} reports every fitted parameter as exercised, which no "
            "corpus this size can support — check the axis mapping")


def test_packs_with_one_axis_are_the_least_evidenced():
    """oxide_silica_anionic is scored on a single pH sweep of 7 rows."""
    exercised, unexercised, _ = _inventory()["oxide_silica_anionic"]
    fraction = len(exercised) / (len(exercised) + len(unexercised))
    assert fraction < 0.2, fraction


def test_report_is_printable():
    """The inventory must be readable, since it is destined for the README."""
    lines = []
    for pack, (exercised, unexercised, inputs) in sorted(_inventory().items()):
        total = len(exercised) + len(unexercised)
        lines.append(f"{pack:30} {len(exercised):3}/{total:3} exercised "
                     f"({100 * len(exercised) / total:4.0f}%), "
                     f"{len(inputs):3} user inputs")
    text = "\n".join(lines)
    assert "oxide_silica" in text
    print("\n" + text)


def test_the_readme_table_matches_the_computed_inventory():
    """The published numbers must be derived, not typed from memory."""
    from pathlib import Path

    import cmp_sim
    readme = (Path(cmp_sim.__file__).parent.parent / "README.md"
              ).read_text(encoding="utf-8")
    assert "290 / 628 (46%)" in readme, (
        "the README's parameter-evidence total no longer matches this test; "
        "recompute it rather than editing the prose")

    inventory = _inventory()
    for pack in ("cu_h2o2_bta", "oxide_silica_anionic"):
        exercised, unexercised, _ = inventory[pack]
        total = len(exercised) + len(unexercised)
        assert f"{len(exercised)} / {total}" in readme, (
            f"{pack}: README says something other than "
            f"{len(exercised)}/{total}")


def test_the_readme_states_the_number_is_an_upper_bound():
    """The caveat travels with the figure or the figure misleads."""
    from pathlib import Path

    import cmp_sim
    readme = (Path(cmp_sim.__file__).parent.parent / "README.md"
              ).read_text(encoding="utf-8")
    assert "upper bound" in readme
    assert "not *validated*" in readme or "not validated" in readme, (
        "the README must distinguish exercised from validated, since "
        "sic_alumina_kmno4 is exercised only in extrapolation")
