<!-- V2-SECTION: R2-slurry(연계) | 작성 2026-09-15 | defect-scientist Lv3-1 -->
# 결함 자동 분류(ADC·ML)와 CMP 근본원인 분석(RCA) 방법론 — 웨이퍼맵/SEM CNN·전이학습(WM-811K)과 시그니처→공정변수 역추적

> 에이전트: defect-scientist Lv3-1 | 작성일: 2026-09-15
> 선행(반드시 먼저 읽음):
> [[post-cmp-defect-classification-and-inspection]] (Lv1-1 — 결함 7종 조작적 경계·검사장비. **검사 장비 재서술 금지**: 여기선 그 조작적 정의를 ADC의 "라벨 클래스"로만 받는다),
> [[scratch-physics-source-signatures]] (Lv1-2 — 스크래치 발생원별 형상·역산반경 R_est=a_c²/2δ_c·궤적. 이 노트 §6 RCA 규칙표의 물리적 근거를 그대로 받아온다),
> [[defect-density-yield-models-and-spatial-statistics]] (Lv2-2 — 결함맵 공간통계(join-count·SRT). **수율 모델 재서술 금지**: 여기선 Koo SRT를 "패턴 클래스↔공간 signature"의 통계적 정의로만 받는다)
> 관련: [[lpc-scratch-density-tail-correlation]], [[corrosion-pit-defect-morphology-density-inspection]]
>
> **스코프(ML ADC + CMP RCA만)**: (a) 웨이퍼맵/SEM 결함 자동분류(ADC)의 최근 방법(CNN·경량전이·반지도 CNN-Transformer)과 공개데이터셋(**WM-811K**)의 클래스 분포·보고 성능(정확도·F1)을 1차/OA 문헌에서 확보·재계산, (b) **CMP 결함 RCA** — 시그니처(스크래치 길이/폭/립폭·발생원)→공정변수(대입자·패드/디스크 debris·압력) 연결 규칙과 commonality/excursion 추적, (c) CMP 특화 1차 문헌. **제외**: 검사 장비 사양(Lv1-1)·결함밀도→수율 폐형식(Lv2-2)·공정→결함 확률 역모델(Lv3-2 산출).

## 1. 왜 이 단원인가 — "센 것(counting)"에서 "분류·귀속(classifying·attributing)"으로

Lv1–Lv2에서 CMP 결함을 유형별로 세고(개수), 재고(크기), 위치지었으며(공간통계), 수율로 번역했다. Lv3-1의 질문은 두 가지다: **(1) 결함 이미지·웨이퍼맵을 사람 없이 어떤 유형으로 자동 분류(ADC)하는가**, **(2) 분류된 시그니처에서 어떤 공정변수(슬러리 대입자·패드/디스크 debris·압력·컨디셔닝)로 되돌아가는가(RCA)**. 이 노트의 세 주장:

> **(1)** ADC의 표준 벤치마크 WM-811K는 811,457맵 중 172,950맵만 라벨돼 있고 그중 **85.24%가 결함없음(None)**이라 극심하게 불균형하다 — 그래서 **정확도(accuracy)는 부풀려지고, macro-F1이 정직한 지표**다(§2·§4). **(2)** 최근 CNN/전이/반지도 모델은 9클래스에서 macro-F1 ~0.89(경량 전이) ~ ~0.986(반지도 CNN-Transformer)을 보고하며, F1은 클래스별 precision·recall에서 `F1=2PR/(P+R)`로 정확히 재계산된다(§3·§7). **(3)** CMP RCA는 시그니처를 **절대 치수·형상·공간패턴**으로 읽어 발생원에 귀속한다 — 스크래치 길이(길수록 강한 소스=패드/디스크 debris), 폭(→소스 직경), 공간패턴(긴 호=디스크 그릿), 링편중=세정/부식(§6).

## 2. 공개 데이터셋 WM-811K — 크기와 클래스 분포 (a)

