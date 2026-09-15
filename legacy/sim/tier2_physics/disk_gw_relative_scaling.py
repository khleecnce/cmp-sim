"""
디스크 설계 파라미터(그릿 크기·개수·grade·leveled 여부)에서 GW(Greenwood-Williamson)
접촉모델 파라미터(λ, Ra, Rpk)의 "상대 배율"을 계산하는 순수함수 모듈.

지식 근거: knowledge/materials/disk-design-pad-roughness-asperity-relation.md
(disk-design Lv2-2) §3.1-§3.3, §4 "GW 파라미터 초기값 제안". 이 모듈은 그 노트의
python verify 블록이 재현한 멱법칙 지수만 옮긴 것이며, 새로운 문헌 숫자를 도입하지
않는다.

지수 출처:
- Ra ∝ N^-0.23, Rpk ∝ N^-0.62 — Kwon et al. (2013), Tribology International 67, 272-277,
  doi.org/10.1016/j.triboint.2013.08.008, Fig.2 판독값 3점 회귀(노트 §3.1).
- surface finish ∝ D^0.57(전체 구간), 45→125 µm 국소지수 0.71, 125→250 µm 국소지수 0.23
  (포화), leveled 배율 0.57 — Pysher, Goers, Zabasajja (2010), MRS Proc. 1249, E02-04,
  doi.org/10.1557/proc-1249-e02-04, Fig.1 군집 중심 판독(노트 §3.2).
- λ ∝ D^0.3~0.4(고하중 ≈8 lb 근방), λ_rel≈1(저하중 ≈3.6 lb 이하 근방, 그릿 크기 무관) —
  Sun (2009) PhD dissertation, Univ. of Arizona, http://hdl.handle.net/10150/194898,
  Fig.7.4 판독값(노트 §3.3). "0.3~0.4"는 노트 §4 종합이 명시한 작업가설 범위이며 이
  모듈은 중간값 0.35를 기본으로 쓴다(근거 명시, 캘리브레이션 시 조정 가능).

주의: 절대값(η, σ, R의 µm 단위 실측치)은 이 모듈에 넣지 않는다 — 캘리브레이션
파라미터로 남긴다(PROFILE.md 구현요청 §1 명시). 여기 하드코딩하는 것은 멱법칙
지수뿐이다. 노트에 정량이 없는 사용법(예: grade sharp/blunt 전환의 연속 스케일링)은
구현하지 않는다 — grade는 문자열 태그로만 받고 수치 변환은 하지 않는다(Kwon 2013 §2.1은
grade 625/640/925 3점 관찰만 있고 회귀하지 않았다).

실행: python3 disk_gw_relative_scaling.py -> self-test 결과 stdout.
"""

# 125 µm 기준 surface finish 멱법칙 국소지수 전환점(노트 §3.2: 45→125 µm 지수 0.71,
# 125→250 µm 지수 0.23 — 두 구간을 하나의 지수로 뭉개지 않고 노트 수치 그대로 분기).
_SF_SATURATION_D_UM = 125.0
_SF_EXPONENT_BELOW_SATURATION = 0.71
_SF_EXPONENT_ABOVE_SATURATION = 0.23
_SF_LEVELED_MULTIPLIER = 0.57  # 노트 §3.2: leveled 150 µm 실측/멱법칙예측 ≈ 0.57

_RA_EXPONENT_VS_N = -0.23   # Kwon 2013 §3.1, 노트 §3.1 python verify 재현값
_RPK_EXPONENT_VS_N = -0.62  # Kwon 2013 §3.1, 노트 §3.1 python verify 재현값

_LAMBDA_EXPONENT_HIGH_LOAD = 0.35  # Sun 2009 §3.3, 노트 §4 작업가설 0.3~0.4의 중간값


def ra_relative(N_ref, N_target):
    """Ra ∝ N^-0.23 (Kwon 2013 §3.1 멱법칙, 그릿 개수 3점 판독 회귀). 기준 대비 대상의
    Ra 배율 = (N_target/N_ref)^-0.23. 그릿 밀도가 낮을수록 Ra가 커지는 방향(§3.1)과 일치."""
    return (N_target / N_ref) ** _RA_EXPONENT_VS_N


def rpk_relative(N_ref, N_target):
    """Rpk ∝ N^-0.62 (Kwon 2013 §3.1). Ra보다 밀도에 더 민감(노트: Rpk가 Ra보다 2.7배
    민감)."""
    return (N_target / N_ref) ** _RPK_EXPONENT_VS_N


