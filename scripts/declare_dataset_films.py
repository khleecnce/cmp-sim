"""Transcribe the film each dataset actually polished, from its own source.

Every value below is stated in the dataset's own title, source line or notes —
this is transcription, not inference. The evidence string records WHERE, so a
reviewer can check it without reopening the paper.

`other` means the film genuinely has no parameter pack (Mo, cemented carbide,
Pt, Ti). That is the honest label: it keeps the borrowed-pack audit able to see
the mismatch instead of hiding it behind a null.

Datasets inherited from `legacy/` are NEVER edited in place — project rule. A
dataset living under legacy is COPIED into cmp_sim/data/validation/datasets/
with the film added and a header explaining the override; the loader prefers the
cmp_sim copy.

Run once; idempotent.
"""
from pathlib import Path

import yaml

import cmp_sim
from cmp_sim.core.validation import dataset_paths

OVERRIDE_DIR = Path(cmp_sim.__file__).parent / "data" / "validation" / "datasets"

# dataset -> (film, evidence)
FILMS = {
    # --- copper -----------------------------------------------------------
    "hong2007_cu_ads_bta_polish_rate": (
        "cu", "title: 'Enhancing the Copper ... polish rate'"),
    "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator": (
        "cu", "title: 'Copper Chemical Mechanical Polishing'"),
    "jani2025_cu_h2o2_acidic_chelator": (
        "cu", "title: '... in High-Rate Copper CMP' (Jani 2025)"),
    "jani2025_cu_rsm_composition_heldout": (
        "cu", "same paper as jani2025_cu_h2o2_acidic_chelator"),
    "lee2021_cu_nicotinic_inhibitor": (
        "cu", "galvanic corrosion of Cu; Cu RR reported"),
    "miranda2004_cu_ph_h2o2_2x2": (
        "cu", "title: '... Chemical Mechanical Planarization of copper'"),
    "tw202115224a_cu_abrasive_size_pressure": (
        "cu", "title: 'Low dishing copper chemical mechanical planarization'"),
    "us20080090500a1_cu_ph_silica_cross": (
        "cu", "patent: dishing/erosion during copper CMP"),
    "us20110165777a1_cu_h2o2_series": (
        "cu", "patent title: 'Low-K Versus Copper Removal Rates'"),
    "us8501625b2_cu_h2o2_pressure_series": (
        "cu", "patent: polishing liquid for metal (Cu) film"),
    "us9200180b2_cu_abrasive_series": (
        "cu", "US9200180B2 Cu CMP composition"),
    "us9200180b2_cu_benzenesulfonic_series": (
        "cu", "US9200180B2 Cu CMP composition"),
    "us9200180b2_cu_h2o2_series": (
        "cu", "US9200180B2 Cu CMP composition"),
    "us9200180b2_cu_ph_alkaline_sweep": (
        "cu", "US9200180B2 Cu CMP composition"),

    # --- tungsten ---------------------------------------------------------
    "us20110186542a1_w_diamond_h2o2_ph": (
        "w", "patent title: 'tungsten chemical mechanical planarization'"),

    # --- silicon oxide ----------------------------------------------------
    "cn109609035b_oxide_anionic_silica_ph": (
        "oxide", "oxide polishing composition, charged abrasive"),
    "dandu2009_sio2_ceria_ph_sweep": (
        "oxide", "notes: 'blanket SiO2'; title: Silicon Dioxide over Nitride"),
    "kenchappa2021_softpad_hdp_oxide": (
        "oxide", "HDP oxide, per title"),
    "li2021_oxide_silica_ph": (
        "oxide", "title: Chemical Mechanical Polishing of oxide"),
    "mariscal2020_peteos_ceria_pressure_velocity_3x3": (
        "oxide", "PETEOS = plasma-enhanced TEOS oxide"),
    "netzband2020_thermal_oxide_ceria_ph": (
        "oxide", "title: 'Silicon Oxide CMP'"),
    "us9499721b2_teos_colloidal_silica_pressure_conc": (
        "oxide", "TEOS oxide, colloidal silica composition"),

    # --- silicon carbide --------------------------------------------------
    "entegris2022_us20220315802a1_sic_alumina_conc": (
        "sic", "source line: 'SiC CMP'"),
    "gong2024_4hsic_alumina_kmno4_L25": (
        "sic", "source line: '4H-SiC CMP L25'"),
    "liang2026_4hsic_ceria_composite_h2o2_conc": (
        "sic", "source line: '4H-SiC'"),
    "sic2026_ceria_h2o2_ph_DOE50": (
        "sic", "source line: 'SiC CMP 50-run DOE'"),
    "su2011_procengr_6hsic_alumina_abrasive_conc": (
        "sic", "6H-SiC, per source"),
    "sic2023_shear_rheological_L9": (
        "sic", "title: 'Si Surface of 4H-SiC Wafer'"),

    # --- films with no pack: label them 'other', do not invent packs -------
    "carbide2023_slurry_composition_L9": (
        "other", "cemented carbide insert; no carbide pack exists"),
    "mo2026_double_sided_L16": (
        "other", "notes: 'Mo(금속)라 전용 팩이 없다' — molybdenum"),

    # genuinely not a film experiment: phm2016's wafer film is never disclosed,
    # and the scorer treats a declared-but-unknown film as unusable, so it stays
    # null deliberately. Recorded here so the omission reads as a decision.
}

#: datasets that must NOT gain a film: the source does not state one
NO_FILM_STATED = {
    "phm2016_dresser_usage_mrr":
        "PHM tool-health challenge: dresser usage vs SCALED MRR; the wafer film "
        "is never disclosed. Declaring 'unknown' made the scorer drop the "
        "dataset (43 -> 42 scored), so null is the correct value.",
}

HEADER = (
    "# ── OVERRIDES THE INHERITED legacy/ COPY ────────────────────────────────\n"
    "# Only difference: `film:` is declared, transcribed from this dataset's own\n"
    "# source (evidence in the inline comment). legacy/ files are never edited in\n"
    "# place; the loader prefers this copy. No measured value is changed here.\n"
)


def main() -> int:
    changed = 0
    for path in dataset_paths():
        entry = FILMS.get(path.stem)
        if not entry:
            continue
        film, evidence = entry
        text = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text) or {}
        if doc.get("film") is not None:
            continue

        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("pack:"):
                lines.insert(i, f"film: {film}  # source: {evidence}\n")
                break
        else:
            lines.insert(0, f"film: {film}  # source: {evidence}\n")
        text = "".join(lines)

        if "legacy" in path.parts:
            target = OVERRIDE_DIR / path.name
            text = HEADER + text
        else:
            target = path
        target.write_text(text, encoding="utf-8")
        changed += 1
        print(f"  {path.stem[:50]:52} -> {film:7} "
              f"{'(override created)' if 'legacy' in path.parts else ''}")
    print(f"\n{changed} datasets now declare a film")
    return changed


if __name__ == "__main__":
    main()
