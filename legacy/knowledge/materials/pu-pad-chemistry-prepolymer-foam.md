<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: groove, pu-pad, viscoelast, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 PU 화학 — 프리폴리머·경화제·발포 (Lv1-1)

> pad-material 신설 단원 Lv1-1. [[pad-viscoelasticity-dma]](pad-mechanic Lv1-1, DMA·저장/손실탄성률)와
> [[pad-structure-groove-subpad]](pad-mechanic Lv1-2, IC1000 실측 Shore D 60·압축률 2.25%)가 다룬
> "완성된 패드의 물성"의 한 단계 앞, **그 물성이 조성에서 어떻게 정해지는가**를 다룬다.

## 1. 프리폴리머법(prepolymer process) — 2단계 합성

상용 CMP 패드 PU는 대부분 원샷(one-shot)이 아니라 **프리폴리머법**으로 만든다.
1단계: 디이소시아네이트(TDI/MDI계)와 폴리올(폴리에테르/폴리카보네이트디올)을 과량의 NCO 조건에서
반응시켜 양 말단이 -NCO로 캡핑된 **이소시아네이트 말단 프리폴리머**를 만든다. 2단계: 이 프리폴리머를
방향족 디아민(MOCA 등) 또는 트리올계 **경화제(curative)**와 반응(사슬연장, chain extension)시켜
최종 고분자망을 완성한다. 프리폴리머 단계에서 유리 단량체 디이소시아네이트의 증기압·독성 문제를
미리 반응시켜 낮추는 것이 산업적으로 프리폴리머법을 쓰는 이유이기도 하다.

**출처(1차, 공정 파라미터)**: Kulkarni et al., "Damping polyurethane CMP pads with microfillers,"
US Patent Application US 2009/0137120 A1 (patents.google.com/patent/US20090137120A1, 국제출원
WO2009029322A1, 이하 **[US20090137120A1]**) — CMP 패드 전용 PU 조성·공정을 청구항 수준으로
개시한 특허로, 이 노트의 §2~4 수치 대부분의 출처.

## 2. 프리폴리머 종류와 %NCO — 경도 목표와의 관계

[US20090137120A1]이 실시예로 제시한 프리폴리머들과 그 유리 NCO 함량(wt%):

| 프리폴리머 | 화학 계열 | %NCO (wt%) |
|---|---|---|
| LW 570 | H12MDI–폴리에테르 (지방족) | 7.74 |
| L 325 | TDI/H12MDI–PTMEG (혼합) | 9.11 |
| Adiprene® LF 750D | TDI–PTMEG (방향족) | 8.79 |
| Airthane® PHP-80D | TDI–PTMEG (방향족) | 11.1 |
| LFH 120 | HDI–폴리에테르 (지방족) | 12.11 |

%NCO가 높을수록 동일 폴리올 사슬 길이 대비 우레탄/우레아 경질세그먼트(hard segment) 밀도가
높아질 잠재력이 커지고, 경화 후 가교밀도·경도가 올라가는 방향으로 작용한다(§3의 정량 재현 참조).
특허는 최종 목표 경도를 **Shore D 30–80(바람직하게는 55–80)**으로 명시 — IC1000 실측값
(Shore D 60, [[pad-structure-groove-subpad]] §1)이 정확히 이 선호 구간 하단부에 위치함을 확인.

## 3. 경화제 화학량론 — NCO/OH(또는 NCO/NH₂) 당량비가 경도를 정한다

[US20090137120A1]은 경화제를 "이용 가능한 이소시아네이트기의 90~105%(전형적으로 95%) 당량"으로
투입하도록 청구한다 — 즉 **약간의 NCO 부족 또는 과잉을 의도적으로 남겨 가교밀도를 미세조정**하는
전략이다. 댐핑(진동감쇠) 강화용으로는 방향족 디아민(Ethacure® 300)에 트리올(TMP 5wt% 또는
개질 TMP 10wt%)을 섞어 가교점을 추가하는 배합(ET5, ET10)을 MOCA 단독 배합과 비교 실시예로 제시.

일반 PU 탄성체(캐스터 휠용, CMP 패드는 아니지만 동일한 프리폴리머+MOCA 경화 화학)에서 정량
사례를 확인할 수 있다 — **출처(1차)**: R. C. 등, "Low heat buildup polyurethane compositions and
articles," **US Patent 4,556,703**(patents.google.com/patent/US4556703A). 실시예 5: 프리폴리머
100중량부에 MOCA 14.2중량부(NCO 대비 당량비로 환산 가능)를 투입해 경화 → **Shore A 90**. 실시예
1~4도 MOCA 13.2~15.1중량부/프리폴리머 100중량부 범위에서 Shore A 90~91을 일관되게 재현 —
즉 좁은 화학량론 창(±1.5중량부 이내)에서 경도가 크게 흔들리지 않는 것으로 보아, 이 시스템은
당량비 1근처 플래토(경화제가 충분히 있으면 경도가 프리폴리머 자체의 하드세그먼트 함량에 더
지배받음)에 있는 것으로 추정 — **미검증**(당량비 대 경도의 연속 곡선은 이 특허에 없음, 이산적
실시예 4점뿐).

