"""The inherited Kp is not the problem — an out-of-range pH term is.

STATUS asked for the one inherited constant whose borrowing is directly
checkable. Kp sets absolute rate, so backing out the scale each pack's own data
implies and comparing with the declared value should expose packs whose Kp was
borrowed rather than fitted. Expected finding: large factors for the borrowers,
especially the silica variants that inherit `kp_m_per_pa` unchanged.

That is not what the measurement says.

    pack                          median measured / predicted    datasets
    oxide_silica                            38.73x                  8
    sic_alumina_kmno4                       12.24x                  2
    sic_ceria_h2o2                           2.13x                  5
    oxide_silica_aminosilane                 2.04x                  1
    w_fe_oxidizer                            1.13x                  3
    cu_alkaline_benzenesulfonic              1.12x                  2
    cu_h2o2_bta                              0.70x                  8
    oxide_silica_anionic                     0.51x                  1
    sti_ceria                                0.37x                  6

The two packs that inherit Kp unchanged — `oxide_silica_anionic` (0.51x) and
`oxide_silica_aminosilane` (2.04x) — are among the BEST calibrated in the corpus.
The worst is their parent, `oxide_silica`, off by nearly 39x.

WHY THE PARENT MISSES, AND WHY IT IS NOT Kp

Splitting that pack's datasets by the pH they ran at:

    dataset                                        pH          measured/predicted
    ep3161098b1_teos_silica_pressure_sweep         4.0                139.24x
    us9499721b2_teos_colloidal_silica_pressure     4.7                 98.25x
    bouvet2002_oxide_silica_size_sweep             3.0                 39.21x
    us6564116b2_oxide_taguchi_L25                  (not varied)         0.85x
    li2021_oxide_silica_ph                         10.0-12.5            0.60x

`oxide_silica` peaks at pH 11 with `ph_valid_range: [10.0, 12.5]`. The datasets
that sit inside that range are calibrated to within a factor of two. The ones
that miss by 40-139x are all running at pH 3-4.7, far down the acidic tail, where
the pH term multiplies the prediction down toward its mechanical floor.

So the deficit is the pH term evaluated outside its fitted range, and it is
ATTRIBUTED to Kp only because Kp is the last free scale in the chain. Refitting
Kp here would bake an extrapolation error into a constant that is currently
correct — precisely the mistake this audit was meant to catch.

(The pH split above also drops `us8142675b2_pt` (8.7x) and `bouvet2002_ti`
(38.2x). Both run on this pack only because no Pt or Ti pack exists, so their
deficit has a different cause — an unsupported film, limits.md entry 9 — and
mixing them in would blur the pH signal. They remain in the pack-level 38.73x
median, which is why that number is not itself a pH measurement.)

This is the same limit already recorded twice (out-of-range pH is a warning, not
a gate; a score can be real and validate nothing you assumed), now measured on
absolute rates instead of shapes. It is the first evidence of its magnitude: not
a few per cent, but two orders.

EXCLUSIONS

Eleven datasets are excluded because their own notes forbid absolute comparison —
`in_scope: false`, benchtop coupons, scaled units, shear-rheological polishing
rather than CMP. Excluding them is not cherry-picking: including a dataset whose
source says its absolute values are meaningless would corrupt the very quantity
being measured. They are listed in EXCLUDED below with the phrase that excludes
each one.

No Kp is refitted by this file.
"""
from __future__ import annotations

import re
import statistics as st
from collections import defaultdict

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _predict
from cmp_sim.core.validation import dataset_paths

#: datasets whose own notes forbid absolute-value comparison
EXCLUDED = {
    "carbide2023_slurry_composition_L9": "in_scope: false",
    "dandu2009_sio2_ceria_ph_sweep": "절대값 대조에는 당연히 부적합",
    "du2004_cu_h2o2_concentration_sweep": "in_scope: false",
    "jani2025_cu_h2o2_acidic_chelator": "in_scope: false",
    "lee2021_cu_nicotinic_inhibitor": "in_scope: false",
    "mo2026_double_sided_L16": "절대 MRR·MAPE 는 의미 없다",
    "phm2016_dresser_usage_mrr": "스케일된 단위",
    "sic2023_shear_rheological_L9": "절대값 비교 부적합 (SRP, not CMP)",
    "us20110165777a1_cu_h2o2_series": "절대값 비교 부적합",
    "us9200180b2_cu_benzenesulfonic_series": "in_scope: false",
    "yang2023_quartz_ceria_L25": "in_scope: false",
}

