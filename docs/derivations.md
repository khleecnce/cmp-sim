# CMP-Sim — Model Derivations

Every model in `cmp_sim/` has an entry here: the equation, where it comes from,
what was assumed, and the range in which it is valid. If a model is used outside
that range the simulator emits a warning at run time rather than returning a
confident wrong number.

Notation: `P` nominal pressure [Pa], `V` relative sliding speed [m/s],
`MRR` material removal rate, `Kp` Preston coefficient [m/Pa] (equivalently
m^2/N, i.e. m^3/(N m) of material per unit load per unit slide).

---

## P1 — Preston baseline

### Equation

    MRR(r) = Kp * P(r) * V(r)

`cmp_sim/models/preston.py`, evaluated on a radial mesh and averaged over the
wafer rotation angle:

    MRR(r) = Kp * P(r) * < |v(r, theta)| >_theta

### Origin

F. Preston, "The theory and design of plate glass finishing machines",
*J. Soc. Glass Technol.* **11**, 214 (1927). Predates the DOI system; no DOI
exists and none is invented here. Preston polished glass, not wafers: the law is
empirical and `Kp` lumps together everything chemical and material-specific.

The datasets this is validated against, all verified against the original
documents rather than a secondary transcription:

| dataset | source | verification |
|---|---|---|
| TEOS / silica, 4 points | US9499721B2 | patent table |
| Pt / alumina, 4 points | US8142675B2 | original PDF: 220/470/750/1020 A/min at 2/4/6/7 psi |
| oxide Taguchi L25, 5 points | US6564116B2 | patent's own S/N response table reproduced to 5 decimals |
| PETEOS / ceria, 9 points | Mariscal 2020, *ECS J. Solid State Sci. Technol.* **9**, 044008, doi:10.1149/2162-8777/ab89bc | published table |
| Cu / IC1000, 6 points | US6918821B2 | Table 1, kept as a counter-example |

Patent PDFs are at `patentimages.storage.googleapis.com/pdfs/US<number>.pdf`.

### Kinematics

For a rotary polisher with wafer angular speed `omega_w`, platen `omega_p`, and
centre-to-centre distance `r_cc`, the relative velocity at a wafer point is

    v_rel = omega_p * r_cc  +  (omega_p - omega_w) x r_wafer

Implemented in the inherited `legacy/sim/tier1_empirical/kinematics.py`
(Lai, MIT PhD thesis 2001, Eq. 2.12). Two consequences the code relies on:

1. When `omega_w = omega_p` the relative *speed* is `omega_p * r_cc`
   everywhere on the wafer — uniform, independent of radius. Any radial
   non-uniformity then comes from the pressure field alone.
2. `omega_p * r_cc` dominates the magnitude, so `r_cc` is a first-order
   parameter and must come from the tool, not a guess.

### Pressure field

* uniform: `P(r) = P_0`
* multi-zone carrier: piecewise-constant `P(r)` over normalised zone edges
  (`legacy/sim/tier1_empirical/wiwnu.py: p_zoned`)

### Kp decomposition

`Kp` is not predicted from first principles; each parameter pack carries a
literature-anchored `kp_m_per_pa` with its source. Physics layers attach as
*dimensionless multipliers*, each exactly `1.0` at the pack's reference
condition:

    Kp_eff = kp_m_per_pa * prod_i factor_i

The unity constraint is the anti-double-counting rule. A pack's `Kp` was
back-calculated from a measurement that already contained that pad, that
chemistry and that abrasive; multiplying in an *absolute* chemical or contact
term would count the same physics twice. (In the inherited project this exact
mistake collapsed a Cu rate by 20x.)

### Assumptions and validity

| assumption | consequence if violated |
|---|---|
| `Kp` constant over the swept range | absolute rate wrong outside the calibration regime; rankings usually survive |
| elastic pad contact, no asperity saturation | see P2 — the simulator warns |
| no slurry starvation (ample flow) | over-predicts at high rpm / low flow (P5) |
| blanket film, no pattern | invalid for patterned wafers (P6) |
| isothermal | ignores frictional heating (P4 temperature term) |

**Kp is a fitted constant, so absolute rate is only as good as the calibration
point.** What P1 genuinely predicts is the *shape*: how the rate responds to
pressure, speed and the pressure profile.

### Validation

`cmp_sim/core/validation.py` groups every published dataset by its chemistry
overrides so that only `P` and the rotation speeds vary inside a group, then
fits the single free constant by least squares:

    Kp* = <x, y> / <x, x>

with `x_i` the geometry/kinematics term at `Kp = 1` and `y_i` the measured
rate. Reported error is `100 * (Kp* x_i - y_i) / y_i`. See the table in
`README.md`.

---

## P2 — Greenwood-Williamson asperity contact

### The problem with nominal pressure

A polyurethane pad is rough. It touches the wafer only at asperity summits, so
the pressure that actually presses abrasive into the film is the *real* contact
pressure, ~100x the nominal value, over well under 1% of the nominal area.

### Equation

Summit heights `z` are taken exponentially distributed with scale `sigma`
(`beta = 1/sigma`), summits have radius `R`, areal density `eta`, and the
Hertzian contact of one summit compressed by `delta` is

    F(delta)   = (4/3) * E* * sqrt(R) * delta^(3/2)
    A(delta)   = pi * R * delta

Integrating over the height distribution above separation `d`:

    n(d)   = eta * A_n * exp(-beta * d)
    A_r(d) = eta * A_n * pi * R * (1/beta) * exp(-beta * d)
    W(d)   = eta * A_n * (4/3) * E* * sqrt(R) * Gamma(5/2) * beta^(-3/2) * exp(-beta*d)

Every term shares the same `exp(-beta d)`, so the exponentials cancel in any
ratio:

    A_r / W = const,    p_r = W / A_r = const,    n proportional to W

### Why this matters

**The mean real contact pressure does not depend on load.** Pressing harder
does not squeeze each abrasive particle harder — it recruits *more* contacts.
Since removal is proportional to the number of active contacts, `MRR` comes out
linear in `P`. So GW supplies the microscopic reason Preston's empirical law
works, which is why P2 sits under P1 rather than replacing it.

Verified numerically over 7-96 kPa in `tests/test_contact_gw.py`: `p_r` is
constant to `<1e-6` relative, and both `n` and `A_r` are linear in load to the
same tolerance. The numeric inverse solution also agrees with the closed-form
`A_r/W` ratio to `<0.1%`.

### Origin

J. A. Greenwood, J. B. P. Williamson, "Contact of nominally flat surfaces",
*Proc. R. Soc. Lond. A* **295**, 300 (1966), doi:10.1098/rspa.1966.0242
The inverse problem (nominal pressure -> separation) is solved by Brent's
method in the inherited `legacy/sim/tier2_physics/gw_pressure_solve.py`; the
Hertz/GW integrals are in `legacy/sim/tier2_physics/gw_contact.py`.

### Pad properties in, contact factor out

    kappa = A_r(this pad) / A_r(reference pad)      at equal nominal pressure

`kappa = 1.0` exactly when the recipe's pad equals the pack's reference pad, so
the calibrated `Kp` is untouched by default. Where a datasheet gives only
durometer, `E` is estimated from Shore D via the Qi/Joyce/Boyce (2003)
polyurethane correlation

    E [MPa] = 10^(0.0235 * S_A - 0.6403),   S_A = 2 * S_D + 20

which puts an IC1000-class 57 Shore D pad at ~320 MPa, the right order for the
few-hundred-MPa values reported for that pad. Outside Shore D 20-60 this is an
extrapolation and the run is flagged. The Hertz reduced modulus then combines
pad and film:

    1/E* = (1 - nu_p^2)/E_p + (1 - nu_w^2)/E_w

### Validity boundary — asperity saturation

The load-independent result depends on contact being confined to the *tail* of
the height distribution. Once most summits touch, the pad can only respond by
compressing existing contacts: `p_r` rises, `A_r` stops growing linearly, and
the Preston linearity fails.

`PadContactState.saturation(P) = n(P) / (eta * A_n)` measures this, and above
50% the simulator warns. A 45 Shore D pad at 4 psi is fully saturated, and the
sub-linear pressure response that follows is asserted as a test rather than
patched away.

A second boundary is plasticity. With

    psi = (E* / H) * sqrt(sigma / R)

`psi > 1` means asperities flow plastically and elastic GW no longer applies.
For a soft pad against 7 GPa oxide `psi ~ 0.03` (safe); against ~0.2 GPa SnAg
solder it rises sharply.

---

## Slurry item 1-3 — bulk properties from the formulation

`cmp_sim/slurry/rheology.py`. Nothing here is CMP-specific; it is standard
colloid and solution physics, which is the point — these are the properties the
transport (P5) and contact (P2) layers consume.

### Volume fraction from weight percent (exact)

    phi = (w/rho_p) / (w/rho_p + (1-w)/rho_w)

### Suspension viscosity — Krieger-Dougherty

    eta = eta_0 * (1 - phi/phi_max)^(-[eta] * phi_max)

with `[eta] = 2.5` (Einstein 1906) and `phi_max = 0.64` (random close packing).
Truncating to first order returns Einstein's `eta = eta_0 (1 + 2.5 phi)`, so the
two agree below `phi ~ 1e-3` — asserted as a test. At the 5-30 wt% loadings of
real slurries the higher-order term matters, and near `phi_max` the suspension
jams, where the code raises instead of extrapolating.

* I. M. Krieger, T. J. Dougherty, *Trans. Soc. Rheol.* **3**, 137 (1959)
* A. Einstein, *Ann. Phys.* **19**, 289 (1906)

Water viscosity uses the Vogel form `eta = A * 10^(B/(T-C))` with
**T in kelvin**, A = 2.414e-5 Pa s, B = 247.8 K, C = 140 K, reproducing the CRC
Handbook 1.002e-3 Pa s at 20 C and 8.90e-4 at 25 C within 2%. (Feeding Celsius
into that formula is a ~15% error — a real bug caught by the handbook test.)

### Ionic strength and screening

    I = 0.5 * sum_i c_i z_i^2

Debye length comes from the inherited verified `dlvo_colloid.debye_length_nm`,
which reproduces the textbook `kappa^-1 ~ 0.304/sqrt(I)` nm for a 1:1
electrolyte (9.6 nm at 1 mM). When only pH is known, only the H+/OH-
contribution can be computed; that is a *floor*, and the result says so rather
than pretending a buffered slurry is that dilute.

### Electrostatic regime from isoelectric points

A surface is negative above its IEP and positive below. Comparing abrasive and
film IEPs at the working pH gives the sign of the particle-wafer interaction:

| system | pH | abrasive | film | regime |
|---|---|---|---|---|
| silica on oxide | 10.5 | negative (IEP ~2.5) | negative (IEP ~2.7) | repulsive |
| ceria on oxide | 5.0 | positive (IEP ~7) | negative (IEP ~2.5) | attractive |

The ceria-on-oxide attraction window is exactly where ceria STI slurries are
formulated. Attraction increases particle-surface contact — and agglomeration
and scratch risk with it, which is the link to the P8 defect proxy.

Colloidal stability is classified by `|pH - IEP|` using the inherited
`stability_qualitative`, whose 1.0/2.0 pH thresholds are explicitly unverified;
the run therefore carries that caveat, and a measured zeta potential overrides
it. `|zeta| < 20 mV` raises an agglomeration warning.

---

## P3 — Luo-Dornfeld abrasive mechanics

### Origin

J. Luo, D. A. Dornfeld, "Material removal mechanism in chemical mechanical
polishing: theory and modeling", *IEEE Trans. Semicond. Manuf.* **14**(2), 112
(2001), doi:10.1109/66.920723

The derivation below is re-done from the indentation geometry rather than
quoted, so the exponents are traceable to an assumption that can be checked
(plastic indentation, Hertzian shallow indent) instead of taken on faith. Note
one consequence of Luo-Dornfeld's own formulation: the particle contact stress
is *set equal* to the film hardness, which is why the packs cannot source the
two independently — see the note under `contact_branch` below.

### Single-particle law, derived

