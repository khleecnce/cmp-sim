"""<= 10 % is above the ceiling of any shared-constant model on this corpus.

STATUS.md's completion criterion allows <= 15 % instead of <= 10 % only if the
run first writes down WHAT MAKES THE FLOOR, in numbers rather than in the word
"hard". Limits 14 and 15 supplied the mechanism (sign-dispersed per-dataset
exponents; the one surviving axis rested on inadmissible evidence). Limit 16
supplies the bound, and these tests pin it:

  Granting EVERY dataset a free exponent on its own best axis -- an oracle no
  physical model can attain, because a model shares its constants -- moves the
  corpus median only 18.6 % -> 11.9 %, and the count at or below 10 % only
  14 -> 20 of 46.

They also pin the finding that reversed the intuition behind the measurement:
the 145-point block that NO axis owns is the part the model gets RIGHT
(median 11.2 % vs 23.9 % for the owned block), so "no axis explains it" is not
"the hard part", and only 18 points of it are unexplained by a named cause.

Finally they pin the honesty boundary: reproducibility is unmeasured on 12 of
the 17 unowned datasets, so the claim is one-sided -- <= 10 % is unreachable, but
whether 15 % sits AT the floor is not yet decidable.
"""
from __future__ import annotations

import functools

from tools import unowned_error_partition as part


@functools.lru_cache(maxsize=1)
def _causes():
    return tuple(part.partition())


@functools.lru_cache(maxsize=1)
def _bound():
    return part.corpus_bound()


@functools.lru_cache(maxsize=1)
def _contrast():
    return part.contrast()


def test_ten_percent_is_unreachable_even_with_a_free_exponent_per_dataset():
    """The load-bearing assertion for the <= 15 % completion criterion.

    The grant is deliberately absurd in the model's favour: a different exponent
    per dataset, fitted on the scored rows, on whichever axis helps most. If the
    median under that grant is still above 10 %, then no shared-constant physics
    reaches 10 % on this corpus, and the criterion is a property of the evidence
    rather than of the effort spent.
    """
    b = _bound()
    assert b["datasets"] >= 40, f"corpus shrank to {b['datasets']} datasets"
    assert b["median_if_every_oracle_granted"] > 10.0, (
        "the unreachable oracle now reaches <= 10 % "
        f"({b['median_if_every_oracle_granted']:.1f} %). That would mean a real "
        "law might reach it too: limit 16 must be rewritten and the <= 15 % "
        "allowance re-argued, not this test relaxed.")
    assert b["median_if_every_oracle_granted"] < b["median_now"], (
        "granting oracles must not make the median worse; if it does, the "
        "residual_after bookkeeping in axis_error_census is wrong")


def test_the_oracle_grant_converts_only_a_handful_of_datasets():
    """Size the grant in datasets too, so the median cannot carry the claim alone.

    A median can move by re-ranking one dataset (pinned by test in the 11th
    run). Counting how many datasets cross the 10 % line is immune to that.
    """
    b = _bound()
    assert b["under_ten_granted"] - b["under_ten_now"] <= 12, (
        f"the grant now converts {b['under_ten_granted'] - b['under_ten_now']} "
        "datasets to <= 10 %; limit 16 claims it converts few (14 -> 20) and "
        "must be re-measured")
    assert b["under_ten_granted"] < b["datasets"] * 0.6, (
        "a majority of datasets would be under 10 % with the grant; that is a "
        "different corpus from the one limit 16 describes")


def test_the_unowned_block_is_the_part_the_model_gets_RIGHT():
    """The intuition-reversing result, pinned because it redirects future work.

    If this ever flips, the 42.4 % unowned block becomes the place to dig and
    limit 16's reading changes completely.
    """
    c = _contrast()
    assert c["unowned"]["median_shape"] < c["owned"]["median_shape"], (
        f"unowned median {c['unowned']['median_shape']:.1f} % is no longer "
        f"better than owned {c['owned']['median_shape']:.1f} %; limit 16's "
        "central claim must be re-argued")
    assert c["unowned"]["share_of_weighted_error"] < 40.0, (
        "the unowned block now carries most of the corpus' weighted error; it "
        "would then be the next target, contradicting limit 16")


