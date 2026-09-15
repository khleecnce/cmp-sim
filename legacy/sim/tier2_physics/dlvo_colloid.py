"""
DLVO 콜로이드 상호작용 에너지 + Debye 길이 + 전기영동 이동도(Henry) 재현.

지식 근거: knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md
  - Debye 길이 kappa^-1 = 0.304/sqrt(I) nm (물, 25C) : Israelachvili
    "Intermolecular and Surface Forces" 3rd ed.(2011) 표준식, 2차 인용.
    앵커 대조값: dispersion.com 튜토리얼 "~1 nm @ 0.1 M, ~10 nm @ 0.001 M".
  - Henry 식 mu_E = 2*eps*zeta*f(ka)/(3*eta), f: Smoluchowski 1.5 / Huckel 1.0
    (Malvern ELS overview PDF, macro.lsu.edu).
  - DLVO 구-구(Derjaguin) 정전반발 V_edl = 2*pi*eps0*epsr*a*zeta^2*ln(1+exp(-k*h))
    (arXiv:1009.6150 constant-potential form) + van der Waals V_vdW = -A*a/(12*h).

목적:
  (1) Debye 길이 공식이 0.304/sqrt(I) nm 및 문헌 앵커값과 일치하는지 검증.
  (2) 실리카 슬러리 DLVO V_T(h) 곡선에서 이온세기 증가 -> 에너지장벽 소멸,
      2차 최소 심화라는 정성 형태(문헌 서술)를 재현.

실행: python3 dlvo_colloid.py  -> self-test 결과 stdout.
"""
import math
import numpy as np

# --- 물리상수 (SI) ---
EPS0 = 8.8541878128e-12   # F/m
KB = 1.380649e-23         # J/K
NA = 6.02214076e23        # 1/mol
QE = 1.602176634e-19      # C
EPSR_WATER = 78.5         # 물 비유전율 (25C)


def debye_length_nm(I_molar, T=298.15, epsr=EPSR_WATER, z=1):
    """대칭 z:z 전해질의 Debye 길이 kappa^-1 [nm]. I: 이온세기 [mol/L]."""
    # 수밀도 n_bulk = I * 1000 * NA (mol/L -> ions/m^3), 대칭 1:1 이면 I=농도
    kappa2 = (2.0 * (z * QE) ** 2 * I_molar * 1000.0 * NA) / (EPS0 * epsr * KB * T)
    kappa = math.sqrt(kappa2)          # 1/m
    return 1.0 / kappa * 1e9           # nm


def debye_length_approx_nm(I_molar):
    """물·25C·1:1 전해질 근사식: 0.304/sqrt(I) nm."""
    return 0.304 / math.sqrt(I_molar)


def henry_zeta_from_mobility(mu_E, f_ka, eta=8.9e-4, epsr=EPSR_WATER):
    """Henry 식 역산: zeta = 3*eta*mu_E/(2*eps0*epsr*f_ka). mu_E [m^2/(V s)]."""
    return 3.0 * eta * mu_E / (2.0 * EPS0 * epsr * f_ka)


def V_vdW(h, A, a):
    """동일 구-구 van der Waals 인력 (Derjaguin, 소분리 근사). h,a [m], A [J]."""
    return -A * a / (12.0 * h)


def V_edl(h, a, zeta, I_molar, T=298.15, epsr=EPSR_WATER):
    """구-구 정전 반발 (일정전위, Derjaguin). zeta [V]."""
    kappa_inv = debye_length_nm(I_molar, T, epsr) * 1e-9   # m
    kappa = 1.0 / kappa_inv
    return 2.0 * math.pi * EPS0 * epsr * a * zeta ** 2 * math.log(1.0 + math.exp(-kappa * h))


def V_total_profile(a, zeta, A, I_molar, T=298.15,
                    h_min=3e-10, h_max=4e-8, npts=4000):
    """V_T(h)=V_vdW+V_edl 곡선. 반환: h[m], V/kT 배열, 장벽·2차최소 요약."""
    h = np.linspace(h_min, h_max, npts)
    kT = KB * T
    vt = np.array([(V_vdW(x, A, a) + V_edl(x, a, zeta, I_molar, T)) / kT for x in h])
    # 에너지장벽 = 곡선 최댓값(있으면), 2차최소 = 장벽 바깥쪽 국소최솟값
    i_bar = int(np.argmax(vt))
    barrier = vt[i_bar]
    # 2차 최소: 장벽 오른쪽 구간의 최솟값
    if i_bar < npts - 2:
        j = i_bar + int(np.argmin(vt[i_bar:]))
        sec_min = vt[j]
        sec_min_h = h[j]
    else:
        sec_min, sec_min_h = float('nan'), float('nan')
    return h, vt, dict(barrier_kT=barrier, barrier_h_nm=h[i_bar] * 1e9,
                       sec_min_kT=sec_min, sec_min_h_nm=sec_min_h * 1e9)


