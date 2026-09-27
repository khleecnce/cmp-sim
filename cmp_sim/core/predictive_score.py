"""Score the model against EVERY measured point, not just the P*V sweeps.

Why this exists
---------------
The P*V gate fits one constant (Kp) per dataset and reports the residual. That
answers "does Preston's law hold", which was the right first question, but it
silently ignores 60% of the measured data in this repository: the pH sweeps,
the oxidizer series, the concentration and particle-size sweeps. The chemistry
layers were therefore never scored against a measurement at all.

This module scores on the axis each dataset actually varies, and reports
out-of-sample error by leave-one-out rather than the in-sample residual. Two
different questions get separate answers:

* **SHAPE** — with the scale fitted to the dataset, how well does the model
  track the trend? This is what a process engineer asking "which way does it
  move, and by how much" needs. Scale-free, because no pack's Kp is calibrated
  to someone else's tool.
* **PREDICTION** — the leave-one-out error: fit on n-1 points, predict the one
  held out. This is the only number that can be quoted as accuracy without
  qualification.

A model that reports the in-sample residual as its accuracy is grading its own
homework; with one free parameter per k points that number always flatters.
"""
from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from cmp_sim.core.declined_axes import declined_axes
from cmp_sim.core.validation import dataset_paths

#: Inherited datasets identify the film only by the pack they target. The
#: engine now requires wafer.film explicitly (a missing film used to return the
#: oxide rate silently), so it is recovered from the pack here. This is a
#: scoring-harness convenience, NOT a fallback inside the engine: guessing the
#: film at runtime is exactly what was removed.
PACK_FILM = {
    "oxide_silica": "oxide",
    "oxide_silica_calibrated_pad": "oxide",
    "oxide_silica_aminosilane": "oxide",
    "oxide_silica_anionic": "oxide",
    "cu_alkaline_benzenesulfonic": "cu",
    "sti_ceria": "sti",
    "cu_h2o2_bta": "cu",
    "w_fe_oxidizer": "w",
    "sic_ceria_h2o2": "sic",
    "poly_si_alkaline": "poly_si",
    "si_substrate_alkaline": "si",
    "snag_solder": "snag",
}

#: Pack override key -> where it belongs in a recipe dict.
OVERRIDE_TO_RECIPE: Dict[str, Tuple[str, str]] = {
    "slurry_ph": ("slurry", "ph"),
    "ph": ("slurry", "ph"),
    "temperature_c": ("slurry", "temperature_c"),
    "abrasive_wt_pct": ("abrasive", "conc_wt_pct"),
    "abrasive_conc_wt_pct": ("abrasive", "conc_wt_pct"),
    "abrasive_d50_nm": ("abrasive", "d50_nm"),
}

#: Overrides that are additives rather than scalar fields, with the UNIT the
#: dataset states them in. The unit is not decoration: ``Additive`` carries
#: ``conc_wt_pct`` and ``conc_mM`` as separate fields and the formulation layer
#: reads whichever one the role needs, so writing a millimolar figure into the
#: weight-percent slot makes the inhibitor term decline the value and the whole
#: axis goes INERT -- silently, because the harness never looked at the
#: warning. Found by ``tools/inert_axis_scan.py``; it had been true for every
#: inhibitor sweep in the corpus.
ADDITIVE_OVERRIDES: Dict[str, Tuple[str, str, str]] = {
    "oxidizer_wt_pct": ("hydrogen_peroxide", "oxidizer", "conc_wt_pct"),
    # Du 2004 reports vol% rather than wt%. For dilute aqueous H2O2 the two are
    # within a few percent, which is well inside the scatter of a digitized
    # figure, so the series is usable -- but the alias must be declared or the
    # whole oxidizer axis is silently dropped.
    "h2o2_vol_pct": ("hydrogen_peroxide", "oxidizer", "conc_wt_pct"),
    "inhibitor_mM": ("benzotriazole", "inhibitor", "conc_mM"),
}


