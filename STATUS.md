# CMP-Sim — STATUS

## 🎯 완성 기준 (사용자 확정 2026-09-25) — 이 줄을 매 실행 갱신하라

### 1차 완성 — 모델링 정확도
- **목표: 예측 오차 median ≤ 10.0%** (이력서에 쓸 수 있는 수준)
- **현재: median 19.5% shape / 21.8% LOO** (코퍼스 46/50, 427점) — **891 tests**.
  2026-09-28(5회차): **19.5%의 정체를 분해했다 — 완성 기준 논쟁의 답이 나왔다.**
  `tools/residual_census.py`가 채점된 46개를 원인별로 한 버킷씩 배정한다(반응성은
  선언이 아니라 **실측** — 첫 행을 각 축의 min/max로 재구성해 실제 시뮬레이터를
  돌려 rate가 0.5% 넘게 움직이는지 본다):
  noise_floor(원리적 불가) 3개/59점 26.8% · no_constant(선언된 공백) 4개/14점
  27.7% · **responsive_miss(더 좋은 법칙이 먹히는 유일한 버킷) 35개/342점 20.2%**
  · few_levels 4개/12점 7.1%.
  **결론: ≤15% 완화는 아직 정당화되지 않는다.** 측정점의 80%가 개선 가능한
  버킷에 있으므로 19.5%는 측정 노이즈나 데이터 공백으로 막힌 수치가 아니다
  (테스트가 이 다수성을 assert — 뒤집히면 시끄럽게 실패한다).
  같은 실행에서 **압력 포화 법칙도 반증**(네 번째 법칙 기각):
  `1/RR = 1/(kPV) + 1/RR_chem`(Kaufman 1991)은 팩당 상수 1개를 요구하는데,
  잔차 기울기 중앙값이 **+0.08**(10개 중 음수 5개)이고 **압력대가 겹치는
  데이터셋들이 부호가 반대**다(같은 특허 ep3161098b1의 teos -0.06 vs w +1.04).
  공통 곡률로는 같은 압력에서 반대 부호가 나올 수 없다 → Preston의 P 선형성 유지,
  상수 추가 없음.
  2026-09-28(4회차): **농도 지수의 피팅 상수를 유도식으로 제거했다**(상수 감소).
  `tools/conc_derived_probe.py`로 농도 스윕 18개(r2≥0.5는 16개)를 측정한 결과:
  (1) size축에서 통했던 **재질 가설은 반증** — between/within 1.6x로 사전에 정한
  2x 기준 미달이고, 잘 샘플된 세 재질이 0.04 이내로 **일치**한다(diamond +0.30,
  silica +0.33, ceria +0.34). 대칭성 때문에 재질표를 만드는 것은 금지했고 안 했다.
  (2) 대신 **유도식 m = +1/3**(Li 2021 표면적 지배 / Cook 1990 공급한계, 간극이
  단층만 수용 → n_gap ~ C^(2/3), 입자당 하중 ~ 1/n_gap → MRR ~ C^(1/3), **피팅
  상수 0개**)이 코퍼스 median +0.33과 정확히 일치. 16개 중 13개가 ±0.25 내.
  (3) Langmuir 포화형도 **반증** — 포화라면 스윕 평균농도가 높을수록 기울기가
  떨어져야 하는데 상관계수 +0.06(0.01~9 wt% 범위).
  팩 5개가 각자 피팅했던 값(+0.227/+0.3333/+0.3333/-0.4295/-0.406)이 법칙 1개로
  대체됐다 — **상수를 줄이면서** swap 조합의 농도축이 실수치로 살아났다.
  이견 3건(모두 SiC)은 제외하지 않고 기록했다: 경한 막질에서는 반응층 공급이 아니라
  압입이 율속일 수 있다는 가설(테스트가 "비-SiC 이견이 나오면 실패"로 고정).
  ⚠ 이 과정에서 **잠재 버그 1건을 잡았다**: 기존 withdraw 게이트가 "override가
  하나도 없을 때"만 작동해서, 농도 법칙이 항상 값을 공급하자 게이트가 꺼지고
  **철회된 size축이 null로 떨어져 반증된 유도값 -0.84를 타게 됐다**(diamond 런의
  rate가 10배 입경 변화에 6.8배 움직였다). `solver._abrasive_hook`을 축별 철회로
  고쳤다. 코퍼스 median은 의도대로 불변 — 채점 행은 모두 팩의 reference 연마재다.
  2026-09-27(3회차): abrasive-size 지수를 **팩별 피팅 상수에서 재질 상수로 재귀속**
  (`SIZE_EXPONENT_BY_ABRASIVE`, silica -0.13 k=3 / alumina +0.28 k=2 / ceria +1.00 k=1).
  상수 개수가 줄었다(팩 6개가 각자 피팅 → 재질 3개 공유). 코퍼스 median은 불변이
  **정상** — 이 경로는 팩의 reference abrasive와 다른 연마재를 넣었을 때만 타므로
  코퍼스 행(모두 reference)에는 닿지 않는다. 얻은 것: alumina·ceria로 swap하면
  이전엔 size축이 `withdrawn`(무반응)이었는데 이제 자기 재질의 측정 지수로 움직인다.
  conc축은 여전히 withdraw — 재질간 전이 검증을 안 했으므로 빌려오지 않는다.
  2026-09-27(2회차): abrasive-size 축 측정 완료. 단일 유도 지수는 **반증**(세 번째),
  그러나 산포가 **연마입자 재질로 정리된다**(재질간 0.51 vs 재질내 0.16) — 피팅
  상수를 재질 상수로 재귀속할 근거. 코퍼스 median은 의도대로 불변(측정만 함).
  2026-09-27: pH 유도식 **반증됨**(두 번째). 법칙 기반 kinetic leg를 빼면 오히려
  좋아진다(60.4%→35.3%) — 튜닝 부족이 아니라 항 자체가 틀렸다. 부수효과가 더
  중요: 현행 Gaussian의 11.0%는 **in-sample 보간**이고, leave-one-pH-level-out은
  **52.9%**다. pH축의 공식 25%는 그만큼 뒷받침되지 않는다. 자세한 내용은 NEXT.
  MERGED to main 2026-09-27, **863 tests pass**.
  `python tools/score_report.py` (scores) / `python tools/readme_numbers.py`
  (every number the README claims) — both inside `.venv`.
  Absolute-scale misses >3x: **13 -> 9**; the four largest silica misses were ONE
  extrapolation artefact, not four physics gaps. Shape median deliberately
  UNMOVED at 19.5% — a pure scale factor divides out of the shape metric, so a
  moved shape would have meant a bug.
  ⚠ 인터프리터: `source .venv/bin/activate` 먼저. 시스템 python3에는 pint가 없다.
- **10%가 물리적으로 불가능하다고 판단되면 15%까지 허용**(사용자 승인 2026-09-25).
  단 그 판단은 **근거를 STATUS.md에 적고** 나서만 인정된다 —
  "어렵다"가 아니라 "무엇이 남은 오차의 하한을 만드는가"를 써라.
  측정 재현성 자체가 N%라면 그 아래로는 물리적으로 못 내려간다는 식의 논증.
- 문헌에 데이터가 없어 못 푸는 BLOCKED(나노인덴테이션·SnAg Preston 등)는
  **완성의 조건이 아니다.** 기록만 하고 넘어간다.

### 2차 완성 — 모델이 적용된 시뮬레이터 (1차 후 착수)
1차 모델링이 끝나면 **그 모델이 실제로 도는 시뮬레이터**를 만든다.
3D는 **실제 폴리셔처럼 보이게 매우 정교하게**. 입력은 부품을 클릭해서 한다:

| 부품 | 입력 |
|---|---|
| **wafer cart / loading** | wafer 종류 선택 (film stack) |
| **operation 화면** | 공정 조건 (pressure, rpm, flow, time, temp) |
| **슬러리 공급장치** | 슬러리 formulation (abrasive 종류·입경·농도, pH, 산화제, 첨가제) |
| **polishing unit** | Pad, conditioning disk 선택 |

입력 → **1차에서 만든 물리 모델이 계산** → MRR·불균일도·결함 출력.

**UI 언어 = 영어**(사용자 확정 2026-09-25). 라벨·버튼·단위·툴팁·에러메시지·
축 이름 전부 영어. 한글 금지. 실제 팹 장비 UI가 영어이고 포트폴리오 대상도
영어권이다. 현재 `cmp_sim/web/` 한글 0건 — 이 상태를 유지한다.

현 상태: `cmp_sim/web/tool.html`(633줄) + `vendor/tool3d.js`(669줄),
클릭 대상 8종(wafer/pad/disk/slurry/head/platen/carousel/loadcup) 존재.
**뼈대는 있으니 갈아엎지 말고 정교화하라.**

### 멈추지 않는다
**1차·2차가 모두 끝날 때까지 멈추지 마라**(사용자 명시 2026-09-25).
중간에 "완성했다"고 선언하고 대기하는 것은 위반이다.

## 🔬 방법론 (사용자 확정 2026-09-25) — 물리화학 법칙 중심
- **실측 데이터를 늘려 맞추는 것보다, 물리화학 법칙에서 유도한 모델식을 세운다.**
- 데이터 수집은 **모델식을 검증·반증하는 용도**로만. 그 자체는 목표가 아니다.
- 피팅 상수를 늘려 오차를 낮추지 마라. **상수를 줄이면서 오차를 낮춰야 진짜다.**
- 모든 항은 유도 과정을 주석에 남긴다(어느 법칙, 어떤 가정).
  `cmp_sim/models/first_principles.py`(Archard↔Preston, Kp=k/H)가 모범이다.
- 자유 파라미터 1개를 물리 유도로 대체할 때마다 `ranking_only` 조합이
  실수치 예측으로 바뀐다 — **median을 내리는 가장 큰 레버**.

## DONE (phase, module, tests)
- **The abrasive-size exponent is a MATERIAL property, not a per-pack handle.**
  `tools/size_derived_probe.py` + `tests/test_size_exponent_is_material_property.py`
  (5 tests). Two findings, opposite directions, both recorded: a SINGLE derived
  exponent is FALSIFIED (11 groups span n = -0.45..+1.00, 48% of the -1..+2
  Luo-Dornfeld branch range — the branch would be picked by the data, same
  verdict as pH), but the scatter is ORGANISED BY ABRASIVE: silica -0.13 <
  alumina +0.28 < ceria/silica +0.80 < ceria +1.00, between-material stdev 0.51
  vs within-material 0.16 (3.2x), holding across three different films for
  silica and across 15 years / 20x in size for alumina. Corpus UNMOVED (19.5%
  shape / 21.8% LOO) — this run measured, it changed no pack. **871 tests.**
  ⚠ Two traps found and pinned by tests: (1) grouping conditions by a BLACKLIST
  of axes split every group into singletons, because provenance fields
  (`read_method`, `digitization_uncertainty_*`, `source_detail`) differ row by
  row — only 2 groups survived instead of 11; a whitelist of process axes is
  correct. (2) Taking the abrasive from the PACK name labels wei2026 (silica)
  and su2011 (alumina) as ceria, because both borrow `sic_ceria_h2o2` and say
  PLACEHOLDER in their own headers — that manufactures a fake within-ceria
  spread of 0.10..1.00 and would have destroyed the finding. Filename is
  authoritative. The ordering is NOT explained by hardness (alumina 20 > silica
  8 > ceria 6 GPa is the wrong order), so it is recorded as a re-attribution
  with a chemical-tooth hypothesis, not as derived physics.

- **`si` finally has a validation dataset — BLOCKED #0 measured, not closed.**
  The si pack was the ONLY film scored against nothing: its Kp came from one
  back-calculated point ([ZHU25], 0.62 psi on a 125 mm single-side lapper) and
  nothing independent ever tested it. Added bae2022_si_wafer_alkali_ph
  (doi:10.3390/nano12213893, rates printed in the body text, not digitised):
  a different tool, a 9x higher down force (5.7 psi), a SUBA 600 pad.
  Shape 12.6% vs its own 4.3% replicate floor. ⚠ It does NOT beat
  predict-the-mean (12.6% both ways) and that is the honest reading — the pack
  has no pH term, so it predicts one number for a ladder that moves 1.27-1.38x.
  Absolute comparison is switched OFF: the paper never states the carrier-
  platen centre distance, so relative velocity — and therefore the Preston
  rate — cannot be formed from it. What the absolute numbers DO buy is the
  first INDEPENDENT confirmation of sanity.py's 100-3,000 A/min Si envelope,
  which until now rested on the same source as the Kp it was checking.
  Deliberately NOT fitted: two pH levels cannot determine a unimodal peak+width
  (two free constants → exact interpolation). Recorded as a THIRD audit state,
  `DECLARED_UNFITTABLE`, distinct from a null result — the effect is REAL but
  under-determined — and the test re-derives the level count and the 1.1-2.0x
  gain from the file rather than trusting the table.
  Also declined: the same figure's three AMINE rows (EDA 552.8, DETA 617.2,
  TETA 499.1 nm/min at pH 10.8-10.9 vs NaOH's 177.1 at pH 10.90). 3x the rate
  at the SAME pH is the paper's own evidence that pH does not set the Si rate;
  scoring them on a pH term would manufacture a failure out of chemistry the
  pack never claimed. That gain already lives in additives.yaml.
  Corpus 46/50 scored, 427 points; medians UNMOVED (19.5%/22.6%). pH axis
  14 → 15 datasets and 29.1% → 26.8%. 849 tests.
  ⚠ Fixed a latent hole while here: test_readme_numbers_are_computed hardcoded
  the denominator ("of 49 datasets"), so adding a dataset made the README's own
  total wrong while the test that guards the README still passed. Now computed.

- P1 Preston · P2 GW contact · P3 Luo-Dornfeld · P4 chemistry (pH/oxidizer/
  inhibitor + Arrhenius) · P5 radial uniformity · P6 pattern dishing/erosion
  · P7 pad glazing & conditioner ageing · P8 defect proxy. **846 tests pass.**
- Model selection by SITUATION not film (`core/regime.py`, `core/profiles.py`);
  maturity grading (`core/maturity.py`) — a pack may lower its grade, never
  raise it; Kp from first principles (`models/first_principles.py`).
- Learning from data: `core/calibration.py`, `core/factor_fit.py` (LOO-gated),
  `core/measurement_io.py`. **Scored on every measured axis**
  (`core/predictive_score.py`, `cmp-sim accuracy`): 41/49 datasets, 388 points.
- **pH belongs to the slurry SYSTEM, not the film** — US9422456B2's cationic
  core-shell silica peaks at pH 4.9 on the SAME TEOS film where plain silica
  peaks at pH 11. Split into `oxide_silica_aminosilane` rather than widening
  the bell: 126.6% → 25.3% on its 22 points, pH axis 49.2% → 39.3%.
- **Abrasive TYPE reaches the rate** (`slurry/abrasive_effects.py`): a swap
  rescales only by a published matched-condition ratio, withdraws the pack's
  measured exponents, says `ranking_only` when unanchored.
