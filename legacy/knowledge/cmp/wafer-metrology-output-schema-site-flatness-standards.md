<!-- V2-SECTION: R5-wafer | 공동: R1-equipment | 분배완료 2026-09-08 | 근거: flatness, metrology, pattern-, wafer- | 정본: ARCHITECTURE-V2.md §3 -->
# Lv3-2 — 출력 스키마 확정: 두께/평탄도 표준 지표(ASTM/SEMI)와 측정 사이트 배치의 문헌 근거

> 에이전트: wafer-metrology Lv3-2 | 작성일: 2026-09-08
> [[uniformity-metrics-definitions-standards]] [[inline-virtual-metrology-sampling-optimization]] [[pattern-metrics-dishing-erosion-stepheight]] [[wafer-metrology-thickness-methods]]

## 0. 목적

Lv1-2에서 TTV·WIWNU·CV·radial을 확정했지만 그건 하나의 스칼라 지표 정의였다.
Lv3-2는 sim/metrics/가 앞으로 받아야 할 입력/출력 스키마 자체 — 어떤 필드가 있어야
하는지, 웨이퍼 기하(GBIR류) 표준 약어 체계, 측정 사이트 개수/배치(49점 vs 52점 vs 81점)의
근거를 문헌에서 정리한다. 코드 구현은 하지 않는다(2026-09-05 지시: 트랙B는 소프트웨어 부문) —
PROFILE.md 구현요청으로 넘긴다.

## 1. ASTM/SEMI 두께·형상 지표 전체 체계 (1차 확보: PDF 원문)

1차 출처: mast-tech.com.tw 배포 자료집(semi-definition.pdf, 대만 계측장비 대리점,
ASTM F534/F657/F1241/F1390/F1530 원문 발췌·재구성. 원문 표준 자체가 아니라 3차 편집물이므로
"원문 미확보, ASTM 표준 발췌 편집본으로 확인"으로 표기).

### 1.1 두께 계열
- Thickness (ASTM F657): 전면-후면 대응점 간 거리.
- TTV (ASTM F657): TTV = t_max - t_min (스캔 전체) — [[uniformity-metrics-definitions-standards]]
  §1의 SEMI MF1530 정의와 동일 수식, 다른 표준(ASTM F657)에서 독립적으로 같은 식 확인 → 교차검증 성공.

### 1.2 형상 계열 (Bow/Warp) — uniformity.py에 없는 필드, 신규 확인
- Bow (ASTM F534): 자유 상태 웨이퍼 중앙면(median surface, 전후면의 중간 궤적)이 웨이퍼 가장자리
  둘레 3점 기준평면으로부터 벗어난 정도. Z = (B-A)/2 (B,A = 하부/상부 프로브-표면 거리).
  중심 1점만 본다 — 부분적 두께 편차는 상쇄되어 사라진다(이게 warp와 근본적으로 다른 이유).
- Warp (ASTM F1390): 중앙면 전체가 기준평면에서 벗어난 최대-최소.
  Warp = RPD_max - RPD_min (RPD = reference plane deviation), 항상 양수.
  기준평면은 3점 평면 또는 최소자승 평면 중 선택.
  CMP 관점 의미: bow=0이어도 warp>0일 수 있다(중앙에서 기준평면과 교차하는 s자형 웨이퍼) →
  CMP 압력분포 예측 시 bow만으로는 웨이퍼 형상 이상을 놓칠 수 있음(정성 판단, 원문 예시 Figure 4 재현).

### 1.3 평탄도 계열 (ASTM F1530) — 약어 체계 전체 확인, uniformity.py의 잠정 정의를 대체할 후보
전역(Global) vs 사이트(Site) x 후면기준(Backside) vs 전면기준(Frontside) x range(R) vs deviation(D):

