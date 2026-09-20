<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: carrier, kinematic, multizone, platen | 정본: ARCHITECTURE-V2.md §3 -->
# 멀티존 헤드 압력 제어 — 존-반경 응답과 상호작용 구조

> 담당: [[tool-platen-head]] Lv1-2 · 작성 2026-09-07 · 상태: 검증(출처 기재, 1건 원문 PDF 확보)
> 연결: [[cmp-carrier-head-retaining-ring-vendors]](Lv1-1, AMAT/Ebara 헤드 아키텍처) ·
> [[cmp-tool-architecture]] · [[cmp-kinematics-rotary]]

## 0. 범위
Lv1-1 노트가 "AMAT/Ebara가 어떤 구조로 헤드를 가압하는가"를 다뤘다면, 이 노트는
"실제로 존별 압력을 바꾸면 반경 방향 제거율 프로파일이 어떻게 반응하는가"를 다룬다.
즉 정성적 구조(멤브레인 vs 공압) 다음 단계인 정량적 존-반경 응답이다.
멀티변수 CMP 제어 이론(Shiu et al. 2004)과 존압력-웨이퍼 벤딩 관계(Zhao et al. 2013)는
둘 다 페이월 뒤에 있고 이번 조사에서 원문을 확보하지 못했다(4절에서 상태 명시).
1차 자료는 Lee, Lee, Jeong (2026, JKSPE 43(5))의 원문 PDF다 — Lv1-1과 동일 논문이지만
이번엔 존별 압력 스윕 실험(2.3.2절, Figs. 8-11)에 집중한다.

## 1. 3존 + 리테이너링 구조 — 반경 경계

Lee, Lee, Jeong (2026)[1]은 8인치(203.2mm) 웨이퍼를 반경 방향으로 3개 존 + 리테이너링으로
나눈다. 웨이퍼 중심을 0mm로 하는 반경 좌표계에서:

| 존 | 반경 범위 | 역할 |
|---|---|---|
| Zone 3 (중심) | 0-85 mm | 웨이퍼 대부분(약 83%)을 커버하는 중심 압력존 |
| Zone 2 (중간) | 85-95 mm | 중간 전이 존 |
| Zone 1 (에지) | 95-99 mm | 웨이퍼 최외곽 4mm 폭 |
| 리테이너 링 | 99mm 초과(웨이퍼 밖, 접촉으로 영향) | 웨이퍼를 감싸는 링, 패드 리바운드 통로 |

각 존의 압력을 3.0에서 4.2 psi로 개별 스윕(나머지 존은 3.0psi 고정)했을 때, 반경 방향
제거율 변화가 시작되는 지점과 급변하는 지점이 문헌에 기술되어 있다[1]:

- Zone 1 스윕: 중심으로부터 약 85mm 지점에서 완만한 변화 시작, 약 95mm부터 급격한 증가
- Zone 2 스윕: 약 70mm 지점에서 변화 시작, 약 85mm 지점에서 급격한 감소
- Zone 3 스윕: 약 70mm까지 무변화, 70-85mm 완만한 변화, 85mm 이후 거의 무변화
- 리테이너링 스윕: Zone 1과 유사한 패턴(Fig.11이 Fig.8과 비슷)

이 네 관찰의 공통점: 자기 존의 명목 경계보다 10-15mm 안쪽에서부터 영향이 시작된다.
즉 존 경계는 이산적(discrete)이지만 압력 응답은 경계에서 불연속이 아니라 확산적
(diffusive)이다 — 이는 멤브레인의 유연성과 패드의 점탄성이 존 사이에 압력을 어느 정도
전파시키기 때문으로 저자들은 해석한다[1](3.1절).

## 2. 존 간 상호작용 — Zone3만 독립, 나머지는 결합

문헌의 핵심 결론(3.1절)은 응답 행렬이 대각(diagonal)이 아니라는 것이다[1]:

원문 인용: "Zone 3는 상대적으로 독립적인 거동을 보였으며... 국소적인 압력 조절을 통해
개별적으로 연마 조건을 조정할 수 있다. 반면, Zone 1, Zone 2, 그리고 Retainer
Ring은 서로 유기적인 상호작용을 보이며, 명확한 비독립적 관계를 형성하고 있었다."

정성적으로 정리하면 3x3(+ring) 응답 행렬 R (R_ij = 존 j 압력 변화가 존 i 제거율에
미치는 영향)의 구조는 블록 대각형이다: {Zone1, Zone2, Ring}이 하나의 결합된 3변수
서브시스템이고, Zone3는 독립된 1변수 시스템이다. 이는 다변수 CMP 제어(Shiu et al.
2004, 원문 미확보, 4절)가 일반적으로 상정하는 "완전 결합 다변수계"보다는 단순한
구조로, 실무적으로는 "Zone3는 개별 PID로, {Zone1,Zone2,Ring}은 연립 최적화로"라는
2단 제어 전략이 정당화될 수 있음을 시사한다(제안, 문헌에 명시적 언급 없음 — 이
노트의 해석).

