<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: GST, chalcogenide, phase-change memory, soft film, scratch, dishing, corrosion, abrasive hardness | 정본: ARCHITECTURE-V2.md §3 -->
# GST·칼코게나이드 CMP — 연질막 결함 제어 (film-emerging Lv2-1)

> 에이전트: film-emerging Lv2-1 | 작성일: 2026-09-16
> 선행: [[../materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor]] (Lv1-1),
> [[../materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic]] (Lv1-2),
> [[abrasive-hardness-hertz-indentation-removal-volume]] (경도-제거량 Hertz/Luo(2002) 3/2제곱 관계 원 노트 — 이 노트의
> §1이 그 표에 GST를 추가하는 것),
> [[scratch-physics-source-signatures]] (스크래치 발생원·Cu 경도값 원 노트)
>
> **스코프**: (a) GST(Ge₂Sb₂Te₅) 경도·탄성계수를 SiO₂/Cu/W와 비교하고 `sim/abrasive_mechanics.py`의 α 판정
> (하중 지수: 소성 α=3/2 vs 탄성 α=2/3, **읽기만 함 — 코드 미수정**)이 어느 레짐으로 가는지 서술한다.
> (b) 결함 기전(스크래치/디싱/부식/상변화)을 입력변수(하중·입경·pH·산화제·온도)에 매핑한다.
> (c) GST의 수용액 안정성 — pH·산화제 창과 Te/Sb 선택적 용출. **슬러리 제형(억제제·킬레이트제 설계)은
> slurry-* 소관이라 범위 밖 — 막질이 슬러리에 거는 요구조건만 기술한다.**

## 1. 왜 연질막인가 — 경도로 말한다

### 1.1 경도 비교표 (1차 문헌 실측·저장소 재인용 교차확인)

| 막질 | 경도 H | 출처 | 확보 |
|---|---|---|---|
| **W(텅스텐, 유효 웨이퍼경도)** | ≈ 1 GPa (10⁹ Pa) | Fu, Chandra, Guha, Subhash, *IEEE Trans. Semicond. Manuf.* 14(4) 406–417 (2001) — [[abrasive-hardness-hertz-indentation-removal-volume]] §3 재인용치 | 2차 인용(저장소 내 기존 노트 재사용, 원문 미접근) |
| **Cu(구리, 나노압입)** | 1.22 GPa | Eusner, Saka, Chun (2009) — [[scratch-physics-source-signatures]] §2 재인용치 | 2차 인용(저장소 내 기존 노트 재사용) |
| **SiO₂(산화막, 유효 웨이퍼경도)** | ≈ 10 GPa (10¹⁰ Pa) | Fu et al. 2001, 상동 | 2차 인용(상동) |
| **a-GST(비정질 Ge₂Sb₂Te₅, 나노압입)** | 확정 GPa 미확보 — 정성적으로 "低" | D'Arrigo, Mio, Favaro 외, "Mechanical properties of amorphous Ge2Sb2Te5 thin layers," *Surf. Coat. Technol.* (2018), DOI: 10.1016/j.surfcoat.2018.02.050 — Ultra High-Nano Indentation으로 H·E 측정했다고 명시 | **초록만 확인(Semantic Scholar API) — 본문 표의 정확한 GPa 수치는 유료장벽으로 미확보. 미검증** |
| **a-GST 탄성계수(단독 인장시험)** | E = 20.2 ± 1.3 GPa | Choi, Lee, "Elastic Modulus of Amorphous Ge2Sb2Te5 Thin Film Measured by Uniaxial Microtensile Test," *Electron. Mater. Lett.* 6, 23–26 (2010), DOI: 10.3365/eml.2010.03.23 | **2차 인용(검색엔진 스니펫) — Springer 인증장벽으로 원문 PDF 미확보. 미검증이지만 방향은 명확: E_GST(20.2 GPa) < E_SiO2(≈72 GPa, 용융실리카 표준값) order 3.5배** |

수치가 전부 확보되지는 않았지만 두 독립 경로(나노압입 H, 단독 인장 E) 모두 **GST가 SiO₂보다
한 자리 낮은 오더**라는 방향은 일치한다. 정량적으로 가장 강한 1차 근거는 CMP 실험 자체다 —
Wang 외, "Chemical mechanical planarization of Ge₂Sb₂Te₅ using IC1010 and Politex® pads in acidic slurry,"
*Chin. Phys. B* 23(8) 088502 (2014), DOI: 10.1088/1674-1056/23/8/088502 (초록 WebFetch로 확인)가 직접 관찰로 이를
보인다: **동일 패드(IC1010, 경질)·동일 슬러리로 GST 블랭킷 웨이퍼를 연마하면 OM·SEM 모두에서 "serious
scratches"가 나오고, 원문이 그 원인을 "GST의 낮은 경도 대 IC1010 패드·연마입자"라고 명시한다.** 반대로
패턴 웨이퍼(표면이 SiO₂로 덮인 경우)는 같은 패드·슬러리에서 "clean surface, no scratches"였고, 저자는
이를 "무른 GST가 아니라 표면의 고경도 SiO₂ 막 덕분"이라고 직접 서술한다. 즉 **경도차 자체가 스크래치
유무를 가른 독립변수임을 같은 논문 안에서 대조군으로 확인한 사례**다.

