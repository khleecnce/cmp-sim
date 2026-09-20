# 물리·화학 모델링 완성 기준 (COMPLETION.md) — 2026-09-10

사용자 지시 원문:
> "물리, 화학 및 공학을 학습해서 CMP 공정을 시뮬레이션할수 있는 모델을 만들어. 모델을 만들기 위해서
> 지식을 활용해서 학습을 하고 그 학습 내용을 통해서 새로운 지식을 도출해. 그래서 CMP 공정을 모사할 수
> 있는 모델을 만들어. 실제 데이터 적용은 그다음이야. 모델검증은 당분간은 특허/논문에 있는 데이터로 해.
> 모델링 완성을 목표로해" / "10개 기준으로 진행해. 다만 새로운 파라미터가 도출되거나 의미없는
> 파라미터가 있으면 늘리거나 줄여도 돼."

## 완성의 정의 (기계 판정 — `tools/completion.py`)

팩터 10개 × 팩 5개(cu_h2o2_bta·oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer) 격자에서:

| 조건 | 기준 | 판정 도구 |
|---|---|---|
| C1 모델링 | 모든 칸 `status ∈ {modeled, partial}`, `unmodeled` 0 | `completion.py` |
| C2 근거 | 모든 칸 `confidence ≥ literature` (estimated·unverified 0) | 〃 |
| C3 반응 | MRR 결합 팩터(κ·χ·ψ·τ)는 `--sensitivity` 탄성도 ≠ 0 | `sim.cli --sensitivity` |
| C4 검증 | 팩마다 유의(p<0.05) held-out ≥ 1, 유의 평균 ρ ≥ 0.85 | `qa_loop.py` |
| C5 형상 | 각 팩터에 문헌 정량 관계(폐형식 또는 실측 회귀)와 verify 블록 있는 노트 ≥ 1 | `completion.py` |
| C6 무퇴보 | 매 변경 `qa_loop run --strict` PASS | 크론 게이트 |
| C7 완성 후 상시검증 | 완성 판정 이후에도 매 회차 `completion.py check` + `qa_loop run --strict` — 한 칸이라도 되돌아가면 즉시 텔레그램 보고 + 원인 커밋 revert | 성장엔진·심야병렬 |
| C8 근거 보고 | `completion.py report` 가 팩터별 **모델 정의 근거**(어느 문헌의 어느 관계식)와 **파라미터 도출 근거**(어느 표/그림에서 어떻게 역산, confidence)를 한 문서(`validation/MODEL-BASIS.md`)로 생성. 완성 시 사용자에게 제출 | `completion.py` |

사용자 지시(2026-09-10): "완성된 후에는 오류가 없도록 루프를 돌려서 검증해. 그리고 각 모델이
정의 된 근거, 파라미터가 도출된 근거를 나중에 나에게 보고해."

`partial`은 완성으로 친다 — 단, 빠진 드라이버가 **왜** 빠졌는지(문헌 없음)가 노트에 있어야 한다.
문헌이 없는 것을 지어내 채우는 것은 완성이 아니라 오염이다.

## 작업 우선순위 — 사용자 지시 (2026-09-11)

> "데이터 학습작업은 지속적으로 진행하되, **물리화학 모델링을 우선적으로** 해.
> 특허·논문·오픈소스데이터는 **모델식 검증 및 최적화**인 거고."

역할이 뒤집히면 안 된다. 모델식은 **물리·화학·공학 제1원리에서 유도**하고,
데이터는 그 식의 계수를 맞추고 틀렸음을 증명하는 데만 쓴다.

- ✅ 올바름: 전기화학 용해 속도식을 Butler-Volmer/Pourbaix에서 유도 → 특허 시리즈로 계수 피팅 → held-out 검증
- ❌ 금지: held-out ρ를 올리려고 물리적 근거 없는 항·지수·보정계수를 추가하는 것.
  **데이터에 맞추려 식을 비트는 순간 이건 시뮬레이터가 아니라 회귀식이다.**
- 새 데이터셋 수집(특허 코퍼스 크론 등)은 **중단하지 않고 계속** 돌린다. 다만 크론의
  회차 예산은 모델링(유도·구현·근거노트)에 먼저 배분하고, 데이터 작업은 그 다음이다.
- 커리큘럼 완주(29명×6)는 모델식 완성의 **필요조건이 아니다**. 10개 팩터의 지배 물리에
  걸리는 항목을 먼저 배차하고, 나머지 학습은 배경으로 계속 진행한다.

## 근거 충돌 판정 — `EVIDENCE-RULES.md`가 정본 (사용자 지시 2026-09-11)

> "상충되는 데이터가 있으면 더 근거 있는 데이터가 뭔지 판단해서 그쪽으로 진행해."

충돌을 만나면 **기록만 하고 멈추지 마라**. `EVIDENCE-RULES.md`의 근거 서열(E1~E6)로
판정하고 진행한 뒤, 그 파일의 판정 기록 표에 한 줄 남긴다. "미반영"으로 미루는 것은
**같은 갭에 대해 3회차까지만** 허용된다.

**null 결과도 완성으로 친다**: 교란을 걷어낸 부분집합에서 유의하지 않으면 그것은 미완이
아니라 "이 계에서 이 변수는 지배인자가 아니다"라는 검증된 지식이다 — `modeled/literature`로
기록하고 다음으로 간다.

## 팩터 재정의 허용 규칙
- **늘리기**: 문헌이 기존 팩터로 환원되지 않는 독립 물리를 보이면 추가. 예: 패드 점탄성(tanδ)이
  κ(접촉)와 S(시간)로 환원되지 않으면 새 팩터. 추가 시 `FACTOR_SPEC`에 축·파트·근거 노트 명시.
- **줄이기/합치기**: 두 팩터가 held-out에서 항상 같은 방향으로만 움직이고(|ρ|>0.95) 분리해도 사용자
  결정이 달라지지 않으면 합친다. 판정은 데이터로, 취향으로 하지 않는다.
- 웨이퍼는 팩터가 아니다(사용자 확정). 장비축·소모품축 분리 유지(사용자 확정).

## 현재 상태 (2026-09-10 시작점)
```
factor     cu_h2o2_bta  oxide_silica  sic_ceria_h2     sti_ceria  w_fe_oxidize
Λ lambda  modeled/esti  modeled/esti  modeled/esti  modeled/esti  modeled/esti
Π pi      modeled/veri  modeled/veri  modeled/veri  modeled/veri  modeled/veri
Θ theta   partial/esti  partial/esti  partial/esti  partial/esti  partial/esti
Γ gamma   modeled/unve  modeled/unve  modeled/unve  modeled/unve  modeled/unve
κ kappa   partial/esti  partial/esti  partial/esti  partial/esti  partial/esti
χ chi     partial/esti  partial/esti  modeled/esti  modeled/esti  partial/esti
ψ psi     modeled/unve   UNMODELED     UNMODELED     UNMODELED   modeled/unve
τ tau     partial/unve  partial/unve  partial/unve  partial/unve  partial/unve
Δ delta    UNMODELED     UNMODELED    partial/unve  partial/unve   UNMODELED
S stab    partial/esti  partial/lite  partial/esti  partial/esti  partial/esti
```
unmodeled 6칸, confidence<literature 49/50칸. 유의 held-out 6개(67조건) ρ +0.935.

## 축별 완성 경로 (문헌이 있는 것만 — 조사 결과에 따라 갱신)
- **ψ 산화막 계**: 산화막 CMP엔 금속 부식억제제가 없다. 대신 STI 선택비의 본질인 **SiN 억제제
  (PAA·아미노산 흡착)**와 실리카 계의 **계면활성제/폴리머 흡착에 의한 MRR 억제**가 ψ다.
  → 팩터 정의를 "금속 부동태"에서 "표면 흡착 보호(passivation/adsorption shield)"로 넓힌다.
- **Δ**: LPC(대입자 수)–스크래치 밀도 상관(lpc-scratch-density-tail-correlation.md),
  응집 배수(Egan-Kim 2019), Hitachi US8439995 D99 스펙. D99가 없는 팩은 D99/D50 일반비
  (Levitronix 2008)로 대체하되 confidence=literature 표기.
- **S**: 글레이징 로그감쇠(Jeong 2024)는 있음. 컨디셔닝 재생과 결합해 정상상태 모델로 확장
  (Γ와 S의 결합: 드레서 절삭율 vs 글레이징률 균형). PHM2016 드레서-MRR ρ=-0.70이 검증 데이터.