- **`cmp-sim accuracy` now prints `repl%` — each dataset's own reproducibility.**
  Reporting only: medians (19.5%/22.6%), scored count (43) and beats-mean (33) all
  unmoved, asserted by test. Three datasets marked `floor` (already at their own
  noise) so they stop reading as model failures. Audit of all 49 files found the
  blank column covers THREE states, not one: rates-are-averages-with-spread-
  withheld (du2004 says so), digitized-with-stated-read-error (bouvet2002_w 1.0%,
  _ti 2.7%), and nothing-stated. That separates bouvet2002_w (2.3% vs 1.0% floor,
  finished) from bouvet2002_ti (30.7% vs 2.7%, a real miss) — previously
  indistinguishable. `at_noise_floor` is None, never False, when unmeasured.
- **3D tool UI now TESTED end-to-end (was 0 tests).** The owner's brief asks for a
  simulator operated by CLICKING an AMAT-style polisher, not a form — and the UI
  had no test at all while the engine had 834. Now driven in headless Chromium
  (SwiftShader, no GPU): canvas 1280x808 with 1,027,557 lit pixels, 0 console
  errors; 10 parts hit-testable by scanning the canvas with the scene's own
  raycaster (frame/pad/head/carousel/slurry/nozzle/disk/platen/loadcup/wafer);
  click -> correct drawer (wafer/pad/disk/slurry); film changes the prediction
  (cu 5458.5 / w 1091.7 / poly_si 1668.7 / oxide 1559.6 A/min).
  ⚠ alumina & zirconia return the PACK rate (1559.6) — not a bug: no published
  same-recipe ratio exists, so abrasive_effects refuses to invent a scale and
  warns the run is a RANKING. Test asserts the WARNING, not a rate difference —
  demanding a difference would demand a fabricated number.
  playwright is an optional extra ('.[ui-test]'); tests skip without it.
- **DEFINITION OF DONE MET (checked, not assumed).** 9/10 examples run; the 10th
  (snag_solder) exits 3 BY DESIGN — SnAg is unestablished and the model refuses
  rather than inventing a pH window (the one primary report eliminated both
  windows it tried). Its pair snag_solder_screening.yaml supplies that input and
  runs. Literature gate: 4 in-scope datasets within 15% (need 3) -> PASS, and the
  gate counts WHOLE datasets — 2 are explicitly excluded for passing only on
  their best group. Every running example emits 4-5 warnings; none silenced,
  each is a disclosed gap. Kept as tests/test_definition_of_done.py, not a
  scrollback.
- **Calibration for limit 11 ALREADY EXISTED — `cmp-sim fit`.** Checked before
  building: no new command needed. Verified it recovers an injected 2.5x tool
  factor to 0.3%. ⚠ Near-miss: fitted Kp 2.3289e-13 vs pack 1e-13 looks like
  2.33x (7% short) — but `fit` regresses BARE Preston while simulate() applies
  chemistry/contact factors netting 0.929, so the target is 0.929*2.5*1e-13 =
  2.322e-13. A fitted Kp is an EFFECTIVE Preston constant, not pack*factor;
  testing against the pack constant would invent a 7% bug. Test also pins that
  calibration never touches corpus scores (else validation is circular).
- **README now states what 19.5% supports (limit 11).** Badges said 688 tests/394
  points (actual 822/424) and the axis table held stale medians. Worse, "19.5%
  median prediction error" reads as a promise to predict absolute rate to 20% —
  false on 13/34 datasets. Page now leads with "ranking claim, not a rate claim",
  carries the concrete 7.1%-shape/139x-scale case, and gives the 1-experiment fix
  (one calibration wafer re-anchors Kp). EVERY README number is now recomputed by
  a test — totals, per-axis medians, counts, scale counts, both badges.
- **`scale` column in accuracy report + JSON (reporting only).** Shape says the
  model RANKS conditions well; scale says whether the rate is right at all, and
  they fail independently — ep3161098b1 is 7.1% shape but 139x off in absolute
  rate, previously invisible. 13/34 comparable datasets are off >3x. 11 datasets
  print "-" because their own notes forbid absolute comparison (Kp-audit rule; a
  test pins the dashes to exactly that set so a silent failure can't hide there).
  Wrongness ranked both directions — us6918821b2 at 0.08x over-predicts 12x.
  Medians unchanged 19.5%/22.6%, 45 datasets, 424 points, pinned by test.
- **One acidic oxide dataset was mis-assigned; two others were NOT.** us9499721b2's
  own notes say the abrasive is 아미노실란 양전하(cationic) silica at pH 4.7 — the
  exact system oxide_silica_aminosilane was built for. Reassigned: scale 98.25x ->
  2.68x, shape 22.9% UNCHANGED. Shape can't move (axes are pressure/conc, no pH
  constant touches them), which is why "fits better" could not decide this —
  ep3161098b1 (139x) and bouvet2002_oxide (39x) improve 4-11x too but neither
  source states abrasive charge, so they were LEFT mis-scaled. ⚠ Exposed a
  circularity: oxide_silica's abrasive_conc_exponent(0.3333) was regressed from
  THIS cationic file's 3psi row; all 3 silica packs share it so nothing moved.
- **Inherited Kp is NOT the problem — hypothesis falsified.** Backed out the scale
  each pack's data implies (11 datasets excluded, each by its own 'absolute values
  incomparable' flag). The 2 packs that INHERIT kp unchanged are among the best
  calibrated (anionic 0.51x, aminosilane 2.04x); the worst is their PARENT
  oxide_silica at 38.7x. Cause: pH position, not Kp — inside the pack's fitted
  range [10,12.5] li2021=0.60x / taguchi=0.85x, but at pH 3-4.7 the same pack is
  39x/98x/139x. The pH term drives the prediction to its floor and the deficit
  lands on Kp, the last free scale. Refitting Kp would bake in an extrapolation
  error. First measurement of this limit's MAGNITUDE (2 orders, not a few %).
- **What a pack split buys (limit 10).** The 2 thinnest packs are justified — but
  in pH ONLY. Re-scoring their datasets with the parent oxide_silica: anionic
  32.1%->94.7%, aminosilane 25.3%->126.6%. So keep the split. But the diff vs
  parent is 6/124 and 7/125 parameters and EVERY one is pH — Kp, pad, abrasive
  exponents all inherited. A 62-parameter file implies independent
  characterisation it does not have; both packs now say so in their headers.
  ⚠ First diff used pack.get() (returns None for all keys) and reported the packs
  as IDENTICAL; correct accessor is pack.param(). Guarded by a test.
- **Parameter-evidence inventory (README table + test).** Per pack, how many
  fitted constants does the data actually exercise? **290/628 = 46%; 338 are
  not.** Spread matters more: cu_h2o2_bta 68% (86 rows/11 axes) vs
  oxide_silica_anionic 11% (7 rows/1 axis) — two packs with similar shape errors
  are NOT equally supported. 46% is an UPPER bound (one pH sweep credits 4 pH
  constants; 'exercised' != 'validated'; 512 user inputs excluded). Not an
  argument to delete the 338 — an argument against reading one median as
  certifying the model.
- **sic_alumina_kmno4: a score can be real and validate nothing you assumed.** Its
  two (newly scorable) datasets both sit BELOW its fitted pH range [9.0,11.0] —
  entegris2022 at pH 2.3, gong2024 at pH 2-6 — so neither validates the pH term;
  sweeping pH 3->13 on a gong row swings 94.7->7889->919 A/min across a peak no
  dataset visits. Evidenced: abrasive loading (entegris 14.1% vs mean 65.1%).
  NOT: pH (extrapolation), oxidizer (gong LOSES to its mean, 24.9 vs 15.0 — the
  data span only 99-119 A/min), abrasive size (never varied). No term is inert.
  Recorded as a documentation-only pack override; medians unchanged.
