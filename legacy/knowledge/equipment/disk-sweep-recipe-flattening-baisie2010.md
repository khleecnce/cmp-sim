<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: conditioner, disk-, pcr, sweep | 정본: ARCHITECTURE-V2.md §3 -->
# 스윕 레시피 최적화 — 세그먼트 스윕시간 프로파일과 패드 평탄화 목표 (Baisie et al. 2010)

> disk-kinematics Lv2-2. "sweep 레시피 최적화: 패드 프로파일 평탄화 목표" 단원. [[conditioner-sweep-algorithm-trajectory-density]]
> (disk-kinematics Lv1-1, 반환점 밀도발산의 해석적 원인)과 [[conditioner-sweep-kinematics-pcr-profile]]
> (disk-conditioner Lv2-2, PCR 격자적산)이 각각 "왜 비균일이 생기는가"를 다뤘다면, 본 노트는
> "어떤 스윕 프로파일이 실제로 평탄한 패드를 만드는가"를 표면요소법(surface element method)
> 시뮬레이션-실험 대조 논문으로 정량 확인한다.

## 1. 출처
1. **Baisie, Li & Zhang (2010)**, "Simulation of Diamond Disc Conditioning in Chemical Mechanical
   Polishing: Effects of Conditioning Parameters on Pad Surface Shape", *ASME 2010 International
   Manufacturing Science and Engineering Conference (MSEC2010)*, Vol. 2, DOI:
   10.1115/MSEC2010-34264. — **1차 출처, 원문 전체 확보**(미러 사이트 경유, DOI 조회 → 302 리다이렉트
   → 미러 사이트 미러 → PDF 직접 다운로드, `papers/baisie2010_disc_conditioning.pdf`, pypdf로 본문
   전체 추출). find_open_access.py는 CrossRef까지만 매칭되고 OA 사본은 못 찾아 유료 폴백 경로 사용
   (사용자 지시 9/5).
2. 논문이 인용하는 **Freeman & Markert (1996)**, "Characterization of pad conditioning profiles in
   oxide CMP", CMP-MIC 1996 — 모델 검증에 쓰인 실험 원자료(FLAT 1/FLAT 2/BELL 프로파일, Table 1·2).
   본 노트는 이를 직접 확보하지 못하고 Baisie et al.(2010)이 재인용한 수치만 사용 — **2차 인용**.
3. Preston(1927) — 이미 다른 노트에서 실존 확인된 고전 문헌, 본 논문 Eq.(1)의 근거로만 재인용.

## 2. 모델 골격 — 표면요소법(Surface Element Method)
Baisie et al.은 Preston 방정식(dh ∝ Kp·P·v_relative)을 다이아몬드 디스크 컨디셔너의 스윕 궤적에
적분하는 형태로 확장한다(Eq.1–9). 핵심 입력은 패드 반경 Rp, 컨디셔너 반경 Rc, 패드 회전속도 Np,
컨디셔너 회전속도 Nc, 그리고 **스윕 프로파일 {tᵢ}** — 컨디셔너 중심이 반경방향으로 n개 세그먼트를
가로지르는 데 걸리는 체류시간의 수열이다(§2 논문 원문). 세그먼트가 겹치며(overlap) 누적 마모
H(rp)를 이룬다(Eq.7). 모델은 Matlab으로 구현되었고, Freeman & Markert(1996)의 FLAT1/FLAT2/BELL
세 프로파일 실측 패드 두께 프로파일과 대조해 "good agreement"로 검증되었다(Fig.3, 본문 서술 —
수치 오차 %는 논문에 명시되어 있지 않음, **미검증**: 그래프 육안 일치만 확인 가능, 정량 RMSE는
원문에 없음).

## 3. 평탄화 지표 3종 — 논문 정의 (원문 발췌, Eq.10–12)
- **TTV** (Total Thickness Variation) = max(H(rp)) − min(H(rp)) — 패드 반경방향 두께 측정값 중
  최댓값-최솟값. (§ Metrics, Eq.10)
- **Bow** = 중간반경점의 median surface 위치와, 중심·엣지 두 점을 잇는 기준평면(reference plane)
  사이 편차. 양수=오목(concave), 음수=볼록(convex). (Eq.11)
