<!-- V2-SECTION: R2-slurry(연계) | 작성 2026-09-13 | tool-post-clean Lv1-1 -->
# Post-CMP 세정 "공정" 관점의 오염 발생원 — 브러시 적재·교차오염·세정화학 자체 잔류

> 에이전트: tool-post-clean Lv1-1 | 작성일: 2026-09-13
> 관련(표면오염 정의/분류 관점 — 중복 없이 상호보완): [[post-cmp-metallic-contamination-sources]](슬러리 화학이
> 남기는 오염원), [[post-cmp-defect-classification-and-inspection]](결함 유형의 조작적 정의·검사장비),
> [[post-cmp-adsorption-cleaning-chemistry]](흡착 메커니즘·제거 화학·막질별 레시피)
> 물성 재사용: [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]](Cu(OH)₂ 용해도곱 logKsp=-19.06 도출)

## 1. 왜 "세정 공정 관점"이 따로 필요한가
[[post-cmp-metallic-contamination-sources]]는 오염을 **슬러리 화학이 웨이퍼에 남기는 것**(Fe 촉매, Ce
잔류, Cu²⁺ 재흡착)으로 다뤘고, [[post-cmp-defect-classification-and-inspection]]은 오염이 만든 **결함의
조작적 정의와 계측**을 다뤘다. 이 노트는 다른 축을 본다 — **세정 공정 자체(브러시·메가소닉·세정액)가
새로운 오염을 만들거나 기존 오염을 다음 웨이퍼로 옮기는 경로**다. 세 가지 오염 유형(입자·유기 잔류·금속
이온)마다, "세정 장비/약액이 어떻게 그 오염의 발생원이 되는가"를 1차 문헌 기준으로 정리한다. 이 관점이
중요한 이유는 실무적이다 — 슬러리 화학을 아무리 개선해도, 세정 공정 자체가 오염을 재생산하면 스펙을
못 맞춘다.

## 2. 입자 오염 — 브러시가 오염을 "먹었다가 다음 웨이퍼에 뱉는다"
**Wortman-Otto, K.M., Watson, D., Dussault, D., Keleher, J.J. (2022). "Coupling Supramolecular
Assemblies and Reactive Oxygen Species (ROS) with Megasonic Action for Applications in Shallow Trench
Isolation (STI) Post-Chemical Mechanical Planarization (p-CMP) Cleaning." *ACS Omega* 7(30), 26029–26039.
DOI: 10.1021/acsomega.2c00683 (PMC9352252, OA CC BY-NC-ND, 전문 확보:
`data/corpus/fulltext/doi_10.1021_acsomega.2c00683.xml`)**

- 저자들은 접촉식 PVA 브러시 세정의 근본 한계를 명시한다: "traditional brush cleaning can be effective in
  removing nanoparticles… but this removal mechanism has shown to also induce further defectivity. This
  increase in wafer defectivity can be attributed to the **uptake of polish waste (i.e., slurry, pad,
  organic residue, etc.) into the brush matrix**, which under contact modality results in further defect
  formation (i.e., **waste redeposition and scratching**)." 즉 브러시는 입자를 제거하는 도구인 동시에,
  다공성 매트릭스에 슬러리·패드 파편·유기물을 흡수했다가 **다른 웨이퍼(또는 같은 웨이퍼의 다른 지점)에
  재부착시키는 저장소**로 작동한다 — 이것이 "세정 공정이 만드는 입자오염"의 1차 기구다.
- 이를 줄이려고 시도한 것이 **비접촉식 메가소닉**(BowlMeg, ProSys Inc.)이다. 실험 조건은 파워 0.5–1.5
  W/cm², 시간 60–600 s이며, 브러시 세정 대비 메가소닉 세정에서 (예외 1건을 제외하고) 입자 계수 변동성이
  유의하게 낮았다 — 브러시가 웨이퍼 표면과 물리 접촉하지 않으므로 "먹었다 뱉는" 경로 자체가 줄어든다는
  논리다. 단, 저출력 정적(static) 메가소닉 탱크의 일부 계면활성제(P-103)는 **장시간에서 오히려 세정효율이
  무너지는 재부착(particle redeposition) 신호**를 보였다 — 즉 비접촉식도 유체역학 조건(정적 탱크·장시간)에
  따라 입자를 재부착시킬 수 있다(저자 해석, 정성).