def surface_finish_relative(D_ref, D_target, leveled_target=False, leveled_ref=False):
    """surface finish ∝ D^0.57(전체 구간 회귀), 단 125 µm를 경계로 국소지수가
    0.71(45→125 µm)에서 0.23(125→250 µm, 포화)으로 바뀐다(Pysher 2010 §3.2, 노트가
    임의 판단 대신 이 두 국소지수를 명시). D_ref, D_target 각각 125 µm 기준 아래/위에
    걸쳐 있으면 두 구간을 이어붙여 배율을 계산한다.

    leveled_target/leveled_ref=True이면 해당 디스크에 ×0.57(노트 §3.2, 팁 높이 정렬 효과)을
    적용한다 — leveled는 크기와 독립적인 별도 배율이므로 멱법칙 위에 곱으로 얹는다.
    """
    def _sf_scale_from(D):
        # 125 µm를 기준점으로 삼아 D의 상대 위치를 국소지수로 환산(단조·연속 보장).
        if D <= _SF_SATURATION_D_UM:
            return D ** _SF_EXPONENT_BELOW_SATURATION
        return (_SF_SATURATION_D_UM ** _SF_EXPONENT_BELOW_SATURATION) * (
            (D / _SF_SATURATION_D_UM) ** _SF_EXPONENT_ABOVE_SATURATION
        )

    rel = _sf_scale_from(D_target) / _sf_scale_from(D_ref)
    if leveled_target:
        rel *= _SF_LEVELED_MULTIPLIER
    if leveled_ref:
        rel /= _SF_LEVELED_MULTIPLIER
    return rel


def lambda_relative(D_ref, D_target, high_load=True):
    """λ(높이분포 감쇠길이) 배율. **입력은 ANSI 그릿 메시 번호(예: 100, 325)** — 메시 번호가
    클수록 입자가 작다(역상관). 노트 §3.3/§4는 "그릿 크기 3.25배(325→100 grit)"라고 서술하며
    이는 메시번호 비 325/100=3.25를 그대로 "크기" 배율로 쓴 것이다(325-grit이 더 곱고, 100-grit이
    더 거칠다 = 크다). 따라서 이 함수는 **메시번호가 작을수록(=입자가 클수록) λ가 커지는 방향**으로
    (D_ref/D_target)^exponent를 계산한다 — 직접 D_target/D_ref를 쓰면 방향이 뒤집힌다(메시번호는
    지름의 역수 스케일이므로).

    high_load=True(≈8 lb 근방): λ ∝ (D_ref/D_target)^0.35(Sun 2009 §3.3, 노트 §4 작업가설
    0.3~0.4의 중간값 — Sun 8lb 조건 100-grit λ=6.7 vs 325-grit λ=4.3 µm, 실측비 1.558, 이
    공식 예측 (325/100)^0.35=1.511로 3% 이내 재현).
    high_load=False(≈3.6 lb 이하 근방): 저하중에서는 그릿 크기와 무관하게 다이아 최상단만
    관여해 λ가 같다는 §3.3 재현 결과에 따라 λ_rel=1.0을 반환한다(그릿 크기 인자는 무시)."""
    if not high_load:
        return 1.0
    return (D_ref / D_target) ** _LAMBDA_EXPONENT_HIGH_LOAD


def disk_gw_relative_scaling(ref, target, high_load=True):
    """ref, target: dict{D_grit, N_grit, grade(optional str), leveled(bool, optional)}.
    D_grit는 함수마다 관례가 다르다 — surface_finish_relative(3M Pysher 2010 기준, µm 실제
    지름)와 lambda_relative(Sun 2009 기준, ANSI 메시 그릿 번호, 지름과 역상관)는 서로 다른
    "D_grit" 정의를 쓴다(원 노트가 그 자체로 서로 다른 단위계를 쓰기 때문 — §3.2는 45~250 µm
    실측 지름, §3.3은 100/325 메시번호). 이 종합함수는 두 원 데이터의 관례를 그대로 보존한다.
    grade는 문자열 태그로만 받고 수치 스케일링에는 쓰지 않는다 — grade 효과는 정량
    미확보(Kwon 2013 §2.1이 grade 625/640/925 3점만 관찰, 회귀하지 않음).

    반환: dict{lambda_rel, Ra_rel, Rpk_rel, surface_finish_rel} — 전부 ref 대비 target의
    배율(무차원)."""
    D_ref, N_ref = ref["D_grit"], ref["N_grit"]
    D_target, N_target = target["D_grit"], target["N_grit"]
    leveled_ref = ref.get("leveled", False)
    leveled_target = target.get("leveled", False)

    return {
        "lambda_rel": lambda_relative(D_ref, D_target, high_load=high_load),
        "Ra_rel": ra_relative(N_ref, N_target),
        "Rpk_rel": rpk_relative(N_ref, N_target),
        "surface_finish_rel": surface_finish_relative(
            D_ref, D_target, leveled_target=leveled_target, leveled_ref=leveled_ref
        ),
    }