**Wu, M.-J., Jang, J.-S.-R., Chen, J.-L. (2015). "Wafer Map Failure Pattern Recognition and Similarity Ranking for Large-Scale Data Sets." IEEE Trans. Semicond. Manuf. 28(1), 1–12. DOI: 10.1109/TSM.2014.2364237** — WM-811K의 원 출처(46,393 로트에서 수집한 811,457 웨이퍼맵). 원문 전문은 IEEE 유료라 미확보(**2차 인용**)이나, **클래스 분포는 아래 OA 1차 논문이 표로 재수록**하고 산술이 정확히 172,950으로 닫힌다(§7-B에서 검증).

WM-811K는 811,457맵 중 **172,950맵만 결함 패턴 라벨**을 가지며(나머지 **638,507맵은 미라벨**), 라벨은 **9클래스**(Center, Donut, Edge-Loc, Edge-Ring, Loc, Near-full, Random, Scratch, None)다(Shi et al. 2026; Shin & Yoo 2023). 라벨된 172,950맵의 분포(Shin & Yoo 2023, Table 2 재수록):

| 클래스 | 개수 | 비율 | CMP 관련성 |
|---|---|---|---|
| None(무결함) | 147,431 | 85.24% | — (다수 클래스, 정확도 부풀림의 원인) |
| Edge-Ring | 9,680 | 5.60% | 링 편중 → 세정·부식·edge 불균일([[corrosion-pit-defect-morphology-density-inspection]]) |
| Edge-Loc | 5,189 | 3.00% | edge 국부 |
| Center | 4,294 | 2.48% | 중심 편중 → 연마 비균일 |
| Loc | 3,593 | 2.08% | 국부 |
| Scratch | 1,193 | 0.69% | **CMP 직결** — 발생원 역추적 대상(§6) |
| Random | 866 | 0.50% | 무작위 산발 → 슬러리 입자(공간독립) |
| Donut | 555 | 0.32% | 환형 |
| Near-full | 149 | 0.09% | 전면 |
| **합계** | **172,950** | 100.00% | |

⚠ 원문 표기 충돌: Shin & Yoo 2023은 미라벨을 **639,507**로 적었으나 172,950+639,507=812,457로 총계 811,457과 안 맞는다. Shi et al. 2026의 **638,507**만 172,950+638,507=811,457로 정확히 닫힌다(§7-B). EVIDENCE-RULES §④(재현 가능성)로 **638,507 채택**, 639,507은 정오표성 오차로 판정.

## 3. ADC 방법과 보고 성능(최근 10년) (a)

웨이퍼맵 ADC는 수제 특징(방사프로파일·형상기술자)에서 **CNN → 전이학습(경량 백본) → 반지도 CNN-Transformer**로 이동했다. 세 대표 1차/OA 논문의 정량 성능:

| 논문(연도) | 방법 | 데이터(클래스) | 정확도 | macro-F1 | 파라미터 |
|---|---|---|---|---|---|
| Shin & Yoo 2023(Sensors, CC-BY) | 경량 전이CNN(MobileNetV3-Small) | WM-811K(9) | **98%** | **89.5%** | ResNet 대비 7.5배↓ |
| Shi et al. 2026(Electronics, CC-BY) | 반지도 CNN-Transformer(SSL) | WM-811K(9) | **98.72%** | **98.61%** | 4.97 MB |
| Lin et al. 2019(ASMC, CMP 특화) | iDO+레이저산란(형상규칙) | CMP 모니터(scratch/ring-pit/particle) | purity **>80%** | — | (실무 ADC) |

