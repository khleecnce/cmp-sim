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
    "oxidizer_gated": ("oxidizer term switched OFF: this pH is outside the "
                       "window the pack's oxidizer constants were measured in, "
                       "and the sign of the response flips across it"),
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
                floor: float = 0.0, acid_floor: float = 0.0) -> float:
    """Rate response to pH, normalised to 1.0 at the peak.

        f(pH) = floor_side + (1 - floor_side) * exp( -((pH - pH_peak)/w)^2 )

    where ``floor_side`` is ``acid_floor`` below the optimum and ``floor``
    above it.

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

    Why the floor is ASYMMETRIC — and why BOTH sides need one
    ---------------------------------------------------------
    Dandu's own numbers rule out a symmetric floor: pH 2 gives 43 A/min (1.2%
    of the 3504 A/min peak) while pH 10 gives 643 (18%). One floor cannot be
    both, and forcing it to be costs 18 points of error (35.8% symmetric vs
    17.9% with side-specific floors).

    The asymmetry has a mechanism rather than being a fitting trick. Below the
    optimum the loss is electrostatic — the abrasive and the film approach the
    same charge state, particles stop attaching, and removal collapses toward
    the mechanical background. Above it the surfaces repel, but alkaline
    hydrolysis keeps softening the film (the Cook 1990 mechanism), so much
    more of the rate survives.

    Both floors must still be non-zero. Setting the acid side to exactly zero
    (the first version of this term) made the response decay without limit:
    at pH 2 against an optimum of 11 the factor reached 2e-4 and the model
    returned 0.0 A/min, while CN109609035B measures 109 A/min there. An
    abrasive under load removes material at any pH; the chemistry scales that,
    it does not switch it off.
    """
    if width <= 0:
        raise ValueError(f"pH response width must be positive, got {width}")
    side = acid_floor if float(ph) < float(ph_peak) else floor
    side = min(max(float(side), 0.0), 1.0)
    bell = math.exp(-(((float(ph) - float(ph_peak)) / float(width)) ** 2))
    return side + (1.0 - side) * bell


def ph_factor_relative_to_reference(ph: float, ph_ref: float, ph_peak: float,
                                    width: float, floor: float = 0.0,
                                    acid_floor: float = 0.0) -> float:
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
    at_ref = ph_response(float(ph_ref), ph_peak, width, floor, acid_floor)
    if at_ref <= 1e-9:
        raise ValueError(
            f"the pH response is ~0 at the pack's reference pH {ph_ref} "
            f"(optimum {ph_peak}, width {width}): the pack cannot be calibrated "
            "at a pH its own response curve says is dead")
    return ph_response(float(ph), ph_peak, width, floor, acid_floor) / at_ref


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
    ("전이하지 않는다", "chelator-specific oxidizer constant NOT transferred: the fitted constant belongs to a different chelator than this pack uses, and the two were measured to move the rate in OPPOSITE directions (oxalic acid up, glycine down), so the legacy oxidizer path is used instead"),
    ("적용 범위를 벗어났다", "outside the validity range of this term"),
    ("건너뜀", "term skipped: a required constant is missing"),
    # The chelator/promoter terms were never called from this wrapper before
    # 2026-09-28, so their notes had no mapping and leaked Korean the moment
    # they were wired (caught by test_inherited_notes_are_reported_in_english,
    # which is exactly the leak it was written for). Species-gate refusals are
    # mapped FIRST: they share vocabulary with the applied-term notes, and the
    # first match wins, so the more specific phrase has to come earlier.
    ("착화제 억제 항을 켜지 않는다",
     "chelator suppression term NOT applied: the fitted constant belongs to a "
     "different chelator species than this pack declares. Oxalate (+536.63) "
     "and glycine (-440.91) have OPPOSITE signs in the same regression, so "
     "the constant does not transfer across species"),
    ("착화제 억제",
     "chelator suppression: exp(-a(C - C_ref)) relative to the pack's "
     "reference glycine concentration, so the term is exactly 1.0 there and "
     "cannot double-count Kp. More glycine removes LESS copper, which is the "
     "source paper's own conclusion (glycine acts as an inhibitor rather "
     "than a dissolution promoter; regression coefficient -440.91, "
     "p=4.1e-7). Two-point fit: use the magnitude for ranking"),
    ("항을 켜지 않는다",
     "term NOT applied: its fitted species does not match the species this "
     "pack declares, and the two move the rate in opposite directions"),
    ("카복실레이트 촉진",
     "carboxylate promoter: g(C) = phi + (1-phi)(C/C_anchor)^m normalised to "
     "the pack reference, fitted on US6309560B1 TABLE 1. An independent "
     "cross-check against a different system gives a ratio 19.2% larger, so "
     "the magnitude is for ranking only"),
    ("정규화가 불가능하다",
     "term skipped: the normalisation anchor is zero or negative"),
    ("분모가 0 이하",
     "term skipped: the reference-normalised denominator is not positive"),
    ("음수가 있다",
     "term skipped: a concentration is negative"),
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


