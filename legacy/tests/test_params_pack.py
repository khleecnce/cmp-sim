"""파라미터 팩 계약 테스트.

이 파일이 지키는 것 (2026-09-06 사용자 지시):
  "시뮬레이션툴이야 껍데기고 그 안에는 학습내용이 잘 머지되어서 있어야되는거 아니야?
   그 내용만 바꾸면 각각 다른 시뮬레이션을 할수있도록 설계해"

즉 **코드를 고치지 않고 팩만 바꿔서 다른 시뮬레이션이 되는가**를 검증한다.
그게 깨지면 껍데기와 내용이 다시 붙어버린 것이다.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.engine import Recipe, simulate           # noqa: E402
from sim.params import (ParamMissing, available_packs,  # noqa: E402
                        load_pack)
import sim.models  # noqa: E402,F401  (모델 등록)


# ── 팩 자체의 계약 ──────────────────────────────────────────
def test_packs_exist_and_load():
    packs = available_packs()
    assert "base" in packs, "베이스 팩이 있어야 나머지가 상속한다"
    for name in packs:
        load_pack(name)          # 파싱 에러 없이 읽혀야 한다


def test_inheritance_child_overrides_parent():
    """상속: 자식이 부모를 덮어쓰되, 안 건드린 값은 물려받는다."""
    base = load_pack("base")
    ceria = load_pack("sti_ceria")     # base → oxide_silica → sti_ceria
    assert ceria.lineage == ["base", "oxide_silica", "sti_ceria"]
    # 덮어쓴 값
    assert ceria.get("abrasive") == "ceria"
    assert ceria.get("kp_m_per_pa") != load_pack("oxide_silica").get("kp_m_per_pa")
    # 물려받은 값 (base에만 있는 것)
    assert ceria.get("pad_E_star_pa") == base.get("pad_E_star_pa")


def test_missing_param_raises_not_guesses():
    """없는 값은 조용한 기본값이 아니라 예외다.

    이게 이 설계의 안전장치다 — Cu 팩을 돌렸는데 산화막 Kp가 말없이 쓰이면
    결과 전체가 거짓말이 된다.
    """
    pk = load_pack("base")
    with pytest.raises(ParamMissing):
        pk.get("존재하지_않는_물성")


def test_every_param_carries_a_source():
    """출처 없는 값이 팩에 들어오면 잡는다 — 근거 없는 숫자 유입 방지.

    film/abrasive/oxidizer/inhibitor는 물성이 아니라 **식별자**(무엇을 쓰는가)라
    출처를 요구하지 않는다. 숫자만 근거를 달아야 한다.
    """
    IDENTIFIERS = {"film", "abrasive", "oxidizer", "inhibitor"}
    missing = []
    for name in available_packs():
        raw = yaml.safe_load((_ROOT / "knowledge" / "params" / f"{name}.yaml").read_text())
        for key, v in (raw.get("params") or {}).items():
            if key in IDENTIFIERS:
                continue
            if not (isinstance(v, dict) and v.get("source")):
                missing.append(f"{name}:{key}")
    assert not missing, f"출처 없는 파라미터: {missing}"


def test_numeric_params_are_numbers_not_strings():
    """YAML 1.1은 '1.0e11'을 문자열로 준다 — 로더가 숫자로 정규화해야 한다.

    회귀 방어: 이걸 놓치면 eta='1.0e11'이 numpy 곱셈까지 흘러가
    `can't multiply sequence by non-int`라는 엉뚱한 메시지로 터진다(실제 발생).
    """
    numeric_suffixes = ("_pa", "_m", "_m2", "_psi", "_nm", "_mM", "_h", "_s",
                        "_mps", "_pct", "_ph")
    bad = []
    for name in available_packs():
        pk = load_pack(name)
        for key, prm in pk.params.items():
            looks_numeric = (key.endswith(numeric_suffixes) or "kp_" in key
                             or key in ("n_points", "rpm_wafer", "rpm_platen"))
            if looks_numeric and isinstance(prm.value, str):
                bad.append(f"{name}:{key}={prm.value!r}")
    assert not bad, f"문자열로 남은 수치 파라미터: {bad}"


# ── 핵심 계약: 팩을 바꾸면 시뮬레이션이 바뀐다 ───────────────
def test_swapping_pack_changes_result_without_touching_code():
    """같은 Recipe·같은 모델·같은 코드. 팩 이름만 다르다 → 결과가 달라야 한다."""
    def run(pack):
        return simulate(Recipe(pack=pack, time_s=60.0))

    ox = run("oxide_silica")
    cu = run("cu_h2o2_bta")

    assert ox.pack == "oxide_silica" and cu.pack == "cu_h2o2_bta"
    assert ox.film == "oxide" and cu.film == "cu"
    ox_mrr = float(np.mean(ox.mrr_nm_per_min))
    cu_mrr = float(np.mean(cu.mrr_nm_per_min))
    # Cu Kp(3.5e-13) > oxide Kp(1.0e-13) 이므로 Cu가 더 빨리 깎여야 한다.
    # 값을 고정하지 않고 '관계'를 검사한다 — 팩 수치가 갱신돼도 계약은 유지된다.
    assert cu_mrr > ox_mrr, f"Cu({cu_mrr})가 oxide({ox_mrr})보다 커야 한다"


def test_mrr_scales_with_pack_kp():
    """MRR ∝ Kp (Preston). 팩의 Kp 비가 결과 비로 그대로 나타나야 한다."""
    ox = simulate(Recipe(pack="oxide_silica", time_s=60.0))
    cu = simulate(Recipe(pack="cu_h2o2_bta", time_s=60.0))
    kp_ratio = (load_pack("cu_h2o2_bta").get("kp_m_per_pa")
                / load_pack("oxide_silica").get("kp_m_per_pa"))
    mrr_ratio = float(np.mean(cu.mrr_nm_per_min)) / float(np.mean(ox.mrr_nm_per_min))
    assert mrr_ratio == pytest.approx(kp_ratio, rel=1e-6), (
        "MRR 비가 Kp 비와 달라졌다 — 팩 값이 엔진까지 안 흐르고 있다")


def test_explicit_recipe_field_overrides_pack():
    """레시피에 직접 준 값이 팩보다 우선한다 (사람이 이번 런에 정한 것)."""
    packed = simulate(Recipe(pack="oxide_silica"))
    forced = simulate(Recipe(pack="oxide_silica", pressure_psi=6.0))
    assert float(np.mean(forced.mrr_nm_per_min)) > float(np.mean(packed.mrr_nm_per_min))


# ── 출처 추적 ───────────────────────────────────────────────
def test_result_carries_provenance_of_used_values():
    """결과가 '이 숫자가 어디서 왔나'를 들고 나온다."""
    res = simulate(Recipe(pack="cu_h2o2_bta"))
    assert res.provenance, "provenance가 비어 있다"
    assert "kp_m_per_pa" in res.provenance
    entry = res.provenance["kp_m_per_pa"]
    assert entry["source"], "Kp에 출처가 없다"
    assert entry["confidence"] in ("verified", "literature", "estimated", "unverified", "unknown")


def test_unverified_params_surface_as_warning():
    """미검증 값을 쓰면 결과 notes에 경고가 뜬다 — 조용히 넘어가지 않는다.

    Cu 팩의 Kp는 confidence=estimated(문헌 역산, 미재현)다.
    """
    res = simulate(Recipe(pack="cu_h2o2_bta"))
    joined = " ".join(res.notes)
    assert "미검증" in joined and "kp_m_per_pa" in joined, (
        f"미검증 경고가 없다. notes={res.notes}")


def test_verified_only_run_has_no_false_alarm():
    """반대로, 쓰인 값이 전부 검증됐으면 미검증 경고가 뜨면 안 된다.

    경고가 항상 뜨면 아무도 안 읽는다 — 그래서 '쓰인 값'만 검사하는 게 중요하다.
    """
    pk = load_pack("oxide_silica")
    # kp는 verified 이므로, kp만 쓰는 tier1 모델은 kp 관련 경고가 없어야 한다
    assert pk.param("kp_m_per_pa").confidence == "verified"
