"""sim/calibration/prior.py 계약 테스트 — ORG.md §7.4 M3 게이트 2번째 항목.

여기서 고정하는 것:
  ① confidence 등급 → sigma_log 순단조, literature=판정#55(≈1.5배) 정합
  ② unverified는 prior를 만들지 않는다(오염 방지, COMPLETION.md)
  ③ mu/source는 팩 YAML 선언값 그대로(지어내지 않는다)
  ④ sample_priors 재현성·로그정규 중심
  ⑤ prior_predictive_mrr이 결정론적 simulate와 같은 오더
  ⑥ prior.py는 sim/factors.py·sim/engine.py·sim/params.py·knowledge/params/*.yaml을
     읽기만 하고 절대 쓰지 않는다(런타임 무변경 + ast 임포트 경계)
"""
import ast
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.params import available_packs, load_pack             # noqa: E402
from sim.engine import Recipe, simulate                       # noqa: E402
from sim.calibration.prior import (                            # noqa: E402
    ParamPrior, PriorExcluded,
    confidence_to_log_sigma, build_param_priors, build_kp_prior,
    sample_priors, prior_predictive_mrr,
)

_MATERIAL_PACKS = [p for p in available_packs() if p != "base"]

_PROTECTED_FILES = [
    ROOT / "sim" / "factors.py",
    ROOT / "sim" / "engine.py",
    ROOT / "sim" / "params.py",
    *sorted((ROOT / "knowledge" / "params").glob("*.yaml")),
]


# ═══════════════════════════════ ① confidence → sigma_log

def test_confidence_to_log_sigma_strictly_monotone():
    m = confidence_to_log_sigma("measured")
    lit = confidence_to_log_sigma("literature")
    est = confidence_to_log_sigma("estimated")
    assert m < lit < est


def test_literature_sigma_matches_verdict_55_scatter():
    # 코드의 _LOG_SIGMA_LITERATURE 식을 베끼지 않고, 판정#55의 "≈1.5배"라는
    # 숫자에서 독립적으로 로그정규 1-시그마 폭을 계산해 대조한다.
    independent_log_sigma = math.log(1.5)
    assert confidence_to_log_sigma("literature") == pytest.approx(independent_log_sigma, rel=1e-12)


def test_verified_and_estimated_bracket_literature():
    # verified(가장 좁음) < measured < literature < estimated(가장 넓음) — 5등급 전 순서
    v = confidence_to_log_sigma("verified")
    m = confidence_to_log_sigma("measured")
    lit = confidence_to_log_sigma("literature")
    est = confidence_to_log_sigma("estimated")
    assert v < m < lit < est


# ═══════════════════════════════ ② unverified 배제

def test_unverified_confidence_raises():
    with pytest.raises(PriorExcluded):
        confidence_to_log_sigma("unverified")


def test_unknown_confidence_raises():
    with pytest.raises(PriorExcluded):
        confidence_to_log_sigma("unknown")


def test_build_param_priors_excludes_unverified_key():
    # base.yaml의 tau_mrr_exponent는 confidence: unverified로 선언돼 있다 —
    # 이 키가 build_param_priors 출력에 나타나면 안 된다.
    pk = load_pack("base")
    assert pk.param("tau_mrr_exponent").confidence == "unverified"
    priors = build_param_priors("base")
    assert "tau_mrr_exponent" not in priors


# ═══════════════════════════════ ③ mu/source는 팩 그대로

@pytest.mark.parametrize("pack", available_packs())
def test_build_param_priors_runs_without_exception(pack):
    priors = build_param_priors(pack)
    assert isinstance(priors, dict)


@pytest.mark.parametrize("pack", available_packs())
def test_mu_matches_pack_exactly(pack):
    pk = load_pack(pack)
    priors = build_param_priors(pack)
    assert priors  # 5개 팩 전부 최소 1개는 나와야 한다(literature가 압도적 다수)
    for key, pr in priors.items():
        assert pr.mu == pk.get(key), f"{pack}.{key}: mu가 팩 값과 다르다(지어냈나?)"


def test_source_matches_pack_yaml():
    pk = load_pack("oxide_silica")
    expected_source = pk.param("kp_m_per_pa").source or None
    kp_prior = build_kp_prior("oxide_silica")
    assert kp_prior.source == expected_source


@pytest.mark.parametrize("pack", _MATERIAL_PACKS)
def test_build_kp_prior_matches_pack_declaration(pack):
    pk = load_pack(pack)
    p = pk.param("kp_m_per_pa")
    kp_prior = build_kp_prior(pack)
    assert kp_prior.mu == p.value
    assert kp_prior.confidence == p.confidence
    assert kp_prior.source == (p.source or None)