def stability_qualitative(ph, abrasive_iep_ph, wafer_iep_ph=None):
    """pH와 IEP 거리로부터 정성적 응집 위험도를 판정 (정량 zeta 없이).

    근거: knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5
      "표면전하가 0이 되는 pH가 등전점(IEP)이며, 이 근처에서 zeta->0이라
      장벽이 무너져 가장 불안정하다."
    |pH - IEP| < 1.0  -> "IEP 근접, 응집 위험 높음" (zeta 작음 추정)
    |pH - IEP| >= 2.0 -> "IEP에서 충분히 이격, 분산 안정 추정"
    그 사이는 "중간" — 정량 zeta 없이는 더 세분화하지 않는다(지어내지 않음).
    이 함수는 zeta 절대값을 계산하지 않는다 — 팩에 실측 zeta가 없기 때문이다.
    임계값 1.0/2.0은 미검증(arbitrary) — 노트 §2의 "|zeta|>=30mV 안정, <15mV 응집"
    서술을 pH 거리로 대략 치환한 것뿐, 정량 매핑 문헌은 없다.
    wafer_iep_ph를 주면 그 거리도 참고 정보로만 note에 덧붙인다(위험도 분류에는
    반영하지 않는다 — 입자-웨이퍼 결합효과를 정량화한 문헌이 없다).
    """
    distance = abs(ph - abrasive_iep_ph)
    if distance < 1.0:
        risk = "high"
    elif distance >= 2.0:
        risk = "low"
    else:
        risk = "medium"
    note = (f"|pH-IEP|={distance:.2f} (미검증 임계 1.0/2.0 — 정량 zeta 매핑 문헌 없음, "
            "knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5 정성 서술의 대략적 치환)")
    if wafer_iep_ph is not None:
        wafer_distance = abs(ph - wafer_iep_ph)
        note += f"; 웨이퍼 IEP 거리(참고, 위험도 미반영)={wafer_distance:.2f}"
    return {"distance_from_iep_ph": distance, "risk": risk, "note": note}


