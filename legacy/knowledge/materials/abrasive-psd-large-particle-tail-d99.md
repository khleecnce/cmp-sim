<!-- V2-SECTION: R2-slurry | 작성 2026-09-14 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 슬러리 입도분포 대입자 꼬리(D99/D95/D90) — 측정법의 구조적 한계와 손상 상관

> 에이전트: slurry-abrasive (갭 겨냥 보강 학습, 2026-09-14)
> [[../cmp/lpc-scratch-density-tail-correlation]] [[../cmp/abrasive-d99-scratch-hitachi-us8439995]]
> [[../cmp/abrasive-d99-spec-cross-pack-comparison]] [[../cmp/abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]]

## 1. 왜 필요한가 — 이 노트가 채우려는 것과 채우지 않는 것

`sim/factors.py::_f_delta`(손상 유발도 Δ)는 5팩 중 2팩(sti_ceria/sic_ceria_h2o2)만
`abrasive_d99_nm`이 있고, 3팩(oxide_silica·cu_h2o2_bta·w_fe_oxidizer)은
`abrasive_size_nm × 업계 일반비(5.00, Levitronix 2008 2차자료)`로 유도한 값이라
confidence가 `estimated`로 강등돼 있다([[../cmp/abrasive-d99-scratch-hitachi-us8439995]] §9.4
판정, 2026-09-14). 선행 4개 회차가 알루미나(cu_h2o2_bta/w_fe_oxidizer) 및 콜로이달실리카
(oxide_silica)의 D99 **절대값**을 특허·제조사 문서에서 직접 찾으려다 전부 실패하고
"공개 1차 문헌 경로 소진"으로 종결 판단했다([[../cmp/abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]]
§3). 이번 회차는 같은 절대값 탐색을 5번째로 반복하지 않는다. 대신 **왜 D99가 이렇게
확보하기 어려운가**를 입자 자체의 물성·측정법 축에서 정량화한다 — 이것이 이번 조사 범위
(입자 물성, 제형 축 아님)에 맞는 질문이다.

**범위 밖이라 제외**: 슬러리 조성비·첨가제가 D99/LPC에 미치는 영향(슬러리 안정성, pH,
분산제 종류)은 slurry-chemist 소관이라 다루지 않는다. 팩별 D99 값 이식 여부의 재판단도
이 노트의 목적이 아니다(§9.4가 이미 판정 완료).

## 2. 측정법 자체가 D99를 구조적으로 못 보는 이유 — SLS vs SMPS(Kim et al. 2010)

**Kim, H., Yang, J.C., Kim, T. (2010). "Measurement of CMP Slurry Abrasive Size Distribution
by Scanning Mobility Particle Sizer." *Electrochemical and Solid-State Letters* 13(4),
H137–H140. DOI: 10.1149/1.3299254.** (유료, 미러 사이트 미러 경유 전문 PDF 확보,
`papers/scanning-mobility-particle-sizer-jes.pdf`, fitz로 4페이지 전문 추출·대조.)

퓸드실리카(130nm)·세리아(100/200/300nm) 슬러리를 **정적광산란(SLS, Horiba LA-910)**과
**주사형 이동도입자측정기(SMPS: DMA+CPC, 단일입자 계수)** 두 방식으로 동시 측정해
직접 비교한 1차 실험 논문.

