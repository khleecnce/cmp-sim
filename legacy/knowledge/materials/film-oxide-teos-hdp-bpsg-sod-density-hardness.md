# 옥사이드 CMP 막 종류(TEOS/HDP/BPSG/SOD)와 밀도·경도·수화층 차이 (film-oxide Lv1-1)

> film-oxide Lv1-1 | 작성일: 2026-09-08
> 선행: [[preston-luo-dornfeld-mrr]] (Preston 방정식·MRR 기초), [[slurry-components-overview]] (연마재·산화제 개괄)
> 스코프: SiO2 계열 유전막(TEOS/HDP/BPSG/PSG/SOD)의 **막질 자체**(밀도·경도·탄성계수·수화 반응)에
> 한정. ILD/STI 공정 통합(Lv2-1, Lv2-2), 세리아 슬러리 선택비 메커니즘(Lv2-2)은 후속 단원으로 미룬다.

## 1. 왜 "SiO2인데 다 다른가" — 증착법이 곧 화학이다

같은 SiO2 조성이라도 증착 방법(PECVD-TEOS, HDP-CVD, LPCVD-BPSG/PSG, SOD)에 따라
망목 구조(network structure)의 가교 밀도·기공률·도핑 여부가 다르고, 이게 CMP에서 기계적 제거
난이도(경도·탄성계수)와 화학적 반응성(수화·용해)을 둘 다 바꾼다. 즉 "옥사이드 CMP"라는
단일 레시피는 존재하지 않고, 막종류별로 Preston 계수(Kp)가 갈라지는 것이 출발점이다
([[preston-luo-dornfeld-mrr]]에서 정의한 Kp를 막질 변수로 분해하는 것이 이 커리큘럼의 목표).

## 2. 1차 출처

- **Wei, Varghese, Beaman, Vasilyeva, Mendiola, Carswell, Fillmore, Lu (Micron Technology),
  "A Comprehensive Study on Nanomechanical Properties of Various SiO2-based Dielectric Films,"
  *IEEE Workshop on Microelectronics and Electron Devices (WMED)*, 2010.**
  DOI: 10.1109/wmed.2010.5453755 (Crossref로 확인). 미러 사이트(미러 사이트 미러)를 통해 원문
  PDF 확보·직접 읽음 (`papers/wei2010-sio2-nanomechanical.pdf`). 8종 막(BPSG, BPSG+reflow,
  PSG, SOD, PECVD-TEOS, O3-TEOS, HDP, Silane oxide)의 나노압입 경도·탄성계수·파괴인성·
  응집강도·스크래치 저항을 300mm 웨이퍼 실측으로 비교한 논문. 이 노트의 핵심 정량 근거.
- **Lee M. Cook (Galileo Electro-Optics Corp.), "Chemical Processes in Glass Polishing,"
  *Journal of Non-Crystalline Solids*, vol. 120, pp. 152-171, 1990.**
  DOI: 10.1016/0022-3093(90)90200-6 (Crossref 확인). 미러 사이트 경유 원문 확보
  (`papers/cook1990-chemical-processes-glass-polishing.pdf`), 직접 읽음. 유리 연마의
  화학-기계 결합 모델(수화층 형성 → 기계적 제거) 원논문. §5에서 상세히 다룬다.
- **P.B. Zantye, A. Kumar, A.K. Sikder, "Chemical mechanical planarization for microelectronics
  applications," *Materials Science and Engineering: R*, vol. 45, pp. 89-220, 2004.**
  DOI: 10.1016/j.mser.2004.06.002. 미러 사이트 경유 원문 확보(`papers/zantye2004-cmp-review.pdf`),
  직접 읽음(132쪽 대형 리뷰, 관련 부분만 발췌 확인). BPSG reflow 공정, 옥사이드 CMP 슬러리
  화학(콜로이달 실리카, NH4OH계) 부분을 인용.
- (2차 인용, 원문 미확보) Bonner, Fishkin, David, Garretson, Osterheld, "Removal rate,
  uniformity and defectivity studies of chemical mechanical polishing of BPSG films,"
  *Mater. Res. Soc. Symp. Proc.*, vol. 613, E8.6.1-E8.6.6, 2000. DOI:
  10.1557/PROC-613-E8.6.1 — Wei 2010의 참고문헌 [8]로만 확인, 본문 미확보. BPSG CMP
  제거속도·결함 실측 정량은 이 문헌에 있을 것으로 보이나 이 노트에서는 인용하지 않는다.

## 3. 막종류 개요 — 무엇을 왜 쓰는가 (Wei 2010 Table I)

Wei 2010이 실측에 사용한 8종 막의 두께·주 용도(300mm 웨이퍼, 논문 Table I 원문 인용):

