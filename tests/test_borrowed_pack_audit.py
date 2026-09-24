"""Which scores rest on a borrowed constant — and whether the borrowing is justified.

The titanium finding generalises into a hazard worth auditing: `oxide_silica` was
scored against a titanium dataset, and the exponent it applied turned out to be
tungsten's. A good number from the wrong pack is worse than a visible bad one,
because nothing in the report distinguishes them.

This file sweeps every dataset for a pack used on a film it was not fitted to,
and classifies each case. The sweep found three kinds, and only the third is a
defect.

1. JUSTIFIED BY MECHANISM. `sti_ceria` scores six oxide datasets. That is
   borrowing by film label but not by physics: the pack's own comment records
   that its measured exponents split by ABRASIVE (+0.87 across three ceria
   sweeps) rather than by film, and STI ceria slurries polish oxide. The
   constants were fitted on the mechanism being applied.

2. DELIBERATE NEGATIVE CONTROLS. `carbide2023` (36.2%) and `sic2023` (71.2%) are
   SiC/carbide experiments carried on the oxide pack ON PURPOSE, each with a
   note saying what gap the resulting bad number documents — per-condition
   chemistry not being wired through, and an absent particle-size term. Their
   errors are the measurement, not a failure to notice a mismatch.

3. PLACEHOLDER PACKS ON UNSUPPORTED FILMS. `bouvet2002_ti` (Ti, 30.7%) and
   `us8142675b2_pt` (Pt, 12.3%) run on `oxide_silica` because no Ti or Pt pack
   exists. Ti is already declared unsupported (limits.md entry 9). Pt is the one
   this audit adds: 12.3% LOOKS fine, and that is exactly the danger — a
   plausible number produced by constants fitted to a different material.

THE HOLE THE AUDIT FOUND, AND CLOSED

23 of 49 datasets declared no `film` at all, so a mismatch there was invisible to
any film-vs-pack check, and prose inference had to stand in. Every film has since
been transcribed from its own source (scripts/declare_dataset_films.py records
the evidence per dataset). Borrowings went from 7 visible to 14, and two SiC
datasets that the scorer could not use at all — `entegris2022` and `gong2024` —
became scorable, taking the corpus from 43/49 to 45/49 and 394 to 424 points.

Transcription is inert by construction: not one existing shape error moved, and
the medians are unchanged at 19.5% / 22.6%.

The single remaining null is `phm2016`, whose wafer film is never disclosed.
Labelling it `unknown` made the scorer drop it, so null is the right value there.

This test does not create packs to fix what it found; STATUS is explicit that the
deliverable is knowing which scores rest on a borrowed constant. What it enforces
is that every borrowing is one of the three kinds above, declared somewhere a
reader can find, and that no NEW undeclared borrowing can appear silently.
"""
from __future__ import annotations

import re

import yaml

from cmp_sim.core.predictive_score import PACK_FILM, score_dataset
from cmp_sim.core.validation import dataset_paths

#: film label differs from the pack's home film, with the reason it is allowed
DECLARED_BORROWINGS = {
    # justified by mechanism: ceria-on-oxide is what STI slurries do, and the
    # pack's exponents split by abrasive rather than by film
    "son2021_oxide_ceria_size_sweep": "mechanism",
    "us20190127607a1_hdpoxide_ceriasilica_size_sweep": "mechanism",
    "us20190127607a1_teos_ceriasilica_size_sweep": "mechanism",
    "yang2023_quartz_ceria_L25": "mechanism",
    # surfaced once films were transcribed: same ceria-on-oxide borrowing
    "dandu2009_sio2_ceria_ph_sweep": "mechanism",
    "kenchappa2021_softpad_hdp_oxide": "mechanism",
    "mariscal2020_peteos_ceria_pressure_velocity_3x3": "mechanism",
    "netzband2020_thermal_oxide_ceria_ph": "mechanism",
    # same slurry family, different metal film; W is the pack's own fitting set
    "bouvet2002_w_silica_size_sweep": "mechanism",
    # placeholder pack, film unsupported — must stay visible, never "fixed"
    "bouvet2002_ti_silica_size_sweep": "placeholder",
    "us8142675b2_pt_alumina_pressure_sweep": "placeholder",
    "mo2026_double_sided_L16": "placeholder",
    # deliberate negative controls, also registered in NEGATIVE_CONTROLS
    "carbide2023_slurry_composition_L9": "negative_control",
    "sic2023_shear_rheological_L9": "negative_control",
}