@dataclass
class Score:
    dataset: str
    film: str
    n: int
    axes: List[str] = field(default_factory=list)
    shape_mape: Optional[float] = None
    shape_max: Optional[float] = None
    loo_mape: Optional[float] = None
    flat_mape: Optional[float] = None       # baseline: predict the mean
    error: Optional[str] = None
    #: rows the model DECLINED to predict because a regime gate fired, i.e.
    #: the pack states its constants were not measured in that regime. These
    #: are excluded from the score: grading a declared silence as a wrong
    #: answer punishes the model for the honesty that makes it usable, and
    #: rewards a future edit that removes the gate and guesses instead.
    gated: int = 0
    gated_reason: Optional[str] = None
    #: Axes the run explicitly DECLINED to predict (`core.declined_axes`), and
    #: which of them this dataset actually sweeps. When the second set is
    #: non-empty, the shape score is not a test of the physics on that axis --
    #: the prediction is constant along it by declaration, so the free scale
    #: fits the measured mean and the block reproduces the `flat` baseline
    #: exactly. Recorded rather than acted on: dropping such a block would be
    #: the forbidden selection, while silently scoring it asserts a refusal as
    #: a prediction.
    declined_axes: List[str] = field(default_factory=list)
    declined_axes_swept: List[str] = field(default_factory=list)
    #: Mean |deviation from group mean| / group mean over rows that are
    #: IDENTICAL in every condition, as a percentage — the dataset's own
    #: reproducibility, and therefore a FLOOR on the error any model can
    #: achieve on it. None when the dataset repeats no condition, which is the
    #: common case: one rate per condition leaves the floor unmeasured, and an
    #: unmeasured floor must not be read as a floor of zero.
    replicate_scatter: Optional[float] = None
    #: Median (measured / predicted) over the dataset's rows — the absolute
    #: scale the data implies, against the scale the pack declares. 1.0 means
    #: calibrated; 39.0 means the model under-predicts absolute rate by 39x
    #: while its SHAPE may still be excellent. None when the dataset's own
    #: notes forbid absolute comparison (benchtop coupons, scaled units,
    #: shear-rheological polishing), where a ratio would be meaningless rather
    #: than merely unknown.
    scale_ratio: Optional[float] = None

    @property
    def scale_is_calibrated(self) -> Optional[bool]:
        """Is absolute rate within a factor of ~3 of measurement?

        Shape and scale are independent failures: ep3161098b1 scores 7.1% shape
        while under-predicting absolute rate by 139x. A report that shows only
        shape hides that completely. None means the dataset forbids absolute
        comparison, not that the answer is no.
        """
        if self.scale_ratio is None:
            return None
        return 0.33 <= self.scale_ratio <= 3.0

    @property
    def at_noise_floor(self) -> Optional[bool]:
        """Is the error already at the dataset's own reproducibility?

        True means further fitting on this dataset is fitting its noise, and a
        shape error that looks poor is not evidence of a broken term. None means
        the dataset has no replicates, so the question cannot be answered — not
        that the answer is no.
        """
        if self.shape_mape is None or self.replicate_scatter is None:
            return None
        return self.shape_mape <= self.replicate_scatter * 1.3

    @property
    def beats_flat(self) -> Optional[bool]:
        """Does the physics beat 'predict the average'? If not, it has added
        nothing beyond a number someone could have guessed."""
        if self.shape_mape is None or self.flat_mape is None:
            return None
        return self.shape_mape < self.flat_mape

    def as_dict(self) -> Dict[str, Any]:
        return {
            "dataset": self.dataset, "film": self.film, "n": self.n,
            "axes": self.axes,
            "shape_mape_percent": (None if self.shape_mape is None
                                   else round(self.shape_mape, 1)),
            "shape_max_percent": (None if self.shape_max is None
                                  else round(self.shape_max, 1)),
            "leave_one_out_mape_percent": (None if self.loo_mape is None
                                           else round(self.loo_mape, 1)),
            "predict_the_mean_mape_percent": (None if self.flat_mape is None
                                              else round(self.flat_mape, 1)),
            "beats_predicting_the_mean": self.beats_flat,
            "replicate_scatter_percent": (
                None if self.replicate_scatter is None
                else round(self.replicate_scatter, 1)),
            "at_own_noise_floor": self.at_noise_floor,
            "scale_ratio_measured_over_predicted": (
                None if self.scale_ratio is None
                else round(self.scale_ratio, 2)),
            "scale_is_calibrated": self.scale_is_calibrated,
            "gated_points": self.gated,
            "gated_reason": self.gated_reason,
            "declined_axes": self.declined_axes,
            "declined_axes_this_dataset_sweeps": self.declined_axes_swept,
            "error": self.error,
        }


