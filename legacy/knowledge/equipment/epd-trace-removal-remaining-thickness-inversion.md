# EPD 트레이스 → 제거량·잔막 역산 — 신호특징점의 물리량 대응과 오버폴리시 계산

> tool-endpoint Lv2-2. 선행: [[epd-optical-motor-friction-eddy-current-comparison]] (Lv1-1, 세 원리),
> [[epd-signal-processing-filtering-overpolish]] (Lv1-2, 필터·오버폴리시 — 이 노트는 §3의 필터지연
> 수치를 재사용하되 재유도하지 않는다), [[epd-film-type-suitability-transparent-multilayer-limits]]
> (Lv2-1, 막질별 한계·간섭 주기 $\lambda/2n$). 관련: [[cmp-tool-endpoint-thermal-slurry-delivery]],
> [[../cmp/preston-luo-dornfeld-mrr]] (제거율 모델).
>
> Lv1-2·Lv2-1이 이미 다룬 **필터·노이즈 처리**, **막질 적합성/한계**는 여기서 반복하지 않는다.
> 이 노트의 초점은 하나: **원시 트레이스의 특징점(슬로프·변곡·플래토·프린지)을 실제 제거량·
> 잔막두께라는 물리량으로 바꾸는 역산 절차**, 그리고 그 절차의 오차가 오버폴리시 계산에
> 어떻게 들어가는가다.

## 1. 세 신호 계열은 "역산 방식"이 근본적으로 다르다

Lv1-1·Lv2-1에서 확인한 원리 차이는 역산 단계에서 두 갈래로 갈린다.

- **직접측정형(간섭)**: 신호 자체가 두께의 주기함수라, 신호 위상/카운트를 두께로 직접 환산할 수
  있다(§2). 단 절대 원점이 필요하다.
- **이벤트검출형(반사·모터전류·마찰)**: 신호는 "언제 재질이 바뀌었는가"라는 **시각**만 알려주고
  **두께를 직접 주지 않는다**. 제거량을 얻으려면 별도의 **제거율(RR) 모델**을 곱해야 한다(§4) —
  이 경로가 실무에서 가장 흔하지만, RR 자체의 불확실성이 그대로 역산 오차가 된다.
- **와전류**: 원리상 두께를 직접 준다고 알려져 있으나(Lv1-1·Lv2-1), 공개 문헌에서 정량 교정식을
  확보하지 못했다 — §6에서 정직하게 그 한계를 표기한다.

## 2. 간섭 프린지 카운팅 — 상대 제거량은 무모호, 절대 두께만 모호

Lv2-1 §2는 간섭 신호가 $\lambda/2n$ 주기의 사인함수라 **단일 파장으로는 초기 두께를
$\lambda/2n$ 이내로만** 안다고 정리했다. 그런데 US 4,293,224(IBM, 1981)는 서론에서
모호성의 조건을 더 정확히 나눈다[1]:

> "it is well known to determine or control the absolute thickness of a deposited film ... by
> counting the number of cycles in the optical interference signal, **starting when the film being
> deposited has zero thickness**. The same technique has been applied to monitoring decreasing film
> thicknesses, **but in this case the initial film thickness may not be known accurately enough** to
> determine absolute thickness unambiguously."[1]

즉 **모호성은 "절대 두께"에만 있고 "상대 변화량(=제거량)"에는 없다** — 증착처럼 두께 0에서
카운팅을 시작하면 사이클 수 자체가 곧 절대 두께이듯, CMP 연마도 **일단 카운팅을 시작한
시점 이후의 사이클 수는 그 이후 제거된 두께를 정확히 준다**. 문제는 "카운팅을 시작하는
순간의 잔막 두께"(=절대 기준점)를 모른다는 것뿐이다. 이것이 Lv2-1이 다룬 모호성(절대
두께 결정 문제)과 이 노트가 다루는 역산(제거량 추적 문제)의 정확한 경계다.

**역산 절차:**
1. 극값(peak/valley) 카운트 $N$을 실시간으로 누적한다.
2. 누적 제거두께 $\Delta d = N \cdot \dfrac{\lambda}{2n} + \delta$ — $\delta$는 마지막
   미완료 반주기의 부분위상(신호값을 $\pm1$로 정규화한 뒤 $\arccos$ 등으로 환산, 0~반주기
   범위의 분해능 한계를 가짐).
