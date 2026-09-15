"""How well established is CMP on this film, and what must the owner supply?

Not every film in this simulator is a routine polish step. Oxide and copper have
decades of published process data; SnAg solder has none, because the packaging
industry planarises fine-pitch tin bumps by fly-cutting rather than CMP, so the
CMP numbers were never generated. Treating those two cases identically is how a
simulator produces a confident number for a process nobody has demonstrated.

So films are graded, and the grade decides how much the owner has to supply
before a prediction is allowed:

``established``
    A Preston coefficient measured on this system, and literature the model has
    been backtested against. Runs on pack defaults.

``emerging``
    A Preston coefficient exists but was *back-calculated* from a single
    published operating point, with no independent dataset to check the shape
    against. Runs, but every absolute number is an extrapolation from one point.

``unestablished``
    No Preston coefficient at any operating point — or the literature records
    attempts that failed. Refuses to predict on defaults and asks for
    measurements instead.

The grade is derived from the pack's own evidence wherever possible rather than
declared, so it cannot drift away from the data. A pack may state
``cmp_maturity`` to *lower* its grade (SnAg does: documented process failures
are evidence the field has not solved it), but it cannot declare itself more
established than its evidence supports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

ESTABLISHED = "established"
EMERGING = "emerging"
UNESTABLISHED = "unestablished"

_ORDER = {ESTABLISHED: 2, EMERGING: 1, UNESTABLISHED: 0}

#: Packs with a literature dataset in the backtest suite. A film whose shape has
#: been checked against independent data is in a different position from one
#: whose single constant was reverse-engineered from one number.
BACKTESTED_PACKS = {
    "oxide_silica", "oxide_silica_calibrated_pad", "sti_ceria",
    "cu_h2o2_bta", "w_fe_oxidizer", "sic_ceria_h2o2",
}

#: Confidences that mean "this number came from a measurement of this system".
MEASURED_CONFIDENCE = {"high", "verified", "literature"}


@dataclass
class Requirement:
    """One thing the owner must supply before an unestablished film will run."""
    key: str
    what: str
    why: str
    satisfied: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "what": self.what, "why": self.why,
                "satisfied": self.satisfied}


@dataclass
class Maturity:
    """The grade of a film, and what it still needs."""
    grade: str
    film: str
    pack: str
    reasons: List[str] = field(default_factory=list)
    requirements: List[Requirement] = field(default_factory=list)

    @property
    def outstanding(self) -> List[Requirement]:
        return [r for r in self.requirements if not r.satisfied]

    @property
    def runnable(self) -> bool:
        return self.grade != UNESTABLISHED or not self.outstanding

    def as_dict(self) -> Dict[str, Any]:
        return {
            "grade": self.grade,
            "film": self.film,
            "pack": self.pack,
            "reasons": self.reasons,
            "requirements": [r.as_dict() for r in self.requirements],
            "outstanding": [r.key for r in self.outstanding],
            "runnable": self.runnable,
        }


def _param(pack, key):
    return pack.params.get(key)


def _has_value(pack, key) -> bool:
    p = _param(pack, key)
    return p is not None and getattr(p, "value", None) is not None


def _confidence(pack, key) -> Optional[str]:
    p = _param(pack, key)
    return None if p is None else str(getattr(p, "confidence", "") or "").lower()


def _requirements_for(film: str, pack, recipe) -> List[Requirement]:
    """What an unestablished film needs before it can be predicted.

    These are deliberately the inputs that cannot be inferred: a rate anchor,
    the chemistry window, and the mechanical state of the surface. Each says
    why it matters, so supplying it is a decision rather than form-filling.
    """
    supplied = set(getattr(recipe, "params", {}) or {})
    measurements = list(getattr(recipe, "measurements", []) or [])

    reqs = [
        Requirement(
            key="film_hardness_or_rate",
            what="either one measured removal rate with its pressure and speed "
                 "(measurements:), or the film hardness so Kp can be estimated "
                 "from the Archard relation Kp = k/H",
            why="Something must set the absolute scale. A measured rate sets it "
                "exactly; a hardness sets it to within about a factor of 3, "
                "which is enough to rank recipes and see trends but not to "
                "quote a number.",
            satisfied=("kp_m_per_pa" in supplied
                       or bool(measurements)
                       or "film_bulk_hardness_pa" in supplied
                       or _has_value(pack, "film_bulk_hardness_pa")),
        ),
        Requirement(
            key="slurry_ph",
            what="the slurry pH you intend to use",
            why="For an unestablished film the viable pH window is itself "
                "unknown. For SnAg the only primary CMP report eliminated both "
                "windows it tried (alkaline etched the tin, acidic scratched "
                "it), so pH cannot be defaulted.",
            satisfied=("slurry_ph" in supplied
                       or getattr(recipe.slurry, "ph", None) is not None),
        ),
        Requirement(
            key="film_bulk_hardness_pa",
            what="the hardness of the film as deposited",
            why="Sets the contact branch and the scratch severity. A soft, "
                "creeping film smears and embeds abrasive instead of "
                "fracturing, which the mechanical terms handle differently.",
            satisfied=("film_bulk_hardness_pa" in supplied
                       or _has_value(pack, "film_bulk_hardness_pa")),
        ),
    ]
    return reqs


def assess(pack, recipe) -> Maturity:
    """Grade a film from its pack's evidence, and list what it still needs."""
    film = str(getattr(recipe.wafer, "film", "") or "")
    name = str(getattr(pack, "name", "") or "")
    reasons: List[str] = []

    has_kp = _has_value(pack, "kp_m_per_pa")
    kp_conf = _confidence(pack, "kp_m_per_pa") or ""
    backtested = name in BACKTESTED_PACKS

    # ── derive the grade from evidence ───────────────────────────────
    if not has_kp:
        grade = UNESTABLISHED
        reasons.append(
            "no Preston coefficient exists for this film at any operating "
            "point, so there is no published anchor for the absolute rate")
    elif kp_conf in MEASURED_CONFIDENCE and backtested:
        grade = ESTABLISHED
        reasons.append(
            f"Kp is measured (confidence '{kp_conf}') and this pack is "
            "backtested against published pressure/velocity data")
    elif backtested:
        grade = ESTABLISHED
        reasons.append(
            "this pack is backtested against published pressure/velocity data")
    else:
        grade = EMERGING
        reasons.append(
            f"Kp exists (confidence '{kp_conf or 'unknown'}') but was derived "
            "from a single published operating point, with no independent "
            "dataset to check the predicted shape against")

    # ── a pack may lower its own grade, never raise it ───────────────
    declared = _param(pack, "cmp_maturity")
    declared_value = None if declared is None else getattr(declared, "value", None)
    if declared_value:
        declared_value = str(declared_value).strip().lower()
        if declared_value in _ORDER:
            if _ORDER[declared_value] < _ORDER[grade]:
                reasons.append(
                    f"the pack declares '{declared_value}', below the grade its "
                    "evidence alone would give — a pack may lower its own grade "
                    "(documented process failures are evidence) but never raise it")
                grade = declared_value
            elif _ORDER[declared_value] > _ORDER[grade]:
                reasons.append(
                    f"the pack declares '{declared_value}' but its evidence only "
                    f"supports '{grade}', so the declaration is ignored")

    m = Maturity(grade=grade, film=film, pack=name, reasons=reasons)
    if grade == UNESTABLISHED:
        m.requirements = _requirements_for(film, pack, recipe)
    return m


class FilmNotEstablished(ValueError):
    """An unestablished film was run without the inputs it needs."""

    def __init__(self, maturity: Maturity):
        self.maturity = maturity
        missing = maturity.outstanding
        lines = [
            f"'{maturity.film}' is not an established CMP target, so it cannot "
            f"be predicted from pack defaults.",
            "",
        ]
        lines.extend(f"  - {r}" for r in maturity.reasons)
        lines += ["", f"Supply {len(missing)} more input(s) and it will run:"]
        for r in missing:
            lines.append(f"  * {r.key}: {r.what}")
            lines.append(f"      why: {r.why}")
        lines += [
            "",
            "Put a Preston coefficient under `params:`, or - better - give "
            "measured rates under `measurements:` and the model will fit Kp "
            "itself and report how far it can be trusted.",
        ]
        super().__init__("\n".join(lines))
