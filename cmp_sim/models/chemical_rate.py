"""P4 — chemical term: surface reaction, passivation, pH and temperature.

The coupling channel
--------------------
.. warning::
   The name "softening" is inherited and is not always literal. An oxidiser can
   make the surface HARDER than the underlying metal — in Cu/H2O2 chemistry it
   grows Cu2O/CuO, and bulk cuprite indents at 17.0-17.5 GPa against ~1.2 GPa
   for electroplated copper (Ihnfeldt & Talbot 2008, doi:10.1149/1.2903293).
   What matters for removal is that the modified layer is *mechanically
   different* and is continuously regenerated, not that it is soft. Do not
   introduce a constraint anywhere that the modified surface hardness must be
   at or below the bulk value: the only direct measurement in this exact
   chemistry violates it.

Chemistry does not remove material in CMP; it *softens* the top few
nanometres so the abrasive can. From P3's single-particle derivation the
groove cross-section goes as `H^(-3/2)`, so the entire chemical layer reaches
the mechanical model through one scalar:

    chemical conditions -> effective surface hardness ratio H_eff/H_0
    MRR multiplier      = (H_0 / H_eff)^(3/2)

Nothing in the kinematics or contact model is touched. Softening the surface
4x raises removal 4^1.5 = 8x.

Relative, never absolute
------------------------
A pack's `kp_m_per_pa` is back-calculated from a published rate measured with
*that* slurry — oxidizer, inhibitor and all. Multiplying in an absolute
chemical term counts the same chemistry twice. Every term here is therefore a
ratio against the pack's reference composition (`*_ref` keys) and is exactly
1.0 there. In the inherited project this mistake collapsed a Cu rate 20x
before it was caught, which is why the unity constraint is enforced by test.

Film-specific mechanisms (inherited implementation, `legacy/sim/chemistry.py`)
------------------------------------------------------------------------------
* **Oxidizer** — Langmuir coverage `theta(C) = KC/(1+KC)`, with one free
  parameter `K`. Two branches: promotion (`theta/theta_ref`, e.g. W with
  Fe/H2O2) and passivation (`(1-theta)/(1-theta_ref)`, e.g. Cu where thick
  passivation slows removal). Both carry an additive *mechanical floor*
  `phi`: at zero oxidizer the abrasive still removes material, and a
  purely multiplicative term would wrongly predict zero rate.
* **Inhibitor** — Langmuir coverage of BTA-class molecules blocks sites,
  weighting removal by the free fraction.
* **Ceria chemical tooth** — Si-O-Ce chemisorption (DFT -111 to -258 kJ/mol)
  is mechanistically different from silica physisorption (-20 to -40), and
  the term is enabled only for ceria. The same coefficient must never be
  carried across abrasive chemistries.
* **pH softening** — real but the weakest link: how a pH shift translates into
  effective hardness is material-specific and largely unmeasured, so it is
  applied only when a pack states the coefficient explicitly.

Temperature (added here)
------------------------
Surface reaction rates follow Arrhenius,

    k(T) = A exp(-Ea / (R T))    =>    k(T)/k(T_ref) = exp(-(Ea/R)(1/T - 1/T_ref))

so a chemically limited process accelerates with temperature while a purely
mechanical one does not. Typical CMP activation energies are 20-80 kJ/mol; the
value must come from the pack with a source. Platen temperature rises from
frictional work, so this term is what makes a run temperature-sensitive.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from cmp_sim.core.legacy_bridge import install  # noqa: F401

from sim import chemistry as legacy_chemistry  # legacy/sim/chemistry.py

NAME = "chemical_rate"

#: MRR ~ H^(-3/2); from the plastic-plowing geometry, not a tuned parameter
SOFTENING_EXPONENT = legacy_chemistry.SOFTENING_EXPONENT

GAS_CONSTANT_J_PER_MOL_K = 8.314462618
KELVIN_OFFSET = 273.15

#: English descriptions of the inherited term names
TERM_MEANING = {
    "oxidizer": "oxidizer coverage (Langmuir) relative to the reference composition",
    "inhibitor": "inhibitor/passivator surface coverage blocking removal sites",
    "ceria_tooth": "ceria Si-O-Ce chemical-tooth activity (ceria only)",
    "ph_softening": "pH-driven surface softening (linear, unverified)",
}


def hardness_ratio_to_mrr_factor(h_eff_over_h0: float) -> float:
    """(H_0/H_eff)^(3/2) — the single chemistry-to-mechanics channel."""
    if h_eff_over_h0 <= 0:
        raise ValueError("hardness ratio must be positive")
    return float(h_eff_over_h0) ** (-SOFTENING_EXPONENT)


def arrhenius_factor(temp_c: float, temp_ref_c: float,
                     activation_energy_kj_per_mol: float) -> float:
    """k(T)/k(T_ref) = exp(-(Ea/R)(1/T - 1/T_ref)), temperatures in Celsius in."""
    t = float(temp_c) + KELVIN_OFFSET
    t_ref = float(temp_ref_c) + KELVIN_OFFSET
    if t <= 0 or t_ref <= 0:
        raise ValueError("absolute temperature must be positive")
    ea = float(activation_energy_kj_per_mol) * 1.0e3
    return math.exp(-(ea / GAS_CONSTANT_J_PER_MOL_K) * (1.0 / t - 1.0 / t_ref))


def langmuir_coverage(conc: float, k: float) -> float:
    """theta = KC/(1+KC). Saturates, which is the point: above ~1/K more
    additive changes almost nothing, so a term that keeps rising is wrong."""
    kc = float(k) * float(conc)
    return kc / (1.0 + kc) if kc > 0 else 0.0


def ph_response(ph: float, ph_peak: float, width: float,
                floor: float = 0.0) -> float:
    """Rate response to pH, normalised to 1.0 at the peak.

        f(pH) = floor + (1 - floor) * exp( -((pH - pH_peak)/w)^2 )

    Why a peak with a floor, and why the peak is an INPUT
    ----------------------------------------------------
    Measured pH sweeps in this repository do not share a shape:

    ===============================  ==============  =========
    system                           shape           span
    ===============================  ==============  =========
    ceria on oxide (Dandu 2009)      peak at pH 4-5  81x
    ceria on oxide (Netzband 2020)   rises to pH 10  1.9x
    charged silica (CN109609035B)    falls from pH 2 22x
    silica + additive (Li 2021)      peak at pH 11   1.2x
    Cu alkaline (US9200180B2)        falls from 6.2  3.4x
    ===============================  ==============  =========

    Two interior peaks at completely different pH, two monotone decays, and an
    81x span against a 1.2x span. **No single pH function can produce all of
    these**, so the peak position must be a property of the
    abrasive/film/additive system and has to be supplied, not fitted. That is
    the same discipline the oxidizer term uses, for the same reason: fitting a
    peak position from data on one side of it is not identifiable.

    The floor matters as much as the peak. Dandu's rate at pH 8-10 is still
    ~650 A/min against a 3500 A/min peak; with floor = 0 the model predicts
    essentially zero there and the error is -100% on those points. Physically
    the abrasive still grinds at the wrong pH — the chemistry is a modulation,
    not an on/off switch.

    Fitted per dataset with the peak taken as given (two free parameters, width
    and floor, plus the overall scale): median 17.6% shape error against 42.8%
    with the term inactive, and every one of the five beats "predict the
    dataset mean" — which four of them did NOT before.

    Why the floor is ASYMMETRIC
    ---------------------------
    Dandu's own numbers rule out a symmetric floor: pH 2 gives 43 A/min (1.2%
    of the 3504 A/min peak) while pH 10 gives 643 (18%). One floor cannot be
    both, and forcing it to be costs 18 points of error (35.8% symmetric vs
    17.9% with the floor applied only above the optimum).

    The asymmetry has a mechanism rather than being a fitting trick. Below the
    optimum the loss is electrostatic — the abrasive and the film approach the
    same charge state, particles stop attaching, and removal genuinely
    collapses. Above it the surfaces repel, but alkaline hydrolysis keeps
    softening the film (the Cook 1990 mechanism), so a floor survives. The
    floor therefore models "chemistry still works, attachment does not", which
    only applies on the alkaline side.
    """
    if width <= 0:
        raise ValueError(f"pH response width must be positive, got {width}")
    floor = min(max(float(floor), 0.0), 1.0)
    bell = math.exp(-(((float(ph) - float(ph_peak)) / float(width)) ** 2))
    if float(ph) < float(ph_peak):
        return bell
    return floor + (1.0 - floor) * bell


def ph_factor_relative_to_reference(ph: float, ph_ref: float, ph_peak: float,
                                    width: float, floor: float = 0.0) -> float:
    """pH response NORMALISED to 1.0 at the pack's reference pH.

    Why the normalisation is not optional
    -------------------------------------
    Every pack's Kp was back-calculated from a rate measured at that pack's own
    ``ph_ref``, so the chemistry at ph_ref is already inside Kp. Applying the
    raw peak-normalised response on top multiplies it in a second time: for
    sti_ceria (ph_ref 5.5, optimum 4.5) the raw term is 0.574, so the model
    would report 57% of the rate the pack was calibrated to produce — at the
    exact condition where it should reproduce it exactly.

    Dividing by the response at ph_ref makes the term a RELATIVE correction:
    exactly 1.0 at the calibration point, above 1.0 when moving toward the
    optimum, below it when moving away. The shape — the part the measured
    sweeps constrain — is unchanged, because a constant divisor cancels out of
    every ratio.
    """
    at_ref = ph_response(float(ph_ref), ph_peak, width, floor)
    if at_ref <= 1e-9:
        raise ValueError(
            f"the pH response is ~0 at the pack's reference pH {ph_ref} "
            f"(optimum {ph_peak}, width {width}): the pack cannot be calibrated "
            "at a pH its own response curve says is dead")
    return ph_response(float(ph), ph_peak, width, floor) / at_ref


def peaked_oxidizer_response(conc: float, peak_conc: float, k: float) -> float:
    """Oxidizer response that RISES, peaks, then falls — normalised to 1.0 at
    the peak.

        f(C) = [KC/(1+KC)] * exp(-C/Cd),   Cd = peak_conc * (1 + K*peak_conc)

    Why this shape
    --------------
    Two competing effects, each with a mechanism:

    * **Promotion.** Removal needs an oxidised surface layer to abrade, and
      surface coverage follows Langmuir: ``KC/(1+KC)``. This dominates at low
      concentration and saturates.
    * **Passivation.** The same oxide keeps thickening. Past a point the film
      is thicker than the abrasive can cut per pass, and the exponential is the
      standard limited-growth penalty on the abradable fraction.

    Why the peak position is not a free parameter
    ---------------------------------------------
    Setting ``d(ln f)/dC = 0`` at ``C = peak_conc`` gives

        1/C - K/(1+KC) - 1/Cd = 0   =>   Cd = peak_conc * (1 + K*peak_conc)

    so the decay scale is *determined* by the measured peak position and K.
    That leaves ONE free parameter (K), which is the whole reason this form is
    usable: the project's own history is that a peaked curve with both the
    position and the shape free is degenerate when data sit on one side only.
    The peak position must therefore come from a measurement, never from a fit.

    Verified against Du 2004, *J. Electrochem. Soc.* **151**(4), G230,
    doi:10.1149/1.1648029, Fig. 1, read off the
    original PDF: 6 points, 0-10 vol% H2O2, peak at 1 vol%. With the peak
    pinned at the paper's own 1 vol%, K = 8 reproduces the set to 5.6% MAPE.
    A free-peak fit prefers 0.52 vol% and does only marginally better, which is
    exactly the weak identification the Du dataset file warns about: there is
    one point on the rising limb, so the peak HEIGHT and the decay are pinned
    but its POSITION is not.
    """
    c = float(conc)
    cp = float(peak_conc)
    kk = float(k)
    if c <= 0:
        return 0.0
    if cp <= 0 or kk <= 0:
        raise ValueError(
            "a peaked oxidizer response needs a positive measured peak "
            f"concentration and rate constant, got peak={cp}, K={kk}")
    decay = cp * (1.0 + kk * cp)
    f = (kk * c / (1.0 + kk * c)) * math.exp(-c / decay)
    f_peak = (kk * cp / (1.0 + kk * cp)) * math.exp(-cp / decay)
    return f / f_peak if f_peak > 0 else 0.0


@dataclass
class ChemicalEffect:
    factor: float
    terms: Dict[str, float] = field(default_factory=dict)
    active: bool = False
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"factor": round(self.factor, 5), "active": self.active,
                "terms": {k: round(v, 5) for k, v in self.terms.items()},
                "notes": self.notes, "warnings": self.warnings}


#: The inherited chemistry layer documents itself in Korean. Its notes carry
#: real information (which branch fired, which constant came from where), so
#: they are mapped to English rather than dropped. Numbers are preserved by
#: appending the original tail when no phrase matches.
_PHRASE_MAP = (
    ("화학층 비활성", "chemistry layer inactive: this pack declares no chemical parameters, so composition is still lumped inside Kp"),
    ("화학 항들을 독립으로 보고 곱했다", "chemical terms multiplied as independent; pH-adsorption and oxidizer-ceria redox couplings are not modelled"),
    ("기계 하한", "oxidizer mechanical floor: at zero oxidizer the abrasive still removes material, so the term is additive, not purely multiplicative. The default sits in the 0.12-0.27 band observed across four independent metal systems and is NOT a measurement of this system"),
    ("흡착상수를", "inhibitor adsorption constant looked up for this (inhibitor, film) pair from electrochemical and quantum-chemical data, Langmuir form"),
    ("억제제", "inhibitor surface coverage computed from the Langmuir isotherm relative to the reference concentration"),
    ("고농도 감쇠 형상", "the high-concentration roll-off shape (inhibitor_strength_k) has no literature value and is a calibration target"),
    ("세리아 chemical tooth", "ceria chemical tooth: Ce3+ active-site fraction drives Si-O-Ce chemisorption, decomposed into a chemical and a residual mechanical path, since ceria remains a hard oxide even with no active sites"),
    ("pH 연화", "pH softening: linear, unverified mapping from pH to effective surface hardness"),
    ("기준=현재 농도로 폴백", "no reference concentration in the pack, so the reference fell back to the current value: changing this additive will NOT change the result. Add the reference concentration to the pack"),
    ("적용 범위를 벗어났다", "outside the validity range of this term"),
    ("건너뜀", "term skipped: a required constant is missing"),
)


_NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*[A-Za-z%/]{0,12}")


def _numeric_detail(body: str) -> str:
    """Pull the quantities out of an inherited note so they are not lost.

    Stripping non-ASCII characters leaves punctuation debris, so the numbers
    (with any trailing unit) are extracted explicitly instead.
    """
    found = [m.group(0).strip() for m in _NUMBER_RE.finditer(body)]
    seen, uniq = set(), []
    for f in found:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return f" [values: {', '.join(uniq[:8])}]" if uniq else ""


def _translate(note: str) -> str:
    """Render an inherited-layer note in English, preserving its numbers."""
    flagged = "⚠" in note
    body = note.replace("⚠", "").strip()
    prefix = "caution: " if flagged else ""
    for needle, english in _PHRASE_MAP:
        if needle in body:
            return f"{prefix}{english}{_numeric_detail(body)}"
    return f"{prefix}[inherited chemistry layer, untranslated] {body}"


def chemical_factor(resolved, temp_c: Optional[float] = None) -> ChemicalEffect:
    """Compute the chemistry multiplier for a resolved recipe.

    Wraps ``legacy/sim/chemistry.py: chemistry_factor`` unchanged and adds the
    Arrhenius temperature term.
    """
    eff = legacy_chemistry.chemistry_factor(resolved.pack)
    notes = [_translate(n) for n in eff.notes]
    warnings = [n for n in notes if n.startswith("caution:")]
    notes = [n for n in notes if not n.startswith("caution:")]

    terms = dict(eff.terms)
    factor = float(eff.factor)
    for name, value in terms.items():
        notes.append(f"{name} = {value:.4f} — {TERM_MEANING.get(name, 'see pack')}")

    if not eff.active:
        warnings.append(
            "chemistry layer inactive: this pack declares no oxidizer/inhibitor/"
            "ceria/pH-softening parameters, so slurry chemistry is still lumped "
            "inside Kp and changing the formulation will not change the result")

    # A pack may declare BOTH a Langmuir passivation constant and a Kaufman
    # peak. The Langmuir branch wins, which makes the oxidizer term fall
    # monotonically and silently contradicts the peak the same pack declares.
    # That choice is defensible - the peak's (n, C_peak) pair is degenerate
    # below the peak, while Langmuir has one identifiable parameter - but it
    # must not be invisible, or a user will read a monotonic curve as the
    # model's opinion about a system famous for having a maximum.
    has_langmuir = (resolved.has("oxidizer_passivation_K")
                    or resolved.has("oxidizer_langmuir_K"))
    peak = resolved.p_or("oxidizer_peak_wt_pct", None)
    conc = resolved.p_or("oxidizer_wt_pct", None)

    # A measured peak position turns the degenerate two-parameter peak into a
    # one-parameter curve (see peaked_oxidizer_response), so when the pack
    # states one it is USED rather than merely declared and ignored.
    peak_k = resolved.p_or("oxidizer_peak_shape_K", None)
    used_peaked = False
    if peak and peak_k and conc is not None and float(conc) > 0:
        # The inherited layer has ALREADY multiplied its own monotonic oxidizer
        # term into `factor`. Multiplying the peaked term on top would count the
        # same physics twice - the mistake that once collapsed a copper rate by
        # 20x in this project - so the old term is divided out and REPLACED.
        legacy_ox = terms.get("oxidizer")
        if legacy_ox:
            if abs(float(legacy_ox)) < 1e-9:
                warnings.append(
                    "peaked oxidizer term skipped: the inherited oxidizer term "
                    "is ~0, so it cannot be divided out without amplifying "
                    "rounding error")
                peak_k = None
            else:
                factor /= float(legacy_ox)
                terms.pop("oxidizer", None)
                notes.append(
                    f"replaced the inherited monotonic oxidizer term "
                    f"({float(legacy_ox):.4f}) with the peaked form rather than "
                    "multiplying both, which would double-count the same "
                    "surface chemistry")
    if peak and peak_k and conc is not None and float(conc) > 0:
        try:
            shape = peaked_oxidizer_response(float(conc), float(peak), float(peak_k))
        except ValueError as exc:
            warnings.append(f"peaked oxidizer term skipped: {exc}")
        else:
            floor = float(resolved.p_or("oxidizer_mechanical_floor", 0.0) or 0.0)
            # The floor is the abrasive-only rate: at zero oxidizer removal does
            # not stop, so a purely multiplicative term would predict zero.
            ox_factor = floor + (1.0 - floor) * shape
            factor *= ox_factor
            terms["oxidizer_peaked"] = ox_factor
            notes.append(
                f"peaked oxidizer response: {float(conc):g} vs measured peak at "
                f"{float(peak):g} -> {shape:.4f} of peak "
                f"(K = {float(peak_k):g}, decay scale set by the peak, not fitted)")
            if float(conc) > 3.0 * float(peak):
                warnings.append(
                    f"the oxidizer concentration ({float(conc):g}) is more than "
                    f"3x the measured peak ({float(peak):g}), far out on the "
                    "falling limb where the exponential penalty is an "
                    "extrapolation rather than a fitted shape")
            used_peaked = True

    # ── pH ──────────────────────────────────────────────────────────────
    # Before this, pH was inert: the packs carried ph_ref and ph_peak but no
    # coefficient, so scanning pH 2 to 10 returned ONE number. Against Dandu's
    # ceria/oxide sweep the model answered 1061 A/min at every pH while the
    # measurement moved 43 -> 3504 -> 643. The parameter was accepted, stored,
    # and ignored.
    ph = resolved.p_or("slurry_ph", None)
    ph_peak = resolved.p_or("ph_peak", None)
    ph_width = resolved.p_or("ph_response_width", None)
    ph_ref = resolved.p_or("ph_ref", None)
    if ph is not None and ph_peak is not None and ph_width:
        try:
            ph_floor = float(resolved.p_or("ph_mechanical_floor", 0.0) or 0.0)
            # Normalised to the pack's reference pH, not to the optimum: Kp was
            # measured at ph_ref and already contains the chemistry there.
            if ph_ref is not None:
                ph_factor = ph_factor_relative_to_reference(
                    float(ph), float(ph_ref), float(ph_peak),
                    float(ph_width), ph_floor)
            else:
                ph_factor = ph_response(float(ph), float(ph_peak),
                                        float(ph_width), ph_floor)
                warnings.append(
                    "this pack declares a pH optimum but no ph_ref, so the pH "
                    "term is normalised to the optimum rather than to the "
                    "calibration point; the absolute rate is then only correct "
                    "if Kp happens to have been measured at the optimum")
        except ValueError as exc:
            warnings.append(f"pH term skipped: {exc}")
        else:
            # The inherited layer may already carry a pH-softening term; divide
            # it out rather than stacking two pH dependencies, the same
            # double-counting guard the oxidizer branch uses.
            legacy_ph = terms.get("ph_softening")
            if legacy_ph and abs(float(legacy_ph)) > 1e-9:
                factor /= float(legacy_ph)
                terms.pop("ph_softening", None)
                notes.append(
                    f"replaced the inherited pH-softening term "
                    f"({float(legacy_ph):.4f}) with the peaked pH response "
                    "rather than multiplying both")
            factor *= ph_factor
            terms["ph_peaked"] = ph_factor
            notes.append(
                f"pH response: pH {float(ph):g} vs optimum {float(ph_peak):g} "
                f"-> {ph_factor:.4f} of peak (width {float(ph_width):g}, "
                f"floor {ph_floor:.2f}; the peak position is a pack input "
                "because measured sweeps peak at pH 2, 4.5, 10 and 11 in "
                "different systems and no one function fits all of them)")
            if abs(float(ph) - float(ph_peak)) > 2.5 * float(ph_width):
                warnings.append(
                    f"pH {float(ph):g} is more than 2.5 widths from the "
                    f"optimum ({float(ph_peak):g}), so the rate rests on the "
                    "mechanical floor and the chemical term is extrapolated")
    elif ph is not None and ph_peak is not None and not ph_width:
        warnings.append(
            f"this pack declares an optimum pH ({float(ph_peak):g}) but no "
            "ph_response_width, so pH is INERT: changing it will not change "
            "the predicted rate. Supply ph_response_width to activate the term")

    if has_langmuir and peak and not used_peaked:
        warnings.append(
            f"this pack declares an oxidizer peak at {float(peak):g} wt% but the "
            "Langmuir branch takes precedence, so the oxidizer term is monotonic "
            "and no maximum will appear in a concentration scan. The Langmuir "
            "form was chosen because it has one identifiable parameter, whereas "
            "the peak's shape exponent and peak position are degenerate when "
            "only sub-peak data exist. Supply oxidizer_peak_shape_K to use the "
            "peaked form instead. Treat a scan across the declared peak as "
            "showing the passivation branch only")
    if (conc is not None and peak and float(conc) < float(peak)
            and has_langmuir and not used_peaked):
        warnings.append(
            f"the oxidizer concentration ({float(conc):g} wt%) sits below the "
            f"declared peak ({float(peak):g} wt%), where the real system is "
            "reported to RISE with concentration while this model falls. "
            "Rankings below the peak are not trustworthy for this term")

    # ── temperature ──────────────────────────────────────────────────
    if temp_c is not None:
        ea = resolved.p_or("chem_activation_energy_kj_per_mol", None)
        t_ref = resolved.p_or("chem_temp_ref_c", None)
        if ea and t_ref is not None:
            t_factor = arrhenius_factor(temp_c, float(t_ref), float(ea))
            factor *= t_factor
            terms["temperature"] = t_factor
            notes.append(
                f"Arrhenius: {temp_c:.1f} C vs reference {float(t_ref):.1f} C with "
                f"Ea = {float(ea):.1f} kJ/mol -> {t_factor:.4f}")
        else:
            warnings.append(
                f"temperature {temp_c:.1f} C was given but this pack has no "
                "activation energy (chem_activation_energy_kj_per_mol) and/or "
                "reference temperature (chem_temp_ref_c), so the thermal response "
                "is NOT modelled — the rate shown is isothermal")

    if len(terms) > 1:
        warnings.append(
            "chemical terms are multiplied as if independent; real couplings "
            "(pH shifting inhibitor adsorption, oxidizer-ceria redox) are not modelled")

    return ChemicalEffect(factor=factor, terms=terms, active=bool(eff.active),
                          notes=notes, warnings=warnings)
