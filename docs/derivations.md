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
