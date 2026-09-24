"""One-off: declare `reference_abrasive` in every own-dir parameter pack.

Run once from ~/CMP-Sim. Inserts the key immediately after the `params:` line so
it sits at the top of the pack, where "which abrasive is this pack about" belongs.
"""
import re
from pathlib import Path

PACKS = Path("cmp_sim/data/params")

BLOCKS = {
    "oxide_silica": ("colloidal_silica", "literature", """
      Which abrasive this pack's kp_m_per_pa was calibrated with. NOT a
      formulation input - it is the declaration that makes an abrasive SWAP
      detectable. Kp was fitted to US9499721B2, whose example tables polish TEOS
      with a COLLOIDAL SILICA slurry, and the pack's size exponent (-0.05) is
      the silica-group value fitted across five silica sweeps. Running ceria or
      alumina through this pack therefore replaces those exponents with the ones
      scoped to that abrasive, and warns that the absolute rate is still
      anchored to silica - see cmp_sim/slurry/abrasive_effects.py.
""", "US9499721B2 TEOS/colloidal-silica example tables (this pack's Kp fit)"),

    "sti_ceria": ("ceria", "literature", """
      This pack is the CERIA pack: its Kp anchor, its +0.87 size exponent (3
      ceria sweeps, 3-211 nm) and its Dandu 2009 loading terms are all ceria
      measurements. Declared so that running a silica or alumina slurry through
      it is detected as an abrasive swap rather than silently predicted with
      ceria's exponents - ceria and silica size exponents differ in SIGN
      (+0.87 vs -0.05), so the swap changes the direction of the prediction.
""", "this pack's own Kp anchor and abrasive_size_exponent notes (ceria sweeps)"),

    "cu_h2o2_bta": ("alumina", "literature", """
      The Cu/H2O2/BTA chemistry this pack models was measured with EKC
      Technology ALUMINA, nominal 100 nm (Gopal & Talbot 2007, JES 154(6) H507,
      doi:10.1149/1.2718474; nominal size confirmed in Ihnfeldt & Talbot 2006,
      JES 153(11) G948, doi:10.1149/1.2335982), which is also the source of this
      pack's abrasive_size_nm. Declared so that a silica-abrasive Cu recipe is
      flagged as a swap: the alumina size exponent (+0.29) and the silica one
      (-0.05) do not share a sign.
""", "doi:10.1149/1.2718474 + doi:10.1149/1.2335982 (this pack's abrasive_size_nm source)"),

    "cu_alkaline_benzenesulfonic": ("colloidal_silica", "literature", """
      This pack's abrasive_size_exponent note already scopes its 0.0 to COLLOIDAL
      SILICA on copper (TW202115224A spherical subset, 15-160 nm). Declaring the
      reference abrasive as a key makes that scope machine-readable, so the
      engine can detect a swap instead of relying on a human reading the note.
""", "this pack's own abrasive_size_exponent note (TW202115224A silica subset)"),

    "w_fe_oxidizer": ("alumina", "med", """
      Alumina, but with a HONEST CAVEAT that lowers the confidence to med.
      The pack's material constants are alumina: abrasive_density_kg_m3 = 3950
      (alpha-Al2O3, CRC corundum) and abrasive_size_nm = 50 nm from Bielmann
      1999's gamma-alumina W-CMP slurry (doi:10.1149/1.1390765). But the Kp
      value 7.0e-14 is the mean of fits to TWO patents, and one of them
      (US2011/0186542A1) uses a DIAMOND abrasive at 0.01-0.04 wt% - which is
      also why abrasive_conc_half_wt_pct is pinned at 0.01 wt% and flagged as
      not a general tungsten value. So this pack's scale is a W-chemistry
      average across two abrasives rather than a single-abrasive calibration.
      'alumina' is declared because the material constants and the mainstream
      W slurry chemistry are alumina; treat a swap warning from this pack as
      approximate in both directions.
      TODO(owner): re-fit Kp on alumina-only W data to make this exact.
""", "this pack's abrasive_density_kg_m3 (CRC alpha-Al2O3) and kp_m_per_pa notes; caveat from US2011/0186542A1 (diamond)"),

    "sic_ceria_h2o2": ("ceria", "literature", """
      Kp was back-calculated from Wang et al. ACS SI Table S3 point S3-27, a
      CeO2 4 wt% / H2O2 4 vol% / pH 10 SiC polish - a ceria measurement. The
      pack's own size-exponent note records that SiC's two sweeps are alumina
      (+0.24) and silica (+0.10) while ceria elsewhere gives +0.87, i.e. the
      abrasives disagree on this film too, so the swap must be detected.
""", "Wang et al. ACS SI Table S3 point S3-27 (this pack's Kp anchor)"),

    "poly_si_alkaline": ("colloidal_silica", "literature", """
      Alkaline COLLOIDAL SILICA (Fuso PL-3/PL-7 class) is the abrasive in every
      source behind this pack, including [PIR14] Table 3-1, from which
      kp_m_per_pa was unit-converted. Poly-Si is also polished with calcined
      ceria + amino acids at very different selectivity, which is precisely the
      swap this declaration makes visible.
""", "doi:10.7939/r3zp3w76c ([PIR14]) Table 3-1 - this pack's Kp source, colloidal silica"),

    "si_substrate_alkaline": ("colloidal_silica", "literature", """
      Bare-Si substrate polish with alkaline COLLOIDAL SILICA: kp_m_per_pa was
      back-calculated from [ZHU25] (doi:10.3390/mi16040450), whose slurry is
      colloidal silica + KOH. Declared so a ceria or alumina Si recipe is
      flagged rather than predicted on silica's numbers.
""", "doi:10.3390/mi16040450 ([ZHU25]) - this pack's Kp derivation, colloidal silica"),

    "snag_solder": (None, "unverified", """
      TODO(owner): NOT FILLED, and deliberately. No primary source publishes a
      SnAg or pure-Sn CMP removal rate with the pressure and velocity it was
      measured at, so this pack has kp_m_per_pa: null and there is no
      calibration whose abrasive could be named. Declaring one would imply a
      calibration that does not exist. The engine reports "this pack does not
      declare reference_abrasive" for SnAg runs, which is the correct state:
      the abrasive cannot be checked because nothing here was calibrated.
""", None),
}


def block(kind, confidence, note, source):
    lines = ["  reference_abrasive:"]
    lines.append(f"    value: {kind if kind else 'null'}")
    lines.append("    unit: abrasive database key")
    lines.append("    note: >")
    for ln in note.strip("\n").split("\n"):
        lines.append(ln if ln.strip() else "")
    lines.append(f"    source: {'null' if source is None else repr(source)}")
    lines.append(f"    confidence: {confidence}")
    lines.append("")
    return "\n".join(lines) + "\n"


for name, (kind, conf, note, source) in BLOCKS.items():
    p = PACKS / f"{name}.yaml"
    text = p.read_text(encoding="utf-8")
    if "reference_abrasive:" in text:
        print(f"skip {name}: already declared")
        continue
    m = re.search(r"^params:[ \t]*$", text, flags=re.M)
    if not m:
        print(f"FAIL {name}: no 'params:' line")
        continue
    at = m.end() + 1
    new = text[:at] + block(kind, conf, note, source) + text[at:]
    p.write_text(new, encoding="utf-8")
    print(f"ok {name}: reference_abrasive = {kind}")