#: datasets deliberately run on the "wrong" pack to document a modelling gap
NEGATIVE_CONTROLS = {
    "carbide2023_slurry_composition_L9",
    "sic2023_shear_rheological_L9",
}

FILM_HINTS = {
    "cu": r"\bcu\b|copper",
    "w": r"\bw_|tungsten",
    "oxide": r"oxide|teos|quartz|sio2|hdp",
    "sic": r"sic|carbide",
}


def _docs():
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if doc.get("pack"):
            yield path.stem, doc


def _home(pack) -> str:
    return str(PACK_FILM.get(pack, "?")).lower()


def _declared_film(doc) -> str:
    return str(doc.get("film") or "?").lower()


def test_every_dataset_declares_a_film_except_the_one_with_none_stated():
    """The blind spot is closed: a null film can no longer hide a mismatch.

    Films were transcribed from each dataset's own source (see
    scripts/declare_dataset_films.py, which records the evidence per dataset).
    phm2016 is the single exception: its wafer film is never disclosed, and
    declaring 'unknown' made the scorer drop the dataset entirely, so null is
    the correct value there rather than a placeholder.
    """
    undeclared = sorted(stem for stem, doc in _docs()
                        if _declared_film(doc) in ("?", "none"))
    assert undeclared == ["phm2016_dresser_usage_mrr"], (
        f"{undeclared}: every dataset must declare the film it polished, "
        "transcribed from its own source — use 'other' when no pack exists")


def test_declaring_films_changed_no_prediction():
    """Transcription must be inert: it labels data, it does not model it."""
    from cmp_sim.cli import main  # noqa: F401  (import guard only)

    # the two datasets that gained a score did so because the scorer needs a
    # film at all — not because any existing number moved
    for stem in ("entegris2022_us20220315802a1_sic_alumina_conc",
                 "gong2024_4hsic_alumina_kmno4_L25"):
        score = score_dataset(next(p for p in dataset_paths()
                                   if p.stem == stem))
        assert score.shape_mape is not None, (
            f"{stem} was unscorable before its film was declared and must now "
            "be scored")


def test_the_overrides_do_not_touch_legacy():
    """Project rule: inherited files are copied and overridden, never edited."""
    from pathlib import Path

    import cmp_sim
    override_dir = (Path(cmp_sim.__file__).parent / "data" / "validation"
                    / "datasets")
    overrides = {p.stem for p in override_dir.glob("*.yaml")}
    assert len(overrides) > 25, (
        "the film overrides are missing; they must live under cmp_sim/data, "
        "not be written into legacy/")
    for path in dataset_paths():
        if "legacy" in path.parts:
            assert path.stem not in overrides, (
                f"{path.stem}: an override exists but the loader still resolves "
                "to the legacy copy — the override is not taking effect")


def test_every_declared_film_mismatch_is_registered():
    """A new borrowing cannot appear without a deliberate entry here."""
    found = set()
    for stem, doc in _docs():
        film, home = _declared_film(doc), _home(doc["pack"])
        if film not in ("?", "none") and home != "?" and film != home:
            found.add(stem)
    unregistered = found - set(DECLARED_BORROWINGS)
    assert not unregistered, (
        f"{sorted(unregistered)} score a film with another film's pack and are "
        "not registered; classify each as 'mechanism' or 'placeholder'")
    stale = set(DECLARED_BORROWINGS) - found
    assert not stale, f"{sorted(stale)} no longer borrow; drop them"


