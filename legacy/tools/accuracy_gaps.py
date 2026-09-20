#!/usr/bin/env python3
"""정확도 갭 랭킹 — "다음에 뭘 채워야 예상값이 정확해지나"를 한 줄로 답한다.

사용자 지시 (2026-09-08):
  "지속적으로 리서치 진행하고 베이스 데이터 채워. 그걸 바탕으로 실제 시뮬레이션 툴하고
   연결해서 정확한 예상값을 뽑아낼수 있도록 시뮬레이터 제작해"

왜 이 도구인가
──────────────
크론 7개가 1년 가까이 "단원 이수"를 생산했지만 엔진 연결률은 9%였다. 학습량이 아니라
**엔진이 반응하는가**가 목표여야 한다. 이 도구는 매 회차 크론이 첫 명령으로 돌려서
가장 값어치 있는 갭 하나를 받아 간다. 순서는 사람이 정하지 않고 실측이 정한다.

갭의 종류 (우선순위 순)
  0b. RESPONSE_GATED — 모델이 그 구간을 "근거 없음"으로 **선언**했다(예측 포기).
                         결함이 아니라 데이터 과제 → score 80
  0. RESPONSE_CONFLICT — 인자를 움직였을 때 모델이 문헌과 **반대 방향**을 가리킨다.
                         부정확한 게 아니라 위험하다 → 최우선 (tools/response_map.py)
  1. VALIDATION  — 팩에 유의한 held-out 데이터가 없다 → 정확한지 알 수조차 없다
  1b. RESPONSE_DEAD / RESPONSE_MISSING — 문헌은 그 인자로 결과가 변한다는데 모델은
                         무반응이거나 팩에 칸조차 없다
  2. UNMODELED   — 사용자가 만지는 입력인데 팩터가 미모델링 (κ/χ/ψ/τ/Δ/S)
  3. UNWIRED     — UI에 있는 슬라이더(pk 있음)인데 --sensitivity 탄성도 0
  4. RECORDED    — UI에서 기록만 되는 필드(pk:null) — 문헌 모델 자체가 없음
  5. CONFIDENCE  — 팩 파라미터가 estimated/unverified — 값은 있으나 근거가 약함
  6. BIAS        — 백테스트 계통편향 > 2배 → 절대값 못 씀

출력: 사람이 읽는 표 + `--next`로 1건 JSON(크론 브리프용) + `--json` 전체.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FACTOR_INPUTS = {   # 팩터 → 그 팩터를 살리려면 팩에 필요한 파라미터(문헌 근거 필요)
    "psi":   ["inhibitor_mM", "inhibitor_ref_mM", "passivation_k"],
    "delta": ["abrasive_d99_nm", "scratch_threshold_nm", "aggregate_ratio"],
    # 2026-09-13: pad_usage_hours/pad_wafer_count/disk_usage_hours는 스코프에서
    # 제외했다(컨디셔너 구조 변수가 팩에 없어 어느 감쇠율을 쓸지 근거 없음 —
    # EVIDENCE-RULES 판정#8, sim/factors.py _f_stab 주석 참고). 남은 드라이버(time_s)
    # 만으로 이 팩터는 "modeled"다.
    "stab":  [],
    "chi":   ["slurry_ph", "ph_ref", "ph_peak", "oxidizer_wt_pct"],
    "kappa": ["abrasive_wt_pct", "abrasive_size_nm", "pad_hardness_shore_d"],
    # 2026-09-13: groove_depth_mm·groove_pitch_mm은 스코프에서 제외했다(Wei/Kim/Guo
    # 3편 모두 배수 관계가 그래프 이미지로만 존재 — EVIDENCE-RULES §3회차 규칙, sim/factors.py
    # _f_tau 주석 참고). 남은 두 드라이버가 전부 반영되면 이 팩터는 "modeled"다.
    "tau":   ["groove_width_um", "pad_porosity_pct"],
}


def _packs():
    from sim.params import available_packs
    return [p for p in available_packs() if p != "base"]


def gaps_validation():
    """유의한 held-out이 없는 팩."""
    out = []
    ds_dir = ROOT / "validation" / "datasets"
    by_pack = defaultdict(list)
    for f in ds_dir.glob("*.yaml"):
        if f.name.startswith("_"):
            continue
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if d.get("used_for_calibration") or d.get("in_scope") is False:
            continue
        pk = d.get("pack") or (d.get("recipe") or {}).get("pack")
        n = len(d.get("conditions") or d.get("points") or [])
        by_pack[pk].append((f.stem, n))
    for p in _packs():
        sets = by_pack.get(p, [])
        sig = [s for s in sets if s[1] >= 4]
        if not sig:
            out.append({
                "kind": "VALIDATION", "pack": p, "score": 100,
                "what": f"팩 '{p}'에 n≥4 held-out 데이터셋이 0건 (보유 {len(sets)}건, 전부 n<4)",
                "action": f"특허 실시예·논문 SI에서 {p} 조성-MRR DOE(n≥4, 조건 변화 1축 이상)를 "
                          f"validation/datasets/에 추가. overrides:에 조성을 반드시 넣어라. "
                          f"tools/patent_mine.py 우선.",
                "why": "검증 데이터 없이는 정확한지 틀린지 알 수 없다 — 다른 모든 갭보다 먼저",
            })
    return out


def gaps_unmodeled_and_confidence():
    from sim.engine import Recipe, simulate
    from sim.params import load_pack
    out = []
    for p in _packs():
        try:
            r = simulate(Recipe(pack=p))
        except Exception as e:
            out.append({"kind": "BROKEN", "pack": p, "score": 200,
                        "what": f"simulate 실패: {type(e).__name__}: {str(e)[:80]}",
                        "action": "팩 파라미터 보강 또는 엔진 수정", "why": "돌지 않으면 아무것도 못 한다"})
            continue
        for k, f in (r.factors or {}).items():
            if f.status == "unmodeled":
                need = FACTOR_INPUTS.get(k, [])
                out.append({
                    "kind": "UNMODELED", "pack": p, "factor": k, "symbol": f.symbol, "score": 80,
                    "what": f"{f.symbol} {f.name} 미모델링 ({p})",
                    "action": f"문헌에서 {f.name} 정량 관계(기준 조건 대비 배수) 확보 → 팩에 "
                              f"{need} 중 필요한 것 추가(출처 필수) → sim/factors.py _f_{k}에 항 추가 "
                              f"→ 기준 1.0 테스트 → MRR_COUPLED 편입 여부는 실측이 지지할 때만",
                    "why": "사용자가 만지는 축인데 결과가 안 변한다 — 도구의 존재 이유가 빠져 있다",
                })
            elif f.status == "partial":
                out.append({
                    "kind": "PARTIAL", "pack": p, "factor": k, "symbol": f.symbol, "score": 40,
                    "what": f"{f.symbol} {f.name} 부분 모델링 — terms={list(f.terms.keys())} ({p})",
                    "action": f"빠진 드라이버를 문헌으로 채워라. 현재 drivers={list(f.drivers.keys())}",
                    "why": "일부 입력만 반응",
                })
        # confidence
        try:
            pk = load_pack(p)
            weak = [k for k, prm in pk.params.items()
                    if prm.confidence in ("estimated", "unverified", "unknown")]
            if weak:
                out.append({
                    "kind": "CONFIDENCE", "pack": p, "score": 30 + min(len(weak), 20),
                    "what": f"{p}: confidence estimated/unverified 파라미터 {len(weak)}개 — {weak[:6]}",
                    "action": "각 파라미터의 1차 출처(DOI/특허)를 찾아 값 대조 → confidence 승격. "
                              "다르면 값을 고치고 노트에 차이를 남겨라.",
                    "why": "값은 있지만 근거가 약해 예상값을 신뢰할 수 없다",
                })
        except Exception:
            pass
    return out


def gaps_unwired_ui():
    """studio3d.html의 필드 중 pk 있는데 dead 배지가 붙은 것 / pk:null 기록 전용."""
    out = []
    html = (ROOT / "sim" / "web" / "studio3d.html").read_text(encoding="utf-8")
    for m in re.finditer(r'\{k:"([a-z0-9_]+)",\s*l:"([^"]+)"[^}]*?pk:(null|"[a-z0-9_]+")[^}]*?(dead|weak):"([^"]{0,90})', html):
        key, label, pk, kind, note = m.groups()
        if pk == "null":
            out.append({"kind": "RECORDED", "field": key, "score": 25,
                        "what": f"UI '{label}' 는 기록만 됨 (엔진 소비 항 없음)",
                        "action": f"문헌에서 {label}→성능 정량 관계를 찾아라. 있으면 팩 키 신설+팩터 항, "
                                  f"없으면 그대로 두고 '문헌 없음'을 노트로 남겨라(지어내지 마라)",
                        "why": note})
        elif kind == "dead":
            out.append({"kind": "UNWIRED", "field": key, "score": 60,
                        "what": f"UI '{label}' 슬라이더가 엔진에 미연결", "action": "위 UNMODELED 항목과 동일 절차",
                        "why": note})
    return out


def gaps_bias():
    out = []
    try:
        sys.path.insert(0, str(ROOT / "validation"))
        import backtest  # noqa
        res = backtest.run_all()
    except Exception:
        res = None
    if not res:
        return out
    for r in res:
        sb = r.scale_factor
        # rank_only: 데이터셋 자신의 절대값이 다른 문헌과 어긋난다는 판정이
        # 근거와 함께 기록된 경우다(validation/backtest.py 참조). 그런 데이터셋의
        # 편향은 우리 Kp 갭이 아니므로 갭 랭킹에 올리지 않는다 — 올리면 크론이
        # 매 회차 같은 종결 판정을 다시 뒤집으려 든다.
        if getattr(r, "rank_only", False):
            continue
        # used_for_calibration: 이 데이터셋으로 팩 파라미터를 역산했으므로 같은
        # 데이터로 그 파라미터가 "틀렸다"고 재판정하면 순환이다(EVIDENCE-RULES
        # 판정#58). validation/backtest.py 의 held-out 집계(`held = [... not
        # r.used_for_calibration]`)가 이미 같은 이유로 이 필터를 쓴다 — 갭
        # 랭커만 빠뜨리면 held-out 지표와 다른 기준으로 같은 데이터를 이중 판정하게 된다.
        if getattr(r, "used_for_calibration", False):
            continue
        if sb is not None and (sb > 2 or sb < 0.5) and (r.p_value or 1) < 0.05 and r.in_scope:
            out.append({"kind": "BIAS", "dataset": r.dataset,
                        "score": 50, "what": f"{r.dataset}: 순위는 맞는데(p={r.p_value:.3f}) 절대값 {sb:.2f}배 계통편향",
                        "action": "Kp 또는 기준 조건(ref)이 그 문헌 조건과 다름. 팩의 Kp 출처 조건과 "
                                  "데이터셋 조건을 대조하고, 다르면 별도 팩(base 상속)로 분리",
                        "why": "절대 MRR 예상값을 내려면 편향을 없애야 한다"})
    return out


def gaps_response():
    """응답 갭 — 인자를 움직였을 때 결과가 문헌과 같은 방향으로 가는가.

    사용자 지시(2026-09-08): "특정 슬러리 하나하나 구분하는것보단 어떤 요인이 결과를
    어떻게 바꾸는지 파악하는데 중점을 둬". 개발 도구로서 가장 나쁜 고장은 "이 슬러리를
    못 맞힘"이 아니라 **"인자를 올리라고 했는데 실제로는 내려야 함"**이다. 그래서
    CONFLICT는 VALIDATION보다도 위에 둔다.
    """
    out = []
    try:
        from tools.response_map import build
        from sim.params import available_packs
        rep = build([p for p in available_packs() if p != "base"])
    except Exception as e:
        return [{"kind": "BROKEN", "score": 190,
                 "what": f"response_map 실행 실패: {type(e).__name__}: {str(e)[:80]}",
                 "action": "tools/response_map.py 수정", "why": "응답 방향 검사가 꺼져 있다"}]
    for r in rep["rows"]:
        v = r["verdict"]
        if v == "CONFLICT":
            out.append({"kind": "RESPONSE_CONFLICT", "pack": r["pack"], "score": 120,
                        "what": f"{r['pack']}/{r['label']}: 모델 {r['model_shape']} vs 문헌 "
                                f"{r['lit_shape']} (n={r['lit_n']}, {', '.join(r['lit_sets'])})",
                        "action": "sim/factors.py의 해당 항을 그 구간에서 문헌 형상을 재현하도록 "
                                  "고쳐라. 정점을 단조로 근사한 경우가 가장 흔하다.",
                        "why": "모델이 개발자에게 틀린 방향을 가리킨다 — 부정확한 게 아니라 위험하다"})
        elif v == "SPLIT":
            # 문헌이 조건에 따라 반대 방향을 준다 → 모델 방향을 뒤집는 게 아니라
            # 팩/레짐을 쪼개야 하는 갱이다. CONFLICT 로 배차하면 크론이 멀쩡한
            # 항의 부호를 뒤집어 다른 레짐을 망친다(2026-09-20 US8501625B2 사례).
            out.append({"kind": "RESPONSE_SPLIT", "pack": r["pack"], "score": 110,
                        "what": f"{r['pack']}/{r['label']}: 문헌이 조건별로 방향이 갈린다 "
                                f"(n={r['lit_n']}, {', '.join(r['lit_sets'])}) — 모델은 "
                                f"{r['model_shape']} 단일 레짐",
                        "action": "부호를 뒤집지 마라. 층을 가르는 조건(압력·pH·착화제 등)을 "
                                  "찾아 팩을 분리하거나 상호작용 항을 유도하라. 근거가 "
                                  "없으면 EVIDENCE-RULES에 레짐 분기로 기록하고 --skip.",
                        "why": "평균내면 어느 레짐에서도 안 맞는 제3의 곡선이 된다"})
        elif v == "GATED":
            # 모델이 그 구간을 스스로 "근거 없음"으로 선언했다. 코드 결함이
            # 아니므로 CONFLICT(120)/SPLIT(110)/DEAD(95)보다 낮게 둔다 —
            # 처방이 "부호를 고쳐라"가 아니라 "그 레짐의 1차 데이터를 가져와라"다.
            out.append({"kind": "RESPONSE_GATED", "pack": r["pack"], "score": 80,
                        "what": f"{r['pack']}/{r['label']}: 모델이 이 구간을 "
                                f"'근거 없는 레짐'으로 선언해 예측하지 않는다",
                        "action": r["note"] or ("해당 레짐의 1차 데이터를 확보해 "
                                                "계수를 선언하라 — 이웃 레짐 계수를 "
                                                "빌려 오지 마라(부호가 반대일 수 있다)"),
                        "why": "개발자가 그 조건을 물어도 도구가 답을 못 한다 — "
                               "다만 틀린 답을 주는 것보다는 낫다"})
        elif v == "DEAD":
            out.append({"kind": "RESPONSE_DEAD", "pack": r["pack"], "score": 95,
                        "what": f"{r['pack']}/{r['label']}: 문헌은 {r['lit_shape']}("
                                f"n={r['lit_n']})인데 모델 무반응",
                        "action": r["note"] or "해당 항을 엔진에 구현하라",
                        "why": "실측이 변한다고 말하는 축인데 도구가 답을 못 한다"})
        elif v == "MISSING":
            out.append({"kind": "RESPONSE_MISSING", "pack": r["pack"], "score": 85,
                        "what": f"knowledge/params/{r['pack']}.yaml에 '{r['key']}' 칸 없음 "
                                f"(문헌 {r['lit_shape']}, n={r['lit_n']})",
                        "action": f"{', '.join(r['lit_sets'])}의 값을 source와 함께 팩에 추가",
                        "why": "문헌이 지지하는 인자인데 사용자가 만질 칸조차 없다"})
    return out


def _dedupe_factors(g):
    """같은 팩터가 팩마다 미모델링이면 한 건으로 묶는다 — 고칠 곳은 factors.py 한 곳이다."""
    merged, out = {}, []
    for x in g:
        if x["kind"] in ("UNMODELED", "PARTIAL") and x.get("factor"):
            key = (x["kind"], x["factor"])
            if key in merged:
                merged[key]["packs"].append(x["pack"])
                merged[key]["score"] += 5      # 여러 팩에 걸칠수록 값어치 ↑
                merged[key]["what"] = f"{x['symbol']} {x['what'].split(' ', 1)[1].split(' (')[0]} ({len(merged[key]['packs'])} packs: {', '.join(merged[key]['packs'])})"
                continue
            x = dict(x); x["packs"] = [x.pop("pack")]
            merged[key] = x
        out.append(x)
    return out


def gaps_completion():
    """COMPLETION.md 기준 미충족 — 완성 목표가 선언된 뒤엔 이것이 최상위다 (2026-09-10)."""
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import completion
        return completion.gaps()
    except Exception as e:
        return [{"kind": "COMPLETION-ERR", "score": 1, "what": f"completion.py 실패: {e}", "action": "", "why": ""}]


def collect():
    g = (gaps_completion() + gaps_validation() + gaps_response() + gaps_unmodeled_and_confidence()
         + gaps_unwired_ui() + gaps_bias())
    g = _dedupe_factors(g)
    g.sort(key=lambda x: -x["score"])
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", action="store_true", help="최우선 갭 1건 JSON (크론 브리프용)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--kind", help="종류 필터")
    ap.add_argument("--skip", nargs="*", default=[], help="이미 진행 중인 갭 what 부분문자열 (건너뜀)")
    a = ap.parse_args()
    g = collect()
    if a.kind:
        g = [x for x in g if x["kind"] == a.kind]
    if a.skip:
        g = [x for x in g if not any(s in x["what"] for s in a.skip)]
    if a.next:
        print(json.dumps(g[0] if g else {"kind": "NONE", "what": "갭 없음"}, ensure_ascii=False, indent=2))
        return
    if a.json:
        print(json.dumps(g, ensure_ascii=False, indent=2))
        return
    kinds = defaultdict(int)
    for x in g:
        kinds[x["kind"]] += 1
    print(f"정확도 갭 {len(g)}건 — " + ", ".join(f"{k} {v}" for k, v in kinds.items()))
    print("(점수 높은 순 = 먼저 채울 순서. 크론은 --next 로 1건을 받아 간다)\n")
    for i, x in enumerate(g[:30], 1):
        print(f"{i:2}. [{x['score']:3}] {x['kind']:10} {x['what']}")
        print(f"          → {x['action'][:150]}")


if __name__ == "__main__":
    main()
