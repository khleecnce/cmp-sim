"""What the silica pack splits buy — and what they do not.

The parameter-evidence inventory ranked `oxide_silica_anionic` (11% exercised,
7 rows, one axis) and `oxide_silica_aminosilane` (16%, 22 rows, two axes) as the
two thinnest packs in the corpus. Both are silica-on-oxide variants that exist to
carry a different pH optimum, which raises a fair question: are they justified as
separate packs at all, or is a 62-parameter file implying an independence the
evidence cannot support?

BOTH ANSWERS ARE YES AND NO, AND THE DISTINCTION IS THE POINT.

The split is decisively justified. Re-scoring each variant's dataset with the
PARENT `oxide_silica` pack instead:

    cn109609035b_oxide_anionic_silica_ph    32.1%  ->   94.7%   (+62.5 points)
    us9422456b2_teos_silica_ph_pressure     25.3%  ->  126.6%  (+101.3 points)

Merging these packs would roughly triple and quintuple their errors. The pH
optimum really does follow the abrasive's surface charge, exactly as the earlier
finding claimed, and one bell centred at pH 11 cannot also serve pH 2 and 4.9.

But the split buys ONLY that. Diffing each variant against its parent, parameter
by parameter:

    oxide_silica_anionic        6 of 124 parameters differ — all six are pH
    oxide_silica_aminosilane    7 of 125 parameters differ — all seven are pH

Every other constant — Preston coefficient, pad mechanics, abrasive exponents,
conditioning, pattern terms — is inherited unchanged from `oxide_silica`. So a
reader opening `oxide_silica_anionic.yaml` and seeing a full parameter set could
reasonably conclude that an anionic-silica slurry had been characterised
independently. It has not. It has been characterised in pH, on seven rows, and
borrows everything else.

That is a defensible design — it is exactly what pack inheritance is for — but it
must be stated, because the failure mode is silent: the pack looks complete.

A NOTE ON HOW THIS WAS MEASURED

The first attempt compared packs with `pack.get(key)`, which returned None for
every key and made the variants look IDENTICAL to their parent (0 and 1
differences). The correct accessor is `pack.param(key)`. A diff that reports "no
differences" between two packs that demonstrably score differently is a broken
diff, not a finding — hence `test_the_diff_uses_the_accessor_that_works`.
"""
from __future__ import annotations

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import score_dataset
from cmp_sim.core.validation import dataset_paths

PARENT = "oxide_silica"
VARIANTS = {
    "oxide_silica_anionic": "cn109609035b_oxide_anionic_silica_ph",
    "oxide_silica_aminosilane": "us9422456b2_teos_silica_ph_pressure",
}


def _path(stem):
    return next(p for p in dataset_paths() if p.stem == stem)


def _value(pack, key):
    try:
        param = pack.param(key)
    except Exception:
        return "<absent>"
    return getattr(param, "value", param)


def _differences(variant_name):
    parent, variant = load_pack(PARENT), load_pack(variant_name)
    keys = sorted(set(parent.params) | set(variant.params))
    return [k for k in keys if _value(parent, k) != _value(variant, k)]


def test_the_diff_uses_the_accessor_that_works():
    """pack.get() silently returns None; pack.param() is the real accessor.

    Guards the mistake that made this audit briefly report two packs as
    identical when they score 62 and 101 points apart.
    """
    pack = load_pack(PARENT)
    assert _value(pack, "ph_peak") == 11.0, (
        "the accessor used by this audit stopped returning values; a diff built "
        "on it would report spurious 'no differences'")


def test_every_difference_between_variant_and_parent_is_ph():
    for variant in VARIANTS:
        diffs = _differences(variant)
        assert diffs, f"{variant} no longer differs from its parent at all"
        non_ph = [k for k in diffs if not k.startswith("ph_")]
        assert not non_ph, (
            f"{variant} now differs from {PARENT} in non-pH parameters "
            f"{non_ph}; this file's claim that the split is pH-only must be "
            "revised, and so must the pack's own note")


def test_the_variants_inherit_almost_everything():
    for variant in VARIANTS:
        pack = load_pack(variant)
        differing = len(_differences(variant))
        total = len(pack.params)
        assert differing / total < 0.10, (
            f"{variant}: {differing}/{total} parameters differ — the 'inherits "
            "almost everything' framing no longer holds")


def test_merging_a_variant_into_the_parent_would_be_much_worse():
    """The split is justified by measurement, not by taxonomy."""
    for variant, stem in VARIANTS.items():
        path = _path(stem)
        original = path.read_text(encoding="utf-8")
        own = score_dataset(path)
        try:
            path.write_text(
                original.replace(f"pack: {variant}", f"pack: {PARENT}"),
                encoding="utf-8")
            merged = score_dataset(path)
        finally:
            path.write_text(original, encoding="utf-8")

        assert own.shape_mape is not None and merged.shape_mape is not None
        assert merged.shape_mape > own.shape_mape * 2.5, (
            f"{stem}: scoring with the parent pack gives "
            f"{merged.shape_mape:.1f}% vs {own.shape_mape:.1f}% — if that gap "
            "has closed, the separate pack may no longer be earning its keep")


def test_the_restore_left_the_datasets_untouched():
    """The measurement above rewrites files; prove it put them back."""
    for variant, stem in VARIANTS.items():
        doc = yaml.safe_load(_path(stem).read_text(encoding="utf-8"))
        assert doc["pack"] == variant, (
            f"{stem} was left pointing at the wrong pack by a failed restore")


def test_the_packs_say_what_the_split_buys():
    """A pack that looks complete must say which part of it is evidenced."""
    from pathlib import Path

    import cmp_sim
    for variant in VARIANTS:
        text = (Path(cmp_sim.__file__).parent / "data" / "params"
                / f"{variant}.yaml").read_text(encoding="utf-8")
        assert "inherit" in text.lower(), (
            f"{variant}.yaml must state that everything except its pH "
            "constants is inherited from oxide_silica")