A rigid sphere of radius `R` pressed into a surface of hardness `H` by load `F`.
Hardness is load per plastically supported area, so `A_c = F/H = pi a^2`, giving
`a = sqrt(F/(pi H))`. For a shallow spherical indent `a^2 = 2 R delta`, hence

    delta = a^2 / (2R) = F / (2 pi R H)

A particle dragged along cuts a groove of cross-section `~ a*delta`, so

    Q_1 / V  ~  F^(3/2) R^(-1) H^(-3/2)

Three consequences:

1. `alpha = 3/2` (load exponent, plastic branch).
2. `beta = -1` (size exponent): *at fixed load per particle* a smaller particle
   indents deeper. The folk claim that bigger particles polish faster comes from
   the count term, not this one — which is why measured size dependence is
   non-monotonic.
3. **`MRR ~ H^(-3/2)`** — the one channel through which chemistry reaches
   mechanics. Chemistry softens the top layer; `H` is that softened hardness,
   not the bulk value.

### Exponents are computed, not tabulated

Writing `MRR ~ C^n_C d^n_d` with fitted exponents is post-hoc description that
only applies to the slurry it was regressed on. Instead three measurable
questions are answered — who carries the load (`chi`), elastic or plastic
(`alpha`), monolayer or multilayer supply (`p`, `q`) — and the exponents follow:

    n_C = p (1 - alpha chi)
    n_d = -q (1 - alpha chi) + beta

Two structural results matter. `n_C <= 1` always, because `p <= 1` and
`0 <= (1-alpha chi) <= 1`, so a literature exponent of 4/3 cannot arise inside
this decomposition. And `n_C = 1/3` is *not* a "surface-area-limited" law as
usually named — it is the signature of elastic contact (`alpha = 2/3`) with full
load sharing (`chi = 1`).

`alpha` and `beta` come from the same contact law and are interpolated together
across the elastic-plastic transition. (Looking `alpha` up in a discrete table
silently returns `beta = 0` in that band, which is not a physical law at all —
a real bug, caught by a test.)

### Size cancellation is a prediction, not an ignored input

In the elastic, fully load-sharing monolayer regime,
`n_d = -2(1 - 2/3) + 2/3 = 0` exactly: smaller particles are more numerous but
each carries less load, and the two effects cancel. The simulator says so
explicitly, because "changing D50 did nothing" otherwise looks like a bug.

### Saturation

A single power law cannot be right at both ends. With finite contact sites,
`N_active = n_s (1 - exp(-C/C_half))`, so the *apparent* exponent slides from 1
(dilute) to 0 (saturated) with no change in physics. Where `C_half` is known the
occupancy ratio is used directly; where it is not, a power law is used and the
result says it cannot saturate.

---

## P4 — Chemical term

### Origins

* **Glass / oxide hydrolysis** — T. A. Cook, "Chemical processes in glass
  polishing", *J. Non-Cryst. Solids* **120**(1-3), 152 (1990),
  doi:10.1016/0022-3093(90)90200-6 — the water-diffusion-then-dissolution
  picture behind the pH dependence.
* **Tungsten passivation** — F. B. Kaufman *et al.*, "Chemical-mechanical
  polishing for fabricating patterned W metal features as chip interconnects",
  *J. Electrochem. Soc.* **138**(11), 3460 (1991), doi:10.1149/1.2085434 — the
  abrade-the-passive-film mechanism, and the source of the oxidizer peak whose
  parameters are degenerate below the peak (see "Fitting factors" below).
* **Copper hardening under oxidizer** — Ihnfeldt & Talbot 2008,
  eScholarship qt0qc211z8, measured Cu bulk at 1.2 GPa but the H2O2-modified
  layer at **3.24 GPa**, i.e. harder, not softer. This refuted the assumption
  originally coded here and it was removed; see the caveat below the table.

Chemistry enters only through the softened surface hardness:

    chemical conditions -> H_eff/H_0 -> MRR multiplier = (H_0/H_eff)^(3/2)

Nothing in the kinematics or contact model is touched. Softening 4x raises
removal 4^1.5 = 8x.

* **Oxidizer** — Langmuir coverage `theta = KC/(1+KC)`, one free parameter.
  Promotion branch `theta/theta_ref` (W with Fe/H2O2) or passivation branch
  `(1-theta)/(1-theta_ref)` (Cu, where thick passivation slows removal). Both
  carry an additive *mechanical floor*: at zero oxidizer the abrasive still
  removes material, so a purely multiplicative term would wrongly predict zero.
* **Inhibitor** — Langmuir coverage of BTA-class molecules weights removal by
  the free site fraction.
* **Ceria chemical tooth** — Si-O-Ce chemisorption (-111 to -258 kJ/mol) versus
  silica physisorption (-20 to -40). Enabled only for ceria; the coefficient
  must never be carried across abrasive chemistries.
* **pH softening** — real but the weakest link, applied only when a pack states
  the coefficient.
* **Temperature** — `k(T)/k(T_ref) = exp(-(Ea/R)(1/T - 1/T_ref))`. A chemically
  limited film accelerates with platen heating; a mechanically limited one does
  not. Without `Ea` in the pack the run is explicitly reported as isothermal.

---

## P5 — Radial non-uniformity

### Kinematics is not the cause

For `omega_w = omega_p` the relative speed is `omega_p r_cc` everywhere on the
wafer; off-match, the wafer's own rotation averages the angle out. Measured
contribution of the velocity field to non-uniformity is <1%, against tens of
percent for zone pressure. **Uniform pressure plus equal rpm gives exactly zero
WIWNU** — a structural result, asserted as a test. That is why zone pressure is
the knob a tool engineer actually reaches for.

### Slurry supply

The land gap is the layer dragged through the contact and consumed there, so it
is what must be replenished each wafer pass; the grooves are a reservoir an
order of magnitude larger that recirculates. Counting the groove volume as
demand would require thousands of ml/min and declare every real process starved
(a 300 mm tool runs 150-300 ml/min). Using the land gap gives a requirement of
~9-40 ml/min, comfortably below practice. Interface volumes come from the Mu
2016 reactor model, `V = V_land + V_groove`.

Lubrication regime from `l_hd = mu U / p` and `lambda = h/sigma`: in CMP
`l_hd` is tens of nm against micron-scale pad roughness, so `lambda << 1` and
contact is boundary-lubricated — which is why abrasives touch the wafer at all.
A full hydrodynamic film (`lambda > 3`) would mean no removal, and is flagged.

**The starvation droop shape is not predicted.** How sharply the centre falls
off depends on groove pattern and injection geometry; the risk is reported and a
profile applied only when a pack supplies a calibrated starvation length.

---

## P6 — Pattern effects

MIT framework: B. E. Stine *et al.*, "Rapid characterization and modeling of
pattern-dependent variation in chemical-mechanical polishing", *IEEE Trans.
Semicond. Manuf.* **11**(1), 129 (1998), doi:10.1109/66.661292; with Boning
MRS 1999 and Ouma's MIT thesis (1999) for the density-filter formulation.

    rho_eff(x) = (w * rho_local)(x)        pad averages over a planarization length
    RR_up(x)   = K / rho_eff(x)            dense regions polish SLOWER

Dense arrays spread the load over more features, so they clear last and end up
thicker. Step height falls linearly at `K/rho` and closes at `t_c = rho h0 / K`
(incompressible pad); with a compressible pad the pad reaches the down-areas
while a residual step `h_c` remains and the step then decays exponentially. The
two branches are joined continuously at `h_c` via `t_c = rho (h0 - h_c) / K`.

Because `t_c` scales with density, dense and sparse regions clear at different
times — that spread forces overpolish, and overpolish causes dishing and
erosion. During overpolish,

    r_metal(d) = RR_m (1 - d/d_max)
    r_oxide(d) = RR_ox/(1 - rho_m) (1 + b d)

and dishing self-limits at the `d_ss` where they balance. High selectivity
protects the stop layer but deepens dishing; the trade-off is computed.

---

## P7 — Pad wear and conditioning

Measured, from Jeong et al. 2024 (*Materials* 17, 1817):

    N(t)/N0 = exp(-t/tau(p))                       contact count decays
    mu_R(t) = (0.28 p + 0.621) t + 5.45 exp(0.18 p)  summits blunt [um]

Note the direction: a naive GW argument says thinning the population at fixed
pressure should *increase* contact count; the measurement says the opposite, and
the measurement wins. The contradiction is recorded, not hidden.

Conditioning regenerates asperities, giving the steady state

    n_ss = k_c G / (k_g + k_c G)

with `G` the disk's current cut rate (exponential ageing, anchored to an
Entegris field observation of 16% remaining after 50 h). A worn disk lowers the
plateau: the pad settles glazed.

**The MRR proxy is direction-only.** It approximates force-per-contact by summit
radius alone, and the inherited self-test found its peak at ~7 min against a
measured ~3 min. Extrapolation beyond the 10 min of measured data, or outside
2-5 psi, raises warnings — at 120 min the fit predicts 0.01% of contacts and a
185 um summit radius, larger than the asperities themselves.

---

## P8 — Defect proxy

Scratches come from the *tail*, not the mean: a 50-150 nm D50 is far below the
~680 nm scratch threshold.

    Delta = (D99 / D99_ref)^n * (1 + aggregate_ratio)

exactly 1.0 at the reference slurry and **never multiplied into MRR**.

* Scratch count is linear in the number of particles above critical size
  (Remsen 2006); on the D99 axis that becomes a power law with `n` = 1.44
  (ceria, Hitachi US8439995B2, R^2 = 0.997) or 2.54 (tungsten, Egan & Kim 2019).
  `n` is not a material constant — it is a secant of a log-normal tail whose
  local slope falls 8.4 -> 4.6 -> 0.7 across the Hitachi points, so a fixed `n`
  is least reliable exactly at the threshold, which the code warns about.
* Agglomeration is independent: Basim & Moudgil 2002 saw mean size unchanged
  while AFM Rmax doubled — a path D99 cannot see.
* Scratch *severity* comes from Saka 2008 / Eusner 2009:
  `2a_max = D99 sqrt(H_pad/H_film)`, `delta_max = (D99/2)(H_pad/H_film)`. The
  same risk index means different damage on different films (Cu `delta_max`
  ~65 nm vs W ~3 nm).

Absolute scratch counts are not predicted, and **Delta must not be compared
across packs**.

---

## Sanity: is the absolute number even possible?

`core/sanity.py` compares every predicted rate against a published envelope for
that film and labels anything outside it `IMPLAUSIBLE`. This is not decoration —
it caught three real bugs:

1. **SiC inherited the oxide Kp.** The pack declared `base: sti_ceria` and never
   overrode `kp_m_per_pa`, so 4H-SiC used the oxide coefficient and
   over-predicted by ~128x (6,296 A/min where its own source DOE reports 2.7-6.7
   nm/min). Refitted to 1.714e-15 m/Pa over all 50 runs; now 4.91 nm/min.
2. **Tungsten Kp came from a quoted range, not data.** Refitted to 7.0e-14 from
   two printed patent tables that agree within 5%, replacing a 2.8e-13 estimate
   that over-predicted by ~4x.
3. **The GW contact factor was correcting against an estimated reference pad**,
   inflating every rate 2-3x. `kappa = A_r(pad)/A_r(reference)` only means
   something when the reference is a real pad, so it is now reported as a
   diagnostic unless the pack sources its reference pad.

The lesson generalises: a pipeline that runs without error is not a pipeline
that is right. Check the output against what the physical world is known to do.

---

## Model selection — situation, not film

### The problem with keying models to films
The first design exposed a ladder: `preston -> gw_preston -> full`. It bundles
choices that are physically independent, and it embeds two false assumptions.

**False assumption 1: more physics is always better.** Enabling the chemistry
layer on a pack whose Kp was *calibrated with that chemistry present* double
counts it. Applying the Greenwood-Williamson correction against a guessed
reference pad inflates every rate by 2-3x (this actually happened; see the
contact-factor note above).

**False assumption 2: the film picks the model.** It does not. The appropriate
model is set by the *regime*, and the regime is a property of the whole
operating point:

- SiC and sapphire are different films in the **same** regime — hard, inert,
  chemically rate-limited. Both need the chemical path and neither is described
  by a P*V law.