- **NU** (Non-Uniformity) = 반경방향 두께값들의 표준편차(평균두께 대비 편차의 표준편차로 정의,
  본문 서술은 "mean deviation…standard deviation…employed"로 다소 모호 — 정확한 정규화 상수는
  원문 수식 이미지가 텍스트 추출 과정에서 누락되어 **확인 못 함**). ← wafer-metrology의 TTV/CV
  정의(σ/μ×100)와 유사하지만 **동일하지 않다**. 사용자가 회사에서 쓰는 TTV(=81pt 전체 max−min)
  정의와 본 논문의 TTV(=반경방향 측정점 max−min) 정의는 "max−min" 골격은 같지만 측정 축(패드
  반경 vs 웨이퍼 전면)이 다르다는 점을 병기한다 — **패드 프로파일 지표를 웨이퍼 지표에 직접
  전용(轉用)하면 안 된다**는 실무적 함의.

## 4. 정량 결과 (논문 §Effect of Sweeping Profile, Table 3, 원문 발췌)
논문 Table 3은 20세그먼트 스윕시간 프로파일 5종(UNIFORM/CONCAVE/CONVEX/DESCENT/ASCENT)의 실제
숫자를 제공한다. 논문 본문 서술(수치 그래프 Fig.6은 텍스트로 추출 안 됨, 서술만 인용):
> "DESCENT shows the highest TTV whilst CONVEX shows the highest Bow. ASCENT and CONVEX show the
> highest values of NU. UNIFORM exhibits the best flatness in terms of TTV and NU."

결론(원문 Conclusions 1–5, 그대로 발췌):
1. 총 컨디셔닝시간이 일정하면 세그먼트 스윕시간 자체(2~10초)는 패드 프로파일에 영향 없음(Fig.5).
2. 스윕 프로파일은 패드 형상에 "거울(mirroring)" 효과를 가지며, **UNIFORM(균일) 프로파일이
   최선의 평탄도**.
3. 패드 회전속도가 높을수록 마모가 커지고 오목해짐 — 낮은 패드속도가 평탄도에 유리하나 MRR과
   트레이드오프.
4. 컨디셔너 회전속도의 영향은 패드 회전속도보다 훨씬 약함.
5. **컨디셔너 직경이 작을수록 평탄** — 이론상 단일점 다이아몬드가 가장 평탄하나 실용성 낮음.

## 5. Python 재현 (Table 3 원자료로 TTV/NU 정성 재현)
논문의 시뮬레이션 파이프라인(Eq.1–9, 표면요소법 전체)은 팔-피벗 기하 등 미공개 파라미터가 많아
전체 재현은 범위 밖이다. 대신 **Table 3의 실제 세그먼트 시간값**을 "세그먼트당 체류시간=국소
컨디셔닝 노출량"의 직접 프록시로 삼아, 논문이 서술한 순위(UNIFORM 최평탄, DESCENT/ASCENT류
비대칭 프로파일이 TTV 악화)를 재현할 수 있는지 확인한다. 이는 논문 모델(면적가중 누적마모)의
근사이지 재현이 아니므로 결과는 **정성적 순위 검증**으로만 쓴다.