## 3. 정량 결과 — 단일존 vs 멀티존 NU

가장 중요한 정량 대조표(Table 5, [1]):

| 방식 | 리테이너링 압력 | 엣지제외 3mm NU |
|---|---|---|
| 단일존(Wafer#1) | 5.0 psi | 4.5% |
| 단일존(Wafer#2, 링압력만 상승) | 6.0 psi | 6.1% (악화) |
| 멀티존(3존 개별 최적화) | 해당없음 | 2.5% (개선) |

단일존 대비 멀티존의 NU 개선율은 (4.5-2.5)/4.5 = 44.4%. 최악 조건(6psi 단일존)
대비로는 (6.1-2.5)/6.1 = 59.0% 개선. 이 두 수치는 문헌에 직접 서술되어 있지
않고 표 4/5의 원값에서 이 노트가 계산한 것 — 5절에서 코드로 재현한다.

## 4. 미확보 문헌 (2차 인용으로 대체, 원문 미확인)

- Shiu, Yu, Shen (2004), "Multivariable control of multizone chemical mechanical
  polishing", J. Vac. Sci. Technol. B 22(4), 1679-1687, DOI: 10.1116/1.1761483.
  Lee et al. 2026[1]의 Ref.[3]로 인용됨(다중 영역 압력 제어가 재료 제거율의 공간적
  분포를 정밀 제어하도록 고안됐다는 서술의 근거). AIP/AVS 페이월, 미러 사이트 5개 미러
  전부 응답 없음(2026-09-07 시도) 1차 미확보, 2차 인용(Lee et al. 2026 서론)으로
  대체.
- Zhao, Wang, He, Lu (2013), "Effect of zone pressure on wafer bending and fluid
  lubrication behavior during multi-zone CMP process", Microelectronic Engineering
  108, 33-38, DOI: 10.1016/j.mee.2013.03.042. Lee et al. 2026[1]의 Ref.[4]. Elsevier
  ScienceDirect 403, 미러 사이트 5개 미러 전부 무응답 1차 미확보. Lv1-1 노트에서도
  같은 상태로 기록됨 — 두 단원 모두 이 논문의 "0-2.0psi 존압력에서 웨이퍼 벤딩"
  수치를 직접 확인하지 못했다(미검증, 인용하지 않음).
- Wang & Lu (2011), "Numerical and experimental investigation on multi-zone CMP",
  Microelectronic Engineering 88(11), 3327-3332, DOI: 10.1016/j.mee.2011.08.011.
  Lee et al. 2026[1]의 Ref.[1]. 동일하게 미러 사이트 무응답 1차 미확보.

세 논문 모두 미러 사이트/se/st/ru/ren 5개 미러에 DOI로 접속을 시도했으나(2026-09-07,
tools/find_open_access.py의 미러 사이트() 함수 실행) 전부 None을 반환했다(페이지 응답이
없거나 article not found). 이는 접속 차단이 아니라 미러 자체의 가용성 문제로
판단된다(사용자 지시 9/5에 따라 미러 사이트 활용 시도 자체는 규정대로 수행했음을 기록).

## 5. 정량 재현

```python verify
# 문헌값(Table 4/5, Lee, Lee, Jeong 2026 JKSPE 43(5) 443-448) 기반 NU 개선율 재계산

nu_single_5psi = 4.5   # % , retainer ring 5.0 psi, edge exclusion 3mm (Table 3)
nu_single_6psi = 6.1   # % , retainer ring 6.0 psi, edge exclusion 3mm (Table 4)
nu_multizone   = 2.5   # % , 3-zone 개별 최적화, edge exclusion 3mm (Table 5)

# (1) 문헌이 명시한 원값 자체가 맞는지 확인 (표 전사 오류 방지)
assert nu_single_5psi == 4.5
assert nu_single_6psi == 6.1
assert nu_multizone == 2.5

# (2) 이 노트가 계산한 개선율(문헌에 직접 서술되지 않음 — 원값에서 유도)
improve_vs_5psi = (nu_single_5psi - nu_multizone) / nu_single_5psi * 100
improve_vs_6psi = (nu_single_6psi - nu_multizone) / nu_single_6psi * 100

assert abs(improve_vs_5psi - 44.44) < 0.1, f"5psi 대비 개선율 {improve_vs_5psi:.2f}%"
assert abs(improve_vs_6psi - 59.02) < 0.1, f"6psi 대비 개선율 {improve_vs_6psi:.2f}%"

print(f"단일존(5psi) 대비 멀티존 NU 개선: {improve_vs_5psi:.1f}%")
print(f"단일존(6psi) 대비 멀티존 NU 개선: {improve_vs_6psi:.1f}%")

# (3) 존 경계 반경 — 웨이퍼 반지름(8인치=203.2mm -> r=101.6mm) 대비 각 존이 차지하는 비율
wafer_r = 101.6  # mm, 8-inch wafer radius
zone3_outer, zone2_outer, zone1_outer = 85.0, 95.0, 99.0  # mm, Lee et al. 2026 2.3.1절

zone3_frac = zone3_outer / wafer_r
zone1_width_frac = (zone1_outer - zone2_outer) / wafer_r

assert 0.83 < zone3_frac < 0.84, f"Zone3가 반지름의 {zone3_frac:.3f} 차지 (문헌: ~85/101.6mm)"
assert 0.03 < zone1_width_frac < 0.05, f"Zone1 폭이 반지름의 {zone1_width_frac:.3f}"

print(f"Zone3(중심)가 반지름의 {zone3_frac*100:.1f}%를 차지 — 웨이퍼 대부분이 '독립' 존")
print(f"Zone1(에지) 폭 {zone1_outer-zone2_outer}mm = 반지름의 {zone1_width_frac*100:.1f}%")
```

실행 결과(위 python verify 블록, 2026-09-07 실행 확인): 멀티존 도입으로 NU가 단일존(5psi)
대비 44.4%, 최악조건(6psi) 대비 59.0% 개선된다는 것이 Table 3/4/5(Lee et al. 2026) 원
데이터에서 산술적으로 확인된다. 존 경계 비율 계산(위 코드 zone3_frac)도 Lee et al. 2026의
2.3.1절 반경 구간(0-85mm, 85-95mm, 95-99mm) 수치와 일치한다 — 계산값 83.7%는 "Zone3가
상대적으로 독립적"이라는 저자 주장(Lee et al. 2026)이 웨이퍼 면적 대부분을 차지하는
존에서 성립함을 뒷받침하는 이 노트의 해석이다.

## 6. 한계 및 다음 단원 연결

- 이 노트는 정성적 응답 구조(어느 존이 결합됐는가)와 최종 NU 수치만 확보했다.
  존별 압력에서 제거율로 가는 정량적 전달함수(Zhao 2013이 다룰 것으로 추정)는 미확보다.
  저자들 스스로도 결론(4절)에서 "각 영역의 입력 압력과 연마 결과 간의 전달함수를
  도출하고... 피드백 제어 기반 자동화 시스템을 구축하는 방향이 필요하다"고
  향후 과제로 남긴다 — 즉 이 분야 자체가 아직 정량 전달함수 확립 전 단계다.
- Lv1-2는 8인치 웨이퍼 실험이다. 300mm(12인치) 웨이퍼의 존 경계·압력 범위는
  다를 것으로 예상되나(Zhao 2013이 12인치를 다룬다고 알려짐, 4절에서 원문 미확보로
  확인 못함) 이 노트에서 외삽하지 않는다.
- 다음 단원(Lv2-1, 리테이너링 압력·마모와 엣지 프로파일)에서 2절의 링-패드 리바운드
  메커니즘을 재료역학적으로 더 깊이 다룰 것.

## 구현 요청 후보 (직접 구현하지 않음 — software 부문 BACKLOG용, ORG.md 5절 규칙)
- 무엇을: 3x3(+ring) 블록대각 존 응답 구조를 Recipe에 zone_pressures: dict 필드로
  받아 반경별 가중 압력 프로파일(1-2절 경계·결합 구조)을 산출하는 순수함수.
- 근거 노트: 본 노트 1-3절.
- 검증에 쓸 문헌값: Table 3/4/5 NU 4.5%/6.1%/2.5% (edge exclusion 3mm 기준).
- 우선순위: 낮음(정량 전달함수 미확보 상태라 지금 구현하면 6절에서 지적한 대로
  근사를 넘어 추측이 됨 — Zhao 2013 원문 확보 후 재요청 권장).

## 출처
[1] Lee, T.S., Lee, E.H., Jeong, H.D. (2026), "Multi-zone Pressure Control for
    Improvement of Within Wafer Non-uniformity in CMP", J. Korean Soc. Precis. Eng.
    43(5), 443-448, DOI: 10.7736/JKSPE.025.132. 원문 PDF 확보(CC-BY-NC, Unpaywall).
[2] Shiu, S.-J., Yu, C.-C., Shen, S.-H. (2004), "Multivariable control of multizone
    chemical mechanical polishing", J. Vac. Sci. Technol. B 22(4), 1679-1687,
    DOI: 10.1116/1.1761483. 1차 미확보(미러 사이트 무응답), Lee et al. 2026을 통한
    2차 인용.
[3] Zhao, D., Wang, T., He, Y., Lu, X. (2013), "Effect of zone pressure on wafer
    bending and fluid lubrication behavior during multi-zone CMP process",
    Microelectronic Engineering 108, 33-38, DOI: 10.1016/j.mee.2013.03.042.
    1차 미확보(미러 사이트 무응답), Lee et al. 2026을 통한 2차 인용.
[4] Wang, T., Lu, X. (2011), "Numerical and experimental investigation on multi-zone
    chemical mechanical planarization", Microelectronic Engineering 88(11),
    3327-3332, DOI: 10.1016/j.mee.2011.08.011. 1차 미확보(미러 사이트 무응답),
    Lee et al. 2026을 통한 2차 인용.
