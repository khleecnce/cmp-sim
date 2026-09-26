"""End-to-end smoke check of the running web app.

Starts the API on a spare port, fetches every route the 3D tool view uses, runs
one full-chemistry prediction with a NAMED pad and a NAMED disk, and prints what
came back. Kept as a script rather than a test because it is the "does the thing
actually run" check, not an assertion of physics; the assertions live in
tests/test_tool_ui_3d.py and tests/test_web_holds_no_physics_constants.py.

    .venv/bin/python tools/web_smoke.py
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8791


def main() -> int:
    env = {**os.environ, "CMPSIM_QUIET": "1", "CMPSIM_TOKEN": ""}
    proc = subprocess.Popen(
        [sys.executable, "-m", "cmp_sim.api", "--port", str(PORT)],
        cwd=str(ROOT), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{PORT}"
    for _ in range(80):
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill()
        print("the server never came up", file=sys.stderr)
        return 1

    try:
        html = urllib.request.urlopen(base + "/tool").read().decode("utf-8")
        hangul = sum(1 for c in html if "\uac00" <= c <= "\ud7a3")
        print(f"GET /tool            {len(html)} bytes, hangul chars {hangul} "
              f"(owner requires an English UI)")

        meta = json.load(urllib.request.urlopen(base + "/api/meta"))
        print(f"GET /api/meta        pads {list(meta['pads'])}")
        print(f"                     disks {list(meta['disks'])}")

        mdl = json.load(urllib.request.urlopen(base + "/api/model?film=cu"))
        print(f"GET /api/model       {mdl['pack']}, "
              f"{len(mdl['parameters'])} constants with sources")

        body = json.dumps({
            "model": "full",
            "wafer": {"film": "cu", "diameter_mm": 300},
            "pad": {"name": "D100"},
            "disk": {"name": "3M_E187_80mesh"},
            "tool": {"pressure_psi": 3.0, "rpm_platen": 80, "rpm_head": 80,
                     "flow_ml_min": 150, "time_s": 60},
            "slurry": {"ph": 4.0, "temperature_c": 30.0,
                       "additives": [{"name": "hydrogen_peroxide",
                                      "conc_wt_pct": 2.0}]},
        }).encode()
        req = urllib.request.Request(
            base + "/api/simulate", data=body,
            headers={"Content-Type": "application/json"})
        res = json.load(urllib.request.urlopen(req))
        print(f"POST /api/simulate   RR {res['removal_rate_A_per_min']} A/min, "
              f"WIWNU {res['wiwnu_percent']}%, "
              f"{len(res['warnings'])} disclosed warnings")
        cons = res.get("consumables") or {}
        print(f"                     pad {cons.get('pad')} -> "
              f"{cons.get('filled')}")
        print(f"                     disk {cons.get('disk')}")
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
