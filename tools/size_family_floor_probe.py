r"""What does the MONOTONE power-law family cost on the corpus's size sweeps?

WHY THIS PROBE EXISTS
---------------------
`docs/limits.md` §53 measured the packs' declared three-parameter peaked size
curves and found all twelve constants inert AND refuted, and it priced the
declared curve against the shipping pooled exponent (pooled won 8/8). That
priced ONE alternative. It did not answer the question the finding opened:

    the shipping size term is a SINGLE POWER LAW, which is monotone by
    construction, and at least three sweeps in this corpus are NOT monotone.
    How much does that functional family cost, and where?

This matters because the two possible answers point opposite ways:

  * if a non-monotone sweep's error survives even the BEST single exponent,
    the family is binding there and the physical cause of the size residual
    (agglomeration, PSD tail, size-dependent chemistry) is worth hunting;
  * if the best exponent already fits the non-monotone sweeps about as well as
    it fits the monotone ones, the non-monotonicity is small against the
    block's own error and the size axis can be CLOSED -- the error lives
    elsewhere and no size-curve work will move the median.

WHAT IS MEASURED (nothing is wired; no pack is modified)
--------------------------------------------------------
For every PURE size sweep (size is the only varying axis, so every other
factor in the product is identical across rows and divides out of the single
free multiplicative scale the shipping scorer fits):

  shipping    shape MAPE under the pack's shipping pooled exponent
  floor       shape MAPE under the BEST single exponent for that block,
              found by scanning n. This is a LOWER BOUND on what any monotone
              power law can achieve here, and it is IN-SAMPLE by construction
              (one free parameter fitted on the block being scored) -- so it
              can only FLATTER the family. A family floor that is still large
              is therefore a strong statement; a small one is not evidence the
              family is right, only that it is not what is costing.
  n_best      the exponent achieving that floor (reported, never adopted:
              adopting a per-block exponent is fitting one constant per
              dataset, which the project forbids -- and `docs/limits.md` §33
              already refused exactly that repair for this constant family)
  flat        shape MAPE at n = 0, i.e. ONE CONSTANT for the whole block.
              THIS COLUMN IS LOAD-BEARING. A floor is small either because
              the family fits or because the block barely varies, and those
              are opposite conclusions. `explained` = (flat - floor)/flat is
              the share of the block's spread the best monotone power law
              accounts for; at `explained ~ 0` the floor is the flat baseline
              wearing an exponent and says nothing about the family at all.

Blocks are split by whether their own measured level means are MONOTONE.

CONTROLS (§43: a probe with no control decays into "nothing matters")
---------------------------------------------------------------------
`controls()` runs the same reduction on two synthetic blocks whose answers are
known by construction: an exact power law (floor must reach ~0 and `explained`
must be high) and a sharply peaked series (floor must stay LARGE -- if the
reduction cannot see family cost where family cost is certain, a small
difference on the corpus is a probe failure, not a finding).

Run:  .venv/bin/python tools/size_family_floor_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import statistics  # noqa: E402
from typing import Any, Dict, List, Optional, Tuple  # noqa: E402

import yaml  # noqa: E402

from cmp_sim.core.params import load_pack                 # noqa: E402
from cmp_sim.core.validation import dataset_paths         # noqa: E402

#: Keys naming the particle size (same list the §53 probe uses).
SIZE_ALIASES = ("abrasive_size_nm", "abrasive_d50_nm", "abrasive_d99_nm")

#: Exponent scan for the family floor. Wide enough to contain every exponent
#: any pack declares (and then some), fine enough that the floor is not a
#: property of the grid.
N_LO, N_HI, N_STEP = -3.0, 3.0, 0.01

#: A block counts as non-monotone only if its interior deviation is larger
#: than this fraction of its own span. §40's lesson: a 0.5% step between two
#: adjacent levels is noise, not a shape. Derived from the corpus's own
#: replicate scatter where available, and stated explicitly otherwise.
NONMONOTONE_MIN_DEPTH = 0.05


def _rows_size_levels(doc: Dict[str, Any]) -> Optional[Tuple[List[float],
                                                             List[float]]]:
    rows = doc.get("conditions") or []
    pts: List[Tuple[float, float]] = []
    for row in rows:
        ov = row.get("overrides") or {}
        d = ov.get("abrasive_size_nm", ov.get("abrasive_d50_nm"))
        rate = row.get("mrr_nm_per_min")
        if rate is None:
            rate = row.get("mrr_A_per_min")
            rate = None if rate is None else float(rate) / 10.0
        if d is None or rate is None:
            continue
        pts.append((float(d), float(rate)))
    if len(pts) < 3:
        return None
    by_level: Dict[float, List[float]] = {}
    for d, r in pts:
        by_level.setdefault(d, []).append(r)
    if len(by_level) < 3:
        return None
    levels = sorted(by_level)
    means = [sum(by_level[d]) / len(by_level[d]) for d in levels]
    return levels, means


def _varies_only_size(rows: List[Dict[str, Any]]) -> bool:
    varying: set = set()
    for key in {k for r in rows for k in (r.get("overrides") or {})}:
        vals = {(r.get("overrides") or {}).get(key) for r in rows}
        if len(vals) > 1:
            varying.add(key)
    for key in ("pressure_psi", "rpm_platen", "rpm_wafer", "temperature_c"):
        if len({r.get(key) for r in rows}) > 1:
            varying.add(key)
    return bool(varying) and varying <= set(SIZE_ALIASES)


def _mape(pairs: List[Tuple[float, float]]) -> float:
    return 100.0 * sum(abs(p - m) / m for m, p in pairs) / len(pairs)


def _shape_mape(levels: List[float], measured: List[float], n: float) -> float:
    """Shape MAPE of `d**n` with ONE free scale, fitted exactly as
    `core.predictive_score.score_dataset` fits it. The algebra is copied from
    there so this probe and the scorer cannot drift apart."""
    pred = [d ** n for d in levels]
    scale = (sum(m * p for m, p in zip(measured, pred))
             / sum(p * p for p in pred))
    return _mape([(m, scale * p) for m, p in zip(measured, pred)])


def _family_floor(levels: List[float],
                  measured: List[float]) -> Tuple[float, float]:
    best_e, best_n = None, None
    n = N_LO
    while n <= N_HI + 1e-9:
        e = _shape_mape(levels, measured, n)
        if best_e is None or e < best_e:
            best_e, best_n = e, n
        n += N_STEP
    return float(best_e), float(best_n)


def _nonmonotone_depth(means: List[float]) -> float:
    """How far the series departs from monotonicity, as a fraction of its span.

    Zero for any monotone series. For a series with an interior extremum it is
    the size of the reversal relative to (max - min), so a rounding-level
    wobble cannot be reported as a shape (§40).
    """
    span = max(means) - min(means)
    if span <= 0:
        return 0.0
    up = sum(max(0.0, b - a) for a, b in zip(means, means[1:]))
    down = sum(max(0.0, a - b) for a, b in zip(means, means[1:]))
    # A monotone series has exactly one of these zero; the smaller one is the
    # material that has to reverse direction.
    return min(up, down) / span


def _analyse(levels: List[float], means: List[float]) -> Dict[str, float]:
    floor, n_best = _family_floor(levels, means)
    flat = _shape_mape(levels, means, 0.0)
    explained = 0.0 if flat <= 0 else (flat - floor) / flat
    return {"floor_pct": floor, "n_best": n_best, "flat_pct": flat,
            "explained": explained,
            "depth": _nonmonotone_depth(means)}


#: Synthetic blocks whose verdict is known by construction. `min_explained`
#: and `min_floor_pct` are the assertions; a probe that fails them is reporting
#: its own reduction, not the corpus.
CONTROLS = (
    # An exact power law: the family CONTAINS this block, so the floor must
    # collapse to ~0 and the exponent must explain essentially all of the
    # spread. If this fails the scan or the scale fit is broken.
    {"name": "synthetic exact power law d^0.9",
     "levels": [20.0, 50.0, 100.0, 200.0],
     "means": [d ** 0.9 for d in (20.0, 50.0, 100.0, 200.0)],
     "min_explained": 0.95, "max_floor_pct": 0.5, "min_floor_pct": None},
    # A sharp interior peak with a large reversal relative to the span. No
    # monotone power law can follow it, so the floor MUST stay large. This is
    # the control that makes a small corpus difference meaningful.
    {"name": "synthetic sharp peak at 50 nm",
     "levels": [20.0, 50.0, 100.0, 200.0],
     "means": [100.0, 400.0, 110.0, 90.0],
     "min_explained": None, "max_floor_pct": None, "min_floor_pct": 20.0},
)


def controls() -> List[Dict[str, Any]]:
    out = []
    for c in CONTROLS:
        res = _analyse(list(c["levels"]), list(c["means"]))
        ok = True
        if c["min_explained"] is not None and res["explained"] < c["min_explained"]:
            ok = False
        if c["max_floor_pct"] is not None and res["floor_pct"] > c["max_floor_pct"]:
            ok = False
        if c["min_floor_pct"] is not None and res["floor_pct"] < c["min_floor_pct"]:
            ok = False
        out.append({"name": c["name"], "passed": ok, **res})
    return out


def measure() -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text()) or {}
        except Exception:
            continue
        got = _rows_size_levels(doc)
        if got is None:
            continue
        levels, means = got
        if not _varies_only_size(doc.get("conditions") or []):
            continue
        pack_name = str(doc.get("pack") or "")
        try:
            pack = load_pack(pack_name)
        except Exception:
            continue
        n_param = pack.params.get("abrasive_size_exponent")
        if n_param is None or n_param.value is None:
            continue
        shipping = _shape_mape(levels, means, float(n_param.value))
        res = _analyse(levels, means)
        blocks.append({
            "dataset": path.stem,
            "pack": pack_name,
            "levels": levels,
            "means": [round(m, 2) for m in means],
            "n_shipping": float(n_param.value),
            "shipping_pct": shipping,
            "nonmonotone": res["depth"] >= NONMONOTONE_MIN_DEPTH,
            "held_out": not bool(doc.get("used_for_calibration")),
            **res,
        })
    return blocks


def main() -> int:
    print("── instrument controls (synthetic; verdict known by construction) ──")
    ctl = controls()
    for c in ctl:
        print(f"  {c['name']:<36} floor {c['floor_pct']:>6.2f}%  "
              f"explained {c['explained']:>5.2f}  "
              f"{'PASS' if c['passed'] else 'FAIL'}")
    if not all(c["passed"] for c in ctl):
        print("  ⚠ A CONTROL FAILED — every number below is the probe's own "
              "reduction speaking, not the corpus. Do not quote them.")

    blocks = measure()
    if not blocks:
        print("NO pure size sweep found — this probe has no subject, which is "
              "indistinguishable from a deleted check. Investigate.")
        return 1

    print("\nPURE size sweeps (size is the only varying axis)\n")
    print(f"  {'dataset':<44} {'n_ship':>7} {'shipping':>9} {'floor':>8} "
          f"{'flat':>8} {'expl':>5} {'n_best':>7} {'rev':>6} {'class':>14}")
    for b in sorted(blocks, key=lambda x: -x["depth"]):
        print(f"  {b['dataset']:<44} {b['n_shipping']:>7.3f} "
              f"{b['shipping_pct']:>8.2f}% {b['floor_pct']:>7.2f}% "
              f"{b['flat_pct']:>7.2f}% {b['explained']:>5.2f} "
              f"{b['n_best']:>7.2f} {b['depth']:>6.3f} "
              f"{'NON-MONOTONE' if b['nonmonotone'] else 'monotone':>14}")

    nm = [b for b in blocks if b["nonmonotone"]]
    mo = [b for b in blocks if not b["nonmonotone"]]
    print(f"\n  non-monotone: {len(nm)}   monotone: {len(mo)}"
          f"   (reversal bar {NONMONOTONE_MIN_DEPTH} of span)")

    def _med(xs):
        return statistics.median(xs) if xs else float("nan")

    print("\n── the question: what does the MONOTONE FAMILY cost? ──")
    print("  'floor' is the best single exponent FITTED ON THE BLOCK ITSELF, "
          "so it is\n  in-sample and can only flatter the family. A floor that "
          "is still large is\n  therefore a strong statement; a small floor is "
          "not evidence the family is\n  right, only that it is not what is "
          "costing.")
    for label, group in (("non-monotone", nm), ("monotone", mo)):
        if not group:
            continue
        print(f"\n  {label}: median floor "
              f"{_med([b['floor_pct'] for b in group]):.2f}%   "
              f"median shipping {_med([b['shipping_pct'] for b in group]):.2f}%")
        for b in group:
            gap = b["shipping_pct"] - b["floor_pct"]
            print(f"    {b['dataset']:<44} floor {b['floor_pct']:>6.2f}%  "
                  f"exponent-repair worth {gap:>6.2f} pp  "
                  f"{'(held-out)' if b['held_out'] else '(CALIBRATION)'}")

    print("\n── reading ──")
    if nm:
        nm_floor = _med([b["floor_pct"] for b in nm])
        mo_floor = _med([b["floor_pct"] for b in mo]) if mo else 0.0
        print(f"  family floor, non-monotone {nm_floor:.2f}% vs monotone "
              f"{mo_floor:.2f}%")
        print("  The difference is what the monotone FAMILY costs; the "
              "'exponent-repair'\n  column is what a better CONSTANT inside "
              "the same family would buy. Those\n  are different purchases and "
              "only the second is available without new\n  physics.")
        blind = [b for b in blocks if b["explained"] < 0.10]
        if blind:
            print(f"\n  ⚠ {len(blind)} block(s) have explained < 0.10: the best "
                  "exponent barely beats a\n    single constant, so their floor "
                  "is the FLAT baseline wearing an exponent\n    and carries no "
                  "verdict about the family:")
            for b in blind:
                print(f"      {b['dataset']:<44} flat {b['flat_pct']:.2f}% -> "
                      f"floor {b['floor_pct']:.2f}% (explained "
                      f"{b['explained']:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