3. 잔막 두께 $d(t) = d_0 - \Delta d(t)$를 얻으려면 **여전히 절대 초기두께 $d_0$**가 필요하다
   — 이것이 US4293224가 두 파장을 도입한 이유다: 두 사이클 길이의 비 $m{:}m{+}1$을 쓰면
   합성 신호의 반복주기가 $m$배로 늘어나(Lv2-1 §2·§5의 0.15/0.25 µm 예시가 이 확장의 구체
   사례), 그 늘어난 범위 안에서 $d_0$ 자체를 무모호하게 결정한다[1]. 일단 $d_0$가 확정되면
   그 뒤로는 위 카운팅만으로 실시간 잔막을 추적한다.

**반사(면적분율) 신호는 이 카운팅이 원리상 불가능**하다는 점도 명확히 해둔다 — Lai(2001) eq(6.10)의
$R=A_f R_{Cu}+(1-A_f)R_{Oxide}$(Lv2-1 §3)는 **단조 감소**(Cu 면적분율이 줄어들며 반사율이
한 방향으로만 이동)이지 주기함수가 아니므로, 카운팅으로 두께를 얻는 이 절이 성립하는 것은
**투명 유전막의 간섭 신호에 한정**된다.

## 3. 신호특징점 → 물리량 대응표

| 특징점 | 어느 신호에서 관측 | 물리적 의미 | 역산 가능한 것 |
|---|---|---|---|
| 프린지 극값(peak/valley) | 광학 간섭(투명막) | 두께가 $\lambda/2n$ 변화 | 누적 제거두께 $N\lambda/2n$ (§2) |
| 슬로프(기울기) 급변 | 모터파워[2] | 계면 마찰계수 전이 개시 | 전이 개시 시각 $t_1$만(두께 아님, §4) |
| 1차 변곡점 | 광학 반사[3] | Cu 면적분율 감소 개시(배리어 노출 시작) | 전이 개시 시각(§4) |
| 2차 변곡점 | 광학 반사[3] | Cu 대부분 제거 완료, 신호 재평탄화 | 전이 완료 시각 → 오버폴리시 기산점(§5) |
| 플래토(평탄 구간) | 모든 계열 | 단일 재질 벌크 연마 진행 중 | **신호로는 제거량 정보 없음** — 이 구간의 제거량은
  오직 §4의 시간×RR로만 안다(신호 자체는 "변화 없다"는 것만 알려줌) |
| PauTa 3σ 이탈 시점 | 광학(통계적 후처리)[3] | 노이즈 범위를 벗어난 재질 전이 | 전이 시각(임계값 기반, Lv1-2 §2a) |

이 표의 핵심 관찰: **"두께"를 직접 주는 특징점은 프린지 극값 하나뿐**이다. 나머지(슬로프·
변곡·PauTa 이탈)는 전부 "시각(time)" 정보이고, 그 시각을 실제 제거두께로 바꾸려면 §4의
제거율 모델이 반드시 개입한다.

## 4. 이벤트 기반 역산 — 시각 → 제거량 (Preston 모델 결합)

모터전류·마찰·반사 계열은 §3에서 본 것처럼 "전이 시각" $t_{ep}$만 준다. 실무 역산은
Preston 방정식([[../cmp/preston-luo-dornfeld-mrr]] §1, $\dot h = K_p P V$)으로 얻은 제거율
$RR$을 그 시각에 곱하는 것이다:

$$\text{제거량}(t_{ep}) = RR \cdot t_{ep}$$

이 환산의 정확도는 전적으로 $RR$의 정확도에 달려 있다 — $RR$이 압력·속도·슬러리·패드
컨디션에 따라 흔들리는 현상론적 상수([[../cmp/preston-luo-dornfeld-mrr]] §1의 $K_p$ 논의)이므로,
**이벤트 기반 역산은 간섭 카운팅(§2)보다 근본적으로 더 큰 불확실성을 갖는다** — 두께를 "재는"
것이 아니라 "시간과 알려진 속도로부터 추정"하는 것이기 때문이다.