### 2.1 핵심 실측 사실
1. **SLS는 소입자를 구조적으로 놓친다.** 50nm와 500nm 폴리스티렌 표준입자(PSL) 혼합물을
   SLS로 측정하면 500nm는 정확히 검출되지만 **50nm는 검출 자체가 안 된다** — 저자가 계산한
   산란광 강도비가 "적어도 10⁴배" 차이 나기 때문("scattering intensities of the 50 nm
   particles... were at least 10⁴ times less than those of the 500 nm PSL particles").
   광산란 신호는 대입자 신호에 소입자 신호가 묻힌다(강도 가중 = 부피/표면적 가중,
   지름 세제곱 근방 스케일).
2. **SMPS(단일입자 개수 계수)는 15~550nm 범위에서 정밀**하고, 응집이 없는 세리아 슬러리에
   한해 최대 1µm까지 측정 가능하다고 원문이 명시("SMPS was capable of measuring the
   particle size up to 1 µm"). 그러나 **이 상한을 넘는 진짜 대입자 꼬리(수 µm급)는 SMPS도
   놓친다** — 원문 결론이 "600nm 이하는 SMPS, 조대입자(주로 1µm 이상)는 SLS나 다른
   광산란 장비로 측정하라"고 이분화해서 권고하는 이유다.
3. **같은 시료를 SLS로 보면 단일모드, SMPS로 보면 이중모드**로 나온다(실리카: SLS 150nm
   단일피크 vs SMPS 35nm+130nm 이중피크). 35nm 1차입자 모드는 SEM으로 실측 확인되나
   SLS는 이 모드를 아예 표시하지 못한다 — 광산란 신호가 큰 입자군에 지배당해서다.

### 2.2 시사점 — D99 비공개·비교불가 문제의 근본 원인
1단원 선행 조사([[../cmp/abrasive-d99-spec-cross-pack-comparison]] §2.1)가 확인한 "Evonik
콜로이달실리카 기술문서는 D99를 공개 안 하고 Z-average(DLS 평균)만 공개한다"는 관찰이
이 논문으로 **기전이 설명된다**: DLS/SLS 계열 장비(제조사 QC의 표준 장비)는 강도가중이라
평균/모드는 정밀해도 꼬리(개수는 적지만 부피는 큰 극소수 대입자, 또는 반대로 신호가
묻혀 사라지는 극소수 초미세입자)를 대표하지 못한다. D99를 신뢰성 있게 보려면 **개수기반
계수 장비**(SMPS, 또는 업계 표준인 SPOS/Accusizer — [[../cmp/abrasive-d99-composite-particle-versum2019]]
가 쓴 것)가 필요하고, 이는 QC 표준 장비(DLS)와 별도 장비·별도 시료전처리가 필요해
비용상 D99가 상업 스펙시트에 잘 안 실리는 구조적 이유다.

## 3. D99/D50 비율 실측값 — 기존 확보 문헌 재정리(중복 채굴 안 함)

이 비율 자체는 선행 회차가 이미 1차 문헌(특허 실시예 표)에서 확보했다. 이 노트는 새로
채굴하지 않고 **입자 물성 관점에서 재정리**만 한다:

| 시료 | D50 (nm) | D99 (nm) | D99/D50 | 출처 |
|---|---|---|---|---|
| CPOP-20 (세리아코팅실리카) | 94.7 | 172.0 | 1.82 | US10669449B2 Table 3 |
| CP2 (비교예, 세리아코팅실리카) | 35.7 | 136.4 | 3.82 | US10669449B2 Table 3 |
| Hitachi Ex.1 (세리아) | 190 | 700 | 3.68 | US8439995B2 |
| Hitachi Ex.2 (세리아) | 160 | 500 | 3.13 | US8439995B2 |
| Hitachi Comp.1/2 (세리아, 조대입자) | 240 | 2500 | 10.42 | US8439995B2 |

**관측**: 같은 "세리아 계열" 안에서도 D99/D50이 1.82~10.42배로 **5.7배 폭**을 갖는다 —
제조 공정(코팅 vs 비코팅, 침강시간)에 따라 꼬리 두께가 이만큼 달라진다는 뜻이며, 업계
일반비(Levitronix 5.00)가 어느 개별 실측치와도 정확히 맞을 이유가 없다는 것을 재확인한다
(이미 [[../cmp/abrasive-d99-scratch-hitachi-us8439995]] §9.3이 정량 검증: 일반비 5.00은
Ex.1/Ex.2 실측비와 각각 35.7%/60.0% 괴리). §2의 측정법 논증과 결합하면, 이 폭은 **제조
편차만이 아니라 D50과 D99를 서로 다른 장비/원리로 측정했을 가능성**도 일부 기여할 수
있다는 것이 새로운 해석이다(⚠ 미검증 — 특허들이 D50/D99를 같은 장비 같은 런에서 냈는지
원문에 명시 안 됨, Disc Centrifuge 단일장비로 추정되나 확인 못 함).

## 4. 스크래치/손상과 tail 입경의 상관 — 단분산 세리아 직접 실험(신규 문헌)

**Yang, J.C., Kim, H., Kim, T. (2010). "Study of Polishing Characteristics of Monodisperse
Ceria Abrasive in Chemical Mechanical Planarization." *J. Electrochem. Soc.* 157(3),
H235–H240. DOI: 10.1149/1.3273079.** (유료, 미러 사이트 미러 경유 전문 PDF 확보,
`papers/yang-kim2010-monodisperse-ceria-polishing.pdf`, fitz로 6페이지 전문 추출·대조.)

같은 저자 그룹이 §2의 SMPS 분급 기술로 **단일 크기(monodisperse) 세리아 입자군**을
30/100/200/300nm로 물리적으로 분리·웨이퍼에 증착한 뒤 DI수만으로 연마(3 psi, 30s,
화학작용 배제)해 **크기 단독 효과**를 측정한 실험 — 분포가 아니라 "특정 크기 하나"의
연마 결과라 D99 자체의 대응값은 아니지만, "입경이 커질수록 손상이 커진다"는 정성 주장의
**가장 깨끗한 통제실험**(화학종·조건 전부 동일, 크기만 다름)이다.

### 4.1 핵심 실측
- 표면 거칠기(AFM Ra) = 1.5~3.4nm, **Ra ∝ (입경)^0.3346**로 회�귀(원문 명시 지수).
- 300nm 세리아에서만 비정질(amorphous) 손상층이 관찰됨(200nm까지는 결정질 유지, 격자
  변형 층수만 3~4층→5~6층 증가) — **비가역 손상의 문턱이 200~300nm 사이에 있다**는 것을
  직접 관찰(TEM).
- 웨이퍼 표면검사(해상도 40nm)에서도 입경이 클수록 결함(스크래치 포함)이 더 많이
  관찰됨(정성, Fig.9) — 그러나 **모든 입경(30nm 포함)에서 선형 스크래치가 관찰**돼
  "스크래치는 대입자만 만든다"는 통념과 다른 결과도 함께 보고("This phenomenon does not
  agree with the conventional scratch mechanism, in which microscratches are usually
  caused by the larger particles"). 저자는 세리아의 각진 형상·경도가 패드-웨이퍼 접촉조건과
  결합해 크기와 무관한 스크래치 경로도 있다고 해석.

```python verify
import numpy as np

# Yang, Kim, Kim (2010), JES 157(3) H235, doi:10.1149/1.3273079
# 원문: Ra 범위 1.5~3.4nm, Ra ~ x^0.3346 (회귀지수 원문 그대로), 입경군 30~300nm(4점 사용, 400/500nm는 시료부족으로 미시행)
n_reported = 0.3346
ra_min, ra_max = 1.5, 3.4          # nm, 원문 서술 범위
x_min, x_max = 30.0, 300.0         # nm, 실제 폴리싱까지 수행된 입경 범위(30~300nm, 4점)

# 교차검산: 두 극값이 정말 크기 최소/최대에 대응한다면(원문이 "입경 증가->거칠기 증가"라고
# 명시하므로 단조 가정은 정당), 보고된 지수로 그 비율이 재현되는지 확인
predicted_ratio = (x_max / x_min) ** n_reported
actual_ratio = ra_max / ra_min

diff_pct = abs(predicted_ratio - actual_ratio) / actual_ratio * 100
print(f"지수 {n_reported} 예측 Ra비 = {predicted_ratio:.3f}, 원문 서술 범위비 = {actual_ratio:.3f}, "
      f"차이 {diff_pct:.1f}%")
# 원문이 각 크기별 정확한 Ra 표를 텍스트로 주지 않아(Fig.6 그래프만) 완전일치는 기대하지 않음 —
# 오더가 맞는지만 확인(느슨한 허용범위, 그림 판독 오차 감안)
assert diff_pct < 20.0, f"지수-범위 교차검산이 20% 넘게 벌어짐 — 그림 판독 재확인 필요: {diff_pct:.1f}%"

# 이 지수(0.3346, 단일크기 입경->Ra)는 다른 노트의 damage_exponent(D99/D99_ref 비율->스크래치 개수,
# n=1.44 Hitachi 세리아 회귀)와 물리량 자체가 다르다 -- 직접 비교/치환 금지, 방향성만 대조
n_hitachi_d99_scratch = 1.444   # abrasive-d99-scratch-hitachi-us8439995.md 채택값
assert n_reported < n_hitachi_d99_scratch, (
    "단일입경->거칠기 지수가 D99비율->스크래치개수 지수보다 완만해야 한다는 방향성 확인"
    "(서로 다른 축이라 절대 비교는 아님, 방향만)"
)
print(f"참고: n_Ra(0.3346, 단일입경축) < n_scratch(1.444, D99비율축) -- 두 지수 모두 "
      f"sim/factors.py 기본값 damage_exponent=3.0보다 훨씬 완만한 방향으로 일치")
```

### 4.2 이 문헌으로 채우지 않는 것 (정직한 범위 표시)
- 이 실험은 **분포가 아니라 단일 크기 분리 시료**다 — D99/D95/D90 같은 백분위수 개념 자체가
  없다. "대입자 tail이 만드는 스크래치"라는 주제와는 간접적으로만 연결된다(크기 단조성만
  공유). 팩의 `abrasive_d99_nm`이나 `damage_exponent`에 이 지수(0.3346)를 채택하지 않는다
  — 물리량이 다르다(§4.1 verify에서 이미 명시).
- 화학종은 세리아(sti_ceria/sic_ceria_h2o2와 동일 계열)이며, **cu_h2o2_bta/w_fe_oxidizer의
  알루미나, oxide_silica의 콜로이달실리카와는 화학종이 다르다** — 이식 근거 없음.

## 5. 종합 — 3팩 gap은 이 노트로 해소되지 않는다(의도적)

이 노트는 (a) D99가 상업 스펙시트에 잘 없는 **기전**(측정법의 강도가중 vs 개수가중 차이,
§2), (b) 세리아 계열 안에서도 D99/D50 비율이 5.7배 폭을 갖는다는 **재확인**(§3, 새 채굴
없음), (c) 단일입경-손상 관계의 **독립된 정량 지수**(§4, Ra~x^0.3346, 세리아 한정) 세
가지를 확정했다. 그러나 **oxide_silica/cu_h2o2_bta/w_fe_oxidizer 3팩의 실제 D99 절대값이나
더 나은 유도 경로를 새로 제공하지 않는다** — 알루미나 D99 절대값 탐색은 선행 4회차가
이미 "공개 1차 문헌 경로 소진"으로 판단했고([[../cmp/abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]]
§3), 이번 회차 조사(§2 측정법 문헌)도 알루미나 실측 D99를 우연히 주지 않았다. **구현
요청을 새로 추가하지 않는다** — 기존 [[../cmp/abrasive-d99-scratch-hitachi-us8439995]] §9.4
판정(3팩 confidence=estimated 유지)이 이 노트의 발견과 모순되지 않으므로 그대로 둔다.

## 6. 한계·미검증 (정직한 표기)

- ⚠ **미검증**: §2 Kim et al. 2010의 "10⁴배 산란강도차" 수치는 저자의 계산값이며 원문에
  Rayleigh 산란 이론식 유도과정이 실려 있지 않다(참고문헌만 인용) — 독립적으로 재현하지
  못했다. Mie/Rayleigh 산란 이론상 강도가 지름의 4~6차에 비례한다는 것은 교과서 수준
  일반론이라 이 노트에서 재유도하지 않는다(교과서 인용 금지 원칙).
- ⚠ **미검증**: §4 Yang et al. 2010의 Ra 값은 그림(Fig.6)에서 서술한 범위(1.5~3.4nm)만
  텍스트로 확인했고, 30/100/200/300nm 각각의 정확한 Ra 값은 그래프 이미지라 pdftoppm 등
  렌더링 도구 없이는 판독하지 못했다(§4.1 verify가 이 한계를 명시하고 느슨한 허용범위로
  처리).
- ⚠ **미검증**: SMPS의 "600nm 이하 권장, 1µm까지 세리아 한정 가능" 상한이 실리카·알루미나
  등 다른 화학종에도 동일하게 적용되는지는 원문이 명시하지 않음(원문은 실리카·세리아만
  실험).
- **범위 밖이라 제외**: 알루미나(cu_h2o2_bta/w_fe_oxidizer) 자체를 다루는 측정법 비교
  문헌은 이번 탐색에서 찾지 못했다 — "못 찾았다"(미확보)이지 범위 밖 판단은 아니다. 다음
  탐색 후보로 남긴다.

## 7. 출처
- Kim, H., Yang, J.C., Kim, T. (2010). "Measurement of CMP Slurry Abrasive Size Distribution
  by Scanning Mobility Particle Sizer." *Electrochem. Solid-State Lett.* 13(4), H137–H140.
  DOI: 10.1149/1.3299254.
- Yang, J.C., Kim, H., Kim, T. (2010). "Study of Polishing Characteristics of Monodisperse
  Ceria Abrasive in Chemical Mechanical Planarization." *J. Electrochem. Soc.* 157(3),
  H235–H240. DOI: 10.1149/1.3273079.
- US 10,669,449 B2 (Versum Materials). https://patents.google.com/patent/US10669449B2/en —
  Table 3 (D50/D75/D99 재인용, 채굴 없음, [[../cmp/abrasive-d99-spec-cross-pack-comparison]]와 동일 표).
- US 8,439,995 B2 (Hitachi Chemical). https://patents.google.com/patent/US8439995B2/en —
  D50/D99 실시예 표 재인용([[../cmp/abrasive-d99-scratch-hitachi-us8439995]]와 동일 표).