def _measured(row: Dict[str, Any]) -> Optional[float]:
    """Measured rate in A/min, whatever unit the file records."""
    for key, scale in (("mrr_a_per_min", 1.0),
                       ("measured_mrr_angstrom_per_min", 1.0),
                       ("mrr_nm_per_min", 10.0),
                       ("measured_mrr_nm_per_min", 10.0)):
        if row.get(key) is not None:
            return float(row[key]) * scale
    for key in ("mrr_nm_per_hour", "measured_mrr_nm_per_hour"):
        if row.get(key) is not None:
            return float(row[key]) * 10.0 / 60.0
    return None


#: Phrases with which a dataset's own notes declare its absolute values
#: incomparable — benchtop coupons, scaled units, shear-rheological polishing
#: rather than CMP. Established by the Kp audit; see
#: tests/test_inherited_kp_is_not_the_problem.py, which pins the resulting set.
_NO_ABSOLUTE = re.compile(
    r"절대값\s*(비교\s*금지|대조에?는?\s*(당연히\s*)?부적합|비교\s*부적합)"
    r"|in_scope:\s*false|절대\s*MRR.*의미\s*없|스케일된\s*단위")


def _forbids_absolute_comparison(doc: Dict[str, Any]) -> bool:
    blob = str(doc.get("notes", "")) + " " + str(doc.get("source", ""))
    return bool(_NO_ABSOLUTE.search(blob)) or doc.get("in_scope") is False


def _scale_ratio(doc: Dict[str, Any],
                 rows: List[Dict[str, Any]]) -> Optional[float]:
    """Median measured/predicted — the absolute scale the data implies.

    Shape error asks whether the model ranks conditions correctly; this asks
    whether it gets the rate right at all. They fail independently, and a report
    showing only shape hides the second failure entirely.

    Returns None when the dataset's own notes forbid absolute comparison, where
    a ratio would be meaningless rather than merely unknown.

    Reporting only. Nothing here feeds the score.
    """
    if _forbids_absolute_comparison(doc):
        return None
    ratios: List[float] = []
    for row in rows:
        measured = _measured(row)
        try:
            predicted = _predict(doc, row)
        except Exception:
            continue
        if measured and predicted:
            ratios.append(measured / predicted)
    if not ratios:
        return None
    return float(statistics.median(ratios))


def _replicate_scatter(rows: List[Dict[str, Any]]) -> Optional[float]:
    """The dataset's own reproducibility, as a percentage.

    Rows that are IDENTICAL in every condition are replicates: their spread is
    measurement noise, and no model can score better than it. Returns None when
    no condition repeats — one rate per condition leaves the floor UNMEASURED,
    which is not the same as a floor of zero and must not be reported as one.

    Reporting only. Nothing here feeds the score.
    """
    groups: Dict[Any, List[float]] = {}
    for row in rows:
        key = (tuple(sorted((k, str(v))
                            for k, v in (row.get("overrides") or {}).items())),
               row.get("pressure_psi"), row.get("rpm_platen"),
               row.get("rpm_head"))
        rate = _measured(row)
        if rate:
            groups.setdefault(key, []).append(rate)

    deviations: List[float] = []
    for rates in groups.values():
        if len(rates) > 1:
            mean = sum(rates) / len(rates)
            deviations += [abs(r - mean) / mean for r in rates]
    if not deviations:
        return None
    return 100 * sum(deviations) / len(deviations)


