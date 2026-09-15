"""
디스크 돌출 높이 분포(protrusion_pdf)와 최고 그릿 기준 침투 깊이(engage_depth)로부터
"활성 그릿 비율" f_active와 유효 절삭점 수 N_eff를 계산하는 순수함수 모듈.

지식 근거: knowledge/equipment/cvd-diamond-disk-patterned-grit-array.md
(disk-design Lv3-1) §2 python verify 블록, §3.2, §7, §8 "구현 요청" 항목 4. 이 모듈은
그 노트의 verify 블록이 이미 재현한 균일분포 오더 추정과 문헌 상수만 옮긴 것이며, 새로운
문헌 숫자를 도입하지 않는다.

출처:
- 균일분포 f_a = engage_depth / (h_hi - h_lo), 종래 전착 디스크 그릿 높이 분포 40~90 µm
  (Fig.1a 히스토그램) — Kim & Kang (2011), Int. J. Machine Tools & Manufacture 51, 565-568,
  DOI: 10.1016/j.ijmachtools.2011.02.008, 노트 §2 verify 블록.
- CVD 패턴 돌기 디스크는 돌기 높이가 일정(Fig.1b, 단일 높이) → f_a ≈ 1.0(사실상 전체 활성) —
  같은 Kim & Kang (2011), 노트 §2·§7.
- RCADD/CDD 유효 팁 비 ≈2.8배(스크래치 선 수/그릿 수: 484/10,000 vs 432/25,000, Fig.8) —
  Tsai et al. (2014), Mathematical Problems in Engineering 2014, 913812,
  DOI: 10.1155/2014/913812, 노트 §3.2 verify 블록.
- 종래 f_a 25~30%(정규화 높이 0.5 이상 기준, Fig.6), "<10%"(Tsai 2014 §2 서술) — 이 두 값은
  균일분포 모델의 "정답"이 아니라 산출값이 같은 오더(10~30%)에 드는지 확인하는 검증
  참고치다(US8657652B2, Saint-Gobain Abrasives, 노트 §6.1·§7).

주의: engage_depth(δ)는 하중·패드 경도의 함수이며 노트가 명시하듯 "가정값, 미검증"이다.
이 모듈은 δ를 함수 인자로만 받으며 기본값을 두지 않는다(PROFILE.md 구현요청 §4 명시).
"measured histogram" protrusion_pdf 옵션은 지금 실측 데이터가 없어 구현하지 않는다.

실행: python3 disk_active_grit_fraction.py -> self-test 결과 stdout.
"""

# knowledge/equipment/cvd-diamond-disk-patterned-grit-array.md §2 verify 블록.
# Kim & Kang 2011 Fig.1a: 종래 Ni 전착 80 mesh 디스크 그릿 높이 분포 범위(µm).
_UNIFORM_H_LO_DEFAULT_UM = 40.0
_UNIFORM_H_HI_DEFAULT_UM = 90.0


def active_fraction_uniform(h_lo, h_hi, engage_depth):
    """돌출 높이가 [h_lo, h_hi] 균일분포라고 가정할 때, 최고 그릿(h_hi) 기준 engage_depth
    만큼 패드가 침투하면 h > h_hi - engage_depth 인 그릿만 접촉한다. 균일분포에서
    P(h > h_hi - engage_depth) = engage_depth / (h_hi - h_lo).

    노트 §2 verify 블록의 재현: h_lo=40, h_hi=90 µm일 때 engage_depth 5/10/15 µm →
    f_a 10%/20%/30%(Kim & Kang 2011 Fig.1a 분포 범위, 노트 §2). engage_depth가 [0, h_hi-h_lo]
    범위를 벗어나면 [0, 1]로 clamp한다(음수 침투는 물리적으로 없으므로 ValueError)."""
    if engage_depth < 0:
        raise ValueError("engage_depth는 음수일 수 없다")
    span = h_hi - h_lo
    f_a = engage_depth / span
    return max(0.0, min(1.0, f_a))


def active_fraction_single_height():
    """CVD 패턴 돌기 디스크는 돌기 높이가 일정(Kim & Kang 2011 Fig.1b, 단일 높이) — 패드가
    침투 깊이만큼 눌리면 전체 돌기가 동시에 접촉하므로 사실상 전체가 활성이다. f_a = 1.0을
    상수로 반환한다(노트 §2 서술, §7 표 "≈100%(단일 높이)")."""
    return 1.0


def n_effective(n_total, f_active):
    """유효 절삭점 수 N_eff = f_active * n_total (노트 §7.3 "GW 파라미터로의 번역")."""
    return f_active * n_total


def known_effective_ratios():
    """문헌 검증용 상수 — 하드코딩 값이 아니라 원자료(스크래치 선 수, 그릿 총수)에서
    직접 나눗셈으로 산출한다. Tsai et al. (2014) Fig.8: 아크릴 10 kg 긁기 스크래치 선 수
    RCADD 484개(그릿 10,000개) vs CDD 432개(그릿 25,000개) — "선 수/그릿 수"를 활성 팁
    효율의 대리지표로 삼으면 RCADD/CDD 비 ≈2.8배(노트 §3.2 verify 블록, DOI: 10.1155/2014/913812).

    반환: dict{rcadd_eff, cdd_eff, ratio}."""
    lines_rcadd, grits_rcadd = 484.0, 10000.0
    lines_cdd, grits_cdd = 432.0, 25000.0
    eff_rcadd = lines_rcadd / grits_rcadd
    eff_cdd = lines_cdd / grits_cdd
    return {
        "rcadd_eff": eff_rcadd,
        "cdd_eff": eff_cdd,
        "ratio": eff_rcadd / eff_cdd,
    }