- 검출 한계: 형광 다크필드 현미경(sulforhodamine B 염색, 532 nm 여기)의 CeO₂ 검출 한계는 **19 nm**이며,
  저자는 "50 nm 미만의 잔류물이 더 있을 수 있다"고 명시한다 — 즉 이 방법론 자체도 나노스케일 잔류입자를
  놓칠 수 있음을 저자가 인정한다.
- 관련 1차 문헌(초록만 확인, 미검증): Hsu, Luo, Berar, "Understanding the formation of circular ring
  defects in post-CMP cleaning," *Solid State Phenom.* 219 (2015) 153–156,
  https://doi.org/10.4028/www.scientific.net/SSP.219.153 — 제목 자체가 "세정 공정이 만드는 고리형 결함"을
  가리키나, 이번 조사에서는 초록 이상을 확보하지 못했다.

## 3. 유기 잔류 — 부식억제제·세정 첨가제 "그 자체"가 잔류막이 된다
**KR102113995B1, "A cleaning composition and method for cleaning a semiconductor device substrate after
chemical mechanical polishing" (EKC Technology, 우선일 2012-09-17, 등록 2020-05-22). 전문 확보:
`data/corpus/fulltext/patent_KR102113995B1.txt`.**

- 이 특허의 배경 설명(명세서 본문)이 유기 잔류 발생 기구를 명시적으로 서술한다: "CMP 슬러리 및 CMP 후
  세정제는, 구리 상호접속부 표면 상에 임시 보호 층을 형성하기 위하여 선택되는 하나 이상의 **부식 억제제를
  종종 포함**한다. 그러나 유기 필름이 세정 공정 후 구리 상호접속부 표면 상에 잔류한다면, 그러한 필름의
  존재는 이후의 단계(CVD 등) 및 최종 성능을 방해할 수 있다. … 예로서, **벤조트라이아졸(BTA)과 같은
  통상의 부식 억제제는 구리 표면 상에 소수성 층을 전형적으로 남길 것이고, 이는 결국 바람직하지 않은 많은
  유기 잔류물의 형성에 기여**한다." 즉 **부식을 막으려고 넣은 바로 그 화학물질(BTA류 억제제)이 유기
  잔류의 정의적(defining) 발생원**이다 — 이것은 "슬러리가 오염원"([[post-cmp-metallic-contamination-sources]]
  §2)이라는 서술과 대구를 이루되, 이 노트가 강조하는 것은 **세정 공정에 투입하는 물질 자체가 다시 오염이
  되는 순환**이다.
- 같은 명세서는 대안(2-아미노에탄올 같은 통상 아민)도 유기 잔류는 줄이지만 **구리 표면을 에칭해 부식
  결함을 만든다**고 지적한다 — "유기 잔류 제거"와 "부식 방지"가 세정 공정 설계에서 서로 당기는 두 축임을
  특허 배경 자체가 인정한다(정성, 정량 수치는 실시예 섹션 미검토).
- §2의 Wortman-Otto 2022도 같은 그림의 다른 절반이다: 브러시 매트릭스에 흡수된 "organic residue"가 접촉
  세정 중 재부착된다는 서술은, 유기 잔류가 슬러리에서만 오는 게 아니라 **세정 공정 중 브러시에 축적된
  이전 웨이퍼의 유기물이 재분배**될 수 있음을 뜻한다.

## 4. 금속 이온 오염 — 브러시가 저장소가 되고, pH가 "씻겨나가는가"를 가른다
**Bisht, S., Peter, J., Sahir, S., Hamada, S., Kim, Y.J., Kim, T.-G., Park, J.-G. (2022). "Effect of
colloidal silica and copper ions on PVA brush contamination during post-Cu CMP cleaning." *ICPT
(International Conference on Planarization/CMP Technology) 2022 proceedings* (학회 발표자료, 1차 실측 데이터
포함). 전문 확보: `papers/bisht2022-icpt-pva-brush-cu-ions.pdf`.**

- 딥핑 실험(브러시 결절 3 mm 조각을 Cu 표준용액 10–100 ppm + 콜로이드 실리카 0.1 wt%에 pH 3/7/11로 침지)
  결과: **pH 3**에서는 Cu가 이온 상태로 남아 브러시에 약하게만 붙고, **DIW로 헹구면 Cu 농도가 크게
  줄었다**(ICP-AES). 반면 **pH 7·11**에서는 Cu가 Cu(OH)₂(중성 부근)→CuO(알칼리)로 바뀌어 브러시 결절
  **내부에 흡수된 채 헹궈도 크게 줄지 않았다** — 저자는 이를 브러시 폴리비닐아세탈(PVA) 매트릭스 안에서의
  **Cu(II)–PVA 착물 형성**으로 설명한다. 즉 **pH가 낮으면 "씻어낼 수 있는" 오염, pH가 중성 이상이면 브러시에
  고정되는 오염**이라는 것이 이 노트의 핵심 관찰이다 — DI 헹굼만으로는 브러시 세정이 안 되는 이유의 1차
  실측 근거다.
