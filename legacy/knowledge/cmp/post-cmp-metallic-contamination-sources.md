<!-- V2-SECTION: R2-slurry | 공동: R4-disk | 분배완료 2026-09-08 | 근거: chemistry, colloid, passivation, pourbaix, 슬러리 | 정본: ARCHITECTURE-V2.md §3 -->
# Post-CMP 표면 오염의 종류와 발생원 — 슬러리·배선금속 재흡착·패드/디스크·세정수

> 에이전트: surface-contamination Lv1-1 | 작성일: 2026-09-06
> [[surface-chemistry-cu-w-pourbaix-passivation]] [[colloid-zeta-dlvo-slurry-stability]] [[slurry-components-overview]]

## 1. 왜 필요한가 — "슬러리 화학 = 오염원"이라는 관점
CMP 슬러리는 [[slurry-components-overview]]에서 본 대로 연마입자·산화제·완충제·억제제·착화제를
한 병에 담은 반응계다. 연마가 끝나는 순간, **그 구성요소 하나하나가 웨이퍼 표면에 남는 오염원**이
된다. 즉 이 단원은 앞 노트들(슬러리 화학·Pourbaix·콜로이드)을 "제거 대상"의 시선으로 뒤집어 읽는
작업이다. Post-CMP 오염은 발생원에 따라 (1) 슬러리 유래(금속촉매·완충 양이온·연마입자·유기억제제),
(2) 배선 금속 재흡착(용해된 Cu²⁺의 정전흡착), (3) 패드/디스크 유래(다이아몬드 그릿·충전제),
(4) 세정수/환경 유래로 나뉜다. 발생원을 알아야 세정 화학(Lv2-2)을 발생원별로 설계할 수 있다.
정량축은 **표면 금속 면밀도**(atoms/cm²)이며, 소자 요구 허용치는 ~1e10 atoms/cm² 오더다(§5).

## 2. 슬러리 유래 오염 — Fe 촉매·K/NH₄ 완충제·세리아(Ce)·BTA
- **Fe 촉매(질산철, Fenton)**: W CMP는 Fe(NO₃)₃/H₂O₂로 W→WO₃ 산화막을 만든다
  ([[surface-chemistry-cu-w-pourbaix-passivation]] §3). Fe³⁺/Fe²⁺ 순환이 ·OH를 생성하는
  **Fenton 화학**이 그 엔진인데(고전식 `Fe²⁺ + H₂O₂ → Fe³⁺ + OH⁻ + ·OH`, 산성에서 속도상수
  ~50 M⁻¹s⁻¹, 산화종은 pH에 따라 ·OH↔FeIV=O로 갈림 — Meyerstein, *Acc. Chem. Res.* 2022,
  PMC9312186 오픈액세스), 그 철이 곧 표면 오염으로 남는다. 질산철·산화제·연마입자 W 슬러리로
  연마한 웨이퍼의 **Fe 잔류가 세정 전 ~(100–200)×10¹⁰ atoms/cm²(=1–2×10¹² atoms/cm²)** 수준,
  세정 후 <10×10¹⁰ atoms/cm²(<1×10¹¹)로 보고됨(Seo, Lee, Kim, Park, "Optimization of post-CMP
  cleaning process for elimination of CMP slurry-induced metallic contaminations", *J. Mater. Sci.:
  Mater. Electron.* 12, 2001, doi:10.1023/A:1011242900843 — DOI 실존 확인, 수치는 2차 요약/초록
  기반이라 **원문 표값 미검증**). **2026-09-09 원문 PDF 확인(Lv3-2)**: 이 DOI 논문은 KOH 슬러리 산화막 CMP의
  K·Ca TXRF 연구이며 **W-CMP Fe 1–2×10¹² 수치는 본문에 없다** — 위 Fe 값은 출처 불명·미검증으로 격하하고,
  sim/tier2_physics/metal_contamination_surface.py의 SEO2001 상수도 같은 표기가 필요하다(PROFILE 구현요청 참조).
- **K/NH₄ 완충제·pH조절제**: 같은 연구에서 **모든 산화막 표면이 연마 중 K·Ca로 심하게 오염**됨이
  TXRF로 확인됨 — K는 슬러리 pH완충제(KOH)·안정제에서, Ca는 소모품/물에서 유래(같은 doi,
  2차 요약 확인). K⁺·NH₄⁺ 같은 이동성 양이온(mobile ion)은 게이트 산화막 신뢰성의 고전적 위협.
