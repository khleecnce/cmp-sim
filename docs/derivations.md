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
*J. Soc. Glass Technol.* **11**, 214 (1927). Preston polished glass, not
wafers: the law is empirical and `Kp` lumps together everything chemical and
material-specific.

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
*Proc. R. Soc. Lond. A* **295**, 300 (1966). doi:10.1098/rspa.1966.0242.
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

MIT framework (Boning MRS 1999; Stine IEEE TSM 1998; Ouma thesis 1999).

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