- **Every dataset now declares its film** (`scripts/declare_dataset_films.py`,
  evidence string per dataset). Transcription from each source, not inference.
  Corpus 43->45 scored, 394->424 points (entegris2022/gong2024 were unscorable
  without a film); medians UNCHANGED at 19.5%/22.6% and no existing error moved.
  Borrowings visible 7->14. Only null left: phm2016 (film never disclosed;
  'unknown' made the scorer drop it). ⚠ First attempt wrote into legacy/ —
  reverted and redone as overrides under cmp_sim/data/validation/datasets/.
- **Borrowed-pack audit** (`tests/test_borrowed_pack_audit.py`): 7 datasets score a
  film with another film's pack, in 3 kinds — justified by mechanism (5: sti_ceria
  on oxide, since its exponents split by ABRASIVE not film), deliberate negative
  controls (2: carbide2023/sic2023 on the oxide pack on purpose, each noting the
  gap its bad number documents), and placeholder packs on unsupported films (2).
  **New find: us8142675b2_pt scores 12.3% on an oxide pack — a PLAUSIBLE number
  from another material's constants**, which is more dangerous than Ti's visible
  30.7%. Audit's own blind spot named: 23/49 datasets declare no film at all, so
  prose inference was needed to surface both negative controls. No packs created.
- **Ti declared UNSUPPORTED (limit 9).** bouvet2002_ti was the largest miss vs its
  own floor (30.7% vs 2.7% digitisation). Cause found: three sweeps from ONE figure
  (Ti/W/oxide, same tool+slurry) have exponents -0.454 / -0.049 / +0.001, and the
  shared pack carries -0.05 = W's value. Fitting Ti's -0.45 was REJECTED: it is the
  only Ti data in the corpus, so the constant would be tested on its own fitting
  set (and R^2 is only 0.89 on 4 digitised points). Miss kept visible in the score.
- **`docs/limits.md` — one page for what the model REFUSES to predict.** 9 entries,
  each with the measurement that establishes the limit, the refit that was rejected
  and its cost, and the experiment that would lift it. Distinct from
  open-questions.md (undecided items): these are DECIDED refusals. Guarded by
  tests/test_limits_doc.py (11 tests) both ways — a limit-enforcing test not cited
  on the page fails, and a cited test that no longer exists fails. README's
  validation table now points at it and states the noise-floor caveat: only 5
  datasets have replicates, so elsewhere the achievable floor is UNKNOWN.
- **Two ceria datasets demand OPPOSITE pH terms; the pack keeps the right one.**
  netzband2020 (49.2%) has a VALLEY — 198/113/200/213 over pH 4/6/8/10, two IEPs
  (oxide 2-3, ceria ~8) with pH 6 optimal for neither — and `ph_response` is
  unimodal, so no constant produces it. Ruled out first: NOT a scale offset (the
  benchtop 2.25 cm2 coupon puts absolute rate 8x out, but 49.2% is already
  scale-free, k=0.128) and NOT out-of-range. A netzband-only refit reaches 15.0%
  by going nearly FLAT — and costs dandu2009 (81x swing, the set the constants
  were fitted to) 31.5% -> 492.6%. Left alone, deliberately.
- **The oxidizer term's SIGN flips with PRESSURE, inside one experiment.**
  Diagnosed the worst remaining miss (jani2025 RSM heldout, 51.2%): oxidizer
  correlates +0.76 with measurement but +0.04 with prediction — the term is blind,
  not mis-scaled (ratio spread 4.1x rules out a Kp offset). Cu sweeps contradict:
  ihnfeldt2008 peaks ~0.1 wt%, jani2025 still rising at 6, us8501625b2 shows BOTH
  signs. "Sign tracks BTA" FALSIFIED (both signs at the same 0.08 mM). The two
  groups differ ONLY in down force: 2 psi falls 8200->6300, 1 psi rises
  1900->3900. Left UNFITTED — two pressures cannot fit a coupling — so 51.2%
  stays an honest miss with a named cause. Confound: GT07's peak is ALUMINA,
  jani2025 is silica; abrasive type and pressure co-vary and cannot be separated.
- **Some datasets cannot be predicted better than they were measured.**
  hong2007's three IDENTICAL zero-inhibitor rows report 2650/2400/1850 A/min =
  13.0% replicate scatter, so 13% is the FLOOR on achievable error; the model's
  14.8% is at it. Also a correction: STATUS recorded hong2007's flat baseline as
  12.6%; it is 14.8%, identical to the model — it ties the mean, never lost to
  it. Corpus-wide, 3 datasets sit at/below their own replicate scatter, incl.
  sic2026 DOE50 (34.0% vs 38.5% scatter) — this session's pH refit crossed it
  from above the noise floor to below, so further fitting there is fitting noise.
  Only 5 datasets have replicates at all; the rest have an UNKNOWN floor.
- **Out-of-range pH is a WARNING, not a gate — measured, not assumed.** Fully
  in-range datasets (n=19) median 18.9%; fully out-of-range (n=11) 19.4%;
  Mann-Whitney z=-0.15. No separation, and the out-of-range group holds some of
  the best results (bouvet2002_w 2.3%, ep3161098b1 7.1%, lai2001 8.7%). A gate
  would discard working predictions. Differs from the oxidizer gate, which WAS
  justified: there the term's SIGN reversed (confidently wrong); here the model
  is merely less constrained. Gate = "would be wrong", warning = "rests on
  fewer measurements".
- **A validity range is the FITTING EXPERIMENT's span, never the union.** All 7
  pH-active packs now declare `ph_valid_range` (+ oxide_silica_calibrated_pad,
  which the enumerating test caught). oxide_silica is served by 9 datasets
  spanning pH 1.75-12.5 but 8 hold pH fixed and constrain nothing, so its range
  is li2021's 10-12.5 — the union would claim support no experiment gives.
  Consequence stated, not hidden: bouvet2002/us8142675b2/ep3161098b1/us9499721b2/
  carbide2023/mo2026/yang2023 now warn as out-of-range. No rate changed.
- **An inert constant that looks active is worse than no constant.**
  `sic_ceria_h2o2` had `ph_response_width: null` (to block the inherited acid
  ceria optimum) but still declared the inherited `ph_peak: 4.5` — a constant
  that looks like a SiC optimum and does nothing; the engine's own INERT warning
  had been firing. Its stated reason ("DOE50 cannot isolate the pH axis") was
  checkable and false: 5 groups isolate pH 9/10/11. Fitted peak 10.5 / width
  1.25 / floor 0.10 = 27.5% vs 57.1% inert, and ALKALINE, as the pack's own
  mechanism argument predicted. Interior to its range (unlike the bound packs).
  Trade recorded: DOE50 39.3->34.0, three held-out SiC sets worsen ~0.1-1.3.
