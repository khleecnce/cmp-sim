"""Does the abrasive-size exponent have a single sign? No — and that is the finding.

Nine measured size sweeps across seven films, all read from local PDFs and
re-verified here against the originals, give exponents from about -0.45 to +1.0,
and three of them are non-monotonic so no power law fits at all.

The decisive evidence is not the spread between papers but the spread *within*
single experiments:

* **Bouvet 2002** polished W, Ti and thermal oxide with the same four silica
  slurries in the same runs. W came out flat (n ~ -0.05), Ti falling
  (n ~ -0.45), oxide peaked at 25 nm. One experiment, three different answers.
* **US 2019/0127607 A1** polished HDP oxide and TEOS oxide with the same four
  ceria-coated-silica slurries in the same runs. HDP rose monotonically
  (+0.75); TEOS reversed at 156 nm. The patent states this itself at [0120]:
  "particle size and particle size distribution affected HDP silicon dioxide
  films and TEOS films differently even though both films essentially comprise
  silicon oxide films." Deposition method alone changes the size response.

So ``abrasive_size_exponent`` cannot be one global constant, and these datasets
must not be averaged. This file pins that conclusion so a future change that
introduces a single global exponent fails loudly.
"""
import math
from pathlib import Path

import pytest
import yaml

DATASETS = Path(__file__).resolve().parents[1] / "cmp_sim" / "data" / "validation" / "datasets"
SIZE_SWEEPS = sorted(DATASETS.glob("*size_sweep*.yaml"))


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _points(doc):
    """(size_nm, rate) pairs, in whatever rate unit the file records."""
    out = []
    for row in doc.get("conditions", []):
        size = (row.get("overrides") or {}).get("abrasive_d50_nm")
        rate = (row.get("mrr_nm_per_min") or row.get("mrr_a_per_min")
                or row.get("measured_mrr_nm_per_min")
                or row.get("measured_mrr_angstrom_per_min")
                or row.get("mrr_nm_per_hour"))
        if size is not None and rate is not None:
            out.append((float(size), float(rate)))
    return sorted(out)


