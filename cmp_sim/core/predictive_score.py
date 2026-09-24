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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

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

#: Overrides that are additives rather than scalar fields.
ADDITIVE_OVERRIDES = {
    "oxidizer_wt_pct": ("hydrogen_peroxide", "oxidizer"),
    # Du 2004 reports vol% rather than wt%. For dilute aqueous H2O2 the two are
    # within a few percent, which is well inside the scatter of a digitized
    # figure, so the series is usable -- but the alias must be declared or the
    # whole oxidizer axis is silently dropped.
    "h2o2_vol_pct": ("hydrogen_peroxide", "oxidizer"),
    "inhibitor_mM": ("benzotriazole", "inhibitor"),
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
            name, role = ADDITIVE_OVERRIDES[key]
            additives.append({"name": name, "role": role,
                              "conc_wt_pct": float(value)})
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
    from cmp_sim.api import run_recipe

    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None
    value = result.get("removal_rate_A_per_min")
    return None if value in (None, 0) else float(value)


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
                  n=len(rows), axes=_varying_axes(rows))
    if len(rows) < 3:
        score.error = f"only {len(rows)} usable rows"
        return score

    measured, predicted = [], []
    for row in rows:
        value = _predict(doc, row)
        if value is None:
            score.error = _why_unscorable(doc, rows)
            return score
        measured.append(_measured(row))
        predicted.append(value)

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
             f"{'LOO%':>7s} {'mean%':>7s} {'beats':>6s}  axes",
             "-" * 118]
    for s in sorted(scores, key=lambda x: (x.shape_mape is None,
                                           x.shape_mape or 0)):
        if s.error:
            lines.append(f"{s.dataset[:44]:44s} {s.film[:8]:8s} {s.n:3d} "
                         f"{'--':>7s} {'--':>7s} {'--':>7s} {'--':>6s}  {s.error}")
            continue
        lines.append(
            f"{s.dataset[:44]:44s} {s.film[:8]:8s} {s.n:3d} "
            f"{s.shape_mape:7.1f} {s.loo_mape:7.1f} {s.flat_mape:7.1f} "
            f"{'yes' if s.beats_flat else 'NO':>6s}  {','.join(s.axes)}")
    ran = [s for s in scores if s.shape_mape is not None]
    if ran:
        lines.append("")
        lines.append(f"{len(ran)}/{len(scores)} datasets scored, "
                     f"{sum(s.n for s in ran)} measured points")
        lines.append(f"median shape error {sorted(s.shape_mape for s in ran)[len(ran)//2]:.1f}%, "
                     f"median leave-one-out {sorted(s.loo_mape for s in ran)[len(ran)//2]:.1f}%")
        lost = [s.dataset for s in ran if not s.beats_flat]
        if lost:
            lines.append(f"does NOT beat predicting the mean on {len(lost)}: "
                         + ", ".join(lost[:6]))
    return "\n".join(lines)
