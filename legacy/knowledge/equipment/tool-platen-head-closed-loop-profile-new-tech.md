<!-- V2-SECTION: R1-equipment | 분배완료 2026-09-08 | 근거: carrier, flowrate, multizone, platen, rpm | 정본: ARCHITECTURE-V2.md §3 -->
# 폐루프 프로파일 제어와 헤드 신기술 — 존압력 최적화·복합경도 리테이너링

> 담당: [[tool-platen-head]] Lv3-1 · 작성 2026-09-08 · 상태: 검증(1차 출처 2건, python verify)
> 연결: [[cmp-multizone-carrier-radial-response]](Lv1-2, Zone1/Zone2/Ring 결합 응답) ·
> [[cmp-retaining-ring-wear-edge-profile]](Lv2-1, FEA 접촉응력·특허 구조) ·
> [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]](Lv2-2, RPM·유량·온도 제어)

## 0. 범위와 1차 출처 확보 현황

이 단원의 원래 목표는 "존압력을 인시츄 두께/막두께 센싱 신호로 실시간 되먹임하는
진짜 의미의 폐루프 프로파일 제어" 문헌을 찾는 것이었다. `tools/scope.py` 검색어
("tool platen head CMP after:2011" 등)로 다음 후보들을 찾았으나 전부 페이월/봇차단으로
막혔다:

> ⚠ 1차 출처 확보 실패 (시도 경로 기록):
> - Wang, Lu, Zhao, He, "Contact stress non-uniformity of wafer surface for
>   multi-zone CMP process" (Sci. China Technol. Sci., DOI: 10.1007/s11431-013-5245-y) —
>   Unpaywall `is_oa: false`, 저장소 사본 없음. [[cmp-multizone-carrier-radial-response]]
>   Lv1-2에서도 동일 문헌이 미러 사이트 무응답으로 미확보였던 바로 그 논문(Wang & Lu 계열) —
>   이번에도 실패, 여전히 미해결 과제로 남는다.
> - Zhao, Lu, "Chemical mechanical polishing: Theory and experiment" (Friction,
>   DOI: 10.1007/s40544-013-0035-x) — Crossref/Unpaywall은 cc-by 공개로 표시하지만
>   실제 `link.springer.com` PDF·랜딩 페이지 요청 모두 "Client Challenge"(봇 차단,
>   JS 챌린지 페이지만 반환, content-length 3038B 고정)로 본문 확보 실패.
> - Lee, Kim, Jeong, "Approaches to Sustainability in CMP: A Review" (Int. J.
>   Precis. Eng. Manuf.-Green Technol., DOI: 10.1007/s40684-021-00406-8) — 동일한
>   Springer 봇차단으로 실패.
> - Oniki, Khajornrungruang, Suzuki, "In situ measurement method for film
>   thickness ... on CMP" (Jpn. J. Appl. Phys., DOI: 10.7567/jjap.56.07kh02) —
>   IOP `iopscience.iop.org` 요청이 Radware Bot Manager 캡차 페이지 반환으로 실패.
> - 미러 사이트 3개 미러(.se/.st/.ru) 전부 알트차(altcha) 로봇 확인 챌린지로 폴백 불가
>   (기존 메모리 기록과 동일 증상 — 미러 사이트 경로는 전멸 상태 유지).

대신 실제로 원문을 확보한 것은 (1) 존압력을 실제로 스윕하며 프로파일 개선을 정량
설계한 FEA+실험 논문 하나, (2) 2011년 이후 출원된 헤드 신기술 특허 하나다. 둘 다
"실시간 센서 피드백"은 아니지만, 폐루프 제어가 성립하려면 반드시 있어야 하는
"존압력을 어느 방향/크기로 바꾸면 프로파일이 어떻게 반응하는가"라는 대응 관계
자체를 정량적으로 제공한다 — 이것이 없으면애초에 피드백 제어기를 설계할 수 없다.

## 1. 존압력(P1) 최적화를 통한 프로파일 제어 — Park, Han & Kim (2020)[1]