- **Validity ranges: a bounded peak has an UNMEASURED side.** The three packs
  whose `ph_peak` is a bound at the data edge (oxide_silica_anionic 2.0,
  cu_alkaline_benzenesulfonic 6.2, cu_h2o2_bta 3.0) had no measured limb beyond
  it and an acid floor of 0, so the model decayed to 0.00 A/min at pH 0.5 with
  no warning (the "2.5 widths" check doesn't fire — pH 1.0 is only 2.0 widths).
  Each now declares `ph_valid_range` = its source table's span, and the engine
  warns outside it, naming the floor and calling a ZERO floor a refusal rather
  than a number. cu_h2o2_bta carries TWO ranges (pH constants 3-6, oxidizer
  constants 2-6.25) — different terms, different experiments, not merged.
- **Pack blindness audit (`tests/test_pack_axis_blindness_audit.py`)**: fails
  if any pack declares no response on an axis its own datasets sweep. One hit —
  `w_fe_oxidizer` on pH — and it is a SOURCED NULL RESULT, re-derived by the
  test from 6 matched pairs (pH 3 vs 6 at matched oxidizer+abrasive: mean ratio
  0.958, sign inconsistent, vs an 8x oxidizer effect in the same table). Null
  results and omissions look identical from outside, so silence is now declared
  in the pack with its table and scope (pH 3-6 only).
- **A missing pH term hid inside the OXIDIZER term.**
  `cu_alkaline_benzenesulfonic` declared no pH response at all (only a
  meaningless inherited `ph_ref: 4.0` from the acidic parent), so a measured
  3.4x pH fall predicted one constant = predict-the-mean, 51.0%. Worse, the
  pack's `oxidizer_peak_wt_pct: 1.0` was justified as "rate falls with
  oxidiser" — but that dataset's pH DRIFTS 10.2→8.5 as acidic H2O2 is added,
  while a KOH-BUFFERED one (us20110165777a1, pH 11.1) measures it FLAT and the
  patent says so explicitly. Added the pH term, peak bounded to the lowest
  measured pH 6.2 (free fit prefers 3.3, outside the data). HELD-OUT evidence:
  h2o2_series 51.7%→12.7%, benzenesulfonic 29.6%→26.8%, both now beat the
  mean. Corpus 20.2%→19.5% trend, 22.6%→21.7% LOO.
- **The velocity exponent is UNRESOLVABLE by this corpus — not fitted.**
  Isolated groups give -0.42 / +0.62 / +0.86 / +0.86 / +1.10 where Preston says
  1.0, and the two datasets need OPPOSITE pressure dependences (mariscal falls
  1.10->0.62 with P, us6918821b2 rises -0.42->0.86). The negative group is the
  patent's own point: an IC1000 pad LOSES Cu rate with speed at low down force
  (lubrication regime, no channel in Preston). A global fit would land ~0.86,
  be wrong at both ends of both datasets, and improve the pooled median.
  Nothing fitted; a test fails if any pack ever declares `velocity_exponent`.
- **NO universal "second pH channel" — hypothesis tested and FALSIFIED.**
  The three pH residuals are three different shapes, and two of them share a
  pack: dandu2009 is a BELL (peak pH 4-5.5), netzband2020 is a V (minimum at
  pH 6, both ends high), same `sti_ceria`, same film, same abrasive. A rising
  alkaline term would have to lift netzband 4.3-4.6x at pH 8/10 — exactly where
  dandu already matches to 1.03/0.96. Fixing one breaks the other, so NOTHING
  was added to the model; the contradiction is pinned as a measurement fact.
  Real lead (recorded, not built): Netzband varies the Ce3+/Ce4+ OXIDATION
  STATE, which the pack holds fixed — a ceria-specific coupling, not a pH term.
- **pH is NOT thin (unlike velocity) and the optimum follows the abrasive's
  CHARGE.** Isolated-pH groups: 12 groups / 66 pts (velocity had 29), isolated
  median ~30% vs pooled 39.3% — isolation does not rescue it, so the term is
  genuinely the weakest physics. Worst group (CN109609035B, 94.7%) was a THIRD
  silica system: anionic silica peaks at or below pH 2 on the same TEOS film
  where cationic core-shell peaks at 4.9 and plain silica at 11 — ordered by
  particle charge vs the oxide's IEP. New pack `oxide_silica_anionic`:
  94.7% -> 32.1%, pH axis 39.3% -> 32.1%, li2021 untouched at 0.2%.
  ⚠ Stops at 32%: the measured pH-6 UPTURN needs a second additive pH channel
  (alkaline hydrolysis), a functional-form change — recorded, not fitted around.
- **The Cu pH optimum is a BOUND, from ONE system.** `ph_peak` was 4.0 =
  "the pack's operating pH", with a note asking for a pH 2-6 sweep — which was
  already in the repo. US20080090500A1 T4 falls monotonically pH 3->6 at all
  three silica loadings, so the optimum is at or BELOW pH 3 and 4.0 predicted a
  rise where the patent measures a 10-24% drop. Peak -> 3.0 (edge of data),
  width 4.1 -> 4.45: shape 10.1% -> 4.3% on those 12 points. Refused to pool
  the alkaline US9200180B2 leg for 17 points — it is BTA-free benzenesulfonic
  and has its OWN pack; same trap `oxide_silica_aminosilane` was split to avoid.
  ⚠ Zero effect on the corpus median: that table prints no down force.
- **The oxidizer term's SIGN belongs to the pH branch — regime gate.**
  Miranda's 2x2 moves H2O2 1.5->3.5 wt% and gets +49% at pH 4, -86% at pH 8
  (interaction p=0.0207, Pourbaix: soluble Cu2+ vs hard CuO). One constant
  cannot be both, so `cu_h2o2_bta` declares `oxidizer_ph_window: [2.0, 6.25]`
  — bounds read off the gated constants' own provenance — and OUTSIDE it the
  term is switched off and says so, instead of extrapolating a wrong sign.
  Scoring now separates "declined" from "wrong"; a gate on an axis a dataset
  holds CONSTANT must not silence it (that rule saved 3 good datasets).
  ⚠ Corpus 20.2% -> 19.5% is NOT a physics gain: 2 datasets stopped answering.
- **The oxidizer floor is MECHANICAL, not chemical** — US8070843B2 is a
  fixed-abrasive pad with no free abrasive, so the pack's free-abrasive 0.14
  background is wrong for it; its own table prints 0.040. 51.7% -> 8.7%, but
  the honest number is the 4 oxidizer-bearing rows: 9.5% -> 8.6% (the zero row
  is near-tautological once the floor is declared). Pack keeps its 0.14.
- **Velocity is the THINNEST axis, not the weakest term** — the 44.1% median
  came from Taguchi arrays that never repeat a chemistry at two speeds. Only
  29 points in the whole corpus isolate velocity; on the one in-scope isolated
  sweep (Mariscal 3x3) the error is 11.7% and the exponent +0.86 vs Preston's
  +1.0. Also fixed a data-fidelity bug: the Yang L25 recorded 2 of its 6
  factors, so four chemical factors' scatter was being read as velocity error.
- Size-matched abrasive-ratio hunt CLOSED with 15 honest nulls
  (`research/rate_ratios_matched.yaml`) — 0 of 15 pairs pass both gates, so
  34/35 film×abrasive pairs stay `ranking_only`.
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si, SiC, SnAg. 55 additives ×
  9 films, 11 abrasives × 9 films. Legacy 2nd transfer absorbed.
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`accuracy`/`packs`/
  `profiles`), zero-dep web UI + API, 3D tool view (`/tool`), `.command`
  launcher. **Published**: github.com/khleecnce/cmp-sim (MIT), demo at
  cmp-sim.vercel.app (`CMPSIM_TOKEN`). History scrubbed before going public.

## NEXT
**Attack the `responsive_miss` bucket by CAUSE, one law per run — starting with
the pH-dominated oxide subset (5 datasets, 25-49% shape, all oxide/ceria).**

The census (below) named the bucket: 35/46 datasets, 342/427 points, median
20.2%. Inside it the misses are NOT spread evenly — they cluster:
* **pH-dominated oxide/ceria** (netzband2020 49.2, cn109609035b 32.1,
  dandu2009 31.5, us9422456b2 25.3, son2021 25.6): the pH axis moves the
  predicted rate 52-89%, so a constant exists and is WRONG, not missing. The pH
  axis is CLOSED to further closed-form attempts by the 2026-09-27 rule (two
  falsifications). What is NOT closed: these five are all **ceria or
  ceria-adjacent on oxide**, where the mechanism is chemical-tooth
  (Ce3+ site density), not electrostatic. Measure whether the residual orders by
  **Ce3+ fraction / dissolved-Ce proxy** before proposing any functional form.
