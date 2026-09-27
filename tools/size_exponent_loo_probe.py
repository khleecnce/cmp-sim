"""Leave-one-out repair for the self-graded ``abrasive_size_exponent`` family.

The problem this answers (docs/limits.md §32)
---------------------------------------------
``tools/calibration_flag_audit.py`` found 18 constant citations where a pack
constant's ``source:`` names a dataset that the SAME pack predicts, on an axis
that dataset sweeps.  Scoring those blocks grades the model on its own answer
key.  Six of the eighteen -- the largest family -- are
``abrasive_size_exponent`` on four packs.

STATUS.md's 37th-run instruction says the repair is per-constant and is one of
two things, and that the two must be DISTINGUISHED by measurement rather than
chosen:

  (a) the ``used_for_calibration`` flag is wrong -- the block really did fit
      the constant, so it is declared and LEAVES the scored corpus, or
  (b) the constant is over-claimed -- it can be supplied from evidence that
      does NOT include this block, and then the block is legitimately scored.

Deleting the citation is explicitly forbidden: it passes the audit while
restoring the undetectable state (the §27 error class).

Why (b) is reachable for THIS family and not in general
-------------------------------------------------------
``cmp_sim/slurry/abrasive_effects.py:SIZE_EXPONENT_BY_ABRASIVE`` already
records the corpus finding that the size exponent is a property of the
ABRASIVE MATERIAL, not of the pack: between-material stdev 0.51 against
within-material 0.16 (3.2x).  A material value is therefore an average over
SEVERAL independent sweeps -- so for a material with k >= 2 sweeps, the
exponent can be re-derived with the block under test HELD OUT, and the block
becomes a genuine prediction instead of a self-grade.

That is a leave-one-out on the constant itself, and it is decisive in both
directions:

  * k >= 2  ->  a held-out exponent exists.  If the block still scores, the
    constant was over-claimed as per-pack and the block is honest evidence.
  * k == 1  ->  no held-out exponent exists.  The constant is UNIDENTIFIABLE
    without this block, which is exactly outcome (a): the flag is wrong and
    the block must leave the corpus.  No amount of re-fitting helps.

What this probe does NOT claim
------------------------------
Leave-one-out does not make the material table derived physics.  It is still a
re-attributed fitted constant (the module says so, and the hardness ordering
does not explain it).  LOO removes CIRCULARITY, not the constant.

It also cannot rescue a material whose k counts sweeps from the SAME dataset:
groups are held out by DATASET, never by group, because two size groups inside
one file share slurry, tool and lab and are not independent evidence.

METHOD
------
1. Re-fit every size sweep in the corpus from the raw dataset files with
   ``tools/size_derived_probe`` (>= 3 distinct diameters at otherwise matched
   conditions, r2 >= 0.5), labelled by abrasive material.  These are the same
   groups the material table was built from, recomputed here rather than
   copied, so a dataset edit cannot leave this probe quoting a stale number.
2. For each scored dataset that carries a size sweep, form the material's
   leave-one-out exponent: the mean over groups of the same material from
   OTHER datasets.
3. Rescore the dataset through the shipping solver with that exponent supplied
   via the ordinary ``params`` override path, and report shape and absolute
   scale before and after -- both, always (docs/limits.md: shape alone buys a
   13x-wrong rate for a better trend number).
4. Report the corpus median three ways: as published, with the self-graded
   blocks removed (the 19.5% held-out figure), and with the blocks RETURNED
   under their leave-one-out exponents.

    python tools/size_exponent_loo_probe.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core import predictive_score as ps
from tools.size_derived_probe import _abrasive, fit_power, load_size_groups

KEY = "abrasive_size_exponent"
R2_FLOOR = 0.5


def measured_groups() -> List[Dict[str, Any]]:
    """Every usable size sweep with its fitted exponent and material label."""
    out: List[Dict[str, Any]] = []
    for g in load_size_groups():
        n, r2 = fit_power(g["points"])
        if r2 < R2_FLOOR:
            continue
        out.append({"dataset": g["dataset"], "material": _abrasive(g["dataset"], g["pack"]),
                    "n": n, "r2": r2, "pack": g["pack"]})
    return out


def publication(dataset: str) -> str:
    """The PUBLICATION a dataset file came from.

    Held out by dataset alone is not enough. ``bouvet2002`` contributes three
    files (Ti, W and oxide films measured in the same runs with the same
    slurry set), so a dataset-level holdout lets that ONE paper donate an
    exponent to itself and calls it independent evidence -- the same
    non-independence that makes two size groups inside one file not count as
    two sweeps. The file-name prefix before the first underscore is the
    author-year / patent number in every file in this corpus.
    """
    return dataset.split("_", 1)[0]


def loo_exponent(groups: List[Dict[str, Any]], dataset: str, material: str,
                 by_publication: bool = True
                 ) -> Tuple[Optional[float], int, List[str]]:
    """Material exponent fitted from every OTHER source of that material.

    ``by_publication`` holds out the whole paper; False holds out only the one
    file, which is reported alongside so the difference between the two is
    visible rather than assumed.
    """
    if by_publication:
        pub = publication(dataset)
        others = [g for g in groups if g["material"] == material
                  and publication(g["dataset"]) != pub]
    else:
        others = [g for g in groups
                  if g["material"] == material and g["dataset"] != dataset]
    if not others:
        return None, 0, []
    donors = sorted({publication(g["dataset"]) if by_publication
                     else g["dataset"] for g in others})
    return statistics.fmean([g["n"] for g in others]), len(donors), donors


def _shape_and_scale(doc: Dict[str, Any], rows: List[Dict[str, Any]],
                     override: Optional[float]
                     ) -> Optional[Tuple[float, float]]:
    """(shape MAPE %, median measured/predicted) under an optional exponent."""
    measured: List[float] = []
    predicted: List[float] = []
    for row in rows:
        r = dict(row)
        if override is not None:
            ov = dict(r.get("overrides") or {})
            ov[KEY] = override
            r["overrides"] = ov
        value = ps._predict(doc, r)
        m = ps._measured(row)
        if not value or m is None:
            return None
        measured.append(m)
        predicted.append(value)
    if len(measured) < 3:
        return None
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    shape = (100.0 * sum(abs(scale * p - m) / m
                         for m, p in zip(measured, predicted)) / len(measured))
    ratios = sorted(m / p for m, p in zip(measured, predicted))
    return shape, ratios[len(ratios) // 2]


def independence_audit(groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Re-measure the between/within ratio with PUBLICATIONS as the unit.

    ``SIZE_EXPONENT_BY_ABRASIVE`` exists because the probe that built it
    measured between-material stdev 0.51 against within-material 0.16 (3.2x)
    and concluded the exponent is carried by the material. That ratio was
    computed over GROUPS. Three of the silica groups are bouvet2002 Ti, W and
    oxide -- one paper, one slurry set, one tool, three films -- so they enter
    the within-material spread three times while contributing one independent
    observation. Non-independent replicates deflate a within-group spread and
    inflate the ratio, which is the quantity the whole re-attribution rests on.

    Recomputed here with each publication collapsed to its mean first.
    """
    by_pub: Dict[Tuple[str, str], List[float]] = {}
    for g in groups:
        by_pub.setdefault((g["material"], publication(g["dataset"])), []).append(g["n"])
    by_mat: Dict[str, List[float]] = {}
    for (mat, _pub), ns in by_pub.items():
        by_mat.setdefault(mat, []).append(statistics.fmean(ns))

    def ratio(table: Dict[str, List[float]]) -> Dict[str, Any]:
        means = [statistics.fmean(v) for v in table.values()]
        within = [v - statistics.fmean(vals)
                  for vals in table.values() if len(vals) > 1 for v in vals]
        between_sd = statistics.stdev(means) if len(means) > 1 else float("nan")
        within_sd = statistics.pstdev(within) if within else float("nan")
        return {"between": between_sd, "within": within_sd,
                "ratio": between_sd / within_sd if within_sd else float("nan"),
                "materials": {m: len(v) for m, v in table.items()}}

    by_group: Dict[str, List[float]] = {}
    for g in groups:
        by_group.setdefault(g["material"], []).append(g["n"])
    return {"by_group": ratio(by_group), "by_publication": ratio(by_mat)}


DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")


def rescore() -> List[Dict[str, Any]]:
    groups = measured_groups()
    swept = sorted({g["dataset"] for g in groups})
    out: List[Dict[str, Any]] = []
    for name in swept:
        path = DATASETS / f"{name}.yaml"
        if not path.exists():
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if ps._measured(r) is not None]
        if len(rows) < 3:
            continue
        material = next(g["material"] for g in groups if g["dataset"] == name)
        loo, k_donors, donors = loo_exponent(groups, name, material)
        file_loo, k_file, _ = loo_exponent(groups, name, material,
                                           by_publication=False)
        before = _shape_and_scale(doc, rows, None)
        after = _shape_and_scale(doc, rows, loo) if loo is not None else None
        own = [g["n"] for g in groups if g["dataset"] == name]
        out.append({
            "dataset": name, "material": material, "pack": doc.get("pack"),
            "own_exponent": statistics.fmean(own),
            "loo_exponent": loo, "donor_publications": donors,
            "k_donors": k_donors,
            "file_loo_exponent": file_loo, "k_file_donors": k_file,
            "declared_holdout": not bool(doc.get("used_for_calibration")),
            "shape_before": before[0] if before else None,
            "scale_before": before[1] if before else None,
            "shape_after": after[0] if after else None,
            "scale_after": after[1] if after else None,
        })
    return out


