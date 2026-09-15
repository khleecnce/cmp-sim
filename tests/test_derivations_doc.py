"""The derivations document must actually cite things.

Project requirement (c): "documented model derivations with citations". A
derivation without a source is a plausible-looking assertion — and this file is
where a reviewing engineer goes to decide whether to trust the model, so an
uncited equation there is worse than one in code.

These tests are deliberately crude: they check that citations exist and point at
resolvable identifiers, not that the physics is right. That judgement is the
owner's.
"""
import re
from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parents[1] / "docs" / "derivations.md"

#: A citation is a DOI, a patent number, a thesis/preprint handle, or a URL.
CITATION = re.compile(
    r"doi:10\.\d{4,9}/\S+"
    r"|US\s?\d{7}\s?[AB]\d?"
    r"|US\d{4}/\d{7}A\d"
    r"|eScholarship\s+\S+"
    r"|https?://\S+",
    re.IGNORECASE)

#: Sections deriving physics. Each must cite a primary source, because each
#: asserts an equation a reader could otherwise only take on trust.
MUST_CITE = ("P1", "P2", "P3", "P4", "P6")


def _text() -> str:
    assert DOC.exists(), f"{DOC} is missing"
    return DOC.read_text(encoding="utf-8")


def _sections(text: str):
    """Split on level-2 headings, returning (heading, body) pairs."""
    parts = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    out = []
    for part in parts:
        head, _, body = part.partition("\n")
        out.append((head.strip(), body))
    return out


def test_the_document_exists_and_is_substantial():
    text = _text()
    assert len(text.splitlines()) > 200, "derivations.md is too thin to be a record"


def test_every_physics_phase_cites_a_primary_source():
    """P1-P8 each assert an equation; each must say where it came from."""
    sections = _sections(_text())
    by_phase = {}
    for head, body in sections:
        m = re.match(r"(P\d)\b", head)
        if m:
            by_phase.setdefault(m.group(1), []).append(body)

    missing = []
    for phase in MUST_CITE:
        bodies = by_phase.get(phase)
        assert bodies, f"no section found for {phase}"
        if not any(CITATION.search(b) for b in bodies):
            missing.append(phase)
    assert not missing, (
        "these derivations assert equations without citing a source: "
        + ", ".join(missing))


def test_the_document_carries_a_reasonable_number_of_citations():
    """It once had 2 citations across 16 sections and 824 lines - the physics
    was sound but untraceable, which fails the documentation requirement."""
    found = CITATION.findall(_text())
    assert len(found) >= 10, (
        f"only {len(found)} citation(s) in the whole derivations document")


def test_dois_are_well_formed():
    """A malformed DOI is indistinguishable from an invented one. The Mariscal
    DOI was once written from memory as .../abb4b5 when the dataset file says
    .../ab89bc - wrong by a character and impossible to spot by eye."""
    for doi in re.findall(r"doi:(10\.\d{4,9}/[^\s,;)\]]+)", _text(), re.IGNORECASE):
        assert not doi.endswith("."), f"{doi} has a trailing full stop"
        assert len(doi) > 12, f"{doi} is too short to be a real DOI"


def test_citations_in_the_document_agree_with_the_data_files():
    """The derivations must not drift from the packs and datasets they describe.
    Any DOI claimed for a validation dataset has to appear in that dataset."""
    root = Path(__file__).resolve().parents[1]
    corpus = []
    for pattern in ("cmp_sim/data/**/*.yaml", "legacy/**/*.yaml"):
        for path in root.glob(pattern):
            try:
                corpus.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    haystack = "\n".join(corpus).lower()

    doc_dois = {
        d.lower().rstrip(".,;")
        for d in re.findall(r"doi:(10\.\d{4,9}/[^\s,;)\]]+)", _text(), re.IGNORECASE)
    }
    # Classic papers (Preston, Greenwood-Williamson, Luo-Dornfeld, Cook,
    # Kaufman, Stine) are cited in the document for provenance and need not
    # appear in a data file. Dataset DOIs must.
    dataset_dois = {d for d in doc_dois if "2162-8777" in d}
    for doi in dataset_dois:
        assert doi in haystack, (
            f"the document cites {doi} for a validation dataset, but no data "
            "file contains it - one of the two is wrong")


@pytest.mark.parametrize("phase", ["P5", "P7", "P8"])
def test_phases_without_a_primary_source_state_their_limits(phase):
    """P5, P7 and P8 are acknowledged proxies rather than derived laws. They
    need not cite a paper, but they must say what they cannot do, so nobody
    reads a proxy as a prediction."""
    bodies = [b for h, b in _sections(_text()) if h.startswith(phase)]
    assert bodies, f"no section found for {phase}"
    text = " ".join(bodies).lower()
    hedges = ("not predicted", "direction-only", "proxy", "never multiplied",
              "flagged", "reported", "cannot", "warn")
    assert any(h in text for h in hedges), (
        f"{phase} neither cites a source nor states its limits")
