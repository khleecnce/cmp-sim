"""Does the oxidiser gate's MECHANISM claim transfer to the alkaline sweeps
this corpus already holds -- and has its own exit condition already fired?

WHY THIS PROBE EXISTS (limits sec.50's general lesson, third instance)
----------------------------------------------------------------------
`cu_h2o2_bta.oxidizer_ph_window = [2.0, 6.25]` switches the oxidiser term OFF
outside its measured pH window.  The DECISION is a function-family claim (one
single-signed constant cannot reach both legs of Miranda 2004's 2x2) and is
closed to new data.  But the note justifying it also makes a claim about the
WORLD:

    "Alkaline H2O2 grows a hard CuO passivation film that the abrasive cannot
     cut" -- so the alkaline oxidiser response is strongly NEGATIVE.

That is a mechanism, hence transferable, hence falsifiable OUTSIDE the single
2x2 that produced it (limits sec.50).  And the same note carries an exit
condition:

    "TODO(owner): an alkaline Cu/H2O2/BTA H2O2 sweep (3+ points) would replace
     this gate with a prediction" ... "one for which no sweep has been located".

WHAT THIS MEASURES
------------------
Q1  Has the exit condition fired?  Enumerate the SCORED corpus for Cu datasets
    that sweep `oxidizer_wt_pct` at >= 3 levels entirely ABOVE the gate's upper
    bound (alkaline), and report whether BTA/inhibitor is declared present.
    Read from the dataset files, never from memory.

Q2  Does the mechanism's SIGN transfer?  Fit a log-log slope of measured rate
    against H2O2 concentration on each such ladder.  Miranda's alkaline leg is
    -86% over a 2.33x step (slope about -2.3).

Q3  Is the ladder CONFOUNDED with pH?  A ladder whose pH moves with H2O2
    cannot separate the oxidiser sign from the pH branch it sits on -- both
    push the same way in the alkaline branch.  Report the pH span alongside.

Q4  Is the ladder ADMISSIBLE as an anchor?  A dataset flagged
    `used_for_calibration: true` cannot supply a held-out constant for the pack
    it was fitted to (limits sec.32), so "a sweep exists" does NOT imply "the
    gate can be closed".  Report the flag and the pack each dataset scores
    under, because a foreign pack's citation is ordinary evidence reuse.

Run:  .venv/bin/python tools/alkaline_oxidizer_sign_transfer_probe.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core.params import load_pack  # noqa: E402

DATASETS = ROOT / "cmp_sim" / "data" / "validation" / "datasets"

GATE_PACK = "cu_h2o2_bta"
GATE_KEY = "oxidizer_ph_window"

# Miranda 2004 TABLE 3, the alkaline leg that the mechanism sentence is built
# on. 1.5 -> 3.5 wt% H2O2 at pH 8: 1743 -> 243 A/min.
MIRANDA_ALKALINE = ((1.5, 174.3), (3.5, 24.3))


def loglog_slope(points):
    """Least-squares slope of ln(rate) on ln(conc). Zero-concentration rows are
    dropped -- ln(0) is undefined, and a zero-oxidiser row is a different
    chemistry, not the bottom of a concentration ladder."""
    pts = [(c, r) for c, r in points if c > 0 and r > 0]
    if len(pts) < 3:
        return None, len(pts)
    xs = [math.log(c) for c, _ in pts]
    ys = [math.log(r) for _, r in pts]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None, n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / sxx, n


def main() -> int:
    pack = load_pack(GATE_PACK)
    window = pack.params[GATE_KEY].value
    lo, hi = float(window[0]), float(window[1])
    print(f"gate: {GATE_PACK}.{GATE_KEY} = [{lo:g}, {hi:g}]  "
          f"(oxidiser term switched off outside this pH range)")

    m_slope, _ = loglog_slope(MIRANDA_ALKALINE + MIRANDA_ALKALINE)
    step = math.log(MIRANDA_ALKALINE[1][1] / MIRANDA_ALKALINE[0][1]) / \
        math.log(MIRANDA_ALKALINE[1][0] / MIRANDA_ALKALINE[0][0])
    print(f"mechanism's own alkaline leg (Miranda 2004, pH 8): "
          f"log-log slope {step:+.2f} over 1.5->3.5 wt%")
    print()

    rows = []
    for path in sorted(DATASETS.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text())
        except Exception:
            continue
        if not isinstance(doc, dict) or doc.get("film") != "cu":
            continue
        conds = doc.get("conditions") or []
        ladder, phs = [], []
        for c in conds:
            ov = (c or {}).get("overrides") or {}
            if "oxidizer_wt_pct" not in ov:
                continue
            rate = c.get("mrr_nm_per_min")
            if rate is None:
                continue
            ladder.append((float(ov["oxidizer_wt_pct"]), float(rate)))
            if ov.get("slurry_ph") is not None:
                phs.append(float(ov["slurry_ph"]))
        if len(ladder) < 3 or not phs:
            continue
        if min(phs) <= hi:
            continue  # not entirely outside the gate window
        levels = sorted({c for c, _ in ladder})
        if len(levels) < 3:
            continue
        slope, n = loglog_slope(ladder)
        text = path.read_text().lower()
        has_bta = ("bta" in text or "benzotriazole" in text
                   or "inhibitor_mm" in text)
        rows.append({
            "name": path.stem,
            "pack": doc.get("pack"),
            "calib": bool(doc.get("used_for_calibration")),
            "ph_lo": min(phs), "ph_hi": max(phs),
            "levels": levels,
            "slope": slope, "n": n,
            "span": max(r for _, r in ladder) / max(1e-12, min(r for _, r in ladder)),
            "bta": has_bta,
        })

    if not rows:
        print("Q1: NO alkaline Cu oxidiser ladder in the corpus -- the exit "
              "condition has NOT fired.")
        return 0

    print(f"Q1: the exit condition HAS fired -- {len(rows)} alkaline Cu "
          f"oxidiser ladder(s) with >=3 levels, all pH > {hi:g}:")
    print()
    hdr = (f"{'dataset':<34} {'pack':<30} {'pH':<11} {'levels':<12} "
           f"{'slope':>7} {'span':>6} {'BTA':>4} {'calib':>6}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        lv = ",".join(f"{v:g}" for v in r["levels"])
        sl = f"{r['slope']:+.2f}" if r["slope"] is not None else "  --"
        ph = f"{r['ph_lo']:g}-{r['ph_hi']:g}"
        print(f"{r['name']:<34} {str(r['pack']):<30} {ph:<11} {lv:<12} "
              f"{sl:>7} {r['span']:>6.2f} {'yes' if r['bta'] else 'no':>4} "
              f"{'yes' if r['calib'] else 'no':>6}")
    print()

    print("Q2/Q3: does the mechanism's magnitude transfer?")
    for r in rows:
        conf = "CONFOUNDED with pH" if r["ph_hi"] - r["ph_lo"] > 0.3 \
            else "pH held fixed"
        print(f"  {r['name']}: slope {r['slope']:+.2f} vs the mechanism's "
              f"{step:+.2f}; {conf} (pH {r['ph_lo']:g}-{r['ph_hi']:g})")
    print()

    print("Q4: can any of them ANCHOR the gate (close it with a prediction)?")
    for r in rows:
        why = []
        if r["calib"]:
            why.append("used_for_calibration: true (self-scoring, limits sec.32)")
        if r["pack"] != GATE_PACK:
            why.append(f"scores under {r['pack']}, not {GATE_PACK} "
                       "(foreign pack = evidence reuse, not an anchor)")
        if r["slope"] is not None and abs(r["slope"]) < 0.15:
            why.append(f"response is FLAT (slope {r['slope']:+.2f}, span "
                       f"{r['span']:.2f}x) -- a flat ladder cannot fix a SIGN")
        if r["ph_hi"] - r["ph_lo"] > 0.3:
            why.append("pH moves with H2O2, so the oxidiser sign is not "
                       "separable from the pH branch")
        print(f"  {r['name']}: " + ("; ".join(why) if why else "ADMISSIBLE"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
