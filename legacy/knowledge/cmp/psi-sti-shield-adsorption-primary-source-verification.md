<!-- V2-SECTION: R2-slurry | 공동: R1-chem | 작성 2026-09-15 | 근거: shield_langmuir_K/hill_n/strength_k — 특허 실시예 인쇄표 탐색 + Hill n 특이성 독립 반증 -->
# ψ STI 세리아 흡착 보호 상수 — 1차 출처(특허 인쇄표) 탐색과 Hill n 특이성 교차검증

> cmp-chemistry Lv3-2 | 작성일: 2026-09-15
> 선행: [[psi-surface-adsorption-shield-oxide-ceria]] (Park 2003 Fig.3 최초 회귀 — 그림 판독),
> [[psi-shield-hill-constants-ceria-primary-source]] (같은 그림을 독립 재판독 + n 비식별
> 반증, confidence estimated 유지 판정), [[psi-adsorption-shield-oxide-systems]] (세 팩 배선).
> 이 노트의 질문 둘: (A) 위 두 선행 노트는 모두 **Park 2003 Fig.3의 그림 판독**에 의존한다
> (원문에 수치표가 없음, 선행 노트 §2에서 확인됨) — 그림 판독이 아니라 **인쇄된 숫자표**를
> 가진 STI 세리아 슬러리 특허 실시예를 찾아 K·n·k를 독립적으로 대조할 수 있는가?
> (B) 못 찾는다면, Hill 협동지수 n=4.62(모든 팩에 공유 적용된 값)가 **이 화학계 일반의
> 성질**인지 아니면 Park의 특정 첨가제(PAA 계면활성제)에 국한된 것인지, 최소한 방향만이라도
> 다른 문헌으로 검증할 수 있는가.

---

## 1. 왜 다시 파는가 — 선행 노트가 이미 답하지 못한 것

`psi-shield-hill-constants-ceria-primary-source.md`(2026-09-15)는 Park 2003 Fig.3를
독립 재판독해 기존 값을 재현했지만, **판독의 정확도**만 검증했지 **판독이라는 방법 자체의
한계**(원문에 수치표 없음, 그 노트 §2에서 이미 확인)는 벗어나지 못했다. 이 노트가 겨냥하는
구멍은 다르다: 인쇄된 숫자로 조성×제거율이 실린 **특허 실시예**를 찾아, 그림 판독 없이
K·n·k를 재추정하고 Park 2003 유도값(K_ox=1.2949, n=4.62, k_ox=3.0 / K_ni=14.02, n=4.62,
k_ni=3.4, `knowledge/params/sti_ceria.yaml`)과 대조하는 것이다.

같은 막다른 길을 반복하지 않기 위해 먼저 확인한 것: 선행 두 노트 모두 "그림 판독은 이
문헌을 쓰는 한 피할 수 없다"(선행 노트 §7-1)고 이미 자백했다. 그러므로 이번 조사는 **다른
문헌**(Park 2003이 아닌 특허 또는 독립 논문)을 찾는 것이지, Park 논문을 다시 읽는 게 아니다.

---

## 2. 특허 실시예 탐색 — 실패 로그

코퍼스 DB(`data/corpus/corpus.sqlite`)에서 kind=patent, 제목에 STI/ceria/polyacrylic/
selectivity 포함 21건을 조회했다.

1. **이미 fulltext 확보된 3건 스캔** (그림 판독 없이 텍스트만 grep):
   - **JP6829197B2**(Rohm and Haas류 STI 세리아, ionic polymer + 폴리비닐알콜 + 폴리하이드록시
     방향족): 조성별 A/B/C 비교(첨가제 있음/없음)만 있고 **농도 스윕이 아니다**. 탈락.
   - **US9828528B2 / EP3265526B1**(Cabot, ceria 표면 tridentate 수산기 + picolinic acid):
     산화막 RR 표(Table 1·3·10 등)는 풍부하나 **질화막 RR 측정이 통째로 없다**(문서 전체
     "nitride" 언급 8건, 전부 배경 설명뿐). 선택비 표 자체가 없어 탈락.
   - 나머지 discovered 상태 특허(CN107353833A 세리아+폴리메타크릴레이트, US6616514B1,
     KR102774703B1, WO2023150245A1, CN117120563B, US12116502B2 등)는 fulltext 미확보.
