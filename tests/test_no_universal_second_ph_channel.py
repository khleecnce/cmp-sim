"""There is no single "second pH channel" — the hypothesis is falsified here.

Three datasets left residuals that looked like a missing second mechanism, and
STATUS.md set the rule before any code was written: check whether it is the
SAME second channel in all three; if it is, derive one additive two-channel pH
response and apply it to every pack; if it is not, say so and stop — do not add
a per-pack fudge term.

It is not the same channel. The three measured shapes are different shapes:

    cn109609035b (anionic silica/oxide)   monotone fall, tiny upturn at pH 6
    dandu2009    (ceria/oxide)            single bell, peak pH 4-5.5
    netzband2020 (ceria/oxide)            a V: minimum at pH 6, BOTH ends high

The last two are the same pack, `sti_ceria`, on the same film with the same
abrasive mineral, and they disagree about the shape itself rather than about a
constant:

    dandu2009     43 -> 953 -> 2763 -> 3474 -> 3443 -> 3504 -> 993 -> 694 -> 643
    netzband2020  198 (pH 4) -> 113 (pH 6) -> 200 (pH 8) -> 213 (pH 10)

A bell with one maximum cannot also be a V with one minimum. Adding a rising
alkaline channel would fix netzband2020 and BREAK dandu2009, which currently
matches to 1.03 and 0.96 at pH 8 and 10 — the region the new channel would
raise.

So the work stops here, and these tests exist to keep it stopped: they pin the
contradiction as a measurement-level fact, so that a future edit which "fixes"
one of the two datasets has to confront the other rather than quietly trading
it away.

What the residual actually is remains open and is recorded in STATUS.md.
Netzband & Dunn's own title points at a mechanism our pH term has no channel
for at all — the cerium OXIDATION STATE (Ce3+/Ce4+), which their paper varies
deliberately and which the `sti_ceria` pack carries as a fixed `ce3_fraction`.
A pH-dependent Ce3+ fraction would be a ceria-specific coupling, not a
universal second pH channel, and it needs its own evidence before it is built.
"""
from __future__ import annotations

import yaml

from cmp_sim.core.predictive_score import _measured, _predict_with_gate
from cmp_sim.core.validation import dataset_paths

DANDU = "dandu2009_sio2_ceria_ph_sweep"
NETZBAND = "netzband2020_thermal_oxide_ceria_ph"
ANIONIC = "cn109609035b_oxide_anionic_silica_ph"


def _doc(stem: str) -> dict:
    for path in dataset_paths():
        if path.stem == stem:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise AssertionError(f"dataset {stem} not found")


def _curve(stem: str) -> list[tuple[float, float]]:
    return sorted((r["overrides"]["slurry_ph"], _measured(r))
                  for r in _doc(stem)["conditions"] if _measured(r) is not None)


def _ratios(stem: str) -> list[tuple[float, float]]:
    """measured / predicted at each pH, with one fitted scale."""
    doc = _doc(stem)
    rows = [r for r in doc["conditions"] if _measured(r) is not None]
    phs, meas, pred = [], [], []
    for row in rows:
        value, _gate = _predict_with_gate(doc, row)
        if value is None:
            continue
        phs.append(row["overrides"]["slurry_ph"])
        meas.append(_measured(row))
        pred.append(value)
    scale = sum(m * p for m, p in zip(meas, pred)) / sum(p * p for p in pred)
    return sorted(zip(phs, [m / (scale * p) for m, p in zip(meas, pred)]))


# ---------------------------------------------------------------------------
# the two ceria datasets measure incompatible SHAPES
# ---------------------------------------------------------------------------

def test_the_two_ceria_datasets_share_a_pack():
    """If they ever stop sharing one, this whole contradiction dissolves and
    the tests below should be revisited rather than deleted."""
    assert _doc(DANDU)["pack"] == _doc(NETZBAND)["pack"] == "sti_ceria"


def test_dandu_is_a_bell_with_an_interior_maximum():
    curve = _curve(DANDU)
    peak_ph = max(curve, key=lambda t: t[1])[0]
    assert 3.5 <= peak_ph <= 5.5, curve
    assert curve[0][1] < 100 and curve[-1][1] < 1000, "both ends must be LOW"


def test_netzband_is_a_V_with_an_interior_minimum():
    curve = _curve(NETZBAND)
    trough_ph = min(curve, key=lambda t: t[1])[0]
    assert trough_ph == 6.0, curve
    # both ends sit well above the trough: that is the V
    assert curve[0][1] > 1.5 * min(v for _, v in curve)
    assert curve[-1][1] > 1.5 * min(v for _, v in curve)


def test_a_single_extra_channel_cannot_serve_both():
    """The falsification, stated as arithmetic rather than as an opinion.

    Netzband needs the model RAISED above pH 6; Dandu is already right there.
    """
    netz = dict(_ratios(NETZBAND))
    dandu = dict(_ratios(DANDU))

    # netzband2020 is under-predicted by >3x in the alkaline half
    assert netz[8.0] > 3.0 and netz[10.0] > 3.0, netz
    # dandu2009 is accurate in exactly that half, so raising it would break it
    assert 0.8 < dandu[8.0] < 1.25, dandu
    assert 0.8 < dandu[10.0] < 1.25, dandu


def test_the_anionic_residual_is_a_different_shape_again():
    """The third dataset's miss is a single point near the bottom of its
    range, not a rising alkaline limb — so it is not evidence for the same
    channel either."""
    ratios = dict(_ratios(ANIONIC))
    worst_ph = min(ratios, key=lambda p: ratios[p])
    assert worst_ph == 5.0, ratios
    assert ratios[6.0] > 0.9, "the pH 6 point is NOT the dominant residual"


def test_no_universal_second_ph_channel_was_added():
    """Guard against the fix this investigation rejected.

    If someone adds a generic rising-alkaline term to the shared pH response,
    dandu2009's alkaline agreement is the first thing that breaks — so assert
    it directly, in the place where the reasoning is written down.
    """
    dandu = dict(_ratios(DANDU))
    for ph in (8.0, 10.0):
        assert abs(dandu[ph] - 1.0) < 0.25, (
            "dandu2009's alkaline points moved; if a second pH channel was "
            "introduced, it must be justified against BOTH ceria datasets")
