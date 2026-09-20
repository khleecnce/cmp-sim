<!-- V2-SECTION: R2-slurry | 작성 2026-09-11 -->
# SiC+세리아 CMP 연마입자 실측 입경 — Chen et al. 2017 (RSC Adv.)

> 목적: `knowledge/params/sic_ceria_h2o2.yaml`의 `abrasive_size_nm`(기존 80nm, estimated,
> 실은 세리아가 아니라 같은 노트의 실리카 dmean 80nm를 잘못 전용한 값으로 보임 — §3 참조)를
> SiC+세리아 계 1차 문헌 실측값으로 승격.

## 1. 문헌
**Chen, G.; Ni, Z.; Bai, Y.; Li, Q.; Zhao, Y. "The role of interactions between abrasive
particles and the substrate surface in chemical-mechanical planarization of Si-face 6H-SiC."
*RSC Adv.* 2017, 7, 16938–16952.** DOI: 10.1039/C6RA27508G. **오픈액세스(CC-BY 3.0)** —
원문 PDF 직접 확보·전문 확인(`papers/chen2017-rsc-adv-ceria-silica-6hsic-particle-interaction.pdf`,
미러 사이트→미러 사이트 미러 경유, 저널 자체가 OA라 라이선스는 정상).

## 2. 실측값 — 세리아 연마입자 입경
원문 §2.1 Materials (p.16939):
> "Silica abrasives (dmean ≈ 80 nm, 30 wt%, Jingrui New materials Co. Ltd., Xuancheng, China)
> and ceria abrasives (**dmean ≈ 120 nm**, 30 wt%, Chuangyuan New materials Co. Ltd., Suzhou,
> China) were obtained as colloidal dispersions... These two abrasive nanoparticles were
> characterized by transmission electron microscopy (TEM, JEOL-2100, Japan), as shown in Fig. 1."

