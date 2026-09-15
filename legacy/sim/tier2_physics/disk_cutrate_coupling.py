"""디스크 그릿 밀도(N)·활성 그릿 비율(N_eff)·표면 거칠기(Rpk)가 패드 절삭율(CR)에
미치는 결합계수를 계산하는 순수함수 모듈.

지식 근거: knowledge/materials/disk-design-cutrate-asperity-regeneration-model.md
(disk-design Lv3-2) §2, §3, §5. 이 모듈은 그 노트가 이미 회귀·재현한 문헌 수치만 옮긴
것이며, 새로운 문헌 숫자를 도입하지 않는다.

출처:
- 밀도 스케일링 CR ∝ N^(-0.53) — Kwon et al. (2013), Tribology International 67, 272-277,
  doi:10.1016/j.triboint.2013.08.008. N=[17e3, 40e3, 60e3] grits, CR=[37.0, 23.0, 19.0]
  µm/h(2h), 3점 로그-로그 회귀. 노트 §2 verify 블록.
- Rpk 스케일링 CR ∝ Rpk^(0.85), R²=0.994 — 같은 Kwon 2013 데이터, Rpk=[3.75, 2.25, 1.7] µm.
  노트 §2 verify 블록.
- 활성 그릿 잔차 배율 — Tsai et al. (2014), Mathematical Problems in Engineering 2014,
  913812, DOI: 10.1155/2014/913812. N_eff proxy(스크래치 선수) 비 1.12배(CDD 432 -> RCADD
  484), PCR 비 1.96배(CDD 24.0 -> RCADD 47.0 µm/h, 1h) — 잔차 = 1.96/1.12 ≈ 1.75. 노트 §3
  verify 블록.

주의: 노트 §5의 종합 결합식은 노트 자신이 "이 노트가 합성한 작업가설, 미검증"이라고
명시한다. 활성 비율 지수 g는 §5·§6이 명시적으로 "미확정, 캘리브레이션 파라미터로 남긴다"고
못박았으므로, 이 모듈은 g에 어떤 기본값도 넣지 않는다 — Neff_ratio와 g가 둘 다 주어지지
않으면 활성 비율 항을 아예 적용하지 않고 그 사실을 반환값에 명시한다(engine에는 미등록).

실행: python3 disk_cutrate_coupling.py -> self-test 결과 stdout.
"""


def cutrate_density_scaling(N, N_ref, CR_ref):
    """CR_ref * (N/N_ref)^(-0.53). Kwon et al. (2013) 3점 로그-로그 회귀 지수(노트 §2).
    N이 클수록 절삭율이 감소하는 방향(그릿당 하중 분산, 노트 §2 본문)."""
    return CR_ref * (N / N_ref) ** (-0.53)


def cutrate_rpk_scaling(Rpk, Rpk_ref, CR_ref):
    """CR_ref * (Rpk/Rpk_ref)^0.85. Kwon et al. (2013) 3점 로그-로그 회귀 지수(R²=0.994,
    노트 §2). Rpk가 클수록 절삭율이 증가하는 방향."""
    return CR_ref * (Rpk / Rpk_ref) ** 0.85


def active_grit_residual_factor(Neff_ratio, pcr_ratio):
    """pcr_ratio / Neff_ratio — Tsai et al. (2014) 데이터 재현용 순수 산술(노트 §3).
    N_eff proxy(스크래치 선수) 증가만으로 PCR 증가를 다 설명하지 못하는 잔차 배율."""
    return pcr_ratio / Neff_ratio


def disk_cutrate_coupled(N, N_ref, Rpk, Rpk_ref, CR_ref, Neff_ratio=None, g=None):
    """N·Rpk 두 항은 항상 계산해 곱한다(노트 §2, 두 개의 독립된 문헌 회귀 지수).
    Neff_ratio와 g가 둘 다 주어진 경우에만 활성 비율 항 (Neff_ratio)^g를 곱한다 — 노트
    §5·§6이 g를 "미확정, 캘리브레이션 파라미터"라고 명시했으므로 하나라도 None이면
    그 항을 생략하고 active_term_applied=False와 안내 note를 반환한다.

    반환: dict{cr_density_term, cr_rpk_term, active_term, active_term_applied, note, cr_coupled}."""
    density_term = cutrate_density_scaling(N, N_ref, CR_ref)
    rpk_term = cutrate_rpk_scaling(Rpk, Rpk_ref, CR_ref)
    # 두 항 모두 CR_ref를 곱한 절대 절삭율이므로, 결합할 때는 CR_ref로 정규화한 상대
    # 배율을 곱한 뒤 CR_ref를 다시 한 번 곱한다(노트 §5 결합식 형태: CR_ref * 곱).
    density_ratio = density_term / CR_ref
    rpk_ratio = rpk_term / CR_ref

    if Neff_ratio is not None and g is not None:
        active_term = Neff_ratio ** g
        active_term_applied = True
        note = None
    else:
        active_term = None
        active_term_applied = False
        note = "g(활성 비율 지수)는 노트가 미확정이라 캘리브레이션 없이는 적용 불가"

    coupled_ratio = density_ratio * rpk_ratio * (active_term if active_term_applied else 1.0)
    cr_coupled = CR_ref * coupled_ratio

    return {
        "cr_density_term": density_term,
        "cr_rpk_term": rpk_term,
        "active_term": active_term,
        "active_term_applied": active_term_applied,
        "note": note,
        "cr_coupled": cr_coupled,
    }


