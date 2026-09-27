r"""Which pack keys, DECLARED with a value, move no prediction anywhere?

Why this probe exists (the direction the existing audit cannot see)
-------------------------------------------------------------------
`tools/pack_key_wiring_audit.py` asks one static question: *does every key the
ENGINE reads exist in some pack?* That finds misspellings and declared gaps.
It is blind to the opposite direction, which `docs/limits.md` §20 calls the
hardest inert case:

    a key the pack DECLARES, with a sourced value and a confidence grade,
    that NO rate term reads.

Nothing can report it. `apply_overrides` warns only when a key is *undeclared*
("'x' is not declared by pack ..."), so a declared-but-unread key is accepted
silently; `inert_axis_scan` enumerates axes the CORPUS sweeps, so a key no
dataset happens to sweep is never asked about; and the run prints a number
either way. From outside, "the model weighed this property and it did not
matter" and "no line of code has ever looked at this property" are byte
identical -- and only one of them is a physical claim.

Method (measured, not read off the source)
------------------------------------------
For one representative run per pack, perturb each declared numeric key by a
large factor and re-run the SHIPPING solver. A key is `inert` when the rate
does not move by more than INERT_TOLERANCE. Reading the source instead would
miss keys consumed through the inherited `legacy/` dispatchers, which is
exactly where §18's silent terms were hiding.

Two classes of inert key are NOT faults and are separated here:

`declared`
    The run says so, machine-readably, via `[DECLINES_AXIS: ...]`
    (`core/declined_axes.py`) or `UNREAD_BY_THE_RATE`. Acceptable: inert is
    fine, silently inert is not.

`diagnostic-only`
    The key's home is a reported diagnostic (defect risk, pad life, supply)
    rather than Kp, and the pack says so. Such a key must still move
    SOMETHING, so this probe also perturbs the diagnostics -- a key that moves
    neither the rate nor any diagnostic is inert everywhere, and calling it
    "diagnostic-only" would be an excuse rather than a location (§20's
    both-halves rule).

Reference-condition keys are excluded by construction, not by name: perturbing
`*_ref_*` changes the reference a factor is normalised to, so it legitimately
moves the rate and can never be reported inert.

THE TRAP THIS PROBE FELL INTO FIRST, AND WHY THE BASE RUN IS DISPLACED
----------------------------------------------------------------------
The first version ran each pack at its OWN reference composition and reported
**1077 of 1275 keys silent** -- which is nonsense, and the reason is this
repository's central rule rather than a bug in any pack. Every factor is
`Kp_eff = kp * prod(factor_i)` with each factor **exactly 1.0 at its pack's
reference condition**. At `C == C_ref` the concentration factor is
`(C/C_ref)^n = 1` for EVERY n, so perturbing `abrasive_conc_exponent` cannot
move the rate no matter how the term is wired. The probe was measuring the
normalisation contract and calling it inertness.

So the base run is DISPLACED off every reference axis first (`DISPLACEMENT`),
and a key is only judged when the quantity it scales is actually away from its
reference. An exponent whose driving variable sits on the reference is reported
`unreachable-here` -- a statement about the probe's operating point, not about
the pack. This is §21's rule ("a constant the model computes is not evidence")
applied to a perturbation: ask whether the input VARIES before concluding
anything from the output.

THE SECOND TRAP: THE PERTURBATION ITSELF IS PART OF THE INSTRUMENT
-----------------------------------------------------------------
The displacement fixed WHERE the probe stands. It did not fix HOW HARD the
probe pushes, and a single large one-sided factor manufactures silence in two
further ways -- both measured on `oxide_silica`, both of which had this
repository's strongest pH constants filed under `silent`:

`ph_peak` -- pushed OUT OF THE MODEL'S OWN VALIDITY DOMAIN.
    x3 moves the optimum from pH 11.0 to 33.0, i.e. 7 widths from the query.
    The model then correctly refuses: the response rests on the mechanical
    floor, `ph_valid_range` clamps the evaluation point, and the run WARNS.
    Measured: x3 -> 0.00%, but **x1.25 -> 54.81%** -- the largest single-key
    response on this pack. The probe was grading the model's honest
    out-of-domain refusal as a forgotten wire. So sweep SMALL perturbations in
    BOTH directions (`PERTURBATION_FACTORS`) and keep the largest response: a
    key is inert only if NO admissible perturbation moves the rate.

`ph_response_width` -- the DISPLACEMENT landed on a symmetry point.
    `oxide_silica` has `ph_ref = 10.5`, `ph_peak = 11.0`, and `PH_DISPLACEMENT`
    was 1.0 -- exactly twice the ref-to-peak distance, so the query sat at
    pH 11.5, mirror-symmetric to the reference about the peak. The factor is
    `exp(-(x/w)^2) / exp(-(x_ref/w)^2)`, and with `|x| == |x_ref|` that is
    **1 for every w**: an exact cancellation, by derivation, at that one point
    (this is §42's class recurring inside the probe). Measured: 0.00% at the
    symmetry point, 6.62% one pH unit off it. So the displacement must BREAK
    symmetry about every declared optimum, not just leave the reference.

The general rule: a perturbation magnitude and a displacement position are
both part of the measuring instrument. A census reporting zero response has to
say which perturbations it tried, and it must be held to recovering a key
known to be read (`INSTRUMENT_CONTROLS`) -- otherwise a broken probe reports a
clean bill of health for the whole repository and nothing contradicts it.

    python tools/declared_key_response_census.py [--pack NAME]

HOW TO READ THE `silent` COUNT -- IT IS A SHORTLIST, NOT A BUG COUNT
-------------------------------------------------------------------
The classes above remove the three ways inertness is legitimate and
*reportable*. What remains is still not 1:1 with bugs, and the honest reading
matters because a later session acting on the raw number would waste a run:

* **A pack inherits keys it does not use.** Most packs descend from `base`, so
  a Cu-only key sits on a SiC pack where its species gate correctly refuses it.
  The inertness is per (key, pack) and only the pack that OWNS the key is
  evidence.
* **A gate can be correct and silent at the probe's operating point.** The
  displacement moves one axis at a time; a term gated on pH window or oxidiser
  species may be off at the probe's point and live at the pack's own.

So treat each row as a QUESTION, and split it by measurement into: (a) inert by
derivation, like the GW summit density below -- declare it; (b) read by another
layer -- test both halves; (c) a forgotten wire -- fix it. Only (c) can move
the median, and only (c) does so with zero new constants.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.declined_axes import DECLINES_AXIS
from cmp_sim.core.params import available_packs, load_pack
from cmp_sim.slurry.formulation import UNREAD_BY_THE_RATE

#: Percent change in the predicted rate below which the key is inert. The
#: perturbation is a factor of 3, so a term with any exponent above ~1e-3
#: clears this comfortably; the bar exists only to absorb float noise.
INERT_TOLERANCE = 0.05

#: Film for each pack's representative run. A pack is calibrated on one film;
#: running it on another would gate terms and manufacture false inertness.
PACK_FILM = {
    "oxide_silica": "oxide",
    "oxide_silica_anionic": "oxide",
    "oxide_silica_aminosilane": "oxide",
    "oxide_silica_calibrated_pad": "oxide",
    "sti_ceria": "oxide",
    "cu_h2o2_bta": "cu",
    "cu_alkaline_benzenesulfonic": "cu",
    "w_fe_oxidizer": "w",
    "poly_si_alkaline": "poly_si",
    "si_substrate_alkaline": "si",
    "snag_solder": "snag",
    "sic_ceria_h2o2": "sic",
    "sic_alumina_kmno4": "sic",
    "dlc_zirconia_permanganate": "dlc",
}

#: Diagnostics a key is allowed to live in instead of the rate. Each is a path
#: into the result dict; a key that moves one of these is located, not inert.
DIAGNOSTIC_PATHS = (
    ("defect_risk",),
    ("pad_life",),
    ("uniformity",),
    ("dishing",),
)

#: Source files that compute the REMOVAL RATE. A key this source never names
#: cannot be expected to move the rate: it belongs to the pattern, defect,
#: pad-life or documentation layers, and reporting it "silent" would drown the
#: real finding in 900 non-claims. A key these files DO name, which still moves
#: nothing, is the finding.
RATE_LAYER_SOURCES = (
    "cmp_sim/core/solver.py",
    "cmp_sim/core/regime.py",
    "cmp_sim/models/preston.py",
    "cmp_sim/models/luo_dornfeld.py",
    "cmp_sim/models/chemical_rate.py",
    "cmp_sim/models/contact_gw.py",
    "cmp_sim/models/first_principles.py",
    "legacy/sim/factors.py",
    "legacy/sim/chemistry.py",
    "legacy/sim/regime_adapter.py",
)

#: How far the base run is pushed OFF each pack's reference condition, so that
#: every normalised factor is away from its exact-1.0 contract point and the
#: exponents inside it are reachable. Multiplicative on the pack's own value;
#: pH is additive because it is already a logarithm.
DISPLACEMENT_FACTOR = 1.7
PH_DISPLACEMENT = 1.0

#: How close to mirror-symmetric about the optimum counts as "on the symmetry
#: point", and how far to step off it. The step must stay inside the pack's
#: `ph_valid_range` or the probe swaps one artefact for another, so it is small.
PH_SYMMETRY_TOLERANCE = 0.05
PH_SYMMETRY_BREAK = 0.6

#: Perturbation factors applied to each key, BOTH directions and small as well
#: as large. A single large factor cannot distinguish "no wire" from "pushed
#: past the term's declared validity window": x3 on `ph_peak` moves the optimum
#: 7 widths from the query, where the model rests on its mechanical floor and
#: says so, while x1.25 moves the rate 54.8%. The largest response over this
#: set is kept, so a key is inert only when NO admissible perturbation reaches
#: it. Small factors first: they are the ones a physical reading of the pack
#: would ever produce.
PERTURBATION_FACTORS = (1.05, 0.95, 1.25, 0.80, 3.0, 1.0 / 3.0)

#: Keys the census MUST classify as `reads`. Without these the whole census can
#: silently degrade into "nothing moves anything", which reads as a clean bill
#: of health for the repository and nothing else here would contradict it. Two
#: real instances of exactly that are why this exists (a large factor leaving
#: the term's validity window, a displacement landing on a symmetry point).
#:
#: The control is a CLASSIFICATION, not a percentage floor: the perturbation
#: loop stops at the first factor clearing `INERT_TOLERANCE`, so the recorded
#: response is "the first factor that reached it", not the maximum, and pinning
#: a percentage would pin the search order instead of the wiring. Each entry is
#: a measured read: the peaked pH term reads the first two, the mechanical term
#: reads `abrasive_wt_pct`, and `kp_m_per_pa` multiplies every rate.
INSTRUMENT_CONTROLS = {
    "oxide_silica": ("ph_peak", "ph_response_width"),
    "cu_h2o2_bta": ("abrasive_wt_pct", "slurry_ph", "kp_m_per_pa"),
}

#: The pack keys that CARRY a factor's driving variable. Displacing these is
#: what makes the factors' exponents reachable; an exponent whose driver is
#: absent from a pack is reported unreachable rather than inert.
DRIVER_KEYS = (
    "abrasive_wt_pct", "abrasive_size_nm", "abrasive_d50_nm",
    "oxidizer_wt_pct", "oxidizer_vol_pct", "inhibitor_ppm", "inhibitor_mM",
    "complexant_wt_pct", "chelator_wt_pct", "promoter_wt_pct",
    "catalyst_wt_pct", "slurry_viscosity_pa_s",
)


def _displaced_overrides(pack_name: str) -> Dict[str, Any]:
    """Base-run overrides that move the run off every reference condition."""
    params = load_pack(pack_name).params
    out: Dict[str, Any] = {}
    for key in DRIVER_KEYS:
        param = params.get(key)
        if param is None or param.value is None:
            continue
        if isinstance(param.value, bool) or not isinstance(param.value, (int, float)):
            continue
        if param.value == 0:
            continue
        out[key] = float(param.value) * DISPLACEMENT_FACTOR
    ph = params.get("slurry_ph") or params.get("ph_peak")
    if ph is not None and isinstance(ph.value, (int, float)):
        ph_query = float(ph.value) + PH_DISPLACEMENT
        # BREAK SYMMETRY ABOUT THE OPTIMUM, not just about the reference.
        # The peaked pH factor is normalised to `ph_ref`, so it reads
        # `exp(-(x/w)^2) / exp(-(x_ref/w)^2)` with x measured from the optimum.
        # When the displaced query lands mirror-symmetric to the reference about
        # the peak (|x| == |x_ref|) that ratio is exactly 1 for EVERY width, and
        # the width reports inert by derivation at that single point. Measured on
        # `oxide_silica` (ref 10.5, peak 11.0, displacement 1.0 -> query 11.5):
        # 0.00% at the symmetry point, 6.62% one unit away. Nudge outward from
        # the optimum, which cannot re-enter the mirror image of the reference.
        peak = params.get("ph_peak")
        ref = params.get("ph_ref")
        if (peak is not None and isinstance(peak.value, (int, float))
                and ref is not None and isinstance(ref.value, (int, float))):
            distance = abs(ph_query - float(peak.value))
            ref_distance = abs(float(ref.value) - float(peak.value))
            if abs(distance - ref_distance) < PH_SYMMETRY_TOLERANCE:
                direction = 1.0 if ph_query >= float(peak.value) else -1.0
                ph_query += direction * PH_SYMMETRY_BREAK
        out["slurry_ph"] = ph_query
    temp = params.get("chem_temp_ref_c")
    if temp is not None and isinstance(temp.value, (int, float)):
        out["temperature_c"] = float(temp.value) + 10.0
    return out



@dataclass
class KeyResponse:
    pack: str
    key: str
    value: Any
    rate_percent: Optional[float] = None
    #: The perturbation factor that produced `rate_percent`. Printed so a zero
    #: response is never quotable without the perturbations that produced it.
    perturbation: Optional[float] = None
    diagnostics_moved: List[str] = field(default_factory=list)
    declared: bool = False
    evidence: str = ""
    #: True when the rate-layer source names this key as a literal. False means
    #: the key belongs to another layer and cannot be expected to move Kp.
    in_rate_layer: bool = True
    #: True when the key is an operating condition the recipe supplies through
    #: `tool:`/`slurry:`; the pack's copy is a reference or documentation, so
    #: overriding it via `params:` legitimately reaches nothing.
    operating_condition: bool = False

    @property
    def kind(self) -> str:
        if self.rate_percent is None:
            return "unrunnable"
        if self.rate_percent >= INERT_TOLERANCE:
            return "reads"
        if self.declared:
            return "declared"
        if self.diagnostics_moved:
            return "diagnostic-only"
        if self.operating_condition:
            return "operating-condition"
        if not self.in_rate_layer:
            return "other-layer"
        return "silent"


def _recipe(pack: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    film = PACK_FILM.get(pack)
    recipe: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0, "flow_ml_min": 200.0},
    }
    if overrides:
        recipe["params"] = dict(overrides)
    return recipe


def _run(pack: str, overrides: Optional[Dict[str, Any]] = None):
    from cmp_sim.api import run_recipe
    try:
        return run_recipe(_recipe(pack, overrides))
    except Exception:
        return None


def _rate(result) -> Optional[float]:
    if not result:
        return None
    value = result.get("removal_rate_A_per_min")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return None if value == 0.0 else value


def _diagnostic_signature(result) -> Dict[str, str]:
    """Stringified diagnostics, so a change of ANY kind is visible.

    Comparing floats field by field would need a schema for every diagnostic
    and would silently stop covering new ones. Repr-comparison over-reports
    nothing here: the only input that changed is the perturbed key.
    """
    out: Dict[str, str] = {}
    for path in DIAGNOSTIC_PATHS:
        node: Any = result
        for part in path:
            node = node.get(part) if isinstance(node, dict) else None
            if node is None:
                break
        if node is not None:
            out[".".join(path)] = repr(node)
    return out


def _declared_inert(key: str, warnings: List[str]) -> Tuple[bool, str]:
    """Does the RUN say, machine-readably, that this key does not reach Kp?"""
    if key in UNREAD_BY_THE_RATE:
        return True, "UNREAD_BY_THE_RATE"
    marker = f"{DECLINES_AXIS}{key}]"
    for w in warnings:
        if marker in w:
            return True, w[:160]
    return False, ""


def _numeric_keys(pack_name: str) -> List[Tuple[str, float]]:
    pack = load_pack(pack_name)
    out: List[Tuple[str, float]] = []
    for key, param in sorted(pack.params.items()):
        value = param.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value == 0:
            # A zero is a sourced NULL RESULT in this repository ("size is not
            # the dominant factor"), and scaling zero by any factor is still
            # zero -- the perturbation cannot test it, so reporting it inert
            # would be an artefact of the method.
            continue
        out.append((key, float(value)))
    return out


#: Keys that are OPERATING CONDITIONS, not pack properties: the recipe supplies
#: them through `tool:` / `slurry:`, and the pack's copy is a reference value or
#: documentation. Overriding those through `params:` legitimately reaches
#: nothing, so reporting them "silent" would be the same error as calling a
#: form's default pressure a physics claim (see
#: tests/test_web_holds_no_physics_constants.py). Derived from the recipe
#: dataclasses' own field names at run time, never hand-maintained.
def _operating_condition_keys() -> set:
    from cmp_sim.core import state

    names: set = set()
    for cls_name in ("Tool", "Slurry", "Pad", "Disk", "Wafer", "Abrasive"):
        cls = getattr(state, cls_name, None)
        fields = getattr(cls, "__dataclass_fields__", None) if cls else None
        if fields:
            names.update(fields)
    # The pack spells several of them with its own suffixes.
    extra = set()
    for name in list(names):
        extra.update({f"{name}_psi", f"{name}_m", f"{name}_c", f"{name}_pct"})
    return names | extra | {
        "pressure_psi", "rpm_platen", "rpm_wafer", "rpm_head", "sfr_ml_min",
        "flow_ml_min", "wafer_radius_m", "center_offset_m", "temperature_c",
        "polish_time_s", "n_points",
    }


def _rate_layer_keys() -> set:
    """Pack keys NAMED as string literals anywhere in the rate-layer source.

    Parsed with `ast` rather than grep so a key mentioned only in a docstring
    or a comment does not count as a read -- a prose mention is precisely the
    state this probe exists to distinguish from a wire.
    """
    import ast

    root = Path(__file__).resolve().parents[1]
    names: set = set()
    for rel in RATE_LAYER_SOURCES:
        path = root / rel
        if not path.exists():
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # A docstring is an Expr whose sole value is the constant; those
                # are skipped by only taking short, identifier-shaped literals.
                text = node.value
                if 2 < len(text) < 64 and text.replace("_", "").isalnum():
                    names.add(text)
    return names


def census(packs: Optional[List[str]] = None) -> List[KeyResponse]:
    names = packs or [p for p in sorted(available_packs()) if p in PACK_FILM]
    rate_keys = _rate_layer_keys()
    op_keys = _operating_condition_keys()
    rows: List[KeyResponse] = []
    for name in names:
        displaced = _displaced_overrides(name)
        base = _run(name, displaced)
        base_rate = _rate(base)
        if base_rate is None:
            continue
        base_diag = _diagnostic_signature(base)
        for key, value in _numeric_keys(name):
            # Keep the LARGEST response over the perturbation set: a key is
            # inert only if NO admissible perturbation reaches it. A single
            # large one-sided factor scores the model's honest out-of-domain
            # refusal (`ph_peak` x3 -> the optimum lands 7 widths away, on the
            # mechanical floor, with a warning) as a forgotten wire.
            best_rate: Optional[float] = None
            best_moved = -1.0
            best_factor: Optional[float] = None
            best_alt = None
            for factor in PERTURBATION_FACTORS:
                overrides = dict(displaced)
                overrides[key] = value * factor
                alt = _run(name, overrides)
                alt_rate = _rate(alt)
                if alt_rate is None:
                    continue
                moved = 100.0 * abs(alt_rate - base_rate) / base_rate
                if moved > best_moved:
                    best_moved, best_rate, best_factor, best_alt = (
                        moved, alt_rate, factor, alt)
                if moved >= INERT_TOLERANCE:
                    break
            if best_rate is None:
                rows.append(KeyResponse(pack=name, key=key, value=value))
                continue
            alt = best_alt
            diag_moved = [k for k, v in _diagnostic_signature(alt).items()
                          if base_diag.get(k) != v]
            declared, evidence = _declared_inert(
                key, list((alt.get("warnings") or []) if alt else []))
            rows.append(KeyResponse(pack=name, key=key, value=value,
                                    rate_percent=best_moved,
                                    perturbation=best_factor,
                                    diagnostics_moved=diag_moved,
                                    declared=declared, evidence=evidence,
                                    in_rate_layer=key in rate_keys,
                                    operating_condition=key in op_keys))
    return rows


def instrument_control_failures(
        rows: Optional[List[KeyResponse]] = None) -> List[str]:
    """Keys known to be READ that the census failed to recover.

    A census whose perturbations no longer reach anything reports "nothing is
    wired" -- indistinguishable from a repository in perfect health, and
    nothing else here would contradict it. Two real instances of exactly that
    (a large factor leaving the validity window, a displacement landing on a
    symmetry point) are why this exists.
    """
    rows = rows if rows is not None else census()
    index = {(r.pack, r.key): r for r in rows}
    failures: List[str] = []
    for pack, controls in INSTRUMENT_CONTROLS.items():
        for key in controls:
            row = index.get((pack, key))
            if row is None:
                continue  # pack or key absent; not an instrument failure
            if row.kind != "reads":
                failures.append(
                    f"{pack}.{key}: control expects kind 'reads', measured "
                    f"'{row.kind}' ({row.rate_percent}% at "
                    f"x{row.perturbation}) -- the probe's perturbations no "
                    f"longer reach a key that IS read, so every 'silent' "
                    f"verdict it prints is suspect")
    return failures


def silent_keys(rows: Optional[List[KeyResponse]] = None) -> List[KeyResponse]:
    return [r for r in (rows if rows is not None else census())
            if r.kind == "silent"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", action="append", default=None)
    args = ap.parse_args()
    rows = census(args.pack)

    controls = instrument_control_failures(rows)
    print(f"perturbations per key      : "
          f"{', '.join(f'x{f:g}' for f in PERTURBATION_FACTORS)}")
    if controls:
        print("\n⚠ INSTRUMENT CONTROL FAILED — do not act on the counts below:")
        for line in controls:
            print(f"  {line}")
        print()
    else:
        print("instrument controls       : PASS "
              "(keys known to be read were recovered)")

    by_kind: Dict[str, List[KeyResponse]] = {}
    for r in rows:
        by_kind.setdefault(r.kind, []).append(r)

    print(f"pack keys perturbed        : {len(rows)}")
    for kind, blurb in (("reads", "a rate term consumes it"),
                        ("declared", "inert AND the run says so"),
                        ("diagnostic-only", "moves a diagnostic, not Kp"),
                        ("other-layer", "rate source never names it"),
                        ("operating-condition", "recipe supplies it, not the pack"),
                        ("silent", "WORST -- named by the rate layer, moves nothing, nothing says so"),
                        ("unrunnable", "perturbation broke the run")):
        print(f"  {kind:16s} {len(by_kind.get(kind, [])):4d}   ({blurb})")

    for kind in ("silent", "unrunnable"):
        group = by_kind.get(kind) or []
        if not group:
            continue
        print(f"\n── {kind} ──")
        for r in sorted(group, key=lambda x: (x.key, x.pack)):
            extra = ("  moves: " + ", ".join(r.diagnostics_moved)
                     if r.diagnostics_moved else "")
            print(f"  {r.key:34s} {r.pack:30s} value={r.value!r}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