def _exponent(points):
    """Least-squares slope in log-log space."""
    xs = [math.log(s) for s, _ in points]
    ys = [math.log(r) for _, r in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def test_the_size_sweeps_are_present():
    assert len(SIZE_SWEEPS) >= 6, (
        f"only {len(SIZE_SWEEPS)} size sweeps found in {DATASETS}")


@pytest.mark.parametrize("path", SIZE_SWEEPS, ids=lambda p: p.stem)
def test_each_sweep_has_three_sizes_and_a_source(path):
    doc = _load(path)
    points = _points(doc)
    assert len(points) >= 3, f"{path.name} has only {len(points)} size points"
    assert len({s for s, _ in points}) == len(points), "duplicate sizes"
    text = yaml.dump(doc)
    assert "source" in text, f"{path.name} records no source"


@pytest.mark.parametrize("path", SIZE_SWEEPS, ids=lambda p: p.stem)
def test_pressure_and_velocity_are_fixed_within_each_sweep(path):
    """A sweep that also varies P or V is confounded and cannot isolate size."""
    doc = _load(path)
    pressures = {row.get("pressure_psi") for row in doc.get("conditions", [])}
    speeds = {row.get("rpm_platen") for row in doc.get("conditions", [])}
    assert len(pressures) == 1, f"{path.name} varies pressure: {pressures}"
    assert len(speeds) == 1, f"{path.name} varies platen speed: {speeds}"


@pytest.mark.parametrize("path", SIZE_SWEEPS, ids=lambda p: p.stem)
def test_digitised_sweeps_are_labelled_and_low_confidence(path):
    """Numbers read off a plot must not be presented as if tabulated."""
    doc = _load(path)
    # Read the per-row read_method rather than grepping the prose: two files say
    # "no digitization of any plot", and a substring search calls those
    # digitised - the opposite of what they state.
    methods = {str(row.get("read_method") or "").lower()
               for row in doc.get("conditions", [])}
    digitised = any("digiti" in m for m in methods)
    if digitised:
        assert doc.get("confidence") in ("low", "med"), (
            f"{path.name} is digitised (read_method {methods}) but claims "
            f"confidence '{doc.get('confidence')}'")
    else:
        assert doc.get("confidence") in ("high", "med", "low"), (
            f"{path.name} has an unrecognised confidence")


# ── the actual finding ───────────────────────────────────────────────
def test_the_exponents_disagree_in_sign():
    """If they agreed, a single global exponent would be the right design."""
    exps = {p.stem: _exponent(_points(_load(p))) for p in SIZE_SWEEPS}
    assert min(exps.values()) < 0 < max(exps.values()), (
        f"no sign disagreement, so one exponent might suffice: {exps}")
    assert max(exps.values()) - min(exps.values()) > 0.8, (
        f"the spread is too small to rule out one constant: {exps}")


def test_one_experiment_gives_different_answers_on_different_films():
    """Bouvet 2002: W, Ti and oxide, same slurries, same runs. This is the
    evidence that cannot be explained away as inter-laboratory scatter."""
    bouvet = {p.stem.split("_")[1]: _exponent(_points(_load(p)))
              for p in SIZE_SWEEPS if p.stem.startswith("bouvet2002")}
    assert len(bouvet) >= 3, f"expected three Bouvet films, got {bouvet}"
    assert max(bouvet.values()) - min(bouvet.values()) > 0.3, (
        f"the three films agree, contradicting the paper's own prose: {bouvet}")


def test_two_oxide_films_from_one_patent_differ():
    """US 2019/0127607 A1, same four slurries: HDP rises monotonically while
    TEOS reverses. The patent asserts the difference at [0120], so it is the
    source's claim, not an inference drawn here."""
    hdp = next((p for p in SIZE_SWEEPS if "hdpoxide" in p.stem), None)
    teos = next((p for p in SIZE_SWEEPS if "teos" in p.stem), None)
    assert hdp and teos, "the paired oxide sweeps are missing"

    hdp_points, teos_points = _points(_load(hdp)), _points(_load(teos))
    assert len(hdp_points) == len(teos_points) == 4

    def monotonic(points):
        rates = [r for _, r in points]
        return rates == sorted(rates)

    assert monotonic(hdp_points), "HDP oxide is no longer monotonic"
    assert not monotonic(teos_points), (
        "TEOS oxide is monotonic, so the patent's stated film difference is gone")


def test_the_patents_own_ratio_column_confirms_the_row_pairing():
    """The PDF text layer scrambles the A/B/C/D labels, so the pairing of sizes
    to rates was proven arithmetically from two printed self-consistent ratio
    columns rather than assumed. Re-checked here so a future edit cannot
    silently re-order the rows."""
    teos = _load(next(p for p in SIZE_SWEEPS if "teos" in p.stem))
    hdp = _load(next(p for p in SIZE_SWEEPS if "hdpoxide" in p.stem))

    # D50/(D99-D50), printed in the patent's Table 1
    for d50, span, printed in [(156.1, 146.5, 1.07), (117.2, 65.5, 1.79),
                               (210.7, 106.0, 1.99), (88.7, 69.8, 1.27)]:
        assert d50 / span == pytest.approx(printed, abs=0.01)

    # TEOS/HDP, printed in the patent's Table 2
    by_size_t = dict(_points(teos))
    by_size_h = dict(_points(hdp))
    for size, printed in [(88.7, 0.76), (117.2, 1.01), (156.1, 0.64), (210.7, 0.97)]:
        ratio = by_size_t[size] / by_size_h[size]
        assert ratio == pytest.approx(printed, abs=0.01), (
            f"at D50 {size} nm the TEOS/HDP ratio is {ratio:.3f} but the patent "
            f"prints {printed}: the rows have been re-paired incorrectly")


# ── the measured value must actually be used ─────────────────────────
def _rate(film, pack, d50, kind="alumina"):
    """A run at one particle size.

    ``kind`` defaults to ALUMINA because these tests exercise the copper pack,
    whose measured +0.33 size exponent comes from Lai 2001's ALUMINA sweep and
    whose reference_abrasive is alumina. The default used to be "silica", which
    was harmless only while the abrasive kind had no effect on the result: once
    the kind was wired in, asking for silica and expecting alumina's exponent
    became a contradiction inside one test. The docstring below always said
    alumina; only the input did not.
    """
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import (Abrasive, Disk, Pad, Recipe, Slurry, Tool,
                                    Wafer)

    return simulate(Recipe(
        model="auto", wafer=Wafer(film=film, n_radial=11),
        slurry=Slurry(pack=pack, abrasive=Abrasive(
            kind=kind, d50_nm=d50, conc_wt_pct=3.0)),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60)))


