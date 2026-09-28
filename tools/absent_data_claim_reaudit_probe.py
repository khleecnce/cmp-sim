"""§51's cheaper audit, run once: is an exit condition that asserts the ABSENCE
of data still true, when you EXECUTE its enumeration instead of quoting it?

WHY THIS PROBE EXISTS
---------------------
§51 found that `cu_h2o2_bta.oxidizer_ph_window`'s exit condition ("no alkaline
Cu/H2O2/BTA sweep has been located") was false when written: two such ladders
were already scored members of this corpus, under a different pack.  The
general rule it produced is that such a sentence is itself a MEASUREMENT and
expires, because the corpus grows and the sentence does not.

The next sentence of the same family sits in §49:

    "both packs' corpora sweep the oxidizer at one level or not at all, so the
     experiment needed is a >=3-level oxidizer sweep on those chemistries"

about `cu_alkaline_benzenesulfonic` and `w_fe_oxidizer`, the two packs that
declare `oxidizer_peak_wt_pct` but no `oxidizer_peak_shape_K`, leaving the
declared peak position dead (§49 measured 0.000% response on both).

WHAT THIS MEASURES
------------------
Q1  ENUMERATE, do not quote.  For each of the two packs, list every scored
    dataset and count the DISTINCT oxidiser levels it sweeps.

Q2  If a >=3-level sweep exists, the stated experiment is no longer missing --
    but "the sweep exists" is not "the constant can be anchored" (§32/§34/§51).
    A peak SHAPE constant needs a ladder that BRACKETS an interior maximum: a
    monotone ladder locates no peak at any K, so it cannot anchor one.  Check
    each ladder for an interior maximum.

Q3  Report admissibility separately from shape: `used_for_calibration` (a
    self-scored ladder cannot supply a held-out constant) and whether the
    oxidiser axis is confounded with pH inside the same ladder.

The three answers are deliberately separate: Q1 can falsify the SENTENCE while
Q2 leaves the DECISION standing, which is exactly what §51 found and is the
outcome this probe must be able to express.

Run:  .venv/bin/python tools/absent_data_claim_reaudit_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core.params import load_pack  # noqa: E402

DATASETS = ROOT / "cmp_sim" / "data" / "validation" / "datasets"

# The two packs §49 measured as declaring a peak POSITION that reaches nothing,
# because the branch selecting it is chosen by a key (`oxidizer_peak_shape_K`)
# that only one other pack declares.
SUBJECT_PACKS = ("cu_alkaline_benzenesulfonic", "w_fe_oxidizer")
POSITION_KEY = "oxidizer_peak_wt_pct"
SHAPE_KEY = "oxidizer_peak_shape_K"

MIN_LEVELS = 3   # the sentence's own threshold


def ladders_for(pack_name: str):
    out = []
    for path in sorted(DATASETS.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text())
        except Exception:
            continue
        if not isinstance(doc, dict) or doc.get("pack") != pack_name:
            continue
        rows = []
        for c in doc.get("conditions") or []:
            ov = (c or {}).get("overrides") or {}
            if "oxidizer_wt_pct" not in ov or c.get("mrr_nm_per_min") is None:
                continue
            rows.append((float(ov["oxidizer_wt_pct"]),
                         float(c["mrr_nm_per_min"]),
                         ov.get("slurry_ph")))
        if not rows:
            continue
        rows.sort()
        levels = sorted({ox for ox, _, _ in rows})
        # collapse replicates at one level to their mean before asking about
        # shape -- otherwise scatter inside a level reads as curvature
        by_level = {}
        for ox, r, _ in rows:
            by_level.setdefault(ox, []).append(r)
        means = [sum(by_level[v]) / len(by_level[v]) for v in levels]
        phs = [ph for _, _, ph in rows if ph is not None]
        out.append({
            "name": path.stem,
            "levels": levels,
            "means": means,
            "calib": bool(doc.get("used_for_calibration")),
            "ph_span": (min(phs), max(phs)) if phs else None,
        })
    return out


def interior_max(means) -> bool:
    """A peak SHAPE constant is anchorable only by a ladder whose maximum is
    strictly inside its own range. A monotone ladder locates no peak at any K."""
    if len(means) < 3:
        return False
    i = means.index(max(means))
    return 0 < i < len(means) - 1


def main() -> int:
    print("§49's exit condition, RE-RUN rather than re-read (limits §51's rule):")
    print('  "both packs\' corpora sweep the oxidizer at one level or not at '
          'all, so the')
    print('   experiment needed is a >=3-level oxidizer sweep on those '
          'chemistries"')
    print()

    any_multi = False
    any_anchor = False
    for pack_name in SUBJECT_PACKS:
        pack = load_pack(pack_name)
        pos = pack.params.get(POSITION_KEY)
        shape = pack.params.get(SHAPE_KEY)
        print(f"── {pack_name}")
        print(f"   declares {POSITION_KEY}="
              f"{getattr(pos, 'value', None)}  "
              f"{SHAPE_KEY}={getattr(shape, 'value', None)}")
        rows = ladders_for(pack_name)
        if not rows:
            print("   no scored dataset sweeps the oxidiser at all")
            print()
            continue
        for r in rows:
            n = len(r["levels"])
            multi = n >= MIN_LEVELS
            any_multi |= multi
            shape_ok = interior_max(r["means"]) if multi else False
            conf = ""
            if r["ph_span"] and r["ph_span"][1] - r["ph_span"][0] > 0.3:
                conf = f"  pH CONFOUNDED {r['ph_span'][0]:g}-{r['ph_span'][1]:g}"
            lv = ",".join(f"{v:g}" for v in r["levels"])
            print(f"   {r['name']:<42} levels={n} [{lv}]"
                  f"{'  calib' if r['calib'] else ''}{conf}")
            if multi:
                trend = " -> ".join(f"{m:g}" for m in r["means"])
                print(f"       means {trend}")
                print(f"       interior maximum: "
                      f"{'YES -- can anchor a peak shape' if shape_ok else 'NO -- monotone, locates no peak at any K'}")
                if shape_ok and not r["calib"]:
                    any_anchor = True
        print()

    print("VERDICT")
    if any_multi:
        print(f"  Q1 the SENTENCE is FALSE: >= {MIN_LEVELS}-level oxidiser "
              "sweeps on these chemistries already exist in the scored corpus.")
    else:
        print("  Q1 the sentence still holds: no multi-level sweep found.")
    if any_anchor:
        print("  Q2 the DECISION has ALSO fallen: a held-out ladder brackets an "
              f"interior maximum, so {SHAPE_KEY} can be anchored. Do it.")
    else:
        print(f"  Q2 the DECISION STANDS, for a STRONGER reason than absence: "
              f"the data exist and are MONOTONE. A monotone ladder locates no "
              f"peak at any {SHAPE_KEY}, so it cannot anchor a peak shape. "
              "'We have no data' becomes 'the data we have refuse to place a "
              "peak' -- a measured statement, not a gap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