2. **`tools/corpus.py`의 `fetch_one`**(patents.google.com 직접 HTTP)로 CN107353833A,
   US6616514B1 시도 → **둘 다 HTTPError**(이 환경의 네트워크 정책상 Google Patents 직접
   요청이 막혀 있음, [[fabsim-literature-access-fallbacks]] 기록과 일치).
3. **WebFetch로 `patents.google.com` 접근** → 503(차단, 위와 동일 원인).
4. **WebFetch로 `freepatentsonline.com`** → US 특허는 렌더 **성공**(예: US6616514B1 —
   실시예는 계면활성제/PAA가 아니라 **mannitol(유기 폴리올)** 농도 스윕이었다. 화학종
   불일치로 탈락). 그러나 CN107353833A·KR102774703B1·WO2023150245A1 같은 비-US 번호는
   이 사이트 자체에 없어 번호 검색이 실패한다 — freepatentsonline은 US 특허 전용 미러다.

⚠ **1차 출처(인쇄된 특허 실시예 표) 확보 실패.** 유력 후보(CN107353833A: 세리아+폴리메타
크릴레이트, 산화막·질화막 선택비 특허 — PAA와 가장 가까운 음이온 폴리머 화학)는 네트워크
차단으로 접근 자체가 안 됐다. 이것이 정직한 결과다 — 특허가 없다는 뜻이 아니라 **이 세션의
네트워크 환경에서 그 특허에 닿지 못했다**는 뜻이다.

---

## 3. 방향 전환 — 같은 연구그룹의 후속 논문 탐색

특허가 막히자 대안으로 Park 2003 저자 그룹(Hanyang Univ., Jea-Gun Park·Ungyu Paik)의
**후속 논문**에서 농도 스윕이 반복됐는지 확인했다(WebSearch → Crossref DOI 확정 →
IOPscience/find_open_access.py 순).

- **Kang, Lee, Park, Paik, Park (2005)**, *Jpn. J. Appl. Phys.* **44**(7R), 4752,
  DOI: 10.1143/JJAP.44.4752, "Dependence of pH, Molecular Weight, and Concentration of
  Surfactant in Ceria Slurry on Saturated Nitride Removal Rate in STI CMP". IOPscience
  초록에서 저자·권/호/페이지 확인, 계면활성제 농도 범위 "0.1 to 0.3 wt%"가 언급됨(Park
  2003의 0~0.8 wt% 범위와 겹친다 — 같은 화학계의 확장 스윕일 가능성이 높음). **본문 접근
  실패**: IOPscience 페이월, `find_open_access.py`는 OA 사본 없음, 미러 사이트 전 도메인이
  이 세션에서 완전 차단(DNS 실패 — `curl` 직접 시도로 확인, [[fabsim-literature-access-fallbacks]]
  "미러 사이트 전멸" 기록과 일치).
- **Kang, Park, Cui, Paik, Park (2008)**, *ECS Meeting Abstracts* MA2008-01, 693,
  DOI: 10.1149/ma2008-01/17/693. 이미 로컬 캐시에 있었다(`papers/kang2008-ecs-organic-
  additive-oxide-nitride-selectivity-ceria-sti.pdf`, 2쪽 회의초록). 확인한 내용: **PAA
  1/2/3 wt%를 고정 배경**으로 두고 amino-methyl-propanol(AMP) 농도 0~3.0 wt%를 스윕,
  Si₃N₄ RR과 선택비를 Fig.2·3에 그래프로만 제시(수치표 없음). 화학종이 AMP(Park 2003의
  PAA 단독계와 다름)라 K/n/k 재추정에 직접 쓸 수 없다 — 하지만 "같은 그룹이 같은 실험
  틀(세리아+음이온/양쪽성 첨가제 농도 스윕)을 5년 뒤에도 반복하고 있다"는 방법론적
  일관성의 정황 증거로만 인용한다.
- **Kang et al. (2008)**, *J. Korean Phys. Soc.* **53**, 1337(트리에탄올아민 첨가),
  DOI: 10.3938/jkps.53.1337 — JKPS 공식 사이트가 빈 페이지를 반환(JS 렌더 의존 추정),
  WebSearch 요약만 확보(정성적 서술, 수치표 없음). 본문 미확보.

**세 편 모두 원문 수치표를 얻지 못했다** — 두 편은 페이월+미러 사이트 차단, 한 편은 사이트
렌더 실패. 이 경로도 정직하게 막다른 길이다.

---

