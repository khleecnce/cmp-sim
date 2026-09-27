"""Is the abrasive-SWAP detector reachable at all, and what would it change?

This is a MEASUREMENT script. It touches no pack and fits nothing.

THE FINDING THAT MOTIVATES IT (31st run)
----------------------------------------
``cmp_sim/slurry/abrasive_effects.py`` exists because ``slurry.abrasive.kind``
once had no effect on the rate whatsoever. It resolves the abrasive actually
used, compares it against the pack's ``reference_abrasive``, and on a mismatch
replaces the pack's abrasive-scoped exponents with material-scoped or derived
ones (and refuses the absolute scale, marking the run ``ranking_only``).

Running the SHIPPING solver over all 49 corpus datasets returns

    kind = None, reference_kind = None, matches_reference = True

on every single one. The module is inert in 100 % of scored runs, because
``_recipe_for`` in ``core/predictive_score.py`` builds the recipe only from a
dataset's ``overrides:`` keys, and NO dataset declares which abrasive it used.
``matches_reference = True`` is therefore not a finding, it is a default --
asserted even for datasets whose own header says in prose that the abrasive is
NOT the pack's (entegris2022: "the abrasive here is alumina/zirconia, not
ceria"; yang2023: "the abrasive is a CeO2-LaOF composite, not plain ceria").

That is the error class this repository names most often: an input accepted and
silently discarded, with a confident answer returned as if the question had
been asked. It is also the class fixable with ZERO new constants -- the
machinery, the material table and the derived law are all already written,
sourced and unit-tested. Nothing here invents a value.

WHAT THIS PROBE ANSWERS, IN ORDER
---------------------------------
1. REACHABILITY. For each dataset, does its pack declare ``reference_abrasive``
   at all? Without one, declaring the abrasive can still not detect a swap, so
   no amount of dataset work helps and the honest state is a warning.
2. SCOPE. How many datasets actually use a DIFFERENT abrasive from their pack's
   reference? A fix that fires nowhere is not a fix.
3. PRICE. For the mismatched datasets, what does the shape error do when the
   abrasive is declared? This is measured by running the real solver with
   ``slurry.abrasive.kind`` set, NOT by reasoning about the code.

⚠ The verdict must be taken on ALL mismatched datasets together, never on the
ones that improve. A swap correction that helps three datasets and wrecks two
is not a correction, and the median is not the place to discover that.

Usage: ``.venv/bin/python tools/abrasive_declaration_probe.py``
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from cmp_sim.api import run_recipe  # noqa: E402
from cmp_sim.core.predictive_score import _measured, _recipe_for  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402
from cmp_sim.slurry.abrasive_effects import canonical_kind  # noqa: E402

#: Abrasive each dataset actually used, transcribed from the dataset file's OWN
#: header prose or its cited source table. This is a transcription, not a
#: judgement: every entry must be quotable from the file it names. Datasets
#: whose abrasive is a composite with no canonical database key are recorded as
#: such rather than resolved onto a parent material -- asserting a composition
#: the source does not give is the same error as inventing a constant.
#:
#: The probe does NOT read this table into the model. It exists so the price
#: below is measured against a stated attribution that a reviewer can check.
DECLARED_ABRASIVE: Dict[str, Optional[str]] = {
    # --- alumina, stated as the abrasive by the dataset's own header ---------
    "entegris2022_us20220315802a1_sic_alumina_conc": "alumina",
    #   "The abrasive here is alumina/zirconia, not ceria"; rows "Al2O3 0.1wt%".
    "gong2024_4hsic_alumina_kmno4_L25": "alumina",
    #   Title quoted in the header: "... Based on an Alumina (Al2O3) Abrasive".
    "su2011_procengr_6hsic_alumina_abrasive_conc": "alumina",
    #   "Based on Abrasive Alumina (Al2O3)"; rows "Al2O3 6g/500mL".
    "su2011_sic_alumina_size_sweep": "alumina",
    #   "PLACEHOLDER: the abrasive is ALUMINA and the workpiece is SiC".
    "lai2001_cu_alumina_size_sweep": "alumina",
    #   "Abrasive  alpha-Al2O3" transcribed from the paper's own table.
    "du2004_cu_h2o2_concentration_sweep": "alumina",
    #   "4.6 wt% alumina" in every row label; "Du used alumina".
    "us8142675b2_pt_alumina_pressure_sweep": "alumina",
    #   "6 wt % alpha-alumina abrasive (CR-30)", TABLE XVI.

    # --- colloidal silica ----------------------------------------------------
    "wei2026_sic_silica_size_sweep": "colloidal_silica",
    #   "slurry contained 4 wt% colloidal silica with different average sizes".
    "ep3161098b1_w_silica_pressure_sweep": "colloidal_silica",
    #   "2.0 wt% core-shell colloidal silica with an internal aminopropyl...".
    "ep3161098b1_teos_silica_pressure_sweep": "colloidal_silica",
    #   Same patent, paragraph [0089], same composition.
    "bouvet2002_oxide_silica_size_sweep": "colloidal_silica",
    "bouvet2002_w_silica_size_sweep": "colloidal_silica",
    "bouvet2002_ti_silica_size_sweep": "colloidal_silica",
    #   Row labels: "12 / 25 / 45 / 75 nm colloidal silica, 16.3 wt%".
    "us9499721b2_teos_colloidal_silica_pressure_conc": "colloidal_silica",
    #   Patent title: "Colloidal silica chemical-mechanical ...".
    "cn109609035b_oxide_anionic_silica_ph": "colloidal_silica",
    #   "ANIONIC colloidal silica, 1 wt%".
    "bae2022_si_wafer_alkali_ph": "colloidal_silica",
    #   "1 wt% colloidal silica, 60 nm primary".

    # --- ceria ---------------------------------------------------------------
    "son2021_oxide_ceria_size_sweep": "ceria",
    #   "3 / 20 / 40 / 70 / 100 nm wet CeO2".
    "dandu2009_sio2_ceria_ph_sweep": "ceria",
    #   "carried out at 0.25% ceria particle loading".
    "netzband2020_thermal_oxide_ceria_ph": "ceria",
    #   Row labels "pH 4 (68nm ceria 1wt%, 20kPa)".
    "kenchappa2021_softpad_hdp_oxide": "ceria",
    #   "current challenges using ceria-based slurries".
    "mariscal2020_peteos_ceria_pressure_velocity_3x3": "ceria",
    #   Header: the slurry is ceria, which is why sti_ceria was chosen.
    "sic2026_ceria_h2o2_ph_DOE50": "ceria",
    #   Levels "CeO2 2/4/6 wt%".

    # --- COMPOSITE particles: deliberately NOT resolved ----------------------
    # Each of these is a two-material particle whose composition the source does
    # not give as a fraction. Resolving it onto either parent would assert a
    # composition nobody measured -- the same error class as inventing a
    # constant -- and the size table's own header already refuses to place
    # ceria-coated silica for exactly this reason. Left None on purpose.
    "us20190127607a1_teos_ceriasilica_size_sweep": None,      # ceria-coated silica
    "us20190127607a1_hdpoxide_ceriasilica_size_sweep": None,  # ceria-coated silica
    "liang2026_4hsic_ceria_composite_h2o2_conc": None,        # CuxO-CeO2/Al2O3
    "yang2023_quartz_ceria_L25": None,                        # CeO2-LaOF
    # Fixed-abrasive pad: the ceria is IN THE PAD, not in the slurry, so
    # "the slurry's abrasive" is not a question this dataset answers.
    "us6918821b2_cu_ic1000_pressure_speed_2x3": None,
}


def pack_reference(doc: Dict[str, Any]) -> Optional[str]:
    """``reference_abrasive`` the pack declares, as the solver would read it."""
    rows = doc.get("conditions") or []
    if not rows:
        return None
    try:
        result = run_recipe(_recipe_for(doc, rows[0]))
    except Exception:
        return None
    prov = result.get("provenance") or {}
    entry = prov.get("reference_abrasive")
    if isinstance(entry, dict):
        return entry.get("value")
    return (result.get("abrasive_type") or {}).get("reference_kind")


def shape_mape(measured: List[float], predicted: List[float]) -> float:
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    return 100.0 * sum(abs(scale * p - m) / m
                       for m, p in zip(measured, predicted)) / len(measured)


def score(doc: Dict[str, Any], kind: Optional[str] = None) -> Optional[float]:
    """Shape MAPE for one dataset, optionally declaring ``kind``."""
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    if len(rows) < 2:
        return None
    predicted: List[float] = []
    for row in rows:
        recipe = _recipe_for(doc, row)
        if kind:
            slurry = recipe.setdefault("slurry", {})
            abrasive = slurry.setdefault("abrasive", {})
            abrasive["kind"] = kind
        try:
            value = run_recipe(recipe).get("removal_rate_A_per_min")
        except Exception:
            return None
        if not value:
            return None
        predicted.append(float(value))
    return shape_mape([float(_measured(r)) for r in rows], predicted)


def main() -> None:
    print("REACHABILITY: does each dataset's pack declare reference_abrasive?")
    print(f"{'dataset':46s} {'pack':24s} {'reference_abrasive'}")
    missing = 0
    total = 0
    refs: Dict[str, Optional[str]] = {}
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if not (doc.get("conditions") or []):
            continue
        name = Path(path).stem
        ref = pack_reference(doc)
        refs[name] = ref
        total += 1
        if ref is None:
            missing += 1
        print(f"{name[:46]:46s} {str(doc.get('pack'))[:24]:24s} "
              f"{ref if ref else '-- NONE: a swap cannot be detected --'}")

    print()
    print(f"{total - missing}/{total} datasets sit on a pack that CAN detect a "
          f"swap; {missing} cannot, and for those declaring the abrasive "
          f"changes nothing but the warning text.")

    if not DECLARED_ABRASIVE:
        print()
        print("SCOPE/PRICE: not measurable yet -- DECLARED_ABRASIVE is empty.")
        print("Fill it ONLY from each dataset file's own header or cited table.")
        return

    print()
    print("PRICE: shape MAPE with the abrasive declared vs the current default")
    print(f"{'dataset':46s} {'used':16s} {'pack ref':16s} "
          f"{'before':>7s} {'after':>7s} {'delta':>7s}")
    deltas: List[float] = []
    for name, used in sorted(DECLARED_ABRASIVE.items()):
        if used is None:
            continue
        path = next((p for p in dataset_paths() if Path(p).stem == name), None)
        if path is None:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        ref = refs.get(name)
        canon_used = canonical_kind(used)
        canon_ref = canonical_kind(ref) if ref else None
        before = score(doc)
        after = score(doc, kind=used)
        if before is None or after is None:
            print(f"{name[:46]:46s} {used[:16]:16s} {str(ref)[:16]:16s} "
                  f"{'n/a':>7s} {'n/a':>7s}")
            continue
        flag = "" if canon_used == canon_ref else "  SWAP"
        deltas.append(after - before)
        print(f"{name[:46]:46s} {used[:16]:16s} {str(ref)[:16]:16s} "
              f"{before:7.1f} {after:7.1f} {after - before:+7.1f}{flag}")

    if deltas:
        worse = sum(1 for d in deltas if d > 0.05)
        better = sum(1 for d in deltas if d < -0.05)
        print()
        print(f"  {better} datasets improve, {worse} worsen, "
              f"{len(deltas) - better - worse} unchanged; "
              f"mean delta {sum(deltas) / len(deltas):+.2f} pp")
        print("  A correction is only a correction if it does not trade one "
              "dataset's error for another's. Read the WORSE column first.")


if __name__ == "__main__":
    main()
