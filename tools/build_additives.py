"""Generate cmp_sim/data/params/additives.yaml.

Discipline (inherited from the FabSim EVIDENCE-RULES convention used in this repo):
  - Every numeric value is a mapping {value, unit, source, confidence}.
  - No number is written unless it can be traced to a named DOI / patent / dataset.
  - Where no source exists the value is null + confidence: unverified + note TODO(owner).
  - "no data" is recorded explicitly (direction: unknown) rather than silently omitted.
"""
import yaml, collections

FILMS = ["cu", "w", "oxide", "poly_si", "si", "sin", "snag", "co", "ru"]

def num(value, unit, source, confidence, note=None):
    d = {"value": value, "unit": unit, "source": source, "confidence": confidence}
    if note:
        d["note"] = note
    return d

def nonum(reason="no primary source located in this pass"):
    return {"value": None, "unit": None, "source": None,
            "confidence": "unverified", "note": "TODO(owner): " + reason}

def unknown(note):
    """A film for which we found no usable primary data."""
    return {"mechanism": "no primary quantitative source located for this additive on this film",
            "direction": "unknown", "model": "none",
            "magnitude_note": "TODO(owner): " + note,
            "source": None, "confidence": "unverified"}

SNAG_NOTE = ("SnAg solder / tin-silver bump CMP: an explicit corpus + web search in this pass "
             "returned zero primary additive-vs-removal-rate studies. Every SnAg entry in this "
             "file is a declared gap, not an estimate.")

A = collections.OrderedDict()

# ---------------------------------------------------------------- OXIDIZERS
A["hydrogen_peroxide"] = {
    "aliases": ["h2o2", "peroxide", "hydrogen peroxide"],
    "role": "oxidizer",
    "cas": "7722-84-1",
    "chemistry": {
        "formula": "H2O2",
        "mw_g_mol": num(34.0147, "g/mol", "PubChem CID 784", "literature"),
        "pka": num(11.65, "-", "PubChem CID 784 / standard aqueous pKa of H2O2", "literature"),
        "standard_potential_V": num(1.776, "V vs SHE",
                                    "H2O2 + 2H+ + 2e- -> 2H2O, acid; CRC electrochemical series "
                                    "(papers/crc-vanysek-electrochemical-series.pdf)", "literature"),
    },
    "film_effects": {
        "cu": {
            "mechanism": ("Oxidises Cu to Cu2O/CuO. The NET effect on removal rate is "
                          "REGIME-DEPENDENT and the sign flips: without a chelator in alkaline "
                          "slurry the oxide passivates and MRR falls with H2O2; with an acidic "
                          "chelator (oxalate) the oxide is dissolved as fast as it forms and MRR "
                          "rises. Do not model this as a single monotonic term."),
            "direction": "nonmonotonic",
            "model": "langmuir",
            "langmuir_K_per_wt_pct": num(0.8232, "1/wt%",
                "US20110165777A1 TABLE 2 (4 points, KOH 0.41 wt% / FSN 500 ppm fixed, H2O2 "
                "0/0.25/0.5/1.0 wt% -> 18.7/14.0/12.9/12.1 nm/min), least-squares fit with "
                "phi=0.15 fixed; max residual 11.9%", "literature",
                "Valid ONLY in the alkaline x chelator-free regime it was fitted in."),
            "saturation_conc_wt_pct": num(None, "wt%", None, "unverified",
                "TODO(owner): no clean saturation point; the two regimes saturate differently."),
            "regime_reversal": {
                "alkaline_no_chelator": num(-35.0, "% MRR change over 0 -> 1 wt% H2O2",
                    "US20110165777A1 TABLE 2 (18.7 -> 12.1 nm/min)", "literature"),
                "acidic_with_oxalate": num(13.0, "% MRR change over 3 -> 6 wt% H2O2",
                    "doi:10.1149/2162-8777/adc59e (Jani 2025, ECS JSST 14 044003, Expt 30/32: "
                    "2282 -> 2578 nm/min, pH 3, oxalic acid 0.08 M, no BTA)", "literature"),
            },
            "magnitude_note": ("Aksu & Doyle 2003 (Electrochim. Acta) report a dissolution-rate "
                               "peak in the 1-3 wt% band with passivation above 3 wt% in acidic "
                               "Na2SO4; that is a dissolution rate, not a CMP MRR."),
            "source": "US20110165777A1; doi:10.1149/2162-8777/adc59e; doi:10.1016/j.electacta.2003.11.010",
            "confidence": "literature",
        },
        "w": {
            "mechanism": ("Oxidises W to WO3; the WO3 layer is softer than W and is abraded. "
                          "With an Fe(III) accelerator the Fenton-type cycle regenerates the "
                          "oxidant, so the rate keeps climbing over the whole practical range."),
            "direction": "enhance",
            "model": "langmuir",
            "langmuir_K_per_wt_pct": num(0.549550, "1/wt%",
                "Back-fitted from US20110186542A1 Example 3 TABLE 3.1/3.2 (nanodiamond x H2O2 x pH, "
                "15 conditions)", "literature"),
            "measured_series_nm_per_min": num([9.6, 150.8, 239.6, 241.0, 296.5], "nm/min",
                "US8070843B2 TABLE 1 (3M Mirra 3400, 4.0 psi, 79/101 rpm) at H2O2 "
                "0 / 2.03 / 4.06 / 4.07 / 6.10 wt%, Fe(III) 5-1180 ppm", "verified",
                "Monotonic increase over 0-6.1 wt%: no Kaufman peak is observed in this window."),
            "saturation_conc_wt_pct": num(None, "wt%", None, "unverified",
                "TODO(owner): peak/saturation lies above 6.1 wt%; never measured. Do not extrapolate."),
            "magnitude_note": "0 -> 6.1 wt% gives ~31x MRR (9.6 -> 296.5 nm/min) with Fe(III) present.",
            "source": "US8070843B2 TABLE 1; US20110186542A1 TABLE 3.1/3.2",
            "confidence": "verified",
        },
        "oxide": {
            "mechanism": ("On SiO2 with a CERIA abrasive H2O2 does not oxidise the film; it "
                          "shifts the Ce3+/Ce4+ balance of the abrasive. Ce3+ sites are the "
                          "'chemical tooth' that forms the Si-O-Ce bond, so the abrasive - not "
                          "the wafer - is what the oxidiser acts on. With a SILICA abrasive the "
                          "effect is essentially absent."),
            "direction": "enhance",
            "model": "threshold",
            "effect_at_0p5_wt_pct": num(5.5, "x MRR ratio vs no H2O2",
                "doi:10.1149/2162-8777/ab8393 (Netzband & Dunn 2020, ECS JSST 9 044001, Fig. 1a; "
                "68 nm ceria 1.0 wt%, 20 kPa, thermal oxide)", "literature"),
            "selectivity_oxide_over_sin": num([1.0, 3.0], "oxide:SiN, before -> after 0.5 wt% H2O2",
                "doi:10.1149/2162-8777/ab8393", "literature"),
            "saturation_conc_wt_pct": num(0.5, "wt%", "doi:10.1149/2162-8777/ab8393",
                "literature", "Single tested level; the shape of the curve below 0.5 wt% is unknown."),
            "magnitude_note": "Abrasive-mediated, not film-mediated. Ceria only.",
            "source": "doi:10.1149/2162-8777/ab8393",
            "confidence": "literature",
        },
        "co": {
            "mechanism": ("Forms a Co oxide/hydroxide that citrate then dissolves. Excess H2O2 "
                          "makes oxidation outrun complexation and both removal rate and static "
                          "dissolution rate fall - a genuine optimum, not a plateau."),
            "direction": "nonmonotonic",
            "model": "threshold",
            "excess_threshold_wt_pct": num(5.0, "wt%",
                "doi:10.1149/2.0111709jss (Popuri 2017, ECS JSST 6 P594, sec. 4.2 - at 5 wt% "
                "H2O2 'oxidation rate outruns complexation' and RR/DR both drop)", "literature"),
            "mechanical_floor_no_oxidizer_nm_per_min": num(140.0, "nm/min",
                "doi:10.1149/2.0111709jss (pH 4, water + 3 wt% silica, H2O2 = 0, citric acid = 0)",
                "literature"),
            "magnitude_note": "An oxidiser-free mechanical floor of ~140 nm/min exists on Co.",
            "source": "doi:10.1149/2.0111709jss",
            "confidence": "literature",
        },
        "ru": {
            "mechanism": ("Oxidises Ru to RuO2/RuO3. Ru is near-noble (Ru2+/Ru approx +0.45 V vs "
                          "SHE) so H2O2 alone gives a low, sharply peaked rate; the oxide must be "
                          "removed by a complexant (see ethylenediamine) for high rate."),
            "direction": "nonmonotonic",
            "model": "threshold",
            "peak_conc_wt_pct": num(0.15, "wt%",
                "doi:10.1039/d1ra08243d (Xu 2022, RSC Adv. 12 228, Fig. 1; 5 wt% SiO2, pH 9 - "
                "RR rises to 0.15 wt% then falls)", "literature"),
            "rate_at_peak_no_complexant": num(116.0, "Angstrom/min",
                "doi:10.1039/d1ra08243d Fig. 2 (0.15 wt% H2O2, EDA = 0)", "literature"),
            "magnitude_note": "Peak at 0.15 wt% - two orders of magnitude lower than the Cu/W optimum.",
            "source": "doi:10.1039/d1ra08243d",
            "confidence": "literature",
        },
        "sin": {
            "mechanism": ("Indirect only: via the ceria Ce3+ fraction it changes the oxide:SiN "
                          "selectivity (1 -> 3). No direct oxidation of Si3N4 is reported."),
            "direction": "negligible",
            "model": "none",
            "source": "doi:10.1149/2162-8777/ab8393",
            "confidence": "literature",
        },
        "poly_si": unknown("no H2O2 concentration sweep on poly-Si MRR found. Note that Si CMP "
                           "chemistry is OH- hydrolysis driven, not oxidiser driven."),
        "si": unknown("same as poly_si: alkaline hydrolysis dominates; no H2O2 sweep located."),
        "snag": unknown(SNAG_NOTE),
    },
}