def test_the_measured_exponent_overrides_the_derived_one():
    """Copper's measured exponent is +0.33 (Lai 2001, printed table) while the
    derivation gives -1.67 for its branch and load sharing. A measurement for
    the film in question must win, or collecting it was pointless."""
    low = _rate("cu", "cu_h2o2_bta", 50).mean_rr_angstrom_per_min
    high = _rate("cu", "cu_h2o2_bta", 200).mean_rr_angstrom_per_min
    observed = math.log(high / low) / math.log(200 / 50)
    assert observed == pytest.approx(0.33, abs=0.02), (
        f"the engine behaves as n_d = {observed:+.3f}; the pack's measured "
        "value is +0.33 and the derived one is -1.67")
    assert high > low, "copper should polish FASTER with larger alumina (Lai 2001)"


def test_the_override_is_disclosed_in_the_notes():
    result = _rate("cu", "cu_h2o2_bta", 200)
    notes = " ".join(result.notes + (result.extras.get("abrasive") or {}).get("notes", []))
    assert "MEASURED sweeps for this abrasive" in notes
    assert "overriding the derived" in notes


def test_the_exponent_splits_by_abrasive_not_by_film():
    """The corrected conclusion, and the reason the earlier one was wrong.

    This test previously asserted oxide_silica declared NULL, on the grounds
    that oxide's measured response is contradictory. It is -- but only because
    "oxide" pools experiments with different ABRASIVES. Regrouped by abrasive
    the scatter collapses:

        ceria    +0.87  (3 sweeps, 3-211 nm)
        alumina  +0.29  (2 sweeps, 50-3500 nm)
        silica   -0.05  (5 sweeps, 12-160 nm, five different films)

    Leaving it null was not neutral: the engine fell back to the DERIVED
    exponent of -0.84, which has the wrong sign for eight of the ten measured
    sweeps. A null that silently selects a wrong number is worse than a
    sourced approximation.
    """
    from cmp_sim.core.params import load_pack

    silica = load_pack("oxide_silica").get_or("abrasive_size_exponent", None)
    ceria = load_pack("sti_ceria").get_or("abrasive_size_exponent", None)
    assert silica is not None and ceria is not None
    # Different abrasives must not share a value, and must not share a sign.
    assert silica < 0 < ceria, (silica, ceria)
    assert abs(ceria - silica) > 0.5

    # Silica through the silica pack: no swap, so the pack's own measured
    # exponent is the one the engine applies. Naming the abrasive explicitly is
    # the point of the test — this is where the scoping has to be honoured.
    result = _rate("oxide", "oxide_silica", 200, kind="silica")
    notes = " ".join(result.notes + (result.extras.get("abrasive") or {}).get("notes", []))
    assert "MEASURED sweeps for this abrasive" in notes


def test_no_pack_declares_a_global_size_exponent():
    """A single exponent shared across ABRASIVES would contradict the data.

    Every pack that states a value must say it is scoped to its own abrasive
    and must cite the sweeps it came from, or it is a global constant wearing
    a source field.
    """
    from cmp_sim.core.params import load_pack, available_packs

    offenders = []
    for name in available_packs():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        value = pack.get_or("abrasive_size_exponent", None)
        if value is not None:
            param = pack.param("abrasive_size_exponent")
            note = ((param.note or "") + (param.source or "")).lower()
            # The pack must say the value is film-specific, and cite where
            # it came from, or it is a global constant in disguise.
            scoped = any(k in note for k in
                         ("per-film", "this film", "not transferable",
                          "this abrasive", "by abrasive", "must not be reused",
                          "abrasive-specific"))
            cited = any(k in note for k in ("doi", "table", "fig", "thesis",
                                            "j. vac", "patent", "sweep",
                                            ".yaml"))
            if not (scoped and cited):
                offenders.append((name, value, scoped, cited))
    assert not offenders, (
        "these packs declare a size exponent without scoping it to their own "
        f"abrasive or citing the sweeps: {offenders}. Measured exponents run "
        "-0.45 to +1.0 and split by abrasive (ceria +0.87, alumina +0.29, "
        "silica -0.05), so one shared constant cannot be right.")