Li et al.(2017)이 보고한 필터 지연 실험(Lv1-2 §3)이 마침 이 환산의 좋은 예다 — 대칭 평균
필터는 전이 시작을 183초에, 인과적(과거값만) 필터는 189초에 검출했다고 보고한다[2]. 같은
논문이 명시한 제거율 $RR=229$ nm/min(다운포스 3 psi)[2]을 그대로 곱하면 두 검출 시각에
대응하는 제거량을 각각 얻을 수 있다 — 이는 Lv1-2가 계산한 "초과제거량"과 달리, 이 노트가
새로 수행하는 **절대 제거량 역산**이다(§7 Block A에서 재현).

## 5. 오버폴리시 계산 — 총 제거량 예산

검출 시각 $t_{ep}$에 곧바로 공정을 멈추지 않고 추가 시간 $t_{op}$(오버폴리시)를 더하는
이유는 두 가지 서로 다른 오차원 때문이다.

**(a) 신호 지연 오차 — 이미 일어난 전이를 늦게 본다.** Lv1-2 §3이 정량화한 필터 지연
$T\approx4.94$s(121점/12.15Hz 조건)에 $RR=229$ nm/min을 곱한 초과제거량 $\approx18.8$
nm[2]는 사실 "검출이 실제보다 항상 늦다"는 오차의 하한이다 — 이 지연분은 오버폴리시가
아니라 이미 **검출 시각 자체에 숨어 있는 오차**다.

**(b) 안전마진 — 아직 오지 않은 잔류를 미리 대비한다.** Tian et al.(2023)은 2차 변곡점(§3)
검출 후 "완전한 금속 제거를 보장하기 위해" 별도의 오버폴리시 시간 $t_{op}$를 추가한다고
명시하지만 구체 초 단위 값은 원문에 없다(미기재)[3]. 대신 같은 논문은 **저다운포스 단계
진입 시 남겨두는 목표 잔막**을 수치로 준다 — "reserved copper layer thickness during the
low downforce polishing stage is usually between 1000 Å and 2000 Å"[3]. 이 100~200 nm는
공정이 **의도적으로** 남겨 저속 구간에서 정밀 제어하는 여유 두께이지, 신호 오차의 산물이
아니다.

**총 제거량 예산:**

$$\text{총 제거량} = RR \cdot t_{ep} + RR \cdot t_{op}$$

여기서 $RR\cdot t_{op}$는 (a)+(b)를 합친 것이지만, §7 Block B에서 보이듯 **(b)의 규모(100~
200 nm)가 (a)의 규모(~19 nm)를 압도**한다 — 즉 실무 오버폴리시 시간 예산은 필터 지연보다
"저다운포스 잔막 관리" 같은 공정설계상의 의도적 여유가 지배적이며, 신호처리를 아무리
정교화해도 (a)만 줄어들 뿐 (b)는 없어지지 않는다. 이는 Lv1-2 §4가 정리한 "디싱은
오버폴리시 시간뿐 아니라 패턴밀도·슬러리·컨디셔닝에도 좌우된다"는 결론과 같은 방향이다 —
오버폴리시 예산 자체도 신호처리 하나로 결정되지 않는다.

## 6. 와전류 역산 — 교정범위는 알지만 교정식은 미확보

Lv2-1 §4에서 확보한 것은 **측정 가능범위**(An et al., 개선 후 550~7000 Å)[4]뿐, "진폭이
두께에 어떻게 대응하는가"를 나타내는 **정량 교정식**은 An et al. 원문에 없다(측정범위·
분해능 개선 수치만 보고, 신호-두께 함수형은 미기재)[4]. 이 노트가 확보한 범위 안에서는
정직하게 다음만 말할 수 있다:

- 와전류는 원리상 진폭이 두께의 (대략 단조인) 함수이므로 **참조 웨이퍼로 만든 교정곡선을
  룩업**하는 방식으로 역산한다는 것이 업계 통념이나, 이를 뒷받침하는 1차 문헌의 함수식은
  **미확보**다.
