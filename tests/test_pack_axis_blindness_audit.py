"""Pack blindness audit: a pack must not be silent on an axis its data sweeps.

`cu_alkaline_benzenesulfonic` carried no pH response while its own datasets
swept pH across 3.4x in rate, and the consequence was not just an unexplained
dataset — the missing term's work was absorbed by the oxidiser term, whose
shape constant was then justified by a trend that was really pH drift.

That failure mode is mechanical to look for, so it is looked for mechanically:
for every pack, compare the parameters it declares against the axes its own
registered datasets actually vary. A pack that is SILENT on an axis its
evidence sweeps is either missing physics or about to hide that physics
somewhere else.

THE AUDIT FOUND EXACTLY ONE, and it is the one STATUS predicted:
w_fe_oxidizer, whose datasets vary pH while the pack declares no pH response.

AND THE BLINDNESS IS CORRECT THERE. US20110186542A1 runs a clean two-level pH
control — pH 3 against pH 6 at MATCHED oxidiser and abrasive loading, six
matched pairs:

    H2O2   abrasive   pH 3    pH 6    ratio
    0.0     0.01       289     246    0.851
    1.0     0.01      1100    1320    1.200
    3.0     0.01      2270    2110    0.930
    0.0     0.02       363     298    0.821
    1.0     0.02      1650    1610    0.976
    3.0     0.02      2430    2360    0.971

Mean ratio 0.958, and the sign is not even consistent: doubling the acidity
raises the rate in one pair and lowers it in five, by amounts comparable to the
scatter. Tungsten's removal in this chemistry is governed by the Fe(III)/H2O2
oxidation of the metal, not by the pH of the medium, across the range tested.

So this pack is silent because the measurement says silence — a sourced NULL
RESULT, which is a different thing from an omission, and the audit must be able
to tell them apart. The distinction is recorded in the pack itself so the next
reader does not "fix" it.

These tests keep the audit running: a NEW pack that is blind to an axis its
datasets sweep will fail here unless it declares the null result explicitly.
"""
from __future__ import annotations

from collections import defaultdict

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

#: axis override key -> the parameter names that would make a pack responsive
AXIS_PARAMS = {
    "slurry_ph": ("ph_peak", "ph_response_width"),
    "oxidizer_wt_pct": ("oxidizer_peak_wt_pct", "oxidizer_ref_wt_pct",
                        "oxidizer_passivation_K"),
    "inhibitor_mM": ("inhibitor_K", "inhibitor_coverage_K", "inhibitor_ref_mM"),
    "abrasive_size_nm": ("abrasive_size_exponent",),
    "abrasive_wt_pct": ("abrasive_conc_exponent", "abrasive_wt_pct"),
    "chelator_M": ("chelator_K", "chelator_ref_M"),
}

#: pack -> axes it is deliberately silent on, with the evidence for silence.
#: An entry here is a CLAIM that the measurement shows no effect, and the test
#: below re-checks that claim against the data rather than trusting it.
DECLARED_NULL_RESULTS = {
    ("w_fe_oxidizer", "slurry_ph"): "us20110186542a1_w_diamond_h2o2_ph",
}


def _swept_axes():
    """pack -> {axis keys its registered datasets actually vary}."""
    swept = defaultdict(set)
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pack = doc.get("pack")
        if not pack:
            continue
        values = defaultdict(set)
        for row in doc.get("conditions") or []:
            for key, value in (row.get("overrides") or {}).items():
                values[key].add(str(value))
        for key, seen in values.items():
            if len(seen) > 1 and key in AXIS_PARAMS:
                swept[pack].add(key)
    return swept


def _declares(pack_name: str, axis: str) -> bool:
    pack = load_pack(pack_name)
    for key in AXIS_PARAMS[axis]:
        try:
            if pack.param(key) is not None:
                return True
        except Exception:
            continue
    return False


def test_no_pack_is_silently_blind_to_an_axis_its_data_sweeps():
    """The audit. A hit is either missing physics or a declared null result."""
    blind = []
    for pack, axes in sorted(_swept_axes().items()):
        for axis in sorted(axes):
            if _declares(pack, axis):
                continue
            if (pack, axis) in DECLARED_NULL_RESULTS:
                continue
            blind.append((pack, axis))

    assert not blind, (
        f"{blind} declare no response on an axis their own datasets vary. "
        "Diagnose each the way cu_alkaline_benzenesulfonic was diagnosed: a "
        "silent term does not stay silent, its work is absorbed by whichever "
        "term is still free to move. If the measurement genuinely shows no "
        "effect, add it to DECLARED_NULL_RESULTS with the dataset that proves "
        "it.")


def test_the_tungsten_pH_null_result_is_backed_by_a_matched_pair_control():
    """Re-derive the claim rather than trusting the registry above.

    The dataset varies pH at MATCHED oxidiser and abrasive, so the pH effect
    can be isolated as a ratio within each pair.
    """
    stem = DECLARED_NULL_RESULTS[("w_fe_oxidizer", "slurry_ph")]
    doc = yaml.safe_load(next(p for p in dataset_paths() if p.stem == stem)
                         .read_text(encoding="utf-8"))

    by_condition = {}
    for row in doc["conditions"]:
        overrides = row["overrides"]
        key = (overrides["oxidizer_wt_pct"], overrides["abrasive_wt_pct"])
        by_condition.setdefault(key, {})[overrides["slurry_ph"]] = _measured(row)

    ratios = [rates[6.0] / rates[3.0] for rates in by_condition.values()
              if 3.0 in rates and 6.0 in rates]

    assert len(ratios) >= 6, f"only {len(ratios)} matched pairs"
    mean = sum(ratios) / len(ratios)
    assert 0.9 < mean < 1.1, f"pH 3 -> 6 changes the rate by {abs(1 - mean):.1%}"
    # the sign is not even consistent, which is what makes it a null result
    assert min(ratios) < 1.0 < max(ratios), ratios


def test_a_declared_null_result_still_names_a_dataset():
    for (pack, axis), stem in DECLARED_NULL_RESULTS.items():
        assert any(p.stem == stem for p in dataset_paths()), (
            f"{pack}/{axis} claims a null result from {stem}, which is not "
            "registered")
        assert not _declares(pack, axis), (
            f"{pack} now declares a response for {axis}; remove the null-result "
            "entry, it is no longer true")