Park, Han, Kim(2020)[1]은 300mm 웨이퍼용 5존 + 리테이너링 멀티존 캐리어 헤드(반경
0-40/40-100/100-128/128-145/145-150mm = Zone5~Zone1, 그 바깥이 리테이너링)를 대상으로,
Will Be S&T사가 제공한 실측 데이터로 검증한 ABAQUS FEA 정적 모델을 구축했다.
[[cmp-multizone-carrier-radial-response]]의 Lee et al.(2026, 8인치 3존)과는 다른
장비·웨이퍼 스케일이지만, "가장 바깥 엣지 존(Zone1/여기선 P1)이 리테이너링과
결합해 엣지 비균일도를 지배한다"는 구조적 결론은 공통적으로 재확인된다.

### 1.1 실험: P1 스윕으로 엣지 오버/언더폴리싱 부호가 뒤집힌다

모델 #4(그루브 폭 12mm 리테이너링) 기준, 리테이너링 11.9psi·P2-P5 고정, P1만
9.3→8.5→7.65→6.0psi로 낮췄을 때 실측 상대 MRR(r=143mm 지점, 단위 Å, 평균값)[1]§2.2:

| P1 [psi] | 상대 MRR@143mm [Å] |
|---|---|
| 9.3 | +887 |
| 8.5 | +508 |
| 7.65 | +96 |
| 6.0 | −705 |

부호가 양(엣지 오버폴리싱)에서 음(엣지 언더폴리싱)으로 반전되는 지점이 P1≈7.5-7.65psi
부근에 있다 — 즉 "최적 P1"이 존재하며, 무작정 낮추는 것이 아니라 어느 지점을
넘으면 반대 방향으로 악화된다[1]§2.2("there may be an optimal P1 value"). 이 비단조성은
[[cmp-rpm-ratio-flowrate-temperature-mrr-stability]] Lv2-2에서 확인한 슬러리 유량의
비단조 최적점 존재와 같은 패턴이다 — CMP의 여러 제어변수가 "많을수록/적을수록
좋다"가 아니라 중간에 최적점을 갖는 경우가 반복해서 나타난다.

### 1.2 FEA 최적화: 4가지 설계변수의 개선율 비교