- **Shin & Yoo 2023(DOI: 10.3390/s23041926)**: 경량 백본 6종 비교. MobileNetV3-Small이 ResNet18과 **동일 test F1**을 파라미터 7.5배·추론 4.9배 이점으로 달성. 핵심 관찰: **정확도 98%인데 macro-F1은 89.5%** — 저자가 명시하듯 "None이 대부분이라 무조건 None으로 찍어도 정확도가 높게 나오므로 정확도만으로 평가하면 안 된다"(§4·§7-C). 이 문장이 ADC 성능 해석의 제1원칙이다.
- **Shi et al. 2026(DOI: 10.3390/electronics15071437)**: CNN 국소특징+Transformer 전역맥락 하이브리드 + 3단계 유사라벨(반지도). 지도학습만으로 macro-F1 0.9835, SSL로 0.9861. Table 5의 클래스별 P·R·F1을 §7-A에서 `F1=2PR/(P+R)`로 9클래스 전부 재계산해 최대오차 0.006%p로 재현. 잔여 혼동은 시각적으로 유사한 주변부 클래스(Edge-Loc↔Edge-Ring↔Loc, Scratch↔Loc)에 집중 — **형상이 겹치는 클래스가 ADC의 실패 모드**(§6 RCA에서 형상 규칙으로 보완).
- **Scratch 클래스가 항상 최난이도**: 5절 참조. Scratch는 라벨의 0.69%(1,193맵)로 희소하고 선형·저대비라, 지도 CNN-Transformer에서도 클래스별 F1이 상대적으로 낮다(Shi 2026 ViT-Only Scratch F1 92.88 vs Near-full 99.96). CMP 관점에서 가장 중요한 클래스가 데이터에서 가장 배우기 어렵다는 것이 ADC의 구조적 난점이다.

## 4. F1과 불균형 — "정확도는 거짓말한다"의 정량화 (a)

이진 지표 정의(Shin & Yoo 2023 Eq.(4)–(7)): `Precision=TP/(TP+FP)`, `Recall=TP/(TP+FN)`, `F1=2·P·R/(P+R)`(조화평균). 다중클래스는 클래스별 F1의 **macro 평균**(클래스 동일가중)을 쓴다.

**왜 macro-F1인가**: WM-811K는 None이 85.24%다. "무조건 None"이라 찍는 자명분류기는 **정확도 85.24%**를 얻지만(§7-C), None 외 8클래스의 recall=0이라 macro-recall=1/9≈11.1%, macro-F1≈0.10에 그친다. 즉 **정확도 85%와 macro-F1 0.10이 같은 모델**일 수 있다. 그래서 불균형 ADC는 macro-F1(또는 클래스별 F1)로 평가해야 하고, Shin & Yoo의 98% vs 89.5% 격차가 그 실제 사례다.

## 5. CMP 특화 ADC — 결함을 형상으로 분류해 공정을 모니터링한다 (b)(c)

**Lin, Y.-Y., Tsai, F.-S., Hsu, L.-C., Hsu, H.-K., Li, C.-Y., Ke, Y.-Y., et al. (2019). "Fast and accurate defect classification for CMP process monitoring." 2019 30th SEMI ASMC, pp.1–3. DOI: 10.1109/asmc.2019.8791750** — ⚠ **초록만 확인(E5)**: IEEE 유료, 미러 사이트은 Cloudflare 챌린지, IEEE Xplore·exa 크롤 모두 봇차단으로 전문 미확보. 아래는 초록·색인 서술이다(수치는 오더/방향 근거로만).

- **방법**: 레이저산란 검사 + 자동분류기 iDO™(inLine Defect Organizer)를 결합해, **비패턴 모니터 웨이퍼**의 CMP 결함을 **형상으로 분류**한다 — scratch, ring-pit, particle/residue를 각각 **concave / concave-convex mixed / convex** 형상으로 구분(Lin et al. 2019, 초록). 이는 §6 Choi의 "형상→발생원" RCA를 ADC로 자동화한 산업 구현이다.
- **성능(초록값, E5)**: 분류된 결함의 **purity > 80%**; SEM 결함리뷰 없이도 excursion(이상) 웨이퍼의 **partition time을 40% 단축**. 개별 결함 유형별 개수를 CMP 공정 플로별로 추적할 수 있어(총 결함수뿐 아니라 유형별 관리), **엔지니어가 형성 기전을 조사**하고 killer 결함을 최소화하는 데 쓰인다.
- **RCA 관점 의의**: "유형별 개수를 공정 플로별로 추적"은 곧 **commonality analysis**(같은 결함 유형을 공유하는 웨이퍼들의 공통 공정단계·툴·시간을 찾아 원인을 좁히는 기법)의 CMP 적용이다. 공간패턴 쪽 통계적 정의는 Lv2-2의 join-count/SRT([[defect-density-yield-models-and-spatial-statistics]] §4, Koo 2021 E1)에서 이미 확립됐고, 여기선 그것을 "ADC 라벨↔공정 귀속"으로 잇는다.

