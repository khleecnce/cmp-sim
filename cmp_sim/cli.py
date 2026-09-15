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
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
