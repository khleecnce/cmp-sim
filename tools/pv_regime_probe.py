"""Probe: what OBSERVABLE decides the pressure branch a dataset sits in?

Context (STATUS.md NEXT, 2026-09-25)
------------------------------------
Refitting RR = k*P^a*V^b per dataset gives per-dataset optima scattered from
(a=0.05, b=0.80) to (a=2.00, b=0.05). That is regime selection, not noise
around one exponent pair, so the question is which observable separates the
branches. This script MEASURES two things and prints them; it changes no model
constant.

1. Per-dataset free (a, b), plus the observables already available without any
   new source: pressure level (min/max/mean psi), velocity level, film, pack,
   and whether the pack carries a passivation chemistry (inhibitor/oxidizer).

2. The THRESHOLD-PRESSURE hypothesis, which is the only super-linear mechanism
   in this corpus with a derivation behind it:

       RR = Kp * (P - P0) * V ,   P0 >= 0

   Physical reading: below P0 the asperity contact stress cannot break the
   passivating film (Cu-BTA complex, WO3, silica gel layer), so removal is
   chemical-only. Above it, Preston resumes. The LOCAL pressure exponent of
   this form is

       a_local = d ln RR / d ln P = P / (P - P0)

   which is > 1 near the threshold and -> 1 far above it, with NO exponent
   ever exceeding what a passivation offset can produce. So the hypothesis is
   falsifiable in a sharp way: the datasets with high fitted `a` must be the
   ones polished CLOSE to their P0, i.e. at low absolute pressure, and P0 must
   come out >= 0 and below the dataset's own pressure range.

   A per-dataset P0 is one constant per dataset, i.e. interpolation. So the
   number that decides the hypothesis is the GLOBAL fit: one P0 shared by every
   pressure-varying dataset (scale still free per dataset, because no two tools
   share a Kp). If one shared P0 beats Preston overall, that is one new
   constant buying many datasets; if it does not, the hypothesis is dead and
   gets recorded as falsified.
"""
from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import _measured  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402


def rows_of(doc):
    return doc.get("conditions") or []


def pv_rows(doc):
    """(P_psi, V_proxy, measured) at OTHERWISE IDENTICAL conditions.

    V proxy is the platen rpm: relative velocity is proportional to it whenever
    the carrier-platen geometry is fixed within a dataset, which it is in every
    file here. A proportionality constant is absorbed by the free scale.

    Rows are grouped by every override EXCEPT pressure and velocity, and only
    the largest group is kept. Without this control a P-V exponent fitted on an
    L25 array absorbs the pH and concentration response as well, which is how a
    dataset can appear to have a = 1.85 when its pressure span is 4.5-5.5 psi.
    """
    groups = {}
    for r in rows_of(doc):
        p = r.get("pressure_psi")
        v = r.get("rpm_platen") or r.get("rpm_wafer")
        m = _measured(r)
        if p is None or v is None or m is None:
            continue
        ov = r.get("overrides") or {}
        key = tuple(sorted((k, repr(val)) for k, val in ov.items()
                           if k not in ("pressure", "velocity",
                                        "pressure_psi", "rpm_platen")))
        groups.setdefault(key, []).append((float(p), float(v), float(m)))
    if not groups:
        return []
    best = max(groups.values(), key=len)
    # keep it only if the control actually leaves a pressure axis
    return best if len({r[0] for r in best}) >= 2 else []


def mape_scale_free(pred, meas):
    """MAPE after the single best multiplicative scale (log-mean)."""
    pairs = [(p, m) for p, m in zip(pred, meas) if p > 0 and m > 0]
    if len(pairs) < 2:
        return None
    k = math.exp(statistics.fmean(math.log(m / p) for p, m in pairs))
    return 100.0 * statistics.fmean(abs(k * p - m) / m for p, m in pairs)