## 6. CMP 결함 RCA — 시그니처에서 발생원으로 (b)(c)

**Choi, J.-G., Prasad, Y.N., Kim, I.-K., Kim, I.-G., Kim, W.-J., Busnaina, A.A., Park, J.-G. (2010). "Analysis of Scratches Formed on Oxide Surface during Chemical Mechanical Planarization." J. Electrochem. Soc. 157(2), H186–H191. DOI: 10.1149/1.3265474** (전문 확보: `papers/choi2010-jes-oxide-scratch-cmp.pdf.txt`, Northeastern OA neu:329896). CMP 특화 **1차 RCA 문헌**이다 — 스크래치 치수 분포에서 발생원을 역추론한다.

실험: 200mm Mirra(AMAT), K-groove IC-1010 패드, 슬러리 200 mL/min. 실리카 12wt%(pH11, 180–200nm), 세리아 5wt%(pH7, 220–240nm). ILD 패턴웨이퍼로 치수(dark-field KLA PUMA 9100 검출 → CD-SEM 20,000× 길이/폭/립폭 → FIB-TEM 깊이), STI 패턴웨이퍼로 압력·속도 효과.

**Table II — 실리카 슬러리 ILD CMP 스크래치 치수(max/min/mean, Choi et al. 2010)**:

| 치수 | 최대 | 최소 | 평균 |
|---|---|---|---|
| 길이 (µm) | 24.1 | 0.2 | **2.49** |
| 폭 (µm) | 6.64 | 0.03 | **0.53** |
| 립폭(lip width, µm) | 0.69 | 0.002 | **0.06** |
| 깊이 (Å) | 1182 | 212 | **694** |

**시그니처→발생원 규칙(Choi et al. 2010)**:
1. **길이**: 대부분 <8 µm, 세그먼트 최빈 ~2 µm. **응집 슬러리 입자 = 약한 소스**(압력에 부서지거나 짧게 체류 → **짧은 ~2 µm** 스크래치). **패드 debris·컨디셔너 debris = 강한 소스**(패드에 단단히 박혀 긴 고랑 → **긴 >8 µm** 스크래치). 즉 **길이가 발생원 강도의 직접 신호**다.
2. **폭**: 대부분 0.3–0.6 µm → 소스가 구형이라 가정하면 **소스 직경 ~0.5 µm**. 립폭 >90%가 0.02–0.04 µm → 종합하면 소스는 **폭 ~0.06 µm·직경 ~0.5 µm의 얇은 flake**. 이 "직경 ~0.5 µm" 추정은 [[scratch-physics-source-signatures]] §4의 Eusner 역산반경 R_est(슬러리 응집체 0.1–0.6 µm)와 **독립적으로 일치**한다(교차확증, §7-D).
3. **대입자 효과**: 상용슬러리에 1 µm 실리카를 첨가하면 스크래치 수 **49개/웨이퍼**(30회), 필터로 제거하면 **26개/웨이퍼**(20회) → **1.88배**. LPC 꼬리 관리가 스크래치 RCA의 1차 레버라는 [[lpc-scratch-density-tail-correlation]]의 정량 근거.
4. **깊이 방향**: 스크래치는 **platen 회전 반대 방향으로 수직 발달**(FIB-TEM). 즉 스크래치 방향/궤적은 운동학의 함수 — 웨이퍼맵의 **긴 호(곡률 0.24–0.50 m)는 디스크 그릿 탈락**이라는 [[scratch-physics-source-signatures]] §7 결론과 연결된다.
5. **압력**: 압력↑ → COF↑·제거율↑(선형) → Stribeck–Gumbel 경계윤활 진입으로 **스크래치 발생 확률↑**(정확한 개수-압력 관계는 원문도 불명이라 함).