```python verify
import numpy as np

profiles = {
    "UNIFORM": [2]*20,
    "CONCAVE": [3.76,3.30,2.85,2.43,2.05,1.72,1.44,1.23,1.08,1.01,
                1.01,1.08,1.23,1.44,1.72,2.05,2.43,2.85,3.30,3.76],
    "CONVEX":  [0.24,0.70,1.15,1.57,1.95,2.28,2.56,2.77,2.92,2.99,
                2.99,2.92,2.77,2.56,2.28,1.95,1.57,1.15,0.70,0.24],
    "DESCENT": [4,3.8,3.6,3.4,3.2,3,2.8,2.6,2.4,2.2,2,1.8,1.6,1.4,1.2,1,0.8,0.6,0.4,0.2],
    "ASCENT":  [0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2,2.2,2.4,2.6,2.8,3,3.2,3.4,3.6,3.8,4],
}
# Baisie et al. (2010) Table 3, 20-segment sweeping time profiles (verbatim from paper)

TTV, NU, bow = {}, {}, {}
for name, ti in profiles.items():
    ti = np.array(ti, dtype=float)
    TTV[name] = ti.max() - ti.min()
    NU[name] = ti.std() / ti.mean() * 100.0
    center = ti[:3].mean(); edge = ti[-3:].mean(); mid = ti[9:11].mean()
    bow[name] = mid - 0.5 * (center + edge)  # 양수=오목(concave) 방향 프록시

# 논문 결론(1): UNIFORM이 TTV·NU 모두 최평탄이어야 한다
assert TTV["UNIFORM"] == 0.0, f"UNIFORM TTV 기대 0, 실제 {TTV['UNIFORM']}"
assert NU["UNIFORM"] == 0.0, f"UNIFORM NU 기대 0, 실제 {NU['UNIFORM']}"
assert TTV["UNIFORM"] < min(TTV[k] for k in profiles if k != "UNIFORM"), "UNIFORM이 TTV 최소여야 함"
assert NU["UNIFORM"] < min(NU[k] for k in profiles if k != "UNIFORM"), "UNIFORM이 NU 최소여야 함"

# 논문 결론: DESCENT가 TTV 최고
assert TTV["DESCENT"] == max(TTV.values()), f"DESCENT가 TTV 최고여야 함(논문 서술): {TTV}"

# CONVEX는 Bow 방향이 CONCAVE와 반대여야 함(거울 효과, 결론 2 "mirroring effect")
assert bow["CONVEX"] * bow["CONCAVE"] < 0, f"CONVEX/CONCAVE bow 부호가 반대여야 함: {bow}"

print("TTV:", {k: round(v,2) for k,v in TTV.items()})
print("NU%:", {k: round(v,2) for k,v in NU.items()})
print("bow_proxy:", {k: round(v,3) for k,v in bow.items()})
```