def medians(rows: List[Dict[str, Any]], implicated: List[str]
            ) -> Dict[str, Any]:
    """Upper median (README convention) three ways."""
    shipping = {s.dataset: s.shape_mape for s in ps.score_all()
                if s.shape_mape is not None}

    def upper(vals: List[float]) -> float:
        s = sorted(vals)
        return s[len(s) // 2]

    removed = {k: v for k, v in shipping.items() if k not in implicated}
    returned = dict(shipping)
    for r in rows:
        if r["dataset"] in implicated and r["shape_after"] is not None:
            returned[r["dataset"]] = r["shape_after"]
    return {
        "published": (upper(list(shipping.values())), len(shipping)),
        "removed": (upper(list(removed.values())), len(removed)),
        "returned": (upper(list(returned.values())), len(returned)),
    }


#: The size-exponent citations the calibration audit flagged as self-graded.
#: Hard-coded here ONLY as the subject list of this probe -- the audit remains
#: the authority, and tests re-derive it rather than trusting this copy.
IMPLICATED = [
    "bouvet2002_w_silica_size_sweep",
    "bouvet2002_oxide_silica_size_sweep",
    "bouvet2002_ti_silica_size_sweep",
    "wei2026_sic_silica_size_sweep",
    "su2011_sic_alumina_size_sweep",
    "lai2001_cu_alumina_size_sweep",
    "son2021_oxide_ceria_size_sweep",
]


def main() -> int:
    rows = rescore()
    groups = measured_groups()
    print(f"size sweeps usable (r2 >= {R2_FLOOR}): "
          f"{len({r['dataset'] for r in rows})} datasets\n")
    hdr = (f"{'dataset':44s} {'material':13s} {'own n':>6s} {'LOO n':>7s} "
           f"{'k':>2s} {'shape%':>15s} {'scale x':>16s}")
    print(hdr)
    for r in sorted(rows, key=lambda r: (r["material"], r["dataset"])):
        loo = f"{r['loo_exponent']:+.2f}" if r["loo_exponent"] is not None else "  --"
        if r["shape_after"] is None:
            shape = f"{r['shape_before']:6.1f}->  UNIDENT"
            scale = f"{r['scale_before']:7.3f}->      --"
        else:
            shape = f"{r['shape_before']:6.1f}->{r['shape_after']:6.1f}"
            scale = f"{r['scale_before']:7.3f}->{r['scale_after']:7.3f}"
        flag = "*" if r["dataset"] in IMPLICATED else " "
        print(f"{flag}{r['dataset'][:43]:43s} {r['material'][:13]:13s} "
              f"{r['own_exponent']:+6.2f} {loo:>7s} {r['k_donors']:2d} "
              f"{shape:>15s} {scale:>16s}")
    print("\n* = flagged self-graded by tools/calibration_flag_audit.py")

    m = medians(rows, IMPLICATED)
    print("\nCORPUS MEDIAN -- upper median sorted(e)[n//2] (README convention)")
    for label, key in (("as published                        ", "published"),
                       ("self-graded blocks REMOVED          ", "removed"),
                       ("self-graded blocks RETURNED via LOO ", "returned")):
        value, n = m[key]
        print(f"  {label} n={n:2d}  median={value:5.2f}%")

    unident = [r["dataset"] for r in rows
               if r["dataset"] in IMPLICATED and r["loo_exponent"] is None]
    if unident:
        print("\nUNIDENTIFIABLE without the block itself -> outcome (a), the "
              "flag is wrong and the block leaves the corpus:")
        for d in unident:
            print(f"  {d}")

    audit = independence_audit(groups)
    print("\nIS THE MATERIAL SPLIT REAL, OR AN ARTEFACT OF REPLICATE COUNTING?")
    print("  the re-attribution rests on between/within >> 1; recomputed with")
    print("  each PUBLICATION collapsed to one observation first:")
    for label, key in (("groups as the unit (as published)", "by_group"),
                       ("publications as the unit        ", "by_publication")):
        a = audit[key]
        mats = ", ".join(f"{m}:k={k}" for m, k in sorted(a["materials"].items()))
        print(f"  {label}  between={a['between']:.2f} within={a['within']:.2f}"
              f"  ratio={a['ratio']:.1f}x   [{mats}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