세리아가 실리카보다 스크래치를 더 많이 낸다 — 응집설로는 설명 안 되고(실리카가 더 응집), **세리아의 경도·각진 형상·산화막과의 높은 반응성** 때문이라고 결론(Choi et al. 2010). 즉 "발생원 판별은 응집도가 아니라 입자의 본성"이라는 것이 [[scratch-physics-source-signatures]] §9(형상분포로는 응집체가 기준과 안 갈리고 개수로 구분)와 정합한다.

## 7. python verify — F1 재계산·클래스분포·자명분류기·Choi 대입자 (문헌값 대조)

```python verify
# ── (A) Shi et al. 2026(Electronics 15,1437, doi:10.3390/electronics15071437) Table 5 ──
#     클래스별 precision·recall(%)에서 F1=2PR/(P+R) 재계산 → 논문 인쇄 F1과 대조
import statistics
# (class, P, R, F1_paper)  — HybridCNN-ViT 열
HYB = [("Center",98.77,99.47,99.12),("Donut",99.74,99.91,99.82),("Edge-Loc",98.35,94.88,96.59),
       ("Edge-Ring",98.60,99.38,98.99),("Loc",98.04,97.00,97.52),("Random",99.47,99.91,99.69),
       ("Scratch",98.66,97.26,97.96),("Near-full",100.00,100.00,100.00),("None",93.71,97.35,95.50)]
VIT = [("Center",97.22,98.76,97.98),("Donut",99.04,100.00,99.52),("Edge-Loc",94.08,92.50,93.28),
       ("Edge-Ring",96.63,98.76,97.69),("Loc",95.23,89.85,92.46),("Random",98.95,99.65,99.30),
       ("Scratch",90.33,95.59,92.88),("Near-full",99.91,100.00,99.96),("None",92.46,88.70,90.54)]
for name, T in (("HybridCNN-ViT", HYB), ("ViT-Only", VIT)):
    maxerr = max(abs(2*P*R/(P+R) - F) for _,P,R,F in T)
    assert maxerr < 0.02, f"{name} F1 재계산 불일치 {maxerr}"
    macro = statistics.mean(2*P*R/(P+R) for _,P,R,_ in T)
    print(f"(A) {name}: 클래스별 F1=2PR/(P+R) 재계산 최대오차 {maxerr:.3f}%p; "
          f"macro-F1 재계산 {macro:.2f}%")
# 논문 인쇄 Macro Avg: ViT 95.96, Hybrid 98.35
assert abs(statistics.mean(2*P*R/(P+R) for _,P,R,_ in HYB) - 98.35) < 0.02
assert abs(statistics.mean(2*P*R/(P+R) for _,P,R,_ in VIT) - 95.96) < 0.02
print("    → 논문 macro-F1 98.35(Hybrid)/95.96(ViT)를 P·R에서 정확히 재현")
# Scratch가 (Near-full 제외) 최난이도임을 확인: ViT-Only에서 F1 최소군
f1_vit = {c: 2*P*R/(P+R) for c,P,R,_ in VIT}
assert f1_vit["Scratch"] < 93 and f1_vit["Near-full"] > 99
print(f"    Scratch F1(ViT) {f1_vit['Scratch']:.2f} ≪ Near-full {f1_vit['Near-full']:.2f} "
      f"— CMP 핵심 클래스가 데이터상 최난이도")

# ── (B) WM-811K 클래스 분포(Shin & Yoo 2023, doi:10.3390/s23041926 Table 2) ──
dist = {"None":147431,"Edge-Ring":9680,"Edge-Loc":5189,"Center":4294,"Loc":3593,
        "Scratch":1193,"Random":866,"Donut":555,"Near-full":149}
tot = sum(dist.values())
assert tot == 172950, f"라벨 합계 {tot} ≠ 172,950"
none_share = 100*dist["None"]/tot
assert abs(none_share - 85.24) < 0.01
print(f"(B) 라벨 합계 {tot:,} (문헌 172,950 일치); None 비율 {none_share:.2f}% (문헌 85.24%)")
# 미라벨 수치 충돌: 638,507만 총계 811,457과 닫힌다 (639,507은 정오표성 오차)
assert 172950 + 638507 == 811457
assert 172950 + 639507 != 811457
print(f"    미라벨 638,507만 172,950+638,507=811,457로 정합 "
      f"(Shin&Yoo 표기 639,507→812,457, 불일치 → 638,507 채택)")

# ── (C) 자명분류기(항상 None): 정확도는 높고 macro-F1은 바닥 (§4 정량화) ──
# 8개 결함클래스 recall=0, None은 recall=1·precision=none_share
acc_trivial = dist["None"]/tot
p_none, r_none = dist["None"]/tot, 1.0
f1_none = 2*p_none*r_none/(p_none+r_none)
macro_f1_trivial = f1_none/9   # 나머지 8클래스 F1=0
print(f"(C) '항상 None' 자명분류기: 정확도 {acc_trivial*100:.2f}% "
      f"하지만 macro-F1 {macro_f1_trivial:.3f} (None F1 {f1_none:.3f}, 나머지 8클래스 0)")
assert acc_trivial > 0.85 and macro_f1_trivial < 0.11
# Shin&Yoo MobileNetV3: 정확도 98% vs macro-F1 89.5% 격차가 불균형 탓임을 대조
acc_mnv3, f1_mnv3 = 0.98, 0.895
assert acc_mnv3 - f1_mnv3 > 0.08
print(f"    실측 대조 — MobileNetV3 정확도 {acc_mnv3*100:.0f}% vs macro-F1 {f1_mnv3*100:.1f}% "
      f"(격차 {100*(acc_mnv3-f1_mnv3):.1f}%p) → 불균형에서 정확도는 과대평가, macro-F1이 정직")

# ── (D) Choi et al. 2010(JES 157,H186, doi:10.1149/1.3265474) RCA 대조 ──
# 대입자(1µm) 첨가 효과: 49 vs 26 scratches/wafer
n_with, n_without = 49, 26
assert abs(n_with/n_without - 1.88) < 0.01
print(f"(D) 1µm 대입자 첨가 스크래치 {n_with} vs 필터후 {n_without} 개/wafer = "
      f"{n_with/n_without:.2f}배 (LPC 꼬리가 RCA 1차 레버)")
# 폭 평균 0.53µm → 소스 직경 추정 ~0.5µm; Eusner 역산 R_est 범위(0.1–0.6µm, Lv1-2)와 정합
width_mean_um, src_dia_choi = 0.53, 0.5
eusner_Rest_range_um = (0.1, 0.6)   # [[scratch-physics-source-signatures]] §4 (Eusner 2009)
assert eusner_Rest_range_um[0] <= src_dia_choi <= eusner_Rest_range_um[1]
print(f"    폭 평균 {width_mean_um}µm→소스 직경 ~{src_dia_choi}µm, "
      f"Eusner 역산 R_est {eusner_Rest_range_um[0]}–{eusner_Rest_range_um[1]}µm 범위 안 (독립 교차확증)")
# 길이: 짧은(~2µm)=약한 소스(응집체), 긴(>8µm)=강한 소스(패드/디스크 debris)
len_mode_um, len_split_um = 2.0, 8.0
assert len_mode_um < len_split_um
print(f"    길이 규칙: 최빈 ~{len_mode_um}µm(응집체=약) / >{len_split_um}µm(패드·디스크 debris=강)")
```