def disk_active_grit_fraction(protrusion_pdf, engage_depth, n_total, h_lo=None, h_hi=None):
    """protrusion_pdf ∈ {"uniform", "single_height"}에 따라 f_a, N_eff를 계산해 반환한다.

    "uniform": h_lo, h_hi(µm)로 균일분포 범위를 받는다(미지정 시 Kim & Kang 2011 Fig.1a
    종래 디스크 실측 범위 40~90 µm를 기본값으로 쓴다 — 이는 실측 문헌값이지 가정값이
    아니므로 engage_depth와 달리 기본값을 둔다).
    "single_height": h_lo, h_hi는 무시하고 f_a=1.0(CVD 패턴 돌기, 노트 §2·§7).
    "measured histogram"(실측 히스토그램) 옵션은 지금 데이터가 없어 미구현이다.

    반환: dict{f_active, n_effective}."""
    if protrusion_pdf == "uniform":
        lo = _UNIFORM_H_LO_DEFAULT_UM if h_lo is None else h_lo
        hi = _UNIFORM_H_HI_DEFAULT_UM if h_hi is None else h_hi
        f_a = active_fraction_uniform(lo, hi, engage_depth)
    elif protrusion_pdf == "single_height":
        f_a = active_fraction_single_height()
    elif protrusion_pdf == "measured histogram":
        raise NotImplementedError(
            "measured histogram 옵션은 실측 돌출 높이 히스토그램 데이터가 아직 없어 미구현이다"
            " (노트 §8 구현 요청 항목4)"
        )
    else:
        raise ValueError(f"알 수 없는 protrusion_pdf: {protrusion_pdf!r}")

    return {
        "f_active": f_a,
        "n_effective": n_effective(n_total, f_a),
    }


def _self_test():
    results = []

    # --- Test 1: 균일분포 f_a 3점(5,10,15 µm) — 노트 §2 verify 그대로 ---
    h_lo, h_hi = 40.0, 90.0
    fracs = [active_fraction_uniform(h_lo, h_hi, e) for e in (5.0, 10.0, 15.0)]
    ok1 = bool(abs(fracs[0] - 0.10) < 1e-9 and abs(fracs[1] - 0.20) < 1e-9 and abs(fracs[2] - 0.30) < 1e-9)
    results.append(("active_fraction_uniform(40,90,{5,10,15}) == {10%,20%,30%}",
                     ok1, f"fracs={fracs}"))

    # --- Test 2: 노트 §2 assert 그대로 재현 (5µm→≥0.05, 15µm→≤0.35) ---
    ok2 = bool(0.05 <= fracs[0] and fracs[2] <= 0.35)
    results.append(("노트 §2 assert 재현: 0.05<=f_a(5µm) and f_a(15µm)<=0.35",
                     ok2, f"f_a(5)={fracs[0]:.3f}, f_a(15)={fracs[2]:.3f}"))

    # --- Test 3: clamp 동작 ---
    over = active_fraction_uniform(40.0, 90.0, 100.0)  # span=50, 100>50 -> clamp 1.0
    ok3 = bool(abs(over - 1.0) < 1e-9)
    results.append(("active_fraction_uniform 상한 clamp(engage_depth>span) == 1.0",
                     ok3, f"f_a={over:.3f}"))

    # --- Test 4: single_height == 1.0 ---
    single = active_fraction_single_height()
    ok4 = bool(abs(single - 1.0) < 1e-9)
    results.append(("active_fraction_single_height() == 1.0 (Kim & Kang 2011 CVD 단일 높이)",
                     ok4, f"f_a={single:.3f}"))

    # --- Test 5: n_effective 산술 ---
    n_eff = n_effective(25000, 0.2)
    ok5 = bool(abs(n_eff - 5000.0) < 1e-9)
    results.append(("n_effective(25000, 0.2) == 5000", ok5, f"n_eff={n_eff:.1f}"))

    # --- Test 6: RCADD/CDD 유효 팁 비 ≈2.8배 (Tsai 2014 Fig.8, 원자료에서 나눗셈으로 산출) ---
    ratios = known_effective_ratios()
    ok6 = bool(2.5 < ratios["ratio"] < 3.0 and abs(ratios["ratio"] - 2.8) < 0.1)
    results.append(("known_effective_ratios()['ratio'] ≈ 2.8 (484/10000 ÷ 432/25000)",
                     ok6, f"ratios={ratios}"))

    # --- Test 7: 종합함수 uniform 모드 ---
    out_uniform = disk_active_grit_fraction("uniform", 10.0, 25000, h_lo=40.0, h_hi=90.0)
    ok7 = bool(abs(out_uniform["f_active"] - 0.20) < 1e-9
               and abs(out_uniform["n_effective"] - 5000.0) < 1e-9)
    results.append(("disk_active_grit_fraction('uniform', 10, 25000, 40, 90) 종합 dict",
                     ok7, f"out={out_uniform}"))

    # --- Test 8: 종합함수 single_height 모드 ---
    out_single = disk_active_grit_fraction("single_height", 10.0, 1300)
    ok8 = bool(abs(out_single["f_active"] - 1.0) < 1e-9
               and abs(out_single["n_effective"] - 1300.0) < 1e-9)
    results.append(("disk_active_grit_fraction('single_height', ...) 종합 dict",
                     ok8, f"out={out_single}"))

    # --- Test 9: measured histogram은 NotImplementedError ---
    try:
        disk_active_grit_fraction("measured histogram", 10.0, 1000)
        ok9 = False
        detail9 = "예외가 발생하지 않음"
    except NotImplementedError:
        ok9 = True
        detail9 = "NotImplementedError 발생 확인"
    results.append(("disk_active_grit_fraction('measured histogram', ...) -> NotImplementedError",
                     ok9, detail9))

    print("=== disk_active_grit_fraction.py self-test ===")
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
