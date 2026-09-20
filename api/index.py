"""Vercel serverless entry point for the CMP-Sim web app.

Why an adapter exists at all
----------------------------
`cmp_sim.api` is a long-lived `ThreadingHTTPServer`: you start it, it owns a
port, it serves until you stop it. Vercel's Python runtime is the opposite —
it hands each request to a `BaseHTTPRequestHandler` subclass named `handler`
and there is no port to own.

Rather than fork the routing logic (two copies that drift is worse than one
adapter), this subclasses the real `Handler`. Every route, every error
message and the token gate are the SAME code that runs locally, so the hosted
demo cannot quietly diverge from what the repository's tests cover.

Cold starts: the first request in a while pays for importing numpy/scipy and
parsing the YAML packs. `/api/accuracy` scores 330 measured points and is the
slowest route; the UI already fetches it out of band so the page paints first.
"""
import os
import sys
from pathlib import Path

# The repository root, so `import cmp_sim` works without an install step.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cmp_sim.api import Handler as _CMPSimHandler  # noqa: E402


class handler(_CMPSimHandler):  # noqa: N801  (Vercel requires this name)
    """The project's own handler, unmodified apart from logging.

    Vercel captures stdout per invocation, so the parent's access log would
    duplicate what the platform already records.
    """

    def log_message(self, fmt, *args):
        return
