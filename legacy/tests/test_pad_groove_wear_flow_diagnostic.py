"""pad_groove_wear_flow.py 엔진 등록 회귀 — WaferResult 진단 필드 4종
(잔존깊이비·유동단계·컨덕턴스비 진단).

근거: sim/tier2_physics/pad_groove_wear_flow.py::groove_depth_um/
residual_depth_fraction/wear_stage/conductance_ratio(원본 무수정, self-test
7/7 PASS), knowledge/materials/pad-groove-wear-flow-change-end-of-life.md
§2·§4·§5. D0·컨디셔닝 시간 관례는 _pad_groove_eol_diagnostic과 완전히 동일
(meta.pad_hours, groove_depth_mm mm->um). 그루브 절대 폭은 groove_width_um=
600um(Mu 2016 패드 B)을 쓴다 — 모듈 기본값 0.5mm(Irfan 2025 기하)는 쓰지 않는다.

⛔ residence_time_s·slurry_volumes_cm3·groove_wear_flow_state(h_land_um·
q_actual_cm3_per_s가 Recipe/팩 어디에도 없음)·micron_cabot_life_wafers(시간
->wafer 환산이 어느 팩에도 없음)는 절대 호출하지 않는다 —
test_forbidden_functions_never_called이 ast로 기계 고정한다.
"""
import ast
import inspect

import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _pad_groove_wear_flow_diagnostic
from sim.params import Param
import pad_groove_wear_flow as PGWF

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria",
              "w_fe_oxidizer"]


def _with_cut_rate(pack, c=1.0, pad_hours="0"):
    recipe = Recipe(pack=pack, time_s=60, meta={"pad_hours": pad_hours})
    rr = recipe.resolve()
    rr.pack.params["pad_cut_rate_um_per_h"] = Param(
        key="pad_cut_rate_um_per_h", value=c, unit="um/h",
        source="test-probe", confidence="estimated")
    return rr


def test_five_packs_fields_filled_or_skipped_with_reason():
    # 현재 5팩 전부 pad_cut_rate_um_per_h 미선언 — 스킵되는 것이 정상
    # (_pad_groove_eol_diagnostic과 동일 사유).
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        assert not rr.pack.has("pad_cut_rate_um_per_h")
        out = _pad_groove_wear_flow_diagnostic(rr)
        assert out["pad_groove_flow_note"] is not None
        if out["pad_groove_residual_fraction"] is None:
            assert "pad_cut_rate_um_per_h" in out["pad_groove_flow_note"]
        else:
            assert out["pad_groove_wear_stage"] in ("initial", "mid", "end_of_life")
            assert out["pad_groove_conductance_ratio"] is not None

        # 팩에 cut_rate를 주입하면 실제로 채워진다.
        rr2 = _with_cut_rate(pack)
        out2 = _pad_groove_wear_flow_diagnostic(rr2)
        assert out2["pad_groove_residual_fraction"] is not None, pack
        assert out2["pad_groove_wear_stage"] is not None, pack
        assert out2["pad_groove_conductance_ratio"] is not None, pack
        assert out2["pad_groove_flow_note"] is not None, pack


def test_zero_hours_is_fresh_pad():
    rr = _with_cut_rate("cu_h2o2_bta", c=1.0, pad_hours="0")
    out = _pad_groove_wear_flow_diagnostic(rr)
    assert out["pad_groove_residual_fraction"] == 1.0
    assert out["pad_groove_wear_stage"] == "initial"
    assert out["pad_groove_conductance_ratio"] == 1.0


def test_conductance_ratio_decreases_faster_than_residual_fraction():
    # h^3 의존이므로 잔존깊이비보다 컨덕턴스비가 더 빨리(더 낮게) 떨어져야 한다.
    prev_residual = 1.0
    prev_cond = 1.0
    for hours in (50, 150, 300, 450):
        rr = _with_cut_rate("cu_h2o2_bta", c=1.0, pad_hours=str(hours))
        out = _pad_groove_wear_flow_diagnostic(rr)
        residual = out["pad_groove_residual_fraction"]
        cond = out["pad_groove_conductance_ratio"]
        assert residual < prev_residual, hours
        assert cond < prev_cond, hours
        assert cond < residual, hours  # 컨덕턴스비가 잔존비보다 더 급하게 감소
        prev_residual, prev_cond = residual, cond


