<!-- V2-SECTION: R2-slurry | cu_h2o2_bta abrasive_size_nm 승격(estimated→literature) 근거 노트 -->
# Cu+알루미나+H2O2+BTA 계 연마입자 D50 — EKC Technology 알루미나 100~120 nm (UCSD Talbot 그룹 1차 문헌 직접 확인)

> 작성일: 2026-09-11
> 대상: `knowledge/params/cu_h2o2_bta.yaml`의 `abrasive_size_nm` (기존 100.0 nm, estimated)
> [[particle-wafer-interaction-mechanical-chemical-balance]] [[slurry-components-overview]]
> [[luo-dornfeld-active-abrasive-size-mrr]]

## 1. 왜 필요한가

`abrasive_size_nm`은 `sim/factors.py::_f_kappa()`가 접촉강도 계산에 쓰는데, 기존 값 100 nm은
근거 문헌 없이 estimated로 남아 있었다. Cu CMP: 알루미나+H2O2+BTA 조합을 **실제로 다루는** 1차
문헌에서 실측 D50을 찾아 대조한다.

## 2. 1차 출처 — 두 논문 모두 원문 PDF 직접 확보·판독

두 논문 모두 미러 사이트 미러(`미러 사이트` → `citation_pdf_url` 메타에서 실제 저장 URL 추출,
`미러 사이트/storage/...` 및 `미러 사이트/storage/...`)로 PDF를 받아 PyMuPDF(`fitz`)로 텍스트
추출 후 직접 읽었다(OCR 아님, 원문 문장 그대로 인용).

- **Gopal, T.; Talbot, J. B.** "Use of Slurry Colloidal Behavior in Modeling of Material Removal
  Rates for Copper CMP." *J. Electrochem. Soc.* **154**(6), H507–H511 (2007).
  doi:10.1149/1.2718474. (Crossref로 저자·연도·저널 확인. 전문 직접 판독 완료.)
- **Ihnfeldt, R.; Talbot, J. B.** "The Effects of Copper CMP Slurry Chemistry on the Colloidal
  Behavior of Alumina Abrasives." *J. Electrochem. Soc.* **153**(11), G948–G955 (2006).
  doi:10.1149/1.2335982. (Crossref로 저자·연도·저널 확인. 전문 직접 판독 완료.)

⚠ 작업 지시에 딸려온 사전 단서는 두 DOI를 서로 다른 저자쌍에 잘못 대응시켰다(Crossref로 교차
검증해 정정): `10.1149/1.2718474`가 Gopal & Talbot(2007), `10.1149/1.2335982`가 Ihnfeldt &
Talbot(2006)이다. 아래 수치는 이 정정된 대응관계 기준.

둘 다 UC San Diego Talbot 그룹(Chemical Engineering Program)의 연속 연구로, 같은 **EKC
Technology 알루미나** 슬러리를 재료로 쓴다.

## 3. 핵심 수치 — EKC Tech 알루미나, 정확히 Cu+H2O2+BTA 조합으로 모델링됨

Ihnfeldt & Talbot(2006), 원문 그대로:
> "Without additives, the IEP was pH ∼ 9 for the EKC Tech alumina (**100 nm diameter**)."

Gopal & Talbot(2007), 원문 그대로:
> "We measured zeta potential and particle size distribution of an EKC Tech alumina (**average
> particle diameter of 120 nm**) slurry with concentrations of glycine and similar range of
> hydrogen peroxide as used by Seal et al." … "the model was used for an EKC Tech alumina slurry
> containing **0.01 wt % BTA**, 10⁻³ M SDS, **0.1 wt % H2O2**, 10⁻³ M KNO3, and either 0.1 M
> glycine or 0.01 M EDTA" (Fig. 3, Table 근처 본문).

→ **이 마지막 문장이 정확히 과제가 요구하는 계다**: 알루미나(EKC Tech, D≈100~120 nm) + H2O2
(0.1 wt%) + BTA(0.01 wt%)를 동시에 포함한 Cu CMP 슬러리를, Luo-Dornfeld 모델에 실측 입경분포를
넣어 MRR을 예측한 사례. 100 nm은 EKC Technology의 공칭(nominal) 입경이고, 120 nm은 같은 그룹이
수용액 중 QELS(준탄성 광산란)로 측정한 유효(effective) 평균 입경이다 — 같은 물질, 공칭값과
현탁액 실측값의 정상적 차이(20%)로 봐야 한다.

같은 그룹의 Ihnfeldt(2006) 본문 Table I 조성 (e), (f)도 **BTA(0.01 wt%) + H2O2(0.1 wt%) + Cu
나노입자(0.12 mM, CMP 중 용해 구리 모사) + 알루미나** 조합을 직접 콜로이드 측정했다(단, 이쪽
알루미나는 EKC Tech가 아니라 **Cabot 사 알루미나**, 1차 입자 20 nm가 뭉쳐 median aggregate
diameter **150 nm**를 이루는 globular aggregate — Cabot 제품 스펙 인용, 원문 각주 28). pH나
첨가제 조합에 따라 유효 응집 입경은 수백 nm~수 μm까지 넓게 퍼지는 이봉(bimodal) 분포를 보이므로
(원문 Table II), "D50 = 100~120 nm"는 **저농도·저응집(낮은 pH, 분산 잘 된) 조건**에서의 대표값
으로 이해해야 한다.

