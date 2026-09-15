"""
Son & Lee 2021 (Appl. Sci. 11(8), 3521, doi.org/10.3390/app11083521) 실측 기반 —
누적 컨디셔닝 시간에 따른 그루브 깊이 소진을 두 번째(glazing과 독립인) 패드 실패
모드로 다룬다. 컷레이트 c(μm/h)로 누적마모 D(t)=c·t를 적산하고, D(t)가 초기 그루브
깊이(패드 사양, US20120225612A1 배경기술상 통상 750-1250 μm)에 도달하면 "그루브
소진"으로 판정한다.

지식 근거: knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md
(pad-lifecycle Lv2-2) §2, §5 (A)(B). 이 모듈은 그 노트 §5 verify (A)(B) 블록의 로직을
순수함수로 옮긴 것이며, 새로운 문헌 숫자를 도입하지 않는다. §5 (D)의 경제성(웨이퍼당
비용) 계산은 이 노트의 산술 추정 수준이라 여기 옮기지 않는다(PROFILE.md 요청에 명시된
금지 사항, 필요시 리포팅 레이어에서만).

주의: 컷레이트 c는 컨디셔너 접촉 방식(풀컨택트 vs 분할)에 따라 거의 2배 차이 난다
(Case I 43.4 μm/h vs Case II 22.2 μm/h) — 상수로 하드코딩하지 않고 함수 인자로만
받는다. 그루브 깊이 초기값도 패드 사양(제조사·모델)마다 다르므로 하드코딩하지 않는다
(문헌 통상 범위 750-1250 μm, US20120225612A1 배경기술은 참고용일 뿐).

glazing 기반 EOL(예: pad_glazing_jeong2024.py 계열에서 계산)과 OR 조건으로 결합해
"둘 중 먼저 도달하는 쪽이 교체 시점"으로 판정한다 — Son & Lee(2021) Case I처럼 두
실패모드가 같은 시점(16h)에 겹치는 경우를 놓치지 않기 위함(replacement_time_hours 참조).

실행: python3 pad_groove_eol.py -> self-test 결과 stdout.
"""


def cumulative_wear_um(cut_rate_um_per_h, hours):
    """D(t) = c*t [μm]. cut_rate_um_per_h: 패드 컷레이트 [μm/h], hours: 누적 컨디셔닝 시간 [h]."""
    return cut_rate_um_per_h * hours


def groove_exhausted(cumulative_wear_um, initial_groove_depth_um):
    """누적마모가 초기 그루브 깊이 이상이면 그루브 소진(True)."""
    return cumulative_wear_um >= initial_groove_depth_um


def groove_eol_hours(cut_rate_um_per_h, initial_groove_depth_um):
    """그루브가 소진되는 시각 [h] = initial_groove_depth_um / cut_rate_um_per_h (D(t)=c*t의 역산)."""
    return initial_groove_depth_um / cut_rate_um_per_h


def replacement_time_hours(glazing_eol_hours, groove_eol_hours):
    """glazing과 그루브 소진, 두 실패모드 중 먼저 도달하는 쪽(OR 조건) = min(...).

    glazing_eol_hours는 이 함수의 입력으로만 받는다 — glazing 판정 로직 자체는
    이 모듈이 아니라 호출자(예: pad_glazing_jeong2024.py 계열)가 계산해서 넘긴다.
    """
    return min(glazing_eol_hours, groove_eol_hours)