def test_wear_stage_three_stage_boundaries():
    d0_um = 760.0
    # residual = 1 - c*t/d0 -> t = (1-residual)*d0/c
    c = 1.0
    for residual, expected_stage in ((0.9, "initial"), (0.5, "mid"), (0.1, "end_of_life")):
        hours = (1.0 - residual) * d0_um / c
        rr = _with_cut_rate("cu_h2o2_bta", c=c, pad_hours=str(hours))
        out = _pad_groove_wear_flow_diagnostic(rr)
        assert out["pad_groove_wear_stage"] == expected_stage, (residual, hours)


def test_eol_exceeded_clamps_conductance_ratio_to_zero_with_warning():
    # D0=760um, c=1um/h -> 800h면 완전 소진(D=0으로 clamp)
    rr = _with_cut_rate("cu_h2o2_bta", c=1.0, pad_hours="800")
    out = _pad_groove_wear_flow_diagnostic(rr)
    assert out["pad_groove_residual_fraction"] == 0.0
    assert out["pad_groove_wear_stage"] == "end_of_life"
    assert out["pad_groove_conductance_ratio"] == 0.0
    assert "EOL" in out["pad_groove_flow_note"]


def test_uses_groove_width_um_not_module_default():
    # 모듈 기본값 0.5mm가 아니라 base.yaml groove_width_um=600um(=0.6mm)을 쓴다.
    rr = _with_cut_rate("cu_h2o2_bta", c=1.0, pad_hours="200")
    out = _pad_groove_wear_flow_diagnostic(rr)
    d0_um = 760.0
    d_um = PGWF.groove_depth_um(d0_um, 1.0, 200.0)
    expected_06 = PGWF.conductance_ratio(d_um, d0_um, 0.6)
    expected_05 = PGWF.conductance_ratio(d_um, d0_um, 0.5)
    assert out["pad_groove_conductance_ratio"] == expected_06
    assert out["pad_groove_conductance_ratio"] != expected_05
    assert "600" in out["pad_groove_flow_note"]
    assert "0.5mm" in out["pad_groove_flow_note"]


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="cu_h2o2_bta", time_s=60, meta={"pad_hours": "10"})
    res_with = simulate(r)

    orig = E._pad_groove_wear_flow_diagnostic
    E._pad_groove_wear_flow_diagnostic = lambda rr: {
        "pad_groove_residual_fraction": 0.001,
        "pad_groove_wear_stage": "end_of_life",
        "pad_groove_conductance_ratio": 0.0,
        "pad_groove_flow_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._pad_groove_wear_flow_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.pad_groove_conductance_ratio == 0.0


def test_forbidden_functions_never_called():
    """residence_time_s·slurry_volumes_cm3·groove_wear_flow_state·
    micron_cabot_life_wafers는 engine.py 어디서도 실제로 호출되지 않는다.

    inspect.getsource + ast로 **실제 함수호출 노드**만 본다 — docstring·주석에
    함수명을 설명 목적으로 적는 것(이 진단 자체의 docstring 포함)은 오탐이면
    안 된다.
    """
    tree = ast.parse(inspect.getsource(E))
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called_names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called_names.add(fn.attr)
    forbidden = {"residence_time_s", "slurry_volumes_cm3",
                 "groove_wear_flow_state", "micron_cabot_life_wafers"}
    hit = forbidden & called_names
    assert not hit, (
        f"engine.py가 {hit}를 실제로 호출한다 — h_land_um·q_actual_cm3_per_s가 "
        "Recipe/팩 어디에도 없고, 시간->wafer 환산도 없어 지어낸 값으로 계산한 "
        "결과가 제품 출력이 되면 안 된다.")


def test_original_module_untouched():
    """원본 모듈 pad_groove_wear_flow.py는 1바이트도 수정하지 않는다 — git diff가
    비어 있어야 한다(트래킹된 파일 기준)."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/tier2_physics/pad_groove_wear_flow.py"],
        capture_output=True, text=True,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"
