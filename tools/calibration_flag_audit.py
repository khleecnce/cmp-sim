"""Does any pack constant cite, as its SOURCE, a dataset that swears it was
not used for calibration? (36th run)

Why this probe exists
---------------------
`used_for_calibration: true` is the repository's only guard against grading a
model on its own answer key. Every probe that asks "is this evidence
admissible?" -- `absolute_scale_audit` (S4), `ce3_residual_probe`,
`oxidizer_order_probe` -- reads that ONE boolean, and every one of them trusts
the dataset's self-declaration.

Nothing checks the declaration against the packs.

A pack constant records WHERE it came from in its `source:` string. When that
string names a dataset in the scored corpus, the constant was fitted on that
dataset, and the dataset is therefore calibration evidence whatever its own
header says. If the header says `false`, the corpus is scoring a constant
against the very rows that produced it, and every admissibility filter in the
repository is waving it through.

This is not hypothetical. `sic_ceria_h2o2.abrasive_size_exponent` reads

    source: su2011_sic_alumina_size_sweep (+0.24),
            wei2026_sic_silica_size_sweep (+0.10)

and both of those files declare `used_for_calibration: false`. They are also
the 3rd and 5th best scores in the whole corpus (3.2 % and 4.4 %).

WHAT THIS PROBE DOES AND DOES NOT CLAIM
---------------------------------------
It MEASURES ONLY. It does not edit a pack or a dataset. A citation is not
automatically a violation: a pack may cite a dataset for a quantity that
dataset does not vary (e.g. citing a paper's stated pH while scoring its
pressure sweep). So the probe separates two cases and reports both:

  IMPLICATED   the pack constant's source names this dataset, AND the dataset
               varies an axis the constant governs -> the score is circular
  CITED-ONLY   the source names the dataset but the dataset does not sweep the
               axis that constant controls -> a provenance note, not a fit

The axis mapping is derived from the scorer's own `axes` list per dataset, so
it cannot drift away from what is actually being scored.

Usage: ``python tools/calibration_flag_audit.py`` (inside ``.venv``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

import yaml

from cmp_sim.core.params import available_packs, load_pack
from cmp_sim.core.predictive_score import score_all
from cmp_sim.core.validation import dataset_paths

#: Which swept axis names (as the scorer reports them) each pack-constant
#: family governs. Keyed by a substring of the constant name so a new
#: `abrasive_size_exp_below_peak` is covered without editing this table.
CONSTANT_AXES: Dict[str, Set[str]] = {
    "abrasive_size": {"abrasive_size_nm", "abrasive_d50_nm", "abrasive_d99_nm"},
    "abrasive_conc": {"abrasive_wt_pct"},
    "abrasive_ref_wt": {"abrasive_wt_pct"},
    "ph_": {"slurry_ph"},
    "oxidizer": {"oxidizer_wt_pct", "h2o2_vol_pct"},
    "h2o2": {"oxidizer_wt_pct", "h2o2_vol_pct"},
    "inhibitor": {"inhibitor_ppm", "inhibitor_mM"},
    "chelator": {"chelator_M"},
    "promoter": {"promoter_M"},
    "kp_m_per_pa": {"pressure", "velocity"},
    "pressure": {"pressure"},
    "velocity": {"velocity"},
    "dispersant": {"dispersant_wt_pct"},
}


def _axes_for(constant: str) -> Set[str]:
    out: Set[str] = set()
    for frag, axes in CONSTANT_AXES.items():
        if frag in constant:
            out |= axes
    return out


@dataclass
class Citation:
    pack: str
    constant: str
    dataset: str
    declared_calibration: bool
    in_source_field: bool            # named by `source:`, not merely by `note:`
    has_value: bool                  # a live constant, not a withdrawn null
    numeric: bool                    # a fitted number, not a documentation flag
    own_pack: bool                   # this IS the pack that predicts the block
    dataset_axes: Set[str] = field(default_factory=set)
    shape: float | None = None

    @property
    def governed(self) -> Set[str]:
        return _axes_for(self.constant) & self.dataset_axes

    @property
    def implicated(self) -> bool:
        """The constant's VALUE was fitted on an axis this dataset sweeps.

        Five conditions, and dropping any one of them produces a false
        positive that this repository actually contains:

        * ``in_source_field`` -- a `note:` may merely cite a dataset as
          context or as the refutation that RETIRED the constant. Only
          `source:` asserts "this value came from here".
        * ``has_value`` -- a withdrawn constant (value ``null``) changes no
          prediction, so scoring its citing dataset is not circular.
        * ``numeric`` -- several keys here are DOCUMENTATION FLAGS whose value
          is a bool or a sentence (`ph_response_is_unimodal_but_this_system_
          is_not`, `oxidizer_peak_is_pressure_dependent_unresolved`). They
          record a known limitation rather than carry a fitted degree of
          freedom, so citing the dataset that revealed the limitation is
          honesty, not circularity.
        * ``own_pack`` -- the decisive one, and the one this probe got wrong
          first. A dataset is predicted by ONE pack. When a DIFFERENT pack
          cites it, that citation cannot touch this block's score: the
          constant it fed is never evaluated here. `tw202115224a` is cited by
          `oxide_silica` and `cu_alkaline_benzenesulfonic` while being scored
          under `cu_h2o2_bta`, whose size exponent comes from Lai 2001
          instead -- cross-pack evidence reuse, which is legitimate, not self
          grading. Counting it would have condemned a clean block.
        * ``governed`` -- a pack may cite a paper for a quantity that paper
          does not vary; then the score does not touch the fit.
        """
        return (bool(self.governed)
                and self.in_source_field
                and self.has_value
                and self.numeric
                and self.own_pack
                and not self.declared_calibration)


def _dataset_docs() -> Dict[str, dict]:
    docs = {}
    for path in dataset_paths():
        docs[Path(path).stem] = yaml.safe_load(
            Path(path).read_text(encoding="utf-8")) or {}
    return docs


def collect() -> List[Citation]:
    docs = _dataset_docs()
    scored = {s.dataset: s for s in score_all()}
    # Longest stems first so `us9422456b2_teos_silica_ph_pressure` is not
    # matched by a shorter sibling's prefix.
    stems = sorted(docs, key=len, reverse=True)

    out: List[Citation] = []
    for pack_name in sorted(available_packs()):
        try:
            pack = load_pack(pack_name)
        except Exception:  # noqa: BLE001
            continue
        for key, param in sorted(pack.params.items()):
            # Only constants this pack OWNS -- an inherited citation belongs to
            # the parent and would otherwise be reported once per child.
            if getattr(param, "owner", pack_name) != pack_name:
                continue
            source = str(getattr(param, "source", "") or "")
            text = source + " " + str(getattr(param, "note", "") or "")
            if not text.strip():
                continue
            seen: Set[str] = set()
            for stem in stems:
                if stem in seen:
                    continue
                if not re.search(re.escape(stem), text):
                    continue
                seen.add(stem)
                doc = docs[stem]
                score = scored.get(stem)
                out.append(Citation(
                    pack=pack_name,
                    constant=key,
                    dataset=stem,
                    declared_calibration=bool(doc.get("used_for_calibration")),
                    in_source_field=bool(re.search(re.escape(stem), source)),
                    has_value=getattr(param, "value", None) is not None,
                    numeric=isinstance(getattr(param, "value", None),
                                       (int, float))
                    and not isinstance(getattr(param, "value", None), bool),
                    own_pack=str(doc.get("pack") or "") == pack_name,
                    dataset_axes=set(getattr(score, "axes", []) or []),
                    shape=getattr(score, "shape_mape", None),
                ))
    return out


def report() -> str:
    cites = collect()
    implicated = [c for c in cites if c.implicated]
    note_only = [c for c in cites
                 if not c.declared_calibration and c.governed
                 and c.has_value and not c.in_source_field]
    withdrawn = [c for c in cites
                 if not c.declared_calibration and c.governed
                 and not c.has_value]
    flags = [c for c in cites
             if not c.declared_calibration and c.governed
             and c.has_value and c.in_source_field and not c.numeric]
    foreign = [c for c in cites
               if not c.declared_calibration and c.governed and c.has_value
               and c.in_source_field and c.numeric and not c.own_pack]
    cited_only = [c for c in cites
                  if not c.declared_calibration and not c.governed]
    honest = [c for c in cites if c.declared_calibration]

    lines = ["pack constants citing a scored dataset : %d" % len(cites)]
    lines.append("  dataset already admits calibration   : %d" % len(honest))
    lines.append("  IMPLICATED (source: + live + swept)  : %d" % len(implicated))
    lines.append("  named by note: only, not by source:  : %d" % len(note_only))
    lines.append("  constant withdrawn (value null)      : %d" % len(withdrawn))
    lines.append("  non-numeric (flag / declared window) : %d" % len(flags))
    lines.append("  cited by a pack that is not this     : %d" % len(foreign))
    lines.append("  cited only, axis not swept           : %d" % len(cited_only))

    if foreign:
        lines.append("")
        lines.append("CROSS-PACK -- legitimate evidence reuse, NOT self-grading")
        lines.append("  (the citing pack does not predict this block)")
        for c in sorted(foreign, key=lambda c: c.dataset):
            lines.append("  %-42s fed %s.%s"
                         % (c.dataset, c.pack, c.constant))

    if implicated:
        lines.append("")
        lines.append("IMPLICATED -- the score is circular: the constant came "
                     "from these rows")
        for c in sorted(implicated, key=lambda c: (c.shape is None, c.shape)):
            lines.append("  %-30s %-34s  shape %s  axes %s"
                         % (c.dataset, "%s.%s" % (c.pack, c.constant),
                            "  --  " if c.shape is None else "%5.1f%%" % c.shape,
                            ",".join(sorted(c.governed))))

    if cited_only:
        lines.append("")
        lines.append("CITED ONLY -- provenance, not a fit (axis not swept here)")
        for c in sorted(cited_only, key=lambda c: c.dataset):
            lines.append("  %-30s %s.%s" % (c.dataset, c.pack, c.constant))

    lines.extend(headline_effect(cites))
    return "\n".join(lines)


def headline_effect(cites: List[Citation]) -> List[str]:
    """What does the corpus median read once self-graded blocks are removed?

    The repository's standing rule is "never drop a dataset to LOWER the
    median". This measurement runs in the opposite direction -- it removes
    blocks the model was FITTED on, which can only hurt the headline -- so it
    is the one exclusion that rule permits and, in fact, demands.

    The bar is quoted on the same upper-median convention as the README
    (`sorted(e)[n//2]`), because `statistics.median` reads ~1.7 points lower
    on this corpus and the two have been confused before.
    """
    tainted = {c.dataset for c in cites
               if c.implicated or c.declared_calibration}
    errs_all, errs_clean = [], []
    for s in score_all():
        if s.shape_mape is None:
            continue
        errs_all.append(s.shape_mape)
        if s.dataset not in tainted:
            errs_clean.append(s.shape_mape)
    out = ["", "HEADLINE -- upper median sorted(e)[n//2] (README convention)"]
    for label, errs in (("as published (every scored block)", errs_all),
                        ("held out (fitted blocks removed)", errs_clean)):
        errs = sorted(errs)
        out.append("  %-34s n=%2d  median=%.1f%%"
                   % (label, len(errs), errs[len(errs) // 2]))
    out.append("  blocks removed: %d (%d self-graded, the rest declared)"
               % (len(errs_all) - len(errs_clean),
                  len({c.dataset for c in cites if c.implicated})))
    return out


if __name__ == "__main__":  # pragma: no cover
    print(report())