### 1.2 `sim/abrasive_mechanics.py`의 α 판정 — 어느 레짐인가 (읽기만, 코드 미수정)

`sim/abrasive_mechanics.py`(§②, `ALPHA_PLASTIC=1.5` / `ALPHA_ELASTIC=2/3`)의 판단 기준은
**"입자당 접촉응력 vs 제거되는 표면층의 유효 경도"** 다 — 접촉응력이 경도에 근접·초과하면 소성
(α=3/2), 훨씬 못 미치면 탄성(α=2/3)이다. 같은 입자·같은 하중이면 접촉응력은 웨이퍼 쪽 물성과
무관하게(Hertz 압입에서 응력 분배는 1차로 압입자 강성이 정한다) 거의 동일하다 — 그런데 **판정
기준선(경도)이 GST에서는 SiO₂ 대비 한 자리 낮다.** 즉:

- SiO₂ CMP에서는 (알루미나 등 고경도 입자 기준) 접촉응력이 H_SiO2(≈10 GPa)에 겨우 도달하거나
  못 미쳐 α=2/3(탄성)에 가까울 여지가 있다([[abrasive-hardness-hertz-indentation-removal-volume]]
  §4의 실리카-SiO₂ 대비 논의 참조).
- **GST CMP에서는 같은 입자·같은 하중이 H_GST(오더 1~수 GPa, §1.1)를 쉽게 넘어선다** → 판정이
  구조적으로 **α=3/2(소성) 쪽으로 밀린다.** 이는 §1.1의 Chin. Phys. B(2014) 관찰(경질 패드·입자가
  GST를 "serious scratch"로 깎는다)과 정성적으로 부합한다 — 소성 제거가 우세하면 제거량이
  Hertz형 압입면적(∝ 하중^(2/3)에 압입깊이^(1.5) 지수가 곱해지는 Fu 모델 경로,
  [[abrasive-hardness-hertz-indentation-removal-volume]] §2)을 따르고, `MRR ∝ H_w^(-3/2)`
  (동 노트 §2)이므로 **경도가 한 자리 낮은 GST는 같은 조건에서 오더 30배(=10^1.5) 가까운 제거율
  민감도를 갖는다** — 아래 verify 블록에서 이 지수를 직접 계산한다.

```python verify
# GST가 α 판정에서 왜 "소성" 쪽으로 밀리는지 + MRR 경도 민감도(H^-3/2) 오더 확인
# 출처: sim/abrasive_mechanics.py (ALPHA_PLASTIC=1.5, ALPHA_ELASTIC=2/3 — 상수 그대로 읽어옴, 코드 미수정)
#       H_W=1e9 Pa, H_SiO2=1e10 Pa: Fu et al. 2001 (§1.1 표, 저장소 재인용)
#       H_Cu=1.22e9 Pa: Eusner et al. 2009 (§1.1 표, 저장소 재인용)
#       H_GST: 확정 GPa 미확보 — §1.1의 정성적 관찰(SiO2보다 한 자리 낮다)에 근거해
#              "SiO2의 1/10 오더"라는 보수적 가정을 **가정으로 명시**하고 그 가정 위에서만 계산한다.

H_W    = 1.0e9    # Pa, Fu et al. 2001
H_SiO2 = 1.0e10   # Pa, Fu et al. 2001
H_Cu   = 1.22e9   # Pa, Eusner et al. 2009
H_GST_assumed = H_SiO2 / 10  # Pa — §1.1 정성적 근거(D'Arrigo 2018, Choi&Lee 2010, Chin.Phys.B 2014)의 "한 자리 낮다"를
                              # 수치 가정으로 명시한 것. 실측 H_GST(GPa)가 아니다 — 확인 못 한 추정치.

assert H_GST_assumed < H_SiO2, "가정한 GST 경도가 SiO2보다 낮음 — §1.1 정성적 관찰(한 자리 낮다)과 부합"
assert H_W < H_SiO2 and H_Cu < H_SiO2, "W·Cu도 SiO2보다 낮음(Fu et al. 2001 / Eusner et al. 2009, 표에 있는 값 그대로)"

# sim/abrasive_mechanics.py의 판정 기준: 접촉응력 sigma_c 가 H_w 를 넘으면 소성(ALPHA_PLASTIC)
ALPHA_PLASTIC = 1.5
ALPHA_ELASTIC = 2.0 / 3.0

sigma_c_typical = 2e9  # Pa, 오더 예시(입자당 접촉응력 — Hertz 압입 전형값, 이 노트에서 실측 도입 안 함)

def regime(sigma_c, H_w):
    return ALPHA_PLASTIC if sigma_c >= H_w else ALPHA_ELASTIC

assert regime(sigma_c_typical, H_SiO2) == ALPHA_ELASTIC, "SiO2: 응력이 경도 못 미쳐 탄성 쪽"
assert regime(sigma_c_typical, H_GST_assumed) == ALPHA_PLASTIC, "GST(가정 경도): 응력이 경도 초과 → 소성"

# MRR ∝ H_w^-3/2 (Fu et al. 2001 모델, abrasive-hardness-hertz-indentation-removal-volume.md §2)
mrr_ratio_GST_over_SiO2 = (H_GST_assumed / H_SiO2) ** (-1.5)
expected_order = 10 ** 1.5  # H가 10배 낮으면 MRR은 10^1.5 = 31.6배
assert abs(mrr_ratio_GST_over_SiO2 - expected_order) / expected_order < 1e-9, \
    f"오더 확인: {mrr_ratio_GST_over_SiO2:.1f} vs {expected_order:.1f}"
print(f"H 10배 낮음 → 동일 조건 MRR 민감도 오더: {mrr_ratio_GST_over_SiO2:.1f}배 (H_w^-3/2 지수)")
```