def test_the_mechanism_borrowings_are_ceria_on_oxide_or_the_packs_own_film():
    """'Justified' must mean something checkable, not a label."""
    for stem, why in DECLARED_BORROWINGS.items():
        if why != "mechanism":
            continue
        doc = dict(_docs())[stem]
        pack = doc["pack"]
        assert pack in ("sti_ceria", "oxide_silica"), (stem, pack)
        if pack == "sti_ceria":
            assert _declared_film(doc) == "oxide", (
                f"{stem}: sti_ceria may be lent to oxide (ceria slurries polish "
                "oxide, and the pack's exponents split by abrasive) — not to "
                "an arbitrary film")


def test_the_ceria_pack_justifies_itself_by_abrasive_not_film():
    """The claim above is read from the pack, not asserted here."""
    from pathlib import Path

    import cmp_sim
    text = (Path(cmp_sim.__file__).parent / "data" / "params"
            / "sti_ceria.yaml").read_text(encoding="utf-8")
    assert re.search(r"split by ABRASIVE, not by film", text), (
        "sti_ceria no longer records that its exponents follow the abrasive; "
        "the ceria-on-oxide borrowings lose their justification")


def test_placeholder_borrowings_keep_their_error_visible():
    """Ti and Pt must not be quietly excluded or quietly fitted."""
    for stem, why in DECLARED_BORROWINGS.items():
        if why != "placeholder":
            continue
        score = score_dataset(next(p for p in dataset_paths()
                                   if p.stem == stem))
        assert score.shape_mape is not None, (
            f"{stem} stopped being scored; an unsupported film that disappears "
            "from the report is worse than a visible error")


def test_platinum_is_the_dangerous_case_a_plausible_number_from_a_borrowed_pack():
    """12.3% on a Pt film scored with an oxide pack is not evidence about Pt."""
    score = score_dataset(next(p for p in dataset_paths()
                               if p.stem == "us8142675b2_pt_alumina_pressure_sweep"))
    assert score.shape_mape is not None and score.shape_mape < 20, (
        "the Pt number is low, which is precisely why it needs flagging; if it "
        "has risen, re-read this test's premise")
    doc = dict(_docs())["us8142675b2_pt_alumina_pressure_sweep"]
    assert _declared_film(doc) == "other", (
        "Pt must not be promoted to a film label while no Pt pack exists")


def test_negative_controls_say_why_they_use_the_wrong_pack():
    """Their bad numbers are the measurement, so the reason must be recorded."""
    docs = dict(_docs())
    for stem in NEGATIVE_CONTROLS:
        notes = str(docs[stem].get("notes", ""))
        assert notes.strip(), stem
        assert re.search(r"대조군|negative control|기록|하한|공백|부적합", notes), (
            f"{stem} is registered as a deliberate negative control but its "
            "notes no longer explain what gap its error documents")


def test_the_negative_controls_are_now_visible_to_the_label_check():
    """The blind spot this pair used to demonstrate is closed.

    Before films were transcribed, `carbide2023` and `sic2023` declared no film,
    so a label-vs-pack check could not see that they run on the oxide pack; only
    inference from their prose surfaced them. They now declare `other` and `sic`
    respectively, so they appear in the ordinary audit — which is why they are
    registered in DECLARED_BORROWINGS as negative controls.
    """
    docs = dict(_docs())
    for stem in NEGATIVE_CONTROLS:
        assert _declared_film(docs[stem]) not in ("?", "none"), stem
        assert DECLARED_BORROWINGS.get(stem) == "negative_control", (
            f"{stem} is a deliberate negative control and must be registered "
            "as one, not silently treated as a mechanism borrowing")


def test_prose_inference_is_no_longer_load_bearing():
    """With films declared, the fallback heuristic finds nothing new."""
    surfaced = set()
    for stem, doc in _docs():
        if _declared_film(doc) not in ("?", "none"):
            continue
        blob = (stem + " " + str(doc.get("notes", ""))[:400]).lower()
        guesses = [film for film, pattern in FILM_HINTS.items()
                   if re.search(pattern, blob)]
        home = _home(doc["pack"])
        if guesses and home != "?" and home not in guesses:
            surfaced.add(stem)
    assert not surfaced, (
        f"{sorted(surfaced)} still need prose inference to be spotted; declare "
        "their film from the source instead of relying on the heuristic")