* **velocity-bearing L25/L16 DOEs** (yang2023 69.0, us6564116b2 20.3,
  mariscal2020 12.9, us6918821b2 44.1): pressure AND velocity both respond, and
  the pressure-residual probe (this run) showed yang2023 alone at -1.28 while
  the others sit near 0 — i.e. yang2023 is an outlier to explain, not a shared
  curvature.
* **two INERT axes inside otherwise-responsive datasets** are worth more than
  any new law: `ep3161098b1_w` (54.9%) varies `fe_ppm` and `inhibitor_ppm` and
  the model answers with the SAME rate for both — the Fenton term never reaches
  the rate. Same for `jani2025_cu_rsm` (`chelator_M`, `promoter_M`, 51.2%) and
  `yang2023` (`dispersant_wt_pct`, `slurry_ph` both inert under its pack).
  These are the two worst-scoring responsive datasets and the cause is a
  plumbing gap, not physics. **Check the wiring before deriving anything.**

Rule kept from earlier runs: do not fit. Measure first, one axis per run.

### Closed 2026-09-28 (2nd run): the residual is DECOMPOSED — 80% of points are improvable
`tools/residual_census.py` + `tests/test_residual_census.py` (7 tests).
Each scored dataset lands in exactly one bucket, with responsiveness MEASURED
(rebuild the first row at each axis' min and max, run the real simulator, ask
whether the rate moved >0.5%) rather than declared by a YAML field:

| bucket | datasets | points | median shape |
|---|---|---|---|
| noise_floor (irreducible) | 3 | 59 | 26.8% |
| no_constant (declared gap, no law can fix) | 4 | 14 | 27.7% |
| **responsive_miss (a better law helps)** | **35** | **342** | **20.2%** |
| few_levels (<=2 levels, one reading dominates) | 4 | 12 | 7.1% |

**Verdict: the ≤15% allowance is NOT justified yet.** The census was built to
test exactly that, and it came back the other way: 80% of measured points sit in
the bucket a better law can move, so the 19.5% median is not floored by
measurement noise or declared gaps. The allowance may only be invoked when this
table says otherwise — the test asserts the improvable bucket is a majority and
fails loudly if that flips.
Two traps avoided: buckets are assigned in priority order (a floored dataset is
never also counted as improvable, so the shares cannot exceed 100%), and
`no_constant` is decided by RUNNING the simulator — four datasets
(lee2021 inhibitor, kenchappa2021 pad hardness, bae2022 Si pH, phm2016 dresser
usage) have a populated axis that provably never reaches the rate, and grading
them as model error would have inflated the improvable bucket.

### Closed 2026-09-28 (2nd run): rate saturation in PRESSURE is FALSIFIED
`tools/pressure_saturation_probe.py` +
`tests/test_pressure_saturation_falsified.py` (4 tests). The standard proposal
for the responsive_miss bucket is the two-resistance form
`1/RR = 1/(k·P·V) + 1/RR_chem` (Kaufman 1991 passivation), which costs one new
per-pack constant. It makes a sharp prediction: after one fitted scale, the
residual ln(measured/predicted) must fall with ln P on every ladder. Over the 10
datasets with >=3 pressure levels the median slope is **+0.08**, only 5/10 are
negative, and pressure-OVERLAPPING datasets disagree in SIGN
(us9499721b2 -0.17 vs us8142675b2 +0.19; ep3161098b1_teos -0.06 vs
ep3161098b1_w +1.04 — the same patent, same pressures, opposite trends).
A shared curvature cannot produce opposite signs at the same pressures, so the
misses belong to the datasets (scale/chemistry/tool), not to the P dependence.
**Preston's linearity in P is kept and no constant was added** — a fourth
derived-law rejection, and the fourth time refusing a handle the data do not
demand.

### Closed 2026-09-28 (was the previous NEXT): decompose the residual
Rationale it was chosen on (kept for the record).
Four consecutive runs improved the model's HONESTY and reduced its constant count
(pH law falsified, size exponent re-attributed to material, conc exponent
replaced by a derived +1/3) and the corpus median did not move once — 19.5% after
all four. That is not a coincidence to work around, it is the finding: **the
scored corpus rows do not exercise the axes being fixed.** Every scored row runs
its pack's reference abrasive, so abrasive-scoped work provably cannot move the
number, and the pH work moved only a shape that was already in-sample.

So before spending another run on a constant, MEASURE where the 19.5% comes from.
Concretely, for the 46 scored datasets produce a per-dataset attribution of the
residual to one of these buckets and count them:
1. **at the dataset's own noise floor** — already 3 marked `floor`; how many more
   would be if `repl%` were measured? (only 6/46 have it). Irreducible.
2. **axis the pack has NO constant for** (declared gap, model declines) — these
   are honest and cannot improve without new literature.
3. **axis the pack HAS a constant for and still misses** — the only bucket where
   a better law helps. THIS is the bucket to size.
4. **single-point / 2-level datasets** where shape error is arithmetically
   dominated by one reading.
Report the four counts and the median WITHIN bucket 3. If bucket 3 is small, the
10% target is arithmetically unreachable on this corpus and the ≤15% allowance
should be invoked WITH THIS TABLE as the required evidence — STATUS.md demands
"what sets the floor", and a bucket census is exactly that argument. If bucket 3
is large, it names the next law to derive instead of guessing.

Do NOT fit anything in this run. It is a measurement, like `ph_derived_probe` and
`conc_derived_probe` were, and it must not touch a pack. Put it in
`tools/residual_census.py` with a test that re-derives the bucket counts from the
dataset files rather than hardcoding them.

### Closed 2026-09-28 (was the previous NEXT): the conc exponent is a DERIVED LAW
Ran exactly the protocol the item specified and it returned a NEGATIVE on the
question asked (material scope, 1.6x < 2x bar) — recorded as required, no
re-attribution made. The probe then tested the next-simplest hypothesis and found
the positive result the item did not anticipate: a single DERIVED +1/3 lands on
the corpus median with zero fitted constants, which removes five per-pack fitted
values instead of renaming them. `abrasive_conc_half_wt_pct` was left alone, as
the item warned. Also fixed the all-or-nothing withdrawal gate this change
exposed in `solver._abrasive_hook` (a withdrawn size axis was falling through to
the falsified derived -0.84). 880 tests.
`tools/conc_derived_probe.py` + `tests/test_conc_exponent_material_scope.py` (6).

### Closed 2026-09-27 (was the previous NEXT): the size exponent is now a MATERIAL constant
Implemented exactly as the item specified, with one deviation recorded: the
ceria/silica composite (+0.80, k=2, US20190127607A1) was left OUT of the table
(`SIZE_EXPONENT_COMPOSITE_NOTE`) because it resolves to neither parent material
and asserting a composition the patent does not state would be inventing a
number. Four tests pin the behaviour in `tests/test_abrasive_type.py`:
alumina/ceria now move the rate with their own measured log-slope (+0.28 /
+1.00, asserted by regressing the simulator itself over a 4x size step), an
abrasive with NO sweep anywhere (diamond) still reports the axis as unapplied
rather than filling it from the falsified derived -0.84, and the table cannot
carry a value whose k or spread contradicts its own sweep list. Three existing
tests changed premise and were rewritten with the superseded reasoning kept in
the docstring rather than deleted.
Corpus UNMOVED at 19.5% / 21.8% (46/50, 427 points), as predicted.

### Closed 2026-09-27 (was the previous NEXT): the pH derived law is FALSIFIED
`tools/ph_derived_probe.py` + `tests/test_ph_derived_law_falsified.py`
(3 tests). In-sample shape medians over the 6 pH sweeps with >=3 levels:
  Gaussian, 4 constants fitted PER GROUP (24 total)      11.0 %
  derived (kinetic x electrostatic), 2 GLOBAL constants  60.4 %
  electrostatic leg ALONE, 2 GLOBAL constants            35.3 %
  kinetic leg ALONE (S**0.5), ZERO constants             93.6 %