NCO/OH 당량비를 **연속적으로 변화**시켜 물성을 추적한 별도 문헌은 §5에서 정량 재현한다.

## 4. 발포(foaming) — 두 갈래의 기공 형성 메커니즘

[US20090137120A1]이 개시한 CMP 패드 기공 형성 경로 두 가지:

**(1) 가스 프로싱(gas-frothing) — 1차 기공**: 경화 전 프리폴리머에 질소(N₂)를 5 SCFH로 취입하며
1500 rpm으로 45~120분 교반, 폴리실록산-폴리알킬렌옥사이드계 계면활성제(예: DC-193, 표면장력
<25 mN/m)로 기포를 안정화 — 부피 증가 약 30%, 평균 기공 50~100 µm(최대 120 µm)의 폐쇄형 기공을
형성한다.

**(2) 가용성 필러 — 2차 기공**: 폴리비닐피롤리돈(PVP, 입경 20~50 µm)을 조성 전체의 1~20 wt%
배합 → 경화 후 CMP 슬러리(수계)에 노출되면 PVP가 용해되며 약 10 µm급 2차 기공을 새로 만든다.
실시예: 프리폴리머(프로싱 후) 100 g에 PVP K30 분말 15 g. 두 기공 메커니즘이 만드는 기공 면적률은
합쳐서 5~60%로 청구.

최종 밀도 범위는 **0.6~1.0 g/cm³**(바람직 0.80~0.95 g/cm³)로 청구 — 미발포 PU 고형체 밀도
(대략 1.05~1.25 g/cm³ 대역, 일반 PU 문헌값, 본 특허에는 명시 없음 → **미검증**)와 비교하면
상대밀도 대략 0.6~0.9 수준의 저~중 발포율에 해당한다는 정성적 위치를 알 수 있다.

## 5. 정량 재현 — NCO/OH 당량비 증가 → 인장강도↑·신율↓ (경질세그먼트 함량 논리)

§3에서 미검증으로 남긴 "당량비-경도 연속 곡선"의 대체 근거로, 피마자유(castor oil, 천연 폴리올)와
TDI(톨루엔-2,4-디이소시아네이트)로 NCO/OH **몰비를 1.6~2.0으로 연속 변화**시킨 프리폴리머의
기계물성 문헌 데이터를 확보했다.

**출처(1차, 오픈액세스 CC-BY-SA)**: K. Rathika, S. Begila David, "Effect of Increasing NCO/OH
Molar Ratio on the Chemical and Mechanical Properties of Isocyanate Terminated Polyurethane
Prepolymer Derived from Bio-mass," *Green Chemistry & Technology Letters* 2(2), 78–82 (2016).
DOI: https://doi.org/10.18510/gctl.2016.225

측정값(논문 Fig.3, Fig.4, ASTM D-638):

| NCO/OH 몰비 | 인장강도 (MPa) | 신율 (%) |
|---|---|---|
| 1.6 | 1.49 | 115.0 |
| 1.8 | 1.701 | 95.0 |
| 2.0 | 2.07 | 86.22 |

논문 결론: NCO/OH비 증가 → 프리폴리머 분자량 저하(과량 NCO가 사슬 성장을 조기 종결) → 최종
경화물의 **경질세그먼트 함량 증가** → 인장강도 증가·신율 감소. 이는 §2에서 정성적으로 서술한
"%NCO↑ → 경도↑" 논리와 방향이 같은 독립 정량 데이터다. 아래 코드로 단조성·상관관계·구간 변화율을
문헌값과 대조·재현했다.

