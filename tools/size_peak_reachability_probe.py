r"""Are the packs' DECLARED peaked particle-size curves reachable, and would
wiring them help?

WHY THIS PROBE EXISTS
---------------------
`docs/limits.md` §49 established that reachability is a **(key, pack)**
property and found two oxidiser peak positions that move nothing on their own
packs. It asked that question of ONE key family. This asks it of the other
peaked family in this repository, and the answer is larger: **four packs
declare a three-parameter peaked particle-size curve, twelve constants, every
one of them graded `literature` with a primary citation, and none of them
reaches the rate.**

    abrasive_size_peak_nm
    abrasive_size_exp_below_peak
    abrasive_size_exp_above_peak

The cause is the §49 cause with the layers swapped. The peaked curve is
implemented in the INHERITED layer (`legacy/sim/factors.py`, the piecewise
branch anchored at `peak**exp_below` so the two legs join continuously), but the
shipping solver's size factor is computed in `cmp_sim/models/luo_dornfeld.py`,
which applies a SINGLE pooled exponent `n_d` per abrasive family and never
consults a peak. So the packs' curve is not overridden by a better number -- it
is not evaluated at all, while the model asserts a **monotone** size dependence
of the opposite functional family.

WHAT THIS MEASURES (nothing is fitted; no pack is modified)
-----------------------------------------------------------
  Q1  For every pack declaring the triple: does perturbing each of the three
      constants move the predicted rate?  Swept SMALL-FIRST and in BOTH
      directions (§43: a large one-sided factor can leave a term's validity
      window and manufacture silence).

  Q2  INSTRUMENT CONTROL, per pack (§43). Perturb `abrasive_size_nm` itself --
      the driver the three constants are supposed to shape. If the driver does
      not move the rate either, the pack's whole row is a probe failure rather
      than a wiring fact.  The base run is displaced OFF `abrasive_ref_size_nm`
      first, because at `d == d_ref` every size factor is 1.0 by the
      normalisation contract and no exponent can be reachable there.

  Q3  Is the declared peak position TRANSFERABLE?  The corpus is asked, not the
      notes: every size sweep is located and its own measured optimum is read
      off the MEASUREMENTS.

  Q4  PRICE THE REPAIR.  For every pure size sweep -- one where the size is the
      only axis the dataset varies, so any condition-independent factor divides
      out of the single free scale the shape metric fits -- compute the shape
      MAPE under the shipping pooled exponent and under the pack's own declared
      piecewise curve.  Wiring a declared constant is only progress if the
      constant predicts better than what it would replace, and that is a
      measurement, not an argument about provenance.

Q3 and Q4 are the load-bearing ones. §49's refusal to transplant an oxidiser
peak rested on a function-family argument; here the corpus answers a cruder
question first, and a peak position contradicted by an independent
same-abrasive/same-film sweep is not a pack constant no matter how it is wired.

Run:  .venv/bin/python tools/size_peak_reachability_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import Any, Dict, List, Optional, Tuple  # noqa: E402

import yaml  # noqa: E402

from cmp_sim.api import run_recipe                        # noqa: E402
from cmp_sim.core.params import load_pack                 # noqa: E402
from cmp_sim.core.predictive_score import PACK_FILM       # noqa: E402
from cmp_sim.core.validation import dataset_paths         # noqa: E402

PEAK_KEYS = ("abrasive_size_peak_nm",
             "abrasive_size_exp_below_peak",
             "abrasive_size_exp_above_peak")

#: Small first, both directions (§43). A key is unreachable only when NO
#: admissible perturbation moves the rate.
FACTORS = (1.05, 0.95, 1.25, 0.8, 1.5, 0.67, 2.0, 0.5)

#: The response, in percent of the base rate, below which a key is inert. Same
#: bar `tools/inert_axis_scan.py` uses, so the two tools cannot disagree.
INERT_TOLERANCE = 0.5

#: How far the base run is displaced off `abrasive_ref_size_nm`. At d == d_ref
#: the size factor is exactly 1.0 for EVERY exponent, so measuring there would
#: report the normalisation contract as inertness (the trap of §43/§42).
SIZE_DISPLACEMENT = 1.7


def _run(pack: str, film: str, overrides: Optional[Dict[str, Any]] = None):
    recipe: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0, "flow_ml_min": 200.0},
    }
    if overrides:
        recipe["params"] = dict(overrides)
    return run_recipe(recipe)


def _rate(res) -> Optional[float]:
    v = res.get("removal_rate_A_per_min")
    return None if not v else float(v)


def _packs_declaring_triple() -> Dict[str, Tuple[Any, str]]:
    out = {}
    for name, film in PACK_FILM.items():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        if all((pack.params.get(k) is not None
                and pack.params[k].value is not None) for k in PEAK_KEYS):
            out[name] = (pack, film)
    return out


def _corpus_size_optima() -> List[Dict[str, Any]]:
    """Every dataset that varies particle size, with its own measured optimum.

    Read from the MEASUREMENTS, not from the dataset's prose: a note can go
    stale against its own rows (limits §40), and the question here is where the
    data put the maximum.
    """
    found: List[Dict[str, Any]] = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text()) or {}
        except Exception:
            continue
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
            continue
        # One size level can carry several rows (other axes vary). Average per
        # level so a co-varying axis cannot masquerade as a size optimum.
        by_level: Dict[float, List[float]] = {}
        for d, r in pts:
            by_level.setdefault(d, []).append(r)
        if len(by_level) < 3:
            continue
        levels = sorted(by_level)
        means = [sum(by_level[d]) / len(by_level[d]) for d in levels]
        best = max(range(len(levels)), key=lambda i: means[i])
        interior = 0 < best < len(levels) - 1
        found.append({
            "dataset": path.stem,
            "pack": str(doc.get("pack") or ""),
            "levels_nm": levels,
            "rates": [round(m, 2) for m in means],
            "argmax_nm": levels[best],
            "interior_maximum": interior,
            "pure_size_sweep": _varies_only_size(rows),
        })
    return found


#: Keys that name the particle size. A dataset that varies ONLY these is a pure
#: size sweep, so every other factor in the product is the same for every row
#: and divides out of the single free scale the shape metric fits.
SIZE_ALIASES = ("abrasive_size_nm", "abrasive_d50_nm", "abrasive_d99_nm")


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


def _shape_mape(levels: List[float], measured: List[float],
                curve) -> Optional[float]:
    """Shape MAPE of a size-factor curve, with ONE free scale fitted exactly as
    `core.predictive_score.score_dataset` fits it (least squares in the ratio
    sense). Reimplementing the metric would let this probe and the scorer drift,
    so the algebra is copied verbatim from there and nothing else is refitted.
    """
    pred = [curve(d) for d in levels]
    if any(p is None or p <= 0 for p in pred):
        return None
    scale = (sum(m * p for m, p in zip(measured, pred))
             / sum(p * p for p in pred))
    return _mape([(m, scale * p) for m, p in zip(measured, pred)])


def _piecewise(peak: float, below: float, above: float):
    """The pack's declared curve, anchored so the two legs join continuously --
    the same form `legacy/sim/factors.py` implements. Duplicating it here is
    deliberate: the point is to price a curve the shipping solver never calls.
    """
    def curve(d: float) -> float:
        if d <= peak:
            return d ** below
        return (peak ** below) * (d / peak) ** above
    return curve


def _power(n: float):
    def curve(d: float) -> float:
        return d ** n
    return curve


def main() -> int:
    packs = _packs_declaring_triple()
    print(f"packs declaring the peaked size triple: {sorted(packs)}")
    if not packs:
        print("NOTHING DECLARES THE TRIPLE — this probe has no subject, which "
              "is indistinguishable from a deleted check. Investigate.")
        return 1

    reached: List[str] = []
    inert: List[str] = []
    control_failures: List[str] = []

    for name, (pack, film) in sorted(packs.items()):
        d = pack.params.get("abrasive_size_nm")
        d_ref = pack.params.get("abrasive_ref_size_nm")
        if d is None or d.value is None:
            print(f"\n=== {name}: no abrasive_size_nm — cannot displace; skipped")
            continue
        ref = float((d_ref.value if d_ref is not None and d_ref.value else d.value))
        query = ref * SIZE_DISPLACEMENT
        base_ov = {"abrasive_size_nm": query}

        print(f"\n=== {name} ({film})")
        print(f"    displaced base: abrasive_size_nm = {query:g} nm "
              f"(ref {ref:g} nm x{SIZE_DISPLACEMENT}) — at d == d_ref every "
              f"size factor is 1.0 for every exponent")
        base = _rate(_run(name, film, base_ov))
        if base is None:
            print("    base run produced no rate — skipping")
            continue
        print(f"    base rate = {base:.4f} A/min")

        for key in PEAK_KEYS:
            val = float(pack.params[key].value)
            conf = getattr(pack.params[key], "confidence", "?")
            best, best_f = 0.0, None
            for f in FACTORS:
                ov = dict(base_ov)
                ov[key] = val * f
                r = _rate(_run(name, film, ov))
                if r is None:
                    continue
                dev = abs(r - base) / base * 100.0
                if dev > best:
                    best, best_f = dev, f
            tag = "REACHED" if best >= INERT_TOLERANCE else "INERT"
            (reached if tag == "REACHED" else inert).append(f"{name}.{key}")
            print(f"    {key:<32} = {val:<14g} [{conf:<10}] "
                  f"max|d rate| = {best:.6f}% over {len(FACTORS)} "
                  f"perturbations ({min(FACTORS)}x..{max(FACTORS)}x)"
                  + (f" at x{best_f}" if best_f else "") + f"  -> {tag}")

        # Q2 — instrument control: the DRIVER the three constants shape.
        moved = 0.0
        for f in (1.25, 0.8, 2.0, 0.5):
            r = _rate(_run(name, film, {"abrasive_size_nm": query * f}))
            if r is not None:
                moved = max(moved, abs(r - base) / base * 100.0)
        if moved < INERT_TOLERANCE:
            control_failures.append(name)
            print(f"    Q2 CONTROL FAILED — abrasive_size_nm itself moves only "
                  f"{moved:.4f}%. This pack's row is a probe failure, not a "
                  f"wiring fact.")
        else:
            print(f"    Q2 control: abrasive_size_nm moves the rate "
                  f"{moved:.3f}% — the probe CAN see this axis")

    print("\n── Q3: where does the CORPUS put the size optimum? ──")
    optima = _corpus_size_optima()
    for row in optima:
        print(f"  {row['dataset']:<46} levels {row['levels_nm']} nm -> "
              f"{row['rates']}  argmax {row['argmax_nm']:g} nm"
              + ("  [INTERIOR MAXIMUM]" if row["interior_maximum"] else ""))
    declared = {n: float(p.params['abrasive_size_peak_nm'].value)
                for n, (p, _) in packs.items()}
    print(f"\n  declared peaks: {declared}")
    interior = [r for r in optima if r["interior_maximum"]]
    print(f"  datasets with an interior maximum: {len(interior)} of {len(optima)}")

    print("\n── Q4: price the repair on PURE size sweeps ──")
    print("  (size is the only varying axis, so every other factor divides out "
          "of the one free scale)")
    print(f"  {'dataset':<46} {'pack':<22} {'pooled n':>9} {'piecewise':>10} "
          f"{'verdict':>10}")
    priced = []
    for row in optima:
        if not row["pure_size_sweep"]:
            continue
        pack_name = row["pack"]
        try:
            pack = load_pack(pack_name)
        except Exception:
            continue
        n_param = pack.params.get("abrasive_size_exponent")
        if n_param is None or n_param.value is None:
            continue
        pooled = _shape_mape(row["levels_nm"], row["rates"],
                             _power(float(n_param.value)))
        pw = None
        if all(pack.params.get(k) is not None
               and pack.params[k].value is not None for k in PEAK_KEYS):
            pw = _shape_mape(row["levels_nm"], row["rates"], _piecewise(
                float(pack.params["abrasive_size_peak_nm"].value),
                float(pack.params["abrasive_size_exp_below_peak"].value),
                float(pack.params["abrasive_size_exp_above_peak"].value)))
        if pooled is None or pw is None:
            continue
        verdict = ("piecewise BETTER" if pw < pooled - 0.05
                   else "pooled better" if pooled < pw - 0.05 else "tie")
        priced.append((row["dataset"], pack_name, pooled, pw, verdict))
        print(f"  {row['dataset']:<46} {pack_name:<22} {pooled:>8.2f}% "
              f"{pw:>9.2f}% {verdict:>18}")
    if not priced:
        print("  NO pure size sweep is pack-matched to a declared triple — the "
              "repair cannot be priced on held-out shape, which is itself the "
              "finding: the twelve constants are not just unreachable, they "
              "are UNTESTABLE by this corpus.")
    else:
        print("  ⚠ SCOPE of Q4: the pooled exponent was ESTIMATED from these "
              "same silica/ceria/alumina sweeps, so its column is partly "
              "in-sample and the margin is an upper bound on its advantage. "
              "Q5 is the fit-free half and does not depend on any exponent.")

    print("\n── Q5: fit-free — does the declared peak sit where the data's "
          "maximum is? ──")
    print("  A peak POSITION is falsifiable without fitting anything: either "
          "the sweep's own argmax is there or it is not.")
    print(f"  {'dataset':<46} {'declared':>9} {'argmax':>9} {'what is testable':>16} "
          f"{'verdict':>10}")
    for row in optima:
        try:
            pack = load_pack(row["pack"])
        except Exception:
            continue
        p = pack.params.get("abrasive_size_peak_nm")
        if p is None or p.value is None:
            continue
        peak = float(p.value)
        lo, hi = row["levels_nm"][0], row["levels_nm"][-1]
        rates = row["rates"]
        # IDENTIFIABILITY FIRST (the lesson of §52: ask what the data CAN
        # decide before reading a verdict off it). A peak POSITION is only
        # pinned by a sweep that brackets it. But a peak outside the range is
        # not untestable -- it asserts the sweep lies wholly on ONE leg, and a
        # leg has a SIGN. So there are two separable claims:
        #
        #   bracketing sweep  -> the position itself is testable
        #   sweep below peak  -> the declared below-peak leg (+4/3) says the
        #                        rates must RISE monotonically across it
        #   sweep above peak  -> the above-peak leg (-1/3) says they must FALL
        #
        # The second and third are weaker but fit-free, and refuting a sign
        # refutes the curve without needing any exponent magnitude.
        if lo <= peak <= hi:
            testable = "position"
            verdict = ("CONFIRMS"
                       if abs(row["argmax_nm"] - peak) / peak <= 0.25
                       else "REFUTES")
        elif peak > hi:
            testable = "below-leg sign"
            rising = all(b >= a for a, b in zip(rates, rates[1:]))
            verdict = "CONFIRMS" if rising else "REFUTES"
        else:
            testable = "above-leg sign"
            falling = all(b <= a for a, b in zip(rates, rates[1:]))
            verdict = "CONFIRMS" if falling else "REFUTES"
        print(f"  {row['dataset']:<46} {peak:>8.1f} {row['argmax_nm']:>8.1f} "
              f"{testable:>16} {verdict:>10}")

    print("\n── verdict ──")
    print(f"  REACHED: {len(reached)}   INERT: {len(inert)}")
    for k in inert:
        print(f"    inert: {k}")
    if control_failures:
        print(f"  CONTROL FAILURES (rows disowned): {control_failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