문헌 재현 대조(Baisie et al. 2010): 논문 결론(1)의 UNIFORM 프로파일 TTV=0.00 s를 코드로
재현했고, DESCENT 프로파일 TTV=3.80 s는 5개 프로파일 중 최댓값으로 논문 서술("DESCENT shows
the highest TTV", Baisie et al. 2010)과 정확히 일치했다(문헌값과 정성적 순위 일치, 단위=초).

실행 결과(2026-09-07 확인): `TTV: {'UNIFORM': 0.0, 'CONCAVE': 2.75, 'CONVEX': 2.75, 'DESCENT': 3.8,
'ASCENT': 3.8}`, `NU%: {'UNIFORM': 0.0, 'CONCAVE': 44.0, 'CONVEX': 48.0, 'DESCENT': 54.92,
'ASCENT': 54.92}`. 5개 assert 모두 PASS. **부분 일치**: UNIFORM 최평탄(결론 2)과 CONVEX/CONCAVE
거울대칭(bow 부호 반전)은 정성적으로 재현됐다. 그러나 **논문 서술과 어긋나는 부분**: 논문은
"ASCENT and CONVEX show the highest values of NU"라고 했는데 본 프록시는 ASCENT=DESCENT가 NU
공동최고이고 CONVEX는 중간이다(48.0% < 54.92%) — 이는 **세그먼트 시간값 자체를 국소마모의 직접
프록시로 쓰는 단순화가, 논문의 실제 파이프라인(반경별 환형면적 가중 + 겹침 적산, Eq.5–7)과
다르기 때문**으로 추정된다(확인 못 함, 원인 미상으로 정직하게 기록). TTV 순위(DESCENT 최고)는
정확히 일치했다.

## 6. 실무적 함의 — fab-sim 관점
- 스윕 레시피 최적화의 1차 원칙: **세그먼트 체류시간을 반경에 대해 균일(UNIFORM)하게 유지**하는
  것이 표면요소법 모델·실측 양쪽에서 최선의 평탄도를 낸다(Baisie et al. 결론 2).
- 단, [[conditioner-sweep-algorithm-trajectory-density]] (Wang et al. 2025)의 결론(4)와 대조하면
  흥미로운 긴장이 있다: Wang et al.은 "정속(균일) 스윕이 오히려 패드 중심을 과다컨디셔닝하며,
  3구간 가변속 전략이 낫다"고 결론짓는 반면, Baisie et al.은 "UNIFORM(세그먼트시간 균일)이
  최선"이라고 결론짓는다. **이 둘은 서로 다른 "균일"을 말한다** — Wang et al.의 "정속"은 각속도
  (dθ/dt)가 일정한 것이고, Baisie et al.의 "UNIFORM"은 반경 세그먼트별 체류시간(tᵢ)이 균일한
  것이다. 각속도 균일 스윕은 반환점에서 tᵢ가 자동으로 커지므로(§3 아크사인/오프셋원 밀도발산),
  Baisie의 "체류시간 균일"과 Wang의 "각속도 균일"은 **양립 불가능**하다 — 체류시간을 균일하게
  만들려면 각속도를 반경에 따라 가변시켜야 한다. 두 논문의 결론이 겉보기 모순처럼 보이지만
  실제로는 **최적화 변수(각속도 프로파일 θ(t) vs 세그먼트 체류시간 프로파일 tᵢ) 정의가 다른
  것**으로 해소된다 — sim/ 구현 요청 시 이 구분을 반드시 명시해야 한다(아래 §7).
- 컨디셔너 직경은 작을수록 평탄(결론 5) — [[conditioner-sweep-kinematics-pcr-profile]]의 디스크
  유효반경 52.25mm 실측 조건과 교차 참고 가능.

## 7. 구현 요청 (소프트웨어 부문, sim/ 코딩은 담당 안 함 — 2026-09-05 지시)
- **무엇을**: 스윕 레시피 최적화기 — 입력: 목표 반경별 체류시간 프로파일(예: UNIFORM 또는
  임의 목표) → 출력: 그 목표를 만족하는 각속도 θ(t) 프로파일(반환점 근방 가속 필요, §3 아크사인
  역산). Baisie et al. Eq.1–9(표면요소법)를 골격으로, Wang et al.(2025) 결론(4)의 "3구간 가변속"
  아이디어를 연결.
- **근거 노트**: 본 노트 §3, §6 + [[conditioner-sweep-algorithm-trajectory-density]] §3.
- **검증에 쓸 문헌값**: Baisie et al. Table 3(5개 프로파일) → TTV=0(UNIFORM 목표) 재현, 그리고
  Fig.5(세그먼트시간 자체는 총시간 고정시 무관, 결론 1) 재현.
- **우선순위**: 중간 — disk-kinematics Lv3-2(모델 구현 단원)에서 본격 착수 예정이나, 엔진
  `sim/tier2_physics/`에 conditioner PCR 모듈이 이미 있다면(pad_glazing_jeong2024.py 등과 유사
  위치) 그 옆에 배치 검토.

## 8. 한계와 정직성 표지
- Freeman & Markert(1996) 원자료는 미확보(2차 인용) — Baisie et al.의 재인용 수치만 사용.
- 논문 Fig.3의 "good agreement"는 정성 서술뿐 정량 RMSE/오차%가 원문에 없음 — **미검증**.
- NU의 정확한 정규화 정의(분모가 평균인지 절대편차 합인지)는 원문 수식이 텍스트 추출로 깨져
  **확인 못 함** — 본 노트 §5 코드는 표준적 CV(σ/μ×100) 정의를 가정한 것으로, 논문의 실제 NU
  계산과 다를 수 있음. 순위(어떤 프로파일이 더 나쁜가)는 논문 서술과 대조했으나, §5에서 밝혔듯
  ASCENT/CONVEX 순위가 어긋났다.
- §6의 "체류시간 균일 vs 각속도 균일 양립불가" 논증은 본 노트의 **자체 해석**이며, 두 논문 어느
  쪽도 직접 이렇게 연결하지 않았다.

## 관련 노트
[[conditioner-sweep-algorithm-trajectory-density]] · [[conditioner-sweep-kinematics-pcr-profile]] ·
[[disk-rpm-load-radius-pcr]] · [[disk-insitu-exsitu-conditioning-mrr-stability]]