def fit_ab(rows):
    """Grid-search the free (a, b) of RR ~ P^a V^b."""
    best = None
    for ai in range(0, 41):
        a = ai * 0.05
        for bi in range(0, 41):
            b = bi * 0.05
            e = mape_scale_free([p ** a * v ** b for p, v, _ in rows],
                                [m for _, _, m in rows])
            if e is None:
                continue
            if best is None or e < best[0]:
                best = (e, a, b)
    return best


def preston_err(rows):
    return mape_scale_free([p * v for p, v, _ in rows], [m for _, _, m in rows])


def threshold_err(rows, p0):
    pred = [max(p - p0, 0.0) * v for p, v, _ in rows]
    if all(x <= 0 for x in pred):
        return None
    return mape_scale_free(pred, [m for _, _, m in rows])


def main():
    sets = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text()) or {}
        rows = pv_rows(doc)
        if len(rows) < 3:
            continue
        ps = sorted({r[0] for r in rows})
        vs = sorted({r[1] for r in rows})
        if len(ps) < 2:                      # needs a pressure axis
            continue
        sets.append((path.stem, doc, rows, ps, vs))

    print(f"{'dataset':44s} {'n':>3s} {'Pmin':>5s} {'Pmax':>5s} "
          f"{'a':>5s} {'b':>5s} {'prest%':>7s} {'free%':>6s}  film")
    table = []
    for stem, doc, rows, ps, vs in sets:
        fit = fit_ab(rows)
        pe = preston_err(rows)
        if fit is None or pe is None:
            continue
        e, a, b = fit
        table.append((stem, rows, ps, a, b, pe, e, doc.get("film")))
        print(f"{stem[:44]:44s} {len(rows):3d} {ps[0]:5.2f} {ps[-1]:5.2f} "
              f"{a:5.2f} {b:5.2f} {pe:7.1f} {e:6.1f}  {doc.get('film')}")

    # --- observable test 1: does `a` track the absolute pressure level? ------
    print("\nSpearman rho(a, observable) over the pressure-varying datasets:")
    def rho(xs, ys):
        n = len(xs)
        rx = {v: i for i, v in enumerate(sorted(xs))}
        ry = {v: i for i, v in enumerate(sorted(ys))}
        dx = [rx[v] for v in xs]
        dy = [ry[v] for v in ys]
        mx, my = statistics.fmean(dx), statistics.fmean(dy)
        num = sum((i - mx) * (j - my) for i, j in zip(dx, dy))
        den = math.sqrt(sum((i - mx) ** 2 for i in dx)
                        * sum((j - my) ** 2 for j in dy))
        return num / den if den else float("nan")

    a_list = [t[3] for t in table]
    for name, getter in (("Pmin", lambda t: t[2][0]),
                         ("Pmax", lambda t: t[2][-1]),
                         ("Pmean", lambda t: statistics.fmean(t[2]))):
        print(f"  {name:6s} {rho(a_list, [getter(t) for t in table]):+.3f}")

    # --- observable test 2: one SHARED threshold pressure --------------------
    print("\nOne shared P0 (psi) across every dataset above, scale free per set:")
    base = statistics.fmean([t[5] for t in table])
    best = (base, 0.0)
    for i in range(0, 61):
        p0 = i * 0.05
        errs = [threshold_err(t[1], p0) for t in table]
        if any(e is None for e in errs):
            continue
        m = statistics.fmean(errs)
        if m < best[0]:
            best = (m, p0)
    print(f"  Preston (P0 = 0)   mean MAPE {base:.1f}%")
    print(f"  best shared P0 = {best[1]:.2f} psi  mean MAPE {best[0]:.1f}%")
    print(f"  per-dataset free (a,b): mean MAPE "
          f"{statistics.fmean([t[6] for t in table]):.1f}% "
          f"(2 constants per dataset -- interpolation, shown as the floor)")

    print("\n  per-dataset at the best shared P0:")
    for t in table:
        e = threshold_err(t[1], best[1])
        print(f"    {t[0][:44]:44s} preston {t[5]:6.1f}%  P0-form "
              f"{e:6.1f}%  {'BETTER' if e < t[5] else ''}")


if __name__ == "__main__":
    main()