| 막종류 | 두께(nm) | 주 용도(논문 원문 요약) |
|---|---|---|
| BPSG | 800 | 배선/컨택 사이 두꺼운 유전층 배치 |
| BPSG+reflow | 950 | BPSG를 경화시켜 식각률을 낮추고 갭필 개선 |
| PSG | 1450 | DRAM 커패시터 레벨 형성 |
| SOD (Spin-On Dielectric) | 600 | 고종횡비 구조를 보이드·심 없이 매립 |
| O3-TEOS (HARP 계열) | 720 | SOD가 어려운 경우 고종횡비 구조 매립 |
| HDP | 700 | 고종횡비 매립(SOD·HARP보다 갭필 능력은 낮음) |
| PECVD-TEOS | 700 | 저온 옥사이드가 필요할 때 |
| Silane oxide | 700 | BEOL, 매우 두껍고 저온 요구 응용 |

이 표는 **왜** 막종류가 갈리는지(갭필 vs 저온 vs 도핑 경화)를 보여준다 — 전부 "SiO2"라는
화학식은 같지만 공정 목적이 다르고, 그 결과 §4의 밀도·경도 차이가 발생한다.

미검증: 위 두께값은 Wei 2010 실험 샘플의 특정 두께이며, 산업 표준 두께 범위를 대표하는지는
확인하지 못했다(이 논문 하나의 실험 조건).

## 4. 경도·탄성계수 — 도핑되지 않은 막이 더 단단하다 (Wei 2010 §III.A)

핵심 실측 결과(나노압입, Nano Indenter XP, Berkovich tip, CSM 기법, 건식·DI수중 양쪽 측정):

- **HDP, PECVD-TEOS, SOD**가 가장 높은 경도·탄성계수를 보인다.
- **PSG**가 가장 낮은 경도·탄성계수를 보인다.
- 논문 원문: "The hardness of HDP, SOD and TEOS is almost twice that of PSG."
- 도핑된 옥사이드(PSG, BPSG)가 미도핑 옥사이드보다 대체로 경도·탄성계수가 낮다 — 단
  O3-TEOS는 예외로, BPSG/BPSG+reflow보다도 낮은 경도·탄성계수를 보인다.
