"""Literature back-testing harness.

Validation datasets are inherited from ``legacy/validation/datasets/*.yaml``
(FabSim corpus: patent example tables and open-access paper figures, each with a
``source:`` block and a ``read_method`` of ``table`` or ``digitized``).

What this harness measures
--------------------------
Preston has exactly one free constant, Kp. A dataset that sweeps pressure and
velocity at fixed chemistry therefore tests the *shape* P*V predicts, with Kp
fitted by least squares on that group:

    Kp* = argmin_K sum_i (K * x_i - y_i)^2 = <x,y> / <x,x>

where ``x_i`` is the geometry/kinematics term (area-averaged P*V for condition i,
with Kp = 1) and ``y_i`` the measured removal rate. Reported error is
``100*(Kp* x_i - y_i)/y_i``.

Conditions are grouped by their chemistry overrides so that a pressure sweep is
never mixed with an abrasive-concentration sweep: within one group only P and
the rotation speeds move, which is precisely the Preston hypothesis.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

from cmp_sim.core.legacy_bridge import LEGACY_DATASETS
from cmp_sim.core.units import psi_to_pa
from cmp_sim.models import preston

#: chemistry-neutral keys: these may vary inside one Preston group
_PV_KEYS = ("pressure_psi", "rpm_platen", "rpm_wafer", "velocity_mps")

DEFAULT_WAFER_RADIUS_M = 0.150
DEFAULT_CENTER_OFFSET_M = 0.200


@dataclass
class GroupFit:
    dataset: str
    group: str
    n: int
    kp_fit: float
    max_abs_error_pct: float
    mape_pct: float
    errors_pct: List[float] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    source: str = ""
    in_scope: Optional[bool] = None
    read_method: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "dataset": self.dataset, "group": self.group, "n": self.n,
            "kp_fit_m_per_pa": self.kp_fit,
            "max_abs_error_pct": round(self.max_abs_error_pct, 2),
            "mape_pct": round(self.mape_pct, 2),
            "read_method": self.read_method,
            "in_scope": self.in_scope,
        }


def _group_key(cond: Dict[str, Any]) -> str:
    """Everything that is NOT pressure/speed defines the chemistry group."""
    ov = {k: v for k, v in (cond.get("overrides") or {}).items() if k not in _PV_KEYS}
    return json.dumps(ov, sort_keys=True, ensure_ascii=False) or "{}"


def _kinematic_term(cond: Dict[str, Any], radius_m: float, r_cc: float) -> float:
    """Area-averaged P*V [Pa*m/s] expressed as nm/min at Kp = 1."""
    rpm_w = cond.get("rpm_wafer", cond.get("rpm_platen"))
    rpm_p = cond.get("rpm_platen", rpm_w)
    if rpm_w is None or rpm_p is None:
        raise ValueError(f"condition has no rotation speed: {cond.get('label')}")
    _, mrr, _ = preston.mrr_radial_nm_per_min(
        radius_m, r_cc, float(rpm_w), float(rpm_p), 1.0,
        psi_to_pa(float(cond["pressure_psi"])), n_radial=21)
    return float(np.mean(mrr))


def fit_dataset(path: Path, min_points: int = 3) -> List[GroupFit]:
    """Fit Preston to every chemistry group in one dataset file."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    conds = [c for c in (raw.get("conditions") or []) if c.get("mrr_nm_per_min")]
    radius_m = float(raw.get("wafer_radius_m", DEFAULT_WAFER_RADIUS_M))
    r_cc = float(raw.get("center_offset_m", DEFAULT_CENTER_OFFSET_M))

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for c in conds:
        if "pressure_psi" not in c:
            continue
        groups.setdefault(_group_key(c), []).append(c)

    out: List[GroupFit] = []
    for key, cs in groups.items():
        distinct = {(c.get("pressure_psi"), c.get("rpm_platen"), c.get("rpm_wafer")) for c in cs}
        if len(cs) < min_points or len(distinct) < min_points:
            continue          # not a P*V sweep — nothing for Preston to be tested on
        x = np.array([_kinematic_term(c, radius_m, r_cc) for c in cs])
        y = np.array([float(c["mrr_nm_per_min"]) for c in cs])
        kp = float(x @ y / (x @ x))
        err = 100.0 * (kp * x - y) / y
        out.append(GroupFit(
            dataset=Path(path).stem, group=key, n=len(cs), kp_fit=kp,
            max_abs_error_pct=float(np.abs(err).max()),
            mape_pct=float(np.abs(err).mean()),
            errors_pct=[float(e) for e in err],
            labels=[str(c.get("label", "")) for c in cs],
            source=str(raw.get("source", "")).strip(),
            in_scope=raw.get("in_scope"),
            read_method=str(cs[0].get("read_method", "")),
        ))
    return out


#: This package's own datasets, which take precedence over the inherited ones.
OWN_DATASETS = Path(__file__).resolve().parents[1] / "data" / "validation" / "datasets"


def dataset_paths(directory: Optional[Path] = None) -> List[Path]:
    """Every validation dataset, this package's own plus the inherited ones.

    Searching only the legacy directory silently hid the datasets added here,
    so the library reported two passing datasets while the CLI, which knew
    about both directories, reported four. A same-named file in the local
    directory wins.
    """
    if directory is not None:
        d = Path(directory)
        return sorted(p for p in d.glob("*.yaml") if not p.stem.startswith("_"))

    found: Dict[str, Path] = {}
    for folder in (LEGACY_DATASETS, OWN_DATASETS):       # later wins
        folder = Path(folder)
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.yaml")):
            if not p.stem.startswith("_"):
                found[p.stem] = p
    return [found[k] for k in sorted(found)]


def run_all(directory: Optional[Path] = None, min_points: int = 3) -> List[GroupFit]:
    fits: List[GroupFit] = []
    for p in dataset_paths(directory):
        fits.extend(fit_dataset(p, min_points=min_points))
    return fits


def best_fit_per_dataset(fits: List[GroupFit]) -> Dict[str, GroupFit]:
    """Largest sweep per dataset (ties broken by lower MAPE)."""
    best: Dict[str, GroupFit] = {}
    for f in fits:
        cur = best.get(f.dataset)
        if cur is None or (f.n, -f.mape_pct) > (cur.n, -cur.mape_pct):
            best[f.dataset] = f
    return best
