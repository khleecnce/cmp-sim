"""MODEL-BASIS 요약절의 '현재 완성도' 문장이 실제 판정과 일치하는지 고정.

2026-09-18 실제 사고: 격자가 59/60 → 60/60 으로 채워진 뒤에도 요약절에
"남은 미충족은 χ/cu_h2o2_bta 1칸뿐" 이라는 **하드코딩 문장**이 남아,
같은 문서 안에서 "완성 판정: 완성 (60/60)" 과 정면으로 모순됐다.
이 문서는 사용자 제출용(C8)이라 모순 자체가 결함이다.

여기서 검사하는 것은 "60/60 이냐"가 아니라 **문장이 res['fails'] 에서
생성되는가**다 — 그래야 미래에 칸이 되돌아가도(C7 무퇴보 조항) 문서가
따라온다.
"""
import re
import pytest

from tools import completion as C


def _summary_text(res, packs=None):
    g = C.grid()
    packs = packs or C._packs()
    return "\n".join(C._summary_section(g, res, packs))


def test_summary_reports_no_shortfall_when_complete():
    res = C.check(verbose=False)
    if res["fails"]:
        pytest.skip("현재 미완 상태 — 반대 방향 테스트가 담당")
    txt = _summary_text(res)
    assert f"{res['cells_done']}/{res['cells_total']}칸" in txt
    # 완성인데 "남은 미충족 ...칸:" 같은 문구가 있으면 모순이다
    assert "남은 미충족" not in txt, "완성 판정인데 미충족 문장이 남아 있다"
    assert "완성 기준을 전부 만족" in txt


def test_summary_lists_actual_fails_not_hardcoded():
    """가짜 fails 를 주입했을 때 그 칸이 문장에 실제로 나오는가."""
    res = dict(C.check(verbose=False))
    res["fails"] = ["C2 psi psi/sti_ceria: confidence=estimated"]
    res["cells_done"] = res["cells_total"] - 1
    txt = _summary_text(res)
    assert "남은 미충족 1칸" in txt
    assert "표면 보호도" in txt or "psi" in txt, txt
    # 낡은 하드코딩 문구가 되살아나면 실패
    assert "cu_h2o2_bta`(Cu CMP, H2O2 산화제) 1칸**뿐" not in txt


def test_summary_fail_count_matches_len_fails():
    res = dict(C.check(verbose=False))
    res["fails"] = [
        "C2 chi chi/sic_ceria_h2o2: confidence=estimated",
        "C1 delta delta/oxide_silica: status=unmodeled",
    ]
    res["cells_done"] = res["cells_total"] - 2
    txt = _summary_text(res)
    m = re.search(r"남은 미충족 (\d+)칸", txt)
    assert m and int(m.group(1)) == 2, txt
