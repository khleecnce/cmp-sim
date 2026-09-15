"""HTTP API + static web UI, on the Python standard library only.

Deliberately dependency-free (``http.server``): the owner must be able to run
this on a lab machine with nothing installed beyond the simulator itself.

    python -m cmp_sim.api          -> http://127.0.0.1:8765

Endpoints
---------
``GET  /``               the web UI
``GET  /api/meta``       packs, models, films, additives and abrasives available
``POST /api/simulate``   a recipe dict in, a result dict out
"""
from __future__ import annotations

import json
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

from cmp_sim.cli import recipe_from_dict
from cmp_sim.core.params import ParamMissing, available_packs
from cmp_sim.core.solver import FILM_PACK, MODELS, simulate

WEB_DIR = Path(__file__).resolve().parent / "web"
DEFAULT_PORT = 8765


def _meta() -> Dict[str, Any]:
    from cmp_sim.core.profiles import LAYERS, PROFILES
    from cmp_sim.slurry.formulation import abrasive_database, additive_database

    additives = additive_database()
    abrasives = abrasive_database()
    return {
        "models": MODELS,
        "profiles": {n: p.as_dict() for n, p in PROFILES.items()},
        "layers": list(LAYERS),
        "packs": available_packs(),
        "films": sorted(FILM_PACK),
        "film_pack": FILM_PACK,
        "additives": sorted(additives),
        "additive_roles": {k: (v or {}).get("role") for k, v in additives.items()},
        "abrasives": sorted(abrasives) or ["silica", "ceria", "alumina", "diamond"],
    }


def run_recipe(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate, simulate, and return a JSON-safe result."""
    recipe = recipe_from_dict(payload)
    result = simulate(recipe)
    out = result.summary()
    out["provenance"] = result.provenance
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "CMPSim/0.1"

    def log_message(self, fmt, *args):
        """One compact line per request; silence with CMPSIM_QUIET=1."""
        import os
        if os.environ.get("CMPSIM_QUIET"):
            return
        super().log_message(fmt, *args)

    # ── helpers ──────────────────────────────────────────────────
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: Any) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    # ── routes ───────────────────────────────────────────────────
    def do_GET(self) -> None:                     # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            html = (WEB_DIR / "index.html").read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")
        if path == "/api/meta":
            return self._json(200, _meta())
        self._json(404, {"error": f"no such path: {path}"})

    def do_POST(self) -> None:                    # noqa: N802
        if self.path.split("?", 1)[0] != "/api/simulate":
            return self._json(404, {"error": "no such path"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": f"invalid JSON: {exc}"})

        try:
            return self._json(200, run_recipe(payload))
        except ParamMissing as exc:
            return self._json(422, {"error": "ParamMissing", "detail": str(exc)})
        except (ValueError, KeyError, TypeError) as exc:
            return self._json(400, {"error": type(exc).__name__, "detail": str(exc)})
        except Exception as exc:                   # pragma: no cover
            return self._json(500, {"error": type(exc).__name__, "detail": str(exc),
                                     "traceback": traceback.format_exc()})


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="cmp-sim-web", description="CMP-Sim web UI")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args(argv)

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"CMP-Sim running at http://{args.host}:{args.port}  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