A["potassium_iodate"] = {
    "aliases": ["kio3", "potassium iodate", "iodate"],
    "role": "oxidizer",
    "cas": "7758-05-6",
    "chemistry": {"formula": "KIO3",
                  "mw_g_mol": num(214.00, "g/mol", "PubChem CID 23665710", "literature"),
                  "pka": nonum("salt of a strong base; no relevant pKa")},
    "film_effects": {
        "w": {
            "mechanism": ("IO3- oxidises W to WO3. The concentration response SATURATES: nearly "
                          "all of the gain is obtained by 2 wt%, and 2 -> 4 wt% adds only ~7%."),
            "direction": "enhance",
            "model": "langmuir",
            "measured_series_angstrom_per_min": num([40, 140, 750, 1500, 1600], "Angstrom/min",
                "doi:10.1007/s40735-016-0041-4 (Stojadinovic 2016, J. Bio-Tribo-Corros. 2 20, "
                "Table 1) at KIO3 0 / 0.1 / 0.5 / 2 / 4 wt%, pH 5, Mecapol E460, 5 psi",
                "verified"),
            "saturation_conc_wt_pct": num(2.0, "wt%", "doi:10.1007/s40735-016-0041-4 Table 1",
                                          "literature"),
            "ph_coupling_k_per_ph": num(0.1163, "1/pH",
                "f(pH)=exp(-k*(pH-pH_ref)); log-mean of the three oxidant-bearing MRR ratios "
                "1.429/1.533/1.300 in doi:10.1007/s40735-016-0041-4 Table 1 over pH 5 -> 2, "
                "divided by dpH=3. Spread of the individual k values is +/-22%.", "literature",
                "Secant over pH 2-5 only; the alkaline branch has the opposite sign."),
            "magnitude_note": "0 -> 2 wt% gives ~37x; 2 -> 4 wt% only +7%.",
            "source": "doi:10.1007/s40735-016-0041-4; WO1995024054A1 Example 2 (alumina 7% + "
                      "KIO3 3.2% + KHP 4.4%, pH 4.1)",
            "confidence": "verified",
        },
        "cu": {
            "mechanism": "Listed as an alternative Cu oxidiser; no concentration-rate table found.",
            "direction": "enhance", "model": "none",
            "magnitude_note": "TODO(owner): direction from patent claim language only, no data.",
            "source": "US20050090104A1", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["ferric_nitrate"] = {
    "aliases": ["fe(no3)3", "ferric nitrate", "iron(iii) nitrate"],
    "role": "oxidizer",
    "cas": "7782-61-8",
    "chemistry": {"formula": "Fe(NO3)3.9H2O",
                  "mw_g_mol": num(403.999, "g/mol", "PubChem CID 24932 (nonahydrate)", "literature"),
                  "standard_potential_V": num(0.771, "V vs SHE",
                      "Fe3+ + e- -> Fe2+; CRC electrochemical series", "literature")},
    "film_effects": {
        "w": {
            "mechanism": ("Fe(III) is not mainly a stoichiometric oxidiser here - it is a "
                          "CATALYST. Fe3+/Fe2+ cycling with H2O2 (Fenton) generates OH radicals "
                          "that drive W -> WO3 far faster than H2O2 alone. This is why ppm-level "
                          "Fe changes the rate by an order of magnitude."),
            "direction": "enhance",
            "model": "threshold",
            "effective_range_wt_pct": num([0.005, 0.20], "wt%",
                "US5958288A (Cabot; catalyst 0.005-0.20 wt% used with H2O2)", "verified"),
            "saturation_conc_wt_pct": num(0.05, "wt%",
                "US5958288A TABLE 3 - below 0.05 wt% is already sufficient", "literature"),
            "evidence_of_catalysis": num([150.8, 239.6], "nm/min at Fe 60 ppm vs 5 ppm",
                "US8070843B2 TABLE 1 Examples 3 and 2 - note H2O2 also differs (2.03 vs 4.06 wt%), "
                "so this pair is NOT a clean Fe sweep", "literature",
                "Confounded pair; kept only to show Fe works at single-digit ppm."),
            "magnitude_note": "Active at 5-1180 ppm Fe; the useful design axis is ppm, not wt%.",
            "source": "US5958288A; US8070843B2; US10676647B1 (0.5-3000 ppm Fe)",
            "confidence": "verified",
        },
        "cu": {"mechanism": "Used as a standalone Cu oxidiser in tribological studies.",
               "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): no concentration-MRR table extracted.",
               "source": "doi:10.1016/j.triboint.2007.09.009", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["ammonium_persulfate"] = {
    "aliases": ["aps", "(nh4)2s2o8", "ammonium peroxydisulfate", "persulfate"],
    "role": "oxidizer",
    "cas": "7727-54-0",
    "chemistry": {"formula": "(NH4)2S2O8",
                  "mw_g_mol": num(228.18, "g/mol", "PubChem CID 62648", "literature"),
                  "standard_potential_V": num(2.010, "V vs SHE",
                      "S2O8^2- + 2e- -> 2SO4^2-; CRC electrochemical series", "literature",
                      "Stronger than H2O2 thermodynamically; kinetically slow without activation.")},
    "film_effects": {
        "w": {"mechanism": "S2O8^2- oxidises W to WO3 in acidic buffered slurry.",
              "direction": "enhance", "model": "none",
              "rate_at_1_wt_pct_angstrom_per_min": num(218.0, "Angstrom/min",
                  "WO1995024054A1 TABLE 2 (K2S2O8 1 wt%, pH 4.1)", "literature",
                  "Potassium salt, not ammonium; same anion chemistry."),
              "magnitude_note": "Single point - no concentration curve.",
              "source": "WO1995024054A1 TABLE 2", "confidence": "literature"},
        "cu": {"mechanism": "Listed Cu / barrier slurry oxidiser, 0.01-10 wt% (preferred 0.1-1).",
               "direction": "enhance", "model": "none",
               "claimed_range_wt_pct": num([0.01, 10.0], "wt%", "US20050090104A1", "verified"),
               "magnitude_note": "Patent claim range only, no MRR table.",
               "source": "US20050090104A1", "confidence": "literature"},
        "co": {"mechanism": "Persulfate-based Co CMP is an active research line.",
               "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): cited second-hand via catalog; primary not read.",
               "source": "doi:10.1016/j.apsusc.2024.162287", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["periodic_acid"] = {
    "aliases": ["hio4", "periodate", "kio4", "potassium periodate", "periodic acid"],
    "role": "oxidizer",
    "cas": "7790-21-8",
    "chemistry": {"formula": "KIO4",
                  "mw_g_mol": num(230.00, "g/mol", "PubChem CID 23675763 (KIO4)", "literature"),
                  "pka": num(1.64, "-", "PubChem - periodic acid HIO4 first dissociation",
                             "literature")},
    "film_effects": {
        "ru": {
            "mechanism": ("Periodate is one of the few oxidants strong enough to take Ru past "
                          "RuO2 towards volatile/soluble RuO4, which is why it is the classical "
                          "Ru CMP oxidiser. Note the RuO4 toxicity constraint on real slurries."),
            "direction": "enhance", "model": "none",
            "saturation_conc_mM": nonum("primary concentration sweep not retrieved in this pass"),
            "magnitude_note": "Qualitative only; combined with silica abrasive; reported synergy "
                              "with persulfate.",
            "source": "doi:10.1149/1.3528942; doi:10.1016/j.mseb.2020.114764",
            "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "oxide": unknown("no data"),
        "poly_si": unknown("no data"), "si": unknown("no data"), "sin": unknown("no data"),
        "co": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["potassium_permanganate"] = {
    "aliases": ["kmno4", "permanganate"],
    "role": "oxidizer", "cas": "7722-64-7",
    "chemistry": {"formula": "KMnO4",
                  "mw_g_mol": num(158.034, "g/mol", "PubChem CID 516875", "literature"),
                  "standard_potential_V": num(1.507, "V vs SHE",
                      "MnO4- + 8H+ + 5e- -> Mn2+ + 4H2O; CRC electrochemical series", "literature")},
    "film_effects": {
        "w": {"mechanism": "Listed W/Cu slurry oxidiser. Consumes H+ during reduction, so pH "
                           "drifts upward and the slurry needs buffering.",
              "direction": "enhance", "model": "none",
              "magnitude_note": "TODO(owner): no MRR table for W/Cu extracted.",
              "source": "US20050090104A1", "confidence": "unverified"},
        "cu": {"mechanism": "Same list as above.", "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): no data.",
               "source": "US20050090104A1", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
    "notes": "Primary industrial use is SiC CMP (outside the film list here): US9368367B2, "
             "WO2020087721A1.",
}

A["potassium_ferricyanide"] = {
    "aliases": ["k3fe(cn)6", "ferricyanide"],
    "role": "oxidizer", "cas": "13746-66-2",
    "chemistry": {"formula": "K3Fe(CN)6",
                  "mw_g_mol": num(329.24, "g/mol", "PubChem CID 26250", "literature"),
                  "standard_potential_V": num(0.358, "V vs SHE",
                      "Fe(CN)6^3- + e- -> Fe(CN)6^4-; CRC electrochemical series", "literature")},
    "film_effects": {
        "w": {"mechanism": ("The original W CMP oxidiser (IBM). Historically important because "
                            "Kaufman's competing-process model - passivating film formation "
                            "versus mechanical abrasion of that film - was derived on this system "
                            "and still underlies every oxidiser term in this file."),
              "direction": "enhance", "model": "none",
              "magnitude_note": "TODO(owner): original rate table not re-extracted.",
              "source": "doi:10.1149/1.2085434 (Kaufman 1991, JES 138 3460)",
              "confidence": "literature"},
        "cu": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

# ------------------------------------------------ INHIBITORS / PASSIVATORS
A["benzotriazole"] = {
    "aliases": ["bta", "1,2,3-benzotriazole", "benzotriazole"],
    "role": "inhibitor", "cas": "95-14-7",
    "chemistry": {"formula": "C6H5N3",
                  "mw_g_mol": num(119.12, "g/mol", "PubChem CID 7220", "verified"),
                  "pka": num(8.2, "-", "PubChem CID 7220 (N-H dissociation)", "literature")},
    "film_effects": {
        "cu": {
            "mechanism": ("Cu(I)-BTA polymeric film. BTA deprotonates and bridges Cu(I) centres "
                          "into an insoluble [Cu(I)BTA]n chain that blocks both static etch and "
                          "mechanically-assisted dissolution - this is what controls dishing."),
            "direction": "suppress",
            "model": "langmuir",
            "dG_ads_kJ_per_mol": num(-35.4, "kJ/mol",
                "Equilibrium adsorption free energy widely quoted for BTA on Cu (second-hand via "
                "knowledge/cmp/slurry-components-overview.md; primary not verified)",
                "unverified",
                "WARNING: using this EQUILIBRIUM dG to compute the CMP steady-state coverage is "
                "quantitatively FALSIFIED - see langmuir_K_effective below."),
            "langmuir_K_equilibrium_L_per_mol": num(28676.0, "L/mol",
                "Derived from dG_ads = -35.4 kJ/mol via K = exp(-dG/RT)/55.5 at 298.15 K",
                "unverified"),
            "langmuir_K_effective_L_per_mol": num(249.73, "L/mol",
                "Two-point exact fit (with k=3.0-family strength) to doi:10.1557/proc-613-e7.4.1 "
                "(Len, McNeill, Gamble 2000, MRS Proc. 613 E7.4.1): 5 vol% NH4OH + 2 wt% alumina, "
                "BTA 0 / 0.1 / 0.25 wt% -> Cu 400 / 65 / 42 nm/min", "literature",
                "K_eff is ~115x SMALLER than K_eq. Physical reading: the pad continuously abrades "
                "the film, so steady-state coverage obeys K_eff ~ K_eq/(1 + k_abrade/k_desorb)."),
            "measured_series_nm_per_min": num([400.0, 65.0, 42.0, 42.0, 42.0], "nm/min",
                "doi:10.1557/proc-613-e7.4.1 at BTA 0 / 0.1 / 0.25 / 0.5 / 0.75 wt% "
                "(= 0 / 8.395 / 20.987 / 41.974 / 62.962 mM)", "verified",
                "Note the PLATEAU above 0.25 wt%: Langmuir theta combined with exp(-k*theta) has "
                "no floor and structurally cannot reproduce it."),
            "isotherm_note": ("Frumkin fits BTA-Cu better than Langmuir in the corrosion "
                              "literature (lateral interaction term); for f > 2 Frumkin is "
                              "mathematically a smooth threshold."),
            "magnitude_note": "0.1 wt% BTA cuts Cu MRR by 84% (400 -> 65 nm/min); beyond 0.25 wt% "
                              "nothing more happens.",
            "source": "doi:10.1557/proc-613-e7.4.1; doi:10.1016/j.corsci.2010.05.002 "
                      "(Finsgar & Milosev 2010 BTA-on-Cu review); US20050090104A1 (0.005-1 wt%)",
            "confidence": "literature",
        },
        "co": {"mechanism": "Azole N coordinates Co as well as Cu; used to suppress Cu/Co "
                            "galvanic corrosion at the interconnect interface.",
               "direction": "suppress", "model": "none",
               "magnitude_note": "TODO(owner): no Co concentration-MRR curve extracted.",
               "source": "doi:10.1149/2.0201909jss", "confidence": "unverified"},
        "ru": unknown("BTA on Ru not characterised in the sources read"),
        "w": {"mechanism": "Not the standard W inhibitor (picolinic acid is). No W data.",
              "direction": "unknown", "model": "none",
              "magnitude_note": "TODO(owner): no data.", "source": None, "confidence": "unverified"},
        "oxide": {"mechanism": "No adsorption on silanol-terminated SiO2 is reported; BTA is a "
                               "metal-selective inhibitor.",
                  "direction": "negligible", "model": "none",
                  "magnitude_note": "Inferred from the metal-specific Cu(I)-BTA mechanism, not "
                                    "from a direct oxide measurement. TODO(owner): confirm.",
                  "source": None, "confidence": "estimated"},
        "poly_si": unknown("no data"), "si": unknown("no data"), "sin": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["tolyltriazole"] = {
    "aliases": ["tta", "tolyltriazole", "5-methyl-1h-benzotriazole", "methylbenzotriazole"],
    "role": "inhibitor", "cas": "29385-43-1",
    "chemistry": {"formula": "C7H7N3",
                  "mw_g_mol": num(133.15, "g/mol", "PubChem CID 15644", "literature"),
                  "pka": nonum("not retrieved; expected close to BTA (~8.5)")},
    "film_effects": {
        "cu": {"mechanism": ("BTA with a methyl group. The extra hydrophobicity makes a denser, "
                             "less water-permeable film, so per-mole it is generally the stronger "
                             "inhibitor - but it also desorbs less readily, which is why it is "
                             "harder to clean off post-CMP."),
               "direction": "suppress", "model": "langmuir",
               "claimed_range_mM": num([0.0001, 300.0], "mM",
                   "US6821309B2 (BTA or TTA, 0.0001-300 mM)", "verified"),
               "langmuir_K_L_per_mol": nonum("no TTA-specific isotherm constant located; do NOT "
                                             "reuse the BTA K_eff - substituent changes both "
                                             "hydrophobicity and sterics"),
               "magnitude_note": "Named alongside BTA as 'most preferred' inhibitor in Cu slurry "
                                 "patents; no public concentration-MRR sweep found.",
               "source": "US20050090104A1; US6821309B2; WO2020091242A1",
               "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["triazole_1_2_4"] = {
    "aliases": ["1,2,4-triazole", "taz", "triazole"],
    "role": "inhibitor", "cas": "288-88-0",
    "chemistry": {"formula": "C2H3N3",
                  "mw_g_mol": num(69.065, "g/mol", "PubChem CID 10442", "literature"),
                  "pka": num(10.26, "-", "PubChem CID 10442 (N-H)", "literature")},
    "film_effects": {
        "cu": {
            "mechanism": ("Five-membered azole without the fused benzene ring. Coordinates Cu "
                          "through ring N. Crucially the inhibition efficiency is NON-MONOTONIC: "
                          "past the optimum the Cu-TAZ complex aggregates and the protective film "
                          "loses integrity."),
            "direction": "nonmonotonic", "model": "threshold",
            "optimum_conc_mM": num(15.0, "mM",
                "doi:10.21203/rs.3.rs-5011272/v1 (Dai 2024, EIS on alkaline Cu slurry: 2 wt% "
                "glycine + 0.5 wt% H2O2, pH 9; TAZ 0/5/10/15/20 mM)", "literature"),
            "inhibition_efficiency_pct": num([85.34, 81.57], "% at 15 mM and 20 mM",
                "doi:10.21203/rs.3.rs-5011272/v1", "literature",
                "Efficiency DROPS above the optimum - a saturating Langmuir term cannot express this."),
            "claimed_range_wt_pct": num([0.001, 0.15], "wt%", "US8974692B2", "verified"),
            "magnitude_note": "Peak inhibition at 15 mM in alkaline glycine/H2O2 Cu slurry.",
            "source": "doi:10.21203/rs.3.rs-5011272/v1; US8506661B2; US8974692B2",
            "confidence": "literature",
        },
        "co": {"mechanism": "Used against Cu/Co galvanic corrosion.", "direction": "suppress",
               "model": "none", "magnitude_note": "TODO(owner): no Co-specific curve.",
               "source": "doi:10.1149/2.0201909jss", "confidence": "unverified"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["nicotinic_acid"] = {
    "aliases": ["niacin", "nicotinic acid", "pyridine-3-carboxylic acid", "vitamin b3"],
    "role": "inhibitor", "cas": "59-67-6",
    "chemistry": {"formula": "C6H5NO2",
                  "mw_g_mol": num(123.11, "g/mol", "PubChem CID 938", "literature"),
                  "pka": num(4.85, "-", "PubChem CID 938 (carboxyl)", "literature"),
                  "pka_ring_N": num(2.0, "-", "PubChem CID 938 (pyridinium)", "literature")},
    "film_effects": {
        "cu": {
            "mechanism": ("Adsorbs on Cu and, in the Cu/Ru pairing, raises the Cu potential "
                          "towards Ru so the galvanic couple is quenched. Removal rate falls "
                          "monotonically with concentration."),
            "direction": "suppress", "model": "langmuir",
            "measured_series_nm_per_min": num([19.196, 8.266, 5.246], "nm/min",
                "doi:10.1038/s41598-021-00689-6 (Lee 2021, Sci. Rep. 11 21214, Table 3) at "
                "0 / 30 / 50 mM; pH 10, colloidal SiO2 5 wt% (70 nm), H2O2 3 wt%, 1.5 psi",
                "verified",
                "Original units were Angstrom/30 s; converted x2 then /10."),
            "saturation_conc_mM": nonum("only three points, all on the descending branch"),
            "magnitude_note": "0 -> 50 mM cuts Cu MRR by 73%.",
            "source": "doi:10.1038/s41598-021-00689-6",
            "confidence": "verified",
        },
        "ru": {"mechanism": "The same molecule protects the Ru barrier in the Cu/Ru couple; the "
                            "published figure of merit is the Cu:Ru selectivity, not a Ru MRR.",
               "direction": "suppress", "model": "none",
               "magnitude_note": "TODO(owner): extract Ru MRR column from Table 3.",
               "source": "doi:10.1038/s41598-021-00689-6", "confidence": "literature"},
        "sin": {
            "mechanism": ("Completely different mechanism from the Cu case. On Si3N4 in a CERIA "
                          "dispersion the molecule must be PROTONATED at the ring N to adsorb; "
                          "the adsorbed layer then blocks the ceria chemical-tooth sites. This "
                          "is why it works at pH <= 5 and switches off above it."),
            "direction": "suppress", "model": "langmuir",
            "required_conc_wt_pct": num(0.1, "wt%",
                "doi:10.1016/j.colsurfa.2013.03.046 (Penta 2013, Colloids Surf. A 429 67, "
                "Table 1; 0.1 wt% ceria)", "literature"),
            "sin_rate_after_inhibition_nm_per_min": num(1.0, "nm/min",
                "doi:10.1016/j.colsurfa.2013.03.046 Table 1", "literature"),
            "ph_window_upper": num(5.0, "pH", "doi:10.1016/j.colsurfa.2013.03.046 Table 1",
                                   "literature", "Above this pH the ring N deprotonates and "
                                                 "inhibition switches off."),
            "magnitude_note": "0.1 wt% is enough - 20x less than proline needs.",
            "source": "doi:10.1016/j.colsurfa.2013.03.046; doi:10.1149/1.1817870",
            "confidence": "literature",
        },
        "oxide": {"mechanism": "Adsorbs on SiO2 too (~100 mg/g saturation) but does not suppress "
                               "the oxide rate appreciably - this asymmetry is what creates STI "
                               "selectivity.",
                  "direction": "negligible", "model": "langmuir",
                  "adsorption_saturation_mg_per_g": num(100.0, "mg/g",
                      "doi:10.1016/j.colsurfa.2013.03.046 Fig. 5 (both SiO2 and Si3N4 saturate "
                      "near 100 mg/g over 0-2 wt%; ceria surface takes <10 mg/g)", "literature"),
                  "magnitude_note": "Adsorbs but does not stop the oxide.",
                  "source": "doi:10.1016/j.colsurfa.2013.03.046", "confidence": "literature"},
        "w": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "co": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["picolinic_acid"] = {
    "aliases": ["picolinic acid", "pyridine-2-carboxylic acid", "2-picolinic acid"],
    "role": "inhibitor", "cas": "98-98-6",
    "chemistry": {"formula": "C6H5NO2",
                  "mw_g_mol": num(123.11, "g/mol", "PubChem CID 1018", "verified"),
                  "pka": num(5.3, "-",
                             "ring N pKa used in doi:10.1016/j.colsurfa.2013.03.046 analysis",
                             "literature")},
    "film_effects": {
        "w": {
            "mechanism": ("Adsorbs on the WO3/W surface and suppresses STATIC dissolution far "
                          "more than it suppresses polish rate. That asymmetry is the whole point: "
                          "it kills plug recess without killing throughput."),
            "direction": "suppress", "model": "langmuir",
            "langmuir_b_L_per_mg": num(0.009, "L/mg",
                "doi:10.3390/app12031227 (Lee & Seo 2022, Appl. Sci. 12 1227, Table 1)",
                "literature"),
            "langmuir_K_L_per_mol": num(1108.0, "L/mol",
                "Unit conversion of b = 0.009 L/mg with MW 123.11 g/mol", "literature"),
            "isotherm_fit_r2": num(0.994, "-",
                "doi:10.3390/app12031227 Table 1 (Langmuir R2 = 0.994 vs Freundlich 0.825 - "
                "Langmuir wins on this system)", "literature"),
            "saturation_conc_wt_pct": num(1.5, "wt%",
                "doi:10.3390/app12031227 sec. 3.3 - adsorption and inhibition both saturate at "
                "1.5 wt%; 5.0 wt% adds nothing", "literature"),
            "saturation_conc_mM": num(121.8, "mM",
                "1.5 wt% converted at rho = 1.000 g/mL, MW 123.11 (= 121.84 mM)", "literature"),
            "static_etch_angstrom_per_min": num([90.0, 11.0], "Angstrom/min, 0 -> 1.5 wt%",
                "doi:10.3390/app12031227", "literature"),
            "magnitude_note": "Static etch drops 8x at the saturation dose.",
            "known_model_failure": ("A Langmuir theta with this b already reaches theta = 0.978 at "
                                    "0.5 wt%, predicting strong inhibition, whereas the paper "
                                    "describes 0.5 wt% as inhibition FAILURE by AFM/SEM. The low- "
                                    "concentration threshold behaviour is not captured."),
            "source": "doi:10.3390/app12031227",
            "confidence": "literature",
        },
        "sin": {"mechanism": "Same protonation-gated adsorption as nicotinic acid, on ceria "
                             "dispersions.",
                "direction": "suppress", "model": "langmuir",
                "required_conc_wt_pct": num(0.1, "wt%",
                    "doi:10.1016/j.colsurfa.2013.03.046 Table 1", "literature"),
                "sin_rate_after_inhibition_nm_per_min": num(1.0, "nm/min",
                    "doi:10.1016/j.colsurfa.2013.03.046 Table 1", "literature"),
                "ph_window_upper": num(6.0, "pH", "doi:10.1016/j.colsurfa.2013.03.046 Table 1",
                                       "literature"),
                "magnitude_note": ("Apparent contradiction resolved by pH: at pH 9.6 picolinic "
                                   "acid does NOT stop SiN (65 nm/min, selectivity 6.5) because "
                                   "the ring N (pKa 5.3) is only ~5e-5 protonated."),
                "source": "doi:10.1016/j.colsurfa.2013.03.046; doi:10.1149/1.1817870",
                "confidence": "literature"},
        "oxide": {"mechanism": "Adsorbs without suppressing - basis of oxide:SiN selectivity.",
                  "direction": "negligible", "model": "langmuir",
                  "magnitude_note": "See nicotinic_acid.oxide.",
                  "source": "doi:10.1016/j.colsurfa.2013.03.046", "confidence": "literature"},
        "cu": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "co": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["imidazole"] = {
    "aliases": ["imidazole", "1h-imidazole"],
    "role": "inhibitor", "cas": "288-32-4",
    "chemistry": {"formula": "C3H4N2",
                  "mw_g_mol": num(68.077, "g/mol", "PubChem CID 795", "literature"),
                  "pka": num(6.95, "-", "PubChem CID 795 (imidazolium)", "literature"),
                  "pka_NH": num(14.4, "-", "PubChem CID 795 (N-H)", "literature")},
    "film_effects": {
        "cu": {"mechanism": "N-heterocyclic passivator; the pyridine-type N donates a lone pair "
                            "to surface Cu. Weaker than BTA because it cannot form the polymeric "
                            "bridged chain.",
               "direction": "suppress", "model": "none",
               "magnitude_note": "TODO(owner): patent listing only; no isotherm or MRR sweep.",
               "source": "US6821309B2; US8734665B2", "confidence": "literature"},
        "w": {"mechanism": "Listed as a basic pH adjuster in W slurries, not as an inhibitor.",
              "direction": "unknown", "model": "none",
              "magnitude_note": "TODO(owner): role differs by film - verify.",
              "source": "US9994735B2", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["mercaptobenzothiazole"] = {
    "aliases": ["mbt", "2-mercaptobenzothiazole"],
    "role": "inhibitor", "cas": "149-30-4",
    "chemistry": {"formula": "C7H5NS2",
                  "mw_g_mol": num(167.25, "g/mol", "PubChem CID 697989", "literature"),
                  "pka": num(6.93, "-", "PubChem CID 697989 (thiol/thione)", "literature")},
    "film_effects": {
        "cu": {"mechanism": "Thiol-azole. Sulfur is a much softer donor than N and binds Cu(I) "
                            "very strongly (HSAB), so MBT adsorbs more tenaciously than BTA - "
                            "which also makes it a post-CMP cleaning problem.",
               "direction": "suppress", "model": "none",
               "magnitude_note": "TODO(owner): no isotherm or MRR data extracted.",
               "source": "US20050090104A1; US6821309B2", "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["potassium_sorbate"] = {
    "aliases": ["potassium sorbate", "sorbate"],
    "role": "inhibitor", "cas": "24634-61-5",
    "chemistry": {"formula": "C6H7KO2",
                  "mw_g_mol": num(150.22, "g/mol", "PubChem CID 23676745", "literature"),
                  "pka": num(4.76, "-", "PubChem CID 643460 (sorbic acid)", "literature")},
    "film_effects": {
        "cu": {"mechanism": "Carboxylate adsorption on Cu; studied as a low-toxicity BTA "
                            "replacement.",
               "direction": "suppress", "model": "none",
               "magnitude_note": "TODO(owner): corrosion studies, not CMP MRR.",
               "source": "doi:10.1016/j.electacta.2007.02.010; doi:10.1016/j.electacta.2009.10.086",
               "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

# --------------------------------------------------- COMPLEXANTS / CHELATORS
A["glycine"] = {
    "aliases": ["glycine", "gly", "aminoacetic acid"],
    "role": "complexant", "cas": "56-40-6",
    "chemistry": {"formula": "C2H5NO2",
                  "mw_g_mol": num(75.067, "g/mol", "PubChem CID 750", "literature"),
                  "pka_cooh": num(2.35, "-",
                      "MINTEQ v4 database (papers/phreeqc-minteq.v4.dat, cumulative protonation "
                      "log beta 12.128 - 9.778)", "verified"),
                  "pka_nh3": num(9.78, "-",
                      "MINTEQ v4 database, H+ + Gly- = HGly, log beta 9.778", "verified")},
    "film_effects": {
        "cu": {
            "mechanism": ("Bidentate N,O chelator. Cu2+ + 2 Gly- -> Cu(Gly)2 is so stable that "
                          "the Pourbaix soluble-Cu region is pushed far into what would otherwise "
                          "be the CuO passive domain. Practically: glycine is what keeps the "
                          "H2O2-grown oxide dissolving instead of accumulating, which is why the "
                          "H2O2 MRR peak moves from ~1 wt% to ~3 wt% when glycine is present."),
            "direction": "enhance", "model": "linear",
            "soluble_cu_enhancement_factor": num(1.4e6, "x [Cu]_total / [Cu2+]_free",
                "Computed from MINTEQ v4 Cu-glycinate stability constants at 0.01 M total glycine, "
                "pH 7 (the Aksu & Doyle 2001 condition)", "literature",
                "This is a thermodynamic speciation ratio, NOT an MRR ratio."),
            "claimed_range_wt_pct": num([0.05, 16.0], "wt%",
                "US8974692B2 (chelating agent glycine 0.01-22 wt%, preferred 0.05-16 wt%)",
                "verified"),
            "saturation_conc_mM": nonum("no glycine concentration-MRR sweep extracted in this pass"),
            "magnitude_note": "Shifts the H2O2 optimum from ~1 wt% to ~3 wt%.",
            "source": "doi:10.1149/1.1344532 (Aksu & Doyle 2001, JES 148 B51); "
                      "doi:10.1149/1.1479157 (Aksu & Doyle 2002, JES 149 G352); "
                      "doi:10.1149/1.1615611; US8974692B2",
            "confidence": "literature",
        },
        "poly_si": {"mechanism": "Amino acids act as TMAH-free hydrolysis accelerators (the amine "
                                 "releases OH- on hydration).",
                    "direction": "enhance", "model": "none",
                    "claimed_range_wt_pct": num([0.05, 1.0], "wt%", "WO2021046080A1", "literature"),
                    "magnitude_note": "TODO(owner): patent range; no MRR curve.",
                    "source": "WO2021046080A1", "confidence": "literature"},
        "w": {"mechanism": "Used as one half of an amino-acid pair (pI<7 + pI>7) that adsorbs on "
                           "W at pH 1-5 to suppress static etch and plug recess.",
              "direction": "suppress", "model": "none",
              "example_conc_mM": num(1.0, "mM",
                  "US10676647B1 (silica 3 wt% + TBAH 0.09 wt% + Fe(NO3)3 0.002 wt% + malonic "
                  "0.004 wt% + amino acid 1 mM)", "verified"),
              "magnitude_note": "Note the SIGN FLIP vs Cu: complexant on Cu, inhibitor on W.",
              "source": "US10676647B1", "confidence": "verified"},
        "co": unknown("no data"), "ru": unknown("no data"), "oxide": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["citric_acid"] = {
    "aliases": ["citric acid", "citrate"],
    "role": "chelator", "cas": "77-92-9",
    "chemistry": {"formula": "C6H8O7",
                  "mw_g_mol": num(192.124, "g/mol", "PubChem CID 311", "literature"),
                  "pka1": num(3.13, "-",
                      "MINTEQ v4 (log beta 14.285 - 11.157); cross-checks the 3.2 quoted in "
                      "doi:10.1149/2.0111709jss", "verified"),
                  "pka2": num(4.76, "-", "MINTEQ v4 (11.157 - 6.396); paper quotes 4.9", "verified"),
                  "pka3": num(6.40, "-", "MINTEQ v4 (6.396); paper quotes 6.4", "verified")},
    "film_effects": {
        "co": {
            "mechanism": ("Tricarboxylate + hydroxyl chelator. It does NOT attack metallic Co - "
                          "it dissolves the oxide/hydroxide that H2O2 has already made. So it is "
                          "a MULTIPLICATIVE gate on the oxidiser term, not an additive one, and "
                          "it has its own saturation."),
            "direction": "enhance", "model": "langmuir",
            "saturation_conc_mM": num(100.0, "mM",
                "doi:10.1149/2.0111709jss (Popuri 2017, ECS JSST 6 P594, sec. 4.3: 'increasing "
                "citric acid concentration beyond 100 mM does not increase Co RRs'; swept "
                "50-500 mM)", "literature",
                "Saturation EXISTS and is bounded; the half-saturation constant is not derivable "
                "because the paper gives a figure, not a table."),
            "half_saturation_mM": nonum("only a figure is published; K_half not extractable"),
            "mechanical_floor_nm_per_min": num(140.0, "nm/min",
                "doi:10.1149/2.0111709jss (pH 4, 3 wt% silica, no H2O2 and no citric acid)",
                "literature"),
            "magnitude_note": "Saturates at ~100 mM.",
            "source": "doi:10.1149/2.0111709jss",
            "confidence": "literature",
        },
        "cu": {"mechanism": "Cu-citrate complexation softens/dissolves the surface layer.",
               "direction": "enhance", "model": "none",
               "example_conc_M": num(0.1, "M", "doi:10.3390/ma17194905", "literature"),
               "magnitude_note": "0.1 M gives ~4.0x Cu MRR versus abrasive-free baseline "
                                 "(Gamagedara & Roy 2024).",
               "source": "doi:10.1149/1.1890786; doi:10.3390/ma17194905", "confidence": "literature"},
        "w": {"mechanism": "Used as an H2O2 stabiliser / pH adjuster rather than a rate driver.",
              "direction": "negligible", "model": "none",
              "magnitude_note": "TODO(owner): no W rate data.",
              "source": "US10676647B1", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["edta"] = {
    "aliases": ["edta", "ethylenediaminetetraacetic acid"],
    "role": "chelator", "cas": "60-00-4",
    "chemistry": {"formula": "C10H16N2O8",
                  "mw_g_mol": num(292.24, "g/mol", "PubChem CID 6049", "literature"),
                  "pka1": num(2.0, "-", "PubChem CID 6049", "literature"),
                  "pka4": num(10.26, "-", "PubChem CID 6049", "literature")},
    "film_effects": {
        "cu": {"mechanism": ("Hexadentate chelator; the enormous chelate effect means Cu is "
                             "locked in solution and cannot redeposit. In practice EDTA is often "
                             "TOO strong for rate control - it is used for contamination control "
                             "and for stabilising Fe catalysts rather than to raise MRR."),
               "direction": "enhance", "model": "none",
               "log_K_cu": num(18.8, "log K (Cu2+ + EDTA4-)",
                   "Quoted in knowledge/additives/catalog.yaml from standard stability-constant "
                   "tables; NOT verified against NIST SRD 46 in this pass", "unverified"),
               "magnitude_note": "TODO(owner): verify log K against NIST SRD 46; no CMP MRR sweep.",
               "source": "US8506661B2", "confidence": "unverified"},
        "w": {"mechanism": "Chelates the Fe(III) accelerator, acting as an H2O2 stabiliser "
                           "(extends pot life at the cost of catalytic rate).",
              "direction": "suppress", "model": "none",
              "log_K_fe": num(25.1, "log K (Fe3+ + EDTA4-)",
                  "Same secondary source as log_K_cu; NOT verified", "unverified"),
              "magnitude_note": "TODO(owner): verify constants and quantify the rate penalty.",
              "source": "US10676647B1", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["oxalic_acid"] = {
    "aliases": ["oxalic acid", "oxalate"],
    "role": "complexant", "cas": "144-62-7",
    "chemistry": {"formula": "C2H2O4",
                  "mw_g_mol": num(90.034, "g/mol", "PubChem CID 971", "literature"),
                  "pka1": num(1.25, "-", "PubChem CID 971", "literature"),
                  "pka2": num(4.14, "-", "PubChem CID 971", "literature")},
    "film_effects": {
        "cu": {
            "mechanism": ("Strong low-pH bidentate complexant. Because pKa1 is 1.25 it is still "
                          "deprotonated at pH 3, which is exactly why it is the chelator of choice "
                          "for ACIDIC high-rate Cu slurries where glycine (amine pKa 9.78) is "
                          "ineffective. It is the presence of oxalate that reverses the sign of "
                          "the H2O2 term on Cu."),
            "direction": "enhance", "model": "none",
            "example_conc_M": num(0.08, "M",
                "doi:10.1149/2162-8777/adc59e (Jani 2025, Table I, Expts 30-32; pH 3, colloidal "
                "silica 6 wt%, no BTA) - Cu RR 2282-2578 nm/min", "verified"),
            "saturation_conc_mM": nonum("oxalate concentration was held fixed in the cited series"),
            "magnitude_note": "Enables 2300+ nm/min Cu rates at pH 3.",
            "source": "doi:10.1149/1.1883873; doi:10.1149/2162-8777/adc59e",
            "confidence": "literature",
        },
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["malic_acid"] = {
    "aliases": ["malic acid", "malate", "hydroxysuccinic acid"],
    "role": "complexant", "cas": "6915-15-7",
    "chemistry": {"formula": "C4H6O5",
                  "mw_g_mol": num(134.087, "g/mol", "PubChem CID 525", "literature"),
                  "pka1": num(3.40, "-", "PubChem CID 525", "literature"),
                  "pka2": num(5.20, "-", "PubChem CID 525", "literature")},
    "film_effects": {
        "cu": {"mechanism": "alpha-hydroxy dicarboxylate; the OH group adds a third donor, so it "
                            "chelates Cu more strongly than plain succinate.",
               "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): listed among Cu slurry complexing agents; no "
                                 "concentration-MRR data located in this pass.",
               "source": "US20050090104A1 (complexing agent list)", "confidence": "unverified"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["malonic_acid"] = {
    "aliases": ["malonic acid", "malonate", "propanedioic acid"],
    "role": "chelator", "cas": "141-82-2",
    "chemistry": {"formula": "C3H4O4",
                  "mw_g_mol": num(104.062, "g/mol", "PubChem CID 867", "literature"),
                  "pka1": num(2.83, "-", "PubChem CID 867", "literature"),
                  "pka2": num(5.69, "-", "PubChem CID 867", "literature")},
    "film_effects": {
        "w": {"mechanism": "Binds the Fe(III) accelerator so H2O2 is not decomposed in the drum - "
                           "a pot-life stabiliser whose dose is set stoichiometrically against Fe.",
              "direction": "suppress", "model": "linear",
              "example_conc_wt_pct": num(0.004, "wt%",
                  "US10676647B1 (against Fe(NO3)3 0.002 wt%, approximately 2 equivalents per Fe)",
                  "verified"),
              "magnitude_note": "Stabiliser, not a rate driver; excess will throttle the Fenton cycle.",
              "source": "US10676647B1", "confidence": "verified"},
        "cu": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["tartaric_acid"] = {
    "aliases": ["tartaric acid", "tartrate"],
    "role": "complexant", "cas": "87-69-4",
    "chemistry": {"formula": "C4H6O6",
                  "mw_g_mol": num(150.087, "g/mol", "PubChem CID 875", "literature"),
                  "pka1": num(2.98, "-", "PubChem CID 875", "literature"),
                  "pka2": num(4.34, "-", "PubChem CID 875", "literature")},
    "film_effects": {
        "cu": {"mechanism": "Dihydroxy dicarboxylate complexant; used to tune Ta:Cu removal.",
               "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): selectivity study, no MRR-vs-concentration table.",
               "source": "doi:10.1149/1.2980345; US20050090104A1", "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
    "notes": "Primary published target is Ta barrier, which is outside this file's film list "
             "(doi:10.1149/1.2980345).",
}

A["ammonia"] = {
    "aliases": ["nh3", "nh4oh", "ammonium hydroxide", "ammonia"],
    "role": "complexant", "cas": "1336-21-6",
    "chemistry": {"formula": "NH4OH",
                  "mw_g_mol": num(35.046, "g/mol", "PubChem CID 14923", "literature"),
                  "pka": num(9.25, "-", "PubChem - NH4+/NH3 conjugate acid pKa", "literature")},
    "film_effects": {
        "cu": {
            "mechanism": ("Dual role and that is the trap: NH3 is both a base (raises pH) and a "
                          "strong Cu(II) ligand forming Cu(NH3)4^2+. In alkaline Cu CMP it is the "
                          "ammine complex, not the pH, that dissolves the oxide."),
            "direction": "enhance", "model": "none",
            "example_conc_vol_pct": num(5.0, "vol%",
                "doi:10.1557/proc-613-e7.4.1 (baseline Cu rate 400 nm/min with 5 vol% NH4OH + "
                "2 wt% alumina, no BTA)", "verified"),
            "magnitude_note": "400 nm/min baseline before any inhibitor is added.",
            "source": "doi:10.1557/proc-613-e7.4.1; US20050090104A1",
            "confidence": "literature",
        },
        "sin": {"mechanism": "Used as a trace metal-free base in SiN slurries.",
                "direction": "negligible", "model": "none",
                "example_conc_wt_pct": num(0.0006, "wt%", "US11999877B2", "verified"),
                "magnitude_note": "pH control only at this dose.",
                "source": "US11999877B2", "confidence": "verified"},
        "w": {"mechanism": "Listed pH adjuster.", "direction": "unknown", "model": "none",
              "magnitude_note": "TODO(owner): no data.", "source": "US10676647B1",
              "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "co": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["ethylenediamine"] = {
    "aliases": ["eda", "ethylenediamine", "1,2-diaminoethane"],
    "role": "complexant", "cas": "107-15-3",
    "chemistry": {"formula": "C2H8N2",
                  "mw_g_mol": num(60.10, "g/mol", "PubChem CID 3301", "literature"),
                  "pka1": num(6.85, "-", "PubChem CID 3301", "literature"),
                  "pka2": num(9.92, "-", "PubChem CID 3301", "literature")},
    "film_effects": {
        "ru": {
            "mechanism": ("Bidentate diamine. XPS shows EDA strips RuO2/RuO3 while leaving "
                          "metallic Ru alone (surface Ru(0) fraction rises 47.5% -> 58.9% after "
                          "treatment). So EDA is a MULTIPLICATIVE GATE on the oxidiser: with no "
                          "H2O2 there is no oxide to complex and EDA does essentially nothing."),
            "direction": "enhance", "model": "linear",
            "gain_at_peak_oxidizer": num(3.23, "x (RR at EDA 40 mM / RR at EDA 0)",
                "doi:10.1039/d1ra08243d Fig. 2: 116 -> 375 Angstrom/min at fixed 0.15 wt% H2O2, "
                "5 wt% SiO2, pH 9", "verified"),
            "rate_without_oxidizer_angstrom_per_min": num([48.0, 67.0], "Angstrom/min",
                "doi:10.1039/d1ra08243d Fig. 2b: EDA 0 -> 40 mM at H2O2 = 0 gives a "
                "non-monotonic 48-67 band, i.e. no trend", "verified",
                "This is the mechanical floor: 41-58% of the no-EDA oxidised rate."),
            "sweep_range_mM": num([0.0, 40.0], "mM", "doi:10.1039/d1ra08243d", "verified"),
            "magnitude_note": "3.23x at 40 mM WITH oxidiser; ~1x without. Model as a product, "
                              "never as a sum.",
            "source": "doi:10.1039/d1ra08243d",
            "confidence": "verified",
        },
        "si": {
            "mechanism": ("Completely different chemistry on Si: the amine hydrolyses water "
                          "(C2H4(NH2)2 + 2H2O -> C2H4(NH3+)2 + 2OH-) and the liberated OH- runs "
                          "Si + 4OH- -> Si(OH)4 + 4e-. The point is that at EQUAL pH the amine "
                          "beats an inorganic base, so the rate is not a function of pH alone."),
            "direction": "enhance", "model": "linear",
            "rate_nm_per_min": num(552.8, "nm/min",
                "doi:10.3390/nano12213893 (Bae 2022, Nanomaterials 12 3893) at EDA 0.10 wt%, "
                "pH 10.8-10.9, 60 nm colloidal silica", "verified"),
            "gain_vs_naoh": num(3.12, "x vs NaOH at the same pH",
                "doi:10.3390/nano12213893 (EDA 552.8 vs NaOH 0.125 wt% 177.1 nm/min)", "verified"),
            "magnitude_note": "3.12x over NaOH at matched pH - proves the amine acts beyond OH- supply.",
            "source": "doi:10.3390/nano12213893",
            "confidence": "verified",
        },
        "poly_si": {"mechanism": "Same OH- hydrolysis pathway as single-crystal Si; poly-Si "
                                 "averages over grain orientations so the anisotropy washes out.",
                    "direction": "enhance", "model": "linear",
                    "magnitude_note": "Transferred from the Si result (same surface reaction), not "
                                      "measured on poly-Si. TODO(owner): confirm on poly-Si.",
                    "source": "doi:10.3390/nano12213893; doi:10.1149/1.2086277",
                    "confidence": "estimated"},
        "cu": {"mechanism": "Listed as an organic amine Cu removal-rate booster.",
               "direction": "enhance", "model": "none",
               "magnitude_note": "TODO(owner): patent listing, no curve.",
               "source": "US8974692B2", "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "sin": unknown("no data"),
        "co": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["diethylenetriamine"] = {
    "aliases": ["deta", "diethylenetriamine"],
    "role": "accelerator", "cas": "111-40-0",
    "chemistry": {"formula": "C4H13N3",
                  "mw_g_mol": num(103.17, "g/mol", "PubChem CID 8113", "literature"),
                  "pka": nonum("three amine pKa values not individually retrieved")},
    "film_effects": {
        "si": {"mechanism": "Same amine hydrolysis-accelerator mechanism as EDA, with one more "
                            "amine group per molecule - highest measured rate of the series.",
               "direction": "enhance", "model": "linear",
               "rate_nm_per_min": num(617.2, "nm/min",
                   "doi:10.3390/nano12213893 at DETA 0.10 wt%, pH 10.8-10.9", "verified"),
               "magnitude_note": "DETA 617.2 > EDA 552.8 > TETA 499.1 nm/min - so it is NOT simply "
                                 "'more amines is better'; TETA falls back.",
               "source": "doi:10.3390/nano12213893", "confidence": "verified"},
        "poly_si": {"mechanism": "Transferred from Si.", "direction": "enhance", "model": "linear",
                    "magnitude_note": "TODO(owner): not measured on poly-Si.",
                    "source": "doi:10.3390/nano12213893", "confidence": "estimated"},
        "cu": unknown("no data"), "w": unknown("no data"), "oxide": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["triethylenetetramine"] = {
    "aliases": ["teta", "triethylenetetramine"],
    "role": "accelerator", "cas": "112-24-3",
    "chemistry": {"formula": "C6H18N4",
                  "mw_g_mol": num(146.23, "g/mol", "PubChem CID 5565", "literature"),
                  "pka": nonum("four amine pKa values not individually retrieved")},
    "film_effects": {
        "si": {"mechanism": "Amine hydrolysis accelerator; the longest chain of the three and the "
                            "slowest - likely steric crowding at the surface.",
               "direction": "enhance", "model": "linear",
               "rate_nm_per_min": num(499.1, "nm/min",
                   "doi:10.3390/nano12213893 at TETA 0.10 wt%, pH 10.8-10.9", "verified"),
               "magnitude_note": "Still 2.8x NaOH at the same pH.",
               "source": "doi:10.3390/nano12213893", "confidence": "verified"},
        "poly_si": {"mechanism": "Transferred from Si.", "direction": "enhance", "model": "linear",
                    "magnitude_note": "TODO(owner): not measured on poly-Si.",
                    "source": "doi:10.3390/nano12213893", "confidence": "estimated"},
        "cu": unknown("no data"), "w": unknown("no data"), "oxide": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["piperazine"] = {
    "aliases": ["piperazine"],
    "role": "accelerator", "cas": "110-85-0",
    "chemistry": {"formula": "C4H10N2",
                  "mw_g_mol": num(86.14, "g/mol", "PubChem CID 4837", "literature"),
                  "pka1": num(5.35, "-", "PubChem CID 4837", "literature"),
                  "pka2": num(9.73, "-", "PubChem CID 4837", "literature")},
    "film_effects": {
        "poly_si": {"mechanism": "Cyclic secondary diamine; by analogy with EDA/DETA it should "
                                 "release OH- on hydration and accelerate Si hydrolysis.",
                    "direction": "unknown", "model": "none",
                    "magnitude_note": "TODO(owner): NO primary CMP source found for piperazine on "
                                      "poly-Si in this pass. The mechanism sentence is an analogy, "
                                      "not evidence. Do not use numerically.",
                    "source": None, "confidence": "unverified"},
        "si": unknown("no primary source; see poly_si note"),
        "cu": unknown("no data"), "w": unknown("no data"), "oxide": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

# ------------------------------------------- SURFACTANTS / DISPERSANTS
A["sodium_dodecyl_sulfate"] = {
    "aliases": ["sds", "sodium dodecyl sulfate", "sodium lauryl sulfate", "sls"],
    "role": "surfactant", "cas": "151-21-3",
    "chemistry": {"formula": "C12H25NaO4S",
                  "mw_g_mol": num(288.38, "g/mol", "PubChem CID 3423265", "literature"),
                  "cmc_mM": num(8.2, "mM",
                      "Standard aqueous CMC of SDS at 25 C, no added salt (classical colloid "
                      "literature value; not re-verified in this pass)", "literature")},
    "film_effects": {
        "sin": {
            "mechanism": ("Electrostatic, not chemical. Si3N4 has an IEP near 5; below that the "
                          "surface is positive and the dodecyl sulfate anion adsorbs, forming a "
                          "hydrophobic layer that blocks silica particle contact. Above pH 5 the "
                          "nitride surface goes negative and the surfactant is repelled - the "
                          "effect simply turns off."),
            "direction": "suppress", "model": "threshold",
            "effective_conc_wt_pct": num(0.25, "wt%",
                "doi:10.1016/j.apsusc.2013.07.057 (Penta 2013, Appl. Surf. Sci. 283 986; SDS "
                "0.25 wt%, near CMC; 10 wt% colloidal silica 50 nm, 4 psi/75 rpm)", "literature"),
            "sin_rate_suppressed_nm_per_min": num(1.0, "nm/min",
                "doi:10.1016/j.apsusc.2013.07.057 Fig. 2, pH <= 4", "literature"),
            "ph_window_upper": num(4.0, "pH", "doi:10.1016/j.apsusc.2013.07.057", "literature",
                                   "Tied to the Si3N4 IEP near 5."),
            "magnitude_note": "SiN suppressed to ~1 nm/min at pH <= 4; no effect above the IEP.",
            "source": "doi:10.1016/j.apsusc.2013.07.057",
            "confidence": "literature",
        },
        "oxide": {
            "mechanism": ("VERIFIED NULL. SiO2 is negatively charged over the whole working pH "
                          "range, so an anionic surfactant cannot adsorb. The paper states it "
                          "outright: 'None of the surfactants studied adsorbs on an oxide surface "
                          "and, hence, does not suppress the oxide RR.' This absence is what makes "
                          "the pair selective - record it as a measured zero, not as ignorance."),
            "direction": "negligible", "model": "none",
            "langmuir_K": num(0.0, "L/mol", "doi:10.1016/j.apsusc.2013.07.057 sec. 4.5",
                              "literature", "A deliberate, sourced zero."),
            "magnitude_note": "Oxide rate unchanged or slightly up at pH 3-4 (counter-ion effect).",
            "source": "doi:10.1016/j.apsusc.2013.07.057",
            "confidence": "literature",
        },
        "cu": {"mechanism": "Used in alumina Cu slurries as a dispersant at ~1 mM; also lowers "
                            "friction sharply (COF 0.43 water -> 0.19 with SDS), which suppresses "
                            "scratching.",
               "direction": "suppress", "model": "none",
               "example_conc_mM": num(1.0, "mM",
                   "Gopal & Talbot 2007 conditions quoted in "
                   "knowledge/cmp/abrasive-size-d50-ekc-alumina-cu-h2o2-bta... (0.01 wt% BTA, "
                   "1e-3 M SDS, 0.1 wt% H2O2, 1e-3 M KNO3)", "literature"),
               "cof_with_sds": num(0.19, "-",
                   "knowledge/cmp/scratch-physics-source-signatures.md (dry 0.55 / water 0.43 / "
                   "SDS 0.01 M 0.19)", "literature"),
               "magnitude_note": "Defect/friction control, not a rate lever.",
               "source": "doi:10.1149/1.2718474", "confidence": "literature"},
        "w": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "co": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["dodecylbenzenesulfonic_acid"] = {
    "aliases": ["dbsa", "sdbs", "dodecylbenzene sulfonate", "sodium dodecylbenzenesulfonate"],
    "role": "surfactant", "cas": "27176-87-0",
    "chemistry": {"formula": "C18H30O3S",
                  "mw_g_mol": num(326.49, "g/mol", "PubChem CID 24845", "literature"),
                  "cmc_mM": nonum("CMC depends strongly on the isomer mix; not retrieved")},
    "film_effects": {
        "sin": {"mechanism": "Same IEP-gated anionic adsorption as SDS; the benzene ring makes it "
                             "bulkier and it works at a lower dose.",
                "direction": "suppress", "model": "threshold",
                "effective_conc_wt_pct": num(0.15, "wt%",
                    "doi:10.1016/j.apsusc.2013.07.057 (DBSA/DP/SLS all at 0.15 wt%, near CMC)",
                    "literature"),
                "magnitude_note": "Effective at 0.15 wt% vs 0.25 wt% for SDS.",
                "source": "doi:10.1016/j.apsusc.2013.07.057", "confidence": "literature"},
        "oxide": {"mechanism": "Verified null, same as SDS.", "direction": "negligible",
                  "model": "none", "magnitude_note": "See sodium_dodecyl_sulfate.oxide.",
                  "source": "doi:10.1016/j.apsusc.2013.07.057", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["ctab"] = {
    "aliases": ["ctab", "cetyltrimethylammonium bromide", "hexadecyltrimethylammonium bromide"],
    "role": "surfactant", "cas": "57-09-0",
    "chemistry": {"formula": "C19H42BrN",
                  "mw_g_mol": num(364.45, "g/mol", "PubChem CID 5974", "literature"),
                  "cmc_mM": num(0.92, "mM",
                      "Standard aqueous CMC of CTAB at 25 C (classical colloid literature value; "
                      "not re-verified in this pass)", "literature")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Cationic. The charge logic is the exact mirror of SDS: CTA+ adsorbs "
                          "strongly on negatively charged SiO2 (IEP ~2.5) and at high coverage "
                          "forms admicelles/bilayers. Expect oxide suppression and, near charge "
                          "neutralisation, abrasive flocculation - the defect risk."),
            "direction": "unknown", "model": "none",
            "magnitude_note": ("TODO(owner): NO CMP concentration-MRR study for CTAB on SiO2 was "
                               "retrieved in this pass. The mechanism above is standard colloid "
                               "science (silica/cationic surfactant adsorption), not a CMP "
                               "measurement. The closest documented analogue in this file is the "
                               "cationic POLYMER class (pdadmac), which switches oxide off at "
                               "single-digit ppm."),
            "source": None, "confidence": "unverified",
        },
        "sin": unknown("no CMP data; charge argument predicts weaker adsorption than on oxide "
                       "above the SiN IEP"),
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["polyacrylic_acid"] = {
    "aliases": ["paa", "polyacrylic acid", "poly(acrylic acid)", "ammonium polyacrylate"],
    "role": "dispersant", "cas": "9003-01-4",
    "chemistry": {"formula": "(C3H4O2)n",
                  "mw_g_mol": nonum("polydisperse; MW is a formulation variable, not a constant"),
                  "pka": num(4.5, "-",
                      "Apparent pKa of poly(acrylic acid) segments (rises with degree of "
                      "ionisation); indicative value", "estimated")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Anionic polyelectrolyte that adsorbs onto CERIA (positively charged "
                          "below its IEP ~6.8) and stabilises it both electrostatically and "
                          "sterically. Effect on oxide rate is indirect: better dispersion means "
                          "smaller effective particles, which typically costs rate but buys "
                          "scratch performance."),
            "direction": "nonmonotonic", "model": "none",
            "particle_size_effect_nm": num([155.0, 111.0], "nm DLS d50, before -> after 5 h milling",
                "doi:10.3390/polym18151899 (Hwang, Lyu, Kim, Polymers 18 1899; PAA-containing "
                "HNU15 ceria, pH ~9.1, no inhibitor)", "literature"),
            "oxide_rate_angstrom_per_min": num(114.4, "Angstrom/min",
                "doi:10.3390/polym18151899 (PAA-only ceria slurry on HDP oxide)", "literature"),
            "magnitude_note": "PAA-only ceria: HDP oxide 114.4 / SiN 14.3 Angstrom/min.",
            "source": "doi:10.3390/polym18151899; doi:10.1143/JJAP.44.5949",
            "confidence": "literature",
        },
        "sin": {"mechanism": "Adsorbs on Si3N4 and suppresses it; MW and abrasive size together "
                             "set where the oxide:SiN balance lands.",
                "direction": "suppress", "model": "none",
                "sin_rate_angstrom_per_min": num(14.3, "Angstrom/min",
                    "doi:10.3390/polym18151899 (PAA-only ceria)", "literature"),
                "selectivity_oxide_over_sin": num(8.0, "-", "doi:10.3390/polym18151899",
                                                  "literature"),
                "magnitude_note": "Selectivity 8.0 with PAA alone - far below the 200+ reachable "
                                  "with amino-acid inhibitors.",
                "source": "doi:10.3390/polym18151899; doi:10.1557/jmr.2007.0097",
                "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["eaa_copolymer"] = {
    "aliases": ["eaa", "ethylene-acrylic acid copolymer"],
    "role": "dispersant", "cas": "9010-77-9",
    "chemistry": {"formula": "poly(ethylene-co-acrylic acid)",
                  "mw_g_mol": nonum("copolymer; not a fixed MW"),
                  "pka": nonum("acrylic acid segments, see polyacrylic_acid")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Steric stabiliser on ceria: TEM shows a ~5 nm polymer shell. Raising "
                          "the dose raises zeta magnitude AND shrinks the secondary (agglomerate) "
                          "size - and agglomerate size is what makes scratches, so dispersant "
                          "dose is really a defect knob."),
            "direction": "nonmonotonic", "model": "none",
            "dose_range_wt_pct_of_ceria": num([5.0, 7.0], "wt% of ceria",
                "doi:10.3390/polym16243593 (Hwang, Park, Kim, Polymers 2024)", "verified"),
            "zeta_potential_mV": num([49.0, 52.0], "mV, at 5 -> 7 wt%",
                "doi:10.3390/polym16243593", "verified"),
            "secondary_particle_size_nm": num([281.6, 227.2], "nm, at 5 -> 7 wt%",
                "doi:10.3390/polym16243593", "verified"),
            "polymer_shell_thickness_nm": num(5.0, "nm", "doi:10.3390/polym16243593 (TEM)",
                                              "verified"),
            "magnitude_note": "5 -> 7 wt% shrinks agglomerates by 19%.",
            "source": "doi:10.3390/polym16243593",
            "confidence": "verified",
        },
        "sin": unknown("no data"), "cu": unknown("no data"), "w": unknown("no data"),
        "poly_si": unknown("no data"), "si": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["pvp"] = {
    "aliases": ["pvp", "polyvinylpyrrolidone", "povidone"],
    "role": "dispersant", "cas": "9003-39-8",
    "chemistry": {"formula": "(C6H9NO)n",
                  "mw_g_mol": num(40000.0, "g/mol",
                      "US20050090104A1 example uses MW ~40,000", "literature",
                      "Formulation choice, not a physical constant."),
                  "pka": nonum("non-ionic; no relevant pKa")},
    "film_effects": {
        "cu": {"mechanism": "Non-ionic amide polymer; the carbonyl coordinates weakly to Cu and "
                            "the chain provides steric protection against particle re-adhesion.",
               "direction": "suppress", "model": "none",
               "claimed_range_wt_pct": num([0.1, 3.0], "wt%", "US20050090104A1", "verified"),
               "magnitude_note": "TODO(owner): no concentration-MRR curve.",
               "source": "US20050090104A1", "confidence": "literature"},
        "oxide": {"mechanism": "Water-soluble polymer for dispersion / surface protection.",
                  "direction": "negligible", "model": "none",
                  "claimed_range_wt_pct": num([0.001, 5.0], "wt%", "US10526508B2", "verified"),
                  "magnitude_note": "TODO(owner): no rate effect quantified.",
                  "source": "US10526508B2", "confidence": "literature"},
        "w": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["triton_x_100"] = {
    "aliases": ["triton x-100", "octylphenol ethoxylate", "tx-100"],
    "role": "surfactant", "cas": "9002-93-1",
    "chemistry": {"formula": "C14H22O(C2H4O)n",
                  "mw_g_mol": num(625.0, "g/mol", "PubChem CID 5590 (average, n~9-10)",
                                  "literature"),
                  "cmc_mM": num(0.24, "mM",
                      "Standard aqueous CMC of Triton X-100 at 25 C (classical value; not "
                      "re-verified in this pass)", "literature")},
    "film_effects": {
        "oxide": {"mechanism": "Non-ionic ethoxylate; adsorbs by H-bonding to silanols rather "
                               "than by charge, so unlike SDS/CTAB its behaviour is only weakly "
                               "pH dependent.",
                  "direction": "unknown", "model": "none",
                  "magnitude_note": "TODO(owner): no oxide CMP concentration sweep located.",
                  "source": None, "confidence": "unverified"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
    "notes": "The only CMP reference found is a single optimum of 0.5 wt% with KMnO4 on 6H-SiC "
             "(doi:10.1016/j.apsusc.2015.10.158, abstract only, full text not obtained, and SiC "
             "is outside this film list). Recorded so the next person does not re-search it.",
}

A["polyethylene_glycol"] = {
    "aliases": ["peg", "polyethylene glycol", "poly(ethylene glycol)"],
    "role": "surfactant", "cas": "25322-68-3",
    "chemistry": {"formula": "H(OCH2CH2)nOH",
                  "mw_g_mol": nonum("grade-dependent"),
                  "pka": nonum("non-ionic")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Patents claim PEG forms an adsorbed stopping layer on oxide. The "
                          "worked examples do NOT support a concentration-dependent suppression: "
                          "across PEG 0 to 1.4 wt% the oxide rate stays in a 30-50 Angstrom/min "
                          "band with Spearman rho = +0.45, i.e. if anything it trends UP. Recorded "
                          "as a claim-versus-data conflict rather than as a suppression term."),
            "direction": "negligible", "model": "none",
            "claimed_range_wt_pct": num([0.001, 7.0], "wt%", "US10526508B2", "verified"),
            "measured_oxide_rate_angstrom_per_min": num([30, 30, 30, 50, 50, 50, 40, 50, 50, 50],
                "Angstrom/min",
                "US10526508B2 Tables 1-2 (10 examples, PEG 0/0.2/0.4/0.45/0.5/0.8/1.0/1.4 wt%, "
                "colloidal silica 1.5-3.5 wt%, pH 3.5, glutaric acid 0.025-1.0 wt%)", "literature"),
            "magnitude_note": "No dose-dependent oxide suppression in the patent's own examples.",
            "source": "US10526508B2",
            "confidence": "literature",
        },
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["pdadmac"] = {
    "aliases": ["pdadmac", "polydadmac", "poly(diallyldimethylammonium chloride)"],
    "role": "dispersant", "cas": "26062-79-3",
    "chemistry": {"formula": "(C8H16NCl)n",
                  "mw_g_mol": nonum("polydisperse"),
                  "pka": nonum("permanently quaternised - charge is pH independent, which is "
                               "exactly why it works across the whole pH range")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Cationic polyelectrolyte. It binds the negatively charged oxide "
                          "surface and shuts it off almost completely at ppm levels. Behaviour is "
                          "a SWITCH, not an isotherm: the transition is complete before the first "
                          "measurable dose, so no Langmuir K can be identified."),
            "direction": "suppress", "model": "threshold",
            "effective_conc_ppm": num(20.0, "ppm",
                "doi:10.1021/la104257k (Penta 2011, Langmuir 27 3502 - oxide and nitride both "
                "<1 nm/min at 20 ppm)", "literature"),
            "patent_example_angstrom_per_min": num({"sin": 125, "oxide": 7}, "Angstrom/min at 30 ppm",
                "US20210115297A1 Table 2 (control without polymer: SiN 223 / oxide 1078)",
                "verified",
                "Selectivity inverts to 17.9 in favour of SiN."),
            "magnitude_note": "Switch-like: oxide 1078 -> 7 Angstrom/min at 30 ppm.",
            "source": "doi:10.1021/la104257k; US20210115297A1",
            "confidence": "verified",
        },
        "sin": {"mechanism": "Also suppressed, but much less than oxide - which is what inverts "
                             "the selectivity.",
                "direction": "suppress", "model": "threshold",
                "patent_example_angstrom_per_min": num(125.0, "Angstrom/min at 30 ppm",
                    "US20210115297A1 Table 2 (control 223)", "verified"),
                "magnitude_note": "SiN only drops 44% while oxide drops 99%.",
                "source": "US20210115297A1", "confidence": "verified"},
        "poly_si": {"mechanism": "Selectively spares poly-Si while stopping oxide and nitride - "
                                 "the basis of poly-Si-selective slurries.",
                    "direction": "negligible", "model": "none",
                    "magnitude_note": "TODO(owner): extract the poly-Si rate column from Penta 2011.",
                    "source": "doi:10.1021/la104257k", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "si": unknown("no data"),
        "co": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["polyethyleneimine"] = {
    "aliases": ["pei", "polyethyleneimine"],
    "role": "dispersant", "cas": "9002-98-6",
    "chemistry": {"formula": "(C2H5N)n",
                  "mw_g_mol": num(None, "g/mol", "EP0846740A1 specifies MW 500-10,000",
                                  "literature", "Range, not a single value."),
                  "pka": nonum("branched amine; charge density varies strongly with pH, unlike "
                               "pdadmac")},
    "film_effects": {
        "oxide": {"mechanism": "Cationic polyamine; same electrostatic suppression family as "
                               "PDADMAC but pH-dependent because the amines must be protonated.",
                  "direction": "suppress", "model": "none",
                  "magnitude_note": "TODO(owner): background citation only, no example table read.",
                  "source": "EP0846740A1", "confidence": "unverified"},
        "sin": unknown("no data"), "cu": unknown("no data"), "w": unknown("no data"),
        "poly_si": unknown("no data"), "si": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["nonionic_alcohol_ethoxylate"] = {
    "aliases": ["aeo-9", "alcohol ethoxylate", "nonionic surfactant"],
    "role": "surfactant", "cas": "68439-46-3",
    "chemistry": {"formula": "R-(OCH2CH2)9-OH",
                  "mw_g_mol": nonum("distribution, not a single value"),
                  "cmc_mM": nonum("depends on alkyl chain distribution")},
    "film_effects": {
        "cu": {"mechanism": "Wets the surface and blocks particle re-adhesion; defect control.",
               "direction": "negligible", "model": "none",
               "claimed_range_ppm": num([1.0, 1000.0], "ppm", "US8974692B2", "verified"),
               "magnitude_note": "TODO(owner): no MRR effect quantified.",
               "source": "US8974692B2", "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["defoaming_polymer"] = {
    "aliases": ["defoamer", "byk", "g-336", "antifoam"],
    "role": "surfactant", "cas": None,
    "chemistry": {"formula": None, "mw_g_mol": nonum("proprietary formulation"),
                  "pka": nonum("n/a")},
    "film_effects": {
        "oxide": {"mechanism": ("Collapses entrained air. Bubbles at the pad interface cause "
                                "locally unpolished regions, so removing them raises the effective "
                                "rate - the chemistry never touches the wafer."),
                  "direction": "enhance", "model": "none",
                  "oxide_rate_angstrom_per_min": num([3493.0, 5558.0],
                      "Angstrom/min, without -> with defoamer",
                      "doi:10.3390/polym16060844 (Hwang & Kim, Polymers 2024, 16, 844)",
                      "verified"),
                  "magnitude_note": "+59% oxide rate from defoaming alone.",
                  "source": "doi:10.3390/polym16060844", "confidence": "verified"},
        "sin": {"mechanism": "Same mechanism; nitride also rises but less, so selectivity improves.",
                "direction": "enhance", "model": "none",
                "sin_rate_angstrom_per_min": num([60.0, 83.0], "Angstrom/min",
                    "doi:10.3390/polym16060844", "verified"),
                "selectivity_oxide_over_sin": num([59.0, 67.0], "-, without -> with BYK defoamer",
                    "doi:10.3390/polym16060844 (G-336 gives 80)", "verified"),
                "magnitude_note": "Selectivity 59 -> 67 (BYK) or 80 (G-336).",
                "source": "doi:10.3390/polym16060844", "confidence": "verified"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

# ---------------------------------------------- pH ADJUSTERS / BUFFERS
A["potassium_hydroxide"] = {
    "aliases": ["koh", "potassium hydroxide"],
    "role": "buffer", "cas": "1310-58-3",
    "chemistry": {"formula": "KOH",
                  "mw_g_mol": num(56.106, "g/mol", "PubChem CID 14797", "literature"),
                  "pka": nonum("strong base; fully dissociated")},
    "film_effects": {
        "oxide": {
            "mechanism": ("Two separable effects and they are often confused. (1) pH: raising pH "
                          "ionises surface silanols and accelerates the hydrolysis/dissolution "
                          "that softens the surface; the rate peaks near pH 11 and falls beyond. "
                          "(2) K+ itself: the counter-ion compresses the electrical double layer "
                          "so particles can approach the wafer - this is a separate, ion-specific "
                          "term that survives at constant pH."),
            "direction": "nonmonotonic", "model": "hill",
            "ph_series_nm_per_min": num([155.1, 172.7, 140.7], "nm/min at pH 10.0 / 11.0 / 12.5",
                "doi:10.1149/2162-8777/ac3e44 (Li 2021, ECS JSST 10 123008, Fig. 1 text: 1551 -> "
                "1727 -> 1407 Angstrom/min; 20 wt% colloidal silica D50 ~80 nm, K+ 0.25 mol/L, "
                "3.0 psi)", "literature"),
            "ph_peak": num(11.0, "pH", "doi:10.1149/2162-8777/ac3e44", "literature"),
            "k_ion_effect_pct": num(36.0, "% MRR increase at K+ 0.2 M",
                "doi:10.1149/2162-8777/ac3e44 Fig. 9 - salt identity does not matter, only the "
                "K+ molarity", "literature"),
            "k_ion_range_M": num([0.0, 0.4], "mol/L K+",
                "doi:10.1149/2162-8777/ac3e44 Fig. 10 - monotonic rise then peak", "literature"),
            "magnitude_note": "pH 11 peak; +36% from 0.2 M K+ at fixed pH.",
            "source": "doi:10.1149/2162-8777/ac3e44",
            "confidence": "literature",
        },
        "si": {"mechanism": "Supplies OH- for Si + 4OH- -> Si(OH)4 + 4e-. Rate follows "
                            "R ~ [H2O]^4 * [KOH]^(1/4), so it PEAKS and then falls as water "
                            "activity drops - raising alkali forever does not help.",
               "direction": "nonmonotonic", "model": "power",
               "rate_law_exponents": num({"h2o": 4.0, "koh": 0.25}, "-",
                   "doi:10.1149/1.2086277 (Seidel 1990, JES 137 3612) - best global fit across "
                   "the full concentration range", "literature"),
               "activation_energy_eV": num({"Si_100": 0.59, "Si_110": 0.61, "Si_111": 0.70}, "eV",
                   "doi:10.1149/1.2086277 Table II", "literature"),
               "rate_nm_per_min": num(193.2, "nm/min",
                   "doi:10.3390/nano12213893 at KOH 0.069 wt%, pH 10.90, 60 nm colloidal silica",
                   "verified"),
               "magnitude_note": "Etch rate peaks near ~20 wt% KOH, not monotonic.",
               "source": "doi:10.1149/1.2086277; doi:10.3390/nano12213893",
               "confidence": "literature"},
        "poly_si": {"mechanism": "Same OH- attack; poly-Si averages the orientation anisotropy "
                                 "(<110>:<100>:<111> approximately 50:30:1 at 100 C).",
                    "direction": "nonmonotonic", "model": "power",
                    "magnitude_note": "Orientation-averaging is a reasoned inference from Seidel's "
                                      "single-crystal data, not a poly-Si measurement. "
                                      "TODO(owner): confirm.",
                    "source": "doi:10.1149/1.2086277", "confidence": "estimated"},
        "cu": {"mechanism": "Sets the alkaline operating point of Cu slurries.",
               "direction": "unknown", "model": "none",
               "example_conc_wt_pct": num([0.41, 0.59], "wt%",
                   "US20110165777A1 TABLE 1 / TABLE 2 (pH 11.1 before H2O2 at 0.59 wt%)",
                   "verified"),
               "magnitude_note": "Cu MRR vs pH is V-shaped with a minimum near pH 6-6.5, so the "
                                 "sign of a pH move depends on which branch you are on.",
               "source": "US20110165777A1", "confidence": "literature"},
        "w": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["tmah"] = {
    "aliases": ["tmah", "tetramethylammonium hydroxide"],
    "role": "buffer", "cas": "75-59-2",
    "chemistry": {"formula": "C4H13NO",
                  "mw_g_mol": num(91.15, "g/mol", "PubChem CID 6285", "literature"),
                  "pka": nonum("quaternary ammonium hydroxide; strong base")},
    "film_effects": {
        "poly_si": {"mechanism": ("Supplies OH- like KOH but carries no mobile metal ion, which "
                                  "is why it is the standard base for front-end poly-Si. The "
                                  "quaternary cation also adsorbs on the Si surface, adding a "
                                  "second effect beyond OH- supply."),
                    "direction": "enhance", "model": "none",
                    "claimed_range_wt_pct": num([0.01, 5.0], "wt%",
                        "KR102644385B1 (KC Tech, quaternary ammonium base 0.01-5 wt%)",
                        "literature"),
                    "magnitude_note": "TODO(owner): no concentration-MRR curve extracted.",
                    "source": "KR102644385B1; WO2021046080A1; "
                              "park2007-jkps-tmah-abrasive-poly-oxide-selectivity",
                    "confidence": "literature"},
        "si": {"mechanism": "Same OH- chemistry; named by Seidel as a usable anisotropic etchant.",
               "direction": "enhance", "model": "power",
               "magnitude_note": "TODO(owner): no TMAH-specific CMP rate in the sources read.",
               "source": "doi:10.1149/1.2086277", "confidence": "literature"},
        "oxide": {"mechanism": "Also raises oxide rate via silanol ionisation, which is why "
                               "poly:oxide selectivity needs a separate stopping additive.",
                  "direction": "enhance", "model": "none",
                  "magnitude_note": "TODO(owner): not quantified here.",
                  "source": "US20050090104A1", "confidence": "unverified"},
        "cu": unknown("no data"), "w": unknown("no data"), "sin": unknown("no data"),
        "co": unknown("no data"), "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["nitric_acid"] = {
    "aliases": ["hno3", "nitric acid"],
    "role": "buffer", "cas": "7697-37-2",
    "chemistry": {"formula": "HNO3",
                  "mw_g_mol": num(63.012, "g/mol", "PubChem CID 944", "literature"),
                  "pka": num(-1.4, "-", "Strong acid; standard aqueous value", "literature")},
    "film_effects": {
        "w": {"mechanism": ("Sets the pH 2-5 window where WO3 is stable but W dissolution is "
                            "slow. The nitrate anion is itself mildly oxidising, so some "
                            "formulations deliberately go nitric-acid-free to avoid static etch "
                            "of the plug."),
              "direction": "nonmonotonic", "model": "none",
              "ph_sensitivity_k_per_ph": num(0.1163, "1/pH",
                  "Same term as potassium_iodate.w.ph_coupling_k_per_ph "
                  "(doi:10.1007/s40735-016-0041-4); the pH effect is oxidant-MEDIATED, not a "
                  "direct acid attack", "literature"),
              "magnitude_note": "Lowering pH 5 -> 2 raises W MRR ~1.3-1.5x when an oxidiser is "
                                "present; without an oxidiser the sign reverses.",
              "source": "doi:10.1007/s40735-016-0041-4; US9994735B2", "confidence": "literature"},
        "cu": {"mechanism": "Acidifies toward the low-pH branch of the V-shaped Cu pH curve.",
               "direction": "unknown", "model": "none",
               "magnitude_note": "TODO(owner): no data with this acid specifically.",
               "source": "US10676647B1", "confidence": "unverified"},
        "oxide": unknown("no data"), "poly_si": unknown("no data"), "si": unknown("no data"),
        "sin": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["phosphoric_acid"] = {
    "aliases": ["h3po4", "phosphoric acid", "phosphate"],
    "role": "buffer", "cas": "7664-38-2",
    "chemistry": {"formula": "H3PO4",
                  "mw_g_mol": num(97.994, "g/mol", "PubChem CID 1004", "literature"),
                  "pka1": num(2.15, "-", "PubChem CID 1004", "literature"),
                  "pka2": num(7.20, "-", "PubChem CID 1004", "literature"),
                  "pka3": num(12.35, "-", "PubChem CID 1004", "literature")},
    "film_effects": {
        "w": {"mechanism": ("Triple duty: pH adjuster, buffer (three pKa values give buffering "
                            "across most of the useful window), and H2O2 stabiliser through "
                            "phosphate binding of the Fe catalyst."),
              "direction": "negligible", "model": "none",
              "magnitude_note": "TODO(owner): patent listing; no rate data.",
              "source": "US10676647B1; US9994735B2", "confidence": "literature"},
        "cu": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["potassium_hydrogen_phthalate"] = {
    "aliases": ["khp", "potassium hydrogen phthalate", "potassium biphthalate"],
    "role": "buffer", "cas": "877-24-7",
    "chemistry": {"formula": "C8H5KO4",
                  "mw_g_mol": num(204.22, "g/mol", "PubChem CID 23676588", "literature"),
                  "pka": num(5.41, "-", "Second dissociation of phthalic acid", "literature")},
    "film_effects": {
        "w": {"mechanism": "Holds the KIO3 slurry at pH ~4 where iodate oxidises W but the WO3 "
                           "does not dissolve away.",
              "direction": "negligible", "model": "none",
              "example_conc_wt_pct": num(4.4, "wt%",
                  "WO1995024054A1 Example 2 (alumina 7% + KIO3 3.2% + KHP 4.4%, final pH 4.1)",
                  "verified"),
              "magnitude_note": "Buffer only; sets the operating point for the oxidiser term.",
              "source": "WO1995024054A1", "confidence": "verified"},
        "cu": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["acetic_acid"] = {
    "aliases": ["acetic acid", "acetate"],
    "role": "buffer", "cas": "64-19-7",
    "chemistry": {"formula": "C2H4O2",
                  "mw_g_mol": num(60.052, "g/mol", "PubChem CID 176", "literature"),
                  "pka": num(4.76, "-", "PubChem CID 176", "literature")},
    "film_effects": {
        "w": {"mechanism": "Acetate buffer near pH 4.76 stops pH drift as the oxidiser is "
                           "consumed during the polish.",
              "direction": "negligible", "model": "none",
              "magnitude_note": "TODO(owner): patent listing; no rate data.",
              "source": "US9994735B2; US10676647B1", "confidence": "literature"},
        "cu": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["benzenesulfonic_acid"] = {
    "aliases": ["bsa", "benzenesulfonic acid"],
    "role": "buffer", "cas": "98-11-3",
    "chemistry": {"formula": "C6H6O3S",
                  "mw_g_mol": num(158.17, "g/mol", "PubChem CID 7370", "literature"),
                  "pka": num(-2.8, "-", "Strong organic acid; indicative literature value",
                             "estimated")},
    "film_effects": {
        "cu": {"mechanism": "Strong organic acid used as a fixed co-component of alkaline Cu "
                            "patent formulations, balancing the KOH.",
               "direction": "unknown", "model": "none",
               "example_conc_wt_pct": num(1.0, "wt%",
                   "US20110165777A1 (held fixed at 1.0 wt% across all examples)", "verified"),
               "magnitude_note": "Held constant in every published table, so its own effect is "
                                 "not identifiable from that data.",
               "source": "US20110165777A1; US9200180B2", "confidence": "literature"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

# ------------------------------------------ SELECTIVITY / STOP-LAYER AGENTS
A["proline"] = {
    "aliases": ["proline", "l-proline"],
    "role": "inhibitor", "cas": "147-85-3",
    "chemistry": {"formula": "C5H9NO2",
                  "mw_g_mol": num(115.13, "g/mol", "PubChem CID 145742", "literature"),
                  "pka_cooh": num(1.99, "-", "PubChem CID 145742", "literature"),
                  "pka_nh": num(10.6, "-",
                      "Secondary amine pKa used in the Penta 2013 protonation analysis",
                      "literature",
                      "This high pKa is exactly why proline still works at pH 9.6 where "
                      "picolinic acid has switched off.")},
    "film_effects": {
        "sin": {
            "mechanism": ("Zwitterionic cyclic amino acid. Hydrogen bonds to the Si3N4 surface "
                          "(and to ceria active sites) and blocks the chemical-tooth contact. Its "
                          "advantage over the pyridine acids is the pKa: at 10.6 the ring NH is "
                          "still ~91% protonated at pH 9.6, so inhibition stays ON in alkaline "
                          "ceria slurries."),
            "direction": "suppress", "model": "langmuir",
            "sin_rate_nm_per_min": num(2.0, "nm/min",
                "doi:10.1149/1.1817870 (America & Babu 2004, ESL 7 G327, Table I; 1 wt% ceria + "
                "2 wt% additive, pH 9.6, 5 psi)", "literature"),
            "oxide_rate_nm_per_min": num(456.0, "nm/min", "doi:10.1149/1.1817870 Table I",
                                         "literature"),
            "selectivity_oxide_over_sin": num(228.0, "-", "doi:10.1149/1.1817870 Table I",
                "literature", "Best of the 10 additives screened; baseline is ~6:1."),
            "required_conc_wt_pct": num(2.0, "wt%",
                "doi:10.1016/j.colsurfa.2013.03.046 Table 1 - 20x more than picolinic acid needs",
                "literature"),
            "ph_window_upper": num(11.0, "pH", "doi:10.1016/j.colsurfa.2013.03.046 Table 1",
                                   "literature"),
            "adsorption_saturation_mg_per_g": num(100.0, "mg/g",
                "doi:10.1016/j.colsurfa.2013.03.046 Fig. 5 (Langmuir-type, saturating over "
                "0-2 wt% on both SiO2 and Si3N4; ceria takes <10 mg/g)", "literature"),
            "magnitude_note": "Selectivity 228 at pH 9.6; needs 2 wt%.",
            "source": "doi:10.1149/1.1817870; doi:10.1016/j.colsurfa.2013.03.046",
            "confidence": "literature",
        },
        "oxide": {"mechanism": "Adsorbs but does not suppress - the oxide rate stays near "
                               "430-460 nm/min across most additives screened.",
                  "direction": "negligible", "model": "none",
                  "oxide_rate_nm_per_min": num(456.0, "nm/min", "doi:10.1149/1.1817870 Table I",
                                               "literature"),
                  "magnitude_note": "Selectivity is decided by how hard SiN is switched off, not "
                                    "by anything happening to the oxide.",
                  "source": "doi:10.1149/1.1817870", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
    "notes": "Additive-abrasive coupling caveat: on high-La (24-31 wt%) commercial ceria, proline "
             "barely suppresses SiN, whereas L-glutamic acid is robust across three ceria grades. "
             "The additive alone does not determine the outcome.",
}

A["lysine"] = {
    "aliases": ["lysine", "l-lysine"],
    "role": "inhibitor", "cas": "56-87-1",
    "chemistry": {"formula": "C6H14N2O2",
                  "mw_g_mol": num(146.19, "g/mol", "PubChem CID 5962", "literature"),
                  "pka_cooh": num(2.18, "-", "PubChem CID 5962", "literature"),
                  "pka_side_nh3": num(10.53, "-", "PubChem CID 5962", "literature")},
    "film_effects": {
        "sin": {"mechanism": ("The extra side-chain amine is positively charged at working pH, "
                              "so lysine suppresses SiN hard - but it also adsorbs on the "
                              "negative silanol oxide surface, so used alone it damages the oxide "
                              "rate. In practice it is paired with glutamic acid."),
                "direction": "suppress", "model": "none",
                "paired_composition_M": num({"lysine": 0.02, "glutamic_acid": 0.02, "teaoh": 0.003},
                    "M, at pH 5",
                    "doi:10.1016/j.mee.2013.10.004 (Praveen 2014, Microelectron. Eng. 114 66)",
                    "literature"),
                "rates_angstrom_per_min": num({"sio2": 3606.1, "si3n4": 101.6}, "Angstrom/min",
                    "doi:10.1016/j.mee.2013.10.004", "literature"),
                "selectivity_oxide_over_sin": num(35.49, "-", "doi:10.1016/j.mee.2013.10.004",
                                                  "literature"),
                "magnitude_note": "Selectivity 35.5 - lower than proline's 228 but at a much "
                                  "higher absolute oxide rate (3606 vs 4560 Angstrom/min).",
                "source": "doi:10.1016/j.mee.2013.10.004; doi:10.1149/2.0061511jss",
                "confidence": "literature"},
        "oxide": {"mechanism": "Protonated side-chain amine can adsorb on the negative oxide "
                               "surface too, so at pH 9 lysine alone suppresses the oxide as well "
                               "- unwanted for STI.",
                  "direction": "suppress", "model": "none",
                  "magnitude_note": "This is why lysine is used paired, not alone.",
                  "source": "doi:10.1149/1.1817870", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["glutamic_acid"] = {
    "aliases": ["glutamic acid", "l-glutamic acid", "glutamate"],
    "role": "inhibitor", "cas": "56-86-0",
    "chemistry": {"formula": "C5H9NO4",
                  "mw_g_mol": num(147.13, "g/mol", "PubChem CID 33032", "literature"),
                  "pka_cooh": num(2.19, "-", "PubChem CID 33032", "literature"),
                  "pka_side_cooh": num(4.25, "-", "PubChem CID 33032", "literature"),
                  "pka_nh3": num(9.67, "-", "PubChem CID 33032", "literature")},
    "film_effects": {
        "sin": {"mechanism": "Extra side-chain carboxyl. Suppresses SiN robustly across ceria "
                             "grades where proline fails - the more transferable choice.",
                "direction": "suppress", "model": "none",
                "sin_rate_nm_per_min": num(3.0, "nm/min",
                    "doi:10.1149/2.0061511jss (Dandu 2015) - <3 nm/min on all three ceria grades "
                    "tested", "literature"),
                "magnitude_note": "Robust to abrasive grade, unlike proline.",
                "source": "doi:10.1149/2.0061511jss; doi:10.1016/j.mee.2013.10.004",
                "confidence": "literature"},
        "oxide": {"mechanism": "Little oxide suppression - this is the selectivity.",
                  "direction": "negligible", "model": "none",
                  "magnitude_note": "See lysine.sin paired composition for measured rates.",
                  "source": "doi:10.1016/j.mee.2013.10.004", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["mannitol"] = {
    "aliases": ["mannitol", "sorbitol", "polyol", "glycerol"],
    "role": "inhibitor", "cas": "69-65-8",
    "chemistry": {"formula": "C6H14O6",
                  "mw_g_mol": num(182.17, "g/mol", "PubChem CID 6251", "literature"),
                  "pka": nonum("polyol; no relevant acid dissociation in the working range")},
    "film_effects": {
        "sin": {"mechanism": "Multiple hydroxyls hydrogen bond to the nitride surface; more "
                             "polyol means lower SiN rate and higher selectivity.",
                "direction": "suppress", "model": "none",
                "claimed_range_wt_pct": num([0.1, 20.0], "wt%",
                    "US6616514B1 (organic polyol 0.1-20 wt%, optimum 0.5-10 wt%, mannitol "
                    "preferred)", "verified"),
                "magnitude_note": "TODO(owner): no rate table extracted, only the claim range.",
                "source": "US6616514B1", "confidence": "literature"},
        "oxide": {"mechanism": "Oxide largely unaffected.", "direction": "negligible",
                  "model": "none", "magnitude_note": "TODO(owner): not quantified.",
                  "source": "US6616514B1", "confidence": "unverified"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["mercaptotriazole"] = {
    "aliases": ["3-mercapto-1,2,4-triazole", "mercaptotriazole"],
    "role": "accelerator", "cas": "3179-31-5",
    "chemistry": {"formula": "C2H3N3S",
                  "mw_g_mol": num(101.13, "g/mol", "PubChem CID 79427", "literature"),
                  "pka": nonum("not retrieved")},
    "film_effects": {
        "sin": {"mechanism": ("The inverse case worth knowing: an amino/thiol-substituted "
                              "heteroaromatic that RAISES the SiN rate while suppressing TEOS - "
                              "used for reverse-STI schemes where nitride must go first."),
                "direction": "enhance", "model": "none",
                "claimed_range_wt_pct": num([0.01, 5.0], "wt%",
                    "US11999877B2 (Versum/Merck; SiN rate enhancers 0.01-5 wt%, preferred 0.1-1)",
                    "verified"),
                "selectivity_sin_over_teos": num(40.0, "-, minimum claimed",
                    "US11999877B2 (example: 0.5 wt% + NH4OH 0.0006 wt% + silica 0.75 wt%)",
                    "verified"),
                "magnitude_note": "SiN:TEOS >= 40 - the reverse of the usual STI direction.",
                "source": "US11999877B2", "confidence": "verified"},
        "oxide": {"mechanism": "TEOS suppressed relative to SiN.", "direction": "suppress",
                  "model": "none", "magnitude_note": "Inferred from the claimed selectivity.",
                  "source": "US11999877B2", "confidence": "literature"},
        "cu": unknown("no data"), "w": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "co": unknown("no data"), "ru": unknown("no data"),
        "snag": unknown(SNAG_NOTE),
    },
}

A["arginine"] = {
    "aliases": ["arginine", "l-arginine"],
    "role": "complexant", "cas": "74-79-3",
    "chemistry": {"formula": "C6H14N4O2",
                  "mw_g_mol": num(174.20, "g/mol", "PubChem CID 6322", "literature"),
                  "pka_guanidinium": num(12.48, "-", "PubChem CID 6322", "literature")},
    "film_effects": {
        "cu": {"mechanism": "The guanidino group complexes Cu2+.", "direction": "enhance",
               "model": "none",
               "magnitude_note": "TODO(owner): MRS proceedings cited second-hand; no curve.",
               "source": "doi:10.1557/proc-0914-f12-03", "confidence": "unverified"},
        "poly_si": {"mechanism": "Amino acid / guanidine accelerator in TMAH-free poly-Si slurries.",
                    "direction": "enhance", "model": "none",
                    "claimed_range_wt_pct": num([0.05, 1.0], "wt%",
                        "WO2021046080A1 (CMC Materials, pH 10-11)", "literature"),
                    "magnitude_note": "TODO(owner): patent range only.",
                    "source": "WO2021046080A1", "confidence": "literature"},
        "sin": {"mechanism": "Suppresses SiN hard (1 nm/min) but the side-chain amine is "
                             "positively charged at pH 9 and also hits the oxide - so it is a "
                             "poor STI choice despite the strong nitride stop.",
                "direction": "suppress", "model": "none",
                "sin_rate_nm_per_min": num(1.0, "nm/min", "doi:10.1149/1.1817870 Table I",
                                           "literature"),
                "magnitude_note": "Stops SiN harder than proline but costs oxide rate.",
                "source": "doi:10.1149/1.1817870", "confidence": "literature"},
        "oxide": {"mechanism": "Unwanted co-adsorption on ionised silanol.",
                  "direction": "suppress", "model": "none",
                  "magnitude_note": "Reason arginine loses to proline for STI.",
                  "source": "doi:10.1149/1.1817870", "confidence": "literature"},
        "w": unknown("no data"), "si": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

A["hedp"] = {
    "aliases": ["hedp", "etidronic acid", "1-hydroxyethylidene-1,1-diphosphonic acid"],
    "role": "chelator", "cas": "2809-21-4",
    "chemistry": {"formula": "C2H8O7P2",
                  "mw_g_mol": num(206.03, "g/mol", "PubChem CID 3305", "literature"),
                  "pka1": num(1.7, "-", "PubChem CID 3305", "literature")},
    "film_effects": {
        "cu": {"mechanism": ("Organophosphonate chelator. Its selling point is that it does not "
                             "itself react with H2O2, so the slurry has a long pot life while "
                             "still giving high Cu rate - an important practical distinction from "
                             "amino-acid chelators."),
               "direction": "enhance", "model": "none",
               "claimed_range_wt_pct": num([0.01, 10.0], "wt%",
                   "US20050090104A1 (organic phosphonate 0.01-10 wt%, preferred 0.1-2 wt%; Cu "
                   "example 0.05-5%)", "verified"),
               "magnitude_note": "TODO(owner): no MRR curve published.",
               "source": "US20050090104A1", "confidence": "verified"},
        "w": unknown("no data"), "oxide": unknown("no data"), "poly_si": unknown("no data"),
        "si": unknown("no data"), "sin": unknown("no data"), "co": unknown("no data"),
        "ru": unknown("no data"), "snag": unknown(SNAG_NOTE),
    },
}

# ------------------------------------------------------------- BIOCIDES
A["cmit_mit"] = {
    "aliases": ["kathon", "cmit/mit", "cmit", "isothiazolinone"],
    "role": "biocide", "cas": "26172-55-4",
    "chemistry": {"formula": "C4H4ClNOS + C4H5NOS",
                  "mw_g_mol": num(149.60, "g/mol", "PubChem CID 27246 (CMIT)", "literature"),
                  "pka": nonum("neutral heterocycle")},
    "film_effects": {
        f: {"mechanism": ("Isothiazolinone ring; the S-N bond is attacked by microbial thiols, "
                          "which is why ppm doses work. Formulated to have NO effect on polishing "
                          "performance - if a biocide changes your rate, something is wrong."),
            "direction": "negligible", "model": "none",
            "magnitude_note": "Active at 1-50 ppm (US10676647B1); a Cu example uses 0.000174 wt% "
                              "(~1.7 ppm) Kathon (US8506661B2).",
            "source": "WO2001060940A1; US10676647B1; US8506661B2",
            "confidence": "literature"}
        for f in FILMS
    },
}

A["mit"] = {
    "aliases": ["mit", "neolone", "2-methyl-4-isothiazolin-3-one"],
    "role": "biocide", "cas": "2682-20-4",
    "chemistry": {"formula": "C4H5NOS",
                  "mw_g_mol": num(115.15, "g/mol", "PubChem CID 39800", "literature"),
                  "pka": nonum("neutral heterocycle")},
    "film_effects": {
        f: {"mechanism": "Chlorine-free isothiazolinone - chosen when halide would pit the metal "
                         "film (Cl- is a known Cu/W pitting agent).",
            "direction": "negligible", "model": "none",
            "magnitude_note": "Example dose 0.15 wt% of product (Neolone M50), not of active.",
            "source": "WO2001060940A1", "confidence": "verified"}
        for f in FILMS
    },
}

# ================================================ INTERACTION RULES
interaction_rules = [
    {"pair": ["hydrogen_peroxide", "glycine"], "films": ["cu"], "sign": "synergy",
     "mechanism": ("H2O2 grows the Cu oxide and glycine chelates it away. Neither alone gives a "
                   "high rate: oxide-only passivates, chelator-only has nothing to dissolve. With "
                   "glycine present the H2O2 MRR optimum shifts from roughly 1 wt% to 3 wt% "
                   "because the chelator keeps consuming the film the oxidiser builds."),
     "model_form": "multiplicative gate (oxidiser term x complexant term), not additive",
     "source": "doi:10.1149/1.1615611; doi:10.1149/1.1479157; doi:10.1016/j.electacta.2003.11.010",
     "confidence": "literature"},

    {"pair": ["hydrogen_peroxide", "oxalic_acid"], "films": ["cu"], "sign": "synergy",
     "mechanism": ("At pH 3 oxalate (pKa1 1.25) is still deprotonated where glycine's amine is "
                   "not, so the same oxide-growth/oxide-dissolution pairing works in acid. This "
                   "combination REVERSES the sign of the H2O2 term: 3 -> 6 wt% H2O2 gives +13.0% "
                   "MRR, whereas the chelator-free alkaline system gives -35%."),
     "model_form": "regime switch - the oxidiser coefficient itself changes sign",
     "source": "doi:10.1149/2162-8777/adc59e", "confidence": "literature"},

    {"pair": ["hydrogen_peroxide", "benzotriazole"], "films": ["cu"], "sign": "antagonism",
     "mechanism": ("BTA caps the Cu(I) sites that the H2O2-grown oxide would otherwise expose to "
                   "dissolution, so the Cu(I)-BTA film sits on top of whatever the oxidiser makes "
                   "and the oxidiser's contribution to removal is largely cancelled. Adding 0.1 "
                   "wt% BTA drops the rate from 400 to 65 nm/min regardless of how much oxidiser "
                   "is present."),
     "model_form": "multiplicative suppression applied AFTER the oxidiser term",
     "source": "doi:10.1557/proc-613-e7.4.1; doi:10.1016/j.corsci.2010.05.002",
     "confidence": "literature"},

    {"pair": ["glycine", "benzotriazole"], "films": ["cu"], "sign": "antagonism",
     "mechanism": ("Direct competition for the same surface Cu sites: glycine wants to carry Cu "
                   "into solution as Cu(Gly)2, BTA wants to lock it into an insoluble polymer. "
                   "SIMS/XPS on Cu CMP surfaces shows both complexes coexisting, and the balance "
                   "between them - not either one alone - sets the dishing outcome."),
     "model_form": "competitive adsorption; the two coverages must sum to <= 1",
     "source": "doi:10.1149/1.1869112 (Elucidating Cu-Glycine and BTA Complexations in Cu-CMP "
               "Using SIMS and XPS)",
     "confidence": "literature"},

    {"pair": ["hydrogen_peroxide", "ethylenediamine"], "films": ["ru"], "sign": "synergy",
     "mechanism": ("The cleanest published example of a multiplicative gate. EDA alone at H2O2 = 0 "
                   "does nothing across 0-40 mM (rate wanders between 48 and 67 Angstrom/min). At "
                   "the H2O2 optimum of 0.15 wt%, the same EDA sweep gives 116 -> 375 Angstrom/min "
                   "(3.23x). XPS confirms EDA removes RuO2/RuO3 and leaves metallic Ru alone."),
     "model_form": "strictly multiplicative: complexant term -> 1 as oxidiser -> 0",
     "source": "doi:10.1039/d1ra08243d", "confidence": "verified"},

    {"pair": ["hydrogen_peroxide", "citric_acid"], "films": ["co"], "sign": "nonmonotonic",
     "mechanism": ("Synergy up to a point, then antagonism. Citrate dissolves the Co oxide that "
                   "H2O2 makes, but at 5 wt% H2O2 the oxidation rate outruns the complexation "
                   "rate and both removal and static dissolution fall. Citrate itself saturates "
                   "beyond 100 mM. So the pair has an interior optimum in BOTH concentrations."),
     "model_form": "two saturating terms with an oxidiser-excess penalty",
     "source": "doi:10.1149/2.0111709jss", "confidence": "literature"},

    {"pair": ["ferric_nitrate", "hydrogen_peroxide"], "films": ["w"], "sign": "synergy",
     "mechanism": ("Fenton catalysis. Fe3+/Fe2+ cycling turns H2O2 into hydroxyl radicals, so "
                   "single-digit ppm of Fe multiplies the effect of the peroxide instead of "
                   "adding to it. This is why the useful Fe axis is ppm while the H2O2 axis is "
                   "wt%."),
     "model_form": "catalytic multiplier on the oxidiser term",
     "source": "US5958288A; US8070843B2", "confidence": "verified"},

    {"pair": ["ferric_nitrate", "malonic_acid"], "films": ["w"], "sign": "antagonism",
     "mechanism": ("Deliberate, dosed antagonism. Malonate chelates the Fe(III) so the Fenton "
                   "cycle does not decompose the H2O2 in the drum. Roughly 2 equivalents per Fe "
                   "(0.004 wt% malonic against 0.002 wt% ferric nitrate). Overdosing kills the "
                   "rate - this is a pot-life/rate trade, not a free lunch."),
     "model_form": "stoichiometric titration of the catalyst term",
     "source": "US10676647B1", "confidence": "verified"},

    {"pair": ["potassium_iodate", "nitric_acid"], "films": ["w"], "sign": "synergy",
     "mechanism": ("pH acts on W only THROUGH the oxidation driving force (Nernst: W + 3H2O -> "
                   "WO3 + 6H+ + 6e-, E_rev = -0.119 - 0.059*pH). Lowering pH from 5 to 2 with HCl "
                   "raised MRR by 1.30-1.53x in all three oxidant-bearing conditions. Without an "
                   "oxidiser the sign reverses, so this is a genuine interaction and not a "
                   "standalone pH term."),
     "model_form": "exp(-k*(pH - pH_ref)) gated on oxidiser presence, k = 0.1163 per pH",
     "source": "doi:10.1007/s40735-016-0041-4", "confidence": "literature"},

    {"pair": ["sodium_dodecyl_sulfate", "picolinic_acid"], "films": ["sin", "oxide"],
     "sign": "antagonism",
     "mechanism": ("Both are pH-gated adsorbates competing for the same Si3N4 sites below the "
                   "nitride IEP (~5): the anionic surfactant needs a positive surface while the "
                   "protonated pyridine acid needs the same surface. Coverage is shared, so the "
                   "suppression from a mixture is NOT the sum of the two. Neither adsorbs on "
                   "oxide, so there is no competition there."),
     "model_form": "competitive Langmuir - a shared denominator (1 + K1*C1 + K2*C2)",
     "source": "doi:10.1016/j.apsusc.2013.07.057; doi:10.1016/j.colsurfa.2013.03.046",
     "confidence": "estimated",
     "note": "TODO(owner): the competitive form is a standard adsorption-engineering inference "
             "from the two single-additive studies. No mixture experiment was found."},

    {"pair": ["polyacrylic_acid", "proline"], "films": ["oxide", "sin"], "sign": "antagonism",
     "mechanism": ("The anionic dispersant and the zwitterionic inhibitor both target ceria "
                   "surface sites. PAA coats the abrasive for stability; proline must reach the "
                   "SiN/ceria contact to inhibit. Heavy dispersant loading can therefore blunt "
                   "the inhibitor. Documented indirectly: proline's effectiveness varies strongly "
                   "with the ceria grade and its surface coating."),
     "model_form": "shared ceria site budget",
     "source": "doi:10.1149/2.0061511jss; doi:10.3390/polym18151899",
     "confidence": "estimated",
     "note": "TODO(owner): inferred from grade-dependence, not from a PAA x proline cross."},

    {"pair": ["hydrogen_peroxide", "ceria_abrasive"], "films": ["oxide", "sin"], "sign": "synergy",
     "mechanism": ("The oxidiser acts on the ABRASIVE, not the film. H2O2 raises the Ce3+ "
                   "fraction, and Ce3+ is the site that forms the Si-O-Ce chemical-tooth bond. "
                   "0.5 wt% H2O2 gives 5.5x oxide MRR and lifts oxide:SiN selectivity from 1 to 3. "
                   "With a silica abrasive the same H2O2 does essentially nothing to oxide."),
     "model_form": "oxidiser modifies an abrasive property, so the term belongs to the abrasive, "
                   "not to the film",
     "source": "doi:10.1149/2162-8777/ab8393", "confidence": "literature",
     "note": "This pair is abrasive-conditional; do not apply it to silica slurries."},

    {"pair": ["potassium_hydroxide", "colloidal_silica"], "films": ["oxide"], "sign": "synergy",
     "mechanism": ("KOH contributes two separable things and they must not be merged into one pH "
                   "knob: the pH raises silanol ionisation (peak near pH 11) while K+ compresses "
                   "the double layer so particles reach the surface (+36% at 0.2 M K+, "
                   "independent of which K salt supplies it)."),
     "model_form": "two independent multipliers: f(pH) x g([K+])",
     "source": "doi:10.1149/2162-8777/ac3e44", "confidence": "literature"},

    {"pair": ["glycine", "hydrogen_peroxide"], "films": ["w"], "sign": "antagonism",
     "mechanism": ("The same amino acid that boosts Cu suppresses W. Paired amino acids (one with "
                   "pI<7, one with pI>7) adsorb on W at pH 1-5 and block the static etch that the "
                   "oxidiser would otherwise drive, protecting the plug from recess. Sign of the "
                   "additive is film-dependent - a good reason to keep per-film entries."),
     "model_form": "inhibitor term on W, complexant term on Cu - same molecule, opposite sign",
     "source": "US10676647B1", "confidence": "verified"},

    {"pair": ["benzotriazole", "sodium_dodecyl_sulfate"], "films": ["cu"], "sign": "antagonism",
     "mechanism": ("Surfactant and inhibitor compete for Cu surface sites; the surfactant also "
                   "lowers the friction coefficient (0.43 -> 0.19), which reduces the mechanical "
                   "abrasion that would otherwise strip the BTA film. Net effect on rate is "
                   "therefore not simply additive and can go either way depending on which term "
                   "dominates."),
     "model_form": "competitive adsorption plus a friction-mediated change in the abrasion rate "
                   "constant that sets K_effective",
     "source": "doi:10.1149/1.2718474; knowledge/cmp/scratch-physics-source-signatures.md",
     "confidence": "estimated",
     "note": "TODO(owner): mechanism is well supported but no BTA x SDS cross-sweep was found."},
]

doc = {
    "schema_version": 1,
    "description": ("CMP slurry additive knowledge base: how each named chemical acts on each "
                    "wafer film, with the physical mechanism and a traceable source for every "
                    "number. Built for prediction, not for lookup."),
    "evidence_policy": {
        "rule": ("Every numeric field is a mapping {value, unit, source, confidence}. A number "
                 "without a real source is written as value: null with confidence: unverified and "
                 "a TODO(owner) note. An invented number is worse than a null."),
        "confidence_levels": {
            "verified": "value read directly from a primary table/figure we hold, or reproduced "
                        "numerically in this repo",
            "literature": "stated in a primary source we identified but not independently "
                          "reproduced here",
            "estimated": "reasoned transfer from an adjacent system; mechanism sound, number not "
                         "measured on this pair",
            "unverified": "no adequate source - do not use the number",
        },
        "direction_values": ["enhance", "suppress", "nonmonotonic", "negligible", "unknown"],
        "model_values": ["langmuir", "linear", "power", "hill", "threshold", "none"],
        "negligible_vs_unknown": ("'negligible' is a SOURCED zero (e.g. anionic surfactants "
                                  "provably do not adsorb on SiO2). 'unknown' means we have no "
                                  "data. Never collapse the two."),
    },
    "films": {
        "cu": "electroplated copper interconnect",
        "w": "CVD tungsten plug",
        "oxide": "SiO2 (TEOS / PETEOS / HDP / thermal)",
        "poly_si": "polycrystalline silicon",
        "si": "single-crystal silicon substrate",
        "sin": "Si3N4 (LPCVD/PECVD nitride, STI stop layer)",
        "snag": "SnAg solder (advanced packaging) - NO primary additive data found; every SnAg "
                "entry in this file is an explicit gap",
        "co": "cobalt liner/cap",
        "ru": "ruthenium liner/barrier",
    },
    "known_gaps": [
        "snag (SnAg solder): zero primary additive-vs-removal-rate sources located. All entries "
        "are declared gaps.",
        "CTAB and other cationic surfactants: no CMP concentration-rate study found; only the "
        "cationic POLYMER class (pdadmac) is quantified.",
        "piperazine: no primary CMP source at all - listed only because it was requested, with "
        "direction: unknown.",
        "Triton X-100: only a single SiC optimum in an abstract; SiC is outside this film list.",
        "EDTA stability constants are second-hand and flagged unverified pending a NIST SRD 46 "
        "check.",
        "Most inhibitor entries lack an isotherm constant. Where one exists (BTA on Cu, picolinic "
        "acid on W) the equilibrium-vs-steady-state distinction is recorded, because using an "
        "equilibrium K in a CMP rate model is quantitatively falsified.",
    ],
    "additives": dict(A),
    "interaction_rules": interaction_rules,
}

OUT = "/Users/khleecnce/cmp-sim/cmp_sim/data/params/additives.yaml"
with open(OUT, "w") as f:
    f.write("# CMP slurry additive database - generated by build_additives.py\n")
    f.write("# Every number carries {value, unit, source, confidence}. Nulls are honest gaps.\n")
    yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
print("wrote", OUT)