def run_selftest():
    passed = 0
    total = 0

    def check(name, cond, detail=""):
        nonlocal passed, total
        total += 1
        mark = "PASS" if cond else "FAIL"
        if cond:
            passed += 1
        print(f"  [{mark}] {name} {detail}")

    print("== 1) Debye 길이: 정확식 vs 0.304/sqrt(I) 근사 ==")
    for I in [1e-3, 1e-2, 1e-1]:
        exact = debye_length_nm(I)
        approx = debye_length_approx_nm(I)
        rel = abs(exact - approx) / approx
        print(f"    I={I:>6} M : 정확식 {exact:6.3f} nm | 근사 {approx:6.3f} nm | 상대오차 {rel*100:4.1f}%")
        check(f"Debye I={I}M 근사식 일치(<3%)", rel < 0.03)

    print("== 2) 문헌 앵커값 대조 (dispersion.com: ~1nm@0.1M, ~10nm@0.001M) ==")
    d_01 = debye_length_nm(0.1)
    d_001 = debye_length_nm(1e-3)
    print(f"    0.1 M -> {d_01:.2f} nm (문헌 ~1 nm),  0.001 M -> {d_001:.2f} nm (문헌 ~10 nm)")
    check("0.1M ~ 1 nm", abs(d_01 - 1.0) < 0.2)
    check("0.001M ~ 10 nm", abs(d_001 - 10.0) < 1.0)

    print("== 3) Henry 식 Smoluchowski/Huckel 한계 ==")
    # 전형 실리카 mu_E = -3e-8 m^2/Vs -> zeta 수십 mV 스케일
    mu = -3.0e-8
    z_smol = henry_zeta_from_mobility(mu, 1.5) * 1e3   # mV
    z_huck = henry_zeta_from_mobility(mu, 1.0) * 1e3
    print(f"    mu_E={mu:.1e} m2/Vs -> zeta(Smol,f=1.5)={z_smol:.1f} mV, zeta(Huckel,f=1.0)={z_huck:.1f} mV")
    check("Huckel/Smol 비 = 1.5", abs((z_huck / z_smol) - 1.5) < 1e-6)
    check("zeta 크기 콜로이드 범위(10~100mV)", 10 < abs(z_smol) < 100)

    print("== 4) DLVO V_T(h): 이온세기 증가 -> 장벽 소멸 (정성 재현) ==")
    # 실리카: a=50nm, zeta=-40mV, A=0.85e-20 J (실리카-물-실리카 문헌 오더)
    a, zeta, A = 50e-9, -0.040, 0.85e-20
    results = {}
    for I in [1e-3, 1e-2, 1e-1]:
        _, _, s = V_total_profile(a, zeta, A, I)
        results[I] = s
        print(f"    I={I:>6} M : 장벽 {s['barrier_kT']:7.1f} kT @ {s['barrier_h_nm']:.1f} nm | "
              f"2차최소 {s['sec_min_kT']:7.2f} kT @ {s['sec_min_h_nm']:.1f} nm")
    # 저이온세기: 큰 장벽 존재(분산 안정). 이온세기 증가: 장벽 단조 감소 + 2차최소 심화.
    check("저이온세기(1mM) 큰 장벽(>15 kT)", results[1e-3]['barrier_kT'] > 15)
    check("이온세기 증가 -> 장벽 단조 감소",
          results[1e-3]['barrier_kT'] > results[1e-2]['barrier_kT'] > results[1e-1]['barrier_kT'])
    check("이온세기 증가 -> 2차최소 심화(더 음수)",
          results[1e-3]['sec_min_kT'] > results[1e-2]['sec_min_kT'] > results[1e-1]['sec_min_kT'])

    print("== 5) DLVO: pH로 IEP 근접(|zeta| 감소) -> 장벽 붕괴(응집) 정성 재현 ==")
    # 동일 I=10mM에서 zeta만 낮춤: -40mV(안정) -> -10mV(IEP 근접, 응집)
    barriers = {}
    for zt in [-0.040, -0.020, -0.010]:
        _, _, s = V_total_profile(a, zt, A, 1e-2)
        barriers[zt] = s['barrier_kT']
        print(f"    zeta={zt*1e3:>5.0f} mV : 장벽 {s['barrier_kT']:7.2f} kT @ {s['barrier_h_nm']:.1f} nm")
    # EDL ~ zeta^2 이므로 |zeta| 감소 시 장벽 급감.
    check("|zeta| 감소 -> 장벽 단조 붕괴",
          barriers[-0.040] > barriers[-0.020] > barriers[-0.010])
    check("IEP 근접(-10mV) 장벽 사실상 소멸(<5 kT)", barriers[-0.010] < 5)

    print("== 6) 정성 안정성 판정(stability_qualitative): pH-IEP 거리 -> risk ==")
    r_oxide = stability_qualitative(10.5, 2.5)   # oxide_silica 팩: pH10.5, IEP2.5, 거리=8.0
    print(f"    oxide_silica(pH10.5,IEP2.5): 거리={r_oxide['distance_from_iep_ph']:.2f} risk={r_oxide['risk']}")
    check("oxide_silica 조건 risk=low(거리 8.0>=2.0)", r_oxide["risk"] == "low")
    r_near = stability_qualitative(3.0, 2.5)     # IEP 근접: 거리=0.5
    print(f"    IEP근접(pH3.0,IEP2.5): 거리={r_near['distance_from_iep_ph']:.2f} risk={r_near['risk']}")
    check("IEP 근접(거리0.5<1.0) risk=high", r_near["risk"] == "high")
    r_mid = stability_qualitative(4.0, 2.5)      # 중간: 거리=1.5
    print(f"    중간거리(pH4.0,IEP2.5): 거리={r_mid['distance_from_iep_ph']:.2f} risk={r_mid['risk']}")
    check("중간거리(1.0<=거리<2.0) risk=medium", r_mid["risk"] == "medium")

    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    ok = run_selftest()
    raise SystemExit(0 if ok else 1)