The ablation is the result: **removing the law-backed kinetic leg IMPROVES the
fit**, so the half-order hydroxide leg (Brady & Walther 1990) is the half that
is wrong — not under-tuned. Reason: S(pH)**0.5 is monotone rising by
construction, but 4 of 6 measured sweeps PEAK IN ACID. Dissolution kinetics set
the hydrated layer's THICKNESS (which saturates), not the removal rate; the
Cook-1990 softening term already carries that mechanism, so importing it again
double-counts. Forcing it makes the electrostatic constant B flip SIGN per pack
(oxide_silica -5.0 vs +2.25..+6.75 elsewhere) — a fitting handle, not an energy.
**Second falsification of a derived pH form** (the first: 2-pKa surface
complexation, 27.3% vs 17.7% on Dandu). Per the rule written into that item,
the pH axis is CLOSED to further closed-form attempts until the corpus has more
sweeps: 6 usable sweeps with 4 distinct peak positions cannot determine a form
whose peak is free.
⚠ The by-product matters more than the verdict: **the incumbent Gaussian's
11.0% is in-sample interpolation.** Two of the six groups have constants >= pH
levels (li2021 n=3 scores 0.0%). Under leave-one-pH-LEVEL-out it scores
**52.9%** on 42 held-out points, while the 2-constant electrostatic form fitted
on the OTHER FIVE GROUPS scores 66.6% — a harsher protocol, 14 points behind.
So the pH axis's reported 25-26% is not a well-supported 25%; the honest
out-of-sample pH error is ~50%, and that is a real contributor to the corpus
median that no amount of re-deriving the same 4-constant form will remove.
Corpus UNMOVED as predicted (19.5% shape / 21.8% LOO, 46/50, 427 points) — this
run changed no pack, only measured. **866 tests pass.**

### Superseded 2026-09-27 (kept for the reasoning): the pH-law proposal
**Attack the pH axis with a DERIVED rate law instead of the fitted Gaussian.**
The Gaussian is the single largest remaining physics debt: 15 datasets, median
25.3%, and it carries 2-3 fitted constants per pack (`ph_peak`, `ph_response_
width`, `ph_acid_floor`) that come from nowhere but the data. The edge-hold just
proved the form is wrong outside its fitting window — it had to be CLAMPED to
stop producing 139x artefacts. A form that needs a clamp is a form to replace.

Target form (oxide/silica, where the corpus is thickest), all terms derivable:
  r = k_OH * a_OH^n  * f_electrostatic(pH; IEP_abrasive, IEP_film)
  - the OH- catalysed hydrolysis leg is FIRST-ORDER-ish in a_OH^0.5 (Iler 1979
    ch.1; Brady & Walther 1990 measured n = 0.5 on amorphous silica) — that is a
    LITERATURE exponent, not a fitted one, so it REMOVES a constant
  - the electrostatic leg is why the optimum MOVES with abrasive charge, the
    fact already established in this repo (anionic silica peaks <=2, cationic
    core-shell at 4.9, plain silica at 11 on the SAME TEOS film). A Gaussian
    cannot express that; a product of two site-ionisation terms at the two IEPs
    can, and IEPs are MEASURED quantities per material, not free parameters.
⚠ Read the falsification note below first: a 2-pKa surface-complexation product
was ALREADY tried and lost (27.3% vs 17.7% on Dandu). The difference proposed
here is that the pH-dependence enters through a_OH^0.5 kinetics MULTIPLIED by
electrostatics, not as a pure site-product — and that the IEPs are fixed from
literature rather than fitted. If it loses again on held-out data, record the
second falsification and STOP pursuing this form; do not fit around it.

Scoring rule for this item: count CONSTANTS before and after. A form that hits
the same median with fewer free constants is the win; a form that needs more is
a loss even if the median falls.

### Closed 2026-09-27 (was the previous NEXT): `ph-edge-hold` MERGED
The pH Gaussian was being evaluated far outside the pH window its width was
fitted in — oxide_silica's width 3.1 comes from Li 2021's three points over
pH 10-12.5, and evaluating that bell at pH 3-4 multiplies the rate by
exp(-(7/3.1)^2) = 1/61, a number produced by the FUNCTION rather than by any
measurement. `chemical_rate.py` now holds the pH argument at the pack's own
`ph_valid_range` edge (a field that already existed and only printed a warning).
Physically: the amorphous-silica hydrolysis plateau — the rate is OH--catalysed
above the neutral point and flattens below it (Iler 1979 ch.1; Brady & Walther
1990). ZERO new constants.
  ep3161098b1_teos 139.2x -> 2.5x    bouvet2002_w    75.6x -> ~1x
  bouvet2002_oxide  39.2x -> ~1x     bouvet2002_ti   38.2x -> ~1x
  >3x absolute misses 13 -> 9;  LOO 22.6 -> 21.8;  beats-the-mean 34 -> 35
  shape median UNMOVED 19.5% (predicted, and the check that it was a pure scale)
13 pinned-number tests re-baselined, each with the superseded reasoning recorded
rather than deleted. Two were checked properly rather than re-pinned:
  - test_sic_kmno4's "jump across the unvisited peak" — the worry was that the
    clamp hides a peak OUTSIDE the declared range. It does not: sic_alumina_
    kmno4's peak 10.5 is INTERIOR to its range 9.0-11.0, now asserted. The test
    was rewritten to state the sharper fact — both its datasets (pH 2-6) sit
    entirely ON the clamp, so the pH term is one constant factor for every row
    they contain and cannot be evidence for or against it.
  - test_readme's "139" assertion was a HARDCODED headline case, so removing the
    artefact broke the test guarding the README. Now recomputes the current
    worst case from the scorer (lai2001_cu 8.7% shape / 17.5x scale).
New: `tools/readme_numbers.py` regenerates every number the README claims.

### Closed 2026-09-26 (was the previous NEXT): BLOCKED #2, the ceria scale
See BLOCKED #2. The pack's Kp was an unreproduced estimate; four measured ceria
datasets agreed one-sidedly on 1.09e-13 m/Pa (was 2.2e-13). STI example
7,235 -> 1,559 A/min, inside the published envelope. Corpus medians UNMOVED
(19.5%/22.6%) exactly as predicted — Kp is a pure scale and the shape metric
divides it out; a moved shape score would have meant something else changed.
first_principles.py's k = Kp*H correlation was recomputed as a consequence
(WEAR_COEFFICIENT 9.50e-4 -> 8.25e-4, spread 1.8x -> 1.5x) and the module now
states that this tightening is bookkeeping, not evidence for the 1/H form.
863 tests.

### Closed 2026-09-26 (was the previous NEXT): per-film P0 is FALSIFIED
The "fit a per-FILM breakthrough pressure P0" item is DONE and the answer is NO.
`tools/p0_per_film_probe.py` ran the leave-one-dataset-out test on oxide, the
only film with 4 matched-condition pressure datasets. The in-sample optimum is
**P0 = 0.00 psi exactly** — the offset does not want to exist even on the data
it is scored on — and out of sample it LOSES (15.5% -> 16.0% mean, 11.4% ->
12.5% median). Hydrated-silica removal has no breakthrough stress in 0.6-8 psi;
the Cook gel layer is soft and continuously re-formed, so there is no yield
stress to exceed. Cu (2 matched datasets) and W (1) cannot test it at all and
are recorded as data-limited, NOT as support. Pinned by
`tests/test_pv_exponent_confound.py::test_a_per_film_threshold_pressure_does_
not_earn_its_constant_either`; derivation in docs/derivations.md.

