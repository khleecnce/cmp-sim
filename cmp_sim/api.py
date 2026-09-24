"""HTTP API + static web UI, on the Python standard library only.

Deliberately dependency-free (``http.server``): the owner must be able to run
this on a lab machine with nothing installed beyond the simulator itself.

    python -m cmp_sim.api          -> http://127.0.0.1:8765

Endpoints
---------
``GET  /``               the form web UI
``GET  /tool``           the 3D tool view — click a part of the polisher to
                         enter its data; the wafer shows the predicted profile
``GET  /vendor/<asset>`` vendored static assets (three.js, the scene module)
``GET  /api/meta``       packs, models, films, additives and abrasives available
``GET  /api/accuracy``   measured predictive error over all 320 literature points
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


def _expected_token() -> str:
    """The shared secret for a hosted demo, or "" when running locally.

    Set CMPSIM_TOKEN to put the whole app behind an unguessable link. Left
    unset — the normal case on a laptop — every route stays open, because
    demanding a token from someone who just double-clicked the launcher would
    be a lock with the key taped to it.
    """
    import os
    return (os.environ.get("CMPSIM_TOKEN") or "").strip()


class Handler(BaseHTTPRequestHandler):
    server_version = "CMPSim/0.1"

    def log_message(self, fmt, *args):
        """One compact line per request; silence with CMPSIM_QUIET=1."""
        import os
        if os.environ.get("CMPSIM_QUIET"):
            return
        super().log_message(fmt, *args)

    # ── access ───────────────────────────────────────────────────
    def _authorised(self) -> bool:
        """True when no token is configured, or the caller presented it.

        Accepts the token from `?t=` (so a single link works when pasted into
        a browser) or from an `X-CMPSim-Token` header (so scripted clients do
        not have to put the secret in a URL that lands in server logs).

        Compared with compare_digest: a plain `==` on a secret leaks its
        length and prefix through timing, which is a needless gift to anyone
        probing a public URL.
        """
        import hmac
        from urllib.parse import parse_qs, urlparse

        want = _expected_token()
        if not want:
            return True
        given = self.headers.get("X-CMPSim-Token", "")
        if not given:
            qs = parse_qs(urlparse(self.path).query)
            given = (qs.get("t") or [""])[0]
        return hmac.compare_digest(given, want)

    def _deny(self) -> None:
        self._json(401, {
            "error": "Unauthorized",
            "detail": "this instance is link-protected; append ?t=<token> to "
                      "the URL or send an X-CMPSim-Token header",
        })

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

    #: Static asset types served from web/vendor. An extension not on this list
    #: is refused rather than guessed: serving an unknown type as octet-stream
    #: is how a mis-set MIME turns into a module that silently will not load.
    _CONTENT_TYPES = {
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".glb": "model/gltf-binary",
        ".ktx2": "image/ktx2",
    }

    def _static(self, path: str) -> None:
        """Serve one file from web/vendor, refusing anything outside it.

        The 3D view's three.js build is VENDORED rather than pulled from a CDN:
        the owner has to be able to run this on a fab machine with no outbound
        network, and a UI that silently degrades to a blank canvas offline would
        be worse than no 3D view at all.

        Path containment is checked by resolving both sides. A request for
        ``/vendor/../../etc/passwd`` must not escape, and checking for ".." in
        the string is not enough once URL escaping is involved.
        """
        from urllib.parse import unquote

        rel = unquote(path).lstrip("/")
        target = (WEB_DIR / rel).resolve()
        root = (WEB_DIR / "vendor").resolve()
        if root not in target.parents or not target.is_file():
            return self._json(404, {"error": f"no such asset: {path}"})
        ctype = self._CONTENT_TYPES.get(target.suffix.lower())
        if ctype is None:
            return self._json(415, {
                "error": f"refusing to serve '{target.suffix}'",
                "detail": "add it to Handler._CONTENT_TYPES with the correct MIME "
                          "type; guessing one breaks module loading silently"})
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # Vendored assets are immutable for a given build, and re-sending 670 KB
        # of three.js on every reload makes the tool view feel broken.
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(body)

    # ── routes ───────────────────────────────────────────────────
    def do_GET(self) -> None:                     # noqa: N802
        if not self._authorised():
            return self._deny()
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            html = (WEB_DIR / "index.html").read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")
        if path in ("/tool", "/tool.html"):
            html = (WEB_DIR / "tool.html").read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")
        if path.startswith("/vendor/"):
            return self._static(path)
        if path == "/api/meta":
            return self._json(200, _meta())
        if path == "/api/accuracy":
            # Measured predictive accuracy across every dataset, so the UI can
            # state how far to trust a number instead of showing it bare.
            from cmp_sim.core.predictive_score import score_all

            scores = [s for s in score_all() if s.shape_mape is not None]
            shape = sorted(s.shape_mape for s in scores)
            loo = sorted(s.loo_mape for s in scores)
            by_axis = {}
            for axis in ("pressure", "velocity", "slurry_ph",
                         "abrasive_wt_pct", "abrasive_d50_nm",
                         "oxidizer_wt_pct"):
                sel = sorted(s.shape_mape for s in scores if axis in s.axes)
                if sel:
                    by_axis[axis] = {
                        "datasets": len(sel),
                        "median_shape_error_percent": round(
                            sel[len(sel) // 2], 1)}
            return self._json(200, {
                "datasets_scored": len(scores),
                "measured_points": sum(s.n for s in scores),
                "median_shape_error_percent": round(shape[len(shape) // 2], 1),
                "median_leave_one_out_percent": round(loo[len(loo) // 2], 1),
                "beat_predicting_the_mean": sum(1 for s in scores
                                                if s.beats_flat),
                "by_axis": by_axis,
                "worst": [{"dataset": s.dataset,
                           "shape_error_percent": round(s.shape_mape, 1)}
                          for s in sorted(scores,
                                          key=lambda x: -x.shape_mape)[:5]],
            })
        self._json(404, {"error": f"no such path: {path}",
                         "valid_get_paths": ["/", "/tool", "/vendor/<asset>",
                                             "/api/meta", "/api/accuracy"]})

    def do_POST(self) -> None:                    # noqa: N802
        if not self._authorised():
            return self._deny()
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
