"""The film must be stated, must exist, and must match the pack.

Three ways this used to produce a confidently wrong answer, all found by
fuzzing the API rather than by the unit tests (every example config names its
film explicitly, so the defaulting path was never exercised):

1. ``film: "cu"`` with ``pack: oxide_silica`` returned **1559.6 A/min** — the
   oxide rate — labelled as copper. The correct pairing gives 5458.5, a factor
   of 3.5 out, with nothing on screen to suggest a problem.
2. ``film: "unobtainium"`` returned a number as though the film existed.
3. Omitting the film entirely returned the oxide rate silently, because the
   dataclass default is ``"oxide"``.
"""
import pytest

from cmp_sim.api import run_recipe
from cmp_sim.core.params import ParamMissing

TOOL = {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60, "time_s": 60}


def body(**wafer):
    return {"model": "auto", "wafer": dict(wafer),
            "slurry": {"pack": "oxide_silica"}, "tool": dict(TOOL)}


# ── a film that does not exist ───────────────────────────────────────
def test_an_unknown_film_is_refused_by_name():
    with pytest.raises(ParamMissing) as exc:
        run_recipe(body(film="unobtainium"))
    msg = str(exc.value)
    assert "unobtainium" in msg
    assert "Known films" in msg, "the refusal does not say what is available"


def test_an_empty_film_is_refused():
    with pytest.raises(ParamMissing, match="wafer.film is required"):
        run_recipe(body(film="   "))


def test_case_is_forgiven_rather_than_refused():
    """'Cu' and 'cu' are the same film; refusing one teaches nothing."""
    result = run_recipe({"model": "auto", "wafer": {"film": "Cu"},
                         "slurry": {"pack": "cu_h2o2_bta"}, "tool": dict(TOOL)})
    assert result["film"] == "cu"
    assert result["removal_rate_A_per_min"] > 0


# ── film / pack mismatch ─────────────────────────────────────────────
def test_a_pack_for_another_film_is_flagged_not_silently_used():
    """The bug: this returned the OXIDE rate under a copper label."""
    result = run_recipe({"model": "auto", "wafer": {"film": "cu"},
                         "slurry": {"pack": "oxide_silica"}, "tool": dict(TOOL)})
    flagged = [w for w in result["warnings"]
               if "reference pack for a different film" in w]
    assert flagged, (
        "an oxide pack was used for copper with no warning; the rate returned "
        f"was {result['removal_rate_A_per_min']} A/min")
    assert "cu_h2o2_bta" in flagged[0], "it does not name the right pack"


def test_the_mismatch_is_a_warning_not_a_refusal():
    """Screening a tungsten slurry on copper is a legitimate experiment."""
    result = run_recipe({"model": "auto", "wafer": {"film": "cu"},
                         "slurry": {"pack": "w_fe_oxidizer"}, "tool": dict(TOOL)})
    assert result["removal_rate_A_per_min"] > 0


def test_the_matching_pack_produces_no_mismatch_warning():
    result = run_recipe({"model": "auto", "wafer": {"film": "oxide"},
                         "slurry": {"pack": "oxide_silica"}, "tool": dict(TOOL)})
    assert not [w for w in result["warnings"]
                if "reference pack for a different film" in w]


def test_the_two_pairings_really_do_differ(capsys):
    """If they agreed, the warning above would be pedantry. They differ 3.5x."""
    wrong = run_recipe({"model": "auto", "wafer": {"film": "cu"},
                        "slurry": {"pack": "oxide_silica"},
                        "tool": dict(TOOL)})["removal_rate_A_per_min"]
    right = run_recipe({"model": "auto", "wafer": {"film": "cu"},
                        "slurry": {"pack": "cu_h2o2_bta"},
                        "tool": dict(TOOL)})["removal_rate_A_per_min"]
    assert abs(right - wrong) / right > 0.2, (
        f"mismatched pack gave {wrong}, correct pack {right}")


# ── an omitted film ──────────────────────────────────────────────────
def test_omitting_the_film_still_runs_but_says_it_guessed():
    """Backward compatible with existing configs, no longer silent."""
    result = run_recipe({"model": "auto", "slurry": {"pack": "oxide_silica"},
                         "tool": dict(TOOL)})
    assert result["removal_rate_A_per_min"] > 0
    guessed = [w for w in result["warnings"] if "was not stated" in w]
    assert guessed, "an omitted film was defaulted silently"
    assert "oxide" in guessed[0]


def test_an_empty_wafer_section_behaves_the_same():
    result = run_recipe(body())
    assert [w for w in result["warnings"] if "was not stated" in w]


def test_stating_the_film_produces_no_guess_warning():
    result = run_recipe(body(film="oxide"))
    assert not [w for w in result["warnings"] if "was not stated" in w]


def test_the_defaulting_flag_cannot_be_set_from_the_payload():
    """Otherwise a caller could silence the warning by asserting it was
    explicit, which is exactly the disclosure this removes."""
    result = run_recipe({"model": "auto",
                         "wafer": {"film_was_defaulted": False},
                         "slurry": {"pack": "oxide_silica"},
                         "tool": dict(TOOL)})
    assert [w for w in result["warnings"] if "was not stated" in w], (
        "the payload managed to suppress the guessed-film warning")