def _self_test():
    results = []

    # --- Test 1: Case I 누적마모 43.4 μm/h * 16h ~= 694 μm ---
    cum_I = cumulative_wear_um(43.4, 16.0)
    ok1 = bool(abs(cum_I - 694.4) < 0.5)
    results.append(("Case I: cumulative_wear_um(43.4, 16) ~= 694 μm",
                     ok1, f"cum={cum_I:.1f} μm (목표 694.4 ±0.5)"))

    # --- Test 2: Case II 누적마모 22.2 μm/h * 20h ~= 444 μm ---
    cum_II = cumulative_wear_um(22.2, 20.0)
    ok2 = bool(abs(cum_II - 444.0) < 0.5)
    results.append(("Case II: cumulative_wear_um(22.2, 20) ~= 444 μm",
                     ok2, f"cum={cum_II:.1f} μm (목표 444.0 ±0.5)"))

    # --- Test 3: Case I 694 μm은 통상 그루브 깊이 하한 750 μm의 0.5~1.3배 범위 ---
    groove_lo = 750.0
    ok3 = bool(0.5 * groove_lo < cum_I < 1.3 * groove_lo)
    results.append(("Case I 누적마모(694 μm)가 그루브 깊이 하한(750 μm)과 물리적으로 정합",
                     ok3, f"cum_I={cum_I:.1f} μm, 0.5*750={0.5*groove_lo:.1f}, 1.3*750={1.3*groove_lo:.1f}"))

    # --- Test 4: Case II 444 μm < 750 μm (20h에도 그루브 잔존) ---
    ok4 = bool(groove_exhausted(cum_II, groove_lo) is False)
    results.append(("groove_exhausted(444, 750) == False (Case II는 20h에도 그루브 잔존)",
                     ok4, f"groove_exhausted={groove_exhausted(cum_II, groove_lo)}"))

    # --- Test 5: 경계 넘김 케이스 ---
    ok5 = bool(groove_exhausted(800.0, groove_lo) is True)
    results.append(("groove_exhausted(800, 750) == True (경계 넘김)",
                     ok5, f"groove_exhausted={groove_exhausted(800.0, groove_lo)}"))

    # --- Test 6: groove_eol_hours(43.4, 750) ~= 17.28h ---
    eol_I = groove_eol_hours(43.4, groove_lo)
    ok6 = bool(abs(eol_I - 17.28) < 0.01)
    results.append(("groove_eol_hours(43.4, 750) ~= 17.28h",
                     ok6, f"eol={eol_I:.3f} h (목표 17.28 ±0.01)"))

    # --- Test 7: replacement_time_hours OR 조건 — glazing이 더 이름 ---
    rep7 = replacement_time_hours(15.0, eol_I)
    ok7 = bool(abs(rep7 - 15.0) < 1e-9)
    results.append(("replacement_time_hours(15.0, groove_eol=17.28) == 15.0 (glazing이 먼저)",
                     ok7, f"replacement={rep7:.3f} h"))

    # --- Test 8: replacement_time_hours OR 조건 — 그루브가 더 이름 ---
    rep8 = replacement_time_hours(20.0, eol_I)
    ok8 = bool(abs(rep8 - eol_I) < 1e-9)
    results.append(("replacement_time_hours(20.0, groove_eol=17.28) == groove_eol (그루브가 먼저)",
                     ok8, f"replacement={rep8:.3f} h"))

    # --- Test 9: 두 실패모드가 근접 시점에 겹치는 경우 (Son & Lee Case I, 둘 다 ~16h) ---
    glazing_eol_caseI = 16.0
    groove_eol_caseI = groove_eol_hours(43.4, groove_lo)
    rep9 = replacement_time_hours(glazing_eol_caseI, groove_eol_caseI)
    ok9 = bool(abs(rep9 - glazing_eol_caseI) < 1e-9 and abs(glazing_eol_caseI - groove_eol_caseI) < 2.0)
    results.append(("두 실패모드가 근접(Case I ~16h vs groove_eol 17.28h)해도 OR 조건이 놓치지 않음",
                     ok9, f"glazing_eol={glazing_eol_caseI:.2f}h, groove_eol={groove_eol_caseI:.2f}h, "
                          f"replacement={rep9:.2f}h"))

    print("=== pad_groove_eol.py self-test ===")
    n_pass = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        print(f"[{status}] {name}\n    {detail}")
    print(f"\n{n_pass}/{len(results)} PASS")
    return n_pass == len(results)


if __name__ == "__main__":
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