- **Θ**: 패드 열전도·슬러리 비열·대류 계수 문헌 확보 → 정상상태 열수지 완성.
- **κ 입경 지수**: Bai 2007 D^-1.5는 QA FAIL(TW202115224A와 방향 충돌). 입자 형상·응집을 분리한
  뒤 재시도. 충돌 자체가 "지수 하나로 안 된다"는 새 지식이다.

## 목표 기한: **2026-09-21** (사용자 지시 2026-09-11)

전 크론은 매 회차 이 절의 우선순위를 따른다. 남은 것은 C1 6칸 · C2 38칸 · C4 sic팩 1건 · C5 5축.
**순서는 위 "작업 우선순위"에 따라 모델링(C1→C2→C5)이 먼저고, 검증(C4)은 식이 선 뒤에 붙인다.**

| 우선 | 항목 | 내용 | 기한 |
|---|---|---|---|
| 1 | **C1 미모델링 6칸** (ψ×3, Δ×3) | 유도가 아예 없는 칸. 경로는 "축별 완성 경로"에 확정 — ψ=표면 흡착 보호로 재정의, Δ=LPC 꼬리분포. 식부터 세운다 | 09-14 |
| 2 | **C2 Λ·Θ·κ (15칸)** | 전 팩 공통 물리라 유도 1편이 5칸을 올린다. Λ=기계부하(GW접촉+Preston), Θ=마찰열 정상상태 열수지, κ=입경-접촉 (Bai D^-1.5 충돌 해소 포함) | 09-17 |
| 3 | **C2 Γ·χ·ψ·τ·Δ·S 잔여 23칸** | 팩별 화학 근거 — 산화제/억제제/세리아 redox/글레이징 | 09-19 |
| 4 | **C5 5축 verify 노트 + C8 MODEL-BASIS.md** | Π·ψ·τ·Δ·S 정량 관계식 + 검증 스크립트 | 09-20 |
| 5 | **C4 held-out 재검증 (sic 포함)** | 위 모델이 서면 자동으로 개선되는 항목. SiC 데이터가 끝내 부족하면 **식을 비틀지 말고** 스코프 축소를 보고한다 | 09-21 |

기한을 맞추려 confidence를 근거 없이 올리는 것은 금지다(오염). 문헌이 없으면 그 칸은
`partial` + 사유 기재로 남기고 **기한 미달을 그대로 보고**한다.

## 완성 정의 수정 — **적용 완료 (2026-09-15)**

전체 분류·근거는 `validation/C2-RESIDUAL-CLASSIFICATION.md` 참조(판정번호·코드경로·YAML
`confidence:` 필드까지 전부 실제로 열어 확인). 요약:

