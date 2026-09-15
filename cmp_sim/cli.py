"""CMP-Sim command line interface.

    cmp-sim run config.yaml --out result.json
    cmp-sim packs
    cmp-sim models
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Dict

import yaml

from cmp_sim.core.params import ParamMissing, available_packs
from cmp_sim.core.solver import MODELS, simulate
from cmp_sim.core.state import (Abrasive, Additive, Disk, Pad, Recipe, Slurry,
                                Tool, Wafer)


def _build(cls, data: Dict[str, Any]):
    """Instantiate a dataclass from a dict, rejecting unknown keys loudly."""
    if not isinstance(data, dict):
        raise ValueError(f"{cls.__name__} section must be a mapping, got {type(data).__name__}")
    known = {f.name for f in fields(cls)}
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"unknown key(s) for {cls.__name__}: {sorted(unknown)}; known: {sorted(known)}")
    return cls(**data)


def recipe_from_dict(cfg: Dict[str, Any]) -> Recipe:
    cfg = dict(cfg or {})
    slurry_cfg = dict(cfg.pop("slurry", {}) or {})
    abrasive = _build(Abrasive, slurry_cfg.pop("abrasive", {}) or {})
    additives = [_build(Additive, a) for a in (slurry_cfg.pop("additives", []) or [])]
    slurry = _build(Slurry, slurry_cfg)
    slurry.abrasive = abrasive
    slurry.additives = additives

    return Recipe(
        slurry=slurry,
        pad=_build(Pad, cfg.pop("pad", {}) or {}),
        disk=_build(Disk, cfg.pop("disk", {}) or {}),
        tool=_build(Tool, cfg.pop("tool", {}) or {}),
        wafer=_build(Wafer, cfg.pop("wafer", {}) or {}),
        model=cfg.pop("model", "preston"),
        meta=cfg.pop("meta", {}) or {},
    )


def load_config(path: str) -> Recipe:
    text = Path(path).read_text(encoding="utf-8")
    cfg = yaml.safe_load(text) or {}
    return recipe_from_dict(cfg)


def _cmd_run(args: argparse.Namespace) -> int:
    recipe = load_config(args.config)
    try:
        result = simulate(recipe)
    except ParamMissing as exc:
        print(f"ParamMissing: {exc}", file=sys.stderr)
        return 2
    payload = result.summary()
    if args.provenance:
        payload["provenance"] = result.provenance
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        rr = payload["removal_rate_A_per_min"]
        sit = payload.get("situation", {})
        print(f"wrote {args.out}  (RR={rr} A/min, "
              f"WIWNU={payload['wiwnu_percent']}%, "
              f"profile={payload.get('profile')}, "
              f"situation={sit.get('film_class')}/{sit.get('rate_limit')}-limited)")
    else:
        print(text)
    return 0


def _cmd_sweep(args: argparse.Namespace) -> int:
    """Vary one parameter across a range, from the same YAML config."""
    import yaml

    from cmp_sim.api import SWEEPABLE, run_sweep

    if args.parameter not in SWEEPABLE:
        print(f"cannot sweep '{args.parameter}'. available: {sorted(SWEEPABLE)}",
              file=sys.stderr)
        return 2
    if args.steps < 2:
        print("--steps must be at least 2", file=sys.stderr)
        return 2

    # The sweep overrides the raw config dict, so the YAML is loaded directly
    # rather than round-tripped through Recipe and back.
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    load_config(args.config)              # validate it before sweeping
    span = args.to_value - args.from_value
    values = [round(args.from_value + span * i / (args.steps - 1), 6)
              for i in range(args.steps)]
    out = run_sweep({"parameter": args.parameter, "values": values,
                     "recipe": cfg})

    if args.json:
        Path(args.json).write_text(
            json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {args.json}")

    for w in out["warnings"]:
        print(f"!! {w}", file=sys.stderr)
    print(f"{args.parameter:>16} {'RR (A/min)':>12} {'WIWNU %':>9}  "
          f"{'lubrication':<11} {'pad load':<12} profile")
    for pt in out["points"]:
        if "error" in pt:
            print(f"{pt['value']:>16} {'-':>12} {'-':>9}  {pt['error']}")
        else:
            print(f"{pt['value']:>16} {pt['removal_rate_A_per_min']:>12} "
                  f"{pt['wiwnu_percent']:>9}  {pt.get('lubrication', '?'):<11} "
                  f"{pt.get('load_regime', '?'):<12} {pt.get('profile', '')}")
    return 0 if out["n_ok"] else 1


def _cmd_validate(args: argparse.Namespace) -> int:
    """Run the literature backtest (same gate as validate_cli)."""
    from cmp_sim.validate_cli import main as validate_main

    argv = ["--gate", str(args.gate)]
    if args.all_groups:
        argv.append("--all-groups")
    return validate_main(argv)


def _cmd_packs(_args: argparse.Namespace) -> int:
    for name in available_packs():
        print(name)
    return 0


def _cmd_models(_args: argparse.Namespace) -> int:
    from cmp_sim.core.profiles import LAYERS, PROFILES
    print("PROFILES — a bundle of physics layers chosen for a SITUATION, not a film\n")
    print(f"{'name':24s} {'layers':56s} suits")
    print("-" * 110)
    for name, p in sorted(PROFILES.items()):
        suits = "; ".join(f"{k}={'/'.join(v)}" for k, v in p.suits.items()) or "-"
        print(f"{name:24s} {', '.join(p.layers) or '(none)':56s} {suits}")
    print(f"\nlayers: {', '.join(LAYERS)}")
    print("\nauto  — detect the situation and pick the profile that fits it")
    print("aliases: preston -> preston_baseline, gw_preston -> mechanical_screening, "
          "full -> auto")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cmp-sim", description="Physics-based CMP process simulator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run a simulation from a YAML config")
    run.add_argument("config")
    run.add_argument("--out", help="write JSON result here (default: stdout)")
    run.add_argument("--provenance", action="store_true", help="include parameter sources in output")
    run.set_defaults(func=_cmd_run)

    sub.add_parser("packs", help="list available parameter packs").set_defaults(func=_cmd_packs)
    sub.add_parser("models", help="list models/profiles").set_defaults(func=_cmd_models)
    sub.add_parser("profiles", help="alias for 'models'").set_defaults(func=_cmd_models)

    sw = sub.add_parser("sweep", help="vary one parameter across a range")
    sw.add_argument("config", help="YAML config, as for 'run'")
    sw.add_argument("parameter", help="parameter to vary (see --help of 'models')")
    sw.add_argument("from_value", type=float, metavar="FROM")
    sw.add_argument("to_value", type=float, metavar="TO")
    sw.add_argument("--steps", type=int, default=7)
    sw.add_argument("--json", help="also write the full result here")
    sw.set_defaults(func=_cmd_sweep)

    va = sub.add_parser("validate", help="run the literature backtest")
    va.add_argument("--gate", type=float, default=15.0,
                    help="require >=3 in-scope datasets within this MAPE %%")
    va.add_argument("--all-groups", action="store_true")
    va.set_defaults(func=_cmd_validate)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
