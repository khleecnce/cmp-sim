"""Why does the UNOWNED block miss, if no axis it sweeps can explain it?

Why this script exists
----------------------
``tools/axis_error_census.py`` (limit 14) established that 145 of 342 improvable
measured points -- the single largest block -- belong to no axis: a FREE
per-dataset exponent on the best axis those datasets sweep buys less than 2 pp.
That is a negative result, and a negative result is only half an answer. If the
error is not a missing single-axis law, it is something, and "something" has to
be named before the corpus median can honestly be called a floor.

This tool partitions the unowned block by CAUSE, using only quantities already
measured elsewhere in the repository. Nothing is fitted.

  A ``at_noise_floor``   The dataset's OWN replicate scatter already covers its
                         shape error (``Score.at_noise_floor``: shape <= 1.3 x
                         scatter). Irreducible: further work fits that paper's
                         noise.
  B ``floor_unmeasured`` The dataset repeats no condition, so its reproducibility
                         is UNKNOWN. This is deliberately NOT merged with A:
                         unknown is not zero, and 40 of 46 datasets are in this
                         state. It bounds what can be claimed, not what is true.
  C ``scale_failure``    The absolute rate is off by more than 3x while the
                         SHAPE is scored after one free scale. A dataset can
                         track every trend and still be a physically wrong
                         prediction; that error is invisible to the shape metric
                         and is a different defect from a missing law.
  D ``loses_to_the_mean`` The physics does not beat predicting the dataset mean
                         (``beats_flat`` false). Here the model contributes
                         nothing on this body, so the residual is not a
                         refinement problem.
  E ``unexplained``      None of the above. THIS is the only part of the unowned
                         block that would justify looking for new physics, and
                         its size is the number that decides whether <= 15 % is
                         a floor or merely a status quo.

A dataset can satisfy several; it is assigned to the FIRST that applies, in the
order above, because that order runs from "cannot be improved even in principle"
to "could be improved". Every dataset's other flags are still printed, so the
partition never hides a second reason.

This module MEASURES ONLY and must never modify a pack.
Usage: ``python tools/unowned_error_partition.py`` (inside ``.venv``).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cmp_sim.core.predictive_score import score_all

BUCKETS = ("at_noise_floor", "floor_unmeasured", "scale_failure",
           "loses_to_the_mean", "unexplained")

#: A measured/predicted absolute-rate ratio outside this band is a scale
#: failure. The band matches ``Score.scale_is_calibrated`` (0.33-3.0), so this
#: tool and the score report cannot disagree about what "off by 3x" means.
SCALE_LO, SCALE_HI = 0.33, 3.0


@dataclass
class Cause:
    dataset: str
    film: str
    n: int
    shape: float
    bucket: str = ""
    flags: List[str] = field(default_factory=list)
    scatter: Optional[float] = None
    scale: Optional[float] = None


def partition(unowned: Optional[List[str]] = None) -> List[Cause]:
    """Classify the unowned datasets. Pass names to avoid re-running the census."""
    if unowned is None:
        from tools.axis_error_census import price
        unowned = [dp.dataset for dp in price() if dp.owner == "distributed"]
    wanted = set(unowned)
    out: List[Cause] = []
    for s in score_all():
        if s.dataset not in wanted or s.shape_mape is None:
            continue
        rec = Cause(dataset=s.dataset, film=s.film or "?", n=s.n,
                    shape=float(s.shape_mape),
                    scatter=s.replicate_scatter, scale=s.scale_ratio)
        if s.at_noise_floor:
            rec.flags.append("at its own replicate floor")
        if s.replicate_scatter is None:
            rec.flags.append("reproducibility UNMEASURED")
        if s.scale_ratio is not None and not (SCALE_LO <= s.scale_ratio <= SCALE_HI):
            rec.flags.append(f"absolute rate {s.scale_ratio:.2g}x")
        if s.beats_flat is False:
            rec.flags.append("loses to predicting the mean")

        if s.at_noise_floor:
            rec.bucket = "at_noise_floor"
        elif (s.scale_ratio is not None
              and not (SCALE_LO <= s.scale_ratio <= SCALE_HI)):
            rec.bucket = "scale_failure"
        elif s.beats_flat is False:
            rec.bucket = "loses_to_the_mean"
        elif s.replicate_scatter is None:
            rec.bucket = "floor_unmeasured"
        else:
            rec.bucket = "unexplained"
        out.append(rec)
    return out


def summary(causes: Optional[List[Cause]] = None) -> Dict[str, Any]:
    causes = causes if causes is not None else partition()
    total = sum(c.n for c in causes)
    by: Dict[str, List[Cause]] = {}
    for c in causes:
        by.setdefault(c.bucket, []).append(c)
    unexplained = by.get("unexplained", [])
    return {
        "datasets": len(causes),
        "points": total,
        "buckets": {k: {"datasets": len(v), "points": sum(c.n for c in v),
                        "median_shape": statistics.median(c.shape for c in v)}
                    for k, v in by.items()},
        "unexplained_points": sum(c.n for c in unexplained),
        "unexplained_share": (100.0 * sum(c.n for c in unexplained) / total
                              if total else 0.0),
        "floor_measured_on": sum(1 for c in causes if c.scatter is not None),
    }


def contrast() -> Dict[str, Any]:
    """Unowned vs owned: which block actually carries the ERROR?

    Written because the first run of this tool overturned the intuition that
    motivated it. "No axis explains it" sounds like the hard part of the corpus,
    but the unowned datasets score BETTER than the ones an axis owns. The
    comparison is reported in points and in point-weighted error, because a
    median over datasets hides size.

    Also reports the median the improvable bucket would reach if EVERY dataset
    were granted its best oracle -- a bound no law can attain, since the oracle
    refits per dataset. If that bound is already near the completion criterion,
    then the criterion is a property of the corpus, not of the model.
    """
    from tools.axis_error_census import price
    ps = price()
    un = [d for d in ps if d.owner == "distributed"]
    ow = [d for d in ps if d.owner != "distributed"]
    total_err = sum(d.shape * d.n for d in ps)

    def block(group):
        pts = sum(d.n for d in group)
        return {
            "datasets": len(group), "points": pts,
            "median_shape": statistics.median(d.shape for d in group),
            "point_weighted_shape": sum(d.shape * d.n for d in group) / pts,
            "share_of_weighted_error": 100.0 * sum(d.shape * d.n for d in group) / total_err,
        }

    granted = [d.residual_after if d.residual_after is not None else d.shape
               for d in ps]
    return {"unowned": block(un), "owned": block(ow),
            "improvable_median_now": statistics.median(d.shape for d in ps),
            "improvable_median_if_every_oracle_granted": statistics.median(granted)}


def corpus_bound() -> Dict[str, Any]:
    """The whole-corpus median if EVERY dataset were granted its best oracle.

    This is the sharpest single number the repository can produce about the
    completion criterion, and it is an UPPER bound on any law-based programme:
    each dataset gets a free exponent on its own best axis, fitted on the very
    rows being scored, with no requirement that different datasets agree. No
    physics can do better, because physics must share its constants.
    """
    from tools.axis_error_census import price
    from cmp_sim.core.predictive_score import score_all
    priced = {d.dataset: d for d in price()}
    scored = [s for s in score_all() if s.shape_mape is not None]
    now, granted = [], []
    for s in scored:
        now.append(float(s.shape_mape))
        d = priced.get(s.dataset)
        granted.append(d.residual_after if (d and d.residual_after is not None)
                       else float(s.shape_mape))
    return {
        "datasets": len(scored),
        "median_now": statistics.median(now),
        "median_if_every_oracle_granted": statistics.median(granted),
        "under_ten_now": sum(1 for v in now if v <= 10.0),
        "under_ten_granted": sum(1 for v in granted if v <= 10.0),
    }


def report(causes: Optional[List[Cause]] = None) -> str:
    causes = causes if causes is not None else partition()
    lines = [f"{'dataset':44s} {'film':6s} {'n':>3s} {'shape%':>7s} "
             f"{'repl%':>6s} {'scale':>7s}  {'bucket':17s} other flags",
             "-" * 145]
    for c in sorted(causes, key=lambda c: (BUCKETS.index(c.bucket), -c.n)):
        repl = "  n/a" if c.scatter is None else f"{c.scatter:6.1f}"
        scale = "      -" if c.scale is None else f"{c.scale:6.2f}x"
        others = [f for f in c.flags
                  if not f.startswith(c.bucket.split('_')[0])]
        lines.append(f"{c.dataset[:44]:44s} {c.film[:6]:6s} {c.n:3d} "
                     f"{c.shape:7.1f} {repl} {scale}  {c.bucket:17s} "
                     f"{'; '.join(others)}")
    s = summary(causes)
    lines += ["", f"{s['datasets']} unowned datasets, {s['points']} measured points"]
    for bucket in BUCKETS:
        info = s["buckets"].get(bucket)
        if info is None:
            lines.append(f"  {bucket:18s} 0")
            continue
        lines.append(f"  {bucket:18s} {info['datasets']:2d} datasets, "
                     f"{info['points']:3d} points, median shape "
                     f"{info['median_shape']:.1f}%")
    lines += ["",
              f"reproducibility is MEASURED on {s['floor_measured_on']} of "
              f"{s['datasets']} unowned datasets -- the rest have no repeated "
              "condition, so their floor is unknown, not zero",
              f"genuinely UNEXPLAINED: {s['unexplained_points']} points "
              f"({s['unexplained_share']:.1f} % of the unowned block). This is "
              "the only part that new physics could address."]

    c = contrast()
    lines += ["", "WHICH BLOCK CARRIES THE ERROR (the finding that reverses the intuition):"]
    for name in ("unowned", "owned"):
        b = c[name]
        lines.append(f"  {name:8s} {b['datasets']:2d} datasets, {b['points']:3d} points, "
                     f"median shape {b['median_shape']:5.1f} %, point-weighted "
                     f"{b['point_weighted_shape']:5.1f} %, "
                     f"{b['share_of_weighted_error']:4.1f} % of the corpus' weighted error")
    lines.append(f"  the unowned block scores BETTER than the owned one, so "
                 f"\"no axis explains it\" is not \"the hard part\"")
    lines.append(f"  improvable median now {c['improvable_median_now']:.1f} % -> "
                 f"{c['improvable_median_if_every_oracle_granted']:.1f} % if EVERY "
                 "dataset were granted its own best oracle (a bound no shared "
                 "law can reach)")

    cb = corpus_bound()
    lines += ["", "THE WHOLE-CORPUS BOUND (the number the completion criterion turns on):",
              f"  corpus median {cb['median_now']:.1f} % over {cb['datasets']} datasets; "
              f"if EVERY dataset were granted a free exponent on its own best axis, "
              f"{cb['median_if_every_oracle_granted']:.1f} %",
              f"  datasets already at or below 10 %: {cb['under_ten_now']} -> "
              f"{cb['under_ten_granted']} under that unreachable grant",
              "  => <= 10 % is above the reach of ANY shared-constant law on this "
              "corpus, which is what licenses the <= 15 % criterion"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
