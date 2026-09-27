"""The definition-of-done check, kept as a test rather than a one-off run.

STATUS's completion criteria are: every example runs, the literature gate passes,
and P1-P8 are implemented. A check that lives only in a terminal scrollback is
not a check, so it lives here.

WHAT THE RUN ACTUALLY SHOWS

Nine of ten examples produce a result; `snag_solder.yaml` exits 3 and that is
CORRECT. SnAg is declared unestablished, and the model refuses to predict it from
pack defaults rather than inventing a pH window — the one primary CMP report on
SnAg eliminated both windows it tried (alkaline etched the tin, acidic scratched
it). The refusal names the single missing input and the two ways to supply it.
`snag_solder_screening.yaml` is the same film with that input provided, and it
runs. The pair is deliberate: one example demonstrates the refusal, the other the
supported path.

Every running example emits 4-5 warnings, and none are silenced here. They are
disclosures of known gaps — an undetermined elastic/plastic contact branch, a
pack whose reference pad is itself estimated, an abrasive concentration deep in
saturation, a chemistry layer still lumped inside Kp. A clean run would mean the
warnings had been removed, not that the gaps had closed.

THE ACCURACY BAR, AND WHY IT IS 15% AND NOT 10%

The owner redefined completion on 2026-09-27 as "the minimum you actually found",
after the search for a 10% median was closed by measurement rather than by
effort. The bar is therefore median shape error <= 15%, and its justification is
a single measured ceiling:

  Grant every scored dataset a free exponent on its own best axis, fitted on the
  very rows being scored, with no requirement that datasets agree. No physical
  model can do this, because a model SHARES its constants. Under that oracle the
  corpus median only reaches 11.9% (from 16.5%), and datasets at or below 10% go
  from 15 to 20 of 46.

So <= 10% sits above the ceiling of the whole "add another law" programme, and
15% is the only band a shared-constant model can actually occupy. Two guards
below pin this: the bar itself, and the fact that the bar is NOT a noise-floor
argument. Published reproducibility in this corpus spans 1.5% to 37%, so 15% is
lenient against jani2025 and strict against miranda2004; conflating the two
arguments would turn a measured bound into an excuse (limits 16 vs 17).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((ROOT / "examples").glob("*.yaml"))

#: the one example that must FAIL, and why
DECLINES = "snag_solder.yaml"


def _run(path):
    return subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "run", str(path)],
        capture_output=True, text=True, cwd=ROOT)


def test_every_film_in_the_brief_has_an_example():
    names = " ".join(p.name for p in EXAMPLES)
    for film in ("cu", "tungsten", "oxide", "poly_si", "si_substrate",
                 "snag", "sti", "sic"):
        assert film in names, f"no example covers {film}"


def test_every_example_runs_except_the_one_that_must_not():
    failures = []
    for path in EXAMPLES:
        result = _run(path)
        if path.name == DECLINES:
            assert result.returncode == 3, (
                f"{path.name} should decline with exit 3 (unestablished film), "
                f"got {result.returncode}")
            continue
        if result.returncode != 0:
            failures.append(f"{path.name}: rc={result.returncode} "
                            f"{result.stderr[:200]}")
    assert not failures, "examples failed:\n" + "\n".join(failures)


def test_the_declining_example_names_what_it_needs():
    result = _run(ROOT / "examples" / DECLINES)
    text = result.stdout + result.stderr
    assert "not an established CMP target" in text
    assert "slurry_ph" in text, (
        "the refusal must name the missing input, not just refuse")
    assert "measurements:" in text, (
        "the refusal must tell the user how to make it run")


def test_the_supported_snag_example_actually_runs():
    """The refusal is only defensible if the supported path exists."""
    result = _run(ROOT / "examples" / "snag_solder_screening.yaml")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["removal_rate_A_per_min"] > 0
    assert any("RANKING" in str(w) for w in payload.get("warnings", [])), (
        "an unestablished film must warn that its absolute rate is a ranking, "
        "not a prediction")


def test_examples_warn_rather_than_run_silently():
    """Warnings are disclosures; a silent example would be the bug."""
    for path in EXAMPLES:
        if path.name == DECLINES:
            continue
        payload = json.loads(_run(path).stdout)
        assert payload.get("warnings"), (
            f"{path.name} runs with no warnings at all — every pack in this "
            "corpus has documented gaps, so silence means they stopped being "
            "reported")


def test_the_literature_gate_still_passes():
    result = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "validate"],
        capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr[:400]
    assert "-> PASS" in result.stdout, (
        "the +/-15% literature gate no longer passes:\n"
        + result.stdout[-600:])


def test_the_gate_counts_whole_datasets_not_best_groups():
    """The gate must not be passable by cherry-picking a good subset."""
    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "validate"],
        capture_output=True, text=True, cwd=ROOT).stdout
    assert "not counted" in out, (
        "datasets whose best group beats 15% but whose overall error does not "
        "must be excluded and shown as excluded")


# ── the accuracy bar, as redefined on 2026-09-27 ────────────────────────────

#: Completion bar for the corpus median shape error. NOT a noise floor: see the
#: module docstring and limits 16/17. Raising this number requires re-deriving
#: the oracle bound, not editing the constant.
COMPLETION_MEDIAN_PCT = 15.0

#: The measured ceiling that justifies the bar. A shared-constant model cannot
#: go below this, because the oracle that produces it fits each dataset alone.
ORACLE_CEILING_PCT = 11.9


def test_the_completion_bar_is_met():
    """The headline claim: median shape error is at or under the redefined bar.

    CURRENTLY FAILING BY DESIGN, AND LEFT FAILING ON PURPOSE.

    Redefining completion at 15% is what exposed the gap: the corpus sits at
    18.9%, so the project is 3.9 points short, not done. Marking this xfail
    would convert a measured shortfall into a green tick, which is the exact
    dishonesty the bar was written to prevent. It turns green when the modelling
    work lands — and the day it does, that is the completion signal.

    ⚠ The shortfall grew 3.2 -> 3.9 points on 2026-09-27 WITHOUT the model
    getting worse: a new dataset (limits.md §31) entered above the median and
    moved the counting position, while no constant changed and no existing
    dataset's score moved. Read this gap as "which dataset is in the middle",
    never as a trend.
    """
    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "accuracy", "--json"],
        capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr[-500:]
    summary = json.loads(out.stdout)["summary"]
    median = summary["median_shape_error_percent"]
    assert median <= COMPLETION_MEDIAN_PCT, (
        f"median shape error is {median:.1f}%, above the {COMPLETION_MEDIAN_PCT}% "
        f"completion bar. The bar is justified by a measured ceiling, so the fix "
        f"is modelling work or a re-derived bound — never a looser constant here")


def test_the_bar_sits_above_the_measured_ceiling():
    """A bar below the oracle ceiling would be unreachable by construction.

    This is the guard that keeps the redefinition honest in the other direction:
    if someone later tightens the bar to 10%, this fails and points at the reason
    rather than letting the project chase an impossible target again.
    """
    assert COMPLETION_MEDIAN_PCT > ORACLE_CEILING_PCT, (
        f"the completion bar ({COMPLETION_MEDIAN_PCT}%) is at or below the "
        f"over-fitted oracle ceiling ({ORACLE_CEILING_PCT}%), which no "
        f"shared-constant model can reach. Either the ceiling was re-measured "
        f"lower, or the bar is now impossible by construction")


def test_the_oracle_ceiling_is_still_what_the_bar_rests_on():
    """Recompute the ceiling; the bar's justification must not silently rot.

    The bar is only defensible while the oracle bound holds. If the corpus grows
    and the bound moves, this fails and forces the constant above to be restated
    with the new number.
    """
    from tools import unowned_error_partition as partition

    bound = partition.corpus_bound()
    granted = bound["median_if_every_oracle_granted"]
    assert granted > 10.0, (
        f"the oracle now reaches {granted:.1f}% — at or below 10%, which would "
        f"mean a real shared-constant law might reach 10% too. The 15% bar was "
        f"argued from this bound and must be re-argued, not assumed")
    assert abs(granted - ORACLE_CEILING_PCT) < 1.5, (
        f"the oracle ceiling moved to {granted:.1f}% from the recorded "
        f"{ORACLE_CEILING_PCT}%. Update ORACLE_CEILING_PCT and the STATUS entry "
        f"together, so the bar and its justification stay in step")


def test_the_bar_is_not_justified_as_a_noise_floor():
    """15% is a modelling ceiling, not a claim about measurement scatter.

    Published reproducibility in this corpus spans 1.5% to 37%, so a noise-floor
    argument would be lenient on jani2025 and strict on miranda2004. Keeping the
    two arguments apart is what stops a measured bound from becoming an excuse.
    """
    from tools import stated_reproducibility as repro

    entries = repro.summary()["datasets"].values()
    values = sorted(e["floor_percent_low"] for e in entries
                    if e.get("floor_percent_low") is not None)
    highs = sorted(e["floor_percent_high"] for e in entries
                   if e.get("floor_percent_high") is not None)
    assert len(values) >= 3, (
        f"only {len(values)} quantified reproducibility statements; the spread "
        f"argument needs at least three to stand")
    assert values[0] < COMPLETION_MEDIAN_PCT < highs[-1], (
        f"published reproducibility spans {values[0]:.1f}%-{highs[-1]:.1f}%, "
        f"which no longer straddles the {COMPLETION_MEDIAN_PCT}% bar. If the "
        f"corpus now agrees on a floor, the bar may finally be argued from noise "
        f"— but that argument has to be written, not inferred")
