"""Does pad CONTACT separate the velocity inversion? No — and here is why not.

The lubrication diagnosis ended by pointing here: both velocity datasets stay
boundary-lubricated, yet down force enters them with opposite sign, so the
discriminating variable looked like pad contact rather than fluid film. STATUS
set the test: compute the contact metrics the model already exposes across both
datasets, check whether any of them separates the inverting rows the way lambda
failed to, and if none does, record it and stop rather than invent a threshold.

None does, and the reason is the same failure mode as lambda in a new costume.

WHAT THE METRICS ACTUALLY ARE. `situation.metrics` exposes three contact
quantities. Across the fifteen velocity rows:

    plasticity_index              constant WITHIN each dataset
    pad_limited_plasticity_lambda constant WITHIN each dataset
    summit_saturation             0.0111 to 0.0296, varying

The first two are fixed by the consumable set (pad and film pair), not by the
operating point, so they cannot separate rows that differ only in speed or down
force. They do differ BETWEEN the datasets — plasticity_index 0.0219 for
us6918821b2 against 0.0029 for mariscal2020 — but that difference points the
WRONG WAY: the inverting dataset has the more plastic contact, which predicts
more removal, not the collapse actually measured.

THE THIRD LOOKS PROMISING AND IS NOT. summit_saturation does order the rows,
and at first sight it separates cleanly where lambda could not:

    us6918821b2  1.5 psi (rate FALLS with speed)   0.01108
    mariscal2020 2.0 psi (never inverts)           0.01478
    mariscal2020 3.0 psi                           0.02217
    us6918821b2  4.0 psi (rate RISES with speed)   0.02956
    mariscal2020 4.0 psi                           0.02956

A threshold anywhere in 0.0111 < t < 0.0148 catches the inverting rows and
nothing else. But

    summit_saturation = 0.007390 * pressure_psi

on every row of both datasets, to six digits. It is DOWN FORCE, rescaled by a
pad constant that happens to be the same because both datasets use the same pad
stack. So "gate when summit_saturation < 0.0148" is precisely "gate when
pressure < 2 psi" — a pressure threshold fitted to one patent's low-pressure
arm, wearing a contact-mechanics name.

That fails the standard already applied to the oxidizer pH window, which was
accepted only because the pack's constants were MEASURED inside a stated pH
range. Here there is no measurement: one dataset inverts below 2 psi, one
dataset does not go below 2 psi, and nothing tells us which fact is causal.

WHAT WOULD SETTLE IT, NAMED. The model's contact state responds to pressure
through a single pad description; the inversion must come from how the asperity
POPULATION changes under load and sliding — density, radius, and whether the
pad glazes at low force. No dataset in the corpus reports pad surface stats
(asperity density or radius, measured by confocal/AFM) alongside a rate-vs-speed
sweep, so the discriminating variable cannot be computed from what we have.
That is now the BLOCKED-1 requirement.

These tests pin the finding so the pressure threshold cannot be reintroduced
under a contact-mechanics alias.
"""
from __future__ import annotations

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.predictive_score import _measured, _recipe_for
from cmp_sim.core.validation import dataset_paths

PRESTON = "us6918821b2_cu_ic1000_pressure_speed_2x3"
MARISCAL = "mariscal2020_peteos_ceria_pressure_velocity_3x3"


def _rows(stem: str):
    """(pressure, rpm, measured, predicted, metrics) per row."""
    path = next(p for p in dataset_paths() if p.stem == stem)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = []
    for row in doc["conditions"]:
        if _measured(row) is None:
            continue
        result = run_recipe(_recipe_for(doc, row))
        out.append((row["pressure_psi"], row["rpm_platen"], _measured(row),
                    result["removal_rate_A_per_min"],
                    result["situation"]["metrics"]))
    return out


def _all_rows():
    return _rows(PRESTON) + _rows(MARISCAL)


def test_two_contact_metrics_are_fixed_by_the_consumable_set_not_the_recipe():
    """They vary BETWEEN datasets but never WITHIN one, so they cannot
    separate rows that differ only in speed or down force."""
    for key in ("plasticity_index", "pad_limited_plasticity_lambda"):
        for stem in (PRESTON, MARISCAL):
            values = {round(m[key], 6) for *_, m in _rows(stem)}
            assert len(values) == 1, (
                f"{key} now varies within {stem} ({values}); it may be worth "
                "re-testing as a separator")

    # and across datasets they move the WRONG way to explain the inversion:
    # the inverting dataset has the HIGHER plasticity index, i.e. more plastic
    # contact, which would predict MORE removal, not less.
    preston = next(iter({m["plasticity_index"] for *_, m in _rows(PRESTON)}))
    mariscal = next(iter({m["plasticity_index"] for *_, m in _rows(MARISCAL)}))
    assert preston > mariscal, (preston, mariscal)


def test_summit_saturation_is_down_force_wearing_a_different_name():
    """The decisive check: it is proportional to pressure, one constant."""
    ratios = [m["summit_saturation"] / pressure
              for pressure, _, _, _, m in _all_rows()]
    spread = (max(ratios) - min(ratios)) / max(ratios)
    assert spread < 0.005, (
        f"summit_saturation is no longer a pure rescaling of pressure "
        f"(spread {spread:.3%}); re-run the diagnosis, it may now carry "
        "information")


def test_the_apparent_separation_is_therefore_a_pressure_threshold():
    """It does separate — which is exactly why it must be refused."""
    inverting = [m["summit_saturation"] for pressure, _, _, _, m
                 in _rows(PRESTON) if pressure == 1.5]
    others = [m["summit_saturation"] for pressure, _, _, _, m
              in _all_rows() if pressure != 1.5]

    # a clean gap exists ...
    assert max(inverting) < min(others), (inverting, others)
    # ... but every inverting row is simply the lowest-pressure row
    assert {p for p, _, _, _, _ in _rows(PRESTON) if p == 1.5} == {1.5}
    assert min(p for p, _, _, _, _ in _all_rows() if p != 1.5) == 2.0


def test_no_pressure_gate_was_introduced_under_a_contact_name():
    """Guard: no pack may declare a low-pressure cut-off for this.

    If the inversion is ever gated, it must be on a MEASURED pad property, not
    on a pressure threshold fitted to one patent's low-force arm.
    """
    from pathlib import Path

    import cmp_sim

    params = Path(cmp_sim.__file__).parent / "data" / "params"
    banned = ("min_pressure_psi", "pressure_gate", "summit_saturation_min",
              "lubrication_gate")
    offenders = {p.name: k for p in params.glob("*.yaml")
                 for k in banned if k in p.read_text(encoding="utf-8")}
    assert not offenders, (
        f"{offenders} declare a pressure-like gate. The corpus cannot justify "
        "one: summit_saturation == 0.00739 * pressure, so such a gate is a "
        "threshold fitted to us6918821b2's 1.5 psi arm.")


def test_the_inversion_is_still_unexplained_and_says_so():
    """The rows remain badly over-predicted; nothing was quietly fixed."""
    worst = min(_rows(PRESTON), key=lambda r: r[2] / r[3])
    assert worst[0] == 1.5 and worst[1] == 200
    assert worst[2] / worst[3] < 0.05, (
        "the 1.5 psi / 200 rpm row is no longer badly over-predicted — if a "
        "real mechanism landed, update this test and docs/derivations.md")