# ═══════════════════════════════ ④ 표본 추출

def test_sample_priors_reproducible_with_same_seed():
    priors = build_param_priors("oxide_silica")
    a = sample_priors(priors, 50, seed=7)
    b = sample_priors(priors, 50, seed=7)
    for key in priors:
        np.testing.assert_array_equal(a[key], b[key])


def test_sample_priors_different_seed_differs():
    priors = {"kp_m_per_pa": build_kp_prior("oxide_silica")}
    a = sample_priors(priors, 50, seed=1)
    b = sample_priors(priors, 50, seed=2)
    assert not np.array_equal(a["kp_m_per_pa"], b["kp_m_per_pa"])


def test_sample_geometric_mean_converges_to_mu():
    kp_prior = build_kp_prior("oxide_silica")
    samples = sample_priors({"kp": kp_prior}, 20000, seed=0)["kp"]
    geo_mean = float(np.exp(np.mean(np.log(samples))))
    assert geo_mean == pytest.approx(kp_prior.mu, rel=0.05)


# ═══════════════════════════════ ⑤ prior predictive MRR

@pytest.mark.parametrize("pack", _MATERIAL_PACKS)
def test_prior_predictive_mrr_median_same_order_as_deterministic(pack):
    out = prior_predictive_mrr(pack, n=60, seed=0)
    det = float(np.mean(simulate(Recipe(pack=pack)).mrr_nm_per_min))
    assert out["deterministic_mrr_nm_per_min"] == pytest.approx(det, rel=1e-9)
    assert out["median_nm_per_min"] == pytest.approx(det, rel=0.5)


def test_prior_predictive_mrr_shape_and_excluded_params():
    out = prior_predictive_mrr("oxide_silica", n=15, seed=0)
    assert out["mrr_samples_nm_per_min"].shape == (15,)
    assert np.all(out["mrr_samples_nm_per_min"] > 0)
    assert "kp_m_per_pa" not in out["excluded_params"]
    assert len(out["excluded_params"]) > 0


# ═══════════════════════════════ ⑥ 읽기 전용 — 런타임 + 정적(ast)

def test_prior_module_never_writes_protected_files():
    before = {p: p.read_bytes() for p in _PROTECTED_FILES}

    for pack in available_packs():
        build_param_priors(pack)
    for pack in _MATERIAL_PACKS:
        build_kp_prior(pack)
    priors = build_param_priors("oxide_silica")
    sample_priors(priors, 10, seed=3)
    prior_predictive_mrr("oxide_silica", n=5, seed=3)

    after = {p: p.read_bytes() for p in _PROTECTED_FILES}
    assert before == after


_WRITE_ATTRS = {
    "write_text", "write_bytes", "write", "dump", "safe_dump",
    "save", "save_scales", "writelines",
}


def test_prior_module_has_no_write_calls_ast():
    """prior.py 소스를 정적으로 스캔해 파일 쓰기 패턴이 전혀 없음을 고정한다.

    ⚠ 이것은 "쓰지 않는다"를 증명하는 화이트리스트가 아니라, 알려진 쓰기
      패턴(open(...,'w'), Path.write_text/write_bytes, yaml.dump 등)이 코드에
      나타나면 실패하는 회귀 가드다 — 향후 누군가 여기 쓰기 코드를 추가하면
      이 테스트가 먼저 죽는다.
    """
    src = (ROOT / "sim" / "calibration" / "prior.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _WRITE_ATTRS:
            offenders.append(func.attr)
        if isinstance(func, ast.Name) and func.id == "open":
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and \
                   any(c in str(kw.value.value) for c in "wax"):
                    offenders.append("open(mode=...)")
            for arg in node.args[1:2]:
                if isinstance(arg, ast.Constant) and any(c in str(arg.value) for c in "wax"):
                    offenders.append("open(..., mode)")
    assert not offenders, f"prior.py에 쓰기 패턴이 있다: {offenders}"


def test_prior_module_does_not_import_yaml_writer_symbols():
    """prior.py가 sim.params/sim.engine 등 읽기 API만 임포트하는지 ast로 고정.

    load_pack/ParamPack/Recipe/simulate 는 전부 읽기(로드·실행) API다 — 팩
    파일을 쓰는 save_scales류(series_scale.py)나 yaml.safe_dump 계열을
    임포트하면 이 테스트가 잡는다.
    """
    src = (ROOT / "sim" / "calibration" / "prior.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned_names = {"save_scales", "yaml"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
    assert not (imported & banned_names), f"금지된 심볼 임포트: {imported & banned_names}"