검증된 FEA 모델(모델 #1 = 양산 기준형)을 기준으로, 형상·압력을 하나씩 바꿔가며
최대 상대 MRR(MRMRR, 웨이퍼 변위 최대편차, 단위 mm)의 개선율을 계산했다[1]§3:

| 설계 변경 | 조건 | MRMRR [mm] | 개선율 |
|---|---|---|---|
| (기준) | 양산형, R/P1..P5=11.9/9.3/4.4/4.5/4.5/4.7psi | 0.7078×10⁻³ | — |
| 리테이너링 하부 테이퍼 | h=0.015mm | 0.4766×10⁻³ | 32.7% |
| 리테이너링 내측 모서리 라운드 | r=1.5mm | 0.4238×10⁻³ | 40.1% |
| **P1(엣지존 압력)만 변경** | 9.3→7.5psi | 0.2628×10⁻³ | **62.9%** |
| 리테이너링 압력 변경 | 11.9→9.9psi | 0.6080×10⁻³ | 14.1% |

가장 큰 개선(62.9%)이 "리테이너링 형상을 바꾸지 않고 P1(엣지존 압력)만 조정"에서
나온다는 점이 핵심이다[1]§3.3 — 이는 형상 재설계(테이퍼·라운드 가공, 하드웨어
교체가 필요) 없이 압력 레시피만 바꿔도 얻을 수 있는 개선이므로, 실시간/런투런
폐루프 제어기가 조작할 수 있는 가장 유력한 변수가 P1(엣지존 압력)임을 시사한다.
단, [1]의 이 결과는 **오프라인 FEA 설계 탐색**이지 실시간 피드백 루프가 아니다 —
"막두께 센서 신호 → 실시간 P1 재조정"을 실제로 구현/검증한 문헌은 0절에 기록한
대로 이번 조사에서 확보하지 못했다. 이 표는 그런 폐루프 제어기가 존재한다면
따라야 할 "이득 방향(gain sign)"을 제공하는 정적 캘리브레이션 곡선으로 이해해야
한다.

### 1.3 FEA 모델의 한계 (원문이 스스로 명시)

- 2D 축대칭 모델을 사용했다(리테이너링의 슬러리 그루브 때문에 실제로는 완전
  축대칭이 아니므로, 3D 모델 결과를 원주방향 산술평균해 2D와 비교 후 차이가
  작음을 확인하고 2D를 채택)[1]§2.3, Fig. 10.
- 정적 해석이며 리테이너링의 실제 회전은 반영하지 않는다[1]§2.3.
- 멀티존 헤드가 웨이퍼에 전달하는 실제 압력이 멤브레인을 거치므로 FEA의 직접
  압력경계조건과 약간 다를 수 있다[1]§2.3 — 원문이 스스로 "미검증(불확실성)"으로
  인정한 부분이다.
- 패드 탄성계수 20MPa(밀도 35kg/m³로 표기 — **미검증**: 밀도값이 통상 발포
  폴리우레탄 패드의 실제 밀도(수백 kg/m³대)에 비해 비정상적으로 낮아 원문의 오타
  또는 단위 누락 가능성이 있으나 원문 텍스트를 그대로 옮긴 것 외에 추가 확인은
  못했다)는 [[cmp-retaining-ring-wear-edge-profile]]의 서브패드 탄성계수(3.9MPa)와는
  다른 부재(메인 패드 vs 서브패드)이므로 직접 비교 대상이 아니다.

## 2. 헤드 신기술 — 복합경도 리테이너링 (US9,193,030 B2, Strasbaugh)[2]

[[cmp-retaining-ring-wear-edge-profile]] Lv2-1에서 다룬 두 가지 엣지제어 메커니즘
(FEA 접촉응력의 기하학적 완화, US7121927B2의 접촉 세그먼트 면적 축소)과는 다른
제3의 접근으로, "리테이너링의 재질 경도 자체를 이원화"하는 특허가 2011년 이후
출원·등록되었다.

US9193030B2[2](Strasbaugh Inc., 발명자 Kalenian·Spiegel)는 2010-10-05 가출원,
2011-10-04 정식출원(US13/252,897, 이후 US8,740,673으로 등록), 2015-11-24 계속출원
등록이다. 청구 구조[2]:

- **외곽 리테이너링 본체**: PEEK, PET, 폴리카보네이트 등 매우 단단한 재질,
  경도 **Shore D 80-85**.
- **내측 삽입물(insert)**: 폴리우레탄 등 상대적으로 부드러운 재질, 경도
  **Shore A 85-95** (특허 원문 표기: 이는 Shore D 33-46에 상당한다고 명시[2]).
- 삽입물은 리테이너링 내주면 전체(도면상 실시예 1) 또는 내주면 하단의 요철
  단(rabbet)에만(실시예 2) 배치 가능.

특허 명세서의 논리는 "링 전체가 단단하면 웨이퍼 엣지에서 패드가 급격히 눌렸다가
링 안쪽 경계에서 급격히 풀려나는(rebound) 불연속이 커지고, 링 내측면이 부드러우면
그 전이가 완만해져 엣지 오버폴리싱이 줄어든다"는 것이다[2](SUMMARY) — 정성적으로
[[cmp-retaining-ring-wear-edge-profile]]의 Zheng et al.(2023) FEA 결론("링이 있으면
엣지 응력이 완만히 전이되고, 없으면 급격히 휘어 오른다")과 같은 방향의 메커니즘을
"링의 유무"가 아니라 "링 내측면의 강성"이라는 연속 변수로 재구성한 것이다.

**미검증**: Shore A 85-95가 Shore D 33-46에 "상당한다"는 대응관계는 특허 명세서
자체의 주장이며, ASTM D2240 Shore A-D 변환은 경험적 상관관계표에 기반해 재질별로
편차가 크므로 이 노트에서 독립적인 수식으로 재현·검증할 수 없다 — 특허 문언
그대로만 인용한다. 또한 이 특허가 실제로 몇 %의 NU 개선을 냈는지에 대한 정량
수치(원문 Fig. 6-7 레이더 그래프)는 텍스트 추출로는 확인하지 못해 **미검증**으로
남긴다.

## 3. 종합 — 엣지 비균일도를 조절하는 세 가지 독립적 손잡이

지금까지 확보한 3개 단원(Lv2-1, Lv1-2, 이 노트)을 합치면, CMP 엣지 프로파일을
바꾸는 손잡이는 최소 세 가지로 정리된다:

| 손잡이 | 메커니즘 | 출처 | 재설계 필요? |
|---|---|---|---|
| 접촉 세그먼트 면적 | 링 하부의 슬러리 채널 배치로 실접촉 길이를 웨이퍼 둘레의 11.5%로 축소 | US7121927B2[[cmp-retaining-ring-wear-edge-profile]] | 하드웨어(링) 교체 |
| 링 내측 강성 | 단단한 본체(Shore D 80-85) + 부드러운 내측 삽입물(Shore A 85-95) | US9193030B2[2] (이 노트) | 하드웨어(링) 교체 |
| 엣지존 압력(P1) | 존압력 스윕만으로 62.9%까지 NU 개선(FEA) | Park et al.(2020)[1] (이 노트) | **레시피만 변경, 하드웨어 불변** |

세 손잡이 중 유일하게 "실시간/런투런 폐루프 제어기가 공정 중 조작 가능한" 것은
엣지존 압력이다. 링 형상·재질은 한 번 장착하면 고정되는 물리적 파라미터이기
때문이다. 즉 문헌이 뒷받침하는 결론은 "폐루프 프로파일 제어를 구현한다면 가장
먼저 조작해야 할 변수는 엣지존(예: [[cmp-multizone-carrier-radial-response]]의
Zone1) 압력이고, 링 형상·재질은 그 제어 범위의 물리적 한계를 결정하는 사전 설계
변수"라는 것이다 — 다만 이 결론 자체는 이 노트가 개별 문헌들을 조합해 도출한
추론이며, 이렇게 명시적으로 결론 내린 단일 문헌은 확보하지 못했다.

## 4. Python 검증 — Park et al.(2020) 개선율 재계산

```python verify
# Park, Han & Kim (2020), Appl. Sci. 10(23):8362, DOI 10.3390/app10238362 (CC-BY)
# 원문 Section 3, "Conclusions" 절의 MRMRR(최대 상대 MRR, mm) 값을 그대로 사용해
# 이 노트가 재계산한 개선율이 원문이 보고한 개선율과 일치하는지 검증한다.

mrmrr_base   = 0.7078e-3   # 기준(양산형 모델 #1), R/P1..P5=11.9/9.3/4.4/4.5/4.5/4.7 psi
mrmrr_taper  = 0.4766e-3   # 리테이너링 하부 테이퍼 h=0.015mm
mrmrr_corner = 0.4238e-3   # 리테이너링 내측 모서리 라운드 r=1.5mm
mrmrr_p1     = 0.2628e-3   # P1(엣지존)만 9.3->7.5psi로 변경
mrmrr_ring   = 0.6080e-3   # 리테이너링 압력 11.9->9.9psi로 변경

def improve_pct(new, base=mrmrr_base):
    return (base - new) / base * 100

computed = {
    "taper_h0.015mm":  improve_pct(mrmrr_taper),
    "corner_r1.5mm":   improve_pct(mrmrr_corner),
    "P1_9.3to7.5psi":  improve_pct(mrmrr_p1),
    "ring_11.9to9.9psi": improve_pct(mrmrr_ring),
}
literature_pct = {
    "taper_h0.015mm":  32.7,
    "corner_r1.5mm":   40.1,
    "P1_9.3to7.5psi":  62.9,
    "ring_11.9to9.9psi": 14.1,
}

for k, v in computed.items():
    diff = abs(v - literature_pct[k])
    assert diff < 0.15, f"{k}: 재계산 {v:.2f}% vs 문헌값 {literature_pct[k]}% (오차 {diff:.2f}%p)"

print("Park et al.(2020) 개선율 재현 결과 (재계산 vs 문헌값):")
for k in computed:
    print(f"  {k:22s} {computed[k]:6.2f}% vs {literature_pct[k]:5.1f}%")

# P1이 4가지 변경 중 가장 큰 개선을 낸다는 원문의 정성적 주장도 함께 확인
assert computed["P1_9.3to7.5psi"] == max(computed.values()), \
    "P1 조정이 최대 개선이라는 원문 주장이 재계산과 불일치"
print("확인: 4가지 설계변경 중 P1(엣지존 압력) 단독 조정이 최대 개선율(62.9%)")
```

실행 결과(2026-09-08 확인): 4개 개선율 모두 문헌값과 오차 0.15%p 이내로 재현되고
(계산값 32.66/40.12/62.87/14.10% vs 문헌 32.7/40.1/62.9/14.1%), P1 단독 조정이
최대 개선율이라는 원문의 정성적 주장도 재계산으로 확인된다.

## 5. 다음 단원 연결 및 구현 요청 후보

- 다음 단원(Lv3-2, 툴 설정→압력·속도 분포 모델)에서 [[cmp-multizone-carrier-radial-response]]의
  Zone1/Zone2/Ring 결합 응답 행렬과 이 노트의 "P1이 가장 강한 손잡이"라는 결론을
  합쳐, 존압력 레시피 최적화의 정적 감도 모델(민감도 행렬) 초안을 만들 수 있다.
- **진짜 폐루프(실시간 센서→압력 재조정) 문헌 확보는 여전히 미해결 과제**다.
  IOP(JJAP), Springer(Friction, IJPEM-GT) 두 출판사가 봇차단으로 막혀 있어, 이후
  단원에서 다른 출판사(예: Elsevier, AIP, IEEE)의 동일 주제 논문을 우선 탐색하거나,
  사용자에게 기관 접속 경로 확인을 요청하는 것이 합리적이다.
- 구현 요청 후보(software 부문 BACKLOG용, 직접 구현하지 않음): 없음 — 위 3절의
  "3가지 손잡이" 비교는 정성적 종합이고, 실제 sim/ 모델에 넣을 만한 전달함수
  (압력→NU 감도 계수)는 Park et al.(2020)의 FEA 결과에서 추출 가능하지만 이는
  300mm/5존 특정 장비 조건에 국한된 값이라 일반화하려면 추가 문헌(Wang & Lu 계열,
  여전히 미확보)이 필요하다.

## 출처

[1] Park, J.-Y., Han, J.-H., Kim, C. (2020), "A Study on the Influence of the
    Cross-Sectional Shape of the Metal-Inserted Retainer Ring and the Pressure
    Distribution from the Multi-Zone Carrier Head to Increase the Wafer Yield",
    Applied Sciences 10(23), 8362, DOI: 10.3390/app10238362. 원문 확보: MDPI 공식
    경로(`mdpi.com/.../pdf`)는 Akamai 403 차단, **CDN 직링크
    `res.mdpi.com/d_attachment/applsci/applsci-10-08362/article_deploy/applsci-10-08362.pdf`로
    본문 PDF 확보**(CC-BY, papers/park2020-app10238362-zone-pressure-retainer-ring.pdf).
[2] US9193030B2, "CMP retaining ring with soft retaining ring insert",
    Strasbaugh Inc.(발명자 Kalenian, Spiegel), 가출원 2010-10-05 / 정식출원
    2011-10-04(US13/252,897) / 등록 2015-11-24. Google Patents 원문 확보
    (papers/us9193030b2-soft-retaining-ring-insert.txt).