- Copper at 1.5 psi and copper at 4 psi are the **same** film in different
  regimes. US 6,918,821 B2 exists precisely because the low-pressure branch
  does not behave like the high-pressure one.
- Any film on a saturated pad leaves the regime where Preston's linearity is
  derivable, regardless of what it is made of.

### What replaced it
Two modules, `core/regime.py` and `core/profiles.py`.

`regime.detect()` classifies a resolved recipe along eight axes, all computed
from quantities already in the model:

| axis | derived from | boundary |
|---|---|---|
| `contact_branch` | particle contact stress / softened surface hardness | elastic <= 0.5, plastic >= 1.0 |
| `asperity_regime` | plasticity index psi = (E*/H) sqrt(sigma/R) | plastic above 1.0 (Greenwood-Williamson 1966) |
| `load_regime` | fraction of summits in contact | saturated above 0.50 |
| `lubrication` | lambda = h_film / roughness | boundary < 1, full film > 3 (Bhushan) |
| `film_class` | material family, then hardness within it | soft metal < 2 GPa; hard ceramic >= 15 GPa |
| `rate_limit` | film class + whether reactive species are present | - |
| `topography` | pattern density given or not | - |
| `pad_state` | pad or conditioner hours given | - |

**Family before hardness.** Classifying by hardness alone puts tungsten
(~4-7 GPa) and thermal oxide (~7-9 GPa) in the same bin, yet W removes by
oxidise-then-abrade and oxide by hydrolyse-then-abrade. The material family
therefore decides the class, and hardness only splits soft from hard *within*
a family. A pack may state `material_family` explicitly; otherwise it comes
from the film name.

An axis that cannot be computed is reported in `undetermined`, never defaulted.
`contact_branch` is the common case: it needs the softened surface hardness,
which is rarely published, and silently assuming the elastic branch would fix
the sign of the particle-size exponent in P3 without the user ever knowing.

### Profiles
A profile is a named bundle of the seven orthogonal layers (`contact`,
`abrasive`, `chemistry`, `transport`, `pattern`, `wear`, `damage`) together
with a declaration of the situations it suits. `recommend()` scores each
profile against a detected situation (+1 per matching axis, -2 per mismatch);
`check()` warns when the chosen profile does not fit what the run actually is.

`auto` detects and picks. An explicitly named profile is **respected as given**
— the simulator warns but does not substitute, because the user asked for that
physics on purpose.

**Overlays.** `wear` and `pattern` describe extra circumstances rather than a
different theory of removal, so they are added to whichever profile fits
instead of competing with it. Without this, a worn patterned copper wafer would
have to choose between modelling copper and modelling pad wear — the earlier
ranking did exactly that, selecting `pad_life_study` for a copper run and
thereby dropping the plastic contact branch.

### Regime-independent warnings
Some mismatches matter whatever profile is chosen, so they are checked
separately: summit saturation (Preston linearity gone), plastic asperities
(elastic GW outside its validity range), a full hydrodynamic film (abrasives
cannot reach the wafer, so any predicted removal is meaningless), chemistry
off on a chemically limited system, pattern off on a patterned wafer, and wear
off when pad hours were supplied.

### Backward compatibility
`preston`, `gw_preston` and `full` still work. `full` now means "the profile
that suits this run", which is what it was always trying to approximate.

---

## The lubrication limit of Preston's law

The clearest validation result in the project is a dataset the model **fails**.

US 6,918,821 B2 Table 1 polished copper on an IC1000 pad at two pressures and
three platen speeds. The two pressure branches disagree about physics:

| pressure | 60 rpm | 120 rpm | 200 rpm | trend | Preston MAPE on that branch |
|---|---:|---:|---:|---|---:|
| 4.0 psi | 594 | 1384 | 1636 | rises 2.75x | 13.4% |
| 1.5 psi | 425 | 419 | 250 | **falls 0.59x** | 60.3% |

Preston requires a 3.33x rise in both cases. A single Kp fitted across all six
points necessarily lands between the branches, at 44.1% MAPE.

The dataset is kept in the suite **failing**. It is not excluded, not split
into the passing branch, and not reweighted, because the failure is the
finding: it marks where a P*V law stops being the right model.

### The model predicts its own failure
`core/regime.py` computes lambda = h_film / roughness for each condition from
pressure, speed, pad and flow — it never sees a measured rate. It flags exactly
one of the six as leaving the boundary-lubrication regime:

| condition | lambda | regime | measured |
|---|---:|---|---|
| 1.5 psi, 60 rpm | 0.37 | boundary | 425 |
| 1.5 psi, 120 rpm | 0.75 | boundary | 419 |
| **1.5 psi, 200 rpm** | **1.24** | **mixed** | **250 (collapse)** |
| 4.0 psi, 60 rpm | 0.14 | boundary | 594 |
| 4.0 psi, 120 rpm | 0.28 | boundary | 1384 |
| 4.0 psi, 200 rpm | 0.47 | boundary | 1636 |

The lambda thresholds are Bhushan's standard tribology boundaries, not tuned
here. Physically: at low load and high speed the slurry film carries part of
the load, asperity contact drops, and removal falls even though P*V rises.

### Independent corroboration from the patent itself
The patent's own inventive pads A, B and C do **not** invert at 1.5 psi
(pad A: 874 / 1293 / 1439 A/min, rising). Only the conventional IC1000
comparison pad does — which is the entire point of the patent, whose subject is
polishing at low pressure where conventional pads fail.

Locked by `tests/test_lubrication_limit.py`.

---

## Sweeps and regime boundaries

`POST /api/sweep` varies one parameter across up to 50 points. Each point
carries its own detected regime, and when a sweep crosses a boundary the
response says so.

This matters because the usual way to present a sweep — one smooth curve — is
exactly the way to hide the result above. Points in a different regime are
marked on the chart rather than dropped, so a trend is never drawn through
physics that changed underneath it.

---

## Why SiC fails the Preston gate — measured, not asserted

"Chemically rate-limited" is a convenient phrase that could excuse any bad fit,
so it is tested numerically against the 50-run DOE rather than asserted.

If removal were mechanically limited, Preston would predict **one** rate at a
given P and V regardless of chemistry. The DOE holds P and V fixed while varying
pH (9/10/11), oxidiser (4/6 wt%) and abrasive loading, so the spread inside such
a group measures directly how much of the process a P*V law cannot see:

| P (psi), rpm | n | min | max | max/min |
|---|---:|---:|---:|---:|
| 4.5, 60 | 13 | 1.24 | 6.00 | 4.8x |
| 5.0, 60 | 10 | 2.49 | 13.01 | 5.2x |
| 5.0, 80 | 5 | 2.00 | 8.03 | 4.0x |
| 5.5, 60 | 15 | 1.81 | 15.00 | 8.3x |
| 5.5, 80 | 5 | 2.00 | 16.00 | 8.0x |

Preston predicts 1.0x in every row. The median observed spread at identical
pressure and velocity is **5.2x**, and across the whole DOE P*V explains only
**R^2 = 0.09** of the variance in removal rate.

Because Kp is a single multiplicative constant it cannot change the *shape* of
the prediction at all: the best possible least-squares Kp still leaves a
residual far outside the 15% gate. The failure is structural, not a calibration
error, and no amount of fitting will remove it.

This is why the `chemically_limited` profile switches the pad contact layer off
and the chemical path on for these systems, and why its caveat says the absolute
rate is not trustworthy while rankings are.

Locked by `tests/test_chemically_limited_limit.py`, which also fails if the
exemption ever goes stale — if P*V starts explaining the variance, the test
demands the exemption be reconsidered rather than kept as a standing excuse.

---

## Films nobody polishes: grading, estimating, converging

### The problem
Not every film here is a routine polish step. Oxide and copper have decades of
published process data; SnAg solder has none, because the packaging industry
planarises fine-pitch tin bumps by fly-cutting rather than CMP, so the CMP
numbers were never generated. Treating those two identically is how a simulator
produces a confident number for a process nobody has demonstrated.

### Grading (`core/maturity.py`)
Films are graded **from their pack's own evidence**, not by declaration:

* `established` — Kp measured, and the pack backtested against published P*V data.
* `emerging` — Kp exists but was back-calculated from one published operating
  point, with no independent dataset to check the predicted shape.
* `unestablished` — no Kp at any operating point, or the literature records
  attempts that failed.

A pack may **lower** its own grade but never raise it. SnAg lowers itself,
because documented process failures are evidence: the only primary CMP-on-Sn
report eliminated alkaline pH 10-11 (etched the tin to bare Ni3Sn4) and
acidic-neutral pH 5-7 (scratched tin and polymer) without qualifying a third.
That is consistent with tin being amphoteric — it dissolves as Sn(2+) at low pH
and as stannate at high pH, with a passivating SnO/SnO2 window only between.

An unestablished film **refuses to run on defaults** and names what it needs: a
rate anchor, the intended pH (the window itself is unknown for such a film), and
the film hardness.

### Estimating Kp from material properties (`models/first_principles.py`)
Preston's law and Archard's wear law are the same statement. Archard gives worn
volume per unit sliding distance as `V/L = k*W/H`; dividing by contact area
turns load into pressure and sliding distance into velocity:

    MRR = k*P*V/H     and Preston says MRR = Kp*P*V     =>     **Kp = k/H**

Hardness carries the film identity; `k` is the dimensionless efficiency of the
abrasive-pad-slurry system. Computed from this repository's own packs:

| pack | Kp [m/Pa] | H [GPa] | k = Kp*H | tool class |
|---|---:|---:|---:|---|
| cu_h2o2_bta | 3.50e-13 | 1.2 | 4.2e-04 | device, 1-6 psi |
| w_fe_oxidizer | 7.00e-14 | 12.0 | 8.4e-04 | device |
| oxide_silica | 1.00e-13 | 9.0 | 9.0e-04 | device |
| poly_si_alkaline | 1.07e-13 | 11.5 | 1.2e-03 | device |
| sti_ceria | 2.20e-13 | 9.0 | 2.0e-03 | device |
| si_substrate_alkaline | 6.91e-13 | 10.0 | 6.9e-03 | **wafer-maker, 0.6 psi** |
| sic_ceria_h2o2 | 1.71e-15 | 26.0 | 4.5e-05 | **chemically limited** |

Two exclusions, both forced by the data rather than chosen:

* **SiC** — chemically rate-limited (rate varies 5.2x at identical P*V, R^2=0.09).
* **Si substrate** — a different machine class; its k is the largest outlier at
  5.2x the geometric mean of the others.

**The improvement is modest, and the module says so.** Over the five device-CMP
films the log-10 standard deviation falls from 0.284 (Kp alone) to 0.247 (k):
a typical factor of 1.9x becomes 1.8x. Include the wafer-maker point and
dividing by hardness is *actively worse* than not doing it (0.378 -> 0.415),
which is exactly why tool class is part of the exclusion rule.

So the physical argument for the 1/H form is far stronger than the statistical
evidence from five points. The estimator earns its place by extrapolating in the
right direction — a film three times softer should polish about three times
faster — not by being accurate. A held-out check is in the tests: estimating
copper from hardness alone lands inside the advertised band.

Two physics caveats it raises rather than models:

* **Creep.** Sn-3.5Ag sits at ~0.6 of its melting point at room temperature, so
  it creeps while being polished. Archard assumes hardness is a fixed flow
  stress; for a creeping solid the effective hardness falls with strain rate, so
  the true rate is likely *higher* and dwell-time dependent.
* **Smearing.** A soft, ductile film embeds abrasive instead of fracturing, which
  no term here represents.

### Converging on the owner's tool (`core/calibration.py`)
Measured rates are fitted with `Kp = sum(pv*r)/sum(pv^2)`, and the accuracy is
reported by **leave-one-out cross-validation** rather than in-sample error. The
distinction is the point: a one-parameter fit passes exactly through a single
point, so its in-sample error is 0% by construction and means nothing. With one
measurement the module refuses to quote an accuracy at all.

Measured on a synthetic tool 1.6x the pack's rate, predicting a held-out point:

| measurements | error vs held-out truth | cross-validated MAPE |
|---:|---:|---:|
| 0 | -56.7% | — |
| 1 | -0.8% | (refused) |
| 2 | -2.0% | 1.5% |
| 3 | -1.3% | 1.7% |
| 4 | -1.2% | 0.9% |

