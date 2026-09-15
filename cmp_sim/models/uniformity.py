"""P5 — radial non-uniformity: velocity field, zone pressure, starvation.

Within-wafer non-uniformity (WIWNU) is what a fab actually complains about,
and it comes from three separable places.

1. Kinematics — and why it is *not* the cause
---------------------------------------------
For a rotary polisher the relative speed at wafer radius `r` and angle `theta`
is (inherited `kinematics.relative_velocity`, Lai 2001 Eq. 2.12)

    |v| = sqrt( (omega_p r_cc)^2 + 2 omega_p r_cc (omega_p - omega_w) r cos(theta)
                + (omega_p - omega_w)^2 r^2 )

When `omega_w = omega_p` the cross and quadratic terms vanish and
`|v| = omega_p r_cc` — identical everywhere on the wafer. Even off-match, the
wafer's own rotation averages `theta` out, so the *time-averaged* speed varies
only weakly with radius. Hence:

    **uniform pressure + equal rpm => zero WIWNU, structurally.**

Radial non-uniformity therefore has to come from the pressure field or from
slurry supply, not from the velocity field. This is asserted as a test, and it
is the reason zone pressure is the main knob a tool engineer reaches for.

2. Zone pressure
----------------
A multi-zone carrier imposes a piecewise-constant `P(r)`
(`legacy/sim/tier1_empirical/wiwnu.py: p_zoned`); the retaining ring adds a
flat-punch edge concentration `P(r) = P_0 [1 + a (r/R)^n]`
(`p_edge_concentration`), which is why unbalanced rings give edge-fast wafers.

Reported metrics (all area-weighted, `legacy .. wiwnu`):
`half_range_pct`, `sigma_pct`, `three_sigma_pct`, `edge_center`. Non-uniformity
is defined on *removed thickness*, not on rate, whenever a time is given.

3. Slurry starvation
--------------------
Fresh slurry arrives at the wafer edge and is dragged inward, so the centre is
fed by what survives the transit. The relevant comparison is the residence time
of slurry under the wafer against the time the pad needs to sweep it out:

    t_transit  ~ R_wafer / V_rel              [s]   (how long slurry stays under the wafer)
    Q_required ~ (swept pad area) * (film thickness needed per pass)

A dimensionless supply number is formed as the delivered flow divided by the
flow the sweep consumes,

    S = Q_delivered / (A_swept * V_rel * h_film)

Starvation shows up as a centre-slow profile because the centre is furthest
from the supply. The inherited lubrication modules give the film thickness and
the regime: `cmp_lubrication_regime.hydrodynamic_length` (l_hd = mu U / p),
`lambda_ratio` and `regime_from_lambda` (boundary / mixed / full-film),
`cof_stribeck`. In CMP, `l_hd` is tens of nm against a micron-scale pad
roughness, so `lambda << 1` and contact is boundary-lubricated — which is
precisely why abrasives touch the wafer at all, and why a fully hydrodynamic
film would mean no removal.

**Honesty note.** The *shape* of the starvation profile (how sharply the centre
falls off at a given flow) is not derivable from these first principles alone;
it depends on groove pattern and injection geometry. This module computes the
supply number and flags starvation risk, and applies a radial profile only when
a pack supplies a calibrated starvation length. Otherwise it reports the risk
and leaves the profile alone rather than inventing a shape.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from cmp_sim.core.legacy_bridge import install  # noqa: F401

import cmp_lubrication_regime as lub   # legacy/sim/tier2_physics/
import pad_groove_wear_flow as flow    # legacy/sim/tier2_physics/
import kinematics as kin               # legacy/sim/tier1_empirical/
import wiwnu as legacy_wiwnu           # legacy/sim/tier1_empirical/

NAME = "uniformity"


# ── velocity field ───────────────────────────────────────────────────
def relative_speed_profile(wafer_radius_m: float, center_offset_m: float,
                           rpm_head: float, rpm_platen: float,
                           n_radial: int = 81, n_theta: int = 360
                           ) -> Tuple[np.ndarray, np.ndarray]:
    """Angle-averaged relative speed [m/s] vs radius (inherited kinematics)."""
    rs = np.linspace(0.0, float(wafer_radius_m), int(n_radial))
    th = np.linspace(0.0, 2.0 * math.pi, int(n_theta), endpoint=False)
    w_w, w_p = kin.rpm_to_rads(rpm_head), kin.rpm_to_rads(rpm_platen)
    out = np.empty_like(rs)
    for i, r in enumerate(rs):
        _, _, v = kin.relative_velocity(r * np.cos(th), r * np.sin(th),
                                        w_w, w_p, float(center_offset_m))
        out[i] = float(np.mean(v))
    return rs, out


def velocity_nonuniformity_pct(wafer_radius_m: float, center_offset_m: float,
                               rpm_head: float, rpm_platen: float) -> float:
    """Area-weighted sigma% of the speed field alone."""
    rs, v = relative_speed_profile(wafer_radius_m, center_offset_m,
                                   rpm_head, rpm_platen)
    return float(legacy_wiwnu.wiwnu(rs, v)["sigma_pct"])


# ── pressure field ───────────────────────────────────────────────────
def edge_pressure_profile(pressure_pa: float, amplitude: float = 0.5,
                          exponent: float = 8.0):
    """Flat-punch edge concentration P(r_norm) = P0 [1 + a r^n] (inherited)."""
    return legacy_wiwnu.p_edge_concentration(float(pressure_pa),
                                             amp=float(amplitude), n=float(exponent))


def zone_pressure_profile(zone_edges_norm, zone_pressures_pa):
    """Piecewise-constant multi-zone carrier pressure (inherited)."""
    return legacy_wiwnu.p_zoned(zone_edges_norm, zone_pressures_pa)


def metrics(radius_m: np.ndarray, values: np.ndarray) -> Dict[str, float]:
    """Area-weighted non-uniformity metrics (inherited definitions).

    ``edge_center`` is edge rate / centre rate, which the inherited routine
    computes unguarded. With a stationary head the centre rate is zero, so it
    emitted a numpy divide-by-zero warning and an ``inf``. The ratio is
    genuinely undefined there, so it is reported as ``None`` rather than as a
    number that would propagate into a summary table.
    """
    vals = np.asarray(values, float)

    # Every non-uniformity metric is a percentage OF THE MEAN, so when nothing
    # is being removed anywhere they are all 0/0. Uniformity is undefined, not
    # zero: reporting 0% would read as a perfectly uniform wafer.
    if not np.any(vals):
        return {"mean": 0.0, "half_range_pct": None, "sigma_pct": None,
                "three_sigma_pct": None, "edge_center": None,
                "undefined_because": (
                    "the removal rate is zero everywhere, so every "
                    "non-uniformity metric is a ratio to a zero mean")}

    with np.errstate(divide="ignore", invalid="ignore"):
        raw = legacy_wiwnu.wiwnu(np.asarray(radius_m, float), vals)
    out: Dict[str, Optional[float]] = {}
    for k, v in raw.items():
        v = float(v)
        out[k] = None if not np.isfinite(v) else v
    if out.get("edge_center") is None and vals.size and vals[0] == 0.0:
        out["undefined_because"] = (
            "the centre removal rate is zero, so edge/centre has no value")
    return out


# ── slurry supply ────────────────────────────────────────────────────
@dataclass
class SupplyState:
    """Slurry supply diagnosis for one operating point."""
    flow_m3_s: float
    swept_area_m2: float
    mean_speed_m_s: float
    film_thickness_m: float
    required_flow_m3_s: float
    supply_number: float
    residence_time_s: float
    lambda_ratio: float
    regime: str
    cof: float
    starved: bool
    interface_volume_cm3: float = 0.0
    mean_residence_time_s: float = 0.0
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "flow_ml_min": round(self.flow_m3_s * 6.0e7, 2),
            "supply_number": round(self.supply_number, 4),
            "required_flow_ml_min": round(self.required_flow_m3_s * 6.0e7, 2),
            "wafer_pass_time_s": round(self.residence_time_s, 4),
            "interface_volume_cm3": round(self.interface_volume_cm3, 4),
            "mean_residence_time_s": round(self.mean_residence_time_s, 4),
            "film_thickness_nm": round(self.film_thickness_m * 1e9, 3),
            "lambda_ratio": round(self.lambda_ratio, 5),
            "lubrication_regime": self.regime,
            "friction_coefficient": round(self.cof, 4),
            "starved": self.starved,
            "notes": self.notes,
            "warnings": self.warnings,
        }


#: supply number below which the wafer is judged slurry-starved
STARVATION_THRESHOLD = 1.0


def diagnose_supply(*, flow_ml_min: float, wafer_radius_m: float,
                    mean_speed_m_s: float, pressure_pa: float,
                    viscosity_pa_s: float, pad_roughness_m: float,
                    groove_depth_m: Optional[float] = None,
                    groove_area_fraction: float = 0.25,
                    contact_area_fraction: float = 0.01) -> SupplyState:
    """Diagnose slurry supply and the lubrication regime.

    The film thickness comes from the hydrodynamic length `l_hd = mu U / p`,
    the regime from `lambda = h/sigma`, both inherited and self-tested.
    """
    notes: List[str] = []
    warnings: List[str] = []

    q = float(flow_ml_min) * 1.0e-6 / 60.0                      # ml/min -> m3/s
    area = math.pi * float(wafer_radius_m) ** 2

    h_film = float(lub.hydrodynamic_length(viscosity_pa_s, mean_speed_m_s, pressure_pa))
    d_eff = float(lub.delta_eff(pad_roughness_m,
                                groove_depth_m if groove_depth_m else pad_roughness_m,
                                contact_area_fraction))
    so = float(lub.cmp_sommerfeld(viscosity_pa_s, mean_speed_m_s, pressure_pa, d_eff))
    lam = float(lub.lambda_ratio(h_film, pad_roughness_m))
    regime = str(lub.regime_from_lambda(lam))
    cof = float(lub.cof_stribeck(so))

    # ── how much flow the interface actually needs ────────────────────
    # Mu et al. 2016 (Microelectron. Eng. 157, 60) treat the pad-wafer
    # interface as a stirred reactor of volume V = V_land + V_groove, where
    # V_land   = (1 - GFQ) * A_wafer * h_land       (space over the land)
    # V_groove = GFQ       * A_wafer * D_groove     (space in the grooves)
    # with GFQ the groove area fraction. The mean residence time is tau = V/Q,
    # so the flow needed to renew that volume once per wafer pass is V / t_pass,
    # with t_pass = R_wafer / V_rel the time slurry spends under the wafer.
    #
    # Using the inherited implementation directly (slurry_volumes_cm3) keeps
    # the geometry identical to the published reactor model rather than
    # substituting an invented criterion.
    gfq = float(groove_area_fraction)
    h_land_um = max(float(pad_roughness_m), float(h_film)) * 1e6
    d_groove_um = (float(groove_depth_m) * 1e6) if groove_depth_m else h_land_um
    _v_land, _v_groove, v_total_cm3 = flow.slurry_volumes_cm3(
        d_groove_um, gfq, h_land_um,
        wafer_diameter_mm=2.0 * float(wafer_radius_m) * 1e3)
    v_land_m3 = _v_land * 1.0e-6
    v_total_m3 = v_total_cm3 * 1.0e-6

    # Which of the two volumes sets the supply requirement?
    # The land gap is the layer actually dragged through the contact and
    # consumed there, so it is what must be replenished every wafer pass.
    # The grooves are a reservoir an order of magnitude larger: they buffer
    # and re-circulate slurry rather than being swept out each pass, so
    # including them would demand thousands of ml/min and declare every real
    # process starved (a 300 mm tool runs 150-300 ml/min). The groove volume
    # is therefore reported as residence time, not added to the requirement.
    residence = float(wafer_radius_m) / max(float(mean_speed_m_s), 1e-12)
    required = v_land_m3 / residence if residence > 0 else float("inf")
    supply = q / required if required > 0 else float("inf")
    tau_s = (v_total_m3 / q) if q > 0 else float("inf")

    notes.append(
        f"hydrodynamic film {h_film * 1e9:.2f} nm vs pad roughness "
        f"{pad_roughness_m * 1e9:.0f} nm -> lambda = {lam:.4f} ({regime}); "
        f"Sommerfeld {so:.3e}, COF {cof:.3f}")
    notes.append(
        f"interface volume {v_total_cm3:.3f} cm^3 = land {_v_land:.3f} + groove "
        f"{_v_groove:.3f} (groove area fraction {gfq:.2f}, groove depth "
        f"{d_groove_um:.0f} um) — Mu 2016 reactor model")
    notes.append(
        f"supply number {supply:.2f} = delivered {q * 6.0e7:.0f} ml/min / "
        f"{required * 6.0e7:.0f} ml/min needed to renew the land gap once per "
        f"wafer pass ({residence * 1e3:.1f} ms). Groove reservoir gives a mean "
        f"residence time of {tau_s:.2f} s over the whole interface volume.")

    starved = supply < STARVATION_THRESHOLD
    if starved:
        warnings.append(
            f"slurry-starved: supply number {supply:.2f} < {STARVATION_THRESHOLD}. "
            "The wafer centre is fed last, so expect a centre-slow radial profile "
            "and degraded WIWNU. The magnitude of that droop is geometry-specific "
            "(groove pattern, injection point) and is NOT predicted here — only "
            "the risk is. Raise the flow or lower the platen speed.")
    if lam > 3.0:
        warnings.append(
            f"lambda = {lam:.2f} > 3 means a full hydrodynamic film separates pad "
            "and wafer. Abrasives would no longer contact the surface, so removal "
            "would collapse — this operating point is outside the model's regime.")
    return SupplyState(flow_m3_s=q, swept_area_m2=area, mean_speed_m_s=mean_speed_m_s,
                       film_thickness_m=h_film, required_flow_m3_s=required,
                       supply_number=supply, residence_time_s=residence,
                       interface_volume_cm3=v_total_cm3, mean_residence_time_s=tau_s,
                       lambda_ratio=lam, regime=regime, cof=cof, starved=starved,
                       notes=notes, warnings=warnings)


def starvation_profile(radius_m: np.ndarray, wafer_radius_m: float,
                       supply_number: float,
                       starvation_length_m: Optional[float]) -> Optional[np.ndarray]:
    """Radial supply weighting, or ``None`` when uncalibrated.

    Slurry enters at the edge and is consumed as it travels inward, so the
    surviving fraction decays with the distance travelled from the rim:

        w(r) = s + (1 - s) * exp( -(R - r) / L )

    with `s = min(supply_number, 1)` the fraction available even at the centre
    and `L` a starvation length. `L` is a calibration parameter (it encodes
    groove pattern and injection geometry); with no value for it this returns
    ``None`` rather than inventing a shape.
    """
    if starvation_length_m is None or starvation_length_m <= 0:
        return None
    s = min(float(supply_number), 1.0)
    r = np.asarray(radius_m, float)
    return s + (1.0 - s) * np.exp(-(float(wafer_radius_m) - r) / float(starvation_length_m))
