"""Read a table of measurements from CSV.

Big data does not arrive as a YAML block. A polishing log is a spreadsheet: one
row per wafer, columns for the conditions and the measured rate. This reads that
directly, tolerates the column names people actually use, and refuses clearly
when a column is missing rather than silently dropping rows — a dropped row is
an invisible change to the fit.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

#: Accepted spellings for each field. Compared case-insensitively with spaces,
#: underscores, hyphens and units in brackets stripped, so "Pressure (psi)",
#: "pressure_psi" and "DownForce" all land on the same field.
ALIASES: Dict[str, Tuple[str, ...]] = {
    "rate_A_per_min": (
        "rateapermin", "rate", "mrr", "removalrate", "rr", "ramin",
        "mrrapermin", "removalrateamin", "rateamin"),
    "rate_nm_per_min": (
        "ratenmpermin", "mrrnm", "mrrnmpermin", "removalratenm", "ratenmmin",
        "mrrnmmin"),
    "pressure_psi": (
        "pressurepsi", "pressure", "psi", "downforce", "downforcepsi",
        "load", "p"),
    "rpm_platen": (
        "rpmplaten", "platenrpm", "platen", "tablerpm", "table", "rpm"),
    "rpm_head": (
        "rpmhead", "headrpm", "head", "carrierrpm", "carrier", "wafer"),
    "abrasive_wt_pct": (
        "abrasivewtpct", "abrasive", "abrasivewt", "solidswtpct", "solids",
        "abrasiveconc", "conc"),
    "abrasive_d50_nm": (
        "abrasived50nm", "d50", "d50nm", "particlesize", "psnm", "size"),
    "oxidizer_wt_pct": (
        "oxidizerwtpct", "oxidizer", "oxidant", "h2o2", "h2o2wtpct",
        "oxidizerwt"),
    "ph": ("ph", "slurryph"),
    "temperature_c": (
        "temperaturec", "temperature", "temp", "tempc", "platentemp"),
    "label": ("label", "name", "id", "run", "wafer", "lot", "condition"),
}

#: Without these nothing can be fitted.
REQUIRED = ("pressure_psi", "rpm_platen")


#: Unit suffixes stripped before matching, so "MRR (A/min)", "MRR_A_per_min"
#: and "MRR" are the same column. Longest first, since "apermin" contains
#: "amin" and stripping the short one first would leave "aper".
_UNIT_SUFFIXES = (
    "angstrompermin", "angstromspermin", "angstromsmin", "angstrommin",
    "apermin", "aperminute", "amin", "aps",
    "nmpermin", "nmperminute", "nmmin", "nms",
    "umpermin", "ummin",
    "wtpct", "wtpercent", "percent", "pct", "psi", "kpa", "rpm", "nm", "um",
    "degc", "c",
)


def _normalise_keep_units(name: str) -> str:
    """Alphanumerics only, units intact."""
    return "".join(ch for ch in str(name).strip().lower() if ch.isalnum())


def _normalise(name: str) -> str:
    keep = []
    for ch in str(name).strip().lower():
        if ch.isalnum():
            keep.append(ch)
        # everything else - spaces, underscores, brackets, slashes - is dropped
    text = "".join(keep)
    # A unit in the header is decoration, not identity: strip one trailing unit
    # so "MRR (A/min)" matches the same field as a bare "MRR".
    for suffix in _UNIT_SUFFIXES:
        if text.endswith(suffix) and len(text) > len(suffix):
            stripped = text[: -len(suffix)]
            # only strip if what remains still names something
            if stripped:
                return stripped
    return text


def _map_columns(fieldnames: Sequence[str]) -> Dict[str, str]:
    """Map each CSV column onto a known field, where one matches.

    Matched against the FULL name first, then against the name with its unit
    stripped. Order matters: "MRR (nm/min)" and "MRR (A/min)" differ only by
    their unit, and stripping first would silently merge them - a 10x error in
    every fitted rate.
    """
    mapping: Dict[str, str] = {}
    for column in fieldnames or []:
        full = _normalise_keep_units(column)
        bare = _normalise(column)
        for field, aliases in ALIASES.items():
            names = {_normalise_keep_units(field), *aliases}
            if full in names:
                mapping.setdefault(field, column)
                break
        else:
            for field, aliases in ALIASES.items():
                names = {_normalise_keep_units(field), *aliases}
                if bare in names:
                    mapping.setdefault(field, column)
                    break
    return mapping


def _to_float(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "")
    if not text or text.lower() in {"na", "n/a", "nan", "-", "none", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def read_measurements(text: str) -> List[Dict[str, Any]]:
    """Parse CSV text into measurement dicts for the calibration layer."""
    # Drop comment lines so a template can explain itself inline.
    body = "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("#"))
    reader = csv.DictReader(io.StringIO(body))
    mapping = _map_columns(reader.fieldnames or [])

    has_rate = "rate_A_per_min" in mapping or "rate_nm_per_min" in mapping
    missing = [f for f in REQUIRED if f not in mapping]
    if not has_rate:
        missing.append("a removal rate (rate_A_per_min or rate_nm_per_min)")
    if missing:
        raise ValueError(
            "this CSV is missing " + ", ".join(missing)
            + f". Columns found: {list(reader.fieldnames or [])}. "
            "Recognised spellings include "
            + "; ".join(f"{k} ({', '.join(v[:3])})" for k, v in ALIASES.items()
                        if k in ("rate_A_per_min", "pressure_psi", "rpm_platen")))

    out: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for i, row in enumerate(reader, start=2):        # row 1 is the header
        record: Dict[str, Any] = {}
        for field, column in mapping.items():
            if field == "label":
                value = str(row.get(column, "") or "").strip()
                if value:
                    record["label"] = value
                continue
            value = _to_float(row.get(column))
            if value is not None:
                record[field] = value
        if "rate_A_per_min" not in record and "rate_nm_per_min" in record:
            record["rate_A_per_min"] = record.pop("rate_nm_per_min") * 10.0
        essential = ("rate_A_per_min", "pressure_psi", "rpm_platen")
        gaps = [f for f in essential if record.get(f) is None]
        if gaps:
            skipped.append(f"row {i} (no {', '.join(gaps)})")
            continue
        record.setdefault("label", f"row {i}")
        out.append(record)

    if not out:
        raise ValueError(
            "no usable rows: every row was missing a rate, a pressure or a "
            "platen speed. " + ("Skipped " + "; ".join(skipped[:5]) if skipped else ""))
    if skipped:
        raise ValueError(
            f"{len(skipped)} of {len(skipped) + len(out)} rows are unusable and "
            "were NOT silently dropped, because that would change the fit "
            "invisibly: " + "; ".join(skipped[:5])
            + (" ..." if len(skipped) > 5 else "")
            + ". Fix or remove them, then re-run.")
    return out


def read_file(path: str | Path) -> List[Dict[str, Any]]:
    return read_measurements(Path(path).read_text(encoding="utf-8"))


TEMPLATE = """label,pressure_psi,rpm_platen,rate_A_per_min,abrasive_wt_pct,oxidizer_wt_pct,temperature_c
# one row per polished wafer. Only label, pressure_psi, rpm_platen and a rate
# are required; every other column unlocks the factor that depends on it, but
# only if it VARIES between rows.
run-1,2.0,60,2380,3.0,3.0,25
run-2,4.0,60,4690,3.0,3.0,25
run-3,3.0,120,7120,3.0,3.0,25
run-4,3.0,60,3610,6.0,3.0,25
"""
