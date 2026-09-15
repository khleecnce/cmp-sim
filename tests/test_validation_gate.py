"""The project's headline claim: >=3 published RR-vs-P*V datasets within +/-15%.

This is success criterion (a). It is a test so it cannot quietly rot.
"""
import pytest

from cmp_sim.core.validation import best_fit_per_dataset
from cmp_sim.validate_cli import collect

GATE_PCT = 15.0
REQUIRED = 3


@pytest.fixture(scope="module")
def best():
    return list(best_fit_per_dataset(collect()).values())


def test_at_least_three_in_scope_datasets_are_within_fifteen_percent(best):
    passing = [f for f in best if f.in_scope and f.mape_pct <= GATE_PCT]
    names = sorted(f"{f.dataset} ({f.mape_pct:.1f}%)" for f in passing)
    assert len(passing) >= REQUIRED, f"only {len(passing)} passed: {names}"


def test_the_passing_datasets_are_independent_sources(best):
    """Three fits to the same patent would not be three validations."""
    passing = [f for f in best if f.in_scope and f.mape_pct <= GATE_PCT]
    stems = {f.dataset.split("_")[0] for f in passing}
    assert len(stems) >= REQUIRED, stems


def test_most_validation_data_comes_from_printed_tables_not_figures(best):
    """Digitised figures carry reading error; printed patent tables do not."""
    tabled = [f for f in best if f.read_method == "table"]
    assert len(tabled) >= 4, [f.dataset for f in best]


def test_the_known_counter_example_is_still_failing(best):
    """US6918821B2 is kept deliberately as a negative control: at 1.5 psi its
    measured rate FALLS with speed, which Preston cannot represent. If this
    ever starts passing, someone has tuned Kp to fit it or mis-edited the data."""
    cu = [f for f in best if "6918821" in f.dataset]
    assert cu, "the counter-example dataset has disappeared"
    assert cu[0].mape_pct > 25.0, (
        "the Preston counter-example now fits — check whether the data was "
        "altered or Kp was tuned to it")


def test_every_fit_has_a_citation(best):
    for f in best:
        assert f.source, f.dataset