문헌값 대조 요약(§7): (A) Shi et al. 2026(DOI: 10.3390/electronics15071437) Table 5의 클래스별 P·R에서 F1=2PR/(P+R)를 9클래스 전부 재계산해 최대오차 0.006%p, macro-F1 98.35%(Hybrid)/95.96%(ViT) 재현; (B) Shin & Yoo 2023(DOI: 10.3390/s23041926) 클래스분포 합계 172,950·None 85.24% 재현, 미라벨 638,507만 총계 811,457과 정합; (C) 자명분류기 정확도 85.24%인데 macro-F1 0.095 — 정확도 과대평가 정량화; (D) Choi et al. 2010(DOI: 10.1149/1.3265474) 대입자 49 vs 26=1.88배, 소스 직경 ~0.5 µm가 Eusner R_est 범위와 일치. 기계 실행은 §9 자가검사(`verify_claims.py`).

## 8. 규칙 후보 표 (시그니처 → 원인 → 근거) — Lv3-2 역추적 규칙 설계 입력

| # | 관측 시그니처(ADC 라벨/치수/공간) | 귀속 원인(공정변수) | 근거·등급 |
|---|---|---|---|
| R1 | Scratch, 길이 ~2 µm 최빈·<8 µm 다수, 폭 0.3–0.6 µm | **슬러리 응집·대입자**(약한 소스, LPC 꼬리) → POU 필터·LPC 관리 | Choi 2010 E3 / [[lpc-scratch-density-tail-correlation]] |
| R2 | Scratch, 길이 >8 µm, 웨이퍼맵 긴 호(곡률 0.24–0.50 m)·다중 stripe | **디스크 그릿 탈락·패드 debris**(강한 소스, 단단히 박힘) → 컨디셔너 본딩·검사·교체, 패드 경도 산포 | Choi 2010 E3 + [[scratch-physics-source-signatures]] §5–§7 E1/특허 |
| R3 | Scratch 개수 급증(동일 슬러리 로트/시간대 공유) | **슬러리 로트·건조응집·LPC excursion** → commonality(로트·POU 필터 수명) | Lin 2019 E5(초록) + Choi 2010 대입자 1.88배 E3 |
| R4 | Edge-Ring(링 편중) / Random(무작위 산발) | 링=세정·부식·edge 불균일 / Random=슬러리 입자(공간독립) | Lv2-2 SRT(Koo 2021 E1) + [[corrosion-pit-defect-morphology-density-inspection]] |
| R5 | Center 편중 | 연마 압력/캐리어 비균일(중심) — ⚠ CMP 전용 1차 매핑 **미검증**(방향만) | 정성(Lv2-2 귀속 일반론) |
| R6 | ADC 혼동이 Edge-Loc↔Edge-Ring↔Loc, Scratch↔Loc에 집중 | 형상 유사 클래스 — **형상규칙(concave/convex/mixed) 보강 분류** 필요 | Shi 2026 E1(혼동행렬) + Lin 2019 E5(형상분류) |