def _self_test():
    results = []

    # --- Test 1: 밀도 스케일링 — Kwon 3점 중 N_ref=17e3,CR_ref=37.0 -> N=40e3 예측이 23.0에 근접 ---
    # 직접 계산한 상대오차 ≈2.2%(3점 회귀 잔차) — tolerance 20%로 넉넉히 잡되 실제 오차도 기록.
    pred_density = cutrate_density_scaling(40e3, 17e3, 37.0)
    relerr_density = abs(pred_density - 23.0) / 23.0
    ok1 = bool(relerr_density < 0.20)
    results.append(("cutrate_density_scaling(40e3,17e3,37.0) ~= 23.0 (Kwon 2013, rel<20%)",
                     ok1, f"pred={pred_density:.3f}, relerr={relerr_density:.3f}"))

    # --- Test 2: Rpk 스케일링 — Rpk_ref=3.75,CR_ref=37.0 -> Rpk=1.7 예측이 19.0에 근접 ---
    pred_rpk = cutrate_rpk_scaling(1.7, 3.75, 37.0)
    relerr_rpk = abs(pred_rpk - 19.0) / 19.0
    ok2 = bool(relerr_rpk < 0.20)
    results.append(("cutrate_rpk_scaling(1.7,3.75,37.0) ~= 19.0 (Kwon 2013, rel<20%)",
                     ok2, f"pred={pred_rpk:.3f}, relerr={relerr_rpk:.3f}"))

    # --- Test 3: 활성 그릿 잔차 배율 — Tsai 2014 재현, 1.75 근처(rel=0.02) ---
    residual = active_grit_residual_factor(1.12, 1.96)
    ok3 = bool(abs(residual - 1.75) / 1.75 < 0.02)
    results.append(("active_grit_residual_factor(1.12, 1.96) ~= 1.75 (Tsai 2014, rel<2%)",
                     ok3, f"residual={residual:.4f}"))

    # --- Test 4: g 또는 Neff_ratio가 None이면 active_term_applied=False + note ---
    out_no_g = disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0, Neff_ratio=1.12, g=None)
    out_no_neff = disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0, Neff_ratio=None, g=0.3)
    out_neither = disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0)
    ok4 = bool(
        out_no_g["active_term_applied"] is False and out_no_g["note"] is not None
        and out_no_neff["active_term_applied"] is False and out_no_neff["note"] is not None
        and out_neither["active_term_applied"] is False and out_neither["note"] is not None
    )
    results.append(("disk_cutrate_coupled: Neff_ratio/g 중 하나라도 None -> active_term_applied=False + note",
                     ok4, f"no_g={out_no_g['note']!r}, no_neff={out_no_neff['note']!r}, neither={out_neither['note']!r}"))

    # --- Test 5: 스키마 계약 — N↑ -> CR↓ (단조감소) ---
    cr_lo_n = cutrate_density_scaling(17e3, 17e3, 37.0)
    cr_hi_n = cutrate_density_scaling(60e3, 17e3, 37.0)
    ok5 = bool(cr_hi_n < cr_lo_n)
    results.append(("cutrate_density_scaling: N↑(17e3->60e3) -> CR↓ (단조감소)",
                     ok5, f"CR(17e3)={cr_lo_n:.3f}, CR(60e3)={cr_hi_n:.3f}"))

    # --- Test 6: 스키마 계약 — Rpk↑ -> CR↑ (단조증가) ---
    cr_lo_rpk = cutrate_rpk_scaling(1.7, 3.75, 37.0)
    cr_hi_rpk = cutrate_rpk_scaling(3.75, 3.75, 37.0)
    ok6 = bool(cr_hi_rpk > cr_lo_rpk)
    results.append(("cutrate_rpk_scaling: Rpk↑(1.7->3.75) -> CR↑ (단조증가)",
                     ok6, f"CR(1.7)={cr_lo_rpk:.3f}, CR(3.75)={cr_hi_rpk:.3f}"))

    print("=== disk_cutrate_coupling.py self-test ===")
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