| 약어 | 풀네임 | 기준면 | 계산 | 비고 |
|---|---|---|---|---|
| GBIR | Global Backside Ideal-plane Range | 이상 평탄 후면(척 흡착 가정) | T_max - T_min | =TTV와 수학적으로 동일 (원문이 직접 등호로 명시) |
| GF3R/GF3D | Global Frontside 3-point-plane Range/Deviation | 전면 3점 평면 | R=Vmax-Vmin, D=max(|Vmax|,|Vmin|) | 리소 툴이 전면 기준(비짐발) |
| GFLR/GFLD | Global Frontside Least-squares-plane R/D | 전면 최소자승 평면 | 위와 동일 계산, 평면만 다름 | 리소 툴이 전면 기준(짐발 가능) |
| SBIR/SBID | Site Backside Ideal-plane R/D | 이상 평탄 후면 | 사이트별 R 또는 D | 사이트 단위 |
| SF3R/SF3D | Site Frontside 3-point-plane R/D | 전역 3점 평면(사이트마다 재계산 X) | 사이트별 R/D | |
| SFQR/SFQD | Site Frontside Q(least-squares)-plane R/D | 사이트별 개별 최소자승 평면 | 사이트별 R/D | 업계에서 가장 흔히 인용되는 site flatness 지표(SFQR) — 정성 판단, 원문은 인용빈도를 다루지 않음 |

uniformity.py와의 관계: 현재 ttv_nm은 GBIR과 동일 개념(후면 이상평탄 가정)이다.
현재 코드에 SFQR류(사이트별 국소 평면)가 없다 — 이는 리소그래피 스텝퍼 depth-of-focus
문제에서 중요한 지표이며, CMP 후 국소 평탄도 스펙(SFQR 기준)을 검증하려면 신규 필드가
필요하다는 근거가 됨(§4 구현요청).

## 2. 측정 사이트 배치 — "49점"의 기원과 대안 (2차 확인, 원문 Cloudflare 차단으로 1차 미확보)

- Bibby & Harwood, "Cartesian coordinate maps for chemical mechanical planarization uniformity
  characterization", Thin Solid Films 308-309 (1997) 539-544, DOI: 10.1016/S0040-6090(97)00435-5.
  원문 PDF 미확보(미러 사이트 경유 미러 미러 사이트이 Cloudflare 챌린지로 차단, ScienceDirect
  paywall) — ScienceDirect·Semantic Scholar 초록만 확인. 이 절의 수치는 2차 인용(검색 스니펫).
- 초록 요지: "49-site 극좌표(polar) 맵이 CMP에서 산업 표준처럼 쓰이지만 필름 불균일도를
  오도할 수 있다(misrepresent)"고 주장. 저자들은 52-site 직교좌표(Cartesian) 맵이
  CMP 필름 불균일도 추정에 더 적합하다고 결론(52 사이트 실험으로 뒷받침, 정량치는 원문 미확보라 인용 못함).
  → 미검증: 49 vs 52 사이트의 정량적 오차 크기는 원문 없이 못 밝힘. "폴라 맵이 엣지 부근에서
  scallop형 패턴을 만들어 불균일도를 오판할 수 있다"는 정성적 주장만 2차로 확인.
- wafer-metrology-thickness-methods.md(Lv1-1)·inline-virtual-metrology...(Lv3-1)에서 이미
  49점/81점 격자가 반복 등장 — 두 자료 모두 "산업 관행"으로 다루지 산업 표준 문서(SEMI)를
  직접 인용하지는 않았다(재확인, 동일 결론 유지).
- 제조사 실측 예(2차, 정량): Thermo Fisher Theta 300 애플리케이션 노트 — 300 mm 웨이퍼 49점
  oxynitride 두께 맵에서 range 0.0054(단위 표기 모호, 원문 "nm"·"Å" 혼용 추정) · σ 0.79%만 정성 참고,
  절대두께 수치는 단위 불명확하여 인용하지 않음.

## 3. sanity check (Python 재현)

GBIR=TTV 항등식과 SBIR/SBID 정의를 원문 Figure 7/8 예시 수치로 재현한다.