def test_the_unowned_block_holds_almost_no_unexplained_error():
    """There is no reservoir for new physics to drain.

    Every unowned dataset is accounted for by a named cause -- unmeasured floor,
    absolute-scale failure, or losing to the mean -- except one.
    """
    s = part.summary(list(_causes()))
    assert s["unexplained_share"] < 25.0, (
        f"{s['unexplained_share']:.1f} % of the unowned block is now "
        "unexplained by any named cause. That IS a target for new physics and "
        "belongs in STATUS.md's NEXT.")
    assert s["points"] > 100, f"the unowned block shrank to {s['points']} points"


def test_every_unowned_dataset_is_assigned_exactly_one_named_cause():
    """The partition must be total and disjoint, or its shares mean nothing."""
    causes = _causes()
    assert causes
    for c in causes:
        assert c.bucket in part.BUCKETS, f"{c.dataset} has bucket {c.bucket!r}"
    s = part.summary(list(causes))
    assert sum(v["points"] for v in s["buckets"].values()) == s["points"], (
        "bucket point counts do not sum to the block: the partition is not "
        "disjoint or not total")


def test_the_claim_stays_one_sided_while_most_floors_are_unmeasured():
    """The honesty boundary of limit 16, enforced.

    Twelve of seventeen unowned datasets repeat no condition, so their own
    reproducibility is UNKNOWN. Unknown is not zero. Limit 16 may therefore
    claim '<= 10 % is unreachable' but must NOT claim '15 % is the floor'.
    """
    causes = _causes()
    unmeasured = [c for c in causes if c.scatter is None]
    assert len(unmeasured) > len(causes) / 2, (
        "most unowned datasets now have a measured replicate floor; limit 16's "
        "one-sided caveat can be tightened into a two-sided claim -- do that "
        "deliberately in the document")
    text = (part.__doc__ or "") + open(
        "docs/limits.md", encoding="utf-8").read()
    assert "unknown is not zero" in text.lower(), (
        "limit 16 must keep its statement that an unmeasured floor is not a "
        "floor of zero")


def test_no_dataset_is_at_its_replicate_floor_in_the_unowned_block():
    """A measured fact worth pinning: the unowned block is not noise-limited.

    If a dataset here were at its own floor it would be irreducible, which is a
    stronger statement than 'unexplained'. None is -- the block's low error
    comes from the model being right, not from the data being noisy.
    """
    s = part.summary(list(_causes()))
    assert s["buckets"].get("at_noise_floor", {"points": 0})["points"] == 0, (
        "an unowned dataset is now at its replicate floor; that is good news "
        "and changes limit 16's partition table")


def test_the_partition_modifies_no_pack():
    import inspect
    source = inspect.getsource(part)
    for forbidden in ("write_text", "safe_dump", "yaml.dump"):
        assert forbidden not in source, (
            f"tools/unowned_error_partition.py contains {forbidden!r}: a "
            "measurement tool must never write a pack")


def test_the_scale_failures_are_reported_not_fitted():
    """Limit 16 rejects per-dataset Kp corrections for the 3 scale failures."""
    from cmp_sim.core.params import available_packs, load_pack
    scale_failures = [c.dataset for c in _causes() if c.bucket == "scale_failure"]
    assert scale_failures, "the scale-failure bucket is empty; re-argue limit 16"
    for name in available_packs():
        params = getattr(load_pack(name), "params", {}) or {}
        for key in params:
            for dataset in scale_failures:
                stem = dataset.split("_")[0]
                assert stem not in str(key), (
                    f"pack {name} has a parameter {key!r} named after the "
                    f"scale-failing dataset {dataset}: limit 16 rejects "
                    "per-dataset calibration constants")