## 4. 대안 검증 — Dandu 2015 (독립 그룹, CC-BY 전문 확보): Hill n=4.62의 화학종 특이성

특허·후속논문 경로가 막힌 뒤, 질문을 좁혔다: 값(K, n, k)을 재추정할 순 없어도, **Hill
협동지수 n=4.62가 이 화학계 일반의 성질인지, 아니면 Park의 특정 첨가제(계면활성제/PAA,
hemimicelle 형성 물질)에 국한된 것인지**는 **다른 첨가제**로 검증할 수 있다. 기존 노트
(psi-surface-adsorption-shield-oxide-ceria.md §3)가 이미 "아미노산은 흡착량-억제율이
반증됐다"고 다른 화학종을 배제했으므로, 여기서는 **소분자 수소결합 공여체**(계면활성제가
아닌) 첨가제의 흡착 곡선 모양을 확인한다.

**Penta, Amanapu, Babu (2015)**, "Further Investigation of Slurry Additives for Selective
Polishing of SiO₂ Films over Si₃N₄ Using Ceria Dispersions", *ECS J. Solid State Sci.
Technol.* **4**(11), P5025–P5028, DOI: 10.1149/2.0061511jss. **CC BY 4.0 오픈 액세스** —
로컬 캐시 `papers/dandu2015-jss-further-slurry-additives-sio2-si3n4-ceria.pdf`에서 전문
확인(4쪽, 저자·DOI·라이선스 원문에서 직접 확인, 미러 사이트 불필요). Clarkson 대학
S.V. Babu 그룹 — Park/Paik 그룹과 무관한 독립 저자.

이 논문은 피리딘·소르비톨의 세리아/산화막/질화막 표면 흡착량을 열중량분석(TGA)으로
직접 측정하고 농도 의존성을 Fig.3에 그래프로 제시한다(원문에 수치표는 없음 — 이 역시
그림 판독이 되지만, **Park 2003이 아닌 완전히 다른 논문의 그림**이라는 점에서 이 노트의
목적("다른 문헌으로 교차검증")에 부합한다). Fig.3을 1200 dpi로 렌더해 곡선 형태를 확인:

- **소르비톨**(Fig.3b, SiO₂/Si₃N₄-pH4): 0, 0.0055, 0.027, 0.055, 0.11 M에서 흡착량이
  대략 0 → 18 → 38(SiO₂)/58(Si₃N₄) → 108/113 → 165/201 mg/g로 **거의 선형**이다 —
  0.11 M까지 포화 기미가 전혀 없다. Hill 곡선이 요구하는 "임계농도에서 급격한 포화"가
  없다.
- **피리딘**(Fig.3a): 0→0.009 M에서 급격히 상승(0→12.5/15 mg/g)한 뒤 0.045 M까지 계속
  완만히 상승 — **오목(concave)** 형태로 단일자리 Langmuir(n=1)와 정성적으로 일치하고,
  Park의 S자(문턱 이하 평탄 → 급락) 형태와는 다르다.

### 4.1 정량 대조 — n=4.62를 소르비톨 곡선에 강제 대입하면?

소르비톨 5점(그림 근사 판독, §6 verify에 명시)에 세 가지 모형을 적합했다:

| 모형 | 자유 파라미터 | SSE |
|---|---|---|
| 순수 선형(원점 통과) | a | 630.2 |
| Hill (K, n, Y_max 자유) | 3개 | **271.97**(n≈2.0으로 수렴) |
| Hill, **n=4.62 고정**(Park 값 강제) | K, Y_max | **993.4** |

n을 자유롭게 두면 데이터는 n≈2.0(약한 협동성)을 선호한다 — 이것도 `shield_hill_n`
(sti_ceria.yaml, [[psi-shield-hill-constants-ceria-primary-source]])의 Park 값 4.62보다
훨씬 작다. 자유 Hill 적합과 순수 선형 모형을 대조하면 SSE가 약 57% 낮다(630.2→272.0, 곡률은 실재하나 Park 값의 절반 이하 세기).
결정적으로 Park의 n=4.62를 문헌값 그대로 강제 대입해 재현을 시도하면 SSE가 993.4로, 순수 선형(630.2)보다도 나빠 재현에 실패한다.
즉 n=4.62는 소르비톨(수소결합 공여체, 비-계면활성제) 흡착을
전혀 설명하지 못하며, 억지로 끼워 맞추면 데이터를 왜곡한다.