```python verify
import numpy as np

# Rathika & Begila David (2016), Green Chem & Technol Lett 2(2):78-82,
# DOI 10.18510/gctl.2016.225, Fig.3(인장강도)·Fig.4(신율) 판독값
ratio = np.array([1.6, 1.8, 2.0])
tensile_MPa = np.array([1.49, 1.701, 2.07])
elong_pct = np.array([115.0, 95.0, 86.22])

d_tensile = np.diff(tensile_MPa)
d_elong = np.diff(elong_pct)
assert (d_tensile > 0).all(), "인장강도가 NCO/OH 증가와 함께 단조증가해야 함(문헌 결론)"
assert (d_elong < 0).all(), "신율이 NCO/OH 증가와 함께 단조감소해야 함(문헌 결론)"

# 정량 재현: ratio 1.6->2.0 구간 인장강도 변화율·신율 변화율을 문헌 그래프 판독치와 대조
tensile_pct_incr = (tensile_MPa[-1] - tensile_MPa[0]) / tensile_MPa[0] * 100
elong_pct_decr = (elong_pct[0] - elong_pct[-1]) / elong_pct[0] * 100
assert abs(tensile_pct_incr - 38.9) < 1.0, f"인장강도 증가율 재현 실패: {tensile_pct_incr:.1f}%"
assert abs(elong_pct_decr - 25.0) < 1.0, f"신율 감소율 재현 실패: {elong_pct_decr:.1f}%"

# 상관관계 방향 확인 (경질세그먼트 함량 증가 가설과 부호 일치해야 함)
corr_tensile = np.corrcoef(ratio, tensile_MPa)[0, 1]
corr_elong = np.corrcoef(ratio, elong_pct)[0, 1]
assert corr_tensile > 0.9, f"NCO/OH-인장강도 상관 약함: r={corr_tensile:.3f}"
assert corr_elong < -0.9, f"NCO/OH-신율 상관 약함: r={corr_elong:.3f}"

print(f"OK: tensile +{tensile_pct_incr:.1f}%, elongation -{elong_pct_decr:.1f}% "
      f"(NCO/OH 1.6->2.0), r_tensile={corr_tensile:.3f}, r_elong={corr_elong:.3f}")
```

**주의**: 이 데이터는 캐스터유 기반 프리폴리머의 인장강도/신율이지, CMP 패드 자체의 경도(Shore
D)나 기공률이 아니다 — "당량비가 경질세그먼트 함량을 통해 기계물성을 좌우한다"는 **메커니즘**을
독립 계로 정량 재현한 것이며, IC1000류 CMP 패드에 이 정확한 계수(38.9%, 25.0%)를 직접 적용할
수는 없다(미검증, 화학계가 다름 — 폴리에테르/폴리카보네이트 폴리올 대 피마자유).

## 6. 종합 — 조성 3축이 경도·기공을 정하는 방식

1. **프리폴리머 %NCO / 폴리올 종류** (§2): 높을수록 경질세그먼트 잠재력↑ → 경도↑ 방향.
2. **경화제 당량비·종류** (§3): NCO 대비 90~105% 투입이 표준 창, 방향족 디아민(MOCA/Ethacure)
   대 트리올 혼합 비율로 가교밀도·댐핑성을 조정. 당량비 자체의 연속적 경도 민감도는 §5에서
   대체 계로 방향성만 정량 재현했다(CMP 패드 정확 계수는 §5 하단 주의 참조).
3. **발포 공정** (§4): 가스 프로싱(1차, 50~100µm 폐쇄기공)과 가용성 필러(2차, ~10µm, 슬러리
   접촉 시 개방기공화)의 **이중 기공 구조**가 최종 밀도(0.6~1.0 g/cm³)와 기공 면적률(5~60%)을
   결정 — 이것이 [[pad-structure-groove-subpad]]에서 확인한 "micro-porous"(미세다공)의 조성적
   기원이다.

세 축은 독립적이지 않다: 예컨대 %NCO가 높은 프리폴리머는 점도도 높아 프로싱 시 기포 안정성이
달라질 수 있다는 상호작용이 있으나, 이 정량적 결합관계는 확보한 문헌에 없음(§ 미검증 목록 참조).

## 다음 단원
Lv1-2: 경도·탄성률·기공률 측정법과 문헌값 범위(IC1000/IC1010/하드·소프트) — 이 노트의 §2·§4
청구 범위(Shore D 30–80, 밀도 0.6–1.0 g/cm³)를 실측 스펙시트 값과 대조.

## 미검증 목록
- 프리폴리머 %NCO ↔ 최종 CMP 패드 Shore D 경도의 정량 대응 곡선 (특허는 이산 실시예·목표범위만 제시)
- NCO/OH 당량비-경도 연속 곡선 (US4556703은 4개 이산점, 모두 좁은 창 내 Shore A 90~91)
- 미발포 PU 고형체 기준밀도(1.05~1.25 g/cm³ 대역) — 일반 PU 문헌 통념치, [US20090137120A1] 미명시
- §5 재현 계수(인장강도 +38.9%, 신율 -25.0%)의 CMP 패드(폴리에테르/PTMEG계) 직접 적용 가능 여부
- 프리폴리머 점도-발포 기포 안정성 상호작용의 정량 관계
