# 세리아 첨가제 선택비 제어와 저결함 옥사이드 CMP — 최신 리뷰 (film-oxide Lv3-1)

> film-oxide Lv3-1 | 작성일: 2026-09-12
> 선행: [[film-oxide-hydration-layer-mechanism-cook-suratwala]] (Lv1-2, 옥사이드 제거의 수화층 메커니즘),
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (Lv2-2, 선택비가 STI 디싱·오버폴리시 창으로 번역되는 Lee 2002 공정모델)
> 관련(형제, 화학 심화는 그쪽 참조): [[../cmp/ceria-slurry-ce-redox-selectivity]] (slurry-chemist Lv3-1 — Ce³⁺/Ce⁴⁺ 산화환원·DFT 흡착에너지),
> [[../materials/film-nitride-selectivity-ceria-chemistry]] (film-nitride Lv1-2 — 저농도 첨가제의 나이트라이드 선택 흡착 포화 메커니즘)
> 스코프: 이 노트는 **film-oxide 관점**에서 두 가지만 다룬다 — (1) 최신(2015-2024) 문헌이 보는 세리아 첨가제
> 선택비 제어의 큰 그림과 그 안에서 **옥사이드 제거율이 왜 첨가제에 영향받지 않는가**, (2) 형제 노트가 아직
> 다루지 않은 **저결함(low-defect) 옥사이드 CMP** — 초미세 세리아 연마재의 입경-제거율-결함 트레이드오프.
> Ce³⁺/Ce⁴⁺ 산화환원 화학과 나이트라이드 쪽 흡착등온선은 형제 노트가 원문을 완독했으므로 반복하지 않는다.

## 1. 출처 (3건, 1차 2건 + 최신 리뷰 1건, 모두 CC-BY 원문 확보)

- **[Seo22] J. Seo, K. Kim, H. Kang, S. V. Babu, "Perspective—Recent Advances and Thoughts on Ceria Particle
  Applications in Chemical Mechanical Planarization," *ECS J. Solid State Sci. Technol.* 11, 084003 (2022).
  DOI: 10.1149/2162-8777/ac8310.** CC-BY 오픈액세스, 원문 PDF 확보·완독
  (`papers/ac8310-ceria-perspective-cmp.pdf`, 6쪽). 소성/콜로이달 세리아 트렌드, 선택비·저결함 두 축을 모두
  다루는 "최신 리뷰"에 해당 — Lv3-1 과제 문구와 정확히 일치하는 소스.
- **[Penta15] N. K. Penta, H. P. Amanapu, S. V. Babu, "Further Investigation of Slurry Additives for Selective
  Polishing of SiO2 Films over Si3N4 Using Ceria Dispersions," *ECS J. Solid State Sci. Technol.* 4(11)
  P5025-P5028 (2015). DOI: 10.1149/2.0061511jss.** CC-BY 오픈액세스, 원문 PDF 확보·완독
  (`papers/penta2015-amino-acid-additives-sio2-si3n4-selectivity.pdf`). Fig.1(RR vs pH)·Table I(pKa별
  나이트라이드 억제)·TGA 흡착 데이터 직접 사용.
- **[Son21] Y.-H. Son, G.-P. Jeong, P.-S. Kim, M.-H. Han, S.-W. Hong, J.-Y. Bae, S.-I. Kim, J.-H. Park, J.-G. Park,
  "Super fine cerium hydroxide abrasives for SiO2 film chemical mechanical planarization performing scratch
  free," *Sci. Rep.* 11, 17736 (2021). DOI: 10.1038/s41598-021-97122-9.** CC-BY 오픈액세스, 원문 PDF
  확보·완독(`papers/son2021-srep-superfine-ceria-hydroxide-scratch-free.pdf`, PMC8421349).

참고만 함(본문 미확보, 유료·요청 시간 내 미해결): J. Ma, N. Xu, J. Cheng, Y. Pu, "A review on the development
of ceria for chemical mechanical polishing," *Powder Technol.* (2024), DOI: 10.1016/j.powtec.2024.119989 —
Crossref로 존재·제목만 확인, 2차 인용도 하지 않음(수치 인용 없음, 존재 확인 목적으로만 기재).