**해석**: 이것은 sti_ceria 팩의 n=4.62가 틀렸다는 증거가 아니다 — Park 2003의 첨가제는
poly-acrylic acid(PAA, Mw=50000)라는 **고분자 음이온 계면활성제**이고, hemimicelle
협동흡착(n≫1)은 정확히 이런 사슬형·자기조립성 분자에서 기대되는 거동이다(기존 노트 §4).
소르비톨·피리딘은 작은 분자, 수소결합 단일 부위 흡착이라 n≈1~2가 물리적으로 맞다. 이
대조는 오히려 **"n=4.62는 물질 일반의 상수가 아니라 Park의 특정 첨가제 화학종에 고유한
값"이라는 기존 노트(§9-③)의 주장을 다른 화학계에서 독립적으로 재확인**한다 — 다른
첨가제로 전이하면 안 된다는 경고를 강화하는 방향의 증거이지, K/n/k 자체의 등급을 올리는
근거는 아니다.

---

## 5. 최종 등급 판정

**confidence=`estimated` 유지, 승격하지 않는다.** 이번 조사는 다음 세 가지를 확립했다:

1. 인쇄된 숫자표를 가진 대체 1차 출처(특허 실시예)는 **찾지 못했다** — 유력 후보
   (CN107353833A)는 네트워크 차단으로 접근 불가, 접근 가능했던 특허(US6616514B1,
   JP6829197B2, US9828528B2)는 화학종·측정 항목 불일치로 사용 불가.
2. 같은 저자 그룹의 후속 문헌 3편(Kang 2005 JJAP, Kang 2008 ECS, Kang 2008 JKPS)이
   존재해 **방법론적 일관성**(세리아+음이온/양쪽성 첨가제 농도 스윕이 이 그룹의 반복
   실험 설계)의 정황은 강화됐지만, 페이월과 미러 사이트 전면 차단으로 **수치는 얻지 못했다**.
3. 독립 그룹(Dandu/Babu 2015, CC-BY)의 다른 첨가제 데이터로 **n=4.62가 Park의 특정
   화학종에 국한된 값**이라는 기존 노트의 경고가 정량적으로(SSE 비교) 재확인됐다 —
   이는 K/n/k **점추정치의 등급**을 올리지는 못하지만, **다른 화학종에 전이 금지**라는
   판정을 더 단단하게 만든다.