def _self_test():
    results = []

    # --- Test 1: Ra_rel(40e3->17e3) 방향(밀도↓→Ra↑) + Kwon 실측 비율(8.05/6.8)과 대조 ---
    ra_rel = ra_relative(40e3, 17e3)
    kwon_ratio = 8.05 / 6.8
    ok1 = bool(ra_rel > 1.0 and abs(ra_rel - kwon_ratio) / kwon_ratio < 0.15)
    results.append(("ra_relative(40e3, 17e3) 방향 및 Kwon 실측(8.05/6.8) 15% 이내",
                     ok1, f"ra_rel={ra_rel:.3f}, kwon={kwon_ratio:.3f}"))

    # --- Test 2: Rpk_rel(40e3->60e3) 방향(밀도↑→Rpk↓) + Kwon 실측 비율(1.7/2.25)과 대조 ---
    rpk_rel = rpk_relative(40e3, 60e3)
    kwon_rpk_ratio = 1.7 / 2.25
    ok2 = bool(rpk_rel < 1.0 and abs(rpk_rel - kwon_rpk_ratio) / kwon_rpk_ratio < 0.20)
    results.append(("rpk_relative(40e3, 60e3) 방향 및 Kwon 실측(1.7/2.25) 20% 이내",
                     ok2, f"rpk_rel={rpk_rel:.3f}, kwon={kwon_rpk_ratio:.3f}"))

    # --- Test 3: surface_finish_relative(45->180) vs 3M 실측(4.1 또는 4.2 / 1.7) ---
    sf_rel = surface_finish_relative(45, 180)
    sf_3m_ratio_lo = 4.1 / 1.7
    sf_3m_ratio_hi = 4.2 / 1.7
    ok3 = bool(min(sf_3m_ratio_lo, sf_3m_ratio_hi) * 0.7 < sf_rel < max(sf_3m_ratio_lo, sf_3m_ratio_hi) * 1.3)
    results.append(("surface_finish_relative(45, 180) 이 3M 실측 비율(1.7->4.1~4.2) 근방",
                     ok3, f"sf_rel={sf_rel:.3f}, 3M 범위=[{sf_3m_ratio_lo:.3f}, {sf_3m_ratio_hi:.3f}]"))

    # --- Test 4: leveled 150 µm 배율이 0.57 근처(노트 §3.2) ---
    sf_leveled_vs_plain = surface_finish_relative(150, 150, leveled_target=True, leveled_ref=False)
    ok4 = bool(abs(sf_leveled_vs_plain - _SF_LEVELED_MULTIPLIER) < 1e-9)
    results.append(("surface_finish_relative(150, 150, leveled_target=True) == 0.57",
                     ok4, f"leveled_multiplier={sf_leveled_vs_plain:.3f}"))

    # --- Test 5: lambda_relative(325->100, high_load=True) vs Sun 실측(8lb: 6.7/4.3 ≈ 1.558) ---
    # (같은 하중 조건끼리 비교해야 함 — 3.3은 325-grit 3.6lb 값이라 다른 하중과 섞으면 안 됨)
    lam_rel_hi = lambda_relative(325, 100, high_load=True)
    sun_ratio = 6.7 / 4.3
    ok5 = bool(abs(lam_rel_hi - sun_ratio) / sun_ratio < 0.20)
    results.append(("lambda_relative(325, 100, high_load=True) vs Sun 실측(8lb: 6.7/4.3) 20% 이내",
                     ok5, f"lam_rel={lam_rel_hi:.3f}, sun={sun_ratio:.3f}"))

    # --- Test 6: lambda_relative(325->100, high_load=False) ~= 1.0 (저하중 무차이) ---
    lam_rel_lo = lambda_relative(325, 100, high_load=False)
    ok6 = bool(abs(lam_rel_lo - 1.0) < 1e-9)
    results.append(("lambda_relative(325, 100, high_load=False) == 1.0 (저하중 그릿 크기 무관)",
                     ok6, f"lam_rel={lam_rel_lo:.3f}"))

    # --- Test 7: disk_gw_relative_scaling 종합 dict 스모크 테스트 ---
    ref = {"D_grit": 325, "N_grit": 40e3, "grade": "640", "leveled": False}
    target = {"D_grit": 100, "N_grit": 40e3, "grade": "640", "leveled": False}
    out = disk_gw_relative_scaling(ref, target, high_load=True)
    ok7 = bool(set(out.keys()) == {"lambda_rel", "Ra_rel", "Rpk_rel", "surface_finish_rel"}
               and abs(out["lambda_rel"] - lam_rel_hi) < 1e-9
               and abs(out["Ra_rel"] - 1.0) < 1e-9)
    results.append(("disk_gw_relative_scaling() 종합 dict가 개별 함수와 일치, N 동일 시 Ra_rel=1",
                     ok7, f"out={out}"))

    print("=== disk_gw_relative_scaling.py self-test ===")
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
