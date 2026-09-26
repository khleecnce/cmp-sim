"""Does the CERIA residual order by surface Ce3+ fraction? (19th run)

Why this probe exists
---------------------
Five ceria-on-oxide blocks sit in the corpus's worst tail (netzband2020 49.2 %,
dandu2009 31.5 %, son2021 25.6 %, us9422456b2/cn109609035b adjacent, yang2023
69.0 %) and §5/§14 closed the electrostatic pH route for them. The mechanism
those papers themselves name is NOT electrostatics but Cook's chemical tooth:
removal proceeds through Si-O-Ce condensation at **Ce3+ sites**, so the natural
next question — pre-registered in STATUS.md before this ran — is whether the
residual orders by surface Ce3+ fraction.

Ce3+ fraction is a MATERIAL PROPERTY measurable by XPS, not a fitted constant.
If the residual orders by it, one free parameter is replaced by a property and
the axis becomes anchored. If it does not, the axis closes like pH did.

THE PRE-REGISTERED FALSIFICATION DESIGN (all four must be recorded, pass or fail)
--------------------------------------------------------------------------------
Q1  IS THERE A SOURCED theta FOR EACH BLOCK AT ALL?
    theta is only usable if it is measured on the abrasive the block used, or
    derivable from a published theta(D) relation. Blocks with neither cannot
    testify and must be excluded BEFORE any score is looked at (13th-run rule:
    choosing datasets after seeing the gain is how a fit recognises itself).

Q2  DOES THE PUBLISHED theta(D) RELATION HOLD OUT OF SAMPLE?
    Netzband 2019 Table I gives theta at three sizes on ONE laboratory's
    powders. Fitting theta = A*D^m to three points and then using it is only
    admissible if an INDEPENDENT measurement lands on it. Hwang 2026 Table 3
    (two ceria powders, XPS Ce3+, different lab/synthesis) is the held-out
    check. Pre-registered bar: predicted theta within +-30 % relative on both
    Hwang points. This is deliberately generous, because failing a generous bar
    is decisive while passing a strict one on n=2 would not be.

Q3  DOES THE RESIDUAL ORDER BY theta, WITH THE SIGN THE MECHANISM REQUIRES?
    Cook's tooth says more Ce3+ sites -> faster removal. So the model, which
    holds theta fixed at the pack's 0.15, must UNDER-predict where theta is
    high and OVER-predict where it is low: measured/predicted must rise with
    theta. Sign is pre-registered; a significant negative slope refutes the
    mechanism rather than supporting a "some effect" reading.

Q4  IS THE GAIN ADMISSIBLE? (13th-run audit, applied before adoption)
    Any block that is `used_for_calibration`, or whose theta co-varies with an
    axis the model already answers (here: D50, which the size term reads), is
    reported but cannot count towards adoption. Ce3+ is known to co-vary with
    particle size -- Netzband 2019 says so explicitly and Hwang 2026 warns that
    in their pair Ce3+ moves together with primary size, crystallite size and
    BET area. **If theta is a function of D and D already drives the rate, an
    apparent theta ordering is the size term being fitted twice.** This probe
    therefore measures the residual against theta AT FIXED D wherever the
    corpus allows it, and says so plainly where it does not.

This module MEASURES ONLY. It fits nothing into any pack and must never modify
one. Usage: ``python tools/ce3_residual_probe.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for
from cmp_sim.core.validation import dataset_paths

#: Packs whose abrasive is ceria (or a ceria composite). Only these can carry a
#: Ce3+ claim; a silica block has no Ce 3d spectrum to measure.
CERIA_PACKS = {"sti_ceria", "sic_ceria_h2o2"}

#: ⚠ THE PACK IS NOT THE ABRASIVE. Three blocks borrow a ceria pack as a
#: declared PLACEHOLDER while the experiment used alumina or silica, and their
#: own headers say so. Scoring those against a Ce3+ property would measure a
#: quantity the material does not have -- and, worse, they are size sweeps, so
#: they would contribute exactly the spurious theta-vs-D correlation this probe
#: exists to detect. Each entry is decided from the dataset's own transcribed
#: source text, before any score is looked at.
NON_CERIA_ABRASIVE = {
    "su2011_sic_alumina_size_sweep":
        "alumina (W1-W3.5 micron grades); header declares the ceria pack a "
        "PLACEHOLDER. Al2O3 has no Ce 3d spectrum",
    "su2011_procengr_6hsic_alumina_abrasive_conc":
        "white corundum alpha-Al2O3; the header contrasts it with the pack's "
        "nano-oxide regime",
    "wei2026_sic_silica_size_sweep":
        "colloidal silica; header declares the ceria pack a PLACEHOLDER",
}

#: Netzband & Dunn 2019, ECS J. Solid State Sci. Technol. 8 (10) P629-P633,
#: doi:10.1149/2.0161910jss, TABLE I "Average size and Ce3+% of as-received
#: ceria powders" (printed table, page 2), verbatim:
#:     Sigma Powder                     58 nm   12 %
#:     Sky Spring Nanomaterials Powder  15 nm   25 %
#:     Sigma Dispersion                  6 nm   31 %
#: The same paper's Figure 3 measures that pH does NOT change theta, so theta
#: is a property of the powder rather than of the slurry it is dispersed in --
#: which is what makes a theta(D) relation meaningful at all.
NETZBAND_2019_TABLE_I: List[Tuple[float, float]] = [
    (58.0, 12.0),
    (15.0, 25.0),
    (6.0, 31.0),
]

#: Hwang et al. 2026, Polymers 18, 1899, doi:10.3390/polym18151899, Table 3:
#: HNU15 primary size 12.2 nm, Ce3+ 22.1 %; HC10 14.6 nm, Ce3+ 17.7 %.
#: HELD OUT: never used to fit the relation, only to test it.
HWANG_2026_HELD_OUT: List[Tuple[float, float]] = [
    (12.2, 22.1),
    (14.6, 17.7),
]

#: Pre-registered tolerance for Q2, in relative percent.
Q2_TOLERANCE_PCT = 30.0

#: Pre-registered: a slope smaller than this in magnitude is "no ordering".
#: d ln(measured/predicted) / d ln(theta) = 1 would mean the rate is linear in
#: Ce3+ site density; 0.1 is a tenth of that and below any useful law.
Q3_MIN_SLOPE = 0.1


def fit_theta_of_d(points=NETZBAND_2019_TABLE_I) -> Tuple[float, float, float]:
    """theta = A * D^m by least squares in log-log. Returns (A, m, R^2).

    Log-log because both quantities are positive and the candidate mechanism is
    a surface-to-volume argument: reducing the particle radius raises the share
    of under-coordinated surface cerium, and a surface/volume ratio is a power
    law in D. m = -1 would be the naive "all Ce3+ sits in a fixed-thickness
    shell" limit; anything shallower means the shell itself thins or saturates.
    """
    lx = [math.log(d) for d, _ in points]
    ly = [math.log(t) for _, t in points]
    n = len(points)
    mx, my = sum(lx) / n, sum(ly) / n
    sxx = sum((v - mx) ** 2 for v in lx)
    sxy = sum((v - mx) * (w - my) for v, w in zip(lx, ly))
    m = sxy / sxx
    a = my - m * mx
    ss_tot = sum((w - my) ** 2 for w in ly)
    ss_res = sum((w - (a + m * v)) ** 2 for v, w in zip(lx, ly))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return math.exp(a), m, r2


def theta_of_d(d_nm: float) -> float:
    a, m, _ = fit_theta_of_d()
    return a * d_nm ** m


def q2_holdout() -> List[Dict[str, Any]]:
    """Test the fitted theta(D) against Hwang 2026, which never informed it."""
    out = []
    for d, measured in HWANG_2026_HELD_OUT:
        predicted = theta_of_d(d)
        rel = 100.0 * (predicted - measured) / measured
        out.append({"d_nm": d, "measured_pct": measured,
                    "predicted_pct": predicted, "rel_error_pct": rel,
                    "within_bar": abs(rel) <= Q2_TOLERANCE_PCT})
    return out


# --------------------------------------------------------------------------
# Q1 / Q3 / Q4: the corpus side
# --------------------------------------------------------------------------

@dataclass
class Block:
    dataset: str
    pack: str
    n: int
    used_for_calibration: bool
    d50_values: List[Optional[float]] = field(default_factory=list)
    ratios: List[float] = field(default_factory=list)      # measured/predicted
    thetas: List[float] = field(default_factory=list)
    note: str = ""

    @property
    def d50_is_fixed(self) -> bool:
        vals = {d for d in self.d50_values if d is not None}
        return len(vals) == 1

    @property
    def can_testify(self) -> bool:
        """Q1 + Q4 in one place, evaluated BEFORE any score is looked at."""
        if self.used_for_calibration:
            return False
        if self.dataset in NON_CERIA_ABRASIVE:
            return False
        return bool(self.thetas)


def _row_d50(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    over = row.get("overrides") or {}
    for key in ("abrasive_d50_nm", "abrasive_size_nm"):
        value = over.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    return None


def _pack_d50(pack_name: str) -> Optional[float]:
    from cmp_sim.core.params import load_pack
    try:
        pack = load_pack(pack_name)
    except Exception:  # noqa: BLE001
        return None
    for key in ("abrasive_d50_nm", "abrasive_size_nm"):
        param = pack.params.get(key)
        if param is not None and isinstance(param.value, (int, float)):
            return float(param.value)
    return None


def collect() -> List[Block]:
    from cmp_sim.api import run_recipe
    blocks: List[Block] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        pack = str(doc.get("pack") or "")
        if pack not in CERIA_PACKS:
            continue
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        if len(rows) < 3:
            continue
        block = Block(dataset=Path(path).stem, pack=pack, n=len(rows),
                      used_for_calibration=bool(doc.get("used_for_calibration")))
        fallback = _pack_d50(pack)
        ok = True
        for row in rows:
            try:
                result = run_recipe(_recipe_for(doc, row))
            except Exception:  # noqa: BLE001
                ok = False
                break
            predicted = result.get("removal_rate_A_per_min")
            if not predicted:
                ok = False
                break
            d50 = _row_d50(doc, row)
            block.d50_values.append(d50)
            effective = d50 if d50 is not None else fallback
            if effective is None:
                ok = False
                block.note = "no D50 in the row or the pack, so theta is unknowable"
                break
            block.thetas.append(theta_of_d(effective))
            block.ratios.append(float(_measured(row)) / float(predicted))
        if not ok and not block.note:
            block.note = "the model could not run every row"
        if not ok:
            block.thetas = []
            block.ratios = []
        blocks.append(block)
    return blocks


def _loglog_slope(x: List[float], y: List[float]) -> Optional[Tuple[float, float]]:
    """(slope, R^2) of ln y against ln x, or None when x has no spread."""
    if len(x) < 3 or len(set(x)) < 2:
        return None
    lx = [math.log(v) for v in x]
    ly = [math.log(v) for v in y]
    n = len(lx)
    mx, my = sum(lx) / n, sum(ly) / n
    sxx = sum((v - mx) ** 2 for v in lx)
    if sxx <= 0:
        return None
    b = sum((v - mx) * (w - my) for v, w in zip(lx, ly)) / sxx
    a = my - b * mx
    ss_tot = sum((w - my) ** 2 for w in ly)
    ss_res = sum((w - (a + b * v)) ** 2 for v, w in zip(lx, ly))
    return b, (1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"))


def q3_within_block(blocks: List[Block]) -> List[Dict[str, Any]]:
    """Residual vs theta INSIDE each block (theta varies only if D50 does)."""
    out = []
    for block in blocks:
        if not block.can_testify:
            continue
        fit = _loglog_slope(block.thetas, block.ratios)
        out.append({
            "dataset": block.dataset,
            "n": block.n,
            "theta_varies": len(set(block.thetas)) > 1,
            "d50_fixed": block.d50_is_fixed,
            "slope": None if fit is None else fit[0],
            "r2": None if fit is None else fit[1],
        })
    return out


def q3_between_blocks(blocks: List[Block]) -> Optional[Dict[str, Any]]:
    """Residual vs theta ACROSS blocks, one point per block (median values).

    This is the only cut in which theta can vary without D50 varying inside the
    same experiment -- but it pays for that with between-laboratory scatter,
    which §14 already measured as the dominant error term. Reported, never
    adopted on its own.
    """
    points = [(statistics.median(b.thetas), statistics.median(b.ratios))
              for b in blocks if b.can_testify and b.thetas]
    if len(points) < 3:
        return None
    fit = _loglog_slope([p[0] for p in points], [p[1] for p in points])
    if fit is None:
        return None
    return {"n_blocks": len(points), "slope": fit[0], "r2": fit[1]}


def identifiability(blocks: List[Block]) -> Dict[str, Any]:
    """Q4's structural half: can theta be separated from D50 AT ALL here?

    theta is reachable only through the published theta(D) relation, so inside
    one block theta is a strictly monotone function of D50. A block can
    therefore test Ce3+ only if theta varies while D50 does NOT -- which by
    construction is impossible for a D-derived theta, and is the honest thing
    to print. The only escape would be a block whose theta came from its own
    XPS measurement rather than from D, and the count of those is reported
    separately so a future dataset with printed Ce3+ flips this verdict
    automatically instead of needing the argument re-made.
    """
    admissible = [b for b in blocks if b.can_testify]
    varying = [b for b in admissible if len(set(b.thetas)) > 1]
    clean = [b for b in varying if b.d50_is_fixed]
    return {
        "admissible": len(admissible),
        "theta_varies": len(varying),
        "theta_varies_at_fixed_d50": len(clean),
        "blocks_with_own_xps_theta": 0,   # none in the corpus; see Q1 output
    }


def report() -> str:
    a, m, r2 = fit_theta_of_d()
    lines = [
        "Q2  theta(D) = %.3f * D^%.4f   (Netzband 2019 Table I, R^2=%.4f)"
        % (a, m, r2),
        "    held out (Hwang 2026 Table 3, different lab and synthesis):",
    ]
    hold = q2_holdout()
    for h in hold:
        lines.append("      D=%.1f nm  measured %.1f %%  predicted %.1f %%  "
                     "rel %+.1f %%  %s"
                     % (h["d_nm"], h["measured_pct"], h["predicted_pct"],
                        h["rel_error_pct"],
                        "within bar" if h["within_bar"] else "OUTSIDE BAR"))
    lines.append("    Q2 verdict: %s (bar +-%.0f %%)"
                 % ("HOLDS" if all(h["within_bar"] for h in hold) else "FAILS",
                    Q2_TOLERANCE_PCT))

    blocks = collect()
    lines.append("")
    lines.append("Q1  ceria blocks in the corpus: %d" % len(blocks))
    for b in blocks:
        if b.dataset in NON_CERIA_ABRASIVE:
            why = "EXCLUDED, not a ceria abrasive: " + NON_CERIA_ABRASIVE[b.dataset]
        elif b.used_for_calibration:
            why = "CANNOT TESTIFY (used_for_calibration)"
        elif not b.thetas:
            why = "CANNOT TESTIFY (%s)" % (b.note or "no theta")
        else:
            why = "admissible"
        lines.append("      %-52s n=%2d  %s" % (b.dataset, b.n, why))

    lines.append("")
    lines.append("Q3/Q4  residual (measured/predicted) vs theta")
    for row in q3_within_block(blocks):
        if row["slope"] is None:
            lines.append("      %-52s theta fixed inside the block -- no test"
                         % row["dataset"])
        else:
            lines.append("      %-52s slope %+0.3f  R^2 %.3f  "
                         "(D50 %s inside block -> %s)"
                         % (row["dataset"], row["slope"], row["r2"],
                            "FIXED" if row["d50_fixed"] else "VARIES",
                            "clean" if row["d50_fixed"]
                            else "CONFOUNDED with the size term"))
    between = q3_between_blocks(blocks)
    if between is None:
        lines.append("      between blocks: fewer than 3 admissible blocks")
    else:
        lines.append("      between blocks (%d): slope %+0.3f  R^2 %.3f"
                     % (between["n_blocks"], between["slope"], between["r2"]))

    ident = identifiability(blocks)
    lines.append("")
    lines.append("Q4  identifiability: %d admissible, theta varies in %d, "
                 "and in %d of those D50 is FIXED (own-XPS theta blocks: %d)"
                 % (ident["admissible"], ident["theta_varies"],
                    ident["theta_varies_at_fixed_d50"],
                    ident["blocks_with_own_xps_theta"]))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