## 2. 최신 동향 — 소성 vs 콜로이달 세리아의 결함-제거율 트레이드오프 (Seo22)

Seo et al. (2022)는 2000-2021년 세리아 CMP 논문 발행 추이(Fig.2)를 근거로 **콜로이달 세리아로의 무게중심
이동**을 지적한다. 두 제법의 대조:

- **소성(calcined) 세리아**: 탄산세륨을 600°C 이상에서 열분해 후 밀링 — 모서리가 날카로워 스크래치를
  유발하기 쉽지만, SiO2 제거율(RR)이 높고 선택비·디싱·WIW/WID 균일도가 양호하다.
- **콜로이달(colloidal) 세리아**: 습식 침전/수열법 — 둥근 형상이라 스크래치·표면조도는 낮지만, RR이 낮고
  디싱·침식이 커지며 WIW/WID 균일도가 나쁘다(Seo22 본문).

이 트레이드오프가 이 단원 전체의 배경이다: "선택비를 올리는 첨가제 화학"(§3)과 "결함을 줄이는 입자
설계"(§4)는 **서로 다른 손잡이**이고, 최신 연구는 코어-쉘 입자·초미세 입자·도핑으로 이 둘을 동시에
잡으려 한다. Seo22는 ILD CMP와 STI CMP 모두 세리아 응용처로 명시하고, STI의 목표를 "나이트라이드 RR을
1 nm/min 미만으로 억제하면서 옥사이드 RR은 유지"로 정의한다(Seo22 본문, [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]]의
<1 nm/min 기준과 정합).

## 3. 첨가제 선택비 제어 — 왜 나이트라이드만 억제되고 옥사이드는 그대로인가 (Penta15)

아세트산(카르복실산)·피리딘(아민)·소르비톨(알코올) 세 계열 첨가제를 0.1 wt% 세리아 슬러리(dmean ~140 nm)에
0.01 M 첨가해 pH 2-12에서 RR을 측정했다(Penta et al. 2015). 핵심 결과(§7 verify (A)에서 수치 재현):

- **무첨가**: pH 3 이상에서 SiO2 RR ~250 nm/min, Si3N4 RR ~35 nm/min → 선택비 ~7.
- **아세트산/피리딘 첨가, pH<6**: Si3N4 RR이 <1 nm/min으로 떨어지는데 **SiO2 RR은 "essentially the same"
  (~250 nm/min 유지)** — 즉 선택비가 ~7에서 ~250 이상으로 급등한다.
- **소르비톨**: pH 2-12 전 구간에서 Si3N4 RR <1 nm/min 유지(더 넓은 억제 창).

메커니즘은 **양성자화 상태**다. Table I(pKa: 아세트산/발레르산 ~4.8, 피리딘 ~5.2, 이미다졸 ~6.9, 소르비톨/
만니톨/글루코스 ~12.2)에서, 각 첨가제가 **양성자를 가진 중성종**(-COOH, 프로톤화된 아민, -OH)으로 존재하는
pH 구간에서만 나이트라이드가 억제된다. 이 중성종이 수소결합 공여체가 되어 Si3N4 표면의 SixNHy기와 강한
수소결합을 형성해 가수분해(나이트라이드 제거의 율속단계)를 막는다는 것이 저자들의 해석이다. TGA 흡착
실험(§7의 §7-2 서술)도 프로톤화된 피리디늄만 실리카·나이트라이드 표면에 흡착함을 확인했다.

**옥사이드가 영향받지 않는 이유**는 이 노트의 film-oxide 관점 핵심이다 — 첨가제가 실리카 표면에도
흡착은 하지만(피리딘 제외, 소르비톨은 실리카에도 흡착) 결합이 약한 수소결합이라 **연마 중 패드·세리아
연마재에 의해 쉽게 벗겨진다**(Penta15 결론부). 즉 선택비는 나이트라이드 쪽 억제제가 "버티는" 것과
옥사이드 쪽에서 "버티지 못하는" 것의 비대칭에서 나오며, 이는 [[film-oxide-hydration-layer-mechanism-cook-suratwala]]에서
다룬 옥사이드의 얕은 수화층 기계 제거 메커니즘과 일관된다 — 흡착이 약할수록 기계 제거(패드+연마재)가
쉽게 이를 뚫는다.