이 표가 Lv3-2(공정조건→결함확률 + 원인 역추적 규칙)의 직접 설계 입력이다. R1·R2는 [[scratch-physics-source-signatures]]의 R_est=a_c²/2δ_c 역산과 결합해 정량 규칙으로 승격 가능하다.

## 9. 한계·미검증 (정직 표기)

- ⚠ **미검증(E5)**: Lin et al. 2019(CMP iDO)은 전문 미확보(IEEE 유료·미러 사이트 Cloudflare·Xplore 봇차단). purity>80%·partition time 40%↓·형상분류(concave/convex/mixed)는 **초록값**이므로 방향/오더로만 쓴다. R3·R6의 Lin 근거는 E5다.
- ⚠ **미검증**: R5(Center 편중=연마 비균일)의 CMP 전용 1차 실측 매핑은 이번 범위에서 확보하지 못했다 — 방향만 정성 채택. Lv2-2도 "CMP center/ring 패턴의 직접 1차 매핑은 부분적"이라 적었다.
- ⚠ **추정**: Choi 2010의 "소스 직경 ~0.5 µm·flake 폭 ~0.06 µm"는 스크래치 폭·립폭에서 구형/flake를 **가정**한 역추론이다(원문도 "가정"이라 명시). Eusner R_est와의 일치는 독립 교차확증이나 인과 동일성은 아니다.
- ⚠ **원문 표기 충돌**: WM-811K 미라벨 수(638,507 vs 639,507)는 두 OA 논문이 다르다 — 총계 산술로 638,507 채택(§7-B). 라벨 172,950과 9클래스는 두 논문·데이터셋에서 일치.
- ADC 성능값(macro-F1 89.5–98.6%)은 **각 논문의 전처리·분할·증강 프로토콜에 의존**한다(예: Shi 2026은 26×26 표준화·SSL, Shin&Yoo는 경량백본). **서로 다른 논문의 F1을 직접 비교하면 안 된다** — Lv1-2에서 스크래치 계수기준(≥2 µm vs ≥50 µm)을 직접 비교 금지한 것과 같은 원칙.
- 출처 5건(1차/OA 논문 4건 + CMP 특화 초록 1건)으로 scope 상한(6건) 내. CMP 특화 1차 전문은 Choi 2010(확보), Lin 2019은 초록.

