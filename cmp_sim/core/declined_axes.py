"""The machine-readable form of "the model declined to predict this axis".

A term can be switched off for a good, cited reason -- the pack's constants
were measured in a window this run is outside of, or the only reachable
constant was refuted by the very dataset in front of us.  When that happens the
rate stops responding to that axis, and the run says so in a warning.

The problem is that a *reader* then has to recognise the sentence.  The scorer
recognised exactly one word, ``GATED``, and therefore counted a block whose
inhibitor term was ``REFUSED`` -- with a citation, a measured ratio and an
unblocking experiment -- as an ordinary prediction that happened to be flat.
That block then scored the `flat` baseline exactly (14.8% == 14.8%) and
contributed to the headline median as though the physics had been tested.

So the refusal carries a marker naming the axis it declines:

    [DECLINES_AXIS: inhibitor_mM] inhibitor term REFUSED at 10 mM ...

Two design points, both learned the hard way here:

* **Name the AXIS, not the term.**  The scorer's question is "does this dataset
  sweep something the model refused to predict?", which is about the input
  the experiment varied, not about the internal term's name.
* **Keep the prose.**  The marker is an addition, never a replacement: the
  human-readable reason (with its citation and its unblocking measurement) is
  the part that stops a refusal from becoming permanent by accident.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Set

# Written into the warning text itself; the closing bracket is supplied by the
# caller after the axis name, so a warning reads "[DECLINES_AXIS: ph] ...".
DECLINES_AXIS = "[DECLINES_AXIS: "

_PATTERN = re.compile(r"\[DECLINES_AXIS:\s*([A-Za-z0-9_,\s]+)\]")

#: The WEAKER sibling of the above, and a different claim.
#:
#: ``DECLINES_AXIS`` means the rate does not respond to that axis at all.  There
#: is a third state between that and an ordinary prediction, and until §48
#: nothing here could report it: a term IS applied and the rate DOES move, but
#: the constant driving it was measured on a different species, material or
#: chemical regime than the run in front of us.  The prediction then spans a
#: token fraction of the measured trend -- enough to clear ``inert_axis_scan``'s
#: 0.5 % bar and to move the shape score off the flat baseline, so every reader
#: in this repository graded it as an ordinary prediction.
#:
#: Two real instances, both with the substitution already documented in prose
#: and neither machine-readable (``tools/trend_share_census.py``):
#:
#: * ``jani2025_cu_h2o2_acidic_chelator`` sweeps H2O2 in the ACIDIC + oxalate
#:   regime, where the measured log-slope is **+0.167**; the pack's fitted
#:   constant belongs to a different chelator whose sign is opposite, so it is
#:   correctly NOT transferred and the legacy path applies **-0.029**.
#: * ``bouvet2002_ti_silica_size_sweep`` measures **-0.454** on titanium while
#:   the abrasive-scoped silica exponent, deliberately shared across five sweeps
#:   on five films, applies **-0.050**.
#:
#: Both refusals are right, and both must remain legible AS refusals.  Naming
#: the axis is what makes the difference between "the model weighed this and
#: found it weak" and "the model is answering about a different system".
SUBSTITUTED_AXIS = "[SUBSTITUTED_AXIS: "

_SUBSTITUTED = re.compile(r"\[SUBSTITUTED_AXIS:\s*([A-Za-z0-9_,\s]+)\]")


def declined_axes(warnings: Iterable[str] | None) -> Set[str]:
    """Axis names the run explicitly declined to predict."""
    out: Set[str] = set()
    for w in warnings or ():
        for m in _PATTERN.finditer(str(w)):
            for name in m.group(1).split(","):
                name = name.strip()
                if name:
                    out.add(name)
    return out


def declining_warnings(warnings: Iterable[str] | None) -> List[str]:
    """The warnings that carry a declaration, in order."""
    return [str(w) for w in (warnings or ()) if _PATTERN.search(str(w))]


def substituted_axes(warnings: Iterable[str] | None) -> Set[str]:
    """Axes the run predicts with a constant from ANOTHER species/material.

    Deliberately a separate set from :func:`declined_axes`: the rate does
    respond on these axes, so calling them declined would be false, while
    calling them ordinary predictions is what let a token response pass for a
    tested one.
    """
    out: Set[str] = set()
    for w in warnings or ():
        for m in _SUBSTITUTED.finditer(str(w)):
            for name in m.group(1).split(","):
                name = name.strip()
                if name:
                    out.add(name)
    return out