- Cu 이온 농도 10→100 ppm 증가에 따라 브러시 적재(loading)가 단조 증가했고, **콜로이드 실리카 단독으로는
  pH 7·11에서 오염이 거의 없었으나 Cu 이온이 함께 있으면 뚜렷한 적재가 나타났다** — 저자는 이를 Cu²⁺가
  실리카 표면과 금속가교(metal-bridging, inner-sphere) 결합을 만들어 Cu(II)-실리카 복합체가 브러시와 더
  강하게 상호작용하기 때문으로 해석한다(정성 기구, 결합상수 등 정량화는 없음).
- §6에서 이 "pH 6 부근에서 씻기는 오염→고정되는 오염으로 전환"이라는 저자 서술을, 이 저장소의
  [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]에서 **CRC 표준전위로부터 이미 도출된
  Cu(OH)₂ 용해도곱(logKsp=-19.06)**을 이용해 **독립적으로(별개 문헌·별개 방법)** 재현한다.

## 5. 접촉식 대 비접촉식 세정의 오염 트레이드오프 — 요약
| 세정 방식 | 오염 생성 경로 | 장점 | 한계 |
|---|---|---|---|
| 접촉식(PVA 브러시 스크럽) | 브러시 매트릭스가 입자·유기물·금속이온을 흡수했다가 재부착(§2,§3,§4) | 기계적 제거력 강함 | 브러시 자체가 오염 저장소·교차오염 매개체 |
| 비접촉식(메가소닉) | 유체역학 조건(정적 탱크·장시간·과출력)에 따라 재부착 가능(§2, Wortman-Otto 2022) | 웨이퍼-브러시 물리접촉 없음 → 저장소 경로 원천 차단 | 캐비테이션 세기·펄스 조건에 성능이 민감, 저출력에서는 입자 제거 자체가 느림 |
이 표는 §2·§4에서 인용한 두 1차 문헌의 서술을 정리한 것이며, 두 방식을 정량적으로 직접 비교한 단일
데이터셋은 이번 6건 범위에서 확보하지 못했다(⚠ 미검증).

