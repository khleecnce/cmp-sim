"""
CMP 슬러리 구성요소 정량관계 재현:
  (A) 부식억제제 BTA의 Langmuir 흡착등온선 (표면피복률·억제효율)
  (B) 산화제 농도 vs 금속 제거율(MRR)의 정점(peak) 거동 — Kaufman 경쟁모델
      기반 현상론(phenomenological) 모델.

지식 근거: knowledge/cmp/slurry-components-overview.md

(A) BTA Langmuir:
  - 흡착등온선  theta = K*C / (1 + K*C)          (Langmuir 단분자층)
  - 자유에너지 관계  dG_ads = -R*T*ln(55.5*K)      (수용액 흡착 관례,
      55.5 mol/L = 물의 몰농도; K [L/mol])
  - 문헌 앵커: BTA가 Langmuir 등온선을 따르고 dG0_ads ≈ -35.4 kJ/mol
      (WebSearch 요지, 2차 인용 — knowledge 노트 §4 참조). 부호(음수)·크기
      (물리흡착~화학흡착 경계 -20~-40 kJ/mol)만 검증, 절대값은 미검증.
  - 억제효율 IE ≈ theta (피복률이 그대로 부식전류 억제율로 근사되는 통상 가정).

(B) 산화제-MRR 정점(Kaufman 1991 경쟁모델의 현상론적 근사):
  - Kaufman: W/Cu CMP는 (i) 산화제가 무른 산화막(WO3/Cu2O 등) 형성 →
      기계연마로 제거, 와 (ii) 과도 산화막이 표면을 보호(passivation)해 오히려
      제거를 늦춤 사이의 경쟁. 따라서 MRR은 산화제 농도에 대해 "급상승 후 완만
      감소"의 단봉(single-peak) 곡선.
  - 문헌 앵커(정성): Cu MRR은 ~1% H2O2에서 최대, 이후 감소; 글리신(착화제)
      첨가 시 최대점이 ~3% H2O2로 이동 (Cambridge MRS OPL, 2차 인용).
  - 아래 mrr_oxidizer()는 그 "단봉+정점이동" 형태를 재현하는 현상론 모델일 뿐,
      특정 데이터 피팅이 아니다(디지털화 데이터 미확보). **정량 절대값 미검증**.

실행: python3 slurry_components.py  -> self-test 결과 stdout.
"""
import math

# --- 상수 ---
R_GAS = 8.314462618      # J/(mol K)
C_WATER = 55.5           # mol/L, 수용액 흡착 표준상태 관례


# ========== (A) BTA Langmuir 흡착 ==========
def K_from_dG_ads(dG_ads_J_per_mol, T=298.15):
    """dG_ads = -R T ln(55.5 K)  =>  K [L/mol]."""
    return math.exp(-dG_ads_J_per_mol / (R_GAS * T)) / C_WATER


def dG_ads_from_K(K, T=298.15):
    """역변환: K [L/mol] -> dG_ads [J/mol]."""
    return -R_GAS * T * math.log(C_WATER * K)


def langmuir_coverage(C_molar, K):
    """Langmuir 단분자층 피복률 theta = K C /(1+K C). C [mol/L], K [L/mol]."""
    KC = K * C_molar
    return KC / (1.0 + KC)


def inhibition_efficiency(C_molar, K):
    """부식 억제효율 IE ≈ theta (피복률 근사)."""
    return langmuir_coverage(C_molar, K)


# ========== (B) 산화제 농도 vs MRR (Kaufman 경쟁 현상론) ==========
def mrr_oxidizer(C, C_peak, mrr_peak=1.0, n=2.0):
    """
    산화제 농도 C에 대한 단봉 MRR 곡선(현상론).
      MRR(C) = mrr_peak * ( (C/C_peak) * (n+1) ) / ( 1 + n*(C/C_peak)^((n+1)/n) )
    설계 목표: C=0에서 0, C=C_peak에서 정확히 mrr_peak로 최대, 이후 완만 감소.
    (미분=0 조건이 x=1에서 성립하도록 지수 (n+1)/n 을 사용.)
    n을 키우면 정점 이후 감소가 완만해진다. **현상론 — 절대값 미검증.**
    """
    x = C / C_peak
    return mrr_peak * ((n + 1.0) * x) / (1.0 + n * x ** ((n + 1.0) / n))