EVIDENCE-RULES 서열로 보면 이 노트는 (K, n, k) 자체에 새 증거를 더하지 못했으므로
E3(선행 노트 판정)를 바꿀 근거가 없다. 승격 조건("파라미터가 데이터로부터 개별
식별되는가")은 여전히 미충족이다.

---

## 6. verify 블록

```python verify
"""ψ STI 세리아 흡착 보호 상수 — 대체 1차 출처 탐색 실패 기록 + Dandu 2015 교차검증.

이 블록이 지키는 것:
  ① sti_ceria.yaml 게시값(Park 2003 유도)이 여전히 참조 가능함을 재확인
  ② Dandu 2015(독립 CC-BY 논문) 소르비톨 흡착 5점(그림 근사 판독, ⚠ 참고용)에
     Park의 n=4.62를 강제 대입하면 순수 선형 모형보다 SSE가 나쁨 — 전이 금지 근거
  ③ 자유 Hill 적합의 n이 4.62보다 훨씬 작음(n≈2) — 화학종별 협동성 차이 정량 확인
"""
import numpy as np
from scipy.optimize import curve_fit

# ── ① sti_ceria.yaml 게시값 (Park 2003 유도, 선행 노트에서 검증됨) ──
K_OX, N_HILL, K_STRENGTH_OX = 1.2949, 4.62, 3.0
K_NI, K_STRENGTH_NI = 14.02, 3.4
assert abs(K_NI / K_OX - 10.83) < 0.05          # 선택비 창의 기원 (K 비)

# ── Dandu 2015 Fig.3b 그림 근사 판독 (SiO2-pH4, 소르비톨) — 5점, 참고용 ──
C = np.array([0.0, 0.0055, 0.027, 0.055, 0.11])
Y = np.array([0.0, 18.0, 38.0, 108.0, 165.0])

def hill(x, K, n, Ymax):
    xx = np.where(x > 0, (K * x) ** n, 0.0)
    return Ymax * xx / (1.0 + xx)

# 순수 선형(원점 통과)
lin_a, _ = curve_fit(lambda x, a: a * x, C, Y)
sse_lin = float(np.sum((Y - lin_a[0] * C) ** 2))

# Hill, n 자유
popt_free, _ = curve_fit(hill, C, Y, p0=[20, 2, 200], maxfev=20000,
                          bounds=([0.1, 0.5, 50], [1000, 20, 500]))
sse_free = float(np.sum((Y - hill(C, *popt_free)) ** 2))
n_free = popt_free[1]

# Hill, n=4.62 강제 (Park sti_ceria.yaml 값 그대로 대입)
def hill_n462(x, K, Ymax):
    return hill(x, K, N_HILL, Ymax)
popt_forced, _ = curve_fit(hill_n462, C, Y, p0=[10, 200], maxfev=20000,
                            bounds=([0.1, 50], [1000, 500]))
sse_forced = float(np.sum((Y - hill_n462(C, *popt_forced)) ** 2))

# ② n=4.62 강제 대입은 순수 선형보다 못하다 -> 다른 화학종에 전이 금지
assert sse_forced > sse_lin, (sse_forced, sse_lin)

# ③ 자유 적합 n은 4.62보다 뚜렷이 작다(소르비톨은 약한 협동성 또는 무협동)
assert n_free < 3.0, n_free
assert sse_free < sse_lin, (sse_free, sse_lin)  # Hill(자유)이 선형보다는 낫다 -> 약한 곡률은 있음

print(f"PASS — n_free={n_free:.2f} (Park 값 4.62보다 작음), "
      f"SSE: 선형={sse_lin:.1f} / Hill자유={sse_free:.1f} / Hill(n=4.62 강제)={sse_forced:.1f} "
      f"-> n=4.62 강제가 선형보다도 나쁨(전이 금지 근거)")
```

실행 결과: `PASS — n_free=2.00 (Park 값 4.62보다 작음), SSE: 선형=630.2 / Hill자유=272.0 /
Hill(n=4.62 강제)=993.4 -> n=4.62 강제가 선형보다도 나쁨(전이 금지 근거)`

---

## 7. 한계 · 정직성 표지

1. **§4의 소르비톨 5점은 그림 근사 판독이다** — Park 2003 그림 판독과 방법론적으로
   같은 한계를 갖는다(1200 dpi 렌더, 마커 중심 눈대중). 다만 이 절의 결론(n=4.62가
   소르비톨에 안 맞는다)은 판독 오차 몇 %에 좌우되지 않는 **정성적 형태 차이**(선형 vs
   S자 문턱)에 의존하므로 판독 정밀도가 결론을 뒤집을 가능성은 낮다.
2. **CN107353833A(세리아+폴리메타크릴레이트) 특허는 여전히 미확인이다.** 이 노트가
   확보하지 못한 것이지, 존재하지 않는다는 뜻이 아니다. 초록만으로는 실시예에 농도 스윕
   표가 있는지 알 수 없다 — 향후 세션에서 이 세션과 다른 네트워크 경로(예: Lens.org,
   Espacenet)로 재시도할 가치가 있다.
3. **Kang 2005 JJAP(10.1143/JJAP.44.4752)는 Park 2003의 직접 후속(같은 그룹, 겹치는
   농도 범위 "0.1–0.3 wt%")이라 확보 시 가치가 매우 높다** — 그러나 이 세션에서는
   IOPscience 페이월과 미러 사이트 전면 차단(DNS 실패)으로 막혔다. 다음 시도자를 위해
   경로를 정확히 남긴다: DOI 확인됨(§3), OA 사본 없음(`find_open_access.py` 확인됨),
   기관 리포지토리(Hanyang Univ.) 확인은 시도하지 않았다 — 다음 후보.
4. **Dandu 2015는 다른 화학종(피리딘·소르비톨) 데이터라 K/n/k 자체를 대체하지 않는다.**
   이 노트가 얻은 것은 "다른 화학종에서는 n=4.62가 안 맞는다"는 **부정적** 확인이지,
   sti_ceria의 값을 검증하거나 대체하는 **긍정적** 확인이 아니다. §5에서 이를 명확히
   승격 사유로 쓰지 않은 이유이기도 하다.
5. **AMP(Kang 2008)·TEA(Kang 2008 JKPS) 데이터는 그래프/정성 서술만 확보돼 정량
   교차검증에 쓰지 않았다.** 방법론적 정황 증거로만 §3에 인용했다.
