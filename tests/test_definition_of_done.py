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
