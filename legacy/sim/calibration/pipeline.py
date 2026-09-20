"""캘리브레이션 end-to-end 파이프라인 — ORG.md §7.6 M5 데모("CSV 업로드 → NPW 보정 →
PTW 예측")가 실제로 성립하는지 기계로 확인하는 단일 진입점.

ingest.py(데이터 입구) → prior.py(물리→사전분포) → fit_npw.py(NPW 반경잔차 GP)
→ fit_ptw.py(NPW→PTW 전이) 를 한 번에 잇는다. 각 모듈은 이미 완성돼 있고 이
파일은 그 공개 계약을 그대로 호출할 뿐이다 — 새 물리·새 팩 키·새 통계 판단을
만들지 않는다(0바이트 수정 목표, 과제 지시 6번).

설계 원칙
────────
1. 단방향(ORG §7): fit_ptw.fit()이 npw_correction을 필수·읽기전용으로 요구하는
   기존 계약을 그대로 통과시킨다 — 파이프라인이 그 계약을 우회하거나 npw
   결과를 ptw 결과로 되돌려 고치는 코드는 어디에도 없다.
2. 단계 실패는 예외로 전체를 죽이지 않는다. StageRecord(status="ok"/"skipped"/
   "failed", reason=...)로 기록하고 다음 단계로 넘어간다. 선행 단계가 없어서
   뒤 단계가 건너뛰어질 때는 reason에 그 선행 단계 이름을 그대로 적는다.
3. improved=False를 성공으로 포장하지 않는다 — fit 자체는 정상 실행됐으므로
   status="ok"로 두지만 metrics["improved"]=False가 그대로 남고, 최종 verdict가
   이를 "uncalibrated"/"partial"로 드러낸다("calibrated"라고 부르지 않는다).
4. is_npw_equivalent(ptw_input)=True는 fit_ptw.fit 자신의 판정을 그대로 호출해서
   얻는다(파이프라인이 미리 가로채 값을 지어내지 않는다) — 그 결과를 소비자가
   읽기 쉽게 status="skipped"로만 라벨링한다.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from sim.calibration import drift, fit_npw, fit_ptw, ingest, prior
from sim.calibration.drift import DriftReport
from sim.calibration.fit_npw import NPWCorrection
from sim.calibration.fit_ptw import PTWCorrection
from sim.calibration.prior import ParamPrior
from sim.calibration.ptw_vm_schema import PTWVMInput, is_npw_equivalent

__all__ = ["StageRecord", "CalibrationRun", "run_calibration", "evaluate_new_lot"]

IngestSource = Union[dict, "ingest.IngestResult", str, pathlib.Path]


@dataclass
class StageRecord:
    """파이프라인 한 단계의 실행 기록. status="failed"만 예외적 상황을 뜻한다 —
    "skipped"는 정상적인 설계상 건너뜀(입력 없음/거부 판정)이다."""
    name: str
    status: str  # "ok" | "skipped" | "failed"
    reason: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalibrationRun:
    """run_calibration() 전체 결과. verdict는 "보정 성공"을 함부로 주장하지 않는다."""
    pack: str
    npw_correction: Optional[NPWCorrection]
    ptw_correction: Optional[PTWCorrection]
    priors: Dict[str, ParamPrior]
    stages: List[StageRecord]
    verdict: str  # "calibrated" | "partial" | "uncalibrated" | "failed"
    note: str
    model: str = "tier1.preston_radial"


def _resolve_ingest(source: IngestSource) -> "ingest.IngestResult":
    """dict(원 레코드) | ingest.IngestResult | 경로(JSON 레코드 파일) → IngestResult."""
    if isinstance(source, ingest.IngestResult):
        return source
    if isinstance(source, (str, pathlib.Path)):
        record = json.loads(pathlib.Path(source).read_text(encoding="utf-8"))
        return ingest.ingest_record(record)
    if isinstance(source, dict):
        return ingest.ingest_record(source)
    raise TypeError(
        "npw_source/ptw_source/new_source는 dict(원 레코드) | ingest.IngestResult | "
        f"경로(JSON 레코드 파일)만 허용한다: {type(source)!r}"
    )


def run_calibration(pack: str, npw_source: IngestSource, *,
                     ptw_source: Optional[IngestSource] = None,
                     ptw_input: Optional[PTWVMInput] = None,
                     model: str = "tier1.preston_radial",
                     seed: int = 0, n_restarts: int = 5) -> CalibrationRun:
    """priors → ingest_npw → fit_npw → ingest_ptw → fit_ptw 순서로 사슬을 돌린다.

    ptw_source가 None이면 fit_ptw 단계는 처음부터 skipped다(NPW만 요청됐다는
    뜻이지, 실패가 아니다). ptw_source는 있는데 ptw_input이 없으면 fit_ptw.fit이
    요구하는 필수 인자가 없다는 뜻이라 마찬가지로 skipped다.
    """
    stages: List[StageRecord] = []

    # ── priors: 나머지 사슬과 독립 — 실패해도 뒤 단계를 막지 않는다.
    try:
        priors = prior.build_param_priors(pack)
        stages.append(StageRecord(
            "priors", "ok", "팩 물리모델 기반 사전분포 생성.", {"n_priors": len(priors)}
        ))
    except Exception as exc:
        priors = {}
        stages.append(StageRecord("priors", "failed", f"prior.build_param_priors 실패: {exc}", {}))

    # ── ingest_npw
    npw_ingest = None
    try:
        npw_ingest = _resolve_ingest(npw_source)
        stages.append(StageRecord(
            "ingest_npw", "ok", "NPW 측정 레코드 수집·검증.",
            {"n_rows": npw_ingest.n_rows, "n_excluded": npw_ingest.n_excluded,
             "n_missing": npw_ingest.n_missing, "n_outliers": npw_ingest.n_outliers},
        ))
    except Exception as exc:
        stages.append(StageRecord("ingest_npw", "failed", f"ingest.ingest_record 실패: {exc}", {}))

    # ── fit_npw (선행: ingest_npw)
    npw_correction: Optional[NPWCorrection] = None
    if npw_ingest is None:
        stages.append(StageRecord(
            "fit_npw", "skipped", "선행 단계 ingest_npw가 실패해 학습 데이터가 없다.", {}
        ))
    else:
        try:
            npw_correction = fit_npw.fit(pack, npw_ingest, model=model, seed=seed, n_restarts=n_restarts)
            reason = "GP 반경잔차 적합 완료."
            if not npw_correction.improved:
                reason += " improved=False — 물리모델 기준선을 이기지 못했다(보정 미적용)."
            stages.append(StageRecord(
                "fit_npw", "ok", reason,
                {"n_train": npw_correction.n_train, "converged": npw_correction.converged,
                 "improved": npw_correction.improved,
                 "loo_rmse_gp": npw_correction.loo_rmse_gp,
                 "loo_rmse_baseline": npw_correction.loo_rmse_baseline},
            ))
        except Exception as exc:
            stages.append(StageRecord("fit_npw", "failed", f"fit_npw.fit 실패: {exc}", {}))

    # ── ingest_ptw (선행: ptw_source 유무)
    ptw_ingest = None
    if ptw_source is None:
        stages.append(StageRecord("ingest_ptw", "skipped", "ptw_source가 제공되지 않았다.", {}))
    else:
        try:
            ptw_ingest = _resolve_ingest(ptw_source)
            stages.append(StageRecord(
                "ingest_ptw", "ok", "PTW 측정 레코드 수집·검증.",
                {"n_rows": ptw_ingest.n_rows, "n_excluded": ptw_ingest.n_excluded,
                 "n_missing": ptw_ingest.n_missing, "n_outliers": ptw_ingest.n_outliers},
            ))
        except Exception as exc:
            stages.append(StageRecord("ingest_ptw", "failed", f"ingest.ingest_record 실패: {exc}", {}))

    # ── fit_ptw (선행: ptw_source, ptw_input, ingest_ptw, fit_npw — 전부 필요)
    ptw_correction: Optional[PTWCorrection] = None
    if ptw_source is None:
        stages.append(StageRecord(
            "fit_ptw", "skipped", "선행 단계 ingest_ptw가 없다(ptw_source 미제공).", {}
        ))
    elif ptw_input is None:
        stages.append(StageRecord(
            "fit_ptw", "skipped",
            "ptw_input(PTWVMInput)이 제공되지 않았다 — fit_ptw.fit의 필수 인자.", {}
        ))
    elif ptw_ingest is None:
        stages.append(StageRecord(
            "fit_ptw", "skipped", "선행 단계 ingest_ptw가 실패해 학습 데이터가 없다.", {}
        ))
    elif npw_correction is None:
        stages.append(StageRecord(
            "fit_ptw", "skipped",
            "선행 단계 fit_npw가 실패/미실행이라 npw_correction이 없다 "
            "(ORG §7 단방향 전이 규칙 — PTW는 NPW 없이 적합할 수 없다).", {}
        ))
    elif is_npw_equivalent(ptw_input):
        # fit_ptw.fit이 이 판정을 이미 내장하고 있다 — 그대로 호출하고(우회하지
        # 않고), 그 결과를 파이프라인 소비자를 위해 skipped로 라벨링만 한다.
        ptw_correction = fit_ptw.fit(pack, ptw_input, ptw_ingest, npw_correction,
                                      model=model, seed=seed, n_restarts=n_restarts)
        stages.append(StageRecord(
            "fit_ptw", "skipped",
            "ptw_input이 is_npw_equivalent=True — local_density/prev_layer_topography가 "
            "모두 없어 NPW와 구분되지 않는다(fit_ptw.fit 자체 판정, ORG §5.3 결론). "
            "NPW 보정까지만 유효하다.",
            {"n_train": ptw_correction.n_train},
        ))
    else:
        try:
            ptw_correction = fit_ptw.fit(pack, ptw_input, ptw_ingest, npw_correction,
                                          model=model, seed=seed, n_restarts=n_restarts)
            reason = "PTW 잔차(2단계) 적합 완료."
            if not ptw_correction.improved:
                reason += " improved=False — NPW보정 대비 PTW 층이 개선하지 못했다(PTW 층 미적용)."
            stages.append(StageRecord(
                "fit_ptw", "ok", reason,
                {"n_train": ptw_correction.n_train, "converged": ptw_correction.converged,
                 "improved": ptw_correction.improved,
                 "loo_rmse_npw_only": ptw_correction.loo_rmse_npw_only,
                 "loo_rmse_ptw": ptw_correction.loo_rmse_ptw},
            ))
        except Exception as exc:
            stages.append(StageRecord("fit_ptw", "failed", f"fit_ptw.fit 실패: {exc}", {}))

    verdict, note = _verdict(stages, npw_correction, ptw_correction, ptw_source)

    return CalibrationRun(
        pack=pack, npw_correction=npw_correction, ptw_correction=ptw_correction,
        priors=priors, stages=stages, verdict=verdict, note=note, model=model,
    )


def _verdict(stages: List[StageRecord], npw_correction: Optional[NPWCorrection],
             ptw_correction: Optional[PTWCorrection],
             ptw_source: Optional[IngestSource]) -> tuple:
    """최종 판정 — "보정 성공"으로 보이면 안 된다(과제 지시 3번)는 제약을 그대로 코드로 만든다."""
    by_name = {s.name: s for s in stages}

    if by_name["ingest_npw"].status == "failed":
        return "failed", f"ingest_npw 실패: {by_name['ingest_npw'].reason}"
    if by_name["fit_npw"].status == "failed":
        return "failed", f"fit_npw 실패: {by_name['fit_npw'].reason}"

    npw_improved = bool(npw_correction is not None and npw_correction.improved)
    if not npw_improved:
        return "uncalibrated", (
            "NPW GP 보정이 물리모델 기준선을 이기지 못했다(improved=False, 또는 fit 자체가 거부됐다) "
            "— 물리모델 예측을 그대로 쓴다. '보정 성공'으로 포장하지 않는다."
        )

    if ptw_source is None:
        return "calibrated", "NPW 보정만 요청됐고 물리모델 기준선을 개선했다."

    ptw_stage = by_name["fit_ptw"]
    if ptw_stage.status == "ok" and ptw_correction is not None and ptw_correction.improved:
        return "calibrated", "NPW+PTW 보정이 모두 물리모델 기준선을 개선했다."

    return "partial", f"NPW 보정만 유효하다 — PTW 층 미적용: {ptw_stage.reason}"


def evaluate_new_lot(run: CalibrationRun, new_source: IngestSource) -> DriftReport:
    """운영 중 새 로트가 기존 보정의 GP 예측분포와 여전히 맞는지 점검한다(drift.check_drift 위임).

    run.ptw_correction이 있으면 그것으로(PTW 층이 비활성이어도 drift.check_drift가
    내부에서 npw/ptw 활성 여부를 각각 판단한다), 없으면 run.npw_correction으로 검사한다.
    이 함수는 재적합을 하지 않는다 — drift.py의 "보고만 한다" 경계를 그대로 물려받는다.
    """
    correction = run.ptw_correction if run.ptw_correction is not None else run.npw_correction
    if correction is None:
        raise ValueError(
            "run에 npw_correction도 ptw_correction도 없다 — drift 점검을 할 보정 대상이 없다."
        )
    new_ingest = _resolve_ingest(new_source)
    return drift.check_drift(correction, new_ingest, pack=run.pack, model=run.model)
