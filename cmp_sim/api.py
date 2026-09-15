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
from typing import Any, Dict, List

from cmp_sim.cli import recipe_from_dict
from cmp_sim.core.maturity import FilmNotEstablished
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
        "sweepable": sorted(SWEEPABLE),
    }


#: Parameters a sweep may vary, mapped to where they live in the recipe.
SWEEPABLE: Dict[str, Any] = {
    "pressure_psi": ("tool", "pressure_psi"),
    "rpm_platen": ("tool", "rpm_platen"),
    "rpm_head": ("tool", "rpm_head"),
    "flow_ml_min": ("tool", "flow_ml_min"),
    "temperature_c": ("slurry", "temperature_c"),
    "ph": ("slurry", "ph"),
    "abrasive_conc_wt_pct": ("slurry.abrasive", "conc_wt_pct"),
    "abrasive_d50_nm": ("slurry.abrasive", "d50_nm"),
    "pattern_density": ("wafer", "pattern_density"),
    "pad_use_hours": ("pad", "use_hours"),
    "disk_hours_used": ("disk", "hours_used"),
}


def run_sweep(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run one recipe across a range of a single parameter.

    A process engineer asks "what happens as I raise the pressure", not "what
    is the rate at exactly 3 psi". Each point carries its own situation, so a
    sweep that crosses a regime boundary says so instead of drawing a smooth
    line through physics that changed underneath it.
    """
    import copy

    param = payload.get("parameter")
    if param not in SWEEPABLE:
        raise ValueError(
            f"cannot sweep '{param}'. available: {sorted(SWEEPABLE)}")
    values = payload.get("values")
    if not isinstance(values, list) or not values:
        raise ValueError("'values' must be a non-empty list")
    if len(values) > 50:
        raise ValueError(f"at most 50 sweep points, got {len(values)}")

    base = payload.get("recipe") or {}
    section, key = SWEEPABLE[param]
    points: List[Dict[str, Any]] = []
    regimes: set = set()

    for v in values:
        body = copy.deepcopy(base)
        target = body
        for part in section.split("."):
            target = target.setdefault(part, {})
        target[key] = v
        try:
            res = run_recipe(body)
        except Exception as exc:                   # one bad point must not kill the sweep
            points.append({"value": v, "error": f"{type(exc).__name__}: {exc}"})
            continue
        sit = res.get("situation") or {}
        regimes.add((sit.get("lubrication"), sit.get("load_regime"),
                     sit.get("contact_branch")))
        points.append({
            "value": v,
            "removal_rate_A_per_min": res.get("removal_rate_A_per_min"),
            "wiwnu_percent": res.get("wiwnu_percent"),
            "profile": res.get("profile"),
            "lubrication": sit.get("lubrication"),
            "load_regime": sit.get("load_regime"),
            "n_warnings": len(res.get("warnings") or []),
        })

    warnings: List[str] = []
    if len(regimes) > 1:
        warnings.append(
            "this sweep crosses a regime boundary: the points are not all "
            "described by the same physics, so do not read a single trend "
            "through them. The per-point regime is given for each value.")
    ok = [p for p in points if "error" not in p]
    if not ok:
        warnings.append("every point failed; see the per-point error messages")

    return {"parameter": param, "unit_hint": param, "points": points,
            "warnings": warnings, "n_ok": len(ok), "n_failed": len(points) - len(ok)}


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
        route = self.path.split("?", 1)[0]
        if route not in ("/api/simulate", "/api/sweep"):
            # Name the valid routes: a bare "no such path" sends the caller
            # reading source to find out what they should have posted to.
            return self._json(404, {
                "error": f"no such path: {route}",
                "valid_post_paths": ["/api/simulate", "/api/sweep"],
                "valid_get_paths": ["/", "/api/meta"]})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": f"invalid JSON: {exc}"})

        try:
            handler = run_sweep if route == "/api/sweep" else run_recipe
            return self._json(200, handler(payload))
        except ParamMissing as exc:
            return self._json(422, {"error": "ParamMissing", "detail": str(exc)})
        except FileNotFoundError as exc:
            # A film with no parameter pack yet is a data gap, not a server
            # fault: 500 would send the user looking for a crash.
            return self._json(422, {"error": "PackMissing", "detail": str(exc)})
        except FilmNotEstablished as exc:
            # 400 would blame the request. The request is fine; the FIELD has
            # no CMP data, and the response says what to supply.
            return self._json(422, {
                "error": "FilmNotEstablished",
                "detail": str(exc),
                "maturity": exc.maturity.as_dict(),
            })
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