def _varying_axes(rows: List[Dict[str, Any]]) -> List[str]:
    axes = []
    if len({r.get("pressure_psi") for r in rows}) > 1:
        axes.append("pressure")
    if len({r.get("rpm_platen") for r in rows}) > 1:
        axes.append("velocity")
    keys = set()
    for row in rows:
        keys |= set((row.get("overrides") or {}).keys())
    for key in sorted(keys):
        values = {(r.get("overrides") or {}).get(key) for r in rows}
        values = {v for v in values if v is not None}
        if len(values) > 1:
            axes.append(key)
    return axes


def _recipe_for(doc: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
    """Build a recipe dict for one measured condition."""
    overrides = dict(row.get("overrides") or {})
    slurry: Dict[str, Any] = {"pack": doc.get("pack")}
    abrasive: Dict[str, Any] = {}
    additives: List[Dict[str, Any]] = []
    leftovers: Dict[str, Any] = {}

    for key, value in overrides.items():
        if key in ADDITIVE_OVERRIDES and value is not None:
            name, role, unit_field = ADDITIVE_OVERRIDES[key]
            additives.append({"name": name, "role": role,
                              unit_field: float(value)})
        elif key in OVERRIDE_TO_RECIPE:
            section, field_name = OVERRIDE_TO_RECIPE[key]
            (abrasive if section == "abrasive" else slurry)[field_name] = value
        else:
            # Anything the recipe has no field for goes through params:, which
            # is the documented owner-override path.
            leftovers[key] = value

    if abrasive:
        slurry["abrasive"] = abrasive
    if additives:
        slurry["additives"] = additives

    tool = {
        "pressure_psi": row.get("pressure_psi"),
        "rpm_platen": row.get("rpm_platen"),
        "rpm_head": row.get("rpm_wafer") or row.get("rpm_head")
                    or row.get("rpm_platen"),
        "time_s": 60.0,
    }
    if doc.get("center_offset_m") is not None:
        tool["center_offset_m"] = doc["center_offset_m"]
    if row.get("flow_ml_min") is not None:
        tool["flow_ml_min"] = row["flow_ml_min"]

    film = doc.get("film")
    if film in (None, "", "other"):
        film = PACK_FILM.get(str(doc.get("pack") or ""))
    recipe: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": slurry,
        "tool": tool,
    }
    # A dataset may declare parameters that belong to ITS formulation rather
    # than to the pack it borrows: Du 2004's oxidizer peak is 1 vol% because
    # its slurry has no glycine, while the pack's 3.0 wt% was measured on a
    # glycine system. Merging those would be wrong in both directions, so the
    # dataset states its own and they are applied on top.
    for key, value in (doc.get("pack_overrides") or {}).items():
        leftovers.setdefault(key, value)
    if doc.get("wafer_radius_m"):
        recipe["wafer"]["diameter_mm"] = float(doc["wafer_radius_m"]) * 2000.0
    if leftovers:
        recipe["params"] = leftovers
    return recipe