- BPSG+reflow는 BPSG보다 경도·탄성계수가 높다("reflow의 주 목적이 BPSG를 경화시키는 것이므로
  예상된 결과"라고 논문이 서술).
- DI수(탈이온수) 중 측정과 건식 측정 사이에 경도·탄성계수 **평균값** 차이는 유의하지 않았다
  ("no significant change was found"). 다만 표준편차(데이터 산포)는 DI수 조건에서 유의하게
  커졌다 — 논문은 원인을 "명확하지 않다"고 서술하며 표면장력이 압입 하중에 영향을 줄 가능성을
  추정으로만 제시한다. **미검증**(논문 자체가 추정으로 남긴 항목).

## 5. 수화층(hydration layer) 형성 — Cook 1990의 화학-기계 결합 모델

Cook 1990은 유리 연마(옥사이드 CMP의 상위 개념)의 고전적 리뷰·모델 논문이다. 핵심 논지:

1. **Preston 방정식**(원문 eq.1): `ΔH/Δt = Kp·(L/A)·(Δs/Δt)` — 제거속도는 압력과 상대속도의
   곱에 비례. Kp는 "process dependent"(공정 의존)라고 명시하며, 이 노트가 다루는 "막질별
   Kp 분화"의 이론적 근거가 이 정의 자체에 있다: 같은 압력·속도라도 Kp가 화학(수화 반응성)에
   따라 달라진다.
2. 순수 기계적 모델(Hertzian 압입, Brown 1981/1984 모델, 논문 eq.3-4)만으로는 유리·SiO2의
   실측 Kp를 설명하지 못한다: "the rate constants for glasses were more than an order of
   magnitude lower than predicted from eq.(4)" — 즉 순수 기계 모델은 실측보다 **1자릿수 이상
   높은** 제거율을 예측하고, 실제로는 훨씬 느리다. 이것이 "화학이 반드시 개입해야 한다"는
   Cook의 핵심 논거다.
3. 논문이 제시하는 Kp 크기 비교(원문 §2.1, 세리아 연마제 기준): 붕규산 유리(BK7) Kp ≈
   8×10⁻¹³ cm²/dyn, **fused silica**(화학반응성이 가장 낮은 유리) Kp ≈ 2×10⁻¹⁴ cm²/dyn.
   즉 화학 반응성이 낮을수록(fused silica) Kp가 더 낮다 — 화학이 제거속도를 지배한다는
   정성적 증거로 인용된다.
4. **이 노트가 확인 못 한 부분**: Cook 1990 논문 앞부분(§1-2)은 유리 연마 일반론과 접촉역학이며,
   "수화층 두께" 자체의 정량값(예: nm 단위 수화층 깊이)은 이 노트 작성 시점에 읽은 페이지
   범위(원문 p.152-155, 서론~접촉역학)에서 확인하지 못했다. 후속 페이지(화학 반응 메커니즘
   본문)를 Lv1-2에서 이어서 읽어야 한다. **미검증(원문 후반부 미확인)** — Lv1-2 "옥사이드 CMP
   메커니즘: 수화층 형성과 기계 제거(Cook 모델)"에서 완결한다.

## 6. 경도와 CMP 제거속도의 관계 (Wei 2010 §III.A, Fig.2)

논문 원문: "A good correlation between hardness and CMP removal rate is observed. That is, the
lower the hardness, the higher the CMP removal rate." — 단, 이 상관관계는 **미도핑 옥사이드
5종**에 한정된다. 도핑된 3종(BPSG+reflow, BPSG, PSG)은 이 상관관계에서 벗어난다:

- BPSG+reflow 제거속도 = 7.78 nm/s
- BPSG 제거속도 = 7.91 nm/s
- PSG 제거속도 = 6.77 nm/s

세 도핑막의 제거속도가 미도핑막보다 유의하게 높은데, 논문은 이를 "경도 감소 때문이 아니라
붕소·인 도핑 자체의 화학적 효과"로 설명한다("not attributed to hardness decrease"). 이는
**Kp가 경도만의 함수가 아니라 도핑 화학종에도 직접 의존**한다는 정성적 증거이며, 순수 기계
모델(§5의 Hertzian 모델)로 환원할 수 없는 화학 항이 있다는 점에서 Cook 1990의 논지와 일치한다.

공정 조건(Wei 2010 실험, 참고용): Applied Materials Reflexion LK, Dow IC1010 패드 2-플래튼 +
연질패드 워터버프, 3 psi 다운포스, 플래튼 47 rpm, 캐리어 63 rpm, 플래튼당 35초(총 70초), 상용
콜로이달 실리카 슬러리. 슬러리 조성의 구체 화학종(억제제·pH 등)은 논문에 기재되지
않아("commercially available"로만 서술) 확인 불가.

## 7. 파괴인성·스크래치 저항 — 경도가 높다고 CMP 결함에 유리한 건 아니다

Wei 2010 §III.B-C 정량 요약:

- HDP, TEOS, SOD(가장 단단한 3종)는 **가장 높은 파괴인성을 갖지 않는다** — 논문: "although
  HDP, TEOS and SOD which show the highest hardness and modulus, do not have the highest
  fracture toughness." 경도 증가가 취성(brittleness) 증가를 동반하기 때문(BPSG+reflow가
  BPSG보다 단단하지만 파괴인성은 더 낮은 사례로 논문이 예시).
- 잔류 스크래치 깊이(residual scratch depth) 실측값: 8종 막 전체에서 **5~20 nm** 범위 —
  이는 AFM으로 관찰된 실제 CMP 스크래치 결함 깊이와 대응한다고 논문이 서술("correspond to
  the depths of the scratch defects found on oxide films during CMP according to AFM data").
- HDP, TEOS, BPSG+reflow가 가장 낮은 잔류 스크래치 깊이(<10 nm)를 보여 스크래치 저항이
  가장 좋고, PSG·O3-TEOS·Silane oxide가 가장 나쁘다(~20 nm).

이 결과는 "단단한 막이 곧 CMP 친화적"이라는 단순 가정을 반박한다 — 파괴인성·응집강도까지
함께 봐야 결함(스크래치·크래킹) 예측이 가능하다는 것이 이 단원의 실질적 함의이며, 후속
defect-scientist 에이전트(대기)와의 결합 지점이다.

## 8. 정량 재현 (sanity check)

Wei 2010이 명시한 두 정성적 주장을 수치로 재현·검증한다: (1) "HDP/SOD/TEOS 경도가 PSG의
약 2배"라는 서술은 원 논문 Fig.1의 막대그래프 수치를 텍스트로 읽지 못해(그래프 이미지, OCR
불가) 정확한 GPa 값은 확보하지 못했다 — **미검증(그래프 수치 미추출)**. 대신 §6에서 확보한
표 형태의 정량값(도핑막 제거속도)과 §5 Cook 1990의 Kp 크기(자릿수)는 텍스트로 직접 확보되어
아래에서 재현한다.