def _ph_is_inside(window: str, ph: float) -> bool:
    """Is ``ph`` inside a window written as "3 to 6" in a declared-null key?

    The window is parsed from the key NAME rather than carried separately, so
    a pack cannot declare one range and be tested against another. An
    unparseable name is treated as "outside", i.e. the cautious answer: the
    warning then says the flat response is an extrapolation.
    """
    try:
        lo_s, hi_s = window.lower().split(" to ")
        return float(lo_s) <= ph <= float(hi_s)
    except (ValueError, AttributeError):
        return False


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

    # ── regime gate on the oxidizer term ────────────────────────────────
    # The oxidizer term carries ONE sign per pack, and that sign is a property
    # of the pH branch it was measured on, not of the film. Miranda 2004's 2x2
    # measures the same copper, same slurry base, same tool, with H2O2 moving
    # in OPPOSITE directions on the two pH legs:
    #
    #     pH 4:  1.5 -> 3.5 wt% H2O2   1953 -> 2908 A/min   (+49%)
    #     pH 8:  1.5 -> 3.5 wt% H2O2   1743 ->  243 A/min   (-86%)
    #
    # with the interaction significant (p = 0.0207) and H2O2 alone not
    # (p = 0.588). The mechanism is Pourbaix: acidic H2O2 makes soluble Cu2+,
    # alkaline H2O2 above ~2.5% grows hard passivating CuO. No value of a
    # single-signed constant reproduces both legs, so refitting cannot fix it.
    #
    # A pack may therefore declare the pH window its oxidizer constant was
    # measured in. Outside that window the term is GATED: it is not silently
    # extrapolated with the wrong sign, the caller is told the model is
    # declining to predict that axis, and the reason is the measurement's
    # provenance rather than a guess. This is the inherited "declared regime
    # gap" idea — a flat response that means "no coefficient here", which must
    # never be read as "this factor does not matter".
    ox_ph_window = resolved.p_or("oxidizer_ph_window", None)
    ph_now = resolved.p_or("slurry_ph", None)
    ox_gated = False
    if ox_ph_window and ph_now is not None and len(ox_ph_window) == 2:
        lo, hi = float(ox_ph_window[0]), float(ox_ph_window[1])
        ph_now = float(ph_now)
        if not (lo <= ph_now <= hi):
            ox_gated = True
            warnings.append(
                f"oxidizer term GATED at pH {ph_now:g}: this pack's oxidizer "
                f"constants were measured between pH {lo:g} and {hi:g}, and the "
                "SIGN of the oxidizer response is known to flip across the "
                "copper Pourbaix boundary (Miranda 2004, 2x2 factorial: H2O2 "
                "1.5->3.5 wt% raises the rate 49% at pH 4 and drops it 86% at "
                "pH 8, interaction p=0.0207). The term is switched off rather "
                "than extrapolated with a sign the data contradict, so the "
                "predicted rate does NOT respond to oxidizer concentration "
                "here. This is a declared gap in the data, not a claim that "
                "oxidizer is unimportant")
    used_peaked = False
    if ox_gated:
        # Divide out the inherited monotonic oxidizer term too: leaving it in
        # would gate only the peaked branch and still apply the wrong-signed
        # Langmuir penalty, which is the failure this gate exists to stop.
        legacy_ox = terms.get("oxidizer")
        if legacy_ox and abs(float(legacy_ox)) > 1e-9:
            factor /= float(legacy_ox)
            terms.pop("oxidizer", None)
            notes.append(
                f"removed the inherited oxidizer term ({float(legacy_ox):.4f}) "
                "because the regime gate above is active: an unmeasured sign is "
                "worse than no term")
        terms["oxidizer_gated"] = 1.0
        peak_k = None
    # Zero oxidizer is a MEASURED condition, not a missing input: Du 2004's
    # first point is 0 vol%, and the inherited Langmuir returns 3.10 there --
    # i.e. "copper polishes 3x faster with no oxidizer at all", which inverts
    # the whole series and made that dataset score 157%. The peaked branch must
    # therefore handle C = 0, where it equals the mechanical floor, rather than
    # declining it and leaving the monotonic term in place.
    if peak and peak_k and conc is not None and float(conc) >= 0:
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
    # Zero oxidizer is a MEASURED condition, not a missing input: Du 2004's
    # first point is 0 vol%, and the inherited Langmuir returns 3.10 there --
    # i.e. "copper polishes 3x faster with no oxidizer at all", which inverts
    # the whole series and made that dataset score 157%. The peaked branch must
    # therefore handle C = 0, where it equals the mechanical floor, rather than
    # declining it and leaving the monotonic term in place.
    if peak and peak_k and conc is not None and float(conc) >= 0:
        try:
            shape = peaked_oxidizer_response(float(conc), float(peak), float(peak_k))
        except ValueError as exc:
            warnings.append(f"peaked oxidizer term skipped: {exc}")
        else:
            # The inherited packs spell this `oxidizer_mech_floor` (legacy
            # chemistry.py reads that name, and w_fe_oxidizer carries a
            # MEASURED 0.14 from US20110186542A1 under it). Reading only the
            # long name meant that measurement could never reach the peaked
            # branch, which would then invent the provisional 0.10 below --
            # a guess standing in front of a citation. Same failure class as
            # the pad glazing constants (STATUS §27).
            floor = float(
                resolved.p_or("oxidizer_mechanical_floor",
                              resolved.p_or("oxidizer_mech_floor", 0.0))
                or 0.0)
            # The floor is the abrasive-only rate: at zero oxidizer removal does
            # not stop, so a purely multiplicative term would predict zero.
            #
            # With no floor declared this branch returned EXACTLY 0.0 A/min at
            # zero oxidizer, against 187 A/min measured in US2011/0165777A1 --
            # the chemistry switching the process off rather than scaling it.
            # A pack that does not state its floor gets a small positive one
            # plus a warning, because "no data" must not become "no removal".
            if floor <= 0.0 and float(conc) <= 0.0:
                floor = 0.10
                warnings.append(
                    "this pack declares no oxidizer_mechanical_floor, so the "
                    "rate at zero oxidizer would be exactly 0 A/min. A "
                    "provisional floor of 10% of the peak is used instead: an "
                    "abrasive under load removes material with no oxidizer at "
                    "all (US2011/0165777A1 measures 187 A/min there). Supply "
                    "the measured zero-oxidizer rate over the peak rate to "
                    "replace this estimate")
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

    # ── chelator / promoter: two SOURCED inherited terms that were never called ──
    #
    # The inherited `chemistry_factor` only assembles four terms (oxidizer,
    # inhibitor, ceria, pH softening). Two further terms exist in the same
    # inherited module, each with its own fitted constants, species gate and
    # unit tests, and the inherited `factors.py` chi/psi path DOES call them —
    # but this wrapper never did. The consequence was not a wrong number, it
    # was SILENCE: `chelator_M` and `promoter_M` could be set to any value and
    # the predicted rate did not move at all (measured: x2 on either gives a
    # 0.00% change). An input the engine accepts, stores and ignores is the
    # failure mode `docs/derivations.md` calls out as worse than a missing
    # feature, because the result looks like a prediction about that axis.
    #
    # This adds NO constant. Both terms are already in the packs with sources:
    #   chelator_suppression_a  exp(-a(C-C_ref)), glycine, Jani 2025 control
    #                           pairs; the paper's own conclusion is that
    #                           glycine acts as an inhibitor, not a dissolution
    #                           promoter, and its regression coefficient is
    #                           -440.91 (p=4.1e-7).
    #   promoter_* (phi, m, anchor)  g(C)=phi+(1-phi)(C/C_a)^m, oxalate,
    #                           fitted on US6309560B1 TABLE 1 — a DIFFERENT
    #                           document from any Cu dataset scored here, so
    #                           switching it on is a held-out test rather than
    #                           a fit.
    # Both are species-gated inside the inherited functions (oxalate +536.63
    # and glycine -440.91 in the same regression, so the two must never share
    # a term), and both are normalised to the pack's own reference composition
    # so they are exactly 1.0 there and cannot double-count Kp.
    for _term_name, _fn in (("chelator_suppression",
                             legacy_chemistry._chelator_suppression_term),
                            ("carboxylate_promoter",
                             legacy_chemistry._carboxylate_promoter_term)):
        if _term_name in terms:                              # pragma: no cover
            continue
        # ── the DEGENERATE-REFERENCE gate (structural, not fitted) ──────
        # A reference-normalised factor is f(C) = g(C)/g(C_ref). When the
        # pack's reference concentration is ZERO the denominator is g(0) =
        # phi, the pure-mechanical floor, so EVERY non-zero concentration is
        # multiplied by 1/phi = 12.8x before its own shape is applied. That
        # amplification is not a statement about the promoter axis: it is the
        # claim "this pack's reference composition removes material only
        # mechanically". For cu_h2o2_bta that claim is FALSE and is
        # contradicted by the pack itself, whose reference carries H2O2 and
        # glycine and whose oxidizer/chelator terms are already normalised to
        # that same chemistry. Applying 1/phi on top counts the reference
        # chemistry twice — the failure that once collapsed a Cu rate 20x here.
        #
        # MEASURED, both directions (tools/jani_residual_probe.py):
        #   SHAPE of the term transfers. The residual log-slope on promoter_M
        #   over jani2025's held-out block is +0.581 +/- 0.233, and the
        #   US6309560B1-fitted term's local slope there is +0.675. Switching
        #   it on drops that block's shape error 51.2% -> 29.9% and flattens
        #   the residual slope to +0.010 — with zero new constants.
        #   MAGNITUDE of the floor does NOT transfer. The same switch moves
        #   that block's absolute scale from 0.91x (right) to 0.075x (13x
        #   over-prediction), i.e. jani's measured rates contain no 12.8x
        #   oxalate boost at all. phi was measured as 21.7 -> 278 nm/min in a
        #   BTA-free alumina system whose ONLY chemistry was the complexant;
        #   in a system that already has an oxidiser and a chelator the
        #   mechanical floor is a different number, and it is not stated
        #   anywhere in this corpus.
        #
        # So the term is HELD OFF at a zero reference and the reason is
        # reported. Fitting a per-pack phi to recover the shape gain is
        # explicitly declined: it would add a free constant to a pack that has
        # one promoter level in its own calibration, which is interpolation,
        # not physics. The unblocking datum is a measured zero-oxalate rate
        # for THIS pack's reference composition (then phi is data, not a fit).
        if _term_name == "carboxylate_promoter":
            _ref = resolved.p_or("promoter_ref_M", None)
            _now = resolved.p_or("promoter_M", None)
            if (_ref is not None and float(_ref) == 0.0
                    and _now is not None and float(_now) > 0.0):
                warnings.append(
                    "carboxylate promoter term HELD OFF: this pack's "
                    "promoter reference concentration is 0 M, so the "
                    "reference-normalised factor divides by the pure-"
                    "mechanical floor phi and multiplies every non-zero "
                    "concentration by 1/phi = 12.8x. phi was measured "
                    "(US6309560B1 TABLE 1, 21.7 -> 278.0 nm/min) in a system "
                    "whose only chemistry was the complexant, whereas this "
                    "pack's reference already carries H2O2 and glycine whose "
                    "own terms are normalised to it — applying 1/phi would "
                    "count that chemistry twice. Measured on the jani2025 "
                    "held-out block: switching the term on improves SHAPE "
                    "(51.2% -> 29.9%, residual slope +0.581 -> +0.010, "
                    "confirming the exponent m transfers) but wrecks ABSOLUTE "
                    "SCALE (0.91x -> 0.075x, refuting the floor magnitude). "
                    "The promoter axis is therefore INERT here by declaration, "
                    "not by oversight. Unblock it with a measured zero-oxalate "
                    "rate for this pack's own reference composition")
                continue
        _raw: List[str] = []
        try:
            _v = _fn(resolved.pack, _raw)
        except Exception as exc:                             # pragma: no cover
            warnings.append(f"{_term_name} term skipped: {exc}")
            continue
        for _n in (_translate(n) for n in _raw):
            (warnings if _n.startswith("caution:") else notes).append(_n)
        if _v is None:
            continue
        factor *= float(_v)
        terms[_term_name] = float(_v)

    # ── the inhibitor term: REFUSED, with the measurement that refutes it ──
    #
    # `tools/inert_axis_scan.py` found that the inhibitor axis did not reach
    # the rate AT ALL anywhere in the corpus: the scoring harness had been
    # handing a millimolar figure to `Additive.conc_wt_pct`, so the term
    # declined the value and said so in a warning nobody was reading (fixed in
    # predictive_score.ADDITIVE_OVERRIDES). Wiring it correctly is what made
    # the following measurable, and it is not good news.
    #
    # WHAT THE TERM CLAIMS. r(C) = exp(-k[theta(C) - theta(C_ref)]) with the
    # (BTA x Cu) pair constant K = 3283 L/mol (dG = -30.02 kJ/mol,
    # doi:10.2320/matertrans.m2016310, electrochemical + quantum-chemical,
    # literature-grade) and the pack's k = 3.0, which the pack itself grades
    # `unverified` with the note "no closed form in the literature -- first
    # calibration target". Relative to this pack's 1 mM reference that gives
    #     0 mM -> 9.97x,   0.5 mM -> 1.55x,   10 mM -> 0.54x.
    #
    # WHAT IS MEASURED. Hong 2007 (doi:10.1149/1.2717410, Fig. 1) polishes Cu
    # at pH 4 with 5 wt% H2O2 + glycine, BTA 0 vs 10 mM, everything else held:
    # 265 -> 220 nm/min. The measured 0/10 mM ratio is 1.21 where the term
    # asserts 18.4 -- a factor of 15 on the two-point comparison the term
    # exists to predict. A quantitative refutation, not a scatter complaint.
    #
    # WHICH CONSTANT IS WRONG IS ALREADY ON RECORD, and it is not k. The
    # pack's own note (EVIDENCE-RULES ruling #17) reports that holding k = 3.0
    # and lowering K alone to 183 L/mol reproduces [LEN00]'s 0.1 wt% point
    # exactly and its 0.25 wt% point to -11.9%. So an EQUILIBRIUM adsorption
    # constant is being used where a STEADY-STATE one is needed: under
    # polishing the Cu-BTA layer is continuously abraded away, so its coverage
    # cannot be the equilibrium coverage of a quiescent corrosion experiment.
    # That is a mechanism, and it is why re-fitting k cannot rescue the term.
    #
    # THE FIRST ATTEMPT AT THIS GATE WAS ONE-SIDED, AND THAT WAS WRONG.
    # Recorded because it is the instructive part. The argument was that with
    # theta_ref = 0.767 the factor is bounded below by exp(-k[1-theta_ref]) =
    # 0.50 above the reference, so the term "makes almost no claim" there and
    # could stay, while below the reference it climbs to exp(+k*theta_ref) =
    # 9.97 and fabricates a rate. The bound is arithmetically correct and the
    # conclusion drawn from it is not: a factor of 2 is not "no claim". On the
    # ONLY above-reference point in the entire corpus the term asserts a 1.84x
    # rate drop from 0 to 10 mM where Hong measures 1.21x -- it OVERSTATES by
    # 1.53x on the one datum available to test it. Keeping the above-reference
    # half also broke hong2007's noise-floor status (shape 14.8% -> 24.0%
    # against its own 13.0% replicate scatter) and moved the corpus median
    # 18.9% -> 19.5%, i.e. a refuted constant was being paid for in score.
    #
    # The lesson generalises: a BOUND on a term's magnitude is not evidence
    # that the term is harmless inside that bound. Only a measurement is, and
    # the single measurement available refutes the term on both sides of the
    # reference. So the whole term is refused.
    #
    # NOT FITTED, and deliberately so: substituting K = 183 L/mol would import
    # an ALKALINE NH4OH/alumina constant into an acidic H2O2/glycine pack
    # across the pH at which BTA protonates and the Cu(I)-BTA complex changes
    # stability. The unblocking datum is a BTA sweep of Cu removal at this
    # pack's own pH 3-4 with H2O2.
    #
    # Scope: this gates a pack whose `inhibitor_K_ads_L_per_mol` is DECLARED
    # null (i.e. the pack states it has no defensible steady-state constant).
    # w_fe_oxidizer, which carries a directly measured 1108 L/mol, is
    # untouched -- this refuses a specific constant, not the inhibitor
    # mechanism.
    _inhib_mM = resolved.p_or("inhibitor_mM", None)
    _inhib_ref_mM = resolved.p_or("inhibitor_ref_mM", None)
    _k_param = resolved.pack.params.get("inhibitor_K_ads_L_per_mol")
    _k_declared_null = (_k_param is not None
                        and getattr(_k_param, "value", None) is None)
    _has_direct_k = resolved.p_or("inhibitor_K_L_per_mol", None) is not None
    if (_k_declared_null and not _has_direct_k
            and _inhib_mM is not None and _inhib_ref_mM is not None
            and float(_inhib_mM) != float(_inhib_ref_mM)):
        _applied = terms.pop("inhibitor", None)
        if _applied and abs(float(_applied)) > 1e-12:
            # The inherited chemistry_factor has ALREADY multiplied this in,
            # so removing the bookkeeping entry without dividing the factor
            # would leave a refused term silently acting on the rate -- the
            # exact failure mode this gate exists to prevent.
            factor /= float(_applied)
        warnings.append(
            f"inhibitor term REFUSED at {float(_inhib_mM):g} mM (reference "
            f"{float(_inhib_ref_mM):g} mM). This pack declares "
            "inhibitor_K_ads_L_per_mol null, so the only constant reachable "
            "is the EQUILIBRIUM (BTA x Cu) adsorption constant K = 3283 L/mol "
            "(doi:10.2320/matertrans.m2016310) -- and under polishing the "
            "Cu-BTA layer is continuously abraded, so its steady-state "
            "coverage is not the equilibrium coverage. Refuted "
            "quantitatively by the only dataset that holds everything else "
            "fixed: Hong 2007 (doi:10.1149/1.2717410 Fig. 1, pH 4, 5 wt% "
            "H2O2) measures a 0/10 mM rate ratio of 1.21 where this term "
            "asserts 18.4. The refusal is TWO-SIDED because the refutation "
            "is: below the reference the factor reaches 9.97x at zero and "
            "fabricates a rate (hong2007's zero-BTA rows come out 16.9-24.3x "
            "high, absolute scale 0.49x -> 0.059x), and above it the factor "
            "is bounded by 0.50 but still overstates the one measured point "
            "by 1.53x -- a bound on a term's size is not evidence that it is "
            "harmless inside that bound. Applying the above-reference half "
            "alone cost hong2007 its noise floor (14.8% -> 24.0% shape "
            "against 13.0% replicate scatter) and moved the corpus median "
            "18.9% -> 19.5%. Substituting the pack's back-solved K = 183 "
            "L/mol is declined: it was measured in an ALKALINE NH4OH/alumina "
            "system and BTA protonation is pH-dependent. Unblock with a "
            "BTA-concentration sweep of Cu removal at this pack's own "
            "pH 3-4 with H2O2, which yields a steady-state effective K")

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
            # Separate acid-side floor: the mechanical background below the
            # optimum, where particles stop attaching electrostatically.
            # Defaults to the alkaline floor rather than to zero, because a
            # zero floor makes the predicted rate collapse to 0.0 A/min far
            # from the optimum, which no measurement supports.
            acid_floor = resolved.p_or("ph_acid_mechanical_floor", None)
            acid_floor = float(ph_floor if acid_floor is None else acid_floor)
            # HOLD AT THE EDGE OF THE MEASURED RANGE, do not extrapolate.
            #
            # A Gaussian is a LOCAL description of a peak: it is fitted where
            # the sweep has points and says nothing about the far tail, yet
            # evaluating it 7 pH units out multiplies the rate by exp(-(7/w)^2),
            # a number no measurement produced. For oxide_silica (peak 11.0,
            # width 3.1 fitted on Li 2021's three points over pH 10-12.5) that
            # tail suppresses pH 4 by 61x, which is the single cause of the four
            # largest absolute-scale misses in the corpus (ep3161098b1 139x,
            # bouvet2002 W/oxide/Ti 75.6/39.2/38.2x) -- all four silica slurries
            # run acidic, all four are one-sided, and all four move together
            # with this one factor, so it is one bug and not four.
            #
            # The clamp is the physically conservative reading, not a fit: it
            # asserts only "outside the range these constants were measured
            # over, the chemistry is no better known than at the nearest edge",
            # which is also what amorphous-silica kinetics predict -- the
            # hydrolysis rate flattens into a pH-independent plateau below the
            # OH--catalysed branch (Iler 1979 ch.1; Brady & Walther 1990,
            # rate ~ a_OH^0.5 only above the neutral point), rather than
            # continuing to fall like a Gaussian tail.
            #
            # It ADDS NO CONSTANT: ph_valid_range already exists in every pack
            # and until now only emitted a warning. The out-of-range warning
            # below is kept and reworded, because a held value is still not a
            # measurement.
            ph_eval = float(ph)
            ph_range_clamp = resolved.p_or("ph_valid_range", None)
            ph_clamped_from = None
            if (isinstance(ph_range_clamp, (list, tuple))
                    and len(ph_range_clamp) == 2):
                lo_c, hi_c = float(ph_range_clamp[0]), float(ph_range_clamp[1])
                if ph_eval < lo_c:
                    ph_clamped_from, ph_eval = ph_eval, lo_c
                elif ph_eval > hi_c:
                    ph_clamped_from, ph_eval = ph_eval, hi_c
            # Normalised to the pack's reference pH, not to the optimum: Kp was
            # measured at ph_ref and already contains the chemistry there.
            if ph_ref is not None:
                ph_factor = ph_factor_relative_to_reference(
                    ph_eval, float(ph_ref), float(ph_peak),
                    float(ph_width), ph_floor, acid_floor)
            else:
                ph_factor = ph_response(ph_eval, float(ph_peak),
                                        float(ph_width), ph_floor, acid_floor)
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
            # A pack whose peak is a BOUND at the edge of its data has no
            # measured limb on the far side of that edge. Falling away from an
            # unmeasured edge is not a prediction, it is the shape of the
            # assumed function, so say so — loudly, because the acid-side floor
            # is frequently 0 and the rate then collapses towards zero.
            ph_range = resolved.p_or("ph_valid_range", None)
            if isinstance(ph_range, (list, tuple)) and len(ph_range) == 2:
                low, high = float(ph_range[0]), float(ph_range[1])
                if not (low <= float(ph) <= high):
                    side = "below" if float(ph) < low else "above"
                    warnings.append(
                        f"pH {float(ph):g} is OUTSIDE the range this pack's pH "
                        f"constants were measured over ({low:g}-{high:g}), "
                        f"{side} it. The pH term is HELD at its value at the "
                        f"nearest measured edge (pH {ph_eval:g}, factor "
                        f"{ph_factor:.4f}) instead of extrapolating the fitted "
                        "Gaussian, whose far tail is an artefact of the "
                        "function rather than of any measurement. The held "
                        "value is a floor-of-knowledge, not a measurement: it "
                        "asserts only that the chemistry here is no better "
                        "known than at the edge")
    elif ph is not None and ph_peak is not None and not ph_width:
        warnings.append(
            f"this pack declares an optimum pH ({float(ph_peak):g}) but no "
            "ph_response_width, so pH is INERT: changing it will not change "
            "the predicted rate. Supply ph_response_width to activate the term")
    elif ph is not None and ph_peak is None:
        # A pack with no pH term at all is inert on the pH axis. When the pack
        # has MEASURED that null and said so in a key, publish the declaration
        # instead of staying mute: a sourced null result and a forgotten wire
        # are indistinguishable from the outside, and only one of them is an
        # answer. Costs zero constants -- it re-states what the pack holds.
        null_key = next((k for k in resolved.pack.params
                         if k.startswith("ph_response_is_null_over_")
                         and resolved.p_or(k, None)), None)
        if null_key:
            window = null_key[len("ph_response_is_null_over_"):].replace("_", " ")
            param = resolved.pack.params[null_key]
            in_window = _ph_is_inside(window, float(ph))
            warnings.append(
                f"pH is INERT here and that is a DECLARED NULL RESULT, not a "
                f"missing term: pack '{resolved.pack.name}' states "
                f"{null_key} = true over pH {window}, so no bell was fitted. "
                f"Source: {param.source}. "
                + (f"pH {float(ph):g} is inside that window, so the flat "
                   "response is the measured answer."
                   if in_window else
                   f"⚠ pH {float(ph):g} is OUTSIDE that window, where this "
                   "repository holds no measurement — the flat response is an "
                   "extrapolation of the null result, not a measurement of it."))

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
