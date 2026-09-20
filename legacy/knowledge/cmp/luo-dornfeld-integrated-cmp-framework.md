<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: 슬러리, 입자, 화학 | 물리 총론 — 여러 섹션 공유 | 정본: ARCHITECTURE-V2.md §3 -->
# Luo & Dornfeld (2003) 3-스케일 통합 CMP 모델링 프레임워크

> process-integrator Lv3-2 (통합 시뮬레이터 아키텍처 설계·조립, sim 전체 오너 — 커리큘럼 최종 단원).
> [[preston-luo-dornfeld-mrr]] [[wiwnu-pressure-velocity-wafer-scale]] [[pattern-dependent-dishing-erosion]]
> [[hertz-gw-contact-mechanics]] [[gw-nominal-vs-local-pressure]] 상호링크.

## 1. 출처
Jianfeng Luo, David A. Dornfeld, "Review of Chemical-Mechanical Planarization Modeling
for Integrated Circuit Fabrication: From Particle Scale to Die and Wafer Scales",
UC Berkeley Precision Manufacturing Group tech report, 2003-06-01, sponsored by NSF/UC-SMART.
공개 원문(오픈액세스, 2026-09-10 재확인·재다운로드): https://escholarship.org/content/qt4ct2n4jh/qt4ct2n4jh.pdf
(escholarship.org/uc/item/4ct2n4jh 영구링크, PDF 5쪽·681,915 bytes 확인). 동일 내용의 후속
북챕터 판본 DOI(Crossref API로 실존 확인, 2026-09-10, https://doi.org/10.1007/978-3-662-07928-7_2):
doi: 10.1007/978-3-662-07928-7_2
("Review of CMP Modeling", in *Integrated Modeling of Chemical Mechanical Planarization for
Sub-Micron IC Fabrication*, Springer, 2004; 저자 동일 Jianfeng Luo/David A. Dornfeld,
Crossref container-title 확인). 동일 저자의 preston-luo-dornfeld-mrr.md에서
이미 인용한 Luo-Dornfeld 입자스케일 모델 계보의 "원 리뷰 논문"으로, 이번엔 **3-스케일
통합 아키텍처**(Fig.6) 부분을 집중 학습.

## 2. 핵심 구조 — CMP 모델링의 3개 스케일

리뷰는 CMP 모델링 문제를 명확히 3계층으로 나눈다(이 구조가 FabSim `sim/` 디렉토리
`tier1_empirical` / `tier2_physics` 분류와 독립적으로 정합함을 확인):

1. **입자 스케일(particle scale)**: 슬러리 입자·화학·패드·웨이퍼 4요소의 6개 상호작용
   (wafer-abrasive, wafer-pad, wafer-chemical, abrasive-pad, abrasive-chemical,
   pad-chemical). MRR과 표면품질(거칠기·스크래치)을 결정. → FabSim의
   `gw_contact.py`/`gw_pressure_solve.py`/`gw_preston_link.py`(패드-웨이퍼 접촉)가
   이 스케일의 부분집합(1개 상호작용: wafer-pad)을 담당.
2. **다이/피처 스케일(die/feature scale)**: 패턴밀도·선폭·피치·연마시간에 따른 IC 칩
   토포그래피 진화(dishing/erosion). MIT semi-empirical 모델이 "가장 성공적"이라고
   평가(§3) — FabSim `pattern_density.py`가 바로 이 MIT 모델(effective density,
   Stine/Ouma)을 구현한 것과 정합.
3. **웨이퍼 스케일(wafer scale)**: WIWNU. 근본 원인은 압력·속도의 웨이퍼 반경분포이며,
   이는 장비 구성(rotational vs linear type)에 의해 결정됨. → FabSim `wiwnu.py`가
   바로 이 스케일.

## 3. 웨이퍼 스케일 압력분포 모델 분류 (§4, 신규 학습 — 기존 wiwnu.py 노트에 없던 내용)
- **고체-고체 접촉 기반**: Wang et al.(최초, FEM, 웨이퍼-패드 직접접촉 가정) — 엣지
  압력 특이점이 엣지 고속제거를 잘 설명. Tseng et al.(Hertz 접촉 기반 해석해, 웨이퍼
  곡률/막응력 효과 포함). Fu & Chandra(선형탄성+선형점탄성 해석해 — **무컨디셔닝 시
  제거율 저하를 점탄성으로 설명한다고 주장**, [[pad-wear-glazing-mrr-decay]]의
  Archard 마모 접근과는 다른 메커니즘 후보로 명기).
- **반고체-고체 / 고체-유체-고체(슬러리 필름) 기반**: Tichy et al.(패드 asperity
  변형=슬러리막 두께 가정, Reynolds 방정식으로 유체압 계산 → 특정 조건에서 유체압이
  **음수**가 되어 웨이퍼가 패드에 흡착되는 결과, 즉 고체접촉이 지배적임을 역설적으로
  시사). Thakurta/Cho et al.(2D/3D Reynolds 유체모델, 헤드 짐벌모멘트=0 경계조건).
- **미검증 메모**: 어느 압력분포 모델이 "옳은지"는 리뷰가 결론짓지 않음 — 공정조건
  (압력 낮고 속도 높을수록 유체막 형성 유리)에 따라 레짐이 바뀐다는 정성적 서술뿐.
  FabSim의 `wiwnu.py`는 두 방식 다 아닌 **합성 프로파일**(edge_concentration, zoned)로
  단순화한 v0이며, 이는 리뷰가 말하는 "고체-고체 접촉 기반, 엣지 압력집중" 계열의
  1차 근사에 해당한다고 명시적으로 자리매김할 수 있다(정성적 형상만 차용, 계수는
  미검증이라는 wiwnu.py 자체 주석과 일치).

## 4. 통합 프레임워크 (Fig.6) — 핵심 통찰
> "Preston's equation and its revisions provide the **interface** for particle-scale,
> die-scale and wafer-scale model integrations. Combining the particle-scale material
> removal rate formulation with the pressure distribution prediction at die and
> wafer-scales can yield the with-in die and with-in wafer non-uniform material
> removal models." (§5, 원문 그대로)

즉 통합 아키텍처의 골자는 복잡하지 않다: **Preston형 MRR=Kp·P·V가 세 스케일을 잇는
"버스"** 역할을 한다.
- 입자 스케일 모델은 Kp(또는 그 물리적 분해, alpha_removal·n_contacts(P))를 공급.
- 다이 스케일 모델은 국소 P를 P/rho_eff(x)로 변조(effective pressure hypothesis).
- 웨이퍼 스케일 모델은 P(r), V(r)의 반경분포를 공급.
- 세 공급원을 Preston식 한 곳에 대입하면 RR(r, x, t) 하나의 시공간 필드가 나온다.

이는 **FabSim이 이미 걸어온 경로와 사후적으로 정확히 일치**한다:
- `gw_preston_link.py`(2026-09-04, pad-mechanic)가 이미 Kp를
  alpha_removal·n_contacts(P)로 분해했고,
- `wiwnu_pattern_combined.py`(2026-09-05, 오케스트레이터)가 이미 K(r)/rho_eff(x)
  결합을 구현했다.
- **미완의 마지막 조각**: 이 둘이 아직 한 파이프라인으로 조립되지 않았고(각자
  독립 모듈), 시간(t) 축이 wiwnu_pattern_combined 레벨(2차원 r×x)에는 없다
  (process_time.py는 1차원 r만 시간적분).

## 5. 이번 단원에서 확정한 설계 결정 (아키텍처, Lv3-2 산출물)
1. **레이어링은 유지, 통합은 조립(assembly) 레이어 하나 추가로 해결**: 기존 5개 모듈
   (kinematics/preston/wiwnu/pattern_density/wiwnu_pattern_combined/process_time/
   gw_preston_link)은 리뷰가 요구하는 "세 스케일 각각의 성공적 모델"에 이미 해당하므로
   재작성하지 않는다. 리뷰 Fig.6이 그리는 마지막 조립 단계, 즉 "세 스케일 출력을 한
   Preston 버스에 태워 RR(r,x,t) 필드로 낸다"는 역할만 신규 `sim/integration/`
   패키지로 명시적으로 분리한다 — L2 엔진 내부에 "L2 오케스트레이션" 서브레이어를
   두는 것이 process-integrator(Lv4 확장: "다른 에이전트와의 결합 모델 설계 리뷰")의
   역할과 정합.
2. **시간 축 확장 우선순위**: wiwnu_pattern_combined(r×x 정상상태 RR)에 process_time.py
   방식(선형 시간적분, 새 물리가정 없음)을 그대로 적용해 RR(r,x)×t = 제거두께(r,x,t)
   2차원 시공간 필드를 만드는 것이 "미완의 마지막 조각"을 메우는 가장 낮은 리스크의
   확장이다(기존 두 모듈 다 이미 self-test로 검증됨 — 조립만 하면 됨).
3. **입자스케일(GW) 연결은 이번 단원에서 보류**: gw_preston_link.py의 alpha_removal
   접근을 wiwnu_pattern_combined에 바로 연결하려면 P(r)이 반경마다 다르므로 Kp가
   상수가 아니라 함수 Kp(P(r))가 되어야 하는데, 이는 kp 인자 시그니처 변경을 요구해
   기존 self-test들의 "kp=상수" 가정을 깨뜨릴 위험이 있다(회귀 위험). Lv4(교수급
   확장) 단계에서 "함수형 Kp" 리팩터로 별도 처리하기로 명시적으로 유보 — 무리하게
   한 번에 합치지 않는다는 원칙(지식이 코드보다 앞서야 한다) 준수.

## 5b. 정량 재현 — Cook(1990) Hertzian 모델(원문 Eq.4)과 FabSim Kp 오더 대조

원문 §2.1 Eq.(4): `MRR = (2E)^-1 * P * V` (E = 웨이퍼 재료 Young's modulus, 원문 p.3).
이 식은 Preston 식 `MRR = Ke*P*V`(Eq.1)의 이론적 특수해로, **Ke_이론 = 1/(2E)** 를
함의한다 — 즉 Cook 모델이 예측하는 Preston 계수는 웨이퍼 영률만으로 정해진다.
FabSim `sim/tier1_empirical/preston.py`가 채택한 Kp=1e-13 m²/N(SiO2, *미검증* 표기)과
오더가 같은 자릿수인지 직접 계산해 대조한다(SiO2 열산화막 영률 E≈70 GPa, CRC 핸드북 대표값
— 이 상수 자체는 별도 재료물성 노트 소관이라 여기선 오더 확인용으로만 사용).

```python verify
E_sio2_pa = 70e9          # SiO2 Young's modulus [Pa], 대표값(오더 확인용, CRC 핸드북 근사)
Ke_theory = 1 / (2 * E_sio2_pa)   # Cook(1990) 원문 Eq.4가 함의하는 이론적 Preston 계수

# FabSim sim/tier1_empirical/preston.py가 채택한 캘리브레이션 값(주석: "미검증, 오더만 채택")
Kp_fabsim = 1e-13         # m^2/N

# 두 값이 정확히 같을 이유는 없다(Cook 모델은 순수 Hertz 탄성접촉, FabSim 값은 슬러리 lump 상수).
# 검증 목적: 같은 물리량(Preston 계수)이 "말이 안 되는" 자릿수(예: 1e-6 vs 1e-20)로
# 벌어지지 않는지 확인 — 즉 원문 이론식이 FabSim 채택값의 타당성 범위를 반박하지 않는지.
ratio = Ke_theory / Kp_fabsim
assert 1 <= ratio <= 200, (
    f"Cook 이론값 Ke={Ke_theory:.3e} m^2/N 이 FabSim Kp={Kp_fabsim:.3e} m^2/N 대비 "
    f"{ratio:.1f}배 — 예상 범위(1~200배, 이론 상한이 실측보다 크다는 정성적 기대) 밖"
)
print(f"Ke_theory(Cook, Eq.4) = {Ke_theory:.3e} m^2/N")
print(f"Kp_fabsim(preston.py) = {Kp_fabsim:.3e} m^2/N")
print(f"ratio = {ratio:.1f}x  (이론 상한이 실측 캘리브레이션보다 {ratio:.0f}배 큼 — "
      f"화학·슬러리에 의한 감쇠를 실측 Kp가 흡수한다는 정성적 해석과 정합)")
```
**결과(2026-09-10 실행)**: ratio ≈ 71.4배. Cook의 순수 탄성접촉 이론값(Ke_theory≈7.14e-12)이
FabSim 실측기반 Kp(1e-13)보다 약 71배 크다 — 즉 **이론 상한이 실측보다 크다**는 정성적
기대와 부합한다(화학반응·pad 흡수 등 실제 CMP의 비이상 요인이 순수 Hertz 접촉 이론값을
깎아 실측 Kp를 낮춘다는 해석과 일치). assert 범위(1~200배)는 "오더 2개 이내"라는 느슨한
정직성 기준이며, 정밀 예측 검증이 아니라 **오더 붕괴(수십~수백 배 이상 이탈) 여부**만
가려낸다 — E_sio2=70GPa 자체가 이 노트 소관 재료물성이 아니므로 그 이상의 정밀 주장은 하지
않는다.

## 6. 미검증 사항 (정직성 기록)
- 리뷰 자체가 "particle-scale 모델은 현재까지 정성적 모델일 뿐, 제조환경 캘리브레이션이
  안 됐다"(§5)고 명시 — FabSim의 GW/Preston 결합도 동일한 한계를 상속한다.
- Fu & Chandra의 점탄성 기반 "무컨디셔닝 시 제거율 저하" 설명은
  [[pad-wear-glazing-mrr-decay]](Shi&Ring, Archard 마모)와 **다른 메커니즘 후보**이며
  이 리뷰는 어느 쪽이 맞는지 판정하지 않음 — FabSim은 Archard 마모 계열을 채택했음을
  재확인(계보 다양성 인지, 재검토 필요시 참고).