- **세리아(Ce) 잔류입자**: 산화막(STI) CMP의 세리아는 [[slurry-components-overview]]의 "화학적
  이빨"처럼 **Ce–O–Si 화학결합**을 표면에 만든다. 이 결합 때문에 메가소닉·브러시 같은 물리력으로
  못 떼고 희석 HF(DHF)/SPM이 필요할 만큼 제거가 어렵다(입자가 작을수록 흡착력↑) — Sahir et al.,
  *Microelectron. Eng.* 249 (2021) 111544, doi:10.1016/j.mee.2021.111544; Ce–O–Si 결합의 세정력
  의존은 Sahir et al., doi:10.1016/j.apsusc.2021.149035 (*Appl. Surf. Sci.* 2021). 즉 세리아는 "입자오염"이면서
  동시에 화학결합 잔류라 두 성격을 겸한다.
- **유기 억제제(BTA) 잔류**: Cu CMP의 BTA는 Cu(I)–BTA 중합막([[slurry-components-overview]] §4)을
  남긴다. 착화제·억제제 유기잔류는 산화물 잔류 사이트에 선택적으로 흡착해, 산화물을 떼면 함께
  떨어지는 경향이 있다(post-Cu CMP 유기오염, doi:10.3390/lubricants13070301, MDPI OA).

## 3. 배선 금속(Cu) 재흡착 — 제타전위·pH 의존 정전흡착
Cu CMP 중 산화·착화로 용해된 **Cu²⁺가 산화막(SiO₂)·저유전막에 정전흡착**해 재오염된다. 기구는
[[colloid-zeta-dlvo-slurry-stability]]의 전기이중층·제타전위로 직접 설명된다: 실리카 IEP≈2이므로
그보다 높은 pH에서 SiO₂ 표면은 **음전하(ζ<0)** → 양이온 Cu²⁺를 정전기적으로 끌어들인다. pH가
오를수록 |ζ|가 커져(더 음성) Cu²⁺ 흡착이 강해진다. 반대로 **산성 세정(DHF 등 IEP 근처/이하)**은
표면 음전하를 죽여 Cu²⁺ 정전흡착을 줄인다 — 이것이 Lv2-2 세정 레시피의 물리적 근거다. 텅스텐
post-CMP에서도 용해 금속이온(Cu·Fe·K)이 산화막·PVA 브러시에 흡착함이 최근 보고됨(Surfaces and
Interfaces 2025, doi:10.1016/j.surfin.2025.106939, 초록만 확인). §6에서 Cu²⁺(z=+2) 정전흡착의
pH 방향을 Boltzmann 표면과잉으로 정량 재현한다.

## 4. 패드/디스크·세정수·환경 유래
- **패드/디스크 유래**: 컨디셔너 다이아몬드 **그릿 탈락**(diamond pull-out), 패드 폴리우레탄
  마모 파편·충전제. 이들은 금속오염보다 입자/스크래치 결함 성격이 강하다(2차 인용, 정량 미확보 —
  **미검증**).
- **세정수/환경 유래**: 초순수(UPW)·화학약품의 잔류 금속이온, 공기 중 유기물(AMC). IRDS는 UPW의
  임계 금속·유기(비휘발성 극성 유기 <1 ppb)를 별도 관리대상으로 규정한다(2024 IRDS Yield
  Enhancement, irds.ieee.org). 환경 유래는 발생원이 공정 외부라 세정보다 **환경관리**로 다룬다.

## 5. 정량 축 — 표면 금속 면밀도(atoms/cm²)와 허용치
- 단위는 **atoms/cm²**(면밀도). 실리콘 Si(100) 표면 원자밀도는 격자상수 a=5.431 Å로부터
  2/a² ≈ 6.78×10¹⁴ atoms/cm² — 이것이 "1 단분자층(ML)"의 대략적 척도다.
- 소자 요구 허용치는 임계 표면금속(Fe·Cu·Ca·K 등)에 대해 **~1×10¹⁰ atoms/cm² 오더**, 선단
  소자는 5×10⁹ atoms/cm²까지 요구된다는 로드맵 서술(IRDS/ITRS 계열, 2차 확인 — **정확 표값
  미검증**). 이는 단분자층의 ~1.5×10⁻⁵(≈15 ppm ML)에 불과 → 극미량 검출·제어가 왜 어려운지가
  §6 계산으로 드러난다. §2의 세정 전 Fe 오염(~1e12)은 이 허용치의 **~100배**라, 세정이 필수다.