_EXCLUSION = re.compile(
    r"절대값\s*(비교\s*금지|대조에?는?\s*(당연히\s*)?부적합|비교\s*부적합)"
    r"|in_scope:\s*false|절대\s*MRR.*의미\s*없|스케일된\s*단위")


def _doc(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _is_excluded(doc) -> bool:
    blob = str(doc.get("notes", "")) + " " + str(doc.get("source", ""))
    return bool(_EXCLUSION.search(blob)) or doc.get("in_scope") is False


def _scale_ratios():
    """pack -> [(dataset, median measured/predicted)]"""
    out = defaultdict(list)
    for path in dataset_paths():
        doc = _doc(path)
        pack = doc.get("pack")
        if not pack or _is_excluded(doc):
            continue
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if len(rows) < 3:
            continue
        ratios = []
        for row in rows:
            predicted = _predict(doc, row)
            measured = _measured(row)
            if predicted and measured:
                ratios.append(measured / predicted)
        if ratios:
            out[pack].append((path.stem, st.median(ratios)))
    return out


def test_the_exclusion_list_matches_what_the_datasets_say():
    """Excluding a dataset must be the source's decision, not ours."""
    found = {path.stem for path in dataset_paths() if _is_excluded(_doc(path))}
    assert found == set(EXCLUDED), (
        f"excluded set drifted: unexpected {sorted(found - set(EXCLUDED))}, "
        f"missing {sorted(set(EXCLUDED) - found)}")


def test_the_packs_that_inherit_kp_are_well_calibrated():
    """The expected finding is falsified: borrowing Kp did not hurt."""
    ratios = _scale_ratios()
    for pack in ("oxide_silica_anionic", "oxide_silica_aminosilane"):
        medians = [r for _, r in ratios[pack]]
        assert medians, pack
        assert 0.3 < st.median(medians) < 3.0, (
            f"{pack} inherits kp_m_per_pa unchanged and was expected to be "
            f"miscalibrated; it is within a factor of ~2, so the hypothesis "
            "that inherited Kp is the problem does not hold")


def test_the_parent_pack_is_the_worst_calibrated():
    ratios = _scale_ratios()
    by_pack = {p: st.median([r for _, r in v]) for p, v in ratios.items()}
    worst = max(by_pack, key=lambda p: by_pack[p])
    assert worst == "oxide_silica", (worst, by_pack)
    assert by_pack["oxide_silica"] > 10, by_pack["oxide_silica"]


def test_the_parents_gap_tracks_ph_distance_not_kp():
    """The decisive test: in-range datasets are fine, acidic ones are not."""
    in_range, out_of_range = [], []
    low, high = load_pack("oxide_silica").param("ph_valid_range").value
    for path in dataset_paths():
        doc = _doc(path)
        if doc.get("pack") != "oxide_silica" or _is_excluded(doc):
            continue
        # Pt and Ti run on this pack only because no pack exists for them
        # (limits.md entry 9). Their deficit has a different cause — an
        # unsupported film — so mixing them in would blur the pH signal.
        if path.stem in ("us8142675b2_pt_alumina_pressure_sweep",
                         "bouvet2002_ti_silica_size_sweep"):
            continue
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        phs = [(r.get("overrides") or {}).get("slurry_ph") for r in rows]
        phs = [p for p in phs if p is not None]
        if not phs:
            continue
        ratios = []
        for row in rows:
            predicted, measured = _predict(doc, row), _measured(row)
            if predicted and measured:
                ratios.append(measured / predicted)
        if not ratios:
            continue
        (in_range if min(phs) >= low else out_of_range).append(
            st.median(ratios))

    assert in_range and out_of_range
    assert max(in_range) < 3.0, (
        f"datasets inside the pack's fitted pH range should be calibrated to "
        f"within a small factor; got {in_range}")
    assert min(out_of_range) > 10.0, (
        f"datasets far below the fitted pH peak should show the large deficit "
        f"this finding is about; got {out_of_range}")


def test_no_kp_was_refitted():
    """The declared constants must be exactly what they were."""
    declared = {
        "oxide_silica": 1.00e-13,
        "oxide_silica_anionic": 1.00e-13,
        "oxide_silica_aminosilane": 1.00e-13,
        "sti_ceria": 2.20e-13,
        "cu_h2o2_bta": 3.50e-13,
    }
    for pack, expected in declared.items():
        value = load_pack(pack).param("kp_m_per_pa").value
        assert abs(value - expected) / expected < 0.01, (pack, value, expected)