With three or more points spread across pressure and speed, the **P*V exponent**
is fitted rather than assumed. Preston requires exactly 1; anything outside
0.75-1.25 means a single Kp cannot describe the process, which is how the model
detects for itself the same departure that makes the published copper dataset in
this repository unfittable.

Precedence throughout: **measurements > explicit `params:` > Archard estimate >
pack default**, and every level is labelled in the provenance.

---

## Fitting factors to data, without inventing physics

### Why named factors rather than a fresh model per dataset
Given a table of measurements one could regress a new expression each time.
Three reasons not to, all already demonstrated inside this repository:

**Identifiability.** The Kaufman oxidizer curve has two free parameters, a peak
position and a shape exponent, which are mathematically degenerate when only
sub-peak data exist. This is why the copper pack uses a one-parameter Langmuir
form. Re-deriving a model per dataset walks into that repeatedly; fitting named
factors makes the degeneracy explicit and refusable.

**Extrapolation.** A black-box regression collapses outside the measured box.
A fitted physical factor keeps the structure: doubling pressure still doubles
rate, because that is the form, not something learned.

**Convergence on few points.** Every free parameter costs data. One measurement
already moves Kp from -56.7% to -0.8% on a held-out point; a ten-parameter
surface fitted to ten points reproduces the points and predicts nothing.

### The factor registry
Six named quantities, each with exactly **one** free parameter by construction:

| factor | form | what it means |
|---|---|---|
| `pressure_exponent` | MRR ~ P^n | n<1: real contact area saturating |
| `velocity_exponent` | MRR ~ V^n | n<1: transport or lubrication limit |
| `abrasive_half_wt_pct` | N ~ 1-exp(-C/C_half) | loading at which sites saturate |
| `abrasive_size_exponent` | MRR ~ d^n | sign is contradictory in the literature, so fitted |
| `oxidizer_langmuir_K` | theta = KC/(1+KC) | coverage saturation |
| `activation_energy_kj_per_mol` | Arrhenius | <20 diffusion-limited, >40 reaction-limited |

Each factor's reference point is the dataset's own mean, so every factor equals
exactly 1.0 at the centre of the data and cannot double-count what Kp absorbed.
Fitted values land on the pack keys the existing physics layers already read,
replacing the literature value in place rather than adding a parallel term.

### Three gates against overfitting
More parameters always fit the training data better, so a factor unlocks only if:

1. **Leverage** — its driving input varies by at least 15% across the runs.
   Fitting an abrasive exponent to runs at one concentration is fitting noise.
2. **Budget** — at least three measurements per free parameter, Kp included.
3. **Out-of-sample gain** — it must improve the **leave-one-out** error by at
   least 25%, never the in-sample error.

The 25% floor is a measurement, not a preference. At 8% measurement scatter on
data that genuinely obeys Preston's law, a 2% threshold admitted a spurious
pressure exponent in 2 runs out of 5; a true departure cuts the error by 60-70%.
Better to miss a marginal factor than to report one that is not there.

### Recovery against known answers
| truth | recovered | cross-validated error |
|---|---|---|
| pressure exponent 0.65 | 0.652 | 19.6% -> 0.12% |
| abrasive C_half 3.0 wt% | 3.08 | 94.4% -> 1.0% |
| activation energy 45 kJ/mol | 44.5 | 122.9% -> 1.1% |
| 0.70 and 3.0 simultaneously, 5% noise | 0.68 / 3.08 | 56.2% -> 2.8% |
| Preston-true data | nothing unlocked | unchanged |

### Reading a CSV
`core/measurement_io.py` accepts the column names people actually use. Two
deliberate strictnesses:

* **Units are matched before being stripped.** "MRR (A/min)" and "MRR (nm/min)"
  differ only by their unit; a lenient parser that merged them would put a silent
  10x error into every fitted rate.
* **Unusable rows are refused, not skipped.** A dropped row changes the fit
  invisibly, which is worse than an error that names the row.

---

## Deciding the contact branch without a circular input

### The circularity
P3 needs to know whether a particle indents the film elastically or plastically:
it sets the load exponent alpha, and through it the concentration and size
exponents. The obvious test is the particle contact stress against the film
hardness — but Luo-Dornfeld *defines* the contact stress as the hardness, so
sourcing it independently is circular. Every pack left it null and the branch
was reported `unknown` for every film.

### The way round: compare loads, capped by the pad
The pad hardness is measured directly, by nanoindentation of a wet pad, and it
caps the load one asperity can put on a particle:

    P_Y   = (pi^3/48) * Hc^3 / Ec^2 * R^2     yield load, Hertz + Tresca
    P_max = pi * R^2 * Hp                     pad-limited load
    plastic when P_max > P_Y:
    Lambda = 48 * Hp * Ec^2 / (pi^2 * Hc^3)  > 1

`R` cancels exactly, so **the branch does not depend on particle size**. That is
not a convenience: it reproduces Eusner's measurement that scratch width and
depth are independent of polishing pressure and pad topography.

Sources, read from the original PDFs: `P_Y` is Eq. 3 in both Saka, Eusner &
Chun, *CIRP Annals* **57**, 341 (2008) and Eusner *et al.*, *J. Electrochem.
Soc.* **156**(7) H528 (2009). Moduli and hardnesses are Eusner Table I (SiO2
92/15, Cu 128/1.22, wet pad 0.53/0.05 GPa). Pad hardness distribution is
Eusner Fig. 15 — 36 measurements, mean 0.05 GPa, standard deviation 0.06 — with
Hp,max = 0.31 GPa in Table IV.

| film state | Hc | Ec | Lambda | branch |
|---|---|---|---|---|
| Cu, glycine+H2O2+BTA pH 3 | 3.24 | 128 | 117 | plastic |
| bare Cu film | 1.22 | 128 | 2194 | plastic |
| Cu, glycine pH 10 (hardest measured) | 15.6 | 128 | 1.05 | marginal |
| SiO2 at 15 GPa | 15 | 92 | 0.61 | elastic |
| SiO2 at 8 GPa | 8.0 | 69.8 | 2.31 | plastic, marginal |

The rule discriminates rather than always answering "plastic", and oxide lands
on the boundary — which is physically right: oxide is the one material in the
source paper's Table IV with no measurable scratches.

### Two traps, recorded because both are easy to fall into
**Do not compare Hp against Hc directly.** `Hp = 0.05 GPa` is a load divided by
the particle's *cross-section*, not by the ~100x smaller particle/film contact
area. The naive test calls copper elastic, contradicting its measured
scratches. Only the load comparison is valid.

**Watch the pack lineage.** Adding SiO2's modulus to the silica packs
propagated it to SiC through SiC -> sti_ceria -> oxide_silica. Lambda goes as
E^2, so SiC looked elastic on a number that was never about SiC. It is now
blocked with `value: null`; the same route once carried the oxide Kp into that
pack and over-predicted SiC by 128x.

### A depth limit that no amount of care removes
Two further caveats came out of the source search and are worth stating because
they bound what the branch can mean at all:

1. **No nanoindentation of an actually CMP-polished surface exists in this
   corpus.** Every "surface" hardness is a statically immersed or as-deposited
   film. Polishing is not immersion — it removes the layer it creates — so even
   the best available number describes a related surface, not the one the
   abrasive meets.
2. **The instrument cannot reach the depth that matters.** Ihnfeldt's
   nanoindenter resolves to roughly 5 nm, while a single abrasive particle
   indents well under 1 nm. So 3.24 GPa is the shallowest *resolvable*
   hardness, not the hardness at the abrasive's working depth. Since Lambda
   goes as 1/Hc^3, a factor of 2 wrong in hardness is a factor of 8 in Lambda.

Copper's Lambda is 117, two orders of magnitude clear of the boundary, so that
verdict survives an 8x error comfortably. Oxide's 2.8 does not, which is
exactly why it is reported as `transition` rather than assigned a side.

### What this does NOT settle
Deciding the branch was supposed to fix the sign of the particle-size exponent.
It does not. The exponent relations assume `0 <= 1 - alpha*chi <= 1`, and the
plastic branch (alpha = 3/2) with copper's measured load sharing (chi = 1.0)
gives `n_C = -0.5` — "more abrasive removes less", which the model's own bound
forbids. alpha and chi are not independently adjustable, since chi comes from
the measured area-pressure exponent. So the engine reports the branch, leaves
the exponents on the inherited elastic values at confidence `unverified`, and
names the measurement that would resolve it.

---

## The abrasive size exponent is per-film, and the data say so loudly

Nine measured sweeps across seven films give exponents from -0.45 to +1.0, and
three are non-monotonic so no power law fits at all. The decisive evidence is
*within* single experiments:

* **Bouvet 2002** (*JVST B* **20**(4) 1556, Fig. 3): W, Ti and thermal oxide,
  same four colloidal-silica slurries, same runs. W flat (n ~ -0.05), Ti
  falling (-0.45), oxide peaked at 25 nm.
* **US 2019/0127607 A1** (Tables 1-2): HDP oxide and TEOS oxide, same four
  ceria-coated-silica slurries, same runs. HDP monotonic rising (+0.75), TEOS
  reversing at 156 nm. The patent states it at [0120]: "particle size and
  particle size distribution affected HDP silicon dioxide films and TEOS films
  differently even though both films essentially comprise silicon oxide films."

Sorting by abrasive chemistry explains more of the spread than sorting by film:
ceria and ceria-coated silica give large positive exponents (+0.75 to +1.0),
plain silica gives about zero or an interior maximum.

### Proving the row pairing before trusting the patent numbers
The patent's PDF text layer scrambles the A/B/C/D label column, so the
size-to-rate correspondence was established arithmetically from two printed,
self-consistent ratio columns rather than assumed:

* Table 1's own `D50/(D99-D50)`: 156.1/146.5 = 1.066 ~ 1.07; 117.2/65.5 = 1.789
  ~ 1.79; 210.7/106 = 1.988 ~ 1.99; 88.7/69.8 = 1.271 ~ 1.27.
* Table 2's own TEOS/HDP ratio: 1311/2041 = 0.642 ~ 0.64; 1828/1807 = 1.012 ~
  1.01; 2223/2299 = 0.967 ~ 0.97; 875/1158 = 0.756 ~ 0.76.

Checking every alignment permutation, only one fits, to within 0.004. Row
identity then follows from the patent's prose about particles A and D.