- 교정범위(550~7000 Å) **밖**에서는 Lv2-1이 이미 정리했듯 "신호가 정확히 형성되지 않는다"[4]
  — 즉 역산 자체가 성립하지 않는 구간이 있다는 것은 확인되지만, 그 실패의 정량적 형태
  (신호가 어떻게 무너지는지)는 미검증이다.

## 7. 정량 재현

```python verify
import math

# ── Block A: 간섭 프린지 카운팅 → 누적 제거두께 (US4293224[1] 원리 + Lv2-1 fringe 상수) ──
n_sio2, lam2 = 1.46, 600e-9
fringe = lam2 / (2 * n_sio2)          # Lv2-1에서 이미 검증한 값(205.5 nm/주기)
assert abs(fringe * 1e9 - 205.5) < 0.5

N = 5                                   # 예시: 실시간 카운팅으로 5개 완전 주기 관측
partial_phase_frac = 0.3                # 마지막 미완료 반주기의 부분위상(예시, 무차원)
removed_by_count = N * fringe + partial_phase_frac * (fringe / 2)
assert abs(removed_by_count * 1e9 - 1058.22) < 0.01
print(f"[A] {N}개 프린지 + 부분위상 {partial_phase_frac} → 누적 제거두께="
      f"{removed_by_count*1e9:.1f} nm (초기두께 d0와 무관하게 '변화량'만 정확)")

# ── Block B: 이벤트 기반 시간→제거량 역산 (Li et al. 2017[2]: RR=229nm/min, t=183/189s) ──
RR = 229.0 / 60.0                       # nm/s, 다운포스 3psi 조건(원문 명시)
t_sym, t_causal = 183.0, 189.0          # s, 원문 명시(대칭 vs 인과적 필터의 전이 검출 시각)
removed_sym = RR * t_sym
removed_causal = RR * t_causal
delta = removed_causal - removed_sym
assert abs(delta - RR * 6.0) < 1e-9
print(f"[B] 대칭필터 검출 t={t_sym}s → 제거량={removed_sym:.1f}nm; "
      f"인과필터 t={t_causal}s → 제거량={removed_causal:.1f}nm; 차이={delta:.1f}nm")

# ── Block C: 오버폴리시 예산 — 필터지연분 vs 저다운포스 잔막마진(Tian 2023[3]) 규모 비교 ──
over_removed_filter = 18.8              # nm, Lv1-2 §5에서 이미 검증된 값(재사용, 재유도 안함)
reserved_thickness_low = 1000 * 0.1     # Å→nm, Tian et al. 저다운포스 잔막 하한(1000 Å)
reserved_thickness_high = 2000 * 0.1    # Å→nm, 상한(2000 Å)
assert reserved_thickness_low > over_removed_filter
assert reserved_thickness_high > over_removed_filter
ratio = reserved_thickness_low / over_removed_filter
print(f"[C] 필터지연 초과제거={over_removed_filter}nm vs 저다운포스 잔막마진="
      f"{reserved_thickness_low:.0f}~{reserved_thickness_high:.0f}nm "
      f"(마진이 지연분의 {ratio:.1f}배 이상 — 오버폴리시 예산은 마진이 지배)")
print("ALL PASS")
```

재현 결과: (A) 프린지 카운팅 공식이 자기 일관되게 작동함을 확인 — $N$과 부분위상만으로
초기두께 없이 **변화량**을 얻는다(절대 잔막을 얻으려면 §2의 $d_0$가 별도로 필요, 이 계산은
포함하지 않음). (B) 동일 제거율(229 nm/min[2])을 다른 검출 시각(183초 vs 189초, 같은
원문[2])에 곱하면 각각 698.5 nm / 721.4 nm의 절대 제거량이 나오고, 차이 22.9 nm는 정확히
$RR\times6$초와 일치한다 — Lv1-2가 "초과제거량"으로만 다룬 것을 이 노트는 "절대 제거량
역산"으로 확장했다. (C) 필터지연 초과제거(18.8 nm, Lv1-2 §5 재사용)는 저다운포스 잔막마진
(100~200 nm[3])의 1/10.6~1/5.3 규모밖에 안 돼, 마진 쪽이 5.3~10.6배 압도적으로 커서 §5에서
주장한 "오버폴리시 예산은 신호지연보다 공정설계 마진이 지배한다"는 정성적 결론을 수치로
뒷받침한다.

