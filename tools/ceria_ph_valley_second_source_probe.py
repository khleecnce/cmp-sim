"""Dawkins 2019 Fig 5-12 -- is the SECOND independent ceria-on-oxide pH sweep a
VALLEY (as netzband2020 is) or a single peak (as `ph_response` can make)?

Self-verification first: the thesis PRINTS six numbers in its own prose that the
figure reading must reproduce.  A raster digitisation nobody can check is not
admissible here, so the reading is graded against the author's text before it is
used for anything.

Then the question sti_ceria's refusal turns on: can one unimodal bell represent
this series at all?
"""
from __future__ import annotations

import math
import statistics

# ── reading of Fig 5-12, oxide (SiO2) series, nm/min ───────────────────────
# panel (a) ceria:silica weight ratio 0.1, panel (b) 0.2
PH = [3.5, 4.0, 6.0, 8.0, 10.0]
OXIDE_A = [365.0, 375.0, 305.0, 182.0, 183.0]
OXIDE_B = [202.0, 381.0, 420.0, 315.0, 202.0]
NITRIDE_B = [8.0, 49.0, 57.0, 29.0, 5.0]
SEL_A = [4.9, 4.6, 6.1, 6.4, 14.7]
SEL_B = [27.0, 7.7, 7.5, 10.3, 27.5]

# ── the six numbers the thesis prints in prose (pp. 79, 83) ────────────────
PRINTED = [
    ("0.2 ratio, pH 4 oxide = 381 nm/min (p.81)", 381.0, OXIDE_B[1]),
    ("0.2 ratio, pH 6 oxide max = 420 nm/min (p.79)", 420.0, OXIDE_B[2]),
    ("0.2 ratio, pH 6 nitride max = 55 nm/min (p.79)", 55.0, NITRIDE_B[2]),
    ("0.2 ratio, pH 10 oxide ~ 200 nm/min (p.79)", 200.0, OXIDE_B[4]),
    ("0.1 ratio, pH 10 selectivity = 15 (p.79)", 15.0, SEL_A[4]),
    ("0.2 ratio, pH 10 selectivity = 28 (p.79)", 28.0, SEL_B[4]),
]
print("=== self-verification against the thesis's own printed numbers ===")
worst = 0.0
for label, printed, read in PRINTED:
    err = 100 * abs(read - printed) / printed
    worst = max(worst, err)
    print(f"  {label:48s} printed {printed:6.1f}  read {read:6.1f}  {err:5.1f}%")
print(f"  worst disagreement {worst:.1f}%\n")

# ── shape: valley or single peak? ──────────────────────────────────────────
def interior_dips(series):
    return [i for i in range(1, len(series) - 1)
            if series[i] < series[i - 1] and series[i] < series[i + 1]]


def interior_peaks(series):
    return [i for i in range(1, len(series) - 1)
            if series[i] > series[i - 1] and series[i] > series[i + 1]]


NETZBAND_PH = [4.0, 6.0, 8.0, 10.0]
NETZBAND = [198.0, 113.0, 200.0, 213.0]

for name, phs, s in (("netzband2020 (the incumbent)", NETZBAND_PH, NETZBAND),
                     ("dawkins2019 panel (a) 0.1", PH, OXIDE_A),
                     ("dawkins2019 panel (b) 0.2", PH, OXIDE_B)):
    print(f"{name:32s} dips at {interior_dips(s)}  peaks at {interior_peaks(s)}"
          f"  span {max(s) / min(s):.2f}x")

# ── can ONE bell represent each series? ────────────────────────────────────
def ph_response(ph, peak, width, floor, acid_floor):
    """Same functional form as cmp_sim.models.chemical_rate.ph_response."""
    f = acid_floor if ph < peak else floor
    return f + (1.0 - f) * math.exp(-(((ph - peak) / width) ** 2))


def best_bell(phs, measured):
    """Grid-search the bell, one free multiplicative scale (the scorer's rule)."""
    best_err = 1e9
    best_par = (float("nan"),) * 4
    for peak in [x / 4 for x in range(8, 49)]:            # 2.0 .. 12.0
        for width in [x / 4 for x in range(2, 41)]:       # 0.5 .. 10.0
            for floor in (0.0, 0.05, 0.15, 0.3, 0.5, 0.7, 0.9, 0.95):
                for acid in (0.0, 0.012, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95):
                    pred = [ph_response(p, peak, width, floor, acid)
                            for p in phs]
                    k = (sum(m * p for m, p in zip(measured, pred))
                         / sum(p * p for p in pred))
                    e = 100 * statistics.mean(
                        [abs(k * p - m) / m for m, p in zip(measured, pred)])
                    if e < best_err:
                        best_err, best_par = e, (peak, width, floor, acid)
    return best_err, best_par


print("\n=== best achievable fit of ONE unimodal bell (scale free) ===")
for name, phs, s in (("netzband2020", NETZBAND_PH, NETZBAND),
                     ("dawkins (a) 0.1", PH, OXIDE_A),
                     ("dawkins (b) 0.2", PH, OXIDE_B)):
    e, par = best_bell(phs, s)
    print(f"  {name:16s} best MAPE {e:6.2f}%  at peak={par[0]} width={par[1]} "
          f"floor={par[2]} acid={par[3]}")