## 4. 비교 대조 — Seal et al. (사전 단서로 주어졌던 170 nm, 2차 인용만 확인)

Gopal & Talbot(2007) 본문이 Seal et al.을 인용한 문장을 원문 그대로 확인:
> "A Rodel alumina slurry containing 28% alumina with a mean particle diameter of **170 nm** was
> used for the experimental polishing of 9 mm diam copper disks... Slurries without additives and
> containing 0.1 M glycine and varying concentrations of H2O2 up to 10 wt % at pH 4 were used."

즉 Seal et al. (Thin Solid Films 423, 243, 2003)의 170 nm Rodel 알루미나는 **H2O2 + glycine**
조합이며 **BTA는 포함되지 않는다** — 과제가 요구하는 "알루미나+H2O2+BTA" 정확 일치가 아니라
"알루미나+H2O2"까지만 일치하는 인접 문헌이다(원문은 유료라 Gopal 2007의 인용을 통한 **2차
확인**에 그친다 — Seal 원문 자체는 미확보). 170 nm은 Rodel(현 CMC Materials/Cabot 계열)이라는
**다른 벤더**의 다른 제품이라, EKC Tech 100~120 nm과 혼동해 평균 내면 안 된다.

## 5. 판정

- Cu+알루미나+H2O2+BTA를 **정확히 동시에** 다루는 1차 문헌(Gopal & Talbot 2007, 원문 직접 확인)
  에서 알루미나 D는 EKC Tech 공칭 **100 nm**(같은 그룹 Ihnfeldt 2006 원문 확인) / 측정 유효
  **120 nm**(Gopal 2007 원문 확인)이다.
- 기존 YAML 값 100.0 nm은 이 문헌의 공칭값과 정확히 일치하고, 측정 유효값(120 nm)과도 20%
  이내로 부합한다. **값을 바꿀 근거가 없다** — 그대로 두고 confidence만 승격한다.
- Seal et al. 170 nm(Rodel, H2O2+glycine, BTA 없음)은 인접하지만 정확 일치가 아니고 2차 인용
  뿐이므로 채택하지 않되, 대조군으로만 기록한다.

## 6. 한계/미검증

- 100~120 nm은 **저응집 조건**의 대표값이며, 슬러리 pH·첨가제 조합에 따라 유효 응집 입경은
  Ihnfeldt(2006) Table II처럼 수백 nm~수 μm까지 벌어질 수 있다(이봉분포). `abrasive_size_nm`
  파라미터가 이 팩에서 단일 스칼라로 쓰이는 한, "잘 분산된 슬러리"를 가정한 값임을 명심.
  (참고: `abrasive_size_exponent=0.0`으로 이미 이 필드가 MRR 지배인자가 아님이 확정됐으므로
  ─ [[../cmp/abrasive-size-null-result-force-partition-theory.md]] ─ 이 값의 정밀도가
  MRR 결과에 미치는 영향 자체는 이미 낮다. 이번 승격은 κ(접촉강도) 계산의 입력값 신뢰도만 올린다.)
- EKC Technology는 이후 사업 인수·개편을 거쳤고(현재 독립 브랜드로는 사실상 소멸), 이 100 nm이
  현재 시중 Cu CMP 알루미나 슬러리의 대표값인지는 별도 확인이 필요하다 — 2000년대 중반 UCSD
  연구용 슬러리 기준값이라는 시대적 한계가 있다.

## 7. 코드 재현 (python verify — CI가 매 push마다 실제 실행)
§5 판정("기존 YAML 100.0 nm이 공칭값과 정확히 일치, 측정 유효값 120 nm과 20% 이내 부합")을
숫자로 재현한다.

```python verify
import yaml
from pathlib import Path

yaml_path = Path("knowledge/params/cu_h2o2_bta.yaml")
pack = yaml.safe_load(yaml_path.read_text())
current_nm = pack["params"]["abrasive_size_nm"]["value"]

# 문헌값 (본문 §3): EKC Tech 공칭 100 nm(Ihnfeldt 2006), 측정 유효 120 nm(Gopal 2007)
nominal_nm = 100.0
measured_nm = 120.0

# 판정 1: 현재 YAML 값이 공칭값과 정확히 일치
assert current_nm == nominal_nm, f"YAML {current_nm} != 공칭값 {nominal_nm}"

# 판정 2: 공칭값과 측정 유효값 차이가 20% 이내(본문 주장)
diff_pct = abs(measured_nm - nominal_nm) / nominal_nm * 100
assert diff_pct <= 20.0, f"공칭-측정 차이 {diff_pct:.1f}% > 20%"

print(f"PASS: YAML={current_nm}nm == 공칭 100nm, 측정값과 차이 {diff_pct:.1f}% (<=20%)")
```

한계: 이 코드는 §5의 수치 판정(값 일치·20% 이내)만 재현한다. §3-4의 원문 인용문 자체는
코드로 검증할 수 없는 텍스트 대조이며, 미러 사이트 경유 PDF 판독의 정확성은 사람 재확인에
의존한다(교차 재현 불가 항목으로 명시).
