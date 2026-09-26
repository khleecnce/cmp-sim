"""Search the corpus's own source PDFs for STATED reproducibility.

The measured noise floor (`Score.replicate_scatter`) exists for only 6 of 46
scored datasets, because it can only be computed where a dataset repeats a
condition. That leaves the question "is 15% error at the measurement floor?"
unanswerable for the other 40 — and unmeasured is not zero.

This tool does the only admissible thing: look in each source for a
reproducibility the AUTHORS state (±sigma, "average of N runs", "n=3", error
bars, a stated repeatability). It prints candidate sentences with page numbers so
each hit can be transcribed by hand and cited. It never estimates: a source that
says nothing produces no number.

Reporting only. Reads PDFs, writes nothing, touches no physics.

Usage:
    python tools/repro_statement_scan.py            # every dataset with a local PDF
    python tools/repro_statement_scan.py bae2022    # one, by stem prefix
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

import yaml

from cmp_sim.core.validation import dataset_paths

#: Phrases that, in a CMP paper, precede a reproducibility claim. Kept broad:
#: a false positive costs one line of reading, a false negative loses a datum.
PATTERNS = [
    r"\u00b1\s*\d",                        # ± 12
    r"\+/-\s*\d",
    r"standard deviation",
    r"std\.?\s*dev",
    r"error bars?",
    r"repeatab\w+",
    r"reproducib\w+",
    r"\bn\s*=\s*[2-9]\b",
    r"average(?:d)? (?:of|over) (?:\w+|\d+) (?:runs?|wafers?|measurements?|samples?|points?)",
    r"(?:three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:repeated|replicate|identical)",
    r"(?:repeated|measured)\s+(?:three|four|five|\d+)\s+times",
    r"mean of (?:\w+|\d+)",
    r"uncertaint\w+",
    r"scatter",
    r"\d+\s*%\s*(?:variation|uncertainty|error)",
]
_RX = re.compile("|".join(PATTERNS), re.I)


def _pdf_paths(doc: Dict) -> List[Path]:
    text = " ".join(str(doc.get(k, "")) for k in ("source", "notes"))
    out = []
    for raw in re.findall(r"[~/][\w./~-]*\.pdf", text):
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = Path("~/fab-sim/papers").expanduser() / p.name
        if not p.exists():
            # the corpus records some paths by filename only
            p = Path("~/fab-sim/papers").expanduser() / Path(raw).name
        if p.exists():
            out.append(p)
    return out


def scan(pdf: Path) -> List[str]:
    try:
        import pymupdf  # type: ignore
    except ImportError:  # pragma: no cover - environment probe
        import fitz as pymupdf  # type: ignore
    hits: List[str] = []
    with pymupdf.open(pdf) as book:
        for page_no, page in enumerate(book, start=1):
            text = page.get_text("text").replace("\n", " ")
            for sentence in re.split(r"(?<=[.;])\s+", text):
                if _RX.search(sentence) and len(sentence) < 400:
                    hits.append(f"  p{page_no}: {sentence.strip()}")
    return hits


def main(argv: List[str]) -> int:
    only = argv[1] if len(argv) > 1 else None
    seen: Dict[Path, List[str]] = {}
    for path in sorted(dataset_paths(), key=lambda p: p.stem):
        if only and not path.stem.startswith(only):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pdfs = _pdf_paths(doc)
        print(f"\n=== {path.stem}  ({len(pdfs)} local pdf)")
        if not pdfs:
            print("  NO LOCAL PDF — reproducibility must come from the "
                  "publisher/patent text, or stay blank.")
            continue
        for pdf in pdfs:
            if pdf not in seen:
                seen[pdf] = scan(pdf)
            print(f"  --- {pdf.name}: {len(seen[pdf])} candidate sentences")
            for line in seen[pdf][:40]:
                print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