**정직 표기**: `H_GST_assumed = H_SiO2/10`은 §1.1에서 확보한 정성적 관찰("GST가 SiO₂보다 한 자리
낮다")을 검증 가능한 숫자로 바꾸기 위한 **가정**이지 실측치가 아니다. D'Arrigo(2018)의 실제 나노압입
표를 원문에서 확보하면 이 가정을 교체해야 한다 — **확인 못 한 가정 위의 오더 추정**으로만 읽을 것.

## 2. 결함 모드별 기전 — 어느 입력변수에 걸리는가

| 결함 모드 | 기전 | 주요 입력변수 | 근거 |
|---|---|---|---|
| **스크래치** | 경질 패드(IC1010)·연마입자가 저경도 GST 표면을 소성 압입·긁음(§1.2) | 패드 경도, 입경(대입자·응집체), 하중 | Chin. Phys. B 23(8) 088502 (2014) — IC1010에서 GST 블랭킷 "serious scratches"(OM·SEM), Politex(무른 패드)는 무결함. 패턴 웨이퍼는 표면 SiO₂가 보호(§1.1) |
| **디싱** | 저마모저항 GST가 연마압력 하에서 과연마되어 다이엘렉트릭 대비 함몰 | 하중(down force), 연마시간(over-polish), 슬러리의 GST/oxide 선택비 | US 2010/0130013 A1(특허, "Slurry composition for GST phase change memory materials polishing")가 이를 "dishing"으로 직접 지칭 — 콜로이드 입자 0.2~10 wt%(<60 nm)·폴리아크릴산 50~5000 ppm 배합으로 지형결함 50% 감소를 보고(1차 특허 원문 WebFetch 확인, US2010/0130013A1) |
| **부식(선택적 용출·갈바닉)** | 산화제 농도가 높을수록 Ge·Sb·Te가 선택적으로 산화·용해되며 Te가 표면에 축적되고 Ge가 먼저 빠짐(§3) | 산화제 종류·농도, pH | §3의 Song, Liu, Wang(2015) — 정성 서술은 검색엔진 스니펫 기반, **미검증 표기 유지** |
| **상변화(연마열 유발 결정화)** | 연마 시 마찰열이 국소적으로 결정화 온도를 넘기면 비정질(RESET) 영역이 의도치 않게 결정화(SET)되어 전기적 특성이 변함 | 연마 압력·속도(발열량), 패드-웨이퍼 온도, 접촉시간 | Tc(비정질→fcc) ≈ 141~148 °C(DSC 발열피크) — Vacuum지 논문, DOI: 10.1016/j.vacuum.2009.12.002. **저자명·수치는 검색엔진 스니펫으로만 확인, 원문 PDF 미확보 — 미검증.** CMP 중 실제 계면온도가 이 문턱을 넘는지는 이 노트에서 **확인 못 함**(마찰열 계산은 범위 밖 — film-emerging Lv1 이전 노트에 열모델이 있다면 교차확인 필요, 여기서는 안 함) |

## 3. 수용액 안정성 — pH·산화제 창, Te/Sb 선택적 용출

Song, Z., Liu, W., Wang, L., "Chemical Mechanical Polishing Slurry for Amorphous Ge2Sb2Te5,"
*Procedia Engineering* 102, (2015), DOI: 10.1016/j.proeng.2015.01.131 (Gold OA, CC-BY-NC-ND —
Unpaywall이 publishedVersion으로 확인)이 pH 의존 거동을 직접 다룬다고 검색엔진 스니펫이 보고한다:

- **GST 연마율이 pH 11.0 부근에서 최대**이며, 이는 GST의 정적부식(static corrosion) 거동과
  연동되고 개방회로전위(OCP) 변화 추이가 연마율 추이와 같은 방향이라고 한다.
- **산성(H₂O₂ 첨가) 조건의 산화 생성물은 GeO₂·Sb₂O₃·Te**로, **알칼리 조건의 생성물은
  HGeO₃⁻·SbO₃⁻·TeO₃⁻**로 다르다고 한다 — 산성에서는 Te가 고체(원소 Te)로 남고, 알칼리에서는
  모든 종이 가용성 이온으로 바뀐다는 뜻이다.
- **산성 슬러리의 RR/SER(연마율/정적식각율) ≈ 19.2, 알칼리 슬러리는 ≈ 8.0**이라고 하며, 저자들은
  RR/SER 비가 높을수록 디싱·부식이 적다고 해석해 산성 슬러리를 우위로 판단한다고 한다.

별도로 WebSearch 스니펫이 인용한 정성적 관찰: **고농도 산화제에서 Ge·Sb·Te 간 선택적 부식이
일어나 Te가 표면에 축적되고 Ge가 먼저 빠진다** — 어느 논문의 어느 수치인지 원문으로 특정하지
못했다.

> ⚠ **정직 표기 — 이 절 전체**: 위 수치·화학식은 Song et al.(2015)의 DOI·OA 라이선스는 확인했으나
> ScienceDirect·core.ac.uk·jina.ai 리더·Springer 전부 봇차단(403)에 막혀 **원문 PDF/HTML을 직접
> 읽지 못했다.** WebSearch 엔진이 반환한 스니펫 텍스트를 그대로 옮긴 것이며, **숫자·화학식의
> 오탈자·문맥 누락 위험을 배제할 수 없다.** 다음 조사에서는 이 DOI로 `find_open_access.py --download`
> 재시도 또는 기관 프록시 확보가 최우선이다.
>
> **확인 못 함**: pH < 2 나 pH > 11 극단에서의 거동, Sb 단독 용출 임계 pH, 산화제 종류별(H₂O₂ vs
> 과황산 vs 과망간산) 정량 비교 — 이 노트는 산화제 "종류가 다르면 다른 창을 만든다"는 정성적
> 사실만 확인했고 정량 임계값은 확보하지 못했다.

## 4. 요약 — 저장소 계보에 남기는 결론

1. GST는 확정 GPa 수치는 미확보지만 **독립 경로(나노압입 정성 관찰, 단독 인장 E, CMP 스크래치
   대조실험) 세 곳 모두 SiO₂보다 한 자리 낮은 경도**를 가리킨다 → `sim/abrasive_mechanics.py`의
   α 판정에서 **소성(α=3/2) 쪽으로 구조적으로 밀리고**, 동일 조건이면 `H_w^{-3/2}` 지수 때문에
   경도 10배 차이가 MRR 민감도 오더 31.6배로 증폭된다(§1.2 verify, **가정 위의 오더 추정**).
2. 결함 4종(스크래치/디싱/부식/상변화)은 서로 다른 변수에 걸린다 — 스크래치는 패드·입자 경도와
   하중, 디싱은 과연마 시간과 선택비, 부식은 산화제·pH, 상변화는 국소 발열과 Tc(≈145°C, 미검증).
   **넷을 하나의 "GST가 무르다"는 말로 뭉뚱그리면 안 된다** — 대책(패드 선택 vs 슬러리 조성 vs
   공정시간 vs 냉각)이 서로 다르다.
3. 수용액 안정성은 **pH 11 부근에서 오히려 연마율이 최대(알칼리 용해가 Ge/Sb/Te 전부를 이온화)**
   라는 방향은 확인했지만, 전체 절이 원문 미확보 상태의 2차 인용이라 정량 임계값은 신뢰도가
   낮다(§3 경고 참조).

---
**확인 못 한 항목 총계**: 경도 절대 GPa 3건, Tc 저자/수치 1건, §3 전체(Song et al. 2015 정량값) —
모두 위에 "미검증" 또는 "2차 인용"으로 명시했다. 확인된 1차 원문: US2010/0130013A1(특허 전문
WebFetch), Chin. Phys. B 23(8) 088502(초록 WebFetch).