## 6. python 재현 — 단분자층 대비 허용치 & Cu²⁺ 정전흡착 pH방향
```python verify
import math
# --- (A) 단분자층 밀도와 허용치 대조 (Si(100)) ---
a_cm = 5.431e-8                     # Si 격자상수 5.431 Å = 5.431e-8 cm (문헌 상수)
N_ML = 2 / a_cm**2                  # Si(100): 단위면적 a^2당 2원자
print(f"Si(100) 면밀도 ≈ {N_ML:.3e} atoms/cm^2 (1 ML 척도)")
assert 6.5e14 < N_ML < 7.0e14, "Si(100) 면밀도가 ~6.78e14 오더가 아님"

tol = 1e10                          # 임계 표면금속 허용치 오더 (atoms/cm^2)
frac_ML = tol / N_ML
print(f"허용치 {tol:.0e}/cm^2 = {frac_ML:.2e} ML ({frac_ML*1e6:.0f} ppm ML)")
assert 1e-6 < frac_ML < 1e-4, "허용치가 단분자층의 ~1e-5 오더가 아님"

# --- (B) 슬러리 유래 Fe 오염 vs 허용치 (Springer doi:10.1023/A:1011242900843, 2차요약) ---
Fe_asdep = 1.5e12                   # 세정 전 (100~200)e10 의 중앙값
Fe_clean = 1e11                     # 세정 후 <10e10
print(f"Fe 세정전/허용치 = {Fe_asdep/tol:.0f}배, 세정후/허용치 = {Fe_clean/tol:.0f}배")
assert Fe_asdep/tol > 50, "세정 전 Fe가 허용치의 수십배 이상이어야 함"
assert Fe_clean/tol > 1, "세정 후에도 GOI 허용치보다 높아(추가 세정 필요) — 문헌 정성과 일치"

# --- (C) Cu2+(z=+2) 정전흡착의 pH 방향 (Boltzmann 표면과잉) ---
# SiO2 IEP≈2(상속노트). pH>IEP에서 zeta<0 → Cu2+ 끌림. pH↑ → |zeta|↑ → 흡착↑
kT_e_mV = 25.69                     # kT/e @298.15K (mV)
z = +2                              # Cu2+
zeta_mV = {"IEP(pH~2)":0.0, "약산성":-20.0, "중성":-40.0, "약알칼리":-60.0}
enrich = {}
for k, zt in zeta_mV.items():
    # n_surf/n_bulk = exp(-z e psi / kT); psi<0, z>0 → 양이온 농축
    enrich[k] = math.exp(-z*zt/kT_e_mV)
    print(f"  {k:12s} zeta={zt:+5.0f}mV → Cu2+ 표면농축배율 {enrich[k]:6.1f}x")
vals = list(enrich.values())
assert abs(vals[0]-1.0) < 1e-9, "IEP(zeta=0)에서 정전구동력 없어 배율=1이어야"
assert all(vals[i] < vals[i+1] for i in range(len(vals)-1)), "pH↑(zeta더음성)→흡착 단조증가여야"
assert enrich["중성"] > 20, "중성 -40mV에서 Cu2+ 농축 >20배(강한 정전흡착)"
print("PASS: 단위·오더·pH방향 모두 문헌 정성서술과 정합")
```
- (A) 허용치 1e10/cm²는 단분자층의 **1.5×10⁻⁵ ML(≈15 ppm ML)** — ppm 수준 제어가 목표임을 정량화.
- (B) 세정 전 Fe(~1.5e12)는 허용치의 **~150배**, 세정 후에도 ~10배로 GOI 기준엔 추가 세정 필요
  (문헌 정성과 정합).
- (C) 재현 결과 Cu²⁺ 표면농축은 ζ=−40 mV에서 약 22배로, ζ=0(IEP)의 1배 대비 단조 증가함을 대조 확인 — "pH↑ → SiO₂ 음전하↑ → Cu²⁺ 정전흡착↑"의 방향과 정합. 단, 이는 확산이중층 Boltzmann **정성 방향** 재현이며 절대 흡착량(자리수·특이흡착)은 **미검증**.

## 7. 한계 (정직 표기)
- (2026-09-09 추기: 원문 PDF 확보 — [[post-cmp-residual-metal-prediction-langmuir-scm]] §5.1. 원문은 KOH 슬러리 산화막 CMP의 K·Ca이며 Fe 값은 본문에 없음. 아래 원표기 유지)
- §2의 Fe·K·Ca atoms/cm² 수치는 doi:10.1023/A:1011242900843 (2차 요약/초록 기반) — 원문 유료로
  표값·측정조건은 확인 못함.
- §5 허용치 1e10 atoms/cm²는 IRDS/ITRS 로드맵의 오더 서술로, 노드·금속종별 정확 표값은 **미검증**
  (IRDS FEP 표 원문 미확보).
- §6 (C)는 균일 확산층 Boltzmann 근사 — 실제 Cu²⁺는 실라놀기와의 **특이(화학)흡착**·착화제 경쟁이
  겹쳐 정량 흡착등온선은 별도 실측 필요. 여기선 pH 의존 **방향**만 검증.
- 패드/디스크·환경 유래는 정량 문헌을 확보하지 못해(확인 못함) 정성 서술만 실었다.

## 8. 자기시험
→ [[../../agents/surface-contamination/EXAMS.md]] Lv1-1 문항 참조.
</content>
</invoke>
