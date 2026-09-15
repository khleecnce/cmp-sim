#!/usr/bin/env python3
"""FabSim CLI — 레시피를 넣고 웨이퍼 결과를 받는다.

  python -m sim.cli --pack cu_h2o2_bta --time 60
  python -m sim.cli --pressure 3.0 --rpm-wafer 60 --rpm-platen 55 --time 60
  python -m sim.cli --wafer PTW --pattern-density 0.4 --model tier1.pattern_density
  python -m sim.cli --zones 3.0,3.0,4.5 --zone-edges 0.5,0.8,1.0 --json
  python -m sim.cli --list-packs / --list-models

**팩(--pack)이 물성을 소유한다.** 막질·슬러리·패드 상수는 knowledge/params/*.yaml에
있고 코드에는 없다. 다른 조건을 돌리려면 코드가 아니라 팩을 바꿔라(또는 새로 써라).
--pressure 같은 개별 인자를 주면 그 값만 팩을 덮어쓴다.

출력의 ⚠ 항목은 "이 값은 못 낸다/확신 못 한다"는 정직한 보고다. 무시하지 마라.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sim.models  # noqa: F401,E402  (모델 등록 부작용)
from sim.engine import Recipe, simulate, available_models  # noqa: E402
from sim.params import available_packs, load_pack  # noqa: E402


def _floats(s):
    return [float(x) for x in s.split(",")] if s else None


def main() -> int:
    ap = argparse.ArgumentParser(prog="fabsim", description="CMP 시뮬레이터")
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--list-packs", action="store_true", help="파라미터 팩 목록과 출처")
    ap.add_argument("--pack", default="oxide_silica",
                    help="물성 팩 이름 (knowledge/params/*.yaml). 이게 시뮬레이션의 정체성이다")
    ap.add_argument("--model", default="tier2.gw_physical_kp")
    ap.add_argument("--wafer", choices=["NPW", "PTW"], default="NPW")
    ap.add_argument("--film", default=None, help="미지정 시 팩의 막질")
    ap.add_argument("--pressure", type=float, default=None, help="psi (미지정 시 팩값)")
    ap.add_argument("--rpm-wafer", type=float, default=None)
    ap.add_argument("--rpm-platen", type=float, default=None)
    ap.add_argument("--time", type=float, default=60.0, help="초")
    ap.add_argument("--kp", type=float, default=None,
                    help="Preston 계수 [m^2/N] — 미지정 시 팩값(권장)")
    ap.add_argument("--zones", type=str, help="존 압력 psi, 쉼표구분 (예: 3.0,3.0,4.5)")
    ap.add_argument("--zone-edges", type=str, help="존 경계 정규화반경 (예: 0.5,0.8,1.0)")
    ap.add_argument("--edge-amp", type=float, default=0.0, help="엣지 압력 집중 진폭")
    ap.add_argument("--pattern-density", type=float, help="PTW 평균 패턴 밀도 0~1")
    ap.add_argument("--pad-hours", type=float, help="패드 누적 사용시간")
    ap.add_argument("--thickness", type=float, help="초기 막두께 nm (잔막 계산)")
    ap.add_argument("--points", type=int, default=None, help="측정점 수 (미지정 시 팩값)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--profile", action="store_true", help="반경별 프로파일 출력")
    ap.add_argument("--sensitivity", action="store_true",
                    help="인자별 민감도·기여 분해 (무엇을 돌려야 성능이 바뀌나)")
    ap.add_argument("--set", action="append", metavar="KEY=VAL", default=[],
                    help="팩 값을 이번 런에만 덮어쓴다 (예: --set oxidizer_wt_pct=6)")
    a = ap.parse_args()

    if a.list_models:
        for m in available_models():
            print(m)
        return 0

    if a.list_packs:
        for name in available_packs():
            pk = load_pack(name)
            weak = pk.unverified()
            print(f"{name:16s} {pk.description}")
            print(f"{'':16s}   상속: {' → '.join(pk.lineage)} · 값 {len(pk.params)}개"
                  f" · 미검증 {len(weak)}개")
        return 0

    meta = {}
    if a.pattern_density is not None:
        meta["pattern_density"] = str(a.pattern_density)
    if a.pad_hours is not None:
        meta["pad_hours"] = str(a.pad_hours)

    overrides = {}
    for kv in a.set:
        if "=" not in kv:
            print(f"오류: --set 형식은 KEY=VAL 이다 (받은 값: {kv})", file=sys.stderr)
            return 1
        k, v = kv.split("=", 1)
        try:
            overrides[k.strip()] = float(v)
        except ValueError:
            print(f"오류: --set 값은 숫자여야 한다: {kv}", file=sys.stderr)
            return 1

    r = Recipe(pack=a.pack, wafer=a.wafer, film=a.film, pressure_psi=a.pressure,
               rpm_wafer=a.rpm_wafer, rpm_platen=a.rpm_platen, time_s=a.time,
               kp_m_per_pa=a.kp, zone_pressures_psi=_floats(a.zones),
               zone_edges_norm=_floats(a.zone_edges), edge_pressure_amp=a.edge_amp,
               initial_thickness_nm=a.thickness, n_points=a.points, meta=meta,
               pack_overrides=overrides)

    if a.sensitivity:
        from sim.sensitivity import rank_factors, decompose, FACTORS, elasticity
        print(f"■ 민감도 분석 — 팩 {a.pack} · {a.model}")
        print("  탄성도 = 인자 1% 변화당 MRR 변화율(무차원). 레버리지 = 탄성도 × 실무 조절폭.")
        print()
        print(f"  {'인자':20s} {'영역':11s} {'탄성도':>8s} {'레버리지':>9s}  판정")
        print("  " + "-" * 74)
        for s_ in rank_factors(r, model=a.model):
            warn = "" if s_.stable else " ⚠"
            print(f"  {s_.factor.label:20s} {s_.factor.domain:11s} "
                  f"{s_.elasticity:+8.3f} {s_.leverage:9.3f}  {s_.direction()}{warn}")
        print()
        print("  ⚠ 민감도 0의 네 가지 의미를 구분하라:")
        print("     ★정점  = 이미 최적. 어느 쪽으로 움직여도 나빠진다")
        print("     상쇄됨 = 모델 구조상 답할 수 없다(실데이터 캘리브레이션 필요)")
        print("     미모델링 = 물리가 아직 엔진에 없다. '영향 없음'이 아니다")
        print()
        print("  [MRR vs 균일도 상충]")
        for f in FACTORS:
            ea = elasticity(r, f, metric="mrr", model=a.model)
            eb = elasticity(r, f, metric="ttv", model=a.model)
            if not ea or not eb or abs(ea.elasticity) < 1e-3:
                continue
            mark = "★ 양쪽 개선" if (ea.elasticity > 0 and eb.elasticity < 0) else ""
            print(f"    {f.label:20s} MRR {ea.elasticity:+7.3f} / TTV {eb.elasticity:+7.3f}  {mark}")
        if overrides or a.pressure is not None:
            print()
            print("  [기여 분해 — 팩 기본 조건 대비]")
            contribs, total, m_cur = decompose(r, model=a.model)
            print(f"    전체 {total:.3f}배 (MRR {m_cur:.1f} nm/min)")
            for c in contribs:
                print(f"    {c.label:20s} [{c.domain:11s}] ×{c.factor_x:6.3f}")
        return 0

    try:
        res = simulate(r, model=a.model)
    except FileNotFoundError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    except KeyError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    if a.json:
        out = res.summary()
        if a.profile:
            out["radius_mm"] = (res.radius_m * 1000).round(2).tolist()
            out["mrr_nm_per_min"] = res.mrr_nm_per_min.round(3).tolist()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    m = res.metrics
    basis = "잔막" if res.remaining_nm is not None else "제거량"
    rr = r.resolve()
    print(f"■ FabSim — {a.model} · 팩 {res.pack}")
    print(f"  입력: {rr.wafer}/{rr.film} · {rr.pressure_psi:g} psi · "
          f"웨이퍼 {rr.rpm_wafer:g}rpm / 플래튼 {rr.rpm_platen:g}rpm · {rr.time_s:g}s")
    if rr.zone_pressures_psi:
        print(f"        존압력 {rr.zone_pressures_psi} psi @ {rr.zone_edges_norm}")
    mrr = res.mrr_nm_per_min
    print(f"\n  제거율   평균 {np.mean(mrr):8.2f} nm/min  "
          f"(min {np.min(mrr):.2f} / max {np.max(mrr):.2f})")
    print(f"  제거량   평균 {np.mean(res.removed_nm):8.2f} nm ({rr.time_s:g}초)")
    if res.remaining_nm is not None:
        print(f"  잔막     평균 {np.mean(res.remaining_nm):8.2f} nm "
              f"(초기 {rr.initial_thickness_nm:g} nm)")
    print(f"\n  균일도 — {basis} 기준 ({m.n_points}pt)")
    print(f"    정의: {m.definition.split('|')[0].strip()}")
    print(f"    TTV          {m.ttv_nm:8.3f} nm")
    print(f"    radial range {m.radial_range_pct:8.3f} %   (문헌default, 방위각평균반경프로파일)")
    print(f"    radial(관행) {m.radial_maxring_range_nm:8.3f} nm  (링 #{m.radial_maxring_range_ring}, 회사관행)")
    print(f"    CV           {m.cv_pct:8.3f} %")
    print(f"    WIWNU(½R)    {m.wiwnu_halfrange_pct:8.3f} %   "
          f"WIWNU(3σ) {m.wiwnu_3sigma_pct:.3f} %")

    미산출 = [k for k, v in (("조도 Ra", res.roughness_ra_nm),
                          ("dishing", res.dishing_nm),
                          ("erosion", res.erosion_nm),
                          ("금속오염", res.metal_contamination),
                          ("결함밀도", res.defect_density)) if v is None]
    if 미산출:
        print(f"\n  미산출: {', '.join(미산출)} — 담당 에이전트 학습 대기 중")
    if res.notes:
        print("\n  ⚠ 모델 한계 보고:")
        for n in res.notes:
            print(f"    · {n}")
    if a.profile:
        print("\n  반경 프로파일 (mm → nm/min)")
        for rr, vv in zip(res.radius_m[::8] * 1000, res.mrr_nm_per_min[::8]):
            bar = "█" * int(vv / max(res.mrr_nm_per_min) * 40)
            print(f"    {rr:6.1f}  {vv:8.2f}  {bar}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