- **세리아 dmean ≈ 120 nm** — 공급업체 콜로이달 분산 스펙값이자 TEM으로 직접 확인(Fig. 1b).
  실제 CMP 실험(§2.3)에서 이 세리아를 2 wt%로 희석해 사용(원문 §2.1: "concentrations of
  silica particles and ceria particles were maintained at 6 wt% and 2 wt%, respectively").
- 같은 원문의 실리카는 dmean ≈ 80 nm (같은 인용문, DOI 10.1039/C6RA27508G §2.1) — 기존
  sti_ceria.yaml의 80nm 값과 수치가 일치하는데,
  이는 실리카 값이고 세리아 값이 아니다(§3 한계 참조).
- 대상 웨이퍼: n형 2인치 Si-face **6H-SiC** 단결정(TanKeBlue Semiconductor). 4H-SiC는 아니나
  둘 다 SiC 폴리타입이고 CMP 연마입자-웨이퍼 상호작용 메커니즘(정전 흡착, Si–O–Ce 화학결합)은
  폴리타입 무관하게 논의된다 — 원문이 4H-SiC 문헌(Kimoto 등)을 배경으로 인용.

## 3. ⚠ 산화제 불일치 — 명시
이 논문의 CMP 실험(§2.3, 4psi, 80/80rpm, IC-1000 패드)은 산화제로 **KMnO4(0.05 M)**를
쓴다. `sic_ceria_h2o2.yaml`은 **H2O2** 산화제 계(Wang et al. ACS SI Table S3 DOE 기반)다.
**산화제는 다르지만, 연마입자 스펙(세리아 dmean)은 산화제와 독립적으로 입자 자체(공급업체
콜로이달 분산·TEM 측정)의 물성이므로 SiC+ceria 계로는 동일하게 본다.** 산화제가 바뀌면
화학층(MRR 배수)은 달라지지만 입자 기하(κ 계산에 쓰이는 abrasive_size_nm)는 별개 축이다.

## 4. 한계
- dmean은 원문이 "TEM 특성화" 및 공급업체 콜로이달 스펙으로 보고한 값이며, D50(중앙값)과
  엄밀히 동일한 정의인지(평균 vs 중앙값)는 원문에 명시되지 않음 — **미검증**. 실무상 두 값은
  근접하다고 가정(단분산에 가까운 콜로이달 세리아 분산의 통상적 관례)했을 뿐이다.
- 6H-SiC(이 논문) vs 4H-SiC(이 파라미터 팩) — 폴리타입 차이. 두 폴리타입 모두 SiC이고
  세리아 연마입자 자체의 입경 스펙은 웨이퍼 폴리타입과 무관(공급업체 스펙이므로)하다고
  **추정**했으나, 원문이 4H-SiC 실험으로 이 스펙을 직접 재현한 것은 아니다.
- 세리아 원 공급 스펙은 30wt% 스톡이고, 실사용은 2wt%로 희석 — 희석이 입경 분포를
  바꾼다는 보고는 원문에 없음(단순 희석, 응집 없음을 가정, 이 가정 자체는 **불명**).

## 5. 교란/대조 — 기존 80nm값의 정체
[[particle-wafer-interaction-mechanical-chemical-balance]]와 [[ceria-slurry-ce-redox-selectivity]]가
다루는 base 팩(sti_ceria)의 기존 abrasive_size_nm=80nm을 이 원문과 대조하면, 그 수치는
세리아(120nm)가 아니라 **같은 원문 §2.1의 실리카 dmean≈80nm과 정확히 일치**한다 — 세리아·
실리카 두 연마입자 수치가 과거 어느 시점에 뒤바뀌어 전용됐을 가능성을 시사한다(재현 대조:
원문 실리카 80nm ≈ 기존 팩값 80nm, 원문 세리아 120nm ≠ 기존 팩값 80nm).

## 6. 결론
`abrasive_size_nm` = **120 nm**, confidence: literature(1차 원문 확인, OA, 실측 CMP
실험에 실사용된 스펙값). 산화제 불일치는 §3에 명시. D50/dmean 등가성, 폴리타입 교차적용,
희석에 따른 응집 여부는 모두 **미검증** 가정임을 함께 남긴다.

## §추가 (2026-09-13, 정확도루프 COMPLETION-C4 갭) — SiC ceria+H2O2 held-out 후보 탐색 결과

COMPLETION-C4(sic_ceria_h2o2 유의 held-out 0건) 갭을 풀기 위해 SiC CMP DOE 데이터를
추가 탐색했다. US9368367B2(Cabot Microelectronics, "CMP of silicon carbide using soft
particles and/or soft surfaces", FreePatentsOnline 전문 확보, 2026-09-13) Example 1에
pH 2~9 · KMnO4 0.02~0.4M 조건 6개의 완전한 제거율 표가 있었다(pH2/0.4M→1400 nm/hr,
pH9/0.4M→360 nm/hr 등).

**검증 시도 결과: 무효 데이터.** 이 실시예의 연마입자는 in-situ 생성 MnO2/MnCl3
"soft particle"(ceria 아님), 산화제는 KMnO4(H2O2 아님)이다. sim/factors.py `_f_chi`가
`abrasive=='ceria'`인 팩에서는 pH 항을 `_ph_ceria_window_term`(IEP 기반 창형)으로
라우팅하는데, sic_ceria_h2o2 팩에 막질(sic_4h)의 `wafer_iep_ph`가 선언되어 있지 않아
이 항이 통째로 스킵된다(sim/chemistry.py, wafer_iep_ph 부재 시 조용히 건너뜀 — 로그
경고만 남김). oxidizer 항도 `oxidizer_peak_wt_pct`가 팩에 없어 발동하지 않는다.
결과적으로 pH·산화제 조성을 6개 조건에 걸쳐 오버라이드해도 χ=1.0으로 **전혀 변하지
않아** 예측 MRR이 전 조건 동일(분산 0, Spearman 판정불가)이었다.

이는 entegris2022(alumina, kappa 기계항만 테스트 가능)와 동일한 "형식적으로는
in_scope=true이나 화학종 불일치로 실효성 없음" 패턴이다. 차이는 entegris는 kappa가
화학종 무관 범용 항이라 살아남았지만, 이번 건은 살아남는 범용 항이 없었다(chi의
oxidizer 항은 화학종 무관이지만 팩에 oxidizer_peak_wt_pct 자체가 없어 죽어있다).

**결론(EVIDENCE-RULES 판정): 데이터셋 등록 보류.** validation/datasets/에 넣지 않았다
(넣어도 backtest.py가 "입력이 안 들어감" 경고와 함께 집계에서 사실상 무의미해진다).
근본 원인은 데이터 문제가 아니라 팩 갭 2건이다:
  1. sic_ceria_h2o2에 wafer_iep_ph(4H-SiC 등전점) 미선언 → pH 창 항 항상 스킵
  2. sic_ceria_h2o2에 oxidizer_peak_wt_pct 미선언 → 산화제 농도 항 항상 스킵
두 갭 모두 이번 회차에서 문헌값을 못 찾아 메우지 않았다(4H-SiC IEP·H2O2/SiC 산화제
포화농도 모두 미검증 상태로 남김 — 지어내지 않음). 다음 SiC 갭 회차의 우선 과제로
남긴다.

**진짜 held-out 후보가 되려면**: ceria 연마입자 + H2O2(또는 팩에 이미 있는 산화제 항이
반응하는 화학종) 조합의 SiC CMP DOE(n≥4, 조성 1축 이상 변화)가 필요하다. 현재 확보한
sic2026(Wang, calibration에 소모), entegris2022(alumina, kappa만), 이번 건(KMnO4,
무효) 외에 세 번째 독립 후보를 못 찾았다 — 미러 사이트·특허 검색 모두 ceria+H2O2 조합의
정량 표를 추가로 내지 못함. "1차 미확보"로 기록.

## 6. 검증 — 원문 실측값이 실제로 팩에 들어갔는가

> ⚠ 갭 1 정정(2026-09-16 부채상환): 위 "sic_ceria_h2o2에 wafer_iep_ph 미선언" 은
> 작성 시점 기준이며 **현재는 해소됐다**(팩 선언값 4.9, 근거는
> [[sic-isoelectric-point-singh2006-jnr]] Singh et al. 2007). 갭 2(산화제 형상
> 파라미터 부재)는 그대로 유효하다 — EVIDENCE-RULES 판정#35 가 기존 3경로
> (촉진 Langmuir / 억제 / 단봉) 전부를 이 계에서 반증해 **항을 만들지 않기로**
> 종결했기 때문이다. 즉 "아직 안 채운 칸"이 아니라 "채우면 안 되는 칸"이다.

이 노트의 유일한 정량 주장은 "원문 dmean 120 nm 를 팩의 `abrasive_size_nm` 으로 채택했다"
이므로, 검증도 그것 하나다 — 원문 인용값과 팩 선언값의 일치, 그리고 기준점(`_ref`)이
같이 옮겨져 기준 조건 배수가 1.0 으로 유지되는지를 확인한다.

```python verify
# Chen et al. 2017, RSC Adv. 7, 16938-16952, DOI 10.1039/C6RA27508G §2.1 Materials
CERIA_DMEAN_NM_PAPER = 120.0   # 원문 인용문: "ceria abrasives (dmean ~ 120 nm ...)"
SILICA_DMEAN_NM_PAPER = 80.0   # 같은 인용문 — 세리아가 아니다(전용 금지, §3)

assert CERIA_DMEAN_NM_PAPER != SILICA_DMEAN_NM_PAPER, (
    "이 노트의 존재 이유: 기존 80nm 는 같은 원문의 **실리카** 값이었다")

import sys, pathlib
root = pathlib.Path(__file__).resolve().parents[2] if "__file__" in dir() else pathlib.Path(".").resolve()
while root != root.parent and not (root / "sim" / "params.py").exists():
    root = root.parent
sys.path.insert(0, str(root))
from sim.params import load_pack

pk = load_pack("sic_ceria_h2o2")
size = float(pk.get("abrasive_size_nm"))
ref = float(pk.get("abrasive_ref_size_nm"))

assert abs(size - CERIA_DMEAN_NM_PAPER) < 1e-9, (
    f"팩 abrasive_size_nm={size} 가 원문 실측 {CERIA_DMEAN_NM_PAPER} nm 와 다르다")
# 기준점 동반 이동 계약: 본값과 기준점이 같아야 기준 조건에서 입경 항 배수가 정확히 1.0.
assert abs(ref - size) < 1e-9, (
    f"기준점 {ref} 가 본값 {size} 와 어긋났다 — Kp 이중 계상 위험(_ref 동반 이동 규칙)")
print(f"OK: 원문 {CERIA_DMEAN_NM_PAPER} nm == 팩 {size} nm, 기준점 {ref} nm 동반")
```