### How the engine uses this
Where a pack carries a sourced sweep for **its own film**, the measured exponent
overrides the derived one — Cu uses +0.33 (Lai 2001 MIT thesis Table 3.6,
confirmed against the thesis prose's own 2.2x and 1.2x ratios) instead of the
-1.67 its branch and load sharing imply. Oxide stays `null`, because its
response is non-monotonic and depends on both abrasive chemistry and deposition
method; a single number would be false, so the derived exponent is used and the
regime is flagged `unverified`.

---

## Abrasive TYPE: what changes when you swap ceria for silica

### The gap this closes
`slurry.abrasive.kind` was accepted by the schema, stored on the recipe, and
used to look up particle properties — but it did not reach the rate. Sweeping
silica → ceria → alumina → zirconia on the oxide pack returned **1601 Å/min for
all four**. `abrasives.yaml` was a 1,500-line database that no Python module
imported.

This matters more than a missing factor, because the abrasive is the first thing
a slurry formulator changes.

### Why a hardness ratio is NOT used
The tempting fix — scale the rate by particle hardness — is wrong, and
`abrasive_effects.py` refuses to do it:

* Ceria (6.4 GPa) removes SiO₂ roughly **3×** faster than alumina (≈20 GPa)
  achieves on that film. Harder cuts *slower* here.
* Silica polishes sapphire, which is far harder than silica itself.

Ceria's advantage on oxide is **chemical tooth** (Ce–O–Si bond formation), not
indentation. A Mohs or GPa ratio presented as a rate ratio would be an invented
number wearing someone else's citation.

### The anchor model
Each pack's `kp_m_per_pa` was back-calculated from a measurement that already
contained one particular abrasive. That abrasive is now declared explicitly:

| pack | `reference_abrasive` |
|---|---|
| `oxide_silica`, `poly_si_alkaline`, `si_substrate_alkaline` | `colloidal_silica` |
| `sti_ceria`, `sic_ceria_h2o2` | `ceria` |
| `cu_h2o2_bta`, `w_fe_oxidizer` | `alumina` |

Swapping the abrasive invalidates the **absolute scale**, not merely the
exponents. Rescaling requires a ratio measured on the *same tool, same recipe,
abrasive-only-swapped* — the only comparison in which pad, pressure, velocity,
pH and oxidizer all cancel. Those live in `abrasives.yaml → relative_rate`.

Such comparisons are rare, so that table is mostly `null`, and **the emptiness is
the honest state**. Where no ratio exists the engine applies *no* scale factor
and flags the result `ranking_only`: usable to compare recipes, not to quote a
predicted rate. Both UIs show this directly under the number.

Ratios are never **chained**. A ratio declared against a reference other than the
pack's own is refused, because multiplying two ratios measured on two different
tools multiplies their errors.

### Withdrawing the exponents
A pack's measured `abrasive_size_exponent` belongs to the abrasive it was
measured with. The sign does not even survive the swap:

| abrasive | size exponent on oxide |
|---|---:|
| colloidal silica | −0.05 |
| alumina | +0.29 |
| ceria | +0.87 |

So on a swap the pack's measured exponents are **withdrawn** and the run says
which ones and why. Withdrawal is explicit rather than a reset to `null`:
`null` was never neutral — it selects the derived −0.84, which is wrong in sign
for 8 of the 10 published sweeps (BLOCKED #3). The withdrawn axes are listed in
`result.abrasive_type.withdrawn`.

### Why `Abrasive.kind` now defaults to `None`
It used to default to `"silica"`. Harmless while the type had no effect —
actively wrong once it did, because every recipe that never mentioned an
abrasive silently became a *deliberate silica swap*, including the ceria
validation datasets. A default must never masquerade as a user's choice.
`None` means "use the pack's own abrasive"; a string means the user chose.

## The pH optimum belongs to the slurry SYSTEM, not to the film

### The contradiction that forced this
Every pack carried one `ph_peak` per film, because a pH bell is a chemical
property and chemistry was modelled per film. Two measurements on the *same*
film refute that outright:

| slurry | film | measured optimum | span over the sweep |
|---|---|---:|---:|
| plain colloidal silica, 20 wt%, 0.25 M K⁺ (Li 2021) | TEOS/SiO₂ | pH **11** | 1.2× |
| aminosilane core-shell colloidal silica, 3 wt% (US 9,422,456 B2 Table 3) | TEOS | pH **4.9** | **57×** |

Same film, same abrasive family, same pad class (IC1010), optima six pH units
apart and sharpness differing by a factor of fifty. No single bell reproduces
both: forced onto US 9,422,456 B2's 22 points, the pH-11 shape scores
**126.6 %** shape error.

### Why, physically
The core-shell particle's shell carries a hydrolysed aminopropyl
trialkoxysilane, so the *particle* is cationic where plain silica is anionic.
The patent measures it on the same slurries: ζ = **+34 mV at pH 2.5**, +25 mV
at pH 4.9, **−51 mV at pH 8.4**. TEOS is already negative above its own IEP
(≈2.5). Removal therefore peaks where particle–film attraction is strongest and
collapses once the amine deprotonates and both surfaces turn negative. Plain
silica has no such shell and rides the alkaline-hydrolysis route (Cook 1990)
instead, whose optimum sits near pH 11.

So the optimum is a property of the *particle–film charge pair*, i.e. of the
slurry system. The fix is a separate pack, `oxide_silica_aminosilane`, not a
wider bell — widening predicts a rate everywhere and the right rate nowhere.
This is the same discipline `sti_ceria` already applies for ceria.

### What was fitted, and what was not
Peak position is **measured** (the maximum of the printed table), not fitted —
the same rule the oxidizer term uses, because a peak fitted from data on one
side of it is not identifiable. Width and the two floors are fitted to the 22
points with one overall scale free:

```
f(pH) = floor_side + (1 − floor_side)·exp(−((pH − 4.9)/1.24)²)
        floor_side = 0.014 (acid) | 0.018 (alkaline)
```

| shape | MAPE on the 22 points |
|---|---:|
| inherited pH-11 bell | 126.6 % |
| predict the dataset mean | 734 % |
| this pack | **25.3 %** (leave-one-out 26.1 %) |

The floors are anchored by measurements rather than by the fit's freedom:
30 Å/min at pH 9–10 against a 1720 Å/min peak *is* 1.7 % of peak. Unlike the
parent pack's strongly asymmetric 1 % / 12 %, both floors here land near 2 % —
on a cationic-shell abrasive the loss mechanism is electrostatic at *both* ends
(the particle loses its charge going up, the film going down), so there is no
reason to expect asymmetry.

Effect on the corpus: the pH axis median falls **49.2 % → 39.3 %**, and pH is
no longer the model's worst axis (velocity, 44.1 %, now is).

### The limit this dataset exposes, and does not fix
Table 3 measures every pH at **both** 2.0 and 4.0 psi. The pressure response is
itself a function of pH:

| pH | 2.5 | 3.0 | 3.5 | 4.0 | 4.6 | 4.9 | 5.8 | 8.4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rate(4 psi)/rate(2 psi) | 1.00 | 0.96 | 0.91 | 1.67 | 1.78 | 1.71 | 1.26 | 6.67 |

Below pH 3.5, doubling the down force changes **nothing**: removal is
chemically starved and Preston's law is not the governing equation there. This
engine multiplies a chemical factor by a Preston P·V term, so it *must* predict
2× for a 2× load everywhere — the 50–65 % residuals at pH 2.5–3.5 are that
structural limit showing, not noise. Closing it needs a rate-limiting-step
(series-resistance) form, not another constant; recorded as a `null` key with
`TODO(owner)` in the pack and asserted as data in
`tests/test_ph_system_split.py::test_below_ph_3_5_the_measured_rate_ignores_pressure`.

## Is the velocity axis weak, or is the corpus thin?

`cmp-sim accuracy --axis velocity` reported a 44.1 % median and that promoted
velocity to "worst axis". The number is not a velocity measurement. The axis
filter selects every dataset in which speed varies *among other things*, so an
L25 that moves speed, pressure, pH, abrasive loading and dispersant together
donates its entire error to the velocity column.

### Isolating the axis
Group the rows of each dataset so that every field except platen speed is
identical, keep only groups with two or more distinct speeds, and fit one scale
per group. Across the whole 49-dataset corpus that leaves **29 points in 11
groups from 3 datasets**:

| dataset | groups | pts | MAPE | measured exponent in MRR ∝ V ⁿ |
|---|---:|---:|---:|---:|
| Mariscal 2020 PETEOS/ceria 3×3 | 3 | 9 | **11.7 %** | **+0.86** |
| US6918821B2 Cu/IC1000 | 2 | 6 | 36.8 % | +0.22 |
| sic2023 shear-rheological L9 | 3 | 9 | 68.6 % | −1.40 |
| US6564116B2 oxide L25 | 0 | 0 | — | — |
| yang2023 quartz L25 | 0 | 0 | — | — |

The conclusion inverts the headline. On the one **in-scope** dataset that
isolates velocity the error is 11.7 %, and the measured exponent is +0.86
against Preston's +1.0 — sub-linear, but not a different law. The two datasets
dragging the median are documented exclusions: US6918821B2 is the repo's
lubrication-transition negative control, and sic2023 is shear-rheological
polishing rather than rotary CMP (`in_scope: false`, exponent −1.40, i.e. the
rate *falls* with speed).

Velocity is the **thinnest** axis in the corpus, not the weakest model term,
and the honest fix is data, not a new constant. Asserted in
`tests/test_velocity_axis.py`, which fails if the isolated-point count grows —
so the diagnosis is re-done rather than silently inherited.

### Why a Taguchi array can never settle this
An orthogonal array never repeats a chemistry at two speeds; that is what makes
it orthogonal. US6564116B2 and yang2023 both appear under
`--axis velocity` and contribute **zero** isolated velocity points between
them. Any axis median that includes them is measuring the model's response to
everything at once.

### A data-fidelity bug this exposed
`legacy/.../yang2023_quartz_ceria_L25.yaml` recorded only two of the paper's
six factors — pressure and speed. Abrasive concentration, pH, dispersant
concentration and slurry flow changed on every row and were not written down,
so the harness read four chemical factors' worth of scatter as velocity error.
The local override restores all six from Table 1 + Table A1 of the PMC
full-text. The dataset's honest score goes 32.4 % → 69.0 % — *worse*, because
it is now being asked the question it actually answers, and the paper's own
extreme-difference ranking puts pressure first and speed behind three chemical
factors. It stays `in_scope: false` (quartz glass, CeO₂–LaOF composite).

## The oxidizer floor belongs to the mechanical path

The oxidizer term is additive at zero concentration:

```
rate ∝ floor + (1 − floor)·shape(C)
```

`floor` is the abrasive-only rate at zero oxidizer, as a fraction of the
reference rate. A purely multiplicative term would predict **zero removal with
no oxidizer**, which no measurement supports — an abrasive under load removes
material regardless.

The inherited knowledge base is explicit that this constant is set by the
MECHANICAL path, not by chemistry: it converges to 0.12–0.27 across four
independent free-abrasive metal systems, holds across metal species, pH 2–9 and
with or without a complexant, rises to 0.28–0.37 with hard abrasives at high
load — and **falls to ~0.02 when the abrasives are removed**.

### The dataset that made the distinction matter
US 8,070,843 B2 polishes W with a **fixed-abrasive pad and an abrasive-free
solution**. Scored with the pack's free-abrasive 0.14 it reported 51.7 %, the
worst oxidizer result in the corpus. Per point:

| H₂O₂ wt% | 0.00 | 2.03 | 4.06 | 4.07 | 6.10 |
|---|---:|---:|---:|---:|---:|
| error, pack floor 0.14 | **+220.5 %** | +26.6 % | +0.4 % | −0.2 % | −10.7 % |
| error, measured floor 0.040 | +8.8 % | +23.8 % | +0.9 % | +0.4 % | +9.4 % |

The whole headline was one row. The floor this system actually has is printed
in the same table it is being scored against: 96 Å/min at 0 wt% over
2396 Å/min at 4.06 wt% = **0.040**, read from two rows, not fitted.

### What the improvement does and does not prove
Declaring the floor necessarily fixes the zero row — the floor *is* that
ratio, so the move from 51.7 % to 8.7 % is close to tautological on that point.
The number that measures the MODEL is the four oxidizer-bearing rows, and they
are essentially unchanged: **9.5 % → 8.6 %**. Nothing was tuned; a measured
constant was moved out of the table and into the model, and the headline
stopped being dominated by a formulation the pack was never told about.

The pack keeps its own 0.14, which is correct for the free-abrasive systems it
was measured on. The override lives in the dataset, the same discipline
`du2004_cu_h2o2_concentration_sweep.yaml` already uses for its glycine-free
peak position: a constant that belongs to the FORMULATION is declared by the
formulation, not merged into the film's pack.

The dataset stays `rank_only`. Its absolute-rate bias — the pack's Kp sits
1.8–3.4× above three independent Preston back-calculations — is a separate,
still-open finding that this change does not touch.

## The oxidizer term's sign belongs to the pH branch — a regime gate

### The measurement that no refit can satisfy
Miranda 2004 ran a 2×2 factorial on electroplated copper. Same Cabot 5001
base, same EPAD-A100 pad, same 4 psi / 60 rpm / 200 mL min⁻¹, three replicates
per cell. Only pH and H₂O₂ moved:

| | H₂O₂ 1.5 wt% | H₂O₂ 3.5 wt% | change |
|---|---:|---:|---:|
| pH 4 | 1953 Å/min | 2908 Å/min | **+49 %** |
| pH 8 | 1743 Å/min | 243 Å/min | **−86 %** |

ANOVA: pH main effect *p*=0.0021, pH×H₂O₂ interaction *p*=0.0207, H₂O₂ alone
*p*=0.588 — not significant on its own. The paper reads this through Pourbaix:
acidic H₂O₂ produces soluble Cu²⁺ and removal rises; alkaline H₂O₂ above
~2.5 % grows a hard CuO film the abrasive cannot cut (Wei et al.: Cu₂O at
0.06 % H₂O₂, CuO at 2.5 %, both at pH 8).

Our oxidizer term multiplies the rate by a factor of concentration alone, so
within one pack the ratio between two concentrations is identical at every pH.
The data demand 1.49 on one leg and 0.14 on the other. **One constant cannot be
both**, for any value of it — a functional-form limit, not a tuning error.

### What was done instead of fitting
`cu_h2o2_bta` now declares `oxidizer_ph_window: [2.0, 6.25]`, the range its
oxidizer constants were actually measured in. The bounds are read off the
provenance of the constants being gated — 6.25 is the acidic/alkaline branch
split the pH term already used (`cu_ph_acid_k` fitted on US2008/0090500A1
Table 4, 12 points, R²=0.954, all below it); 2.0 is the lowest pH in that same
set — **not** chosen to make a dataset score well.

Outside the window the oxidizer term is switched off, both the peaked branch
and the inherited monotonic one, and the caller is told:

> oxidizer term GATED at pH 8: this pack's oxidizer constants were measured
> between pH 2 and 6.25, and the SIGN of the oxidizer response is known to flip
> across the copper Pourbaix boundary … This is a declared gap in the data, not
> a claim that oxidizer is unimportant.

pH itself keeps predicting across the boundary; only the one unsupported term
goes quiet.

### Making silence scoreable without making it free
A declined row is neither a prediction nor a failure, so `score_dataset` now
separates them. Two rules keep the gate from becoming a way of dodging a bad
score:

1. **A gate only invalidates a score if the dataset varies the gated axis.**
   `lai2001` runs at pH 7 but never moves H₂O₂; the switched-off term is then a
   constant that cancels out of a shape comparison, so the dataset is still
   scored on the size axis it does probe. Without this rule the gate silently
   removed three sound datasets.
2. **Gated rows are always counted and reported**, in `gated_points` and in the
   accuracy table, even where they change nothing.

`test_oxidizer_ph_regime_gate.py` pins all of it, including the anti-laundering
rule and an explicit assertion that exactly two datasets are declined.

### The honest ledger
Corpus median went 20.2 % → 19.5 % (LOO 22.6 % → 21.7 %), but **not** because
the physics improved: two datasets the model was answering wrongly are now
declining to answer. That is a real gain in usability — a 107 % prediction that
looks confident is worse than a refusal that names the missing experiment —
and it is not a gain in accuracy. Closing it needs an alkaline-branch Cu/H₂O₂
sweep with an inhibitor present, which is recorded as `TODO(owner)` in the pack.

## The copper pH optimum is a bound, and it comes from one slurry system

`cu_h2o2_bta` carried `ph_peak: 4.0` at `confidence: low`, justified as "the
pack's own operating pH", with the note: *a sweep across pH 2–6 would pin it*.
That sweep was already in the repository.

US 2008/0090500 A1 TABLE 4 varies pH 3/4/5/6 at three silica loadings with
glycine, BTA, H₂O₂, load, speeds, flow and time all fixed — the same table
`cu_ph_acid_k` was back-fitted from — and the rate falls monotonically at every
loading:

| silica | pH 3 | pH 4 | pH 5 | pH 6 |
|---|---:|---:|---:|---:|
| 2 wt% | 597 | 537 | 483 | 393 |
| 3 wt% | 705 | 617 | 528 | 451 |
| 4 wt% | 801 | 644 | 565 | 520 |

(Å/min.) There is no interior maximum, so **the optimum lies at or below pH 3**
— a bound, not a measured peak. The old value placed the model's maximum inside
a measured falling limb: it predicted a *rise* from pH 3 to 4 where all three
series drop 10–24 %.

### The peak goes at the edge of the data
3.0 is the lowest pH measured. Putting the peak there is the weakest claim the
data support; anything lower extrapolates into pH nobody probed. Refitting the
width on the same 12 points gives 4.45 and takes the shape error from
**10.13 % → 4.29 %**. The width fit is shallow (4.0 → 5.35 %, 5.0 → 5.31 %), so
the note explicitly warns against reading 4.45 as precise.

### The pooling trap, avoided on purpose
US 9,200,180 B2 continues the fall to pH 9.9, and using both legs would give 17
points instead of 12. **It would be wrong.** That series is BTA-free and
benzenesulfonic-based, and this repository already files it under a separate
pack, `cu_alkaline_benzenesulfonic`. Pooling two slurry systems to tighten a
constant manufactures agreement — the same error `oxide_silica_aminosilane` was
split off to avoid, where one TEOS film peaks at pH 4.9 with one abrasive and
pH 11 with another.

The fitted numbers happen to come out the same either way. The *justification*
does not, and only the system-matched 12 points are cited. `ph_mechanical_floor`
does still rest on the other system — kept, because a floor is a claim about
the mechanical background surviving when chemistry stops helping, which
transfers better than an optimum position — and it now says so in the entry
rather than looking like same-system evidence.

### What this did not do
Nothing to the corpus median. The acidic table prints no down force, so it
cannot be scored at all, and it is calibration data besides. The change is
justified by shape against a printed table, and the test suite asserts that it
is invisible to the headline — so that a future edit making the dataset
scorable fails loudly instead of silently inheriting an unearned claim.

## The pH axis is not thin — and the optimum belongs to the abrasive's charge

### First, the diagnosis that had to come before any refit
When velocity looked like the worst axis, isolating it dissolved the problem:
only 29 points in the corpus vary speed with everything else fixed, and on the
one isolated sweep the error was 11.7 %, not 44.1 %. The same test had to be run
on pH before touching a pH constant, because a pooled median cannot distinguish
*the term is wrong* from *these datasets move four things at once*.

Grouping rows so that **only** pH varies gives **12 groups and 66 points** —
more than twice velocity's isolated set — and an isolated median of ~30 %
against a pooled 39.3 %. Isolation does not rescue pH. The term really is the
weakest physics in the model, and there is enough data to work on it.

### What the isolated groups then showed
The worst of them, at 94.7 %, was CN 109609035 B: anionic colloidal silica on
TEOS oxide, 7 pH levels at fixed loading, pressure and flow.

| pH | 2.0 | 2.5 | 3.0 | 3.5 | 4.0 | 5.0 | 6.0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| measured (Å/min) | 109 | 32 | 16 | 15 | 11 | 5 | 12 |
| `oxide_silica` predicted | 2.2 | 2.3 | 2.5 | 2.8 | 3.5 | 7.3 | 18.3 |

The model predicted a *rise* across the range where the patent measures a 9×
fall, and sat two orders of magnitude low. Not a mis-set constant — the wrong
system.

### Three silica systems, three optima, nine pH units apart
The repository now holds three pH sweeps on the **same TEOS film with the same
abrasive mineral**, and their maxima are ordered by the abrasive's surface
charge:

| pack | abrasive | optimum |
|---|---|---|
| `oxide_silica_anionic` | anionic silica, 1 wt% | ≤ pH 2 |
| `oxide_silica_aminosilane` | cationic core-shell | pH 4.9 |
| `oxide_silica` | plain silica, 20 wt% | pH 11 |

The mechanism is electrostatic and is stated by the patents themselves. TEOS
oxide is negative above its isoelectric point (~2.5). An **anionic** particle is
therefore repelled as soon as the surface charges up, so removal survives only
at the acid end. A **cationic** shell is attracted instead, peaking in mid-acid
until its amine deprotonates and both surfaces turn negative. **Plain** silica
has neither and follows the alkaline hydrolysis route.

So the pH optimum is a property of the slurry system, not of the film — the
same conclusion the aminosilane split reached, now confirmed by a third point
that extends the ordering in the opposite direction. Each gets its own pack;
widening one bell to span pH 2–11 would predict a rate everywhere and the right
rate nowhere, and would destroy Li 2021 (currently 0.2 %).

### The honest residual
The split takes CN 109609035 B from **94.7 % to 32.1 %**, and stops there. The
measured series turns **up** at pH 6 (5 → 12 Å/min), and a monotone-decaying
bell cannot rise again — with every parameter free, the best this functional
form manages on these 7 points is ~24 %, with the residual concentrated on that
one point. The patent reads the upturn as the alkaline hydrolysis route
switching on, i.e. a *second mechanism*, not a wider bell. Closing it needs two
additive pH channels — a change to the functional form and to every pack that
uses it — so it is recorded in the pack and in a test rather than fitted around.

Corpus effect: pH axis 39.3 % → 32.1 %, and four datasets that could not be
scored at all (no pack knew their film) now score.

## There is no universal "second pH channel" — a hypothesis, falsified

Three datasets left residuals shaped like a missing second mechanism, and the
rule was set before any code was written: check whether it is the **same**
second channel in all three; if so, derive one additive two-channel pH response
and apply it to every pack; if not, say so and stop. Do not add a per-pack
fudge term.

It is not the same channel. The three measured shapes are different shapes:

| dataset | system | shape |
|---|---|---|
| CN 109609035 B | anionic silica / oxide | monotone fall, slight upturn at pH 6 |
| Dandu 2009 | ceria / oxide | single bell, peak pH 4–5.5 |
| Netzband 2020 | ceria / oxide | a **V**: minimum at pH 6, both ends high |

The last two are the **same pack** (`sti_ceria`), same film, same abrasive
mineral — and they disagree about the shape itself, not about a constant:

```
dandu2009     43 → 953 → 2763 → 3474 → 3443 → 3504 → 993 → 694 → 643   (pH 2→10)
netzband2020  198 (pH 4) → 113 (pH 6) → 200 (pH 8) → 213 (pH 10)
```

A bell with one maximum cannot also be a V with one minimum. And the arithmetic
kills the proposed fix directly: Netzband is under-predicted **4.3×** at pH 8
and **4.6×** at pH 10, so a rising alkaline channel would have to lift the model
several-fold there — exactly where Dandu already matches to **1.03** and
**0.96**. Fixing one breaks the other.

The anionic dataset does not support the channel either: its dominant residual
is a single point at pH 5 (ratio 0.44), while the pH 6 upturn it was supposed to
explain sits at 1.06 — already fine.

### What was done instead
Nothing to the model. The contradiction is pinned as a measurement-level fact in
`tests/test_no_universal_second_ph_channel.py`, including a direct guard on
Dandu's alkaline agreement, so that any future edit introducing a generic
alkaline term must confront both ceria datasets rather than quietly trading one
for the other.

### Where the real lead points
Netzband & Dunn's title names a mechanism our pH term has no channel for: the
**cerium oxidation state**. Their paper varies Ce³⁺/Ce⁴⁺ deliberately, and
`sti_ceria` carries `ce3_fraction` as a *fixed* number with the pack's own note
saying no closed form was found in the literature. A pH-dependent Ce³⁺ fraction
would be a ceria-specific coupling — not a universal second pH channel — and it
needs its own evidence before it is built. Recorded, not guessed.

## The velocity exponent cannot be resolved by this corpus — so it is not fitted

Preston's law puts the velocity exponent at exactly 1.0. The corpus was asked
whether that holds, under the rule written down before any code: fit an exponent
to every *isolated* velocity group (only speed moves), report the spread, and if
they scatter across 1.0, say the axis cannot resolve it and stop.

Every in-scope isolated group, log-log slope of rate against platen speed at
fixed down force:

| dataset | pressure | exponent | measured rates |
|---|---:|---:|---|
| US 6,918,821 B2 | 1.5 psi | **−0.42** | 425 → 419 → 250 |
| Mariscal 2020 | 4.0 psi | +0.62 | 2064 → 3079 → 3463 |
| Mariscal 2020 | 3.0 psi | +0.86 | 1404 → 2529 → 2838 |
| US 6,918,821 B2 | 4.0 psi | +0.86 | 594 → 1384 → 1636 |
| Mariscal 2020 | 2.0 psi | +1.10 | 698 → 1558 → 1718 |

Preston says all five should be +1.0. They span 1.5 in exponent, and one is
**negative** — rate *falls* as speed rises.

### Why even a pressure-dependent exponent is not writable
The obvious rescue is to make the exponent a function of down force. The two
datasets demand opposite functions:

```
Mariscal 2020     exponent FALLS with pressure    1.10 → 0.86 → 0.62
US 6,918,821 B2   exponent RISES with pressure   −0.42 → 0.86
```

A single fitted constant would land near 0.86 — wrong at both ends of both
datasets, while improving a pooled median. That is exactly the failure mode the
stop rule exists to prevent, so nothing was fitted.

### The negative group is evidence, not noise
US 6,918,821 B2 exists to make that measurement: a conventional IC1000 pad
*loses* copper removal rate as speed rises at low down force, which is the
patent's argument for fixed-abrasive pads. Mechanistically it is the slurry-film
/ lubrication regime — faster sliding thickens the fluid film and lifts asperity
contact — which the Preston form has no channel for, and which is the first
point any global fit would discard as an outlier.

So the finding is not a constant. It is that `velocity 44.1 %` is a **regime**
boundary the model does not represent, and the honest statement is that the
corpus contains two velocity datasets, in different regimes, that cannot be
reconciled by an exponent. Pinned in `tests/test_velocity_exponent_unresolvable.py`,
including a guard that fails if any pack ever declares `velocity_exponent`.

## The lubrication gate would be WRONG, not merely premature

The velocity diagnosis ended at a regime the Preston form has no channel for:
US 6,918,821 B2 measures copper rate *falling* as speed rises at 1.5 psi. Since
`core/regime.py` already classifies lubrication, the question was whether an
existing flag separates those rows — and if not, whether a published criterion
does, with the missing quantity named rather than a threshold invented.

### The flag cannot fire
`classify_lubrication` splits λ = film thickness / pad roughness at
`LAMBDA_BOUNDARY = 1.0`. Every row of both velocity datasets lies between
**λ = 0.0135 and 0.187** — one to two orders of magnitude below it. All fifteen
classify as `boundary`, including the three whose rate falls with speed. That
is correct Stribeck physics, not a mis-tuned flag: CMP is supposed to run in
boundary contact.

### And no calibration would rescue it
The obvious objection is that λ is merely *uncalibrated*: it divides a modelled
film thickness — a function of an assumed viscosity — by an assumed pad
roughness, and neither source reports either. Get one dataset with a measured
film thickness, the argument goes, and the gate becomes possible.

The arithmetic refuses. In this model, to five digits on every row:

```
λ = 0.001401 × (rpm / pressure)
```

λ **is** the pseudo-Sommerfeld number *V/p* of the CMP lubrication literature,
up to a single multiplicative constant. (Wu & Liao, *Lubrication in Chemical and
Mechanical Planarization*, Advances in Tribology 2016, doi:10.5772/64484, which
also records the standard convention that the effective slurry film thickness
δ_eff is taken as the pad's arithmetic average roughness — exactly what this
model assumes.) Measuring viscosity and roughness fixes that constant. **A
constant cannot reorder anything**, so it cannot manufacture a separation that
is not already present.

And the separation is not present:

| rows | λ |
|---|---|
| rate **falls** with speed (1.5 psi) | 0.056, 0.112, 0.187 |
| rate **rises** with speed (4.0 psi) | 0.021, 0.042, 0.070 |

They overlap: a threshold would have to be below 0.056 *and* above 0.070 at
once. Worse, Mariscal 2020 — nine rows that never invert under any combination —
spans λ 0.0135–0.0628, sitting **inside** the inverting range.

### What that actually means
The velocity inversion is not a Stribeck phenomenon in the data available. Both
datasets are boundary-lubricated by every published criterion and still behave
oppositely, so the discriminating variable is something else. Down force enters
the two datasets with opposite sign, which points at **pad contact** — asperity
population and real contact area — rather than a fluid film.

So the earlier BLOCKED entry asking for a measured-film-thickness dataset was
itself wrong, and has been corrected: no such dataset would unblock this gate.
Pinned in `tests/test_lubrication_gate_is_wrong_not_premature.py`, which fails
if λ ever stops being proportional to V/p, or if the two groups ever separate.

### The one piece of real evidence that survives
Ranking each dataset's rows by λ against how badly the model over-predicts:

| dataset | n | Spearman ρ |
|---|---:|---:|
| US 6,918,821 B2 | 6 | **−0.714** |
| Mariscal 2020 | 9 | **−0.517** |

Both negative, independently, in different films, labs and abrasives: the higher
*V/p*, the more the model over-predicts, and the corpus's worst-predicted row
(1.5 psi / 200 rpm, measured/predicted = 0.027) is its highest-λ row. That is a
monotone trend, not a threshold — enough to keep, not enough to gate on.

## Pad contact does not separate the velocity inversion either

The lubrication result pointed here: both velocity datasets stay
boundary-lubricated, yet down force enters them with opposite sign, so the
discriminating variable looked like pad contact rather than fluid film. The
model already exposes three contact quantities, so the test was direct — does
any of them separate the inverting rows the way λ could not?

### Two are properties of the consumable set
`plasticity_index` and `pad_limited_plasticity_lambda` are constant **within**
each dataset: they describe the pad and film pair, not the operating point, so
they cannot separate rows that differ only in speed or down force.

They do differ *between* the datasets — plasticity index 0.0219 for
US 6,918,821 B2 against 0.0029 for Mariscal 2020 — but that points the **wrong
way**. The inverting dataset has the *more plastic* contact, which predicts more
removal, not the collapse actually measured.

### The third separates perfectly, and must still be refused
`summit_saturation` orders every row, and a threshold in 0.0111 < t < 0.0148
catches the inverting rows and nothing else:

| rows | summit_saturation |
|---|---|
| US 6,918,821 B2, 1.5 psi — rate **falls** | 0.01108 |
| Mariscal 2020, 2.0 psi — never inverts | 0.01478 |
| Mariscal 2020, 3.0 psi | 0.02217 |
| both datasets, 4.0 psi — rate **rises** | 0.02956 |

But across all fifteen rows, to six digits:

```
summit_saturation = 0.007390 × pressure_psi
```

It is down force rescaled by a pad constant — the same constant in both, because
both use the same pad stack. So *"gate when summit_saturation < 0.0148"* is
exactly *"gate when pressure < 2 psi"*: a threshold fitted to one patent's
low-pressure arm, wearing a contact-mechanics name.

That fails the standard already applied to the oxidizer pH window, which was
accepted only because the pack's constants were **measured** inside a stated
range. Here there is no measurement — one dataset inverts below 2 psi, the other
never goes below 2 psi, and nothing says which fact is causal.

This is the second time the same trap has appeared: λ looked like a lubrication
criterion and was V/p; `summit_saturation` looked like a contact criterion and
is P. Both are the operating point relabelled.

### What is missing, named
The inversion must come from how the asperity **population** changes under load
and sliding — density, radius, and whether the pad glazes at low force. No
dataset in the corpus reports pad surface statistics (asperity density or
radius, by confocal or AFM) alongside a rate-versus-speed sweep, so the
discriminating variable cannot be computed from what we have. That is the
BLOCKED-1 requirement, and `tests/test_contact_metrics_do_not_separate_the_inversion.py`
fails if a pressure-like gate is ever reintroduced under a contact alias.

## A missing pH term does not stay missing — it hides inside another term

`cu_alkaline_benzenesulfonic` declared **no pH response at all**: no peak, no
width, no floor. Its only pH-adjacent entry was `ph_ref: 4.0`, inherited from
the acidic parent and meaningless for a slurry run between pH 8.5 and 11.1.

### The visible symptom
US 9,200,180 B2's pH series measures a 3.4× fall — 732 → 214 Å/min from pH 6.2
to 9.9, with H₂O₂ and abrasive fixed. The model returned the *same number* for
all five rows and scored 51.0%, exactly its predict-the-mean baseline. A
constant is what predicting the mean *is*.

### The invisible symptom, which mattered more
The inherited pack sets `oxidizer_peak_wt_pct: 1.0`, justified in its own note
as placing the whole observed window on the *falling* side of the Kaufman peak
— a shape chosen so that rate decreases with oxidiser. Two datasets on this
pack test that claim, and they disagree:

| dataset | pH | H₂O₂ response |
|---|---|---|
| US 9,200,180 B2 | **drifts** 10.2 → 8.5 as acidic H₂O₂ is added | falls 208 → 77 Å/min |
| US 2011/0165777 A1 | **buffered** at 11.1 by KOH | flat, 160 → 157 Å/min |

The second patent states it outright: *"H₂O₂ 1–7% has little effect on copper
removal rate."* Same pack, opposite behaviour, and the variable that differs is
whether pH was held. **Part of what the pack called an oxidiser effect was a pH
effect wearing the oxidiser's label.**

### The fix and its evidence
The pH term was fitted to the pH series, with the peak pinned to the lowest pH
actually measured (6.2) rather than the free optimum (3.3), which lies outside
the data — the same bound discipline applied to `cu_h2o2_bta`. Cost of the
bound: 0.55% → 3.65% on the fitted series.

| dataset | before | after | |
|---|---:|---:|---|
| `us9200180b2_cu_ph_alkaline_sweep` | 51.0% | **3.7%** | fitted — *not* evidence |
| `us9200180b2_cu_h2o2_series` | 51.7% | **12.7%** | held out |
| `us9200180b2_cu_benzenesulfonic_series` | 29.6% | **26.8%** | held out |

The held-out improvements are the evidence; the fitted dataset's score is
disclosed as self-scoring and excluded from it. Both held-out sets also stopped
losing to predicting their own mean. Corpus median 20.2% → **19.5%**, LOO 22.6%
→ **21.7%**.

The buffered dataset (`us20110165777a1`) still scores 33.8% and still loses to
its mean — correctly. Its measured spread is 4%, which the patent attributes to
measurement scatter, so there is no trend to get right; that is now the honest
residual rather than a term absorbing someone else's physics.

## Pack blindness audit — silence must be sourced, not accidental

The `cu_alkaline_benzenesulfonic` finding generalises into a check. A pack that
declares **no response on an axis its own datasets sweep** is not merely
incomplete: the missing term's work is absorbed by whichever term is still free
to move, and that term's constants then get justified by a trend belonging to
something else. That is exactly how a pH drift ended up as an oxidiser shape
constant.

So the check is run mechanically over every pack: compare the parameters it
declares against the axes its registered datasets actually vary.

### Result: one hit, and it is legitimate
Only `w_fe_oxidizer` is silent on an axis it sweeps (pH). US 2011/0186542 A1
runs a two-level pH control — pH 3 against pH 6 at **matched** oxidiser and
abrasive loading, six matched pairs:

| H₂O₂ | abrasive | pH 3 | pH 6 | ratio |
|---:|---:|---:|---:|---:|
| 0.0 | 0.01 | 289 | 246 | 0.851 |
| 1.0 | 0.01 | 1100 | 1320 | 1.200 |
| 3.0 | 0.01 | 2270 | 2110 | 0.930 |
| 0.0 | 0.02 | 363 | 298 | 0.821 |
| 1.0 | 0.02 | 1650 | 1610 | 0.976 |
| 3.0 | 0.02 | 2430 | 2360 | 0.971 |

Mean ratio **0.958** — a 4% effect — and the **sign is not consistent**: more
acid raises the rate in one pair and lowers it in five, by amounts comparable to
run-to-run scatter. Over the same table the oxidiser axis moves the rate by a
factor of **8**.

Fitting a bell to that would be fitting noise, and would hand the pH term credit
for variance that belongs to the oxidiser. The physics agrees: tungsten removal
here is controlled by Fe(III)-catalysed H₂O₂ oxidation and the mechanical
removal of the resulting oxide, not by the pH of the medium, over pH 3–6.

### The distinction that matters
A **sourced null result** and an **omission** look identical from outside — both
are a pack saying nothing — but they are opposite in meaning. So the null result
is declared in the pack, with its table and its scope, and registered in the
audit; the audit re-derives the claim from the six matched pairs rather than
trusting the declaration.

⚠ Scope: the null covers pH 3–6 only. Nothing licenses an alkaline W slurry;
outside that window the honest behaviour is to decline, not to extrapolate a
flat response.

## A peak pinned to the edge of the data has an unmeasured side

Three packs now carry a `ph_peak` that is deliberately a **bound** rather than a
fitted optimum — `oxide_silica_anionic` (2.0), `cu_alkaline_benzenesulfonic`
(6.2), `cu_h2o2_bta` (3.0) — each sitting at the lowest pH its source table
contains, because free fitting wanted a maximum at a pH nobody polished at.

That discipline fixed one problem and created a quieter one. When the peak *is*
the edge of the data, everything beyond it is the assumed bell and nothing else.
And `ph_acid_mechanical_floor` is frequently 0, precisely because there is no
measured acid limb to floor. So the model decays to nothing, with confidence:

| pH | status | predicted |
|---:|---|---:|
| 2.0 | measured | 213.60 Å/min |
| 1.0 | unmeasured | 3.90 Å/min |
| 0.5 | unmeasured | **0.00 Å/min** |

A CMP slurry that removes *exactly nothing* is not a prediction; it is the tail
of a Gaussian being read as physics. The existing "more than 2.5 widths from the
optimum" warning does not catch it either — at pH 1.0 the distance is 2.0
widths, so the number came back clean.

### The fix
Each such pack declares `ph_valid_range`, the span of the source table its pH
constants were fitted to, and the engine warns when asked outside it — naming
the floor it is using on that side, and stating explicitly that a **zero** floor
makes the answer a refusal rather than a number:

> pH 0.5 is OUTSIDE the range this pack's pH constants were measured over
> (2–6), below it. The pH term is extrapolated with a floor of 0.000 on that
> side, which is ZERO: the predicted rate decays towards nothing with no
> measurement supporting it, so treat it as a refusal rather than as a number.

Above the range, where the alkaline floor *is* measured, the same warning fires
without the refusal language — the two cases are genuinely different and the
wording distinguishes them.

Note that `cu_h2o2_bta` now carries two separate ranges: `ph_valid_range`
(3.0–6.0, scoping the pH constants) and `oxidizer_ph_window` (2.0–6.25, scoping
the oxidiser constants). They are claims about different terms, measured in
different experiments, and are deliberately not merged.

This is the validity-range half of the pack audit: the blindness audit asks
whether a pack declares a term at all; this asks whether the term states where
it may be believed.

## An inert constant that looks active is worse than no constant

`sic_ceria_h2o2` declared `ph_response_width: null` deliberately, and the
reasoning went as far as it went correctly: SiC is oxidation-limited rather than
hydrolysis-limited, its reported pH dependence runs opposite to silica's, and the
inheritance chain (SiC → `sti_ceria` → `oxide_silica`) would otherwise hand it
its parent's **acid-side** ceria optimum of pH 4.5. Nulling the width switched
the term off rather than guessing a SiC optimum.

But switching the term off did not remove the inherited peak. The pack was left
declaring `ph_peak: 4.5` with no width — a constant that *looks* like a SiC
optimum and does nothing. The engine already warns about exactly this shape of
mistake ("declares an optimum pH but no `ph_response_width`, so pH is INERT");
the warning existed and the condition persisted anyway.

### The stated justification was checkable, and it was wrong
The note said the DOE50 set "varies pH together with oxidizer and pressure, so it
cannot isolate the pH axis". True of the set as a whole, false of its structure.
Grouping the 50 rows so that **only** pH moves leaves five isolated groups:

| pH 9 | pH 10 | pH 11 |
|---:|---:|---:|
| 26.7 | 31.1 | 62.7 |
| 18.1 | 66.1 | 66.9 |
| 19.6 | 60.0 | 63.3 |
| 40.0 | 29.1 | 24.9 |
| 15.2 | 45.1 | 38.7 |

Enough to fit peak, width and floor: **pH 10.5, width 1.25, floor 0.10** at
27.5% shape error, against **57.1%** with the term inert. The fitted optimum is
alkaline — which is what the pack's own mechanism argument predicted, and the
opposite of the 4.5 it was protecting against.

Unlike the three bounded-peak packs, this optimum is **interior** to the measured
range: the data bracket it on both sides. The range is narrow (9–11), so the
position is better supported than the width, and `ph_valid_range: [9.0, 11.0]` is
declared accordingly.

### The trade, recorded
Activating the term improves the DOE50 set from 39.3% → **34.0%** and slightly
worsens three held-out SiC datasets that sweep other axes at fixed pH
(liang2026 18.1 → 19.4, su2011_size 4.2 → 4.4, wei2026 3.1 → 3.2), because their
`Kp` normalisation now runs through a pH term that is no longer identically 1.
Net strongly positive, but not free — a future re-fit should know it.

An aside worth keeping: the first version of the test for this asserted the new
peak differs from `oxide_silica`'s. It failed, because `oxide_silica` sits at 11.0
and SiC's fit landed at 10.5. The inherited value to guard against is the *direct
parent's* 4.5, not the grandparent's — the test was asserting the wrong lineage.

## A validity range is the fitting experiment's span, never the union

Extending `ph_valid_range` from the three bounded-peak packs to *every* pH-active
pack raised a question the first three did not have: a pack used by **several**
datasets has several pH spans. Which one is the range?

Not the union. Nine datasets reference `oxide_silica` and their pH values span
**1.75 to 12.5**, but eight of them hold pH *fixed* at a single value and
therefore constrain nothing whatever about the pH response — they simply inherit
it. Only `li2021` sweeps pH (10.0 / 11.0 / 12.5), and it is the calibration set
`ph_response_width` was fitted to.

Declaring the union would claim support no experiment gives: no single
measurement here brackets pH 1.75–12.5, and a pack asserting validity across
eleven pH units on the strength of nine unrelated fixed-pH runs is precisely the
overreach this field exists to prevent.

So the rule is: **the range is the span of the experiment the constants were
fitted to.**

| pack | fitting experiment | range | peak |
|---|---|---|---|
| `oxide_silica` | li2021 | 10.0–12.5 | 11.0 (interior) |
| `oxide_silica_aminosilane` | US 9,422,456 B2 T3 | 2.5–11.0 | 4.9 (interior, measured) |
| `sti_ceria` | dandu2009 | 2.0–10.0 | 4.5 (interior) |
| `sic_ceria_h2o2` | DOE50 | 9.0–11.0 | 10.5 (interior) |
| `oxide_silica_anionic` | CN 109609035 B | 2.0–6.0 | 2.0 (**bound**) |
| `cu_h2o2_bta` | US 2008/0090500 A1 T4 | 3.0–6.0 | 3.0 (**bound**) |
| `cu_alkaline_benzenesulfonic` | US 9,200,180 B2 | 6.2–9.9 | 6.2 (**bound**) |

The aminosilane pack gets the widest honest range of any pack here — 2.5 to 11.0
— because one experiment really does bracket it.

### The consequence, stated rather than hidden
Several datasets now sit outside their own pack's declared range and are warned
about: bouvet2002 (pH 3), us8142675b2 (1.75), ep3161098b1 (4), us9499721b2 (4.7),
carbide2023 (8–11), mo2026 (4–11), yang2023 (to 10.5, half a unit above
dandu2009's span). Those warnings are correct — their rates are predicted with a
pH term fitted only in the alkaline decade. This is information the engine was
previously withholding, not a new defect, and no rate changed: the corpus median
is unmoved at 19.5%.

`netzband2020` deliberately does **not** widen `sti_ceria`'s range even though it
sweeps pH 4–10, because it is one of the three residuals shown earlier not to
share a common second pH channel. An unexplained dataset is not evidence of
validity.

### What the new test caught
Requiring a range from *every* pH-active pack immediately found one I had missed:
`oxide_silica_calibrated_pad`, a pad variant that changes contact parameters only
and inherits li2021's pH constants and range unchanged. Registered as such — the
audit works because it enumerates rather than trusting a hand-written list.

## Out-of-range pH is a warning, not a gate — because the corpus says so

Declaring `ph_valid_range` everywhere switched on out-of-range warnings for
fifteen datasets, and the obvious next step looked like gating them: the
declined machinery already exists for `oxidizer_ph_window`, so refusing to score
an unsupported extrapolation would have been a three-line change.

It would also have been wrong, and the corpus says so before any code is
written. Splitting the scored datasets by whether **every** row sits inside its
pack's declared range:

| group | n | median | mean |
|---|---:|---:|---:|
| fully in-range | 19 | 18.9% | 19.8% |
| fully out-of-range | 11 | 19.4% | 20.8% |

Mann-Whitney U = 101.0 against an expected 104.5 under the null, **z = −0.15**.
No detectable difference. Out-of-range prediction here is not degraded
prediction — it is prediction whose pH term is evaluated on its floor or flank
rather than near its optimum, which is an ordinary thing for a bounded function
to do.

The out-of-range group also contains some of the best results in the whole
corpus: bouvet2002_w **2.3%**, ep3161098b1 7.1%, lai2001 8.7%, bouvet2002_oxide
11.2%, us8142675b2 12.3%. A gate would discard those and return silence.

### Why this differs from the oxidiser gate, which *was* justified
There, Miranda's 2×2 showed the oxidiser term's **sign** reversing across the pH
branch: the model was confidently wrong in a direction no refit could fix, and
declining was the only honest answer. Here the model is not wrong, merely less
constrained. A gate is for *"this prediction would be wrong"*, not for *"this
prediction rests on fewer measurements"* — the latter is what warnings and
confidence fields are for.

The one genuinely pathological case is handled separately and does not need a
corpus-wide gate to express it: an acid-side floor of zero, where the rate
decays to 0.00 Å/min, already carries its own warning naming it a refusal.

So the range is declared, the warning fires, and the score stands. The decision
is fixed in a test that requires anyone reaching for the gate to first explain
away z = −0.15.

An aside on the test itself: the first version asserted `not score.gated` and
failed, because `gated` counts gates of any kind and lai2001 carries an
unrelated oxidiser-data-gap gate. The assertion had to be narrowed to gates
whose *reason* is the pH range — the distinction between "declined for this
reason" and "declined at all" matters here for exactly the same reason it
mattered when the oxidiser gate was first scoped.

## Some datasets cannot be predicted better than they were measured

STATUS listed `hong2007_cu_ads_bta_polish_rate` as a failure: 14.8% shape error
against a flat baseline of 12.6%, the model apparently losing to predicting the
dataset's own mean. Since hong2007 is a BTA adsorption series, the inhibitor term
was the obvious suspect.

Two things are wrong with that reading.

**The flat baseline is not 12.6%.** It is 14.8% — identical to the model's, to
four decimal places. The model does not lose to the mean, it *is* the mean here:
the inhibitor term is flat across these points, so the two predictions coincide.
The recorded 12.6% was stale.

**And the tie is correct, because of what the dataset's own replicates show.**
Three rows are identical in every override — pH, oxidiser, abrasive, chelator,
promoter, flow, and `inhibitor_mM = 0` — and report:

    2650, 2400, 1850 Å/min

Mean 2300, mean absolute deviation **13.0%**. No model can score better than 13.0%
here, because the measurement does not resolve rates more finely than that. Both
14.8% figures sit at the noise floor.

The inhibitor levels barely escape that scatter either: the zero-inhibitor
replicates span 1850–2650, the 10 mM point (2200) falls **inside** that span, and
the 0.5 mM point (1700) sits only 8% below its floor. One of the two levels is
indistinguishable from no inhibitor at all and the other is marginal — no Langmuir
coverage curve can be established from this, and a term that declines to fit one
is behaving correctly.

### The same test, corpus-wide
| dataset | replicate scatter | shape | flat |
|---|---:|---:|---:|
| `sic2026_ceria_h2o2_ph_DOE50` | 38.5% | **34.0%** | 62.5% |
| `us9200180b2_cu_benzenesulfonic_series` | 24.6% | 26.8% | 29.6% |
| `hong2007_cu_ads_bta_polish_rate` | 13.0% | 14.8% | 14.8% |

The SiC entry is the instructive one. Its 34.0% has been treated throughout this
session as the SiC model's weak point, and it is in fact **better than the set's
own reproducibility**. The pH refit earlier in this session moved it 39.3 → 34.0,
crossing from above the noise floor to below it: that refit was worth doing, and
further fitting on this set would be fitting its noise.

⚠ Only datasets with genuine replicates can be checked this way. Most of the
corpus reports one rate per condition, so its noise floor is simply unknown —
a limit of the evidence, not a licence to assume the floor is zero.