def _predict(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    """Model rate in A/min at Kp = pack default, or None if it cannot run."""
    value, _, _ = _predict_with_gate(doc, row)
    return value


def _predict_with_gate(
    doc: Dict[str, Any], row: Dict[str, Any]
) -> Tuple[Optional[float], Optional[str], Set[str]]:
    """Rate in A/min, the reason if the model DECLINED, and which axes it
    declined.

    A regime gate is not a failure and not a prediction: the pack is stating
    that its constants were never measured in this regime, so the returned
    rate does not respond to the gated axis at all. Scoring such a row as a
    wrong answer would make silence look like error and would reward removing
    the gate in favour of an extrapolation with a known-wrong sign.

    The third return value is the machine-readable form of that statement
    (`core.declined_axes`). The prose reason is not enough on its own: this
    scorer recognised only the word "GATED" and therefore read an inhibitor
    term that was REFUSED -- with a citation and a measured refutation -- as an
    ordinary prediction that happened to be flat.
    """
    from cmp_sim.api import run_recipe

    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None, None, set()
    value = result.get("removal_rate_A_per_min")
    value = None if value in (None, 0) else float(value)
    warns = result.get("warnings") or []
    gate = next((w for w in warns if "GATED" in w), None)
    return value, gate, declined_axes(warns)


def _why_unscorable(doc: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    """Name the missing input rather than reporting a generic failure.

    A dataset that cannot be scored is not necessarily a model defect: some
    published tables omit the down force entirely, and the honest response is
    to say which field is missing rather than to invent a pressure.
    """
    if not any(r.get("pressure_psi") for r in rows):
        return ("the source table states no down force, so P*V cannot be "
                "formed; scoring it would require inventing a pressure")
    if not any(r.get("rpm_platen") for r in rows):
        return "the source table states no platen speed"
    return "the model could not run this dataset's conditions"


def _mape(pairs: List[Tuple[float, float]]) -> float:
    return 100.0 * sum(abs(p - m) / m for m, p in pairs) / len(pairs)


def score_dataset(path: Path) -> Score:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    film = doc.get("film") or PACK_FILM.get(str(doc.get("pack") or "")) or "?"
    score = Score(dataset=path.stem, film=str(film),
                  n=len(rows), axes=_varying_axes(rows),
                  replicate_scatter=_replicate_scatter(rows),
                  scale_ratio=_scale_ratio(doc, rows))
    if len(rows) < 3:
        score.error = f"only {len(rows)} usable rows"
        return score

    measured, predicted = [], []
    gated_rows = 0
    # A gate only invalidates a SCORE if the gated axis is one the dataset
    # varies. When oxidizer is held constant across every row, the switched-off
    # term is a constant factor that cancels out of a shape comparison — the
    # dataset is still a fair test of the axes it does vary (size, pressure).
    # Declining those would silence three good datasets to say something about
    # an axis they never probe.
    gate_matters = any(a in score.axes for a in
                       ("oxidizer_wt_pct", "h2o2_vol_pct"))
    all_declined: Set[str] = set()
    for row in rows:
        value, gate, declined = _predict_with_gate(doc, row)
        all_declined |= declined
        if value is None:
            score.error = _why_unscorable(doc, rows)
            return score
        if gate:
            gated_rows += 1
            score.gated_reason = score.gated_reason or gate
            if gate_matters:
                # Declared silence, not a prediction. Excluded and counted, so
                # a gate can never quietly drop the rows a model does badly on.
                continue
        measured.append(_measured(row))
        predicted.append(value)
    score.gated = gated_rows
    score.declined_axes = sorted(all_declined)
    score.declined_axes_swept = sorted(all_declined & set(score.axes))

    if gate_matters and len(measured) < 3:
        score.error = (
            f"{gated_rows} of {len(rows)} rows are in a regime this pack "
            f"declares it has no constants for, leaving {len(measured)} "
            "scorable rows on an axis this dataset actually varies. The model "
            "is declining to predict them rather than extrapolating: "
            + (score.gated_reason or ""))
        return score

    # SHAPE: one free scale, fitted by least squares through the origin in the
    # ratio sense, so the number reflects trend rather than calibration.
    scale = sum(m * p for m, p in zip(measured, predicted)) / sum(p * p for p in predicted)
    pairs = [(m, scale * p) for m, p in zip(measured, predicted)]
    score.shape_mape = _mape(pairs)
    score.shape_max = max(100.0 * abs(p - m) / m for m, p in pairs)

    # BASELINE: predict the dataset mean. If the physics cannot beat this, the
    # physics is not contributing.
    mean = sum(measured) / len(measured)
    score.flat_mape = _mape([(m, mean) for m in measured])

    # PREDICTION: leave-one-out on the same single free parameter.
    errs = []
    for i in range(len(rows)):
        others = [(m, p) for j, (m, p) in enumerate(zip(measured, predicted)) if j != i]
        s = sum(m * p for m, p in others) / sum(p * p for _, p in others)
        errs.append(abs(s * predicted[i] - measured[i]) / measured[i])
    score.loo_mape = 100.0 * sum(errs) / len(errs)
    return score


def score_all(only_non_pv: bool = False) -> List[Score]:
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = doc.get("conditions") or []
        if only_non_pv:
            pv = (len({r.get("pressure_psi") for r in rows}) > 1
                  or len({r.get("rpm_platen") for r in rows}) > 1)
            if pv:
                continue
        out.append(score_dataset(path))
    return out


def report(scores: List[Score]) -> str:
    lines = [f"{'dataset':44s} {'film':8s} {'n':>3s} {'shape%':>7s} "
             f"{'LOO%':>7s} {'mean%':>7s} {'repl%':>7s} {'scale':>7s} "
             f"{'beats':>6s}  axes",
             "-" * 136]
    for s in sorted(scores, key=lambda x: (x.shape_mape is None,
                                           x.shape_mape or 0)):
        if s.error:
            lines.append(f"{s.dataset[:44]:44s} {s.film[:8]:8s} {s.n:3d} "
                         f"{'--':>7s} {'--':>7s} {'--':>7s} {'--':>7s} "
                         f"{'--':>7s} {'--':>6s}  {s.error}")
            continue
        # blank, not zero, where the dataset repeats no condition: the floor is
        # unmeasured there and printing 0.0 would assert a floor of zero
        repl = (f"{s.replicate_scatter:7.1f}" if s.replicate_scatter is not None
                else f"{'':>7s}")
        # '-' where the dataset's own notes forbid absolute comparison: the
        # ratio is meaningless there, not merely unknown
        scale = (f"{s.scale_ratio:6.2f}x" if s.scale_ratio is not None
                 else f"{'-':>7s}")
        beats = "yes" if s.beats_flat else "NO"
        if s.at_noise_floor:
            beats = "floor"
        lines.append(
            f"{s.dataset[:44]:44s} {s.film[:8]:8s} {s.n:3d} "
            f"{s.shape_mape:7.1f} {s.loo_mape:7.1f} {s.flat_mape:7.1f} "
            f"{repl} {scale} {beats:>6s}  {','.join(s.axes)}")
    ran = [s for s in scores if s.shape_mape is not None]
    if ran:
        lines.append("")
        lines.append(f"{len(ran)}/{len(scores)} datasets scored, "
                     f"{sum(s.n for s in ran)} measured points")
        lines.append(f"median shape error {sorted(s.shape_mape for s in ran)[len(ran)//2]:.1f}%, "
                     f"median leave-one-out {sorted(s.loo_mape for s in ran)[len(ran)//2]:.1f}%")
        floored = [s for s in ran if s.at_noise_floor]
        with_repl = [s for s in ran if s.replicate_scatter is not None]
        if with_repl:
            lines.append(
                f"repl% is the dataset's OWN reproducibility — a floor on any "
                f"model's error. Measured on {len(with_repl)}/{len(ran)}; blank "
                f"means UNMEASURED, not zero.")
        if floored:
            lines.append(
                f"'floor' = error already at that floor, so further fitting "
                f"there fits noise: " + ", ".join(s.dataset for s in floored))
        scaled = [s for s in ran if s.scale_ratio is not None]
        if scaled:
            off = [s for s in scaled if not s.scale_is_calibrated]
            lines.append(
                f"scale = median measured/predicted ABSOLUTE rate, a failure "
                f"independent of shape. Comparable on {len(scaled)}/{len(ran)}; "
                f"'-' means the dataset's own notes forbid it.")
            if off:
                # rank by how far off in EITHER direction: 0.08x (over-predicts
                # 12x) is as wrong as 12x, and sorting on the raw ratio would
                # bury every over-prediction at the bottom of the list
                worst = sorted(off, key=lambda s: -max(s.scale_ratio or 1,
                                                       1 / (s.scale_ratio or 1))
                               )[:4]
                lines.append(
                    f"absolute rate off by >3x on {len(off)}: "
                    + ", ".join(f"{s.dataset} ({s.scale_ratio:.1f}x)"
                                for s in worst))
        lost = [s.dataset for s in ran
                if not s.beats_flat and not s.at_noise_floor]
        if lost:
            lines.append(f"does NOT beat predicting the mean on {len(lost)}: "
                         + ", ".join(lost[:6]))
    return "\n".join(lines)