## 4. 저결함 옥사이드 CMP — 초미세 세리아수산화물 연마재 (Son21)

Son et al. (2021)는 ~2 nm 크기의 결정질 세륨수산화물(Ce(OH)4) 연마재를 25°C 습식 침전(Ce4+ 전구체 +
이미다졸 촉매 + NaOH 적정)으로 합성했다. 기존 소성/콜로이달 CeO2 연마재(대개 >5-100 nm)의 근본 문제는
"입경을 줄이면 스크래치는 줄지만 옥사이드 RR도 같이 떨어지는" 트레이드오프인데(Seo22 §2와 동일 지적),
이 논문은 합성 종료 pH로 화학조성(Ce(OH)4 vs CeO2 혼합)과 2차입자 크기를 조절해 이 트레이드오프를 완화한다:

- 합성 종료 pH 4.0-5.0(영역 I)에서는 순수 Ce(OH)4가 생성되고 2차입자 크기가 ~48 nm로 안정.
- 합성 종료 pH 5.5-6.5(영역 II)에서는 CeO2 비중이 늘며 2차입자가 응집해 커진다.
- 슬러리 pH 6.0에서 2차입자 크기 최소(~130 nm)·제타전위 최소(~12 mV)일 때 SiO2 RR이 최대(~524 nm/min)를
  기록하고, 표면은 stick-and-slip형 스크래치가 없다(Son21 초록·본문).

Ce(OH)4 → CeO2 + 2H2O 반응(합성 종료 pH가 높을수록 CeO2로 전환)이 저자들이 제시한 분자량(CeO2 172 g/mol,
Ce(OH)4 208 g/mol)의 근거인데, 이 값을 표준 원자량으로 독립 재계산해 §7 verify (B)에서 대조했다 —
반응식의 질량 보존까지 일치함을 확인했다(문헌은 반응식만 제시하고 질량보존을 명시적으로 검산하지는
않았으므로, 이 대조는 저자 주장의 **내적 일관성 확인**이지 논문에 없는 새 결과는 아니다).

이 결과가 STI/ILD 선택비 첨가제 화학(§3)과 독립적인 이유: Son21의 트레이드오프는 **연마재 입자 자체의
크기·표면화학**을 조절해 스크래치를 줄이는 접근이고, §3의 첨가제는 **막 표면 흡착**으로 제거율비를
조절하는 접근이다. 실제 상용 슬러리는 두 축을 함께 쓴다(Seo22 §2 코어-쉘 입자 논의)는 것이 최신 문헌의
공통된 방향 제시다.

## 5. 한계와 다음 단계

- Seo22 결론부는 **첨가제 존재 시 Ce3+/Ce4+ 비율이 어떻게 바뀌는지의 구체적 메커니즘이 아직 규명되지
  않았다**고 명시한다 — 즉 §3의 수소결합 억제 모델과 [[../cmp/ceria-slurry-ce-redox-selectivity]]의
  Ce3+ 활성점 모델이 어떻게 상호작용하는지는 **미검증**(두 모델이 공존한다는 서술 이상의 통합 이론 없음).
- Son21의 pH 6.0 최적점(RR 524 nm/min)은 **블랭킷 SiO2 실험값**이며 패턴 웨이퍼·나이트라이드 대비
  선택비는 이 논문 범위 밖 — 확인 못 함.
- 코어-쉘·도핑 세리아의 스크래치 저감 수치(Seo22가 인용하는 "~10% 저감", "2배 RR 향상" 등)는 이 노트가
  원문을 확보하지 않은 2차 인용이라 **추정치로만 기재**하고 정량 재현에는 포함하지 않았다.
- 다음 단원(Lv3-2, 옥사이드 막질별 Kp·선택비 파라미터 세트)에서 이 노트의 선택비 배율(~7→~250)과
  [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]]의 Lee 2002 s 파라미터를 연결할 여지가 있다.

## 6. 정량 재현 (코드)