## 8. 확인 못 한 것

- **US4293224의 정확한 부분위상 분해능**: 특허는 "peak location uncertainty ±F of a cycle"라는
  일반형과 $m_1, m_2, R$을 쓰는 조건식을 제시하지만, $R$의 정의 수식(원문 `##EQU1##`로 도식
  처리되어 OCR 텍스트로 복원 불가)은 **미확인**이다. §2·§7 Block A의 부분위상 처리는 이
  노트가 일반적인 사인파 위상 로직으로 구성한 예시이며, 특허가 제시하는 구체 $F$ 값이나
  실측 분해능은 인용하지 않았다.
- **와전류 교정식**: §6에서 명시했듯 진폭↔두께의 함수형을 주는 1차 문헌을 확보하지 못했다.
  find_open_access.py로 "Thickness Measurement Based on Eddy Current Sensor With Coaxial
  Double Coil for CMP"(IEEE Trans. Instrum. Meas., DOI 10.1109/TIM.2022.3204104)를 찾았으나
  OA 경로가 없고 미러 사이트 미러도 응답하지 않아 **원문 미확보**로 인용에서 제외했다.
- **모터전류/마찰 전이 시각의 절대 정확도**: §4·§7 Block B는 Li et al.(2017)이 보고한 **검출
  시각**(183s/189s)을 그대로 썼다 — 그 시각이 "실제 물리적 전이 시각"과 얼마나 가까운지
  (전이 자체의 물리적 폭)는 별도 문제이며 이 노트가 검증한 것이 아니다.
- **오버폴리시 시간의 실제 초 단위 값**: Lv1-2 §6과 동일하게, Tian et al.은 "일정 기간"이라고만
  하고 구체 값을 주지 않는다. §5·§7 Block C는 대신 "잔막 목표치"(1000~2000 Å)를 규모 비교의
  대리 지표로 썼음을 분명히 한다 — 이것이 실제 오버폴리시 **시간**과 직접 등치되지는 않는다.

## 출처

1. US 4,293,224, "Optical system and technique for unambiguous film thickness monitoring",
   IBM Corp., 등록 1981-10-06. https://patents.google.com/patent/US4293224 (본문 확인:
   FreePatentsOnline 미러 https://www.freepatentsonline.com/4293224.html — "counting the
   number of cycles... starting when the film... has zero thickness" 서론 문단, peak
   uncertainty 조건식 문단 직접 확인. Lv2-1에서 이미 인용한 특허의 **다른 문단**을 이 노트가
   새로 인용). 특허(가중 0.9).
2. H.K. Li, X.C. Lu, J.B. Luo, "Motor Power Signal Analysis for End-Point Detection of Chemical
   Mechanical Planarization", *Micromachines* 8(6):177 (2017), doi:10.3390/mi8060177, PMC6190379
   (오픈액세스, `papers/pmc6190379-motor-power-epd.xml`; RR=229nm/min, 검출시각 183s/189s —
   Lv1-2에서 이미 확보한 수치를 이 노트가 새 계산(절대 제거량 역산)에 재사용).
3. F. Tian, T. Wang, X. Lu, J. Guo, "Endpoint Detection Based on Optical Method in Chemical
   Mechanical Polishing", *Micromachines* 14(11):2053 (2023), doi:10.3390/mi14112053, PMC10673209
   (오픈액세스, `papers/pmc10673209-optical-epd.xml`; §5.2 "reserved copper layer thickness ...
   1000 Å and 2000 Å" 직접 확인 — Lv1-2·Lv2-1이 인용한 절과 다른 절).
4. H. An, E. Kim, S. Oh, T. Kim, "Development of Eddy Current Sensor for End-point Detection in
   sub-Micron scale during Cu CMP", NCCAVS user-group 확장초록(Sungkyunkwan Univ.).
   https://nccavs-usergroups.avs.org/wp-content/uploads/2023/01/P10-HAn.pdf (본문 확인:
   `papers/an-nccavs-eddy-current-epd-submicron-cu.pdf` — Lv2-1과 동일 출처 재인용, 측정범위
   수치만 재사용하고 교정식은 §6에서 명시하듯 원문에 없음을 확인).