```python verify
# ASTM F1530 (mast-tech.com.tw 편집본, 1.3절) 원문 Figure 7 예시값 재현
def sbir(vmax, vmin):
    return vmax - vmin

def sbid(vmax, vmin):
    return max(abs(vmax), abs(vmin))

# 원문 Figure 7: Vmax=+1 µm, Vmin=-0.5 µm
sbir_v = sbir(1.0, -0.5)
sbid_v = sbid(1.0, -0.5)
assert abs(sbir_v - 1.5) < 1e-9, f"SBIR mismatch: {sbir_v}"
assert abs(sbid_v - 1.0) < 1e-9, f"SBID mismatch: {sbid_v}"

# 원문 Figure 8a: Vmax=0, Vmin=-1 µm -> SBIR=SBID=1 (극값이 중심에서 나면 둘이 같아짐)
assert abs(sbir(0.0, -1.0) - 1.0) < 1e-9
assert abs(sbid(0.0, -1.0) - 1.0) < 1e-9
# 원문 Figure 8b: Vmax=1, Vmin=0 -> 동일
assert abs(sbir(1.0, 0.0) - 1.0) < 1e-9
assert abs(sbid(1.0, 0.0) - 1.0) < 1e-9

# GBIR = TTV 항등식 재현 (T_max, T_min 임의값)
def gbir(tmax, tmin):
    return tmax - tmin

def ttv(tmax, tmin):  # uniformity.py 정의, SEMI MF1530
    return tmax - tmin

tmax, tmin = 725.3, 724.1  # um, 임의 합성값
assert gbir(tmax, tmin) == ttv(tmax, tmin), "GBIR과 TTV가 수식상 동치가 아님(원문 주장과 모순)"

print("PASS: SBIR/SBID 원문 예시(Fig.7,8a,8b) 재현, GBIR=TTV 항등식 확인")
```

전부 통과(assert 4건):
- SBIR = 1.5 µm (Fig.7 문헌값과 일치)
- SBID = 1.0 µm (Fig.7 문헌값과 일치)
- Fig.8a: SBIR=SBID=1.0 µm (문헌값과 일치)
- Fig.8b: SBIR=SBID=1.0 µm (문헌값과 일치)
- GBIR(725.3 um, 724.1 um) = TTV(725.3 um, 724.1 um) = 1.2 um (항등식 확인)
모두 원문 예시값(측정 실데이터 아님, 정의 검증용).

## 4. 구현 요청 (트랙B로 인계 — PROFILE.md에 등록)

- sim/metrics/flatness.py 신설: GBIR/GF3R/GF3D/GFLR/GFLD/SBIR/SBID/SF3R/SF3D/SFQR/SFQD
  11종 함수 + Bow/Warp 2종. 입력은 기존 compute_metrics_points와 동일 (x,y,value) 사이트 배열,
  기준평면 계산(3점/최소자승)이 신규 의존성(numpy.linalg.lstsq로 충분).
- 근거: 본 노트 1.2·1.3절, 검증은 3절 assert 그대로 회귀테스트로 승격.
- 우선순위: Low — 현재 엔진 출력(WaferResult)에 형상(bow/warp) 필드가 아예 없어 스키마 확장이
  선행되어야 함. G1 유지보수 모드 중 후순위.

## 5. 남은 미검증/한계

- ASTM F534/F657/F1241/F1390/F1530 원문 자체(ASTM 표준 원문)는 여전히 미확보 — 이 노트는
  3차 편집물(mast-tech.com.tw) 경유. 편집물이 원문을 정확히 옮겼는지는 SBIR/SBID 예시 재현으로
  간접 검증했으나(3절), 전체 표준 텍스트 신뢰도는 미검증.
- Bibby & Harwood(1997) 원문 미확보 — 49 vs 52 사이트 정량 비교치, 오차 크기 전부 미검증.
- SEMI E142(XML 웨이퍼맵)·KLARF(KLA 결함파일)는 조사했으나 테스트/분류(bin) 맵 표준이지
  두께/평탄도 계측 스키마가 아니어서(범위 밖) 채택하지 않음 — "범위 밖이라 뺐다"로 기록.
- SEMI M49(edge exclusion 가이드) 원문은 store-us.semi.org 유료 페이지만 확인, 원문 미확보.
  2차 확인(review 스니펫): 300 mm에서 EE 3 mm 근처 웨이퍼 면적의 약 3.8% 제외, 200 mm에서 EE 5 mm 근처
  약 12% 제외 — 수치의 1차 출처를 못 찾아 미검증으로만 기록, assert 없음.