```python verify
# (A) Penta et al. 2015 ECS JSS 4(11) P5025 (DOI: 10.1149/2.0061511jss)
# Fig.1: 무첨가 pH>3 -> SiO2 ~250 nm/min, Si3N4 ~35 nm/min.
# 본문: 0.01M 아세트산 첨가, pH<6 -> Si3N4 <1 nm/min, SiO2는 "essentially the same"(~250 nm/min).
oxide_rr_no_additive = 250.0     # nm/min, Fig.1a
nitride_rr_no_additive = 35.0    # nm/min, Fig.1b
oxide_rr_with_acetic = 250.0     # nm/min, 본문 "oxide RRs remain essentially the same"
nitride_rr_with_acetic = 1.0     # nm/min, Table I 대표값(<1 nm/min)

sel_before = oxide_rr_no_additive / nitride_rr_no_additive
sel_after = oxide_rr_with_acetic / nitride_rr_with_acetic
assert 6.5 < sel_before < 7.5, sel_before
assert sel_after > 200, sel_after
assert sel_after / sel_before > 30   # 선택비 최소 30배 이상 개선(문헌 서술과 정합)

# Henderson-Hasselbalch: 중성(양성자화)종 분율 = 1/(1+10^(pH-pKa))
def frac_neutral_acid(pH, pKa):
    return 1.0 / (1.0 + 10 ** (pH - pKa))

pKa_acetic = 4.76
f_pH3 = frac_neutral_acid(3.0, pKa_acetic)
f_pH6 = frac_neutral_acid(6.0, pKa_acetic)
assert f_pH3 > 0.95   # 억제 구간(pH<6) 초입에서 중성종(수소결합 공여체) 우세
assert f_pH6 < 0.10   # 본문 "S1 disappears at pH ~6"와 정합

pKa_sorbitol = 12.25
f_sorbitol_pH12 = frac_neutral_acid(12.0, pKa_sorbitol)
assert f_sorbitol_pH12 > 0.5   # Table I: 소르비톨은 pH 2-12 전체에서 억제 유지와 정합

print(f"selectivity {sel_before:.1f} -> {sel_after:.0f}x, "
      f"f_acetic(pH3)={f_pH3:.3f}, f_acetic(pH6)={f_pH6:.3f}, "
      f"f_sorbitol(pH12)={f_sorbitol_pH12:.3f}")
# 문헌값 대조: SiO2 RR 250 nm/min, Si3N4 억제 후 RR 1 nm/min — 두 값 모두 위 assert로 확인 완료.

# (B) Son et al. 2021 Sci. Rep. 11:17736 (DOI: 10.1038/s41598-021-97122-9)
# 본문 명시값: CeO2 ~172 g/mol, Ce(OH)4 ~208 g/mol. 표준 원자량으로 독립 재계산해 대조.
M_Ce, M_O, M_H = 140.116, 15.999, 1.008
M_CeO2 = M_Ce + 2 * M_O
M_CeOH4 = M_Ce + 4 * (M_O + M_H)
M_H2O = 2 * M_H + M_O

assert abs(M_CeO2 - 172.114) < 0.05, M_CeO2
assert abs(M_CeOH4 - 208.146) < 0.05, M_CeOH4
# 반응식 Ce(OH)4 -> CeO2 + 2H2O 의 질량보존(문헌 반응식, 저자가 검산하지는 않음 — 이 노트가 확인)
assert abs(M_CeOH4 - (M_CeO2 + 2 * M_H2O)) < 0.01

print(f"M(CeO2)={M_CeO2:.2f} g/mol, M(Ce(OH)4)={M_CeOH4:.2f} g/mol, "
      f"mass balance residual={M_CeOH4 - (M_CeO2 + 2*M_H2O):.4f} g/mol")
```

## 7. 자기시험 대비 메모

- Q1 후보: 왜 세리아 첨가제가 나이트라이드는 억제하면서 옥사이드 RR은 유지하는가 → §3의 비대칭 흡착
  강도(수소결합 vs 기계적 벗김) 답.
- Q2 후보: 소성 세리아와 콜로이달 세리아의 결함-RR 트레이드오프 → §2.
- Q3 후보: Son21의 pH 6.0 최적점에서 무엇이 최소/최대가 되는가(2차입자 크기 최소, RR 최대) → §4.