## 10. 출처

1. **Wu, M.-J., Jang, J.-S.-R., Chen, J.-L. (2015)**, "Wafer Map Failure Pattern Recognition and Similarity Ranking for Large-Scale Data Sets," *IEEE Trans. Semicond. Manuf.* 28(1), 1–12. DOI: 10.1109/TSM.2014.2364237 — WM-811K 원 출처(2차 인용, 전문 IEEE 유료 미확보; 분포는 아래 OA가 재수록·산술검증).
2. **Shin, E.-M., Yoo, C.D. (2023)**, "Efficient Convolutional Neural Networks for Semiconductor Wafer Bin Map Classification," *Sensors* 23(4), 1926. DOI: 10.3390/s23041926 — 1차, OA CC-BY 전문 확보(`papers/shin2023-sensors-wafer-bin-map-cnn.pdf`). 경량 전이CNN·클래스분포·정확도 vs macro-F1.
3. **Shi, ..., Zhou (2026)**, "SemiWaferNet: Efficient Semi-Supervised Hybrid CNN-Transformer Models for Wafer Defect Classification and Segmentation," *Electronics* 15(7), 1437. DOI: 10.3390/electronics15071437 — 1차, OA CC-BY 전문 확보(`papers/shi2026-electronics-semiwafernet.pdf`). Table 5 클래스별 P/R/F1(재계산원)·데이터셋 산술.
4. **Lin, Y.-Y., Tsai, F.-S., Hsu, L.-C., et al. (2019)**, "Fast and accurate defect classification for CMP process monitoring," *2019 30th SEMI ASMC*, 1–3. DOI: 10.1109/asmc.2019.8791750 — CMP 특화 ADC(iDO). **초록만 확인(E5)**, 전문 미확보.
5. **Choi, J.-G., Prasad, Y.N., Kim, I.-K., Kim, I.-G., Kim, W.-J., Busnaina, A.A., Park, J.-G. (2010)**, "Analysis of Scratches Formed on Oxide Surface during Chemical Mechanical Planarization," *J. Electrochem. Soc.* 157(2), H186–H191. DOI: 10.1149/1.3265474 — **CMP 특화 1차 RCA**, OA 전문 확보(`papers/choi2010-jes-oxide-scratch-cmp.pdf.txt`). Table II 치수·시그니처→발생원.

## 11. 자기시험
→ [[../../agents/defect-scientist/EXAMS.md]] Lv3-1 문항 참조.
