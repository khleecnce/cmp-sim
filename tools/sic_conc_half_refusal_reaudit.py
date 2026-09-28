r"""Does the `abrasive_conc_half_wt_pct` refusal on `sic_ceria_h2o2` still hold?

WHY THIS PROBE EXISTS
---------------------
`cmp_sim/data/params/sic_ceria_h2o2.yaml` declares `abrasive_conc_half_wt_pct:
null` and justifies it with a MEASUREMENT, stated in the note:

    "Six iso-condition series give exponents of -0.40, -0.28, +0.01, +0.44,
     +0.49 and +1.43. Two of them fall with loading, which no saturating form
     can produce: Entegris US 2022/0315802 A1 measures 966.7 -> 200 A/min as
     alumina goes 0.1 -> 5 wt% ..."

`docs/limits.md` §52 established that a refusal resting on an ENUMERATION is a
measurement that EXPIRES, and must be re-RUN rather than re-read.  There is a
specific reason to suspect this one: the SIBLING constant on the SAME axis of
the SAME pack (`abrasive_conc_exponent`) was corrected by ruling #52 for
exactly this cause -- its value came from Entegris US20220315802A1, that
dataset LEFT this pack for `sic_alumina_kmno4` under ruling #49-B, and the
constant stayed behind as an orphan.  The sign was flipped -0.406 -> +0.227.

The C_half refusal cites the SAME departed Entegris rows as its decisive
counter-example.  So the question is whether the refusal is a second orphan.

WHAT IS MEASURED (nothing is wired; no pack is modified)
--------------------------------------------------------
Every iso-condition abrasive-loading ladder in the corpus is enumerated from
the datasets themselves, tagged with the pack that predicts it and with the
abrasive the DATASET declares (not the pack -- §27: the pack is not the
abrasive), and its log-log slope is reported.  The refusal is then re-read
against only those ladders that are actually this pack's material system.

This probe NEVER writes.  A per-block C_half would be one fitted constant per
dataset, which the project forbids (`docs/limits.md` §33).

Run:  .venv/bin/python tools/sic_conc_half_refusal_reaudit.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import Any, Dict, List, Optional, Tuple  # noqa: E402

import yaml  # noqa: E402

from cmp_sim.core.validation import dataset_paths  # noqa: E402

#: The pack whose refusal is under audit.
PACK = "sic_ceria_h2o2"

#: Keys naming the abrasive loading.
CONC_ALIASES = ("abrasive_wt_pct", "abrasive_conc_wt_pct")

#: A ladder needs at least this many distinct loading levels to carry a slope.
MIN_LEVELS = 3


def _rate(row: Dict[str, Any]) -> Optional[float]:
    v = row.get("mrr_nm_per_min")
    if v is not None:
        return float(v)
    v = row.get("mrr_A_per_min")
    return None if v is None else float(v) / 10.0


def _iso_conc_ladder(rows: List[Dict[str, Any]]
                     ) -> Optional[Tuple[List[float], List[float]]]:
    """Rows where loading is the ONLY thing that varies.

    Everything else divides out of the scorer's single free multiplicative
    scale, so the ladder's slope is a property of the data alone.
    """
    varying = set()
    for key in {k for r in rows for k in (r.get("overrides") or {})}:
        if len({(r.get("overrides") or {}).get(key) for r in rows}) > 1:
            varying.add(key)
    for key in ("pressure_psi", "rpm_platen", "rpm_wafer", "temperature_c"):
        if len({r.get(key) for r in rows}) > 1:
            varying.add(key)
    if not varying or not varying <= set(CONC_ALIASES):
        return None
    pts: List[Tuple[float, float]] = []
    for row in rows:
        ov = row.get("overrides") or {}
        c = next((ov[k] for k in CONC_ALIASES if k in ov), None)
        r = _rate(row)
        if c is None or r is None or float(c) <= 0:
            continue
        pts.append((float(c), r))
    by: Dict[float, List[float]] = {}
    for c, r in pts:
        by.setdefault(c, []).append(r)
    if len(by) < MIN_LEVELS:
        return None
    levels = sorted(by)
    return levels, [sum(by[c]) / len(by[c]) for c in levels]


def _loglog_slope(levels: List[float], means: List[float]) -> float:
    xs = [math.log(c) for c in levels]
    ys = [math.log(m) for m in means]
    xb = sum(xs) / len(xs)
    yb = sum(ys) / len(ys)
    den = sum((x - xb) ** 2 for x in xs)
    return sum((x - xb) * (y - yb) for x, y in zip(xs, ys)) / den


def ladders() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        rows = doc.get("conditions") or []
        got = _iso_conc_ladder(rows)
        if got is None:
            continue
        levels, means = got
        # §27: the pack is not the abrasive. Read the abrasive the DATASET
        # declares; fall back to None (unknown) rather than to the pack's.
        abrasive = doc.get("abrasive")
        out.append({
            "dataset": path.stem,
            "pack": str(doc.get("pack") or ""),
            "abrasive": None if abrasive is None else str(abrasive),
            "levels": levels,
            "means": means,
            "slope": _loglog_slope(levels, means),
            "held_out": not bool(doc.get("used_for_calibration")),
            "scope_note": str(doc.get("scope_note") or ""),
        })
    return out


def main() -> int:
    rows = ladders()
    if not rows:
        print("NO iso-condition loading ladder found in the corpus -- this "
              "probe has no subject, which is indistinguishable from a "
              "deleted check. Investigate.")
        return 1

    print(f"iso-condition abrasive-loading ladders in the corpus: {len(rows)}\n")
    print(f"  {'dataset':<52} {'pack':<20} {'slope':>7} {'lvls':>5}  held-out")
    for r in sorted(rows, key=lambda x: x["slope"]):
        print(f"  {r['dataset']:<52} {r['pack']:<20} {r['slope']:>+7.3f} "
              f"{len(r['levels']):>5}  {'yes' if r['held_out'] else 'NO'}")

    mine = [r for r in rows if r["pack"] == PACK]
    print(f"\n── ladders predicted by {PACK} ──")
    if not mine:
        print("  none.")
    for r in mine:
        print(f"  {r['dataset']:<52} slope {r['slope']:+.3f}  "
              f"{'held-out' if r['held_out'] else 'CALIBRATION'}")

    neg = [r for r in mine if r["slope"] < 0]
    print(f"\n  falling ladders under this pack: {len(neg)}")
    for r in neg:
        print(f"    {r['dataset']:<52} slope {r['slope']:+.3f}")

    print("\n── reading ──")
    print("  The refusal's decisive counter-example (Entegris US20220315802A1,")
    print("  966.7 -> 200 A/min for alumina 0.1 -> 5 wt%) is checked here by")
    print("  asking which pack predicts it NOW. If it no longer belongs to")
    print(f"  {PACK}, the refusal is an orphan of the same kind ruling #52")
    print("  corrected for abrasive_conc_exponent -- the evidence moved pack")
    print("  and the constant stayed behind.")
    print("\n  A dissolved contradiction is NOT a licence to fit C_half: the")
    print("  only loading ladders left under this pack must still be able to")
    print("  ANCHOR it without scoring the model on its own answer key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