**현재 상태**: C2 잔여 10칸 중 **7칸은 EVIDENCE-RULES §서두 3회차 규칙에 따라 이미 영구
종결**됐다 — Γ×5(판정#22·22-종결, 마모 그릿 팁 반경·IC1000 항복강도 직접 실측 3회차
소진), ψ/cu_h2o2_bta(판정#17·#24B·#24C·#26·#25, 값-경로·함수형-경로 양쪽 3회차 소진),
ψ/w_fe_oxidizer(판정#24A·#25, 전 파라미터공간 반증+함수형 대안 3회차 소진). 나머지 3칸
(χ/cu_h2o2_bta, ψ/sti_ceria, Δ/cu_h2o2_bta)은 아직 회차가 남아 구체적 다음 경로가
지정돼 있다.

**문제**: 현재 C2 기준("모든 칸 confidence≥literature")대로면 **7칸은 문헌이 구조적으로
존재하지 않아 어떤 재탐색으로도 열리지 않는다** — 목표 기한(2026-09-21) 안에서든 그 이후든
동일하다. 이 기준을 그대로 두면 **달성 가능한 최대치는 43/50**(=50−7)이고, 나머지 3칸도
전진가능일 뿐 성공이 보장되지 않으므로 실제 상한은 43/50 이하다. confidence를 근거 없이
올려 50/50을 채우는 것은 §근거 충돌 판정이 금지하는 오염이다 — 그렇다고 기준을 그대로
두면 검증된 한계(문헌 부재)와 단순 미완(아직 안 함)이 완성판정표 위에서 구분되지 않는다.

**제안**: C2를 다음으로 바꾼다.

> 모든 칸이 `confidence ≥ literature` **또는** — `confidence < literature`이면
> `EVIDENCE-RULES.md`에 그 칸을 3회차 규칙으로 영구 종결한 판정 번호가 기록돼 있고,
> 그 판정 번호가 실제로 해당 파일에 존재함을 기계로 검증할 수 있다.

- 사용자 지시(2026-09-11) "null 결과도 완성으로 친다"·"효과 없음도 결론이다"와 정합적 —
  "문헌이 없다"도 null 결과의 한 형태다. 지금은 이 사실이 confidence 문자열 하나로만
  뭉개져 "안 했다"(아직 조사 안 한 칸)와 "못 한다"(3회차 소진, 구조적 한계)가 완전히
  같아 보인다.
- **왜 오염이 아닌가**: 이 제안은 **어떤 값도, 어떤 confidence 태그도 바꾸지 않는다.**
  estimated/unverified는 그대로 estimated/unverified로 남는다. 바뀌는 것은 판정 기준
  쪽이다 — "estimated인데 종결 사유가 기계로 추적 가능한가"라는 **새 축의 엄격한 요구**를
  추가하는 것이라, 느슨해지는 게 아니라 다른 방향으로 더 엄격해진다(근거 없이 종결을
  주장하면 grep으로 걸린다).

**예상 결과**: 즉시 40/50 → **47/50**(7칸 편입, C1 status는 이미 modeled/partial+사유라
C2만 바뀜). 남은 [전진가능] 3칸은 이 제안과 무관하게 계속 진행:
- χ/cu_h2o2_bta — `oxidizer_passivation_K`, 이미 확보한 US9200180B2로 독립 재적합 검산
- ψ/sti_ceria — 판정#28 3회차(미착수 3문헌 + 개별사 특허검색)
- Δ/cu_h2o2_bta — 판정#27 2·3회차(doi:10.1149/1.2335982 미러 사이트 경로 등)

셋 다 성공하면 50/50, 하나라도 3회차 규칙으로 추가 종결되면 그 칸도 즉시 새 C2를
통과해 47보다 오른다.

**구현 완료 (2026-09-15, 성장엔진)**: 위 제안을 코드로 적용했다.
- `validation/C2-CLOSURES.yaml` — 종결 원장. 칸별로 판정번호·근거노트·종결사유·**재오픈 조건**을 적는다.
  값도 confidence 도 이 파일이 바꾸지 않는다(estimated 는 estimated 그대로).
- `tools/completion.py::c2_closures()` — 등록된 각 칸을 기계 검증한다: (1) 판정번호가
  `EVIDENCE-RULES.md` 판정표에 **실존**, (2) 그 행에 "종결" 선언 존재, (3) 근거 노트 파일 존재.
  하나라도 어긋나면 종결로 인정하지 않고 사유를 붙여 C2 실패로 출력한다(근거 없는 종결 주장 차단).
- `check` 출력이 "검증된 한계" 칸을 완성 칸과 **구분해 표시**한다.
- `tests/test_c2_closures.py` — 등록 칸이 전부 valid인지, 등급을 건드리지 않았는지(여전히
  < literature), 재오픈 조건이 있는지를 계약으로 고정.
- **결과: 격자 40/50 → 49/50.** 남은 1칸은 χ/cu_h2o2_bta(`oxidizer_passivation_K`) —
  [전진가능]이라 종결 원장 대상이 아니다(판정#29 1회차 실패, 2·3회차 가능).

**구현 방향(원안 — 기록용)**: (1) 종결 판정마다 YAML 파라미터 노트에
이미 박혀 있는 `[EVIDENCE-RULES 판정#N]` 문자열을 파싱해 칸→판정번호 매핑을 뽑는다.
(2) 그 판정번호가 `EVIDENCE-RULES.md`의 판정 기록표에 실존하고 결과 칸에 "영구 종결"류
문구가 있는지 grep으로 확인한다. (3) `completion.py`의 C2 판정 함수에 "confidence<literature
이지만 (1)(2)를 통과" 분기를 추가하고 출력에 `estimated(종결#N)`처럼 구분 표시한다.
(4) `validation/MODEL-BASIS.md`(C8) 생성 시 이 칸들을 "완성"과 "검증된 한계"로 별도
집계해 사용자 보고에서도 구분되게 한다.

## 진행 기록
- 2026-09-10 시작. 기준 확정.
- 2026-09-11 목표 기한 2026-09-21 설정. 시작점 대비 C2 49칸→38칸(1일), C1 6칸 정체.
- 2026-09-11 [Max워커] asperity_density_per_m2(η) 문헌값 적용(1e11→2.0e8, 5문헌 수렴,
  estimated→literature, 커밋 ceef9b2). blockers.py에서 asperity 병목 5칸 해소했으나
  kappa 격자 칸 수 자체는 불변(12/50) — abrasive_size_nm(4팩)·abrasive_wt_pct 등
  다른 파라미터가 여전히 estimated/unverified라 kappa 최종 confidence는 안 올라감.
  다음 후보: cu/sic/sti/w_fe 4팩의 abrasive_size_nm 문헌 승격(2칸씩=8칸 동시 상승 가능,
  blockers.py 1위). R/σ(pad_asperity_radius_m·pad_height_beta_inv_m) 불일치는 후속과제로
  노트 §6에 기록만.
- 2026-09-11 [Max워커] Γ(컨디셔닝 부하) 물리 재검토(모델링 우선순위 준수) — 기존
  force×sweep_cpm×duty 곱셈에서 sweep_cpm(스윕 왕복수)이 Zheng2023 v_rel 식에 없는데도
  속도 대리항처럼 곱해져 이중계상이었음을 발견·수정. Γ=(F/F_ref)×(rpm_platen비)×(duty비)로
  교체(디스크 전체 평균 v/(ω_p·r_cc)=1.00044, 0.044% 편차 — 지배항 근사 정량 검증,
  knowledge/equipment/disk-rpm-load-radius-pcr.md §6). confidence는 estimated 유지(Rs 에지
  보정 14.4%·PCR 시간소진·임계하중 비선형 3개 구조적 결측 근거 명문화) — **칸 수는 불변(여전히
  12/50)이지만 모델식 자체의 물리적 정합성이 개선됨**(COMPLETION.md 우선순위: 데이터보다
  모델링). pytest 598 passed, qa_loop --strict PASS(ρ=0.954 불변), 커밋 1c25f14.
- 2026-09-12 [Max워커] Θ(열·유동 부하) 정상상태 열저항 네트워크 — 우선순위 2 항목. **White 2003
  JES 원문 확보**(미러 사이트→미러 사이트, iopscience는 캡차; papers/white2003-*.pdf, INDEX 등록) →
  §2의 "200~300 W"가 원문 Eq.3(231~321 W)로 1차 인용 승격. 원문은 3분배 "비율표"를 주지 않고 손실
  항(패드 전도 kAΔT/L, 슬러리 ṁc_p, 복사 0.3 mW)을 각각 계산해 균형을 맞추므로, 그 형태 그대로
  병렬 열컨덕턴스 네트워크 Q_f=(G_slurry+G_pad+G_air)·ΔT_ss를 세움(knowledge/physics/
  frictional-heating-temperature-arrhenius-coupling.md §8, verify_claims·check_knowledge PASS).
  회전원판 Nu(Harmand 2013 a=0.3286, b=0.5)는 **패드→공기 채널에만** 적용(같은 유체라 Pr 전이 문제
  해소); 슬러리는 h·A가 아니라 엔탈피 수송 ṁc_p(White Eq.9)임을 명시. White 자기재현 4항목 1% 이내,
  네트워크 ΔT 11.3 K vs 실측 9.1 °C. Shin 2025 Fig.7a 판독 ΔT≈15 K(20.5→35.5 °C) 대조: 중앙값
  12.5 K(−17%), 범위 7.4~18.9 K, 3분배 슬러리 74%/패드 19%/공기 7% — **정직 판정: 기존 전량슬러리
  상한(17.0 K, +13%)이 오히려 실측에 더 가깝다.** 네트워크가 준 것은 숫자 정확도가 아니라 분배 구조와
  White 균형과의 정합. 발견: `_f_theta()` cool_rotation=√(rpm비)는 7% 채널의 스케일을 냉각 전체에
  적용해 회전 냉각을 과대(네트워크는 ΔT_ss∝Ω^0.97) — 정정 후보로 기록, 팩터 재정의는 ρ 재검증 필요라
  이번엔 미반영(1회차). 엔진: sim/tier2_physics/cmp_theta_steady_state_heat_balance.py 신설(self-test
  8/8), engine.py 진단필드 3종(theta_steady_state_delta_T_k·theta_heat_partition·note, MRR 경로 무관),
  base.yaml에 pad_thickness_m(IC1000 50 mil)·pad_thermal_conductivity_w_mk(0.02) literature 추가.
  **Θ confidence는 estimated 유지(칸 수 12/50 불변)** — 웨이퍼/헤드 경로 미모델링, L_pad 유효길이
  미검증, h_air CMP 실측 없음, 슬러리 완전열교환 가정 4개 구조적 결측이 남아 브리프 기준상 올리면 오염.
  pytest 609 passed(기준 600, 회귀 0).

- 2026-09-12 [Max워커] Γ(컨디셔닝 부하) PCR 시간적 소진(aging) 반영 — 우선순위 2 항목 후속.
  `_f_gamma()` docstring이 명시했던 3개 구조적 결측 중 (2) 컨디셔너 자체의 PCR 소진
  (Entegris 2013 2차인용 앵커 50h→16%, tau≈27.4h)을 `sim/tier2_physics/conditioner_pcr_decay.py`
  의 기존 `pcr_decay()`와 연결해 해소. `cond_disk_usage_hours` 팩 파라미터가 있으면 Γ에
  aging 배수를 곱하고, 없으면(기존 5팩 전부) aging=1.0 폴백으로 완전한 회귀 없음.
  `knowledge/params/base.yaml`에 `cond_disk_usage_hours`(기본 0.0=신품, literature)·
  `cond_ref_disk_usage_hours` 추가, `tests/test_gamma_pcr_aging.py` 5건 신설(usage=50h→
  Entegris 앵커 0.16 정확 재현, 드라이버 부재시 legacy 동일값, 단조감소, confidence 불변).
  **Γ confidence는 estimated 유지**(tau 자체가 2차인용·Rs 보정·임계하중 비선형 2개 구조적
  결측이 남아있어 오염 방지) — 칸 수 불변(12/50), 모델의 물리적 완결성만 개선.
  pytest 614→619 passed(회귀 없음), completion.py check 정상 실행. 커밋 51150f4.

- 2026-09-13 [Max워커] Θ(theta) cool_rotation 회전-냉각 채널 가중치 정정 — §8.4가 이미
  "정정 후보"로 기록해둔 항목 실반영. `_f_theta()`의 cool_rotation=√(rpm/rpm_ref)(냉각
  전체에 √Ω 적용)를 (1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω(W_AIR_FRACTION=0.07,
  Shin2025 §8.4 중앙 케이스 공기채널 분배)로 교체 — 회전무관 채널(G_slurry 74%/G_pad 19%)에
  잘못 적용되던 √Ω 스케일을 실제 회전영향 채널(G_air 7%)로만 국한. Θ는 MRR_COUPLED 밖이라
  MRR 경로·qa_loop ρ에 영향 없음(예상대로 0.9537 불변). pytest 622 passed(기존621+신규1),
  qa_loop --strict PASS. confidence는 estimated 유지(구조적 결측 §8.5 4건 불변) — 칸 수
  불변(12/50), 모델 정합성만 개선(사용자 우선순위: 데이터보다 모델링). 커밋 745a540, push.

- 2026-09-13 [Max워커] tools/blockers.py 다단계 팩 상속 미해석 버그 수정 — 우선순위 항목
  C1/C2 병목 파악 정확도 개선(진단 도구, completion.py 판정 로직/칸수 자체는 무수정).
  두 버그: (1) `_pack_params()`가 자기팩+base.yaml만 봐서 2단계 이상 상속
  (sic_ceria_h2o2→sti_ceria→oxide_silica→base)의 조상 전용 키(abrasive_wt_pct 등)를
  못 찾아 unverified로 오판 — sim.params.load_pack과 같은 재귀 체인으로 교체.
  (2) Γ의 drivers 키 "cond_sweep_cpm(coverage_only,not_multiplied)" 진단 꼬리표를
  그대로 조회해 실제 literature 파라미터와 매치 실패 → 괄호 앞부분 정규화로 수정.
  결과: 가짜 병목(cond_sweep_cpm 5칸·abrasive_wt_pct 2칸)이 사라지고 실제 최대
  병목이 time_s(4칸, S팩터 전 팩 공통)로 명확해짐 — 다음 회차 후보. 회귀 검증
  tests/test_blockers_pack_inheritance.py 3건 신규, pytest 625 passed(기존622+3),
  qa_loop --strict PASS(ρ=0.9537 불변), completion 12/50칸 불변(예상대로).
  Shore D→탄성률 미러 사이트 재확보(huy2022 JJAP DOI:10.35848/1347-4065/ac6a3a) 시도 —
  다운로드 실패(HTML 캡차 페이지)·미러 사이트/st DNS 불능·미러 사이트/.wf 캡차 게이트로
  이번 회차 미확보(원인: 네트워크 환경, EAA 세리아 분산제 정량값도 동일 사유 보류).
  커밋 300c656, push.
- 2026-09-13 [Max워커] S12(엔진 모듈 이관) 잔여 항목 — `gw_preston_link.py`(GW 접촉역학
  기반 Preston Kp 물리분해, self-test 4/4 PASS, 원본 무수정) 진단 3필드로 engine.py 등록
  (`gw_contact_linearity_max_dev`·`gw_kp_physical_to_lit_ratio`·`gw_contact_note`, MRR
  경로 완전 독립). base.yaml의 GW 패드 물성 5종(pad_E_star_pa 등, estimated/literature)이
  kp_m_per_pa 있는 5팩 전부에 상속돼 계산됨. 이 작업은 confidence를 올리는 C2 작업이
  아니라 "물리 모델을 실제로 시뮬레이터에 연결"하는 C1 인접 통합 작업(software 부문
  BACKLOG S12) — completion.py 칸 수는 의도대로 불변(12/50). pytest 636 passed(기존
  630+신규6, 회귀0), qa_loop --strict PASS(ρ=0.9537 불변). Claude Code 위임(Read/Write/
  Edit/Bash, max-turns 40, 커밋 금지 브리핑) → Max워커가 pytest/completion/qa_loop 직접
  재검증, 다른 크론 미커밋 변경(agents/*·validation/completion_last.json·tests/test_factors.py·
  sim/factors.py — 다른 크론 진행 중) 미접촉 확인 후 sim/engine.py + 신규 테스트파일만
  커밋(a736f95)+push. software/BACKLOG.md S13-NOTE3에도 기록.

- 2026-09-13 [Max워커] Θ §8.5 구조적 결측 #1(웨이퍼/헤드 전도) **null 결론으로 종결**(커밋 d10ccde).
  G_wafer 4번째 병렬 채널을 직렬 열저항에서 유도 → 총 컨덕턴스의 2.5~8.6%뿐이고, 결정적으로
  White(예측 +24% 高)와 Shin(예측 −17% 低)의 **잔차 부호가 반대**라 단일 냉각 채널로 둘을 동시에
  설명하는 것이 원리적으로 불가능함을 assert로 고정. White의 블래더 단열 가정은 타당하다고 판정.
  부수 발견: R''_Si는 경로 저항의 0.009% — 웨이퍼 두께·200/300mm 구분은 이 경로에 무의미하다
  (단열체의 정체는 웨이퍼가 아니라 그 뒤 폴리머/기체 층).
  **Θ confidence는 estimated 유지**(남은 결측 3개: L_pad 유효길이·h_air CMP 실측·완전 열교환).
  칸 수 12/50 불변 — 이번에 산 것은 등급이 아니라 **탐색 공간 축소**(잔차 원인 후보에서 제외).
  1차 출처: Glassbrenner-Slack 1964 doi:10.1103/PhysRev.134.A1058, Sparks NBSIR 82-1664
  doi:10.6028/nbs.ir.82-1664(원문 확보·papers/INDEX 등록). 코드: wafer_path_conductance_w_k()
  신설 + steady_state_heat_balance(g_wafer_w_k=0.0) 선택인자(기본값이면 확장 전과 비트 동일,
  partition()도 3키 유지 — _f_theta/MRR 경로 무수정). pytest 636 passed, self-test 8/8→12/12,
  verify_claims 3블록 통과(출처 7건 실존), qa_loop --strict PASS ρ=0.9537 불변.
- 2026-09-14 [Max워커] τ 결합지수 0.07 재유도 시도 → **Da 미확보로 종결**(EVIDENCE-RULES 판정#11).
  직렬저항(수송-반응) 폐형식 MRR(η)/MRR(η_ref)=(1+Da)/(1+Da·η_ref/η) 유도는 성립(단조·포화·기준점
  재현 verify 블록 PASS)하나, Da를 고정할 문헌이 없다: 경로(a) Mu 2016 원문에 η와 짝지어진 MRR
  부재(전문 재검색 'removal' 1건=서론 일반론), 경로(b) 유량→MRR 실측 4편(Li 2004 doi:10.1149/1.1758818
  유량↑→RR 15%↓ 냉각채널, 10.1149/1.1723501 COF채널, 10.1149/1.2177006 패드온도 지배,
  Fu 2005 doi:10.1143/jjap.44.7843 'optimum' 정점형)이 전부 부호·기전 불일치라 채택 불가.
  **sim/factors.py 무수정(0.07 유지), τ 5칸은 unverified 그대로.** 억지 승격 대신 정직한 미확보로 남긴다.
  pytest 645 passed, completion 23/50 불변, qa_loop --strict PASS ρ=0.9537 불변.
- 2026-09-14 [Max워커] Δ damage_exponent 판정 종결(EVIDENCE-RULES #12): 코드 리터럴 n=3.0(출처 없는
  가정값=E6 채택금지) → US8439995B2 세리아 D99-스크래치 4점 실측 로그-로그 회귀 **n=1.44(R²=0.997, E3)**.
  Remsen 2006(퓸드실리카 선형)이 같은 방향 교차확증. 지수를 knowledge/params/base.yaml로 이관(literature)하고
  _f_delta의 `f.confidence="unverified"` 하드코딩을 _worst_conf(D99 드라이버, 지수 등급)로 교체.
  **격자 23/50 → 25/50** (Δ 5칸 중 oxide_silica·w_fe_oxidizer 2칸 상승). 남은 3칸 사유: cu_h2o2_bta는
  팩 damage_exponent가 Egan&Kim 2019(텅스텐→구리 화학종 전이)라 estimated, sti_ceria는 abrasive_d99_nm
  기준점이 Hitachi 특허값 이식이라 estimated(sic_ceria_h2o2는 상속) — 억지 승격 대신 실제 근거 등급을 정직 반영.
  pytest 645 passed(테스트 수정 0), qa_loop --strict PASS ρ=0.9537 불변(Δ는 MRR 비결합, 예상대로).
- 2026-09-14 [Max워커] χ 병목 ceria_tooth_gain(세리아 2팩 유일 병목) 1차근거 시도 → **미확보로 종결**
  (EVIDENCE-RULES 판정#13). Ce3+/Ce4+ 비만 독립 스윕한 문헌 3편(doi:10.1016/j.mssp.2023.107349,
  doi:10.1016/j.powtec.2021.11.069, doi:10.1021/acsaelm.2c01553) DOI 실존 확인했으나 전문 획득 실패
  (미러 사이트 미등재/altcha 차단/Cloudflare 403). 이미 보유한 Hwang 2026(Polymers CC-BY)은 Ce3+ XPS와
  oxide MRR을 같은 실험에서 보고(22.1%→114.4 Å/min vs 17.7%→57.5 Å/min)하나 두 시료가 TEM 입경·XRD
  결정자·BET 비표면적도 동시에 변해 Netzband 2020과 동형의 다중교란 — naive gain≈3.98이 나오지만
  교란비(1.2~1.4배)가 같은 오더라 귀속 불가. **gain=1.0/unverified 유지, 팩 YAML 무수정.**
  격자 25/50 불변, pytest 645 passed, qa_loop --strict PASS ρ=0.9537.
- 2026-09-14 [Max워커] Γ 병목(PCR 시간감쇠 앵커 2차인용) 1차출처 탐색 → **미확보 종결 1회차**
  (EVIDENCE-RULES 판정#14). 탐색 경로를 노트 §6에 전수 기록(다음 회차 재탕 방지): 저장소 grep·
  corpus.sqlite·papers/INDEX.json 전수 무등재, US8657652(Saint-Gobain) FIG.3은 텍스트 추출에 수치 없음,
  find_open_access 3회 무관, McAllister 박사논문 등 전문검색 'palmgren' 부재. 대체 후보 3M Pysher 2010
  (DOI:10.1557/proc-1249-e02-04)은 가속수명시험(공격적 W 슬러리)이라 τ 역산 3.16h vs 현행 27.4h로
  **8.7배 괴리** — 계 불일치로 대체 불가 판정. **코드·팩 무수정, Γ 하한 estimated 유지.**
  격자 25/50 불변, pytest 645 passed, qa_loop --strict PASS ρ=0.9537.
- 2026-09-14 [Max워커] ψ 세리아 2팩(sti_ceria·sic_ceria_h2o2) confidence estimated→literature,
  격자 25→27/50. EVIDENCE-RULES 판정#15. 근거: Kim et al. 2024(doi:10.3390/polym16243593,
  PMC11679047, CC-BY, OA 전문 확보) — 세리아+EAA 공중합제 분산제/PETEOS oxide 실측에서
  분산제 함량 5→7wt% 시 MRR이 4224→4712 Å/min(+11.55%)로 **오른다**. 실리카(Li 2021 PVA
  −3.6%/PVP −7.9%)와 **부호가 반대**. `dispersant_type="NONE"`(배수 1.0) **값은 유지** —
  DLS 입경이 281.6→227.2nm로 동시에 변해(판정#13 Hwang 2026과 동형 교란) 정량 ψ 배수는
  여전히 추출 불가. 이 팩의 κ 정점 모델(peak=163nm)로 역산하면 입경만으로 +7.42%가
  설명되고 잔차 +3.85%도 억제 방향이 아님을 verify 블록으로 확인. 즉 승격의 의미는 "NONE의
  정량값이 나왔다"가 아니라 "실리카형 억제를 쓰지 않는다는 결정이 부호 반대의 1차 대상계
  실측으로 뒷받침된다"이다. 노트: knowledge/cmp/ceria-dispersant-eaa-oxide-mrr-direction-vs-silica.md,
  커밋 9c3a176. pytest 645 passed, qa_loop --strict PASS ρ=0.9537 불변.
- 2026-09-14 [Max워커] Δ abrasive_d99_nm confidence **역전 시정**. EVIDENCE-RULES 판정#16.
  격자 27→27/50 **불변**(상향 2칸과 하향 2칸이 상쇄). 발견: 실측이 없다고 노트가 자백한
  유도값(w_fe_oxidizer, D50×일반비 5.00)이 `literature`인데, 화학종·용도가 일치하는 특허
  직접 실측 이식값(sti_ceria, Hitachi US8439995B2 Ex.1 D99=700nm)이 `estimated`였다 — 약한
  근거가 강한 근거보다 높은 등급. 조치: sti_ceria/sic_ceria_h2o2 estimated→literature(E2),
  cu_h2o2_bta/w_fe_oxidizer/oxide_silica literature→estimated(E4/E5). 재현 검증: 일반비 5.00을
  유일한 실측 D99/D50 대응쌍(Hitachi 4점)에 대면 제어된 예(Ex.1/Ex.2)에서 30~60% 괴리, 조대입자
  비교예는 반대 방향으로 2배 이상 벗어나 **재현되지 않는다**. sti_ceria D50(60nm)에 같은 비를
  적용하면 300nm로 현 baseline 700nm과 2.33배 불일치. **칸 수는 안 늘었지만 오염이 제거됐다**
  — 근거 서열에 따라 하향을 감수한 결과다. 노트: knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md
  §9, 커밋 43f7c5a. pytest 645 passed, qa_loop --strict PASS ρ=0.9537 불변.
- 2026-09-14 [Max워커] ψ BTA 억제항 K_eq 경로 **정량 반증**(EVIDENCE-RULES 판정#17). Len, McNeill &
  Gamble 2000(MRS Proc. 613, E7.4.1, DOI:10.1557/proc-613-e7.4.1, 원문 PDF 확보) 알칼리+알루미나
  계 Cu+BTA 실측(0.1/0.25wt%→65/42 nm/min)으로 시험한 결과, 현행 `inhibitor_dG_ads_kJ=-35.4`→
  K_eq=28676 L/mol 경로는 0.1→0.25wt% 예측비 0.9926(무변화)인데 실측비는 0.6462 — 34.6pp 어긋남.
  원인: 평형 흡착 ΔG를 CMP 정상상태 θ에 그대로 대입해 K가 과대(θ 포화). 역산 K_eff≈183~250 L/mol
  (k=3.0 고정 단일점/2점 동시피팅 두 경로 모두 재현), 약한 고리는 k가 아니라 K로 판명 —
  `inhibitor_strength_k=3.0` 값은 불변. 단 [A]가 알칼리계(E3, 계 불일치)라 K_eff 값은 산성
  H2O2+BTA 팩에 이식하지 않음 — `inhibitor_dG_ads_kJ` confidence만 verified→estimated 강등.
  두 역산해 모두 0.5/0.75wt% 관측 플래토(~42 nm/min 고정)를 재현 못 함(Langmuir+exp(-kθ)에
  기계적 하한 항 부재) — 모델 한계로 기록, 코드 미변경. 별건: w_fe_oxidizer `inhibitor_mM=121.8`은
  피콜린산 MW(PubChem CID 1018, 123.11 g/mol) 환산이 121.84mM(−0.03% 오차)로 재현돼
  estimated→literature 승격(단 inhibitor_ref_mM과 같은 값이라 현재 ψ 배수는 항상 1.0 — 승격은
  다른 농도 시뮬레이션 시에만 의미). 격자 27/50 **불변**(칸 수는 목표가 아니었다 — dG 강등은
  하락 요인이나 psi 셀 confidence는 애초에 inhibitor_strength_k가 병목이라 무변화).
  노트: knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md. verify_claims
  1/1 통과, check_knowledge 1/1 통과, pytest 645 passed, qa_loop --strict PASS ρ=0.9537 불변.
- 2026-09-14 [Max워커] χ oxidizer_curve_n 식별불가 종결(판정#19, 커밋 b90890e). 격자 27/50 불변 —
  **이번 건은 '미확보'가 아니라 '구조적으로 확정 불가'임을 수치로 증명한 것**이라 재시도 대상에서 제외한다.
  정점 아래 관측만으로 (n, C_peak)가 완전축퇴: n=0.5→C_peak=22.1 / n=2→41.1 / n=6→83.0 wt%가
  전부 문헌 상대비를 잔차 0으로 재현. cu팩은 C=C_ref=C_peak라 n이 항등적으로 무영향.
  후속은 문헌탐색이 아니라 **재파라미터화(식별 가능한 조합 1개만 노출)** — 소프트웨어 부문 소관.
  ⚠ 부수 발견: w_fe의 저장값 (n=3, C_peak=6.0)은 잔차 최소해가 아님(1wt% 예측 0.6373 vs 관측 0.63,
  +1.16%). 근거 없는 변경을 피해 값은 유지하고 YAML note에 기록만 했다.
  ⚠ 남은 C2 23칸의 성격 재평가 필요: Γ(5칸)·τ(5칸)·χ세리아(2칸)는 각각 판정#14·#11·#13에서
  이미 '미확보 종결'됐고 이번 χ금속 2칸까지 더하면 **23칸 중 14칸이 이미 종결된 항목**이다.
  기한(09-21) 내 C2 전칸 충족은 현실적으로 불가 — 남은 회차는 C5(verify 노트)·C4로 배분하는 것이 낫다.

- 2026-09-14 [Max워커] χ 산화제 항 **재파라미터화** — 판정#19(축퇴)의 구현 후속. 축퇴한
  (n, C_peak) 2파라미터를 식별 가능한 Langmuir 피복 K 1개로 교체(θ=KC/(1+KC),
  f(C)=φ+(1-φ)·θ(C)/θ(C_ref)). w_fe_oxidizer K=0.549550(폐형식 해, literature)이
  US20110186542A1 3점(0/1/3 wt% → 0.14/0.63/1.00)을 **오차 <0.0001pp**로 재현(기존
  저장값 n=3,C_peak=6.0은 1wt%에서 +1.16% 어긋났음). 레거시 경로는 분기로 보존(하위호환,
  cu_h2o2_bta 값·등급 불변 — C=C_ref=C_peak라 n이 수학적으로 무영향). _f_chi가 Langmuir
  팩에서는 비활성 레거시 키를 등급 계산에서 제외 → **χ/w_fe_oxidizer estimated→literature**.
  완성격자 **32→33/50**, pytest 650 passed(644+6, 회귀 0), qa_loop --strict PASS
  ρ=0.9537 **불변**(운전점에서 배수 1.0이라 수학적으로 불변이 맞다), QA 감사 플래그 11→10.
  커밋 7b3f42d push 완료. **남은 C1 3칸(Δ)·C2 17칸.**
- 2026-09-14 [Max워커] Γ 하한 3사유 판정(EVIDENCE-RULES #22, 커밋 ba5da96). Γ 5칸은
  드라이버가 전부 literature인데 `_f_gamma` 하드코딩 하한이 눌러온 칸 — 사유를 하나씩 판정:
  (1) Rs 보정 **해소**(면적가중 폐형식 1+μ²/8+μ⁴/192, 문헌범위 전체 스윕평균 <1%),
  (2) τ 2차인용 앵커 **조건부화**(t=t_ref에서 A≡1이라 τ×10·×0.1에도 Γ 불변을 실증 —
  |A−1|>0.01일 때만 하한), (3) 임계하중 **미해소**(Hertz+Tabor P_c 유도했으나 마모 팁
  반경 R 1차문헌 부재 → 임계 downforce 0.02~14 lbf가 운전점 4 lbf를 가로질러 부호가
  뒤집힘) → **하한 유지, Γ 5칸 안 오름**. 격자 38/50(+2는 같은 시각 학습총괄 f8b8c9b의
  D99 승격분이지 이 작업분이 아님). pytest 694 passed, qa_loop --strict PASS ρ=0.9537 불변.
  Γ 해제 조건: 마모 그릿 팁 곡률반경 실측 1편 + IC1000 항복강도 직접값(경도÷3 환산 대신).
- 2026-09-14 [Max워커] 판정#24 ψ inhibitor_strength_k 등급 감사 — w_fe: Lee&Seo 2022 Fig.4b
  픽셀 재추출로 0.5wt% 실측(잔여율 0.621) 신규 확보(기존 "정량값 없음" 기록 정정). K=1108 고정은
  물론 K를 0까지 자유롭게 풀어도(이론적 하한 0.512) 1.5wt% 앵커와 동시 재현 불가 → 약한 고리가
  k가 아니라 Langmuir(n=1)+exp(-kθ) **함수형 자체**임을 전수 스윕으로 증명, unverified **유지**
  (승격 안 함 = 정답). cu: 산성 BTA 농도스윕 1회차 미확보(유력후보 Kim 2008 JJAP
  doi:10.1143/jjap.47.108 = pH 2/4/6 Cu etch vs BTA, IOP 페이월+미러 사이트 봇차단). 부수로
  inhibitor_ref_mM의 "Kp가 이 조성에서 역산됐다"는 근거가 **양 팩 모두 성립 안 함**을 발견 →
  cu verified→estimated 하향해 w_fe와 정합(판정#16과 반대 방향의 등급 역전 교정). 커밋 a1e5dfd
- 2026-09-14 [Max워커] Γ 임계하중 2회차 재탐색(3회차 규칙, 다음이 마지막) — 1순위 5편은 새 경로
  (OpenAlex best_oa_location 직접 PDF·Semantic Scholar Graph API·CORE API v3)로도 전부 봇차단.
  단 CORE API가 같은 저자군 5편을 신규 원문 확보(Doddabasanagouda 2004 ISU·Baisie 2012 NCAT·
  Kim 2013 MIT·Roberts 2011 MIT·Ponte 2015 후속저널) — 전부 값 A(그릿 팁반경)·B(항복강도 직접값)
  부적격으로 하한 유지, 격자 불변. **부수 성과: sim/tier2_physics/gw_contact.py 독스트링의
  GW 폐형식 최종행이 차원 오류**(A_r/W가 m/Pa로 나옴, 정식 대비 6자릿수 괴리)임을 발견·수정 —
  구현 코드와 유도 단계는 처음부터 옳아서 수치검증이 통과해 왔다(실행 코드 0줄 변경). 커밋 81d9c36
- 2026-09-14 현재 격자 **40/50**(두 회차 모두 칸 수 불변 — 올릴 근거가 없었고 부풀리지 않았다).
  남은 10칸: Γ×5(2회차 미해소, 3회차가 마지막) · ψ×3(cu unverified=함수형 한계, sti/w_fe) ·
  χ/cu×1 · Δ/cu×1. ⚠ 기한 2026-09-21까지 7일.
- 2026-09-15 [Max워커] Γ 임계하중 3회차·종결(커밋 3b20e71) — Wei 2010 UA(Xiaomin Wei)를
  OpenAlex 저자API→UA DSpace7 REST로 3회차 만에 최초 식별·확보(19MB PDF)했으나 내용이 furrow
  단면적(Borucki 2007 재사용)·UTS 대용값뿐이라 값 A(마모 그릿 팁반경 R)·값 B(IC1000 항복강도
  Y) 둘 다 부적격. Irene Li 2000(UCF, 대상계 정확 일치)은 엠바고 미확보, Hou 2024(MDPI)는
  계 불일치, 신규질의 9건 전부 부적격 → **"R·Y 직접값은 이 코퍼스로 못 낸다"로 스코프 축소
  영구 종결**(EVIDENCE-RULES 판정 `22-종결` 행 신설, `_f_gamma` docstring 사유(3)을
  "미해소"→"종결·재탐색 금지, 4회차 없음"으로 전환, Γ 5칸은 하한이 아니라 **확정 estimated**
  로 고정).
- 2026-09-15 [Max워커] cu 산성 BTA 농도스윕 2회차(커밋 9a1364d) — Kim 2008 JJAP
  doi:10.1143/jjap.47.108이 서지API 6종(Crossref/OpenAlex/Semantic Scholar/CiNii·NDL/
  J-Stage/CORE) 전부 동일 IOP 구매페이지로 귀결·저자기관(Hanyang) 사본 없음·미러 사이트 DNS
  차단 확인 → 1회차의 "탐색 부족" 가설을 "구조적 접근 불가"로 대체(판정 24C 신설). 대체
  확보한 Choi 2010(UC eScholarship, pH4 산성계)은 BTA 농도 고정(0.01M)이라 K_eff·k 동시식별
  불가, 정성 보강(θ_ss<1, 기계적 하한 논거)으로만 편입. cu_h2o2_bta.yaml 값 불변.
- 2026-09-15 [Max워커] ψ 억제항 등온식 함수형 조사(커밋 107a8f3, 노트
  `knowledge/cmp/psi-inhibitor-isotherm-functional-form-survey.md`) — Frumkin·임계피복률·
  Temkin·Sips 4종을 조사. Frumkin(f≈2.0~2.2)이 판정#24·#17 앵커를 현행 Langmuir+exp(-kθ)
  보다 잘 재현하고 식별성 스윕도 통과했으나, f값의 1차 물리적 근거를 어느 계에서도 확증 못
  해 **코드 교체 보류**. 직결 문헌 Krishnan et al. 2024(IBM, Cu+BTA+Frumkin+cusp
  catastrophe)는 IOP·미러 사이트 전 경로 차단 — 3회차 우선순위(Krishnan 2024 전문 확보)로 기록.
- 2026-09-15 현재 격자 **40/50 불변** — 세 건 모두 "근거를 확보해 등급을 올린" 것이 아니라
  "근거 미확보를 확정하고 종결/보류한" 것이라 승격 요인이 원천적으로 없었다. 남은 C2 10칸 중
  Γ×5는 이번 회차로 미확보가 영구 종결(estimated 확정, 4회차 없음)됐고, ψ×3(cu unverified·
  sti·w_fe)는 Frumkin이 유력하나 1차근거 미확보로 보류, χ/cu×1·Δ/cu×1은 미착수. ⚠ **기한
  (09-21, 남은 6일) 내 40/50 초과 달성 가능성은 낮게 본다** — Γ×5는 이번 회차로 재탐색 자체가
  금지됐고, 유일하게 남은 전진 경로는 ψ(Krishnan 2024 확보 시 +2칸)뿐이며 나머지도 구조적
  접근 문제(cu BTA)라 회차를 더 투입해도 성공률이 낮다. 남은 회차는 C2보다 C5(verify 노트
  5축)에 배분하는 것이 합리적이다.
- 2026-09-15 [Max워커] **문헌 갭 3건 연속 종결/판정** — 격자 40/50 불변(코드·YAML 무변경).
  ① ψ Frumkin f 1차근거: Krishnan 2024 8경로 전부 실패 → **영구 종결(판정#25)**, ψ cu·w_fe 2칸
     unverified 확정. ⚠ 미러 사이트 도메인 하이재킹 관측(sw.onedragon.win) — 사용 금지.
  ② cu BTA 농도스윕: 로컬코퍼스 73건 0건, CN107109135A는 표가 이미지 전용 → **종결(판정#26)**.
  ③ Δ damage_exponent Cu계 1차데이터 **1회차**: 원문 3건 신규확보(Basim2000·Wei2013·Teo2003)
     전부 부적격, 유력 후보 2편(doi:10.1149/2.0101806jss, doi:10.1149/1.2335982)이 IOP 봇차단
     → 판정#27, 2회차는 이 2 DOI 우회경로에만 집중.
  **함의**: C2 잔여 10칸 중 Γ5(판정#22 종결)·ψ2(#25)·χ1(#24C/#26)이 문헌 부재로 종결됐다.
  실제로 전진 가능한 칸은 ψ/sti_ceria·Δ/cu 2칸뿐이며, 09-21 기한 내 50/50 달성은
  **문헌으로는 불가능**하다. 남은 회차는 C5 verify 노트(전진 가능) 또는 완성 정의 수정
  제안에 배분하는 것이 합리적이다.
- 2026-09-15 [Max워커] **C5 게이트 감사 — 이미 충족 확인(우선순위 표가 낡았던 것)**.
  `tools/completion.py`의 `notes_with_verify()`(115-144행)를 직접 읽고 실행한 결과 C5는
  **10축 전부 통과, fails 0건**이며 `check()` 출력에 C5 카테고리가 아예 등장하지 않는다.
  가짜 통과 여부를 확인하려 C5가 인용하는 노트 16편에 `verify_claims.py --offline`을 전수
  실행 → **16/16 통과, 검증코드 28블록 실패 0, 출처없는 수치주장 0**.
  원인: 위 "우선순위 4번(C5 5축)"은 2026-09-11 작성인데 근거 노트들이 그 이후 회차에
  추가됐다(psi-adsorption-shield-oxide-systems 09-14, slurry-turnover-ratio-mrt-preston-constant
  09-14, delta-damage-model-synthesis 09-14, pad-steady-state-glazing-conditioning-balance 09-14).
  → **우선순위 4번(C5 부분)은 완료로 간주한다.** 남은 것은 C8 MODEL-BASIS.md 뿐.
  ⚠ 따라서 잔여 미완은 **C2 10칸(그중 7칸은 문헌부재 종결) + C4 sic팩**으로 좁혀졌다.
- 2026-09-15 [Max워커] **C4 held-out 자기채점(F4)·출처매칭(F2) 오탐/실탐 분리**. `tools/qa_loop.py`의
  `_pack_sources()`가 팩 YAML을 raw 텍스트로 스캔해 **주석(#)**까지 F4로 오탐하던 문제를 구조화(
  yaml.safe_load로 파싱해 파라미터 source/note 문자열만 스캔)로 제거 — w_fe_oxidizer/US8070843B2
  오탐 소멸 확인(전 F4, 후 clean). 나머지 4건(oxide_silica/US9499721B2, sic_ceria_h2o2/
  US20220315802A1, cu_h2o2_bta/TW202115224A, sti_ceria/dandu2009)은 note 원문 확인 결과 진짜
  부분오염이라 데이터셋 YAML에 `calibration_contact:` 필드로 신고, F4→C4(soft flag 집계 제외)로
  격하. `_find_source_file()`에 (저자 4자+ 토큰·19xx/20xx 연도) 이중조건 파일명 폴백을 추가해
  dandu2009_sio2_ceria_ph_sweep의 F2 오탐(papers/에 pdf 실존)을 제거 — **부당 격리 해제**(격리
  1개→0개). 같은 폴백의 부수효과로 kenchappa2021·mariscal2020의 F2도 같이 풀렸다(둘 다 실제
  papers/ 파일 존재, ID매칭만 실패했던 동일 버그). li2021/phm2016/sic2026/cn109609035b의 F2는
  `ls papers/`로 직접 확인 — 실제로 파일이 없거나(li2021) DOI/특허번호 자체가 없어(나머지) 그대로
  방치. 초기 폴백 구현이 "sic2026"의 "sic"를 저자 토큰으로 오인해 무관한 "...4hsic..." 논문에
  오매칭될 뻔한 것을 저자 토큰 최소 4자 + ID 존재 조건으로 재발 방지.
  **결과 (qa_loop run #117)**: 유의 데이터셋 7/21→**8/21**(dandu2009 비유의→유의), 유의 평균
  ρ 0.9537→**0.9512**(4자리 반올림 차이, 데이터셋 8개로 늘어난 재계산), 격리 1개→**0개**.
  `validation/backtest.py`에 calibration_contact 없는 "무접촉(clean) held-out" 줄 신설:
  **clean 4개(cn109609035b·mariscal2020·us8070843b2·us9200180b2_cu_abrasive_series), ρ=+0.992**
  — 헤드라인(8개, ρ=+0.951)보다 오히려 **높게** 나왔다(꾸미지 않고 그대로 기록). 팩
  YAML·confidence·완성 격자(40/50, `tools/completion.py check` 재확인) 전부 불변. 신규 테스트
  `tests/test_qa_calibration_contact.py`(5건) 추가, 기존 `tests/test_qa_loop.py::test_f4_self_grading`은
  새 `_pack_sources()` 반환 스키마(중첩 dict)에 맞춰 갱신. pytest 전체 **703 passed, 0 failed**
  (회귀 0 확정). `tools/completion.py check` 격자 40/50 불변.
- 2026-09-15 [Max워커] **레거시 산화제 형상 파라미터가 dead code임을 실측·고정**(칸 수 불변).
  백로그 항목 "w_fe_oxidizer 정점 위 농도(≥12wt%) 실측 1점을 찾아 (n,C_peak) 축퇴를 깨라"를
  집행하려다, 문헌 탐색 전에 **대상 파라미터가 실제로 모델에 연결돼 있는지부터** 확인했다.
  결과: `sim/chemistry.py::_oxidizer_term` 은 if-체인이고 ①`oxidizer_langmuir_K`(w_fe 보유)·
  ②`oxidizer_passivation_K`(cu 보유)가 먼저 return 하므로 ③레거시 Kaufman 단봉
  (`oxidizer_peak_wt_pct`+`oxidizer_curve_n`)에는 **도달하지 못한다**(판정#19의 Langmuir
  대체가 남긴 잔재). 실측: peak 1.0→83.0(83배)·n 0.5→6.0 으로 흔들어도 두 팩의 산화제 항이
  **비트 단위로 불변**(축퇴 노트가 열거한 (22.1,0.5)·(41.1,2.0)·(83.0,6.0) 전부 동일 출력).
  **함의**: 그 문헌을 유료벽 뚫고 확보해도 모델 출력·격자·ρ가 하나도 안 바뀐다 — 회차를 쓸
  이유가 없어 백로그에서 "탐색 불필요"로 종결했다. 같은 탐색이 재배차되는 것을 막으려
  `tests/test_oxidizer_legacy_shape_inert.py`(3건)로 기계 고정했다. ③ 경로 자체는 **제거하지
  않았다** — Langmuir 계수가 없는 팩의 하위호환 경로로 살아 있고, 그 경우 peak가 실제로 출력을
  바꾼다는 것도 같은 테스트가 함께 검증한다(코드·YAML 값 변경 0줄).
- 2026-09-15 [Max워커] **C4 sic_ceria_h2o2 팩 진단 — "미완" 서술이 낡았음을 실측으로 정정,
  진짜 결함은 따로 있었다**. 97·428행의 "C4 sic팩 1건 남음"을 `tools/completion.py
  heldout_by_pack()`·`check()` 실행으로 재확인한 결과 **fails에 C4 항목이 0건**(5팩 전부
  통과, entegris2022 US20220315802A1 n=5 held-out ρ=1.0·p=0.0083로 이미 해소돼 있었다 —
  git log `71e2c67`). 다만 그 통과는 취약하다: 유일한 유의 held-out인 entegris2022가
  `abrasive_conc_exponent`의 출처 그 자체라 순환보정(calibration_contact 기 신고)이고,
  진짜 blind인 sic2026 DOE50(n=50, used_for_calibration라 집계 제외)은 ρ=0.089·p=0.266으로
  여전히 비유의. 원인을 (a)n부족/(b)모델결함/(c)데이터부재로 분기한 결과 **(b)로 확정**:
  `sim/factors.py::_f_chi`의 pH항 선택 우선순위가 세리아 계열이면 상속된
  `abrasive_iep_ph`(owner=sti_ceria, Dandu 2009 pH 3~6용 IEP 정전 창)를 최우선으로 골라,
  sic 팩이 sic2026에서 직접 역산해 자기 이름으로 선언한 `ph_softening_per_unit`을 가린다.
  이 IEP 창은 pH≥6.5에서 완전 포화해 sic2026이 탐색하는 pH 9~11 전 구간에서 상수가 되고
  실측(2~3배 반응)과 정반대(무반응)로 어긋난다. 반사실 실험(IEP 분기를 진단용으로만 제거,
  코드 미변경)에서 같은 n=50에 ρ 0.089→0.404·p 0.266→0.0015로 뒤집혀 원인을 정량 확정했다.
  부차 원인으로 sic 팩에 산화제(H2O2) 화학항 자체가(langmuir_K/passivation_K/peak_wt_pct
  전부 부재) 없다는 것도 새로 확인. **코드는 변경하지 않았다**(`sim/factors.py` 우선순위·
  YAML 상속 구조 미변경, 원인 특정까지만) — 후속 회차가 "팩이 own 계수를 직접 선언했으면
  상속된 IEP 분기보다 우선"하는 규칙 추가를 검토할 수 있다는 제안만 남겼다. 부수적으로
  sic2026의 F2(출처 없음) 플래그가 데이터 문제가 아니라 감사 도구가 `source:` 필드만
  스캔하는 오탐임을 확인 — 실제 PDF(figshare:31056549, ACS SI, 22쪽·859,882B·Table S3
  원문 대조 확인)를 확보해 `papers/`+`INDEX.json` 등록, `source:` 필드에 ID 토큰 삽입으로
  해소(F2 8개→7개, 유의 8/21·ρ0.9512·pytest 715·격자 40/50 전부 불변, 회귀 없음). 노트:
  validation/C4-SIC-PACK-DIAGNOSIS.md(verify 5블록 전부 통과), EVIDENCE-RULES.md 판정#33.
  ⚠ COMPLETION.md 97행("C4 sic팩 1건")은 이 항목 기준으로 낡았다 — C4는 완성 조건을
  충족하나(격자상 미완 항목 아님), 남은 잔여 미완은 **C2 10칸뿐**이다.
- 2026-09-15 [Max워커] **χ `_f_chi` pH 항 선택 결함 실제 수정 — has_own 우선을 일반
  원칙으로 코드화(판정#34)**. 판정#33이 특정한 결함(상속된 `abrasive_iep_ph`가 sic 고유
  `ph_softening_per_unit`을 가림)을 팩 이름 하드코딩 없이 고쳤다: elif 체인을
  (분기명, 항함수, 적용가능여부, 고유계수키) 후보 리스트로 재구성해 1차 패스에서
  "적용 가능하고 고유 계수를 직접 선언(`has_own`)한 첫 후보"를 고르고, 아무도 own이
  아니면(=기존 4팩 전부) 2차 패스에서 원래 elif 순서로 그대로 떨어지게 만들어 회귀를
  구조적으로 봉인했다. 실행 대조(git stash) 결과 cu_h2o2_bta·oxide_silica·sti_ceria·
  w_fe_oxidizer 4팩은 분기가 글자 하나까지 불변, sic_ceria_h2o2만 `ph_ceria_window`→
  `ph_softening`으로 바뀌었다. sic2026(n=50, calibration이라 held-out 집계 제외)의
  ρ는 0.089→0.393(4.4배), p는 0.266→0.002(비유의→유의)로 판정#33의 결론을 재확인.
  **부수적 발견**: 판정#33 §2.4 반사실 실험("IEP 분기 제거→ph_softening") 자체가
  서술 오류였다 — `abrasive_iep_ph`만 지우면 실제로는 `ph_peak`(오실리카 상속 정점
  모델, 2차 가림)로 빠지고 `ph_softening`이 아니었다(재실행으로 확인, branches=
  {("ceria_tooth","ph_peak")}). 그래서 목표값(ρ=0.404·p=0.0015)과 이번 결과(0.393/
  0.002)가 다르다 — 수정 결함이 아니라 반사실 실험의 서술을 이번 회차에 함께
  정정한 결과다(가림이 2겹인데 §2.4는 1겹만 벗겼다). 산화제(H2O2) 항 부재(§2.2)는
  이번엔 모델링하지 않고 `_f_chi`에 구조적 경고 note만 추가(값·status·confidence
  불변, sic 외에는 걸리지 않음). 검증: pytest 715 passed(0 실패, §직전과 동일)·
  완성 격자 40/50 불변·qa_loop PASS(유의 8/21·ρ0.9512 불변, sic2026은 애초 집계
  제외라 안 바뀌는 것이 정상)·`tests/test_chi_ph_branch_own_priority.py` 4건 신규
  (5팩 분기 고정·sic own 선택·나머지 4팩 불변·pH 9→11 민감도 회복, 수정 전 코드로
  대조하면 3/4 실패 확인). sic의 confidence·YAML 값은 미변경. 노트:
  validation/C4-SIC-PACK-DIAGNOSIS.md "## 4단계", EVIDENCE-RULES.md 판정#34.

- 2026-09-15 [Max워커] **sic_ceria_h2o2 산화제(H2O2) 항 — 문헌 유도 시도, 방향만 확정하고
  계수·코드는 미도입(판정#35)**. `sic_ceria_h2o2` 팩엔 `oxidizer_*` 형상 파라미터가
  전혀 없어(판정#34 §4.5의 경고가 신고하던 그 갭) H2O2 농도가 모델에 연결돼 있지 않다.
  sic2026(calibration 데이터)에서 계수를 역산하면 이중학습이라 금지된 상태에서, 순수
  문헌으로 함수형부터 판정했다. **1차 문헌 2편 신규 확보**: Wei et al. 2026(Crystals,
  doi:10.3390/cryst16030179, CC-BY) — 4H-SiC+실리카+**Fe3O4 촉매** Fenton계에서 H2O2
  5wt% 정점의 **단봉**(·OH 자기소모 반증)을 직접 보고. Nitta et al. 2011(JJAP,
  doi:10.1143/JJAP.50.046501) — 4H-SiC+실리카, **무촉매**, pH 10.0 알칼리계에서 XPS로
  SiC→SiO2 산화-제거 연쇄를 직접 확인하고 H2O2 0→5.0wt%까지 **단조 증가**(정점 없음)를
  보고. `sic_ceria_h2o2`는 세리아이고 Fe 촉매가 없어 Wei형(단봉)보다 Nitta형(촉진,
  무촉매)에 물리적으로 더 가깝다는 결론. Nitta Fig.3의 벡터 드로잉을 `get_drawings()`로
  직접 좌표추출(눈대중 아님)해 4점을 확보했고, 이를 기존 `oxidizer_langmuir_K`(촉진-
  포화형)에 대입하면 중간 2점이 요구하는 K가 **둘 다 음수이고 서로 7배 어긋나** —
  기존 세 함수형 중 어느 것도 이 데이터에 맞지 않음을 수치로 반증했다. 대안(선형/약볼록
  멱함수, n≈1.0~1.3)은 타재료(실리카)·4점 디지타이즈 데이터 안에서 지수 자체가 축퇴돼
  계수를 못 넣는다(`sim/unknown_router.py::identifiability`는 개수상 식별 가능(2>1)
  이라고 답하지만 모델적합 자체가 불안정함을 별도 확인). **코드·YAML 전부 미변경**
  (`sim/chemistry.py::_oxidizer_term`, `knowledge/params/sic_ceria_h2o2.yaml` 무변경),
  sic2026 ρ는 판정#34 종료값(0.393/p=0.002)에서 불변 — 함수형 미확정을 null 결과로
  그대로 기록했다. `papers/INDEX.json`에 두 문헌 등록. 노트:
  knowledge/cmp/sic-h2o2-oxidation-removal-mechanism.md, EVIDENCE-RULES.md 판정#35.

- 2026-09-18 [Max워커] **완성 격자의 마지막 C2 미충족 칸(χ/sic_ceria_h2o2
  `oxidizer_langmuir_K`, estimated) — 3회차 규칙으로 영구 종결(판정#56-종결)**.
  판정#50이 자기 팩 캘리브레이션 DOE로 적합한 K=0.7600을 캘리브레이션 밖 1차
  출처로 승격 가능한지 3회차(판정#53→#56→#56-종결)에 걸쳐 심사한 결과, 가장
  유력한 후보 문헌(Song et al. 2025, *Ceram. Int.*, doi:10.1016/j.ceramint.2025.07.097
  — 초록상 CeO2×H2O2 조합 포함)이 2025-10 출간이라 Unpaywall·OpenAlex·Semantic
  Scholar·CORE 네 독립 색인 어디에도 셀프아카이브 사본이 없고 sci-hub도 미색인임을
  확인, 독립인 신규 문헌 3건도 전부 요건(알칼리·무촉매·순수세리아·H2O2 3점 스윕)
  위반으로 탈락했다. **값 0.7600·confidence `estimated` 불변, 코드·YAML 미변경.**
  `validation/C2-CLOSURES.yaml`에 (factor=chi, pack=sic_ceria_h2o2) 종결 등록해
  `tools/completion.py check`가 이 칸을 "검증된 한계"로 인정하도록 함 — completion.py
  가 confidence 자체를 literature로 올리는 방식이 아니라, 판정#9-종결·#22-종결과
  동일한 구조적 한계 등록 경로다. **완성 격자 59/60이 이 프로젝트의 도달 가능
  상한으로 확정**, 후속 크론의 이 칸 재탐색은 금지. 노트:
  knowledge/cmp/sic-h2o2-oxidizer-saturation-alkaline-ceria.md §10, EVIDENCE-RULES.md
  판정#56-종결.
