"""List every validation dataset with the provenance a reproducibility hunt needs.

Reporting only — reads the corpus, writes nothing, touches no physics. Used to
hand out transcription work in CORPUS ORDER (alphabetical), deliberately
independent of each dataset's score, so the search cannot be steered towards the
sources that would raise the measured floor.
"""
from __future__ import annotations

import re
import sys

import yaml

from cmp_sim.core.validation import dataset_paths


def main() -> int:
    for i, path in enumerate(sorted(dataset_paths(), key=lambda p: p.stem)):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        src = " ".join(str(doc.get(k, "")) for k in ("source", "notes")).replace("\n", " ")
        pdf = re.findall(r"[~/][\w./~-]*\.pdf", src)
        pat = re.findall(r"\b(?:US|EP|CN|TW|WO|KR|JP)[\d/]{5,}[A-Z\d]*\b", src)
        doi = re.findall(r"10\.\d{4,9}/[^\s,;]+", src)
        print(f"{i:3d} {path.stem}")
        print(f"     pdf={pdf[:1]} patent={pat[:1]} doi={doi[:1]}")
        print(f"     {src[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