Still genuinely unexplained, and NOT caused by the exponent confound:
ep3161098b1_w (a = 2.00 on 3 matched rows), sic2023 (62% at every form tried),
us6918821b2 (the Cu low-pressure velocity inversion, BLOCKED #1).

### Do NOT re-attempt (measured and falsified 2026-09-25, see docs/derivations.md)
- pH term as a 2-pKa surface-complexation site product (Cook Si-O-Ce bond):
  27.3% vs the current bell's 17.7% on Dandu 2009; the best fit inverts the
  pKa order, and Dandu's 15x tail asymmetry is outside the form's reach.
- Preston -> Tseng-Wang P^(5/6)V^(1/2): loses on 6 of 8 P/V datasets.

### Standing context carried forward (was the previous NEXT)
⚠ CORRECTION. A previous session reported the project "complete" against the
P1-P8 engine gates alone. That was the WRONG bar: the owner's actual brief
(desktop, 09-24 10:49) is (1) a simulator that turns inputs into predictions,
(2) a clickable 3D AMAT-style polisher UI, (3) per-WAFER/film learning, (4) per-
ABRASIVE learning (ceria/silica/alumina/zirconia separately). All four now have
passing end-to-end evidence (844 tests, incl. 10 browser-driven UI tests).

OWNER DECISION (09-24): alumina and zirconia are OUT OF THE PICKER. They were
confusing because selecting them changed nothing — abrasives.yaml holds exactly
ONE published same-recipe ratio (ceria/colloidal_silica = 3.0x on oxide), so any
other swap leaves the rate anchored to the pack's own abrasive.

Implemented as a RULE, not a blocklist (cmp_sim/api.py:_selectable_abrasives):
offer an abrasive on a film when it has a published ratio there, or when it IS
that film's pack reference (the anchored 1.0x case). Result —
  oxide -> ceria, colloidal_silica    cu -> alumina    w -> alumina
  sic/sti/oxide_ceria -> ceria        poly_si/si -> colloidal_silica
zirconia is gone everywhere; alumina survives only on Cu/W, the two packs
actually calibrated with it. Nothing was DELETED: alumina still supplies the
measured size exponent +0.29 and still scores in six datasets (su2011 SiC 4.4%,
lai2001 Cu 8.7%, gong2024, entegris2022, us8142675b2 Pt, su2011 6H-SiC). A config
file may still name any abrasive and it resolves with warnings as before.

Remaining gap is DATA, not build: no same-recipe ratio exists for the withheld
abrasives. Do NOT close it by deriving a ratio from hardness; Mohs order does not
predict CMP rate (ceria is softer than alumina and removes oxide faster), and
abrasive_effects.py refuses that on purpose.

## BLOCKED  (numbers + sources: `docs/open-questions.md`)
0. `si` — HALVED, not closed. The film now has one independent dataset
   (bae2022, 12.6% shape) so it is no longer unscored, and its 5.7 psi rates
   confirm the 100-3,000 A/min envelope independently of the Kp source. What
   is STILL missing is the thing the entry originally asked for: a second
   ABSOLUTE point. bae2022 cannot supply one — it never states the carrier-
   platen centre distance, so no relative velocity and no Kp can be recovered
   from it. The 10,776 A/min over-prediction at bare defaults therefore stands
   unexplained, and Kp still rests on one Seidel-era point.
   NEEDED: a bare-Si rate measured at a stated pressure AND a recoverable
   relative velocity (rpm plus carrier-platen geometry, or m/s directly).
   Secondary gap now named: the pack has NO pH term at all
   (tests/test_pack_axis_blindness_audit.py::DECLARED_UNFITTABLE), because two
   pH levels cannot fit a peak and a width. A three-level pH sweep on bare Si
   with colloidal silica would lift that.
1. Velocity inversion is NOT a lubrication effect — no dataset will fix it.
   λ = 0.001401·(rpm/P) exactly, i.e. λ IS the pseudo-Sommerfeld number V/p
   (Wu & Liao 2016, doi:10.5772/64484) up to one constant, so calibrating it
   with measured viscosity/roughness only rescales and cannot reorder. The
   inverting rows (λ .056/.112/.187) OVERLAP the non-inverting ones
   (.021/.042/.070), and mariscal2020 — 9 rows that never invert — sits inside
   that range. A threshold would need to be below .056 and above .070 at once.
   (This corrects the earlier entry asking for a film-thickness dataset.)
   Surviving evidence: λ ORDERING predicts over-prediction independently in
   both datasets (ρ −0.714, −0.517). Pad CONTACT was then tested and also
   fails: `plasticity_index`/`pad_limited_plasticity_lambda` are constant
   within each dataset (consumable properties) and differ between them the
   WRONG way (inverting set is MORE plastic ⇒ predicts more removal), while
   `summit_saturation` = 0.00739·P exactly — down force relabelled. Its clean
   separation (0.0111 inverting vs ≥0.0148) is therefore just "P < 2 psi"
   fitted to one patent's low-force arm. Twice now the candidate criterion was
   the operating point in disguise (λ=V/p, saturation=P).
   NEEDED: pad surface stats (asperity density/radius by confocal or AFM, or
   glazing state) measured beside a rate-vs-speed sweep. Nothing in the corpus
   reports them.
2. `sti_ceria` absolute scale — **CLOSED 2026-09-26.** Diagnosed: the pack's
   Kp was the wrong one of the two cited sources. The inherited 2.2e-13 m/Pa
   was `confidence: estimated`, self-described as a representative,
   unreproduced value, and never back-calculated from any measured run. All
   FOUR absolute-comparable ceria datasets implied a LOWER Kp (one-sided, not
   scatter): kenchappa2021 8.4e-14, netzband2020 7.6e-14, mariscal2020
   1.34e-13, son2021 1.64e-13 → geometric mean **1.09e-13 m/Pa**, LOO range
   9.5e-14–1.23e-13. Re-anchored. examples/sti_ceria.yaml now returns
   **1,559 Å/min**, inside the 200–6,000 envelope. Residual scales moved to
   0.70–1.51x (were 0.35–0.75x). The two ceria-COATED-silica composite
   datasets imply ~2.3e-14 and were EXCLUDED, not averaged in — a ceria shell
   on a silica core is a different abrasive; that disagreement stays open and
   visible (their scale is now 0.19x/0.24x). Guarded by
   tests/test_ceria_kp_backed_out_of_four_datasets.py, which re-derives the
   number from the scorer and asserts no shape score moved.
3. Size exponent splits by ABRASIVE, not film; packs must scope and cite it.
4. P3 exponents still `unverified` — no nanoindentation of a CMP-polished
   surface exists in the corpus.
5. SnAg has no published Preston coefficient (Archard ranking only); SiC
   inherits SiO₂'s modulus — `null` + TODO(owner).
6. Three judgement calls kept as compromises over flattering per-dataset fits.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

All axes (427 pts, 46/50 scored + 4 DECLINED): median **19.5%** trend,
**21.8%** LOO. By axis — size 11.2%, oxidizer 21.3%, loading 22.4%,
pressure 24.1%, pH 25.3%, velocity 39.0%. 35/46 beat predict-the-mean.
⚠ Caveats, all against us: the axis
medians pool datasets that vary several things at once — velocity's 39.0% is
11.7% once isolated (thin axis, 29 pts), while pH's holds up under isolation
(12 groups / 66 pts, ~30%) so it IS the weakest term. Cu datasets are
DECLINED rather than answered wrongly (honesty, not accuracy). The pH axis
moved 29.1 -> 26.8% only because a NEW dataset entered below the median, not
because any prediction improved.
Resume handover: `~/CMP-SIM-FOR-RESUME.md`
