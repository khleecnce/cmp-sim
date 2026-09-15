"""The additive and abrasive databases: schema, honesty, and wiring."""
import pytest
import yaml

from cmp_sim.core.params import OWN_PACK_DIR
from cmp_sim.slurry import formulation as fm
from cmp_sim.core.state import Additive


def _numeric_entries(node, out=None):
    """Every {value, confidence, ...} leaf in the tree."""
    out = [] if out is None else out
    if isinstance(node, dict):
        if "value" in node and "confidence" in node:
            out.append(node)
        for v in node.values():
            _numeric_entries(v, out)
    elif isinstance(node, list):
        for v in node:
            _numeric_entries(v, out)
    return out


# ── additives ────────────────────────────────────────────────────────
def test_additive_database_parses_and_is_substantial():
    db = fm.additive_database()
    assert len(db) >= 40, len(db)


def test_additives_cover_the_films_we_simulate():
    db = fm.additive_database()
    films = set()
    for entry in db.values():
        films |= set((entry or {}).get("film_effects", {}) or {})
    for required in ("cu", "w", "oxide", "poly_si", "si"):
        assert required in films, required


def test_every_additive_declares_a_role_we_understand():
    known = {"oxidizer", "inhibitor", "passivator", "complexant", "chelator",
             "surfactant", "dispersant", "accelerator", "buffer", "biocide"}
    for name, entry in fm.additive_database().items():
        role = (entry or {}).get("role")
        assert role in known, (name, role)


def test_the_key_additives_a_formulator_would_reach_for_are_present():
    db = fm.additive_database()
    for name in ("hydrogen_peroxide", "benzotriazole", "glycine", "citric_acid",
                 "potassium_hydroxide", "polyacrylic_acid"):
        assert name in db, name


# ── abrasives ────────────────────────────────────────────────────────
def test_abrasive_database_parses_and_covers_the_main_particle_types():
    db = fm.abrasive_database()
    for kind in ("colloidal_silica", "fumed_silica", "ceria", "alumina", "diamond"):
        assert kind in db, kind


def test_fumed_and_colloidal_silica_are_separate_entries():
    """They differ in shape and aggregation, so they cannot share one entry."""
    db = fm.abrasive_database()
    assert db["fumed_silica"] != db["colloidal_silica"]


def test_abrasive_lookup_resolves_aliases():
    props, err = fm.abrasive_properties("silica")
    assert err is None
    assert props.get("density_kg_m3")


def test_isoelectric_points_are_recorded_for_particles_and_films():
    raw = yaml.safe_load((OWN_PACK_DIR / "abrasives.yaml").read_text(encoding="utf-8"))
    assert "film_iep" in raw
    assert raw["film_iep"]["oxide"]["iep_ph"]["value"] is not None


def test_ceria_and_silica_have_different_removal_mechanisms():
    """Ceria forms Si-O-Ce chemical bonds; silica physisorbs. Reusing one
    concentration term across both is a modelling error the database must
    record explicitly."""
    db = fm.abrasive_database()
    ceria = db["ceria"]["film_effects"]["oxide"]
    silica = db["colloidal_silica"]["film_effects"]["oxide"]
    assert ceria["removal_mode"] != silica["removal_mode"]
    assert "chemical_tooth" in ceria["removal_mode"]
    blob = str(ceria)
    assert "do NOT copy" in blob or "not transfer" in blob.lower()


# ── the honesty contract ─────────────────────────────────────────────
@pytest.mark.parametrize("filename", ["additives.yaml", "abrasives.yaml"])
def test_unknown_numbers_are_null_and_explained_never_invented(filename):
    """A missing number must be null AND say why.

    Two legitimate reasons for a null: nothing was found (confidence
    unverified/unknown), or a source exists but gives a range rather than a
    single value (confidence names the source's kind, and the note explains).
    What is forbidden is a bare null with no explanation, or a confident value
    with no source."""
    raw = yaml.safe_load((OWN_PACK_DIR / filename).read_text(encoding="utf-8"))
    entries = _numeric_entries(raw)
    assert entries, "no numeric entries found"
    for e in entries:
        if e.get("value") is None:
            explained = (e.get("confidence") in ("unverified", "unknown")
                         or e.get("note") or e.get("source"))
            assert explained, e
        elif e.get("confidence") in ("literature", "measured", "verified"):
            assert e.get("source"), e


@pytest.mark.parametrize("filename", ["additives.yaml", "abrasives.yaml"])
def test_gaps_are_marked_for_the_owner_to_fill(filename):
    """Unknowns should be findable: TODO(owner) is the agreed marker."""
    text = (OWN_PACK_DIR / filename).read_text(encoding="utf-8")
    assert "TODO(owner)" in text


@pytest.mark.parametrize("filename", ["additives.yaml", "abrasives.yaml"])
def test_a_meaningful_fraction_of_values_is_actually_sourced(filename):
    raw = yaml.safe_load((OWN_PACK_DIR / filename).read_text(encoding="utf-8"))
    entries = _numeric_entries(raw)
    sourced = [e for e in entries if e.get("value") is not None and e.get("source")]
    assert len(sourced) >= 40, f"{filename}: only {len(sourced)} sourced values"


# ── wiring: a formulation must reach the physics ─────────────────────
def test_role_is_resolved_from_the_database_when_not_given():
    role, note = fm.resolve_role(Additive("hydrogen_peroxide", conc_wt_pct=1.0))
    assert role == "oxidizer"
    assert "additive database" in (note or "")


def test_an_unknown_additive_is_reported_not_assumed_inert():
    role, note = fm.resolve_role(Additive("unobtainium_x", conc_mM=1.0))
    assert role is None
    assert "not in the additive database" in note


def test_role_keys_match_what_the_physics_layer_actually_reads():
    """A plausible but wrong key name means the input is accepted and silently
    ignored — the exact failure this mapping exists to prevent."""
    assert fm.ROLE_TO_KEYS["inhibitor"] == ("inhibitor_mM",)
    assert fm.ROLE_TO_KEYS["oxidizer"] == ("oxidizer_wt_pct",)