def oxidizer_coverage_langmuir(C, K):
    """산화제 농도 C에 대한 표면 피복률(Langmuir-Hinshelwood 포화형).

      theta(C) = K*C / (1 + K*C)          C [wt%], K [1/wt%]

    판정#19(knowledge/cmp/chi-oxidizer-curve-exponent-identifiability.md)로
    기존 mrr_oxidizer()의 (n, C_peak) 단봉 형상이 정점 아래 관측만으로는
    완전축퇴(식별 불가)임이 수치로 확인됐다. 이 함수는 그 대체 경로 —
    자유 파라미터가 K 하나뿐이라 관측 2점(C=0, C=C_ref)만으로 완전히 식별된다.
    물리적 근거: 산화제의 금속 표면 흡착·산화막 형성은 가용 산화 사이트가
    유한한 포화형 표면반응이다(정점형 부동태화가 아니라 포화형 흡착).
    신규 팩은 이 경로를 쓴다. 기존 mrr_oxidizer()는 하위호환을 위해 유지한다.
    """
    KC = K * C
    return KC / (1.0 + KC)


def _argmax_scan(C_peak, n, hi=8.0, npts=20001):
    """[0,hi*C_peak] 격자에서 MRR 최대 위치(농도)를 수치 탐색."""
    best_c, best_v = 0.0, -1.0
    for i in range(npts):
        C = hi * C_peak * i / (npts - 1)
        v = mrr_oxidizer(C, C_peak, n=n)
        if v > best_v:
            best_v, best_c = v, C
    return best_c, best_v


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

    T = 298.15
    print("== (A1) BTA dG_ads = -35.4 kJ/mol -> 흡착상수 K ==")
    dG = -35.4e3
    K = K_from_dG_ads(dG, T)
    print(f"    dG_ads={dG/1e3:.1f} kJ/mol -> K={K:.3e} L/mol")
    # 물리흡착(-20)~화학흡착(-40) 경계의 강한 흡착. K는 대략 1e4~1e5 L/mol.
    check("K 크기 1e3~1e6 L/mol", 1e3 < K < 1e6, f"(K={K:.2e})")
    check("dG 역변환 왕복 일치", abs(dG_ads_from_K(K, T) - dG) < 1e-6)

    print("== (A2) Langmuir 피복률: 반포화·단조·포화 ==")
    C_half = 1.0 / K                       # KC=1 -> theta=0.5
    th_half = langmuir_coverage(C_half, K)
    print(f"    반포화 농도 C=1/K={C_half:.3e} M -> theta={th_half:.4f}")
    check("C=1/K 에서 theta=0.5", abs(th_half - 0.5) < 1e-9)
    ths = [langmuir_coverage(c, K) for c in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]]
    print("    theta @ [1e-6..1e-2 M] = " + ", ".join(f"{t:.3f}" for t in ths))
    check("피복률 농도에 단조증가", all(ths[i] < ths[i + 1] for i in range(len(ths) - 1)))
    check("고농도(<1) 포화 theta<1", ths[-1] < 1.0 and ths[-1] > 0.99)

    print("== (A3) 강한 passivation: mM 수준 BTA에서 IE>0.9 ==")
    ie_mM = inhibition_efficiency(1e-3, K)
    print(f"    C=1 mM BTA -> IE≈theta={ie_mM:.3f}")
    check("1 mM 에서 억제효율 >0.9", ie_mM > 0.9)

    print("== (B1) 산화제-MRR 단봉: C_peak 에서 최대 ==")
    for Cp, nn in [(1.0, 2.0), (3.0, 2.0)]:
        c_at_max, v_max = _argmax_scan(Cp, nn)
        print(f"    C_peak={Cp}%: 수치최대 @ C={c_at_max:.3f}% (목표 {Cp}%), MRR={v_max:.4f}")
        check(f"C_peak={Cp}% 근처에서 최대", abs(c_at_max - Cp) / Cp < 0.02)
        check(f"C_peak={Cp}% 정점값≈mrr_peak(1.0)", abs(v_max - 1.0) < 1e-3)

    print("== (B2) 정점 이후 감소 & 착화제 첨가 시 정점 이동(1%->3%) ==")
    # C_peak 이후 감소 확인
    v_at_peak = mrr_oxidizer(1.0, 1.0)
    v_past = mrr_oxidizer(4.0, 1.0)
    print(f"    C_peak=1%: MRR(1%)={v_at_peak:.3f} -> MRR(4%)={v_past:.3f} (감소)")
    check("정점 이후 MRR 감소", v_past < v_at_peak)
    # 착화제 없음(peak=1%) vs 있음(peak=3%): 3% 지점에서 후자가 더 큼
    v_noCA_at3 = mrr_oxidizer(3.0, 1.0)
    v_CA_at3 = mrr_oxidizer(3.0, 3.0)
    print(f"    C=3%: 착화제無(peak1%)={v_noCA_at3:.3f}  vs  착화제有(peak3%)={v_CA_at3:.3f}")
    check("착화제 첨가 시 정점이 3%로 이동(3%에서 더 큼)", v_CA_at3 > v_noCA_at3)

    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    ok = run_selftest()
    raise SystemExit(0 if ok else 1)