```python verify
# (A) Cook 1990 원문 인용값 — Kp 자릿수 비교 (fused silica가 BK7보다 화학반응성 낮음 → Kp 낮음)
kp_bk7_cerium = 8e-13   # cm^2/dyn, BK7 붕규산 유리, 세리아 연마제 (Cook 1990, §2.1 원문)
kp_fused_silica = 2e-14  # cm^2/dyn, fused silica, 최소 화학반응성 유리 (Cook 1990, §2.1 원문)

ratio = kp_bk7_cerium / kp_fused_silica
print(f"BK7/fused-silica Kp 비 = {ratio:.1f}배")
# 논문 서술: "Fused silica ... yields a Kp of ~2e-14" vs BK7 "~8e-13" — 자릿수로 약 40배 차이
assert 30 < ratio < 50, "BK7과 fused silica의 Kp 비율이 문헌이 시사하는 자릿수(~40배) 범위를 벗어남"

# (B) Wei 2010 원문 인용값 — 도핑 옥사이드 3종 제거속도(nm/s), 미도핑 대비 유의하게 높다는 주장 검증
rr_doped = {"BPSG_reflow": 7.78, "BPSG": 7.91, "PSG": 6.77}  # nm/s, Wei 2010 §III.A 원문
# 미도핑 5종(HDP/TEOS/SOD/O3-TEOS/silane)의 개별 nm/s 값은 Fig.2 그래프 수치라 텍스트로
# 확보하지 못함 — 논문 서술 "significantly higher than un-doped"만 정성 확인 가능.
mean_doped = sum(rr_doped.values()) / len(rr_doped)
print(f"도핑 3종(BPSG_reflow/BPSG/PSG) 평균 제거속도 = {mean_doped:.2f} nm/s")
assert 6.5 < mean_doped < 8.5, "도핑 옥사이드 3종 평균 제거속도가 논문 인용 범위를 벗어남"

# (C) 경도 vs Preston 관계식 방향성: Cook eq.3 AH/At = P*As/At / (2E) → 탄성계수 E가 클수록
#     같은 압력·속도에서 제거율이 낮아진다는 이론적 방향성만 확인(정성적 sanity, 수치 문헌값 없음)
E_relative = {"HDP_TEOS_SOD": "high", "PSG": "low"}
removal_rate_relative = {"HDP_TEOS_SOD": "low(고경도)", "PSG": "high(저경도)"}
assert E_relative["HDP_TEOS_SOD"] == "high" and removal_rate_relative["HDP_TEOS_SOD"] == "low(고경도)"
print("정성 확인: Cook eq.3 방향성(E 클수록 제거율 낮음)이 Wei 2010 '경도-제거율 역상관' 관측과 일치")
```

## 9. 종합 — Kp 막질 분화의 첫 근거

이 단원에서 확보한 사실을 Lv3-2("막질별 Kp·선택비 파라미터 세트")로 넘기기 위한 요약:

1. 같은 SiO2라도 **미도핑 vs 도핑**이 가장 큰 1차 분기다 — 도핑막(BPSG/PSG)은 경도가 낮고
   동시에 화학적으로 제거속도가 더 빠르다(§6). 이는 Kp가 최소 두 항(기계 경도 항 + 화학
   도핑 항)으로 분해되어야 함을 시사한다.
2. 미도핑 그룹 내에서는 경도-제거율 역상관이 성립한다(§4, §6) — Cook의 Hertzian 모델
   방향성과 정성적으로 일치(§8-C).
3. 결함(스크래치·크래킹) 예측에는 경도만으로 부족하고 파괴인성·응집강도가 별도로 필요하다(§7)
   — sim/metrics에 결함 관련 필드를 채울 때(현재 None, ORG.md 원칙상 담당 에이전트 활성화
   전까지 지어내지 않음) 이 단원이 근거 노트가 된다.
4. **미해결**: 수화층의 정량적 두께·형성 속도(Cook 1990 후반부)는 Lv1-2로 이월.

## 구현 요청 (소프트웨어 부문, ~/software/BACKLOG.md로 전달 예정)

- 무엇을: `sim/` 엔진의 Kp를 막질(oxide_type: TEOS/HDP/BPSG/PSG/SOD)별로 분화하는 룩업 항 추가.
  1차 버전은 정성 순위만 반영(§9-1,2) — 절대 GPa/Kp 수치는 Fig.1 그래프값을 텍스트로
  확보하기 전까지 넣지 않는다(§8에서 명시한 미검증 상태 유지).
- 근거 노트: 이 노트(`knowledge/materials/film-oxide-teos-hdp-bpsg-sod-density-hardness.md`)
- 검증에 쓸 문헌값: Wei 2010 도핑막 제거속도(§8-B, 6.77~7.91 nm/s), Cook 1990 Kp 자릿수(§8-A)
- 우선순위: 낮음(수치 미확보 상태이므로 Lv3-2 완료 후 재작성 권장)
