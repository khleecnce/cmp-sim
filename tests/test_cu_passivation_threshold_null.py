"""Lock the NULL result: the W passivation-shear threshold does NOT generalise
to Cu, so no Cu pack may carry a yield-offset constant.

Background
----------
`cmp_sim/models/passivation_threshold.py` derived, for tungsten, a Preston law
with a yield offset set by inhibitor coverage:

    RR = K*V*max(P - P0, 0),   P0 = P_y*theta,  theta = K_L*C/(1 + K_L*C)

from the Kaufman cycle (JES 138 (1991) 3460). Cu/BTA is the textbook
passivation system, so the same shear-off logic PREDICTS a Cu threshold. STATUS
forbade copying P_y across films and required measuring Cu's own ladders, with
the null outcome pre-registered.

`tools/cu_passivation_threshold_probe.py` measured it. Every Cu pressure ladder
at frozen chemistry was fitted with RR = a*(P - P0):

  * the intercept sign is a COIN FLIP (5/12 ladders positive), and
  * the median intercept is NEGATIVE as a fraction of the ladder's own mean
    pressure (~-0.09), i.e. the opposite sign a yield threshold requires, and
  * the Cu corpus's ladders all sit at ONE inhibitor level, so even a positive
    intercept could not have been attributed to coverage.

So the law is not supported on Cu, and this test exists to stop a later run
from "improving" Cu by fitting an offset that the data does not license.

These tests re-derive the numbers from the datasets on every run; they are not
snapshots of a JSON artefact.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "cu_passivation_threshold_probe.py"


def _load_probe():
    spec = importlib.util.spec_from_file_location("cu_thr_probe", PROBE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def probe():
    return _load_probe()


@pytest.fixture(scope="module")
def records(probe):
    out = []
    for name, _doc, rows in probe.cu_datasets():
        for lad in probe.ladders(rows):
            fit = probe.fit_threshold(lad)
            if fit is None:
                continue
            a, p0, r2, sse2 = fit
            _, sse1 = probe.fit_proportional(lad)
            pmid = 0.5 * (lad[0]["p"] + lad[-1]["p"])
            out.append({
                "dataset": name, "n": len(lad), "p0": p0,
                "p0_frac": p0 / pmid, "r2": r2,
                "sse_ratio": (sse2 / sse1) if sse1 > 0 else float("nan"),
                "inh": probe.inhibitor_level(lad[0]["ov"])[1],
            })
    return out


def test_probe_finds_cu_ladders(records):
    """Guard against the grouping silently collapsing (the bug found once:
    per-row bookkeeping keys made every row its own singleton group)."""
    assert len(records) >= 10, f"only {len(records)} Cu ladders found"
    names = {r["dataset"] for r in records}
    assert len(names) >= 3, f"ladders come from too few datasets: {names}"


def test_cu_threshold_intercept_sign_is_a_coin_flip(records, probe):
    """A yield threshold demands P0 > 0 on essentially every ladder."""
    p0s = [r["p0"] for r in records if math.isfinite(r["p0"])]
    frac_pos = sum(1 for v in p0s if v > 0) / len(p0s)
    assert frac_pos < 0.75, (
        "Cu intercepts became predominantly positive "
        f"({frac_pos:.0%} > 0) -- the null result no longer holds and the "
        "threshold must be RE-DERIVED for Cu before any constant is added.")


def test_cu_threshold_median_intercept_is_not_a_meaningful_fraction(records, probe):
    """Even if signs were favourable, the offset must be large enough to
    matter. The pre-registered bar is 10% of the ladder's mean pressure."""
    fracs = [r["p0_frac"] for r in records if math.isfinite(r["p0_frac"])]
    med = probe.median(fracs)
    assert med < 0.10, (
        f"median P0/P_mid rose to {med:+.3f} (>= 0.10): the Cu threshold "
        "would now be physically significant and this null test is stale.")
    # and it is in fact on the wrong side of zero
    assert med < 0.0, (
        f"median P0/P_mid = {med:+.3f}; the recorded null result had it "
        "NEGATIVE. Re-run the probe and update the recorded finding.")


def test_cu_inhibitor_axis_cannot_attribute_a_threshold(records):
    """The mechanism claim needs >=2 inhibitor levels among the ladders.
    Today there is one, and that is the reason attribution is impossible.
    If a new dataset adds a level, this test fails to PROMPT the re-test."""
    levels = {r["inh"] for r in records if r["inh"] is not None}
    assert len(levels) <= 1, (
        f"Cu ladders now span inhibitor levels {sorted(levels)}. The "
        "coverage attribution test (Q2 in the probe) is now possible -- run "
        "tools/cu_passivation_threshold_probe.py and decide on the evidence.")


def test_no_cu_pack_carries_a_yield_offset_constant():
    """Structural guard: no Cu parameter pack may declare a threshold/yield
    pressure. Preston stays linear in P for Cu until the data says otherwise."""
    import yaml

    banned = ("yield_pressure", "threshold_pressure", "p0_psi",
              "passivation_yield", "shear_yield_psi")
    packs = list((ROOT / "cmp_sim" / "data" / "params").rglob("*cu*.yaml"))
    assert packs, "no Cu parameter packs found -- path assumption broke"
    for path in packs:
        text = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text) or {}

        def walk(node, trail=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    low = str(k).lower()
                    for b in banned:
                        assert b not in low, (
                            f"{path.name}:{trail}{k} looks like a Cu yield "
                            "offset. The Cu threshold is a NULL result "
                            "(tests/test_cu_passivation_threshold_null.py); "
                            "do not add one without new pressure ladders at "
                            ">=2 inhibitor levels.")
                    walk(v, trail + f"{k}.")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, trail + f"[{i}].")

        walk(doc)


def test_threshold_gains_nothing_on_multi_level_cu_ladders(records, probe):
    """On the only ladders where the extra constant is falsifiable (>=3
    pressures) it must not deliver a decisive SSE win; a large win would mean
    real curvature we are ignoring."""
    inf = [r for r in records if r["n"] >= 3 and math.isfinite(r["sse_ratio"])]
    assert inf, "no >=3-point Cu ladder: the Q3 test lost its data"
    med = probe.median([r["sse_ratio"] for r in inf])
    # An SSE ratio near 1 means the free intercept bought almost nothing.
    assert med > 0.25, (
        f"median SSE2/SSE1 fell to {med:.3f} on Cu's multi-level ladders: the "
        "free intercept now explains most of the residual, so the Cu "
        "threshold deserves a fresh derivation.")