## 6. python 재현 — Cu(OH)₂ 침전 pH 문턱값을 Pourbaix 열역학으로 독립 재현
```python verify
import math

# --- CRC Vanysek 표준전위에서 이미 도출된 Cu(OH)2 용해도곱 (다른 노트에서 검증된 값을 재사용) ---
# [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] 참조: logKsp = -2*(E0_Cu2_Cu - E0_CuOH2_alk)/k = -19.06
k = 0.05916          # RT/F * ln(10) @298.15K
pKw = 14.00
logKsp = -19.06      # Cu(OH)2 + 2e = Cu + 2OH- 반쪽반응(알칼리형)에서 유도, 그 노트에서 이미 검증됨

def pH_onset(total_Cu_M):
    """총 Cu 농도(mol/L)를 모두 Cu2+로 가정했을 때 Cu(OH)2가 석출을 시작하는 pH.
    Q = [Cu2+][OH-]^2 = Ksp 인 지점: pH = (logKsp + 2*pKw - log10([Cu2+]))/2"""
    return (logKsp + 2*pKw - math.log10(total_Cu_M)) / 2

# --- Bisht et al. 2022 (ICPT) 조건: 100 ppm Cu 표준용액, "전이 pH 6 부근"(ref [14] Gao & Liu 2015 인용) ---
M_CU = 63.546          # g/mol
c_100ppm = 100e-3 / M_CU     # 100 mg/L -> mol/L
pH_100 = pH_onset(c_100ppm)
print(f"100 ppm Cu2+ ({c_100ppm:.3e} M) 침전 개시 pH(Pourbaix 독립 재현) = {pH_100:.2f} "
      f"(Bisht 2022가 인용한 전이 pH ~6과 비교)")
assert abs(pH_100 - 6.0) < 0.5, "Pourbaix에서 재현한 침전 개시 pH가 문헌 서술(~6)과 0.5 pH 이상 벗어남"

# --- pH 3/7/11에서 실제로 과포화(침전) 상태인지 판정 -> §4의 "pH3=씻김, pH7/11=고정" 관찰과 대조 ---
for pH in (3.0, 7.0, 11.0):
    oh = 10 ** (pH - 14.0)
    Q = c_100ppm * oh**2
    state = "과포화(석출, 브러시에 고정)" if Q > 10**logKsp else "미포화(이온상태, DI 헹굼으로 제거 가능)"
    print(f"  pH {pH:4.1f}: Q={Q:.2e} vs Ksp={10**logKsp:.2e} -> {state}")
    if pH == 3.0:
        assert Q < 10**logKsp, "pH3은 Bisht 관찰대로 미포화(이온 상태)여야 함"
    else:
        assert Q > 10**logKsp, "pH7/11은 Bisht 관찰대로 과포화(고정 오염)여야 함"

# --- 농도 의존성: Cu 농도가 높을수록 침전 개시 pH가 낮아져야(더 쉽게 고정) -> §4 "농도 증가=적재 증가"와 정합 ---
concs_ppm = (10, 50, 100)
onsets = [pH_onset(c/M_CU*1e-3) for c in concs_ppm]
print(f"  농도별 침전개시 pH: {dict(zip(concs_ppm, [round(x,2) for x in onsets]))}")
assert onsets[0] > onsets[1] > onsets[2], "Cu 농도 10->50->100 ppm 증가 시 침전개시 pH는 단조 감소해야 함"
print("PASS: 서로 다른 1차 문헌(Pourbaix 열역학 vs 브러시 딥핑 실측)이 pH~6 문턱값과 농도의존 방향에서 정합")
```
- 재현 결과: 100 ppm Cu²⁺ 기준 Pourbaix 유도 침전개시 pH ≈ 5.87 — 문헌이 인용한 "전이 pH 6"(Bisht et al., 2022)과
  0.13 pH 단위(**상대차 2.2%**) 차이로 **독립 재현 일치**(서로 다른 방법·다른 논문). pH 3은 미포화(이온 상태 유지 → DI
  헹굼으로 제거됨), pH 7·11은 과포화(Cu(OH)₂/CuO 고체화 → 브러시에 고정)로 계산돼, §4의 ICP-AES 관찰
  패턴과 부호가 일치한다. 농도 10→100 ppm 증가에 따라 침전개시 pH가 단조 감소해, "Cu 농도가 높을수록 브러시
  적재가 심해진다"는 정성 관찰과도 정합한다.
- 단, 이 계산은 **Cu(II)–PVA 착물 형성(Bisht 2022가 실제 고정 기구로 지목)이나 실리카와의 금속가교 결합을
  전혀 포함하지 않은 단순 Cu(OH)₂ 침전 모델**이다. pH 문턱값이 정성적으로 맞아떨어진 것이 착물 형성 기구를
  대체 설명한다는 뜻은 아니다 — "왜 그 근방 pH에서 전환이 일어나는가"에 대한 열역학적 하한선 재현일 뿐이다.

## 7. 한계 (정직 표기)
- §2 Hsu et al. 2015(고리형 결함)는 초록만 확인했고 본문 기구·수치는 **미확보**.
- §3 KR102113995B1의 실시예(정량 유기잔류 감소율, 부식전류 등)는 이번 조사에서 명세서 배경 설명까지만
  확인했고, 실시예 표의 수치는 **미검토**(범위 밖).
- §4 Bisht 2022는 학회 발표자료(scope 가중치 0.5)로, 동료심사 저널 논문이 아니다 — pH별 정량 Cu 흡착량
  (µg/cm² 등)은 도표(Fig. 4b)로만 제시돼 있어 **본문 수치 인용은 하지 못했다**(그림 판독 시도 안 함).
- §6의 Pourbaix 재현은 Cu(II)–PVA 착물화·실리카 금속가교를 무시한 **순수 무기 침전 모델**이며, 실제 브러시
  재질(PVA 하이드로겔)의 표면화학은 별도 문헌이 필요하다(**미검증**).
- §5 표는 두 문헌의 서술을 정리한 것이며, 접촉식 대 비접촉식을 **동일 조건에서 직접 비교한 정량 데이터셋**은
  확보하지 못했다.
- 회사 데이터·특정 장비 벤더의 실제 세정 레시피는 이 노트에서 다루지 않았다(문헌 정의만).

## 8. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv1-1 문항 참조.
